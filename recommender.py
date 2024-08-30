"""Easy recommendation system based on cosine similarity between ingredients"""

import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

    def get_recipe_ingredients(self, recipe_id):
        # Fetch ingredients for a specific recipe
        self.cursor.execute("SELECT ingredients FROM recipes WHERE id = ?", (int(recipe_id),))
        return set(self.cursor.fetchone()[0].split())
    
    def get_home_ingredients_by_category(self, category):
        # Fetch all home ingredients of a specific category
        self.cursor.execute("SELECT name, price FROM home WHERE category = ?", (category,))
        return self.cursor.fetchall()

    def get_grocery_items_by_category(self, category):
        # Fetch all grocery items of a specific category
        self.cursor.execute("SELECT id, name, price FROM groceries WHERE category = ?", (category,))
        return self.cursor.fetchall()

    def add_to_chosen_for_recipe(self, name, category, price, athome):
        # Add a chosen ingredient to the 'chosenforrecipe' table
        self.cursor.execute("""
            INSERT INTO chosenforrecipe (name, category, price, athome)
            VALUES (?, ?, ?, ?)
        """, (name, category, price, athome))
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