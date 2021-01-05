# python2 code for reading config tools pickle file
# for a given receiver and converting it to a text file
# readable in python3

import cPickle

def pkl2txtConfigLog(fn):
    """
    Converts python 2 pickle with dict of this struct:
        {
            "manager": {"param": "value\n"}
        }
    To a text file of
    manager param value\n    
    """

    with open(fn, 'r') as f:
        d = cPickle.load(f)

    lines = []
    for manager, values in d.items():
        for paramName, value in values.items():
            line = "%s %s %s" % (manager, paramName, value)
            lines.append(line)

    fn2 = "%s.txt" % fn
    
    f2 = open(fn2, 'w')

    for line in lines:
        f2.write(line)

    f2.close()
            
def pkl2txt(fn, rx):

    with open(fn, 'r') as f:
        d = cPickle.load(f)

    # keys for each receiver
    dr = d[rx]
    # this should be a list of strings;
    # save them to a txt file so
    # we can read them in python 3
    fn2 = "%s.%s.txt" % (fn, rx) 
    f2 = open(fn2, 'w')

    for path in dr:
        f2.write(str(path) + '\n')   

    f2.close()

def unitTestPkl2txt():
    rxs = ["RcvrPF_1"]
    fn = "test_pkl"
    for rx in rxs:
        pkl2txt(fn, rx)

def rcvrs2txt():
    rxs = [
        "RcvrPF_1", 
        "Rcvr1_2",
        "Rcvr2_3",
        "Rcvr4_6",
        "Rcvr8_10",
        "Rcvr12_18",
        "RcvrArray18_26",
        "Rcvr26_40",
        "RcvrArray75_115"
    ]
    fn = "zdb.201118.pkl"
    for rx in rxs:
        pkl2txt(fn, rx)

def configLogs2txt():
    # rxs = ["Rcvr342", "Rcvr1_2", "Rcvr2_3", "Rcvr4_6", "Rcvr8_10", "Rcvr12_18"]
    rxs = ["RcvrArray18_26", "Rcvr26_40", "RcvrArray75_115"]
    for rx in rxs:
        fn = "configLogs/%sConfigLog" % rx
        pkl2txtConfigLog(fn)

def main():
    #rx = "RcvrPF_1"
    #rx = "Rcvr1_2"
    # configLogs2txt()
    # unitTestPkl2txt()
    rcvrs2txt()
    
if __name__ == "__main__":
    main()
