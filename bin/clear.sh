#!/usr/bin/env bash

# Script que neteja el metadades d'un fitxer Jupyter Notebook especificat per
# l'usuari. També es pot utilitzar per eliminar les sortides de cèl·les i
# restablir l'estat del fitxer a un estat net.

# Comprova els arguments amb getopts "-f FILE_PATH", -h mostra ajuda
while getopts "f:h" opt; do
	case $opt in
	f) FILE_PATH="$OPTARG" ;;
	h) echo "Usage: $0 -f FILE_PATH" && exit 0 ;;
	*)
		echo "Usage: $0 -f FILE_PATH"
		exit 1
		;;
	esac
done

# Comprova si s'ha proporcionat el camí del fitxer
if [ -z "$FILE_PATH" ]; then
	echo "Error: No s'ha proporcionat cap camí de fitxer."
	echo "Usage: $0 -f FILE_PATH"
	exit 1
fi

jupyter nbconvert \
	--ClearMetadataPreprocessor.enabled=True \
	--ClearOutputPreprocessor.enabled=True \
	--to notebook --inplace "$FILE_PATH"
