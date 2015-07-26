#!/usr/bin/python
# This is check_authlogs.py
# Author: Julien Boisdequin boisdequin.julien@gmail.com
####################################################################

import sys
import getopt

status = { 'OK' : 0 , 'WARNING' : 1, 'CRITICAL' : 2 , 'UNKNOWN' : 3}

def print_usage():
    print "USAGE: "+sys.argv[0]
    print "-r | --rsa  : RSA key fingerprint allowed to connect through ssh (ssh-keygen -lf /path/to/ssh/key)"
    print "-u | --user : User allowed to connect through ssh"
    print "-h | --help : display this help information and exit"
    print "example: "+sys.argv[0]+" -r a4:f4:de:0f:10:0f:17:fb:cb:c8:3e:f7:5a:eb:b8:79 -u julien"
    sys.exit(status['UNKNOWN'])

if len(sys.argv) != 5:
  print_usage()

# users

def usage(argv):
   try:
      opts, args = getopt.getopt(argv,"hr:u:",["rsa=", "users="])
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
      elif opt in ("-u", "--user"):
         global allowed_user
         allowed_user = arg
         
if __name__ == "__main__":
   usage(sys.argv[1:])

sshStatus = 3
loginStatus = 3

logs = "/var/log/auth.log"

#1 check that there's only a single fingerprint allowed
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
allowed_users = []
allowed_users.append(allowed_user)

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

#EOF