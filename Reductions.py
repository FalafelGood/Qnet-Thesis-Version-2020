from QNET import *
import networkx as nx
import collections
import functools
import copy

def purify_reduce(Q, head, tail, threshold=None, prob=0.5):
    """
    Reduce a graph by purifying one or more paths

    Given a Qnet Q and two communication parties "head" and "tail," this function purifies paths together starting
    from the highest fidelity path until either the threshold is reached or no more paths exist to purify.

    :param Q: Qnet()
    :param head: Source Node
    :param tail: Target Node
    :param: threshold: Maximum number of paths to purify before returning graph
    :param: prob: Probability of a given projective measurement. The default is 0.5
    :return: A Qnet of the reduced graph
    """

    if threshold is not None:
        assert isinstance(threshold, int)
        assert threshold > 0

    # Make copy of graph
    C = copy.deepcopy(Q)

    # Get source and target
    head = C.getNode(head)
    tail = C.getNode(tail)

    # List of cost_vectors used in purification
    cv_list = []

    # Purify paths against each other until either no path exists or threshold is reached
    path_counter = 0
    while nx.has_path(C, head, tail) is True:
        if threshold is not None:
            if path_counter > threshold:
                break
        path = best_path(C, head, tail, 'f')
        cv_list.append(path.cost_vector)
        path.remove_edges()
        path_counter += 1

    new_cv = {}

    # Calculate new_fidelity
    f_list = [d['f'] for d in cv_list]
    # Iteratively apply fidTransform
    pur_f = functools.reduce(QNET.fidTransform, f_list)
    new_cv["f"] = pur_f

    # Calculate new_add_f
    new_cv["add_f"] = Q.conversions["f"][0](pur_f)

    # Calculate new_efficiency
    e_list = [d['e'] for d in cv_list]
    # Efficiency is weakest-link. Update pur_e to whatever the lowest path efficiency is.
    pur_e = min(e_list)
    # Each path purification requires 2*(n-1) bell projections, where n is the number of bell pairs
    # Assume that projections are done with a PBS with e = 1/2
    # WRONG
    pur_e = pur_e * prob ** (2 * (path_counter - 1))
    new_cv["e"] = pur_e

    # Calculate new_add_e
    new_cv["add_e"] = Q.conversions["e"][0](pur_e)

    # Calculate all other costs
    # Sum cost_vectors together
    def sum_cost_vectors(cv_list):
        counter = collections.Counter()
        for d in cv_list:
            counter.update(d)
        return dict(counter)

    sum_cv = sum_cost_vectors(cv_list)
    # Iterate through sum_cv, updating new_cv whenever a new cost appears
    for cost_type in sum_cv:
        if cost_type not in new_cv and cost_type.startswith("add_"):
            cost = sum_cv[cost_type]
            new_cv[cost_type] = cost
            cost_type = QNET.remove_prefix(cost_type, "add_")
            cost = Q.conversions[cost_type][1]
            new_cv[cost_type] = cost

    # Add a new Qchan between head and tail with the new cost vector, then return the graph
    C.add_qchan(edge=(head, tail), **new_cv)
    return C


def swap_reduce(Q, head, tail, threshold=None):
    """
    Reduce a graph by swapping one or more paths

    Given a Qnet Q and two communication parties "head" and "tail," this function reduces the graph by swapping valid
    paths starting with the highest efficiency path until either the threshold is reached or no more paths exist to
    swap.

    Parameters
    ----------
    Q: Qnet()
        The Graph to be reduced
    head: Qnode()
        One of two communication parties
    tail: Qnode()
        One of two communication parties
    threshold: int
        The maximum number of paths to swap before the reduced graph is returned.
        The default is None, meaning that the function will run until all valid paths between "head" and "tail" are
        swapped.

    Returns
    -------
    Qnet()
        The reduced graph
    """

    if threshold is not None:
        assert isinstance(threshold, int)
        assert threshold > 0

    # Make a copy of the graph
    C = copy.deepcopy(Q)
    # Get head and tail from C
    head = C.getNode(head)
    tail = C.getNode(tail)

    # List of swapped edge costs
    swap_costs = []

    while nx.has_path(C, head, tail) is True:
        # get best path in efficiency
        path = QNET.best_path(C, head, tail, 'e')
        # Perform swapping in path, add new cost vector to swap_costs
        new_cv = path.swap_path()
        swap_costs.append(new_cv)
        # remove path
        path.remove_edges()

    for cost_vector in swap_costs:
        # Make an edge with that cost_vector
        C.add_qchan(edge = (head, tail), **cost_vector)
    return C



