#!/bin/sh
# usage ./offline.sh <pcap file> 
./bin/joy -x ./config/offline.conf $1 >tmp.gz
./dashboard-post-process.sh tmp.gz 0 > tmp_results.txt
python Dashboard.py -i tmp_results.txt -o N 
