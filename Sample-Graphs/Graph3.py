#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 13:44:28 2020

Small static tripartite graph without node costs

@author: hudson
"""

import networkx as nx
import QNET

X = QNET.Qnet()

nbunch = [{'name':'A', 'coords':[0, 50, 0]},
          {'name':'B', 'coords':[200, 50, 0]},
          {'name':'G1', 'qnode_type': 'Ground', 'coords':[100, 20, 0]},
          {'name':'G2', 'qnode_type': 'Ground', 'coords':[100, 40, 0]},
          {'name':'G3', 'qnode_type': 'Ground', 'coords':[100, 60, 0]}]

ebunch = [{'edge': ('A', 'G1'), 'e': 0.9, 'f': 0.9},
          {'edge': ('A', 'G2'), 'e': 0.8, 'f': 0.8},
          {'edge': ('A', 'G3'), 'e': 0.7, 'f': 0.7},
          {'edge': ('B', 'G1'), 'e': 0.9, 'f': 0.9},
          {'edge': ('B', 'G2'), 'e': 0.8, 'f': 0.8},
          {'edge': ('B', 'G3'), 'e': 0.7, 'f': 0.7}]

X.add_qnodes_from(nbunch)
X.add_qchans_from(ebunch)