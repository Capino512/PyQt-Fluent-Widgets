

import subprocess

from PySide6.QtCore import QThread, Signal


class Thread(QThread):
    on_finished = Signal(bool)
    on_progress = Signal(int)
    on_message = Signal(str)

    def __init__(self, cmd, cwd=None, parent=None):
        super(Thread, self).__init__(parent)
        self.cmd = cmd
        self.cwd = cwd
        self.process = None
        self.cancel = None

    def force_stop(self):
        self.process.kill()
        self.cancel = True

    def run(self):
        self.cancel = False
        process = subprocess.Popen(self.cmd, cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        self.process = process
        while (code := process.poll()) is None:
            try:
                line = process.stdout.readline().strip()
            except:
                continue
            if line:
                self.on_message.emit(line)
                print(line)
                if line.startswith('[Progress]'):
                    self.on_progress.emit(float(line.removeprefix('[Progress]').strip()))
                for s in ['[Info]', '[Warning]', '[Error]']:
                    if line.startswith(s):
                        self.on_message.emit(line.removeprefix(s).strip())
        success = code == 0 and not self.cancel
        print(success)
        self.on_finished.emit(success)
