## Prerequisites
### Python, tested with both Python 7 and python 8.
* pip install numpy
* pip install finnhub-python
### Install TA-LIB
#### You can try to place the precompiled x86 ta-lib folder included in this project and at C:\ to skip steps 1-4.
1. Download ta-lib-0.4.0-msvc.zip from https://sourceforge.net/projects/ta-lib/
2. unzip to C:\ 
3. Open x86 Native Tools Command Prompt for VS (If using Python x64 use x64 Native Tools) (This requires Visual Studio Builder Tools)
4. Navigate to C:\ta-lib\c\make\cdr\win32\msvc and run nmake
5. pip install ta-lib

