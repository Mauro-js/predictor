#!/bin/bash

# Cambia al directorio ~/predictor (~/ expande a /home/usuario)
cd ~/predictor

# Ejecuta git pull desde la URL proporcionada
git pull https://github.com/Mauro-js/predictor

# Si deseas que el script muestre un mensaje después de completar el git pull, puedes agregar:
echo "Git pull completado."

# Guarda el archivo y asegúrate de que sea ejecutable con el siguiente comando:
# chmod +x git_pull.sh
