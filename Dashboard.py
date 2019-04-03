#!/usr/bin/python

"""
MIT License

Copyright (c) 2019 NCTA - The Internet & Television Association

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from socket import socket
from pprint import pprint
import sys, getopt
import warnings
from IPy import IP
import time
from cymruwhois import Client
import os


CARBON_SERVER = "127.0.0.1"
CARBON_PORT = 2003

#whitelist = {'AKAMAI', 'akamai', 'Google', 'MSFT', 'AMAZON-AES', 'CMCS',
#             'MICROSOFT-CORP-MSN-AS-BLOCK'}

whitelist = []

def readWhitelist(filename):

    if not os.path.isfile(filename):
        print("File {} not found".format(filename))
    with open (filename) as fp:
        line = fp.readline()
        while line:
            # add to whitelist
            whitelist.append(line.rstrip())
            line = fp.readline()


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


    # Check to see if it is in the list of known cdns and public hosts
    cdn_ips[ip1] = 'no'
    for n in name1.split():
        if n in whitelist:
            cdn_ips[ip1] = 'yes'
    for n in name2.split():
        if n in whitelist:
            cdn_ips[ip1] = 'yes'


    if dashboard_f == True:
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
    print ('-'*150)
    print (' p-Piracy',' ' *6, 'bytes', ' '*12, 'IP',' '*6,'<---->','    IP',' '*8,'|','        Hostname',' '*3,'<-->','Hostname',' '*30,'|', 'White-List')
    print ('-'* 150)
    for ip in ipList:
        host1 = ip_host1[ip].split()
        host2 = ip_host2[ip].split()
        print ("{: <16}{: <16}{: <2}<--> {: <16} | {: <30} <--> {: <30} | {: <10}".format(p_piracy[ip], bytesout[ip], ip, saddr_d[ip], host1[0], host2[0],cdn_ips[ip]))



ip_list = []
ip_dict = {}
ip_host1 = {}
ip_host2 = {}
p_piracy = {}
bytesout = {}
saddr_d = {}
cdn_ips = {}
flow_cnt = {}
dashboard_f = False

dbase_name = 'pirates'

def main(argv):

    inputfile = ''
    try:
        opts, args=getopt.getopt(argv,"hi:o:w:",["help","ifile=","output=","whitelist="])
    except getopt.GetoptError:
        print("dashboard-post-procss.py -i <inputfile> -o [Y/N]")
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('usage: dashboard-post-process -i <inputfile> -o [Y/N] -w <whitelist>')
            sys.exit()
        if opt in ("-i", "--ifile"):
            inputfile = arg
        if opt in ("-o", "--output"):
            if arg == 'Y':
                dashboard_f = True
            else:
                dashboard_f = False
        if opt in ("-w", "--whitelist"):
            whitelist_file = arg

    #Populate whitelist
    readWhitelist((whitelist_file))

    # print ("Inputfile is:", inputfile)
    fname = inputfile
    # open the file
    with open(fname) as f:
        for line in f:
            #line = f.readline()
# {"time_start": 1525190870.073982, "bytes_out": 600, "sp": 67, "da": "192.168.8.115", "dp": 68, "p_piracy": 0.463818, "sa": "192.168.8.1", "num_pkts_out": 2}

            try:
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
            except:
                print ("Exception processing ", line)

        printIpList(ip_list)




if __name__ == "__main__":
    main(sys.argv[1:])

