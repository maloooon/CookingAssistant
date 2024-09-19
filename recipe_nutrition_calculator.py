import sqlite3
import re

class MissingNutritionInfoError(Exception):
    pass

def is_unit_less(amount):
    # Check if the amount is a fraction or a whole number without units
    return bool(re.match(r'^(\d+(/\d+)?|\d+\.\d+)$', amount))

def extract_number_from_amount(amount):
    # Extract the numerical part from the amount string
    match = re.match(r'^([\d./]+)', amount)
    if match:
        num_str = match.group(1)
        # Handle fractions
        if '/' in num_str:
            num, denom = map(float, num_str.split('/'))
            return num / denom
        return float(num_str)
    return None

def calculate_recipe_nutrition(recipe_name):
    # Connect to the database
    conn = sqlite3.connect('groceries.db')
    cursor = conn.cursor()

    # Get recipe ingredients and amounts
    cursor.execute("SELECT ingredients, amount FROM recipes WHERE name = ?", (recipe_name,))
    recipe_data = cursor.fetchone()

    if not recipe_data:
        print(f"Recipe '{recipe_name}' not found.")
        conn.close()
        return

    ingredients = recipe_data[0].split()
    amounts = recipe_data[1].split()

    # Initialize nutritional totals
    total_calories = total_fat = total_protein = total_carbs = total_sugar = total_fiber = 0
    skipped_ingredients = []

    try:
        # Calculate nutrition for each ingredient
        for ingredient, amount in zip(ingredients, amounts):
            if is_unit_less(amount):
                skipped_ingredients.append(ingredient)
                continue

            amount_value = extract_number_from_amount(amount)
            if amount_value is None:
                skipped_ingredients.append(ingredient)
                continue

            # Get nutritional data for the ingredient
            cursor.execute("""
                SELECT calories, fat, protein, carbs, sugar, fiber
                FROM nutrition
                WHERE category = ?
            """, (ingredient,))
            nutrition_data = cursor.fetchone()

            if not nutrition_data:
                raise MissingNutritionInfoError(f"Missing nutritional information for ingredient: {ingredient}")

            # Calculate nutrition based on amount
            calories, fat, protein, carbs, sugar, fiber = nutrition_data
            factor = amount_value / 100  # Since nutrition data is per 100g/ml

            total_calories += calories * factor
            total_fat += fat * factor
            total_protein += protein * factor
            total_carbs += carbs * factor
            total_sugar += sugar * factor
            total_fiber += fiber * factor

        # Format the nutrition values as a string
        nutrition_string = f"""Calories: {total_calories:.2f}
Fat: {total_fat:.2f}g
Protein: {total_protein:.2f}g
Carbs: {total_carbs:.2f}g
Sugar: {total_sugar:.2f}g
Fiber: {total_fiber:.2f}g"""

        # Update the recipe table with the calculated nutrition values
        cursor.execute("""
            UPDATE recipes
            SET nutrition_values = ?
            WHERE name = ?
        """, (nutrition_string, recipe_name))
        conn.commit()
        print(f"Nutrition values for '{recipe_name}' have been updated in the database.")
        
        if skipped_ingredients:
            print(f"Note: The following ingredients were skipped due to lack of unit information or invalid format: {', '.join(skipped_ingredients)}")

    except MissingNutritionInfoError as e:
        print(f"Error: {e}")
        print("The nutrition values were not calculated or updated.")
    except sqlite3.Error as e:
        print(f"An error occurred while updating the database: {e}")
    finally:
        conn.close()


