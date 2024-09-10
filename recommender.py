"""Easy recommendation system based on cosine similarity between ingredients"""

import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from amount_comparison import extract_value_and_unit, convert_to_common_unit

class RecipeRecommender:
    def __init__(self, db_path):
        # Initialize the connection to the SQLite database
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def get_home_ingredients(self):
        # Fetch all ingredients available at home from the 'home' table
        self.cursor.execute("SELECT name, category FROM home")
        return self.cursor.fetchall()

    def get_recipes(self):
        # Fetch all recipes from the 'recipes' table
        self.cursor.execute("SELECT id, name, ingredients FROM recipes")
        return self.cursor.fetchall()


    def prepare_recipe_data(self):
        # Prepare recipe data for content-based filtering
        recipes = self.get_recipes()
        recipe_data = []
        for recipe_id, name, ingredients in recipes:
            # Ingredients are already space-separated, so we don't need to modify them
            recipe_data.append((recipe_id, name, ingredients))
        # Convert the recipe data to a pandas DataFrame for easier manipulation
        return pd.DataFrame(recipe_data, columns=['id', 'name', 'ingredients'])

    def recommend_recipes(self, top_n=5):
        # Get ingredients available at home
        home_ingredients = self.get_home_ingredients()
        # Create a space-separated string of home ingredient categories
        home_ingredients_string = ' '.join([category for _, category in home_ingredients])

        # Prepare recipe data
        recipe_df = self.prepare_recipe_data()

        # Create a TF-IDF vectorizer
        # This will convert our ingredient lists into numerical vectors
        tfidf = TfidfVectorizer(token_pattern=r'\b\w+\b')

        # Fit the vectorizer on recipe ingredients and transform them to TF-IDF vectors
        recipe_vectors = tfidf.fit_transform(recipe_df['ingredients'])

        # Transform the home ingredients to a TF-IDF vector
        home_vector = tfidf.transform([home_ingredients_string])

        # Calculate cosine similarity between home ingredients and all recipes
        # This measures how similar each recipe is to the ingredients we have at home
        cosine_similarities = cosine_similarity(home_vector, recipe_vectors).flatten()

        # Add similarity scores to the recipe DataFrame
        recipe_df['similarity'] = cosine_similarities

        # Sort recipes by similarity score (descending) and select top N
        recommended_recipes = recipe_df.sort_values('similarity', ascending=False).head(top_n)

        # Return the ids, names and similarity scores of the top N recipes
        return recommended_recipes[['id', 'name', 'similarity']]
    

    def get_home_ingredient_amount(self, name):
        self.cursor.execute("SELECT amount FROM home WHERE name = ?", (name,))
        result = self.cursor.fetchone()
        return result[0] if result else "0g"

    def get_grocery_item_amount(self, name):
        self.cursor.execute("SELECT amount FROM groceries WHERE name = ?", (name,))
        result = self.cursor.fetchone()
        return result[0] if result else "0g"
    
    def get_grocery_item_price(self, name):
        self.cursor.execute("SELECT price FROM groceries WHERE name = ?", (name,))
        result = self.cursor.fetchone()
        return result[0] if result else 0.0

    def get_recipe_ingredients(self, recipe_id):
        # Fetch ingredients for a specific recipe
        self.cursor.execute("SELECT ingredients FROM recipes WHERE id = ?", (int(recipe_id),))
        return set(self.cursor.fetchone()[0].split())
    
    def get_home_ingredients_by_category(self, category):
        # Fetch all home ingredients of a specific category
        self.cursor.execute("SELECT name, price, amount FROM home WHERE category = ?", (category,))
        return self.cursor.fetchall()

    def get_grocery_items_by_category(self, category):
        # Fetch all grocery items of a specific category
        self.cursor.execute("SELECT id, name, price, amount FROM groceries WHERE category = ?", (category,))
        return self.cursor.fetchall()

    def add_to_chosen_for_recipe(self, name, category, price, athome, amount):
        # Add a chosen ingredient to the 'chosenforrecipe' table
        self.cursor.execute("""
            INSERT INTO chosenforrecipe (name, category, price, athome, amount)
            VALUES (?, ?, ?, ?, ?)
        """, (name, category, price, athome, amount))
        self.conn.commit()

    def get_total_prices(self):
        # Calculate both the total price and the price for items not at home
        self.cursor.execute("""
            SELECT 
                SUM(price) as total_price,
                SUM(CASE WHEN athome = 0 THEN price ELSE 0 END) as to_buy_price
            FROM chosenforrecipe
        """)
        return self.cursor.fetchone()
    
    def clear_chosen_for_recipe(self):
        # Clear all entries from the 'chosenforrecipe' table
        self.cursor.execute("DELETE FROM chosenforrecipe")
        self.conn.commit()
    
    def add_to_shopping_list(self):
        try:
            # Fetch items that are not at home from chosenforrecipe
            self.cursor.execute("SELECT name, category, price, amount FROM chosenforrecipe WHERE athome = 0")
            items_to_buy = self.cursor.fetchall()

            if not items_to_buy:
                print("No items need to be added to the shopping list.")
                return

            for name, category, price, amount in items_to_buy:
                # Get the original amount from the groceries table
                self.cursor.execute("SELECT amount FROM groceries WHERE name = ?", (name,))
                original_amount = self.cursor.fetchone()

                if original_amount:
                    original_amount = original_amount[0]
                    # Calculate the quantity ratio
                    current_amount_value = self.get_amount_value(amount)
                    original_amount_value = self.get_amount_value(original_amount)
                    quantity_ratio = current_amount_value / original_amount_value if original_amount_value != 0 else 0

                    # Check if the item already exists in the shopping list
                    self.cursor.execute("SELECT amount, price, quantity FROM shoppinglist WHERE name = ?", (name,))
                    existing_item = self.cursor.fetchone()

                    if existing_item:
                        existing_amount, existing_price, existing_quantity = existing_item
                        # Add the amounts together
                        new_amount_value = self.get_amount_value(existing_amount) + current_amount_value
                        new_amount = f"{new_amount_value}{self.get_amount_unit(existing_amount)}"
                        new_price = existing_price + price
                        new_quantity = existing_quantity + quantity_ratio

                        # Update the existing item
                        self.cursor.execute("""
                            UPDATE shoppinglist 
                            SET amount = ?, price = ?, quantity = ?
                            WHERE name = ?
                        """, (new_amount, new_price, new_quantity, name))
                    else:
                        # Insert new item
                        self.cursor.execute("""
                            INSERT INTO shoppinglist (name, category, price, amount, quantity)
                            VALUES (?, ?, ?, ?, ?)
                        """, (name, category, price, amount, quantity_ratio))

            self.conn.commit()
            print(f"Updated shopping list with {len(items_to_buy)} item(s).")

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()

    def get_amount_value(self, amount_str):
        return float(''.join(char for char in amount_str if char.isdigit() or char == '.'))

    def get_amount_unit(self, amount_str):
        return ''.join(char for char in amount_str if char.isalpha())

    def add_to_cooked_recipes(self, recipe_id):
        # Add a recipe to the 'cookedrecipes' table
        self.cursor.execute("SELECT name FROM recipes where id = ?", (int(recipe_id),))
        recipe_name = self.cursor.fetchone()[0]
        self.cursor.execute("INSERT INTO cookedrecipes (name) VALUES (?)", (recipe_name,))
        self.conn.commit()

    def get_recipe_amounts(self, recipe_id):
        self.cursor.execute("SELECT ingredients, amount FROM recipes WHERE id = ?", (int(recipe_id),))
        result = self.cursor.fetchone()
        print(result)
        if result:
            ingredients = result[0].split(' ')
            amounts = result[1].split(' ')
            return dict(zip(ingredients, amounts)) 
        return {}


    

    def get_recipe_ingredients_and_amounts(self, recipe_id):
        self.cursor.execute("SELECT ingredients, amount FROM recipes WHERE id = ?", (recipe_id,))
        result = self.cursor.fetchone()
        if result:
            ingredients = result[0].split()  # Split by whitespace
            amounts = result[1].split()  # Split by whitespace
            return list(zip(ingredients, amounts))
        return []

    def update_home_ingredients(self, recipe_id):
        recipe_ingredients = self.get_recipe_ingredients_and_amounts(recipe_id)
        for ingredient, amount in recipe_ingredients:
            self.subtract_ingredient_from_home(ingredient, amount)

    def subtract_ingredient_from_home(self, ingredient, amount):
        self.cursor.execute("SELECT amount FROM home WHERE category = ?", (ingredient,))
        result = self.cursor.fetchone()
        if result:
            home_amount = result[0]
            new_amount = self.calculate_new_amount(home_amount, amount, subtract=True)
            if new_amount[0] <= 0:
                self.cursor.execute("DELETE FROM home WHERE category = ?", (ingredient,))
            else:
                new_amount = f"{new_amount[0]}{new_amount[1]}"
                self.cursor.execute("UPDATE home SET amount = ? WHERE category = ?", (new_amount, ingredient))
            self.conn.commit()

    def calculate_new_amount(self, amount1, amount2, subtract=False):
        value1, unit1 = extract_value_and_unit(amount1)
        value2, unit2 = extract_value_and_unit(amount2)
        
        common_value1 = convert_to_common_unit(value1, unit1)
        common_value2 = convert_to_common_unit(value2, unit2)
        
        if subtract:
            new_value = common_value1 - common_value2
        else:
            new_value = common_value1 + common_value2
        
        return max(0, new_value), unit1 

    



"""

    def interactive_recipe_selection(self):
        # Get the top 5 recommended recipes
        recommendations = self.recommend_recipes()
        print("\nTop 5 recommended recipes:")
        for i, (id, name, similarity) in recommendations.iterrows():
            print(f"{i+1}. {name} (Similarity: {similarity:.2f})")
        
        # Let the user choose a recipe
        choice = int(input("\nChoose a recipe (1-5): ")) - 1
        chosen_recipe_id = recommendations.iloc[choice]['id']
        chosen_recipe_name = recommendations.iloc[choice]['name']
        print(f"\nYou chose: {chosen_recipe_name}")
        return chosen_recipe_id, chosen_recipe_name

    def interactive_ingredient_selection(self, recipe_id):
        # Clear any previously chosen ingredients
        self.clear_chosen_for_recipe()
        # Get the ingredients for the chosen recipe
        recipe_ingredients = self.get_recipe_ingredients(recipe_id)
        missing_ingredients = set()

        for ingredient in recipe_ingredients:
            # Check if we have this ingredient category at home
            home_options = self.get_home_ingredients_by_category(ingredient)
            if home_options:
                print(f"\nFor {ingredient}, you have these options at home:")
                for i, (name, price) in enumerate(home_options, 1):
                    print(f"{i}. {name} (${price:.2f})")
                print("0. Don't use any of these")
                
                choice = int(input("Choose an option: "))
                if choice != 0:
                    chosen_name, chosen_price = home_options[choice-1]
                    self.add_to_chosen_for_recipe(chosen_name, ingredient, chosen_price, True)
                    print(f"Added {chosen_name} to the recipe (from home).")
                else:
                    missing_ingredients.add(ingredient)
            else:
                missing_ingredients.add(ingredient)

        for ingredient in missing_ingredients:
            grocery_options = self.get_grocery_items_by_category(ingredient)
            if grocery_options:
                print(f"\nFor {ingredient}, you need to buy. Options:")
                for id, name, price in grocery_options:
                    print(f"{id}. {name} (${price:.2f})")
                
                choice = int(input("Choose an option by ID: "))
                chosen_item = next(item for item in grocery_options if item[0] == choice)
                self.add_to_chosen_for_recipe(chosen_item[1], ingredient, chosen_item[2], False)
                print(f"Added {chosen_item[1]} to the recipe (need to buy).")
            else:
                print(f"Warning: No options found for {ingredient}")


        # Calculate and display both prices
        total_price, to_buy_price = self.get_total_prices()
        print(f"\nTotal price for the recipe (including items at home): ${total_price:.2f}")
        print(f"Price for items you need to buy: ${to_buy_price:.2f}")

        choice = input("Would you like to make this recipe? In this case, the items you need to buy will be added to your shopping list. (yes/no): ")
        if choice.lower() == 'yes':
            # Add items to the shopping list that are not at home
            self.add_to_shopping_list()
            # Furthermore, add the recipe into the table 'cookedrecipes'
            self.add_to_cooked_recipes(recipe_id)
            
        else:
            print("No items were added to the shopping list.")
        # Clear ingredients in chosen for recipe
        self.clear_chosen_for_recipe()

    def close_connection(self):
        # Close the database connection
        self.conn.close()

if __name__ == "__main__":
    # Create a RecipeRecommender instance
    recommender = RecipeRecommender('groceries.db')
    
    # Let the user choose a recipe
    chosen_recipe_id, chosen_recipe_name = recommender.interactive_recipe_selection()
    # Let the user choose ingredients for the recipe
    recommender.interactive_ingredient_selection(chosen_recipe_id)

    # Close the database connection
    recommender.close_connection()

"""