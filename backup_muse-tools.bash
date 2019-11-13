#!/bin/bash

home_dir='/home/pi/'
dev_dir='/home/pi/dev/bluetooth/abcs-muse'

cd  ${dev_dir}

sudo rm -f logs/* 

cd ${home_dir}

# d=`date --iso-8601=date`
d=`date +%F-%m-%H-%M`

echo ${d}

tar cvfz pi-dev-backup-${d}.tar.gz --exclude="${dev_dir}/plots/*" ${dev_dir}
