"""
@author: georg

Extract summary features about the participation of nodes in the cascades
Extract node centralities from the follower network and the cascades
Extract the train node cascades without duplicates
"""


import os
import time
import numpy as np
import igraph as ig
import pandas as pd
import json


def remove_duplicates(cascade_nodes,cascade_times):
    """
    # Some tweets have more then one retweets from the same person
    # Keep only the first retweet of that person
    """
    duplicates = set([x for x in cascade_nodes if cascade_nodes.count(x)>1])
    for d in duplicates:
        to_remove = [v for v,b in enumerate(cascade_nodes) if b==d][1:]
        cascade_nodes= [b for v,b in enumerate(cascade_nodes) if v not in to_remove]
        cascade_times= [b for v,b in enumerate(cascade_times) if v not in to_remove]

    return cascade_nodes, cascade_times

"""
Main
"""

os.chdir("Path/To/Data")

log= open("time_log.txt","a")
print("Reading the network")

g = ig.Graph.Read_Ncol("digg_network.txt")

f = open("train_cascades.csv")  
#inf2vec_set = open("inf2vec_set.txt","w")
#node_cascades = {}  

#----- Iterate through training cascades
deleted_nodes = []
g.vs["Cascades_started"] = 0
g.vs["Cumsize_cascades_started"] = 0
g.vs["Cascades_participated"] = 0
g.es["Inf"] = 0
g.es["Dt"] = 0
node_cascades = {}


idx=0
start = time.time()
to_train_on = open("/train_set.txt","w")
for line in f:        
    cascade = line.replace("\n","").split(";")
    cascade_nodes = map(lambda x:  x.split(" ")[0],cascade[1:])
    cascade_times = map(lambda x:  x.replace("\r","").split(" ")[1],cascade[1:])
    
    #---- Remove retweets by the same person in one cascade
    cascade_nodes, cascade_times = remove_duplicates(cascade_nodes,cascade_times)
    
    #---------- Dictionary nodes -> cascades
    op_id = cascade_nodes[0]
    
    #---------- Update metrics
    try:
        g.vs.find(name=op_id)["Cascades_started"]+=1
        g.vs.find(op_id)["Cumsize_cascades_started"]+=len(cascade_nodes)
    except: 
        deleted_nodes.append(op_id)
        continue
    
    if(len(cascade_nodes)<2):
        continue
    
    #---- Derive propagation network
    prop_net = ig.Graph(directed=True)

    prop_net.add_vertices(cascade_nodes)

    #---- Data-based weighing
    for i in range(len(cascade_nodes)): 
        #--- Update participation
        if(i!=0):
            try:
                g.vs.find(name=cascade_nodes[i])["Cascades_participated"]+=1
            except:
                prop_net.delete_vertices(cascade_nodes[i])
                continue
           
    no_samples = round(len(cascade_nodes)*sampling_perc/100)
	times = [op_time/(abs((cascade_times[i]-op_time))+1) for i in range(0,len(cascade_nodes))]
	s_times = sum(times)
	if s_times==0:
		samples = []	
	else:
	   probs = [float(i)/s_times for i in times]
		samples = np.random.choice(a=cascade_nodes, size=int(no_samples), p=probs) 
	
    for i,v in enumerate(prop_net.vs):
        try:
            g.vs.find(name=v["name"])["Cascading_outdegree"] += degrees[i] 
        except:
            deleted_nodes.append(v["name"])
			
   if op_id in node_cascades:
        node_cascades[op_id].append(cascade_nodes)
    else:
        node_cascades[op_id] =  []
        node_cascades[op_id].append(cascade_nodes)
		for i in samples:
			#---- Write inital node, copying node, copying time, length of cascade
			to_train_on.write(str(op_id)+","+i+","+casc_len+"\n")
    idx+=1
    if(idx%1000==0):
        print("-------------------",idx)
    
 
        
#-----80 deleted nodes
print("Number of nodes not found in the graph: ",len(deleted_nodes))
f.close()

log.write("Training time digg:"+str(time.time()-start)+"\n")

f= open("digg_node_cascades.json","w")
f.write(json.dumps(node_cascades))
f.close()

start = time.time()
kcores = g.shell_index()
log.write("K-core time:"+str(time.time()-start)+"\n")


#------ Store node charateristics
pd.DataFrame({"Node":g.vs["name"],
              "Kcores":kcores,
			  "avg_cascades_size": g.vs["Cumsize_cascades_started"]/g.vs["Cascades_started"]}).to_csv("node_features.csv",index=False)

