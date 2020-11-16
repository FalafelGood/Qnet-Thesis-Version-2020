"""
Costs.py contains all of the relevant software for instantiating cost vectors, converting between various cost types
and calculating optimal path costs
"""
import networkx as nx
import QNET
import numpy as np
import copy

def remove_prefix(s, prefix):
    """
    Remove the prefix of a string
    Parameters
    ----------
    s: str
    prefix: str

    Returns
    -------
    str

    """
    return s[len(prefix):] if s.startswith(prefix) else s

# Basic conversions
def to_log(x):
    """
    Convert a number to its negative log
    Parameters
    ----------
    x: float

    Returns
    -------
    float

    """
    return -np.log(x) + 0


def from_log(x):
    """
    Convert a number from its negative log
    Parameters
    ----------
    x: float

    Returns
    -------
    float

    """
    return np.exp(-x)


def to_add_f(x):
    """
    Convert fidelity to its additive form
    Parameters
    ----------
    x: float
        Fidelity

    Returns
    -------
    float

    """
    return -np.log(np.abs(2 * x - 1)) + 0


def from_add_f(x):
    """
    Convert from additive form of fidelity to fidelity
    Parameters
    ----------
    x: float
        Additive fidelity

    Returns
    -------
    float
    """
    return (1 + np.exp(-1 * x)) / 2


def make_cost_vector(Q, **kwargs):
    """
    Creates a cost vector (that includes additive costs) for an object in the graph Q.

    Parameters
    ----------
    Q: Qnet()
        The graph with reference to the cost vector
    kwargs
        Keyword arguements for the cost vector

    Returns
    -------
    dict

    Warnings
    --------
    Additional costs specified in **kwargs that are not in Q.cost_vector will not be added. This is because
    such costs do not have an associated range or additive conversion method.

    Raises
    AssertionError
        If any of the costs are out of their specified ranges
    """

    # The default cost vector
    cost_vector = copy.copy(Q.cost_vector)
    # The valid ranges of each cost
    cost_ranges = Q.cost_ranges
    # The conversion methods from multiplicative cost to additive and vice versa
    conversions = Q.conversions

    # Update the cost vector with all valid costs found in kwargs
    for item in kwargs.items():
        key = item[0]
        if key in cost_vector:
            cost_vector.update([item])

    # Assert that costs are within the correct range:
    for item in cost_vector.items():
        name, value = item[0], item[1]
        cost_range = cost_ranges[name]
        cost_min, cost_max = cost_range[0], cost_range[1]
        assert (cost_min <= value <= cost_max), f"Out of range -- ({cost_min} <= {name} <= {cost_max}), " + \
                                                f"{name} == {value}"

    # Initialize additive costs
    additive_costs = {}
    for item in cost_vector.items():
        name, value = item[0], item[1]
        add_cost_func = conversions[name][0]
        additive_costs["add_" + name] = add_cost_func(value)
    cost_vector.update(additive_costs)

    return cost_vector

def make_memory_vector(Q, **kwargs):
    """
    Creates a dictionary of memory costs for a node with quantum memory.
    Memory Efficiency and Memory Fidelity are initalized, as are their additive costs and any other key word arguements specified
    by the user.
    
    This memory cost vector is then used to create quantum channels in the temporal dimension. 

    :param QNET Q: Corresponding QNET in which memory nodes are present
    :param float kwargs: Other costs or qualifying attributes
    :return dictionary: Memory Cost vector
    """
    # The default cost vector
    memory_vector = copy.copy(Q.memory_vector)
    # The valid ranges of each cost
    memory_ranges = Q.memory_ranges
    # The conversion methods from multiplicative cost to additive and vice versa
    memory_conversions = Q.memory_conversions

    # Update the cost vector with all valid costs found in kwargs
    for item in kwargs.items():
        key = item[0]
        if key in memory_vector:
            memory_vector.update([item])

    # Assert that costs are within the correct range:
    for item in memory_vector.items():
        name, value = item[0], item[1]
        memory_range = memory_ranges[name]
        cost_min, cost_max = memory_range[0], memory_range[1]
        assert (cost_min <= value <= cost_max), f"Out of range -- ({cost_min} <= {name} <= {cost_max}), " + \
                                                f"{name} == {value}"

    # Initialize additive costs
    additive_memory = {}
    for item in memory_vector.items():
        name, value = item[0], item[1]
        add_memory_func = memory_conversions[name][0]
        additive_memory["add_" + name] = add_memory_func(value)
    memory_vector.update(additive_memory)

    return memory_vector


def convert_cost_vector(Q, cost_vector=None, add_cost_vector=None):
    """
    Convert a cost_vector to or from its additive form

    NOTE: Currently useless since the additive costs of the cost vector are not currently a seperate
    object.

    Parameters
    ----------
    Q
    cost_vector
    add_cost_vector

    Returns
    -------

    """
    assert(cost_vector is not None and add_cost_vector is not None)
    new_cv = {}
    if cost_vector is not None:
        for cost_type in cost_vector:
            cost = cost_vector[cost_type]
            new_cv[cost_type] = Q.conversions[cost_type][0](cost)
    elif add_cost_vector is not None:
        for cost_type in add_cost_vector:
            cost = add_cost_vector[cost_type]
            new_cv[cost_type] = Q.conversions[cost_type][1](cost)
    return new_cv


def best_path(Q, source, target, cost_type):
    """
    Given a source node, target node, and a cost type, this function returns the path that optimises this cost.
    
    Parameters
    ----------
    Q: Qnet()
    source: Union[string, Qnode()]
    target: Union[string, Qnode()]
    cost_type: string

    Returns
    -------
    Path()

    """
    def get_weight_function(costType):
        """
        Given a costType, returns a corresponding weight_function
        for use in nx.shortest_path_length

        :param string costType: cost type in ['e', 'p']
        :return: weight function
        """

        def weight(u, v, d):
            node_u_wt = u.costs[costType]
            node_v_wt = v.costs[costType]
            # Attempts to get edge weight, returns 1 if not found
            edge_wt = d.get(costType, 1)
            return node_u_wt / 2 + node_v_wt / 2 + edge_wt
            # Note that shortest path cost will need to be compensated with 1/2 head and 1/2 tail cost

        return weight

    def picky_path(Q, node_list, cost_type):
        """
        Given a list of nodes for the shortest path in cost_type, this function returns a QNET.Path object specifying
        the shortest path.

        Since Qnet is a multi-graph, a list of nodes is insufficient to specify the true shortest path. What picky_path
        does is find the edges in the list of nodes that minimizes cost_type and then create a QNET.Path object with
        this information contained.

        Parameters
        ----------
        Q: Qnet()
        node_list: [Qnode()]
            list of nodes in the shortest path
        cost_type: str
            Any valid cost from the cost vector

        Returns
        -------
        Path()
        """
        edge_keys = []
        path_len = len(node_list)
        i = 0
        while i < path_len - 1:
            cur = node_list[i]
            nxt = node_list[i + 1]
            edge_num = Q.number_of_edges(cur, nxt)
            edge_list = [Q.edges[cur, nxt, j] for j in range(edge_num)]
            seq = [e[cost_type] for e in edge_list]
            key = seq.index(max(seq))
            edge_keys.append(key)
            i += 1
        return QNET.Path(Q, node_list, edge_keys)

    # MAIN
    source = Q.getNode(source)
    target = Q.getNode(target)

    conversions = Q.conversions
    assert cost_type in conversions, f"Invalid cost type. \"{cost_type}\" not in {str([key for key in conversions])}"
    # Change cost type to additive
    cost_type = "add_" + cost_type

    weight = get_weight_function(cost_type)
    node_list = nx.dijkstra_path(Q, source, target, weight)
    short_path = picky_path(Q, node_list, cost_type)
    return short_path

### OUTMODED
def best_path_cost(Q, source, target, cost_type):
    """
    Get the lowest path cost in a Qnet for a given costType.
    Considers edge weights and node weights

    :param Q: Qnet Graph
    :param Union[str, Qnode] source: Source node
    :param Union[str, Qnode] target: Target node
    :param str costType: Any of {'e', 'p', 'de', 'dp'}
    :return: float length of shortest path in units of costType
    """

    def get_weight_function(costType):
        """
        Given a costType, returns a corresponding weight_function
        for use in nx.shortest_path_length

        :param string costType: cost type in ['e', 'p']
        :return: weight function
        """

        def weight(u, v, d):
            node_u_wt = u.costs[costType]
            node_v_wt = v.costs[costType]
            # Attempts to get edge weight, returns 1 if not found
            edge_wt = d.get(costType, 1)
            return node_u_wt / 2 + node_v_wt / 2 + edge_wt
            # Note that shortest path cost will need to be compensated with 1/2 head and 1/2 tail cost

        return weight

    source = Q.getNode(source)
    target = Q.getNode(target)

    conversions = Q.conversions
    assert cost_type in conversions, f"Invalid cost type. \"{cost_type}\" not in {str([key for key in conversions])}"
    # Change cost type to additive
    cost_type = "add_" + cost_type

    # Calculate best cost in terms of additive cost
    weight = get_weight_function(cost_type)
    cost = nx.shortest_path_length(Q, source, target, weight)
    # Compensate shortest path cost with 1/2 head cost and 1/2 tail cost
    cost += source.costs[cost_type] / 2 + target.costs[cost_type] / 2

    # Convert multiplicative costs back to additive costs
    back_convert = conversions[cost_type.strip("_add")][1]
    cost = back_convert(cost)

    return cost
