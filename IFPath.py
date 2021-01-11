from Bandpasses import Bandpasses

class IFPath():

    """
    This list is responsible for containing and interpreting a single
    path through the IF system, stored as a list of IFPathNodes
    """

    def __init__(self, ifPathNodes):

        # a list of IFPathNodes
        self.path = ifPathNodes

    def __str__(self):
        return "IFPath (%s -> %s)" % (self.path[0], self.path[-1])

    def getSummary(self):
        return "IFPath (%s -> %s)" % (self.path[0], self.path[-1])

    def getNodeNameList(self):
        return [p.name for p in self.path]

    def getBackendNode(self):
        "Assume it's the last one!"
        return self.path[-1]

    def getUniqueDeviceNode(self, device):
        "Retrieves node in path that is like given name, assuming it appears just once or never"
        devices = [n for n in self.path if device in n.name]
        assert len(devices) < 2
        return None if len(devices) == 0 else devices[0]

    def getFirstLikeDeviceNode(self, device):
        "Retrieves first node in path that is like given device name"
        devices = [n for n in self.path if device in n.name]
        return None if len(devices) == 0 else devices[0]        

    def aggregatePathBandpasses(self):
        "Put together bandpasses for each node in given path to one collection"

        # one motivation is the fact that Bandpasses.show() needs them to all be on 
        # the same scale to visualize correctly
        bps = []
        for node in self.path:
            if node.ifInfo is not None and node.ifInfo.bandpasses is not None:
                bps.extend(node.ifInfo.bandpasses.bandpasses)
        bps = Bandpasses(bps)
        return bps

    def getBandpassUpToNode(self, targetNode):
        "Returns the bandpass as it appears before the given node"
        
        bp = None
        for node in self.path:
            if node == targetNode:
                break
            if node.ifInfo is not None and node.ifInfo.bandpasses is not None:
                bp = node.ifInfo.bandpasses.bandpasses[-1]
        return bp