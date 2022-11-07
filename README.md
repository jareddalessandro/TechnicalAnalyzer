# Technical Analyzer
### This application monitors intraday technicals for a specified ticker and gives buy/sell recommendations.  
---
## Running
1. Use Command Prompt to navigate to the parent directory, then run 'python main.py'
--------
## Prerequisites
### Python, tested with both Python 3.7 and python 3.8. Use pip to install required libraries.
* pip install -r requirements.txt 
### Install TA-LIB
#### You can try to place the precompiled x86 ta-lib folder included in this project and at C:\ to skip steps 1-4.
1. Download ta-lib-0.4.0-msvc.zip from https://sourceforge.net/projects/ta-lib/
2. unzip to C:\ 
3. Open x86 Native Tools Command Prompt for VS (If using Python x64 use x64 Native Tools) (This requires Visual Studio Builder Tools)
4. Navigate to C:\ta-lib\c\make\cdr\win32\msvc and run nmake
5. pip install ta-lib
6. If errors are encountered visit https://github.com/mrjbq7/ta-lib for instructions
### Obtain a free API key from Finnhub (https://finnhub.io/)
### Open config.properties and fill out the properties with your API key, the time your market opens (for VWAP calculations), and the ticker you would like to monitor
------------------------
