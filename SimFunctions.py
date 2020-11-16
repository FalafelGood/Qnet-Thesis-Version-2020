#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 17:25:13 2020
@author: Hudson Leone
"""

import networkx as nx
import QNET
import copy
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import art3d
# from mpl_toolkits.basemap import Basemap


def getTimeArr(tMax, dt):
    """
    Make uniform array from 0 to tMax with interval dt
    Parameters
    ----------
    tMax : float
        Maximum time
    dt : float
        Time increment
    Returns
    -------
    Array
    """
    return np.arange(0, tMax, dt)


def sim_path(G, path, tMax, dt, cost_type=None):
    """
    Return an array of path costs over time

    Parameters
    ----------
    G: Qnet Graph
    path: An array of node names
    tMax: float
        Timespan of the simulation
    dt: Time increment
    cost_type: string, optional
        (The default value is None, which returns a list of cost vectors for the path over time)

    Returns
    -------
    List of floats or list of dicts
    """
    if cost_type is not None:
        assert cost_type in G.cost_vector

    C = copy.deepcopy(G)
    path = QNET.Path(C, path)

    cost_array = []
    i = 0
    size_arr = len(np.arange(0, tMax, dt))
    while i < size_arr:
        if cost_type is not None:
            cost_array.append(path.cost_vector[cost_type])
        else:
            cost_array.append(path.cost_vector)
        C.update(dt)
        path.update()
        i += 1
    return cost_array


def sim_method(G, source, target, method, tMax, dt,):
    """
    Return an array of costs between source and target after running
    a graph reduction method

    Parameters
    ----------
    G: Qnet Graph
    source: Qnet node
    target: Qnet node
    method: graph reduction method
        method = method(Qnet graph, qnode, qnode)
    tMax: float
        Timespan of simulation
    dt: float
        Time increment

    Returns
    -------

    """
    C = copy.deepcopy(G)
    u = C.getNode(source)
    v = C.getNode(target)

    # Initialize cost array
    cost_arr = []
    # Initialize size of array
    size_arr = len(np.arange(0, tMax, dt))
    i = 0
    while i < size_arr:
        # Run method to get either scalar cost or cost vector
        cost = method(C, u, v)
        cost_arr.append(cost)
        # Update graph
        C.update(dt)
        i += 1
    return cost_arr


def sim_all_simple(G, source, target, tMax, dt, cost_type=None):
    """
    Get the cost arrays for all simple paths over time
    :param G: Qnet Graph
    :type G: Qnet()
    :param source: Qnode
    :param target: Qnode
    :param tMax: Timespan
    :type tMax: float
    :param dt: Time interval
    :type dt: float
    :param cost_type: string, optional
    :return: Dictionary of paths to a list of cost arrays over time
    """
    C = copy.deepcopy(G)

    # get source and target from names
    source = C.getNode(source)
    target = C.getNode(target)

    # Create a generator of all simple paths
    simplePathGen = nx.algorithms.simple_paths.all_simple_paths(C, source, target)

    # Unpack paths from generator into array as QNET paths
    path_arr = []
    for path in simplePathGen:
        path_arr.append(QNET.Path(C, path))

    # Assign each path to an empty cost array
    path_dict = {path: [] for path in path_arr}

    # Initialize array size
    size_arr = len(np.arange(0, tMax, dt))
    i = 0
    while i < size_arr:
        j = 0
        while j < len(path_arr):
            # Get the cost of each path and append it to respective array
            if cost_type is None:
                # Fetch all costs in cost vector
                cost = path_arr[j].cost_vector
            else:
                # Fetch specified cost
                cost = path_arr[j].cost_vector[cost_type]
            path_dict[path_arr[j]].append(cost)
            j += 1

        C.update(dt)
        i += 1

    for path in path_arr:
        for node in path.node_array:
            if isinstance(node, QNET.Satellite):
                if node.cartesian is False:
                    node.setTime()

    return path_dict


def sim_protocol(G, source, target, protocol, tMax, dt):
    """
    Get the cost arrays of a simple protocol over time
    :param G: Qnet Graph
    :type G: Qnet()
    :param source: Qnode
    :param target: Qnode
    :param tMax: Timespan
    :type tMax: float
    :param dt: Time interval
    :type dt: float
    :return: List of cost arrays for the protocol over time.
    """
    C = copy.deepcopy(G)
    u = C.getNode(source)
    v = C.getNode(target)

    # Initialize cost array
    cost_arr = []
    # Initialize size of array
    size_arr = len(np.arange(0, tMax, dt))
    i = 0
    while i < size_arr:
        # Run protocol to get either scalar cost or cost bector
        cost = protocol(C, u, v)
        cost_arr.append(cost)
        # Update graph
        C.update(dt)
        i += 1
    return cost_arr

def plot_cv(x, cva, label):
    for cost in cva[0].keys():
        a = []
        for d in cva:
            a.append(d[cost])
        plt.plot(x, a, label=f"{label} ({cost})")


def sim_optimal_cost(G, source_name, target_name, cost_type, tMax, dt):
    """
    Calculate the costs of the lowest cost path from "source" to "target" over time.
    :param G: Qnet Graph
    :param string source_name: Name of source node
    :param string target_name: Name of target node
    :param string cost_type: The type of cost to optimise over. Choose from {'loss', 'fid'}
    :param float tMax: Time period
    :param float dt: Time increment
    :return: Optimal loss array
    """
    C = copy.deepcopy(G)

    u = C.getNode(source_name)
    v = C.getNode(target_name)

    # Initialize arrays
    cost_arr = []
    size = len(np.arange(0, tMax, dt))

    # Get optimal path cost and append it to costArr
    i = 0
    while i < size:
        cost = QNET.best_path_cost(C, source_name, target_name, cost_type)
        cost_arr.append(cost)
        # Update network
        C.update(dt)
        i += 1

    """ 
    simplePathGen = nx.algorithms.simple_paths.all_simple_paths(C, u, v) 
    pathArr = []
    for path in simplePathGen:
        pathArr.append(QNET.Path(C, path))
    for path in pathArr:
        for node in path.node_array:
            if isinstance(node, QNET.Satellite):
                if node.cartesian is False:
                    node.setTime()
    """

    return cost_arr

def posPlot(Q, u, v, tMax, dt):
    """
    Plot the distance between two nodes over time
    :param Q: QNet Graph
    :param u: Name of Qnode
    :param v: Name of Qnode
    :param tMax: Maximum time
    :param dt: Size of timestep
    :return: None
    """
    C = copy.deepcopy(Q)

    u = C.getNode(u)
    v = C.getNode(v)

    posArr = []
    sizeArr = len(np.arange(0,tMax,dt))

    i = 0
    while i < sizeArr:
        if isinstance(u, QNET.Satellite):
            dist = u.distance(v)
        elif isinstance(v, QNET.Satellite):
            dist = v.distance(u)
        else:
            assert(False)
        posArr.append(dist)
        C.update(dt)
        i += 1
    if isinstance(u, QNET.Satellite):
        u.setTime()
    if isinstance(v, QNET.Satellite):
        v.setTime()
    
    timeArr = QNET.getTimeArr(tMax, dt)
    plt.plot(timeArr, posArr)
    plt.xlabel("Time (in s)")
    plt.ylabel("Distance (in 10^3 km)")
    plt.title(f"Distance between {u.name} and {v.name}")
    plt.show()    
    

def plot_2d(Q, node_label = None, edge_label=None, edge_color='k', title=None, FOV=('x', 'y')):
    """
    Plots a 2d view of a Qnet graph in spatial coordinates of nodes
    Edge costs listed are rounded to four significant figures

    :param Q: Qnet Graph
    :param node_label: Node cost to be labeled
    :type node_label: string, optional
    :param edge_label: Edge cost to be labeled
    :type edge_label: string, optional
    :param title: Title of the graph
    :type title: string
    :param FOV: Field of view. Choose any pair of cartesian axes. I.E. ('x','y'), ('y','z')
    :type FOV: (string, string), optional
    :return:
    """
    # Dictionary of node positions
    pos_dict = {}
    # Dictionary of node labels
    node_labels = {}
    # Dictionary of node positions but offset for labeling
    offset = {}
    # Offset for node labeling in y direction
    y_off = 5
    # Dictionary of labels for edges
    edge_labels = {}
    # Array of colours for nodes
    node_colours = []
    # Dictionary between colours and node types
    colour_dict = {QNET.Qnode: 'r', QNET.Ground: 'y', QNET.Swapper: 'c', QNET.Satellite: 'b'}

    for axes in FOV:
        assert axes in ('x', 'y', 'z'), "Field of view usage: Two from (\'x\', \'y\', \'z\')."
    axis_to_index = {'x':0, 'y':1, 'z':2}
    u = axis_to_index[FOV[0]]
    v = axis_to_index[FOV[1]]

    for node in Q.nodes():
        pos_dict[node] = [node.coords[u], node.coords[v]]
        node_colours.append(colour_dict[type(node)])

        if node_label is not None:
            cost = round(node.costs[node_label], 4)
            node_labels[node] = str(node_label) + ' = ' + str(cost)

            offset[node] = [node.coords[u], node.coords[v] + y_off]

        if edge_label is not None:
            for nbr in Q.neighbors(node):
                # If there's no key for the reverse direction case, add edge label (Only one direction needed)
                if not (nbr, node) in edge_labels:
                    # Since our graph is a multi graph then we need to label each of the edges connecting a given node pair
                    num_edges = Q.number_of_edges(node, nbr)
                    for k in range(num_edges):
                        cost = round(Q.edges[node, nbr, k][edge_label], 4)
                        # Note here that edge_labels can't actually distinguish multiple edges... See below
                        edge_labels[(node, nbr)] = str(edge_label) + ' = ' + str(cost)

        """
        Warning: Networkx's edge labels are keyed by a two-tuple (u, v) in draw_networkx_edge_labels
        meaning that labels aren't possible for the multigraph representation. This stack exchange here 
        seems to have a messy workaround to this problem. In the meantime, DON'T TRY TO LABEL MULTI-GRAPHS
        
        https://stackoverflow.com/questions/32905262/how-do-i-draw-edge-labels-for-multigraph-in-networkx/32910209
        
        """

    # draw_networkx
    nx.draw_networkx(Q, pos=pos_dict, node_color=node_colours, edge_color=edge_color, linewidths = 0)
    nx.draw_networkx_labels(Q, pos=offset, labels=node_labels)
    nx.draw_networkx_edge_labels(Q, pos_dict, edge_labels=edge_labels)

    # Scale Axes to avoid cutoff
    # plt.axes("off")
    axis = plt.gca()
    axis.set_xlim([1.0 * x for x in axis.get_xlim()])
    axis.set_ylim([1.1 * y for y in axis.get_ylim()])
    plt.tight_layout()

    if title is not None:
        plt.title(title)

    plt.show()


def plot_3d(Q, title=None):
    """
    Draws a 3d plot of a Qnet graph
    Parameters
    :param Q: Qnet Graph
    :param title: Title of Graph
    :return:
    """
    # Create new matplotlib figure and add axes
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for node in Q.nodes:
        x, y, z = node.coords[0], node.coords[1], node.coords[2]
        # Dictionary between colours and node types
        qnode_color = {QNET.Qnode: 'r', QNET.Ground: 'y', QNET.Swapper: 'c', QNET.Satellite: 'b'}
        ax.scatter(x, y, z, c=qnode_color[type(node)], marker='o')
        ax.text(x, y, z, '%s' % node.name, size=12, zorder=1)

        # Draw arrow for satellite velocity
        if isinstance(node, QNET.Satellite):
            v = node.velocity
            ax.quiver(x, y, z, v[0], v[1], 0, length = 1.5)

    for edge in Q.edges:
        xs = [edge[0].coords[0], edge[1].coords[0]]
        ys = [edge[0].coords[1], edge[1].coords[1]]
        zs = [edge[0].coords[2], edge[1].coords[2]]
        if isinstance(edge[0], QNET.Satellite) or isinstance(edge[1], QNET.Satellite):
            line = art3d.Line3D(xs, ys, zs, linestyle='--')
        else:
            line = art3d.Line3D(xs, ys, zs)
        ax.add_line(line)
    if title is not None:
        plt.title(f"{title}")
    fig.show()

def plot_paths(Q, tMax, dt):
    """
    Plot the costs of all simple paths over time along with the cost from simple_purify
    :param Q: Qnet Graph
    :param tMax: Maximum time
    :param dt: Size of time increment
    :return: None
    """
    # Get Time Array
    time_arr = QNET.getTimeArr(tMax, dt)

    # Plot the costs of every simple path over time
    path_dict = sim_all_simple(Q, 'A', 'B', tMax, dt)
    for path in path_dict:
        for cost in Q.cost_vector.keys():
            a = []
            for d in path_dict[path]:
                a.append(d[cost])
            plt.plot(time_arr, a, label = f"{str(path)} ({cost})")

    # Purified costs over time:
    pur_arr = sim_protocol(Q, "A", "B", QNET.simple_purify, tMax, dt)
    plot_cv(time_arr, pur_arr, label = "Path Purification")

    plt.xlabel('Time')
    plt.ylabel("Path Costs")
    plt.title("Network Path Costs Over Time Between Nodes \"A\" and \"B\"")

    plt.legend()
    plt.show()
