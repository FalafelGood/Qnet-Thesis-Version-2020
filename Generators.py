"""
Created on Fri Mar 6 13:02:25 2020
@author: Hudson and Deepesh
"""

import networkx as nx
import QNET
import numpy as np
import random
import copy


def multidim_lattice(dim, size, e, f, periodic=False):
    dim = [size]*dim
    G = nx.grid_graph(dim, periodic)

    Q = QNET.Qnet()
    for edge in G.edges():
        u = edge[0]
        v = edge[1]
        Q.add_qchan(edge=(u, v), e=e, f=f)
    return Q

# This is bad code. Using it to get a nice picture. That's about it.
def square_lattice(m, n, efficiency, fidelity):
    G = nx.grid_2d_graph(m, n, periodic=False, create_using=None)
    Q = QNET.Qnet()

    for node in G.nodes():
        Q.add_qnode(name = str(node), qnode_type="Ground", coords=(node[0], node[1], 0))

    for edge in G.edges():
        u = edge[0]
        v = edge[1]
        Q.add_qchan(edge=(u, v), e=efficiency, f=fidelity)
    return Q


def triangular_lattice(m, n, efficiency, fidelity, periodic=False, with_positions=True):
    """
    Returns the m by n triangular lattice Qnet

    Parameters
    ----------
    m
    n
    efficiency
    fidelity
    periodic
    with_positions
    create_using

    Returns
    -------
    Qnet
    """
    G = nx.generators.triangular_lattice_graph(m, n, periodic=periodic, with_positions=with_positions)

    Q = QNET.Qnet()
    for edge in G.edges():
        u = edge[0]
        v = edge[1]
        Q.add_qchan(edge=(u, v), e=efficiency, f=fidelity)

    if with_positions is True:
        for node_name, position in list(G.nodes(data="pos")):
            # Update Qnet nodes with positions
            Q.add_qnode(name=str(node_name), coords=[position[0], position[1], 0])
    return Q


def hexagonal_lattice(m, n, efficiency, fidelity, periodic=False, with_positions=True):
    """
    Returns the m by n triangular lattice Qnet

    Parameters
    ----------
    m
    n
    efficiency
    fidelity
    periodic
    with_positions
    create_using

    Returns
    -------
    Qnet
    """
    G = nx.generators.hexagonal_lattice_graph(m, n, periodic=periodic, with_positions=with_positions)

    Q = QNET.Qnet()
    for edge in G.edges():
        u = edge[0]
        v = edge[1]
        Q.add_qchan(edge=(u, v), e=efficiency, f=fidelity)

    if with_positions is True:
        for node_name, position in list(G.nodes(data="pos")):
            # Update Qnet nodes with positions
            Q.add_qnode(name=str(node_name), coords=[position[0], position[1], 0])
    return Q


def altLinGen(n, spacing, e=1, f=1):
    '''
    Constructs a linear chain with end Qnodes A and B, and alternating Swapper and Ground nodes in the middle.

    Parameters
    ----------
    n : int
        Total number of nodes in the chain, including end nodes A and B.
    spacing : Array of float
        Distance between two consecutive nodes in [x,y,z] format.
    e : float
        Efficiency of a single channel in the regular lattice. The default is 1.

    Returns
    -------
    Q : QNET Graph
        A linear chain of length n consisting of alternating Bell pair generator and swappers.

    '''

    Q = QNET.Qnet()

    if n > 0:
        firstNode = QNET.Qnode(Q, name='A', coords=spacing)
        Q.add_node(firstNode)

    previousNode = QNET.Qnode(Q)
    currentNode = QNET.Qnode(Q)

    ChannelList = []

    if n > 2:
        for i in range(n - 2):
            GroundNode = QNET.Ground(Q, name=('G' + str(i + 1)), coords=np.multiply(i + 2, spacing))
            SwapNode = QNET.Swapper(Q, name=('T' + str(i + 1)), coords=np.multiply(i + 2, spacing))

            if n > 3:
                if (i) % 2 == 0:
                    currentNode = SwapNode
                else:
                    currentNode = GroundNode
            else:
                currentNode = GroundNode

            Q.add_node(currentNode)

            if i > 0:
                ChannelList.append(
                    {'edge': (previousNode.name, currentNode.name), 'e': e, 'f': f})

            previousNode = currentNode

    if n > 1:
        lastNode = QNET.Qnode(Q, name='B', coords=np.multiply(n, spacing))
        Q.add_node(lastNode)

        ChannelList.append(
            {'edge': (firstNode.name, list(Q.nodes)[1].name), 'e': e, 'f': f})
        ChannelList.append(
            {'edge': (list(Q.nodes)[n - 2].name, lastNode.name), 'e': e, 'f': f})

    Q.add_qchans_from(ChannelList)

    return Q


def altLinSatGen(n, spacing, e=1, f=1, startTime=0, Line1='', Line2='', *args):
    '''
    Constructs a linear chain with end Qnodes A and B, and alternating Swapper and Ground nodes in the middle.

    A satellite is connected to end nodes A and B, and all swapper nodes.

    Parameters
    ----------
    n : int
        Total number of nodes in the chain, including end nodes A and B.
    spacing : Array of float
        Distance between two consecutive nodes in [x,y,z] format.
    eVal : float
        Efficiency of a single channel in the regular lattice. The default is 1.
    pxVal : float
        Probability of state not undergoing X-flip in the regular lattice. The default is 0.
    pyVal : float
        Probability of state not undergoing Y-flip in the regular lattice. The default is 0.
    pzVal : float
        Probability of state not undergoing Z-flip in the regular lattice. The default is 0.
    startTime : int
        Time in seconds from now (current time) starting which the satellite should be tracked. The default is 0.
    Line1 : String
        Line 1 of satellite TLE. The deault is ''.
    Line2 : String
        Line 2 of satellite TLE. The deault is ''.

    Returns
    -------
    Q : QNET Graph
        A linear chain of length n consisting of alternating Bell pair generator and swappers.
        End nodes A and B, and all swapper nodes are connected to a satellite.

    '''

    Q = QNET.Qnet()

    if n > 0:
        firstNode = QNET.Qnode(Q, name='A', coords=spacing)
        Q.add_node(firstNode)

    previousNode = QNET.Qnode(Q)
    currentNode = QNET.Qnode(Q)

    ChannelList = []

    if n > 2:
        for i in range(n - 2):
            GroundNode = QNET.Ground(Q, name=('G' + str(i + 1)), coords=np.multiply(i + 2, spacing))
            SwapNode = QNET.Swapper(Q, name=('T' + str(i + 1)), coords=np.multiply(i + 2, spacing))

            if n > 3:
                if (i) % 2 == 0:
                    currentNode = SwapNode
                else:
                    currentNode = GroundNode
            else:
                currentNode = GroundNode

            Q.add_node(currentNode)

            if i > 0:
                ChannelList.append(
                    {'edge': (previousNode.name, currentNode.name), 'e': e, 'f': f})

            previousNode = currentNode

    if n > 1:
        lastNode = QNET.Qnode(Q, name='B', coords=np.multiply(n, spacing))
        Q.add_node(lastNode)

        ChannelList.append(
            {'edge': (firstNode.name, list(Q.nodes)[1].name), 'e': e, 'f': f})
        ChannelList.append(
            {'edge': (list(Q.nodes)[n - 2].name, lastNode.name), 'e': e, 'f': f})

    S = QNET.Satellite(Q, name='S', t=startTime, line1=Line1, line2=Line2, cartesian=False)
    Q.add_node(S)

    nodeList = Q.nodes()
    for node in nodeList:
        if type(node) != QNET.Ground and type(node) != QNET.Satellite:
            ChannelList.append({'edge': (node.name, S.name)})

    Q.add_qchans_from(ChannelList)

    return Q


def regularLatticeGen(x, y, xspacing, yspacing=[0, 0, 0], e=1, f=1):
    '''
    Constructs a 2D Regular Lattice with end Qnodes A and B, and alternating Swapper and Ground nodes in the middle.


    Parameters
    ----------
    x : int
        Number of columns in the regular lattice.
    y : int
        Number of rows in the regular lattice.
    xspacing : 3x1 Array of float
        Distance between two consecutive columns in 2D regular lattice in [x,0,0] format.
    yspacing : 3x1 Array of float
        Distance between two consecutive rows in 2D regular lattice in [0,y,0] format. The default is [0,0,0].
    eVal : float
        Efficiency of a single channel in the regular lattice. The default is 1.
    pxVal : float
        Probability of state not undergoing X-flip in the regular lattice. The default is 0.
    pyVal : float
        Probability of state not undergoing Y-flip in the regular lattice. The default is 0.
    pzVal : float
        Probability of state not undergoing Z-flip in the regular lattice. The default is 0.

    Returns
    -------
    Q : QNET Graph
        A y*x 2D regular lattice.

    '''

    assert (x > 0)
    assert (y > 0)

    if yspacing == [0, 0, 0]:
        yspacing[1] = xspacing[0]

    Q = QNET.Qnet()

    firstNode = QNET.Qnode(Q, name='A', coords=[0, 0, 0])
    lastNode = QNET.Qnode(Q, name='B', coords=np.add(np.multiply(x - 1, xspacing), np.multiply(y - 1, yspacing)))

    previousNode = QNET.Qnode(Q)
    currentNode = QNET.Qnode(Q)

    ChannelList = []

    # Constructing the nodes in the Regular Lattice
    for i in range(x):
        for j in range(y):

            GroundNode = QNET.Ground(Q, name=('G(' + str(i + 1) + ',' + str(j + 1) + ')'),
                                     coords=np.add(np.multiply(i, xspacing), np.multiply(j, yspacing)))
            SwapNode = QNET.Swapper(Q, name=('T(' + str(i + 1) + ',' + str(j + 1) + ')'),
                                    coords=np.add(np.multiply(i, xspacing), np.multiply(j, yspacing)))

            # Swap nodes at odd positions and Ground nodes at even positions in a Regular Lattice
            if x >= 1 and y >= 1:
                if (i + j) % 2 == 0:
                    currentNode = GroundNode
                else:
                    currentNode = SwapNode

            # Linear chain of length 3 exception
            if (x == 3 and y == 1) or (x == 1 and y == 3):
                currentNode = GroundNode

            # 2*2 2D lattice exception
            if x == 2 and y == 2:
                currentNode = GroundNode

            # Initialising the first node as A
            if i == 0 and j == 0:
                currentNode = firstNode

            # Initialising the last node as B
            if i == (x - 1) and j == (y - 1):
                currentNode = lastNode

            Q.add_node(currentNode)

            previousNode = currentNode

    # Constructing the vertical edges in the Regular Lattice
    for i in range(x):
        previousNode = list(Q.nodes)[i * y]
        for j in range(y - 1):
            currentNode = list(Q.nodes)[j + 1 + (i * y)]
            ChannelList.append(
                {'edge': (previousNode.name, currentNode.name), 'e': e, 'f': f})
            previousNode = currentNode

    # Constructing the horizontal edges in the Regular Lattice
    for j in range(y):
        previousNode = list(Q.nodes)[j]
        for i in range(x - 1):
            currentNode = list(Q.nodes)[j + (i + 1) * y]
            ChannelList.append(
                {'edge': (previousNode.name, currentNode.name), 'e': e, 'f': f})
            previousNode = currentNode

    Q.add_qchans_from(ChannelList)
    # Q.print_qchans()

    return Q
    
def temporalGen(Q, dt, n, startLayer = 0, endLayer = None):
    """
    Creates a temporal extension of given graph.

    Creates a temporal extension of given graph to simulate the effect of quantum memory. Each layer(slice)
    of this temporal graph is an updated/evolved version of the previous layer by dt time. n such layers of
    these time updated graphs are created and only those nodes with quantum memory (node.isMemory == True)
    are connected in the temporal dimension.

    However, out of all these n time-updated layers of graph Q, we might only want to connect a few in the
    temporal dimension. The arguments startLayer and endLayer correspond to the number of layer between which
    all the graphs are connected.

    Example: If startLayer=1 and endLayer=3, only layers from 1 to 3 are connected in temporal dimension.

        t=0   -------

        t=1   ------- startLayer=1
              | | | |
        t=2   -------
              | | | |
        t=3   ------- endLayer=3
        :
        t=n-1 -------

    Parameters
    ----------
    Q : QNET Graph
        The spatial graph which is to be utilised to make a spatio-temporal graph.
    dt : float
        Time steps by which each layer/slice/graph is to be updated.
    n : int
        Number of such layers/slices/graphs to be made.
    startLayer : int
        The number corresponding to first layer starting which the layers are connected in temporal dimension.
        Default value is 0 i.e. the first layer itself.
    endLayer : int
        The number corresponding to last layer at which the layers' connection in temporal dimension ends.
        Default value is n-1 i.e. the last layer itself.

    Returns
    -------
    finalGraph : QNET Graph
        The temporal extension (including both connected and unconnected layers) of given graph Q.

    """

    if endLayer==None:
        endLayer = n-1

    ## Create a list of time-updated graph layers ##
    G = []
    new_graph = copy.deepcopy(Q)
    layer_num = 0
    for i in range(0,n):
        C = copy.deepcopy(new_graph)

        dummy_graph = copy.deepcopy(new_graph)
        dummy_graph.updateName(layer_num)
        G.append(dummy_graph)

        C.update(dt)
        layer_num = layer_num + 1
        new_graph = copy.deepcopy(C)

    ## Join these time-updated graph layers ##
    assert (0 <= startLayer <= n-1), f"Out of range -- 0 <= startLayer <= n-1 "
    assert (0 <= endLayer <= n-1), f"Out of range -- 0 <= endLayer <= n-1 "
    assert (startLayer <= endLayer), f"startLayer <= endLayer <= n-1 "


    finalGraph = QNET.Qnet()

    for layer_num in range(0, len(G)):
        finalGraph = nx.compose(finalGraph, G[layer_num])
        #print(finalGraph)

    for node in Q.nodes():
        for layer_num in range(startLayer+1, endLayer+1):
            if node.isMemory and layer_num>0:
                u = finalGraph.getNode(str(layer_num-1)+node.name)
                v = finalGraph.getNode(str(layer_num)+node.name)
                finalGraph.add_memory_qchan(edge=[u, v], e = u.memory['mem_e'], f = u.memory['mem_f'])

    return finalGraph



def percolate(Q, prob, head_tail_method):
    """
    Percolates a graph with some probability, making sure not to remove particular nodes of interest (head, tail)
    :param Q: Qnet Graph
    :param prob: Probability of not removing a given node not in (head, tail)
    :param head: Qnode
    :param tail: Qnode
    :return: Percolated Graph, head node, tail node
    """
    C = copy.deepcopy(Q)
    head, tail = head_tail_method(C)

    kill_list = []
    for node in C.nodes():
        xd = random.uniform(0,1)
        if xd < prob:
            if node not in (head, tail):
                kill_list.append(node)
    C.remove_nodes_from(kill_list)
    return C, head, tail
