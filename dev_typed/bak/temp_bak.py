import os
import sys
import subprocess

from PySide6.QtWidgets import QApplication, QWidget, QFormLayout, QGroupBox, QVBoxLayout, QLineEdit
from PySide6.QtCore import Qt, QThread, Signal
import qfluentwidgets
from qfluentwidgets import LineEdit, BodyLabel, ComboBox, CheckBox, PrimaryPushButton
from qframelesswindow import FramelessMainWindow
from typed_var import *


# module/config.py
# module/config.ini
# module/module.ini
# module/main.py

def parse(path, mode):
    config = Config()
    config.add_section('xxx')
    config.add_option('xxx', 'aaa', Var(Int, 10, 'desc'))
    config.add_option('xxx', 'bbb', Var(Float, 1.5, 'desc'))
    config.add_option('xxx', 'ccc', Var(Bool, desc='desc'))
    config.add_option('xxx', 'DDD', Var(String, 'abc', 'desc'))
    config.add_option('xxx', 'eee', ArrayVar(Int, 5, [1] * 5, 'desc'))
    config.add_option('xxx', 'fff', ListVar([Int, Float, Bool, String], [1, 1.2, True, 'aaa'], 'desc'))
    config.add_option('xxx', 'ggg', ComboVar(String, ['a', 'b', 'c'], 'a', 'desc'))
    config.add_option('xxx', 'hhh', ComboVar(Int, [1, 2, 3], 1, 'desc'))
    config.add_option('xxx', 'iii', ComboVar(Bool, [True, False], True, 'desc'))
    config.add_section('yyy')
    config.add_option('yyy', 'aaa', Var(Int, desc='desc'))
    config.add_option('yyy', 'bbb', Var(Float, desc='desc'))
    config.add_option('yyy', 'ccc', Var(Bool, desc='desc'))
    config.add_option('yyy', 'ddd', Var(String, desc='desc'))
    if mode == 'w':
        config.to_ini(path)
    else:
        config.from_ini(path)
    return config


# def parse(path, mode):
#     config = Config()
#     config.add_section('file')
#     config.add_option('file', 'input', Var(String, 'input.txt', desc='输入文件（为空时默认为input.txt）'))
#     config.add_option('file', 'output', Var(String, desc='输出文件（为空时默认根据当地时间命名为%Y-%d-%m_%H-%M-%S.txt）'))
#     config.add_section('setting')
#     config.add_option('setting', 'mistiming', Var(Int, 600, desc='最大查询时间差（单位秒，为空时默认为600）'))
#     config.add_option('setting', 'timezone', ComboVar(String, ['local', 'utc'], 'local', desc='输入时间时区（为空时默认为当地时区）'))
#     config.add_option('setting', 'num_length', Var(Int, 4, desc='显示序号长度（为空时默认为4）'))
#     if mode == 'w':
#         config.to_ini(path)
#     else:
#         config.from_ini(path)
#     return config


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
        # print(self.cmd)
        process = subprocess.Popen(self.cmd, cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        self.process = process
        while (code := process.poll()) is None:
            try:
                line = process.stdout.readline().strip()
            except:
                continue
            if line:
                print(line)
                if line.startswith('[Progress]'):
                    self.on_progress.emit(float(line.removeprefix('[Progress]').strip()))
                for s in ['[Info]', '[Warning]', '[Error]']:
                    if line.startswith(s):
                        self.on_message.emit(line.removeprefix(s).strip())
        success = code == 0 and not self.cancel
        self.on_finished.emit(success)


class Demo(FramelessMainWindow):
    def __init__(self):
        super(Demo, self).__init__()

        # self.setTitleBar(StandardTitleBar(self))
        h = self.titleBar.height()
        # self.setWindowTitle('TITLE')
        # self.setWindowIcon(QIcon(FluentIcon.IOT.path()))
        self.setContentsMargins(0, h, 0, 0)

        widget = QWidget()
        vbox = QVBoxLayout()
        config_path = 'test.ini'
        mode = 'r' if os.path.exists(config_path) else 'w'
        # mode = 'w'
        config = parse(config_path, mode)
        self.values = []
        for section, values in config._config.items():
            box = QGroupBox(section)
            layout = QFormLayout()
            for option, value in values.items():
                label = BodyLabel(option)
                label.setFixedWidth(100)
                if isinstance(value, ComboVar):
                    w = ComboBox()
                    w.addItems(value.values_as_string)
                    if value.has_value():
                        w.setText(value.to_string())
                elif isinstance(value, Var) and getattr(value, 'type', None) is Bool:
                    w = CheckBox()
                    if value.has_value():
                        w.setChecked(value.get_value())
                    else:
                        # w.setTristate(True)
                        w.setCheckState(Qt.CheckState.PartiallyChecked)
                else:
                    w = LineEdit()
                    w.setClearButtonEnabled(True)
                    if value.has_value():
                        w.setText(value.to_string())
                w.setToolTip(value.get_desc())
                layout.addRow(label, w)
                self.values.append([value, w])
            box.setLayout(layout)
            vbox.addWidget(box)
        vbox.addStretch()
        btn = PrimaryPushButton('start')
        btn.clicked.connect(self.parse)
        vbox.addWidget(btn)
        widget.setLayout(vbox)
        self.setCentralWidget(widget)

    def parse(self):
        for value, w in self.values:
            if isinstance(value, ComboVar):
                value.set_value(value.values[w.currentIndex()])
            elif isinstance(value, Var) and getattr(value, 'type', None) is Bool:
                state = w.checkState()
                assert state is not Qt.CheckState.PartiallyChecked
                value.set_value(state is Qt.CheckState.Checked)
            else:
                value.set_value(value(w.text()))
            print(value.get_value())



if __name__ == '__main__':

    W = 1100
    H = 700

    app = QApplication(sys.argv)

    demo = Demo()
    demo.show()

    app.exec()
