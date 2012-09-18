#!/bin/bash

#set -e
#set -u

#service crond stop
#service dsm_om_connsvc stop
#service dsm_om_shrsvc stop
#service dataeng stop
#service postfix stop

cd /root/tpcc
#mysql tpcc1000 < add_fkey_idx.sql 2>&1 | tee /root/add_fkey_idx.log

for sched in noop deadline cfq; do
    echo "Setting scheduler to $sched"
    echo $sched > /sys/block/sda/queue/scheduler

    echo "Dropping caches"
    echo 1 > /proc/sys/vm/drop_caches

    echo "Restarting MySQL"
    service mysql restart

    echo "Starting TPCC benchmark"
    ./tpcc_start -h localhost -d tpcc1000 -u root -p "" -w 1000 -c 32 -r 60 -l 10800 -f /root/tpcc.$sched.report | tee /root/tpcc.$sched
done
