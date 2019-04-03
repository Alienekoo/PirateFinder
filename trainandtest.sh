#!/bin/sh
# Train the ML model with the training data
echo "Step 1"
./bin/joy bidir=1 dist=1 verbosity=3 ./piracy/*.pcap > ./piracy_train/piracy.gz
echo "Step 2"
./bin/joy bidir=1 dist=1 verbosity=3 ./benign/*.pcap > ./benign_train/benign.gz
echo "Step 3 - Training"
python analysis/model.py -m -l -t -p ./piracy_train/ -n ./benign_train/ -o /home/ncta/PirateFinder/classifiers/params.txt
echo "Step 4 - Training"
python analysis/model.py -m -l -t -d -p ./piracy_train/ -n ./benign_train/ -o /home/ncta/PirateFinder/classifiers/params_bd.txt
#echo "copying classifiers to their dir"
#cp params.txt ./classifiers/params.txt
#cp params_bd.txt ./classifiers/params_bd.txt
echo "Testing with new classifier"
#./offline.sh /home/ncta/ncta_split_00001_20190305125812.pcap .95
echo "Testing against benign data"
./offline.sh /home/ncta/pcap_repository/benign_library/benign3.pcap 0
echo "Testing against pirate data"
./offline.sh /home/ncta/pcap_repository/piracy_library/excursion1.pcap 0
