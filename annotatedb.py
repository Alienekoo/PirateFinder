import pymongo
import socket
import time
from IPy import IP
import pyasn
from geoip import geolite2
#import re
#import json
#from urllib2 import urlopen

hosts = {}
asns = {}
geoloc = {}
asndb = pyasn.pyasn('ipasn_db.dat')
def get_host_name(ip):
    name = ''
    asn, cidr = asndb.lookup(ip)

    if cidr in hosts:
        return hosts[cidr][0], asn, hosts[cidr][1]

    try:
        result = socket.gethostbyaddr(ip)
        name = result[0]
        fullgeo = geolite2.lookup(ip)
        geo = fullgeo.location
    except:
        ip = IP(ip)
        if ip.iptype() == 'PRIVATE':
            name = "private"
        geo = 'Unknown'

            #name = tryWhoIs(ip)
    hosts[cidr] = [name, geo]
    return name, asn, geo

keys = {}
'''
def aggregate(doc):
    sa = doc['sa']
    da = doc['da']
    sp = doc['sp']
    dp = doc['dp']
    f_bytes = doc['bytes_out']
    source_tuple = (sa, sp)
    dest_tuple = (da, dp)
    key_t = (source_tuple, dest_tuple)
    if (key_t in keys):
        keys[key_t]
    else:
        keys[key_t] = [f_bytes, 1, [f_bytes],]
'''

client = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = client["flowdb"]
if 'ann_flow' in mydb.list_collection_names():
    collection = mydb['ann_flow']
    collection.drop()
iflowc = mydb['flowcoll']
#sif 'ann_flow' not in mydb.list_collection_names():
    #mydb.create_collection('ann_flow', capped=True, size = 500000, max = 1000000)
annflowc = mydb['ann_flow']
mydb.ann_flow.create_index([('da', 1)], unique = False)



#{ip address : {asn, organization, location}}

counter = 0
init_t = time.time()
last_t = time.time()
for doc in iflowc.find():
    newdoc = doc

    sa = doc['sa']
    da = doc['da']

    reversed_sa, s_asn, s_geo = get_host_name(sa)
    reversed_da, d_asn, d_geo = get_host_name(da)

    newdoc['Source Host Name'] = reversed_sa
    newdoc['Dest Host Name'] = reversed_da
    newdoc['Source ASN'] = s_asn
    newdoc['Dest ASN'] = d_asn
    newdoc['Source Lat/Lng'] = s_geo
    newdoc['Dest Lat/Lng'] = d_geo
    annflowc.insert(newdoc)

    counter += 1
    if counter % 1000 == 0:
        dt = time.time() - last_t
        lines_per_sec = 1000 / dt
        print("Lines per second: ", lines_per_sec)
        last_t = time.time()
dt = time.time() - init_t
lines_per_sec = counter/dt
print("Finished. Lines per second: ", lines_per_sec)