

import os
import sys
import importlib

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QWidget, QFormLayout, QGroupBox, QVBoxLayout, QTabWidget, QHBoxLayout, \
    QTextEdit, QListWidgetItem
from qfluentwidgets import LineEdit, BodyLabel, ComboBox, CheckBox, PrimaryPushButton, ListWidget, ScrollArea, setFont
from qframelesswindow import FramelessMainWindow
from typed_var import *
from utils.module import parse_module_config, parse_input_config
from utils.thread import Thread


# module/config.py
# module/config.ini
# module/module.ini
# module/main.py

class Module(QWidget):
    def __init__(self, module_dir, execute, config_path, config, parent=None):
        super(Module, self).__init__(parent)

        self.values = []
        self.config = config
        self.config_path = config_path
        self.module_dir = module_dir
        self.execute = execute

        layout = QVBoxLayout()
        scroll = ScrollArea()
        scroll.setStyleSheet('''ScrollArea{background-color: transparent}''')
        widget = QWidget()
        vbox = QVBoxLayout()

        self.vbox = vbox
        self.init()
        widget.setLayout(vbox)
        scroll.setWidget(widget)
        layout.addWidget(scroll)

        btn_start = PrimaryPushButton('start')
        btn_cancel = PrimaryPushButton('cancel')
        btn_reset = PrimaryPushButton('reset')
        btn_start.setFixedWidth(100)
        btn_cancel.setFixedWidth(100)
        btn_reset.setFixedWidth(100)
        btn_cancel.hide()
        btn_start.clicked.connect(self.parse)
        btn_cancel.clicked.connect(self.on_cancel)
        btn_reset.clicked.connect(self.reset)
        text_area = QTextEdit()
        text_area.setReadOnly(True)
        text_area.setMinimumHeight(120)
        text_area.setMaximumHeight(160)

        hbox = QHBoxLayout()
        hbox.addWidget(btn_start, Qt.AlignmentFlag.AlignLeft)
        hbox.addWidget(btn_cancel, Qt.AlignmentFlag.AlignLeft)
        hbox.addStretch()
        hbox.addWidget(btn_reset, Qt.AlignmentFlag.AlignRight)

        layout.addLayout(hbox)
        layout.addWidget(text_area)

        self.setLayout(layout)
        self.btn_start = btn_start
        self.btn_cancel = btn_cancel
        self.text_area = text_area
        self.thread = None

    def init(self):
        vbox = self.vbox

        items = [vbox.itemAt(i) for i in range(vbox.count())]
        for item in items:
            if widget_or_layout:= (item.widget() or item.layout()):
                widget_or_layout.deleteLater()
            vbox.removeItem(item)

        for section, values in self.config.data.items():
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

    def on_start(self):
        self.btn_start.hide()
        self.btn_cancel.show()

    def on_finished(self, success):
        self.btn_start.show()
        self.btn_cancel.hide()

    def on_cancel(self):
        self.thread.force_stop()

    def on_message(self, line):
        self.text_area.append(line)

    def reset(self):
        for value, w in self.values:
            value.reset()

        self.init()

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
        self.config.to_ini(self.config_path)
        cwd = os.path.abspath(self.module_dir)
        ini = os.path.abspath(self.config_path)
        thread = Thread(f'{self.execute} "{ini}"', cwd, self)
        thread.on_finished.connect(self.on_finished)
        thread.on_message.connect(self.on_message)
        self.thread = thread
        self.on_start()
        thread.start()


class Demo(FramelessMainWindow):
    def __init__(self):
        super(Demo, self).__init__()

        h = self.titleBar.height()
        self.setContentsMargins(0, h, 0, 0)
        widget = QWidget()

        h_layout = QHBoxLayout()
        module_list = ListWidget()
        module_list.setMinimumWidth(120)
        module_list.setMaximumWidth(160)
        module_list.setStyleSheet('border: 1px solid rgba(0, 0, 0, 15)')
        module_list.itemDoubleClicked.connect(self.add_tab)

        tab_widget = QTabWidget()
        # tab_widget.setTabShape(QTabWidget.TabShape.Triangular)
        tab_widget.setTabsClosable(True)
        tab_widget.tabCloseRequested.connect(lambda index: tab_widget.removeTab(index))
        setFont(tab_widget)

        h_layout.addWidget(module_list)
        h_layout.addWidget(tab_widget)
        widget.setLayout(h_layout)

        self.tab_widget = tab_widget
        self.setCentralWidget(widget)
        self.resize(W, H)
        self.center()

        for module in os.listdir('./extensions'):
            module_ini = os.path.join('./extensions', module, 'module.ini')
            if not os.path.exists(module_ini):
                continue
            item = QListWidgetItem(module)
            setFont(item)
            module_list.addItem(item)

    def add_tab(self, index):
        module = index.text()
        module_ini = os.path.join('./extensions', module, 'module.ini')
        module_config = parse_module_config()
        module_config.from_ini(module_ini)
        module_dir = os.path.join('./extensions', module)
        execute = module_config.get('module', 'execute')
        config_path = os.path.join(module_dir, module_config.get('module', 'config'))
        mode = 'r' if os.path.exists(config_path) else 'w'
        input_config = parse_input_config(importlib.import_module(f'extensions.{module}').init_config, config_path, mode)
        index = self.tab_widget.addTab(Module(module_dir, execute, config_path, input_config), module_config.get('module', 'name'))
        self.tab_widget.setCurrentIndex(index)

    def center(self):
        qr = self.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == '__main__':

    W = 720
    H = 640

    app = QApplication(sys.argv)

    demo = Demo()
    demo.show()

    app.exec()
