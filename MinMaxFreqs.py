class MinMaxFreqs:

    def __init__(self, minf=None, maxf=None, bw=None):
        self.minf = minf
        self.maxf = maxf
        self.bw = bw # max bw

    def setMinMax(self, f):
        self.setMin(f)
        self.setMax(f)

    def setMin(self, f):
        if self.minf is not None:
            if self.minf > f:
                self.minf = f
        else:
            self.minf = f  

    def setMax(self, f):
        if self.maxf is not None:
            if self.maxf < f:
                self.maxf = f
        else:
            self.maxf = f

    def setBW(self, bw):
        if self.bw is not None:
            if self.bw < bw:
                self.bw = bw
        else:
            self.bw = bw

    def avgFreqs(self):
        if self.minf is None or self.maxf is None:
            return None
        return (self.minf + self.maxf) / 2.0
            
    def computeBW(self, bw=None):
        bw = self.bw if bw is None else bw
        return (self.maxf - self.minf + bw)

    def __str__(self):
        return "%s - %s (%s)" % (self.minf, self.maxf, self.bw) 