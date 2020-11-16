#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 6 10:32:19 2020

Static tripartite graph

@author: hudson
"""

import networkx as nx
import QNET

X = QNET.Qnet()

nbunch = [{'name':'A', 'coords': [0, 50, 0], 'f':0.9},
          {'name':'B', 'coords': [100, 50, 0], 'f':0.9},
          {'name':'G1', 'qnode_type': 'Ground', 'coords': [50, 10, 0], 'f':0.95},
          {'name':'G2', 'qnode_type': 'Ground', 'coords': [50, 30, 0], 'f':0.90},
          {'name':'G3', 'qnode_type': 'Ground', 'coords': [50, 50, 0], 'f':0.85},
          {'name':'G4', 'qnode_type': 'Ground', 'coords': [50, 70, 0], 'f':0.80},
          {'name':'G5', 'qnode_type': 'Ground', 'coords': [50, 90, 0], 'f':0.75}]

ebunch = [{'edge': ('A', 'G1'), 'f': 0.95},
          {'edge': ('A', 'G2'), 'f': 0.90},
          {'edge': ('A', 'G3'), 'f': 0.85},
          {'edge': ('A', 'G4'), 'f': 0.80},
          {'edge': ('A', 'G5'), 'f': 0.75},
          {'edge': ('B', 'G1'), 'f': 0.95},
          {'edge': ('B', 'G2'), 'f': 0.90},
          {'edge': ('B', 'G3'), 'f': 0.85},
          {'edge': ('B', 'G4'), 'f': 0.80},
          {'edge': ('B', 'G5'), 'f': 0.75}]

X.add_qnodes_from(nbunch)
X.add_qchans_from(ebunch)