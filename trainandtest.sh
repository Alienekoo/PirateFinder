#!/bin/sh
#usage ./trainandtest.sh <splt model> <bd model>
echo Training....

./bin/joy bidir=1 dist=1 ./benign/*.pcap > ./benign_train/benign.gz
./bin/joy bidir=1 dist=1 ./piracy/*.pcap > ./piracy_train/piracy.gz

echo Building Classifiier
if [ $# -eq 0 ]
then
    python analysis/model.py -m -l -t -p ./piracy_train/ -n ./benign_train/ -o params1.txt
    python analysis/model.py -m -l -t -d -p ./piracy_train/ -n ./benign_train/ -o params1_bd.txt

    ./testmodel.sh .9

else

    python analysis/model.py -m -l -t -p ./piracy_train/ -n ./benign_train/ -o $1
    python analysis/model.py -m -l -t -d -p ./piracy_train/ -n ./benign_train/ -o $2

    string1=$1
    string2=$2
    model=${string1}:${string2}
    echo model=$model
    ./testmodel.sh .9 $model

fi
