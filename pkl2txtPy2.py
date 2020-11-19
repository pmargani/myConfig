# python2 code for reading config tools pickle file
# for a given receiver and converting it to a text file
# readable in python3

import cPickle

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

def main():
    #rx = "RcvrPF_1"
    #rx = "Rcvr1_2"
    rxs = ["RcvrPF_1", "Rcvr1_2", "Rcvr2_3", "Rcvr4_6", "Rcvr8_10"]
    fn = "zdb.201118.pkl"
    for rx in rxs:
        pkl2txt(fn, rx)

if __name__ == "__main__":
    main()
