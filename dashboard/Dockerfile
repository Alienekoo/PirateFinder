##############################################
# Dockerfile to build Piratehunter
#############################################

# Set the base image to ubuntu
FROM mjtooley/joy_v4

MAINTAINER Matt Tooley

RUN apt-get update && apt-get install inotify-tools -y
############## Begin Installation ###########
RUN git clone https://github.com/mjtooley/PirateFinder.git
WORKDIR /PirateFinder
# Set the default container command
# ENTRYPOINT /PirateHunter/output/probe.sh eth0
WORKDIR /PirateFinder/
ENTRYPOINT ./dashmonitor.sh



