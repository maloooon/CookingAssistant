import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QListWidget, QMessageBox, QDialog, QRadioButton, QButtonGroup, QScrollArea, QGroupBox, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt

from recommender import RecipeRecommender  # Import your existing RecipeRecommender class

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
        recommendation_layout.addWidget(QLabel('Recommended Recipes:'))
        recommendation_layout.addWidget(self.recommendation_list)

        recommend_button = QPushButton('Get Recommendations')
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
        self.recommender.cursor.execute("SELECT name, category FROM home")
        home_ingredients = self.recommender.cursor.fetchall()

        dialog = QDialog(self)
        dialog.setWindowTitle("Ingredients at Home")
        dialog.setGeometry(150, 150, 400, 300)

        layout = QVBoxLayout(dialog)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        for name, category in home_ingredients:
            scroll_layout.addWidget(QLabel(f"{name} - {category}"))

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

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




class IngredientSelectionDialog(QDialog):
    def __init__(self, recommender, recipe_id):
        super().__init__()
        self.recommender = recommender
        self.recipe_id = recipe_id
        self.chosen_ingredients = {}
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
        for ingredient in recipe_ingredients:
            group_box = QGroupBox(ingredient)
            group_layout = QVBoxLayout()
            button_group = QButtonGroup(self)

            # Add "Choose nothing" option
            nothing_radio = QRadioButton("Choose nothing")
            nothing_radio.toggled.connect(lambda checked, ing=ingredient: 
                                          self.on_ingredient_selected(checked, ing, None, None))
            button_group.addButton(nothing_radio)
            group_layout.addWidget(nothing_radio)

            home_options = self.recommender.get_home_ingredients_by_category(ingredient)
            if home_options:
                for name, price in home_options:
                    radio = QRadioButton(f"{name} (${price:.2f}) - At Home")
                    radio.toggled.connect(lambda checked, n=name, p=price, ing=ingredient: 
                                          self.on_ingredient_selected(checked, ing, (n, p), True))
                    button_group.addButton(radio)
                    group_layout.addWidget(radio)

            grocery_options = self.recommender.get_grocery_items_by_category(ingredient)
            for id, name, price in grocery_options:
                radio = QRadioButton(f"{name} (${price:.2f}) - Need to Buy")
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
                self.chosen_ingredients[ingredient] = (item[0], item[1], at_home)

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

        for ingredient, (name, price, at_home) in self.chosen_ingredients.items():
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