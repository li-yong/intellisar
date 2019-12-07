#!/usr/bin/env python
import time
import logging
import datetime

import requests
import json


def request(sequence, distance):

    pi_ip= "192.168.199.142" #homewifi
    pi_ip= "192.168.43.9" #mixrrr
    #http://pi/test/distance/<distance>/sequence/<sequence>/sentts/<sentts>
    #r =requests.get('http://'+pi_ip+'/distance/')
    #url = 'http://'+pi_ip+'/test/'+'distance/'+distance+'/sequence/'+sequence+'/sentts/'+sentts
    url = 'http://'+pi_ip+'/test'

    #sentts = datetime.datetime.timestamp(datetime.datetime.now())
    ts1 = time.time()
    ts1a = datetime.datetime.timestamp(datetime.datetime.now())
    ts1b = datetime.datetime.now()

    data = {'distance':distance, 'sequence':sequence, 'ts1':ts1, 'ts1a':ts1a, 'ts1b':ts1b }
    #print(str(sentts)+", post url: "+url+", data:"+str(data))
    r = requests.post(url, data=data)

    r = json.loads(r.content)

    ts4=time.time()
    ts4a = datetime.datetime.timestamp(datetime.datetime.now())
    ts4b = datetime.datetime.now()
    #print("I am client. Seq "+str(sequence)+", ts1 "+str(ts1)+", received ts4 "+str(ts4)+", response "+str(r))

    r['ts4']=ts4
    #time.sleep(0.1)

    ts5 = time.time()
    ts5a = datetime.datetime.timestamp(datetime.datetime.now())
    ts5b = datetime.datetime.now()

    r.update({'ts4': ts4, 'ts4a': ts4a, 'ts4b': ts4b})
    r.update({'ts5': ts5, 'ts5a': ts5a, 'ts5b': ts5b})

    #print("")
    #print(r)
    #print("")


    d_12 = float(r['ts2'])-float(r['ts1'])
    d_23 = float(r['ts3'])-float(r['ts2'])
    d_34 = float(r['ts4'])-float(r['ts3'])
    d_14 = float(r['ts4'])-float(r['ts1'])
    d_15 = float(r['ts5'])-float(r['ts1'])

    d_12a = float(r['ts2a'])-float(r['ts1a'])
    d_23a = float(r['ts3a'])-float(r['ts2a'])
    d_34a = float(r['ts4a'])-float(r['ts3a'])
    d_14a = float(r['ts4a'])-float(r['ts1a'])
    d_15a = float(r['ts5a'])-float(r['ts1a'])



    #print("d12 "+str(d_12)+" d23 "+str(d_23)+" d34 "+str(d_34)+" d14 "+str(d_14)+" d15 "+str(d_15))
    #print("d12a "+str(d_12a)+" d23a "+str(d_23a)+" d34a "+str(d_34a)+" d14a "+str(d_14a)+" d15a "+str(d_15a))

    #use the rrt d_14
    delay = d_14*1000/2
    print("dealy "+str(delay)+" ms distance "+str(distance) )
    return(delay)



    pass


def delay_statistic(distance):
    ##distance = 100
    n = 20
    delay = 0
    cnt = 0
    for i in range(n):
        delay += request(sequence=i, distance=distance)
    delay = round(delay / n, 2)
    print("average delay " + str(delay) + " ms at distance " + str(distance))

def measure_max_disstance():
    i=0
    while(1):
        delay = request(sequence=i, distance=0)
        i += 1
        time.sleep(1)
        print("seq "+str(i)+", delay "+str(delay))


if __name__ == "__main__":
    #measure_max_disstance()
    delay_statistic(10)

