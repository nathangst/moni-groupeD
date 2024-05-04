#!/bin/bash

# Vérifier si le nombre d'arguments est correct
if [ "$#" -ne 1 ]; then
echo "Usage: $0 <timestamp>"
exit 1
fi

# Stocker le timestamp fourni en argument
timestamp="$1"

# Vérifier si le répertoire /var/log/clients/ existe
if [ ! -d "/var/log/clients/" ]; then
echo "Le répertoire /var/log/clients/ n'existe pas."
exit 1
fi

# Aller dans le répertoire /var/log/clients/
cd /var/log/clients/ || exit 1

# Parcourir tous les fichiers du répertoire
for file in *; do
# Vérifier si le fichier est un fichier ordinaire
if [ -f "$file" ]; then
# Filtrer les lignes contenant le timestamp avec awk
awk -v timestamp="$timestamp" '$0 !~ timestamp' "$file" > "$file.tmp" && mv "$file.tmp" "$file"

fi
done

echo "End"
