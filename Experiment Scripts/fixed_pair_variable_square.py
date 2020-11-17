"""
In this file, we characterise the "Simple_Purify" reduction method for different square lattice sizes where the communication pair remains at equidistant fixed points.
"""

from QNET import *
from textwrap import wrap

square = multidim_lattice(dim=2, size=6, e=1, f=0.8)


def fixed_pair(square):
    """
    Get the nodes that are a fixed off-diagonal distance from eachother in a given graph, as close to the middle as
    possible

    Parameters
    ----------
    square: Square lattice graph

    Returns
    -------
    (Qnode, Qnode)
    """
    # Diagonal distance required. Diagonal distance is measured in number of diagonal steps. Hence an n x n graph has
    # A max diag of 5
    diag = 5
    square_width = int(np.sqrt(number_of_nodes(square)))
    # nodes separated by a diagonal of length "diag" lie on a square of size diag + 1.
    small_square_width = diag + 1
    # Check if graph is large enough for given diag.
    assert(square_width >= small_square_width)

    # Center small_square
    lower_coord = (square_width - small_square_width) // 2
    upper_coord = lower_coord + small_square_width -1

    u_str = "(" + str(lower_coord) + ", " + str(lower_coord) + ")"
    v_str = "(" + str(upper_coord) + ", " + str(upper_coord) + ")"

    u = square.getNode(u_str)
    v = square.getNode(v_str)

    return u, v

def fixed_pairs_variable_square():
    e = 1
    f = 0.975
    sample_size = 1000

    dfs = []
    lattice_sizes = [8, 10, 12, 14]
    for size in lattice_sizes:
        print(f"LATTICE SIZE {size}")
        square = square_lattice(m=size, n=size, efficiency=e, fidelity=f)
        data = monte_method(square, pair_method=fixed_pair, reduction_method=QNET.purify_reduce,
                            data_method=data_method, num_iters=sample_size, num_steps=20, percolation_range=None)
        dfs.append(data)
        data.to_csv(path_or_buf=f"/home/hudson/Documents/Code/fixed_pair_square_lattice_{size}x{size}.csv")

    better_simul_plot(dfs, leg_labels=["6x6", "8x8", "10x10", "12x12"],
               title="\n".join(wrap(f"Fixed Pair Variable Size Square Lattice with edge efficiency "
                                    f"{e} and edge fidelity {f}")), ylabel="Costs of \"Simple Purify\" Method")

# fixed_pairs_variable_size()
fixed_pairs_variable_square()
