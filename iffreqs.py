from copy import copy, deepcopy
import math

import numpy as np

from ifpaths import getGraph, chooseVegasPaths, getFrontend, PathNode, chooseDcrPaths
from StaticDefs import *
from Vdef import Vdef

RAWPATHS = 'rawpaths'

class MinMaxFreqs:

    def __init__(self, minf=None, maxf=None, bw=None):
        self.minf = minf
        self.maxf = maxf
        self.bw = bw # max bw

    def setMinMax(self, f):
        self.setMin(f)
        self.setMax(f)

    def setMin(self, f):
        if self.minf is not None:
            if self.minf > f:
                self.minf = f
        else:
            self.minf = f  

    def setMax(self, f):
        if self.maxf is not None:
            if self.maxf < f:
                self.maxf = f
        else:
            self.maxf = f

    def setBW(self, bw):
        if self.bw is not None:
            if self.bw < bw:
                self.bw = bw
        else:
            self.bw = bw

    def avgFreqs(self):
        if self.minf is None or self.maxf is None:
            return None
        return (self.minf + self.maxf) / 2.0
            
    def computeBW(self, bw=None):
        bw = sef.bw if bw is None else bw
        return (self.maxf - self.minf + bw)

    def __str__(self):
        return "%s - %s (%s)" % (self.minf, self.maxf, self.bw)    

def appearsLikeInList(ls, name):
    return [l for l in ls if name in l]

def isLikeInList(ls, name):
    pass

def savePaths(g, paths, wins):
    "mimics IFPath.savePaths"

    rx = getFrontend(g)
    for p in paths:
        assert rx in p[0]

    ifs = []
    for path in paths:
        ifpathInfo = {} #copy(wins)

        # frontend info
        n = PathNode(path[0])
        ifpathInfo["beam"] = n.port
        ifpathInfo["beam_num"] = n.getPortNumber()

        # backend info
        n = PathNode(path[-1])
        ifpathInfo["backend"] = n.device
        ifpathInfo["backendPort"] = n.port

        # add other stuff to our ifpathInfo
        saveInfo(path, "ConverterModule", ifpathInfo, deviceIdKey='cm')
        saveInfo(path, "IFXS", ifpathInfo, portKey='xswSetting', deviceIdKey='xsw')
        saveInfo(path, "OpticalDriver", ifpathInfo, deviceIdKey='opticalDriver')
        saveInfo(path, "SWITCH", ifpathInfo, deviceIdKey='IFRackSw')

        ifpathInfo[RAWPATHS] = deepcopy(wins)

        # TBF: if 'rawpaths' not in this path, 
        # do something for DCR: ifpathInfo["restfreq"] = config["DOPPLERTRACKFREQ"] 
        # if VEGAS, it should have 'rawpaths'?

        print(ifpathInfo)        
        ifs.append(ifpathInfo)

    return ifs

def saveInfo(path, device, dct, portKey=False, deviceIdKey=False):

    ds = appearsLikeInList(path, device)
    if len(ds) > 0:
        n = PathNode(ds[0])
        if portKey is not None:
            dct[portKey] = n.port
        if deviceIdKey is not None:
            _, dId = n.device.split(device)
            dct[deviceIdKey] = dId 
        return n
    else:    
        return None            

def setRxFilters(receiver, tuning_freq, bw_total):
    """Set receiver filters:
        use the first filter in the list for this receiver that
        encompasses the bandwidth defined by the given
        tuning frequency and bandwidth.
    """
    print("setRxFilters: ", receiver, tuning_freq, bw_total)
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
        print ("bw:", bw_low, bw_high)
        filter_setting = filter_bandwidth = None
        # Choose the first one that encompasses our bw_low and bw_high!
        for freq in filters:
            print("filter freqs: ", freq[0], freq[1])
            if bw_low >= freq[0] and bw_high <= freq[1]:
                filter_setting = freq[2]
                filter_bandwidth = freq[1] - freq[0]
                found = 1
                break

    return filter_setting, freq[0], freq[1]
                
def computeBW(paths):

    # global min max freqs
    minMaxFreqs = MinMaxFreqs()
    minMaxBeamPathFreqs = MinMaxFreqs()

    ifRackFreqs = {}
    beamIFRackFreqs = {}
    IFRackSw = "IFRackSw"

    bandwidths = []
    band = {}

    for path in paths:
        beamNum = path["beam_num"]
        # min/max freqs for just this path
        minMaxFreqsPath = MinMaxFreqs()
        # initialize IF Rack stuff?
        if IFRackSw in path:
            ifRackSwitch = path[IFRackSw]
            if ifRackSwitch not in ifRackFreqs:
                ifRackFreqs[ifRackSwitch] = MinMaxFreqs()
        if RAWPATHS in path and path['backend'] != 'DCR':
            rawpaths = path[RAWPATHS]
            if isinstance(rawpaths, list):
                beam = path[RAWPATHS][0]["beam"]
                bw = rawpaths[0]['bandwidth']
                bandwidths.append(bw)
                # TBF: IFRackSw?
                for p in rawpaths:
                    vel_freq = p["vel_freq"]
                    minMaxFreqs.setMinMax(vel_freq)
                    minMaxFreqsPath.setMinMax(vel_freq)
                    minMaxFreqsPath.setBW(bw)
                    # TBF: IFRackSw
                    if IFRackSw in path:
                        ifRackFreqs[ifRackSwitch].setMinMax(minMaxFreqsPath.minf)
                        ifRackFreqs[ifRackSwitch].setMinMax(minMaxFreqsPath.maxf)
                        ifRackFreqs[ifRackSwitch].setBW(minMaxFreqsPath.bw)
                    # max of all freq and bw using for a given beam is used
                    # for ifrack filters
                    minMaxBeamPathFreqs.setMinMax(vel_freq)
                    minMaxBeamPathFreqs.setBW(bw)

                    # ifRackSwitch[]
                    # TBF: Beam and IFRackSW
                    if beamNum not in beamIFRackFreqs:
                        beamIFRackFreqs[beamNum] = MinMaxFreqs()
                    beamIFRackFreqs[beamNum].setMinMax(minMaxBeamPathFreqs.minf)    
                    beamIFRackFreqs[beamNum].setMinMax(minMaxBeamPathFreqs.maxf)
                    beamIFRackFreqs[beamNum].setBW(minMaxBeamPathFreqs.bw) 

                    # update path dict
                    path["max_freq"] = minMaxFreqsPath.maxf   
                    path["min_freq"] = minMaxFreqsPath.minf   
                        
                    if beam not in band:
                        band[beam] = []
                    band[beam].append(bw)
                    
                path["ifrack_bw_old"] = minMaxFreqsPath.computeBW(bw=bandwidths[-1]) 
                #minMaxFreqsPath.maxf - minMaxFreqsPath.minf + bandwidths[-1]
                path["ifrack_bw"] = minMaxBeamPathFreqs.computeBW(bw=max(band[beam])) 
                #minMaxBeamPathFreqs.maxf - minMaxBeamPathFreqs.minf + max(band[beam])

            elif isinstance(rawpaths, dict):
                pass

    print( "min max freqs: ", minMaxFreqs)
    print( "min max freqs paths: ", minMaxFreqsPath)
    print( "min max freqs IF Rack: ", ifRackFreqs)
    print( "min max freqs Beam: ", beamIFRackFreqs)

        # for path in self.pathInfo:
        #     if "rawpaths" in path and isinstance(path["rawpaths"], list):
        #         beam = path["rawpaths"][0]["beam"]
        #         if beam in BeamIFRackfreqs and "ifrack_bw" in path:
        #             path["ifrack_bw"] = (BeamIFRackfreqs[beam][0] -
        #                                  BeamIFRackfreqs[beam][1] +
        #                                  BeamIFRackfreqs[beam][2])
        #             path["ifrackModFreq"] = BeamIFRackfreqs[beam]

    receiverBW = None
    if bandwidths != []:
        receiverBW = minMaxFreqsPath.computeBW(bw=max(bandwidths))
        paths[0]["receiver_bw"] = receiverBW
    return receiverBW


def setFreqWithVelocity(config, paths):
    be = config['backend']
    return setFreqWithVelocityDCR(config, paths) if be == 'DCR' else setFreqWithVelocityVegas(config, paths)

def setFreqWithVelocityDCR(config, paths):

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
        
def setFreqWithVelocityVegas(config, paths):
    print("config", config)
    vlow = config['vlow']
    vhigh = config['vhigh']
    vdef = config['vdef']
    
    vd = Vdef()

    freqs = []
    dfreqs = []
    freqAvgVels = []

    minMaxFreqs = MinMaxFreqs()

    for path in paths:
        if RAWPATHS in path:
            setRestFreq(path)
            restfreq = path['restfreq']
            print("restfreq: ", restfreq)
            dfreq = path[RAWPATHS][0]["deltafreq"]
            vd.compute_local_frame_with_vdef(vdef, vhigh, restfreq, vlow)
            minMaxFreqs.setMin(vd.cur_vlow)
            minMaxFreqs.setMax(vd.cur_vhigh)
            vel_freq = vd.get_vave() + dfreq
            path["vel_freq"] = vel_freq 
            path["freq"] = path["aveFreq"]
            freqAvgVels.append(vel_freq)
            freqs.append(vel_freq)
            dfreqs.append(dfreq)

    # TBF: set_all_path_freqs?

    return freqs, dfreqs, freqAvgVels, minMaxFreqs

def setRestFreq(path):
    mmf = MinMaxFreqs()
    mm = MinMaxFreqs()

    if RAWPATHS in path:
        if isinstance(path[RAWPATHS], list):

            for d in path[RAWPATHS]:
                mmf.setMinMax(d["restfreq"])
                mm.setMinMax(d["vel_freq"])
                path["restfreq"] = mmf.avgFreqs()
                path["aveFreq"] = mm.avgFreqs()

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

def computeLO2(freqToOffset, if0, if1, config, paths):
    receiver = config['receiver']
    be = config['backend']
    multiplier1 = RCVR_SIDEBAND[receiver]
    lo2freq = config['lo2freq']
    lo3freq = 10500


    multiplier2 = 1
    tmpMult = multiplier1 * multiplier2
    ifComputeDiff = 0

    lo2HighCutoff = 17900.0
    lo2LowCutoff = 10501.0
    lo2s = []
    lo2_low_adjust = 0
    lo2_high_adjust = 0
    doppler_lo2 = None
    int_doppler_lo2 = None

    freq_w_avg_vel_Doppler = None

    if lo2freq[0] == 0:
        for i, path in enumerate(paths):
            print ("")
            print (i, path, path[RAWPATHS][0])
            if "vel_freq" in path and "cm" in path:

                centerIf3 = path[RAWPATHS][0]["if3"]
                velFreq = float(path["vel_freq"])
                print("if1Eff from", tmpMult, velFreq, freqToOffset, if1, ifComputeDiff)
                if1Eff = tmpMult * (velFreq - freqToOffset) + if1 + ifComputeDiff
                lo2 = (if1Eff + lo3freq - centerIf3)
                print("new lo2 from", if1Eff, centerIf3)
                print("new lo2", lo2)
                path['lo2'] = lo2
                rawpath0 = path[RAWPATHS][0]
                for j, raw in enumerate(path[RAWPATHS]):
                    if isinstance(raw, dict):
                        if ("mode" in rawpath0 and rawpath0["mode"] > 19):
                            print ("mode > 19")
                            if3 = (tmpMult * (float(raw['vel_freq']) - freqToOffset)) + if1 + ifComputeDiff + lo3freq - lo2
                        else:    
                            if3 = rawpath0['if3']
                            path["if3"] = if3
                        raw["if3"] = if3
                        print ("Now if3 in this rawpath", j, if3)    
                if velFreq == freq_w_avg_vel_Doppler:
                    doppler_lo2 = lo2
                    int_doppler_lo2 = int(lo2 * 1000.0 + 0.49)
                    int_doppler_lo2 = int_doppler_lo2 * 0.001
                int_lo2 = int(lo2 * 1000.0 + 0.49)  
                round_lo2 = int_lo2 * 0.001
                path["lo2"] = round_lo2
                if round_lo2 > lo2HighCutoff:
                    print (" lo2 too high needs lo2 adjustment")
                    print ("self.round_lo2 ", round_lo2)
                    # lo2_high_adjust = max(
                        # lo2_high_adjust, self.round_lo2 - lo2HighCutoff)
                    # print "lo2_high_adjust ", lo2_high_adjust
                elif round_lo2 < lo2LowCutoff:
                    print (" lo2 too low needs lo2 adjustment")
                    lo2_low_adjust = min(
                        lo2_low_adjust, round_lo2 - lo2LowCutoff)

    if doppler_lo2 is not None and int_doppler_lo2 is not None:
        epsfreq = doppler_lo2 - int_doppler_lo2
        new_if1 = if1 - epsfreq
        new_if0 = if0 - epsfreq
    else:
        if receiver != "Holography" and be != "VEGAS":
            print("Warning: The doppler tracking frequency was not one of"
                  " the specified rest frequencies. The telescope is "
                  "being configured as specified but if this was not "
                  "intentional, please fix and re-submit")
        epsfreq = 0
        new_if1 = if1 - epsfreq
        new_if0 = if0 - epsfreq
    print("new_if0, if1:", new_if0, new_if1)

    if lo2_high_adjust != 0 and lo2_low_adjust != 0:
        print( "Frequency spread is too great -- setup will be incorrect!")
    if lo2_high_adjust != 0 or lo2_low_adjust != 0:
        print("Warning: LO2 out of range, adjusting LO2 and IF1 by {}"
              "".format(lo2_high_adjust + lo2_low_adjust))
        new_if1 -= multiplier2 * (lo2_high_adjust + lo2_low_adjust)
        new_if0 -= multiplier2 * (lo2_high_adjust + lo2_low_adjust)
        for path in paths:
            if "lo2" in path:
                adjusted = (lo2_high_adjust + lo2_low_adjust)
                lo2 -= adjusted
                print("adjusted lo2", lo2)
                path["lo2"] = lo2

    lo1_est = freqToOffset - multiplier1 * new_if0
    print("lo1 estimated:", lo1_est)
    center_freq = new_if0

    lo1synth = lo1_est * 1e6

    print("lo1synth", lo1synth)
    # lofreq = ((self.lo_restfreq +
    #                     self.sidebandmult * self.center_freq) /
    #                    self.lo_multiplier)

    # TBF!  more stuff, but what do we need???

def set_if_filters_oldstyle(total_bw_low, total_bw_high, ifpath):

    params = []
    for path in ifpath:
        filter_value = "pass_all"
        param = None

        if True:
            for f in IFfilters:
                if f[1] <= total_bw_low and f[2] >= total_bw_high:
                    filter_value = f[0]
                    break
        if "opticalDriver" in path:
            filterNum = path["opticalDriver"]
            param = "IFRack,filter_select,{}".format(filterNum)

                # self.seq.add_param(self.mng, fs, self.filter_value)
        params.append((param, filter_value))
    return params  

def set_if_filters(iffilter_center, ifpath):
    """Set IF filters"""
    # TBF interim solution, is IFrack bw part of path list or not?
    # Some backends yes, some backends no.
    params = []
    for path in ifpath:
        filter_value = "pass_all"
        param = None
        if "ifrack_bw" in path:
            total_bw_low = iffilter_center - (0.5 * path["ifrack_bw"])
            total_bw_high = iffilter_center + (0.5 * path["ifrack_bw"])
            total_bw_low = math.ceil(total_bw_low)
            total_bw_high = math.floor(total_bw_high)
            # if 0 == isinstance(rcvr, RcvrPF_1):
            if True:
                for f in IFfilters:
                    if f[1] <= total_bw_low and f[2] >= total_bw_high:
                        filter_value = f[0]
                        break
            if "opticalDriver" in path:
                filterNum = path["opticalDriver"]
                param = "IFRack,filter_select,{}".format(filterNum)

                # self.seq.add_param(self.mng, fs, self.filter_value)
        params.append((param, filter_value))
    return params    

def calcFreqs(config, ifPath):

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
    # only one tuning freq, so just look at the first path?
    ifp = ifPath[0]
    paths = ifp['rawpaths']
    if len(paths) > 0:
        restfreqs = [p['restfreq'] for p in paths]

        tuningFreq = np.mean(restfreqs)    
    else:
        tuningFreq = config['restfreq']

    print("tuning freq", tuningFreq)

    if backend != 'DCR':
        bwTotal = computeBW(ifPath)
    else:
        bwTotal = config['bandwidth']

    print("BW: ", bwTotal)



    # now we can see how the band pass changes at this stage?

    # 2) set the LO1 freq to match the IF1.  That seems to be 3000; always?  No.
    freq, vfreq, _, minMaxFreqs = setFreqWithVelocity(config, ifPath)
    span = minMaxFreqs.maxf - minMaxFreqs.minf
    skyFreq = minMaxFreqs.avgFreqs()
    ifNom = RCVR_IF_NOMINAL[receiver]
    multiplier1 = RCVR_SIDEBAND[receiver]
    freqLocal = compute_Flocal(config)
    print("IF1 computed from: ", multiplier1, freqLocal, skyFreq, ifNom)
    # Compute the IF frequencies!  What equation is this????
    if1 = (multiplier1 * (freqLocal - skyFreq) + ifNom)
    if0 = if1
    print("IF1", if1)

    # 1) filter to set in receiver!
    if receiver in ["Rcvr8_10"]:
        # fitler is AFTER LO1
        filterFreq = if1

    else:
        # filter are BEFORE LO1
        filterFreq = tuningFreq

    filterSetting, filterLo, filterHi = setRxFilters(receiver, filterFreq, bwTotal)

    print("Receiver filter: ", filterSetting, filterLo, filterHi)
    for x in ['left', 'right']:
        paramName = "%s,%sIfFilterSwitch" % (receiver, x)
        params.append((paramName, filterSetting))

    # now we can see how the band pass changes by mixing in the LO1
    # LO1 params set:
    velocity = (config["vlow"] + config["vhigh"])/2.0
    velframe = vframe[config["vframe"]]
    centerFreq = if0 # If no adjustments needed!
    print("LO1,restFrequency", config["DOPPLERTRACKFREQ"])
    print("LO1,velocityDefinition", config["vdef"])
    print("LO1,sourceVelocity,position", velocity)
    print("LO1,restFrame", velframe)
    print("LO1,ifCenterFreq", centerFreq)
    print("LO1 derived mixing freq", centerFreq + config["DOPPLERTRACKFREQ"])

    params.append(("LO1,restFrequency", config["DOPPLERTRACKFREQ"]))
    params.append(("LO1,velocityDefinition", config["vdef"]))
    params.append(("LO1,sourceVelocity,position", velocity))
    params.append(("LO1,restFrame", velframe))
    params.append(("LO1,ifCenterFreq", centerFreq))
    
    # what about the IF2, LO2 settings?
    if3s = []
    try:
        for path in ifPath:
            if3s.append(path[RAWPATHS][0]["if3"])
    except:
        if3s = copy(IF3[config["backend"]])
    print("IFs:", if0, if1, if3s)    

    # lo1aFreq = (self.flocal + self.if1) / 2.0
    # RCVR_IF_NOMINAL[receiver]
    if backend == "VEGAS":
        ifRackFilters = set_if_filters(RCVR_IF_NOMINAL[receiver], ifPath)
    else:    
        centerFreq = RCVR_IF_NOMINAL[receiver]
        low = centerFreq - (bwTotal*.5)
        high = centerFreq + (bwTotal*.5)
        ifRackFilters = set_if_filters_oldstyle(low, high, ifPath)
    print("ifRackFilters: ", ifRackFilters)
    for f in ifRackFilters:
        params.append(f)

    if backend == "VEGAS":
        computeLO2(freqLocal, if0, if1, config, ifPath)

        # report results
        print("LO2 settings")
        keys = ['beam', 'cm', 'xsw', 'opticalDriver', 'IFRackSw', 'backendPort']
        for p in ifPath:
            vs = ["%s = %s" % (k, p[k]) for k in keys]
            print (",".join(vs))
            for r in p['rawpaths']:
                print ("  restfreq, if3", r['restfreq'], r['if3'])
            print("LO2: ", p["lo2"])
            # set appropriate parameter
            param = "ConverterRack,GFrequency,%s" % p['cm']
            print("Set param %s = %f" % (param, p["lo2"]))
            params.append((param, p["lo2"]))

    return params

def test1():
    "Mimics VEGASTests.testBasic"

    # config from unit test:

        # g = gbtsetup()
        # g.set_test_pickle_file("./test_pkl")
        # g.set_devHealth("./dev_health.conf")
        # g.set_vegas_conf_file("/users/monctrl/bin/Universal_vegas.conf")
        # # g.set_test_pickle_file("./test_pkl")
        # # g.set_devHealth("./dev_health.conf")
        # g.restfreq = 1400, 1430
        # g.nwin = 2
        # g.backend = "VEGAS"
        # g.receiver = "Rcvr1_2"
        # g.obstype = "Spectroscopy"
        # g.bandwidth = 23.44
        # g.vegas.subband = 8
        # g.nchan = "low"
        # g.dopplertrackfreq = 1401

    configMaybe = {
        "receiver": "Rcvr1_2",
        "backend": "VEGAS",
        "obstype": "Spectroscopy",
        "nchan": "low",
        "dopplertrackfreq": 1401,
        "restfreq": [1400., 1430.],
        "nwin": 2,
        "subband": 8,
        "bandwidth": 23.44
    }    

    config = getTest1ConfigFull()
    # ConfigValidator set None to actual values.  Here we care about:
    #     beam :         None ->           B1                                                                     
    #    dfreq :         None ->       [0, 0]                                                                     
    #  if3freq :         None ->       [0, 0]                                                                     
    #  lo2freq :            0 ->       [0, 0]                                                                     
    # noisecal :         None ->       lo-ext                                                                     
    # notchfilter :         None ->           In                                                                     
    # phasecal :         None ->          off                                                                     
    # polarization :      None ->       Linear                                                                     
    # polswitch :         None ->         thru                                                                     
    #   swfreq :         None ->       (0, 0)                                                                     
    #   swmode :         None ->           tp                                                                     
    #    swper :         None ->          1.0                                                                     
    #     tint :         None ->          1.0                                                                     
    #     vdef :         None ->        Radio                                                                     
    #    vfits :         None ->       sdfits                                                                     
    #   vframe :         None ->         topo                                                                     
    #     vpol :         None ->         self    
    config['vdef'] = 'Radio'
    config['vframe'] = 'topo'
    config['vpol'] = 'self'
    config['beam'] = 'B1'
    config['lo2freq'] = [0, 0]

    # restuls of 'collapsing' IF
    win1 = {'filter_bw': 1400, 'tint': 1.0, 'number_spectra': 2, 'deltafreq': 0, 'if3': 750, 'res': 5.7, 'vel_freq': 1400.0, 'beam': '1', 'bandwidth': 23.44, 'vpol': 'self', 'mode': 20, 'restfreq': 1400, 'subband': 8, 'nchan': 4096}
    win2 = {'tint': 1.0, 'deltafreq': 0, 'vel_freq': 1430.0, 'beam': '1', 'bandwidth': 23.44, 'vpol': 'self', 'subband': 8, 'mode': 20, 'restfreq': 1430}
    
    wins = [win1, win2]
    beam = win1['beam']

    rx = "Rcvr1_2"
    g = getGraph(rx)
    
    paths = chooseVegasPaths(g, rx, beam) 

    ifInfo = savePaths(g, paths, wins)

    exp1 = {'xsw': '9', 'cm': '1', 'backendPort': 'J1', 'xswSetting': 'thru', 'beam': 'XL', 'IFRackSw': '1', 'beam_num': '1', 'opticalDriver': '1', 'backend': 'VEGAS'
    , 'rawpaths': [{'filter_bw': 1400, 'tint': 1.0, 'number_spectra': 2, 'deltafreq': 0, 'if3': 750, 'res': 5700.0, 'vel_freq': 1400.0, 'beam': '1', 'bandwidth': 23.44, 'used': 1, 'vpol': 'self', 'mode': 20, 'restfreq': 1400, 'subband': 8, 'nchan': 4096, 'bank': 'BankA'},
                    {'tint': 1.0, 'deltafreq': 0, 'vel_freq': 1430.0, 'beam': '1', 'bandwidth': 23.44, 'vpol': 'self', 'subband': 8, 'mode': 20, 'restfreq': 1430}]
    }

    exp2 =  {'xsw': '10', 'cm': '5', 'backendPort': 'J2','xswSetting': 'thru', 'beam': 'YR', 'IFRackSw': '3', 'beam_num': '1', 'opticalDriver': '3', 'backend': 'VEGAS'
    , 'rawpaths': [{'filter_bw': 1400, 'tint': 1.0, 'number_spectra': 2, 'deltafreq': 0, 'if3': 750, 'res': 5700.0, 'vel_freq': 1400.0, 'beam': '1', 'bandwidth': 23.44, 'used': 1, 'vpol': 'self', 'mode': 20, 'restfreq': 1400, 'subband': 8, 'nchan': 4096, 'bank': 'BankA'}
        , {'tint': 1.0, 'deltafreq': 0, 'vel_freq': 1430.0, 'beam': '1', 'bandwidth': 23.44, 'vpol': 'self', 'subband': 8, 'mode': 20, 'restfreq': 1430}],}
    exps = [exp1, exp2]

    # this shows that we're only not getting the beam_num not right
    for i in range(2):
        ifi = ifInfo[i]
        exp = exps[i]
        for key, value in ifi.items():
            if key == 'rawpaths':
                continue
            if key not in exp:
                print("no key", key)
                continue
            if value != exp[key]:
                print("DIFF", key, value, exp[key]) 

    # assert ifInfo[0] == exp1
    # assert ifInfo[1] == exp2

    params = calcFreqs(config, ifInfo)

    for p in params:
        print(p)

    exp = [
        ('Rcvr1_2,leftIfFilterSwitch', '3'),
        ('Rcvr1_2,rightIfFilterSwitch', '3'),
        ('LO1,restFrequency', 1401),
        ('LO1,velocityDefinition', 'Radio'),
        ('LO1,sourceVelocity,position', 0.0),
        ('LO1,restFrame', 'Local'),
        ('LO1,ifCenterFreq', 3014.0),
        ('IFRack,filter_select,1', 'pass_2960_3040'),
        ('IFRack,filter_select,3', 'pass_2960_3040'),
        ('ConverterRack,GFrequency,1', 12750.0),
        ('ConverterRack,GFrequency,5', 12750.0),
    ]

    assert exp == params

    # These are the parameters set for the receiver for VEGASTests.testBasic:
       # by DB lookup:
       # Rcvr1_2 cpuLoCalPwrSw  =  swOn                                                                               
       # Rcvr1_2 cryoState  =  refrigCool                                                                             
       # Rcvr1_2 lbBiasSwitch  =  swOn                                                                                
       # Rcvr1_2 raBiasSwitch  =  swOn
       # from somewhere else:                                                                                
       # Rcvr1_2 leftIfFilterSwitch  =  3  # Receivers.py                                                                           
       # Rcvr1_2 loOrHiCalSel  =  lowCal # R                                                                             
       # Rcvr1_2 notchFilter  =  In      # R                                                                             
       # Rcvr1_2 polarizationSelect  =  polLinear # R                                                                     
       # Rcvr1_2 rightIfFilterSwitch  =  3           # R                                                                 
       # Rcvr1_2 tuning_frequency  =  1415.0            # R                                                              
       # Rcvr1_2 xferSwCtlMode  =  ctlMcb               # R                                                              
       # Rcvr1_2 xferSwitch  =  tsThru                  # R                                                              
       # Rcvr1_2 xlCPUNoiseSwCtrl  =  swOff            # R                                                               
       # Rcvr1_2 xlExtToMCBCtrlSel  =  ctlExt          # R                                                               
       # Rcvr1_2 yrCPUNoiseSwCtrl  =  swOff            # R                                                               
       # Rcvr1_2 yrExtToMCBCtrlSel  =  ctlExt         # Receivers.py

    # How are these set?  Mostly from the giant config table, that started off like in 
    # Test1ConfigFull(), but 

    # most notably, beam, noisecal, notchfilter, polarization, polswitch.  see what happens:

    # Set by mapping these config keywords to these values in Receivers.py:
    # 'config keyword':
    #     'value': (paramName, paramValue)

    # polswitch:
    #     "ext": (
        #     ("xferSwCtlMode", "ctlExt"),
        # ),
        # "thru": (
        #     ("xferSwCtlMode", "ctlMcb"),
        #     ("xferSwitch", "tsThru")
        # ),
        # "cross": (
        #     ("xferSwCtlMode", "ctlMcb"),
        #     ("xferSwitch", "tsCrossed")
        # )

    # noisecal
        # For Rcvr1_2, NOISECAL_LO is used
        # NOISECAL_LO = {
        #     "off": (
        #         ("xlExtToMCBCtrlSel", "ctlMcb"),
        #         ("yrExtToMCBCtrlSel", "ctlMcb"),
        #         ("xlCPUNoiseSwCtrl", "swOff"),
        #         ("yrCPUNoiseSwCtrl", "swOff"),
        #         ("loOrHiCalSel", "lowCal")),
        # 
        # ...
        #
        # "lo": (
        #     ("xlExtToMCBCtrlSel", "ctlExt"),
        #     ("yrExtToMCBCtrlSel", "ctlExt"),
        #     ("xlCPUNoiseSwCtrl", "swOff"),
        #     ("yrCPUNoiseSwCtrl", "swOff"),
        #     ("loOrHiCalSel", "lowCal")),

    # polarization
    #     (polarizationSelect, pol + value of polarization)
    # I don't see how this doesn't fail when config['polarization'] = None, as here

    # notchFilter
    #   simply set notchFilter param to config value!

    # chopper
    #   ('chopperCntrl', swOn/swOff depending on above)

    # Filters are different:
    #    if info derived from freq_calc object.  Then.
    #    range frond from bandwidth and tunning freq
    # rcvr: (filter names), (filter min, filter max, switch setting to select
    # filter, type)
    # FILTERS = {
    #     "Rcvr1_2": (
    #         ("leftIfFilterSwitch", "rightIfFilterSwitch"), (
    #             (1300, 1450, "3"),
    #             (1100, 1450, "4"),
    #             (1600, 1750, "2"),
    #             (1100, 1800, "1")
    #         ),
    #         1
    #     ),    
    # according to the code: choose the first of the above filters that is larger then 
    # computing range found around the tuning frequency.  What the hell is the tuning freq?

    # tuning frequency is derived from FrequencyCalculator.sky_freq_orig, and sky_freq is 
    # derived from the center of the frequencies (freq_min, freq_max), from all_vfreqs,
    # which in turn is local_freq_vlow and local_freq_vhigh.
    # These in turn are set in the FrequencyCalculator.set_freq_w_vel* methods.
    # So, this all hinges on what's going on with the velocity stuff.

    # since our vframe is topo, there should be no freq. shift to take into account.
    # maybe that's why our final tuning frequency of 1415 is right between the
    # two original config['restfreq'] = [1400, 1430]?  

    # but what about the bandwidth used when determing which filter to use (along with tuning freq?
    # This is even more complicated in FrequencyCalculator.  looks like it involves all_vfreq, but swfreq
    # as well.  But can't be over 4000!

    # Path from Rcvr1_2:J4 to VEGAS:J2:
    # Bandpass changes:
    #    LO to    HI (   BW):  CNTR,  TRGT
    # 1100.00 to 1752.00 (652.00): 1426.00, 1375.00  change:  Rcvr1_2:YR (feed) Polarization: linear_y Freq: 1100 to 1752 MHz Horn: 1
    #    <******>                                                                       

    # 1300.00 to 1450.00 (150.00): 1375.00, 1375.00  change:  Rcvr1_2:FL4R (filter) Freq: 1300 to 1450 MHz
    #      <*>                                                                          
    # 1. CHECK!  We are setting this filter!

    # 2965.00 to 3115.00 (150.00): 3040.00, 3040.00  change:  Rcvr1_2:MXR (mixer) frequency: 4415 sideband: lower name: LO1A:synthesizer
    #                    <**>                                                           
    # 2. CHECK! We are setting LO1 freq to 4415 based off L1 rest freq (1401) and center freq (3014) = 1401 + 3014 = 4415!
    # BUT: the Rcvr1_2XL:0 IF parmater has sky of 1375 and center freq of 3040, which also give 4415!

    # 2965.00 to 3040.00 (75.00): 3002.50, 3040.00  change:  OpticalDriver3:F3 (filter) Freq: 2960 to 3040 MHz
    #                    <*>                                                            
    # 3. CHECK! We are setting [('filter_select,1', 'pass_2960_3040'), ('filter_select,3', 'pass_2960_3040')]
    # But: 2965 != 2960?

    # 9710.00 to 9785.00 (75.00): 9747.50, 9710.00  change:  ConverterModule5:MX2 (mixer) frequency: 12750 sideband: lower name: LO2_G1:synthesizer
    #                                                                                <*>
    # 4. CHECK! We are setting ConverterRack,GFrequency,1 and 5 to 12750!

    # 715.00 to 790.00 (75.00): 752.50, 790.00  change:  ConverterModule5:MX3 (mixer) frequency: 10500 sideband: lower name: LO3Distribution1:synthesizer
    # <> 
    # 5. CHECK!  This is a fixed mixer.  

def test2():
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

    wins = []
    ifInfo = savePaths(g, paths, wins)

    params = calcFreqs(config, ifInfo)

    for p in params:
        print(p)

    exp = [
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
    assert params == exp

    # here are the bandpass changes we need to make:
    # Path from Rcvr1_2:J3 to DCR:J1:
    # Bandpass changes:
    #    LO to    HI (   BW):  CNTR,  TRGT
    # 1100.00 to 1752.00 (652.00): 1426.00, 1375.00  change:  Rcvr1_2:XL (feed) Polarization: linear_x Freq: 1100 to 1752 MHz Horn: 1
    # <**************************>

    # 1300.00 to 1450.00 (150.00): 1375.00, 1375.00  change:  Rcvr1_2:FL4L (filter) Freq: 1300 to 1450 MHz
    #         <******>
    # CHECK!

    # 2950.00 to 3100.00 (150.00): 3025.00, 3025.00  change:  Rcvr1_2:MXL (mixer) frequency: 4400 sideband: lower name: LO1A:synthesizer
    #                                                                           <******>
    # CHECK!

    # 2960.00 to 3040.00 (80.00): 3000.00, 3025.00  change:  OpticalDriver1:F3 (filter) Freq: 2960 to 3040 MHz
    #                                                                       <***>       
    # CHECK!

    # So, this is:
    #    * 1 filter in Rcvr1_2
    #    * mix with LO1A
    #    * filter in OpticalDriver

    # Requirements:
    #   * no doppler tracking
    #   * DCR center IF should be 3000


def test3():
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
        
    exp = [
        ['Rcvr2_3:XL', 'R2_3XL:0', 'R2_3XL:1', 'IFRouter:J5', 'SWITCH1', 'IFXS9:thru', 'IFRouter:J65', 'OpticalDriver1:J1', 'OpticalDriver1:J4', 'DCR:A_1'],
        ['Rcvr2_3:YR', 'R2_3YR:0', 'R2_3YR:1', 'IFRouter:J21', 'SWITCH3', 'IFXS10:thru', 'IFRouter:J67', 'OpticalDriver3:J1', 'OpticalDriver3:J4', 'DCR:A_3']
    ]

    rx = "Rcvr2_3"
    fn = "zdb.201118.pkl.%s.txt" % rx
    g = getGraph(rx, filepath=fn)
    paths = chooseDcrPaths(g, rx, 1, debug=False)
    
    # test paths
    assert len(paths) == 2
    assert paths[0] == exp[0]
    assert paths[1] == exp[1]


    wins = []
    ifInfo = savePaths(g, paths, wins)

    params = calcFreqs(config, ifInfo)

    # test freq. related params set
    exp = [
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
    assert params == exp

def test4():
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
        
    rx = "Rcvr8_10"
    fn = "zdb.201118.pkl.%s.txt" % rx
    g = getGraph(rx, filepath=fn)
    paths = chooseDcrPaths(g, rx, 1, debug=False)

    exp = [
        ['Rcvr8_10:L', 'R8_10XL:0', 'R8_10XL:1', 'IFRouter:J13', 'SWITCH1', 'IFXS9:cross', 'IFRouter:J65', 'OpticalDriver1:J1', 'OpticalDriver1:J4', 'DCR:A_1'],
        ['Rcvr8_10:R', 'R8_10YR:0', 'R8_10YR:1', 'IFRouter:J29', 'SWITCH3', 'IFXS10:cross', 'IFRouter:J67', 'OpticalDriver3:J1', 'OpticalDriver3:J4', 'DCR:A_3']
    ]
        
    # test paths - these ONLY depend on 'rx' variable above!
    assert len(paths) == 2
    assert paths[0] == exp[0]
    assert paths[1] == exp[1]


    wins = []
    ifInfo = savePaths(g, paths, wins)

    params = calcFreqs(config, ifInfo)

    for p in params:
        print(p)
    # test freq. related params set
    exp = [
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
    assert params == exp

def getTest1ConfigFull():

    config = {}
    VEGAS = 'VEGAS'
    config['DOPPLERTRACKFREQ'] = 1401                                                                               
    config['XL_on_integs'] = None                                                                                   
    config['YR_on_integs'] = None                                                                                   
    config['backend'] = VEGAS                                                                                       
    config['bandwidth'] = 23.44                                                                                     
    config['beam'] = None                                                                                           
    config['beamswitch'] = None                                                                                     
    config['both_on_integs'] = None                                                                                 
    config['broadband'] = None                                                                                      
    config['bswfreq'] = None                                                                                        
    config['cal_off_integs'] = None                                                                                 
    config['chopper'] = None                                                                                        
    config['crosspol'] = None                                                                                       
    config['datadisk'] = None                                                                                       
    config['defaultdac'] = None                                                                                     
    config['dfreq'] = None                                                                                          
    config['dm'] = None                                                                                             
    config['fold_bins'] = None                                                                                      
    config['fold_dumptime'] = None                                                                                  
    config['fold_parfile'] = None                                                                                   
    config['freq'] = (1400, 1430)                                                                                   
    config['if0freq'] = 0                                                                                           
    config['if3freq'] = None                                                                                        
    config['ifbw'] = 0                                                                                              
    config['iftarget'] = None                                                                                       
    config['ignore_dopplertrackfreq'] = False                                                                       
    config['init'] = 'basic'                                                                                          
    config['levels'] = None                                                                                         
    config['lo1bfreq'] = 0                                                                                          
    config['lo2freq'] = 0                                                                                           
    config['lsync'] = 300                                                                                           
    config['lutstart'] = 0                                                                                          
    config['mode'] = None                                                                                           
    config['nchan'] = 'low'                                                                                           
    config['newDeltaFreq'] = {}                                                                                     
    config['newFreq'] = {}                                                                                          
    config['noisecal'] = None                                                                                       
    config['notchfilter'] = None                                                                                    
    config['nsamp'] = 80                                                                                            
    config['nstep'] = 8                                                                                             
    config['numbanks'] = None                                                                                       
    config['numchan'] = None                                                                                        
    config['nwin'] = 2                                                                                              
    config['obsmode'] = None                                                                                        
    config['obstype'] = 'Spectroscopy'                                                                                
    config['outbits'] = None                                                                                        
    config['phasecal'] = None                                                                                       
    config['polarization'] = None                                                                                   
    config['polnmode'] = None                                                                                       
    config['polswitch'] = None                                                                                      
    config['polyco'] = None                                                                                         
    config['receiver'] = 'Rcvr1_2'                                                                                    
    config['refatten'] = 0                                                                                          
    config['reqinteg'] = 0                                                                                          
    config['scale'] = None                                                                                          
    config['settle'] = 200                                                                                          
    config['subband'] = 8                                                                                           
    config['swfreq'] = None                                                                                         
    config['swmode'] = None                                                                                         
    config['swper'] = None                                                                                          
    config['swtype'] = None                                                                                         
    config['testatten'] = 0                                                                                         
    config['tint'] = None                                                                                           
    config['tuning'] = None                                                                                         
    config['vdef'] = None                                                                                           
    config['vfits'] = None                                                                                          
    config['vframe'] = None                                                                                         
    config['vhigh'] = 0                                                                                             
    config['vlbirack'] = None                                                                                       
    config['vlow'] = 0                                                                                              
    config['vpol'] = None                                                                                           
    config['xfer'] = None           

    return config

def main():
    test1()
    test2()
    test3()
    test4()

if __name__ == '__main__':
        main()    
