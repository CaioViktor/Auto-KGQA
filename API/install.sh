#!/bin/bash
echo "Installing dependecies..."
pip install -r requirements.txt
echo "Installing spacy en_core_web_md mode..." 
python -m spacy download en_core_web_md
echo "Installing punkt from nltk..."
python -m nltk.downloader punkt
echo "It will create the indexes files, this process can be executed later by running: python create_indexes.py"
echo "Remember to have the triplestore with the desired KG running and to have configured the 'configs.py' file"
echo "Creating indexes..."
python create_indexes.py
echo "Installation completed successfully!"