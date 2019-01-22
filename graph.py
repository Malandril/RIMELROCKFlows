import json

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# Build your graph
with open("res.json", "r") as f:
    res = json.load(f)
    G = nx.Graph(res)
    # layout = nx.spring_layout(nx.spring_layout(G, k=0.15, iterations=20))
    # Plot it
    nx.draw(G, with_labels=True)
    plt.show()
