"""
This module is responsible for replicating some of the results from the 
GBT_DB class from the config tool.

This class uses an interesting method of extracting sets of manager,parameter,value
triplets from the gbtconfigurations DB based off the values of keywords 
in the configuration.

For example, from the standard 'Continuum with Rcvr1_2' configuration, these
keywords result in the following:

KEYWORD - VALUE - # PARAMS - NOTES
backend - DCR (DCRPrimary) - 3 - all switching signal selector related
reciever - Rcvr1_2 - 5 - mostly sets Rcvr1_2, but also sets receiver in SC
swmode - tp - 7 - all SC phase related params
vframe - topo - 1 - L01, restframe, Local
vdef - radio - 1 - LO1, velocifyDefinition, Radio

Other config keywords that are check but make no contribution for this example
are: obstype, swtype, beam, noisecal.

Finally, the GBT_DB class ALWAYS reads in 26 manager, param, value triplets, 
no matter the configuration.

You would think this system would be a huge list of manager,param,value triplets,
but the DB only contains 133, triggered off 55 'meta' keywords.

"""

from pprint import pprint

def copyRcvrParams(params, newRx):
    "Rcvr params are very similar, so copy one to make one for a new rx"
    newParams = []
    for mgr, param, value in params:
        if mgr == 'ScanCoordinator':
            new = (mgr, param, newRx)
        else:
            new = (newRx, param, value)
        newParams.append(new)
    return newParams            
    # 'Rcvr2_3': copyRcvrParams(Rcvr1_2Params, 'Rcvr2_3') 

# MariaDB [gbt_configuration]> select manager, mc_param, mc_value from (mc, meta_to_mc) inner join meta on (meta_to_mc.meta_id=meta.meta_id and meta_to_mc.mc_id=mc.mc_id and (meta.meta_set = ''));
# +-------------------------+----------------------------+------------+
# | manager                 | mc_param                   | mc_value   |
# +-------------------------+----------------------------+------------+
# | LO1                     | autoSetLOPowerLevel        | 1          |
# | IFRack                  | laser_auto_level_control,4 | swOn       |
# | IFRack                  | laser_auto_level_control,3 | swOn       |
# | IFRack                  | laser_auto_level_control,2 | swOn       |
# | SwitchingSignalSelector | disableLOBlanking          | 1          |
# | IFRack                  | laser_auto_level_control,1 | swOn       |
# | IFRack                  | noise_bandwidth            | narrowband |
# | LO1                     | useOffsets                 | 0          |
# | LO1                     | subsystemSelect,LO1A       | 1          |
# | LO1                     | subsystemSelect,LO1B       | 1          |
# | LO1                     | subsystemSelect,LO1Counter | 0          |
# | LO1                     | subsystemSelect,LO1Router  | 1          |
# | IFRack                  | subsystemSelect,driver3    | 1          |
# | IFRack                  | subsystemSelect,driver2    | 1          |
# | IFRack                  | subsystemSelect,noise      | 1          |
# | IFRack                  | subsystemSelect,driver1    | 1          |
# | IFRack                  | subsystemSelect,router     | 1          |
# | IFRack                  | subsystemSelect,driver8    | 1          |
# | IFRack                  | subsystemSelect,driver7    | 1          |
# | IFRack                  | subsystemSelect,driver6    | 1          |
# | IFRack                  | subsystemSelect,driver5    | 1          |
# | IFRack                  | subsystemSelect,driver4    | 1          |
# | IFRack                  | laser_auto_level_control,6 | swOn       |
# | IFRack                  | laser_auto_level_control,5 | swOn       |
# | IFRack                  | laser_auto_level_control,8 | swOn       |
# | IFRack                  | laser_auto_level_control,7 | swOn       |

swOn = 'swOn'
narrowband = 'narrowband'
LO1 = 'LO1'

baseParams = [
    ('LO1',    'autoSetLOPowerLevel',       1         ),
    ('LO1',    'useOffsets',                0         ),
    ('LO1',    'subsystemSelect,LO1A', 1         ),
    ('LO1',    'subsystemSelect,LO1B', 1         ),
    ('LO1',    'subsystemSelect,LO1Counter', 0         ),
    ('LO1',    'subsystemSelect,LO1Router ', 1         ),
    # There is no manager 'Switch'.  WTF?
    # ('Switch', 'disableLOBlanking', 1         ),
    ('IFRack', 'noise_bandwidth', narrowband),
    ('IFRack', 'subsystemSelect,driver3', 1         ),
    ('IFRack', 'subsystemSelect,driver2',    1         ),
    ('IFRack', 'subsystemSelect,driver1',    1         ),
    ('IFRack', 'subsystemSelect,driver8',    1         ),
    ('IFRack', 'subsystemSelect,driver7',    1         ),
    ('IFRack', 'subsystemSelect,driver6',    1         ),
    ('IFRack', 'subsystemSelect,driver5',    1         ),
    ('IFRack', 'subsystemSelect,driver4',    1         ),
    ('IFRack', 'subsystemSelect,router', 1         ),
    ('IFRack', 'subsystemSelect,noise', 1         ),
    ('IFRack', 'laser_auto_level_control,4', swOn      ),
    ('IFRack', 'laser_auto_level_control,3', swOn      ),
    ('IFRack', 'laser_auto_level_control,2', swOn      ),
    ('IFRack', 'laser_auto_level_control,1', swOn      ),
    ('IFRack', 'laser_auto_level_control,6', swOn      ),
    ('IFRack', 'laser_auto_level_control,5', swOn      ),
    ('IFRack', 'laser_auto_level_control,8', swOn      ),
    ('IFRack', 'laser_auto_level_control,7', swOn       ),
]

# Backends:

dcrSwitchingSignalParams = [
   ('SwitchingSignalSelector', 'disableLocalBlanking', 1  ),
   ('SwitchingSignalSelector', 'switching_signals_master', 'DCR'),
   # ('SwitchingSignalSelector', 'disableLocalBlanking', 1  ),
]

backends = {
    'DCR': dcrSwitchingSignalParams
}

# Receivers:

Rcvr1_2Params = [
    ('Rcvr1_2', 'raBiasSwitch', 'swOn'),
    ('Rcvr1_2', 'lbBiasSwitch', 'swOn'),
    ('Rcvr1_2', 'cryoState', 'refrigCool'),
    ('Rcvr1_2', 'cpuLoCalPwrSw', 'swOn'),
    ('ScanCoordinator', 'receiver', 'Rcvr1_2'),
]


# supported receivers
rxs = ["Rcvr1_2", "Rcvr2_3", "Rcvr4_6", "Rcvr8_10", "Rcvr12_18", "Rcvr26_40"]

receivers = {}
for rx in rxs:
    receivers[rx] = copyRcvrParams(Rcvr1_2Params, rx)

# not supported receivers
rxsNotSupported = ["Rcvr_342", "Rcvr_450", "Rcvr_800", "Rcvr_600"]

# we can at least do this; put them in the SC:
for rx in rxsNotSupported:
    receivers[rx] = [('ScanCoordinator', 'receiver', rx)]

# receivers = {
#     'Rcvr1_2': Rcvr1_2Params,
#     'Rcvr2_3': copyRcvrParams(Rcvr1_2Params, 'Rcvr2_3')    
#     'Rcvr': copyRcvrParams(Rcvr1_2Params, 'Rcvr4_6')    
# }


# swmode - switching modes
SC = 'ScanCoordinator'
Sig = 'Sig'
Ref = 'Ref'
Noise = 'Noise'
NoNoise = 'NoNoise'

tpSwmodParams = [
    (SC, 'number_phases', 2      ),
    (SC, 'cal_state,1', NoNoise),
    (SC, 'cal_state,2', Noise  ),
    (SC, 'sig_ref_state,1', Sig    ),
    (SC, 'sig_ref_state,2', Sig    ),
    (SC, 'phase_start,1', 0      ),
    (SC, 'phase_start,2', 0.5    ),
]

spSwmodParams = [
    (SC, 'number_phases', 4      ),
    (SC, 'cal_state,1', NoNoise),
    (SC, 'cal_state,2', Noise  ),
    (SC, 'cal_state,3', NoNoise),
    (SC, 'cal_state,4', Noise  ),    
    (SC, 'sig_ref_state,1', Sig    ),
    (SC, 'sig_ref_state,2', Sig    ),
    (SC, 'sig_ref_state,3', Ref    ),
    (SC, 'sig_ref_state,4', Ref    ),    
    (SC, 'phase_start,1', 0      ),
    (SC, 'phase_start,2', 0.25   ),
    (SC, 'phase_start,3', 0.50   ),
    (SC, 'phase_start,4', 0.75   ),
]

swmodParams = {
    "tp" : tpSwmodParams,
    "sp" : spSwmodParams
}

# vframe
vframeParams = {
    'top': (LO1, "restframe", "Local")
}

# vdef
vdefParams = {
    'radio': (LO1, "velocifyDefinition", "Radio")
}

def getDBParamsFromConfig(config, dct=True, tuples=False):

    params = baseParams

    config2values = [
        (backends, 'backend'),
        # (receivers, 'receiver'),
        (swmodParams, 'swmode')
    ]

    # not all receivers supported
    if config['receiver'] in receivers:
        config2values.append((receivers, 'receiver'))



    for paramDct, configKeyword in config2values:
        params.extend(paramDct[config[configKeyword]])

    # params.extend(backends[config['backends']])
    # params.extend(receivers[config['receivers']])
    # params.extend(swmodParams[config['swmod']])

    # TBF: return type chaos!

    if tuples:
        tuples2=[]
        # convert 3 tuple to 2 tuple
        for mgr, param, value in params:
            tuples2.append(("%s,%s" % (mgr, param), value))
        return tuples2 

    return params if not dct else paramTripletList2Dict(params)

def paramTripletList2Dict(paramsList):
    "[(mgr,param,value)] -> {mgr: {param: value}}"
    d = {}
    for mgr, param, value in paramsList:
        if mgr not in d:
            d[mgr] = {}
        # don't overwrite shit  
        # assert param not in d[mgr]
        if param in d[mgr]:
            print ("waring overwriting", mgr, param, d[mgr][param], " w/ ", value)
        d[mgr][param] = value   
    return d



def quickRcvr1_2test():

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

    ps = getDBParamsFromConfig(config)

    pprint(ps)
    
def main():
    quickRcvr1_2test()
if __name__ == '__main__':
    main()