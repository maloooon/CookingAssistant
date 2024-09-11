import sqlite3

def add_nutritional_info(file_path, db_path='groceries.db'):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Read and process the file
    with open(file_path, 'r') as file:
        ingredient_data = []
        current_ingredient = []

        for line in file:
            line = line.strip()
            if line:
                current_ingredient.append(line)
            else:
                if current_ingredient:
                    ingredient_data.append(current_ingredient)
                    current_ingredient = []
        
        # Add the last ingredient if file doesn't end with an empty line
        if current_ingredient:
            ingredient_data.append(current_ingredient)

    # Insert data into the database
    for ingredient in ingredient_data:
        if len(ingredient) != 9:
            print(f"Skipping ingredient due to incorrect data format: {ingredient}")
            continue

        try:
            cursor.execute('''
            INSERT OR REPLACE INTO nutrition 
            (name, category, amount, calories, fat, protein, carbs, sugar, fiber)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ingredient[0],  # name
                ingredient[1],  # category
                ingredient[2],  # amount
                float(ingredient[3]),  # calories
                float(ingredient[4][:-1]),  # fat (remove 'g')
                float(ingredient[5][:-1]),  # protein (remove 'g')
                float(ingredient[6][:-1]),  # carbs (remove 'g')
                float(ingredient[7][:-1]),  # sugar (remove 'g')
                float(ingredient[8][:-1])   # fiber (remove 'g')
            ))
            print(f"Added nutritional info for: {ingredient[0]}")
        except sqlite3.Error as e:
            print(f"Error adding {ingredient[0]}: {e}")

    # Commit changes and close connection
    conn.commit()
    conn.close()


if __name__ == "__main__":
   add_nutritional_info('nutrition_example.txt')