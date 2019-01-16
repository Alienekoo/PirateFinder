#!/bin/sh
# usage ./classify.sh <interface_name>
../bin/joy bidir=1 \
           dist=1 \
           classify=1 \
           output=auto \
           count=10 \
           username=root \
           show_interfaces=1 \
           verbosity=1 \
           model="../params.txt:../params_bd.txt" \
           nfv9_port=4739 \
           interface=$1
