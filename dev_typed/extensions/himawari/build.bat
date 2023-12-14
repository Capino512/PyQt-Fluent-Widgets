@echo off
call conda remove -y -n for_dist --all
call conda create -y -n for_dist python=3.11
call conda activate for_dist
call pip install -r requirements.txt
call pyinstaller -F -c -p . -p D:\project\python\01\PyQt-Fluent-Widgets\dev_typed main.py
rem call pyinstaller -F -c -p . -p D:\03\python\04\PyQt-Fluent-Widgets\dev_typed main.py
pause