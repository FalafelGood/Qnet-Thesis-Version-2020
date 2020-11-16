from QNET import *
import matplotlib.pyplot as plt
from QNET.Sample_Graphs.Graph1 import X

def plot_cv(x, cva, label):
    for cost in cva[0].keys():
        a = []
        for d in cva:
            a.append(d[cost])
        plt.plot(x, a, label=f"{label} ({cost})")

tMax = 20
dt = 0.1
time = QNET.getTimeArr(tMax, dt)

costs = QNET.sim_path(X, path=['A','S','B'], tMax=tMax, dt=dt, cost_type='e')
plt.plot(time, costs, label="A-S-B")

pur_arr = QNET.sim_method(X, "A", "B", QNET.simple_purify, tMax, dt)
costs = []
print(pur_arr)
for cost in pur_arr:
    costs.append(cost['e'])
plt.plot(time, costs, label="Path Purification")
# plot_cv(time, pur_arr, label = "Path Purification")

costs = QNET.sim_path(X, path=['A','G','B'], tMax=tMax, dt=dt, cost_type='e')
plt.plot(time, costs, label="A-G-B")

optimal_fid = QNET.sim_optimal_cost(X, "A", "B", cost_type="e", tMax=tMax, dt=dt)
plt.plot(time, optimal_fid, 'b--', linewidth = 2, label="Best Classical Cost")

plt.legend()
plt.xlabel("Time (seconds)")
plt.ylabel("Efficiency")
plt.title("Efficiency of Different Methods for Distributing Entanglement Between Nodes \"A\" and \"B\"", fontsize = 10)
plt.show()

plot_3d(X)