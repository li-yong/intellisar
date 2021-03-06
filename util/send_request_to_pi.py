#!/usr/bin/env python
import time
import logging
import datetime
import sys
import requests
import json
import argparse

global TIMEOUT
TIMEOUT = 5

def request(pi_ip, sequence, distance):
    url = 'http://'+pi_ip+'/test'

    ts1 = time.time()
    ts1a = datetime.datetime.timestamp(datetime.datetime.now())
    ts1b = datetime.datetime.now()

    data = {'distance':distance, 'sequence':sequence, 'ts1':ts1, 'ts1a':ts1a, 'ts1b':ts1b }
    #print(str(sentts)+", post url: "+url+", data:"+str(data))

    try:
        r = requests.post(url, data=data, timeout=TIMEOUT)
    except requests.exceptions.RequestException as e:
        print("seq "+str(sequence)+" timed out. > "+str(TIMEOUT)+" seconds")
        return(-1)

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
    #print("delay "+str(delay)+" ms distance "+str(distance) )
    return(delay)



def delay_statistic(pi_ip, packetcnt, distance):
    ##distance = 100
    n = packetcnt
    delay = 0
    timeoutcnt = 0
    cnt = 0
    for i in range(n):
        rst = request(pi_ip, sequence=i, distance=distance)

        if rst == -1:
            timeoutcnt += 1
        else:
            delay += rst

    notimeoutcnt = n-timeoutcnt
    if notimeoutcnt == 0:
        delay = "Null" #all packets have timeout
    else:
        delay = round(delay /notimeoutcnt, 2)
    timeout_rate = round(timeoutcnt/n, 2)
    print("Distance " + str(distance)+", timeout ratio "+str(timeout_rate)+", average delay " + str(delay) + " ms")

def measure_max_distance(pi_ip):
    i=0
    while(1):
        try:
            delay = request(pi_ip, sequence=i, distance=0)
        except requests.exceptions.RequestException as e:
            print("timeout at sequence " + str(i))
            delay = "Timeout > "+str(TIMEOUT)+" seconds"
        i += 1
        time.sleep(1)
        print("seq "+str(i)+", delay "+str(delay)+" ms")


if __name__ == "__main__":
    # Define and parse input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', help='<m: measure_max_distance|d: dalay_statistic>', default='d')
    parser.add_argument('--ip', help='ip of pi')
    parser.add_argument('--packets', help='how many packets sent to server ', default=100)
    parser.add_argument('--distance', help='distance of robot to hotspot', default=0)

    args = parser.parse_args()

    #measure_max_disstance()
    if (args.mode == "d"):
        delay_statistic(args.ip, int(args.packets), int(args.distance))
    elif (args.mode == "m"):
        measure_max_distance(args.ip)

#python send_request_to_pi.py --mode d  --ip 192.168.59.136:8080 --packets 300 --distance 10
#python send_request_to_pi.py --mode m  --ip 192.168.59.136:8080
#pi_ip= "192.168.199.142" #homewifi
#pi_ip= "192.168.43.9" #mobile hotspot mixrrr