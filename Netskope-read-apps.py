import sys
import logging
import requests
import json
import pandas as pd
import argparse


# netskope-read-apps is script/functions that pulls the private apps via API, then pulls the publisher names and formats
# them into an excel spreadsheet format.
#
# 
# It currently uses two Netskope API v2 endpoints and needs Read access:
# '/api/v2/infrastructure/publishers'
# '/api/v2/steering/apps/private'
#
# It requires these arguments in order:  tenant name, private app API key, Publisher API key, destination Json filename, destination excel filename
# excel file must end in .xlsx
#
#  If you don't specify arguments in will prompt for them.
#
#  You can specify a filename with arguments by using the argument '@filename.txt'
#  This file should contain the argument value in order (above) on seperate lines.
#
# It also requires pandas which sometimes is not installed (sudo pip install pandas)
# Also requires openpyxl (sudo pip install openpyxl)
#
# This was written for Netskope release 101 originally, python 3.10 and pandas 2.0.1
#
#
#
####################################################################################
# function to pull the list of publishers, write to a file for debug, and return it in a list.

def pullpublisherjson(tenant, APItokenforpublisher, jsonfile):
""" Requests the publishers from the tenant via API and writes to a JSON file for use later.
	tenant - tenant FQDN
 	APItokenforpublisher - the API token for the tenant only read-only is needed
  	jsonfile - a name for the JSON file"""

    print('\n Starting function pullpublisherjson')

# API Endpoint URL for getting publishers
    API_URL_FOR_PUBLISHER = '/api/v2/infrastructure/publishers'

# Format the three arguments
    apiurlrequest = 'https://' + tenant + API_URL_FOR_PUBLISHER
    netskopeapitoken = { 'Netskope-Api-Token': APItokenforpublisher }

    print('\n API request is: '+ apiurlrequest)



# Get the JSON from the tenant via Netskope API
    webresponse = requests.get(apiurlrequest, headers=netskopeapitoken)
    print('\n HTTP response is:' + str(webresponse))

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

    print('\n Got publisher list....looping through list:\n')

    for pub in publishers: 
        publisher_id = pub['publisher_id']
        publisher_name = pub['publisher_name']
        common_name = pub['common_name']
        ip_address = pub['assessment']['ip_address']
        print('\n', publisher_id, publisher_name, common_name, ip_address)
        publisherlist.append({'publisher_id': publisher_id, 'publisher_name': publisher_name, 'common_name': common_name, 'ip_address': ip_address})

# write the list to a json file

    print('\n Writing list to temp file publisher-jsonoutput.json....')

    with open('publisher-jsonoutput.json', 'w') as output_file:
	    json.dump(publisherlist, output_file, indent=4)

    print('Done')

# return the list to whatever called us.
    return publisherlist





def createprivateappidlist(jsonfile, excelfile, publisherlist): 
"""	This function reads a json file of private apps (created in another function below), 
	pulls out some of the attributes into a list and creates a spreadsheet with them.

	jsonfile - the JSON file created with the list of privater apps
	excel file - the name of the excel spreadsheet file to create
	publisherlist - a list of the publishers from the pullpublisherjson function"""
 
    print('\n Running function createprivateappidlist...\n')

    with open(jsonfile, 'r') as f:
        data = json.load(f)

        private_apps = data['data']['private_apps']
#        print(f"Number of objects in private_apps: {len(private_apps)}")
    print('\n Read private app list from file: ' + str(jsonfile))
    privateapplist = []

# loop through the private apps 
    
    print('\n Looping through JSON file....\n')
    
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

    print('\n Finished adding private apps: \n')
    print(str(privateapplist))

#    length = len(privateapplist)
#    print('Length of list:'+str(length))
#    print(privateapplist)


#   output to an excel file
    df = pd.DataFrame(privateapplist, columns=['app_id', 'app_name', 'host', 'use_publisher_dns', 'port/protocol', 'publisher_name/publisher_id'])
    df.to_excel(excelfile, index=False)
    print('\n Finished writing to execl file: ' +str(excelfile))



#######################################################################
#
# This function pulls the private apps via API and writes to a json file.

def pullprivateappjson(tenant, APItokenforprivateapps, jsonfile):

    print('\n Running function pullprivateappjson')

#   API Endpoint URL for getting private apps

    API_URL_PRIVATE_APPS = '/api/v2/steering/apps/private'

# Check for correct arguments and deliver help message

#. Need to add argument assignment code


#   Format the three arguments
    appurlrequest = 'http://' + tenant + API_URL_PRIVATE_APPS
    netskopeapitoken = { 'Netskope-Api-Token': APItokenforprivateapps }
    outputfile = jsonfile

# Get the JSON from the tenant via Netskope API

    print('\n Sending API request for privaate apps....')

    webresponse = requests.get(appurlrequest, headers=netskopeapitoken)

    print('\n Got response: ' + str(webresponse))

# Load into a JSON object
    privateapplist = json.loads(webresponse.text)

    print('\n Private apps are: \n')
    print(str(privateapplist))

#  print it for debug
#print(appconfig)


# Save it to a file
    print(']\n Saving it to file: ' + str(outputfile))

    with open(str(outputfile), 'w') as f:
        json.dump(privateapplist, f, indent=4,)

##########################################################################
#
# main function
# def Netskope-read-apps(tenant, APItokenforprivateapps, APItokenforpublisher, appfilejson, appfilexlsx):
#
#  Someday I'll use argparse module (haha)
#
####### Check for correct arguments and deliver help message
# 


def get_parameters_via_input():

    print('\n Running function get_parameters_via_input')

    print('\n Asking for parameters: \n')

    tenant = input("Enter tenant URL: ")
    APItokenforprivateapps = input("Enter API key for reading private apps: ")
    APItokenforpublisher = input("Enter API key for reading publishers : ")
    jsonfile = input("Enter a name for the temporary JSON file: ")
    excelfile = input("Enter a name for the Excel file: ")
    return(tenant, APItokenforprivateapps, APItokenforpublisher, jsonfile, excelfile)


def main():

    tenant = ""
    APItokenforprivateapps = ""
    APItokenforpublisher = ""
    jsonfile = ""
    excelfile = ""

    if not len(sys.argv) > 1:
        get_parameters_via_input()
    else:
        print('\n Using argparse function to process arguments/parameters \n')
        parser = argparse.ArgumentParser(fromfile_prefix_chars="@", description="Reads private apps and saves to Excel file") 
        parser.add_argument("tenant", help="URL for the tenant")
        parser.add_argument("APItokenforprivateapps", help="API key for reading Netskope private apps")
        parser.add_argument("APItokenforpublisher", help="API key for reading Netskope publishers" )
        parser.add_argument("jsonfile", help="name of temporary JSON file" )
        parser.add_argument("excelfile", help="name of Excel file" )
        args = parser.parse_args()
        
# This can probably be more efficient with a seperate function and dictionary....change later

        tenant = args.tenant
        APItokenforprivateapps = args.APItokenforprivateapps
        APItokenforpublisher = args.APItokenforpublisher
        jsonfile = args.jsonfile
        excelfile = args.excelfile

    print('\n Got the following arguments: \n')   
    print(tenant, APItokenforprivateapps, APItokenforpublisher, jsonfile, excelfile)    
    publisherjsonfile = 'testfile-publisher-api.json'

# pull publisher list
    listofpublishers = pullpublisherjson(tenant, APItokenforpublisher, publisherjsonfile)

# pull private app via API
    pullprivateappjson(tenant, APItokenforprivateapps, jsonfile)

# create private app list with publishers and write to excel file.
    createprivateappidlist(jsonfile, excelfile, listofpublishers)


    print('###################################\nFinished....main()\n')

if __name__ == "__main__":
    main()
    
   
