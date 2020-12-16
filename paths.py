from IFPathNode import IFPathNode

def getPaths(fn):
    "Read paths from python 3 text file derived form python 2 pickle file"
    with open(fn, 'r') as f:
        ls = f.readlines()
    return [eval(l) for l in ls]

def getIFPaths(receiver, filepath=None):
    "Returns a list of paths from the pickled cabling file for given receiver"

    if filepath is None:
        fn = "zdb.pkl.%s.txt" % receiver
    else:
        fn = filepath

    ps = getPaths(fn)

    ifPaths = []
    ifPath = None

    for path in ps:
        #print(path)
        
        ifPath = []
        for p in path:
            pn = IFPathNode(p)
            ifPath.append(pn)

        ifPaths.append(ifPath)
        
    return ifPaths
    
def test1():

    rx = "Rcvr1_2"
    fn = "zdb.201118.pkl.%s.txt" % rx
    paths = getIFPaths(rx, filepath=fn)

    for path in paths:
        print(path)
        for p in path:
            print (p.name, p.device, p.deviceId, p.port, p.getPortNumber())
    print(len(paths))

    
            
def main():
    test1()

if __name__ == '__main__':
    main()            
            

