#!/usr/bin/python

"""
sleuth-postprocess does a post processing tasks to the output from sleuth
 *
 * Copyright (c) 2018 NCTA, Inc.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   Redistributions of source code must retain the above copyright
 *   notice, this list of conditions and the following disclaimer.
 *
 *   Redistributions in binary form must reproduce the above
 *   copyright notice, this list of conditions and the following
 *   disclaimer in the documentation and/or other materials provided
 *   with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
 * INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
"""

from socket import socket
from pprint import pprint
import sys, getopt
import warnings
from IPy import IP
import time
from cymruwhois import Client


CARBON_SERVER = "127.0.0.1"
CARBON_PORT = 2003

def tryWhoIs(ip_addr):

    try:
        c = Client()
        r = c.lookup(ip_addr)
        name = r.owner
    except:
        name= "unknown"

    return name


def addToList(ip1, ip2, prob, bytes_out, pkts_out):
    ip_list.append(ip1)

    try:
        result = socket.gethostbyaddr(ip1)
        name1 = result[0]
    except:
        ip = IP(ip1)
        if ip.iptype() == 'PRIVATE':
            name1 = "private"
        else:
            name1 = tryWhoIs(ip1)
    try:
        result = socket.gethostbyaddr(ip2)
        name2 = result[0]
    except:
        ip = IP(ip2)
        if ip.iptype() == 'PRIVATE':
            name2 = "private"
        else:
            name2 = tryWhoIs(ip2)

    ip_host1[ip1] = name1
    ip_host2[ip1] = name2
    p_piracy[ip1] = prob
    saddr_d[ip1] = ip2
    bytesout[ip1] = bytes_out

    cdns = {'AKAMAI', 'akamaitechnologies', 'GOOGLE', 'MSFT'}
    # Check to see if it is in the list of known cdns and public hosts
    cdn_ips[ip1] = 'no'
    for n in name1.split('.'):
        if n in cdns:
            cdn_ips[ip1] = 'yes'
    for n in name2.split('.'):
        if n in cdns:
            cdn_ips[ip1] = 'yes'

    # Add it to the Graphite DB for Grafana
    sock = socket()
    try:
        sock.connect( (CARBON_SERVER, CARBON_PORT))
    except:
        print ("Could NOT connect to Carbon, is Carbon running?")
        sys.exit(1)

    dest = name1.replace(".","-") # replace dots with dashes
    dest = dest.replace(" ","") # remove whitespace
    dest = dest.replace(",","-")
    ts = int(time.time()) # Get Time stamp in seconds, TODO Use flow start time from NF
    if (float(prob) > 0.8):
        message = "dashboard.piracy." + dest + ".bytes" + " " + str(bytes_out) + " " + str(ts) + "\n"
        sock.sendall(message)
        message = "dashboard.piracy." + dest + ".packets" + " " + str(pkts_out) + " " + str(ts) + "\n"
        sock.sendall(message)
        message = "dashboard.piracy." + dest + ".probability" + " "  + str(prob) + " " + str(ts) + "\n"
        sock.sendall(message)
    else:
        message = "dashboard.web." + dest + ".bytes" + " " + str(bytes_out) + " " + str(ts) + "\n"
        sock.sendall(message)
        message = "dashboard.web." + dest + ".packets" + " " + str(pkts_out) + " " + str(ts) + "\n"
        sock.sendall(message)
        message = "dashboard.web." + dest + ".probability" + " " + str(prob) + " " + str(ts) + "\n"
        sock.sendall(message)


    message = "dashboard.hosts." + dest + " " + str(prob) + " " + str(ts) + "\n"
    sock.sendall(message)

    sock.close()


def publicIP(ip_addr):
    ip = IP(ip_addr)
    if ip.iptype() == "PRIVATE":
        return False
    else:
        return True

def printIpList(ipList):
    # Print the Header
    print '-'*150
    print ' p-Piracy',' ' *6, 'bytes', ' '*12, 'IP',' '*6,'<---->','    IP',' '*8,'|','        Hostname',' '*3,'<-->','Hostname',' '*30,'|', 'CDN'
    print '-'* 150
    for ip in ipList:
        host1 = ip_host1[ip].split()
        host2 = ip_host2[ip].split()
        print "{: <16}{: <16}{: <2}<--> {: <16} | {: <30} <--> {: <30} | {: <10}".format(p_piracy[ip], bytesout[ip], ip, saddr_d[ip], host1[0], host2[0],cdn_ips[ip])



######



ip_list = []
ip_dict = {}
ip_host1 = {}
ip_host2 = {}
p_piracy = {}
bytesout = {}
saddr_d = {}
cdn_ips = {}
flow_cnt = {}

dbase_name = 'pirates'

def main(argv):

    inputfile = ''
    try:
        opts, args=getopt.getopt(argv,"hi:o",["ifile="])
    except getopt.GetoptError:
        print("dashboard-post-procss.py -i <inputfile>")
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('dashboard-post-process   css.py -i <inputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg

    # print ("Inputfile is:", inputfile)
    fname = inputfile
    # open the file
    with open(fname) as f:
        for line in f:
            #line = f.readline()
# {"time_start": 1525190870.073982, "bytes_out": 600, "sp": 67, "da": "192.168.8.115", "dp": 68, "p_piracy": 0.463818, "sa": "192.168.8.1", "num_pkts_out": 2}
        #    content = [x.strip() for x in content]
            fields = line.split(",")

            st_str = fields[0] # Get time_start
            st_str2 = st_str.split(":")
            time_start = st_str2[1]

            bytes_str = fields[1] # Get bytes_out
            bytes_str2 = bytes_str.split(":")
            bytes_str3 = bytes_str2[1]
            #bytes_str4 = bytes_str3.split('"')
            bytes_out = bytes_str2[1]

            pkts_str = fields[7] # get num_pkts_out
            pkts_str2 = pkts_str.split(":")
            pkts_str3 = pkts_str2[1]
            pkts_str4 = pkts_str3.split("}")
            num_pkts_out = pkts_str4[0]

            sa_string = fields[6] # Get the source address
            sa_string2 = sa_string.split(":")
            sa_string3 = sa_string2[1]
            sa_string4 = sa_string3.split('"')
            saddr = sa_string4[1]

            da_string = fields[3] # Get the DA
            da_string = da_string.split(":")
            da_string2 = da_string[1]
            da_string3 = da_string2.split('"')
            daddr = da_string3[1]

            ip1 = saddr
            ip2 = daddr

            probstring = fields[4]
            prob2 = probstring.split(":")
            prob3 = prob2[1]
            prob4 = prob3.split('}')
            prob = prob4[0]

            # Now check to see if the IPs are in the list
            if ip_list.count(ip1) == 0 :
                addToList(ip1, ip2, prob, bytes_out, num_pkts_out)
            elif ip_list.count(ip2) == 0 :
                addToList(ip2,ip1, prob, bytes_out, num_pkts_out)
            else:
                # we already know of these IPs, maybe we average the probability?
                pass

        printIpList(ip_list)

#        for ip in ip_list:
#            print ("P_piracy: %s | IP: %s <--> %s Hosts: %s <-> %s " % (p_piracy[ip],ip,saddr_d[ip],ip_host1[ip], ip_host2[ip] ))

        #pprint(ip_dict)


if __name__ == "__main__":
    main(sys.argv[1:])

