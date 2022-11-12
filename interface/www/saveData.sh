#!/bin/bash
lockfile -r 0 /tmp/the.locksave  >/dev/null 2>&1 || exit 1 ## WHAT IS THAT?
sudo mount -t vfat /dev/sda1 /media/usb # NO GUARANTEE IT WILL MOUNT AS SDA1
sudo cp -v /var/www/data_*.txt* /media/usb/
sleep 5
sudo umount /media/usb
rm -f /tmp/the.locksave
