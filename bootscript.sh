#!/bin/bash

echo
echo "YRL028 - APIHAT - York Robotics Laboratory, March 2019"
echo
#Check to see if HOSTNAME is correctly set [based on MAC address] or if it is default [raspberry-pi]
  # Find MAC of eth0, or if not exist wlan0
  if [ -e /sys/class/net/eth0 ]; then
      MAC=$(cat /sys/class/net/eth0/address)
  elif [ -e /sys/class/net/enx* ]; then
      MAC=$(cat /sys/class/net/enx*/address)
  else
      MAC=$(cat /sys/class/net/wlan0/address)
  fi
  #echo MAC Address:$MAC
  TRIMMED_MAC="${MAC:9}"
  STRIPPED_MAC="${TRIMMED_MAC//:}"
  TARGET_HOSTNAME="rpi-${STRIPPED_MAC}"
  #echo Hostname: $TARGET_HOSTNAME

if [ "$HOSTNAME" != "$TARGET_HOSTNAME" ]; then
  echo
  echo The HOSTNAME is currently set to $HOSTNAME but the MAC address is $MAC
  echo The expected hostname is $TARGET_HOSTNAME
  echo
  echo Run \"sudo ./fixhostname.sh\" to update the hostname variable
  echo
fi

#Check to see if server is active by looking for existence of /ramdisk/system.csv
if [ ! -f /ramdisk/system.csv ]; then
    #Kill all instances of python
    if pgrep -x "python" > /dev/null
    then
      killall python
    fi  
    echo "system.csv not found - running core.py"
    python camera.py &
    python index.py &
    python core.py &
else
  echo "Not starting Python services; they may already be running [/ramdisk/system.csv exists]"
  echo
  echo "To erase ramdisk and restart core.py try:"
  echo
  echo ". rerun"
  echo
  echo
fi
#python core.py
