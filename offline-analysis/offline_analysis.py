import os
import numpy as np
from datetime import datetime, timedelta
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import cm  # Import the colormap

class OfflineAnalysis:
    def __init__(self, directory):
        # Directory where the .dat files are located
        self.directory = directory
        self.data = []
        self.times = []
        self.labels = []  # Control or Xenon labels for each timestamp
        self.masses = []
        self.interpolated_data = []

        # Control and Xenon run time intervals
        self.run_intervals = {
            "control_run": [datetime(2024, 9, 11, 16, 46), datetime(2024, 9, 16, 9, 44)],
            "xenon_run": [datetime(2024, 9, 16, 11, 21), datetime(2024, 9, 26, 11, 0)]
        }
    
    def load_data(self, target_mass_grid=None):
        # Automatically find all .dat files in the directory
        data_files = [f for f in os.listdir(self.directory) if f.endswith('.dat')]
        
        # If no target mass grid is provided, generate a common one from 1 to 150 with 0.05 step size
        if target_mass_grid is None:
            target_mass_grid = np.arange(1, 150 + 0.05, 0.05)  # Create mass grid with 0.05 amu steps
        
        self.masses = target_mass_grid  # Store the target mass grid

        time_and_data = []  # Temporarily store timestamp and interpolated data together
        
        # Iterate through all data files and interpolate their data to the target mass grid
        for file in data_files:
            # Extract timestamp from the filename
            time_str = '_'.join(file.split('_')[2:]).split('.')[0]
            timestamp = datetime.strptime(time_str, '%Y%m%d_%H%M%S')
            label = self._assign_run_label(timestamp)  # Assign control or xenon run
            
            # Load the data file
            file_data = np.loadtxt(os.path.join(self.directory, file), delimiter=',', skiprows=1)
            file_masses = file_data[:, 0]  # Assuming first column contains the masses
            file_pressures = file_data[:, 1]  # Assuming second column contains the pressures
            
            # Interpolate to the target mass grid
            interp_func = interp1d(file_masses, file_pressures, bounds_error=False, fill_value=np.nan)
            interpolated_pressures = interp_func(target_mass_grid)
            # Store the timestamp and corresponding interpolated data
            time_and_data.append((timestamp, interpolated_pressures, label))
            
            # Store the interpolated data
            self.interpolated_data.append(interpolated_pressures)
        
        # Sort by timestamp
        time_and_data.sort(key=lambda x: x[0])  # Sort by the timestamp
        
        # Unpack the sorted times and data into self.times and self.interpolated_data
        self.times, self.interpolated_data, self.labels = zip(*time_and_data)
        
        # Convert the interpolated data list to a numpy array for easier manipulation
        self.interpolated_data = np.array(self.interpolated_data)

    def _assign_run_label(self, timestamp):
        if self.run_intervals["control_run"][0] <= timestamp <= self.run_intervals["control_run"][1]:
            return "control_run"
        elif self.run_intervals["xenon_run"][0] <= timestamp <= self.run_intervals["xenon_run"][1]:
            return "xenon_run"
        else:
            return None

    def get_times(self):
        return self.times
    
    def get_masses(self):
        return self.masses
    
    def get_pressures(self):
        return self.interpolated_data  # Return interpolated pressure data
    
    def plot_scan(self, scan_index=0):
        """
        Plot the uncalibrated spectrum for a specific scan (default is the first scan).
        """
        # Get masses and pressures for the specified scan
        masses = self.get_masses()
        pressures = self.get_pressures()
        
        # Select the pressures from the scan based on scan_index
        pressures_scan = pressures[scan_index]

        # Use the timestamp for the plot title
        timestamp = self.times[scan_index].strftime('%Y-%m-%d %H:%M:%S')

        # Create a new figure and axis object with a wider aspect ratio (width increased)
        fig, ax = plt.subplots(figsize=(12, 6))  # Increase the width of the figure

        # Use semilogy to create a semi-logarithmic plot
        ax.semilogy(masses, pressures_scan, lw=1, label=f'Scan {scan_index}')

        # Set axis labels, limits, legend, and title
        ax.set_xlabel('Mass [amu]')
        ax.set_ylabel('Partial pressure [torr]')
        ax.set_xlim([1, 140])  # Adjust the x-axis range as needed
        ax.set_ylim([1e-11, 1e-6])  # Adjust the y-axis range as needed
        ax.legend()  # Display legend
        ax.grid()  # Show grid lines
        ax.set_title(f'Uncalibrated Spectrum - {timestamp}')  # Set the plot title with timestamp

        # Save the figure as a PNG file
        fig.savefig(f'figures/uncalibrated_spectrum_{timestamp}.png')

        # Display the plot
        plt.show()

    def plot_scan_zoom(self, scan_index=0, x_min=1, x_max=140):
        """
        Plot the spectrum for a specific scan with zoomed x-axis (manual input) and auto-adjusted y-axis.
        
        Parameters:
        - scan_index: the index of the scan to plot
        - x_min: minimum value for the x-axis (mass range)
        - x_max: maximum value for the x-axis (mass range)
        """
        # Get masses and pressures for the specified scan
        masses = self.get_masses()
        pressures = self.get_pressures()
        
        # Select the pressures from the scan based on scan_index
        pressures_scan = pressures[scan_index]

        # Use the timestamp for the plot title
        timestamp = self.times[scan_index].strftime('%Y-%m-%d %H:%M:%S')

        # Create a new figure and axis object with a wider aspect ratio (width increased)
        fig, ax = plt.subplots(figsize=(12, 6))  # Increase the width of the figure

        # Use semilogy to create a semi-logarithmic plot
        ax.semilogy(masses, pressures_scan, lw=1, label=f'Scan {scan_index}')

        # Set axis labels and legend
        ax.set_xlabel('Mass [amu]')
        ax.set_ylabel('Partial pressure [torr]')
        ax.legend()  # Display legend
        ax.grid()  # Show grid lines

        # Apply the zoomed x-axis range (input by user)
        ax.set_xlim([x_min, x_max])
        ax.set_ylim([1e-11, 1e-6])
        
        # Automatically adjust the y-axis based on the data within the x range
        mask = (masses >= x_min) & (masses <= x_max)
        y_min, y_max = np.nanmin(pressures_scan[mask]), np.nanmax(pressures_scan[mask])
        ax.set_ylim([y_min * 0.9, y_max * 1.1])  # Add some padding for better visibility

        # Set the plot title with timestamp
        ax.set_title(f'Zoomed Spectrum - {timestamp}')

        # Save the figure as a PNG file
        fig.savefig(f'figures/zoomed_spectrum_{timestamp}.png')

        # Display the plot
        plt.show()  

    def get_mass_evolution(self, mass):
        """
        Extracts the pressure evolution for a given mass over time.
        """
        ps = []
        ts = []
        mass_exclusion = 0.5  # Allowable deviation for mass selection

        # Iterate through each scan (time point)
        for i, pressures in enumerate(self.interpolated_data):
            # Find the index of the mass closest to the desired mass
            m_idx = (np.abs(self.masses - mass)).argmin()
            m_returned = self.masses[m_idx]
            
            # Check if the returned mass is within the acceptable range
            if np.abs(m_returned - mass) > mass_exclusion:
                continue  # Skip if the mass is too far from the target
            
            # Store the pressure and corresponding timestamp
            ps.append(pressures[m_idx])
            ts.append(self.times[i])

        return ps, ts

    def plot_mass_evolution(self, mass, ax=None, smoothing=False):
        """
        Plots the pressure evolution over time for a specific mass.
        """
        # Get pressure and time for the specific mass
        ps, ts = self.get_mass_evolution(mass)

        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 6))

        # Plot the pressure over time (log scale for pressure)
        ax.plot(ts, ps, '.', label=f'Mass {mass} amu')
        
        if smoothing:
            # Apply a smoothing function if requested
            smoothed_ps = gaussian_filter(ps, sigma=5)
            ax.plot(ts, smoothed_ps, '-', label=f'Smoothed Mass {mass} amu')

        # Set plot labels and formatting
        ax.set_xlabel('Time')
        ax.set_ylabel('Partial Pressure [Torr]')
        ax.set_yscale('log')
        ax.legend()
        ax.grid(True)

        # Format the x-axis with readable date format
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        fig.autofmt_xdate()

        plt.show()
    
    def plot_mass_evolution_peakfound(self, mass, ax=None, window=2.2, fit=False, label_gap=True):
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 6))

        ps_control, ts_control_h = [], []
        ps_xenon, ts_xenon_h = [], []
        start_control = self.run_intervals["control_run"][0]
        start_xenon = self.run_intervals["xenon_run"][0]

        for i, timestamp in enumerate(self.times):
            p, m_ret = self.get_peakfound_pressure(mass, i, window=window)
            if p is None:
                continue
            
            if self.labels[i] == "control_run":
                ts_control_h.append((timestamp - start_control).total_seconds() / 3600)  # Control run hours since start
                ps_control.append(p)
            elif self.labels[i] == "xenon_run":
                ts_xenon_h.append((timestamp - start_xenon).total_seconds() / 3600)  # Xenon run hours since start
                ps_xenon.append(p)
        
        # Plot control run
        if ps_control:
            ax.plot(ts_control_h, ps_control, '.', label=f'{mass} amu (Control Run)')
        
        # Plot xenon run with complete gap removal and vertical marker
        if ps_xenon:
            ts_xenon_h, ps_xenon = self._handle_large_gaps(ts_xenon_h, ps_xenon, ax, label_gap)

            ax.plot(ts_xenon_h, ps_xenon, '.', label=f'{mass} amu (Xenon Run)')
        
        ax.set_xlabel('Hours since start')
        ax.set_ylabel('Partial pressure [torr]')
        ax.set_yscale('log')
        ax.legend()
        plt.show()
    
    def _handle_large_gaps(self, ts, ps, ax, label_gap):
        """
        Handle large gaps by removing the time between files where the gap exceeds 24 hours.
        Adds a marker and label for the gap.
        """
        new_ts, new_ps = [], []
        last_time = ts[0]
        time_shift = 0  # Track how much time has been shifted

        for i in range(len(ts)):
            # Check for a gap larger than 24 hours
            if ts[i] - last_time > 24:
                gap_duration = ts[i] - last_time  # Entire gap duration
                
                # Adjust time_shift to remove the entire gap
                time_shift += gap_duration
                
                if label_gap:
                    # Add a vertical marker for the gap
                    ax.axvline(last_time, color='#FA8072', linestyle='--', linewidth=2)  # Vertical line in red
                    # Add the label above the vertical line
                    ax.text(last_time + 1, max(ps) * 1.1, '5 days of scrubbing', color='#FA8072', verticalalignment='center', horizontalalignment='left')

            # Shift the current timestamp by the full gap duration
            new_ts.append(ts[i] - time_shift)
            new_ps.append(ps[i])
            last_time = ts[i]

        return new_ts, new_ps
    
    def get_peakfound_pressure(self, mass, scan_index, window=2):
        pressures = self.interpolated_data[scan_index]
        masses = self.masses
        
        mass_window = float(window)
        mask = (masses >= mass - mass_window / 2) & (masses <= mass + mass_window / 2)
        if not np.any(mask):
            return None, None
        
        masses_window = masses[mask]
        pressures_window = pressures[mask]

        smoothed_pressures = gaussian_filter(pressures_window, sigma=2)

        peaks, _ = find_peaks(smoothed_pressures, distance=2, height=5e-12)
        if len(peaks) == 0:
            idx = np.argmin(np.abs(masses_window - mass))
            return pressures_window[idx], masses_window[idx]
        
        peak_idx = peaks[np.argmin(np.abs(masses_window[peaks] - mass))]
        return smoothed_pressures[peak_idx], masses_window[peak_idx]



    def plot_mass_evolution_peakfound_relative(self, mass, mass_rel, ax=None, window=5):
        """
        Plots the ratio of the pressure evolution for a specific mass relative to another mass.
        """
        pressures_ratio = []
        times = []

        # Loop through each scan and calculate the pressure ratio between the two masses
        for i in range(len(self.times)):
            p, _ = self.get_peakfound_pressure(mass, i, window=window)
            p_rel, _ = self.get_peakfound_pressure(mass_rel, i, window=window)
            if p is not None and p_rel is not None and p_rel != 0:
                pressures_ratio.append(p / p_rel)
                times.append(self.times[i])

        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 6))

        # Plot the ratio of pressure evolution over time
        ax.plot(times, pressures_ratio, '.', label=f'Mass {mass} amu / Mass {mass_rel} amu')

        ax.set_xlabel('Time')
        ax.set_ylabel(f'Pressure Ratio [{mass}/{mass_rel}]')
        ax.set_yscale('log')
        ax.legend()
        ax.grid(True)

        # Format the x-axis with readable date format
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        plt.gcf().autofmt_xdate()

        plt.show()