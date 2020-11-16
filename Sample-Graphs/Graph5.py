import QNET

X = QNET.Qnet()

Qnodes = [{'name': 'A'},
          {'name': 'B'},
          {'name': 'G1', 'qnode_type':'Ground'},
          {'name': 'G2', 'qnode_type': 'Ground'},
          {'name': 'T1', 'qnode_type': 'Swapper'},
          {'name': 'G3', 'qnode_type': 'Ground'},
          {'name': 'G4', 'qnode_type': 'Ground'},
          {'name': 'T2', 'qnode_type': 'Swapper'}]

X.add_qnodes_from(Qnodes)

ebunch = [{'edge': ('A', 'G1'), 'e': 0.9, 'f': 0.9},
          {'edge': ('G1', 'T1'), 'e': 0.9, 'f': 0.9},
          {'edge': ('T1', 'G2'), 'e': 0.9, 'f': 0.9},
          {'edge': ('G2', 'B'), 'e': 0.9, 'f': 0.9},
          {'edge': ('A', 'G3'), 'e': 0.9, 'f': 0.9},
          {'edge': ('G3', 'T2'), 'e': 0.9, 'f': 0.9},
          {'edge': ('T2', 'G4'), 'e': 0.9, 'f': 0.9},
          {'edge': ('G4', 'B'), 'e': 0.9, 'f': 0.9}
          ]

X.add_qchans_from(ebunch)