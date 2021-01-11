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

import math

# from RcvrPF_1 import RcvrPF_1
from StaticDefs import IFFiltersToBandwidth
from StaticDefs import IFfilters
from StaticDefs import ReceiverGroup
from StaticDefs import ReceiverGroupPF
from StaticDefs import RCVR_IF_NOMINAL

from Manager import Manager

class IFRack(Manager):

    # def __init__(self, config_table, rcvr, ifpath, seq, prev_sws,
                 # all_backends):
    def __init__(self, config_table, ifSys, rcvrObj):             
        """Responsible for setting up all IFRack parameters"""
        super(IFRack, self).__init__(config_table)

        self.mng = "IFRack"

        self.ifSys = ifSys
        paths = ifSys.ifPaths.paths
        self.receiver = config_table["receiver"]
        self.rcvr = rcvrObj  # the receiver object, not its name
        self.opt_drvr = []
        # self.prev_sws = prev_sws
        # self.seq = MySeq() #seq
        self.filter_value = "pass_all"
        self.iftarget = config_table["iftarget"]
        self.opt_drvr = self.get_optical_drivers(paths)

        self.switches_used = self.input_sw = self.cross_switches_used = None

        self.switches_used = self.get_ifrack_switches(paths)
        self.input_sw = self.get_ifrack_input_settings(paths)
        self.cross_switches_used = self.get_ifrack_cross_switches(paths)
        # if "IFRouter" in ifpath.get_list():
        # self.set_if_filters(self.rcvr, ifpath, config_table)
        # self.set_if_filters(self.rcvr, paths, config_table)
        self.set_if_filters()
        self.set_ifrack_switches()

        all_backends = ['DCR']
        self.set_ifrack_power_level(config_table["backend"],
                                    config_table["receiver"], 3,
                                    config_table["bandwidth"], all_backends)
        # self.switches_used += self.prev_sws

    def get_optical_drivers(self, paths):
        ods = []
        for path in paths:
            for node in path.path:
                if "OpticalDriver" in node.name:
                    ods.append(node.deviceId)
        return ods
                    
    def get_ifrack_switches(self, paths):
        if self.switches_used is None:
            self.get_ifrack_settings(paths)
        return self.switches_used

    def get_ifrack_input_settings(self, paths):
        if self.input_sw is None:
            self.get_ifrack_settings(paths)
        return self.input_sw

    def get_ifrack_cross_switches(self, paths):
        if self.cross_switches_used is None:
            self.get_ifrack_settings(paths)
        return self.cross_switches_used

    def get_ifrack_settings(self, paths):

        self.switches_used = []
        self.cross_switches_used = []
        self.input_sw = {}

        for path in paths:
            # for node, j in map(None, path, range(len(path))):
            for j, node in enumerate(path.path):
                # if isinstance(node, str):
                if True:    
                    if "SWITCH" in node.name:
                        # sw, num = node.split("H")
                        # self.ifrack_sw_used.append(int(num))
                        # self.ifrack_sw_used.append(node.getPortNumber())
                        self.switches_used.append(node.deviceId)
                        nextNode = path.path[j+1]
                        if "IFXS" in nextNode.name:
                            # sw, num = path[j + 1].split("S")
                            # num = num.split(":")
                            # num = nextNode.getPortNumber()
                            # self.ifrack_cross_sw_used.append(num)
                            values = (str(nextNode.deviceId), nextNode.port)
                            self.cross_switches_used.append(values)
                    # find the IFrouter inputs
                    if "IFRouter" in node.name:
                        # name, conn = node.split(":")
                        # junk, num_str = node.split("J")
                        # num = int(num_str)
                        num = node.getPortNumber()
                        # input sw are the conn < 65
                        if num < 65:
                            # convert Connector number to sw number
                            sw_num = int((num - 1) / 8) + 1
                            self.input_sw[sw_num] = \
                                str((num - 1) % 8 + 1) 
        # print("switches used", self.switches_used)
        # print("cross switches used", self.cross_switches_used)
        # print("input_sw: ", self.input_sw)

    def set_laser_power(self):
        """Set the laser power on for ifrack paths in use"""
        sws = []
        for sw in self.switches_used:
            # switches_used can have redundencies, so send only 1 laser on cmd
            # per sw
            if sw not in sws:
                self.seq.add_param(self.mng, "laser_power," + str(sw), "swOn")
                self.seq.add_param(self.mng,
                                   "balance_select,driver" + str(sw), "1")
                self.seq.remove_param([self.mng,
                                       "balance_select,driver" + str(sw), "0"])
                sws.append(sw)
            # turn the balance_select to off for the ones not in use

        for i in range(1, 9):
            if i not in sws:  # or i not in self.prev_sws:
                self.seq.add_param(self.mng,
                                   "balance_select,driver" + str(i), "0")

    def set_ifrack_power_level(self, be, rcvr, level, bw, all_backends):
        """
        Set the value of the analog_power_level parameter based on the
        backend, IF bandwidth, user supplied bandwidth and levels (if ACS)
        """
        ifbw = IFFiltersToBandwidth[self.get_filter_value()]
        if self.iftarget is None:
            if "RcvrArray18_26" in self.receiver:
                value = "5.0"
            elif ("Rcvr68_92" in self.receiver or
                    "RcvrArray75_115" in self.receiver):
                value = "1.5"
            elif "VEGAS" == be and "GUPPI" not in all_backends:
                value = "3.0"
            # For dual operation of VEGAS/GUPPI, set value to 1.0
            # (might be changed)
            elif "VEGAS" == be and "GUPPI" in all_backends:
                value = "1.0"
            elif "GUPPI" not in all_backends:
                value = "1.0"
            elif "GUPPI" in all_backends and bw >= 100:
                value = "1.0"
            elif bw >= 200:
                value = "1.0"
            elif rcvr in ReceiverGroup:
                rcvrGroup = ReceiverGroup[rcvr]
                value = rcvrGroup[ifbw][level]
            elif self.receiver == "Holography":
                value = "1"
            else:  # PF receiver
                rcvr_bw = self.rcvr.get_filter_bandwidth()
                value = ReceiverGroupPF[rcvr_bw][level]
        else:  # user specified target level
            value = str(self.iftarget)
        for i in range(1, 9):
            param = "analog_power_level,{}".format(i)
            self.seq.add_param(self.mng, param, value)
        self.target = value

    def set_if_filters(self):

        centerFreq = RCVR_IF_NOMINAL[self.rcvr.rxName]

        totalBWLow = centerFreq - (self.ifSys.bwTotal*.5)
        totalBWHigh = centerFreq + (self.ifSys.bwTotal*.5)

        for path in self.ifSys.ifPaths.paths:
            filterValue = "pass_all"
            for fv, fLow, fHigh in IFfilters:
                if fLow <= totalBWLow and fHigh >= totalBWHigh:
                    filterValue = fv
                    # print("print found good filter at", filter_value, fLow, fHigh)
                    break

            opticalDriver = path.getFirstLikeDeviceNode("OpticalDriver")
            if opticalDriver is not None:
                param = "filter_select,%d" % opticalDriver.deviceId
                self.seq.add_param(self.mng, param, filterValue)

    def set_if_filters_oldstyle(self, rcvr, ifpath, config_table):
        """Set IF filters"""
        total_bw_low, total_bw_high = rcvr.get_if_freq_range()
        total_bw_low = math.ceil(total_bw_low)
        total_bw_high = math.floor(total_bw_high)
        if 0 == isinstance(rcvr, RcvrPF_1):
            for f in IFfilters:
                self.filter_value = "pass_all"
                if f[1] <= total_bw_low and f[2] >= total_bw_high:
                    self.filter_value = f[0]
                    break
        for x in map(None, self.opt_drvr):
            fs = "filter_select,{}".format(x)
            self.seq.add_param(self.mng, fs, self.filter_value)

    def set_if_filters_what(self, rcvr, ifpath, config_table):
        """Set IF filters"""
        # TBF interim solution, is IFrack bw part of path list or not?
        # Some backends yes, some backends no.
        usingNewPaths = False
        iffilter_center = self.rcvr.iffilter_center
        for path in ifpath.ifpathList:
            self.filter_value = "pass_all"
            if "ifrack_bw" in path:
                usingNewPaths = True
                total_bw_low = iffilter_center - (0.5 * path["ifrack_bw"])
                total_bw_high = iffilter_center + (0.5 * path["ifrack_bw"])
                total_bw_low = math.ceil(total_bw_low)
                total_bw_high = math.floor(total_bw_high)
                if 0 == isinstance(rcvr, RcvrPF_1):
                    for f in IFfilters:
                        if f[1] <= total_bw_low and f[2] >= total_bw_high:
                            self.filter_value = f[0]
                            break
                if "opticalDriver" in path:
                    filterNum = path["opticalDriver"]
                    fs = "filter_select,{}".format(filterNum)
                    self.seq.add_param(self.mng, fs, self.filter_value)

        # use old style, DCR or spp, or spectrometer backend in use
        if not usingNewPaths:
            self.set_if_filters_oldstyle(rcvr, ifpath, config_table)

    def set_ifrack_switches(self):
        """Set ifrack switches"""
        for sw in self.cross_switches_used:
            self.seq.add_param(self.mng, "S" + sw[0], sw[1])

        for key in self.input_sw:
            self.seq.add_param(self.mng, "S" + str(key), self.input_sw[key])

    def get_filter_value(self):
        return self.filter_value

    def get_opt_drvr(self):
        """Return the optical drivers in use"""
        return self.opt_drvr

    def get_target_level(self):
        return self.target
