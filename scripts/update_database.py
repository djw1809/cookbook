import json
import os
import subprocess
#https://docs.python.org/3/howto/logging.html
def check_update_folder(update_folder = "../recipes_update/", recipes_master_folder = "../recipes_master", db_path = "../db/db.json"):
    return_string = subprocess.check_output(["ls", update_folder], universal_newlines = True, encoding = 'utf-8')
    if len(return_string) == 0: #ls returns '' when folder is empty
        print("nothing in update folder")
        #LOG MESSAGE
        return
    else:
        folder_names = return_string.split('\n') #get name of each folder in update_folder
        folder_names = folder_names[:len(folder_names)-1] #strip off the empty string caused by the newline ubuntu always appends to the output of ls a folder is nonempty
        print("processing recipes {}".format(folder_names))
        #LOG MESSAGE
        #check folder for recipe
        for folder in folder_names:
            folder_path = update_folder + folder +"/"
            folder_contents = subprocess.check_output(["ls", folder_path], universal_newlines = True, encoding = 'utf-8').split('\n')

            for file in folder_contents:
                if file.lower().endswith(('.txt', '.json')): #process first recipe found (there should only be one recipe in a recipe folder)
                    recipe_filename = file
                    recipe_filepath = folder_path + recipe_filename
                    print("found recipe file {} - processing".format(recipe_filename))
                    #LOG MESSAGE
                    try:
                        process_recipe_file(recipe_filepath, db_path)
                        subprocess.run(["mv", folder_path, recipes_master_folder])
                        break
                    except Exception as e:
                        print("error processing recipe file".format(recipe_filename))
                        print(e)
                        break
                        #LOG MESSAGE

            else: #if a recipe wasn't found move on to the next folder
                print("no recipe file found in {}")
                #LOG MESSAGE
        return

def process_recipe_file(recipe_filepath, db_path):

    if recipe_filepath.lower().endswith('.json'):
        with open(recipe_filepath, 'rb') as file:
            recipe_object = json.load(file)
            update_db(recipe_object, db_path)

    else:
        with open(recipe_filepath, 'r') as f:
            raw_recipe = f.read()

        recipe_object = {'recipe_name': '' ,
                          'ingredients': '',
                          'prep': '',
                          'recipe': ''}
        components = raw_recipe.replace('\n', '').strip().split('$')



        recipe_object['recipe_name'] = components[0].strip()
        recipe_object['ingredients'] = {ingred.split(':')[0].strip(): ingred.split(':')[1].strip() for ingred in components[1].split('&') if len(ingred.strip()) > 0 }
        recipe_object['prep'] = [step.strip() for step in components[2].split('&') if len(step.strip()) > 0]
        recipe_object['recipe'] = [step.strip() for step in components[3].split('&') if len(step.strip()) > 0]

        update_db(recipe_object, db_path)
        return recipe_object


def update_db(recipe_object, db_path):
    with open(db_path, 'r') as f:
        db = json.load(f)
    subprocess.run(["rm", db_path])

    db[recipe_object['recipe_name']] = recipe_object

    with open(db_path, 'w') as f:
        json.dump(db, f)

    print("updated")
    return
