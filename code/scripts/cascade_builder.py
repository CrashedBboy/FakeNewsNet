import os
from os import path
import shutil
import json

def get_index_in_forest(forest, id):
    for index, cascade in enumerate(forest):
        if cascade['id'] == id:
            return index
    return -1

# BFS
def append_child(type, forest, parent_id, child_id):

    child_index = get_index_in_forest(forest, child_id)

    candidates = forest[:]
    visited = 0

    while visited < len(candidates):
        
        if candidates[visited]['id'] == parent_id:
            if type == 'quote':
                candidates[visited]['quoted_by'].append(forest[child_index])
            if type == 'reply':
                candidates[visited]['replied_by'].append(forest[child_index])
            forest.remove(forest[child_index])

            return (True, forest)
        else:
            candidates += candidates[visited]['quoted_by']
            candidates += candidates[visited]['replied_by']

        visited += 1

    return (False, forest)

NEWS_DIR = "../fakenewsnet_dataset/politifact/fake"
news_count = 0

for item in os.listdir(NEWS_DIR):
    news_dir_path = path.abspath( path.join(path.dirname(__file__), NEWS_DIR, item) )
    
    if path.isdir(news_dir_path):

        news_count += 1
        print(f"{news_count}: {item}")

        # check whether news article exists
        news_path = path.join(news_dir_path, "news content.json")
        if path.exists(news_path):

            # check whether tweets/ dir exists
            tweet_dir_path = path.join(news_dir_path, "tweets")
            if path.exists(tweet_dir_path):

                tweet_filenames = os.listdir(tweet_dir_path)
                cascade_forest = [ {'id': int(fn.split(".")[0]), 'quoted_by': [], 'replied_by': []} for fn in tweet_filenames]
                tweet_filenames = None

                quote_map, reply_map = None, None
                # read quote mapping file
                with open(f"{news_dir_path}/tweet_quote_map.json", "r") as quote_map_file:
                    quote_map = json.loads(quote_map_file.read())

                # read reply mapping file
                with open(f"{news_dir_path}/tweet_reply_map.json", "r") as reply_map_file:
                    reply_map = json.loads(reply_map_file.read())

                if quote_map is None or reply_map is None:
                    print(f"mapping of news {item} is missing!")
                    exit()

                for mapping in quote_map['map']:
                    parent_id = mapping['quoted']
                    child_id = mapping['quoting']

                    # grow cascade tree
                    (result, new_cascade_forest) = append_child('quote', cascade_forest, parent_id, child_id)

                    if result == False:
                        print(f"cannot find parent!! quote, {item}, {parent_id}, {child_id}")
                        print(cascade_forest)
                        print(new_cascade_forest)
                        exit()
                    else:
                        cascade_forest = new_cascade_forest

                for mapping in reply_map['map']:
                    parent_id = mapping['replied']
                    child_id = mapping['replying']

                    # grow cascade tree
                    (result, new_cascade_forest) = append_child('reply', cascade_forest, parent_id, child_id)

                    if result == False:
                        print(f"cannot find parent!! reply, {item}, {parent_id}, {child_id}")
                        print(cascade_forest)
                        print(new_cascade_forest)
                        exit()
                    else:
                        cascade_forest = new_cascade_forest

                # export to file
                with open(f"{news_dir_path}/cascade.json", "w") as cascade_file:
                    cascade_file.write(json.dumps(cascade_forest))
                    

                    