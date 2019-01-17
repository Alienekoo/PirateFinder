#!/bin/sh
# usage ./post-process.sh <joy output results> <probability>
# echo Post-processing $1 for results with probability greater than $2
./sleuth $1 --select "sa, da, sp, dp, p_malware, bytes_out, num_pkts_out, time_start" --where "da~8.8.8.8,\
 da~8.8.8.4, \
 da~224.0.0.*, \
 da~172.*, \
 da~255.*, \
 da~239.*, \
 dp~53, \
 dp~443,\
 dp~37, \
 p_piracy > $2"

