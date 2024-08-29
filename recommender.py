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
        # Create a space-separated string of home ingredient names
        home_ingredients_string = ' '.join([name for name, _ in home_ingredients])

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
        
        # Return the names and similarity scores of the top N recipes
        return recommended_recipes[['name', 'similarity']]

    def calculate_recipe_cost(self, recipe_id):
        # Fetch ingredients for the given recipe
        self.cursor.execute("SELECT ingredients FROM recipes WHERE id = ?", (recipe_id,))
        ingredients = self.cursor.fetchone()[0].split()
        
        total_cost = 0
        for ingredient in ingredients:
            # Look up the price of each ingredient
            self.cursor.execute("SELECT price FROM groceries WHERE name = ?", (ingredient,))
            result = self.cursor.fetchone()
            if result:
                price = result[0]
                total_cost += price
            else:
                print(f"Warning: Price not found for ingredient '{ingredient}'")
        
        return total_cost

    def get_missing_ingredients(self, recipe_id):
        # Fetch ingredients for the given recipe
        self.cursor.execute("SELECT ingredients FROM recipes WHERE id = ?", (recipe_id,))
        recipe_ingredients = set(self.cursor.fetchone()[0].split())
        
        # Fetch ingredients available at home
        self.cursor.execute("SELECT name FROM home")
        home_ingredients = set(row[0] for row in self.cursor.fetchall())
        
        # Find ingredients in the recipe that are not available at home
        missing_ingredients = recipe_ingredients - home_ingredients
        
        missing_info = []
        for ingredient in missing_ingredients:
            # Look up the price of each missing ingredient
            self.cursor.execute("SELECT name, price FROM groceries WHERE name = ?", (ingredient,))
            result = self.cursor.fetchone()
            if result:
                name, price = result
                missing_info.append((name, price))
            else:
                print(f"Warning: Info not found for ingredient '{ingredient}'")
        
        return missing_info

    def close_connection(self):
        # Close the database connection when done
        self.conn.close()

# Usage example
if __name__ == "__main__":
    # Create a RecipeRecommender instance
    recommender = RecipeRecommender('groceries.db')
    
    print("Top 5 recommended recipes based on ingredients at home:")
    # Get recipe recommendations
    recommendations = recommender.recommend_recipes()
    print(recommendations)

    # Get the ID of the top recommended recipe
    top_recipe_id = recommender.get_recipes()[recommendations.index[0]][0]
    
    # Calculate the cost of the top recommended recipe
    cost = recommender.calculate_recipe_cost(top_recipe_id)
    
    # Get missing ingredients for the top recommended recipe
    missing = recommender.get_missing_ingredients(top_recipe_id)

    print(f"\nCost of the top recommended recipe: ${cost:.2f}")
    print("Missing ingredients:")
    for ingredient, price in missing:
        print(f"- {ingredient}: ${price:.2f}")

    # Close the database connection
    recommender.close_connection()