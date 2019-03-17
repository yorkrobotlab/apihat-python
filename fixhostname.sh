#!/bin/bash

# Find MAC of eth0, or if not exist wlan0
if [ -e /sys/class/net/eth0 ]; then
    MAC=$(cat /sys/class/net/eth0/address)
elif [ -e /sys/class/net/enx* ]; then
    MAC=$(cat /sys/class/net/enx*/address)
else
    MAC=$(cat /sys/class/net/wlan0/address)
fi
echo fixhostname.sh : Update the hostname and hosts file to one based on the MAC address
echo
if [ $# -eq 0 ]; then
  echo MAC Address     : $MAC
  TRIMMED_MAC="${MAC:9}"
  STRIPPED_MAC="${TRIMMED_MAC//:}"
  TARGET_HOSTNAME="rpi-${STRIPPED_MAC}"
else
  TARGET_HOSTNAME="$1"
fi
echo Target Hostname : $TARGET_HOSTNAME
echo Current Hostname: $HOSTNAME
echo
if [ "$TARGET_HOSTNAME" != "$HOSTNAME" ]; then
  echo Updating files
  
  for file in \
     /etc/hostname \
     /etc/hosts \
     /etc/ssh/ssh_host_rsa_key.pub \
     /etc/ssh/ssh_host_dsa_key.pub \
     /etc/ssh/ssh_host_ed25519_key.pub \
     /etc/ssh/ssh_host_ecdsa_key.pub
  do
     [ -f $file ] && sed -i.old -e "s:$HOSTNAME:$TARGET_HOSTNAME:g" $file
  done
  echo 
  echo Restart now \(\"sudo reboot\"\) to update hostname.
  echo
else
  echo Nothing to do - hostname set correctly.
fi
