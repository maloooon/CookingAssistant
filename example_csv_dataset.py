import pandas as pd 
import sqlite3
import csv

def load_csv_to_groceries(csv_file_path, columns_to_import):
    try:
        # Connect to the database
        conn = sqlite3.connect('groceries.db')
        cursor = conn.cursor()

        # Prepare the SQL query
        placeholders = ', '.join(['?' for _ in columns_to_import])
        columns = ', '.join(columns_to_import)
        sql = f"INSERT INTO groceries ({columns}) VALUES ({placeholders})"

        # Read the CSV file and insert data
        with open(csv_file_path, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                # Extract only the specified columns
                values = [row[column] for column in columns_to_import]
                cursor.execute(sql, values)

        # Commit the changes
        conn.commit()

        # Verify the number of rows inserted
        cursor.execute('SELECT COUNT(*) FROM groceries')
        count = cursor.fetchone()[0]
        print(f"Data loaded successfully. Total rows in groceries table: {count}")

    except sqlite3.Error as e:
        print(f"An SQLite error occurred: {e}")
    except IOError as e:
        print(f"An error occurred while reading the CSV file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Close the connection
        if conn:
            conn.close()


def load_csv_to_home(csv_file_path, columns_to_import):
    try:
        # Connect to the database
        conn = sqlite3.connect('groceries.db')
        cursor = conn.cursor()

        # Prepare the SQL query
        placeholders = ', '.join(['?' for _ in columns_to_import])
        columns = ', '.join(columns_to_import)
        sql = f"INSERT INTO home ({columns}) VALUES ({placeholders})"

        # Read the CSV file and insert data
        with open(csv_file_path, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                # Extract only the specified columns
                values = [row[column] for column in columns_to_import]
                cursor.execute(sql, values)

        # Commit the changes
        conn.commit()

        # Verify the number of rows inserted
        cursor.execute('SELECT COUNT(*) FROM home')
        count = cursor.fetchone()[0]
        print(f"Data loaded successfully. Total rows in home table: {count}")

    except sqlite3.Error as e:
        print(f"An SQLite error occurred: {e}")
    except IOError as e:
        print(f"An error occurred while reading the CSV file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Close the connection
        if conn:
            conn.close()


def load_csv_to_recipes(csv_file_path, columns_to_import):
    try:
        # Connect to the database
        conn = sqlite3.connect('groceries.db')
        cursor = conn.cursor()

        # Prepare the SQL query
        placeholders = ', '.join(['?' for _ in columns_to_import])
        columns = ', '.join(columns_to_import)
        sql = f"INSERT INTO recipes ({columns}) VALUES ({placeholders})"

        # Read the CSV file and insert data
        with open(csv_file_path, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                # Extract only the specified columns
                values = [row[column] for column in columns_to_import]
                cursor.execute(sql, values)

        # Commit the changes
        conn.commit()

        # Verify the number of rows inserted
        cursor.execute('SELECT COUNT(*) FROM recipes')
        count = cursor.fetchone()[0]
        print(f"Data loaded successfully. Total rows in recipes table: {count}")

    except sqlite3.Error as e:
        print(f"An SQLite error occurred: {e}")
    except IOError as e:
        print(f"An error occurred while reading the CSV file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Close the connection
        if conn:
            conn.close()





if __name__ == "__main__":

    csv_file_path = 'ingredients.csv'
    columns_to_import = ['name', 'price', 'category']  
    load_csv_to_groceries(csv_file_path, columns_to_import)

    csv_file_path = 'home_items.csv'
    columns_to_import = ['name', 'category']
    load_csv_to_home(csv_file_path, columns_to_import)

        
    csv_file_path = 'recipes.csv'
    columns_to_import = ['name', 'ingredients']
    load_csv_to_recipes(csv_file_path, columns_to_import)

