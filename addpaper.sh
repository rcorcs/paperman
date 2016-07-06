#!/bin/bash
DATA=./data

if [ -f "$1" ]
then

FILECOUNT=0
for item in $DATA/*.txt
do
if [ -f "$item" ]
then 
FILECOUNT=$((FILECOUNT+1))
fi
done

cp $1 $DATA/$FILECOUNT.pdf
pdftotext $1 $DATA/$FILECOUNT.txt

if [ -f "$2" ]
then 
cp $2 $DATA/$FILECOUNT.bib
else
vim $DATA/$FILECOUNT.bib
fi

else
echo "Usage: $0 <PDF> [<BIBTEX>]"
fi
