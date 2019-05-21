import pymongo
import socket
import time
from IPy import IP
import pyasn
#from geoip import geolite2


client = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = client["flowdb"]
if 'agg_flow' in mydb.list_collection_names():
    collection = mydb['agg_flow']
    collection.drop()
annflowc = mydb['ann_flow']
aggflowc = mydb['agg_flow']
mydb.agg_flow.create_index([('da', 1)], unique = False)

keyset = set()
def aggregate(doc):
    sa = doc['sa']
    da = doc['da']
    sp = doc['sp']
    dp = doc['dp']
    f_bytes = doc['bytes_out']
    time_s = doc['time_start']
    time_e = doc['time_end']
    p_malware = doc['p_malware']
    dt = time_e - time_s
    newdoc = doc
    #source_tuple = (sa, sp)
    #dest_tuple = (da, dp)
    ip_tuple = (sa, da)
    #key_t = (source_tuple, dest_tuple)
    if (ip_tuple in keyset):
        query = {'sa': sa, 'da': da}
        newvals = {
            '$inc': {'# of flows': 1, 'total_bytes': f_bytes},
            '$push': {'byte_array': f_bytes, 'time_start': time_s, 'time_end': time_e, 'dt': dt,
                      'dp': dp, 'sp': sp, 'p_malware': p_malware}
                   }
        aggflowc.update_one(query, newvals)
    else:
        keyset.add(ip_tuple)
        newdoc['total_bytes'] = f_bytes
        newdoc['byte_array'] = [f_bytes]
        newdoc['# of flows'] = 1
        newdoc['dt'] = [dt]
        newdoc['time_start'] = [time_s]
        newdoc['time_end'] = [time_e]
        newdoc['dp'] = [dp]
        newdoc['sp'] = [sp]
        newdoc['p_malware'] = [p_malware]
        #derivative of dt
        aggflowc.insert(newdoc)


#da:'34.239.145.113', sa:'72.255.74.114'


counter = 0
init_t = time.time()
last_t = time.time()
for doc in annflowc.find():
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