# Copyright (C) 2016 Associated Universities, Inc. Washington DC, USA.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
# Correspondence concerning GBT software should be addressed as follows:
#       GBT Operations
#       National Radio Astronomy Observatory
#       P. O. Box 2
#       Green Bank, WV 24944-0002 USA

# from gbt.ygor import getConfigValue
# import ConfigParser

EXPECTED_VARS = (
    "__del__",
    "__doc__",
    "__init__",
    "__module__",
    "GetIFPathInfo",
    "GetKeywordValue",
    "Log",
    "RadioAstron",
    "RcvrArray1_2",
    "Rcvr_MBA1_5",
    "Rcvr_PAR",
    "LASSI",
    "XL_on_integs",
    "YR_on_integs",
    "abort_callback",
    "add_bad_converter_modules",
    "add_bad_devices",
    "add_device",
    "add_logger",
    "afr",
    "allpaths",
    "backend",
    "backends",
    "bad_devices",
    "bal",
    "balance_acs",
    "balance_ifrack",
    "balance_sp",
    "bandwidth",
    "be",
    "beam",
    "beamswitch",
    "both_on_integs",
    "broadband",
    "bswfreq",
    "cal_off_integs",
    "ccb",
    "checkStatus",
    "check_config",
    "check_dcr_override",
    "check_devices",
    "check_local_scope",
    "check_telescope",
    "chopper",
    "ckDopplerUse",
    "cm",
    "command_line",
    "config",
    "configDir",
    "configToolDir",
    "configure",
    "create_list",
    "datadisk",
    "db",
    "db_items",
    "dcr",
    "default_values",
    "defaultdac",
    "delete_list",
    "deltafreq",
    "devHealth",
    "devHealthPath",
    "devVegasConfPath",
    "devices",
    "dm",
    "dopplertrackfreq",
    "fold_bins",
    "fold_dumptime",
    "fold_parfile",
    "freq_calc",
    "generic",
    "get_db_items",
    "get_meta",
    "get_param",
    "get_port",
    "grailHost",
    "guppi",
    "holo",
    "if0freq",
    "if3freq",
    "ifPathInfo",
    "ifbw",
    "ifpath",
    "ifrack",
    "ifstat",
    "iftarget",
    "ignore_dopplertrackfreq",
    "init",
    "lo",
    "lo1bfreq",
    "lo2freq",
    "log",
    "logfile",
    "loggers",
    "lopickled_data",
    "lsync",
    "mc",
    "meta",
    "mustang",
    "nchan",
    "newDeltaFreq",
    "newFreq",
    "noisecal",
    "notchfilter",
    "nsamp",
    "nstep",
    "numbanks",
    "numchan",
    "nwin",
    "obsmode",
    "obstype",
    "oldifpath",
    "orig_be",
    "orig_nwin",
    "outbits",
    "phasecal",
    "pickled_data",
    "pol",
    "polnmode",
    "polswitch",
    "prepare",
    "print_config",
    "print_paths",
    "rcvr",
    "re_init",
    "recBW",
    "receiver",
    "redefine_be",
    "remove_bad_devices",
    "reset",
    "reset_devHealth",
    "reset_test_pickle_file",
    "restfreq",
    "revert_be",
    "savedFreq",
    "savedSolutions",
    "saveddoppler",
    "sc",
    "scale",
    "seq",
    "setAstridReqDefaults",
    "set_devHealth",
    "set_log",
    "set_manager_off",
    "set_manager_on",
    "set_manager_standby",
    "set_param",
    "set_sim_mode",
    "set_test_pickle_file",
    "set_user",
    "set_vegas_conf_file",
    "settle",
    "setup",
    "sideband",
    "sp",
    "spect",
    "split_backend_name",
    "subband",
    "swfreq",
    "swmode",
    "swper",
    "swtype",
    "tint",
    "tuning",
    "user",
    "user_bad_devices",
    "validate",
    "validator",
    "vdef",
    "vegas",
    "vframe",
    "vhigh",
    "vlbi",
    "vlow",
    "xfer",
    "ygorDir",
)

def fuzzy_matcher(pattern):
    """
    A utility called from a filter operation on a dict, which has tuples as keys.
    None's in the tuple act as * or all inclusive.
    :returns a functional closure to be used with filter().
    """
    def f(reo):
        return all(p is None or r == p for r, p in zip(reo, pattern))
    return f


def get_vegas_config_value(keyword, section):

    def get_items(config, section):
        kv = dict()
        try:
            parent = config.get(section, "parent")
        except ConfigParser.NoOptionError as e:
            parent = None
        except ConfigParser.NoSectionError as e:
            parent = None
        if parent is not None:
            kv = dict(config.items(parent))
        kv.update(config.items(section))
        return kv

    ygor_telescope=getConfigValue("/home/gbt", "YGOR_TELESCOPE")
    if ygor_telescope is None:
        return None
    filename=ygor_telescope + '/etc/config/vegas.conf'
    cp=ConfigParser.ConfigParser()
    cp.readfp(open(filename))
    try:
        allkvs = get_items(cp, section)
    except ConfigParser.NoOptionError as e:
        print("No such keyword %s in section %s in file %s" % (keyword, section, filename))
        return None

    if keyword is not None and keyword in allkvs.keys():
        return allkvs[keyword]
    else:
        return None


# VEGAS DEFS -------------------------
class VegasModeData:

    def __len__(self):
        return len(self.d)

    def __iter__(self):
        return self.d.__iter__()

    def items(self):
        return self.d.items()

    def keys(self):
        return self.d.keys()

    def __getitem__(self, key):
        """
        The big list is a dict of dicts, with the primary dict keys of the form:
        (bandwidth, abstract_nchan_name, either_subbands_or_coherentness)
        In VPM its easier/necessary to search for nchan by value, instead of name.
        So the fuzzy matcher will look for a key match for each non-None element
        in the search pattern. The None elements act as a wildcard match.

        So if the provided search key is (bw, nchan, coh_name), we can find the set
        of possiblilties using a pattern of (bw, None, coh_name), then iterating
        through the candidates, looking into the value for the integer nchan value.

        Contorted, but I'm working with what we here originally.
        """
        # print "__getitem__(", str(key), ")"
        k = self.find_native_key(key)
        if k is None:
            raise KeyError("No such combination of (bw,nchan,sb_or_cohmode) in %s" % str(key))
        else:
            return self.d[k]


    def find_native_key(self, key):
        """
        A utility to help index the vegas modes dictionary by numeric or named nchan
        Also string matches are always case-insensitive.
        :param key:
        :return: the native key where the match was found, which can in turn be used to access the value.
        """

        # Allow for case insensitive string matches
        sss = list(key)
        newkeylist = []
        for x in sss:
            if isinstance(x, str):
                newkeylist.append(x.lower())
            else:
                newkeylist.append(x)

        newkey = tuple(newkeylist)
        # the fastpath is if the key is already in native form and it exists
        if newkey in self.d.keys():
            return newkey

        # if the nchan is numeric, find a record matching the two other fields
        if isinstance(newkey[1], int):
            skey = (newkey[0], None, newkey[2])
            target_nchan = newkey[1]
            candidates = filter(fuzzy_matcher(skey), self.d)
            #print "found %d candidates" % len(candidates)
            for i in candidates:
                if target_nchan == self.d[i]["nchan"]:
                    return i
        else:
            pass
            #print("The VEGAS_MODES key %s does not exist" % str(newkey))
        return None

    def select(self, key, field=None):
        """
        Performs a slice-like operation based on the key.
        Values of None are taken to be wildcards.
        If the data subfield is specified (a string key into the inner dict),
        then the actual subfields are extracted and returned as a list.
        If left unspecified, the matching keys are returned as a list.
        """
        candidates = filter(fuzzy_matcher(key), self.d)
        if field is not None:
            rtn=[]
            for i in candidates:
                rtn.append(self.d[i][field])
            return rtn
        return candidates

    def __contains__(self, key):
        """
        Search for the key and see if it exists and is accessible by __getitem__
        :returns True/False

        Keys can be specified as explained in __getitem__
        """

        r= self.find_native_key(key) is not None
        #print "__contains__(", str(key), ") is ", r
        return r

    def __init__(self):
        """
        Builds the hard-coded data for vegas modes. Should really get this
        from a database query or config file.
        """
        # res= spectral resolution in KHz
        # min_int = minimum allowable integration time in seconds
        # key is bandwidth,nchans,vegas.subband
        # mode 1 and 2
        # was 1406 and 88
        # notes the min_blanking is in sec
        self.d = {
            (1500, "low", 1): {
                "res": 1465.0,
                "min_int": .0005,
                "mode": "MODE1",
                "nchan": 1024,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": 0.0005
            },
            (1500, "medium-low", 1): {
                "res": 92.0,
                "min_int": .001398,
                "mode": "MODE2",
                "nchan": 16384,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": .001398
            },
            (1500, "medium", 1): {
                "res": 92.0,
                "min_int": .001398,
                "mode": "MODE2",
                "nchan": 16384,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": .001398
            },
            (1500, "medium-high", 1): {
                "res": 92.0,
                "min_int": .001398,
                "mode": "MODE2",
                "nchan": 16384,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": .001398
            },
            (1500, "high", 1): {
                "res": 92.0,
                "min_int": .001398,
                "mode": "MODE2",
                "nchan": 16384,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": .001398
            },
            # mode 3
            (1080, "low", 1): {
                "res": 66.0,
                "min_int": .002097,
                "mode": "MODE3",
                "nchan": 16384,
                "valonFreq": 1080,
                "if3": 540,
                "filter_bw": 950,
                "min_blank": .002097
            },
            (1080, "medium-low", 1): {
                "res": 66.0,
                "min_int": .002097,
                "mode": "MODE3",
                "nchan": 16384,
                "valonFreq": 1080,
                "if3": 540,
                "filter_bw": 950,
                "min_blank": .002097
            },
            (1080, "medium", 1): {
                "res": 66.0,
                "min_int": .002097,
                "mode": "MODE3",
                "nchan": 16384,
                "valonFreq": 1080,
                "if3": 540,
                "filter_bw": 950,
                "min_blank": .002097
            },
            (1080, "medium-high", 1): {
                "res": 66.0,
                "min_int": .002097,
                "mode": "MODE3",
                "nchan": 16384,
                "valonFreq": 1080,
                "if3": 540,
                "filter_bw": 950,
                "min_blank": .002097
            },
            (1080, "high", 1): {
                "res": 66.0,
                "min_int": .002097,
                "mode": "MODE3",
                "nchan": 16384,
                "valonFreq": 1080,
                "if3": 540,
                "filter_bw": 950,
                "min_blank": .002097
            },

            # mode 4,5,6
            (187.5, "low", 1): {
                "res": 5.7,
                "min_int": .009961,
                "mode": "MODE4",
                "nchan": 32768,
                "valonFreq": 1500,
                "if3": 562.5,
                "filter_bw": 950,
                "min_blank": .001398
            },
            (187.5, "medium-low", 1): {
                "res": 2.9,
                "min_int": .019923,
                "mode": "MODE5",
                "nchan": 65536,
                "valonFreq": 1500,
                "if3": 562.5,
                "filter_bw": 950,
                "min_blank": .002796
            },
            (187.5, "medium", 1): {
                "res": 2.9,
                "min_int": .019923,
                "mode": "MODE5",
                "nchan": 65536,
                "valonFreq": 1500,
                "if3": 562.5,
                "filter_bw": 950,
                "min_blank": .002796
            },
            (187.5, "medium-high", 1): {
                "res": 1.4,
                "min_int": .029360,
                "mode": "MODE6",
                "nchan": 131072,
                "valonFreq": 1500,
                "if3": 562.5,
                "filter_bw": 950,
                "min_blank": .005592
            },
            (187.5, "high", 1): {
                "res": 1.4,
                "min_int": .029360,
                "mode": "MODE6",
                "nchan": 131072,
                "valonFreq": 1500,
                "if3": 562.5,
                "filter_bw": 950,
                "min_blank": 0.005592
            },
            # modes 7,8,9
            (100, "low", 1): {
                "res": 3.1,
                "min_int": .009830,
                "mode": "MODE7",
                "nchan": 32768,
                "valonFreq": 800,
                "if3": 300,
                "filter_bw": 950,
                "min_blank": .002621
            },
            (100, "medium-low", 1): {
                "res": 1.5,
                "min_int": .019661,
                "mode": "MODE8",
                "nchan": 65536,
                "valonFreq": 800,
                "if3": 300,
                "filter_bw": 950,
                "min_blank": .005243
            },
            (100, "medium", 1): {
                "res": 1.5,
                "min_int": .019661,
                "mode": "MODE8",
                "nchan": 65536,
                "valonFreq": 800,
                "if3": 300,
                "filter_bw": 950,
                "min_blank": .005243
            },
            (100, "medium-high", 1): {
                "res": .8,
                "min_int": .028836,
                "mode": "MODE9",
                "nchan": 131072,
                "valonFreq": 800,
                "if3": 300,
                "filter_bw": 950,
                "min_blank": .010486
            },
            (100, "high", 1): {
                "res": .8,
                "min_int": .028836,
                "mode": "MODE9",
                "nchan": 131072,
                "valonFreq": 800,
                "if3": 300,
                "filter_bw": 950,
                "min_blank": .010486
            },
            # modes 10,11,12,13,14
            (23.44, "low", 1): {
                "res": .7,
                "min_int": .005592,
                "mode": "MODE10",
                "nchan": 32768,
                "valonFreq": 1500,
                "if3": 250,
                "filter_bw": 950,
                "min_blank": .011185
            },
            (23.44, "medium-low", 1): {
                "res": .4,
                "min_int": .011185,
                "mode": "MODE11",
                "nchan": 65536,
                "valonFreq": 1500,
                "if3": 250,
                "filter_bw": 950,
                "min_blank": .022370
            },
            (23.44, "medium", 1): {
                "res": .2,
                "min_int": .027962,
                "mode": "MODE12",
                "nchan": 131072,
                "valonFreq": 1500,
                "if3": 250,
                "filter_bw": 950,
                "min_blank": .044739
            },
            (23.44, "medium-high", 1): {
                "res": .1,
                "min_int": .044739,
                "mode": "MODE13",
                "nchan": 262144,
                "valonFreq": 1500,
                "if3": 250,
                "filter_bw": 950,
                "min_blank": .089478
            },
            (23.44, "high", 1): {
                "res": .05,
                "min_int": .089478,
                "mode": "MODE14",
                "nchan": 524288,
                "valonFreq": 1500,
                "if3": 250,
                "filter_bw": 950,
                "min_blank": .178957
            },
            # modes 20,21,22,23,24
            # fs/4 bump at 375
            (23.44, "low", 8): {
                "res": 5.7,
                "min_int": .004893,
                "mode": "MODE20",
                "nchan": 4096,
                "valonFreq": 1500,
                "if3": 1500 / 2,
                "filter_bw": 1400,
                "min_blank": .001398
            },
            (23.44, "medium-low", 8): {
                "res": 2.9,
                "min_int": .009787,
                "mode": "MODE21",
                "nchan": 8192,
                "valonFreq": 1500,
                "if3": 1500 / 2,
                "filter_bw": 1400,
                "min_blank": .002796
            },
            (23.44, "medium", 8): {
                "res": 1.4,
                "min_int": .029360,
                "mode": "MODE22",
                "nchan": 16384,
                "valonFreq": 1500,
                "if3": 1500 / 2,
                "filter_bw": 1400,
                "min_blank": .005592
            },
            (23.44, "medium-high", 8): {
                "res": .7,
                "min_int": .039147,
                "mode": "MODE23",
                "nchan": 32768,
                "valonFreq": 1500,
                "if3": 1500 / 2,
                "filter_bw": 1400,
                "min_blank": .011185
            },
            (23.44, "high", 8): {
                "res": .4,
                "min_int": .072701,
                "mode": "MODE24",
                "nchan": 65536,
                "valonFreq": 1500,
                "if3": 1500 / 2,
                "filter_bw": 1400,
                "min_blank": .022370
            },

            # modes 15,16,17,18,19
            (11.72, "low", 1): {
                "res": .4,
                "min_int": .005592,
                "mode": "MODE15",
                "nchan": 32768,
                "valonFreq": 750,
                "if3": 250,
                "filter_bw": 950,
                "min_blank": .022370
            },
            (11.72, "medium-low", 1): {
                "res": .2,
                "min_int": .011185,
                "mode": "MODE16",
                "nchan": 65536,
                "valonFreq": 750,
                "if3": 250,
                "filter_bw": 950,
                "min_blank": .044739
            },
            (11.72, "medium", 1): {
                "res": .1,
                "min_int": .033554,
                "mode": "MODE17",
                "nchan": 131072,
                "valonFreq": 750,
                "if3": 250,
                "filter_bw": 950,
                "min_blank": .089478
            },
            (11.72, "medium-high", 1): {
                "res": .05,
                "min_int": .044739,
                "mode": "MODE18",
                "nchan": 262144,
                "valonFreq": 750,
                "if3": 250,
                "filter_bw": 950,
                "min_blank": .178957
            },
            (11.72, "high", 1): {
                "res": .02,
                "min_int": .089478,
                "mode": "MODE19",
                "nchan": 524288,
                "valonFreq": 750,
                "if3": 250,
                "filter_bw": 950,
                "min_blank": .357914
            },

            # mode 25,26,27,28,29
            # fs/4 bump at 270
            (16.9, "low", 8): {
                "res": 4.1,
                "min_int": .006816,
                "mode": "MODE25",
                "nchan": 4096,
                "valonFreq": 1080,
                "if3": 1080 / 2,
                "filter_bw": 950,
                "min_blank": .002097 # FIXME: I have .001942 for mode 25 - JJB
            },
            (16.9, "medium-low", 8): {
                "res": 2.1,
                "min_int": .013631,
                "mode": "MODE26",
                "nchan": 8192,
                "valonFreq": 1080,
                "if3": 1080 / 2,
                "filter_bw": 950,
                "min_blank": .004194 # FIXME: I have 0.003884 for mode 26 - JJB
            },
            (16.9, "medium", 8): {
                "res": 1.0,
                "min_int": .039846,
                "mode": "MODE27",
                "nchan": 16384,
                "valonFreq": 1080,
                "if3": 1080 / 2,
                "filter_bw": 950,
                "min_blank": .008389 # FIXME: I have 0.007767 for mode 27 - JJB
            },
            (16.9, "medium-high", 8): {
                "res": .5,
                "min_int": .054526,
                "mode": "MODE28",
                "nchan": 32768,
                "valonFreq": 1080,
                "if3": 1080 / 2,
                "filter_bw": 950,
                "min_blank": .016777 # FIXME: I have 0.15534 for mode 28 - JJB
            },
            (16.9, "high", 8): {
                "res": .26,
                "min_int": .096469,
                "mode": "MODE29",
                "nchan": 65536,
                "valonFreq": 1080,
                "if3": 1080 / 2,
                "filter_bw": 950,
                "min_blank": .033554 # FIXME: I have 0.031069 for mode 29 - JJB
            },

            # Pulsar modes
            (800, "hypolowest", "coherent"): {
                "res": 12500.0,
                "min_int": 1.600e-07,
                "mode": "MODEc0800x0032",
                "nchan": 32,
                "valonFreq": 800,
                "if3": 400,
                "filter_bw": 950,
                "min_blank": 0
            },
            (800, "lowest", "coherent"): {
                "res": 12500.0,
                "min_int": 1.600e-07,
                "mode": "MODEc0800x0064",
                "nchan": 64,
                "valonFreq": 800,
                "if3": 400,
                "filter_bw": 950,
                "min_blank": 0
            },
            (800, "very-low", "coherent"): {
                "res": 6250.0,
                "min_int": 3.200e-07,
                "mode": "MODEc0800x0128",
                "nchan": 128,
                "valonFreq": 800,
                "if3": 400,
                "filter_bw": 950,
                "min_blank": 0
            },
            (800, "low", "coherent"): {
                "res": 3125.0,
                "min_int": 6.400e-07,
                "mode": "MODEc0800x0256",
                "nchan": 256,
                "valonFreq": 800,
                "if3": 400,
                "filter_bw": 950,
                "min_blank": 0
            },
            (800, "medium-low", "coherent"): {
                "res": 1562.5,
                "min_int": 1.280e-06,
                "mode": "MODEc0800x0512",
                "nchan": 512,
                "valonFreq": 800,
                "if3": 400,
                "filter_bw": 950,
                "min_blank": 0
            },
            (800, "medium-high", "coherent"): {
                "res": 781.25,
                "min_int": 2.560e-06,
                "mode": "MODEc0800x1024",
                "nchan": 1024,
                "valonFreq": 800,
                "if3": 400,
                "filter_bw": 950,
                "min_blank": 0
            },
            (800, "high", "coherent"): {
                "res": 390.625,
                "min_int": 5.120e-06,
                "mode": "MODEc0800x2048",
                "nchan": 2048,
                "valonFreq": 800,
                "if3": 400,
                "filter_bw": 950,
                "min_blank": 0
            },
            (800, "very-high", "coherent"): {
                "res": 195.3125,
                "min_int": 1.024e-05,
                "mode": "MODEc0800x4096",
                "nchan": 4096,
                "valonFreq": 800,
                "if3": 400,
                "filter_bw": 950,
                "min_blank": 0
            },
            (800, "highest", "coherent"): {
                "res": 97.65625,
                "min_int": 2.048e-05,
                "mode": "MODEc0800x8192",
                "nchan": 8192,
                "valonFreq": 800,
                "if3": 400,
                "filter_bw": 950,
                "min_blank": 0
            },
            (800, "hypolowest", "incoherent"): {
                "res": 12500.0,
                "min_int": 1.600e-07,
                "mode": "MODEi0800x0032",
                "nchan": 32,
                "valonFreq": 800,
                "if3": 400,
                "filter_bw": 950,
                "min_blank": 0
            },
            (800, "lowest", "incoherent"): {
                "res": 12500.0,
                "min_int": 1.600e-07,
                "mode": "MODEi0800x0064",
                "nchan": 64,
                "valonFreq": 800,
                "if3": 400,
                "filter_bw": 950,
                "min_blank": 0
            },
            (800, "very-low", "incoherent"): {
                "res": 6250.0,
                "min_int": 3.200e-07,
                "mode": "MODEi0800x0128",
                "nchan": 128,
                "valonFreq": 800,
                "if3": 400,
                "filter_bw": 950,
                "min_blank": 0
            },
            (800, "low", "incoherent"): {
                "res": 3125.0,
                "min_int": 6.400e-07,
                "mode": "MODEi0800x0256",
                "nchan": 256,
                "valonFreq": 800,
                "if3": 400,
                "filter_bw": 950,
                "min_blank": 0
            },
            (800, "medium-low", "incoherent"): {
                "res": 1562.5,
                "min_int": 1.280e-06,
                "mode": "MODEi0800x0512",
                "nchan": 512,
                "valonFreq": 800,
                "if3": 400,
                "filter_bw": 950,
                "min_blank": 0
            },
            (800, "medium-high", "incoherent"): {
                "res": 781.25,
                "min_int": 2.560e-06,
                "mode": "MODEi0800x1024",
                "nchan": 1024,
                "valonFreq": 800,
                "if3": 400,
                "filter_bw": 950,
                "min_blank": 0
            },
            (800, "high", "incoherent"): {
                "res": 390.625,
                "min_int": 5.120e-06,
                "mode": "MODEi0800x2048",
                "nchan": 2048,
                "valonFreq": 800,
                "if3": 400,
                "filter_bw": 950,
                "min_blank": 0
            },
            (800, "very-high", "incoherent"): {
                "res": 195.3125,
                "min_int": 1.024e-05,
                "mode": "MODEi0800x4096",
                "nchan": 4096,
                "valonFreq": 800,
                "if3": 400,
                "filter_bw": 950,
                "min_blank": 0
            },
            (800, "highest", "incoherent"): {
                "res": 97.65625,
                "min_int": 2.048e-05,
                "mode": "MODEi0800x8192",
                "nchan": 8192,
                "valonFreq": 800,
                "if3": 400,
                "filter_bw": 950,
                "min_blank": 0
            },
            (1500, "hypolowest", "coherent"): {
                "res": 23437.5,
                "min_int": 8.5333e-08,
                "mode": "MODEc1500x0032",
                "nchan": 32,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": 0
            },
            (1500, "lowest", "coherent"): {
                "res": 23437.5,
                "min_int": 8.5333e-08,
                "mode": "MODEc1500x0064",
                "nchan": 64,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": 0
            },
            (1500, "very-low", "coherent"): {
                "res": 11718.75,
                "min_int": 1.7066e-07,
                "mode": "MODEc1500x0128",
                "nchan": 128,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": 0
            },
            (1500, "low", "coherent"): {
                "res": 5859.375,
                "min_int": 3.4133e-07,
                "mode": "MODEc1500x0256",
                "nchan": 256,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": 0
            },
            (1500, "medium-low", "coherent"): {
                "res": 2929.6875,
                "min_int": 6.8266e-07,
                "mode": "MODEc1500x0512",
                "nchan": 512,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": 0
            },
            (1500, "medium-high", "coherent"): {
                "res": 1464.84375,
                "min_int": 1.3653e-06,
                "mode": "MODEc1500x1024",
                "nchan": 1024,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": 0
            },
            (1500, "high", "coherent"): {
                "res": 732.421875,
                "min_int": 2.7306e-06,
                "mode": "MODEc1500x2048",
                "nchan": 2048,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": 0
            },
            (1500, "very-high", "coherent"): {
                "res": 366.2109375,
                "min_int": 5.4613e-06,
                "mode": "MODEc1500x4096",
                "nchan": 4096,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": 0
            },
            (1500, "highest", "coherent"): {
                "res": 183.10546875,
                "min_int": 1.0922e-05,
                "mode": "MODEc1500x8192",
                "nchan": 8192,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": 0
            },
            (1500, "hypolowest", "incoherent"): {
                "res": 23437.5,
                "min_int": 8.5333e-08,
                "mode": "MODEi1500x0032",
                "nchan": 32,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": 0
            },
            (1500, "lowest", "incoherent"): {
                "res": 23437.5,
                "min_int": 8.5333e-08,
                "mode": "MODEi1500x0064",
                "nchan": 64,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": 0
            },
            (1500, "very-low", "incoherent"): {
                "res": 11718.75,
                "min_int": 1.7066e-07,
                "mode": "MODEi1500x0128",
                "nchan": 128,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": 0
            },
            (1500, "low", "incoherent"): {
                "res": 5859.375,
                "min_int": 3.4133e-07,
                "mode": "MODEi1500x0256",
                "nchan": 256,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": 0
            },
            (1500, "medium-low", "incoherent"): {
                "res": 2929.6875,
                "min_int": 6.8266e-07,
                "mode": "MODEi1500x0512",
                "nchan": 512,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": 0
            },
            (1500, "medium-high", "incoherent"): {
                "res": 1464.84375,
                "min_int": 1.3653e-06,
                "mode": "MODEi1500x1024",
                "nchan": 1024,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": 0
            },
            (1500, "high", "incoherent"): {
                "res": 732.421875,
                "min_int": 2.7306e-06,
                "mode": "MODEi1500x2048",
                "nchan": 2048,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": 0
            },
            (1500, "very-high", "incoherent"): {
                "res": 366.2109375,
                "min_int": 5.4613e-06,
                "mode": "MODEi1500x4096",
                "nchan": 4096,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": 0
            },
            (1500, "highest", "incoherent"): {
                "res": 183.10546875,
                "min_int": 1.0922e-05,
                "mode": "MODEi1500x8192",
                "nchan": 8192,
                "valonFreq": 1500,
                "if3": 750,
                "filter_bw": 1400,
                "min_blank": 0
            },
            # New VPM 100MHz LBW entries
            # NOTE: the min_int values are probably wrong - but they are calculated values anyway
            # NOTE: since there are fewer LBW modes, things like 'hyper-low' etc don't exist
            (100, "lowest", "incoherent"): {
                "res": 195.3125,
                "min_int": 3.4133e-07,
                "mode": "MODEi0100x0512",
                "nchan": 512,
                "valonFreq": 800,
                "if3": 350,
                "filter_bw": 950,
                "min_blank": 0,
                "polnmode" : "full_stokes"
            },
            (100, "medium-low", "incoherent"): {
                "res": 97.65625,
                "min_int": 3.4133e-07,
                "mode": "MODEi0100x1024",
                "nchan": 1024,
                "valonFreq": 800,
                "if3": 350,
                "filter_bw": 950,
                "min_blank": 0,
                "polnmode": "full_stokes"
            },
            (100, "medium-high", "incoherent"): {
                "res": 48.828125,
                "min_int": 3.4133e-07,
                "mode": "MODEi0100x2048",
                "nchan": 2048,
                "valonFreq": 800,
                "if3": 350,
                "filter_bw": 950,
                "min_blank": 0,
                "polnmode": "full_stokes"
            },
            (100, "very-high", "incoherent"): {
                "res": 24.4140625,
                "min_int": 3.4133e-07,
                "mode": "MODEi0100x4096",
                "nchan": 4096,
                "valonFreq": 800,
                "if3": 350,
                "filter_bw": 950,
                "min_blank": 0,
                "polnmode": "full_stokes"
            },
            (100, "highest", "incoherent"): {
                "res": 24.4140625/2.,
                "min_int": 3.4133e-07,
                "mode": "MODEi0100x8192",
                "nchan": 8192,
                "valonFreq": 800,
                "if3": 350,
                "filter_bw": 950,
                "min_blank": 0,
                "polnmode": "full_stokes"
            },
            # 200MHz Incoherent modes
            (200, "lowest", "incoherent"): {
                "res": 195.3125,
                "min_int": 3.4133e-07,
                "mode": "MODEi0200x1024",
                "nchan": 1024,
                "valonFreq": 800,
                "if3": 300,
                "filter_bw": 950,
                "min_blank": 0,
                "polnmode": "full_stokes"
            },
            (200, "medium-low", "incoherent"): {
                "res": 97.65625,
                "min_int": 3.4133e-07,
                "mode": "MODEi0200x2048",
                "nchan": 2048,
                "valonFreq": 800,
                "if3": 300,
                "filter_bw": 950,
                "min_blank": 0,
                "polnmode": "full_stokes"
            },
            (200, "medium-high", "incoherent"): {
                # only_i mode
                "res": 48.828125,
                "min_int": 3.4133e-07,
                "mode": "MODEi0200x4096",
                "nchan": 4096,
                "valonFreq": 800,
                "if3": 300,
                "filter_bw": 950,
                "min_blank": 0,
                "polnmode": "full_stokes"
            },
            (200, "highest", "incoherent"): {
                # Note: only_i mode
                "res": 24.414065,
                "min_int": 3.4133e-07,
                "mode": "MODEi0200x8192",
                "nchan": 8192,
                "valonFreq": 800,
                "if3": 300,
                "filter_bw": 950,
                "min_blank": 0,
                "polnmode": "full_stokes"
            },
            # 100MHz Coherent Modes
            (100, "lowest", "coherent"): {
                "res": 781.25,
                "min_int": 2.560e-06,
                "mode": "MODEc0100x0064",
                "nchan": 64,
                "valonFreq": 800,
                "if3": 350,
                "filter_bw": 950,
                "min_blank": 0
            },
            (100, "medium-low", "coherent"): {
                "res": 390.625,
                "min_int": 5.120e-06,
                "mode": "MODEc0100x0128",
                "nchan": 128,
                "valonFreq": 800,
                "if3": 350,
                "filter_bw": 950,
                "min_blank": 0
            },
            (100, "medium-high", "coherent"): {
                "res": 195.3125,
                "min_int": 1.024e-05,
                "mode": "MODEc0100x0256",
                "nchan": 256,
                "valonFreq": 800,
                "if3": 350,
                "filter_bw": 950,
                "min_blank": 0
            },
            (100, "highest", "coherent"): {
                "res": 97.65625,
                "min_int": 2.048e-05,
                "mode": "MODEc0100x0512",
                "nchan": 512,
                "valonFreq": 800,
                "if3": 350,
                "filter_bw": 950,
                "min_blank": 0
            },
            # 200MHz Coherent Modes
            (200, "hypolowest", "coherent"): {
                "res": 781.25,
                "min_int": 2.560e-06,
                "mode": "MODEc0200x0064",
                "nchan": 64,
                "valonFreq": 800,
                "if3": 300,
                "filter_bw": 950,
                "min_blank": 0
            },
            (200, "lowest", "coherent"): {
                "res": 781.25,
                "min_int": 2.560e-06,
                "mode": "MODEc0200x0128",
                "nchan": 128,
                "valonFreq": 800,
                "if3": 300,
                "filter_bw": 950,
                "min_blank": 0
            },
            (200, "medium-low", "coherent"): {
                "res": 390.625,
                "min_int": 5.120e-06,
                "mode": "MODEc0200x0256",
                "nchan": 256,
                "valonFreq": 800,
                "if3": 300,
                "filter_bw": 950,
                "min_blank": 0
            },
            (200, "medium-high", "coherent"): {
                "res": 195.3125,
                "min_int": 1.024e-05,
                "mode": "MODEc0200x0512",
                "nchan": 512,
                "valonFreq": 800,
                "if3": 300,
                "filter_bw": 950,
                "min_blank": 0
            },
            (200, "highest", "coherent"): {
                "res": 97.65625,
                "min_int": 2.048e-05,
                "mode": "MODEc0200x1024",
                "nchan": 1024,
                "valonFreq": 800,
                "if3": 300,
                "filter_bw": 950,
                "min_blank": 0
            },
    }

VEGAS_MODES = VegasModeData()

ALLOWED_RF_KEYWORDS = (
    "restfreq",
    "bandwidth",
    "tint",
    "vpol",
    "bank",
    "deltafreq",
    "subband",
    "beam",
    "nchan"
)

VEGAS_PORT_TO_BANK = {
    "J1": "VEGASBankA",
    "J2": "VEGASBankA",
    "J3": "VEGASBankB",
    "J4": "VEGASBankB",
    "J5": "VEGASBankC",
    "J6": "VEGASBankC",
    "J7": "VEGASBankD",
    "J8": "VEGASBankD",
    "J9": "VEGASBankE",
    "J10": "VEGASBankE",
    "J11": "VEGASBankF",
    "J12": "VEGASBankF",
    "J13": "VEGASBankG",
    "J14": "VEGASBankG",
    "J15": "VEGASBankH",
    "J16": "VEGASBankH"
}
# IFPATH defs --------

KHZ_RESTABLE = [
    1465.0,
    92.0,
    61.0,
    5.7,
    2.9,
    1.4,
    3.1,
    1.5,
    0.8,
    0.7,
    0.4,
    0.2,
    0.1,
    0.05,
    5.7,
    2.9,
    1.4,
    0.7,
    0.4,
    0.2,
    0.1,
    0.05,
    0.02,
    3.8,
    1.9,
    0.95,
    0.48,
    0.24
]

RCVRS_NEEDING_PRUNING = (
    "Rcvr_342",
    "Rcvr_450",
    "Rcvr_600",
    "Rcvr_800",
    "Rcvr_1070",
    "Rcvr18_22",
    "Rcvr22_26",
    "Rcvr18_26"
)

BEAMS_NEEDING_PRUNING = (
    "Rcvr18_22",
    "Rcvr22_26",
    "Rcvr18_26",
    "Rcvr40_52"
)

NEW_ALGM_BACKENDS = [
    "VEGAS",
    "GUPPI",
    "JPL_RSR",
    "LLRADAR",
    "VLBA_DAR"
]

# Freq defs ----------

# each receiver has a mixer in it, some have multipliers too
LO1MULTIPLIER = {
    "Rcvr22_26": 1,
    "Rcvr18_22": 1,
    "Rcvr12_18": 1,
    "Rcvr1_2": 1,
    "Rcvr26_40": 3,
    "Rcvr2_3": 1,
    "Rcvr40_52": 4,
    "Rcvr4_6": 1,
    "Rcvr8_10": 1,
    "Rcvr_342": 1,
    "Rcvr_450": 1,
    "Rcvr_600": 1,
    "Rcvr_800": 1,
    "Rcvr_1070": 1,
    "NoiseSource": 1,
    "Holography": 1,
    "Rcvr68_92": 4,
    "RcvrArray18_26": 1,
    "RcvrArray75_115": 8
}

# maps the receiver to its sideband type.
RCVR_SIDEBAND = {
    "Rcvr1_2": -1,
    "Rcvr_342": -1,
    "Rcvr_450": -1,
    "Rcvr_600": -1,
    "Rcvr_800": -1,
    "Rcvr2_3": -1,
    "Rcvr4_6": -1,
    "Rcvr8_10": -1,
    "RcvrPF_1": -1,
    "Rcvr_1070": -1,
    "RcvrPF_2": -1,
    "Rcvr26_40": 1,
    "Rcvr18_22": 1,
    "Rcvr22_26": 1,
    "Rcvr12_18": 1,
    "Rcvr40_52": 1,
    "NoiseSource": 1,
    "Holography": 1,
    "Rcvr68_92": 1,
    "RcvrArray18_26": -1,
    "RcvrArray75_115": 1
}

# map intermediate frequency 3 associated with a backend and (in some
# cases) the bandwidth in use
IF3 = {
    "ACS-12.5MHz": 468.75,
    "ACS-50MHz": 425,
    "ACS-50.0MHz": 425,
    "ACS-200MHz": 900,
    "ACS-200.0MHz": 900,
    "ACS-100MHz": 850,
    "ACS-100.0MHz": 850,
    "ACS-800MHz": 1200,
    "ACS-800.0MHz": 1200,
    "VLBA_DAR": 750,
    "Radar": 720,
    "LLRADAR": 425,
    "JPL_RSR": 315,
    "NoiseSource": 100,
    "DCR": 100,
    "CCB": 100,
    "VEGAS": 775
}

lower_sideband_rcvrs = (
    "Rcvr1_2",
    "Rcvr_342",
    "Rcvr_450",
    "Rcvr_600",
    "Rcvr_800",
    "RcvrPF_1",
    "Rcvr_1070",
    "RcvrPF_2",
    "Rcvr2_3",
    "Rcvr4_6",
    "Rcvr8_10",
    "NoiseSource_2.75_3.25",
    "NoiseSource_1_8"
)

upper_sideband_rcvrs = (
    "Rcvr18_22",
    "Rcvr22_26",
    "Rcvr12_18"
)

# phase table and switching defs ---------------

PHASE_TABLE_PARAMS = (
    "phase_start,1",
    "phase_start,2",
    "phase_start,3",
    "phase_start,4",
    "cal_state,1",
    "cal_state,2",
    "cal_state,3",
    "cal_state,4",
    "sig_ref_state,1",
    "sig_ref_state,2",
    "sig_ref_state,3",
    "sig_ref_state,4",
    "blanking,1",
    "blanking,2",
    "blanking,3",
    "blanking,4",
    "switching_signals_master",
    "switch_period"
)

SWTYPES = (
    "none",
    "fsw",
    "bsw",
    "psw",
    "tsw"
)

BLANKING = {
    "tp": 2,
    "tp_nocal": 1,
    "sp": 4,
    "sp_nocal": 2
}

# backend defs --------
AFR_BACKENDS = (
    "DCR_AF",
    "LLRADAR",
    "GUPPI"
)

NO_CR_BACKENDS = (
    "DCR",
    "DCR_PF",
    "CCB"
)

SC_BACKENDS = (
    "DCR",
    "DCR_AF",
    "CCB",
    "GUPPI",
    "VEGAS"
)

DCR_SSS_BACKENDS = (
    "LLRADAR",
    "CCB",
    "GUPPI",
    "DCR_AF"
)

SSS_BACKENDS = (
    "VLBA_DAR",
    "DCR",
    "VEGAS"
)

BACKENDS = (
    "VLBA_DAR",
    "Radar",
    "DCR",
    "DCR_AF",
    "LLRADAR",
    "VEGAS",
    "JPL_RSR",
    "CCB",
    "GUPPI",
    "Holography",
    "MBA15"
)

PULSARBACKENDS = (
    "VLBA_DAR",
    "GUPPI",
    "VEGAS"
)

# receiver defs -------------

RCVR_FREQS = {
    "Rcvr1_2": (1100, 1752),
    "Rcvr2_3": (1714, 2740),
    "Rcvr8_10": (7700, 10400),
    "Rcvr_342": (270, 420),
    "Rcvr_450": (360, 540),
    "Rcvr_600": (450, 710),
    "Rcvr_800": (660, 940),
    "Rcvr_1070": (910, 1230),
    "RcvrPF_2": (910, 1230),
    "Rcvr4_6": (3900, 8000),
    "Rcvr12_18": (11800, 15600),
    "Rcvr26_40": (26000, 40000),
    "Rcvr40_52": (40000, 52000),
    "Rcvr18_22": (17800, 22600),
    "Rcvr22_26": (21800, 26600),
    "NoiseSource": (0, 100000),
    "RcvrArray18_26": (17800, 27500),
    "Holography": (0, 100000),
    "Rcvr68_92": (67000, 93300),
    "RcvrArray75_115": (75000, 1160000)
}

TUNING_FREQ = {
    "Rcvr1_2": 1,
    "Rcvr18_26": 0,
    "Rcvr2_3": 1,
    "Rcvr8_10": 0,
    "Rcvr_342": 1,
    "Rcvr_450": 1,
    "Rcvr_600": 1,
    "Rcvr_800": 1,
    "Rcvr4_6": 1,
    "Rcvr12_18": 0,
    "Rcvr40_52": 0,
    "RcvrPF_2": 1,
    "RcvrPF_1": 1,
    "Rcvr18_22": 0,
    "Rcvr22_26": 0,
    "Rcvr26_40": 0,
    "RcvrArray18_26": 0,
    "NoiseSource": 0,
    "Holography": 0,
    "Rcvr68_92": 0,
    "RcvrArray75_115": 0
}

# key = receivers that have a poloarization switch
# first value = receiver manager parameter name associated with polarization
# second value = the prefix to use when setting the parameter value.
POL = {
    "Rcvr1_2": ("polarizationSelect", "pol"),
    "Rcvr2_3": ("polarizationSelect", "pol"),
    "Rcvr_342": ("lowBandPolarizationSelect", ""),
    "Rcvr_450": ("lowBandPolarizationSelect", ""),
    "Rcvr_600": ("highBandPolarizationSelect", ""),
    "Rcvr_800": ("highBandPolarizationSelect", ""),
    "Rcvr4_6": ("polarizationSelect", "pol"),
    "Rcvr_1070": ("polarizationSelect", "")
}

BW_XFER = {
    "Rcvr12_18": {
        "thru": (
            ("xferSwR", "tsThru"),
            ("xferSwL", "tsThru"),
            ("xferState", "ctlMcb")
        ),
        "cross": (
            ("xferSwR", "tsCrossed"),
            ("xferSwL", "tsCrossed"),
            ("xferState", "ctlMcb")
        ),
        "ext": (
            ("xferSwR", "tsThru"),
            ("xferSwL", "tsThru"),
            ("xferState", "ctlMcb")
        )
    },
    "Rcvr18_26":
    {
        "thru": (
            ("rabXferSw", "tsThru"),
            ("labXferSw", "tsThru"),
            ("rcdXferSw", "tsThru"),
            ("lcdXferSw", "tsThru"),
            ("xferState", "ctlMcb")
        ),
        "cross": (
            ("rabXferSw", "tsCrossed"),
            ("labXferSw", "tsCrossed"),
            ("rcdXferSw", "tsCrossed"),
            ("lcdXferSw", "tsCrossed"),
            ("xferState", "ctlMcb")
        ),
        "ext": (
            ("rabXferSw", "tsThru"),
            ("labXferSw", "tsThru"),
            ("rcdXferSw", "tsThru"),
            ("lcdXferSw", "tsThru"),
            ("xferState", "ctlExt")
        )
    },
    "Rcvr22_26":
    {
        "thru": (
            ("rabXferSw", "tsThru"),
            ("labXferSw", "tsThru"),
            ("rcdXferSw", "tsThru"),
            ("lcdXferSw", "tsThru"),
            ("xferState", "ctlMcb")
        ),
        "cross": (
            ("rabXferSw", "tsCrossed"),
            ("labXferSw", "tsCrossed"),
            ("rcdXferSw", "tsCrossed"),
            ("lcdXferSw", "tsCrossed"),
            ("xferState", "ctlMcb")
        ),
        "ext": (
            ("rabXferSw", "tsThru"),
            ("labXferSw", "tsThru"),
            ("rcdXferSw", "tsThru"),
            ("lcdXferSw", "tsThru"),
            ("xferState", "ctlExt")
        )
    },
    "Rcvr18_22":
    {
        "thru": (
            ("rabXferSw", "tsThru"),
            ("labXferSw", "tsThru"),
            ("rcdXferSw", "tsThru"),
            ("lcdXferSw", "tsThru"),
            ("xferState", "ctlMcb")
        ),
        "cross": (
            ("rabXferSw", "tsCrossed"),
            ("labXferSw", "tsCrossed"),
            ("rcdXferSw", "tsCrossed"),
            ("lcdXferSw", "tsCrossed"),
            ("xferState", "ctlMcb")
        ),
        "ext": (
            ("rabXferSw", "tsThru"),
            ("labXferSw", "tsThru"),
            ("rcdXferSw", "tsThru"),
            ("lcdXferSw", "tsThru"),
            ("xferState", "ctlExt")
        ),
    },
    "Rcvr26_40":
    {
        "thru": (
            ("s1PhaseSwitch", "swOff"),
            ("d1PhaseSwitch", "swOff"),
            ("s2PhaseSwitch", "swOff"),
            ("d2PhaseSwitch", "swOff"),
            ("sigRefs1PhaseSwitch", "swOff"),
            ("sigRefs2PhaseSwitch", "swOff"),
            ("sigRefd1PhaseSwitch", "swOff"),
            ("sigRefd2PhaseSwitch", "swOff"),
            ("phaseModState", "ctlMcb")
        ),
        "cross": (
            ("s1PhaseSwitch", "swOn"),
            ("d1PhaseSwitch", "swOff"),
            ("s2PhaseSwitch", "swOn"),
            ("d2PhaseSwitch", "swOff"),
            ("sigRefs1PhaseSwitch", "swOff"),
            ("sigRefs2PhaseSwitch", "swOff"),
            ("sigRefd1PhaseSwitch", "swOff"),
            ("sigRefd2PhaseSwitch", "swOff"),
            ("phaseModState", "ctlMcb")
        ),
        "ext": (
            ("s1PhaseSwitch", "swOff"),
            ("d1PhaseSwitch", "swOff"),
            ("s2PhaseSwitch", "swOff"),
            ("d2PhaseSwitch", "swOff"),
            ("sigRefs1PhaseSwitch", "swOff"),
            ("sigRefs2PhaseSwitch", "swOff"),
            ("sigRefd1PhaseSwitch", "swOn"),
            ("sigRefd2PhaseSwitch", "swOn"),
            ("phaseModState", "ctlExt")
        )
    }
}


XFERSWITCH = {
    "Rcvr1_2": {
        "ext": (
            ("xferSwCtlMode", "ctlExt"),
        ),
        "thru": (
            ("xferSwCtlMode", "ctlMcb"),
            ("xferSwitch", "tsThru")
        ),
        "cross": (
            ("xferSwCtlMode", "ctlMcb"),
            ("xferSwitch", "tsCrossed")
        )
    },
    "Rcvr2_3": {
        "ext": (
            ("xferSwCtlMode", "ctlExt"),
        ),
        "thru": (
            ("xferSwCtlMode", "ctlMcb"),
            ("xferSwitch", "tsThru")
        ),
        "cross": (
            ("xferSwCtlMode", "ctlMcb"),
            ("xferSwitch", "tsCrossed")
        )
    },
    "Rcvr8_10": {
        "ext": (
            ("xferSwCtlMode", "ctlExt"),
        ),
        "thru": (
            ("xferSwCtlMode", "ctlMcb"),
            ("xferSwitch", "tsThru")
        ),
        "cross": (
            ("xferSwCtlMode", "ctlMcb"),
            ("xferSwitch", "tsCrossed")
        )
    }
}


RCVR_IF_NOMINAL = {
    "Rcvr1_2": 3000,
    "Rcvr_342": 1080,
    "Rcvr_450": 1080,
    "Rcvr_600": 1080,
    "Rcvr_800": 1080,
    "RcvrPF_1": 1080,
    "Rcvr2_3": 6000,
    "Rcvr4_6": 3000,
    "Rcvr8_10": 3000,
    "Rcvr18_22": 6000,
    "Rcvr22_26": 6000,
    "Rcvr18_26": 6000,
    "Rcvr12_18": 3000,
    "Rcvr_1070": 1500,
    "RcvrPF_2": 1500,
    "RcvrArray18_26": 6800,
    "RcvrArray18_26_LO": 2100,
    "Rcvr40_52": 6000,
    "NoiseSource_2.75_3.25": 3000,
    "Rcvr26_40": 6000,
    "NoiseSource_1_8": 4500,
    "NoiseSource": 3000,
    "Holography": 1250,
    "Rcvr68_92": 6000,
    "RcvrArray75_115": 1525
}

# rcvr: (filter names), (filter min, filter max, switch setting to select
# filter, type)
FILTERS = {
    "Rcvr1_2": (
        ("leftIfFilterSwitch", "rightIfFilterSwitch"), (
            (1300, 1450, "3"),
            (1100, 1450, "4"),
            (1600, 1750, "2"),
            (1100, 1800, "1")
        ),
        1
    ),
    "Rcvr2_3": (
        ("leftIfFilterSwitch", "rightIfFilterSwitch"), (
            (2100, 2400, "3"),
            (1680, 2650, "2")
        ),
        1
    ),
    "Rcvr8_10": (
        ("leftIfFilterSwitch", "rightIfFilterSwitch"), (
            (2750, 3250, "narrowband"),
            (1800, 4200, "wideband")
        ),
        0
    ),
    "Rcvr12_18": (
        ("laIfFilterSwitch", "raIfFilterSwitch"), (
            (2750, 3250, "1"),
            (1250, 4750, "0")
        ),
        0
    ),
    "Rcvr_342": (
        ("ifChannelCFilterBank", "ifChannelDFilterBank"), (
            (1070, 1090, "1"),
            (1060, 1100, "2"),
            (1040, 1120, "3"),
            (960, 1200, "4")
        ),
        0
    ),
    "Rcvr_450": (
        ("ifChannelCFilterBank", "ifChannelDFilterBank"), (
            (1070, 1090, "1"),
            (1060, 1100, "2"),
            (1040, 1120, "3"),
            (960, 1200, "4")
        ),
        0
    ),
    "Rcvr_600": (
        ("ifChannelAFilterBank", "ifChannelBFilterBank"), (
            (1070, 1090, "1"),
            (1060, 1100, "2"),
            (1040, 1120, "3"),
            (960, 1200, "4")
        ),
        0
    ),
    "Rcvr_800": (
        ("ifChannelAFilterBank", "ifChannelBFilterBank"), (
            (1070, 1090, "1"),
            (1060, 1100, "2"),
            (1040, 1120, "3"),
            (960, 1200, "4")
        ),
        0
    ),
    "Rcvr_1070": (
        ("ifChannelXFilterBank", "ifChannelYFilterBank"), (
            (590, 610, "1"),
            (580, 620, "2"),
            (560, 640, "3"),
            (480, 720, "4")
        ),
        0
    )
    # The values used are in the IF plane i.e 900 Mhz is added because of the
    # mixer, the actual filter values are commented out below::: Adjustments no
    # longer needed, done in freqCalc
    # ((1490,1510,"1"), (1480,1520,"2"),
    #  (1460,1540,"3"), (1380,1620,"4")), 0)
}

NOISECAL_HI = {
    "off": (
        ("calState", "ctlMcb"),
        ("noiseSourceSwR", "swOff"),
        ("noiseSourceSwL", "swOff")
    ),
    "on-mcb": (
        ("calState", "ctlMcb"),
        ("noiseSourceSwR", "swOn"),
        ("noiseSourceSwL", "swOn")
    ),
    "on-ext": (
        ("calState", "ctlExt"),
        ("noiseSourceSwR", "swOn"),
        ("noiseSourceSwL", "swOn")
    ),
    "lo-mcb": (
        ("calState", "ctlMcb"),
        ("noiseSourceSwR", "swOn"),
        ("noiseSourceSwL", "swOn")
    ),
    "hi-mcb": (
        ("calState", "ctlMcb"),
        ("noiseSourceSwR", "swOn"),
        ("noiseSourceSwL", "swOn")
    ),
    "lo-ext": (
        ("calState", "ctlExt"),
        ("noiseSourceSwR", "swOn"),
        ("noiseSourceSwL", "swOn")
    ),

    "hi-ext": (
        ("calState", "ctlExt"),
        ("noiseSourceSwR", "swOn"),
        ("noiseSourceSwL", "swOn")
    ),
    "lo": (
        ("calState", "ctlExt"),
        ("noiseSourceSwR", "swOn"),
        ("noiseSourceSwL", "swOn")
    ),

    "hi": (
        ("calState", "ctlExt"),
        ("noiseSourceSwR", "swOn"),
        ("noiseSourceSwL", "swOn")
    )
}

NOISECAL_LO = {
    "off": (
        ("xlExtToMCBCtrlSel", "ctlMcb"),
        ("yrExtToMCBCtrlSel", "ctlMcb"),
        ("xlCPUNoiseSwCtrl", "swOff"),
        ("yrCPUNoiseSwCtrl", "swOff"),
        ("loOrHiCalSel", "lowCal")),
    "on-mcb": (
        ("xlExtToMCBCtrlSel", "ctlMcb"),
        ("yrExtToMCBCtrlSel", "ctlMcb"),
        ("xlCPUNoiseSwCtrl", "swOn"),
        ("yrCPUNoiseSwCtrl", "swOn"),
        ("loOrHiCalSel", "lowCal")),
    "on-ext": (
        ("xlExtToMCBCtrlSel", "ctlExt"),
        ("yrExtToMCBCtrlSel", "ctlExt"),
        ("xlCPUNoiseSwCtrl", "swOff"),
        ("yrCPUNoiseSwCtrl", "swOff"),
        ("loOrHiCalSel", "lowCal")),
    "lo-mcb": (
        ("xlExtToMCBCtrlSel", "ctlMcb"),
        ("yrExtToMCBCtrlSel", "ctlMcb"),
        ("xlCPUNoiseSwCtrl", "swOn"),
        ("yrCPUNoiseSwCtrl", "swOn"),
        ("loOrHiCalSel", "lowCal")),
    "hi-mcb": (
        ("xlExtToMCBCtrlSel", "ctlMcb"),
        ("yrExtToMCBCtrlSel", "ctlMcb"),
        ("xlCPUNoiseSwCtrl", "swOn"),
        ("yrCPUNoiseSwCtrl", "swOn"),
        ("loOrHiCalSel", "highCal")),
    "lo-ext": (
        ("xlExtToMCBCtrlSel", "ctlExt"),
        ("yrExtToMCBCtrlSel", "ctlExt"),
        ("xlCPUNoiseSwCtrl", "swOff"),
        ("yrCPUNoiseSwCtrl", "swOff"),
        ("loOrHiCalSel", "lowCal")),
    "hi-ext": (
        ("xlExtToMCBCtrlSel", "ctlExt"),
        ("yrExtToMCBCtrlSel", "ctlExt"),
        ("xlCPUNoiseSwCtrl", "swOff"),
        ("yrCPUNoiseSwCtrl", "swOff"),
        ("loOrHiCalSel", "highCal")),
    "lo": (
        ("xlExtToMCBCtrlSel", "ctlExt"),
        ("yrExtToMCBCtrlSel", "ctlExt"),
        ("xlCPUNoiseSwCtrl", "swOff"),
        ("yrCPUNoiseSwCtrl", "swOff"),
        ("loOrHiCalSel", "lowCal")),
    "hi": (
        ("xlExtToMCBCtrlSel", "ctlExt"),
        ("yrExtToMCBCtrlSel", "ctlExt"),
        ("xlCPUNoiseSwCtrl", "swOff"),
        ("yrCPUNoiseSwCtrl", "swOff"),
        ("loOrHiCalSel", "highCal"))
}

NOISECAL40_52 = {
    "off": (
        ("calState", "ctlMcb"),
        ("noiseSourcePwrSwAB", "swOff"),
        ("noiseSourcePwrSwCD", "swOff")
    ),
    "on-mcb": (
        ("calState", "ctlMcb"),
        ("noiseSourcePwrSwAB", "swOn"),
        ("noiseSourcePwrSwCD", "swOn")
    ),
    "on-ext": (
        ("calState", "ctlExt"),
        ("noiseSourcePwrSwAB", "swOn"),
        ("noiseSourcePwrSwCD", "swOn")
    ),
    "lo-mcb": (
        ("calState", "ctlMcb"),
        ("noiseSourcePwrSwAB", "swOn"),
        ("noiseSourcePwrSwCD", "swOn")
    ),
    "hi-mcb": (
        ("calState", "ctlMcb"),
        ("noiseSourcePwrSwAB", "swOn"),
        ("noiseSourcePwrSwCD", "swOn")
    ),
    "lo-ext": (
        ("calState", "ctlExt"),
        ("noiseSourcePwrSwAB", "swOn"),
        ("noiseSourcePwrSwCD", "swOn")
    ),
    "hi-ext": (
        ("calState", "ctlExt"),
        ("noiseSourcePwrSwAB", "swOn"),
        ("noiseSourcePwrSwCD", "swOn")
    ),
    "lo": (
        ("calState", "ctlExt"),
        ("noiseSourcePwrSwAB", "swOn"),
        ("noiseSourcePwrSwCD", "swOn")
    ),
    "hi": (
        ("calState", "ctlExt"),
        ("noiseSourcePwrSwAB", "swOn"),
        ("noiseSourcePwrSwCD", "swOn")
    )
}

NOISECAL_NONE = {}

NOISECAL26_40 = {
    "off": (
        ("calState", "ctlMcb"),
        ("b1noiseSourcePwrSw", "swOff"),
        ("b2noiseSourcePwrSw", "swOff"),
        ("b1EXTnoiseSourcePwrSw", "swOff"),
        ("b2EXTnoiseSourcePwrSw", "swOff")
    ),
    "on-mcb": (
        ("calState", "ctlMcb"),
        ("b1noiseSourcePwrSw", "swOn"),
        ("b2noiseSourcePwrSw", "swOn"),
        ("b1EXTnoiseSourcePwrSw", "swOff"),
        ("b2EXTnoiseSourcePwrSw", "swOff")
    ),
    "on": (
        ("calState", "ctlExt"),
        ("b1noiseSourcePwrSw", "swOff"),
        ("b2noiseSourcePwrSw", "swOff"),
        ("b1EXTnoiseSourcePwrSw", "swOn"),
        ("b2EXTnoiseSourcePwrSw", "swOn")
    ),
    "on-ext": (
        ("calState", "ctlExt"),
        ("b1noiseSourcePwrSw", "swOff"),
        ("b2noiseSourcePwrSw", "swOff"),
        ("b1EXTnoiseSourcePwrSw", "swOn"),
        ("b2EXTnoiseSourcePwrSw", "swOn")
    ),
    "lo": (
        ("calState", "ctlExt"),
        ("b1noiseSourcePwrSw", "swOff"),
        ("b2noiseSourcePwrSw", "swOff"),
        ("b1EXTnoiseSourcePwrSw", "swOn"),
        ("b2EXTnoiseSourcePwrSw", "swOn")
    ),
    "lo-ext": (
        ("calState", "ctlExt"),
        ("b1noiseSourcePwrSw", "swOff"),
        ("b2noiseSourcePwrSw", "swOff"),
        ("b1EXTnoiseSourcePwrSw", "swOn"),
        ("b2EXTnoiseSourcePwrSw", "swOn")
    ),
    "LR": (
        ("calState", "ctlExt"),
        ("b1noiseSourcePwrSw", "swOff"),
        ("b2noiseSourcePwrSw", "swOff"),
        ("b1EXTnoiseSourcePwrSw", "swOn"),
        ("b2EXTnoiseSourcePwrSw", "swOn")
    ),
    "RL": (
        ("calState", "ctlExt"),
        ("b1noiseSourcePwrSw", "swOff"),
        ("b2noiseSourcePwrSw", "swOff"),
        ("b1EXTnoiseSourcePwrSw", "swOn"),
        ("b2EXTnoiseSourcePwrSw", "swOn")
    ),
    "R": (
        ("calState", "ctlExt"),
        ("b1noiseSourcePwrSw", "swOff"),
        ("b2noiseSourcePwrSw", "swOff"),
        ("b1EXTnoiseSourcePwrSw", "swOn"),
        ("b2EXTnoiseSourcePwrSw", "swOff")
    ),
    "L": (
        ("calState", "ctlExt"),
        ("b1noiseSourcePwrSw", "swOff"),
        ("b2noiseSourcePwrSw", "swOff"),
        ("b1EXTnoiseSourcePwrSw", "swOff"),
        ("b2EXTnoiseSourcePwrSw", "swOn")
    )
}

NOISECAL_ARRAY = {
    "off": (
        ("CalSelect,1,State", "swOff"),
        ("CalSelect,2,State", "swOff"),
        ("CalSelect,3,State", "swOff"),
        ("CalSelect,4,State", "swOff"),
        ("CalSelect,5,State", "swOff"),
        ("CalSelect,6,State", "swOff"),
        ("CalSelect,7,State", "swOff"),
        ("CalState", "MCB")
    ),
    "on-mcb": (
        ("CalSelect,1,State", "swOn"),
        ("CalSelect,2,State", "swOn"),
        ("CalSelect,3,State", "swOn"),
        ("CalSelect,4,State", "swOn"),
        ("CalSelect,5,State", "swOn"),
        ("CalSelect,6,State", "swOn"),
        ("CalSelect,7,State", "swOn"),
        ("CalState", "MCB")
    ),
    "on-ext": (
        ("CalSelect,1,State", "swOn"),
        ("CalSelect,2,State", "swOn"),
        ("CalSelect,3,State", "swOn"),
        ("CalSelect,4,State", "swOn"),
        ("CalSelect,5,State", "swOn"),
        ("CalSelect,6,State", "swOn"),
        ("CalSelect,7,State", "swOn"),
        ("CalState", "External1")
    ),
    "on-ext2": (
        ("CalSelect,1,State", "swOn"),
        ("CalSelect,2,State", "swOn"),
        ("CalSelect,3,State", "swOn"),
        ("CalSelect,4,State", "swOn"),
        ("CalSelect,5,State", "swOn"),
        ("CalSelect,6,State", "swOn"),
        ("CalSelect,7,State", "swOn"),
        ("CalState", "External1")
    ),
    "lo-mcb": (
        ("CalSelect,1,State", "swOn"),
        ("CalSelect,2,State", "swOn"),
        ("CalSelect,3,State", "swOn"),
        ("CalSelect,4,State", "swOn"),
        ("CalSelect,5,State", "swOn"),
        ("CalSelect,6,State", "swOn"),
        ("CalSelect,7,State", "swOn"),
        ("CalState", "MCB")
    ),
    "hi-mcb": (
        ("CalSelect,1,State", "swOn"),
        ("CalSelect,2,State", "swOn"),
        ("CalSelect,3,State", "swOn"),
        ("CalSelect,4,State", "swOn"),
        ("CalSelect,5,State", "swOn"),
        ("CalSelect,6,State", "swOn"),
        ("CalSelect,7,State", "swOn"),
        ("CalState", "MCB")
    ),
    "lo-ext": (
        ("CalSelect,1,State", "swOn"),
        ("CalSelect,2,State", "swOn"),
        ("CalSelect,3,State", "swOn"),
        ("CalSelect,4,State", "swOn"),
        ("CalSelect,5,State", "swOn"),
        ("CalSelect,6,State", "swOn"),
        ("CalSelect,7,State", "swOn"),
        ("CalState", "External1")
    ),
    "lo-ext2": (
        ("CalSelect,1,State", "swOn"),
        ("CalSelect,2,State", "swOn"),
        ("CalSelect,3,State", "swOn"),
        ("CalSelect,4,State", "swOn"),
        ("CalSelect,5,State", "swOn"),
        ("CalSelect,6,State", "swOn"),
        ("CalSelect,7,State", "swOn"),
        ("CalState", "External1")
    ),
    "hi-ext": (
        ("CalSelect,1,State", "swOn"),
        ("CalSelect,2,State", "swOn"),
        ("CalSelect,3,State", "swOn"),
        ("CalSelect,4,State", "swOn"),
        ("CalSelect,5,State", "swOn"),
        ("CalSelect,6,State", "swOn"),
        ("CalSelect,7,State", "swOn"),
        ("CalState", "External1")
    ),
    "hi-ext2": (
        ("CalSelect,1,State", "swOn"),
        ("CalSelect,2,State", "swOn"),
        ("CalSelect,3,State", "swOn"),
        ("CalSelect,4,State", "swOn"),
        ("CalSelect,5,State", "swOn"),
        ("CalSelect,6,State", "swOn"),
        ("CalSelect,7,State", "swOn"),
        ("CalState", "External1")
    ),
    "lo": (
        ("CalSelect,1,State", "swOn"),
        ("CalSelect,2,State", "swOn"),
        ("CalSelect,3,State", "swOn"),
        ("CalSelect,4,State", "swOn"),
        ("CalSelect,5,State", "swOn"),
        ("CalSelect,6,State", "swOn"),
        ("CalSelect,7,State", "swOn"),
        ("CalState", "External1")
    ),
    "hi": (
        ("CalSelect,1,State", "swOn"),
        ("CalSelect,2,State", "swOn"),
        ("CalSelect,3,State", "swOn"),
        ("CalSelect,4,State", "swOn"),
        ("CalSelect,5,State", "swOn"),
        ("CalSelect,6,State", "swOn"),
        ("CalSelect,7,State", "swOn"),
        ("CalState", "External1")
    )
}

RECEIVERS = {
    "Rcvr_342": NOISECAL_LO,
    "Rcvr_450": NOISECAL_LO,
    "Rcvr_600": NOISECAL_LO,
    "Rcvr_800": NOISECAL_LO,
    "Rcvr_1070": NOISECAL_LO,
    "Rcvr1_2": NOISECAL_LO,
    "Rcvr4_6": NOISECAL_LO,
    "Rcvr8_10": NOISECAL_LO,
    "Rcvr12_18": NOISECAL_HI,
    "Rcvr2_3": NOISECAL_LO,
    "Rcvr18_22": NOISECAL_HI,
    "Rcvr22_26": NOISECAL_HI,
    "RcvrArray18_26": NOISECAL_ARRAY,
    "Rcvr40_52": NOISECAL40_52,
    "Rcvr26_40": NOISECAL26_40,
    "NoiseSource": NOISECAL_LO,
    "Holography": NOISECAL_NONE,
    "Rcvr68_92": NOISECAL_NONE,
    "RcvrArray75_115": NOISECAL_NONE
}

NOTCH_FILTER = {"Rcvr1_2": (1180, 1350)}

CHOPPER = ("Rcvr40_52",)

QD_AND_ACTIVE_SURFACE_ON_RCVRS = (
    "Rcvr4_6",
    "Rcvr8_10",
    "Rcvr18_22",
    "Rcvr22_26",
    "Rcvr40_52",
    "Rcvr12_18",
    "Rcvr26_40",
    "Holography",
    "Rcvr68_92",
    "RcvrArray18_26",
    "RcvrArray75_115"
)

BEAM = {
    "B1": 1,
    "B2": 1,
    "B3": 1,
    "B4": 1,
    "B12": 2,
    "B34": 2,
    "B1234": 4
}

# allowed beams, -1 is used as the "special" addition beam for KFPA receiver
# and is used to route an addition Beam 1 signal
ALLOWEDNEWBEAMS = (
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "ALL",
    "-1"
)

ALLOWEDNEWBEAMSWBAND = (
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "ALL"
)

BEAM_CONVERSION = {
    "B1": "1",
    "B2": "2",
    "B3": "3",
    "B4": "4",
    "B12": "1,2",
    "B34": "3,4",
    "B1234": "1,2,3,4",
    "1": "B1",
    "2": "B2",
    "3": "B3",
    "4": "B4",
    "1,2": "B12",
    "3,4": "B34",
    "1,2,3,4": "B1234"
}

BEAMTYPE = {
    "L1": 2,
    "L2": 2,
    "L3": 2,
    "L4": 2,
    "R1": 2,
    "R2": 2,
    "R3": 2,
    "R4": 2,
    "L5": 1,
    "L6": 1,
    "L7": 1,
    "R5": 1,
    "R6": 1,
    "R7": 1,
    "WL1": 2,
    "WL2": 2,
    "WR1": 2,
    "WR2": 2
}

BEAMPAIR = {
    "L1": "R1",
    "L2": "R2",
    "L3": "R3",
    "L4": "R4",
    "L5": "R5",
    "L6": "R6",
    "L7": "R7",
    "R4": "L4",
    "R3": "L3",
    "R2": "L2",
    "R1": "L1",
    "R5": "L5",
    "R6": "L6",
    "R7": "L6",
    "XL": "YR",
    "YR": "XL",
    "XLC_IF": "YRD_IF",
    "YRD_IF": "XLC_IF",
    "XLA_IF": "YRB_IF",
    "YRB_IF": "XLA_IF",
    "test_monitor": "ref_monitor",
    "ref_monitor": "test_monitor",
    "J1": "J2",
    "J2": "J1",
    "J3": "J4",
    "J4": "J3",
    "L": "R",
    "R": "L",
    "XL1": "YR1",
    "YR1": "XL1",
    "X2": "Y2",
    "Y2": "X2",
    "WR1": "WL1",
    "WL2": "WR2",
    "WL1": "WR1",
    "WR2": "WL2"
}

Rcvr26_40BEAMPAIR = {
    "L2": "R1",
    "R1": "L2",
    "R2": "L1",
    "L1": "R2"
}

DUAL_POL_RCVRS = (
    "Rcvr_342",
    "Rcvr_450",
    "Rcvr_600",
    "Rcvr_800",
    "Rcvr68_92",
    "Rcvr_1070",
    "Rcvr1_2",
    "Rcvr4_6",
    "Rcvr2_3",
    "Holography"
)

MULTI_BEAM_RCVRS = (
    "Rcvr12_18",
    "Rcvr22_26",
    "Rcvr18_22",
    "Rcvr26_40",
    "Rcvr40_52",
    "NoiseSource",
    "RcvrArray18_26",
    "Rcvr68_92",
    "RcvrArray75_115",
)

PFRCVRS = (
    "Rcvr_342",
    "Rcvr_450",
    "Rcvr_600",
    "Rcvr_800"
)

PF2RCVRS = ("Rcvr_1070",)


IFfilters = (
    ("pass_2990_3010", 2990, 3010),
    ("pass_2960_3040", 2960, 3040),
    ("pass_2840_3160", 2840, 3160),
    ("pass_2360_3640", 2360, 3640),
    ("pass_5960_6040", 5960, 6040),
    ("pass_5840_6160", 5840, 6160),
    ("pass_5360_6640", 5360, 6640)
)

IFFiltersToBandwidth = {
    "pass_2990_3010": 20,
    "pass_2960_3040": 80,
    "pass_2840_3160": 320,
    "pass_2360_3640": 1280,
    "pass_5960_6040": 80,
    "pass_5840_6160": 320,
    "pass_5360_6640": 1280,
    "pass_all": 4000
}

# {bandwidth  in IFRack: { acs level : targetlevel}}
ReceiverGroupIFCenter3000 = {
    20: {9: "0.1", 3: "0.5"},
    80: {9: "0.1", 3: "0.5"},
    100: {9: "0.1", 3: "0.5"},
    320: {9: "1.0", 3: "1.0"},
    1280: {9: "1.0", 3: "1.0"},
    4000: {9: "3.0", 3: "5.0"}
}

# {PF filter setting:" (acs level : targetlevel}}
ReceiverGroupPF = {  # PF filter bandwidth" (acs level : targetlevel}}
    20: {9: "0.1", 3: "0.5"},
    40: {9: "0.1", 3: "0.5"},
    80: {9: "0.1", 3: "0.5"},
    100: {9: "0.1", 3: "0.5"},
    240: {9: "1.0", 3: "1.0"}
}


ReceiverGroupIFCenter6000 = {
    20: {9: "1.0", 3: "1.0"},
    80: {9: "1.0", 3: "1.0"},
    100: {9: "1.0", 3: "1.0"},
    320: {9: "1.0", 3: "1.0"},
    1280: {9: "1.0", 3: "1.0"},
    4000: {9: "3.0", 3: "5.0"}
}

ReceiverGroup = {
    "Rcvr1_2": ReceiverGroupIFCenter3000,
    "Rcvr4_6": ReceiverGroupIFCenter3000,
    "Rcvr8_10": ReceiverGroupIFCenter3000,
    "Rcvr12_18": ReceiverGroupIFCenter3000,
    "Rcvr2_3": ReceiverGroupIFCenter3000,
    "Rcvr18_26": ReceiverGroupIFCenter6000,
    "Rcvr18_22": ReceiverGroupIFCenter6000,
    "Rcvr22_26": ReceiverGroupIFCenter6000,
    "Rcvr26_40": ReceiverGroupIFCenter6000,
    "Rcvr40_52": ReceiverGroupIFCenter6000,
    "RcvrArray18_26": ReceiverGroupIFCenter6000
}

# feed designators that are uniquely valid for a particular feed
RCVRS_FEED_DES = {
    "Rcvr_342": ("XLC_IF", "YRD_IF"),
    "Rcvr_450": ("XLC_IF", "YRD_IF"),
    "Rcvr_600": ("XLA_IF", "YRB_IF"),
    "Rcvr_800": ("XLA_IF", "YRB_IF"),
    "Rcvr_1070": ("XLA_IF", "YRB_IF"),
    "Rcvr18_22": ("L1", "R1", "L2", "R2"),
    "Rcvr22_26": ("L3", "R3", "L4", "R4"),
    "Rcvr26_40": ("R1", "L1", "R2", "L2"),
    "Holography": ("test_monitor", "ref_monitor")
}

# BEAM to  cabling file feed designations
BEAM_TO_FEED_DES = {
    "Holography":
    {
        "B1": ("test_monitor", "ref_monitor", "test_monitor", "ref_monitor"),
        "B2": ("J1", "J2", "J3", "J4"),
        "B12": ("J1", "J2", "J3", "J4"),
        "1": ("test_monitor", "ref_monitor", "test_monitor", "ref_monitor"),
        "2": ("J1", "J2", "J3", "J4"),
        1: ("J1", "J2", "J3", "J4"),
        2: ("J1", "J2", "J3", "J4")
    },
    "NoiseSource":
    {
        "B1": ("J1", "J2", "J3", "J4"),
        "B2": ("J1", "J2", "J3", "J4"),
        "B12": ("J1", "J2", "J3", "J4"),
        "1": ("J1", "J2", "J3", "J4"),
        "2": ("J1", "J2", "J3", "J4"),
        1: ("J1", "J2", "J3", "J4"),
        2: ("J1", "J2", "J3", "J4")
    },
    "Rcvr26_40":
    {
        "B1": ("L2", "R1"),
        "B2": ("R1", "L2"),
        "B12": ("L1", "R1", "L2", "R2"),
        "B12": ("L1", "R1", "L2", "R2"),
        "1": ("L2", "R1"),
        "2": ("R1", "L2"),
        1: ("L2", "R1"),
        2: ("R1", "L2"),
        "1,2": ("L2", "R1", "L1", "R2"),
        "2,1": ("R1", "L2", "L1", "R2")
    },
    "Rcvr40_52":
    {
        "B1": ("L1", "R1"),
        "B2": ("L2", "R2"),
        "B12": ("L1", "R1", "L2", "R2"),
        "B3": ("L3", "R3"),
        "B4": ("L4", "R4"),
        "B34": ("L3", "R3", "L4", "R4"),
        "B1234": ("L1", "R1", "L2", "R2", "L3", "R3", "L4", "R4"),
        "1": ("L1", "R1"),
        "2": ("L2", "R2"),
        1: ("L1", "R1"),
        2: ("L2", "R2"),
        "3": ("L3", "R3"),
        "4": ("L4", "R4"),
        3: ("L3", "R3"),
        4: ("L4", "R4"),
        "1,2": ("L1", "R1", "L2", "R2"),
        "2,1": ("L2", "R2", "L1", "R1"),
        "1,2,3,4": ("L1", "R1", "L2", "R2", "L3", "R3", "L4", "R4"),
        "3,4": ("L3", "R3", "L4", "R4"),
        "4,3": ("L4", "R4", "L3", "R3")
    },
    "Rcvr18_22":
    {
        "B1": ("L1", "R1"),
        "B2": ("L2", "R2"),
        "B12": ("L1", "R1", "L2", "R2"),
        "1": ("L1", "R1"),
        "2": ("L2", "R2"),
        1: ("L1", "R1"),
        2: ("L2", "R2"),
        "1,2": ("L1", "R1", "L2", "R2"),
        "2,1": ("L2", "R2", "L1", "R1")
    },
    "Rcvr22_26":
    {
        "B3": ("L3", "R3"),
        "B4": ("L4", "R4"),
        "B34": ("L3", "R3", "L4", "R4"),
        "3": ("L3", "R3"),
        "4": ("L4", "R4"),
        3: ("L3", "R3"),
        4: ("L4", "R4"),
        "3,4": ("L3", "R3", "L4", "R4"),
        "4,3": ("L4", "R4", "L3", "R3")
    },
    "Rcvr12_18":
    {
        "B1": ("L1", "R1"),
        "B2": ("L2", "R2"),
        "B12": ("L1", "R1", "L2", "R2"),
        "1": ("L1", "R1"),
        "2": ("L2", "R2"),
        1: ("L1", "R1"),
        2: ("L2", "R2"),
        "1,2": ("L1", "R1", "L2", "R2")
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
    "Rcvr_342":
    {
        "B1": ("XLC_IF", "YRD_IF"),
        "1": ("XLC_IF", "YRD_IF"),
        1: ("XLC_IF", "YRD_IF")
    },
    "Rcvr_450":
    {
        "B1": ("XLC_IF", "YRD_IF"),
        "1": ("XLC_IF", "YRD_IF"),
        1: ("XLC_IF", "YRD_IF")
    },
    "Rcvr_600":
    {
        "B1": ("XLA_IF", "YRB_IF"),
        "1": ("XLA_IF", "YRB_IF"),
        1: ("XLA_IF", "YRB_IF")
    },
    "Rcvr_800":
    {
        "B1": ("XLA_IF", "YRB_IF"),
        "1": ("XLA_IF", "YRB_IF"),
        1: ("XLA_IF", "YRB_IF")
    },
    "Rcvr_1070":
    {
        "B1": ("XLA_IF", "YRB_IF"),
        "1": ("XLA_IF", "YRB_IF"),
        1: ("XLA_IF", "YRB_IF")
    },
    "RcvrArray18_26":
    {
        "B1": ("L1", "R1"),
        "B2": ("L2", "R2"),
        "B3": ("L3", "R3"),
        "B4": ("L4", "R4"),
        "B5": ("L5", "R5"),
        "B6": ("L6", "R6"),
        "B7": ("L7", "R7"),
        "1": ("L1", "R1"),
        "2": ("L2", "R2"),
        "3": ("L3", "R3"),
        "4": ("L4", "R4"),
        "5": ("L5", "R5"),
        "6": ("L6", "R6"),
        "7": ("L7", "R7"),
        "-1": ("L1", "R1"),
        "10": ("WL1", "WR1"),
        "20": ("WL2", "WR2"),
        "B12": ("L1", "R1", "L2", "R2"),
        "B34": ("L3", "R3", "L4", "R4"),
        1: ("L1", "R1"),
        2: ("L2", "R2"),
        3: ("L3", "R3"),
        4: ("L4", "R4"),
        5: ("L5", "R5"),
        6: ("L6", "R6"),
        7: ("L7", "R7"),
        -1: ("L1", "R1"),
        10: ("WL1", "WR1"),
        20: ("WL2", "WR2")
    },
    "Rcvr68_92":
    {
        "B1": ("XL1", "YR1"),
        "B2": ("X2", "Y2"),
        "B12": ("XL1", "YR1", "X2", "Y2"),
        "1": ("XL1", "YR1"),
        "2": ("X2", "Y2"),
        1: ("XL1", "YR1"),
        2: ("X2", "Y2"),
        "1,2": ("XL1", "YR1", "X2", "Y2"),
        "2,1": ("X2", "Y2", "XL1", "YR1")
    },
    "RcvrArray75_115":
    {
        "B1": ("J1"),
        "B2": ("J2"),
        "B3": ("J3"),
        "B4": ("J4"),
        "B5": ("J5"),
        "B6": ("J6"),
        "B7": ("J7"),
        "B8": ("J8"),
        "B9": ("J9"),
        "B10": ("J10"),
        "B11": ("J11"),
        "B12": ("J12"),
        "B13": ("J13"),
        "B14": ("J14"),
        "B15": ("J15"),
        "B16": ("J16"),
        "B12345678910111213141516": ("J1", "J2", "J3", "J4", "J6", "J7", "J8"),
        "1": ("J1"),
        "2": ("J2"),
        "3": ("J3"),
        "4": ("J4"),
        "5": ("J5"),
        "6": ("J6"),
        "7": ("J7"),
        "8": ("J8"),
        "9": ("J9"),
        "10": ("J10"),
        "11": ("J11"),
        "12": ("J12"),
        "13": ("J13"),
        "14": ("J14"),
        "15": ("J15"),
        "16": ("J16"),
        1: ("J1"),
        2: ("J2"),
        3: ("J3"),
        4: ("J4"),
        5: ("J5"),
        6: ("J6"),
        7: ("J7"),
        8: ("J8"),
        9: ("J9"),
        10: ("J10"),
        11: ("J11"),
        12: ("J12"),
        13: ("J13"),
        14: ("J14"),
        15: ("J15"),
        16: ("J16")
    }
}


# misc ----------
LEGAL_XFER_STATES = (
    None,
    "ext",
    "thru",
    "cross"
)

OBSTYPES = (
    "Continuum",
    "Spectroscopy",
    "Pulsar",
    "Radar",
    "VLBI"
)

VELOCITYDEFINITION = (
    "Optical",
    "Radio",
    "Relativistic",
    "Red"
)

VELFRAMES = (
    "topo",
    "bary",
    "lsrk",
    "lsrd",
    "galac",
    "cmb",
    "lgr",
    "helio"
)

LO1B_PWR_LEVELS = (
    (13000, "3"),
    (14500, "4"),
    (15050, "2"),
    (18000, "5.2"),
    (44000, "1")
)

# maps astronomical velocity frame terms into MC velocity fram terms
vframe = {
    "topo": "Local",
    "bary": "Barycentric",
    "lsrk": "KinematicalLSR",
    "lsrd": "DynamicalLSR",
    "galac": "Gactocentric",
    "cmb": "CosmicBackground",
    "helio": "Heliocentric",
    "lgr": "LocalGroup"
}

LEVELS = {
    "clear": 0,
    "Info": 1,
    "Notice": 2,
    "Warning": 3,
    "Error": 4,
    "Fault": 5,
    "Fatal": 6,
    "Off": 7
}

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

LLRADAR_PORTS = {
    2: ("1", "2"),
    4: ("1", "2", "3", "4")
}

# KFPA defs ----------
KFPA_NOTUSED_ATTEN = {
    1: "17",
    2: "27"
}
KFPA_ATTEN_NAMES = {
    1: "IDMType1Attenuators,",
    2: "IDMType2Attenuators,"
}

KFPA_NOMINAL_ATTEN = {
    "L1": "17",
    "L2": "15",
    "L3": "11",
    "L4": "15",
    "R1": "4",
    "R2": "5",
    "R3": "11",
    "R4": "12",
    "L5": "5",
    "L6": "5",
    "L7": "5",
    "R5": "5",
    "R6": "5",
    "R7": "5"
}

# ARGUS defs ---------
ARGUS_SIDEBANDS = {
    0: "upper",
    1: "lower"
}

# KA defs ----------
BYPASS_SWITCHES = {
    "diff1_bypassHybrid": "swOff",
    "sum1_bypassHybrid": "swOff",
    "diff1_toZpectrometer": "swOff",
    "sum1_toZpectrometer": "swOff",
    "diff2_bypassHybrid": "swOff",
    "sum2_bypassHybrid": "swOff",
    "diff2_toZpectrometer": "swOff",
    "sum2_toZpectrometer": "swOff"
}
ZPECTROMETER_BYPASS_SWITCHES = {
    "diff1_bypassHybrid": "swOn",
    "sum1_bypassHybrid": "swOn",
    "diff1_toZpectrometer": "swOn",
    "sum1_toZpectrometer": "swOn",
    "diff2_bypassHybrid": "swOn",
    "sum2_bypassHybrid": "swOn",
    "diff2_toZpectrometer": "swOn",
    "sum2_toZpectrometer": "swOn"
}


# keyword def ------------
KEYWORDLIST = [
    "obstype",
    "backend",
    "receiver",
    "freq",
    "bandwidth",
    "tint",
    "swmode",
    "swtype",
    "swper",
    "swfreq",
    "beam",
    "nwin",
    "dfreq",
    "vlow",
    "vhigh",
    "vdef",
    "vframe",
    "noisecal",
    "polarization",
    "nchan",
    "phasecal",
    "vlbirack",
    "notchfilter",
    "beamswitch",
    "polswitch",
    "xfer",
    "chopper",
    "iftarget",
    "ifbw",
    "if0freq",
    "lo1bfreq",
    "lo2freq",
    "if3freq",
    "cal_off_integs",
    "XL_on_integs",
    "YR_on_integs",
    "both_on_integs",
    "bswfreq",
    "obsmode",
    "polnmode",
    "numchan",
    "outbits",
    "scale",
    "fold_dumptime",
    "fold_bins",
    "fold_parfile",
    "datadisk",
    "dm",
    "refatten",
    "testatten",
    "reqinteg",
    "nstep",
    "lsync",
    "settle",
    "nsamp",
    "tuning",
    "init",
    "lutstart",
    "defaultdac",
    "newFreq",
    "newDeltaFreq",
    "broadband",
    "vpol",
    "vfits",
    "DOPPLERTRACKFREQ",
    "ignore_dopplertrackfreq",
    "subband",
    "sideband",
    "obsmode",
    "polnmode",
    "numchan",
    "outbits",
    "vegas_scale",
    "fold_dumptime",
    "fold_bins",
    "fold_parfile",
    "datadisk",
    "dm",
    "obsmode",
    "polnmode",
    "numchan",
    "outbits",
    "scale",
    "fold_dumptime",
    "fold_bins",
    "fold_parfile",
    "datdisk",
    "dm"
]


# DCR_AF ----------
SPCHS = ("low", "medium", "high")


SPECTROSCOPY_BW = (
    12.5,
    50,
    200,
    800,
    50.0,
    200.0,
    800.0
)


SPECTROSCOPY_BW_FORMATTED = {
    12.5: 12.5,
    50: 50,
    200: 200,
    800: 800,
    50.0: 50,
    200.0: 200,
    800.0: 800
}

# GUPPI -----------
GUPPI_BW = (
    100,
    200,
    800
)

GUPPI_OBSMODES = (
    "search",
    "fold",
    "cal",
    "coherent_cal",
    "coherent_fold",
    "coherent_search",
    "raw"
)

GUPPI_POLNMODES = (
    "full_stokes",
    "total_intensity"
)

GUPPI_PORTS = {
    2: ("1", "2")
}

GUPPI_POL_MAP = {
    "XX": "I,Q",
    "YY": "U,V",
    "XY": "I,Q",
    "YX": "U,V",
    "LL": "I,Q",
    "RR": "U,V",
    "LR": "I,Q",
    "RL": "U,V",
    # these are the cross product secondary pol
    "X": "Y",
    "Y": "X",
    "R": "L",
    "L": "R"
}
# VLBA dfs ----
VLBA_PORTS = {
    "A": ("VLBA_DAR:C", "VLBA_DAR:A"),
    "B": ("VLBA_DAR:D", "VLBA_DAR:B"),
    "AB": ("VLBA_DAR:C", "VLBA_DAR:A", "VLBA_DAR:D", "VLBA_DAR:B")
}

VLBA_PORT_LETTER_TO_NUM = {
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4
}


# CCB defs ----------------
CCB_FREQ_RANGES = (
    (26000, 29500),
    (29501, 33000),
    (33001, 36500),
    (36501, 40000)
)

CCB_BEAM_FREQ_RANGES = {
    "B1": (
        (26000, 29500, (1, 12)),
        (29501, 33000, (2, 11)),
        (33001, 36500, (3, 10)),
        (36501, 40000, (4, 9))
    ),
    "B2": (
        (26000, 29500, (5, 16)),
        (29501, 33000, (6, 15)),
        (33001, 36500, (7, 14)),
        (36501, 40000, (8, 13))
    ),
    "B12": (
        (26000, 29500, (1, 5, 12, 16)),
        (29501, 33000, (2, 6, 11, 15)),
        (33001, 36500, (3, 7, 10, 14)),
        (36501, 40000, (4, 8, 9, 13))
    ),
    "1": (
        (26000, 29500, (1, 12)),
        (29501, 33000, (2, 11)),
        (33001, 36500, (3, 10)),
        (36501, 40000, (4, 9))
    ),
    "2": (
        (26000, 29500, (5, 16)),
        (29501, 33000, (6, 15)),
        (33001, 36500, (7, 14)),
        (36501, 40000, (8, 13))
    ),
    "(1,2)": (
        (26000, 29500, (1, 5, 12, 16)),
        (29501, 33000, (2, 6, 11, 15)),
        (33001, 36500, (3, 7, 10, 14)),
        (36501, 40000, (4, 8, 9, 13))
    )
}

CCB_RCVRS = ("Rcvr26_40",)

CCB_PARAMS = (
    "cal_off_integs",
    "XL_on_integs",
    "YR_on_integs",
    "both_on_integs",
    "bswfreq"
)

CCBDEFAULT = {
    "cal_off_integs": 10,
    "XL_on_integs": 0,
    "YR_on_integs": 0,
    "both_on_integs": 0,
    "bswfreq": 4
}

CCBSWITCHSETTINGS = {
    # when in total power, switches depend on xfer value
    "thru": (
        ("active_switches", "none"),
        ("closed_switches", "none")
    ),
    "cross": (
        ("active_switches", "none"),
        ("closed_switches", "A")
    ),
    # when in switched power,
    # switches depend on swtype value
    "bsw": (
        ("active_switches", "both"),
        ("closed_switches", "none")
    ),
    "bswCcbAonly": (
        ("active_switches", "A"),
        ("closed_switches", "none")
    ),
    "bswCcbBonly": (
        ("active_switches", "B"),
        ("closed_switches", "none")
    )
}

CCBSWTYPES = (
    "none",
    "bsw",
    "bswCcbAonly",
    "bswCcbBonly"
)

ARCHIVIST_PARAMETERS = (
    ("dataAssociatedParameters,1,device", "Weather"),
    ("dataAssociatedParameters,1,manager", "Weather2"),
    ("dataAssociatedParameters,1,sampler", "weather2"),
    ("dataAssociatedParameters,1,delta", "1"),
    ("dataAssociatedParameters,2,device", "Weather"),
    ("dataAssociatedParameters,2,manager", "Weather1"),
    ("dataAssociatedParameters,2,sampler", "weather1"),
    ("dataAssociatedParameters,2,delta", "1"),
    ("dataAssociatedParameters,3,device", "Weather"),
    ("dataAssociatedParameters,3,manager", "Weather3"),
    ("dataAssociatedParameters,3,sampler", "weather3"),
    ("dataAssociatedParameters,3,delta", "1"),
    ("dataAssociatedParameters,4,device", "QuadrantDetector"),
    ("dataAssociatedParameters,4,manager", "QuadrantDetector"),
    ("dataAssociatedParameters,4,sampler", "QuadrantDetectorData"),
    ("dataAssociatedParameters,4,delta", "0.1"),
    ("dataAssociatedParameters,5,device", "Pyrgeometer"),
    ("dataAssociatedParameters,5,manager", "Pyrgeometer"),
    ("dataAssociatedParameters,5,sampler", "monitorData"),
    ("dataAssociatedParameters,5,delta", "0.1")
)

DEF_OFF_SYSTEMS = {
    "Default": [
        "LASSI",
        "Holography",
        "Rcvr1_2",
        "Rcvr18_26",
        "Rcvr2_3",
        "Rcvr8_10",
        "RcvrPF_1",
        "Rcvr4_6",
        "Rcvr12_18",
        "Rcvr40_52",
        "Rcvr26_40",
        "ConverterRack",
        "RcvrPF_2",
        "Archivist",
        "DCR",
        "AnalogFilterRack",
        "CCB26_40",
        "GUPPI",
        "RcvrArray18_26",
        "Rcvr68_92",
        "VEGAS",
        "RcvrArray1_2",
        "Rcvr_MBA1_5",
        "RcvrArray75_115"
    ],
    "LASSI": [
        "ActiveSurface",
        "QuadrantDetector",
        "Holography",
        "Rcvr1_2",
        "Rcvr18_26",
        "Rcvr2_3",
        "Rcvr8_10",
        "RcvrPF_1",
        "Rcvr4_6",
        "Rcvr12_18",
        "Rcvr40_52",
        "Rcvr26_40",
        "ConverterRack",
        "RcvrPF_2",
        "DCR",
        "AnalogFilterRack",
        "CCB26_40",
        "Measurements",
        "LO1",
        "IFRack",
        "IFManager",
        "RcvrArray18_26",
        "SwitchingSignalSelector",
        "GUPPI",
        "Rcvr68_92",
        "VEGAS",
        "RcvrArray1_2",
        "Rcvr_MBA1_5",
        "RcvrArray75_115"
    ],    
    "Rcvr_PAR": [
        "Holography",
        "Rcvr1_2",
        "Rcvr18_26",
        "Rcvr2_3",
        "Rcvr8_10",
        "RcvrPF_1",
        "Rcvr4_6",
        "Rcvr12_18",
        "Rcvr40_52",
        "Rcvr26_40",
        "ConverterRack",
        "RcvrPF_2",
        "DCR",
        "AnalogFilterRack",
        "CCB26_40",
        "Measurements",
        "LO1",
        "IFRack",
        "IFManager",
        "RcvrArray18_26",
        "SwitchingSignalSelector",
        "GUPPI",
        "Rcvr68_92",
        "VEGAS",
        "RcvrArray1_2",
        "Rcvr_MBA1_5",
        "RcvrArray75_115"
    ],
    "RcvrArray1_2": [
        "Holography",
        "Rcvr1_2",
        "Rcvr18_26",
        "Rcvr2_3",
        "Rcvr8_10",
        "RcvrPF_1",
        "Rcvr4_6",
        "Rcvr12_18",
        "Rcvr40_52",
        "Rcvr26_40",
        "ConverterRack",
        "RcvrPF_2",
        "Archivist",
        "DCR",
        "AnalogFilterRack",
        "CCB26_40",
        "Measurements",
        "IFRack",
        "IFManager",
        "RcvrArray18_26",
        "SwitchingSignalSelector",
        "GUPPI",
        "Rcvr68_92",
        "VEGAS",
        "Rcvr_PAR",
        "Rcvr_MBA1_5",
        "RcvrArray75_115"
    ],
    "Rcvr_MBA1_5": [
        "LASSI",
        "Holography",
        "Rcvr1_2",
        "Rcvr18_26",
        "Rcvr2_3",
        "Rcvr8_10",
        "RcvrPF_1",
        "Rcvr4_6",
        "Rcvr12_18",
        "Rcvr40_52",
        "Rcvr26_40",
        "Rcvr_PAR",
        "ConverterRack",
        "RcvrPF_2",
        "DCR",
        "AnalogFilterRack",
        "CCB26_40",
        "Measurements",
        "LO1",
        "IFRack",
        "IFManager",
        "RcvrArray18_26",
        "SwitchingSignalSelector",
        "GUPPI",
        "Rcvr68_92",
        "VEGAS",
        "RcvrArray1_2",
        "RcvrArray75_115"
    ]
}

DEF_ON_SYSTEMS = {
    "Default": [
        "Measurements",
        "LO1",
        "IFRack",
        "IFManager",
        "SwitchingSignalSelector"
    ],
    "RcvrArray1_2": [
        "RcvrArray1_2",
        "LO1"
    ],
    "LASSI": [
        "LASSI"
    ],
    "Rcvr_MBA1_5": [
        "Rcvr_MBA1_5",
        "ActiveSurface",
        "Archivist",
        "QuadrantDetector"
    ],
    "Rcvr_PAR": [
        "Rcvr_PAR",
        "ActiveSurface",
        "Archivist",
        "QuadrantDetector"
    ]
}

DEF_SIM_ON_SYSTEMS = {
    "Rcvr_MBA1_5": [
        "Rcvr_MBA1_5",
        "ActiveSurface",
        "Archivist"
    ],
    "Rcvr_PAR": [
        "Rcvr_PAR",
        "ActiveSurface",
        "Archivist"
    ]
}

DEF_ON_HOLOGRAPHY_SYSTEMS = [
    "LO1",
    "IFRack",
    "IFManager",
    "SwitchingSignalSelector"
]

DEF_ON_CCB_SYSTEMS = [
    "Measurements",
    "IFManager",
    "Archivist"
]

VFITS_ALLOWED = [
    "psrfits",
    "sdfits"
]

VPOL_ALLOWED = [
    "cross",
    "self",
    "self1",
    "self2",
    "none",
    "None"
]

VPM_BWS = (
    100,
    200,
    800,
    1500
)

VPM_POLNMODES = (
    "full_stokes",
    "total_intensity"
)

VPM_OBSMODES = (
    "raw",
    "search",
    "fold",
    "cal",
    "coherent_cal",
    "coherent_fold",
    "coherent_search",
    "fast"
)


VEGAS_ERRORS = {
    "vfits": (
        "Error: Illegal value for vegas.vfits. Legal values are psrfits, "
        "sdfits"
    ),
    "vpol": (
        "Error: Illegal value for vegas.vpol. Legal values are cross, self, "
        "self1 and self2"
    ),
    "vpolKa": (
        "Error: Illegal value for vegas.vpol. vpol='cross' not valid for "
        "Rcvr26_40."
    ),
    "doppler": (
        "Error: Illegal Configuration: (you must specify a doppler track freq "
        "when using a restfreq dictionary with vegas parameters is used. "
        "Please fix the error and run the configuration again. "
    ),
    "bank": (
        "Error: {0} is an illegal value in the vegas.freq bank specification. "
        "Legal values are 'A'-'H'"
    ),
    "tintMinMax": (
        "Error: {0} is an illegal integration time. The integration time must "
        "be between .0005 and 60 seconds."
    ),
    "tintVal": (
        "Error: {0} is an illegal integration time. The integration time must "
        "be an integral of the switchperiod. "
    ),
    "tint": (
        "Warning: (Data generated using this configuration can NOT be reduced "
        "using GBTIDL. If GBTIDL is required, change the integration time(s) "
        "to a integral number of switch periods."
    ),
    "bogusBW": (
        "Error: {0} is an illegal bandwidth or is invalid with the "
        "specified vegas.subband value. Legal VEGAS bandwidths are: "
        "(11.72, 16.9, 23.44, 100, 187.5, 1080, and 1500.\n "
        "Bandwidths of 16.9 and 23.44 are allowed when vegas.subband=8.\n "
        "Bandwidths of 11.72, 23.44, 100, 187.5, 1080, and 1500 are allowed "
        "when vegas.subband = 1.\n To reset the subband mode from a previous "
        "configuration use 'vegas.subband=None' in your Configuration "
        "statement.\n\n"
    ),
    "bwVsNchanSub": (
        "Error: bandwidth of {0} and nchan of {1} and subband of {2} are "
        "inconsistent. Please fix error and re submit configuration. The "
        "Vegas mode table can be found at http://www.gb.nrao.edu/vegas/modes/"
    ),
    "bwVsRes": (
        "Error: bandwidth of {0} and res of {1} are inconsistent. Please fix "
        "error and re submit configuration. The Vegas mode table can be found "
        "at http://www.gb.nrao.edu/vegas/modes/"
    ),
    "noBW": (
        "Error: Illegal configuration Bandwidth must be specified in each "
        "window."
    ),
    "noRestFreq": (
        "Error: A restfreq must be specified for every entry in restfreq "
        "dictionary."
    ),
    "noNchan": (
        "Error: Nchan must be specified"
    ),
    "coherentBadNwin": (
        "Error: For coherent modes, nwin must be 1. "
        "If unspecified, it defaults to 1."
    ),
    "coherentManyRestFreq": (
        "Error: For coherent modes, must specify only one restfrequency."
    ),
    "badNumChan": (
        "Error: Illegal value in vegas.numchan. numchan must be a "
        "power of 2 between 64 and 8192"
    )
}

CONSTRAINTS = {
    "DCR": lambda path: "OpticalDriver" in path[-2],
    "DCRKA": lambda path: (
        "MMConverter" in path[1] and
        "SamplerFilter" not in path[-2] and
        "ConverterFilter" not in path[-2]
    ),
    "Default": lambda path: 1
}
