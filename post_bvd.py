#!/usr/bin/python
# Post data to BVD endpoint -pete 2016-10-17

#import requests
from requests import Request, Session
from time import sleep
from requests.auth import HTTPBasicAuth
import StringIO
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()


def post_bvd(input_fileh, output_fileh, apikey, bvd_url):
    

    
    s = Session()
    s.headers.update({'Content-Type': 'application/json'})
    REQ_WAIT_TIME = 0.5
    verify='/etc/ssl/certs/ca-certificates.crt'
    
    REQ=[]
    for e in input_fileh:
        REQ.append({
            "req":Request(
                "POST",
                "{}/api/submit/{}/dims/ciId,kpiName/tags/eum"
                    .format(bvd_url, apikey),
                data = e
            )
        })

    output = StringIO.StringIO()

    for e in REQ:
    
      req = s.prepare_request(e["req"])
      res = s.send(req, verify=verify)
      
      
      print >>output_fileh,res.content
      sleep(REQ_WAIT_TIME)

    

    
    

    
    