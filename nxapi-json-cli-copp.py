import requests
import json
import time

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

switchuser='admin'
switchpassword='cisco!123'


url='https://10.66.94.199/ins'
myheaders={'content-type':'application/json'}
payload={
  "ins_api": {
    "version": "1.0",
    "type": "cli_show",
    "chunk": "0",
    "sid": "sid",
    # "input": "show version ; show hardware ; show ip interface brief",
    "input": "show policy-map interface control-plane",
    "output_format": "json"
  }
}

start = time.time()
response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword), verify=False).json()
for x in response["ins_api"]["outputs"]["output"]['body']['TABLE_cmap']['ROW_cmap']:
    print(x['cmap-key'])
    for y in x['TABLE_slot']['ROW_slot']:
        print(f"Slot Num : {y['slot-no-out']} and viloate-avg-rate : {y['violate-avg-rate']}")
    print("\n")
print(len(x), len(y))

end = time.time()
print("How long it takes to run this :", (end-start) * 10**3, "ms")