#
#
# This script reads the publishers from a Netskope tenant and saves them to a file. 
# Mostly used to get the Publisher ID number for use in creating new private apps
#
# It uses the Netskope v2 API endpoint and needs Read access:
# '/api/v2/infrastructure/publishers'
#
#  This was written for Netskope release 101 originally, uses python 3.10 and pandas 2.0.1
#
# Requires the following arguments in order:
# 	Full tenant hostname, API token, json filename
# Example:    python3 tron-get-publishers hostname.goskope.com a458ef832xs389 jsonfile')
#        


import sys
import requests
import json
import pandas as pd



def pullpublisherjson(tenant, APItoken, jsonfile):

# API Endpoint URL for getting publishers
    API_URL = '/api/v2/infrastructure/publishers'

# Format the three arguments
    apiurlrequest = 'http://' + sys.argv[1] + API_URL
    netskopeapitoken = { 'Netskope-Api-Token': sys.argv[2] }

# Get the JSON from the tenant via Netskope API
    webresponse = requests.get(apiurlrequest, headers=netskopeapitoken)

# Load into a JSON object
    publisherlist = json.loads(webresponse.text)

# Save it to a file
    with open(str(jsonfile), 'w') as f:
        json.dump(publisherlist, f, indent=4,)


def createpublisherlist(publisherjsonfile):

    with open(publisherjsonfile, 'r') as f:
        data = json.load(f)

    # load the publishers into a list
    publishers = data['data']['publishers']

    # create an array for the publishers
    publisherlist = []

    # loop through each publisher in the publishers list
    for pub in publishers: 
        # assigne what we need for the json file
        publisher_id = pub['publisher_id']
        publisher_name = pub['publisher_name']
        common_name = pub['common_name']
        ip_address = pub['assessment']['ip_address']

        # Append the elements into the publisherlist array
        publisherlist.append({'publisher_id': publisher_id, 'publisher_name': publisher_name, 'common_name': common_name, 'ip_address': ip_address})
    
    # write to json file and print it too
    with open('jsonoutput.json', 'w') as output_file:
	    json.dump(publisherlist, output_file, indent=4)
    return(publisherlist)

  
###############################     End of functions

# check for correct arguments
if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print('Full tenant hostname, API token, and json filename required.  In order \n')
        print('Example:    python3 tron-get-publishers hostname.goskope.com a458ef832xs389 jsonfile')
        exit()


if len(sys.argv) < 3:
    print('Error: This program requires 2 arguments: Full tenant hostname and API token required')
    print('Example:    python3 tron-get-publishers hostname.goskope.com a458ef832xs389 myoutputjson')
    exit()

arg1=sys.argv[1]
arg2=sys.argv[2]
arg3=sys.argv[3]

if len([arg1, arg2, arg3]) < 3:
        raise Exception("This function requires 3 arguments")

tenant = str(arg1)
APItoken = str(arg2)

publisherjsonfile = str(arg3)

pullpublisherjson(tenant, APItoken, publisherjsonfile)
publisherlist=createpublisherlist(publisherjsonfile)
print(publisherlist)

