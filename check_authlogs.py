#!/usr/bin/python
# This is check_authlogs.py
# Author: Julien Boisdequin boisdequin.julien@gmail.com
####################################################################

import sys
import getopt

status = { 'OK' : 0 , 'WARNING' : 1, 'CRITICAL' : 2 , 'UNKNOWN' : 3}

if len(sys.argv) != 3:
    print "USAGE: "+sys.argv[0]
    print "-r | --rsa  : RSA key fingerprint (ssh-keygen -lf /path/to/ssh/key)"
    print "-h | --help : display this help information and exit"
    print "example: "+sys.argv[0]+" -r d8:d5:f3:5a:7e:27:42:91:e6:a5:e6:9e:f9:fd:d3:ce"
    sys.exit()

# users

def usage(argv):
   try:
      opts, args = getopt.getopt(argv,"hr:")
   except getopt.GetoptError:
      print sys.argv[0]
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h' or '--help':
         print "USAGE: "+sys.argv[0]
         print "-r          : RSA key (ssh-keygen -lf /path/to/ssh/key)"
         print "-h | --help : display this help information and exit"
         print "example: "+sys.argv[0]+" -r d8:d5:f3:5a:7e:27:42:91:e6:a5:e6:9e:f9:fd:d3:ce"
         sys.exit()
      elif opt in ("-r"):
         global RSA
         RSA = arg

def usage(argv):
   try:
      opts, args = getopt.getopt(argv,"hr:",["rsa="])
   except getopt.GetoptError:
      print sys.argv[0]+' -r <rsa key fingerprint>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print sys.argv[0]+' -r <rsa key fingerprint>'
         sys.exit()
      elif opt in ("-r", "--rsa"):
         global RSA
         RSA = arg
         
if __name__ == "__main__":
   usage(sys.argv[1:])

sshStatus = 3
loginStatus = 3

logs = "auth.log"

#1 check that there's only a single fingerprint allowed to ssh connect to awladmin
keys=[]
forbidden_keys=[]

for line in open(logs):
    if "Found matching RSA key" in line:
        keys.append(line.split('Found matching RSA key: ')[1].strip('\n'))

for key in keys:
    if key != RSA:
        sshStatus = 2
        forbidden_keys.append(key)
    else:
        sshStatus = 0

if not forbidden_keys:
    print 'OK: ssh login ok, ',
else:
    print 'CRITICAL: Another ssh key was found, fingerprint is: {}, '.format(key),

#2 check that factory is the only user who connects locally
allowed_users=['julien']
users_connected=[]
for line in open(logs):
    if "session opened for user" in line and "sudo" not in line and "cron" not in line:
        users_connected.append(line.strip('\n').split('session opened for user ')[1].split(' ')[0])

#print users_connected
forbidden_users = list(set(users_connected) - set(allowed_users))

if not forbidden_users:
    loginStatus = 0
    print 'OK: only user connects'
else:
    loginStatus = 2
    print 'CRITICAL: user {} connects'.format(forbidden_users)

if sshStatus + loginStatus == 0:
    sys.exit(status['OK'])
else:
    sys.exit(status['CRITICAL'])