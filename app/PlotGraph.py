#------------------------------------------------------------------------------
# THIS FILE IS DEPRECATED AND LEFT HERE FOR LEGACY REASONS
# THE FILE IS NOT IN USE BY app.py AND IS ONLY HERE FOR REFERENCE
#
#'PlotGraph.py'                                     Hearn WSU-ECE
#                                                   17apr23
# Open-Source Antenna Pattern Measurement System
# Performs the following project-specific functions:
#   Plots the provided data and shows the plot in a new window     
#       
#   
#
#    
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
# WSU-ECE legal statement here 
#------------------------------------------------------------------------------
import math
import matplotlib.pyplot as plt
from numpy import array, log10, sqrt
#
class PlotGraph():
    def __init__(self, data, title):
        # parse data
        self.title = title
        self.mast_angles = []
        self.arm_angles = []
        self.rssi = []
        self.data = [list(x) for x in data]
        self.elv_angles = sorted(list(set([d[1] for d in self.data])))
        for entry in data:
            mast_angle,arm_angle,background_rssi,transmit_rssi = entry
            self.mast_angles.append(float(mast_angle))
            self.arm_angles.append(float(arm_angle))
            self.rssi.append(float(transmit_rssi)-float(background_rssi))
        self.rssi = array(self.rssi);

        self.rssi = self.rssi/max(self.rssi);

        # normalize the self.data
        rssi_vals = [d[3] for d in self.data]
        max_rssi_vals = max(rssi_vals)
        for i in range(len(self.data)):
            self.data[i][3] = self.data[i][3] / max_rssi_vals

    def show_plot(self, azm_cross_section=None):
        # self.plot_in_db = input('plot pattern data in dB? (y/n): ');
        # self.plot_in_db = self.plot_in_db.lower();
        if azm_cross_section is None:
            selection = input('Select either elevation or azimuth angle as primary axis:\n\n   1:  AZIMUTH\n   2:  ELEVATION\n\n>> ')
            if '1' in selection:
                print("USING AZIMUTH")
                azm_cross_section = True
            elif '2' in selection:
                print("USING ELEVATION")
                azm_cross_section = False
            else:
                print("INVALID INPUT. Exiting...")
                return
        rssi = self.rssi.copy()
        plot_in_db = 'y' in input('plot pattern data in dB? (y/n)')
        if plot_in_db:
            rssi = 20*log10(self.rssi);
            for i in range(len(self.rssi)):
                if rssi[i] < -20 :
                    rssi[i] = -20;


            for i in range(len(self.data)):
                self.data[i][3] = 20 * log10(self.data[i][3])
                self.data[i][3] = -20 if self.data[i][3] < -20 else self.data[i][3]

        ax = plt.subplot(111, projection='polar')
        theta = [angle*(math.pi/180) for angle in self.mast_angles]
        phi = [math.radians(angle) for angle in self.arm_angles]
        if azm_cross_section:
            ax.plot(theta, rssi)
        else:
            ax.plot(phi, rssi)
#        ax.set_rmax(20.0)
        if plot_in_db:
            ax.set_rticks([-20, -15, -10, -5, 0]);
#        ax.set_rticks([-20,-16,-12,-8,-4,0]);
#        ax.set_rticks([-18, -15, -12, -9, -6, -3, 0]);
#        ax.set_rlabel_position(-22.5)
#        ax.set_xticklabels(['0', '45', '90', '135', '180', '-135', '-90', '-45'])
#        ax.grid(True)
        ax.set_title(self.title, va="bottom")
        ax.set_theta_zero_location("N")
        plt.show()

    def show_each_elv(self):
        print(self.elv_angles)
        for elv in self.elv_angles:
            small_data = [d for d in self.data if d[1] == elv]
            ax = plt.subplot(111)
            x = [d[0] for d in small_data]
            y = [10**(d[3]/20) for d in small_data]
            ax.plot(x, y)
            plt.show()
            ax = plt.subplot(111, projection='polar')
            mast_angles = []
            arm_angles = []
            rssi = []
            for entry in small_data:
                mast_angles.append(entry[0])
                arm_angles.append(entry[1])
                rssi.append(entry[3] - entry[2])
            print(mast_angles, arm_angles, rssi, sep="\n\n")
            theta = [math.radians(angle) for angle in mast_angles]
            ax.plot(theta, rssi)
            if self.plot_in_db == 'y':
                ax.set_rticks([-20, -15, -10, -5, 0])
            ax.set_title(f"{self.title} - {elv}", va="bottom")
            ax.set_theta_zero_location("N")
            plt.show()

#                                                        # plot the data

