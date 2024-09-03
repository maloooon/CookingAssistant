import sqlite3
from collections import Counter
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_top_3_cooked_recipes(db_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Execute SQL query to get all recipe names
        cursor.execute("SELECT name FROM cookedrecipes")
        
        # Fetch all results
        recipes = cursor.fetchall()
        
        # Count occurrences of each recipe name
        recipe_counts = Counter(recipe[0] for recipe in recipes)
        
        # Sort recipes by count in descending order and get top 3
        top_3_recipes = recipe_counts.most_common(3)
        
        top_3 = []
        # Print results
        print("Top 3 most cooked recipes:")
        for i, (recipe, count) in enumerate(top_3_recipes, 1):
            print(f"{i}. {recipe}: cooked {count} time{'s' if count > 1 else ''}")
            top_3.append(recipe)

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Close the database connection
        conn.close()
    
    return top_3



class RecipeSimilarityCalculator:
    # Calculating the similarity between recipes based on ingredients
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.recipes_df = None
        self.tfidf_matrix = None
        self.vectorizer = None

    def load_recipes(self):
        query = "SELECT name, ingredients FROM recipes"
        self.recipes_df = pd.read_sql_query(query, self.conn)
        self.recipes_df['ingredients'] = self.recipes_df['ingredients'].fillna('')

    def vectorize_ingredients(self):
        self.vectorizer = TfidfVectorizer(token_pattern=r'\b\w+\b')
        self.tfidf_matrix = self.vectorizer.fit_transform(self.recipes_df['ingredients'])

    def get_recipe_similarity(self, recipe_name, top_n=5):
        if self.recipes_df is None or self.tfidf_matrix is None:
            self.load_recipes()
            self.vectorize_ingredients()

        if recipe_name not in self.recipes_df['name'].values:
            print(f"Recipe '{recipe_name}' not found in the database.")
            return []

        recipe_index = self.recipes_df[self.recipes_df['name'] == recipe_name].index[0]
        recipe_vector = self.tfidf_matrix[recipe_index]

        cosine_similarities = cosine_similarity(recipe_vector, self.tfidf_matrix).flatten()
        similar_indices = cosine_similarities.argsort()[::-1][1:top_n+1]  # Exclude the recipe itself

        similar_recipes = []
        for index in similar_indices:
            similar_recipe = self.recipes_df.iloc[index]
            similarity_score = cosine_similarities[index]
            similar_recipes.append({
                'name': similar_recipe['name'],
                'similarity': similarity_score,
                'ingredients': similar_recipe['ingredients']
            })

        return similar_recipes

    def close_connection(self):
        self.conn.close()

def print_similar_recipes(similar_recipes):
    print("\nSimilar Recipes:")
    for i, recipe in enumerate(similar_recipes, 1):
        print(f"{i}. {recipe['name']}")
        print(f"   Similarity: {recipe['similarity']:.4f}")
        print(f"   Ingredients: {recipe['ingredients']}")
        print()



if __name__ == "__main__":
    db_path = 'groceries.db' 
    top_3 = get_top_3_cooked_recipes(db_path)
    calculator = RecipeSimilarityCalculator(db_path)

    try:
        recipe_name = top_3[0]
        print("For your most favourite recipe, {}, I can recommend similar recipes based on ingredients.".format(recipe_name))
        similar_recipes = calculator.get_recipe_similarity(recipe_name)
        print_similar_recipes(similar_recipes)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        calculator.close_connection()

    