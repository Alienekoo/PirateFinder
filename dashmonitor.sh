#!/bin/sh
MINIMUMSIZE=10
MONITORDIR="./output"
inotifywait -m -e close_write --format '%w%f' "${MONITORDIR}" | while read NEWFILE
do
     actualsize=$(wc -c < $NEWFILE)
     # echo size of file is $actualsize
     if [ $actualsize -ge $MINIMUMSIZE ]; then
#        echo Post-processing $NEWFILE
        ./dashboard-post-process.sh $NEWFILE 0 > tmp_results.txt
        tmp_size=$(wc -c < tmp_results.txt)
        if [ $tmp_size -ge $MINIMUMSIZE ]; then
           python Dashboard.py -i tmp_results.txt
        fi
        rm $NEWFILE
     else
        echo "."
     fi
done

