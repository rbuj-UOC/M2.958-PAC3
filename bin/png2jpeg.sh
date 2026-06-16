#!/usr/bin/env bash

# Script que converteix els fitxers d'imatges png de la carpeta actual i
# subcarpetes a jpeg amb imagemagick.

find . -type f -name "*.png" | while read file; do
	jpeg_file="${file%.png}.jpeg"
	echo "Converting $file to $jpeg_file..."
	convert "$file" -background white -alpha remove -alpha off -quality 85 "$jpeg_file"
done

# Eliminar els fitxers png originals després de la conversió
# find . -name *.png -exec rm {} \;

# Substituir el text ".png" per ".jpeg" alf fitxer activitat_cloud_aws_CAT.ipynb
# sed -i 's/\.png/\.jpeg/g' activitat_cloud_aws_CAT.ipynb

# Substituir el text ".png" per ".jpeg" alf fitxer activitat_cloud_aws_CAT.ipynb (per a MacOS)
# sed -i '' 's/\.png/\.jpeg/g' activitat_cloud_aws_CAT.ipynb
