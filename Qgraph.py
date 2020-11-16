#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 17:22:47 2020
@author: hudson
"""

import networkx as nx
import QNET
from typing import Callable

typeDict = {'Ground': QNET.Ground,
            'Satellite': QNET.Satellite,
            'Swapper': QNET.Swapper}


class Qnet(nx.MultiGraph):
    def __init__(self, cost_vector=None, cost_ranges=None, conversions=None, memory_vector=None, memory_ranges=None, memory_conversions=None, incoming_graph_data=None, **attr):
        """
        Initialization method for the Qnet class.

        The Qnet class is the

        Parameters
        ----------
        cost_vector: dict [str, float], optional
            Dictionary between cost types and values

            cost_vector is a dictionary containing costs and values. All objects in the Qnet graph are initialized with
            this object. All costs are assumed to be multiplicative (like probability) unless the cost has the prefix
            "add_", in which case it will be additive. The keys in cost_vector are the valid costs for the Qnet graph,
            and the values are the default magnitudes of these costs.

            (The default is None, which gives cost_vector = {'e':1, 'p':1, 'add_e':0, 'add_p':0})

        cost_ranges: dict [str, (float, float)], optional
            Dictionary between cost types and their valid range

            All costs in Qnet must have a corresponding range. The first item in the tuple is the minimum value of the
            cost, and the second item is the maximum.

        conversions: dict [str, (function, function)], optional
            Dictionary between cost types and conversion methods to and from the respective additive cost

            All costs in Qnet must have an additive analogue for classic networking protocols like shortest path cost
            to be well defined. For example, a multiplicative cost like efficiency (the proportion of photons that
            successfully pass through an element) can be made into an additive cost by taking its log. The first
            function in the tuple is the conversion to the additive cost, and the second is the conversion from the
            additive cost. The convention we recommend for naming these functions is "cost_type_to_add" and
            "cost_type_from_add" Each function must take a float as an input and return a float as an output.

            (The default is None, which gives conversions = {'e':[to_log, from_log], 'f':[to_add_f, from_add_f]})

        incoming_graph_data:
            Additional NetworkX graph data

            See NetworkX Documentation
            https://networkx.github.io/documentation/stable/reference/classes/graph.html#methods

        attr:
            Additional NetworkX attributes

            See NetworkX Documentation
            https://networkx.github.io/documentation/stable/reference/classes/graph.html#methods

        Attributes
        ----------
        cost_vector
        cost_ranges
        conversions

        Examples
        --------
        Create an instance of a Qnet with a custom cost vector
        >>> cv = {"a":1}
        >>> ranges = {"a":(0,100)}
        >>> a_to_add = lambda a: (a+1)
        >>> a_from_add = lambda a: (a-1)
        >>> conversions = {"a": [a_to_add, a_from_add]}
        >>> Q = Qnet(cost_vector = cv, cost_ranges = ranges, conversions = conversions)
        >>> print(Q)
        """

        if cost_vector is None and conversions is None:
            cost_vector = {'e': 1, 'f': 1}
            cost_ranges = {'e': (0, 1), 'f': (0.5, 1)}
            conversions = {'e': [QNET.to_log, QNET.from_log], 'f': [QNET.to_add_f, QNET.from_add_f]}
        else:
            assert set(cost_vector.keys()) == set(cost_ranges.keys()), \
                "Keys in \"cost_vector\" do not match keys in \"cost_ranges\""
            assert set(cost_vector.keys()) == set(conversions.keys()), \
                "Keys in \"cost_vector\" do not match keys in \"conversions\""
            for rng in cost_ranges.values():
                assert(len(rng) == 2),\
                    "Usage: cost_ranges = {cost: (min_val, max_val)}"
            for functions in conversions.values():
                assert(len(functions) == 2),\
                    "Usage: conversions = {'cost': [convert_to_additive, convert_to_multiplicative]}"


        if memory_vector is None and memory_conversions is None:
            memory_vector = {'mem_e': 1, 'mem_f': 1}
            memory_ranges = {'mem_e': (0, 1), 'mem_f': (0.5, 1)}
            memory_conversions = {'mem_e': [QNET.to_log, QNET.from_log], 'mem_f': [QNET.to_add_f, QNET.from_add_f]}
        else:
            assert set(memory_vector.keys()) == set(memory_ranges.keys()), \
                "Keys in \"cost_vector\" do not match keys in \"cost_ranges\""
            assert set(memory_vector.keys()) == set(conversions.keys()), \
                "Keys in \"cost_vector\" do not match keys in \"conversions\""
            for rng in memory_ranges.values():
                assert(len(rng) == 2),\
                    "Usage: cost_ranges = {cost: (min_val, max_val)}"
            for functions in conversions.values():
                assert(len(functions) == 2),\
                    "Usage: conversions = {'cost': [convert_to_additive, convert_to_multiplicative]}"

        self.cost_vector = cost_vector
        self.cost_ranges = cost_ranges
        self.conversions = conversions

        self.memory_vector = memory_vector
        self.memory_ranges = memory_ranges
        self.memory_conversions = memory_conversions
        super().__init__(incoming_graph_data, **attr)

    def __str__(self):
        qnodes = ""
        if len(self.nodes()) == 0:
            qnodes += "None\n"
        else:
            for node in self.nodes():
                qnodes += "Name: " + "\"" + node.name + "\"" + '\n' \
                          + str(type(node)) + '\n' \
                          + "Coordinates: " + str(node.coords) + '\n' \
                          + "Costs: " + str(node.costs) + '\n'
                if isinstance(node, QNET.Satellite):
                    qnodes += "Cartesian == " + str(node.cartesian) + '\n'
                    if node.cartesian == True:
                        qnodes += "Velocity == " + str(node.velocity) + '\n'
                if isinstance(node, QNET.Swapper):
                    qnodes += "Swap probability == " + str(node.swap_prob) + '\n'

                qnodes += "\n"

        qchans = ""
        if len(self.edges()) == 0:
            qchans += "None\n"
        else:
            for chan in self.edges:
                edge_data = self.edges[chan]
                qchans += str(chan[0].name + " <--> " + chan[1].name + '\n' +
                              "Costs: " + str(edge_data))
                qchans += "\n"

        return (f"-- Default cost vector --\n{self.cost_vector}\n"
                f"-- Cost ranges -- \n{self.cost_ranges}\n"
                f"\n-- Qnodes --\n{qnodes}-- Qchans --\n{qchans}")

    def add_qnode(self, name=None, qnode_type=None, coords=None, **kwargs):
        """
        Initialize a qnode of some type and add it to the graph

        In the event where a node of the same name is initialised, update the old node with new parameters

        Parameters
        ----------
        name: str
            Node name

        qnode_type: str {'Ground', "Satellite', 'Swapper'}, optional
            Qnode subclass

            (The default is None, which initializes a Qnode of the default type)

        kwargs
            Keyword arguments for qnode initialization

            For details, consult the documentation for the Node class

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If the qnode_type is invalid
        """
        # Check if node already exists in graph. If yes, update old node
        old_node = self.getNode(name)
        if old_node is not None:
            old_node.update(self, name=name, coords=coords, **kwargs)
        # Else, add new node
        else:
            # If qnode_type is none, initialize a node of the default type
            if qnode_type is None:
                new_node = QNET.Qnode(self, name=name, coords=coords, **kwargs)
            # Else initialize a node of the specified type
            else:
                # Check if type is valid
                assert (qnode_type in typeDict), f"Unsupported qnode type: \'{qnode_type}\'"
                new_node = typeDict[qnode_type](self, name=name, coords=coords, **kwargs)
            self.add_node(new_node)

    def add_qnodes_from(self, nbunch):
        """
        Add multiple Qnodes to the Qnet from a list of dictionaries.

        This function simply loops through the dictionary and runs "add_qnode" for each element.

        Parameters
        ----------
        nbunch:
            A list of dictionaries containing the key word arguments for node initialization.

            For details, consult the documentation for the node class

        Returns
        -------
        None

        Raises
        ------
        AssertionError
            If the qnode_type is invalid.

            (For details, see documentation for add_qnode() or Node class)
        """
        for data in nbunch:
            # We pop these elements because they are common for each node instance, and hence are keyword arguments
            name = data.pop("name", None)
            qnode_type = data.pop("qnode_type", None)
            coords = data.pop("coords", None)
            self.add_qnode(name, qnode_type, coords, **data)

    def remove_qnode(self, qnode):
        """
        Remove a qnode from the graph
        Parameters
        ----------
        qnode:
            Node object or

        Returns
        -------

        """
        qnode = self.getNode(qnode)
        if qnode is None:
            return
        self.remove_node(qnode)

    def remove_qnodes_from(self, nbunch):
        for data in nbunch:
            self.remove_qnode(data)

    def add_qchan(self, edge=None, key=None, **kwargs):
        """
        Add a Qchan to the graph.

        If either of the node types are Satellites, the costs of the edge will be automatically calculated with
        the Node class method "airCost"

        Parameters
        ----------
        edge: (qnode, qnode)
            A pair of nodes to be connected. Order does not matter.

        key: int
            Optional
            A key specifying a specific edge

        kwargs:
            Key word arguments for the edge cost

        Returns
        -------
        None

        Warnings
        --------
        Additional costs specified in **kwargs that are not in self.cost_vector will not be added. This is because
        such costs do not have an associated range or additive conversion method.
        """
        # Assert edge is valid
        assert (edge != None), "\'edge\' must be an array-like object of two qnodes"
        assert (len(edge) == 2), "\'edge\' must be an array-like object of two qnodes"

        u = self.getNode(str(edge[0]))
        v = self.getNode(str(edge[1]))

        if u is None:
            u = QNET.Ground(self, name=str(edge[0]))
            self.add_node(u)
        if v is None:
            v = QNET.Ground(self, name=str(edge[1]))
            self.add_node(v)

        # If either of the nodes are satellites, get air costs
        if isinstance(u, QNET.Satellite):
            e, f = u.airCost(v)
            kwargs.update({'e': e, 'f': f})
        elif isinstance(v, QNET.Satellite):
            e, f = v.airCost(u)
            kwargs.update({'e': e, 'f': f})

        # Pass it through make_cost_vector to ensure that
        cost_vector = QNET.make_cost_vector(self, **kwargs)
        self.add_edge(u, v, key=key, **cost_vector)

    def add_qchans_from(self, cbunch):
        """
        Adds multiple edges to the Qnet from a list of dictionaries.

        This function simply loops through the dictionary and runs "add_qchan" for each element.

        Parameters
        ----------
        cbunch: dict
            A list of dictionaries of edge attributes

        Returns
        -------
        None

        Warnings
        --------
        Additional costs specified in **kwargs that are not in self.cost_vector will not be added. This is because
        such costs do not have an associated range or additive conversion method.

        """
        for edge in cbunch:
            self.add_qchan(**edge)

    def add_memory_qchan(self, edge=None, **kwargs):
        """
        Add a temporal Qchan to the graph to show time-connection of nodes with quantum memory.

        The only difference with add_qchan() is that if either of the node types are Satellites, the airCosts
        will be not be updated since the memory costs are inherent properties of the nodes themselves and
        hence, are time independent.

        :param list edge: Array-like object of two qnodes to be connected
        :param float kwargs: Other costs or qualifying attributes
        :return: None
        """

        # Assert edge is valid
        assert (edge != None), "\'edge\' must be an array-like object of two qnodes"
        assert (len(edge) == 2), "\'edge\' must be an array-like object of two qnodes"

        u = self.getNode(str(edge[0]))
        v = self.getNode(str(edge[1]))

        if u is None:
            u = QNET.Ground(self, name=str(edge[0]))
            self.add_node(u)
        if v is None:
            v = QNET.Ground(self, name=str(edge[1]))
            self.add_node(v)

        cost_vector = QNET.make_cost_vector(self, **kwargs)
        self.add_edge(u, v, **cost_vector)


    def add_memory_qchans_from(self, cbunch):
        """
        Adds a list of temporal channels connecting layers/slices/graphs
        """
        for edge in cbunch:
            self.add_memory_qchan(**edge)

    def getNode(self, node_name):
        """
        This function returns a node with a given name. If no such node exists, returns None.

        Parameters
        ----------
        node_name: str
            Name of node

        Returns
        -------
        Qnode

        Warnings
        --------
        As node names in Qnet are expected to be unique, this function simply returns the first instance of a node that
        matches the name given. In theory, this shouldn't be a problem regardless since the add_qnode method handles
        a duplicate name by overwriting the existing node.

        """
        if isinstance(node_name, QNET.Qnode):
            for node in self.nodes():
                if node.name == node_name.name:
                    return node
        for node in self.nodes():
            if node.name == node_name:
                return node
        return None

    def update(self, dt):
        """
        Updates all time dependent elements in the Qnet by a given time increment

        Currently, this function:
            + Updates Satellite positions
            + Updates Satellite channel costs by performing the Node method "airCost"

        Parameters
        ----------
        self:
        dt : float
            Size of time increment
        Returns
        -------
        None.
        """
        assert (dt is not None)

        # Update satellite positions
        for node in self.nodes:
            if isinstance(node, QNET.Satellite):
                # Update satellite position:
                node.posUpdate(dt)

        # Update satellite channels
        for node in self.nodes:
            if isinstance(node, QNET.Satellite):
                # Get neighboring channels:           
                edges = self.edges(node)
                # Update channels:
                for edge in edges:
                    if isinstance(edge[0], QNET.Satellite):
                        s = edge[0]
                        n = edge[1]
                    else:
                        n = edge[0]
                        s = edge[1]

                    # newCost = [e, p]
                    newCost = s.airCost(n)

                    # Unpack newCost
                    new_e = newCost[0]
                    new_p = newCost[1]

                    # Update edge
                    # self.remove_edge(s, n)
                    # No longer need to remove edge, since add_qchan updates properly now
                    # TODO: Fix keys to handle multigraph update
                    self.add_qchan(edge=(s.name, n.name), key=0, e=new_e, p=new_p)

    def updateName(self, n):
        """
        Updates names of nodes for different layers of spatio-temporal graph.

        Changes "nodeName" to str(n)+"nodeName".

        Parameters
        ----------
        n : int
            Graph layer number in spatio-temporal description of quantum memory.

        Returns
        -------
        None.

        """
        for node in self.nodes:
            node.name = str(n)+node.name
