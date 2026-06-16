#!/usr/bin/env bash

# Script que converteix els fitxers d'imatges png de la carpeta actual a avif,
# amb imagemagick.

for file in *.png; do
	if [ -f "$file" ]; then
		avif_file="${file%.png}.avif"
		echo "Converting $file to $avif_file..."
		convert "$file" "$avif_file"
	fi
done
