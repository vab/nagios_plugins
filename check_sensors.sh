#!/usr/bin/env bash
#this is check_sensors.sh
# Author: Julien Boisdequin boisdequin.julien@gmail.com
####################################################################
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:/usr/nagios/sbin:/usr/local/nagios/sbin

PROGNAME=`basename $0`
PROGPATH=`echo $0 | sed -e 's,[\\/][^\\/][^\\/]*$,,'`
REVISION="QSPIN 1.1"

#. $PROGPATH/utils.sh

exit_ok="0"
exit_warn="1"
exit_crit="2"
exit_unkn="3"

print_usage() {
   echo "Usage: $PROGNAME [options]"
   echo "  e.g. $PROGNAME -n 'Core X' -w 50 -c 60"
   echo "  Multicore: e.g. $PROGNAME -n 'Core' -w 50 -c 60"
   echo
   echo "Options:"
   echo -e "\t --help | -h          print help"
   echo -e "\t --version | -V       print version"
   echo -e "\t --verbose | -v       be verbose"
   echo -e "\t -n [value]           set sensor name"        
   echo -e "\t -w [value]           set warning value"
   echo -e "\t -c [value]           set critical value"

   echo
   echo "If no options are given, $PROGRAME will print only status."
   echo "NOTE: you can only ask one data type at once, $PROGNAME will"
   echo "      not output several temperatures at the same time."
   echo
}

print_help() {
   echo $PROGNAME $REVISION
   echo 
   echo "This plugin checks hardware status using the lm_sensors package."
   echo 
   print_usage
   exit 3
}

# set defaults
check_temp=0
isverbose=0
hddtype="ata"

# test dependencies
if [ ! "$(type -p sensors)" ]; then
   echo "SENSORS UNKNOWN - command not found (did you install lm-sensors?)"
   exit -1
else
   # get the data
   sensordata=$(sensors 2>&1)
   status=$?

   # test status
   if test ${status} -ne 0 ; then
      echo "WARNING - sensors returned state $status"
      exit -1
   #elif [ $check_smart -eq 1 ] && [ ! "$hdd_drive" ]; then
   # echo "No HDD drive defined. Use the -d switch."
   # exit -1
   fi
fi


# all is ok
if [ $isverbose -eq 1 ]; then
   echo -e "${sensordata}"
fi

# check functions
check_temp() {
        #sensor_temp=$(grep -i "$1" <<< "${sensordata}"  | awk -F "(" '{print $1}' | \
        #            grep -Eo '[0-9\.]+[[:punct:]]?[ ]?[CF]+' | awk -F "." '{print $1}')
        sensor_temp=$(grep -i "$1" <<< "${sensordata}"  | awk -F "(" '{print $1}' | \
                    grep -Eo '[0-9\.]+[[:punct:]]?[ ]?[CF]+' | awk -F "." '{print $1}')
        
        units=$(grep -i "$1" <<< "${sensordata}" | \
               grep -Eo '[0-9\.]+[[:punct:]]?[ ]?[CF]+' | head -n 1 | awk -F "." '{print $2}' | sed 's/[0-9]//')
        
        if [[ -z "$sensor_temp" ]]; then
            echo "[UNKNOWN] Sensor name does not match"
            exit $exit_unkn
        fi

   local drive
   hdd_temp[0]="reserved"


   for drive in $(seq 1 1 ${#hdd_drives[@]}); do
      [ -e "${hdd_drives[$drive]}" ] && \
      hdd_temp[${#hdd_temp[@]}]="$(smartctl -A ${hdd_drives[$drive]} -d $hddtype | \
            grep -i temperature | \
            awk '{for (i=10; i<=NF; i++) printf("%s ",$i);printf ("\n")}') C"
   done
}

main() {
   # Determine the status output
   if [ $check_temp -eq 1 ]; then
      check_temp "$sensor_name"
      temp_status=$exit_unkn
      
      for temp in $sensor_temp
      do                    
         if [ "$critical" ] && [ $temp -ge $critical ]; then
            echo -n "[CRITICAL] "
            temp_status=$exit_crit
            break
         elif [ "$warning" ] && [ $temp -ge $warning ]; then
            echo -n "[WARNING] "
            temp_status=$exit_warn
            break
         elif [ "$warning" ] && [ "$critical" ] && [ $temp -lt $warning ] && [ $temp -lt $critical ]; then
            temp_status=$exit_ok
         else
            echo -n "[UNKNOWN] "
            temp_status=$exit_unkn
            break
         fi
      done

   if [ $temp_status == $exit_ok ]; then    
      echo -en "[OK] "
   fi

   # if multicore
   total_sensors=`echo $sensor_temp | wc -w`

# print output data
   i=0
   for temp in $sensor_temp
   do
       if [ $i -ne 0 ]; then
           echo -en ", "
       fi
       
       if [ $total_sensors -eq 1 ]; then
           echo -en "$sensor_name= $temp${units}"
       else
           echo -en "$sensor_name$i= $temp${units}"
       fi
       
       let i++
   done
   
   echo -en " | "
   
# print perf data
   i=0
   for temp in $sensor_temp
   do
       if [ $i -ne 0 ]; then
           echo -en ", "
       fi
       
       # if sensors contains whitespace
       #ex: "Core 1" becomes "Core1" in perfdata
       case "$sensor_name" in  
            *\ * )
                  sensor_name="$(echo -e "${sensor_name}" | tr -d '[[:space:]]')"
                 ;;
       esac

       if [ $total_sensors -eq 1 ]; then
           echo -en "temperature_$sensor_name=${temp}"
       else
           echo -en "temperature_$sensor_name$i=${temp}"
       fi
       
       let i++
   done
   
   echo -en "\n"
                
		for drive in $(seq 1 1 ${#hdd_drives[@]}); do
			echo -n "${hdd_drives[$drive]} = ${hdd_temp[$drive]}  "
		done
                
		exit $temp_status

	#default operation
	else
		if echo ${sensordata} | egrep ALARM > /dev/null; then
			echo SENSOR CRITICAL - Sensor alarm detected!
			exit 2
		else
			echo sensor ok
			exit 0
		fi
	fi
}


# parse cmd arguments
if [ "$#" -gt 0 ]; then
        while [ "$#" -gt 0 ]; do
		case "$1" in
			'--help'|'-h')
				print_help
				exit 3
				;;
			'--version'|'-V')
				echo $PROGNAME $REVISION
				exit 3
				;;
			'--verbose'|'-v')
				isverbose=1
				shift 1
				;;
			'-n')
            check_temp=1
            sensor_name="$2"
            shift 2
            ;;
         '-c')
				critical="$2"
				shift 2
				;;
			'-w')
				warning="$2"
				shift 2
				;;
			*)
				echo "Unknown option!"
				print_usage
				exit 3
				;;
		esac
	done
fi


# call the main function
main
