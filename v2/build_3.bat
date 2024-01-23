@echo off
call conda env create --force -n for_dist -f environment.yml
call conda activate for_dist
call pyinstaller -F -w -p . -i .\asserts\logo.png main.py
pause
