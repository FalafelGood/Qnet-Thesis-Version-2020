"""
The purpose of this module is to use monte carlo methods to benchmark the performance of reduction methods in QNET.

The functions defined here are hierarchical. A brief summary of what they do and the order in which they are used is
provided here.
-------------
percolate:
    Percolates a graph with some probability
reduce_graph:
    Given a percolated graph, perform a reduction method
generate_graphs:
    Generate a list of reduced graphs for a range of percolation densities
measure_graphs
    Given a list of reduced graphs and communication parties,
plot_statistics

"""

import QNET
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axes as ax
import copy
import random
import pandas as pd
from cycler import cycler

def percolate(Q, prob, pair_method):
    """
    Percolates a graph with some probability, making sure not to remove communication parties selected with pair_method.
    Parameters
    ----------
    Q: Qnet()
    prob: float
        Probability of removing a node
    pair_method: function
        Method for picking pairs in Q. See monte_reduction documentation

    Returns
    -------
    Qnet(), list of pairs in Qnet
    """
    # Copy the graph and get pairs
    C = copy.deepcopy(Q)
    pairs = pair_method(C)
    if type(pairs) is not list:
        pairs = [pairs]

    # Go through and mark random nodes not in pairs
    kill_list = []
    for node in C.nodes():
        if any(node not in item for item in pairs):
            xd = random.uniform(0,1)
            if xd < prob:
                kill_list.append(node)
    C.remove_nodes_from(kill_list)
    return C, pairs

def reduce_graph(Q, pair_method, percolation_prob, reduction_method):
    """
    This function runs a reduction method against a graph.

    1. Given a graph, select one or more pairs of communication parties with the function pair_method.
    2. Percolate the graph with some probability. (I.E. Remove every node that is not a communication party with
       some probability percolation_prob)
    3. Given the percolated graph, check if at least one path exists between each pair of communication parties. If yes,
       run reduction_method on the percolated and return the reduced graph. If no, return None.

    Parameters
    ----------
    Q: Qnet()

    pair_method: function
    A method for choosing one or more communication pairs in the graph Q. This arguement is a function of the
    following form:
        function(Q)
        Q -- Qnet()
        returns -- list of pairs of Qnodes

    percolation_prob: float
    Probability of removing a given node that is not a part of a communication pair

    reduction_method: function
    A method for reducing the map with swapping and purification algorithms. This argument is a function of the
    following form:
        function(Q, pairs, **kwargs)
        Q -- Qnet()
        pairs -- list of pairs of Qnodes
        returns -- Qnet()

    Returns
    -------
    Qnet, list of communication parties
    """
    # Get percolated graph and communication pairs
    P, pairs = percolate(Q, percolation_prob, pair_method)
    # Check if paths exist between pairs. If not, return None
    for pair in pairs:
        if nx.has_path(P, pair[0], pair[1]) is False:
            return None, None
    # Run reduction method against P
    u, v = pairs[0]
    R = reduction_method(P, head=u, tail=v)
    return R, pairs


def generate_graphs(Q, pair_method, reduction_method, num_iters, percolation_prob):
    """
    Generate a list of reduced graphs and their communication pairs for a given percolation probability.

    1. Get reduced graph and communication parties from reduction_method
    2. Add reduced graph and parties to a list
    3. Repeat steps one and two num_iters times.

    Parameters
    ----------
    Q
    pair_method
    reduction_method
    num_iters
    percolation_prob

    Returns
    -------
    list of reduced graphs and their communication pairs
    """
    graph_list = []
    for i in range(num_iters):
        R, pairs = reduce_graph(Q, pair_method, percolation_prob, reduction_method)
        # if R is not None:
        graph_list.append((R, pairs))
    return graph_list


def data_method(Q, pairs):
    """
    An arbitrary method for measuring the effectiveness of a graph

    For all given communication pairs, find the best path between them in terms of fidelity.
    Average the cost vectors, and return the result.

    Parameters
    ----------
    Q: Qnet
    pairs: list

    Returns
    -------
    dict
        Cost vector
    """
    # If no path exists, return minimum values for efficiency and fidelity
    if Q is None or pairs is None:
        return {"e":0, "f":0.5}

    df = pd.DataFrame()
    for index, pair in enumerate(pairs):
        # Get shortest path between pairs in fidelity
        u, v = pair
        best_path = QNET.best_path(Q, u, v, 'f')

        # Get cost vector, and forget the additive costs
        cost_vector = best_path.cost_vector
        cost_vector = QNET.cv_strip_add(cost_vector)

        # Add the costs to the DataFrame
        df = df.append(pd.Series(cost_vector), ignore_index=True)
    # Convert data frame into single cost vector
    meanie = df.mean()
    return meanie.to_dict()


def monte_method(Q, pair_method, reduction_method, data_method, num_iters, num_steps, percolation_range=None):
    """
    The main Monte-Carlo method used for benchmarking a reduction method.

    1. If percolation_range is not None, Make a linspace of percolation probabilities of size num_steps within that
       range. Else, make a linspace of probabilities of size num_steps within range (0, 1)
    2. For each probability in range, make "num_iters" many graphs with the generate_graphs method
    3. Use data_method to determine performance quality of the graphs, then find the mean and standard error of these
       qualities.
    4. Put data into a Pandas DataFrame and plot

    Parameters
    ----------
    Q: Qnet
    pair_method: function
    reduction_method: function
    data_method: function
    num_iters: int
        number of samples taken per data point
    num_steps: int
        number of datapoints
    percolation_range: (float, float) or None
        range over which data points are collected.

    Returns
    -------
    """

    # Get array of probabilities "prob_list"
    if percolation_range is not None:
        assert (percolation_range[0] >= 0 and percolation_range[1] <= 1)
        prob_list = np.linspace(percolation_range[0], percolation_range[1], num_steps)
    else:
        prob_list = np.linspace(0, 1, num_steps)

    # Build column labels for main DataFrame from cost_vector
    column_labels = ["p"]
    for key in Q.cost_vector:
        column_labels.append(key)
        column_labels.append(key + " (std)")

    # Build main DataFrame
    main = pd.DataFrame(columns=column_labels, index=range(len(prob_list)))
    # Fill column "p" with values from prob_list
    main.update({"p": prob_list})

    # Collect mean and error for data points
    for index, p in enumerate(prob_list):
        print(f"-- Percolating graphs with probability {p} --")
        graph_list = generate_graphs(Q, pair_method, reduction_method, num_iters, percolation_prob=p)

        print("Collecting statistics...")
        # minor contains raw data for all generated graphs for a given data point
        minor = pd.DataFrame()
        for R, pairs in graph_list:
            data = data_method(R, pairs)
            minor = minor.append(pd.Series(data), ignore_index=True)
        # Compress minor DataFrame into mean and unbiased standard error
        mean = minor.mean()
        std = minor.sem()
        # Add (std) qualifiers to standard error variables
        for name, dummy in mean.items():
            # mean = mean.rename({name: name + " (mean)"})
            std = std.rename({name: name + " (std)"})
        # Update main DataFrame with mean and std
        for name, val in mean.items():
            main.at[index, name] = val
        for name, val in std.items():
            main.at[index, name] = val
    return main


def plot_monte_method(df, title=None, ylabel=None):
    """
    Plot DataFrames obtained from monte_method:

    Parameters
    ----------
    df: Pandas DataFrame
        DataFrame obtained from monte_method
    title: string, optional
        Title of the plot

    Returns
    -------
    None
    """
    i = 1
    c_names = list(df.columns)
    p_arr = df[c_names[0]]
    while i < len(c_names):
        plt.errorbar(p_arr, df[c_names[i]], df[c_names[i + 1]], label=c_names[i])
        i += 2
    if title is not None:
        plt.title(title)
    plt.xlabel("Probability of Node Deletion")
    if ylabel is not None:
        plt.ylabel(ylabel)
    else:
        plt.ylabel("Cost")
    plt.legend()
    plt.show()

def simul_plot(dfs, leg_labels, title=None, ylabel=None):
    """
    More sophisticated version of plot_monte_method, capable of plotting multiple DataFrames with a nice colour palate.
    Parameters
    ----------
    dfs: array
        DataFrames obtained from plot_monte_method
    leg_labels: array
        Legend labels
    title: sting
        Title of the graph
    ylabel:
        string

    Returns
    -------
    None
    """

    # Generate colors
    red_map = plt.cm.get_cmap("Reds")
    blue_map = plt.cm.get_cmap("Blues")
    reds = red_map(np.linspace(0.40, 0.60, len(dfs)))
    blues = blue_map(np.linspace(0.40, 0.60, len(dfs)))

    for df_index, df in enumerate(dfs):
        # Initialize iteration items for the data frame
        i = 1
        c_names = list(df.columns)
        p_arr = df[c_names[0]]

        # Need quick way to alternate between colours. It's not good code, but it'll be fine for small stuff.
        paint_red = True
        while i < len(c_names):
            if paint_red is True:
                plt.errorbar(p_arr, df[c_names[i]], df[c_names[i + 1]], label=c_names[i] + " (" + leg_labels[df_index] + ")",
                             c=reds[df_index])
                paint_red = False

            else:
                plt.errorbar(p_arr, df[c_names[i]], df[c_names[i + 1]], label=c_names[i] + " (" + leg_labels[df_index] + ")",
                             c=blues[df_index])
                paint_red = True
            i += 2

    if title is not None:
        plt.title(title)
    plt.xlabel("Probability of Node Deletion")
    if ylabel is not None:
        plt.ylabel(ylabel)
    else:
        plt.ylabel("Cost")

    # TODO: Rearrange legend so it's colour coordinated

    plt.legend()
    plt.show()

def better_simul_plot(dfs, leg_labels, title=None, ylabel=None):
    # Generate colors
    # rainbow_map = plt.cm.get_cmap("rainbow")
    # rainbow = rainbow_map(np.linspace(0.1, 0.9, len(dfs)))

    # Set color cycle to something bearable:
    custom_cycle = cycler(color=['r', 'r', 'b', 'b', 'g', 'g', 'tab:orange', 'tab:orange'])
    plt.rc('axes', prop_cycle=custom_cycle)

    # Alternatively use a default style
    # plt.style.use("seaborn-colorblind")

    for df_index, df in enumerate(dfs):
        # Initialize iteration items for the data frame
        i = 1
        c_names = list(df.columns)
        p_arr = df[c_names[0]]

        # Quick way to alternate between line styles.
        dotted = False
        while i < len(c_names):
            if dotted is False:
                plt.errorbar(p_arr, df[c_names[i]], df[c_names[i + 1]],
                             label=c_names[i] + " (" + leg_labels[df_index] + ")")
                dotted = True

            else:
                plt.errorbar(p_arr, df[c_names[i]], df[c_names[i + 1]], fmt='--',
                             label=c_names[i] + " (" + leg_labels[df_index] + ")",
                             )
                dotted = False
            i += 2

    if title is not None:
        plt.title(title)
    plt.xlabel("Probability of Node Deletion")
    if ylabel is not None:
        plt.ylabel(ylabel)
    else:
        plt.ylabel("Cost")

    plt.legend()
    plt.show()


# Possibly useful for another application
    """
    def cost_vector_statistics(cv_list):
        # Convert list of dictionarties into Pandas DataFrame
        df = pd.DataFrame(cv_list)
        # Get mean and sample standard deviation as dataframes
        df_mean = df.mean()
        df_std = df.std()
        # Convert dataframes to dictionaries
        dict_mean = df_mean.to_dict()
        dict_std = df_std.to_dict()
        return dict_mean, dict_std
    """
