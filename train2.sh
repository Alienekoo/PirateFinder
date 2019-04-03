#!/bin/bash
# Train the ML model with the training data
# Usage train2.sh <dir of piracy> <dir of benign>
PCAP="/*.pcap"
PIRACY=$1$PCAP
BENIGN=$2$PCAP
echo "Piracy Folder:" $PIRACY
echo "Benign Folder:" $BENIGN
#NAME=$1
#echo "var 1:" $NAME
#FILENAME=${NAME:1}
#echo $FILENAME
FILE1="params.txt"
FILE2="params_bd.txt"
echo $FILE1 $FILE2
echo "Step 1: Creating piracy.gz"
./bin/joy bidir=1 dist=1 $PIRACY > ./piracy_train/piracy.gz
echo "Step 2: Creating benign.gz"
./bin/joy bidir=1 dist=1 $BENIGN > ./benign_train/benign.gz
echo "Step 3: analyzing and creating params.txt"
python analysis/model.py -m -l -t -p ./piracy_train/ -n ./benign_train/ -o $FILE1
echo "Step 4: analyzing and creating params_bd.txt"
python analysis/model.py -m -l -t -d -p ./piracy_train/ -n ./benign_train/ -o $FILE2
