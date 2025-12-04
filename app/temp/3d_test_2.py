from csv import reader, writer
import numpy as np
import argparse
import statistics
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser(description="Process input files and write to an output file.")

    parser.add_argument(
        "-o", "--output",
        default="output.csv",
        help="Path to the output file."
    )

    parser.add_argument(
        "input_file",
        help="Input file to process."
    )

    args = parser.parse_args()


    print("Output file:", args.output)
    print("Input file:", args.input_file)


    with open(args.input_file, 'r') as fin:
        rdr = reader(fin)
        content = list(rdr)

    print(content[:10])
    data = content[2:]

    arm_angles = sorted(list(set([d[1] for d in data])), key=lambda x: int(float(x)))
    print(arm_angles)

    for ang in arm_angles:
        # let's get some stats
        ang_data = [d for d in data if d[1] == ang]
        trans_rssi_data = [float(d[3]) for d in ang_data]
        avg_trans_rssi = statistics.mean(trans_rssi_data)
        dev_trans_rssi = statistics.stdev(trans_rssi_data)
        print(ang, avg_trans_rssi, dev_trans_rssi)
        print(f"{ang}")
        ang_points = calc_3d_points(ang_data)
        show_points(ang_points)



    print("ALL OF THEM TOGETHER")
    points = calc_3d_points(data)
    show_points(points)

def show_points(points):
    x_vals, y_vals, z_vals = zip(*points)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    sc = ax.scatter(x_vals, y_vals, z_vals, cmap='viridis')

    plt.colorbar(sc, label='Z value')

    plt.show()


def calc_3d_points(data):
    points = []
    for point in data:
        mast = np.radians(float(point[0]))
        arm = np.radians(float(point[1]))
        r = 20 * np.log10(float(point[3]))

        x = r * np.cos(mast) * np.cos(arm)
        y = r * np.sin(mast) * np.cos(arm)
        z = r * np.sin(arm)
        points.append((x, y, z))
    return points



if __name__ == '__main__':
    main()
