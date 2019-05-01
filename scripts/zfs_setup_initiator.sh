#!/bin/bash

# Install iscsiadm client
sudo apt-get install -y open-iscsi

# Connect to iscsi node
sudo iscsiadm --mode discovery --type sendtargets --portal 192.168.1.211
sudo iscsiadm -m node -T iqn.2003-01.org.linux-iscsi.uranus.x8664:sn.d1ee8ae123c5 -l -v automatic

# Create a new filesystem
#sudo mkfs.ext4 /dev/sdb

# Edit /etc/iscsi/iscsid.conf to autostart and /etc/fstab to mount



