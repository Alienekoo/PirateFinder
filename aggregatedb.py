import pymongo
import socket
import time
from IPy import IP
import pyasn
#from geoip import geolite2


client = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = client["flowdb"]
cname = raw_input('What is the annotated collection name? ')
aname = raw_input('Name the aggregated collection: ')
if aname in mydb.list_collection_names():
    collection = mydb[aname]
    collection.drop()
annflowc = mydb[cname]
aggflowc = mydb[aname]
aggflowc.create_index([('da', 1)], unique = False)

keyset = set()
def aggregate(doc):
    sa = doc['sa']
    da = doc['da']
    sp = doc['sp']
    dp = doc['dp']
    o_bytes = doc['bytes_out']
    try:
        i_bytes = doc['bytes_in']
    except:
        i_bytes = 0
    try:
        i_pkts = doc['num_pkts_in']
    except:
        i_pkts = 0
    try:
        o_pkts = doc['num_pkts_out']
    except:
        o_pkts = 0
    time_s = doc['time_start']
    time_e = doc['time_end']
    p_malware = doc['p_malware']
    byte_dist = doc['byte_dist']
    dt = time_e - time_s
    packets = doc['packets']
    newdoc = doc
    ip_tuple = (sa, da)
    if (ip_tuple in keyset):
        query = {'sa': sa, 'da': da}
        aggdoc = aggflowc.find_one(query)
        agg_time_start = aggdoc['time_start']
        #agg_time_end = aggdoc['time_end']
        a = aggdoc['byte_dist']
        for i in range(len(a)):
            byte_dist[i] += a[i]
        newvals = {
            '$inc': {'# of flows': 1, 'total_bytes': o_bytes + i_bytes, 'bytes_in': i_bytes, 'bytes_out': o_bytes,
                     'num_pkts_in': i_pkts, 'num_pkts_out': o_pkts, 'total_num_pkts': i_pkts + o_pkts},
                     #'byte_dist.$[]': byte_dist[]},
            '$push': {'byte_array': i_bytes + o_bytes, 'time_start': time_s, 'time_end': time_e, 'dt': dt,
                      'dp': dp, 'sp': sp, 'p_malware': p_malware, 'conv_packets': packets,
                      'ift': abs(time_s - agg_time_start[aggdoc['# of flows'] - 1])},
            '$set': {'conv_time': time_e - agg_time_start[0], 'byte_dist': byte_dist}
                   }
        aggflowc.update_one(query, newvals)
        #keyset[ip_tuple] += 1

    else:
        keyset.add(ip_tuple)
        newdoc['total_bytes'] = i_bytes + o_bytes
        newdoc['byte_array'] = [i_bytes + o_bytes]
        newdoc['# of flows'] = 1
        newdoc['dt'] = [dt]
        newdoc['time_start'] = [time_s]
        newdoc['time_end'] = [time_e]
        newdoc['dp'] = [dp]
        newdoc['sp'] = [sp]
        newdoc['p_malware'] = [p_malware]
        newdoc['conv_packets'] = [packets]
        newdoc['conv_time'] = time_e - time_s
        newdoc['ift'] = [0]
        newdoc['bytes_in'] = i_bytes
        newdoc['bytes_out'] = o_bytes
        newdoc['total_num_pkts'] = i_pkts + o_pkts
        newdoc['num_pkts_in'] = i_pkts
        newdoc['num_pkts_out'] = o_pkts
        newdoc['byte_dist'] = byte_dist
        #derivative of dt
        aggflowc.insert(newdoc)


#da:'34.239.145.113', sa:'72.255.74.114'


counter = 0
init_t = time.time()
last_t = time.time()
for doc in annflowc.find(no_cursor_timeout=True):
    aggregate(doc)

    counter += 1
    if counter % 1000 == 0:
        dt = time.time() - last_t
        lines_per_sec = 1000 / dt
        print("Lines per second: ", lines_per_sec)
        last_t = time.time()
dt = time.time() - init_t
lines_per_sec = counter / dt
print("Finished. Lines per second: ", lines_per_sec)