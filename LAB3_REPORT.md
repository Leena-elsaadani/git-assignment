# Lab 3: Code Forensics

## 1. Objective

The objective of this lab was to investigate Git history and use the SZZ (Sliwerski-Zimmermann-Zeller) approach to trace a code change in a fixing commit back to a candidate bug-inducing commit.

## 2. Repository and Environment

Repository: `Lab3-Code-Forensics`

Tools used:
- Git
- Python 3.13.0
- PyDriller 2.12
- Visual Studio Code

PyDriller was installed using:

```powershell
python -m pip install pydriller
```

The installation was verified successfully with:

```powershell
python -c "from pydriller import Repository; print('PyDriller is ready')"
```

## 3. Commit History

The command `git log --oneline` showed these commits:

| Commit | Message |
|---|---|
| `eafd5ba` | Fix international tax calculation |
| `4837fe7` | Add tax calculator |

The initial commit added the tax calculator with an international tax rate of `0.05`. The later commit changed that rate to `0.15`.

## 4. Manual Code Investigation

The following commands were used to inspect the history:

```bash
git log --oneline
git log -p -n 1 HEAD
git blame src/tax_calculator.py
git show --format=fuller eafd5ba -- src/tax_calculator.py
git blame eafd5ba^ -L 1,9 -- src/tax_calculator.py
git show --format=fuller 4837fe7 -- src/tax_calculator.py
```

The current `git blame` output attributes the line `tax_rate = 0.15` to commit `eafd5ba`. Blaming the file at the parent of that commit shows the earlier value `tax_rate = 0.05`, attributed to `4837fe7`.

This investigation shows how Git history can help trace a code change to its earlier version.

## 5. SZZ Implementation

I created `szz_tracer.py` using Python and PyDriller. The script accepts a repository path and a fixing commit hash, examines deleted lines in the fixing commit, traces those lines using Git blame on the parent revision, counts candidate commits, and saves the detailed results to `szz_results.csv`.

I checked the script syntax using:

```powershell
python -m py_compile szz_tracer.py
```

The command completed without reporting a syntax error.

I ran the script using:

```powershell
python szz_tracer.py --repo "." --fix eafd5ba
```

## 6. Results

The script completed successfully and reported:

- **Bug-fixing commit (BFC):** `eafd5ba35613a569ba57c6a6e64f3cf846d33a56`
- **Parent revision:** `4837fe71cdbcaf3c8b066bdf7614e0297b0dce6c`
- **Candidate bug-inducing commit (BIC):** `4837fe7`
- **Candidate commit message:** `Add tax calculator`
- **Number of traced lines:** 1

The output was saved to `szz_results.csv`.

The result agrees with the manual investigation: the fixing commit changed the international tax rate from `0.05` to `0.15`, and the earlier line was attributed to commit `4837fe7`.

## 7. Discussion and Limitations

The experiment demonstrates how Git commands and SZZ tracing can help investigate code changes. Manual inspection provides context, while SZZ automates tracing changed lines to earlier commits.

SZZ identifies candidate bug-inducing commits; it does not prove on its own that a commit introduced a defect. The result should be reviewed alongside the code and commit history.

This experiment used a small practice repository with two commits. These findings describe this practice repository and should not be presented as results from a separate instructor-provided repository.

## 8. Conclusion

I used `git log`, `git show`, and `git blame` to investigate the tax calculator's history. I then ran a Python SZZ tracer using PyDriller. The script identified `4837fe7` as the candidate bug-inducing commit for fixing commit `eafd5ba`, traced one line, and saved the details in `szz_results.csv`.

## 9. Deliverables

- `szz_tracer.py` — SZZ tracing script.
- `szz_results.csv` — generated results.
- `LAB3_REPORT.md` — lab report.
