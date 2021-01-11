from copy import copy

from StaticDefs import DEF_ON_SYSTEMS, DEF_OFF_SYSTEMS, QD_AND_ACTIVE_SURFACE_ON_RCVRS
from StaticDefs import PFRCVRS, PF2RCVRS

from Manager import Manager

class ScanCoordinator(Manager):

    "Responsiple for turning config into into manager parameters"

    def __init__(self, config):
        super(ScanCoordinator, self).__init__(config)

        self.mgrName = 'ScanCoordinator'

        self.DEFAULT = 'Default'
        self.AS = 'ActiveSurface'
        self.QD = 'QuadrantDetector'

    def findParameterValues(self):

        self.findSubsystemSelectValues()

        # Misc stuff
        self.seq.add_param(self.mgrName, 'switching_signals_master', self.config['backend'])

        # TBF: Why?
        self.seq.add_param(self.mgrName, 'scanLength,seconds', 1)

    def findSubsystemSelectValues(self):

        # what's the default always on managers?
        onMgrs = copy(DEF_ON_SYSTEMS[self.DEFAULT])

        # then what's on for these observations?
        onMgrs.append(self.config['backend'])

        # convert PF receiver names to RcvrPF_1/2:
        # onMgrs.append(config['receiver'])
        rx = self.config['receiver']
        if rx in PFRCVRS:
            rx = 'RcvrPF_1'
        if rx in PF2RCVRS:
            rx = 'RcvrPF_2'
        onMgrs.append(rx)        

        # will the QD and Active Surface mgrs be on?
        qdActiveSurfaceOn = rx in QD_AND_ACTIVE_SURFACE_ON_RCVRS
        if qdActiveSurfaceOn:
            onMgrs.extend([self.QD, self.AS])

        # set params for those that are off, but maybe should be on?
        systems = copy(DEF_OFF_SYSTEMS[self.DEFAULT])
        if not qdActiveSurfaceOn:
            systems.extend([self.QD, self.AS])

        for mgr in systems:
            onBool = mgr in onMgrs
            on = 1 if onBool else 0
            # param = ('ScanCoordinator,subsystemSelect,%s' % mgr, on)
            # params.append(param)
            self.seq.add_param(self.mgrName, 'subsystemSelect,%s' % mgr, on)

        # make sure everything's covered
        params = []
        for mgr in onMgrs:
            param = (self.mgrName, 'subsystemSelect,%s' % mgr, 1)
            if param not in params:
                params.append(param)
                self.seq.add_param(self.mgrName, param[1], 1)
