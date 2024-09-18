import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QListWidget, QMessageBox, QDialog, QRadioButton, QButtonGroup, QScrollArea, QGroupBox, 
                             QTableWidget, QTableWidgetItem, QLineEdit, QListView, QTextEdit, QHBoxLayout, QPushButton, QSpinBox, QComboBox)
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QUrl
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QDesktopServices

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

        select_by_ingredient_button = QPushButton('Select by Ingredient')
        select_by_ingredient_button.clicked.connect(self.open_select_by_ingredient)
        button_layout.addWidget(select_by_ingredient_button)

        cooking_button = QPushButton('Cooking...')
        cooking_button.clicked.connect(self.open_cooking_dialog)
        button_layout.addWidget(cooking_button)

        exit_button = QPushButton('Exit')
        exit_button.clicked.connect(self.close)
        button_layout.addWidget(exit_button)

        main_layout.addLayout(button_layout)


    def open_select_by_ingredient(self):
        dialog = SelectByIngredientDialog(self.recommender)
        dialog.exec_()


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



class SelectByIngredientDialog(QDialog):
    def __init__(self, recommender):
        super().__init__()
        self.recommender = recommender
        self.selected_ingredients = {}  
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Select Recipes by Ingredient')
        self.setGeometry(100, 100, 800, 600)

        layout = QHBoxLayout()

        # Left side (search and ingredient selection)
        left_layout = QVBoxLayout()

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search ingredients by name or category...")
        self.search_bar.textChanged.connect(self.update_search_results)
        left_layout.addWidget(self.search_bar)

        # Ingredient list
        self.ingredient_list = QListWidget()
        self.ingredient_list.itemClicked.connect(self.add_ingredient)
        left_layout.addWidget(self.ingredient_list)

        # Possible recipes dropdown
        self.recipe_combo = QComboBox()
        self.recipe_combo.setPlaceholderText("Possible recipes...")
        left_layout.addWidget(self.recipe_combo)

        layout.addLayout(left_layout)

        # Right side (selected ingredients)
        right_layout = QVBoxLayout()

        # Delete button
        delete_button = QPushButton("-")
        delete_button.clicked.connect(self.remove_selected_ingredient)
        right_layout.addWidget(delete_button)

        # Selected ingredients list
        self.selected_list = QListWidget()
        right_layout.addWidget(self.selected_list)

        layout.addLayout(right_layout)

        self.setLayout(layout)

        # Populate initial ingredient list
        self.populate_ingredients()


    def populate_ingredients(self):
        self.recommender.cursor.execute("SELECT name, category FROM groceries")
        ingredients = self.recommender.cursor.fetchall()
        for name, category in ingredients:
            self.ingredient_list.addItem(f"{name} ({category})")

    def update_search_results(self, text):
        self.ingredient_list.clear()
        self.recommender.cursor.execute("""
            SELECT name, category FROM groceries 
            WHERE name LIKE ? OR category LIKE ?
        """, (f'%{text}%', f'%{text}%'))
        ingredients = self.recommender.cursor.fetchall()
        for name, category in ingredients:
            self.ingredient_list.addItem(f"{name} ({category})")

    def add_ingredient(self, item):
        full_text = item.text()
        ingredient_name = full_text.split(' (')[0]
        category = full_text.split('(')[1].rstrip(')')
        
        if ingredient_name not in self.selected_ingredients:
            self.selected_ingredients[ingredient_name] = category
            self.selected_list.addItem(ingredient_name)
            self.update_possible_recipes()

    def remove_selected_ingredient(self):
        current_item = self.selected_list.currentItem()
        if current_item:
            ingredient_name = current_item.text()
            del self.selected_ingredients[ingredient_name]
            self.selected_list.takeItem(self.selected_list.row(current_item))
            self.update_possible_recipes()

    def update_possible_recipes(self):
        self.recipe_combo.clear()
        if not self.selected_ingredients:
            return

        # Get all recipes
        self.recommender.cursor.execute("SELECT id, name, original_ingredients FROM recipes")
        all_recipes = self.recommender.cursor.fetchall()

        possible_recipes = []
        for recipe_id, recipe_name, original_ingredients in all_recipes:
            recipe_ingredients = set(original_ingredients.split())
            if all(category in recipe_ingredients for category in self.selected_ingredients.values()):
                possible_recipes.append(recipe_name)

        for recipe in possible_recipes:
            self.recipe_combo.addItem(recipe)


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

            total_price += price

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

"""
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
"""

class CookingDialog(QDialog):
    def __init__(self, recommender):
        super().__init__()
        self.recommender = recommender
        self.initUI()

    def initUI(self):
        self.setWindowTitle('What did you cook?')
        self.setGeometry(200, 200, 600, 400)

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
        select_button = QPushButton('View Recipe Details')
        select_button.clicked.connect(self.view_recipe_details)
        layout.addWidget(select_button)

    def populate_recipes(self):
        recipes = self.recommender.get_recipes()
        for recipe in recipes:
            item = QStandardItem(recipe[1])  # Assuming recipe[1] is the name
            item.setData(recipe[0], Qt.UserRole)  # Store the recipe ID
            self.model.appendRow(item)

    def update_search_results(self, text):
        self.proxy_model.setFilterRegExp(f"\\b{text}")

    def view_recipe_details(self):
        selected_indexes = self.list_view.selectedIndexes()
        if selected_indexes:
            proxy_index = selected_indexes[0]
            source_index = self.proxy_model.mapToSource(proxy_index)
            selected_item = self.model.itemFromIndex(source_index)
            
            recipe_name = selected_item.text()
            recipe_id = selected_item.data(Qt.UserRole)
            
            detail_dialog = RecipeDetailDialog(self.recommender, recipe_id, recipe_name)
            detail_dialog.exec_()
        else:
            QMessageBox.warning(self, 'No Selection', 'Please select a recipe first.')

class RecipeDetailDialog(QDialog):
    def __init__(self, recommender, recipe_id, recipe_name):
        super().__init__()
        self.recommender = recommender
        self.recipe_id = recipe_id
        self.recipe_name = recipe_name
        self.original_servings = self.get_original_servings()
        self.current_servings = self.original_servings
        self.insufficient_ingredients = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f'Recipe Details: {self.recipe_name}')
        self.setGeometry(150, 150, 800, 600)

        layout = QVBoxLayout(self)

        # Recipe name as title
        title_label = QLabel(self.recipe_name)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)

        # Original recipe link
        original_link = self.get_original_link()
        link_button = QPushButton("View Original Recipe")
        link_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(original_link)))
        layout.addWidget(link_button, alignment=Qt.AlignRight)

        # Add serving adjustment section
        serving_layout = QHBoxLayout()
        serving_layout.addWidget(QLabel("Servings:"))
        
        self.serving_spinbox = QSpinBox()
        self.serving_spinbox.setMinimum(1)
        self.serving_spinbox.setMaximum(100)  # You can adjust this maximum value
        self.serving_spinbox.setValue(int(self.current_servings))
        self.serving_spinbox.valueChanged.connect(self.update_servings)
        serving_layout.addWidget(self.serving_spinbox)
        
        layout.addLayout(serving_layout)


        # Ingredients
        ingredients_label = QLabel("Ingredients:")
        ingredients_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(ingredients_label)
        self.ingredients_text = QTextEdit()
        self.ingredients_text.setReadOnly(True)
        self.ingredients_text.setPlainText(self.get_ingredients())
        layout.addWidget(self.ingredients_text)

        # User-editable summary
        summary_label = QLabel("Recipe Summary (Editable):")
        summary_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(summary_label)
        
        self.summary_text = QTextEdit()
        self.summary_text.setPlaceholderText("Enter your recipe summary or important notes here...")
        layout.addWidget(self.summary_text)

        # Load existing summary if available
        existing_summary = self.load_existing_summary()
        if existing_summary:
            self.summary_text.setPlainText(existing_summary)

        # Save Summary button
        save_button = QPushButton('Save Summary')
        save_button.clicked.connect(self.save_summary)
        layout.addWidget(save_button)

        # Create a horizontal layout for the bottom section
        bottom_layout = QHBoxLayout()

        # Add Finish Cooking button to the bottom left
        finish_button = QPushButton('Finish Cooking')
        finish_button.clicked.connect(self.finish_cooking)
        bottom_layout.addWidget(finish_button)

        # Nutrition values
        self.nutrition_label = QLabel()
        self.nutrition_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.nutrition_label.setStyleSheet("font-size: 12px;")
        bottom_layout.addWidget(self.nutrition_label)

        # Update initial values
        self.update_display()

        # Add the bottom layout to the main layout
        layout.addLayout(bottom_layout)



    def get_original_servings(self):
        self.recommender.cursor.execute("SELECT servings FROM recipes WHERE id = ?", (self.recipe_id,))
        servings = self.recommender.cursor.fetchone()
        return servings[0] if servings else 1
    

    def update_servings(self, new_servings):
        self.current_servings = new_servings
        self.update_display()
        self.check_ingredient_availability()

    def check_ingredient_availability(self):
        self.insufficient_ingredients = []
        recipe_ingredients = self.recommender.get_recipe_ingredients_and_amounts(self.recipe_id)[0]
        scaling_factor = self.current_servings / self.original_servings

        for ingredient, amount in recipe_ingredients:
            required_amount = self.recommender.scale_amount(amount, scaling_factor)
            home_amount = self.recommender.get_home_ingredient_amount(ingredient)

            if not self.recommender.is_sufficient_amount(home_amount, required_amount):
                self.insufficient_ingredients.append(ingredient)

        if self.insufficient_ingredients:
            self.show_ingredient_warning()

    def show_ingredient_warning(self):
        missing_ingredients = ", ".join(self.insufficient_ingredients)
        QMessageBox.warning(self, "Insufficient Ingredients", 
                            f"You don't have enough of the following ingredients: {missing_ingredients}")

    def update_display(self):
        self.update_ingredients()
        self.update_nutrition()

    def update_ingredients(self):
        self.recommender.cursor.execute("""
            SELECT original_ingredients, amount, servings 
            FROM recipes 
            WHERE id = ?
        """, (self.recipe_id,))
        result = self.recommender.cursor.fetchone()
        
        if result:
            original_ingredients, original_amounts, original_servings = result
            ingredients_list = original_ingredients.split()
            amounts_list = original_amounts.split()
            
            # Ensure the lists have the same length
            min_length = min(len(ingredients_list), len(amounts_list))
            ingredients_list = ingredients_list[:min_length]
            amounts_list = amounts_list[:min_length]
            
            # Calculate new amounts based on serving size
            scaling_factor = self.current_servings / original_servings
            new_amounts = [f"{float(amt.rstrip('gml')) * scaling_factor:.1f}{amt[-1] if amt[-1] in 'gml' else ''}" 
                           for amt in amounts_list]
            
            ingredients_with_amounts = [f"• {ing}: {amt}" for ing, amt in zip(ingredients_list, new_amounts)]
            formatted_ingredients = "\n".join(ingredients_with_amounts)
            
            self.ingredients_text.setPlainText(f"Servings: {self.current_servings}\n\nIngredients:\n{formatted_ingredients}")
        else:
            self.ingredients_text.setPlainText("No ingredients found for this recipe.")

    def update_nutrition(self):
        self.recommender.cursor.execute("SELECT nutrition_values FROM recipes WHERE id = ?", (self.recipe_id,))
        nutrition = self.recommender.cursor.fetchone()
        if nutrition and nutrition[0]:
            original_nutrition = nutrition[0].split('\n')
            scaling_factor = self.current_servings / self.original_servings
            new_nutrition = []
            for line in original_nutrition:
                nutrient, value = line.split(': ')
                if 'g' in value:
                    new_value = f"{float(value[:-1]) * scaling_factor:.2f}g"
                else:
                    new_value = f"{float(value) * scaling_factor:.2f}"
                new_nutrition.append(f"{nutrient}: {new_value}")
            self.nutrition_label.setText('\n'.join(new_nutrition))
        else:
            self.nutrition_label.setText("Nutrition information not available")





    def get_original_link(self):
        self.recommender.cursor.execute("SELECT link FROM recipes WHERE id = ?", (self.recipe_id,))
        link = self.recommender.cursor.fetchone()
        return link[0] if link else ""

    def get_ingredients(self):
        self.recommender.cursor.execute("""
            SELECT original_ingredients, amount, servings 
            FROM recipes 
            WHERE id = ?
        """, (self.recipe_id,))
        result = self.recommender.cursor.fetchone()
        
        if result:
            original_ingredients, amounts, servings = result
            ingredients_list = original_ingredients.split()
            amounts_list = amounts.split()
            
            # Ensure the lists have the same length
            min_length = min(len(ingredients_list), len(amounts_list))
            ingredients_list = ingredients_list[:min_length]
            amounts_list = amounts_list[:min_length]
            
            ingredients_with_amounts = [f"• {ing}: {amt}" for ing, amt in zip(ingredients_list, amounts_list)]
            formatted_ingredients = "\n".join(ingredients_with_amounts)
            
            return f"Servings: {servings}\n\nIngredients:\n{formatted_ingredients}"
        else:
            return "No ingredients found for this recipe."
        

    def get_nutrition_values(self):
        self.recommender.cursor.execute("SELECT nutrition_values FROM recipes WHERE id = ?", (self.recipe_id,))
        nutrition = self.recommender.cursor.fetchone()
        if nutrition and nutrition[0]:
            return nutrition[0]
        else:
            return "Nutrition information not available"
        

    def load_existing_summary(self):
        self.recommender.cursor.execute("SELECT summary FROM recipes WHERE id = ?", (self.recipe_id,))
        summary = self.recommender.cursor.fetchone()
        return summary[0] if summary and summary[0] else ""

    def save_summary(self):
        summary = self.summary_text.toPlainText()
        self.recommender.cursor.execute("UPDATE recipes SET summary = ? WHERE id = ?", (summary, self.recipe_id))
        self.recommender.conn.commit()
        QMessageBox.information(self, 'Success', 'Recipe summary has been saved.')

    def finish_cooking(self):
        if self.insufficient_ingredients:
            QMessageBox.critical(self, "Not Possible", "Not possible due to missing ingredients")
            return

        reply = QMessageBox.question(self, 'Confirm Cooking', 
                                     f"Have you finished cooking {self.recipe_name} for {self.current_servings} servings?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.recommender.add_to_cooked_recipes(self.recipe_id)
            self.recommender.update_home_ingredients(self.recipe_id, self.current_servings)
            QMessageBox.information(self, 'Success', f'{self.recipe_name} for {self.current_servings} servings has been added to your cooked recipes and home ingredients have been updated.')
            self.accept()
        else:
            QMessageBox.information(self, 'Cancelled', 'No recipe was added to cooked recipes.')


class IngredientSelectionDialog(QDialog):
    def __init__(self, recommender, recipe_id):
        super().__init__()
        self.recommender = recommender
        self.recipe_id = recipe_id
        self.chosen_ingredients = {}
        self.original_recipe_amounts = {}  # Store the original amounts
        self.current_recipe_amounts = {}   # Store the current (potentially scaled) amounts
        self.original_servings = self.get_original_servings()
        self.current_servings = self.original_servings
        self.initUI()

    def get_original_servings(self):
        self.recommender.cursor.execute("SELECT servings FROM recipes WHERE id = ?", (self.recipe_id,))
        servings = self.recommender.cursor.fetchone()
        return servings[0] if servings else 1

    def initUI(self):
        self.setWindowTitle('Select Ingredients')
        self.setGeometry(150, 150, 800, 600)

        layout = QVBoxLayout(self)

        # Add serving adjustment section at the top
        serving_layout = QHBoxLayout()
        serving_layout.addWidget(QLabel(f"Original servings: {self.original_servings}"))
        serving_layout.addWidget(QLabel("Adjust servings:"))
        
        self.serving_spinbox = QSpinBox()
        self.serving_spinbox.setMinimum(1)
        self.serving_spinbox.setMaximum(100)  # You can adjust this maximum value
        self.serving_spinbox.setValue(self.current_servings)
        self.serving_spinbox.valueChanged.connect(self.update_servings)
        serving_layout.addWidget(self.serving_spinbox)
        
        layout.addLayout(serving_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)

        recipe_ingredients = self.recommender.get_recipe_ingredients(self.recipe_id)
        self.original_recipe_amounts = self.recommender.get_recipe_amounts(self.recipe_id)
        self.current_recipe_amounts = self.original_recipe_amounts.copy()

        for ingredient in recipe_ingredients:
            self.add_ingredient_group(ingredient)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        confirm_button = QPushButton('Confirm Selection')
        confirm_button.clicked.connect(self.confirm_selection)
        layout.addWidget(confirm_button)

    def add_ingredient_group(self, ingredient):
        group_box = QGroupBox(ingredient)
        group_layout = QVBoxLayout()

        original_amount = self.original_recipe_amounts.get(ingredient, "0g")
        self.amount_label = QLabel(f"Needed: {original_amount}")
        self.amount_label.setObjectName(f"amount_label_{ingredient}")
        group_layout.addWidget(self.amount_label)

        # Add "Choose nothing" option
        nothing_radio = QRadioButton("Choose nothing")
        nothing_radio.toggled.connect(lambda checked, ing=ingredient: 
                                      self.on_nothing_selected(checked, ing))
        group_layout.addWidget(nothing_radio)

        # Add "At Home" options
        home_options = self.recommender.get_home_ingredients_by_category(ingredient)
        if home_options:
            for name, price, amount in home_options:
                radio = QRadioButton(f"{name} (${price:.2f}) (Available: {amount}) - At Home")
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
        total_label = QLabel(f"Selected: 0{original_amount[-1]} / {original_amount}")
        group_layout.addWidget(total_label)
        self.chosen_ingredients[ingredient]['total_label'] = total_label

        group_box.setLayout(group_layout)
        self.scroll_layout.addWidget(group_box)

    def update_servings(self, new_servings):
        self.current_servings = new_servings
        scaling_factor = self.current_servings / self.original_servings

        for ingredient, original_amount in self.original_recipe_amounts.items():
            new_amount = self.scale_amount(original_amount, scaling_factor)
            self.current_recipe_amounts[ingredient] = new_amount
            
            # Update the "Needed" label for each ingredient
            amount_label = self.findChild(QLabel, f"amount_label_{ingredient}")
            if amount_label:
                amount_label.setText(f"Needed: {new_amount}")

        self.update_all_total_amounts()

    def scale_amount(self, amount, factor):
        value = float(''.join(char for char in amount if char.isdigit() or char == '.'))
        unit = ''.join(char for char in amount if char.isalpha())
        return f"{value * factor:.1f}{unit}"

    def update_all_total_amounts(self):
        for ingredient in self.chosen_ingredients:
            self.update_total_amount(ingredient)

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
        current_recipe_amount = self.current_recipe_amounts.get(ingredient, "0g")
        recipe_amount_parsed = self.parse_amount(current_recipe_amount)
        recipe_amount_value = self.get_amount_value(current_recipe_amount)

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
            current_recipe_amount = self.current_recipe_amounts.get(ingredient, "0g")
            recipe_amount_value = self.get_amount_value(current_recipe_amount)

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

        _, to_buy_price = self.recommender.get_total_prices()
        message = (
                   f"Price for items you need to buy: ${to_buy_price:.2f}\n\n"
                   f"This recipe is adjusted for {self.current_servings} servings.\n\n"
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