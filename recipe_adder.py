import sqlite3
import sys
import recipe_nutrition_calculator


category_mapping = {
    # Mapped together (individual per user)
    "pasta": ["spaghetti", "rigatoni", "penne", "fettuccine", "linguine", "farfalle", "fusilli"],
    "vegetarian_meat_replacement": ["tofu", "tempeh", "seitan"],


    "black_rice": ["black rice"],

    


    # Vegetables
    "tomato": ["tomato", "tomatoes"],
    "potato": ["potato", "potatoes"],
    "onion": ["onion", "onions", "shallot", "shallots"],
    "garlic": ["garlic", "garlics"],
    "carrot": ["carrot", "carrots"],
    "broccoli": ["broccoli", "broccolis"],
    "spinach": ["spinach", "spinaches"],
    "lettuce": ["lettuce", "lettuces"],
    "cucumber": ["cucumber", "cucumbers"],
    "bell_pepper": ["bell pepper", "bell peppers"],
    "zucchini": ["zucchini", "zucchinis"],
    "eggplant": ["eggplant", "eggplants"],
    "mushroom": ["mushroom", "mushrooms"],
    "corn": ["corn", "corns"],
    "pea": ["pea", "peas"],
    "green_bean": ["green bean", "green beans"],
    "asparagus": ["asparagus", "asparaguses"],
    "cauliflower": ["cauliflower", "cauliflowers"],
    "celery": ["celery", "celeries"],
    "cabbage": ["cabbage", "cabbages"],
    "kale": ["kale", "kales"],
    "brussels_sprout": ["brussels sprout", "brussels sprouts"],
    "artichoke": ["artichoke", "artichokes"],
    "leek": ["leek", "leeks"],
    "beet": ["beet", "beets"],
    "radish": ["radish", "radishes"],
    "turnip": ["turnip", "turnips"],
    "squash": ["squash", "squashes"],
    "pumpkin": ["pumpkin", "pumpkins"],
    "sweet_potato": ["sweet potato", "sweet potatoes"],

    # Fruits
    "apple": ["apple", "apples"],
    "banana": ["banana", "bananas"],
    "orange": ["orange", "oranges"],
    "lemon": ["lemon", "lemons"],
    "lime": ["lime", "limes"],
    "strawberry": ["strawberry", "strawberries"],
    "blueberry": ["blueberry", "blueberries"],
    "raspberry": ["raspberry", "raspberries"],
    "blackberry": ["blackberry", "blackberries"],
    "grape": ["grape", "grapes"],
    "pineapple": ["pineapple", "pineapples"],
    "mango": ["mango", "mangoes"],
    "peach": ["peach", "peaches"],
    "pear": ["pear", "pears"],
    "plum": ["plum", "plums"],
    "cherry": ["cherry", "cherries"],
    "kiwi": ["kiwi", "kiwis"],
    "watermelon": ["watermelon", "watermelons"],
    "cantaloupe": ["cantaloupe", "cantaloupes"],
    "honeydew": ["honeydew", "honeydews"],
    "fig": ["fig", "figs"],
    "pomegranate": ["pomegranate", "pomegranates"],
    "avocado": ["avocado", "avocados"],

    # Meats
    "chicken": ["chicken", "chickens"],
    "beef": ["beef", "beefs"],
    "pork": ["pork", "porks"],
    "lamb": ["lamb", "lambs"],
    "turkey": ["turkey", "turkeys"],
    "duck": ["duck", "ducks"],
    "veal": ["veal", "veals"],
    "bacon": ["bacon", "bacons"],
    "ham": ["ham", "hams"],
    "sausage": ["sausage", "sausages"],
    "salami": ["salami", "salamis"],
    "prosciutto": ["prosciutto", "prosciuttos"],
    "ground_beef": ["ground beef", "ground beefs"],
    "steak": ["steak", "steaks"],
    "rib": ["rib", "ribs"],
    "meatball": ["meatball", "meatballs"],

    # Fish and Seafood
    "salmon": ["salmon", "salmons"],
    "tuna": ["tuna", "tunas"],
    "cod": ["cod", "cods"],
    "halibut": ["halibut", "halibuts"],
    "trout": ["trout", "trouts"],
    "tilapia": ["tilapia", "tilapias"],
    "sardine": ["sardine", "sardines"],
    "anchovy": ["anchovy", "anchovies"],
    "shrimp": ["shrimp", "shrimps"],
    "crab": ["crab", "crabs"],
    "lobster": ["lobster", "lobsters"],
    "scallop": ["scallop", "scallops"],
    "mussel": ["mussel", "mussels"],
    "clam": ["clam", "clams"],
    "oyster": ["oyster", "oysters"],
    "calamari": ["calamari", "calamaris"],

    # Dairy and Eggs (singular only)
    "milk": ["milk"],
    "cheese": ["cheese"],
    "butter": ["butter"],
    "cream": ["cream"],
    "yogurt": ["yogurt"],
    "sour_cream": ["sour cream"],
    "cream_cheese": ["cream cheese"],
    "cottage_cheese": ["cottage cheese"],
    "ricotta": ["ricotta"],
    "mozzarella": ["mozzarella"],
    "parmesan": ["parmesan"],
    "cheddar": ["cheddar"],
    "feta": ["feta"],
    "egg": ["egg"],
    "margarine": ["margarine"],
    "heavy_cream": ["heavy cream"],

    # Herbs and Spices (singular only)
    "salt": ["salt"],
    "pepper": ["pepper"],
    "basil": ["basil"],
    "oregano": ["oregano"],
    "thyme": ["thyme"],
    "rosemary": ["rosemary"],
    "parsley": ["parsley"],
    "cilantro": ["cilantro"],
    "mint": ["mint"],
    "dill": ["dill"],
    "chive": ["chive"],
    "sage": ["sage"],
    "bay_leaf": ["bay leaf"],
    "paprika": ["paprika"],
    "cumin": ["cumin"],
    "coriander": ["coriander"],
    "turmeric": ["turmeric"],
    "cinnamon": ["cinnamon"],
    "nutmeg": ["nutmeg"],
    "ginger": ["ginger"],
    "garlic_powder": ["garlic powder"],
    "onion_powder": ["onion powder"],
    "chili_powder": ["chili powder"],
    "cayenne": ["cayenne"],
    "red_pepper_flake": ["red pepper flake"],
    "clove": ["clove"],
    "allspice": ["allspice"],
    "cardamom": ["cardamom"],
    "saffron": ["saffron"],
    "vanilla": ["vanilla"],
    "fennel": ["fennel"],
    "tarragon": ["tarragon"],

    # Nuts and Seeds
    "almond": ["almond", "almonds"],
    "walnut": ["walnut", "walnuts"],
    "pecan": ["pecan", "pecans"],
    "cashew": ["cashew", "cashews"],
    "pistachio": ["pistachio", "pistachios"],
    "peanut": ["peanut", "peanuts"],
    "hazelnut": ["hazelnut", "hazelnuts"],
    "pine_nut": ["pine nut", "pine nuts"],
    "sunflower_seed": ["sunflower seed", "sunflower seeds"],
    "pumpkin_seed": ["pumpkin seed", "pumpkin seeds"],
    "sesame_seed": ["sesame seed", "sesame seeds"],
    "chia_seed": ["chia seed", "chia seeds"],
    "flax_seed": ["flax seed", "flax seeds"],

    # Legumes
    "bean": ["bean", "beans"],
    "lentil": ["lentil", "lentils"],
    "chickpea": ["chickpea", "chickpeas"],
    "soybean": ["soybean", "soybeans"],
    "black_bean": ["black bean", "black beans"],
    "kidney_bean": ["kidney bean", "kidney beans"],
    "pinto_bean": ["pinto bean", "pinto beans"],
    "lima_bean": ["lima bean", "lima beans"],

    # Oils and Vinegars (singular only)
    "olive_oil": ["olive oil"],
    "vegetable_oil": ["vegetable oil"],
    "canola_oil": ["canola oil"],
    "coconut_oil": ["coconut oil"],
    "sesame_oil": ["sesame oil"],
    "balsamic_vinegar": ["balsamic vinegar"],
    "apple_cider_vinegar": ["apple cider vinegar"],
    "red_wine_vinegar": ["red wine vinegar"],
    "white_vinegar": ["white vinegar"],
    "rice_vinegar": ["rice vinegar"],

    # Condiments and Sauces (singular only)
    "ketchup": ["ketchup"],
    "mustard": ["mustard"],
    "mayonnaise": ["mayonnaise"],
    "soy_sauce": ["soy sauce"],
    "hot_sauce": ["hot sauce"],
    "worcestershire_sauce": ["worcestershire sauce"],
    "bbq_sauce": ["bbq sauce"],
    "salsa": ["salsa"],
    "pesto": ["pesto"],
    "tomato_sauce": ["tomato sauce"],
    "marinara_sauce": ["marinara sauce"],
    "teriyaki_sauce": ["teriyaki sauce"],
    "hoisin_sauce": ["hoisin sauce"],
    "fish_sauce": ["fish sauce"],
    "oyster_sauce": ["oyster sauce"],

    # Sweeteners (singular only)
    "sugar": ["sugar"],
    "brown_sugar": ["brown sugar"],
    "powdered_sugar": ["powdered sugar"],
    "honey": ["honey"],
    "maple_syrup": ["maple syrup"],
    "agave_nectar": ["agave nectar"],
    "molasses": ["molasses"],
    "corn_syrup": ["corn syrup"],

    # Baking Ingredients (singular only)
    "baking_powder": ["baking powder"],
    "baking_soda": ["baking soda"],
    "yeast": ["yeast"],
    "cocoa_powder": ["cocoa powder"],
    "chocolate_chip": ["chocolate chip"],
    "vanilla_extract": ["vanilla extract"],
    "almond_extract": ["almond extract"],
    "cornstarch": ["cornstarch"],
    "gelatin": ["gelatin"],

    # Broths and Stocks (singular only)
    "chicken_broth": ["chicken broth"],
    "beef_broth": ["beef broth"],
    "vegetable_broth": ["vegetable broth"],
    "fish_stock": ["fish stock"],

    # Alcoholic Ingredients (singular only)
    "white_wine": ["white wine"],
    "red_wine": ["red wine"],
    "beer": ["beer"],
    "brandy": ["brandy"],
    "rum": ["rum"],
    "vodka": ["vodka"],
    "whiskey": ["whiskey"],
    "sherry": ["sherry"],
    "cooking_wine": ["cooking wine"],

    # Miscellaneous
    "water": ["water"],
    "coconut_milk": ["coconut milk"],
    "nutritional_yeast": ["nutritional yeast"],
    "miso_paste": ["miso paste"],
    "tahini": ["tahini"],
    "condensed_milk": ["condensed milk"],
    "evaporated_milk": ["evaporated milk"],
    "broth": ["broth"],
    "stock_cube": ["stock cube"],
    "tomato_paste": ["tomato paste"],
    "anchovy_paste": ["anchovy paste"],
    "caper": ["caper", "capers"],
    "olive": ["olive", "olives"],
    "pickle": ["pickle", "pickles"],
    "sun_dried_tomato": ["sun-dried tomato", "sun-dried tomatoes"],
    "dried_fruit": ["dried fruit", "dried fruits"],
    "raisin": ["raisin", "raisins"],
    "cranberry": ["cranberry", "cranberries"],
}



def read_recipe_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    title = lines[0].strip()
    servings = float(lines[1].strip())
    link = lines[2].strip()
    recipe_content = [line.strip() for line in lines[3:] if line.strip()]
    
    return title, servings, link, recipe_content

def create_word_to_category_mapping(category_mapping):
    return {word.lower(): category 
            for category, words in category_mapping.items() 
            for word in words}

class IngredientMappingError(Exception):
    pass

def process_recipe(recipe_content, word_to_category):
    all_ingredients = []
    for line in recipe_content:
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            amount, ingredient = parts
            original_ingredient = ingredient
            ingredient_words = ingredient.lower().split()
            mapped_ingredient = None
            for i in range(len(ingredient_words), 0, -1):
                potential_ingredient = ' '.join(ingredient_words[:i])
                if potential_ingredient in word_to_category:
                    mapped_ingredient = word_to_category[potential_ingredient]
                    break
            
            if mapped_ingredient is None:
                raise IngredientMappingError(f"The mapping for ingredient '{original_ingredient}' is missing")
            
            all_ingredients.append((amount, original_ingredient, mapped_ingredient))
    return all_ingredients

def insert_recipe_to_db(db_path, recipe_name, original_ingredients, mapped_ingredients, amounts, servings, link):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    formatted_original = ' '.join(original_ingredients)
    formatted_mapped = ' '.join(mapped_ingredients)
    formatted_amounts = ' '.join(amounts)

    recipe_data = (
        recipe_name,
        formatted_original,
        formatted_mapped,
        formatted_amounts,
        servings,
        link
    )

    cursor.execute('''
        INSERT INTO recipes (name, original_ingredients, ingredients, amount, servings, link)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', recipe_data)

    conn.commit()
    conn.close()


# Create word to category mapping
word_to_category = create_word_to_category_mapping(category_mapping)

# Read the recipe file
recipe_file_path = 'recipe_ingredients.txt'  
recipe_name, servings, link, recipe_content = read_recipe_file(recipe_file_path)

try:
    # Process the recipe
    result = process_recipe(recipe_content, word_to_category)

    # Prepare data for database insertion
    original_ingredients = [item[1] for item in result]
    mapped_ingredients = [item[2] for item in result]
    amounts = [item[0] for item in result]

    # Insert the recipe into the database
    db_path = 'groceries.db'
    insert_recipe_to_db(db_path, recipe_name, original_ingredients, mapped_ingredients, amounts, servings, link)

    print(f"Recipe '{recipe_name}' has been added to the database.")

    # Verify the insertion
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM recipes WHERE name = ?", (recipe_name,))
    print("\nInserted recipe:")
    print(cursor.fetchone())

    # Calculate nutrition values for the recipe
    recipe_nutrition_calculator.calculate_recipe_nutrition(recipe_name)


    conn.close()

except IngredientMappingError as e:
    print(f"Error: {e}")
    print("The recipe was not added to the database.")
    sys.exit(1)







