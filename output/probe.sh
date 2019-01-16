#!/bin/sh
# usage ./probe.sh <interface_name>
../bin/joy \
       bidir=1 \
       dist=1 \
       classify=1 \
       output=auto \
       count=10 \
       verbosity=1 \
       show_interfaces=1 \
       username=root \
       model="params.txt:params_bd.txt" \
       URLmodel="https://github.com/mjtooley/PirateHunter/blob/master" \
       interface=$1
