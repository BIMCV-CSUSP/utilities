#!/usr/bin/env python3

import os
import sys
import datetime
import csv
import json
import re
import requests
import getpass
import base64
import hashlib
import re

folder_base = sys.argv[1]
sr_folder = sys.argv[2]
xnat_url = sys.argv[3]
dep_files = os.listdir(folder_base)
accesion = {}
for d in dep_files:
    max_date = datetime.date.min
    csv_file = None
    for data_file in os.listdir(os.path.join(folder_base,d)):
        match = re.match(r"data_ids_(\d\d)-(\d\d)-(\d{4}).*\.tsv",data_file)
        if not match: continue
        date = datetime.date(int(match.group(3)), int(match.group(2)), int(match.group(1)))
        if date > max_date:
            csv_file = match.group(0)
            max_date = date
    if not csv_file: continue
    with open(os.path.join(folder_base,d,csv_file), encoding="latin-1") as csv_file:
        reader = csv.DictReader(csv_file,delimiter="\t")
        for row in reader:
            if(row[" Access Number "] != ""):
                accesion[row[" Access Number "]] = {"sess":row[" MR ID XNAT "], "subject":row[" Subject anonymized "], "dep":d}

s = requests.Session()
username = input("username: ")
password = getpass.getpass(prompt = "Password: ")
s.auth = (username,password)

regex = ( r""
       + r"(^\s*[Pp][Aa][Cc][Ii][Ee][Nn][Tt][Ee]\s*:?\s*.*$)|" #Paciente: nombre
       + r"(^\s*[Hh]\.?[Cc]\.?\s*:?\s*.*$)|" #H.C.:
       + r"(^\s*[Ee][Pp][Ii][Ss][Oo][Dd][Ii][Oo]\s*:?\s*.*$)|" #episodio:
       + r"(^\s*[Pp][Rr][Ee][Ss][Cc][Rr][Ii][Pp][Cc][Ii][OoÓó][Nn]\s*:?\s*.*$)|" #Prescripcion
       + r"(^\s*[Hh][Aa][Bb][Ii][Tt][Aa][Cc][Ii][OoÓó][Nn]\s*:?\s*.*$)|" #Habitacion
       + r"(^\s*[Ff][Dd][Oo]\.?\s*:?\s*.*$)|" #Fdo.
       + r"(^\s*(([Mm][EeéÉ][Dd][Ii][Cc][Oo]\s*[Rr][Aa][Dd][Ii][OoóÓ][Ll][Oo][Gg][Oo]\s*\.?\s*)|"
          + r"([[Cc]([Oo][Ll][Ee][Gg][Ii][Aa])?[Dd][Oo]\.?\s*[Nn]º?\.?\s*:?\s*.*)){1,}$)|" #Colegiado Nº
       + r"")



expression = re.compile(regex, flags = re.MULTILINE)

sr_files = os.listdir(sr_folder)
for i,sr_file in enumerate(sr_files):
    print("Oppening file",i,"of",len(sr_files),sr_file)
    with open(os.path.join(sr_folder,sr_file), encoding='utf-8' if "UTF8" in sr_file else 'latin-1') as json_file:
        data = json.load(json_file)
    for d in data.values():
        for sr in d:
            
            sr_accesions = [sr["num_examen_1"],sr["num_examen_2"],sr["num_examen_3"]]
            xnat_id = [accesion[sr_accesion] for sr_accesion in sr_accesions if sr_accesion in accesion]

            hasher = hashlib.sha1(sr["info_key"].encode())
            sr_id = hasher.hexdigest()[:10]
            
            if xnat_id:
                print("Found sr for seccions:",xnat_id)
                #with open("/tmp/sr_for_sesions_xyz","w") as output_file:
                #    if "info_valoracion" in sr:
                #        output_file.write(sr["info_valoracion"])
                if "info_valoracion" in sr and sr["info_valoracion"] != "":
                    resource_label = "sr"
                    for sess in xnat_id:
                        success=False
                        while(not success):
                            try:
                                s.put(xnat_url
                                      + xnat_id[0]["dep"]
                                      + "/subjects/"
                                      + xnat_id[0]["subject"]
                                      + "/experiments/"
                                      + sess["sess"]
                                      + "/resources/"
                                      + resource_label)
                                success = True
                            except requests.exceptions.ConnectionError as e:
                                pass
        
                        resource_filename = "sr_"
                        resource_filename += sr_id
                        resource_filename += "_for_"
                        resource_filename += "_and_".join([str(id_["sess"]) for id_ in xnat_id])
                        resource_filename += ".txt"
    
                        print(resource_filename)
    
                        success=False
                        while(not success):
                            try:
                                s.put(xnat_url
                                      + xnat_id[0]["dep"]
                                      + "/subjects/"
                                      + xnat_id[0]["subject"]
                                      + "/experiments/"
                                      + sess["sess"]
                                      + "/resources/"
                                      + resource_label
                                      + "/files/"
                                      + resource_filename
                                      + "?inbody=true&overwrite=true" , data=expression.sub("",sr["info_valoracion"]))
                                success = True
                                print(sr["info_valoracion"])
                            except requests.exceptions.ConnectionError as e:
                                pass
    

#                       if r.status_code != 200:
#                            print(r.text)
#                            raise Exception('Recieved non 200 response while sending response to CFN.')
 
