from copy import copy

from IFPath import IFPath

class IFPaths():

    """
    This class is responsible for organizing and interpreting more then
    one path through the IF system.  This means a list of IFPath objects,
    which in turn, contain each lists of IFPathNode objects. 
    """

    def __init__(self, ifPaths):

        # IFPaths are made up of plural IFPath
        self.paths = []
        for path in ifPaths:
            if isinstance(path, IFPath):
                self.paths.append(copy(path))
            else:    
                self.paths.append(IFPath(copy(path)))

    def printSummary(self):
        "Just print start and end of each path"
        for p in self.paths:
            print(p.path[0], " -> ", p.path[-1])

    def getFrontendFeeds(self, feed):
        "We call the port of a frontend (receiver) node a feed"
        nodes = self.getFrontendNodes()
        return [n for n in nodes if n.port == feed]

    def getFrontendNodes(self):
        "Get the first node of each path"
        return [p.path[0] for p in self.paths]

    def getBackendNodes(self):    
        "Get the last node of each path"
        return [p.path[-1] for p in self.paths]

    def getSortedBackendNodes(self, backend):
        "Sort by integer port number"
        backendNodes = [b for b in self.getBackendNodes() if backend in b.name] #[path[-1] for path in paths]
        backendNodes = sorted(backendNodes, key = lambda b: b.getPortNumber())
        # return [b.name for b in backendNodes]
        return backendNodes

    def getMatchingPaths(self, start, end):
        "Return those paths that share the given start and end"
        return [p for p in self.paths if p.path[0] == start and p.path[-1] == end]

    def prunePathsForBackend(self, backend):
        "Let's remove all paths that don't end with the given backend"

        self.paths = [path for path in self.paths if backend in path.getBackendNode().name]

    def printFreqs(self):
        "Shows the IFInfo graphically (bandpasses) for each path"

        for path in self.paths:
            print("path: ", path)

            # one can show the bandpasses this way, but then
            # the graphic bandpass is not calibrated correctly
            # for node in path:
            #     if node.ifInfo is not None:
            #         print ("  node:", node)
            #         bps = node.ifInfo.bandpasses
            #         bps.show()

            # gather all the bandpasses for this path so that
            # we can have the scale right when drawing each bandpass
            # bps = []
            # for node in path:
            #     if node.ifInfo is not None and node.ifInfo.bandpasses is not None:
            #         bps.extend(node.ifInfo.bandpasses.bandpasses)
            # bps = Bandpasses(bps)
            bps = path.aggregatePathBandpasses()
            bps.show()