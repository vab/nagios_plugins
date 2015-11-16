#!/bin/bash
#
# evaluate free system memory from Linux based systems
#
# Date: 2007-11-12
# Author: Thomas Borger - ESG
#
# the memory check is done with following command line:
# free -m | grep buffers/cache | awk '{ print $4 }'

# get arguments

while getopts 'w:c:hp' OPT; do
  case $OPT in
    w)  int_warn=$OPTARG;;
    c)  int_crit=$OPTARG;;
    h)  hlp="yes";;
    p)  perform="yes";;
    *)  unknown="yes";;
  esac
done

# usage
HELP="
    usage: $0 [ -w value -c value -p -h ]

    syntax:

            -w --> Warning integer value
            -c --> Critical integer value
            -p --> print out performance data
            -h --> print this help screen
"

if [ "$hlp" = "yes" -o $# -lt 1 ]; then
  echo "$HELP"
  exit 0
fi

# get free memory
FMEM=`free -m | grep buffers/cache | awk '{ print $3 }'`
SMEM=`free -m | grep Swap: | awk '{ print $3 }'`
TMEM=`free -mt | grep Total: | awk '{ print $3 }'`

# output with or without performance data
if [ "$perform" = "yes" ]; then
  OUTPUTP="system memory used: $FMEM MB, used swap: $SMEM MB, total: $TMEM MB | used memory="$FMEM"MB;$int_warn;$int_crit;0"
else
  OUTPUT="system memory used: $FMEM MB, used swap: $SMEM MB, total: $TMEM MB"
fi

if [ -n "$int_warn" -a -n "$int_crit" ]; then

  err=0

  if (( $FMEM >= $int_crit )); then
    err=2
  elif (( $FMEM >= $int_warn )); then
    err=1
  fi

  if (( $err == 0 )); then

    if [ "$perform" = "yes" ]; then
      echo -n "OK - $OUTPUTP"
      exit "$err"
    else
      echo -n "OK - $OUTPUT"
      exit "$err"
    fi

  elif (( $err == 1 )); then
    if [ "$perform" = "yes" ]; then
      echo -n "WARNING - $OUTPUTP"
      exit "$err"
    else
      echo -n "WARNING - $OUTPUT"
      exit "$err"
    fi

  elif (( $err == 2 )); then
    
    if [ "$perform" = "yes" ]; then
      echo -n "CRITICAL - $OUTPUTP"
      exit "$err"
    else
      echo -n "CRITICAL - $OUTPUT"
      exit "$err"
    fi

  fi
  
else
  
  echo -n "no output from plugin"
  exit 3

fi
exit  
