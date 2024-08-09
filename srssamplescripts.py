import os
import sys
import subprocess
from datetime import datetime
import matplotlib.pyplot as plt
import argparse
import numpy as np
import time
import signal

def is_venv_active():
    return (
        hasattr(sys, 'real_prefix') or  # Python 2 and some versions of Python 3
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)  # Modern Python 3
    )

def activate_venv(venv_path):
    activate_script = os.path.join(venv_path, 'Scripts', 'activate.bat')
    subprocess.call(activate_script, shell=True)

def generate_filename(prefix):
    # Get the current date and time
    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create the filename with the prefix and current time
    filename = f"{prefix}_{current_time}.txt"
    
    return filename

def get_partial_pressures(isotopes, mass_axis, pressures):
    mass_indices = np.array([np.argmin(np.abs(mass_axis - i)) for i in isotopes])
    partial_pressures = np.array(pressures)[mass_indices]
    return partial_pressures


def get_abundances(pressures):
    total_pressure = np.sum(pressures)
    return pressures*100/total_pressure

def disconnect_rga(rga):
    rga1.filament.turn_off()
    rga.disconnect()

shutdown_requested = False

def signal_handler(signal, frame):
    global shutdown_requested
    print("Shutdown requested. Waiting for the current scan to finish...")
    shutdown_requested = True



def main():

    global shutdown_requested

    parser = argparse.ArgumentParser(description="Process scan parameters.")

    # Add arguments
    parser.add_argument(
        'file_prefix', 
        type=str, 
        help='The file prefix as a string.'
    )
    parser.add_argument(
        '-s', '--scan_speed', 
        type=int, 
        required=False,
        default=1
        help='The scan speed as an integer.'
    )
    parser.add_argument(
        '-r', '--scan_resolution', 
        type=int, 
        required=False,
        default=20
        help='The scan resolution as an integer.'
    )

    # Parse the arguments
    args = parser.parse_args()
    file_prefix = args.file_prefix
    scan_speed = args.scan_speed
    scan_resolution = args.scan_resolution

    # Path to your virtual environment
    venv_path = r'C:\Users\lxere\Software'

    if not is_venv_active():
        print("Virtual environment is not active. Activating now...")
        activate_venv(venv_path)
    else:
        print("Virtual environment is already active.")

    # def check_virtual_env():
    #     venv_path = r'C:\Users\lxere\Software\srsnst-rga-env\Scripts\activate'
    #     if sys.executable == venv_path:
    #         print(f"Virtual environment is actives: {sys.executable}")
    #     else: 
    #         print(f"No virtual enviroment is active")

    # check_virtual_env()

    # connect rga
    from srsinst.rga import RGA100
    tries = 0
    while(tries < 5):
        try:
            rga1 = RGA100('serial', 'COM4', 28800)
            break
        except UnicodeDecodeError:
            print('Connection error! Trying again...')
            tries += 1
            time.sleep(2)
    if tries == 5:
        print('Error: could not connect to the RGA!')
        sys.exit()
    rga1.check_id()

    if rga1.ionizer.emission_current < 0.8:
        rga1.filament.turn_on()
        print('Filament turned on.')
    else:
        print('Filament already on.')

    print('Setting up scan...')

    rga1.scan.set_parameters(1, 150, scan_speed, scan_resolution)
    print('RGA scan parameters set to:')
    print(rga1.scan.get_parameters())

    data_folder = r'C:\Users\lxere\Software\srsinst-rga-env\myscripts\data'
    prefix = data_folder + r'\\' + file_prefix

    signal.signal(signal.SIGINT, signal_handler)

    print("Program is running. Press Ctrl+C to exit.")
    
    files_written = 0
    try:
        if shutdown_requested:
            print("Finishing current scan before shutdown...")

        while(True):
            this_file = generate_filename(prefix)
            mass_axis = rga1.scan.get_mass_axis(for_analog_scan=True)
            spectrum = rga1.scan.get_analog_scan()
            spectrum_in_torr = rga1.scan.get_partial_pressure_corrected_spectrum(spectrum)

            isotopes = [124 + i for i in range(13)]
            pressures = get_partial_pressures(isotopes, mass_axis, spectrum_in_torr)
            abundances = get_abundances(pressures)

            [print('Xenon {}: {} percent'.format(isotopes[i], abundances[i])) for i in range(len(isotopes))]

            with open(this_file, 'w') as f:
                for x, y in zip(mass_axis, spectrum_in_torr):
                    f.write('{:.2f} {:.4e}\n'.format(x, y))
            files_written += 1

            print('File number ' + str(files_written) + ' written to ' + this_file)

            if shutdown_requested:
                break

    except KeyboardInterrupt:
        disconnect_rga(rga1)

        disconnect_rga(rga1)

        # fig, ax = plt.subplots()
        # ax.semilogy(mass_axis, spectrum_in_torr)
        # ax.set_xlabel('Mass [amu]')
        # ax.set_ylabel('Partial pressure [torr]')
        # ax.set_title('Analog scan')
        # ax.grid(which='both')
        # plt.show()




if __name__=='__main__':
    main()