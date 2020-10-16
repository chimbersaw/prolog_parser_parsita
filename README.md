# Parseca prolog parser
## Preparation:
### Ubuntu
```
sudo apt-get install -y python-pytest
pip install -U parsita
```
### MacOs
```
pip install -U pytest
pip install -U parsita
```
## Usage:
```
python prolog_parser.py input_file
```
## Options
 --atom — parse one atom
 
 --typeexpr — parse only one type (without type name or a dot)
 
 --type — parse one type definition (with keyword 'type' and a dot in the end)
 
 --module — parse only module declaration (the one with the keyword 'module')
 
 --list - parse one list
 
 --relation — parse one relation (with a dot in the end)
 
 --prog — parse while program
## Tests:
```
pytest -v
```
