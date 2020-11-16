"""
A static tripartite graph much like the one used in Graph4
"""

import networkx as nx
import QNET

X = QNET.Qnet()

nbunch = [{'name':'A', 'coords': [0, 50, 0]},
          {'name':'B', 'coords': [100, 50, 0]},
          {'name':'G1', 'qnode_type': 'Ground', 'coords': [50, 110, 0]},
          {'name':'G2', 'qnode_type': 'Ground', 'coords': [50, -10, 0]}]

ebunch = [{'edge': ('A', 'G1'), 'f': 0.7},
          {'edge': ('A', 'G2'), 'f': 0.70},
          {'edge': ('B', 'G1'), 'f': 0.70},
          {'edge': ('B', 'G2'), 'f': 0.70}]

X.add_qnodes_from(nbunch)
X.add_qchans_from(ebunch)