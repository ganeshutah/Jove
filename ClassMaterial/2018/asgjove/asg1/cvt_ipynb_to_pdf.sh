#!/bin/bash
echo "Type Q<n> for grading a Jove quiz, J<n> for grading a Jove assignment"
echo "Example Q3 for thie third Quiz Jove, J4 for the fourth assignment Jove"
read -p 'Input> ' prefix
echo 'Will convert files of the form ' "${prefix}"_"*".ipynb
#-
for file in "${prefix}"_*.ipynb
do
    jupyter nbconvert --to pdf ${file}
done
