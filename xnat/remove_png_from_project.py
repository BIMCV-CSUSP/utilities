#!/usr/bin/env python3

import json
import requests
import getpass
import sys

url_base = sys.argv[1]
proj = sys.argv[2]
user = input("username: ")
password = getpass.getpass("Password: ")

interface = requests.Session()
if (user is not None) or (password is not None):
    interface.auth = (user, password)


resources = interface.get( url_base+"/data/archive/projects/"+proj+"/resources/zip/files?type=json").json()
files = resources["ResultSet"]["Result"]
print(len(files))
#print(type(files))
files_filtered = [f["URI"] for f in files if ".png" in f["Name"].lower()]
print(len(files_filtered))
#print(files_filtered)
for i,uri in enumerate(files_filtered):
    interface.delete(url_base+uri)
    print(i/len(files_filtered),str(i)+"/"+str(len(files_filtered)))
