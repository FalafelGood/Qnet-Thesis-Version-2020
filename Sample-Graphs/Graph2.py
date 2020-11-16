#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 14:09:24 2020

Linear network with two ground nodes, a swapper node, and one satellite

@author: hudson
"""
import QNET

X = QNET.Qnet()

Qnodes = [{'name': 'A', 'coords': [50, 0, 0]},
          {'name': 'B', 'coords': [250, 0, 0]},
          {'name': 'G1', 'qnode_type':'Ground', 'coords': [100, 0, 0]},
          {'name': 'G2', 'qnode_type': 'Ground', 'coords': [200, 0, 0]},
          {'name': 'T', 'qnode_type': 'Swapper', 'coords': [150, 0, 0]},
          {'name': 'S', 'qnode_type': 'Satellite', 'coords': [0, 0, 100], 'v_cart': [30, 0], 'range':100}]

X.add_qnodes_from(Qnodes)

ebunch = [{'edge': ('A', 'G1'), 'e': 0.9, 'f': 0.9},
          {'edge': ('G1', 'T'), 'e': 0.9, 'f': 0.9},
          {'edge': ('T', 'G2'), 'e': 0.9, 'f': 0.9},
          {'edge': ('G2', 'B'), 'e': 0.9, 'f': 0.9},
          {'edge': ('S', 'A')},
          {'edge': ('S', 'B')}
          ]

X.add_qchans_from(ebunch)