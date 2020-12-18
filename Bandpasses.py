def overlap(s1, e1, s2, e2):
    "Returns overlap between two ranges"
    # print "overlaps:"
    # print s1, e1
    # print s2, e2
    # check for end points in the wrong order
    if (s1 > e1):
        tmp = e1
        e1 = s1
        s1 = tmp
    if (s2 > e2):
        tmp = e2
        e2 = s2
        s2 = tmp

    # 1. first range is entirely in second
    if s1 >= s2 and e1 <= e2:
        return e1 - s1, s1, e1
    # 2. first range encompasses second
    if s1 <= s2 and e1 >= e2:
        return e2 - s2, s2, e2
    # 3. first range begins before second but overlaps
    if s1 <= s2 and e1 > s2 and e1 < e2:
        return e1 - s2, s2, e1
    # 4. first range begins before second ends, but overlaps
    if s1 >= s2 and s1 < e2 and e1 > e2:
        return e2 - s1, s1, e2

    # no overlap
    return 0.0, None, None

class Bandpasses:

    def __init__(self, bandpasses):

        self.bandpasses = bandpasses
        self.getRange()

        self.freqCols = 80
        self.freqPerCol = (self.hi - self.lo) / self.freqCols

    
    def getNumBandpasses(self):
        return len(self.bandpasses)

    def getRange(self):
    
        self.lo = min([bp.lo for bp in self.bandpasses])
        self.hi = max([bp.hi for bp in self.bandpasses])


    def show(self):
    
        self.getRange()

        self.freqPerCol = (self.hi - self.lo) / self.freqCols
        # print "range: ", self.lo, self.hi
        # print "freqPerCol: ", self.freqPerCol

        for bp in self.bandpasses:
            loFreqStart = bp.lo - self.lo
            hiFreqStart = bp.hi - self.lo
            loCol = int(loFreqStart/self.freqPerCol)
            hiCol = int(hiFreqStart/self.freqPerCol)
            # import ipdb; ipdb.set_trace()
            rng = " " * (loCol)
            rng += "<"
            rng += "*" * (hiCol - loCol)
            rng += ">"
            rng += " " * (self.freqCols - hiCol)
            rng += "\n"
            print (bp, " change: ", bp.changes)
            print (rng)

class Bandpass:

    def __init__(self, lo=None, hi=None, target=None):

        # all in MHz
        self.lo = lo
        self.hi = hi
        self.target = target
        self.order()
        if lo is not None and hi is not None:
            self.bw = self.hi - self.lo 
            self.center = self.lo + (self.bw/2.)
        else:
            self.bw = None
            self.center = None

        self.labelWidth = (7*3) + 3 + 2

        # holding place for an annotation
        self.change = None
        self.changes = None

        self.debug = False

        # print self.__str__()

    def __str__(self):
        lo = 'None' if self.lo is None else "%5.2f" % self.lo
        hi = 'None' if self.hi is None else "%5.2f" % self.hi
        bw = 'None' if self.bw is None else "%5.2f" % self.bw
        t = 'None' if self.target is None else "%5.2f" % self.target
        return "%s to %s (%s): %s" % (lo, hi, bw, t) 

    def label(self):
        lo = 'None' if self.lo is None else "%5.2f" % self.lo
        hi = 'None' if self.hi is None else "%5.2f" % self.hi
        t = 'None' if self.target is None else "%5.2f" % self.target
        return "%-7s - %-7s: %-7s" % (lo, hi, t) 

    def __eq__(self, other):
        return self.lo == other.lo and \
            self.hi == other.hi and \
            self.target == other.target

    def isInband(self):
        return self.target >= self.lo and self.target <= self.hi

    def mix(self, mixFreq, lowerSideband=True):

        if lowerSideband:
            self.mixDown(mixFreq)
        else:
            self.mixUp(mixFreq)

    def filter(self, loFilter, hiFilter):
        "Filter this bandpass by the given range"

        # self.bw, self.lo, self.hi = overlap(loFilter, hiFilter, self.lo, self.hi)
        bw, lo, hi = overlap(loFilter, hiFilter, self.lo, self.hi)

        if lo is None or hi is None:
            print ("ERROR in filter ", loFilter, hiFilter)
            print (self.__str__())
            return

        self.lo = lo
        self.hi = hi
        self.bw = bw
        self.center = self.lo + (self.bw/2.)
        # if self.debug:
            # print "After filter:", self.lo, self.hi, self.target

        # TBF: not sure about this:
        # if our target freq is now not in range,
        # the new target becomes the center of the band.
        if not self.isInband():
            # if self.debug:
                # print "Filtering changed target freq to: ", self.center
            self.target = self.center

    def mixDown(self, mixFreq):
        "Mix bandpass with given frequency, lower sideband"
        self.lo = mixFreq - self.lo
        self.hi = mixFreq - self.hi
        self.target = mixFreq - self.target
        self.order()

    def mixUp(self, mixFreq):
        "Mix bandpass with given frequency, upper sideband"
        # TBF: what the hell?
        # self.lo =  self.lo - mixFreq
        # self.hi =  self.hi - mixFreq
        # self.target =  self.target - mixFreq
        self.lo = mixFreq - self.lo
        self.hi = mixFreq - self.hi
        self.target = mixFreq - self.target        
        self.order()

    def order(self):
        "Make sure we always have lo < hi"
        if self.lo > self.hi:
            tmp = self.lo
            self.lo = self.hi
            self.hi = tmp

