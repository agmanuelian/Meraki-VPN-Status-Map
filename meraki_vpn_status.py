# import gmplot package 
import gmplot 
import requests
import json

def get_coordinates(serial):
    device = requests.get(url= f"https://api.meraki.com/api/v1/devices/{serial}", headers=headers).json()
    if "lat" in device.keys():
        lat = device["lat"]
        long = device["lng"]
        return lat, long
    else:
        return 0, 0

org_id = "YOUR_ORG_ID" 
api_key = "YOUR_MERAKI_API_KEY"
google_api_key= "YOUR_GOOGLE_API_KEY"
base_url = "https://api.meraki.com/api/v1"
vpn_status = f"/organizations/{org_id}/appliance/vpn/statuses"

headers = {
    'X-Cisco-Meraki-API-Key' : api_key
} 

gmap1 = gmplot.GoogleMapPlotter(-34.59682, 
                                -58.37111, 
                                15, apikey= google_api_key) 

#### GET VPN STATUS ####

vpn_req = requests.get(url= f"{base_url}{vpn_status}", headers=headers).json()

# Map serial number to device
serial_dict = {}

for device in vpn_req:
    serial_dict[device["networkId"]] = device["deviceSerial"] 

# Map coordinates to device
device_coordinates = {} 
for device, serial in serial_dict.items():
    print(f"Device: {device}, Serial: {serial}")
    lat, long = get_coordinates(serial)
    while [lat, long] in device_coordinates.values():
        lat += 0.001
    device_coordinates[device] = [lat, long]
print(device_coordinates)

#Put tags into the map whether the devices are offline or online
for network in vpn_req:
    if network["deviceStatus"] == "online":
        gmap1.scatter([device_coordinates[network["networkId"]][0]], [device_coordinates[network["networkId"]][1]], '#00FF00', size=50)
        gmap1.text(device_coordinates[network["networkId"]][0], device_coordinates[network["networkId"]][1], network["networkName"], color = "lime")
    elif network["deviceStatus"] == "alerting":
        gmap1.scatter([device_coordinates[network["networkId"]][0]], [device_coordinates[network["networkId"]][1]], '#FFA500', size=50)
        gmap1.text(device_coordinates[network["networkId"]][0], device_coordinates[network["networkId"]][1], network["networkName"], color = "orange")        
    else:
        gmap1.scatter([device_coordinates[network["networkId"]][0]], [device_coordinates[network["networkId"]][1]], '#FF0000', size=50)
        gmap1.text(device_coordinates[network["networkId"]][0], device_coordinates[network["networkId"]][1], network["networkName"], color = "red")

# Draw lines between connected devices
for network in vpn_req:
    for peer in network["merakiVpnPeers"]:
        if peer["reachability"] == "reachable":
            gmap1.plot([device_coordinates[network["networkId"]][0],device_coordinates[peer["networkId"]][0]], [device_coordinates[network["networkId"]][1],device_coordinates[peer["networkId"]][1]], '#00FF00', edge_width=2.5)
        else:
            gmap1.plot([device_coordinates[network["networkId"]][0],device_coordinates[peer["networkId"]][0]], [device_coordinates[network["networkId"]][1],device_coordinates[peer["networkId"]][1]], '#FF0000', edge_width=2.5)
# print(json.dumps(vpn_req, indent=2))

gmap1.draw("test_meraki_vpn.html" ) 