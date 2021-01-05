#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# takes UUID and gives server name
# 
# version: 0.0.1a
# Copyright 2019 Dylan Habedank
# License: Apache



import argparse
import requests
from getpass import getpass
import json
import os
import keyring
import sys
from prettytable import PrettyTable, ALL, FRAME, NONE
from urllib.parse import urlparse






REGIONS= ['DFW', 'ORD', 'IAD', 'SYD', 'HKG', 'LON']

def getset_keyring_credentials(username=None, password=None):
    #Method to retrieve credentials from keyring.
    #print (sys.version_info.major)
    username = keyring.get_password("raxcloud", "username")
    if username is None:
        if sys.version_info.major < 3:
            username = raw_input("Enter Rackspace Username: ")
            keyring.set_password("raxcloud", 'username', username)
            print ("Username value saved in keychain as raxcloud username.")
        elif sys.version_info.major >= 3:
            username = input("Enter Rackspace Username: ")
            keyring.set_password("raxcloud", 'username', username)
            print ("Username value saved in keychain as raxcloud username.")
    else:
        print ("Authenticating to Rackspace cloud as %s" % username)
    password = keyring.get_password("raxcloud", "password")
    if password is None:
        password = getpass("Enter Rackspace API key:")
        keyring.set_password("raxcloud", 'password' , password)
        print ("API key value saved in keychain as raxcloud password.")
    return username, password


def wipe_keyring_credentials():
    """Wipe credentials from keyring."""
    try:
        keyring.delete_password('raxcloud', 'username')
        keyring.delete_password('raxcloud', 'password')
    except:
        pass
    return True


# Request to authenticate using password
def get_auth_token(username,password):
    #setting up api call
    url = "https://identity.api.rackspacecloud.com/v2.0/tokens"
    headers = {'Content-type': 'application/json'}
    payload = {'auth':{'passwordCredentials':{'username': username,'password': password}}}
    payload2 = {'auth':{'RAX-KSKEY:apiKeyCredentials':{'username': username,'apiKey': password}}}

    #authenticating against the identity
    try:
        r = requests.post(url, headers=headers, json=payload)
    except requests.ConnectionError as e:
        print("Connection Error: Check your internet!")
        sys.exit()


    if r.status_code != 200:
        r = requests.post(url, headers=headers, json=payload2)
        if r.status_code != 200:
            print ("Error! API responds with %d" % r.status_code)
            print("Rerun the script and you will be prompted to re-enter username/password.")
            wipe_keyring_credentials(username, password)
            sys.exit()
        else:
            print("Authentication was successful!")
    elif r.status_code == 200:
        print("Authentication was successful!")

    #loads json reponse into data as a dictionary.
    data = r.json()
    #assign token and account variables with info from json response.
    auth_token = data["access"]["token"]["id"]
    catalog = r.json()['access']['serviceCatalog']


    return auth_token






def find_endpoints(auth_token, region=None, desired_service=None):
    
    
    desired_endpoints = []
    headers = ({'content-type': 'application/json', 'Accept': 'application/json',
    'X-Auth-Token': auth_token})
    url = ("https://identity.api.rackspacecloud.com/v2.0/tokens/%s/endpoints" % auth_token)
    #region is always uppercase in the service catalog
    
    raw_service_catalog = requests.get(url, headers=headers)
    raw_service_catalog.raise_for_status()
    the_service_catalog = raw_service_catalog.json()
    endpoints = the_service_catalog["endpoints"]

    if region is None:
        region = REGIONS
    else:
        region = region.upper()
        region = region.split(',')


    for r in region:
        for service in endpoints:
            if desired_service == service["name"] and r == service["region"]:
                desired_endpoints.append(service["publicURL"])

    return desired_endpoints


def get_servers(auth_token, cs_endpoints, uuid=None, region=None):
    
    foundsever = False
    table = PrettyTable(["name",
            "uuid", "region", "accessIPv4"])

    headers = ({'content-type': 'application/json', 'Accept': 'application/json',
    'X-Auth-Token': auth_token})


    path = "/servers/detail"
    for ep in cs_endpoints:
        if region is None:
            base = urlparse(ep)
            reg = base.hostname.split('.')[0].upper()
        else:
            reg = region.upper()
        url = ep + path
        r = requests.get(url, headers=headers)
        response = r.json()
        servers = response['servers']

        for server in servers:
            server_name = server
            if uuid is not None:
                if server['id'] == uuid:
                    foundsever = True
                    table.add_row([server['name'], server['id'], reg, server['accessIPv4']])
            else:
                table.add_row([server['name'], server['id'], reg, server['accessIPv4']])

    if uuid is not None and foundsever is False:
        print("Error: Could not find supplied UUID")
    else:
        print(table)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='Get a Rackspace server name with UUID')
    parser.add_argument("-u", "--uuid", help="Rackspace server UUID")
    parser.add_argument("-c", "--configure", dest='config',action="store_true", help='Configure the Rackspace username and api key')
    parser.add_argument("-r", "--region", help="Select specific region e.g. dfw, ord, iad")
    args = parser.parse_args()


    if args.config:
        wipe_keyring_credentials()
        username,password = getset_keyring_credentials()
        exit()


    username,password = getset_keyring_credentials()   
    auth_token = get_auth_token(username, password)
    cs_endpoints = find_endpoints(auth_token, args.region, desired_service="cloudServersOpenStack")
    
    get_servers(auth_token, cs_endpoints, args.uuid, args.region) 
