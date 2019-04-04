#!/bin/sh
# usage ./offline.sh <pcap file> <probability threshold> 
echo "Step 1 - Analyze flows"
./bin/joy -x ./config/offline.conf $1 >tmp.gz
echo "Step 2 - Extract flows of interest with Sleuth"
./dashboard-post-process.sh tmp.gz $2 > tmp_results.txt
echo "Step 3 - Post process and run through white list filter"
python Dashboard.py -i tmp_results.txt -o N -w whitelist.txt 
