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
RUN cp /joy/bin/* /PirateFinder/bin
RUN cp /joy/analysis/* /PirateFinder/analysis
RUN cp /joy/sleuth /PirateFinder/sleuth
# Set the default container command
WORKDIR /PirateFinder/output
#ARG interface=eth0
#ENV if=$interface
#ENTRYPOINT ./probe.sh $if



