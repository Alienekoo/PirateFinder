
import sys, getopt
import time
from pymongo import MongoClient
import json
from threading import Thread




# Python 2.7
atlas_connection = "mongodb://pymongo:ncta1234@testcluster0-shard-00-00-e9cwj.mongodb.net:27017,testcluster0-shard-00-01-e9cwj.mongodb.net:27017,testcluster0-shard-00-02-e9cwj.mongodb.net:27017/test?ssl=true&replicaSet=testCluster0-shard-0&authSource=admin&retryWrites=true"

# Python 3.6
#atlas_connection = "mongodb+srv://pymongo:ncta1234@testcluster0-e9cwj.mongodb.net/test?retryWrites=true"


def initMongodb(uri):
    try:
        client = MongoClient(uri)
        db = client.joyDB
    except Exception as e:
        print(e)
        sys.exit(1)

    db_collections = db.collection_names()
    if 'flows' not in db_collections:
        db.create_collection('flows')



def worker(line):

    aline = ''.join(char for char in line if ord(char) != 45)
    j = json.loads(aline)

    try:
        client = MongoClient(atlas_connection)
        db = client.joyDB

    except Exception as e:
        print(e)
        sys.exit(1)

    try:
        dbResult = db.flows.insert(j)
        return True
    except Exception as e:
        print(e)
        return False

    return

class DataInsertThread(Thread):
    database = None
    threadNumber = None

    def __init__(self,database_in, threadNumber, flow):
        self.database = database_in
        self.threadNumber = threadNumber
        self.flow = flow
        Thread.__init__(self)

    def run(self):
        self.database.flows.insert(self.flow)

THREAD_COUNT = 2

def main(argv):

    mongo_uri = atlas_connection

    try:
        client = MongoClient(mongo_uri)
        db = client.joyDB
    except Exception as e:
        print(e)
        sys.exit(1)

    db_collections = db.collection_names()
    if 'flows' not in db_collections:
        db.create_collection('flows')


    line_count = 0

    databaseobject = client.sample
    threads = []
    # Read and process one line at time from stdin
    last_time = time.time()
    bulk = []
    count = 0
    for line in sys.stdin:
        line_count += 1
        aline = ''.join(char for char in line if ord(char) != 45)
        j = json.loads(aline)
        bulk.append(j)
        if line_count % 1000 == 0:
            try:
                dbResult = db.flows2.insert_many(bulk)
            except Exception as e:
                print(e)
            bulk = []

            print "Lines processed", line_count
            delta_t = time.time() - last_time
            lines_per_sec = line_count / delta_t
            print "Lines per second:", lines_per_sec
            line_count = 0
            last_time = time.time()


if __name__ == "__main__":
    main(sys.argv[1:])
