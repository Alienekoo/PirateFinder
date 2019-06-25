#!/usr/bin/env python
# coding: utf-8

# Move Joy Flows to MongoDB

# In[18]:


import sys, getopt
import time
from pymongo import MongoClient
import json


# In[19]:


def initMongodb(uri):
    try:
        client = MongoClient(uri)
        db = client.flowdb
    except Exception as e:
        print(e)
        sys.exit(1)


    return db

# In[20]:


# JSON Files to move to MongoDB

# Training Data
p_train = "./piracy_train/piracy.json"
b_train = "./benign_train/benign.json"

# Test Data
b_test = "./test_data/benign1.json"
p_test = "./test_data/iptvshop.json"

test_data = "./test_data/mediacom1.json"

db_name = "flowdb"
p_train_coll = "p2"
p_test_coll = "testP"
b_train_coll = "b2"
b_test_coll = "testB"
net_train_coll = "Netflow"


# In[21]:


# Read the file line by line and write MongoDB
def process_file(filename, db, collection):
    with open(filename,'r') as file:
        for line in file:
            if 'version' not in line:
                aline = ''.join(char for char in line if ord(char) != 45)
                j = json.loads(aline)
                try:
                    dbResult = db[collection].insert_one(j)
                except Exception as e:
                    print(e)


# In[22]:



#mongo_uri = atlas_connection
mongo_uri = "mongodb://localhost:27017/"

db = initMongodb(mongo_uri)

# Now move each JSON file to the MongoDB
process_file(p_train, db, p_train_coll)
process_file(b_train, db, b_train_coll)
process_file(b_test, db, b_test_coll)
process_file(p_test, db, p_test_coll)

print "Done"
#print db.flowdb.stats()


# In[ ]:




