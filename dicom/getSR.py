#!/usr/bin/env python3

import pydicom
import sys
from shutil import copy2

in_file = sys.argv[1]
out_folder = sys.argv[2]

def copy_if_sr(in_file, out_folder, dry_run=False):
  ds = pydicom.dcmread(in_file, force=True)
  if 'SR' in ds[0x8,0x60].value:
    print("SR found. Copying to {} from {}".format(out_folder, in_file))
    if not dry_run: copy2(in_file,out_folder)
    return True
  return False

#def search_in_folder(in_folder,out_folder, dry_run=False):

copy_if_sr(in_file,out_folder,True)
  
