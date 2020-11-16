"""A linear network of nodes arranged in a semicircle configuration. This allows for easier visualisation
of the swap_reduce method."""
from QNET import *
X = QNET.Qnet()

Qnodes = [{'name': 'A', 'coords': [-1, 0, 0]},
          {'name': 'G1', 'qnode_type':'Ground', 'coords': [-0.866, 0.5, 0]},
          {'name': 'T1', 'qnode_type': 'Swapper', 'coords': [-0.5, 0.866, 0]},
          {'name': 'G2', 'qnode_type': 'Ground', 'coords': [0, 1, 0]},
          {'name': 'T2', 'qnode_type': 'Swapper', 'coords': [0.5, 0.866, 0]},
          {'name': 'G3', 'qnode_type': 'Ground', 'coords': [0.866, 0.5, 0]},
          {'name': 'B', 'coords': [1, 0, 0]}]

X.add_qnodes_from(Qnodes)

ebunch = [{'edge': ('A', 'G1'), 'e': 1, 'f': 1},
          {'edge': ('G1', 'T1'), 'e': 1, 'f': 1},
          {'edge': ('T1', 'G2'), 'e': 1, 'f': 1},
          {'edge': ('G2', 'T2'), 'e': 1, 'f': 1},
          {'edge': ('T2', 'G3'), 'e': 1, 'f': 1},
          {'edge': ('G3', 'B'), 'e': 1, 'f': 1}
          ]

X.add_qchans_from(ebunch)