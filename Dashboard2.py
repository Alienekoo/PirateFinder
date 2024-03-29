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

import socket
from pprint import pprint
import sys, getopt
import warnings
from IPy import IP
import time
from cymruwhois import Client
import os
import csv
from pymongo import MongoClient
import logging
from logging.config import fileConfig
import json
import math



CARBON_SERVER = "127.0.0.1"
CARBON_PORT = 2003

dbase_name = 'pirates'
dashboard_f = False
grafana = True


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
            whitelist.append(line.rstrip().lower())
            line = fp.readline()

def whitelisted(asn):
    for n in asn.split("."):
        if n.lower() in whitelist:
            return True

    for n in asn.split():
        if n.lower() in whitelist:
            return True

    return False


def tryWhoIs(ip_addr):

    try:
        c = Client()
        r = c.lookup(ip_addr)
        name = r.owner
    except:
        name= "unknown"

    return name

hosts = {}
def get_host_name(ip):
    if ip in hosts:
        return hosts[ip]

    try:
        result = socket.gethostbyaddr(ip)
        name = result[0]
    except Exception as e:
        ip = IP(ip)
        if ip.iptype() == 'PRIVATE':
            name = "private"
        else:
            name = tryWhoIs(ip)
    hosts[ip] = name
    return name



def addToGrafana(ts, ip1, ip2, prob, bytes_out, pkts_out):
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

    sock = socket()
    try:
        sock.connect( (CARBON_SERVER, CARBON_PORT))
    except:
        print ("Could NOT connect to Carbon, is Carbon running?")
        sys.exit(1)

    dest = name1.replace(".","-") # replace dots with dashes
    dest = dest.replace(" ","") # remove whitespace
    dest = dest.replace(",","-")
#    ts = int(time.time()) # Get Time stamp in seconds, TODO Use flow start time from NF
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

def gen_csv(csv_file, ipList):

    with open(csv_file, mode='a') as dashboard_file:
        dash_writer = csv.writer(dashboard_file, delimiter=',', quotechar='"')

        for ip in ipList:
            host1 = ip_host1[ip].split()
            host2 = ip_host2[ip].split()
            row = [p_piracy[ip], bytesout[ip], ip, saddr_d[ip], host1[0], host2[0], cdn_ips[ip]]
            # print (row)
            dash_writer.writerow(row)
    dashboard_file.close()

def init_csv(csv_file):
    open(csv_file, mode='w')

ip_dict = {}
ip_host1 = {}
ip_host2 = {}
p_piracy = {}
bytesout = {}
pktsout = {}
saddr_d = {}
cdn_ips = {}
flow_cnt = {}
sp = {}
dp = {}

def addToList(ip_list, ip1, sp1, ip2, dp1, prob, bytes_out, pkts_out, grafana):
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
    pktsout[ip1] = pkts_out
    sp[ip1] = sp1
    dp[ip1] = dp1

    # Check to see if it is in the list of known cdns and public hosts
    cdn_ips[ip1] = 'no'
    for n in name1.split():
        if n in whitelist:
            cdn_ips[ip1] = 'yes'
    for n in name2.split():
        if n in whitelist:
            cdn_ips[ip1] = 'yes'

def printIpList(ipList):
    for ip in ipList:
        host1 = ip_host1[ip].split()
        host2 = ip_host2[ip].split()
        print ("{: <10}{: <8}{: <2}:{: <2}<-->{: <12}:{: <8} | {: <5}<-->{: <30} ".format(p_piracy[ip], bytesout[ip], ip, sp[ip], saddr_d[ip],dp[ip], host1[0], host2[0]))


def is_empty(any):
    if any:
        return False
    else:
        return True

def save_to_mongo2(uri, flow):
    try:
        client = MongoClient(uri)
        db = client.flowDB2
    except Exception as e:
        print(e)
        sys.exit(1)

    try:
        dbResult = db.flows2.insert_one(flow)
        return True
    except Exception as e:
        print(e)
        return False


def save_to_mongo(uri, flow):
    try:
        client = MongoClient(uri)
        db = client.flowDB
    except Exception as e:
        print(e)
        sys.exit(1)

    # See if the flow already exists
    try:
        r = db.flows.find_one({'da':flow['da']})
    except Exception as e:
        print(e)
        sys.exit(1)

    if is_empty(r):
        # Save flow to DB
        flow['count'] = 1 # Init the count
        flow['mean_piracy'] = float(flow['p_malware'])
        flow['max_piracy'] = float(flow['p_malware'])
        flow['score'] = flow['bytes_out']*flow['p_malware']

        ip = flow['sa']

        host1 = get_host_name(ip)
        ip = flow['da']
        host2 = get_host_name(ip)

        flow['host1'] = host1
        flow['host2'] = host2

        try:
            dbResult = db.flows.insert_one(flow)
            return True
        except Exception as e:
            print(e)
            return False
    else:
        r = db.flows.find_one({'da': flow['da']})
        count = r['count']+1
        bytes_out = int(r['bytes_out'])+int(flow['bytes_out'])
        pkts = int(r['num_pkts_out'])+int(flow['num_pkts_out'])
        piracy = float(r['p_malware'])+float(flow['p_malware'])
        mean_piracy = float(float(flow['p_malware']) / (r['count']+1))
        if flow['p_malware'] > r['max_piracy']:
            max_piracy = flow['p_malware']
        else:
            max_piracy = r['max_piracy']

        piracy_score = bytes_out*mean_piracy

        update = {
            'count': count,
            'bytes_out' : bytes_out,
            'num_pkts_out' : pkts,
            'p_piracy': piracy,
            'mean_piracy' : mean_piracy,
            'max_piracy': max_piracy,
            'score': piracy_score
        }
        try:
            dbResult = db.flows.update_one(
                                           {'da': flow['da']},
                                           {
                                               '$set':update
                                           }
                        )
            return True
        except Exception as e:
            print(e)
            return False

#  flow = {'time_start':time_start, 'source_IP':saddr,'dest_IP':daddr,'bytesout':bytes_out, 'num_pkts':num_pkts_out, 'p_piracy':prob}

db_initialized = False


def initMongodb(uri):
    try:
        client = MongoClient(uri)
        db = client.flowDB
    except Exception as e:
        print(e)
        sys.exit(1)

    db_collections = db.collection_names()
    if 'flows' not in db_collections:
        db.create_collection('flows')

    #r = db.command('collstats','flows')
    #if 'capped' not in r:
    #    db.command('convertToCapped', 'results',size=5000000, max=1000000)

    try:
        r= db.flows.create_index([('da',1)],unique = True)
    except Exception as e:
        print(e)
        pass

    db_initialized = True


# Python 2.7
atlas_connection = "mongodb://pymongo:ncta1234@testcluster0-shard-00-00-e9cwj.mongodb.net:27017,testcluster0-shard-00-01-e9cwj.mongodb.net:27017,testcluster0-shard-00-02-e9cwj.mongodb.net:27017/test?ssl=true&replicaSet=testCluster0-shard-0&authSource=admin&retryWrites=true"

# Python 3.6
#atlas_connection = "mongodb+srv://pymongo:ncta1234@testcluster0-e9cwj.mongodb.net/test?retryWrites=true"

parameters_splt = [] # list
def update_params(param_type, params_file):
    if (params_file == ''):
        print "no file name specified"
        return

    f = open(params_file)
    for line in f:
        parameters_splt.append(line)

    f.close()


def classify(flow):
    features = [] # list

    features.append(1) # features[0] = 0.0
    features.append(flow['dp'])
    features.append(flow['sp'])
    try:
        features.append(flow['num_pkts_in'])
    except:
        features.append(0.0)
    try:
        features.append(flow['num_pkts_out'])
    except:
        features.append(0.0)
    try:
        features.append(flow['bytes_in'])
    except:
        features.append(0.0)
    try:
        features.append(flow['bytes_out'])
    except:
        features.append(0.0)

    features.append(0.0)

    duration = flow["time_end"] - flow["time_start"]
    features[7] = duration/1000

    # Lengths
    # Times
    # Byte Distrubtion

    #Score
    try:
        score = 0.0
        index = 0
        for feature in features:
            param = float(parameters_splt[index])
            score = score +(feature * param)
            index = index + 1
    except Exception as e:
        print e

    score = min(-score, 500.0)

    score = 1.0/(1.0+math.exp(score))

    return score



def main(argv):

    inputfile = ''
    mongo_uri = "mongodb://127.0.0.1:27017"
    whitelist_file = "whitelist.txt"
    ip_list = []

    logging.basicConfig(filename="piratefinder.log",level=logging.ERROR)
    logger = logging.getLogger('piratefinder')
    #handler = logging.StreamHandler()
    #formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    #handler.setFormatter((formatter))
    #logger.addHandler((handler))
    #logger.setLevel(logging.ERROR)
    try:
        opts, args=getopt.getopt(argv,"ho:w:x:m:p:",["help","output=","whitelist=","csv=","mongodb=","prob="])
    except getopt.GetoptError:
        print("dashboard-post-procss.py -i <inputfile> -o [Y/N] -w <whitelist> -m <mongo URI>")
        sys.exit(2)

    prob_thresh = .9 # default value

    for opt, arg in opts:
        if opt == '-h':
            print('usage: dashboard-post-process -i <inputfile> -o [Y/N] -w <whitelist> -x <csv file> -x <prob>')
            sys.exit()
        if opt in ("-o", "--output"):
            if arg == 'Y':
                grafana  = True
            else:
                grafana = False
        if opt in ("-w", "--whitelist"):
            whitelist_file = arg
        if opt in ("-m", "--mongodb"):
            mongo_uri = arg
        if opt in ("-x", "--csv"):
            csv_filename = arg
        if opt in ("-p", "--prob"):
            prob_thresh = float(arg)

    if not csv_filename:
        # open the csv file
        init_csv(csv_filename)

    # Populate whitelist
    readWhitelist((whitelist_file))

 #   if mongo_uri:
 #       if not db_initialized:
 #           initMongodb(mongo_uri)

    ts = int(time.time())  # Get Time stamp in seconds

    line_count = 0
    lines_processed = 0
    lines_notprocessed = 0

    update_params("SPLT","/home/ncta/PirateFinder/params_m.txt")

    # Read and process one line at time from stdin
    last_time = time.time()
    for line in sys.stdin:
# {"time_start": 1525190870.073982, "bytes_out": 600, "sp": 67, "da": "192.168.8.115", "dp": 68, "p_piracy": 0.463818, "sa": "192.168.8.1", "num_pkts_out": 2}
        if "version" in line:
            pass
        else:
            line_count += 1
            # For whatever reason there is a - in the timestamp that is messing up the json encoding, so strip that out
            aline = ''.join(char for char in line if ord(char) != 45)
            try:
                j = json.loads(aline)
                # save_to_mongo2(j)
                lines_processed += 1

                p_piracy = classify(j)
                p_malware = j['p_malware']
                print("p_piracy % 2.5f  p_malware % 2.5f" %(p_piracy, p_malware))

                skip_ports = {443, 53, 22}
                if (j['p_malware'] > prob_thresh) and (j['dp'] not in skip_ports) and (j['sp'] not in skip_ports) :

                    source = get_host_name(j['sa']) # Check to see if the ASN is on the white list
                    destination = get_host_name(j['da'])
                    if not whitelisted(source) and not whitelisted(destination):
                        #save_to_mongo(mongo_uri, j)
                        #save_to_mongo2(mongo_uri,j)




                        if ip_list.count(j['sa']) == 0 :
                            addToList(ip_list, j['sa'], j['sp'], j['da'], j['dp'], j['p_malware'], j['bytes_out'], j['num_pkts_out'], False)
                        elif ip_list.count(j['da']) == 0 :
                            addToList(ip_list, j['da'], j['sp'], j['sa'], j['dp'], j['p_malware'], j['bytes_out'], j['num_pkts_out'], False)
                        else:
                            # we already know of these IPs, maybe we average the probability?
                            pass

            except Exception as e:
                logger.error(str(e))
                lines_notprocessed += 1
                pass # keep going


            if ip_list:
                printIpList(ip_list)
                # gen_csv(csv_filename, ip_list)
                ip_list = []







if __name__ == "__main__":
    main(sys.argv[1:])

