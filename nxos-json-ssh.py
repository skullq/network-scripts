import json
from netmiko import ConnectHandler as Conn
import time

remote_NXOS = {
    'device_type': 'cisco_ios',
    'ip': '10.66.94.199',
    'username': 'admin',
    'password': 'cisco!123',
    'port': 22
}

connect = Conn(**remote_NXOS)
# json_out1 = json.loads(connect.send_command('show policy-map interface control-plane | json'))

# start = time.time()
# for x in json_out1['TABLE_cmap']['ROW_cmap']:
#     print(x['cmap-key'])
#     for y in x['TABLE_slot']['ROW_slot']:
#         print(f"Slot Num : {y['slot-no-out']} and viloate-avg-rate : {y['violate-avg-rate']}")
#     print("\n")
# print(len(x), len(y))

# end = time.time()
# print("The time of execution of above program is :", (end-start) * 10**3, "ms")
start = time.time()
json_out2 = json.loads(connect.send_command('show interface counters errors non-zero | json-pretty'))
for x in json_out2['TABLE_interface']['ROW_interface']:
    print("\n")
    for y, z in x.items():
        if y == 'interface':
            print(z)
        else:
            print(y + "=" + z)

end = time.time()
ttime = (end - start) * 10**3
print("How long it takes to run this :" + %.1f{ttime} + "ms")