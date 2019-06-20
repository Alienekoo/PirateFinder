import numpy as np
import pandas as pd
from sklearn.model_selection import GridSearchCV, learning_curve
from sklearn.metrics import accuracy_score, make_scorer

import json


def getFlowData(json_file):
    flows = []
    with open(json_file, 'r') as fp:
        try:
            for line in fp:
                try:
                    tmp = json.loads(line)
                    if 'version' not in tmp:
                        flows.append(tmp)
                except:
                    continue
        except:
            return
    return flows


def getByteDistribution(flows):
    if flows == []:
        return None

    data = []
    for flow in flows:
        if len(flow['packets']) == 0:
            continue
        if 'byte_dist' in flow and sum(flow['byte_dist']) > 0:
            tmp = map(lambda x: x / float(sum(flow['byte_dist'])), flow['byte_dist'])
            data.append(tmp)
        else:
            data.append(np.zeros(256))

    return data


def getIndividualFlowPacketLengths(flows):
    if flows == []:
        return None

    data = []
    numRows = 10
    binSize = 150.0

    for flow in flows:
        transMat = np.zeros((numRows, numRows))
        if len(flow['packets']) == 0:
            continue
        elif len(flow['packets']) == 1:
            curPacketSize = min(int(flow['packets'][0]['b'] / binSize), numRows - 1)
            transMat[curPacketSize, curPacketSize] = 1
            data.append(list(transMat.flatten()))
            continue

        # get raw transition counts
        for i in range(1, len(flow['packets'])):
            prevPacketSize = min(int(flow['packets'][i - 1]['b'] / binSize), numRows - 1)
            if 'b' not in flow['packets'][i]:
                break
            curPacketSize = min(int(flow['packets'][i]['b'] / binSize), numRows - 1)
            transMat[prevPacketSize, curPacketSize] += 1

        # get empirical transition probabilities
        for i in range(numRows):
            if float(np.sum(transMat[i:i + 1])) != 0:
                transMat[i:i + 1] = transMat[i:i + 1] / float(np.sum(transMat[i:i + 1]))

        data.append(list(transMat.flatten()))

    return data


def getIndividualFlowIPTs(flows):
    if flows == []:
        return None

    data = []

    numRows = 10
    binSize = 50.0

    for flow in flows:
        transMat = np.zeros((numRows, numRows))
        if len(flow['packets']) == 0:
            continue
        elif len(flow['packets']) == 1:
            curIPT = min(int(flow['packets'][0]['ipt'] / float(binSize)), numRows - 1)
            transMat[curIPT, curIPT] = 1
            data.append(list(transMat.flatten()))
            continue

        # get raw transition counts
        for i in range(1, len(flow['packets'])):
            prevIPT = min(int(flow['packets'][i - 1]['ipt'] / float(binSize)), numRows - 1)
            curIPT = min(int(flow['packets'][i]['ipt'] / float(binSize)), numRows - 1)
            transMat[prevIPT, curIPT] += 1

        # get empirical transition probabilities
        for i in range(numRows):
            if float(np.sum(transMat[i:i + 1])) != 0:
                transMat[i:i + 1] = transMat[i:i + 1] / float(np.sum(transMat[i:i + 1]))

        data.append(list(transMat.flatten()))

    return data


def getIndividualFlowMetadata(flows):
    if flows == []:
        return None

    data = []
    for flow in flows:
        if len(flow['packets']) == 0:
            continue
        tmp = []

        key = flow['sa'].replace('.', '') + flow['da'].replace('.', '') + str(flow['sp']) + str(flow['dp']) + str(
            flow['pr'])

        if flow['dp'] != None:
            tmp.append(float(flow['dp']))  # destination port
        else:
            tmp.append(0)  # ICMP/etc.
        if flow['sp'] != None:
            tmp.append(float(flow['sp']))  # source port
        else:
            tmp.append(0)  # ICMP/etc.
        if 'num_pkts_in' in flow:
            tmp.append(flow['num_pkts_in'])  # inbound packets
        else:
            tmp.append(0)
        if 'num_pkts_out' in flow:
            tmp.append(flow['num_pkts_out'])  # outbound packets
        else:
            tmp.append(0)
        if 'bytes_in' in flow:
            tmp.append(flow['bytes_in'])  # inbound bytes
        else:
            tmp.append(0)
        if 'bytes_out' in flow:
            tmp.append(flow['bytes_out'])  # outbound bytes
        else:
            tmp.append(0)
        # elapsed time of flow
        if flow['packets'] == []:
            tmp.append(0)
        else:
            time = 0
            for packet in flow['packets']:
                time += packet['ipt']
            tmp.append(time)

        data.append(tmp)

    if data == []:
        return None
    return data


def getFlowMetadata(flow):
    if flow == []:
        return None
    tmp = []
    data = []

    if flow['dp'] != None:
        tmp.append(float(flow['dp']))  # destination port
    else:
        tmp.append(0)  # ICMP/etc.
    if flow['sp'] != None:
        tmp.append(float(flow['sp']))  # source port
    else:
        tmp.append(0)  # ICMP/etc.
    if 'num_pkts_in' in flow:
        tmp.append(flow['num_pkts_in'])  # inbound packets
    else:
        tmp.append(0)
    if 'num_pkts_out' in flow:
        tmp.append(flow['num_pkts_out'])  # outbound packets
    else:
        tmp.append(0)
    if 'bytes_in' in flow:
        tmp.append(flow['bytes_in'])  # inbound bytes
    else:
        tmp.append(0)
    if 'bytes_out' in flow:
        tmp.append(flow['bytes_out'])  # outbound bytes
    else:
        tmp.append(0)
    # elapsed time of flow
    if flow['packets'] == []:
        tmp.append(0)
    else:
        time = 0
        for packet in flow['packets']:
            time += packet['ipt']
        tmp.append(time)

    data.append(tmp)

    if data == []:
        return None
    return data

benign_file = "/home/ncta/PirateFinder/benign_train/benign.json"
data = []
labels = []
flows = getFlowData(benign_file)
tmpMeta = getIndividualFlowMetadata(flows)
for i in range(len(tmpMeta)):
    tmp = []
    tmp.extend(tmpMeta[i])
    data.append(tmp)
    labels.append(0.0) #Lable it Piracy=1.0, Benign=0.0

#tmpPL = getIndividualFlowPacketLengths(flows)
#for i in range(len(tmpPL)):
#    tmp = []
#    tmp.extend(tmpPL[i])
#    data.append(tmp)
#    labels.append(0.0)

#tmpIPT = getIndividualFlowIPTs(flows)
#for i in range(len(tmpIPT)):
#    tmp = []
#    tmp.extend(tmpIPT)
#    data.append(tmp)
#    labels.append(0.0)

print("Benign data set created from: ", benign_file)

piracy_file = "/home/ncta/PirateFinder/piracy_train/piracy.json"

flows = getFlowData(piracy_file)

# Now get the features of interest from the Joy Flow data

tmpMeta = getIndividualFlowMetadata(flows)

# For each file processed, extend the data set; and then append the extended result
for i in range(len(tmpMeta)):
    tmp = []
    tmp.extend(tmpMeta[i])
    data.append(tmp)
    labels.append(1.0)  # Lable it Piracy=1.0, Benign=0.0

#tmpPL = getIndividualFlowPacketLengths(flows)
#for i in range(len(tmpPL)):
#    tmp = []
#    tmp.extend(tmpPL[i])
#    data.append(tmp)
#    labels.append(1.0)

#tmpIPT = getIndividualFlowIPTs(flows)
#for i in range(len(tmpIPT)):
#    tmp = []
#    tmp.extend(tmpIPT)
#    data.append(tmp)
#    labels.append(1.0)

print("Piracy data set created from ", piracy_file)

def classify(flow):
    # run the flow thru the ML predictor
    # return pred
    return 0


# Take a list of flows, and return a list probabilities or predictions for each flow
def classifyFlows(flows):
    p = []
    for flow in flows:
        if "version" in flow:
            pass  # Skip it
        else:
            try:

                p_piracy = classify(flow)
                p.append(p_piracy)
                # print p_piracy

            except Exception as e:
                # print "Exception:", e
                pass  # keep going

    return p

# Import Random Forest Model
from sklearn.ensemble import RandomForestClassifier

# Create a Gaussian Classifier
clf = RandomForestClassifier(n_estimators=100)

# Train the model

list1 = [['A','B','C'],['D','E','F']]

headings=["DP","SP","PktsIn","PktsOut", "BytesIn", "BytesOut","Packets"]
datapd = pd.DataFrame.from_records(data, columns=headings)
print datapd.head()

clf.fit(data,labels)

RandomForestClassifier(bootstrap=True,class_weight=None, criterion='gini',max_depth=None,
                       max_features='auto',max_leaf_nodes=None,
                       min_samples_leaf=1, min_samples_split=2,
                       min_weight_fraction_leaf=0.0, n_estimators=100, n_jobs=1,
                       oob_score=False, random_state=None, verbose=0,
                       warm_start=False)

feature_imp = pd.Series(clf.feature_importances_,index=headings)

import matplotlib.pyplot as plt
import seaborn as sns
sns.barplot(x=feature_imp, y=feature_imp.index)
plt.xlabel('Feature Importance Score')
plt.ylabel('Features')
plt.title("Visualizing")
plt.legend()
plt.show

def getTestData(file, label):
    flows = getFlowData(piracy_file)

    # Now get the features of interest from the Joy Flow data

    tmpMeta = getIndividualFlowMetadata(flows)
    data = []
    labels = []

    for i in range(len(tmpMeta)):
        tmp = []
        tmp.extend(tmpMeta[i])
        data.append(tmp)
        labels.append(label)

    return data, labels


test_benign = "benign1.json"
test_piracy = "iptvshop.json"

benign_data, benign_labels = getTestData(test_benign, 0.0)
piracy_data, piracy_labels = getTestData(test_piracy, 1.0)

benign_pred = clf.predict(benign_data)
piracy_pred = clf.predict(piracy_data)

from sklearn import metrics

print("Accuracy with benign:", metrics.accuracy_score(benign_labels, benign_pred))
#print(metrics.classification_report(benign_pred, benign_labels))

print("Accuracy with piracy:", metrics.accuracy_score(piracy_labels, piracy_pred))
#print(metrics.classification_report(piracy_pred, piracy_labels))




test_file = "mediacom1small.json"
flows = getFlowData(test_file)
flowcount = 0
piratecount = 0
for flow in flows:
    meta = getFlowMetadata(flow)
    data = []

    flowcount = flowcount+1
    for i in range(len(meta)):
        tmp = []
        tmp.extend(meta[i])
        data.append(tmp)

        # Predict
        prediction = clf.predict_proba(data)
        predict = clf.predict_proba((data))

        if prediction[:,1] >= .9 :
            # print prediction[:,1], flow['sa'], flow['da'], data
            piratecount = piratecount+1

print flowcount, piratecount
