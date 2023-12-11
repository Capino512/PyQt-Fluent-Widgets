

import os
import sys
import importlib

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QWidget, QFormLayout, QGroupBox, QVBoxLayout, QHBoxLayout, \
    QListWidgetItem, QFileDialog, QStackedWidget
from qfluentwidgets import LineEdit, BodyLabel, ComboBox, CheckBox, PrimaryPushButton, ListWidget, \
    SmoothScrollArea, TextEdit, PushButton, IndeterminateProgressBar, Slider, setFont, TabBar, \
    TabCloseButtonDisplayMode
from qframelesswindow import FramelessMainWindow
from typed import *
from utils.module import init_module_config, parse_input_config
from utils.thread import Thread


CURRENT_DIR = '.'


class TabWidget(QWidget):
    def __init__(self, parent=None):
        super(TabWidget, self).__init__(parent)
        tab_bar = TabBar()
        tab_bar.setTabsClosable(True)
        tab_bar.setCloseButtonDisplayMode(TabCloseButtonDisplayMode.ON_HOVER)
        tab_bar.setAddButtonVisible(False)
        tab_bar.tabCloseRequested.connect(self.close_tab)
        stack = QStackedWidget()
        vbox = QVBoxLayout()
        vbox.addWidget(tab_bar)
        vbox.addWidget(stack)
        self.setLayout(vbox)
        self.tab_bar = tab_bar
        self.stack = stack
        self._count = 0

    def close_tab(self, index):
        self.tab_bar.removeTab(index)
        self.stack.removeWidget(self.stack.widget(index))
        self.stack.setCurrentIndex(self.tab_bar.currentIndex())

    def add_tab(self, name, widget, icon=None):

        def on_click():
            self.stack.setCurrentIndex(self.tab_bar.currentIndex())

        self._count += 1
        self.stack.addWidget(widget)
        self.tab_bar.addTab(str(self._count), name, icon, onClick=on_click)
        self.tab_bar.setCurrentIndex(self.stack.count() - 1)
        self.stack.setCurrentIndex(self.stack.count() - 1)


def default_input_widget(value):
    w = LineEdit()
    w.setClearButtonEnabled(True)
    if value.has_value():
        w.setText(value.to_string())
    w.setToolTip(value.get_desc())

    def get_value():
        return value(w.text())

    return w, get_value


def combo_input_widget(value):
    w = ComboBox()
    w.addItems(value.values_as_string)
    if value.has_value():
        w.setText(value.to_string())
    w.setToolTip(value.get_desc())

    def get_value():
        return value.values[w.currentIndex()]

    return w, get_value


def bool_input_widget(value):
    w = CheckBox()
    if value.has_value():
        w.setChecked(value.get_value())
    else:
        w.setCheckState(Qt.CheckState.PartiallyChecked)
    w.setToolTip(value.get_desc())

    def get_value():
        state = w.checkState()
        assert state is not Qt.CheckState.PartiallyChecked
        value.set_value(state is Qt.CheckState.Checked)

    return w, get_value


def file_input_widget(value, parent=None):
    # "Images (*.png *.jpg *.bmp)"

    is_file = isinstance(value, FileVar)
    is_open = isinstance(value, OpenFileVar)
    filters = value.filters if is_file else ''

    def dialog():
        global CURRENT_DIR
        if is_file:
            selected, _ = (QFileDialog.getOpenFileName if is_open else QFileDialog.getSaveFileName)(parent, '选择文件', CURRENT_DIR, filters)
            dir_ = os.path.dirname(selected)
        else:
            selected = dir_ = QFileDialog.getExistingDirectory(parent, '选择文件夹', CURRENT_DIR)
        if selected:
            CURRENT_DIR = dir_
            line.setText(selected)

    layout = QHBoxLayout()
    line = LineEdit()
    btn = PushButton('...')

    if value.has_value():
        line.setText(value.to_string())
    line.setToolTip(value.get_desc())

    layout.addWidget(line)
    layout.addWidget(btn)
    btn.clicked.connect(dialog)

    def get_value():
        return line.text()

    return layout, get_value


def range_input_widget(value):
    lower = value.lower
    upper = value.upper
    is_float = isinstance(value, FloatRangeVar)
    steps = value.steps if is_float else (upper - lower)
    minimum, maximum = (0, steps) if is_float else (lower, upper)
    fmt = f'%.{value.precision}f' if is_float else '%d'

    def raw2slider(x):
        return round((x - lower) / (upper - lower) * steps) if is_float else x

    def slider2raw(x):
        return (x / steps * (upper - lower) + lower) if is_float else x

    def set_text(x):
        label.setText(fmt % slider2raw(x))

    layout = QHBoxLayout()
    slider = Slider()
    label = BodyLabel()
    label.setFixedWidth(value.value_display_width)

    slider.setRange(minimum, maximum)
    if value.has_value():
        slider.setValue(raw2slider(value.get_value()))
    set_text(slider.value())

    slider.setOrientation(Qt.Orientation.Horizontal)
    slider.setToolTip(value.get_desc())
    slider.valueChanged.connect(set_text)

    layout.addWidget(slider)
    layout.addWidget(label)

    def get_value():
        return slider2raw(slider.value())

    return layout, get_value


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
        scroll = SmoothScrollArea()
        # scroll.setViewportMargins(0, 0, 0, 0)
        scroll.setWidgetResizable(True)
        # scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # scroll.setStyleSheet('''ScrollArea{background-color: transparent}''')
        widget = QWidget()
        widget.setMinimumWidth(500)
        widget.setMaximumWidth(800)
        # widget.setStyleSheet('''QWidget{background-color: rgba(0, 0, 0, 5)}''')
        vbox = QVBoxLayout()

        btn_start = PrimaryPushButton('start')
        btn_cancel = PrimaryPushButton('cancel')
        btn_reset = PrimaryPushButton('reset')
        progress_bar = IndeterminateProgressBar()
        btn_start.setFixedWidth(100)
        btn_cancel.setFixedWidth(100)
        btn_reset.setFixedWidth(100)
        btn_cancel.hide()
        progress_bar.hide()
        btn_start.clicked.connect(self.start)
        btn_cancel.clicked.connect(self.on_cancel)
        btn_reset.clicked.connect(self.reset)
        text_area = TextEdit()
        text_area.setReadOnly(True)
        text_area.setMinimumHeight(120)
        text_area.setMaximumHeight(160)

        hbox = QHBoxLayout()
        hbox.addWidget(btn_start, Qt.AlignmentFlag.AlignLeft)
        hbox.addWidget(btn_cancel, Qt.AlignmentFlag.AlignLeft)
        hbox.addStretch()
        hbox.addWidget(btn_reset, Qt.AlignmentFlag.AlignRight)

        self.vbox = vbox
        self.btn_start = btn_start
        self.btn_cancel = btn_cancel
        self.progress_bar = progress_bar
        self.text_area = text_area
        self.thread = None
        self.init()

        widget.setLayout(vbox)
        scroll.setWidget(widget)
        layout.addWidget(scroll)
        layout.addWidget(progress_bar)
        layout.addLayout(hbox)
        layout.addWidget(text_area)
        self.setLayout(layout)

    def init(self):
        vbox = self.vbox

        items = [vbox.itemAt(i) for i in range(vbox.count())]
        for item in items:
            if widget_or_layout:= (item.widget() or item.layout()):
                widget_or_layout.deleteLater()
            vbox.removeItem(item)
        self.values.clear()

        for section, values in self.config.items():
            box = QGroupBox(section)
            layout = QFormLayout()
            for option, value in values.items():
                label = BodyLabel(option)
                label.setFixedWidth(100)
                if isinstance(value, ComboVar):
                    w, get_value = combo_input_widget(value)
                elif isinstance(value, Var) and getattr(value, 'type', None) is Bool:
                    w, get_value = bool_input_widget(value)
                elif isinstance(value, (FileVar, DirVar)):
                    w, get_value = file_input_widget(value)
                elif isinstance(value, RangeVar):
                    w, get_value = range_input_widget(value)
                else:
                    w, get_value = default_input_widget(value)
                layout.addRow(label, w)
                self.values.append([value, get_value])
            box.setLayout(layout)
            vbox.addWidget(box)
        vbox.addStretch()

    def on_start(self):
        self.btn_start.hide()
        self.btn_cancel.show()
        self.progress_bar.show()
        self.text_area.clear()

    def on_finished(self, code):
        self.btn_start.show()
        self.btn_cancel.hide()
        self.progress_bar.hide()
        self.text_area.append(f'Exit code: {code}')

    def on_cancel(self):
        self.thread.force_stop()

    def on_message(self, line):
        self.text_area.append(line)

    def reset(self):
        for value, _ in self.values:
            value.reset()
        self.init()

    def parse(self):
        for value, get_value in self.values:
            value.set_value(get_value())
        self.config.dump_ini(self.config_path)

    def run_in_background(self):
        cwd = os.path.abspath(self.module_dir)
        ini = os.path.abspath(self.config_path)
        thread = Thread(f'{self.execute} "{ini}"', cwd, self)
        thread.on_finished.connect(self.on_finished)
        thread.on_message.connect(self.on_message)
        self.thread = thread
        self.on_start()
        thread.start()

    def start(self):
        self.parse()
        self.run_in_background()


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
        # module_list.setStyleSheet('border: 1px solid rgba(0, 0, 0, 15)')
        module_list.itemDoubleClicked.connect(self.add_tab)

        tab_widget = TabWidget()
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
            module_config = init_module_config()
            module_config.load_ini(module_ini)
            module_name = module_config.get_option('module', 'name')
            item = QListWidgetItem(module_name)
            item.setData(Qt.ItemDataRole.UserRole, module)
            module_list.addItem(item)

    def add_tab(self, item):
        module = item.data(Qt.ItemDataRole.UserRole)
        module_ini = os.path.join('./extensions', module, 'module.ini')
        module_config = init_module_config()
        module_config.load_ini(module_ini)
        module_dir = os.path.join('./extensions', module)
        execute = module_config.get_option('module', 'execute')
        config_path = os.path.join(module_dir, module_config.get_option('module', 'config'))
        mode = 'r' if os.path.exists(config_path) else 'w'
        input_config = parse_input_config(importlib.import_module(f'extensions.{module}').init_config, config_path, mode)
        self.tab_widget.add_tab(module_config.get_option('module', 'name'), Module(module_dir, execute, config_path, input_config))

    def center(self):
        qr = self.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == '__main__':

    W = 960
    H = 640

    app = QApplication(sys.argv)

    demo = Demo()
    demo.show()

    app.exec()
