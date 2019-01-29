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


