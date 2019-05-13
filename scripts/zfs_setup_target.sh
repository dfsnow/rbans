#!/bin/bash
# Script for setting up ZFS pools necessary to store all the data

# Install some prereqs
sudo apt-get install -y git wget open-vm-tools fio

# ZFS Install from ZFS on Linux repo
sudo echo "deb http://deb.debian.org/debian stretch-backports main contrib" > \
    /etc/apt/sources.list.d/stretch-backports.list
sudo echo "deb-src http://deb.debian.org/debian stretch-backports main contrib" >> \
    /etc/apt/sources.list.d/stretch-backports.list

sudo echo "Package: libnvpair1linux libuutil1linux libzfs2linux libzpool2linux spl-dkms zfs-dkms zfs-test zfsutils-linux zfsutils-linux-dev zfs-zed
Pin: release n=stretch-backports
Pin-Priority: 990" > /etc/apt/preferences.d/90_zfs

sudo apt update

apt install --yes dpkg-dev linux-headers-$(uname -r) linux-image-amd64

sudo apt-get install -y zfs-dkms zfsutils-linux

# Telegraf install for monitoring
sudo apt-get update && sudo apt-get install apt-transport-https
wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add -
source /etc/os-release
test $VERSION_ID = "9" && echo "deb https://repos.influxdata.com/debian stretch stable" | sudo tee /etc/apt/sources.list.d/influxdb.list

sudo apt-get update && sudo apt-get install -y telegraf

# Install multipath tools
sudo apt-get install -y multipath-tools

 Install ZFS pool with appropriate option#s
sudo zpool create -f tank -o ashift=12 -o autoreplace=on \
    raidz1 35000cca01c42e454 35000c5004117b9e3 35000cca01c49ebb0 35000cca01c49ebbc \
    raidz1 35000c5004117811f 35000cca01c42a998 35000cca01b4a0d54 35000cca01b4a0a34 \
    raidz1 35000cca01c424570 35000cca01c401858 35000cca01c42aa58 35000cca01c49d45c \
    cache nvme-INTEL_SSDPEDMW800G4_CVCQ53500085800EGN

sudo zfs set atime=off tank
sudo zfs set acltype=posixacl tank
sudo zfs set xattr=sa tank
sudo zfs set compression=lz4 tank
sudo zfs set dedup=off tank
sudo zfs set sync=disabled tank

 Increase ARC max with the following run as root:
echo 60129542144 > /sys/module/zfs/parameters/zfs_arc_max

# Create a zvol for connecting via iSCSI
sudo zfs create -o compression=lz4 -o dedup=off -o volblocksize=8K -V 3T tank/psql_data

# TargetCLI iscsi setup, see this link:
# https://www.rootusers.com/how-to-configure-an-iscsi-target-and-initiator-in-linux/

# Open TCP 3260 to allow all connections
sudo apt-get install -y firewalld

sudo firewall-cmd --permanent --add-port=3260/tcp
sudo firewall-cmd --reload

