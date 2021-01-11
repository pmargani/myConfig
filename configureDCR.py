from copy import copy

# from ifpaths import *
# from paths import getIFPaths
from StaticDefs import IF3, IFfilters, BEAM_TO_FEED_DES, FILTERS, RCVR_IF_NOMINAL, RCVR_SIDEBAND, vframe
from StaticDefs import RCVR_FREQS, DEF_ON_SYSTEMS, DEF_OFF_SYSTEMS
from StaticDefs import QD_AND_ACTIVE_SURFACE_ON_RCVRS, PFRCVRS, PF2RCVRS
from Vdef import Vdef
from MinMaxFreqs import MinMaxFreqs
from IFPathNode import IFPathNode, IFInfo
from IFPaths import IFPaths
from Bandpasses import Bandpasses, Bandpass
from dbParams import getDBParamsFromConfig
from IFSystem import IFSystem

# Managers
from Receiver import Receiver
from LO1 import LO1
from IFRack import IFRack
from DCR import DCR
from ScanCoordinator import ScanCoordinator

LO1_FIRST_RXS = ['Rcvr8_10']


def getPathsFromFile(fn):
    "Read paths from python 3 text file derived form python 2 pickle file"
    with open(fn, 'r') as f:
        ls = f.readlines()
    return [eval(l) for l in ls]

def getIFPaths(receiver, filepath=None):
    "Returns an IFPaths from the pickled cabling file for given receiver"

    if filepath is None:
        fn = "zdb.pkl.%s.txt" % receiver
    else:
        fn = filepath

    # lists of lists of strings!
    strPaths = getPathsFromFile(fn)

    ifPathNodesList = []
    # ifPath = None

    # now turns these into related ojects
    for strPath in strPaths:

        ifPathNodes = []
        for strNode in strPath:
            ipn = IFPathNode(strNode)
            ifPathNodes.append(ipn)

        # ifPath = IFPath(ifPathNodes)
        ifPathNodesList.append(ifPathNodes)

    ifPaths = IFPaths(ifPathNodesList)

        #print(path)
        
        # ifPath = []
        # for p in path:
        #     pn = IFPathNode(p)
        #     ifPath.append(pn)

        # ifPaths.append(ifPath)
        
    return ifPaths


def getArbitraryFirstPath(ifPaths, rx, backend, beam, debug=False, firstBackendNode=None):
    "Choose the first path you come across that gets you from the first rx feed to the backend"

    # short hand
    # g = ifPaths

   # what are the feeds for our given beam?
    feeds = BEAM_TO_FEED_DES[rx][beam]

    # get a path with the first feed to backend:
    # what are the graph nodes for our backend?  Sorting by port number
    backendNodes = ifPaths.getSortedBackendNodes(backend)
    if firstBackendNode is not None:
        backendNodes = [IFPathNode(firstBackendNode)]
        if debug:
            print("Constrained to use backend node: ", firstBackendNode)
    backendNames = [b.name for b in backendNodes]

    if debug:
        print("Backend nodes: ", backendNodes)

    # start arbitrarly with the first feed
    feed1 = feeds[0]

    # and get the nodes that use this port
    #starts = getPortNodes(g, feed1)
    starts = ifPaths.getFrontendFeeds(feed1)
    firstFeed1Node = starts[0]

    if debug:
        print("feed1 nodes:", feed1, starts)

    if debug:
        ifPaths.printSummary()
        # print("paths summary")
        # for path in paths:
            # print(path.path[0], path.path[-1])

    # now simply find all the paths from the first of our feeds, to an arbitrary backend node       
    # firstBackendNode = backendNodes[0]
    feed1path = None
    for backendNode in backendNodes:
        feed1paths = ifPaths.getMatchingPaths(firstFeed1Node, backendNode)
        # feed1paths = list(nx.all_simple_paths(g, source=firstFeed1Node, target=backendNode))
        if debug:
            print("found # paths between %s and %s: %d" % (firstFeed1Node, backendNode, len(feed1paths)))
            print(feed1paths) 
            print("Constained to use backend node: ", firstBackendNode)
        if len(feed1paths) > 0:    
            # arbitrarily pick the first path
            feed1path = feed1paths[0]
            break  

    return feed1path

def getDCRPaths(config, pathsFile=None, debug=False, firstBackendNode=None):
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

    if debug:
        print ("Path summary:")
        for path in paths.paths:
            print(path.path[0], path.path[-1])

    # prune the paths of non-DCR backends
    # paths = [p for p in paths if 'DCR' in p[-1].name]
    paths.prunePathsForBackend(backend)

    if debug:
        print ("Path summary:")
        for path in paths.paths:
            print(path.path[0], path.path[-1])

    feed1path = getArbitraryFirstPath(
        paths,
        rx,
        backend,
        beam,
        debug=debug,
        firstBackendNode=firstBackendNode
    )

    feeds = BEAM_TO_FEED_DES[rx][beam]

    ifxs1s = feed1path.getUniqueDeviceNode(IFXS)

    ifxsSetting1 = None if ifxs1s is None else ifxs1s.port

    # Find the next feed, with criteria:
    #   * different polarization, or feed
    #   * different backend node
    #   * if IFXS node is used, make sure port (setting) is the same

    # now get the other feed
    feed2 = feeds[1]

    # and get the nodes that use this port
    starts = paths.getFrontendFeeds(feed2)
    firstFeed2Node = starts[0]
    
     # get all paths between this feed and other backend nodes: remove first backend node
    backendNodes = paths.getSortedBackendNodes(backend)
    firstBackendNode = feed1path.getBackendNode()
    unusedBackendNodes = [b for b in backendNodes if b != firstBackendNode]
         
    # go through all possiblilities till you find a match
    feed2path = None
    for backendNode in unusedBackendNodes:
        feed2paths = paths.getMatchingPaths(firstFeed2Node, backendNode)

        # feed2paths = list(nx.all_simple_paths(g, source=firstFeed2Node, target=backendNode))
        if debug:
            print("found # paths between %s and %s: %d" % (firstFeed2Node, backendNode, len(feed2paths)))
            for p in feed2paths:
                print(p.getSummary()) 
        
        # go through these paths, and check for IFXS setting
        for ifPath in feed2paths:
            ifxs2s = [p for p in ifPath.path if IFXS in p.name]
            if len(ifxs2s) == 0:
                ifxsSetting2 = None
            else:
                ifxsSetting2 = ifxs2s[0].port
            if ifxsSetting2 == ifxsSetting1:
                feed2path = ifPath
                break

        # are we done yet?
        if feed2path is not None:
            break

    # return feed1path, feed2path  
    return IFPaths([feed1path, feed2path])

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

    filter_setting = freqLow = freqHigh = None

    if receiver in FILTERS:
        param_names, filters, rcvr_type = FILTERS[receiver]
        bw_low = tuning_freq - (0.5 * bw_total)
        bw_high = tuning_freq + (0.5 * bw_total)
        # if rcvr_type == 0:  # Mixer before filter. Convert filter freq
        #     bw_low = self.if_freq_low
        #     bw_high = self.if_freq_high
        filter_setting = filter_bandwidth = None
        # Choose the first one that encompasses our bw_low and bw_high!
        for freqLow, freqHigh, freqSetting in filters:
            if bw_low >= freqLow and bw_high <= freqHigh:
                filter_setting = freqSetting
                filter_bandwidth = freqHigh - freqLow
                found = 1
                break

    return filter_setting, freqLow, freqHigh  

def setIFFilters(total_bw_low, total_bw_high, ifpath):
    "Returns IFRack parameters and updates paths bandpass info"
    # print("setIFFilters", total_bw_low, total_bw_high)

    params = []
    for path in ifpath:
        filter_value = "pass_all"
        param = None

        for fv, fLow, fHigh in IFfilters:
            # fLow = f[1]
            # fHigh = f[2]
            # if f[1] <= total_bw_low and f[2] >= total_bw_high:
                # filter_value = f[0]
            if fLow <= total_bw_low and fHigh >= total_bw_high:
                filter_value = fv
                # print("print found good filter at", filter_value, fLow, fHigh)
                break

        opticalDriver = path.getFirstLikeDeviceNode("OpticalDriver")        
        # if "opticalDriver" in path:
        if opticalDriver is not None:
            # update the IFRack parameters
            filterNum = opticalDriver.deviceId # path["opticalDriver"]
            param = "IFRack,filter_select,{}".format(filterNum)
            params.append((param, filter_value))
            if filter_value != "pass_all":
                # set this nodes ifInfo filter info
                opticalDriver.ifInfo = IFInfo()
                opticalDriver.ifInfo.filters = []
                opticalDriver.ifInfo.filters.append((param, filter_value))
                # then use filter range to update the bandpass at this node
                bp = path.getBandpassUpToNode(opticalDriver)
                bpFilter = copy(bp)
                bpFilter.filter(fLow, fHigh)
                bpFilter.changes = "%s, (%f, %f)" % (param, fLow, fHigh)
                opticalDriver.setBandpasses([bpFilter])
                # self.seq.add_param(self.mng, fs, self.filter_value)
    return params 

def getFilterBandpasses(bp1, rxNode):
    "Return bandpasses representing filters in receiver"
    bps = []
    bp = copy(bp1)
    for fName, fLow, fHigh in rxNode.ifInfo.filters:
        bp = copy(bp)
        bp.filter(fLow, fHigh)
        bp.changes = "Filter %s (%f, %f)" % (fName, fLow, fHigh)
        bps.append(bp)
    return bps

def getLO1Bandpass(bp1, rxNode, lowerSideband=None):
    "Return bandpass representing receivers LO1 mixing"
    if lowerSideband is None:
        s = RCVR_SIDEBAND[rxNode.device]
        lowerSideband = s == -1

    bpLO1 = copy(bp1)
    loMixFreq = rxNode.ifInfo.lo['freq']
    bpLO1.mix(loMixFreq, lowerSideband=lowerSideband)
    sideband = "lower" if lowerSideband else "upper"
    bpLO1.changes = "LO %s sideband at %f" % (sideband, loMixFreq)
    return bpLO1

def calcFreqs(config, ifPaths, debug=False):
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
        config['DOPPLERTRACKFREQ'] = int(config['restfreq'])

    if 'lo2freq' not in config:
        config['lo2freq'] = [0]

    # we need the tuning freq of our receiver
    tuningFreq = config['restfreq']
    bwTotal = config['bandwidth']

    # now we can see how the band pass changes at this stage?

    # 2) set the LO1 freq to match the IF1.  That seems to be 3000; always?  No.
    freq, vfreq, _, minMaxFreqs = setFreqWithVelocity(config, ifPaths.paths)
    span = minMaxFreqs.maxf - minMaxFreqs.minf
    skyFreq = minMaxFreqs.avgFreqs()
    ifNom = RCVR_IF_NOMINAL[receiver]
    multiplier1 = RCVR_SIDEBAND[receiver]
    freqLocal = compute_Flocal(config)
    if debug:
        print("IF1 computed from: ", multiplier1, freqLocal, skyFreq, ifNom)
    # Compute the IF frequencies!  What equation is this????
    if1 = (multiplier1 * (freqLocal - skyFreq) + ifNom)
    if receiver == "Rcvr26_40": # W-band too!
        # mmconverter!
        if_offset = 44000.
        if0 = if_offset - freqLocal
    else:    
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
    # print("*** Receiver filter: ", filterSetting, filterLo, filterHi)
    # if filterSetting is not None:
        # for x in ['left', 'right']:
            # paramName = "%s,%sIfFilterSwitch" % (receiver, x)
            # print(paramName, filterSetting)
    #         params.append((paramName, filterSetting))

    # start calculating band pass info    
    for path in ifPaths.paths:
        frontendNode = path.path[0]
        frontendNode.ifInfo = IFInfo()
        if filterSetting is not None:
            frontendNode.ifInfo.filters = [(filterSetting, filterLo, filterHi)]
        else:    
            frontendNode.ifInfo.filters = []

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
    for path in ifPaths.paths:
        # path[0].ifInfo = IFInfo()
        frontendNode = path.path[0]
        frontendNode.ifInfo.lo = {'freq': loMixFreq}

    # calculate LO1 paramters
    # params.append(("LO1,restFrequency", int(config["DOPPLERTRACKFREQ"])))
    # params.append(("LO1,velocityDefinition", config["vdef"]))
    params.append(("LO1,sourceVelocity,position", velocity))
    # params.append(("LO1,restFrame", velframe))
    # params.append(("LO1,ifCenterFreq", centerFreq))
    
    # TBF: for now use config dct to pass this along
    config['center_freq'] = centerFreq

    # we're now ready to setup the bandpasses in the receiver
    for path in ifPaths.paths:
        # setup the receiver bandpasses
        # path[0].ifInfo = IFInfo()
        # initial bandpass for this receiver
        low, high = RCVR_FREQS[receiver]
        bpFeed = Bandpass(lo=low, hi=high, target=config['restfreq'])
        bpFeed.changes = 'feed'
        bps = [bpFeed]
        rxNode = path.path[0]

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
    ifRackFilters = setIFFilters(low, high, ifPaths.paths)
    # print("ifRackFilters: ", ifRackFilters)
    for f in ifRackFilters:
        params.append(f)

    # now that we're done, print the bandpasses to make sure
    # that we got it right
    if debug:
        print("paths", ifPaths)
        ifPaths.printFreqs()

    vdef = config["vdef"]
    ifSystem = IFSystem(
        ifPaths,
        receiver,
        if1,
        centerFreq,
        tuningFreq,
        bwTotal,
        velocity,
        vdef,
        vframe
    )
    # return the values added paths
    return ifSystem

    # return params

def getDCRContinuumParams(config, ifSys):
    "Set obvious manager parameters for these types of observations"

    ifPaths = ifSys.ifPaths

    # simple enough!
    motorRack = ('MotorRack,receiver', config['receiver'])

    dcr = getDCRParams(config, ifPaths)

    scSubsystem = getScanCoordinatorDCRContinuumSysParams(config)
 
    # TBF: are these correct?
    tuningFreq = ifSys.tuningFreq #config['restfreq']
    centerFreq = str(config['center_freq'])
    velocity = ifSys.velocity # 0.
    vdef = ifSys.vdef #config['vdef']

    rxMgr = Receiver(config, ifSys) #tuning_freq=tuningFreq, bw_total=ifSys.bwTotal, if_center=tuningFreq)
    rxMgr.setParams()

    # s12 = 4
    s12 = None
    lo1 = LO1(config, tuningFreq, centerFreq, velocity, vdef, s12_value=s12)

    ifRack = IFRack(config, ifSys, rxMgr)
    # TBF: why is this singled out to be called last in config tool?
    ifRack.set_laser_power()

    # TBF: what else?

    # put them together
    params = [
       motorRack,
    ]
    params.extend(dcr)
    params.extend(scSubsystem)
    params.extend(rxMgr.getParams())
    params.extend(lo1.getParams())
    params.extend(ifRack.getParams())

    return params

        
def getScanCoordinatorDCRContinuumSysParams(config):
    "Use the config info to set the managers ScanCoordinator will use"

    sc = ScanCoordinator(config)
    sc.findParameterValues()
    return sc.getParams()

def getDCRParams(config, paths):
    "Use the paths information to determine some DCR params"

    dcr = DCR(config, paths)
    dcr.findDCRParams()
    return dcr.getParams()

def addMissingKeywords(config):
    "Config tool expands all configs to more then 50 values."

    # Here we'll just add what we need as we go
    ks = [
        # needed by Receiver.setReceiverDefaults
        'polarization',
        'notchfilter',
        'polswitch',
        'beamswitch',
        'xfer',
        # LO1
        'phasecal',
        # IFRack
        'iftarget',
    ]

    # add them
    for k in ks:
        if k not in config:
            config[k] = None

def configureDCR(config, pathsFile=None, debug=False, firstBackendNode=None):
    """
    The Main Event.
    Here we are given a standard config tool dictionary.  We return
    the resultant paths (lists of IFPathNodes) and the manager params.
    """

    # Step 1: expand user's configuration

    # first let's add any necessary missing keywords
    addMissingKeywords(config)

    # let's expand the configuration with defaults
    rxMgr = Receiver(config)
    rxMgr.setReceiverDefaultsForConfig(config)

    # Step 2: find IF paths 

    # now find how we're getting from our rx to the DCR
    paths = getDCRPaths(config, pathsFile=pathsFile, debug=debug, firstBackendNode=firstBackendNode)

    # Step 3: define bandpasses

    # now add frequency info to these paths, and return some
    # related manager parameters
    ifSys = calcFreqs(config, paths, debug=debug)

    # Last Step: translate everything into manager parameters
    params = []

    # get more parameters: First ones from the DB
    params.extend(getDBParamsFromConfig(config, dct=False, tuples=True))

    # then some really simple ones from what we've done so far    
    params.extend(getDCRContinuumParams(config, ifSys))        

    return ifSys, params

    
def testKFPA():
    "Mimics Configure('Continuum with RcvrArray18_26')"


    # configure from DB
    config = {
        'receiver'  : 'RcvrArray18_26', # changes from other 'Continuum with *' scripts
        'beam' : '4,6', 
        'obstype'   : 'Continuum',
        'backend'   : 'DCR', # 'DCR_AF' used by config tool to enforce Analog Filter rack routing
        'nwin'      : 1,
        'restfreq'  : 2500, # changes
        'deltafreq' : 0,
        'bandwidth' : 800, # changed from 80!
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
    # from unit test, but no difference 
    # fn = "test_pkl.RcvrPF_1.txt"

    paths, params = configureDCR(config, pathsFile=fn, debug=True)

    # convert list of IFPathNode lists to list of list of strings
    pathNames = []
    for path in paths:
        print (path)
        pathNames.append([p.name for p in path])

    # from unit test
    expPaths = [
        ['RcvrArray18_26:R4', 'IFRouter:J24', 'SWITCH3', 'IFXS10:thru', 'IFRouter:J67', 'OpticalDriver3:J1', 'OpticalDriver3:J2', 'OpticalReceiver3:J1', 'OpticalReceiver3:D', 'ConverterModule8:J1', 'ConverterModule8:J3', 'SamplerFilter8:J1', 'SamplerFilter8:J6', 'DCR:A_16'], #, [{'tint': 0.1, 'beam': '4', 'nchan': 'low', 'deltafreq': 0, 'bandwidth': 800, 'vpol': None, 'subband': None, 'restfreq': 2500}]],
        ['RcvrArray18_26:L4', 'IFRouter:J7', 'SWITCH1', 'IFXS9:thru', 'IFRouter:J65', 'OpticalDriver1:J1', 'OpticalDriver1:J2', 'OpticalReceiver1:J1', 'OpticalReceiver1:D', 'ConverterModule4:J1', 'ConverterModule4:J3', 'SamplerFilter4:J1', 'SamplerFilter4:J6', 'DCR:A_12'], #, [{'tint': 0.1, 'beam': '4', 'nchan': 'low', 'deltafreq': 0, 'bandwidth': 800, 'vpol': None, 'subband': None, 'restfreq': 2500}]],
        ['RcvrArray18_26:L6', 'IFRouter:J15', 'SWITCH2', 'IFXS9:thru', 'IFRouter:J66', 'OpticalDriver2:J1', 'OpticalDriver2:J2', 'OpticalReceiver2:J1', 'OpticalReceiver2:A', 'ConverterModule1:J2', 'ConverterModule1:J3', 'SamplerFilter1:J1', 'SamplerFilter1:J6', 'DCR:A_9'], #, [{'tint': 0.1, 'beam': '6', 'nchan': 'low', 'deltafreq': 0, 'bandwidth': 800, 'vpol': None, 'subband': None, 'restfreq': 2500}]],
        ['RcvrArray18_26:R6', 'IFRouter:J31', 'SWITCH4', 'IFXS10:thru', 'IFRouter:J68', 'OpticalDriver4:J1', 'OpticalDriver4:J2', 'OpticalReceiver4:J1', 'OpticalReceiver4:A', 'ConverterModule5:J2', 'ConverterModule5:J3', 'SamplerFilter5:J1', 'SamplerFilter5:J6', 'DCR:A_13'] #, [{'tint': 0.1, 'beam': '6', 'nchan': 'low', 'deltafreq': 0, 'bandwidth': 800, 'vpol': None, 'subband': None, 'restfreq': 2500}]]
    ]

    # from productions etc/log/config/config_status:
    # RcvrArray18_26:R4->IFRouter:J24->SWITCH3->IFXS10:thru->IFRouter:J67->OpticalDriver3:J1->OpticalDriver3:J2->OpticalReceiver3:J1->OpticalReceiver3:D->ConverterModule8:J1->ConverterModule8:J3->SamplerFilter8:J1->SamplerFilter8:J6->DCR:A_16
    # RcvrArray18_26:L4->IFRouter:J7->SWITCH1->IFXS9:thru->IFRouter:J65->OpticalDriver1:J1->OpticalDriver1:J2->OpticalReceiver1:J1->OpticalReceiver1:D->ConverterModule4:J1->ConverterModule4:J3->SamplerFilter4:J1->SamplerFilter4:J6->DCR:A_12
    # RcvrArray18_26:L6->IFRouter:J15->SWITCH2->IFXS9:thru->IFRouter:J66->OpticalDriver2:J1->OpticalDriver2:J2->OpticalReceiver2:J1->OpticalReceiver2:A->ConverterModule1:J2->ConverterModule1:J3->SamplerFilter1:J1->SamplerFilter1:J6->DCR:A_9
    # RcvrArray18_26:R6->IFRouter:J31->SWITCH4->IFXS10:thru->IFRouter:J68->OpticalDriver4:J1->OpticalDriver4:J2->OpticalReceiver4:J1->OpticalReceiver4:A->ConverterModule5:J2->ConverterModule5:J3->SamplerFilter5:J1->SamplerFilter5:J6->DCR:A_13     
        
    assert pathNames == expPaths

    # checkBandpasses(paths, 2, 340., 1080.)

    # compare to production mgr param values
    # compareParams(rx, params)

def test9():

    # Argus

    # from production config_status:
    # RcvrArray75_115:J10->IFRouter:J12->SWITCH2->IFXS9:thru->IFRouter:J66->OpticalDriver2:J1->OpticalDriver2:J4->DCR:A_2
    # RcvrArray75_115:J11->IFRouter:J20->SWITCH3->IFXS10:thru->IFRouter:J67->OpticalDriver3:J1->OpticalDriver3:J4->DCR:A_3

    pass
               

def main():
    testKFPA()

if __name__ == '__main__':
    main()
