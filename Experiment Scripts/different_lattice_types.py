from QNET import *
import random
from textwrap import wrap

f = 0.975
e = 1

triangle = triangular_lattice(m=14, n=14, efficiency=e, fidelity=f)
square = square_lattice(m=8, n=8, efficiency=e, fidelity=f)
hexagon = hexagonal_lattice(m=5, n=5, efficiency=e, fidelity=f)

def print_node_numbers():
    for graph in [triangle, square, hexagon]:
        print(graph.number_of_nodes())

def plot_graphs():
    plot_2d(triangle)
    plot_2d(square)
    plot_2d(hexagon)


def random_pair_variable_lattice():
    def random_pair(G):
        """Get a random pair of nodes from G"""
        assert(G.number_of_nodes() >= 2)
        while True:
            n1, n2 = random.sample(G.nodes, 2)
            if n1 is not n2:
                return n1, n2

    print("TRIANGULAR LATTICE")
    tri_data = monte_method(triangle, pair_method=random_pair, reduction_method=QNET.purify_reduce,
                            data_method=data_method, num_iters = 1000, num_steps = 20, percolation_range=None)

    print("SQUARE LATTICE")
    square_data = monte_method(square, pair_method=random_pair, reduction_method=QNET.purify_reduce,
                               data_method=data_method, num_iters=1000, num_steps=20, percolation_range=None)

    print("HEXAGONAL LATTICE")
    hex_data = monte_method(hexagon, pair_method=random_pair, reduction_method=QNET.purify_reduce,
                               data_method=data_method, num_iters=1000, num_steps=20, percolation_range=None)

    simul_plot([tri_data, square_data, hex_data], leg_labels=["Triangle", "Square", "Hexagon"],
               title="\n".join(wrap("Random Pair Variable Lattice with Edge Efficiency 1 and Edge Fidelity 0.8")),
               ylabel="Costs of \"simple_purify\" method")


def fixed_pairs_variable_lattice():
    # Fix pairs such that shortest distance between off-diagonal nodes is 14 edges

    # Triangle fixed pair: (0,0), (7,14)
    def tri_pair(G):
        u = G.getNode("(0, 0)")
        v = G.getNode("(7, 14)")
        return u, v

    # Square fixed pair (1,1), (4,3)
    def square_pair(G):
        u = G.getNode("(0, 0)")
        v = G.getNode("(7, 7)")
        return u, v

    # Hexagon fixed pair: (1,2), (3,5)
    def hex_pair(G):
        u = G.getNode("(0, 0)")
        v = G.getNode("(4, 10)")
        return u, v

    sample_size = 1000

    print("TRIANGULAR LATTICE")
    tri_data = monte_method(triangle, pair_method=tri_pair, reduction_method=QNET.purify_reduce,
                            data_method=data_method, num_iters=sample_size, num_steps=20, percolation_range=None)

    print("SQUARE LATTICE")
    square_data = monte_method(square, pair_method=square_pair, reduction_method=QNET.purify_reduce,
                               data_method=data_method, num_iters=sample_size, num_steps=20, percolation_range=None)

    print("HEXAGONAL LATTICE")
    hex_data = monte_method(hexagon, pair_method=hex_pair, reduction_method=QNET.purify_reduce,
                            data_method=data_method, num_iters=sample_size, num_steps=20, percolation_range=None)

    better_simul_plot(dfs=[tri_data, square_data, hex_data], leg_labels=["Triangle", "Square", "Hexagon"], title="\n".join(
        wrap(f"Fixed Pair Variable Lattice with Edge Efficiency {e} and Edge Fidelity {f}")),
        ylabel="Costs of \"Simple Purify\" Method")

    tri_data.to_csv(path_or_buf="/home/hudson/Documents/Code/fixed_pair_tri_lattice.csv")
    square_data.to_csv(path_or_buf="/home/hudson/Documents/Code/fixed_pair_square_lattice.csv")
    tri_data.to_csv(path_or_buf="/home/hudson/Documents/Code/fixed_pair_hex_lattice.csv")

# compare_purification_with_lattice()
# compare_fixed_pairs()
# compare_lattice_types()
fixed_pairs_variable_lattice()