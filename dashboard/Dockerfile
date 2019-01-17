##############################################
# Dockerfile to build Piratehunter
#############################################

# Set the base image to ubuntu
FROM mjtooley/joy_v4

MAINTAINER Matt Tooley

############## Begin Installation ###########
RUN apt-get update && apt-get install inotify-tools python python-pip -y
RUN pip install IPy
RUN pip install cymruwhois
RUN git clone https://github.com/mjtooley/PirateFinder.git
WORKDIR /PirateFinder
RUN mkdir /PirateFinder/bin
RUN mkdir /PirateFinder/analysis
RUN mkdir /PirateFinder/lib
RUN cp /joy/bin/* /PirateFinder/bin
RUN cp /joy/analysis/* /PirateFinder/analysis
RUN cp /joy/sleuth /PirateFinder/sleuth
RUN cp -r /joy/sleuth_pkg/ /PirateFinder/sleuth_pkg

# Set the default container command
WORKDIR /PirateFinder/
ENTRYPOINT ./dashmonitor.sh



