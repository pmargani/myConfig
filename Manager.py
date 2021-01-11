class MySeq:
    "Fakes the config tools Sequencer class"

    def __init__(self):
        self.params = []

    def add_param(self, mgr, name, value, seq=None):
        self.params.append((mgr, name, value))

    def remove_param(self, x): #mgr, name, value):
        # self.params.remove((mgr, name, value))
        if x[0] in self.params:
            self.params.remove(x[0]) 

class Manager:

    """
    An base class for classes that convert configurations into
    parameter key value pairs
    """

    def __init__(self, config_table):
        self.config = config_table
        self.seq = MySeq()        

    def getParams(self, triplet=False):
        if triplet:
            return self.seq.params
        params = []   
        # convert 3 tuple to 2 tuple
        for mgr, param, value in self.seq.params:
            params.append(("%s,%s" % (mgr, param), value))
        return params   
