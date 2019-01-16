#!/bin/sh
# Train the ML model with the training data
./bin/joy bidir=1 dist=1 ./piracy/*.pcap > ./piracy_train/piracy.gz
./bin/joy bidir=1 dist=1 ./benign/*.pcap > ./benign_train/benign.gz
python analysis/model.py -m -l -t -p ./piracy_train/ -n ./benign_train/ -o params.txt
python analysis/model.py -m -l -t -d -p ./piracy_train/ -n ./benign_train/ -o params_bd.txt
