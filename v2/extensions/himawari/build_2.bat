@echo off
call conda remove -y -n for_dist_himawari --all
call conda create -y -n for_dist_himawari python=3.11
call conda activate for_dist_himawari
call pip install -r requirements.txt
call pyinstaller -F -c --copy-metadata aioftp -p . -p D:\03\python\04\PyQt-Fluent-Widgets\v2 main.py
call conda env export -f environment.yml
pause
