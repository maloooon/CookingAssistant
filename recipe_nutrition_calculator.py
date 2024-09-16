import sqlite3

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

    # Calculate nutrition for each ingredient
    for ingredient, amount in zip(ingredients, amounts):
        # Remove 'g' or 'ml' from amount and convert to float
        amount_value = float(amount[:-1] if amount.endswith(('g', 'l')) else amount)

        # Get nutritional data for the ingredient
        cursor.execute("""
            SELECT calories, fat, protein, carbs, sugar, fiber
            FROM nutrition
            WHERE category = ?
        """, (ingredient,))
        nutrition_data = cursor.fetchone()

        if nutrition_data:
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
    try:
        cursor.execute("""
            UPDATE recipes
            SET nutrition_values = ?
            WHERE name = ?
        """, (nutrition_string, recipe_name))
        conn.commit()
        print(f"Nutrition values for '{recipe_name}' have been updated in the database.")
    except sqlite3.Error as e:
        print(f"An error occurred while updating the database: {e}")

    conn.close()

# Example usage
calculate_recipe_nutrition("Easy Black Rice")