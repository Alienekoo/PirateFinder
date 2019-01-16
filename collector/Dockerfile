##############################################
# Dockerfile to build Piratehunter
#############################################

# Set the base image to ubuntu
FROM mjtooley/joy_v4

MAINTAINER Matt Tooley

############## Begin Installation ###########
RUN git clone https://github.com/mjtooley/PirateFinder.git
WORKDIR /PirateFinder
RUN mkdir /PirateFinder/bin
RUN mkdir /PirateFinder/analysis
RUN mkdir /PirateFinder/lib
RUN cp /joy/bin/joy /PirateFinder/bin/joy
RUN cp /joy/analysis/* /PirateFinder/analysis
RUN cp /joy/sleuth /PirateFinder/sleuth
#RUN cp /joy/lib /PirateFinder/lib
# Set the default container command
# ENTRYPOINT /PirateHunter/output/probe.sh eth0
WORKDIR /PirateFinder/output
EXPOSE 4739
ARG interface=eth0
ENV if=$interface
#ENTRYPOINT ./collector.sh $if



