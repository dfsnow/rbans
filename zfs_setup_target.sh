# Script for setting up ZFS pools necessary to store all the data

sudo apt-get install -y software-properties-common

# Add zfs to sources list
sed -i 's/main/main contrib non-free/g' /etc/apt/sources.list
sudo apt-get install linux-headers-amd64
sudo apt-get install zfs-dkms zfsutils-linux

# Install ZFS pool with appropriate options
sudo zpool create -f tank -o ashift=12 -o autoreplace=on -o autoexpand=on \
    raidz2 scsi-35000c5004117811f scsi-35000c5004117b9e3 scsi-35000cca01b4a0a34 \
    scsi-35000cca01b4a0d54 scsi-35000cca01c401858 scsi-35000cca01c424570 \
    raidz2 scsi-35000cca01c42a998 scsi-35000cca01c42aa58 scsi-35000cca01c42e454 \
    scsi-35000cca01c49d45c scsi-35000cca01c49ebb0 scsi-35000cca01c49ebbc

sudo zfs set atime=off tank
sudo zfs set acltype=posixacl tank
sudo zfs set xattr=sa tank
sudo zfs set compression=lz4 tank
sudo zfs set dedup=off tank

# Create a zvol for connecting via iSCSI
sudo zfs create -o compression=lz4 -o dedup=off -o volblocksize=32K -V 11T tank/primary_pool

# TargetCLI iscsi setup, see this link:
# https://www.rootusers.com/how-to-configure-an-iscsi-target-and-initiator-in-linux/

# Open TCP 3260 to allow all connections
sudo apt-get install -y firewalld

firewall-cmd --permanent --add-port=3260/tcp
firewall-cmd --reload

