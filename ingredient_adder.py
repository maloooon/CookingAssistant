import sqlite3

# Adding ingredients either to the list of possible ingredients to buy or to the list of ingredients at home 
# TODO : import idea into contents interface 


def add_ingredient(ingredient_name, category, price, amount, to_home):
    """
    Adds an ingredient to the database 'groceries.db', in particular to either
    the table 'home' or 'groceries'. If to_home is True, the ingredient is added to the table 'home'.
    Both tables have the same structure : the columns are 
    'name' (ingredient_name),
    'category' (category),
    'price' (price),
    'amount' (amount).
    """
    conn = sqlite3.connect('groceries.db')
    c = conn.cursor()

    if to_home == False: 
        c.execute("SELECT name FROM groceries WHERE name = ?", (ingredient_name,))
        if c.fetchone() is not None:
            print(f"Ingredient '{ingredient_name}' is already in the database.")
            conn.close()
            return

    table = 'home' if to_home else 'groceries'
    c.execute(f"INSERT INTO {table} (name, category, price, amount) VALUES (?, ?, ?, ?)", 
              (ingredient_name, category, price, amount))

    conn.commit()
    conn.close()

    print(f"Added '{ingredient_name}' to the {table} table.")

def read_ingredients_file(filename):
    """
    Reads ingredients from a file and adds them to the database.
    The file should have the following format:
    First line: TRUE or FALSE (indicating whether ingredients are at home)
    Subsequent lines: ingredient_name, category, price, amount
    """
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    if not lines:
        print("The file is empty.")
        return

    at_home = lines[0].strip().upper() == 'TRUE'

    for line in lines[1:]:
        parts = line.strip().split(',')
        if len(parts) != 4:
            print(f"Skipping invalid line: {line.strip()}") # means a column is missing 
            continue

        name, category, price, amount = parts
        try:
            price = float(price)
            amount = amount.strip()  # Keep amount as string to preserve units
            add_ingredient(name.strip(), category.strip(), price, amount, at_home)
        except ValueError:
            print(f"Skipping line due to invalid price: {line.strip()}")

def main():
    filename = 'all_ingredients_despar.txt'  # You can change this to accept user input
    read_ingredients_file(filename)

if __name__ == "__main__":
    main()