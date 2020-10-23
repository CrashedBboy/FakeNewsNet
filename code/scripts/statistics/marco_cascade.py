####
# Statistics: fraction of cascade having at least 2 nodes
####

import os
from os import path
import numpy as np

import json

NEWS_DIR = "../../fakenewsnet_dataset/politifact/fake"

def tree_depth(root_node):

    max_depth = 1 # itself

    children = [] + root_node["quoted_by"] + root_node["replied_by"] + root_node["retweeted_by"]
    for child in children:
        max_depth = max(max_depth, 1 + tree_depth(child))

    return max_depth

news_count = 0
fractions = []
for item in os.listdir(NEWS_DIR):
    news_dir_path = path.abspath( path.join(path.dirname(__file__), NEWS_DIR, item) )
    
    if path.isdir(news_dir_path):

        if not path.exists(f"{news_dir_path}/news content.json"):
            continue

        if not path.exists(f"{news_dir_path}/cascade.json"):
            continue

        news_count += 1
        # if news_count > 3:
        #     exit()

        with open(f"{news_dir_path}/cascade.json", "r") as cascade_file:
            cascades = json.loads(cascade_file.read())

            cascade_depths = []
            for cas in cascades:
                cascade_depths.append(tree_depth(cas))

            cascade_depths = np.array(cascade_depths)
            frac = len(cascade_depths[cascade_depths>1]) / len(cascade_depths)
            fractions.append(frac)

            print(f"{item}: {frac}")

fractions = np.array(fractions)

print(f"fraction of cascades having >= 2 nodes: min={fractions.min()}, max={fractions.max()}, mean={fractions.mean()}, median={np.median(fractions)}")
# fraction of cascades having >= 2 nodes: min=0.0, max=1.0, mean=0.14256603529782425, median=0.11320754716981132