#!/bin/sh
# usage ./probe.sh <interface_name>
../bin/joy \
       bidir=1 \
       dist=1 \
       classify=1 \
       output=auto \
       count=10 \
       verbosity=3 \
       show_interfaces=1 \
       username=root \
       model="~/PirateFinder/classifiers/params.txt:~/PirateFinder/classifiers/params_bd.txt" \
       interface=$1
