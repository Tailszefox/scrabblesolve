#!/bin/bash

arrayV=(A E I O U Y)
arrayR=(A B C D E F G H I J K L M N O P Q R S T U V W X Y Z '#')

numV=${#arrayV[*]}
numR=${#arrayR[*]}

len=0
tailleMax=6

> lettresRandom

while [ $len -lt $tailleMax ]
do
  index=$(($RANDOM%$numR))
  lettre="${arrayR[$index]}"
  echo $lettre >> lettresRandom
  ((len++))
done

index=$(($RANDOM%$numV))
lettre="${arrayV[$index]}"
echo $lettre >> lettresRandom

cat lettresRandom
./scrabblesolv.py -print -points -update grille1 lettresRandom

