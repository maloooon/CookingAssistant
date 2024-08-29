
import sqlite3


def search_groceries(search_term, search_type='both'):
    conn = sqlite3.connect('groceries.db')
    cursor = conn.cursor()
    
    if search_type == 'name':
        query = "SELECT * FROM groceries WHERE name LIKE ?"
        params = (f"%{search_term}%",)
    elif search_type == 'category':
        query = "SELECT * FROM groceries WHERE category LIKE ?"
        params = (f"%{search_term}%",)
    else:  # 'both'
        query = "SELECT * FROM groceries WHERE name LIKE ? OR category LIKE ?"
        params = (f"%{search_term}%", f"%{search_term}%")
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

def add_to_grocerylist(item_id):
    conn = sqlite3.connect('groceries.db')
    cursor = conn.cursor()
    
    # Get item details from groceries table
    cursor.execute("SELECT name, category, price FROM groceries WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    
    if item:
        # Add item to grocerylist table
        cursor.execute("INSERT INTO grocerylist (name, category, price) VALUES (?, ?, ?)", item)
        conn.commit()
        print(f"Added {item[0]} to your grocery list.")
    else:
        print("Item not found.")
    
    conn.close()

def view_grocerylist():
    conn = sqlite3.connect('groceries.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM grocerylist")
    items = cursor.fetchall()
    conn.close()
    
    if items:
        print("Your grocery list:")
        for item in items:
            print(f"ID: {item[0]}, Name: {item[1]}, Category: {item[2]}, Price: ${item[3]:.2f}")
    else:
        print("Your grocery list is empty.")

def calculate_total_price():
    conn = sqlite3.connect('groceries.db')
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(price) FROM grocerylist")
    total = cursor.fetchone()[0]
    conn.close()
    return total if total else 0

def clear_grocerylist():
    conn = sqlite3.connect('groceries.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM grocerylist")
    conn.commit()
    conn.close()
    print("Grocery list cleared.")

def main():
    
    while True:
        print("\n1. Search for items")
        print("2. View grocery list")
        print("3. Calculate total price")
        print("4. Clear grocery list")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == '1':
            search_term = input("Enter search term: ")
            search_type = input("Search by 'name', 'category', or 'both' (default): ")
            if search_type not in ['name', 'category']:
                search_type = 'both'
            
            results = search_groceries(search_term, search_type)
            if results:
                print("Search results:")
                for item in results:
                    print(f"ID: {item[0]}, Name: {item[1]}, Category: {item[2]}, Price: ${item[3]:.2f}")
                
                item_id = input("Enter the ID of the item to add to your list (or press Enter to skip): ")
                if item_id:
                    add_to_grocerylist(int(item_id))
            else:
                print("No results found.")
        
        elif choice == '2':
            view_grocerylist()
        
        elif choice == '3':
            total = calculate_total_price()
            print(f"Total price of items in your grocery list: ${total:.2f}")
        
        elif choice == '4':
            clear_grocerylist()
        
        elif choice == '5':
            print("Thank you for using the Grocery List Manager. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()


