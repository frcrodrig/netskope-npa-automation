import sys
import logging
import requests
import json
import pandas as pd


# netskope-read-apps is script/functions that pulls the private apps via API, then pulls the publisher names and formats
# them into an excel spreadsheet format.
#
# 
# It currently uses two Netskope API v2 endpoints and needs Read access:
# '/api/v2/infrastructure/publishers'
# '/api/v2/steering/apps/private'
#
# It requires 4 arguments in order:  tenant name, private app API key, Publisher API key, destination Json filename, destination excel filename
# excel file must end in .xlsx
#
# It also requires pandas which sometimes is not installed (sudo pip install pandas)
#
# This was written for Netskope release 101 originally, python 3.10 and pandas 2.0.1
#
#
#
####################################################################################
# function to pull the list of publishers, write to a file for debug, and return it in a list.

def pullpublisherjson(tenant, APItokenforpublisher, jsonfile):

# API Endpoint URL for getting publishers
    API_URL_FOR_PUBLISHER = '/api/v2/infrastructure/publishers'

# Format the three arguments
    apiurlrequest = 'http://' + tenant + API_URL_FOR_PUBLISHER
    netskopeapitoken = { 'Netskope-Api-Token': APItokenforpublisher }

# Get the JSON from the tenant via Netskope API
    webresponse = requests.get(apiurlrequest, headers=netskopeapitoken)

# Load into a JSON object
    publisherlist = json.loads(webresponse.text)

# Save it to a file
    with open( str(jsonfile), 'w') as f:
        json.dump(publisherlist, f, indent=4,)

#  open and load the file into a new list

    with open(jsonfile, 'r') as f:
        data = json.load(f)

# start at the correct place in the json file

    publishers= data['data']['publishers']

# create an empty list for publisher data

    publisherlist=[]

# loop through the json file and pull only the items we need into a list

    for pub in publishers: 
        publisher_id = pub['publisher_id']
        publisher_name = pub['publisher_name']
        common_name = pub['common_name']
        ip_address = pub['assessment']['ip_address']
        publisherlist.append({'publisher_id': publisher_id, 'publisher_name': publisher_name, 'common_name': common_name, 'ip_address': ip_address})

# write the list to a json file

    with open('publisher-jsonoutput.json', 'w') as output_file:
	    json.dump(publisherlist, output_file, indent=4)
    
# return the list to whatever called us.

    return(publisherlist)  

######################################################################################
# This function reads the json file of private apps, pulls out some of the attributes into a list and creates a spreadsheet with them.

def createprivateappidlist(jsonfile, excelfile, publisherlist): 
    with open(jsonfile, 'r') as f:
        data = json.load(f)

        private_apps = data['data']['private_apps']
#        print(f"Number of objects in private_apps: {len(private_apps)}")
    
    privateapplist = []

# loop through the private apps 
    for app in private_apps:  
        app_id = app['app_id']
        app_name = app['app_name']
        host = app['host']
        use_publisher_dns = app['use_publisher_dns']
        protocols = app['protocols']
        publishers = app['service_publisher_assignments']

    # ports/protocols are a nested array so create an array to put them in   
        portresult = []    
        
    # loop through the ports/protocols
        
        for protocol in protocols:      
            port = str(protocol['port'])
            transport = protocol['transport']

            #  Combine them into a string and comma delimit them.
            
            portresult.append(f"{port}/{transport}") 
        portresult_str = ','.join(portresult)

    # publishers are in nested array so create an array
        publisherresult = []

    # loop through publishers
        for assignment in publishers:
            publisher_id = str(assignment['publisher_id'])

# don't think service_id is needed
#            service_id = str(assignment['service_id'])


# Find the publisher name in publisherlist using publisher id

            publisher_name = ''
            search_item = publisher_id
            for item in publisherlist:
                if search_item in str(item):
                    publisher_name = str(item['publisher_name'])
            publisherresult.append(f"{publisher_name}/{publisher_id}")

            
                    
            
        publisherresult_str = ','.join(publisherresult)


        #  Add everything to the private app list
        privateapplist.append((app_id, app_name, host, use_publisher_dns, portresult_str, publisherresult_str))   

#    length = len(privateapplist)
#    print('Length of list:'+str(length))
#    print(privateapplist)


#   output to an excel file
    df = pd.DataFrame(privateapplist, columns=['app_id', 'app_name', 'host', 'use_publisher_dns', 'port/protocol', 'publisher_name/publisher_id'])
    df.to_excel(excelfile, index=False)


#######################################################################
#
# This function pulls the private apps via API and writes to a json file.

def pullprivateappjson(tenant, APItokenforprivateapps, jsonfile):

#   API Endpoint URL for getting private apps

    API_URL_PRIVATE_APPS = '/api/v2/steering/apps/private'

# Check for correct arguments and deliver help message

#. Need to add argument assignment code


#   Format the three arguments
    appurlrequest = 'http://' + tenant + API_URL_PRIVATE_APPS
    netskopeapitoken = { 'Netskope-Api-Token': APItokenforprivateapps }
    outputfile = jsonfile

# Get the JSON from the tenant via Netskope API

    webresponse = requests.get(appurlrequest, headers=netskopeapitoken)

# Load into a JSON object
    privateapplist = json.loads(webresponse.text)

#  print it for debug
#print(appconfig)


# Save it to a file
    with open(str(outputfile), 'w') as f:
        json.dump(privateapplist, f, indent=4,)

##########################################################################
#
# main function
# def tronstart(tenant, APItokenforprivateapps, APItokenforpublisher, appfilejson, appfilexlsx):
#
#
# Start here
#
####### Check for correct arguments and deliver help message
# 
if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print('Full tenant hostname, API token, destination JSON filename, destination excel filename required.  In order \n')
        print('Example:    python3 pull-private-apps.py hostname.goskope.com a458ef832xs389 myoutputjson myoutputexcel')
        exit()


if len(sys.argv) < 5:
        print("Error: This program requires 5 arguments: Full tenant hostname, API token for private apps, API token for publishers, and destination filenames required  ")
        print('Example:    python3 pull-private-apps.py hostname.goskope.com a458ef832xs389 b4837a933f myoutputjson myoutputexcel')
        exit()

arg1 = sys.argv[1]
arg2 = sys.argv[2]
arg3 = sys.argv[3]
arg4 = sys.argv[4]
arg5 = sys.argv[5]

if len([arg1, arg2, arg3, arg4, arg5]) < 5:
    raise Exception("This function requires 5 arguments")
    exit()

tenant = str(arg1)
APItokenforprivateapps = str(arg2)
APItokenforpublisher = str(arg3)
jsonfile = str(arg4)
excelfile = str(arg5)
publisherjsonfile = 'testfile-publisher-api.json'

# pull publisher list
listofpublishers = pullpublisherjson(tenant, APItokenforpublisher, publisherjsonfile)

# pull private app via API
pullprivateappjson(tenant, APItokenforprivateapps, jsonfile)

# create private app list with publishers and write to excel file.
createprivateappidlist(jsonfile, excelfile, listofpublishers)


print('###################################\n\n')


    
   
