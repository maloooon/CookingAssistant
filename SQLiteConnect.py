import sqlite3


def add_column_to_table(database_name, table_name, column_name, column_type):
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    try:
        # SQL command to add a new column
        sql_command = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        
        # Execute the SQL command
        cursor.execute(sql_command)
        
        # Commit the changes
        conn.commit()
        print(f"Column '{column_name}' added successfully to table '{table_name}'")
    
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Close the connection
        conn.close()

def create_groceries_database():
    # Connect to the database (creates it if it doesn't exist)
    conn = sqlite3.connect('groceries.db')
    cursor = conn.cursor()

    # Create the groceries table

    # id: Primary key, auto-incremented
    # name: Name of the grocery item
    # category: Category of the grocery item
    # price: Price of the grocery item

    # Drop existing tables
  #  cursor.execute("DROP TABLE IF EXISTS groceries")
   # cursor.execute("DROP TABLE IF EXISTS home")
   # cursor.execute("DROP TABLE IF EXISTS grocerylist")
    cursor.execute("DROP TABLE IF EXISTS recipes")
  #  cursor.execute("DROP TABLE IF EXISTS chosenforrecipe")
  #  cursor.execute("DROP TABLE IF EXISTS shoppinglist")
   # cursor.execute("DROP TABLE IF EXISTS cookedrecipes")
   # cursor.execute("DROP TABLE IF EXISTS nutrition")


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nutrition (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            amount TEXT NOT NULL,
            calories REAL NOT NULL,
            fat REAL NOT NULL,
            protein REAL NOT NULL,
            carbs REAL NOT NULL,
            sugar REAL NOT NULL,
            fiber REAL NOT NULL
            )      
        ''')


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groceries (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            amount TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS home (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            amount TEXT NOT NULL

        )
    ''')


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grocerylist (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            original_ingredients TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            amount TEXT NOT NULL,
            servings REAL NOT NULL,
            link TEXT NOT NULL,
            nutrition_values TEXT 
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chosenforrecipe (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            athome BOOL NOT NULL,
            amount TEXT NOT NULL
        )
    ''')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS shoppinglist (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                amount TEXT NOT NULL,
                quantity REAL NOT NULL
                   
        )
    ''')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS cookedrecipes (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                quantity REAL NOT NULL
         )
    ''')



    # Commit changes and close connection
    conn.commit()
    conn.close()

    print("Database created successfully")


def drop_table(database_name, table_name):
    try:
        # Connect to the database
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()

        # SQL command to drop the table
        drop_table_sql = f"DROP TABLE IF EXISTS {table_name}"

        # Execute the SQL command
        cursor.execute(drop_table_sql)

        # Commit the changes
        conn.commit()

        print(f"Table '{table_name}' has been successfully dropped from '{database_name}'.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connection
        if conn:
            conn.close()



def insert_sample_data():
    conn = sqlite3.connect('groceries.db')
    cursor = conn.cursor()

    # Sample grocery items
    groceries = [
        ('Apple', 'Fruit'),
        ('Bread', 'Bakery'),
        ('Milk', 'Dairy'),
        ('Chicken', 'Meat'),
        ('Carrot', 'Vegetable')
    ]

    # Insert sample data
    cursor.executemany('INSERT INTO home (name, category) VALUES (?, ?)', groceries)

    conn.commit()
    conn.close()

    print("Sample data inserted successfully.")

def display_all_groceries():
    conn = sqlite3.connect('groceries.db')
    cursor = conn.cursor()

    # Query and display all groceries
    cursor.execute('SELECT * FROM groceries')
    groceries = cursor.fetchall()

    print("\nAll Groceries:")
    for grocery in groceries:
        print(f"ID: {grocery[0]}, Name: {grocery[1]}, Category: {grocery[2]}, Price: ${grocery[3]:.2f}")

    conn.close()

def display_all_home():
    conn = sqlite3.connect('groceries.db')
    cursor = conn.cursor()

    # Query and display all groceries
    cursor.execute('SELECT * FROM home')
    groceries = cursor.fetchall()

    print("\nAll Items at Home:")
    for grocery in groceries:
        print(f"ID: {grocery[0]}, Name: {grocery[1]}, Category: {grocery[2]}")

    conn.close()

def display_all_recipes():
    conn = sqlite3.connect('groceries.db')
    cursor = conn.cursor()

    # Query and display all groceries
    cursor.execute('SELECT * FROM recipes')
    groceries = cursor.fetchall()

    print("\nAll Recipes:")
    for grocery in groceries:
        print(f"ID: {grocery[0]}, Name: {grocery[1]}, Ingredients: {grocery[2]}")

    conn.close()



def empty_groceries_table():
    try:
        # Connect to the database
        conn = sqlite3.connect('groceries.db')
        cursor = conn.cursor()

        # Delete all rows from the groceries table
        cursor.execute('DELETE FROM groceries')

        # Try to reset the auto-incrementing primary key if sqlite_sequence exists
        try:
            cursor.execute('DELETE FROM sqlite_sequence WHERE name="groceries"')
        except sqlite3.OperationalError:
            # If sqlite_sequence doesn't exist, we can ignore this step
            pass

        # Commit the changes
        conn.commit()

        # Verify that the table is empty
        cursor.execute('SELECT COUNT(*) FROM groceries')
        count = cursor.fetchone()[0]

        print(f"All data has been deleted from the groceries table. Current row count: {count}")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connection
        if conn:
            conn.close()

if __name__ == "__main__":
    create_groceries_database()
   # insert_sample_data()
  #  display_all_groceries()
  #  display_all_home()
    
   # empty_groceries_table()
  #  drop_table('groceries', 'home')
  #  add_column_to_table('groceries.db', 'recipes', 'nutrition_values', 'TEXT')




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