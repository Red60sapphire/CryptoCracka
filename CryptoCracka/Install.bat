@echo off
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install --target=%~dp0\libs -r requirements.txt
echo Dependencies installed in the 'libs' folder.
pause