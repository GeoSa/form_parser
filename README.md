# form_parser

Requirements:
1. python v. 3.8.3
2. pip
3. venv
4. aiohttp v. 3.7.4
5. aiofiles v. 0.6.0
6. beautifulsoup4 v. 4.9.3

Python version: 3.8.3

Install dependencies for windows:
1. cd to script directory
2. python -m venv venv
3. venv\Scripts\activate
4. pip install -r requirements.txt
5. python script1.py
6. python script2.py

Install dependencies for Linux:
1. cd to script directory
2. python -m venv venv
3. source venv/bin/activate
4. pip install -r requirements.txt
5. python script1.py
6. python script2.py


Notice:
1. script1.py will be creating an output file, called results.txt, which includes all tax forms info.
If file exist it will be overwriting.
2. script2.py will be creating a subdirectory, called downloads, wich include all tax forms directories with downloaded
files.
