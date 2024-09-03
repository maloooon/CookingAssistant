import sqlite3

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
  #  cursor.execute("DROP TABLE IF EXISTS home")
  #  cursor.execute("DROP TABLE IF EXISTS grocerylist")
  #  cursor.execute("DROP TABLE IF EXISTS recipes")
   # cursor.execute("DROP TABLE IF EXISTS chosenforrecipe")
   # cursor.execute("DROP TABLE IF EXISTS shoppinglist")
  #  cursor.execute("DROP TABLE IF EXISTS cookedrecipes")


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groceries (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS home (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL

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
            ingredients TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chosenforrecipe (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            athome BOOL NOT NULL
        )
    ''')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS shoppinglist (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL
                   
        )
    ''')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS cookedrecipes (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
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
    display_all_groceries()
    display_all_home()
    
   # empty_groceries_table()
  #  drop_table('groceries', 'home')