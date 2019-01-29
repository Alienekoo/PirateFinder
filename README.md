# PirateFinder

Docker build and deployment files for PirateFinder.  PirateFinder is a video piracy detection system based up on the Cisco/Joy machine learning system.  

## Installing

1.	Install Docker
2.	Install Docker-compose
3.	Clone source code from Github
  a.	Git clone http://github.com/mjooley/PirateFinder
  b.	Git clone http://github.com/cisco/joy
4.	Build Cisco Joy
  a.	sudo apt-get install build-essential libssl-dev libpcap-dev libcurl4-openssl-dev libssl-dev
  b.	sudo apt-get install python-dev python-numpy python-setuptools python-scipy
  c.	sudo pip install -U scikit-learn
  d.	cd joy
  e.	./configure –enable-gzip
  f.	Make clean;make
5.	Build PirateFinder
  a.	Cd PirateFinder
  b.	Edit docker-compose.yml to 
    i.	deploy either the probe or the collector service
  c.	Create a docker volume to share the data between containers
    i.	Docker volume create grafana-volume
  d.	Docker-compose build
6.	Edit the Configuration
  a.	Cd /config
  b.	Nano probe.conf or collector.conf
    i.	Change the interface to match the interface to use
7.	Setup the environment
  a.	Run ./setupjoy.sh  -Note assumes Joy was built at default location
8.	Deploy PirateFinder
  a.	Docker-compose up -d
  b.	Check the status
    i.	Docker ps   - this should list four containers running
9.	Dashboard
  a.	https://<IP of the machine running the containers>:3000
  b.	Login admin/admin
  c.	Add data source Graphite, http://localhost:8080
  d.	Create dashboards with dashboard metrics (see below for description)

## PirateFinder Scripts and Apps

`/PirateHunter/bin/joy – Joy is the packet processor that can either: 1) read packets from one of the local interfaces, 2) process Netflow/IPFix from a Netflow Exporter (switch, router, etc.), 3) packet capture file (e.g. wireshark, tcpdump).  Joy outputs a summary of the observed traffic in a JSON formatted file.

sleuth -  Sleuth is a tool to read the JSON output from Joy to find selected traffic

dashboard-post-process.sh – This script is used by the dashboard’s dashmonitor.sh script to select the potential pirate video flows

dashmonitor.sh – Ths is the primary script that is run to generate the dashboard and the reports.  This script monitors a subdirectory, ./output, for new JSON output file.

Dashboard.py – Dashboard.py is called from the dashmonitor each time a joy output file is ready for processing.  The script does additional post-processing on the JSON output file and then writes the results to the graphite database for the Grafana application to use for generating dashboards.

## Training

** Training PirateFinder ** involves training the machine learning model on what is a pirated video flow and what is a benign or non-pirated video flow.  There are two subdirectories – benign and piracy – where packet capture (pcap files) with the respective flows stored.  The training scripts are hard-coded to look in these two directories for the training files.

Train.sh – This script looks in ./piracy and ./benign for the pcap files to use for training.  It generates update model files – params.txt and params_bd.txt.

Trainandtest.sh – This script looks in ./piracy and ./benign for the pcap files to use for training.  It takes as input the names for the two model files.  It generates the two named model files and then uses the new model to test model against the test files in ./benign_test and ./piracy_test and ./benign_test and then outputs the accuracy of the new model.

## Operating

## Log files
-	Docker logs [-f] [probe, collector, dashboard]

Attaching to docker container shell
-	List container ids:
o	Docker ps
-	Docker exec -it <container id> bash

