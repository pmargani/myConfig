from Manager import Manager

class DCR(Manager):

    "Responsible for turning config and if path info into DCR params"

    def __init__(self, config, paths):

        super(DCR, self).__init__(config)

        self.paths = paths
        self.numChannels = 16
        self.mgrName = 'DCR'

    def findDCRParams(self):
        "Convert config and if path info into parameters"        

        # last node of each path tells us what channels to select
        selectedPorts = []
        banks = []
        for path in self.paths:
            backendNode = path[-1]
            assert backendNode.type == 'Backend'
            assert backendNode.device == self.mgrName
            selectedPorts.append(backendNode.getPortNumber())
            banks.append(backendNode.getBankName())

        # DCR Channel,11 0
        # DCR Bank Bank_A

        for i in range(1, self.numChannels+1):
            onBool = i in selectedPorts  
            on = 1 if onBool else 0
            # TBF: we can't check each DCR channel because of the
            # arbitrary difference in paths taken between our code
            # and production!
            # params.append(('DCR,Channel,%d' % i, on))
            self.seq.add_param(self.mgrName, 'Channel,%d' %i, on)


        # TBF: handle better
        self.seq.add_param(self.mgrName, 'Bank', "Bank_%s" % banks[0])

        self.seq.add_param(self.mgrName, 'CyclesPerIntegration', 1)
