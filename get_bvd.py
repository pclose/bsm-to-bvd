#!/usr/bin/python
# Gets CI statuses from BSM -pete 2016-10-14

#import requests
from requests import Request, Session
from time import sleep
from datetime import datetime as dt
from datetime import timedelta as td
from lxml import etree
#from requests.auth import HTTPBasicAuth
import re,StringIO,sys,getpass
import random
import json
import logging
L = logging.getLogger()
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()


TARGET_KPI = "Application Availability"
MINUTES = 1

def print_everything(req,result):
  print "----Request Method and URL----"
  print req.method,req.url
  print "----Request Headers----"
  print '\n'.join([x+': '+y for x,y in req.headers.items()])
  print "----POST Data----"
  print req.body

  print "----Result Status----"
  print result.status_code
  print "----Result Headers----"
  print '\n'.join([x+': '+y for x,y in result.headers.items()])
  print "----Result Body----"
  print ''.join(result.iter_lines())

def get_status(username, password, bsm_url, inputfh, outputfh):
        
    s = Session()
    s.headers.update({'Content-Type': 'application/json'})
    s.auth = (username, password)
    REQ_WAIT_TIME = 0.5
    verify = False
    
    urlt = "{}/topaz/servicehealth/customers/1/kpiOverTime?ciIds={{}}&startDate={{}}&endDate={{}}"
    url = urlt.format(bsm_url)

    ciids = []
    for e in inputfh:
        e = e.replace('\n', '').replace('\r','').split()[0]
        ciids.append(e)
        
    start_time = dt.strftime(dt.now() - td(minutes=MINUTES), "%s")
    end_time = dt.strftime(dt.now(), "%s")
    REQ=[]
    for e in ciids:
        REQ.append({
            "req":Request(
                "GET",
                url.format(e, start_time, end_time),
            ),
            "value":e
        })

    
    output = StringIO.StringIO()
    
    result = []
    
    for e in REQ:
        output = StringIO.StringIO()
        req = s.prepare_request(e["req"])
        res = s.send(req, verify=verify)
        #print_everything(req,res)
        
        print >>output,res.content
        try:
            ee = etree.fromstring(output.getvalue())
            
            if len(ee) < 1: 
                r = {
                    "ciId":e["value"], 
                    "status": "No Data",
                    "kpiName": TARGET_KPI
                }
                result.append(r)
            
            for i in ee:
                if TARGET_KPI == i.find("kpiDisplayName").text:
                
                    status = i.find("statusDisplayName").text
                    if status:
                        r = {
                            "ciId":e["value"], 
                            "status": status,
                            "kpiName": TARGET_KPI
                        }
                        
                    else:
                        r = {
                            "ciId":e["value"], 
                            "status": "No Data",
                            "kpiName": TARGET_KPI
                        }
                    
                    result.append(r)
                    L.debug(r)
        except Exception, ex:
            L.debug("{} at Line #: {}".format(ex, sys.exc_info()[2].tb_lineno))
            L.error("Problem getting statuses from BSM HTTP Status: {}".format(res.status_code))
        
        
        sleep(REQ_WAIT_TIME)
    
    print >>outputfh, json.dumps(result)



def get_status_definitions(username, password, bsm_url):
    s = Session()
    s.headers.update({'Content-Type': 'application/json'})
    s.auth = (username, password)
    REQ_WAIT_TIME = 0.5
    verify = False
    
    urlt = "{}/topaz/servicehealth/customers/1/repositories/indicators/statuses"
    url = urlt.format(bsm_url)
        
    response = s.get(url, verify=verify).content
    e = etree.fromstring(response)
    for i in e:
        print i.find("id").text, i.find("name").text
        


def shorten_words(value, length):
    if not length or len(value) <= length: return value
    
    half = len(value)/6
    first = value[0:half]
    second = value[half:len(value)]
    start = second.split(" ")
    result = first + start[0] + " "
    
    for e in start[1:]:
        result = result + e[0:3] + " "
    
    if "(" in result and ")" not in result: result = result.replace("(", "")
    
    if len(result) > length: return result[0:length]
    
    return result[0:-1]

def get_ci_info(username, password, bsm_url, str_size=0):

    urlt = "{}/topaz/eumopenapi/bpm/application"
    url = urlt.format(bsm_url)
    
    verify = False

    s = Session()
    s.auth = (username, password)
    response = s.get(url, verify=verify)
        
    if response.status_code != 200:
        raise Exception(response.status_code)
        return []
    
    data = etree.fromstring(response.content)
    
    result = []
    
    for e in data:
        ciid = e.find("ci_id").text
        name = shorten_words(e.find("name").text, str_size)
        result.append([str(ciid), str(name)])
        
    random.shuffle(result)
    return result
    

if __name__ == "__main__":
    
    #if len(sys.argv) > 2 and sys.argv[2] != "": username = sys.argv[2]
    #else: username = raw_input("Username: ")
    #if len(sys.argv) > 3 and sys.argv[3] != "": password = sys.argv[3]
    #else: password = getpass.getpass("Password for {}: ".format(username))
    #if len(sys.argv) > 4: get_status(username, password, sys.argv[4])
    #else: get_status(username, password, "intg")
    print "\n".join (
        map(lambda i: "{} {}".format(i[0], i[1]),  get_ci_info(sys.argv[1], sys.argv[2], sys.argv[3]))
    )
