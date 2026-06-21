#!/usr/bin/env bash

# Script que executa un fitxer Jupyter Notebook i el converteix a HTML. També
# pot generar un fitxer HTML amb les sortides de les cèl·les.

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
	--to html \
	--execute \
	--embed-images \
	"$FILE_PATH"
