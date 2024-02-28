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
# Example:    python3 netskope-get-publishers hostname.goskope.com a458ef832xs389 jsonfile')
#       If arguments are not specified it will prompt the user
#       Also, by specifying the @ symbol followed by a filename, you can load the arguments from a file
#       with each argument in order on a single line


import sys
import requests
import json
import pandas as pd
import argparse



def pullpublisherjson(tenant, APItoken, jsonfile):

    print('\n Running function pullpublisherjson....')

# API Endpoint URL for getting publishers
    API_URL = '/api/v2/infrastructure/publishers'

# Format the three arguments
    apiurlrequest = 'http://' + tenant + API_URL
    netskopeapitoken = { 'Netskope-Api-Token': APItoken }

    print('\n Requesting data via API: ' + apiurlrequest)

# Get the JSON from the tenant via Netskope API
    webresponse = requests.get(apiurlrequest, headers=netskopeapitoken)

    print('\n Got response: ')
    print(str(webresponse))

# Load into a JSON object
    publisherlist = json.loads(webresponse.text)

# Save it to a file
    with open(str(jsonfile), 'w') as f:
        json.dump(publisherlist, f, indent=4,)

    print('\n Save to file:')
    print(str(jsonfile))



def createpublisherlist(publisherjsonfile):

    print('\n Running function createpublisherlist\n')

    with open(publisherjsonfile, 'r') as f:
        data = json.load(f)

    # load the publishers into a list
    publishers = data['data']['publishers']

    # create an array for the publishers
    publisherlist = []

    # loop through each publisher in the publishers list
    print('\n Looping through publishers...')
    for pub in publishers: 
        # assigne what we need for the json file
        publisher_id = pub['publisher_id']
        publisher_name = pub['publisher_name']
        common_name = pub['common_name']
        ip_address = pub['assessment']['ip_address']

        # Append the elements into the publisherlist array
        publisherlist.append({'publisher_id': publisher_id, 'publisher_name': publisher_name, 'common_name': common_name, 'ip_address': ip_address})
    
    # write to json file and print it too
        
    print('\n Writing temp file jsonoutput.json')

    with open('jsonoutput.json', 'w') as output_file:
	    json.dump(publisherlist, output_file, indent=4)

    return publisherlist

def get_parameters_via_input():

    print('\n Running function get_parameters_via_input')

    print('\n Asking for parameters: \n')

    tenant = input("Enter tenant URL: ")
    APItoken = input("Enter API key for reading publishers: ")
    publisherjsonfile = input("Enter a name for the JSON file: ")
        
    return(tenant, APItoken, publisherjsonfile)




   

def main():

    if not len(sys.argv) > 1:
        tenant, APItoken, publisherjsonfile = get_parameters_via_input()
    else:
        print('\n Using argparse function to process arguments/parameters \n')
        parser = argparse.ArgumentParser(fromfile_prefix_chars="@", description="Reads publishers and saves to JSON file") 
        parser.add_argument("tenant", help="URL for the tenant")
        parser.add_argument("APItoken", help="API key for reading Netskope publishers")
        parser.add_argument("publisherjsonfile", help="name of temporary JSON file" )
        args = parser.parse_args()
        tenant = args.tenant
        APItoken = args.APItoken
        publisherjsonfile = args.publisherjsonfile
        

    pullpublisherjson(tenant, APItoken, publisherjsonfile)
    publisherlist=createpublisherlist(publisherjsonfile)
    print(publisherlist)

    print('\n Finished.\n')

if __name__ == "__main__":
    main()