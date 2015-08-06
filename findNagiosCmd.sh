#!/bin/bash
# This is findNagiosCmd.sh
# Author: Julien Boisdequin, julien.boisdequin@qspin.be

ARG="check_ntp_time"

NAGIOS_PLUGIN_CFG="/home/jbo/Documents/Thales/backups/etc/nagios-plugins"
#later: /etc/nagios-plugins

NAGIOS_CONF="/home/jbo/Documents/Thales/backups/etc/nagios3/conf.d/"
#later: /etc/nagios3/conf.d

RESOURCES_CONF="/home/jbo/Documents/Thales/backups/etc/nagios3/resource.cfg"
#later: /etc/nagios3/resource.cfg

NAGIOS_COMMAND_LINE=`find $NAGIOS_PLUGIN_CFG -name "*.cfg" -print | xargs cat | sed -n "/"$ARG"/{n;p;}" | grep command_line | awk -F "command_line" '{print $2}' | sed -e 's/^[ \t]*//' | sed 's/\\\$//g'`
#echo $NAGIOS_COMMAND_LINE

HOSTFILE_LIST=`find $NAGIOS_CONF -name "*.cfg" -print | xargs grep $ARG 2> /dev/null | cut -d':' -f1`
echo $HOSTFILE_LIST
#if check_nrpe_1arg before -> ignore it


for file in $HOSTFILE_LIST
do
    # get host ip
    HOSTADDRESS=`grep address $file | awk -F"address" '{print $2}' | sed -e 's/^[ \t]*//'`
    NAGIOS_COMMAND_LINE=`echo $NAGIOS_COMMAND_LINE | sed "s/HOSTADDRESS/"$HOSTADDRESS"/g"`
    
    # get arguments
    for i in {2..10}
    do
        ARG_N=`grep $ARG $file 2> /dev/null | cut -d'!' -f$i`
        j=$((i - 1)) 
        if [ -z $ARG_N ]; then
            break
        fi
        NAGIOS_COMMAND_LINE=`echo $NAGIOS_COMMAND_LINE | sed "s/ARG"$j"/"$ARG_N"/g"`
    done
    
    # get resources variables
    
    USER_VAR=`grep USER $RESOURCES_CONF | grep -v "#"`
    #echo $USER_VAR
    
    for var in $USER_VAR
    do
        #echo $var
        VAR_NAME=`echo $var | awk -F "=" '{print $1}' | sed 's/\\\$//g'`
        #echo $VAR_NAME
        USER_VALUE=`echo $var | awk -F "=" '{print $2}' | sed 's/\//\\\\\//g'`
        #echo $USER_VALUE
        if [ -z $USER_VALUE ]; then
            break
        fi
        NAGIOS_COMMAND_LINE=`echo $NAGIOS_COMMAND_LINE | sed "s/"${VAR_NAME}"/"${USER_VALUE}"/g"`
    done

    echo $NAGIOS_COMMAND_LINE
done

