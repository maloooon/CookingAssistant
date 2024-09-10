import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QListWidget, QMessageBox, QDialog, QRadioButton, QButtonGroup, QScrollArea, QGroupBox, 
                             QTableWidget, QTableWidgetItem, QLineEdit, QListView)
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from recommender import RecipeRecommender  
from amount_comparison import compare_amounts, extract_value_and_unit, convert_to_common_unit, is_enough_ingredient

class RecipeRecommenderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.recommender = RecipeRecommender('groceries.db')
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Recipe Recommender')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Recommendation section
        recommendation_layout = QVBoxLayout()
        self.recommendation_list = QListWidget()
        
        recommendation_layout.addWidget(self.recommendation_list)

        recommend_button = QPushButton('Get Recommendations based on Ingredients at Home')
        recommend_button.clicked.connect(self.show_recommendations)
        recommendation_layout.addWidget(recommend_button)

        select_button = QPushButton('Select Recipe')
        select_button.clicked.connect(self.select_recipe)
        recommendation_layout.addWidget(select_button)

        main_layout.addLayout(recommendation_layout)

        # Additional buttons
        button_layout = QHBoxLayout()

        show_home_button = QPushButton("Show What's at Home")
        show_home_button.clicked.connect(self.show_home_ingredients)
        button_layout.addWidget(show_home_button)

        show_shopping_list_button = QPushButton('Show Shopping List')
        show_shopping_list_button.clicked.connect(self.show_shopping_list)
        button_layout.addWidget(show_shopping_list_button)

        exit_button = QPushButton('Exit')
        exit_button.clicked.connect(self.close)
        button_layout.addWidget(exit_button)

        main_layout.addLayout(button_layout)

        cooking_button = QPushButton('Cooking...')
        cooking_button.clicked.connect(self.open_cooking_dialog)
        button_layout.addWidget(cooking_button)

    def show_recommendations(self):
        recommendations = self.recommender.recommend_recipes()
        self.recommendation_list.clear()
        for _, row in recommendations.iterrows():
            self.recommendation_list.addItem(f"{row['name']} (Similarity: {row['similarity']:.2f})")

    def select_recipe(self):
        selected_items = self.recommendation_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Warning', 'Please select a recipe first.')
            return

        selected_recipe = selected_items[0].text().split(' (')[0]  # Extract recipe name
        recipe_df = self.recommender.prepare_recipe_data()
        recipe_id = recipe_df[recipe_df['name'] == selected_recipe]['id'].values[0]
        
        ingredient_dialog = IngredientSelectionDialog(self.recommender, recipe_id)
        ingredient_dialog.exec_()

    def show_home_ingredients(self):
        self.recommender.cursor.execute("SELECT name, category, amount FROM home")
        home_ingredients = self.recommender.cursor.fetchall()

        dialog = QDialog(self)
        dialog.setWindowTitle("Ingredients at Home")
        dialog.setGeometry(150, 150, 500, 400)

        layout = QVBoxLayout(dialog)
        
        table = QTableWidget()
        table.setColumnCount(3)  
        table.setHorizontalHeaderLabels(["Name", "Category", "Amount"])
        table.setRowCount(len(home_ingredients))

        for row, (name, category, amount) in enumerate(home_ingredients):
            table.setItem(row, 0, QTableWidgetItem(name))
            table.setItem(row, 1, QTableWidgetItem(category))
            table.setItem(row, 2, QTableWidgetItem(str(amount)))  

        table.resizeColumnsToContents()
        layout.addWidget(table)

        # Add total count label
        total_count = len(home_ingredients)
        total_label = QLabel(f"Total Ingredients: {total_count}")
        total_label.setAlignment(Qt.AlignRight)
        total_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        layout.addWidget(total_label)

        dialog.exec_()


    def open_cooking_dialog(self):
        dialog = CookingDialog(self.recommender)
        dialog.exec_()

    def show_shopping_list(self):
        dialog = ShoppingListDialog(self.recommender)
        dialog.exec_()

"""
    def show_shopping_list(self):
        self.recommender.cursor.execute("SELECT name, category, price, amount, quantity FROM shoppinglist")
        shopping_list = self.recommender.cursor.fetchall()

        dialog = QDialog(self)
        dialog.setWindowTitle("Shopping List")
        dialog.setGeometry(150, 150, 600, 400)

        layout = QVBoxLayout(dialog)
        
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Name", "Category", "Price", "Amount", "Quantity"])
        table.setRowCount(len(shopping_list))

        total_price = 0
        for row, (name, category, price, amount, quantity) in enumerate(shopping_list):
            table.setItem(row, 0, QTableWidgetItem(name))
            table.setItem(row, 1, QTableWidgetItem(category))
            
            price_item = QTableWidgetItem(f"${price:.2f}")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 2, price_item)
            
            table.setItem(row, 3, QTableWidgetItem(amount))
            
            quantity_item = QTableWidgetItem(f"{quantity:.2f}")
            quantity_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 4, quantity_item)

            total_price += price

        table.resizeColumnsToContents()
        layout.addWidget(table)

        total_label = QLabel(f"Total Price: ${total_price:.2f}")
        total_label.setAlignment(Qt.AlignRight)
        total_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        layout.addWidget(total_label)

        dialog.exec_()

    def get_amount_value(self, amount_str):
        # Remove all non-numeric characters except the decimal point
        numeric_string = ''.join(char for char in amount_str if char.isdigit() or char == '.')
        
        # Handle cases where there might be multiple decimal points
        parts = numeric_string.split('.')
        if len(parts) > 2:
            # If there are multiple decimal points, join all parts after the first
            numeric_string = parts[0] + '.' + ''.join(parts[1:])
        
        try:
            return float(numeric_string)
        except ValueError:
            print(f"Warning: Could not convert '{amount_str}' to a numeric value.")
            return 0.0
"""

"""
    def confirm_selection(self):
        recipe_ingredients = self.recommender.get_recipe_ingredients(self.recipe_id)
        missing_ingredients = set(recipe_ingredients) - set(self.chosen_ingredients.keys())
        
        for ingredient in missing_ingredients:
            if not is_enough_ingredient(self.home_amounts[ingredient], self.recipe_amounts[ingredient]):
                reply = QMessageBox.question(self, 'Insufficient Ingredient',
                                             f"You don't have enough {ingredient} at home. Do you want to choose an alternative?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.Yes:
                    return  # Go back to selection
"""


class ShoppingListDialog(QDialog):
    def __init__(self, recommender):
        super().__init__()
        self.recommender = recommender
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Shopping List")
        self.setGeometry(150, 150, 800, 600)

        layout = QVBoxLayout(self)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for groceries...")
        self.search_bar.textChanged.connect(self.update_search_results)
        search_layout.addWidget(self.search_bar)

        add_button = QPushButton("Add to List")
        add_button.clicked.connect(self.add_selected_grocery)
        search_layout.addWidget(add_button)

        layout.addLayout(search_layout)

        # List view for search results
        self.list_view = QListView()
        self.model = QStandardItemModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.list_view.setModel(self.proxy_model)
        layout.addWidget(self.list_view)

        # Shopping list table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Name", "Category", "Price", "Amount", "Quantity", "Actions"])
        layout.addWidget(self.table)

        # Total price label
        self.total_label = QLabel()
        self.total_label.setAlignment(Qt.AlignRight)
        self.total_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        layout.addWidget(self.total_label)

        self.populate_groceries()
        self.load_shopping_list()

    def populate_groceries(self):
        self.recommender.cursor.execute("SELECT name FROM groceries")
        groceries = self.recommender.cursor.fetchall()
        for grocery in groceries:
            item = QStandardItem(grocery[0])
            self.model.appendRow(item)

    def update_search_results(self, text):
        self.proxy_model.setFilterRegExp(f"\\b{text}")

    def add_selected_grocery(self):
        selected_indexes = self.list_view.selectedIndexes()
        if selected_indexes:
            grocery_name = self.proxy_model.data(selected_indexes[0])
            self.recommender.cursor.execute("SELECT name, category, price, amount FROM groceries WHERE name = ?", (grocery_name,))
            grocery_data = self.recommender.cursor.fetchone()
            if grocery_data:
                self.recommender.add_to_shopping_list(grocery_data[0], grocery_data[1], grocery_data[2], grocery_data[3], 1)
                self.load_shopping_list()

    def load_shopping_list(self):
        self.recommender.cursor.execute("SELECT name, category, price, amount, quantity FROM shoppinglist")
        shopping_list = self.recommender.cursor.fetchall()

        self.table.setRowCount(len(shopping_list))
        total_price = 0

        for row, (name, category, price, amount, quantity) in enumerate(shopping_list):
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(category))
            self.table.setItem(row, 2, QTableWidgetItem(f"${price:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(amount))
            self.table.setItem(row, 4, QTableWidgetItem(f"{quantity:.1f}"))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)  # Remove layout margins
            actions_layout.setSpacing(2)  # Reduce space between buttons

            minus_button = QPushButton("-")
            minus_button.setFixedSize(30, 30)  # Set a fixed size for the buttons
            minus_button.clicked.connect(lambda _, n=name: self.update_quantity(n, -1))
            
            plus_button = QPushButton("+")
            plus_button.setFixedSize(30, 30)  # Set a fixed size for the buttons
            plus_button.clicked.connect(lambda _, n=name: self.update_quantity(n, 1))
            
            actions_layout.addWidget(minus_button)
            actions_layout.addWidget(plus_button)
            actions_layout.addStretch()  # Add stretch to push buttons to the left

            self.table.setCellWidget(row, 5, actions_widget)

            total_price += price * quantity

        # Adjust column widths
        self.table.setColumnWidth(0, 200)  # Name
        self.table.setColumnWidth(1, 100)  # Category
        self.table.setColumnWidth(2, 80)   # Price
        self.table.setColumnWidth(3, 80)   # Amount
        self.table.setColumnWidth(4, 80)   # Quantity
        self.table.setColumnWidth(5, 100)  # Actions

        self.table.resizeRowsToContents()
        self.total_label.setText(f"Total Price: ${total_price:.2f}")

    def update_quantity(self, name, change):
        self.recommender.cursor.execute("SELECT quantity, price, amount FROM shoppinglist WHERE name = ?", (name,))
        current_data = self.recommender.cursor.fetchone()
        if current_data:
            current_quantity, current_price, current_amount = current_data
            new_quantity = max(0, current_quantity + change)

            if new_quantity == 0:
                self.recommender.cursor.execute("DELETE FROM shoppinglist WHERE name = ?", (name,))
            else:
                # Get original price and amount from groceries table
                self.recommender.cursor.execute("SELECT price, amount FROM groceries WHERE name = ?", (name,))
                original_data = self.recommender.cursor.fetchone()
                if original_data:
                    original_price, original_amount = original_data
                    new_price = (new_quantity / current_quantity) * current_price
                    new_amount = f"{self.get_amount_value(current_amount) * (new_quantity / current_quantity)}{self.get_amount_unit(current_amount)}"

                    self.recommender.cursor.execute("""
                        UPDATE shoppinglist 
                        SET quantity = ?, price = ?, amount = ? 
                        WHERE name = ?
                    """, (new_quantity, new_price, new_amount, name))

            self.recommender.conn.commit()
            self.load_shopping_list()

    def get_amount_value(self, amount_str):
        return float(''.join(char for char in amount_str if char.isdigit() or char == '.'))

    def get_amount_unit(self, amount_str):
        return ''.join(char for char in amount_str if char.isalpha())          


class CookingDialog(QDialog):
    def __init__(self, recommender):
        super().__init__()
        self.recommender = recommender
        self.initUI()

    def initUI(self):
        self.setWindowTitle('What did you cook?')
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout(self)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for recipes...")
        self.search_bar.textChanged.connect(self.update_search_results)
        layout.addWidget(self.search_bar)

        # List view for search results
        self.list_view = QListView()
        self.model = QStandardItemModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.list_view.setModel(self.proxy_model)
        layout.addWidget(self.list_view)

        # Populate the model with all recipes
        self.populate_recipes()

        # Select button
        select_button = QPushButton('Select Recipe')
        select_button.clicked.connect(self.select_recipe)
        layout.addWidget(select_button)

    def populate_recipes(self):
        recipes = self.recommender.get_recipes()
        for recipe in recipes:
            item = QStandardItem(recipe[1])  # Assuming recipe[1] is the name
            item.setData(recipe[0], Qt.UserRole)  # Store the recipe ID
            self.model.appendRow(item)

    def update_search_results(self, text):
        self.proxy_model.setFilterRegExp(f"\\b{text}")

    def select_recipe(self):
        selected_indexes = self.list_view.selectedIndexes()
        if selected_indexes:
            proxy_index = selected_indexes[0]
            source_index = self.proxy_model.mapToSource(proxy_index)
            selected_item = self.model.itemFromIndex(source_index)
            
            recipe_name = selected_item.text()
            recipe_id = selected_item.data(Qt.UserRole)
            
            reply = QMessageBox.question(self, 'Confirm Cooking', 
                                         f"Did you cook {recipe_name}?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.recommender.add_to_cooked_recipes(recipe_id)
                self.recommender.update_home_ingredients(recipe_id)
                QMessageBox.information(self, 'Success', f'{recipe_name} has been added to your cooked recipes and home ingredients have been updated.')
                self.accept()
            else:
                QMessageBox.information(self, 'Cancelled', 'No recipe was added to cooked recipes.')
        else:
            QMessageBox.warning(self, 'No Selection', 'Please select a recipe first.')




class IngredientSelectionDialog(QDialog):
    def __init__(self, recommender, recipe_id):
        super().__init__()
        self.recommender = recommender
        self.recipe_id = recipe_id
        self.chosen_ingredients = {}
        self.recipe_amounts = {}
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Select Ingredients')
        self.setGeometry(150, 150, 800, 600)

        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        confirm_button = QPushButton('Confirm Selection')
        confirm_button.clicked.connect(self.confirm_selection)
        layout.addWidget(confirm_button)

        recipe_ingredients = self.recommender.get_recipe_ingredients(self.recipe_id)
        self.recipe_amounts = self.recommender.get_recipe_amounts(self.recipe_id)

        for ingredient in recipe_ingredients:
            group_box = QGroupBox(ingredient)
            group_layout = QVBoxLayout()

            recipe_amount = self.recipe_amounts.get(ingredient, "0g")
            amount_label = QLabel(f"Needed: {recipe_amount}")
            group_layout.addWidget(amount_label)

            # Add "Choose nothing" option
            nothing_radio = QRadioButton("Choose nothing")
            nothing_radio.toggled.connect(lambda checked, ing=ingredient: 
                                          self.on_nothing_selected(checked, ing))
            group_layout.addWidget(nothing_radio)

            # Add "At Home" options
            home_options = self.recommender.get_home_ingredients_by_category(ingredient)
            if home_options:
                for name, price, amount in home_options:
                    radio = QRadioButton(f"{name} (${price:.2f}) (Available : {amount}) - At Home")
                    radio.toggled.connect(lambda checked, n=name, p=price, a=amount, ing=ingredient: 
                                          self.on_home_ingredient_selected(checked, ing, n, p, a))
                    group_layout.addWidget(radio)

            # Add "Need to Buy" options
            grocery_options = self.recommender.get_grocery_items_by_category(ingredient)
            for id, name, price, amount in grocery_options:
                h_layout = QHBoxLayout()
                label = QLabel(f"{name} (${price:.2f}) (Amount: {amount}) - Need to Buy")
                h_layout.addWidget(label)
                
                minus_button = QPushButton("-")
                minus_button.setFixedSize(30, 30)
                minus_button.clicked.connect(lambda _, ing=ingredient, n=name, p=price, a=amount:
                                             self.update_quantity(ing, n, p, a, -1))
                h_layout.addWidget(minus_button)
                
                quantity_label = QLabel("0")
                quantity_label.setAlignment(Qt.AlignCenter)
                quantity_label.setFixedSize(30, 30)
                h_layout.addWidget(quantity_label)
                
                plus_button = QPushButton("+")
                plus_button.setFixedSize(30, 30)
                plus_button.clicked.connect(lambda _, ing=ingredient, n=name, p=price, a=amount:
                                            self.update_quantity(ing, n, p, a, 1))
                h_layout.addWidget(plus_button)
                
                group_layout.addLayout(h_layout)
                
                if ingredient not in self.chosen_ingredients:
                    self.chosen_ingredients[ingredient] = {}
                self.chosen_ingredients[ingredient][name] = {
                    'quantity_label': quantity_label,
                    'minus_button': minus_button,
                    'plus_button': plus_button,
                    'quantity': 0
                }

            # Add total selected amount label
            total_label = QLabel(f"Selected: 0{recipe_amount[-1]} / {recipe_amount}")
            group_layout.addWidget(total_label)
            self.chosen_ingredients[ingredient]['total_label'] = total_label

            group_box.setLayout(group_layout)
            scroll_layout.addWidget(group_box)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        confirm_button = QPushButton('Confirm Selection')
        confirm_button.clicked.connect(self.confirm_selection)
        layout.addWidget(confirm_button)

    def on_nothing_selected(self, checked, ingredient):
        if checked:
            # Reset all selections for this ingredient
            for item_data in self.chosen_ingredients[ingredient].values():
                if isinstance(item_data, dict) and 'quantity_label' in item_data:
                    item_data['quantity'] = 0
                    item_data['quantity_label'].setText("0")
            if 'selected' in self.chosen_ingredients[ingredient]:
                del self.chosen_ingredients[ingredient]['selected']
            self.update_total_amount(ingredient)

    def on_home_ingredient_selected(self, checked, ingredient, name, price, amount):
        if checked:
            self.chosen_ingredients[ingredient]['selected'] = (name, price, amount, True)
        else:
            if 'selected' in self.chosen_ingredients[ingredient]:
                del self.chosen_ingredients[ingredient]['selected']
        self.update_total_amount(ingredient)

    def update_quantity(self, ingredient, name, price, amount, change):
        item_data = self.chosen_ingredients[ingredient][name]
        new_quantity = item_data['quantity'] + change
        if new_quantity >= 0:
            item_data['quantity'] = new_quantity
            item_data['quantity_label'].setText(str(new_quantity))
            self.update_total_amount(ingredient)

    def update_total_amount(self, ingredient):
        total_amount = 0
        recipe_amount = self.recipe_amounts.get(ingredient, "0g")
        recipe_amount_parsed = self.parse_amount(recipe_amount)
        recipe_amount_value = self.get_amount_value(recipe_amount)

        # Calculate amount from "At Home" selection
        if 'selected' in self.chosen_ingredients[ingredient]:
            name, price, amount, is_home = self.chosen_ingredients[ingredient]['selected']
            if is_home:
                total_amount += self.get_amount_value(amount)

        # Calculate amount from "Need to Buy" selections
        for name, item_data in self.chosen_ingredients[ingredient].items():
            if isinstance(item_data, dict) and 'quantity' in item_data:
                quantity = item_data['quantity']
                amount = self.recommender.get_grocery_item_amount(name)
                total_amount += quantity * self.get_amount_value(amount)

        total_label = self.chosen_ingredients[ingredient]['total_label']
        total_label.setText(f"Selected: {total_amount}{recipe_amount_parsed.split()[1]} / {recipe_amount_parsed}")

        # Update color based on whether enough has been selected
        if total_amount >= recipe_amount_value:
            total_label.setStyleSheet("color: green;")
        else:
            total_label.setStyleSheet("color: red;")

    def parse_amount(self, amount_str):
        # Convert amount string to a consistent format with a space before the unit
        units = ['kg', 'g', 'ml', 'l', 'piece']
        for unit in units:
            if amount_str.endswith(unit):
                number = amount_str[:-len(unit)]
                return f"{number} {unit}"
        return amount_str  # Return as is if no known unit is found

    def get_amount_value(self, amount_str):
        parsed = self.parse_amount(amount_str)
        value, unit = parsed.split()
        return float(value)


    def confirm_selection(self):
        missing_ingredients = []
        selected_ingredients = []

        for ingredient, data in self.chosen_ingredients.items():
            total_amount = 0
            recipe_amount = self.recipe_amounts.get(ingredient, "0g")
            recipe_amount_value = self.get_amount_value(recipe_amount)

            # Check "At Home" selection
            if 'selected' in data and data['selected'][3]:  # is_home
                name, price, amount, _ = data['selected']
                total_amount += self.get_amount_value(amount)
                selected_ingredients.append((ingredient, name, price, amount, True))

            # Check "Need to Buy" selections
            for name, item_data in data.items():
                if isinstance(item_data, dict) and 'quantity' in item_data:
                    quantity = item_data['quantity']
                    if quantity > 0:
                        amount = self.recommender.get_grocery_item_amount(name)
                        price = self.recommender.get_grocery_item_price(name)
                        amount_value = self.get_amount_value(amount)
                        total_amount += quantity * amount_value
                        new_amount = f"{quantity * amount_value}{amount[-1]}"
                        new_price = price * quantity
                        selected_ingredients.append((ingredient, name, new_price, new_amount, False))

            if total_amount < recipe_amount_value:
                missing_ingredients.append(ingredient)

        if missing_ingredients:
            message = "You haven't selected enough of the following ingredients:\n"
            message += ", ".join(missing_ingredients)
            message += "\n\nDo you want to continue anyway?"
            reply = QMessageBox.question(self, 'Confirm Selection', message, 
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        for ingredient, name, price, amount, is_home in selected_ingredients:
            self.recommender.add_to_chosen_for_recipe(name, ingredient, price, is_home, amount)

        _, to_buy_price = self.recommender.get_total_prices() # TODO : _ can be removed
        message = (
                   f"Price for items you need to buy: ${to_buy_price:.2f}\n\n"
                   "Would you like to make this recipe? "
                   "If yes, items you need to buy will be added to your shopping list.")
        reply = QMessageBox.question(self, 'Confirm Recipe', message, 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.recommender.add_to_shopping_list()
            QMessageBox.information(self, 'Success', 'Items added to shopping list.')
            self.accept()  # Close the dialog
        else:
            QMessageBox.information(self, 'Cancelled', 'No items were added to the shopping list.')

        self.recommender.clear_chosen_for_recipe()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RecipeRecommenderGUI()
    ex.show()
    sys.exit(app.exec_())