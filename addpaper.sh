#!/bin/bash
DATA=./data

if [ -f "$1" ]
then

MAXFILEID=0
for item in $DATA/*.txt
do
if [ $(basename "$item" ".txt") -gt "$MAXFILEID" ]
then 
MAXFILEID=$(basename "$item" ".txt")
fi
done
MAXFILEID=$((MAXFILEID+1))

cp $1 $DATA/$MAXFILEID.pdf
pdftotext $1 $DATA/$MAXFILEID.txt

if [ -f "$2" ]
then 
cp $2 $DATA/$MAXFILEID.bib
else
touch $DATA/$MAXFILEID.bib
vim $DATA/$MAXFILEID.bib
fi

else
echo "Usage: $0 <PDF> [<BIBTEX>]"
fi
