from QNET import *
repeater = QNET.Qnet()

Qnodes = [{'name': 'A', 'coords': [50, 0, 0]},
          {'name': 'B', 'coords': [250, 0, 0]},
          {'name': 'G1', 'qnode_type':'Ground', 'coords': [100, 0, 0]},
          {'name': 'G2', 'qnode_type': 'Ground', 'coords': [200, 0, 0]},
          {'name': 'T', 'qnode_type': 'Swapper', 'coords': [150, 0, 0]},]

repeater.add_qnodes_from(Qnodes)

ebunch = [{'edge': ('A', 'G1'), 'e': 0.9, 'f': 0.9},
          {'edge': ('A', 'G1'), 'e': 0.9, 'f': 0.9},
          {'edge': ('G1', 'T'), 'e': 0.9, 'f': 0.9},
          {'edge': ('T', 'G2'), 'e': 0.9, 'f': 0.9},
          {'edge': ('G2', 'B'), 'e': 0.9, 'f': 0.9},
          ]

repeater.add_qchans_from(ebunch)