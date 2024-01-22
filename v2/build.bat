@echo off
call conda remove -y -n for_dist --all
call conda create -y -n for_dist python=3.11
call conda activate for_dist
call pip install -r requirements.txt
call pyinstaller -F -w --upx-dir D:\sys\bin\upx-4.2.1-win64 -p . -i .\asserts\logo.png main.py
pause