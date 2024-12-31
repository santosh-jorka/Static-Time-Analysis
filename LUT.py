class LUT:
    def __init__(self, cellName, inputSlews, loadCap, delays):
        self.cellName = cellName
        self.inputSlews = inputSlews
        #self.inputCap = inputCap
        self.loadCap = loadCap
        self.delays = delays