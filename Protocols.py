#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 10:59:46 2020
@author: hudson

Protocols.py contains functions for entanglement purification, entanglement swapping, and other functions that can be
used to reduce Qnet graphs
"""

import copy
import numpy as np
import networkx as nx
import QNET


def simple_swap(Q, source, dest):
    """
    Given a linear graph or subgraph, this function calculates the efficiency from head to tail if all valid swapper
    nodes are used. Currently, both this quantity and the normal efficiency of the path are returned

    In the future, if it's more efficient not to use any swappers, the normal efficiency of the path
    will be returned.

    :param Q: Linear Qnet Graph
    :return float: no_swap and swap efficiencies of the graph

    Example:

    A - G1 - T - G2 - T - G3 - B
    net_eff = min ( e[A-G1-T], e[T-G2], e[T-G3-B] ) * e[T]**2

    Where e[A-G-T] is taken to mean the efficiency of the path [A-G-T]
    and e[T] is taken to mean the efficiency cost of performing a swap with the node T.

    """
    # Check that path exists from A to B
    assert(nx.has_path(Q, source, dest))

    # Create generator of paths from A to B. If no generator exists raise exception
    path_gen = nx.all_simple_paths(Q, source, dest)
    assert (path_gen != None), f"No valid path exists between {source.name} and {dest.name}."

    #  Unpack generator. If more than one path exists, raise exception
    path_count = 0
    for obj in path_gen:
        path = QNET.Path(Q, obj)
        path_count += 1

    assert(path_count == 1), "More than one path exists, linear reduction cannot be done."

    # Does a Swapper with swapping potential exist?
    swap_candidate = None
    # Does ground exist before a swapper?
    front_ground = False
    # Local efficiency of a Ground - Swapper - Ground configuration (or equivalent)
    local_eff = 1
    # list of swapper nodes used in the swapping process
    swap_list = []
    # Total efficiency of path
    net_eff = 1

    # Current node
    cur = source
    # Counter
    i = 0

    while cur != dest:
        # If current node is a Ground and we haven't seen a Swapper yet, set front_ground to True
        if isinstance(cur, QNET.Ground) and swap_candidate is None:
            # Add node eff to local
            local_eff *= cur.costs['e']
            front_ground = True

        # If Current node is a Swapper and we've seen a ground node previously, we now have a candidate for a swapper
        # that could be used.
        elif isinstance(cur, QNET.Swapper) and front_ground is True:
            swap_switch = True
            if swap_candidate == None:
                swap_candidate = cur
            # If we had another swap candidate previously, update swap_candidate to be better efficiency option
            elif swap_candidate.swap_prob < cur.swap_prob:
                swap_candidate = cur
            local_eff *= cur.costs['e']

        # If current node is a Ground and we've seen a Swapper, we perform a swap with the local resources
        # (Front-Ground, Swapper, Back-Ground) and update net_eff.
        elif isinstance(cur, QNET.Ground) and swap_candidate is not None:
            # Add node eff to local
            local_eff *= cur.costs['e']

            # Update net_eff to local_eff if net_eff is smaller
            if local_eff < net_eff:
                net_eff = local_eff

            # Add the swapper we were considering to the list of swappers used
            swap_list.append(swap_candidate)

            # Reset parameters to prepare for the next swap
            local_eff = 1
            swap_candidate = None
            front_ground = False

        # Otherwise include the node cost in the local efficiency
        else:
            local_eff *= cur.costs['e']

        # Increment counter and get the edge efficiency
        i += 1
        edge_costs = Q.get_edge_data(cur, path.node_array[i])

        # Update local_eff with edge efficiency
        local_eff *= edge_costs['e']
        # Move to next node
        cur = path.node_array[i]

        # If the new node is the destination
        if cur == dest:
            # Append node costs from dest
            local_eff *= cur.costs['e']
            # Update net_eff to local_eff if net_eff is smaller
            # This also handles the case where no valid swapper was encountered
            if local_eff < net_eff:
                 net_eff = local_eff

    # Multiply net_eff with the costs of all swappers used.
    for swapper in swap_list:
        net_eff *= swapper.costs['e']

    """Calculate cost of path without any swapping"""
    # Cost of path without swapping
    no_swap = 1
    # Length of path
    path_len = len(path.node_array)
    i = 0

    # Sum all edge efficiencies
    while (i < path_len - 1):
        cur = path.node_array[i]
        nxt = path.node_array[i + 1]
        edgeData = path.G.get_edge_data(cur, nxt)
        no_swap *= edgeData['e']
        i += 1

    # Sum all node efficiencies except for swappers
    for node in path.node_array:
        no_swap *= node.costs['e']

    # DEBUG: For now, return both swap and no swap:
    return(no_swap, net_eff)

    """
    # Return whatever cost is better
    if net_eff > no_swap:
        return net_eff
    else:
        return no_swap
    """

def fidTransform(F1, F2):
    return (F1 * F2) / (F1 * F2 + (1 - F1) * (1 - F2))

def purify(Q, source, target):
    """

    This function performs a multi-path entanglement purification between a source and target node using all
    available paths.

    :param Q: Qnet Graph
    :param source: Name of source node
    :param target: Name of target node
    If none, will purify all possible paths
    :param string, optional, method: The method used to do the purification.
    Supported options: "edge_disjoint", "node_disjoint", "total_disjoint", "greedy".
        edge_disjoint: No intersecting edges
        node_disjoint: No intersecting nodes
        total_disjoint: No intersecting edges or nodes
        Other inputs produce a ValueError
    :return: float
    """

    # TODO: Implement a threshold attribute so user doesn't have to iterate through all paths

    def fidTransform(F1, F2):
        return (F1 * F2) / (F1 * F2 + (1 - F1) * (1 - F2))

    # Get paths for Graph
    u = Q.getNode(source)
    v = Q.getNode(target)

    # TODO: Find a better way of producing disjoint paths
    generator = nx.node_disjoint_paths(Q, u, v)

    # Get p values for each path
    f_arr = []
    for path in generator:
        new_path = QNET.Path(Q, path)
        # check if path is valid
        if new_path.is_valid() == True:
            f = new_path.cost_vector['f']
            f_arr.append(f)
        else:
            pass

    assert (len(f_arr) != 0), f"No path exists from {source} to {target}"

    # Initialize purified fidelity as the max fidelity value
    pure_cost = max(f_arr)
    f_arr.remove(pure_cost)

    # Purify fidelities together
    # TODO: Depreciate this code
    while len(f_arr) != 0:
        pmax = max(f_arr)
        pure_cost = fidTransform(pure_cost, pmax)
        f_arr.remove(pmax)

    return pure_cost


def simple_purify(Q = None, head = None, tail = None, threshold = None):
    """
    A simple purification algorithm that works as follows:
    1. Find the best path between source and target and save the cost
    2. Remove the edges of this path from the graph
    3. Find the next best path
    4. Purify the paths together
    5. Repeat steps 3 and 4 until either we hit the threshold number or there are no more paths between source and
    target

    :param Q:
    :param source: Source Node
    :param target: Target Node
    :param: threshold: Maximum number of paths to purify before returning cost vector
    :return: cost vector
    :param: dict
    """
    if threshold is not None:
        assert isinstance(threshold, int)
        assert threshold > 0

    # Default cost_array
    if None in [Q, head, tail]:
        return {'e': 0, 'f': 0}

    # Make copy of graph
    C = copy.deepcopy(Q)

    # Get source and target
    head = C.getNode(head)
    tail = C.getNode(tail)

    # Find the best path in terms of fidelity,
    path = QNET.best_path(C, head, tail, 'f')
    # pur_f = path.cost('f')
    pur_f = path.cost_vector['f']
    # pur_e = path.cost('e')
    pur_e = path.cost_vector['e']
    path.remove_edges()
    path_counter = 1

    # Purify paths against eachother until either no path exists or threshold is reached
    while nx.has_path(C, head, tail) is True:
        if threshold is not None:
            if path_counter > threshold:
                break
        path = QNET.best_path(C, head, tail, 'f')
        # new_f = path.cost('f')
        new_f = path.cost_vector['f']
        # new_e = path.cost('e')
        new_e = path.cost_vector['e']

        # Efficiency is weakest-link. Update pur_e to whatever the lowest path efficiency is.
        if new_e < pur_e:
            pur_e = new_e

        pur_f = QNET.fidTransform(pur_f, new_f)
        path.remove_edges()
        path_counter += 1

    # Each path purification requires 2*(n-1) bell projections, where n is the number of bell pairs
    # Assume that projections are done with a PBS with e = 1/2
    pur_e = pur_e * 0.5**(2*path_counter - 1)

    return {'e':pur_e, 'f':pur_f}


def best_costs(P = None, head = None, tail = None):
    # Default cost_array
    if None in [P, head, tail]:
        return {'e': 0, 'f': 0}
    else:
        e = QNET.best_path_cost(P, head, tail, cost_type='e')
        f = QNET.best_path_cost(P, head, tail, cost_type='f')
    cost_vector = {'e':e, 'f':f}
    return cost_vector


def path_exist(P=None, head=None, tail=None):
    if None in [P, head, tail]:
        return {'p': 0}
    if isinstance(head, QNET.Qnode):
        if not nx.has_path(P, head, tail):
            return{'p': 0}
    else:
        for i in range(len(head)):
            if not nx.has_path(P, head[i], tail[i]):
                return{'p': 0}
    return {'p': 1}

