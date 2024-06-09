import json
import pprint as pp
import numpy as np
from scipy.sparse import csr_matrix


class Akinator:
    def __init__(self, recipes = None):
        self.recipes = recipes
        self.ingredient_index = {}
        self.recipe_index = []
        self.sparse_matrix = None
        self.asked_questions = []
        self.similar_ingr = self.load_similar_ingr()
        self._initialize_sparse_matrix()

    def load_similar_ingr(self):
        with open('Defs/similar_ingredients.json', 'r') as file:
            similar_ingredients_dict = json.load(file)
        return similar_ingredients_dict
    
    def reset(self):
        self.ingredient_index = {}
        self.recipe_index = []
        self.sparse_matrix = None
        self.asked_questions = []
        self._initialize_sparse_matrix()

    def _initialize_sparse_matrix(self):
        unique_ingredients = set()
        for recipe in self.recipes:
            ingredients = self.recipes[recipe]["ingredients"]
            for ing in ingredients:
                ingredient_name = ing["ingredient"].lower().strip()
                if ingredient_name:
                    unique_ingredients.add(ingredient_name)
        sorted(unique_ingredients)
        self.ingredient_index = {ing: i for i, ing in enumerate(unique_ingredients)}
        sorted(self.ingredient_index)
        self.recipe_index = list(self.recipes.keys())
        sorted(self.recipe_index)

        rows, cols, data = [], [], []
        for recipe_id, recipe in enumerate(self.recipe_index):
            ingredients = self.recipes[recipe]["ingredients"]
            for ing in ingredients:
                ingredient_name = ing["ingredient"].lower().strip()
                if ingredient_name in self.ingredient_index:
                    rows.append(recipe_id)
                    cols.append(self.ingredient_index[ingredient_name])
                    data.append(1)

        self.sparse_matrix = csr_matrix((data, (rows, cols)), shape=(len(self.recipe_index), len(self.ingredient_index)))
        #dense_matrix = self.sparse_matrix.todense()

    def remove_without_ingredient(self, ingredient):
        if ingredient in self.ingredient_index:
            ingredient_id = self.ingredient_index[ingredient]
            rows = self.sparse_matrix[:, ingredient_id].nonzero()[0]
            for ingr in self.similar_ingr[ingredient]:
                ingr = ingr.lower().strip()
                if ingr in self.ingredient_index:
                    ingr_id = self.ingredient_index[ingr]
                    new_rows = self.sparse_matrix[:, ingr_id].nonzero()[0]
                    rows = np.unique(np.concatenate((rows, new_rows)))
            filtered_recipes = [self.recipe_index[row] for row in rows]
            self.recipes = {recipe: self.recipes[recipe] for recipe in filtered_recipes}
            self._initialize_sparse_matrix()

    def remove_with_ingredient(self, ingredient):
          if ingredient in self.ingredient_index:
            ingredient_id = self.ingredient_index[ingredient]
            rows = self.sparse_matrix[:, ingredient_id].nonzero()[0]
            rows_to_remove = set(range(self.sparse_matrix.shape[0])) - set(rows)
            filtered_recipes = [self.recipe_index[row] for row in rows_to_remove]
            self.recipes = {recipe: self.recipes[recipe] for recipe in filtered_recipes}
            self._initialize_sparse_matrix()

    def best_question_to_ask(self):
        recipe_count = len(self.recipe_index)
        if recipe_count == 0:
            return None
        
        best_ingredient = None
        best_entropy = 0
        
        for ingredient, ingredient_id in self.ingredient_index.items():

            p_yes = self.sparse_matrix[:, ingredient_id].sum() / recipe_count
            p_no = 1 - p_yes
            
            if p_yes > 0 and p_no > 0:
                entropy = -(p_yes * np.log2(p_yes) + p_no * np.log2(p_no))
            else:
                entropy = 0
        
            if ingredient not in self.asked_questions and entropy > best_entropy:
                best_entropy = entropy
                best_ingredient = ingredient
        self.asked_questions.append(best_ingredient)
        return best_ingredient

    def play(self):
        self.reset()
        
        # Ask for an initial ingredient
        print("Enter an initial ingredient to start:")
        initial_ingredient = input().strip().lower()
        self.asked_questions.append(initial_ingredient)
        self.remove_without_ingredient(initial_ingredient)

        while len(self.recipes) > 1:
            question = self.best_question_to_ask()
            if not question:
                print("No more questions available.")
                break
            
            print(f"Does the recipe contain {question}? (yes/no)")
            answer = input().strip().lower()
            
            if answer == 'yes':
                self.remove_without_ingredient(question)
            elif answer == 'no':
                self.remove_with_ingredient(question)
            else:
                print("Please answer with 'yes' or 'no'.")

            print(f"Remaining recipes: {len(self.recipes)}")

        if len(self.recipes) == 1:
            title = list(self.recipes.values())[0]["displayName"]
            print(f"The recipe is likely: {title}")
        else:
            print("No matching recipe found.")




def load_json():
    with open("./Defs/recipes_data_comp_trans.json", "r") as read_file:
        data = json.load(read_file)
    return data

recipes = load_json()


from OpenSearch import transformer as model
from sklearn.metrics.pairwise import cosine_similarity
import pprint as pp
def ing_embeddings():
    unique_ingredients = set()
    for recipe in recipes:
        ingredients = recipes[recipe]["ingredients"]
        for ing in ingredients:
            ingredient_name = ing["ingredient"].lower().strip()
            if ingredient_name:
                unique_ingredients.add(ingredient_name)
    unique_ingredients = list(unique_ingredients)
    threshold = 0.6
    similar_ingredients_dict = {ingredient: [] for ingredient in unique_ingredients}
    embeddings_cache = {}
 
    # Compute embeddings and fill cache
    for ingredient in unique_ingredients:
        embeddings_cache[ingredient] = model.encode([ingredient])
    print("embeddings computed")
    # Calculate similarities using cached embeddings
    for i in range(len(unique_ingredients)):
        ing_i_embedding = embeddings_cache[unique_ingredients[i]]
        for j in range(i + 1, len(unique_ingredients)):
            ing_j_embedding = embeddings_cache[unique_ingredients[j]]
            similarity = cosine_similarity(ing_i_embedding, ing_j_embedding)
            if similarity > threshold:
                similar_ingredients_dict[unique_ingredients[i]].append(unique_ingredients[j])
                similar_ingredients_dict[unique_ingredients[j]].append(unique_ingredients[i])

    # Save the dictionary to a file
    with open('similar_ingredients.json', 'w') as file:
        json.dump(similar_ingredients_dict, file, indent=4)
    
    return similar_ingredients_dict
    

#print(cosine_similarity(model.encode(["bread"]), model.encode(["bread crumbs"])))
# similar_ingredients_dict = ing_embeddings()
# for ing, similar_ings in similar_ingredients_dict.items():
#     pp.pprint(f"Ingredient: {ing}, Similar Ingredients: {similar_ings}")


# a = Akinator(recipes)
# a.remove_without_ingredient("lasagna noodle")
# a.remove_with_ingredient("egg")
# a.remove_without_ingredient("white onion")
# a.remove_with_ingredient("ginger root")
# a.remove_with_ingredient("no-boil lasagna noodles")
# a.remove_without_ingredient("parmesan cheese")
# a.remove_with_ingredient("vegetable broth")
# print(len(a.recipes), "141"in a.recipes)
# print(a.best_question_to_ask())

a = Akinator(recipes)
a.play()