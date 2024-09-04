import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QListWidget, QMessageBox, QDialog, QRadioButton, QButtonGroup, QScrollArea, QGroupBox, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt

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


    def show_shopping_list(self):
        self.recommender.cursor.execute("SELECT name, category, price FROM shoppinglist")
        shopping_list = self.recommender.cursor.fetchall()

        dialog = QDialog(self)
        dialog.setWindowTitle("Shopping List")
        dialog.setGeometry(150, 150, 500, 400)

        layout = QVBoxLayout(dialog)
        
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Name", "Category", "Price"])
        table.setRowCount(len(shopping_list))

        total_price = 0
        for row, (name, category, price) in enumerate(shopping_list):
            table.setItem(row, 0, QTableWidgetItem(name))
            table.setItem(row, 1, QTableWidgetItem(category))
            price_item = QTableWidgetItem(f"${price:.2f}")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 2, price_item)
            total_price += price

        table.resizeColumnsToContents()
        layout.addWidget(table)

        # Add total price label
        total_label = QLabel(f"Total Price: ${total_price:.2f}")
        total_label.setAlignment(Qt.AlignRight)
        total_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        layout.addWidget(total_label)

        dialog.exec_()

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
        self.setGeometry(150, 150, 600, 400)

        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        recipe_ingredients = self.recommender.get_recipe_ingredients(self.recipe_id)
        self.recipe_amounts = self.recommender.get_recipe_amounts(self.recipe_id)

        for ingredient in recipe_ingredients:
            group_box = QGroupBox(ingredient)
            group_layout = QVBoxLayout()
            button_group = QButtonGroup(self)

            recipe_amount = self.recipe_amounts.get(ingredient, "0")

            amount_label = QLabel(f"Needed: {recipe_amount}")
            group_layout.addWidget(amount_label)

            # Add "Choose nothing" option
            nothing_radio = QRadioButton("Choose nothing")
            nothing_radio.toggled.connect(lambda checked, ing=ingredient: 
                                          self.on_ingredient_selected(checked, ing, None, None))
            button_group.addButton(nothing_radio)
            group_layout.addWidget(nothing_radio)

            home_options = self.recommender.get_home_ingredients_by_category(ingredient)
            if home_options:
                for name, price, amount in home_options:
                    radio = QRadioButton(f"{name} (${price:.2f}) (Available : {amount}) - At Home")
                    radio.toggled.connect(lambda checked, n=name, p=price, ing=ingredient: 
                                          self.on_ingredient_selected(checked, ing, (n, p), True))
                    button_group.addButton(radio)
                    group_layout.addWidget(radio)

            grocery_options = self.recommender.get_grocery_items_by_category(ingredient)
            for id, name, price, amount in grocery_options:
                radio = QRadioButton(f"{name} (${price:.2f}) (Amount : {amount}) - Need to Buy")
                radio.toggled.connect(lambda checked, n=name, p=price, ing=ingredient: 
                                      self.on_ingredient_selected(checked, ing, (n, p), False))
                button_group.addButton(radio)
                group_layout.addWidget(radio)

            group_box.setLayout(group_layout)
            scroll_layout.addWidget(group_box)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        confirm_button = QPushButton('Confirm Selection')
        confirm_button.clicked.connect(self.confirm_selection)
        layout.addWidget(confirm_button)

    def on_ingredient_selected(self, checked, ingredient, item, at_home):
        if checked:
            if item is None:  # "Choose nothing" was selected
                self.chosen_ingredients.pop(ingredient, None)
            else:
                name, price = item
                amount = self.get_amount_for_item(name, at_home)
                needed_amount = self.recipe_amounts.get(ingredient, "0")
                
                difference = self.calculate_amount_difference(needed_amount, amount)

                self.chosen_ingredients[ingredient] = (name, price, at_home, amount)
                
                if difference > 0:
                    self.show_additional_options(ingredient, difference, at_home, name)
                
                

    def get_amount_for_item(self, name, at_home):
        if at_home:
            return self.recommender.get_home_ingredient_amount(name)
        else:
            return self.recommender.get_grocery_item_amount(name)

    def calculate_amount_difference(self, needed, available):
        needed_value, needed_unit = extract_value_and_unit(needed)
        available_value, available_unit = extract_value_and_unit(available)
        
        needed_common = convert_to_common_unit(needed_value, needed_unit)
        available_common = convert_to_common_unit(available_value, available_unit)
        
        difference = needed_common - available_common
        return max(0, difference)  # Return 0 if difference is negative

    def show_additional_options(self, ingredient, difference, previous_at_home, previous_name):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Additional {ingredient} Needed")
        dialog.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout(dialog)
        
        label = QLabel(f"You still need {difference:.2f}g of {ingredient}. Please select an additional option:")
        layout.addWidget(label)

        button_group = QButtonGroup(dialog)

        home_options = self.recommender.get_home_ingredients_by_category(ingredient)
        grocery_options = self.recommender.get_grocery_items_by_category(ingredient)

        for name, price, amount in home_options:
            if not (previous_at_home and name == previous_name):
                radio = QRadioButton(f"{name} (${price:.2f}) (Available: {amount}) - At Home")
                radio.toggled.connect(lambda checked, n=name, p=price, a=amount: 
                                      self.on_additional_selected(checked, ingredient, (n, p), True, a))
                button_group.addButton(radio)
                layout.addWidget(radio)

        for id, name, price, amount in grocery_options:
            radio = QRadioButton(f"{name} (${price:.2f}) (Amount: {amount}) - Need to Buy")
            radio.toggled.connect(lambda checked, n=name, p=price, a=amount: 
                                  self.on_additional_selected(checked, ingredient, (n, p), False, a))
            button_group.addButton(radio)
            layout.addWidget(radio)

        confirm_button = QPushButton('Confirm Additional Selection')
        confirm_button.clicked.connect(dialog.accept)
        layout.addWidget(confirm_button)

        dialog.exec_()

    def on_additional_selected(self, checked, ingredient, item, at_home, amount):
        if checked:
            name, price = item
            current_name, current_price, current_at_home, current_amount = self.chosen_ingredients[ingredient]
            
            new_amount = self.calculate_new_amount(current_amount, amount)
            
            self.chosen_ingredients[ingredient] = (
                f"{current_name} + {name}",
                current_price + price,
                current_at_home and at_home,
                new_amount
            )

    def calculate_new_amount(self, amount1, amount2):
        value1, unit1 = extract_value_and_unit(amount1)
        value2, unit2 = extract_value_and_unit(amount2)
        
        total_value = convert_to_common_unit(value1, unit1) + convert_to_common_unit(value2, unit2)
        
        return f"{total_value}g"  # Assuming we're using grams as the common unit

    def confirm_selection(self):
        recipe_ingredients = self.recommender.get_recipe_ingredients(self.recipe_id)
        missing_ingredients = set(recipe_ingredients) - set(self.chosen_ingredients.keys())
        
        if missing_ingredients:
            message = "You've chosen to use nothing for the following ingredients:\n"
            message += ", ".join(missing_ingredients)
            message += "\n\nDo you want to continue?"
            reply = QMessageBox.question(self, 'Confirm Selection', message, 
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        for ingredient, (name, price, at_home, _) in self.chosen_ingredients.items():
            self.recommender.add_to_chosen_for_recipe(name, ingredient, price, at_home)

        total_price, to_buy_price = self.recommender.get_total_prices()
        message = (f"Total price for the recipe: ${total_price:.2f}\n"
                   f"Price for items you need to buy: ${to_buy_price:.2f}\n\n"
                   "Would you like to make this recipe? "
                   "If yes, items you need to buy will be added to your shopping list.")
        reply = QMessageBox.question(self, 'Confirm Recipe', message, 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.recommender.add_to_shopping_list()
            self.recommender.add_to_cooked_recipes(self.recipe_id)
            QMessageBox.information(self, 'Success', 'Recipe added to cooked recipes and items added to shopping list.')
        else:
            QMessageBox.information(self, 'Cancelled', 'No items were added to the shopping list.')

        self.recommender.clear_chosen_for_recipe()
        self.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RecipeRecommenderGUI()
    ex.show()
    sys.exit(app.exec_())