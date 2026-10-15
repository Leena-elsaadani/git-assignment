def calculate_tax(price, international=False):
    tax_rate = 0.10
    if international:
        tax_rate = 0.05
    return price * tax_rate


def calculate_total(price, international=False):
    return price + calculate_tax(price, international)
