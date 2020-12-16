# Copyright (C) 2012 Associated Universities, Inc. Washington DC, USA.
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

from math import sqrt


class Vdef:

    def __init__(self):
        """Helper: algorithms to calculate frequencies w.r.t. velocity def"""
        self.cur_freq_w_avg_vel = 0
        self.c_light = 299792.458

    def compute_local_frame_Red(self, v_high, freq, v_low):
        """Determine max velocity and min velocity with Redshifted defn"""
        self.cur_vhigh = freq / (1.0 + v_high)
        self.cur_vlow = freq / (1.0 + v_low)
        avg_vel = 0.5 * (v_high + v_low)
        self.cur_freq_w_avg_vel = freq / (1.0 + avg_vel)

    def compute_local_frame_Radio(self, v_high, freq, v_low):
        """Determine max velocity and min velocity in Radio defn"""
        avg_vel = 0.5 * (v_high + v_low)
        self.cur_vhigh = (freq * (1.0 - (v_high / self.c_light)))
        self.cur_vlow = (freq * (1.0 - (v_low / self.c_light)))
        self.cur_freq_w_avg_vel = freq * (1.0 - (avg_vel / self.c_light))

    def compute_local_frame_Optical(self, v_high, freq, v_low):
        """Determine max velocity and min velocity in Optical defn"""
        self.cur_vhigh = (freq * (1 / (1.0 + (v_high / self.c_light))))
        self.cur_vlow = (freq * (1 / (1.0 + (v_low / self.c_light))))
        avg_vel = 0.5 * (v_high + v_low)
        self.cur_freq_w_avg_vel = freq * (1 / (1.0 + avg_vel / self.c_light))

    def compute_local_frame_Relativistic(self, v_high, freq, v_low):
        """Determine max velocity and min velocity in Relativistic defn"""
        self.cur_vhigh = (freq * sqrt(1 - (v_high / self.c_light)**2) /
                          (1 + v_high / self.c_light))
        self.cur_vlow = (freq * sqrt(1 - (v_low / self.c_light)**2) /
                         (1 + v_low / self.c_light))

        v_avg = 0.5 * (v_high + v_low)
        self.cur_freq_w_avg_vel = (freq * sqrt(1 - (v_avg / self.c_light)**2) /
                                   (1 + v_avg / self.c_light))

    def compute_local_frame_with_vdef(self, vdef, v_high, freq, v_low):
        if vdef == "Red":
            self.compute_local_frame_Red(v_high, freq, v_low)
        elif vdef == "Radio":
            self.compute_local_frame_Radio(v_high, freq, v_low)
        elif vdef == "Optical":
            self.compute_local_frame_Optical(v_high, freq, v_low)
        elif vdef == "Relativistic":
            self.compute_local_frame_Relativistic(v_high, freq, v_low)
        else:
            raise NameError("vdef {} not defined".format(vdef))

    def get_vhigh(self):
        return self.cur_vhigh

    def get_vlow(self):
        return self.cur_vlow

    def get_vave(self):
        return self.cur_freq_w_avg_vel
