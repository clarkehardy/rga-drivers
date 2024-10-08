from srsinst.rga.tasks.analogscantask import AnalogScanTask
from srsgui import InstrumentInput, IntegerInput, ListInput, StringInput
from rgadrivers.utils import *
from rgadrivers.analysis import *
import os

class IsotopeAnalysis(AnalogScanTask):

    InstrumentName = 'instrument to control'
    StartMass = 'start mass'
    StopMass = 'stop mass'
    ScanSpeed = 'scan speed'
    StepSize = 'step per AMU'
    IntensityUnit = 'intensity unit'
    OutputDirectory = 'Output directory'

    # input_parameters values can be changed interactively from GUI
    input_parameters = {
        InstrumentName: InstrumentInput(),
        StartMass: IntegerInput(1, " AMU", 0, 319, 1),
        StopMass: IntegerInput(150, " AMU", 1, 320, 1),
        ScanSpeed: IntegerInput(1, " ", 0, 9, 1),
        StepSize: IntegerInput(20, " steps per AMU", 10, 80, 1),
        IntensityUnit: ListInput(['Partial Pressure (Torr)', 'Ion current (fA)']),
        OutputDirectory: StringInput(r'C:\Users\lxere\Software\rga-drivers\data')
    }
    
    def setup(self):
        print('Setting up IsotopeAnalysis measurement...')
        self.file_prefix = 'analog_scan'
        super().setup()
        print('Starting measurement...')

    def test(self):
        self.set_task_passed(True)
        self.add_details('{}'.format(self.id_string), key='ID')

        # make the output directory if it doesn't already exist
        os.makedirs(self.params['Output directory'], exist_ok=True)

        files_written = 0
        while self.is_running():
            try:
                # run the scan
                spectrum = self.rga.scan.get_analog_scan()
                output_dir = self.params['Output directory']
                this_file = output_dir + r'\\' + generate_filename(self.file_prefix)
                mass_axis = self.rga.scan.get_mass_axis(for_analog_scan=True)
                spectrum_in_torr = self.rga.scan.get_partial_pressure_corrected_spectrum(spectrum)

                # compute the uncalibrated abundances
                isotopes = [124 + i for i in range(13)]
                pressures = get_partial_pressures(isotopes, mass_axis, spectrum_in_torr)
                abundances = get_abundances(pressures)
                [print('Xenon {}: {:.3} percent'.format(isotopes[i], abundances[i])) for i in range(len(isotopes))]

                # save the data to a file
                with open(this_file, 'w') as f:
                    f.write('Mass [amu], Pressure [torr]\n')
                    for x, y in zip(mass_axis, spectrum_in_torr):
                        f.write('{:.2f}, {:.4e}\n'.format(x, y))
                files_written += 1

                print('Scan ' + str(files_written) + ' written to ' + this_file)

            except Exception as e:
                self.set_task_passed(False)
                self.logger.error('{}: {}'.format(e.__class__.__name__, e))
                if not self.rga.is_connected():  # Check if RGA is connected.
                    self.logger.error('"{}" is disconnected'.format(self.params[self.InstrumentName]))
                    break

        