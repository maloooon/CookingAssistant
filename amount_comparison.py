import re

def compare_amounts(amount1, amount2):
    value1, unit1 = extract_value_and_unit(amount1)
    value2, unit2 = extract_value_and_unit(amount2)

    # Convert to a common unit (grams for weight, milliliters for volume)
    value1 = convert_to_common_unit(value1, unit1)
    value2 = convert_to_common_unit(value2, unit2)

    # Compare the numeric values
    return value1 - value2

def extract_value_and_unit(amount_str):
    # Use regex to extract the numeric value and unit
    match = re.match(r"(\d+(?:\.\d+)?)\s*([a-zA-Z]+)", amount_str)
    if match:
        value = float(match.group(1))
        unit = match.group(2).lower()
        return value, unit
    else:
        raise ValueError(f"Invalid amount format: {amount_str}")

def convert_to_common_unit(value, unit):
    # Convert to grams for weight, milliliters for volume
    if unit in ['g', 'ml']:
        return value
    elif unit == 'kg':
        return value * 1000  # convert to grams
    elif unit == 'l':
        return value * 1000  # convert to milliliters
    else:
        raise ValueError(f"Unsupported unit: {unit}")


def is_enough_ingredient(home_amount, recipe_amount):
    try:
        comparison = compare_amounts(home_amount, recipe_amount)
        return comparison >= 0
    except ValueError as e:
        print(f"Error comparing amounts: {e}")
        return False


