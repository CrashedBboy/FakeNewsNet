####
# Statistics:
# out-degree centrality
# in-degree centrality
# closeness centrality
# betweenness centrality
# graph diameter
# #node ( = #user)
# #edge
####

import os
from os import path
import json

import numpy as np
import matplotlib.pyplot as plt

import networkx as nx

DATASET_DIR = "../../fakenewsnet_dataset"
DATASET_DIR = path.abspath( path.join(path.dirname(__file__), DATASET_DIR) )

NEWS_DIR = f"{DATASET_DIR}/politifact/fake"

U_FOLLOWER_LIST_DIR = f"{DATASET_DIR}/user_followers"
RT_FOLLOWER_LIST_DIR = f"{DATASET_DIR}/rt_user_followers"

def tree_size(root_node):

    node_count  = 1 # itself

    children = [] + root_node["quoted_by"] + root_node["replied_by"] + root_node["retweeted_by"]
    for child in children:
        node_count += tree_size(child)

    return node_count

def tree_user_set(root_node):

    user_set = set()
    user_set.add(root_node['user'])

    children = [] + root_node["quoted_by"] + root_node["replied_by"] + root_node["retweeted_by"]
    for child in children:
        user_set.update(tree_user_set(child))

    return user_set

def get_follower_list(uid):

    if path.exists(f"{U_FOLLOWER_LIST_DIR}/{uid}.json"):

        with open(f"{U_FOLLOWER_LIST_DIR}/{uid}.json", "r") as follower_list_file:
            return json.loads(follower_list_file.read())['followers']

    elif path.exists(f"{RT_FOLLOWER_LIST_DIR}/{uid}.json"):

        with open(f"{RT_FOLLOWER_LIST_DIR}/{uid}.json", "r") as follower_list_file:
            return json.loads(follower_list_file.read())['followers']

    else:
        return []

news_count = 0
sizes = []
max_out_degrees = []
avg_out_degrees = []
max_in_degrees = []
avg_in_degrees = []
max_closeness = []
avg_closeness = []
max_betweenness = []
avg_betweenness = []
node_numbers = []
edge_numbers = []
for item in os.listdir(NEWS_DIR):
    news_dir_path = f"{NEWS_DIR}/{item}"
    
    if path.isdir(news_dir_path):

        if not path.exists(f"{news_dir_path}/news content.json"):
            continue

        if not path.exists(f"{news_dir_path}/cascade.json"):
            continue

        news_count += 1
        print(f"{news_count}: {item}")
        # if news_count > 5:
        #     break

        with open(f"{news_dir_path}/cascade.json", "r") as cascade_file:
            cascades = json.loads(cascade_file.read())

            for cas in cascades:
                sizes.append(tree_size(cas))
                users_in_cascade = tree_user_set(cas)

                G = nx.DiGraph()

                # add vertex(user)
                for u in users_in_cascade:
                    G.add_node(u)

                # get all user's follower list
                follower_map = {}
                for u in users_in_cascade:
                    follower_map[u] = get_follower_list(u)

                # add directed edges
                for u1 in users_in_cascade:
                    for u2 in users_in_cascade:
                        if u1 == u2:
                            continue

                        if u2 in follower_map[u1]:
                            G.add_edge(u2, u1)

                follower_map = None # clear up

                # out-degree
                out_degree_tuples = list(G.out_degree(list(users_in_cascade))) # retrun [(uid, degree), ...]
                out_degrees = np.array([ degree for (uid, degree) in out_degree_tuples])
                max_out_degrees.append(out_degrees.max())
                avg_out_degrees.append(out_degrees.mean())

                # in-degree
                in_degree_tuples = list(G.in_degree(list(users_in_cascade))) # retrun [(uid, degree), ...]
                in_degrees = np.array([ degree for (uid, degree) in in_degree_tuples])
                max_in_degrees.append(in_degrees.max())
                avg_in_degrees.append(in_degrees.mean())

                # closeness centrality
                closeness = list(nx.closeness_centrality(G).values())
                closeness = np.array(closeness)
                max_closeness.append(closeness.max())
                avg_closeness.append(closeness.mean())

                # betweenness centrality
                betweenness = list(nx.betweenness_centrality(G).values())
                betweenness = np.array(betweenness)
                max_betweenness.append(betweenness.max())
                avg_betweenness.append(betweenness.mean())

                # node number
                node_numbers.append(G.number_of_nodes())

                # edge number
                edge_numbers.append(G.size())

sizes = np.array(sizes)
max_out_degrees = np.array(max_out_degrees)
avg_out_degrees = np.array(avg_out_degrees)
max_in_degrees = np.array(max_in_degrees)
avg_in_degrees = np.array(avg_in_degrees)
max_closeness = np.array(max_closeness)
avg_closeness = np.array(avg_closeness)
max_betweenness = np.array(max_betweenness)
avg_betweenness = np.array(avg_betweenness)
node_numbers = np.array(node_numbers)
edge_numbers = np.array(edge_numbers)

print(f"avg out-degree: min={avg_out_degrees.min()}, max={avg_out_degrees.max()}, \
    mean={avg_out_degrees.mean()}, Q1 = {np.percentile(avg_out_degrees, 25)}, \
        median={np.median(avg_out_degrees)}, Q3 = {np.percentile(avg_out_degrees, 75)}")

print(f"max out-degree: min={max_out_degrees.min()}, max={max_out_degrees.max()}, \
    mean={max_out_degrees.mean()}, Q1 = {np.percentile(max_out_degrees, 25)}, \
        median={np.median(max_out_degrees)}, Q3 = {np.percentile(max_out_degrees, 75)}")

print(f"max in-degree: min={max_in_degrees.min()}, max={max_in_degrees.max()}, \
    mean={max_in_degrees.mean()}, Q1 = {np.percentile(max_in_degrees, 25)}, \
        median={np.median(max_in_degrees)}, Q3 = {np.percentile(max_in_degrees, 75)}")

print(f"avg in-degree: min={avg_in_degrees.min()}, max={avg_in_degrees.max()}, \
    mean={avg_in_degrees.mean()}, Q1 = {np.percentile(avg_in_degrees, 25)}, \
        median={np.median(avg_in_degrees)}, Q3 = {np.percentile(avg_in_degrees, 75)}")

print(f"max closeness: min={max_closeness.min()}, max={max_closeness.max()}, \
    mean={max_closeness.mean()}, Q1 = {np.percentile(max_closeness, 25)}, \
        median={np.median(max_closeness)}, Q3 = {np.percentile(max_closeness, 75)}")

print(f"avg closeness: min={avg_closeness.min()}, max={avg_closeness.max()}, \
    mean={avg_closeness.mean()}, Q1 = {np.percentile(avg_closeness, 25)}, \
        median={np.median(avg_closeness)}, Q3 = {np.percentile(avg_closeness, 75)}")

print(f"max betweenness: min={max_betweenness.min()}, max={max_betweenness.max()}, \
    mean={max_betweenness.mean()}, Q1 = {np.percentile(max_betweenness, 25)}, \
        median={np.median(max_betweenness)}, Q3 = {np.percentile(max_betweenness, 75)}")

print(f"avg betweenness: min={avg_betweenness.min()}, max={avg_betweenness.max()}, \
    mean={avg_betweenness.mean()}, Q1 = {np.percentile(avg_betweenness, 25)}, \
        median={np.median(avg_betweenness)}, Q3 = {np.percentile(avg_betweenness, 75)}")

print(f"node number: min={node_numbers.min()}, max={node_numbers.max()}, \
    mean={node_numbers.mean()}, Q1 = {np.percentile(node_numbers, 25)}, \
        median={np.median(node_numbers)}, Q3 = {np.percentile(node_numbers, 75)}")

print(f"edge number: min={edge_numbers.min()}, max={edge_numbers.max()}, \
    mean={edge_numbers.mean()}, Q1 = {np.percentile(edge_numbers, 25)}, \
        median={np.median(edge_numbers)}, Q3 = {np.percentile(edge_numbers, 75)}")


# filter out cascade whose size = 1
max_out_degrees = max_out_degrees[sizes > 1]
avg_out_degrees = avg_out_degrees[sizes > 1]
max_in_degrees = max_in_degrees[sizes > 1]
avg_in_degrees = avg_in_degrees[sizes > 1]
max_closeness = max_closeness[sizes > 1]
avg_closeness = avg_closeness[sizes > 1]
max_betweenness = max_betweenness[sizes > 1]
avg_betweenness = avg_betweenness[sizes > 1]

##### avg out-degree vs cascade size

# scatter plot
plt.scatter(avg_out_degrees, sizes[sizes > 1], alpha = 0.1, s = 50)

# linear regression
a, b = np.polyfit(avg_out_degrees, sizes[sizes > 1], 1)
plt.plot(avg_out_degrees, a*avg_out_degrees + b, color = "tomato", linewidth = 1.5, linestyle = "--")

plt.xlabel("Average out-degree"), plt.ylabel("Cascade size")
plt.show()

##### max out-degree vs cascade size

# scatter plot
plt.scatter(max_out_degrees, sizes[sizes > 1], alpha = 0.1, s = 50)

# linear regression
a, b = np.polyfit(max_out_degrees, sizes[sizes > 1], 1)
plt.plot(max_out_degrees, a*max_out_degrees + b, color = "tomato", linewidth = 1.5, linestyle = "--")

plt.xlabel("Max out-degree"), plt.ylabel("Cascade size")
plt.show()

##### avg in-degree vs cascade size

# scatter plot
plt.scatter(avg_in_degrees, sizes[sizes > 1], alpha = 0.1, s = 50)

# linear regression
a, b = np.polyfit(avg_in_degrees, sizes[sizes > 1], 1)
plt.plot(avg_in_degrees, a*avg_in_degrees + b, color = "tomato", linewidth = 1.5, linestyle = "--")

plt.xlabel("Average in-degree"), plt.ylabel("Cascade size")
plt.show()

##### max in-degree vs cascade size

# scatter plot
plt.scatter(max_in_degrees, sizes[sizes > 1], alpha = 0.1, s = 50)

# linear regression
a, b = np.polyfit(max_in_degrees, sizes[sizes > 1], 1)
plt.plot(max_in_degrees, a*max_in_degrees + b, color = "tomato", linewidth = 1.5, linestyle = "--")

plt.xlabel("Max in-degree"), plt.ylabel("Cascade size")
plt.show()

##### max closeness centrality vs cascade soze
# scatter plot
plt.scatter(max_closeness, sizes[sizes > 1], alpha = 0.1, s = 50)

# linear regression
a, b = np.polyfit(max_closeness, sizes[sizes > 1], 1)
plt.plot(max_closeness, a*max_closeness + b, color = "tomato", linewidth = 1.5, linestyle = "--")

plt.xlabel("Max closeness centrality"), plt.ylabel("Cascade size")
plt.show()

##### avg closeness centrality vs cascade soze
# scatter plot
plt.scatter(avg_closeness, sizes[sizes > 1], alpha = 0.1, s = 50)

# linear regression
a, b = np.polyfit(avg_closeness, sizes[sizes > 1], 1)
plt.plot(avg_closeness, a*avg_closeness + b, color = "tomato", linewidth = 1.5, linestyle = "--")

plt.xlabel("Avg closeness centrality"), plt.ylabel("Cascade size")
plt.show()

##### max betweenness centrality vs cascade soze
# scatter plot
plt.scatter(max_betweenness, sizes[sizes > 1], alpha = 0.1, s = 50)

# linear regression
a, b = np.polyfit(max_betweenness, sizes[sizes > 1], 1)
plt.plot(max_betweenness, a*max_betweenness + b, color = "tomato", linewidth = 1.5, linestyle = "--")

plt.xlabel("Max betweenness centrality"), plt.ylabel("Cascade size")
plt.show()

##### avg betweenness centrality vs cascade soze
# scatter plot
plt.scatter(avg_betweenness, sizes[sizes > 1], alpha = 0.1, s = 50)

# linear regression
a, b = np.polyfit(avg_betweenness, sizes[sizes > 1], 1)
plt.plot(avg_betweenness, a*avg_betweenness + b, color = "tomato", linewidth = 1.5, linestyle = "--")

plt.xlabel("Avg betweenness centrality"), plt.ylabel("Cascade size")
plt.show()


#avg out-degree: min=0.0, max=29.548387096774192,     mean=0.08767661104184948, Q1 = 0.0,         median=0.0, Q3 = 0.0
#max out-degree: min=0, max=89,     mean=0.2941553134662858, Q1 = 0.0,         median=0.0, Q3 = 0.0
#max in-degree: min=0, max=77,     mean=0.21365922705558224, Q1 = 0.0,         median=0.0, Q3 = 0.0
#avg in-degree: min=0.0, max=29.548387096774192,     mean=0.08767661104184948, Q1 = 0.0,         median=0.0, Q3 = 0.0
#max closeness: min=0.0, max=1.0,     mean=0.06460233093064978, Q1 = 0.0,         median=0.0, Q3 = 0.0
#avg closeness: min=0.0, max=1.0,     mean=0.041000610081774705, Q1 = 0.0,         median=0.0, Q3 = 0.0
#max betweenness: min=0.0, max=1.0,     mean=0.007285345386291383, Q1 = 0.0,         median=0.0, Q3 = 0.0
#avg betweenness: min=0.0, max=0.3333333333333333,     mean=0.002030984490669036, Q1 = 0.0,         median=0.0, Q3 = 0.0
#node number: min=1, max=163,     mean=1.878581839934619, Q1 = 1.0,         median=1.0, Q3 = 1.0
#edge number: min=0, max=2748,     mean=1.3941140291012646, Q1 = 0.0,         median=0.0, Q3 = 0.0