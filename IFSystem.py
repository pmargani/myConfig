class IFSystem:

    def __init__(self, paths, receiver, if1, ifCenter, tuningFreq, bwTotal, velocity, vdef, vframe):

        # [[IFPathNode]]
        self.paths = paths

        # rx name
        self.receiver = receiver

        # TBF: I don't understand all this frequency stuff
        self.if1 = if1
        self.ifCenter = ifCenter
        self.tuningFreq = tuningFreq
        self.bwTotal = bwTotal

        # velocity related
        self.velocity = velocity
        self.vdef = vdef
        self.vframe = vframe

    def getFirstLikeDeviceNode(self, path, device):
        "Retrieves first node in path that is like given device name"
        devices = [n for n in path if device in n.name]
        return None if len(devices) == 0 else devices[0]
