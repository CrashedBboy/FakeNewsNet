####
# Statistics: tree depth, #user, #post, max out-degree, depth of node with max degree
####

import os
from os import path
import json

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


NEWS_DIR = "../../fakenewsnet_dataset/politifact/fake"

def tree_depth(root_node):

    max_depth = 1 # itself

    children = [] + root_node["quoted_by"] + root_node["replied_by"] + root_node["retweeted_by"]
    for child in children:
        max_depth = max(max_depth, 1 + tree_depth(child))

    return max_depth

def tree_size(root_node):

    node_count  = 1 # itself

    children = [] + root_node["quoted_by"] + root_node["replied_by"] + root_node["retweeted_by"]
    for child in children:
        node_count += tree_size(child)

    return node_count

def tree_user_number(root_node):

    user_set = set()
    user_set.add(root_node['user'])

    children = [] + root_node["quoted_by"] + root_node["replied_by"] + root_node["retweeted_by"]
    for child in children:
        user_set.update(tree_user_number(child))

    return user_set

def max_out_degree(root_node):

    children = [] + root_node["quoted_by"] + root_node["replied_by"] + root_node["retweeted_by"]

    out_degree = len(children)
    for child in children:
        out_degree = max(out_degree, max_out_degree(child))

    return out_degree

news_count = 0
depths = []
sizes = []
users = []
max_degrees = []
for item in os.listdir(NEWS_DIR):
    news_dir_path = path.abspath( path.join(path.dirname(__file__), NEWS_DIR, item) )
    
    if path.isdir(news_dir_path):

        if not path.exists(f"{news_dir_path}/news content.json"):
            continue

        if not path.exists(f"{news_dir_path}/cascade.json"):
            continue

        news_count += 1
        # if news_count > 10:
        #     break

        with open(f"{news_dir_path}/cascade.json", "r") as cascade_file:
            cascades = json.loads(cascade_file.read())

            for cas in cascades:
                depths.append(tree_depth(cas))
                sizes.append(tree_size(cas))
                users_in_cascade = tree_user_number(cas)
                users.append(len(users_in_cascade))
                max_degrees.append(max_out_degree(cas))

depths = np.array(depths, dtype=np.uint)
sizes = np.array(sizes)
users = np.array(users)
max_degrees = np.array(max_degrees)

print(f"tree depth: min={depths.min()}, max={depths.max()}, mean={depths.mean()}, median={np.median(depths)}")
print(f"cascade size: min={sizes.min()}, max={sizes.max()}, mean={sizes.mean()}, median={np.median(sizes)}")
print(f"user number: min={users.min()}, max={users.max()}, mean={users.mean()}, median={np.median(users)}")
print(f"max degrees: min={max_degrees.min()}, max={max_degrees.max()}, mean={max_degrees.mean()}, median={np.median(max_degrees)}")

# tree depth: min=1, max=43, mean=1.2090589692389353, median=1.0
# cascade size: min=1, max=163, mean=1.89783383464348, median=1.0
# user number: min=1, max=163, mean=1.878581839934619, median=1.0
# max degrees: min=0, max=100, mean=0.6746792036330241, median=0.0

##### tree depth vs cascade size

# scatter plot
plt.scatter(depths, sizes, alpha = 0.15, s = 60)

# linear regression
a, b = np.polyfit(depths, sizes, 1)
plt.plot(depths, a*depths + b, color = "tomato", linewidth = 1.5, linestyle = "--")

plt.xlim(0,18), plt.xlabel("Tree depth"), plt.ylabel("Cascade size")
plt.show()

##### max degree vs cascade size

# scatter plot
plt.scatter(max_degrees, sizes, alpha = 0.1, s = 50)

# linear regression
a, b = np.polyfit(max_degrees, sizes, 1)
plt.plot(max_degrees, a*max_degrees + b, color = "tomato", linewidth = 1.5, linestyle = "--")

plt.xlabel("Max degree"), plt.ylabel("Cascade size")
plt.show()