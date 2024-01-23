@echo off
call conda env create --force -n for_dist_himawari -f environment.yml
call conda activate for_dist_himawari
call pyinstaller -F -c --copy-metadata aioftp -p . -p D:\03\python\04\PyQt-Fluent-Widgets\v2 main.py
pause
