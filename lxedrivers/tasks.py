from srsinst.rga.tasks.analogscantask import AnalogScanTask
from srsinst.rga import RGA100

class IsotopeAnalysis(AnalogScanTask):

    def __init__(self):
        print('Initializing IsotopeAnalysis class...')
        super().__init__()
        