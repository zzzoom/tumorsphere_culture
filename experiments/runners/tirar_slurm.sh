#!/bin/bash

### Configuración del trabajo

### Nombre de la tarea
#SBATCH --job-name=tumoresfera

### Cola a usar (gpu, mono, multi)
####SBATCH --partition=multi

### Cantidad de nodos a usar
####SBATCH --nodes=1

### Cores a utilizar por nodo = procesos por nodo * cores por proceso
####SBATCH --ntasks-per-node=64
### Cores por proceso (para MPI+OpenMP)
####SBATCH --cpus-per-task=1

### Tiempo de ejecucion. Formato dias-horas:minutos.
### short:  <= 1 hora
### multi:  <= 2 días
#SBATCH --time 15-0:00

#---------------------------------------------------

# Script que se ejecuta al arrancar el trabajo

# Cargar el entorno del usuario incluyendo la funcionalidad de modules
# No tocar
. /etc/profile


# Lanzar el programa

for realiz in {1..10}
do

for rs in  0.65 0.66 0.67 0.68 0.69 0.71 0.70 0.72 0.73 0.74 0.75
do 

nombre=S-$realiz-$rs

 sed  's/val_ps/'$rs'/g' < template_python_script.py \
|sed  's/val_realiz/'$realiz'/g'> $nombre.py


sed  's/val_nombre/'$nombre'/g' <simple.sh > .$nombre.sh


#cp .hecho.sh ~/scratch/.$nombre.$proc.sh
#cd ~/scratch/
chmod +x .$nombre.sh
chmod +x $nombre.py

qsub ./.$nombre.sh 


#unad

sleep 1
done
done


#rm .${nombre}.py
