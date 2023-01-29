#!/bin/bash

cd ~/experiment

echo "Please enter RIN: "
read rin

echo "Please enter SID: "
read sid

while true; do
    read -p "Is the eyetracker initialized? (y/n): " yn
    case $yn in
        [Yy]* ) python meta-t.py -e $IVIEWX_IP -rin $rin -id $sid -c training_D1; break;;
        [Nn]* ) python meta-t.py -rin $rin -id $sid -c training_D1; break;;
        * ) echo "Please answer y or n.";;
    esac
done

echo "Press ENTER to exit."

read junk