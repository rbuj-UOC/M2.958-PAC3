#!/usr/bin/env bash

# Script que copia els fitxers necessaris per realitzar l'entrega de l'activitat

TARGET_DIR=~/Activitat\ CLOUD\ 2025_2
cp activitat_cloud_aws_CAT.ipynb "$TARGET_DIR"/
for dir in img source; do
	mkdir -p "$TARGET_DIR"/"$dir"
	cp -r "$dir"/* "$TARGET_DIR"/"$dir"/
done
