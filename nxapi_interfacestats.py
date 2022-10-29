import argparse
import textwrap
import requests
import json
import urllib3
import time
import sys
import yaml


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Login to NX-API function
def aaa_login(username, password, ip_addr):
    # Define the payload
    payload = {
        'aaaUser': {
            'attributes': {
                'name': username,
                'pwd': password
            }
        }
    }
    url = "https://" + ip_addr + "/api/mo/aaaLogin.json"
    auth_cookie = {}

    # Send the login request
    response = requests.request("POST", url, data=json.dumps(payload), verify=False)

    # Parse the login request and grab the authentication cookie
    if response.status_code == requests.codes.ok:
        data = json.loads(response.text)['imdata'][0]
        token = str(data['aaaLogin']['attributes']['token'])
        auth_cookie = {"APIC-cookie": token}

    # Return status code and authentication cookie
    return response.status_code, auth_cookie

# Logout from NX-API function
def aaa_logout(username, ip_addr, auth_cookie):
    # Define the payload
    payload = {
        'aaaUser': {
            'attributes': {
                'name': username
                }
            }
        }
    url = "https://" + ip_addr + "/api/mo/aaaLogout.json"

    # Send the logout request
    response = requests.request("POST", url, data=json.dumps(payload), cookies=auth_cookie, verify=False)

# NX-API GET function
def nxapi_get(url, auth_cookie):
    response = requests.request("GET", url, cookies=auth_cookie, verify=False)
    return response

# Main function
if __name__ == '__main__':
    # Print help to CLI and parse the arguments
    parser=argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            Cisco Nexus get interface counters via NX-API
            --------------------------------
            Required parameter is the output format (-f json/influxdb)

            Examples for usage:
            python nxapi_interfacestats.py -f json
       '''))

    parser.add_argument('-f', required=True, type=str, dest='arg_format', help='Output format')
    args=parser.parse_args()
    output_format = args.arg_format

    # Verify that correct output format is set
    if output_format not in "json" and output_format not in "influxdb":
        print("Output format not set correctly. Use -f json or influxdb as an argument.")
        sys.exit()

    # Username and password
    # username = 'USERNAME'
    # password = 'PASSWORD'
    username = 'admin'
    password = 'cisco'

    # Array where to include the switches and interfaces to get the data from
    switch_array = {
        'switch1':
            {
                'mgmt': '192.168.160.91',
                'name': 'lf02-04a',
                'interfaces': ['1/49', '1/50']
            },
        'switch2':
            {
                'mgmt': '192.168.160.92',
                'name': 'lf02-04b',
                'interfaces': ['1/49', '1/50']
            }
    }

    # Get timestamp and define needed variables
    ts = time.strftime('%Y-%m-%dT%H:%M:%SZ')
    unixtime = time.time_ns()
    interface_stats = {}
    interface_stats = {'time': ts}
    interface_stats['interfaces'] = []

    # Parse switches from the input array
    for key, value in switch_array.items():
        # Call the login function
        status, auth_cookie = aaa_login(username, password, value['mgmt'])
        if status == requests.codes.ok:
            for port in value['interfaces']:
                # Get input stats for the interface
                url = "https://" + value['mgmt'] + "/api/node/mo/sys/intf/phys-[eth" + port + "]/dbgIfIn.json"
                result_in = nxapi_get(url, auth_cookie)
                
                # Get output stats for the interface
                url = "https://" + value['mgmt'] + "/api/node/mo/sys/intf/phys-[eth" + port + "]/dbgIfOut.json"
                result_out = nxapi_get(url, auth_cookie)
                
                result_in_json = result_in.json()
                result_out_json = result_out.json()
                
                # If output format is JSON, parse the output and append into the output dictionary
                if output_format in "json":
                    interface_stats['interfaces'].append({
                        'switch': value['name'],
                        'interface': "Ethernet" + port,
                        'discards_in': result_in_json["imdata"][0]["rmonIfIn"]["attributes"]["discards"],
                        'discards_out': result_out_json["imdata"][0]["rmonIfOut"]["attributes"]["discards"],
                        'errors_in': result_in_json["imdata"][0]["rmonIfIn"]["attributes"]["errors"],
                        'errors_out': result_out_json["imdata"][0]["rmonIfOut"]["attributes"]["errors"],
                        'multicastPkts_in': result_in_json["imdata"][0]["rmonIfIn"]["attributes"]["multicastPkts"],
                        'multicastPkts_out': result_out_json["imdata"][0]["rmonIfOut"]["attributes"]["multicastPkts"],
                        'broadcastPkts_in': result_in_json["imdata"][0]["rmonIfIn"]["attributes"]["broadcastPkts"],
                        'broadcastPkts_out': result_out_json["imdata"][0]["rmonIfOut"]["attributes"]["broadcastPkts"],
                        'ucastPkts_in': result_in_json["imdata"][0]["rmonIfIn"]["attributes"]["ucastPkts"],
                        'ucastPkts_out': result_out_json["imdata"][0]["rmonIfOut"]["attributes"]["ucastPkts"],
                        'octets_in': result_in_json["imdata"][0]["rmonIfIn"]["attributes"]["octets"],
                        'octets_out': result_out_json["imdata"][0]["rmonIfOut"]["attributes"]["octets"],
                        'octetRate_in': result_in_json["imdata"][0]["rmonIfIn"]["attributes"]["octetRate"],
                        'octetRate_out': result_out_json["imdata"][0]["rmonIfOut"]["attributes"]["octetRate"],
                        'packetRate_in': result_in_json["imdata"][0]["rmonIfIn"]["attributes"]["packetRate"],
                        'packetRate_out': result_out_json["imdata"][0]["rmonIfOut"]["attributes"]["packetRate"]  
                    })
                 # If output format is InfluxDB, parse the output and print out the data in InfluxDB format
                elif output_format in "influxdb":
                    print("nexusinterface,switch=" + value['name'] + ",interface=Ethernet" + port + " discards_in=" + result_in_json["imdata"][0]["rmonIfIn"]["attributes"]["discards"] + " " + str(unixtime))
                    print("nexusinterface,switch=" + value['name'] + ",interface=Ethernet" + port + " discards_out=" + result_out_json["imdata"][0]["rmonIfOut"]["attributes"]["discards"] + " " + str(unixtime))
                    print("nexusinterface,switch=" + value['name'] + ",interface=Ethernet" + port + " errors_in=" + result_in_json["imdata"][0]["rmonIfIn"]["attributes"]["errors"] + " " + str(unixtime))
                    print("nexusinterface,switch=" + value['name'] + ",interface=Ethernet" + port + " errors_out=" + result_out_json["imdata"][0]["rmonIfOut"]["attributes"]["errors"] + " " + str(unixtime))
                    print("nexusinterface,switch=" + value['name'] + ",interface=Ethernet" + port + " multicastPkts_in=" + result_in_json["imdata"][0]["rmonIfIn"]["attributes"]["multicastPkts"] + " " + str(unixtime))
                    print("nexusinterface,switch=" + value['name'] + ",interface=Ethernet" + port + " multicastPkts_out=" + result_out_json["imdata"][0]["rmonIfOut"]["attributes"]["multicastPkts"] + " " + str(unixtime))
                    print("nexusinterface,switch=" + value['name'] + ",interface=Ethernet" + port + " broadcastPkts_in=" + result_in_json["imdata"][0]["rmonIfIn"]["attributes"]["broadcastPkts"] + " " + str(unixtime))
                    print("nexusinterface,switch=" + value['name'] + ",interface=Ethernet" + port + " broadcastPkts_out=" + result_out_json["imdata"][0]["rmonIfOut"]["attributes"]["broadcastPkts"] + " " + str(unixtime))
                    print("nexusinterface,switch=" + value['name'] + ",interface=Ethernet" + port + " ucastPkts_in=" + result_in_json["imdata"][0]["rmonIfIn"]["attributes"]["ucastPkts"] + " " + str(unixtime))
                    print("nexusinterface,switch=" + value['name'] + ",interface=Ethernet" + port + " ucastPkts_out=" + result_out_json["imdata"][0]["rmonIfOut"]["attributes"]["ucastPkts"] + " " + str(unixtime))
                    print("nexusinterface,switch=" + value['name'] + ",interface=Ethernet" + port + " octets_in=" + result_in_json["imdata"][0]["rmonIfIn"]["attributes"]["octets"] + " " + str(unixtime))
                    print("nexusinterface,switch=" + value['name'] + ",interface=Ethernet" + port + " octets_out=" + result_out_json["imdata"][0]["rmonIfOut"]["attributes"]["octets"] + " " + str(unixtime))
                    print("nexusinterface,switch=" + value['name'] + ",interface=Ethernet" + port + " octetRate_in=" + result_in_json["imdata"][0]["rmonIfIn"]["attributes"]["octetRate"] + " " + str(unixtime))
                    print("nexusinterface,switch=" + value['name'] + ",interface=Ethernet" + port + " octetRate_out=" + result_out_json["imdata"][0]["rmonIfOut"]["attributes"]["octetRate"] + " " + str(unixtime))
                    print("nexusinterface,switch=" + value['name'] + ",interface=Ethernet" + port + " packetRate_in=" + result_in_json["imdata"][0]["rmonIfIn"]["attributes"]["packetRate"] + " " + str(unixtime))
                    print("nexusinterface,switch=" + value['name'] + ",interface=Ethernet" + port + " packetRate_out=" + result_out_json["imdata"][0]["rmonIfOut"]["attributes"]["packetRate"] + " " + str(unixtime))

            # Log out after getting the statistics
            aaa_logout(username, value['mgmt'], auth_cookie)

    # Print out the data in JSON format if requested in the arguments
    if output_format in "json":
        print(json.dumps(interface_stats, indent=2))