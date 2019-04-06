# -*- coding: utf-8 -*-
"""
@author: georg

Create the train and test set (2011.10.29 -2012.9.28) and test (2012.9.28 -2012.10.29)
"""

import os
import time


def split_train_and_test(cascades_file):
    """
    # Splits the cascades into those that start before and after the 25th day of recording
    # Keeps the ids of the users that are actively retweeting
    """
    
    f = open(cascades_file)
    ids = set()
    train_cascades = []
    test_cascades = []
    counter = 0
    
    for line in f: 
        
        date = line.split(" ")[1].split("-")
        original_user_id = line.split(" ")[2]
        
        retweets = f.next().replace(" \n","").split(" ")
        #----- keep only the cascades and the nodes that are active in train (2011.10.29 -2012.9.28) and test (2012.9.28 -2012.10.29)
           
        retweet_ids = ""
        
        #------- last month at test
        if int(date[0])==2012 and ((int(date[1])>=9 and int(date[2])>=28)  or (int(date[1])==10  and int(date[2])<=29)): 
            ids.add(original_user_id)           
           
            cascade = ""
            for i in range(0,len(retweets)-1,2):
                ids.add(retweets[i])
                retweet_ids = retweet_ids+" "+retweets[i]
                cascade = cascade+";"+retweets[i]+" "+retweets[i+1]
               
           #------- For each cascade keep also the original user and the relative day of recording (1-32)
            date = str(int(date[2])+3)
            op = line.split(" ")
            op = op[2]+" "+op[1]
            test_cascades.append(date+";" +op+cascade)
    
       #------ The rest are used for training
        elif (int(date[0])==2012 and int(date[1])<9 and int(date[2])<28) or (int(date[0])==2011 and int(date[1])>=10 and int(date[2])>=29):
             
            ids.add(original_user_id)          
            cascade = ""          
            for i in range(0,len(retweets)-1,2):
                ids.add(retweets[i])
                retweet_ids = retweet_ids+" "+retweets[i]
                cascade = cascade+";"+retweets[i]+" "+retweets[i+1]
            if(int(date[1])==9):
                date = str(int(date[2])-27)
            else:
                date = str(int(date[2])+3)
            op = line.split(" ")
            op = op[2]+" "+op[1]
            train_cascades.append(date+";" +op+cascade)
           
        counter+=1    
        if (counter % 10000==0):
            print("------------"+str(counter))
    f.close()
    
    return train_cascades, test_cascades, ids 




"""
Main
"""

os.chdir("Path/To/Init_Data")


start = time.time()

#------ Split the original retweet cascades
train_cascades, test_cascades, ids  = split_train_and_test("Init_Data\\total.txt")

#------ Store the cascades
print "Size of train:",len(train_cascades)
print "Size of test:",len(test_cascades)

with open("\\train_cascades.txt","w") as f:
    for cascade in train_cascades:
        f.write(cascade+"\n")

with open("\\test_cascades.txt","w") as f:
    for cascade in test_cascades:
        f.write(cascade+"\n")

#------- Keep the processing time
log.write("Cascade extraction time :"+str(time.time()-start)+"\n")

start = time.time()

#------ Store the active ids
f = open("\\active_users.txt","w")
for uid in ids:
    f.write(uid+"\n")
f.close()


#------ Keep the subnetwork of the active users
g = open("\\active_network.txt","w")

f = open("Init_Data\\graph_170w_1month.txt","r")

found =  0
idx=0
for line in f:
    edge = line.replace("\n","").split(" ")
    
    if edge[0] in ids and edge[1] in ids and edge[2]=='1':
        found+=1
        g.write(line)
    idx+=1    
    if (idx%2000000==0):
        print(idx)
        print(found)
        print("---------")

g.close()

f.close()

