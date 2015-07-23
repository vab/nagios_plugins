#!/usr/bin/python
# This is check_authlogs.py
# Author: Julien Boisdequin boisdequin.julien@gmail.com
####################################################################

import sys
import getopt

status = { 'OK' : 0 , 'WARNING' : 1, 'CRITICAL' : 2 , 'UNKNOWN' : 3}

if len(sys.argv) != 3:
    print "USAGE: "+sys.argv[0]
    print "-f : path/to/lsyncd/logfile"
    sys.exit(status['UNKNOWN'])

def usage(argv):
   try:
      opts, args = getopt.getopt(argv,"hf:",["file="])
   except getopt.GetoptError:
      print sys.argv[0]+' -f <path/to/lsyncd/logfile>'
      sys.exit(status['UNKNOWN'])
   for opt, arg in opts:
      if opt == '-h':
         print sys.argv[0]+' -f <path/to/lsyncd/logfile>'
         sys.exit(status['UNKNOWN'])
      elif opt in ("-f"):
         global logfile
         logfile = arg

if __name__ == "__main__":
   usage(sys.argv[1:])

if 'rsync error' in open(logfile).read():
  print "CRITICAL: Error in lsyncd logs: "+logfile
  sys.exit(status['CRITICAL'])
else:
  print 'OK. No error in Lsyncd logs'
  sys.exit(status['OK'])