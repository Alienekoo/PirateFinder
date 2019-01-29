#!/bin/bash
# Train the ML model with the training data
# Usage train2.sh <dir of piracy> <dir of benign>
PCAP="/*.pcap"
PIRACY=$1$PCAP
BENIGN=$2$PCAP
NAME=$1
FILENAME=${NAME:2}
echo $FILENAME
FILE1=$FILENAME".txt"
FILE2=$FILENAME"_bd.txt"
echo $FILE1 $FILE2
./bin/joy bidir=1 dist=1 $PIRACY > ./piracy_train/piracy.gz
./bin/joy bidir=1 dist=1 $BENIGN > ./benign_train/benign.gz
python analysis/model.py -m -l -t -p ./piracy_train/ -n ./benign_train/ -o $FILE1
python analysis/model.py -m -l -t -d -p ./piracy_train/ -n ./benign_train/ -o $FILE2