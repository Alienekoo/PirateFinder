##############################################
# Dockerfile to build Piratehunter
#############################################

# Set the base image to ubuntu
FROM mjtooley/joy_v4

MAINTAINER Matt Tooley

############## Begin Installation ###########
RUN git clone https://https://github.com/mjtooley/PirateFinder.git
WORKDIR /PirateFinder
# Set the default container command
# ENTRYPOINT /PirateHunter/output/probe.sh eth0
WORKDIR /PirateFinder/
ENTRYPOINT ./dashboard.sh



