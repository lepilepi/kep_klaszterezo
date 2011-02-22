import sys,os
import getopt

argv=sys.argv[1:]
optlist, args = getopt.getopt(argv, ':vir:d')
optlist=dict(optlist)

verbose='-v' in optlist
interactive='-i' in optlist
num_of_repeats=int(optlist.get('-r') or 1)
num_of_clusters=optlist.get('-c') or None
draw='-d' in optlist
