from copy import copy

# from ifpaths import *
from paths import getIFPaths
from StaticDefs import IF3, IFfilters, BEAM_TO_FEED_DES, FILTERS, RCVR_IF_NOMINAL, RCVR_SIDEBAND, vframe
from StaticDefs import RCVR_FREQS
from Vdef import Vdef
from MinMaxFreqs import MinMaxFreqs
from IFPathNode import IFPathNode, IFInfo
from Bandpasses import Bandpasses, Bandpass

LO1_FIRST_RXS = ['Rcvr8_10']


def getBandpassUpToNode(path, targetNode):
    "Returns the bandpass as it appears before the given node"
    
    bp = None
    for node in path:
        if node == targetNode:
            break
        if node.ifInfo is not None and node.ifInfo.bandpasses is not None:
            bp = node.ifInfo.bandpasses.bandpasses[-1]
    return bp

def traceFreqs(paths):
    "Shows the IFInfo graphically (bandpasses) for each path"

    for path in paths:
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
        bps = []
        for node in path:
            if node.ifInfo is not None and node.ifInfo.bandpasses is not None:
                bps.extend(node.ifInfo.bandpasses.bandpasses)
        bps = Bandpasses(bps)
        bps.show()

def getFrontendFeeds(g, feed):
    "We call the port of a frontend (receiver) node a feed"
    nodes = getFrontendNodes(g)
    return [n for n in nodes if n.port == feed]

def getFrontendNodes(paths):
    "Get the first node of each path"
    return [p[0] for p in paths]

def getBackendNodes(paths):    
    "Get the last node of each path"
    return [p[-1] for p in paths]

def getSortedBackendNodes(paths, backend):
    "Sort by integer port number"
    backendNodes = [b for b in getBackendNodes(paths) if backend in b.name] #[path[-1] for path in paths]
    backendNodes = sorted(backendNodes, key = lambda b: b.getPortNumber())
    # return [b.name for b in backendNodes]
    return backendNodes

def getMatchingPaths(paths, start, end):
    "Return those paths that share the given start and end"
    return [path for path in paths if path[0] == start and path[-1] == end]
            
def getUniqueDeviceNode(path, device):
    "Retrieves node in path that is like given name, assuming it appears just once or never"
    devices = [n for n in path if device in n.name]
    assert len(devices) < 2
    return None if len(devices) == 0 else devices[0]

def getFirstLikeDeviceNode(path, device):
    "Retrieves first node in path that is like given device name"
    devices = [n for n in path if device in n.name]
    return None if len(devices) == 0 else devices[0]

def getArbitraryFirstPath(ifPaths, rx, backend, beam, debug=False):
    "Choose the first path you come across that gets you from the first rx feed to the backend"

    # short hand
    g = ifPaths

   # what are the feeds for our given beam?
    feeds = BEAM_TO_FEED_DES[rx][beam]

    # get a path with the first feed to backend:
    # what are the graph nodes for our backend?  Sorting by port number
    backendNodes = getSortedBackendNodes(g, backend)
    backendNames = [b.name for b in backendNodes]

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

    if debug:
        print("paths summary")
        for path in g:
            print(path[0], path[-1])

    # now simply find all the paths from the first of our feeds, to an arbitrary backend node       
    # firstBackendNode = backendNodes[0]
    feed1path = None
    for backendNode in backendNodes:
        feed1paths = getMatchingPaths(g, firstFeed1Node, backendNode)
        # feed1paths = list(nx.all_simple_paths(g, source=firstFeed1Node, target=backendNode))
        if debug:
            print("found # paths between %s and %s: %d" % (firstFeed1Node, backendNode, len(feed1paths)))
            print(feed1paths) 
        if len(feed1paths) > 0:    
            # arbitrarily pick the first path
            feed1path = feed1paths[0]
            break

    return feed1path

def getDCRPaths(config, pathsFile=None, debug=False):
    "Returns the paths that satisfy the given configuration"

    rx = config["receiver"]
    backend = config["backend"]
    assert backend == 'DCR'
    IFXS = "IFXS"

    # get all the default IF paths from the standard source?
    if pathsFile is None:
        pathsFile = "zdb.201118.pkl.%s.txt" % rx

    # TBF: multi-beam rcvrs?
    beam = 1

    paths = getIFPaths(rx, filepath=pathsFile)

    # prune the paths of non-DCR backends
    paths = [p for p in paths if 'DCR' in p[-1].name]

    feed1path = getArbitraryFirstPath(paths, rx, backend, beam, debug=debug)

    feeds = BEAM_TO_FEED_DES[rx][beam]

    ifxs1s = getUniqueDeviceNode(feed1path, IFXS)

    ifxsSetting1 = None if ifxs1s is None else ifxs1s.port

    # Find the next feed, with criteria:
    #   * different polarization, or feed
    #   * different backend node
    #   * if IFXS node is used, make sure port (setting) is the same

    # now get the other feed
    feed2 = feeds[1]

    # and get the nodes that use this port
    starts = getFrontendFeeds(paths, feed2)
    firstFeed2Node = starts[0]
    
     # get all paths between this feed and other backend nodes: remove first backend node
    backendNodes = getSortedBackendNodes(paths, backend)
    firstBackendNode = feed1path[-1]
    unusedBackendNodes = [b for b in backendNodes if b != firstBackendNode]
         
    # go through all possiblilities till you find a match
    feed2path = None
    for backendNode in unusedBackendNodes:
        feed2paths = getMatchingPaths(paths, firstFeed2Node, backendNode)

        # feed2paths = list(nx.all_simple_paths(g, source=firstFeed2Node, target=backendNode))
        if debug:
            print("found # paths between %s and %s: %d" % (firstFeed2Node, backendNode, len(feed2paths)))
            print(feed2paths) 
        
        # go through these paths, and check for IFXS setting
        for path in feed2paths:
            ifxs2s = [p for p in path if IFXS in p.name]
            if len(ifxs2s) == 0:
                ifxsSetting2 = None
            else:
                ifxsSetting2 = ifxs2s[0].port
            if ifxsSetting2 == ifxsSetting1:
                feed2path = path
                break

        # are we done yet?
        if feed2path is not None:
            break

    return feed1path, feed2path  

def setFreqWithVelocity(config, paths):
    "TBF: explain this"

    vlow = config['vlow']
    vhigh = config['vhigh']
    vdef = config['vdef']

    # for no doppler affect, I think we do this:
    config['freq'] = config['restfreq']
    config['dfreq'] = 0

    user_freqs = [config["freq"]]
    user_dfreqs = [config["dfreq"]]

    freqs = user_freqs
    dfreqs = user_dfreqs

    vd = Vdef()
    minMaxFreqs = MinMaxFreqs()

    freqList = []
    freqAvgVels = []

    for freq, dfreq in zip(freqs, dfreqs):
        vd.compute_local_frame_with_vdef(vdef, vhigh, freq, vlow)
        minMaxFreqs.setMin(vd.cur_vlow + dfreq)
        minMaxFreqs.setMax(vd.cur_vhigh + dfreq)
        vel_freq = vd.get_vave() + dfreq
        freqAvgVels.append(vel_freq)
        freqList.append(vel_freq)

    return freqList, dfreqs, freqAvgVels, minMaxFreqs

def compute_Flocal(config):
    """Compute the frequency compensated for the velociy of the source"""
    
    vlow = config['vlow']
    vhigh = config['vhigh']
    vdef = config['vdef']
    lo_restfreq = config["DOPPLERTRACKFREQ"]

    velocity = (vlow + vhigh) * 0.5
    vd = Vdef()
    vd.compute_local_frame_with_vdef(vdef, velocity,
                                               lo_restfreq, velocity)
    # this better be the same as vlow since i sent in the avg
    cur_vhigh = vd.get_vhigh()
    cur_vlow = vd.get_vlow()
    if cur_vhigh != cur_vlow:
        "PANIC: How can the avg velocities differ!!!!!"
    
    return cur_vhigh

def setRxFilters(receiver, tuning_freq, bw_total):
    """Set receiver filters:
        use the first filter in the list for this receiver that
        encompasses the bandwidth defined by the given
        tuning frequency and bandwidth.
    """

    found = 0
    # bw_total = None #self.freq_calc.get_bw_total()
    # if_center = self.freq_calc.get_center_freq()
    # self.if_freq_low = if_center - (0.5 * bw_total)
    # self.if_freq_high = if_center + (0.5 * bw_total)

    # fake the bandwidth?  Nope, too wide, no filter will get selected.
    # TBF: we need to figure out the freq stuff better - start with compute_bw algo.
    # lo, hi = RCVR_FREQS[receiver]
    # bw_total = hi - lo

    if receiver in FILTERS:
        param_names, filters, rcvr_type = FILTERS[receiver]
        bw_low = tuning_freq - (0.5 * bw_total)
        bw_high = tuning_freq + (0.5 * bw_total)
        # if rcvr_type == 0:  # Mixer before filter. Convert filter freq
        #     bw_low = self.if_freq_low
        #     bw_high = self.if_freq_high
        filter_setting = filter_bandwidth = None
        # Choose the first one that encompasses our bw_low and bw_high!
        for freq in filters:
            if bw_low >= freq[0] and bw_high <= freq[1]:
                filter_setting = freq[2]
                filter_bandwidth = freq[1] - freq[0]
                found = 1
                break

    return filter_setting, freq[0], freq[1]  

def setIFFilters(total_bw_low, total_bw_high, ifpath):
    "TBF: explain this"

    params = []
    for path in ifpath:
        filter_value = "pass_all"
        param = None

        for filter_value, fLow, fHigh in IFfilters:
            # fLow = f[1]
            # fHigh = f[2]
            # if f[1] <= total_bw_low and f[2] >= total_bw_high:
                # filter_value = f[0]
            if fLow <= total_bw_low and fHigh >= total_bw_high:
                break
        opticalDriver = getFirstLikeDeviceNode(path, "OpticalDriver")        
        # if "opticalDriver" in path:
        if opticalDriver is not None:
            filterNum = opticalDriver.deviceId # path["opticalDriver"]
            param = "IFRack,filter_select,{}".format(filterNum)
            opticalDriver.ifInfo = IFInfo()
            opticalDriver.ifInfo.filters = []
            opticalDriver.ifInfo.filters.append((param, filter_value))
            bp = getBandpassUpToNode(path, opticalDriver)
            bpFilter = copy(bp)
            bpFilter.filter(fLow, fHigh)
            bpFilter.changes = "%s, (%f, %f)" % (param, fLow, fHigh)
            opticalDriver.setBandpasses([bpFilter])
                # self.seq.add_param(self.mng, fs, self.filter_value)
        params.append((param, filter_value))
    return params 

def getFilterBandpasses(bp1, rxNode):
    bps = []
    bp = copy(bp1)
    for fName, fLow, fHigh in rxNode.ifInfo.filters:
        bp = copy(bp)
        bp.filter(fLow, fHigh)
        bp.changes = "Filter %s (%f, %f)" % (fName, fLow, fHigh)
        bps.append(bp)
    return bps

def getLO1Bandpass(bp1, rxNode, lowerSideband=True):    
    bpLO1 = copy(bp1)
    loMixFreq = rxNode.ifInfo.lo['freq']
    bpLO1.mix(loMixFreq, lowerSideband=lowerSideband)
    sideband = "lower" if lowerSideband else "upper"
    bpLO1.changes = "LO %s sideband at %f" % (sideband, loMixFreq)
    return bpLO1

def calcFreqs(config, paths):
    "Make the bandpass decisions to get our signal to the backend"

    # we'll return what manager parameters are set here
    params = []

    # At minimum:
    # set filters in receiver
    # set LO1 freq
    # set optical driver freqs
    
    receiver = config['receiver']
    backend = config['backend']

    # first see if there's a doppler shift
    if config['vframe'] is not None and config['vframe'] != 'topo':
        # can't handle this
        assert False

    # doppler shit sux
    if 'DOPPLERTRACKFREQ' not in config:
        config['DOPPLERTRACKFREQ'] = config['restfreq']

    if 'lo2freq' not in config:
        config['lo2freq'] = [0]

    # we need the tuning freq of our receiver
    tuningFreq = config['restfreq']
    bwTotal = config['bandwidth']

    # now we can see how the band pass changes at this stage?

    # 2) set the LO1 freq to match the IF1.  That seems to be 3000; always?  No.
    freq, vfreq, _, minMaxFreqs = setFreqWithVelocity(config, paths)
    span = minMaxFreqs.maxf - minMaxFreqs.minf
    skyFreq = minMaxFreqs.avgFreqs()
    ifNom = RCVR_IF_NOMINAL[receiver]
    multiplier1 = RCVR_SIDEBAND[receiver]
    freqLocal = compute_Flocal(config)
    # print("IF1 computed from: ", multiplier1, freqLocal, skyFreq, ifNom)
    # Compute the IF frequencies!  What equation is this????
    if1 = (multiplier1 * (freqLocal - skyFreq) + ifNom)
    if0 = if1
    # for path in paths:
    #     path[0].ifFreq = config['restfreq']
    #     path[0].bw = bwTotal
    #     path[1].ifFreq = if1

    # print("IF1", if1)

    # 1) filter to set in receiver!
    if receiver in LO1_FIRST_RXS: #["Rcvr8_10"]:
        # fitler is AFTER LO1
        filterFreq = if1

    else:
        # filter are BEFORE LO1
        filterFreq = tuningFreq

    # Set the receiver filters, record the bandpass and parameters used
    filterSetting, filterLo, filterHi = setRxFilters(receiver, filterFreq, bwTotal)

    # parameters
    # print("Receiver filter: ", filterSetting, filterLo, filterHi)
    for x in ['left', 'right']:
        paramName = "%s,%sIfFilterSwitch" % (receiver, x)
        params.append((paramName, filterSetting))

    # start calculating band pass info    
    for path in paths:
        path[0].ifInfo = IFInfo()
        path[0].ifInfo.filters = [(filterSetting, filterLo, filterHi)]

    # now we can see how the band pass changes by mixing in the LO1
    # LO1 params set:
    velocity = (config["vlow"] + config["vhigh"])/2.0
    velframe = vframe[config["vframe"]]
    centerFreq = if0 # If no adjustments needed!
    # print("LO1,restFrequency", config["DOPPLERTRACKFREQ"])
    # print("LO1,velocityDefinition", config["vdef"])
    # print("LO1,sourceVelocity,position", velocity)
    # print("LO1,restFrame", velframe)
    # print("LO1,ifCenterFreq", centerFreq)
    # print("LO1 derived mixing freq", centerFreq + config["DOPPLERTRACKFREQ"])
    
    # recrod lo details for band pass info
    loMixFreq = centerFreq + config['restfreq']
    for path in paths:
        # path[0].ifInfo = IFInfo()
        path[0].ifInfo.lo = {'freq': loMixFreq}

    # calculate LO1 paramters
    params.append(("LO1,restFrequency", config["DOPPLERTRACKFREQ"]))
    params.append(("LO1,velocityDefinition", config["vdef"]))
    params.append(("LO1,sourceVelocity,position", velocity))
    params.append(("LO1,restFrame", velframe))
    params.append(("LO1,ifCenterFreq", centerFreq))
    
    # we're now ready to setup the bandpasses in the receiver
    for path in paths:
        # setup the receiver bandpasses
        # path[0].ifInfo = IFInfo()
        # initial bandpass for this receiver
        low, high = RCVR_FREQS[receiver]
        bpFeed = Bandpass(lo=low, hi=high, target=config['restfreq'])
        bpFeed.changes = 'feed'
        bps = [bpFeed]
        rxNode = path[0]

        # TBF: check the receiver type for filter-lo1 order
        if receiver in LO1_FIRST_RXS: #["Rcvr8_10"]:
            bps.append(getLO1Bandpass(bpFeed, rxNode))
            bps.extend(getFilterBandpasses(bps[-1], rxNode))
        else:
            bps.extend(getFilterBandpasses(bpFeed, rxNode))
            bps.append(getLO1Bandpass(bps[-1], rxNode))

        rxNode.setBandpasses(bps)

    # What about the IF2, LO2 settings?
    # Does not matter for DCR.
    if3s = copy(IF3[config["backend"]])
    # print("IFs:", if0, if1, if3s)    

    # Calculate the filters in the IF Rack
    # lo1aFreq = (self.flocal + self.if1) / 2.0
    # RCVR_IF_NOMINAL[receiver]  
    centerFreq = RCVR_IF_NOMINAL[receiver]
    low = centerFreq - (bwTotal*.5)
    high = centerFreq + (bwTotal*.5)
    # we will record the bandpass info in this function
    ifRackFilters = setIFFilters(low, high, paths)
    # print("ifRackFilters: ", ifRackFilters)
    for f in ifRackFilters:
        params.append(f)

    # now that we're done, print the bandpasses to make sure
    # that we got it right
    traceFreqs(paths)

    return params

def configureDCR(config, pathsFile=None, debug=False):
    paths = getDCRPaths(config, pathsFile=pathsFile, debug=debug)
    params = calcFreqs(config, paths)
    return paths, params

def test1():
    "Mimics Configure('Continuum with Rcvr1_2')"

    # configure from DB
    config = {
        'receiver'  : 'Rcvr1_2',
        'beam' : 'B1',
        'obstype'   : 'Continuum',
        'backend'   : 'DCR',
        'nwin'      : 1,
        'restfreq'  : 1400,
        'deltafreq' : 0,
        'bandwidth' : 80,
        'swmode'    : "tp",
        'swtype'    : "none",
        'swper'     : 0.1,
        # 'swfreq'    : 0,0,
        'tint'      : 0.1,
        'vlow'      : 0.0,
        'vhigh'     : 0.0,
        'vframe'    : "topo",
        'vdef'      : "Radio",
        'noisecal'  :  "lo",
        'pol'       : "Linear"
    }

    rx = config["receiver"]
    fn = "zdb.201118.pkl.%s.txt" % rx  

    paths, params = configureDCR(config, pathsFile=fn)

    # convert list of IFPathNode lists to list of list of strings
    pathNames = []
    for path in paths:
        pathNames.append([p.name for p in path])

    expPaths = [
        ['Rcvr1_2:XL', 'R1_2XL:0', 'R1_2XL:1', 'IFRouter:J2', 'SWITCH1', 'IFXS9:thru', 'IFRouter:J65', 'OpticalDriver1:J1', 'OpticalDriver1:J4', 'DCR:A_1'],
        ['Rcvr1_2:YR', 'R1_2YR:0', 'R1_2YR:1', 'IFRouter:J18', 'SWITCH3', 'IFXS10:thru', 'IFRouter:J67', 'OpticalDriver3:J1', 'OpticalDriver3:J4', 'DCR:A_3']
    ]
    expParams = [
        ('Rcvr1_2,leftIfFilterSwitch', '3'),
        ('Rcvr1_2,rightIfFilterSwitch', '3'),
        ('LO1,restFrequency', 1400),
        ('LO1,velocityDefinition', 'Radio'),
        ('LO1,sourceVelocity,position', 0.0),
        ('LO1,restFrame', 'Local'),
        ('LO1,ifCenterFreq', 3000.0),
        ('IFRack,filter_select,1', 'pass_2960_3040'),
        ('IFRack,filter_select,3', 'pass_2960_3040')
    ]
    assert pathNames == expPaths
    assert params == expParams

    compareParams(rx, params)

def test2():
    "Mimics Configure('Continuum with Rcvr2_3')"


    # configure from DB
    config = {
        'receiver'  : 'Rcvr2_3',
        'beam' : 'B1',
        'obstype'   : 'Continuum',
        'backend'   : 'DCR',
        'nwin'      : 1,
        'restfreq'  : 2000,
        'deltafreq' : 0,
        'bandwidth' : 80,
        'swmode'    : "tp",
        'swtype'    : "none",
        'swper'     : 0.1,
        # 'swfreq'    : 0,0,
        'tint'      : 0.1,
        'vlow'      : 0.0,
        'vhigh'     : 0.0,
        'vframe'    : "topo",
        'vdef'      : "Radio",
        'noisecal'  :  "lo",
        'pol'       : "Linear",
    }
        

    rx = config["receiver"]
    fn = "zdb.201118.pkl.%s.txt" % rx  

    paths, params = configureDCR(config, pathsFile=fn)

    # convert list of IFPathNode lists to list of list of strings
    pathNames = []
    for path in paths:
        pathNames.append([p.name for p in path])

    expPaths = [
        ['Rcvr2_3:XL', 'R2_3XL:0', 'R2_3XL:1', 'IFRouter:J5', 'SWITCH1', 'IFXS9:thru', 'IFRouter:J65', 'OpticalDriver1:J1', 'OpticalDriver1:J4', 'DCR:A_1'],
        ['Rcvr2_3:YR', 'R2_3YR:0', 'R2_3YR:1', 'IFRouter:J21', 'SWITCH3', 'IFXS10:thru', 'IFRouter:J67', 'OpticalDriver3:J1', 'OpticalDriver3:J4', 'DCR:A_3']
    ]

     # test freq. related params set
    expParams = [
        ('Rcvr2_3,leftIfFilterSwitch', '2'),
        ('Rcvr2_3,rightIfFilterSwitch', '2'),
        ('LO1,restFrequency', 2000),
        ('LO1,velocityDefinition', 'Radio'),
        ('LO1,sourceVelocity,position', 0.0),
        ('LO1,restFrame', 'Local'),
        ('LO1,ifCenterFreq', 6000.0),
        ('IFRack,filter_select,1', 'pass_5960_6040'),
        ('IFRack,filter_select,3', 'pass_5960_6040')
    ]

    assert pathNames == expPaths
    assert params == expParams

    compareParams(rx, params)

def test3():
    "Mimics Configure('Continuum with Rcvr8_10')"


    # configure from DB
    config = {
        'receiver'  : 'Rcvr8_10', # changes from other 'Continuum with *' scripts
        'beam' : 'B1',
        'obstype'   : 'Continuum',
        'backend'   : 'DCR',
        'nwin'      : 1,
        'restfreq'  : 9000, # changes
        'deltafreq' : 0,
        'bandwidth' : 80,
        'swmode'    : "tp",
        'swtype'    : "none",
        'swper'     : 0.1,
        # 'swfreq'    : 0,0,
        'tint'      : 0.1,
        'vlow'      : 0.0,
        'vhigh'     : 0.0,
        'vframe'    : "topo",
        'vdef'      : "Radio",
        'noisecal'  :  "lo",
        'pol'       : "Circular", # changes
    }
        

    rx = config["receiver"]
    fn = "zdb.201118.pkl.%s.txt" % rx  

    paths, params = configureDCR(config, pathsFile=fn, debug=False)

    # convert list of IFPathNode lists to list of list of strings
    pathNames = []
    for path in paths:
        print (path)
        pathNames.append([p.name for p in path])

    expPaths = [
        ['Rcvr8_10:L', 'R8_10XL:0', 'R8_10XL:1', 'IFRouter:J13', 'SWITCH1', 'IFXS9:cross', 'IFRouter:J65', 'OpticalDriver1:J1', 'OpticalDriver1:J4', 'DCR:A_1'],
        ['Rcvr8_10:R', 'R8_10YR:0', 'R8_10YR:1', 'IFRouter:J29', 'SWITCH3', 'IFXS10:cross', 'IFRouter:J67', 'OpticalDriver3:J1', 'OpticalDriver3:J4', 'DCR:A_3']
    ]

     # test freq. related params set
    expParams = [
        ('Rcvr8_10,leftIfFilterSwitch', 'narrowband'),
        ('Rcvr8_10,rightIfFilterSwitch', 'narrowband'),
        ('LO1,restFrequency', 9000),
        ('LO1,velocityDefinition', 'Radio'),
        ('LO1,sourceVelocity,position', 0.0),
        ('LO1,restFrame', 'Local'),
        ('LO1,ifCenterFreq', 3000.0),
        ('IFRack,filter_select,1', 'pass_2960_3040'),
        ('IFRack,filter_select,3', 'pass_2960_3040')
    ]

    assert pathNames == expPaths
    assert params == expParams

    compareParams(rx, params)

def compareParams(rx, params):

    # get the values logged by config tool
    configParams = getConfigLogValues(rx)

    # convert our tuples to dictionary
    ourParams = {}
    for mgrParam, value in params:
        idx = mgrParam.find(',')
        mgr = mgrParam[:idx]
        paramName = mgrParam[idx+1:]
        if mgr not in ourParams:
            ourParams[mgr] = {}
        ourParams[mgr][paramName] = value
        
    # make sure whatever we are setting so far, has been set
    # the same way in the config logs    
    for mgr, paramValues in ourParams.items():
        for param, value in paramValues.items():
            # print (mgr, param, value)
            # print (configParams[mgr][param])
            if param not in configParams[mgr]:
                print("We set this but config tool didn't", mgr, param)
                continue
            assert str(configParams[mgr][param]) == str(value)

def getConfigLogValues(rx):
    "Read text made from config log pickle file, return dct of values"

    fn = "configLogs/%sConfigLog.txt" % rx
    with open(fn, 'r') as f:
        ls = f.readlines()

    # convert text to dct of {mgr: {param: value}}
    values = {}
    for l in ls:
        mgr, param, value = l.split(' ')
        value = value[:-1] # remove \n
        if mgr not in values:
            values[mgr] = {}
        values[mgr][param] = value
        
    return values
                

def main():
    test1()
    test2()
    test3()

if __name__ == '__main__':
    main()