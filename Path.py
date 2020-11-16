#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 12:00:05 2020

@author: hudson
"""

import networkx as nx
import QNET
import numpy as np
import collections
import copy


class Path:
    def __init__(self, G, array, edge_keys=None):
        """
        Initialization method for the Qnet Path class

        Parameters
        ----------
        G: Qnet()
        array: list
            List of nodes in the path
        edge_keys:
            List of edge keys. Since Qnet is a multigraph, reference to the networkx edge keys is essential in order
            to fully distinguish paths that follow the same sequence of nodes.
        """
        assert (isinstance(G, QNET.Qnet)), "path.__init__ requires reference to the graph containing the path"
        assert (array != None), "path.__init__ received an empty array"

        # Build node array from what was given in array
        node_array = []
        for node in array:
            node = G.getNode(node)
            assert node is not None
            node_array.append(node)

        # If edge_keys is None, assume each key is is default "0"
        if edge_keys is None:
            edge_keys = [0] * (len(node_array) - 1)

        self.G = G
        self.node_array = node_array
        self.edge_keys = edge_keys
        self.head = node_array[0]
        self.tail = node_array[len(self.node_array) - 1]
        self.cost_vector = self.get_cost_vector()

        # Assert path is valid in G
        # Maybe we could just incorperate this into is_valid instead?
        if all([(node_array[i], node_array[i + 1]) in G.edges() \
                or (node_array[i + 1], node_array[i]) in G.edges() for i in range(len(node_array) - 1)]):
            pass
        else:
            assert False, f"Path {self.stringify()} does not exist in Qnet."

    def __str__(self):
        return "Path: " + self.stringify() + ", Cost: " + str(self.cost_vector)
        # return self.stringify()

    def __repr__(self):
        return self.stringify()

    def is_valid(self):
        """
        Checks to see if the given path is valid for entanglement distribution.
        :return: Boolean
        """
        has_ground = False
        for node in self.node_array:
            if isinstance(node, QNET.Ground) or isinstance(node, QNET.Satellite):
                has_ground = True
                break
        return has_ground

    def get_cost_vector(self):
        # List of cost vectors for all elements in the path:
        element_cvs = []

        # Get cost vectors of edges
        path_len = len(self.node_array)
        i = 0
        while i < path_len - 1:
            cur = self.node_array[i]
            nxt = self.node_array[i + 1]
            # TODO: Add key key here to make it more clear
            edge_data = self.G.get_edge_data(cur, nxt, self.edge_keys[i])
            element_cvs.append(edge_data)
            i += 1

        # Get cost vectors of nodes
        for node in self.node_array:
            element_cvs.append(node.costs)

        # Cost vectors have identical keys
        # Sum all key elements together, convert additive costs to correct value, update dictionary
        def sum_cost_vectors(cv_list):
            counter = collections.Counter()
            for d in cv_list:
                counter.update(d)
            return dict(counter)

        new_cv = sum_cost_vectors(element_cvs)
        # Convert additive costs into regular costs:
        for cost_type in new_cv:
            if cost_type.startswith("add_"):
                # Get additive cost
                cost = new_cv[cost_type]
                # Remove prefix of cost_type
                cost_type = QNET.remove_prefix(cost_type, "add_")
                # Convert additive cost to normal, add it to new_cv
                new_cv[cost_type] = self.G.conversions[cost_type][1](cost)

        return new_cv

    # TODO Test this
    def subgraph(self):
        return self.G.subgraph(self.array)

    def stringify(self):
        """
        Returns
        -------
        pString : str
            Stringified version of the path

        """
        # Given a path, returns a string of the path
        pString = ""
        i = 0
        while i < len(self.node_array):
            pString = pString + str(self.node_array[i].name)
            i += 1
            if i < len(self.node_array):
                pString = pString + "-"
        return pString

    def remove_edges(self):
        """
        Remove all edges in path from the graph G
        :return: None
        """
        path_len = len(self.node_array)
        i = 0
        while i < path_len - 1:
            cur = self.node_array[i]
            nxt = self.node_array[i + 1]
            key = self.edge_keys[i]
            self.G.remove_edge(cur, nxt, key)
            i += 1

    def update(self):
        self.cost_vector = self.get_cost_vector()

    def swap_path(self):
        """
        Perform the swapping operation with all valid swapper nodes in the path.
        A swapper is valid if there exist ground nodes at any point on its adjacent sides.

        Returns:
            cost_vector
        -------
        """
        # Does a ground exist before a potential swapper?
        ground_switch = False
        # Variable storing a potential swapper
        swapper = None
        # Swap costs of valid swapper nodes
        swap_costs = []

        for node in self.node_array:
            if isinstance(node, QNET.Ground):
                if ground_switch is False:
                    ground_switch = True
                elif swapper is not None:
                    swap_costs.append(swapper.swap_prob)
                    swapper = None
                    # ground_switch = False

            if isinstance(node, QNET.Swapper) and ground_switch is True:
                swapper = node

        swap_cost = 1
        for cost in swap_costs:
            swap_cost *= cost

        new_cv = copy.copy(self.cost_vector)
        new_cv['e'] = new_cv['e'] * swap_cost
        return new_cv


