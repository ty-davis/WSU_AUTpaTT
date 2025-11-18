import numpy as np
import matplotlib.pyplot as plt
from matplotlib.tri import Triangulation
import csv
import sys


filename = ''
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    response = input("Use a file or simulated? (f for file, s for simulated)")
    if 'f' in response:
        filename = input("Input the filename:\n>> ")
    elif 's' not in response:
        exit()

data = None
if filename:
    with open(filename, 'r') as fin:
        rdr = csv.reader(fin)
        content = list(rdr)

        trimmed = content[2:]
        reduced = trimmed[::10]
        data = [[float(d) for d in row] for row in reduced]
else:
    N = 36
    M = 72
    t = np.linspace(0, np.pi, N)
    p = np.linspace(0, 2*np.pi, M)
    # t, p = np.meshgrid(t, p)
    print(np.shape(t))
    print(np.shape(p))
    data = []
    r = np.abs(np.sin(t))
    for i in range(len(t)):
        for j in range(len(p)):
            data.append((p[j], t[i], 0, r[i]))
    # data = [(t[i][j], p[i][j], 0, r[i]) for i in range(len(t)) for j in range(len(p))]
    print("\n\n\n")
    print(*data[:10], sep='\n')
    print(*data[-10:], sep='\n')

    if False and input('save new data? '):
        content = [
            [ "Experiment" ],
            [ "% Mast Angle", "Arm Angle", "Background RSSI", "Transmission RSSI"],
        ] + data
        with open("output.csv", 'w') as fout:
            wtr = csv.writer(fout)
            wtr.writerows(content)

if not data:
    print("ERROR NO DATA. EXITING...")
    exit()



p_flat = np.array([d[0] for d in data])
t_flat = np.array([d[1] for d in data])
r_flat = np.array([float(d[3]) - float(d[2]) for d in data])
r_norm = r_flat / np.max(r_flat)
r_db = 20 * np.log10(r_norm)


t, p = np.meshgrid(t_flat, p_flat)

x = r_norm * np.sin(t_flat) * np.cos(p_flat)
y = r_norm * np.sin(t_flat) * np.sin(p_flat)
z = r_norm * np.cos(t_flat)
x_2d = r_norm * np.sin(t) * np.cos(p)
y_2d = r_norm * np.sin(t) * np.sin(p)
z_2d = r_norm * np.cos(t)

print(np.shape(x), np.shape(y), np.shape(z_2d))

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
# ax.plot_surface(x_2d, y_2d, z_2d, cmap='viridis', alpha=0.8)
# ax.scatter(x, y, z)

tri = Triangulation(p_flat, t_flat)
ax.plot_trisurf(x, y, z, triangles=tri.triangles, cmap=plt.cm.CMRmap, linewidths=0.5, antialiased=True)


plt.show()
