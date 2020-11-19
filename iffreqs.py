from copy import copy

from ifpaths import getGraph, chooseVegasPaths, getFrontend, PathNode

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

        ifpathInfo["rawpaths"] = wins

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

def test1():
    "Mimics VEGASTests.testBasic"

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


def main():
    test1()

if __name__ == '__main__':
        main()    
