# Add recipes to the database

# Right now implemented for https://minimalistbaker.com/white-bean-eggplant-caponata/ (working)
# but just ingredients put in line by line
# first line is title of recipe
# second line is amount of servings (for the given amounts)

import sqlite3
import re

# Connect to the database
conn = sqlite3.connect('groceries.db')


def read_recipe_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    title = lines[0].strip()
    servings = float(lines[1].strip())
    recipe_content = [line.strip() for line in lines[2:] if line.strip()]
    
    return title, servings, recipe_content

def create_word_to_category_mapping(category_mapping):
    return {word.lower(): category 
            for category, words in category_mapping.items() 
            for word in words}

def extract_ingredients_and_amounts(line, word_to_category):
    amount_pattern = r'(\d+(?:\.\d+)?|\d+/\d+|\w+)\s*(g|kg|ml|l|piece|pieces|medium|large|small|tsp|ts)'
    amount_regex = re.compile(amount_pattern, re.IGNORECASE)
    
    ingredient_pattern = r'\b(' + '|'.join(re.escape(word) for word in word_to_category.keys()) + r')\b'
    ingredient_regex = re.compile(ingredient_pattern, re.IGNORECASE)
    
    amounts = amount_regex.findall(line)
    ingredients = ingredient_regex.findall(line)
    
    if not ingredients:
        return None  # No matched ingredient found
    
    results = []
    seen_ingredients = set()
    for ingredient in ingredients:
        if ingredient.lower() not in seen_ingredients:
            category = word_to_category[ingredient.lower()]
            amount = next((f"{amt[0]} {amt[1]}" for amt in amounts if line.index(amt[0]) < line.index(ingredient)), None)
            results.append((ingredient, category, amount))
            seen_ingredients.add(ingredient.lower())
            if amount:
                amounts = [amt for amt in amounts if f"{amt[0]} {amt[1]}" != amount]
    
    return results

def process_recipe(recipe_content, word_to_category):
    all_ingredients = []
    unmatched_lines = []
    for line in recipe_content:
        ingredients = extract_ingredients_and_amounts(line, word_to_category)
        if ingredients:
            all_ingredients.extend(ingredients)
        else:
            unmatched_lines.append(line)
    return all_ingredients, unmatched_lines

def format_as_single_word(text):
    return re.sub(r'\s+', '_', text.strip())

def insert_recipe_to_db(db_path, recipe_name, original_ingredients, mapped_ingredients, amounts, servings):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()


    formatted_original = ' '.join(format_as_single_word(ing) for ing in original_ingredients)
    formatted_amounts = ' '.join(format_as_single_word(amt) if amt != 'N/A' else amt for amt in amounts)

    recipe_data = (
        recipe_name,
        formatted_original,
        ' '.join(mapped_ingredients),
        formatted_amounts,
        servings
    )

    cursor.execute('''
        INSERT INTO recipes (name, original_ingredients, ingredients, amount, servings)
        VALUES (?, ?, ?, ?, ?)
    ''', recipe_data)

    conn.commit()
    conn.close()



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


# Create word to category mapping
word_to_category = create_word_to_category_mapping(category_mapping)

# Read the recipe file
recipe_file_path = 'recipe_ingredients.txt'  # Replace with your actual file path
recipe_name, servings, recipe_content = read_recipe_file(recipe_file_path)

# Process the recipe
result, unmatched_lines = process_recipe(recipe_content, word_to_category)

# Check for unmatched ingredients
if unmatched_lines:
    print("Warning: The following lines contain ingredients that were not matched:")
    for line in unmatched_lines:
        print(f"  - {line}")
    print("Please add these ingredients to the category mapping and try again.")
    print("The recipe will not be added to the database.")
else:
    # Prepare data for database insertion
    original_ingredients = [item[0] for item in result]
    mapped_ingredients = [item[1] for item in result]
    amounts = [item[2] if item[2] else 'N/A' for item in result]

    # Insert the recipe into the database
    db_path = 'groceries.db'
    insert_recipe_to_db(db_path, recipe_name, original_ingredients, mapped_ingredients, amounts, servings)

    print(f"Recipe '{recipe_name}' has been added to the database.")

    # Verify the insertion
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM recipes WHERE name = ?", (recipe_name,))
    print("\nInserted recipe:")
    print(cursor.fetchone())

    conn.close()



