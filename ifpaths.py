import networkx as nx
from graphviz import Digraph
#from networkx.drawing.nx_agraph import graphviz_layout, to_agraph

import matplotlib.pyplot as plt

# STATIC DEFS

# beam to feed des:
beam2feeds = {
    "RcvrPF_1":
    {
        "B1": ("XLA_IF", "YRB_IF"),
        "1": ("XLA_IF", "YRB_IF"),
        1: ("XLA_IF", "YRB_IF")
    },

    "Rcvr1_2":
    {
        "B1": ("XL", "YR"),
        "1": ("XL", "YR"),
        1: ("XL", "YR")
    },
    "Rcvr2_3":
    {
        "B1": ("XL", "YR"),
        "1": ("XL", "YR"),
        1: ("XL", "YR")
    },
    "Rcvr4_6":
    {
        "B1": ("XL", "YR"),
        "1": ("XL", "YR"),
        1: ("XL", "YR")
    },
    "Rcvr8_10":
    {
        "B1": ("L", "R"),
        "1": ("L", "R"),
        1: ("L", "R")
    },

}

# converter module pairs
CM_PAIRS = {
    1: "5",
    2: "6",
    3: "7",
    4: "8",
    5: "1",
    6: "2",
    7: "3",
    8: "4",
    9: "13",
    10: "14",
    11: "15",
    12: "16",
    13: "9",
    14: "10",
    15: "11",
    16: "12"
}

RECEIVERS = ["RcvrPF_1", "Rcvr1_2", "Rcvr2_3", "Rcvr4_6", "Rcvr8_10"]
BACKENDS = ["VEGAS", "DCR"]

class PathNode:

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

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


def getPaths(fn):
    "Read paths from python 3 text file derived form python 2 pickle file"
    with open(fn, 'r') as f:
        ls = f.readlines()
    return [eval(l) for l in ls]
    
def getDeviceLikeNodes(g, device):
    "Return nodes in graph that have part of given name in their device"
    return [x for x in g.nodes() if device in g.nodes()[x]['data'].device]

def getDeviceNodes(g, device):
    "Return nodes in graph that have given device name"
    return [x for x in g.nodes() if g.nodes()[x]['data'].device == device]

def getPortLikeNodes(g, port):
    "Return nodes in graph that have part of given name in their port"
    return [x for x in g.nodes() if port in g.nodes()[x]['data'].port]

def getPortNodes(g, port):
    "Return nodes in graph that have given port name"
    return [x for x in g.nodes() if g.nodes()[x]['data'].port == port]

def getFrontendNodes(g):
    "Return nodes with nothing going into them, but something coming out"
    return [x for x in g.nodes() if g.out_degree(x) >= 1 and g.in_degree(x)==0]

def getFrontendFeeds(g, feed):
    "We call the port of a frontend (receiver) node a feed"
    nodes = getFrontendNodes(g)
    return [n for n in nodes if getNodeInfo(g, n).port == feed]

def getFrontend(g):
    "Graphs should all start with the same receiver"
    rcvrs = set([getNodeInfo(g, n).device for n in getFrontendNodes(g)])
    assert len(list(rcvrs))
    return list(rcvrs)[0]

def getBackendNodes(g):
    "Return nodes with nothing coming out of them, but something going in"
    return [x for x in g.nodes() if g.in_degree(x) >= 1 and g.out_degree(x)==0]

def getBackends(g):
    "Lists all backends found in the graph"
    ns = getBackendNodes(g)
    return set([g.nodes()[node]['data'].device for node in ns])

def getNodeInfo(g, nodeName):
    "provides access to the associated PathNode object for nodeName"
    return g.nodes()[nodeName]['data']

def pathHasDevice(path, device):
    "Returns whether the given list of devices has something like the device in it"
    hasDevice = False
    for node in path:
        if device in node:
            hasDevice = True
            break
    return hasDevice

def getSortedBackendNodes(g, backend):
    "Sort by integer port number"
    backendNodes = [getNodeInfo(g, b) for b in getBackendNodes(g) if backend in b]
    backendNodes = sorted(backendNodes, key = lambda b: b.getPortNumber())
    return [b.name for b in backendNodes]

def getFrontBackendPaths(g, frontend, backend):
    "Returns all paths between the given frontend and backend in the given graph"
    ns = getFrontendNodes(g)
    fns = [n for n in ns if g.nodes()[n]['data'].device == frontend]

    ns = getBackendNodes(g)
    bns = [n for n in ns if g.nodes()[n]['data'].device == backend]
    
    paths = []
    for fn in fns:
        for bn in bns:
            ps = list(nx.all_simple_paths(g, source=fn, target=bn))
            #print(fn, bn, ps)
            paths.extend(ps)
    
    return paths

def drawGraph(receiver, backend=None, fn=None):
    "Returns a graph from the pickled cabling file for given receiver"

    if fn is None:
        fn = "zdb.pkl.%s.txt" % receiver

    ps = getPaths(fn)
    #print(ps)

    # make a graph of it!
    #path = ps[0]

    D = Digraph()

    for path in ps:
        # just draw for certain backend?
        if backend is not None and backend not in path[-1]: 
            continue

        prevNode = None
        for node in path:
            pg = node.replace(":", "_")
            D.node(pg)
            if prevNode is not None:
                D.edge(prevNode, pg)
            prevNode = pg
            
    D.view(receiver)
                    
def getGraph(receiver, draw=False, test=False, filepath=None):
    "Returns a graph from the pickled cabling file for given receiver"

    if filepath is None:
        fn = "zdb.pkl.%s.txt" % receiver
    else:
        fn = filepath

    ps = getPaths(fn)
    #print(ps)

    # make a graph of it!
    #path = ps[0]

    #G = nx.MultiDiGraph()
    G = nx.DiGraph()
    D = Digraph()

    for path in ps:
        #print(path)

        prevNode = None
        prevGNode = None
        for p in path:
            pn = PathNode(p)
            G.add_node(p, data=pn)

            # graphviz can't handle ':'
            pg = p.replace(":", "_")
            D.node(pg)
            

            if prevNode is not None:
                G.add_edge(prevNode, p)
                D.edge(prevGNode, pg)

            prevNode = p
            prevGNode = pg

    if test:
        print ("simple paths from one end to another: ")
        #xl = "XLA_IF" # "XL"
        xl = "XL" if receiver != "RcvrPF_1" else "XLA_IF"
        src = "%s:%s" % (receiver, xl)
        target = ps[0][-1] #'DCR:B_1"
        print("Paths between: ", src, target)
        for pp in nx.all_simple_paths(G, source=src, target=target):
            print(pp)
    
        ps = getFrontBackendPaths(G, receiver, "VEGAS")
        print("Paths from Rcvr1_2 to VEGAS: ", len(ps))
        print(ps)
        for p in ps:
            print(p[0], p[-1])
            if p[-1] == "VEGAS:J1":
                print(p)
    
        print(getDeviceNodes(G, "ConverterModule1"))
        print(getDeviceLikeNodes(G, "ConverterModule"))


    if draw:
        D.view('test')
        nx.draw(G, with_labels=True)
        #A = to_agraph(G)
        #A.layout('dot')
        #nx.draw(A)
        #pos = nx.spring_layout(G, iterations=10)
        #nx.draw(G, pos, with_labels=True)
        plt.show()
    

    return G

def chooseVegasPaths(ifGraph, rx, neededBeam, debug=False):
    """
    For the given receiver and beam information,
    chooses paths between the receiver and the vegas backend,
    based off these rules:
       * first path is arbitrary
       * second path chosen with contraints:
          * must use other receiver feed from first
          * vegas port must be one port above or below from first
          * must use the converter module twin used in first path

    Several edge cases this algorithm does not handle:
       * user specified bank
       *       
    """

    # shorthand for the graph of the IF system (all available paths)
    g = ifGraph

    backend = "VEGAS"

    # find first path!  Then we'll find a second path.
    
    # what are the feeds for our given beam?
    feeds = beam2feeds[rx][neededBeam]

    # # arbitrarily pick the first path
    feed1path = getArbitraryFirstPath(g, rx, backend, neededBeam, debug=debug)
    firstBackendNode = feed1path[-1]

    # now find a second path that uses:
    #  * the other feed
    #  * the other vegas port number
    #  * the other converter module

    # what's the backend port number for this one?
    # backendPortNumber = g.nodes()[firstBackendNode]['data'].getPortNumber()
    backendPortNumber = getNodeInfo(g, firstBackendNode).getPortNumber()

    # what's the next port number to be? one up, or one down
    nextBePortNum = backendPortNumber + 1 if backendPortNumber % 2 else backendPortNumber - 1
    # Avoid string parsing and formating here - abstract it out elsewhere:
    #nextBackendNode = "%s:J%s" % (backend, nextBePortNum)
    nextBackendNode = getNodeInfo(g, firstBackendNode).getNameForPortNumber(nextBePortNum)

    # which converter module is used?
    CM = "ConverterModule"
    cms = [p for p in feed1path if CM in p]
    if debug:
        print("CM in feed1path: ", cms)
    assert len(cms) == 2
    cmId = int(getNodeInfo(g, cms[0]).device[-1])

    nextCMId = CM_PAIRS[cmId]
    nextCMDevice = "%s%s" % (CM, nextCMId)
    nextCMNodes = getDeviceNodes(g, nextCMDevice)
    if debug:
        print("next CM to use: ", nextCMDevice)

    # now we get our second feed, and we have all the constraint info
    feed2 = feeds[1]
    starts = getPortNodes(g, feed2)
    firstFeed2Node = starts[0]

    # find the paths between our feed and the other vegas port number
    feed2paths = list(nx.all_simple_paths(g, source=firstFeed2Node, target=nextBackendNode))

    if debug:
        print("found # paths between %s and %s: %d" % (firstFeed2Node, nextBackendNode, len(feed2paths)))

    # use only paths that use the next converter module
    feed2paths = [path for path in feed2paths if pathHasDevice(path, nextCMDevice)]

    if debug:
        print("Paths that only use this converter module:", nextCMDevice)
        print(feed2paths)

    # arbitrarily pick the first one
    feed2path = feed2paths[0]

    if debug:
        print("FINAL PATHS:")
        print(feed1path)
        print(feed2path)

    return [feed1path, feed2path]

def chooseDcrPaths(ifGraph, rx, beam, debug=False):
    # shorthand for the graph of the IF system (all available paths)
    g = ifGraph

    backend = "DCR"
    IFXS = "IFXS"

    # find first path!  Then we'll find a second path.
    feed1path = getArbitraryFirstPath(ifGraph, rx, backend, beam, debug=debug)

    feeds = beam2feeds[rx][beam]

    # reject other paths that don't have the same IFXS setting as this path.
    # what is that setting?
    ifxs1s = [p for p in feed1path if IFXS in p]
    if len(ifxs1s) == 0:
        ifxsSetting1 = None
    else:
        ifxsSetting1 = getNodeInfo(g, ifxs1s[0]).port

    # Find the next feed, with criteria:
    #   * different polarization, or feed
    #   * different backend node
    #   * if IFXS node is used, make sure port (setting) is the same

    # now get the other feed
    feed2 = feeds[1]

    # and get the nodes that use this port
    starts = getFrontendFeeds(g, feed2)
    firstFeed2Node = starts[0]

    # get all paths between this feed and other backend nodes: remove first backend node
    backendNodes = getSortedBackendNodes(g, backend)
    firstBackendNode = feed1path[-1]
    unusedBackendNodes = [b for b in backendNodes if b != firstBackendNode]

    # go through all possiblilities till you find a match
    feed2path = None
    for backendNode in unusedBackendNodes:
        feed2paths = list(nx.all_simple_paths(g, source=firstFeed2Node, target=backendNode))
        if debug:
            print("found # paths between %s and %s: %d" % (firstFeed2Node, backendNode, len(feed2paths)))
            print(feed2paths) 
        
        # go through these paths, and check for IFXS setting
        for path in feed2paths:
            ifxs2s = [p for p in path if IFXS in p]
            if len(ifxs2s) == 0:
                ifxsSetting2 = None
            else:
                ifxsSetting2 = getNodeInfo(g, ifxs2s[0]).port
            if ifxsSetting2 == ifxsSetting1:
                feed2path = path
                break
        # are we done yet?
        if feed2path is not None:
            break

    return feed1path, feed2path                    


def getArbitraryFirstPath(ifGraph, rx, backend, beam, debug=False):
    "Choose the first path you come across that gets you from the first rx feed to the backend"

    # short hand
    g = ifGraph

   # what are the feeds for our given beam?
    feeds = beam2feeds[rx][beam]

    # get a path with the first feed to backend:
    # what are the graph nodes for our backend?  Sorting by port number
    backendNodes = getSortedBackendNodes(g, backend)

    if debug:
        print("Backend nodes: ", backendNodes)

    # start arbitrarly with the first feed
    feed1 = feeds[0]

    # and get the nodes that use this port
    #starts = getPortNodes(g, feed1)
    starts = getFrontendFeeds(g, feed1)
    firstFeed1Node = starts[0]

    if debug:
        print("feed1 nodes:", feed1, starts)

    # now simply find all the paths from the first of our feeds, to an arbitrary backend node       
    # firstBackendNode = backendNodes[0]
    feed1path = None
    for backendNode in backendNodes:
        feed1paths = list(nx.all_simple_paths(g, source=firstFeed1Node, target=backendNode))
        if debug:
            print("found # paths between %s and %s: %d" % (firstFeed1Node, backendNode, len(feed1paths)))
            print(feed1paths) 
        if len(feed1paths) > 0:    
            # arbitrarily pick the first path
            feed1path = feed1paths[0]
            break

    return feed1path

def test1():
    "Mimics results of IFPathTests.test_config_paths"

    # results of 'collapsing' IF
    wins = [[{'filter_bw': 1400, 'tint': 0.2, 'number_spectra': 1, 'deltafreq': 0, 'res': 5.7, 'vel_freq': 750.0, 'if3': 750, 'valonFreq': 1500, 'beam': '1', 'bandwidth': 23.44, 'vpol': 'self', 'subband': None, 'mode': 'MODE20', 'upper_tolerance': 1400, 'restfreq': 750, 'lower_tolerance': 150, 'nchan': 4096}]]
    beam = wins[0][0]['beam']
    rx = "RcvrPF_1"
    g = getGraph(rx)
    paths = chooseVegasPaths(g, rx, beam)

    assert len(paths) == 2
    exp1 = ['RcvrPF_1:XLA_IF', 'PF_IF_Conditioner:J1', 'PF_IF_Conditioner:XLA', 'PF_XLA:0', 'PF_XLA:1', 'IFRouter:J1', 'SWITCH1', 'IFXS9:thru', 'IFRouter:J65', 'OpticalDriver1:J1', 'OpticalDriver1:J2', 'OpticalReceiver1:J1', 'OpticalReceiver1:A', 'ConverterModule1:J1', 'ConverterModule1:J9', 'VEGAS_IF:J1', 'VEGAS_IF:J17', 'VEGAS:J1']
    exp2 = ['RcvrPF_1:YRB_IF', 'PF_IF_Conditioner:J2', 'PF_IF_Conditioner:YRB', 'PF_YRB:0', 'PF_YRB:1', 'IFRouter:J17', 'SWITCH3', 'IFXS10:thru', 'IFRouter:J67', 'OpticalDriver3:J1', 'OpticalDriver3:J2', 'OpticalReceiver3:J1', 'OpticalReceiver3:A', 'ConverterModule5:J1', 'ConverterModule5:J9', 'VEGAS_IF:J2', 'VEGAS_IF:J18', 'VEGAS:J2']
    assert paths[0] == exp1
    assert paths[1] == exp2

def test2():
    "Mimics VEGASTests.testBasic"

    # restuls of 'collapsing' IF
    wins = {'filter_bw': 1400, 'tint': 1.0, 'number_spectra': 2, 'deltafreq': 0, 'if3': 750, 'res': 5.7, 'vel_freq': 1400.0, 'beam': '1', 'bandwidth': 23.44, 'vpol': 'self', 'mode': 20, 'restfreq': 1400, 'subband': 8, 'nchan': 4096}
    beam = wins['beam']

    rx = "Rcvr1_2"
    g = getGraph(rx)
    
    paths = chooseVegasPaths(g, rx, beam)    

    assert len(paths) == 2
    exp1 = ['Rcvr1_2:XL', 'R1_2XL:0', 'R1_2XL:1', 'IFRouter:J2', 'SWITCH1', 'IFXS9:thru', 'IFRouter:J65', 'OpticalDriver1:J1', 'OpticalDriver1:J2', 'OpticalReceiver1:J1', 'OpticalReceiver1:A', 'ConverterModule1:J1', 'ConverterModule1:J9', 'VEGAS_IF:J1', 'VEGAS_IF:J17', 'VEGAS:J1']
    exp2 = ['Rcvr1_2:YR', 'R1_2YR:0', 'R1_2YR:1', 'IFRouter:J18', 'SWITCH3', 'IFXS10:thru', 'IFRouter:J67', 'OpticalDriver3:J1', 'OpticalDriver3:J2', 'OpticalReceiver3:J1', 'OpticalReceiver3:A', 'ConverterModule5:J1', 'ConverterModule5:J9', 'VEGAS_IF:J2', 'VEGAS_IF:J18', 'VEGAS:J2']
    assert paths[0] == exp1
    assert paths[1] == exp2

def test3():
    "Find paths for a bunch of receivers"

    for rx in RECEIVERS:
        g = getGraph(rx)
        paths = chooseDcrPaths(g, rx, 1, debug=False)
        # print("DCR paths: ", rx, paths)
        assert len(paths) == 2
        # drawGraph(rx, backend="VEGAS")
        paths = chooseVegasPaths(g, rx, 1, debug=False)
        assert len(paths) == 2

def test4():
    "Find paths for a bunch of receivers"

    for rx in RECEIVERS:
        fn = "zdb.201118.pkl.%s.txt" % rx
        g = getGraph(rx, filepath=fn)
        paths = chooseDcrPaths(g, rx, 1, debug=False)
        # print("DCR paths: ", rx, paths)
        assert len(paths) == 2
        # drawGraph(rx, backend="VEGAS")
        paths = chooseVegasPaths(g, rx, 1, debug=False)
        assert len(paths) == 2
        # print("VEGAS paths: ", rx, paths)

def test5():
    "Finds paths for 'Cont. with Rcvr1_2' config"

    # from TINT tests

    expCabling = [
        ['Rcvr1_2:J3', 'R1_2XL:0', 'R1_2XL:1', 'IFRouter:J2', 'SWITCH1', 'IFXS9:thru', 'IFRouter:J65', 'OpticalDriver1:J1', 'OpticalDriver1:J4', 'DCR:J1'],
        ['Rcvr1_2:J4', 'R1_2YR:0', 'R1_2YR:1', 'IFRouter:J18', 'SWITCH3', 'IFXS10:thru', 'IFRouter:J67', 'OpticalDriver3:J1', 'OpticalDriver3:J4', 'DCR:J3']
    ]
    exp = [
        ['Rcvr1_2:XL', 'R1_2XL:0', 'R1_2XL:1', 'IFRouter:J2', 'SWITCH1', 'IFXS9:thru', 'IFRouter:J65', 'OpticalDriver1:J1', 'OpticalDriver1:J4', 'DCR:A_1'],
        ['Rcvr1_2:YR', 'R1_2YR:0', 'R1_2YR:1', 'IFRouter:J18', 'SWITCH3', 'IFXS10:thru', 'IFRouter:J67', 'OpticalDriver3:J1', 'OpticalDriver3:J4', 'DCR:A_3']
    ]

    rx = "Rcvr1_2"
    fn = "zdb.201118.pkl.%s.txt" % rx
    g = getGraph(rx, filepath=fn)
    paths = chooseDcrPaths(g, rx, 1, debug=False)
    # print("DCR paths: ", rx, paths)
    assert len(paths) == 2
    assert paths[0] == exp[0]
    assert paths[1] == exp[1]

def main():
    # make sure it all works
    test1()
    test2()
    test3()
    test4()
    test5()
    print("completed all tests")

if __name__ == '__main__':
    main()
