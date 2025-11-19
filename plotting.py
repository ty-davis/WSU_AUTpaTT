import numpy as np
import matplotlib.pyplot as plt
from matplotlib.tri import Triangulation
import csv
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help="Path to the input file")
    parser.add_argument('--plot-layers', action='store_true', help='Plot each line before showing the 3d plot')

    args = parser.parse_args()

    filename = args.filename
    if not filename:
        response = input("Use a file or show simulated? (f for file, s for simulated)")
        if 'f' in response:
            filename = input("Input the filename:\n>> ")
        elif 's' not in response:
            exit()

    data = []
    if filename:
        data = read_csv_file(filename)
    else:
        # generate the simulated data
        N = 36
        M = 72
        t = np.linspace(0, np.pi, N)
        p = np.linspace(0, 2*np.pi, M)
        data = []
        r = np.abs(np.sin(t))
        for i in range(len(t)):
            for j in range(len(p)):
                data.append((p[j], t[i], 0, r[i]))

    if not data:
        print("ERROR NO DATA. EXITING...")
        exit()

    if False and input('save new data? '):
        content = [
            [ "Experiment" ],
            [ "% Mast Angle", "Arm Angle", "Background RSSI", "Transmission RSSI"],
        ] + data
        with open("output.csv", 'w') as fout:
            wtr = csv.writer(fout)
            wtr.writerows(content)

    process_data(data)

def read_csv_file(filename):
    with open(filename, 'r') as fin:
        rdr = csv.reader(fin)
        content = list(rdr)
        trimmed = content[2:]
        data = [[float(d) for d in row] for row in trimmed]
        return data


def process_data(data):
    data = [(np.radians(d[0]), np.radians(d[1]), d[2], d[3]) for d in data]

    p_flat = np.array([d[0] for d in data])
    t_flat = np.array([d[1] for d in data])

    r_flat = np.array([float(d[3]) - float(d[2]) for d in data])
    r_norm = r_flat / np.max(r_flat)
    r_db = 20 * np.log10(r_norm)

    if False:
        theta_values = sorted(list(set([t for t in t_flat])))
        while len(theta_values) > 10:
            theta_values = theta_values[::2]

        for tv in theta_values:
            ps = np.array([d[0] for d in data if d[1] == tv])
            rs = np.array([d[3] - d[2] for d in data if d[1] == tv])
            rs_norm = rs / np.max(rs)
            rs_db = 20 * np.log10(rs_norm)
            print("phis:", len(ps), ps)
            print("rs_db:", len(rs_db), rs_db)
            ax = plt.subplot(111, projection='polar')
            ax.plot(ps, rs_db)
            ax.set_title(r"$\theta = $" + str(tv))
            plt.show()



    x = r_norm * np.sin(t_flat) * np.cos(p_flat)
    y = r_norm * np.sin(t_flat) * np.sin(p_flat)
    z = r_norm * np.cos(t_flat)


    tri = Triangulation(p_flat, t_flat)
    return x, y, z, tri
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_trisurf(x, y, z, triangles=tri.triangles, cmap=plt.cm.CMRmap, linewidths=0.5, antialiased=True)


    plt.show()

if __name__ == '__main__':
    main()

