#!/usr/bin/python
# coding: utf8
#
# This is check_speedtest_ping.py
#
# Author: Julien Boisdequin boisdequin.julien@gmail.com


from subprocess import Popen, PIPE, STDOUT
import sys, getopt
import apt

status = { 'OK' : 0 , 'WARNING' : 1, 'CRITICAL' : 2 , 'UNKNOWN' : 3}
exitCode=3

warning_ping=""
critical_ping=""
warning_download=""
critical_download=""
warning_upload=""
critical_upload=""

testtype=''

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def print_usage():
    print "USAGE: "+sys.argv[0]
    print "-t | --testtype : 'ping', 'download', 'upload' or all"
    print "-q | --wp             : Warning threshold for ping"
    print "-w | --cp             : Critical threshold for ping"
    print "-e | --wd             : Warning threshold for download "
    print "-r | --cd             : Critical threshold for download"
    print "-t | --wu             : Warning threshold for upload"
    print "-y | --cu             : Critical threshold for upload"
    print "example: "+sys.argv[0]+"-t all --wp 30 --cp 40 --wd 40 --cd 30 --wu 15 --wu 10"
    sys.exit(status['UNKNOWN'])

cache = apt.Cache()
if not cache['speedtest-cli'].is_installed:
    print "Install the package speedtest-cli (# apt-get install speedtest-cli)"
    sys.exit(status['UNKNOWN'])

if len(sys.argv) < 3:
   print_usage()

def usage(argv):
   try:
      opts, args = getopt.getopt(argv,"ht:q:w:e:r:t:y:",["type=","wp=","cp=","wd=","cd=","wu=","cu="])
   except getopt.GetoptError:
      print_usage()
   for opt, arg in opts:
      if opt == '-h':
         print sys.argv[0]+' -t <test_type>'
         sys.exit(status['UNKNOWN'])
      if opt in ("-t", "--type"):
         global testtype
         testtype = arg
      elif opt in ("-q", "--wp"):
         global warning_ping
         warning_ping = arg
         if not is_number(warning_ping):
            print 'UNKNOWN: Warning ping thresold \''+warning_ping+'\' is not a number'
            sys.exit(status['UNKNOWN'])
      elif opt in ("-w", "--cp"):
         global critical_ping
         critical_ping = arg
         if not is_number(critical_ping):
            print 'UNKNOWN: Critical ping thresold \''+critical_ping+'\' is not a number'
            sys.exit(status['UNKNOWN'])
      elif opt in ("-e", "--wd"):
         global warning_download
         warning_download = arg
         if not is_number(warning_download):
            print 'UNKNOWN: Warning download thresold \''+warning_download+'\' is not a number'
            sys.exit(status['UNKNOWN'])
      elif opt in ("-r", "--cd"):
         global critical_download
         critical_download = arg
         if not is_number(critical_download):
            print 'UNKNOWN: Critical download thresold \''+critical_download+'\' is not a number'
            sys.exit(status['UNKNOWN'])
      elif opt in ("-t", "--wu"):
         global warning_upload
         warning_upload = arg
         if not is_number(warning_upload):
            print 'UNKNOWN: Warning upload thresold \''+warning_upload+'\' is not a number'
            sys.exit(status['UNKNOWN'])
      elif opt in ("-y", "--cu"):
         global critical_upload
         critical_upload = arg
         if not is_number(critical_upload):
            print 'UNKNOWN: Critical upload thresold \''+critical_upload+'\' is not a number'
            sys.exit(status['UNKNOWN'])
         
if __name__ == "__main__":
   usage(sys.argv[1:])

if warning_ping > critical_ping or warning_download < critical_download or warning_upload < critical_upload:
     print "For ping: Critical threshold  must be greater than Warning threshold"
     print "For download and upload: Warning threshold must be greater than Critical threshold"
     sys.exit(status['UNKNOWN'])

#cmd = Popen("speedtest-cli", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
#output = cmd.stdout.read()

output="""Retrieving speedtest.net configuration...
Retrieving speedtest.net server list...
Testing from Belgacom Skynet (194.78.34.161)...
Selecting best server based on latency...
Hosted by Cu.be Solutions (Diegem) [7.76 km]: 28.526 ms
Testing download speed........................................
Download: 22.64 Mbits/s
Testing upload speed..................................................
Upload: 9.07 Mbits/s
"""

def grep_ping(s):
    try:
        ping = s.splitlines()[4].split(': ')[1].split()[0]
        return ping
    except ValueError:
        return False

def grep_ping_unit(s):
    try:
        u_ping = s.splitlines()[4].split(': ')[1].split()[1]
        return u_ping
    except ValueError:
        return False

def grep_download(s):
    try:
        download = s.splitlines()[6].split()[1]
        return download
    except ValueError:
        return False

def grep_download_unit(s):
    try:
        u_download = s.splitlines()[6].split()[2].replace('/','p')
        return u_download
    except ValueError:
        return False
    
def grep_upload(s):
    try:
        upload = s.splitlines()[8].split()[1]
        return upload
    except ValueError:
        return False

def grep_upload_unit(s):
    try:
        u_upload = s.splitlines()[8].split()[2].replace('/','p')
        return u_upload
    except ValueError:
        return False

if testtype == 'ping':
  pingValue = grep_ping(output)
  pingUnit = grep_ping_unit(output)

  if critical_ping and pingValue > critical_ping:
    print "CRITICAL:",
    exitCode=2
  elif warning_ping and pingValue > warning_ping:
    print "WARNING:",
    exitCode=1
  else:
    print "OK:",
    exitCode=0

  status='Ping: '+pingValue+' '+pingUnit
  print '|',
  print 'ping='+pingValue.replace(" ", "")+pingUnit+';'+warning_ping+';'+critical_ping
  
  sys.exit(exitCode)

elif testtype == 'download':
  downloadValue = grep_download(output)
  downloadUnit = grep_download_unit(output)
  
  if critical_download and downloadValue < critical_download:
    print "CRITICAL:",
    exitCode=2
  elif warning_download and downloadValue < warning_download:
    print "WARNING:",
    exitCode=1
  else:
    print "OK:",
    exitCode=0
  
  print 'Download: '+downloadValue+' '+downloadUnit,
  print '|',
  print 'download='+downloadValue.replace(" ", "")+downloadUnit+';'+warning_download+';'+critical_download
  
  sys.exit(exitCode)

elif testtype == 'upload':
  uploadValue = grep_upload(output)
  uploadUnit = grep_upload_unit(output)
  
  if critical_upload and uploadValue < critical_upload:
    print "CRITICAL:",
    exitCode=2
  elif warning_upload and uploadValue < warning_upload:
    print "WARNING:",
    exitCode=1
  else:
    print "OK:",
    exitCode=0

  print 'Upload: '+uploadValue+' '+uploadUnit,
  print '|',
  print 'upload='+uploadValue.replace(" ", "")+uploadUnit+';'+warning_upload+';'+critical_upload
  
  sys.exit(exitCode)
  
elif testtype == 'all':
  pingValue = grep_ping(output)
  pingUnit = grep_ping_unit(output)
  
  downloadValue = grep_download(output)
  downloadUnit = grep_download_unit(output)

  uploadValue = grep_upload(output)
  uploadUnit = grep_upload_unit(output)
  
  if critical_ping and pingValue > critical_ping:
    print "CRITICAL:",
    exitCode=2
  elif warning_ping and pingValue > warning_ping:
    print "WARNING:",
    exitCode=1
  if critical_download and downloadValue < critical_download:
    print "22 CRITICAL:",
    exitCode=2
  elif warning_download and downloadValue < warning_download:
    print "WARNING:",
    exitCode=1
  if critical_upload and uploadValue < critical_upload:
    print "33 CRITICAL:",
    exitCode=2
  elif warning_upload and uploadValue < warning_upload:
    print "WARNING:",
    exitCode=1
  else:
    print "OK:",
    exitCode=0

  print 'Ping: '+pingValue+' '+pingUnit,
  print '-',
  print 'Download: '+downloadValue+' '+downloadUnit,
  print '-',
  print 'Upload: '+uploadValue+' '+uploadUnit,
  
  # perfdata
  print '|',
  print 'ping='+pingValue.replace(" ", "")+pingUnit+';'+warning_ping+';'+critical_ping,
  print 'download='+downloadValue.replace(" ", "")+downloadUnit+';'+warning_download+';'+critical_download,
  print 'upload='+uploadValue.replace(" ", "")+uploadUnit+';'+warning_upload+';'+critical_upload
  
  sys.exit(exitCode)

else:
  print "Type should be 'ping', 'download', 'upload' or 'all'"
  sys.exit(status['UNKNOWN'])
