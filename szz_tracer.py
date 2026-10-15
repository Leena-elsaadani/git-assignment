
import argparse
import csv
import subprocess
from collections import Counter
from pathlib import Path

from pydriller import Repository


def run_git(repo_path, args):
    """Run a Git command inside the target repository."""
    result = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.strip()


def trace_szz(repo_path, fix_hash):
    repo_path = str(Path(repo_path).resolve())

    # Check that the fixing commit exists.
    run_git(repo_path, ["cat-file", "-e", f"{fix_hash}^{{commit}}"])

    # Load the fixing commit.
    commits = list(
        Repository(repo_path, single=fix_hash).traverse_commits()
    )

    if not commits:
        raise ValueError("Fixing commit not found.")

    fix_commit = commits[0]

    if not fix_commit.parents:
        raise ValueError("Fixing commit has no parent.")

    parent_hash = fix_commit.parents[0]
    candidates = Counter()
    results = []

    for modified_file in fix_commit.modified_files:
        old_path = modified_file.old_path

        if not old_path:
            continue

        deleted_lines = modified_file.diff_parsed["deleted"]

        for line_number, old_line in deleted_lines:
            try:
                blame = run_git(
                    repo_path,
                    [
                        "blame",
                        "-L", f"{line_number},{line_number}",
                        parent_hash,
                        "--", old_path
                    ]
                )
            except subprocess.CalledProcessError:
                print(f"Could not trace {old_path}:{line_number}")
                continue

            tokens = blame.split()

            if not tokens:
                continue

            bic_hash = tokens[0].lstrip("^")

            if not bic_hash or not all(
                char in "0123456789abcdefABCDEF"
                for char in bic_hash
            ):
                continue

            candidates[bic_hash] += 1

            results.append({
                "BFC": fix_commit.hash,
                "parent": parent_hash,
                "file": old_path,
                "old_line_number": line_number,
                "deleted_line": old_line,
                "candidate_BIC": bic_hash
            })

    return fix_commit.hash, parent_hash, candidates, results


def main():
    parser = argparse.ArgumentParser(
        description="Trace candidate bug-inducing commits using SZZ."
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="Path to the Git repository"
    )
    parser.add_argument(
        "--fix",
        required=True,
        help="Bug-fixing commit hash"
    )
    args = parser.parse_args()

    try:
        bfc, parent, candidates, results = trace_szz(
            args.repo, args.fix
        )
    except (ValueError, subprocess.CalledProcessError) as error:
        print(f"Error: {error}")
        return

    print(f"\nBug-fixing commit (BFC): {bfc}")
    print(f"Parent revision: {parent}")
    print("\nCandidate bug-inducing commits (BICs):")

    if not candidates:
        print("No candidates found from deleted lines.")
    else:
        for bic_hash, count in candidates.most_common():
            details = run_git(
                args.repo,
                [
                    "show", "-s",
                    "--format=%h | %ad | %an | %s",
                    "--date=short", bic_hash
                ]
            )
            print(f"{bic_hash} — traced lines: {count}")
            print(details)

    output_file = Path("szz_results.csv")

    with output_file.open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        fields = [
            "BFC", "parent", "file", "old_line_number",
            "deleted_line", "candidate_BIC"
        ]
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults saved to: {output_file.resolve()}")


if __name__ == "__main__":
    main()
