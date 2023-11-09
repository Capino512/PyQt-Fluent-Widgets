import subprocess

cmd = r'.\dist\cwd.exe'
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, cwd=None,
                           universal_newlines=True)

while (code := process.poll()) is None:
    line = process.stdout.readline().strip()
    if line:
        print(line)



