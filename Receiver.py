# Copyright (C) 2011 Associated Universities, Inc. Washington DC, USA.
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

# from Holography import Holography
from StaticDefs import BW_XFER
from StaticDefs import CHOPPER
from StaticDefs import FILTERS
from StaticDefs import NOTCH_FILTER
from StaticDefs import POL
from StaticDefs import RCVR_FREQS
from StaticDefs import RECEIVERS
from StaticDefs import TUNING_FREQ
from StaticDefs import XFERSWITCH

from StaticDefs import DUAL_POL_RCVRS

from Manager import Manager

rcvr_mng = "NONE"


def get_rcvr():
    return rcvr_mng


def set_rcvr(mng):
    global rcvr_mng
    rcvr_mng = mng




class Receiver(Manager):
    """
    This class is responsible for:
       * expanding a given configuration for given receiver using defaults
       * generating parameters from given info

    This was stolen from config tools Receiver, along with the 
    ConfigValidator.set_receiver_defaults.
    The seq attribute is just a convenience so I didn't have to 
    change a lot of code.   
    """

    # def __init__(self, config_table, freq_calc, seq=None):
    def __init__(self, config_table, tuning_freq=None):
        """Base class for all Receivers"""
        super(Receiver, self).__init__(config_table)

        # if config_table["backend"] == "CCB":
        #     return
        # if config_table["receiver"] == "Holography":
        #     Holography(config_table, freq_calc, None, seq)
        #     if config_table["backend"] == "Holography":
        #         return

        # if seq is not None:
        #     self.seq = seq
        # else:
        #     self.seq = MySeq()

        self.filter_setting = -1

        # self.config = config_table
        # self.freq_calc = freq_calc
        # self.tuning_freq = self.freq_calc.get_tuning_freq()
        self.tuning_freq = tuning_freq

    def setParams(self):
        "Use the current info to generate manager parameters"

        self.set_manager()

        self.set_tuning_freq()

        # we've done this already
        # self.set_filters()

        if self.config["receiver"] in POL:
            self.set_polarization()
        if self.config["receiver"] in XFERSWITCH:
            self.set_transfer_switches()

        if self.mng in BW_XFER:
            self.set_beam_xfer_switches()

        # self.check_rcvr_freqs()



    def setReceiverDefaults(self, config):
        """Set receiver default keyword values; stolen from ConfigValidator"""
        
        self.default_values = []

        receiver = config["receiver"]
        if config["polarization"] is None:
            if receiver in DUAL_POL_RCVRS:
                if (config["backend"] in ("VLBA_DAR", "S2", "Radar") and
                        "Rcvr68_92" not in receiver):
                    config["polarization"] = "Circular"
                    self.default_values.append(("polarization",
                                                config["polarization"]))
                else:
                    config["polarization"] = "Linear"
                    self.default_values.append(("polarization",
                                                config["polarization"]))
            else:
                config["polarization"] = "Circular"
                self.default_values.append(("polarization",
                                            config["polarization"]))

        if config["receiver"] == "Holography":
            config["noisecal"] = None
        elif config["noisecal"] is None:
            if config["receiver"] == "RcvrArray18_26":
                config["noisecal"] = "lo"
            elif config["backend"] == "Radar":
                config["noisecal"] = "off"
            else:
                config["noisecal"] = "lo-ext"
            self.default_values.append(("noisecal", config["noisecal"]))

        if receiver == "Rcvr1_2" and config["notchfilter"] is None:
            config["notchfilter"] = "In"
            self.default_values.append(("notchfilter", config["notchfilter"]))

        if receiver == "Rcvr40_52" and config["chopper"] is None:
            config["chopper"] = "off"
            self.default_values.append(("chopper", config["chopper"]))

        if receiver in ("Rcvr12_18", "Rcvr18_22", "Rcvr22_26", "Rcvr18_26"):
            if config["beamswitch"] is None:
                if config["swtype"] == "bsw":
                    config["beamswitch"] = "ext"
                    self.default_values.append(("beamswitch",
                                                config["beamswitch"]))
                else:
                    config["beamswitch"] = "thru"
                    self.default_values.append(("beamswitch",
                                                config["beamswitch"]))

        if config["receiver"] in XFERSWITCH:
            if config["polswitch"] is None:
                if config["swtype"] == "psw":
                    config["polswitch"] = "ext"
                    self.default_values.append(("polswitch",
                                                config["polswitch"]))
                else:
                    config["polswitch"] = "thru"
                    self.default_values.append(("polswitch",
                                                config["polswitch"]))

        rcvr_mgr = config["receiver"]
        if config["receiver"] in ("Rcvr18_22", "Rcvr22_26"):
            rcvr_mgr = "Rcvr18_26"
        if rcvr_mgr in BW_XFER:
            if config["xfer"] is None:
                config["xfer"] = "thru"
            elif config["xfer"] not in BW_XFER[rcvr_mgr]:
                print("WARNING: xfer keyword value = {} is invalid. "
                      "Setting xfer to 'thru'".format(config["xfer"]))
                config["xfer"] = "thru"
            self.default_values.append(("xfer", config["xfer"]))

        return config
    # def check_rcvr_freqs(self):
    #     """Verify frequencies are within a give receivers nominal range"""
    #     bad_freqs = self.freq_calc.check_freqs(
    #         RCVR_FREQS[self.config["receiver"]][0],
    #         RCVR_FREQS[self.config["receiver"]][1]
    #     )
    #     if bad_freqs:
    #         print("WARNING: Frequencies adjusted to the local frame and "
    #               "velocities are outside the recommended receiver range: ")
    #         for freq in bad_freqs:
    #             print "Frequency = ", freq

    def set_manager(self):
        """Set mgr name which may be different than user specified name"""
        global rcvr_mng
        

        self.mng = self.config["receiver"]
        NOISECAL = RECEIVERS[self.mng]
        if self.mng in ("Rcvr18_22", "Rcvr22_26"):
            self.mng = "Rcvr18_26"
        self.set_noisecal(NOISECAL)
        rcvr_mng = self.mng

    def get_rcvr_mng(self):
        return self.mng

    def set_beam_xfer_switches(self):
        """Set beam transfer switches"""
        if self.config["swtype"] != "bsw":
            params_to_set = BW_XFER[self.mng][self.config["xfer"]]
            for p in params_to_set:
                self.seq.add_param(self.mng, p[0], p[1])

        else:
            self.seq.add_param(self.mng, "xferState", "ctlExt")

    def set_transfer_switches(self):
        """Set transfer switches"""
        params_to_set = \
            XFERSWITCH[self.config["receiver"]][self.config["polswitch"]]
        for i in range(0, len(params_to_set)):
            self.seq.add_param(self.mng, params_to_set[i][0],
                               params_to_set[i][1])

    def set_noisecal(self, NOISECAL):
        """Set noise cal switches"""
        if self.config["noisecal"] in NOISECAL:
            for i in range(0, len(NOISECAL[self.config["noisecal"]])):
                self.seq.add_param(self.mng,
                                   NOISECAL[self.config["noisecal"]][i][0],
                                   NOISECAL[self.config["noisecal"]][i][1])

    def set_polarization(self):
        """Set receiver polarization"""
        self.seq.add_param(self.mng, POL[self.config["receiver"]][0],
                           POL[self.config["receiver"]][1] +
                           self.config["polarization"])

    def get_if_freq_range(self):
        """Return frequency range """
        return self.if_freq_low, self.if_freq_high

    def set_tuning_freq(self):
        """Set tuning frequency"""
        if TUNING_FREQ[self.mng]:
            self.seq.add_param(self.mng, "tuning_frequency",
                               str(self.tuning_freq))

    def get_tuning_freq(self):
        """Return tuning frequency"""
        return self.tuning_freq

    def set_filters(self):
        """Set receiver filters"""
        found = 0
        bw_total = self.freq_calc.get_bw_total()
        if_center = self.freq_calc.get_center_freq()
        self.if_freq_low = if_center - (0.5 * bw_total)
        self.if_freq_high = if_center + (0.5 * bw_total)

        if self.config["receiver"] in FILTERS:
            param_names, filters, rcvr_type = FILTERS[self.config["receiver"]]
            bw_low = self.tuning_freq - (0.5 * bw_total)
            bw_high = self.tuning_freq + (0.5 * bw_total)
            if rcvr_type == 0:  # Mixer before filter. Convert filter freq
                bw_low = self.if_freq_low
                bw_high = self.if_freq_high
            for freq in filters:
                if bw_low >= freq[0] and bw_high <= freq[1]:
                    self.filter_setting = freq[2]
                    self.filter_bandwidth = freq[1] - freq[0]
                    found = 1
                    break
            if found == 0:
                self.filter_setting = filters[len(filters) - 1][2]
                self.filter_bandwidth = (filters[len(filters) - 1][1] -
                                         filters[len(filters) - 1][0])
                print("Warning: Total bandwidth is greater than any receiver "
                      "filter available:  Setting receiver filter to maximum")
            self.seq.add_param(self.mng, param_names[0], self.filter_setting)
            self.seq.add_param(self.mng, param_names[1], self.filter_setting)

        if self.config["receiver"] in NOTCH_FILTER:
            self.seq.add_param(self.mng, "notchFilter",
                               self.config["notchfilter"])
            if self.config["notchfilter"] != "Out":
                bad_freqs = self.freq_calc.compare_local_frame_freqs(
                    NOTCH_FILTER[self.config["receiver"]][0],
                    NOTCH_FILTER[self.config["receiver"]][1]
                )
                if bad_freqs:
                    print("WARNING: Frequencies adjusted to the local frame "
                          "and velocities fall within notch filter limits")
                    for freq in bad_freqs:
                        print ("Frequency = ", freq)

        if self.config["receiver"] in CHOPPER:
            if self.config["chopper"] == "on":
                self.seq.add_param(self.mng, "chopperCntl", "swOn")
            else:
                self.seq.add_param(self.mng, "chopperCntl", "swOff")

        # the if_freq_low high is used by IFRAck to determine its filters
        # is based on the center ifnom center freq not the computed one
        self.iffilter_center = self.freq_calc.get_ifcenter()
        self.if_freq_low = self.iffilter_center - (0.5 * bw_total)
        self.if_freq_high = self.iffilter_center + (0.5 * bw_total)

    def get_filter_setting(self):
        """Return receiver filters"""
        return self.filter_setting

    def get_filter_bandwidth(self):
        """Return bandwidth"""
        return self.filter_bandwidth

def quickRcvr1_2Test():

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
    
    # add these!  But how and why? TF
    config['polarization'] = 'XL'
    config['polswitch'] = 'cross'

    tuning = 1420.
    r = Receiver(config, tuning)

    print (r.seq.params)

def main():
    quickRcvr1_2Test()

if __name__ == '__main__':
    main()