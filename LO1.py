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

import string

# from gbt.ygor import getConfigValue

from StaticDefs import vframe
from Manager import Manager


class LO1(Manager):

    # def __init__(self, config_table, freq_calc, rcvr, seq, ifpath):
    def __init__(self, config_table, tuning_freq, center_freq, velocity, vdef, s12_value=None):
        """
        Responsible for setting up the L01 parameters that are computed from
        the configuration keyword values
        """
        # need
        # tuning_freq, velocity, vdef, center_freq

        super(LO1, self).__init__(config_table)

        self.mng_name = "LO1"
        # self.seq = MySeq()
        self.delta = 0
        self.velframe = None
        self.vdef = config_table["vdef"]
        self.swtype = config_table["swtype"]
        if "CCB" not in config_table["backend"]:
            self.rcvr_name = config_table['receiver'] #rcvr.mng
            self.number_switching_periods = 0
            self.set_freq_params(config_table["DOPPLERTRACKFREQ"])
            self.be = config_table["backend"]
            # self.set_velocity_params(config_table, freq_calc)
            self.set_velocity_params(config_table, velocity, vdef)
            self.set_switching_params(config_table)
            # self.tuning_freq = freq_calc.get_tuning_freq()
            self.tuning_freq = tuning_freq
            self.center_freq = "0"
            # self.set_if_center_freq(freq_calc)
            self.set_if_center_freq(center_freq)
            # self.set_sw(ifpath, config_table["phasecal"])
            self.set_sw(config_table["phasecal"], s12_value=s12_value)
            # self.set_lo1b(freq_calc, ifpath, rcvr)
            self.set_lo1b()
            # self.set_lo1b_off()

            if "RcvrArray18_26" in config_table["receiver"]:
                self.seq.remove_param(("LO1", "autoSetLOPowerLevel", "1"))
                self.seq.add_param(self.mng_name, "testTonePowerLevel",
                                   "10", 4)
                self.seq.add_param(self.mng_name, "loPowerLevel", "12", 4)
                self.seq.add_param(self.mng_name, "autoSetLOPowerLevel",
                                   "0", 3)
        else:
            if "RcvrArray18_26" not in config_table["receiver"]:
                self.set_lo1ab_off()

    # def set_sw(self, ifpath, phasecal):
    def set_sw(self, phasecal, s12_value=None):
        """Set the lo to the receiver switches S12, and (S13 or S14 or S15)"""
        s12_value = 3 if s12_value is None else s12_value
        # TBF: we'll have to look at the LO pickled data to
        # determine the switches being used

        # switches = ifpath.get_lo_sw()
        # for sw in switches:
        #     self.seq.add_param(self.mng_name, sw[0], sw[1])
        #     if sw[0] == "S13":
        #         s12_value = "4"
        # self.seq.add_param(self.mng_name, "S12", str(s12_value))

        if phasecal in ["on"]:
            self.seq.add_param(self.mng_name, "S1", "cross")
            self.seq.add_param(self.mng_name, "S11", "thru")
            self.seq.add_param(self.mng_name, "S3", "4")
            self.seq.add_param(self.mng_name, "phaseCalMode", phasecal)
            self.seq.add_param(self.mng_name, "phaseCalCtl", "On")
        elif phasecal in ["M1-disconnect", "M5-disconnect"]:
            self.seq.add_param(self.mng_name, "S1", "cross")
            self.seq.add_param(self.mng_name, "S11", "cross")
            self.seq.add_param(self.mng_name, "S3", "4")
            self.seq.add_param(self.mng_name, "phaseCalMode", phasecal[0:2])
            self.seq.add_param(self.mng_name, "phaseCalCtl", "On")
        elif phasecal in ["M1", "M5"]:
            self.seq.add_param(self.mng_name, "S3", "4")
            self.seq.add_param(self.mng_name, "S1", "cross")
            self.seq.add_param(self.mng_name, "S11", "thru")
            self.seq.add_param(self.mng_name, "phaseCalMode", phasecal)
            self.seq.add_param(self.mng_name, "phaseCalCtl", "On")
        else:
            self.seq.add_param(self.mng_name, "S3", "3")
            self.seq.add_param(self.mng_name, "S1", "cross")
            self.seq.add_param(self.mng_name, "S11", "cross")
            self.seq.add_param(self.mng_name, "phaseCalCtl", "Off")

        if self.rcvr_name not in ("Rcvr26_40", "RcvrArray18_26", "Rcvr68_92"):
            self.seq.add_param(self.mng_name, "loConfig", "TrackA_BNotUsed", 1)
            self.seq.add_param(self.mng_name, "testTonePowerLevel", "-110", 4)
            self.seq.add_param(self.mng_name, "testToneFreq", "17000", 1)

    def set_lo1ab_off(self):
        """Remove LO1 paths for CCB configurations to stop unwanted effects"""
        self.seq.add_param(self.mng_name, "testTonePowerLevel", "-110", 4)
        self.seq.add_param(self.mng_name, "loPowerLevel", "-110", 1)
        self.seq.add_param(self.mng_name, "autoSetLOPowerLevel", "0", 3)
        self.seq.add_param(self.mng_name, "S4", "4")
        self.seq.add_param(self.mng_name, "S8", "5")
        self.seq.add_param(self.mng_name, "S12", "1")

    def read_config_file(self, filename):
        """Read the lo1 pwr levels from the receiver conf file"""
        self.LO1_pwr = []
        self.LO1_freq_pwr = []
        fd = open(filename, "r")
        for line in fd:
            if line[0:8] == "LO1pwr.N":
                trash, num = line.split("=")
                self.num_pwr_readings = string.atoi(num)
                break
        for i in range(0, self.num_pwr_readings):
            self.LO1_pwr.append(0)
            self.LO1_freq_pwr.append(0)

        for line in fd:
            if line[0:7] == "LO1pwr[":
                ind = line.find("frequency")
                if ind != -1:
                    trash, num = line.split("[")
                    index, trash = num.split("]")
                    trash, freq = line.split("=")
                    index = string.atoi(index)
                    freq.lstrip()
                    self.LO1_freq_pwr[index] = string.atof(freq)
                else:
                    ind = line.find("power")
                    if ind != -1:
                        trash, num = line.split("[")
                        index, trash = num.split("]")
                        index = string.atoi(index)
                        trash, pwr = line.split("=")
                        pwr.lstrip()
                        self.LO1_pwr[index] = string.atof(pwr)

    def set_lo1b_off(self):
        "For most receivers"
        self.seq.add_param(self.mng_name, "loConfig", "TrackA_BNotUsed", 1)
        self.seq.add_param(self.mng_name, "S10", "2")        

    # def set_lo1b(self, freq_calc, ifpath, rcvr):
    def set_lo1b(self):
        """Set lo1b if required in config"""
        freq_units = 1
        power_units = 1
        intpol_units = 1
        power = 10
        mindist = 10000000
        if self.rcvr_name == "RcvrArray18_26":
            lo1b_value = freq_calc.get_lo1b()
            self.seq.add_param(self.mng_name, "testToneFreq",
                               str(lo1b_value), 1)
            self.seq.add_param(self.mng_name, "testTonePowerLevel",
                               str(power), 4)
            self.seq.add_param(self.mng_name, "S8", "5", 1)
            # if only type 2 beams are being used then completely disconnect
            # the Lo1B signal to stop signals from the unused
            # idm type 1 kfpa beam atrributing signal strength so that it is
            # possible to balance this path
            # Note: The setting of loConfig must match the S10 setting below.
            # The LO1 coordinator has an S10 dependency method which sets S10
            # based on loConfig. (Hence the setting of S10 is redundant.)
            if 1 not in rcvr.get_idmtypes():
                self.seq.add_param(self.mng_name, "S10", "2")
                self.seq.add_param(self.mng_name, "loConfig", "TrackA_BNotUsed", 1)
            else:
                self.seq.add_param(self.mng_name, "S10", "1")
                self.seq.add_param(self.mng_name, "loConfig", "TrackA_TToneB", 1)

        elif self.rcvr_name in ("Rcvr26_40", "Rcvr68_92"):
            # reset switch for LO1B because these rcvrs use it
            self.seq.add_param(self.mng_name, "loConfig", "TrackA_TToneB", 1)
            self.seq.add_param(self.mng_name, "S10", "1")
            # mmc_sw = freq_calc.get_filter()
            # if mmc_sw != "F2_8":
            #     MMConvFile = (getConfigValue("/home/gbt", "YGOR_TELESCOPE") +
            #                   "/etc/config/MMConverter.conf")
            #     self.read_config_file(MMConvFile)
            #     lo1b_value = freq_calc.get_lo1b()
            #     self.seq.add_param(self.mng_name, "testToneFreq",
            #                        str(lo1b_value), 1)
            #     self.seq.add_param(self.mng_name, "loConfig",
            #                        "TrackA_TToneB", 1)
            #     if lo1b_value >= self.LO1_freq_pwr[self.num_pwr_readings - 1]:
            #         power = self.LO1_pwr[self.num_pwr_readings - 1]
            #     elif lo1b_value <= self.LO1_freq_pwr[0]:
            #         power = self.LO1_pwr[0]
            #     else:
            #         for i in range(0, self.num_pwr_readings):
            #             freq_diff = abs((lo1b_value) - self.LO1_freq_pwr[i])
            #             if freq_diff < mindist:
            #                 ind = i
            #                 mindist = freq_diff
            #                 power = self.LO1_pwr[i]
            #         if ind != self.num_pwr_readings:
            #             if lo1b_value - self.LO1_freq_pwr[ind] > 0:
            #                 freq_diff = (self.LO1_freq_pwr[ind + 1] -
            #                              self.LO1_freq_pwr[ind])
            #                 freq_units = (self.LO1_freq_pwr[ind + 1] -
            #                               self.LO1_freq_pwr[ind])
            #                 power_units = (self.LO1_pwr[ind + 1] -
            #                                self.LO1_pwr[ind])
            #                 if power_units != 0:
            #                     intpol_units = power_units / freq_units
            #                     power = (self.LO1_pwr[ind] +
            #                              intpol_units * freq_diff)
            #             elif lo1b_value - self.LO1_freq_pwr[ind] < 0:
            #                 power_units = (self.LO1_pwr[ind] -
            #                                self.LO1_pwr[ind - 1])
            #                 if power_units != 0:
            #                     intpol_units = power_units / freq_units
            #                     power = (self.LO1_pwr[ind] -
            #                              intpol_units * freq_units)

            #     self.seq.add_param(self.mng_name, "testTonePowerLevel",
            #                        str(power), 3)
            #     self.seq.add_param(self.mng_name, "S8", "3", 1)
            # elif self.rcvr_name in ("Rcvr68_92"):
            #     self.seq.add_param(self.mng_name, "loConfig",
            #                        "TrackA_BNotUsed", 1)
            #     self.seq.add_param(self.mng_name, "testTonePowerLevel",
            #                        "-110", 4)
            #     self.seq.add_param(self.mng_name, "testToneFreq", "17000", 1)
            if self.rcvr_name in ("Rcvr26_40"):
                self.seq.add_param("LO1,MMConverterCrd", "sw1", "2", 1)
            else:
                self.seq.add_param("LO1,MMConverterCrd", "sw1", "1", 1)
            # self.seq.add_param("LO1,MMConverterCrd", "filter", mmc_sw, 1)

        else:  # disconnect lo1b thru s10 for rcvrs that do not use it
            self.seq.add_param(self.mng_name, "loConfig", "TrackA_BNotUsed", 1)
            self.seq.add_param(self.mng_name, "S10", "2")

    def set_freq_params(self, freq):
        """Add the freqeuncy parameter to the needs update list"""
        self.seq.add_param(self.mng_name, "restFrequency", str(freq), 1)

    def set_velocity_params(self, config_table, velocity, vdef): #freq_calc):
        """Sets avg velocity and add velocity param to "needs update" list"""
        # self.velocity, self.vdef = freq_calc.get_velocity()
        self.velocity = velocity 
        self.vdef = vdef
        self.seq.add_param(self.mng_name, "velocityDefinition", self.vdef, 1)
        self.seq.add_param(self.mng_name, "sourceVelocity,1,theVelocity,pos",
                           str(self.velocity), 1)
        self.seq.add_param(self.mng_name, "sourceVelocity,1,theVelocity,vel",
                           "0", 1)
        self.seq.add_param(self.mng_name, "sourceVelocity,1,theVelocity,acl",
                           "0", 1)
        self.velframe = vframe[config_table["vframe"]]
        self.seq.add_param(self.mng_name, "restFrame", self.velframe, 1)

    def get_velocity(self):
        """Created for unit tests: just returns average velocity"""
        return self.velocity

    def get_velframe(self):
        """Created for unit tests: just returns mapped velocity frame"""
        return self.velframe

    def get_number_switching_periods(self):
        """Created for unit tests: just returns mapped velocity frame"""
        return self.number_switching_periods

    def set_switching_params(self, config_table):
        """Add the switching parameters to the needs update list"""
        self.set_number_switching_periods(config_table)
        if self.swtype == "fsw":
            for i in range(1, len(self.delta) + 1):
                sd = "switchDeltas,{}".format(i)
                self.seq.add_param(self.mng_name, sd, str(self.delta[i - 1]))
        else:
            self.seq.add_param(self.mng_name, "switchDeltas,1",
                               str(self.delta))

    def get_switch_deltas(self):
        """Created for unit tests: just returns computed delta"""
        return self.delta

    # def set_if_center_freq(self, freq_calc):
    def set_if_center_freq(self, center_freq):
        """Get the center freq from freq_calc and then sets the param"""
        # self.center_freq = freq_calc.get_center_freq()
        self.center_freq = center_freq
        self.seq.add_param(self.mng_name, "ifCenterFreq",
                           str(self.center_freq), 1)

    def set_number_switching_periods(self, config):
        """Set the internal state of the switching periosds and delta"""
        if config["swmode"] == "sp":
            self.number_switching_periods = 4
        elif config["swmode"] == "tp_nocal":
            self.number_switching_periods = 1
        else:
            self.number_switching_periods = 2

        if config["swtype"] == "fsw":
            self.delta = config["swfreq"]
        else:
            self.delta = 0.0

    def get_center_freq(self):
        return self.center_freq

def quickTest():

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
    # config['polarization'] = 'XL'
    # config['polswitch'] = 'cross'
    tuning = 1420.
    config['DOPPLERTRACKFREQ'] = tuning
    config['phasecal'] = 'on'

    r = LO1(config, tuning, 0., 0., 0.)

    print (r.seq.params)    
def main():
    quickTest()
if __name__ == '__main__':
    main()