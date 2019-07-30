#!/bin/bash

inFile=$1
outFolder=$2

CABECERA_DICOM=$(gdcmdump $inFile)
MODALIDAD=$(echo "$CABECERA_DICOM" | grep '0008,0060')

if [[ "$MODALIDAD" = *"[SR]"* ]]; then
    echo "SR found. Copying to $outFolder"
    cp $inFile $outFolder 
fi

