from Bandpasses import Bandpasses

RECEIVERS = ["RcvrPF_1", "Rcvr1_2", "Rcvr2_3", "Rcvr4_6", "Rcvr8_10"]
BACKENDS = ["VEGAS", "DCR"]
MULTI_DEVICES = ["ConverterModule", "OpticalDriver", "ConverterFilter", 
    "OpticalReceiver", "SWITCH", "IFXS"]

class IFInfo:

    def __init__(self):

        self.bandpasses = None
        self.filters = None
        self.lo = None

class IFPathNode:

    """
    Represents a device:port combination as represented
    in the cabling file and seen in the config tool
    cabling pickle file
    """

    def __init__(self, name):

        self.name = name

       # deconstruct the name into it's components
        if ':' in name:
            device, port = name.split(':')
        else:
            device = name
            port = None

        self.device = device
        self.port = port

        # try to identify this node
        if device in RECEIVERS:
            self.type = "Receiver"
        elif device in BACKENDS:
            self.type = "Backend"
        else:
            self.type = None

        # if it's not a front or backend, try to determine it's 
        # 'device ID': example ConverterModule2 -> 2
        self.deviceId = None
        if self.type is None:
            for d in MULTI_DEVICES:
                if d in self.name:
                    # try:
                        # "ConverterModule2" -> "", "2"

                    _, self.deviceId = self.device.split(d)
                    self.deviceId = int(self.deviceId)
                    break
                    # except:
                        # pass    
        # IF info:
        self.ifInfo = None
        # what are the frequency attributes at this point in the path?
        # self.has
        # self.ifFreq = None
        # self.skyFreq = None
        # self.bw = None
        # self.bandpasses = None
        # # are we mixing anything in?
        # self.lo = None
        # # any filters being applied?
        # self.filters = []

    def getBankName(self):
        if self.type != 'Backend':
            return None
        return self.port[0]
            
    def getPortNumber(self):
        " 'J1' => 1 "
        # TBF: should be handled by class heirarchy?
        if self.type == "Receiver":
            return None
        if self.device == "DCR":
            # 'A_10' -> 10
            return int(self.port[2:]) 
        return self.getTypicalPortNumber()
               
    def getTypicalPortNumber(self):    
        " 'J1' => 1 "
        try:
            portNumber = int(self.port[1:])
        except:
            portNumber = -1
        return portNumber

    def getNameForPortNumber(self, portNumber):
        " 2: VEGAS:J1 => VEGAS:J2"
        return "%s:%s%d" % (self.device, self.port[:1], portNumber)

    def setBandpasses(self, bandpassList):
        if self.ifInfo is None:
            self.ifIfno = IFInfo()
        self.ifInfo.bandpasses = Bandpasses(bandpassList)


    def __eq__(self, other): 
        "comparisons simply use the name of the node"

        if not isinstance(other, IFPathNode):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.name == other.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name