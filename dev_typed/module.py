

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QFormLayout, QGroupBox, QVBoxLayout, QHBoxLayout
from qfluentwidgets import BodyLabel, PrimaryPushButton, SmoothScrollArea, TextEdit, IndeterminateProgressBar
from utils import Thread
from widgets import get_input_widget


# module/config.py
# module/config.ini
# module/module.ini
# module/main.py

class Module(QWidget):
    def __init__(self, module_dir, execute, config_path, config, ui_config, parent=None):
        super(Module, self).__init__(parent)

        self.values = []
        self.config = config
        self.ui_config = ui_config
        self.config_path = config_path
        self.module_dir = module_dir
        self.execute = execute

        layout = QVBoxLayout()
        scroll = SmoothScrollArea()
        scroll.setWidgetResizable(True)
        widget = QWidget()
        widget.setMinimumWidth(ui_config.get_option('module', 'min_width'))
        # widget.setMaximumWidth(800)

        btn_start = PrimaryPushButton('start')
        btn_cancel = PrimaryPushButton('cancel')
        btn_reset = PrimaryPushButton('reset')
        progress_bar = IndeterminateProgressBar()
        btn_start.setFixedWidth(ui_config.get_option('module', 'btn_width'))
        btn_cancel.setFixedWidth(ui_config.get_option('module', 'btn_width'))
        btn_reset.setFixedWidth(ui_config.get_option('module', 'btn_width'))
        btn_cancel.hide()
        progress_bar.hide()
        btn_start.clicked.connect(self.start)
        btn_cancel.clicked.connect(self.on_cancel)
        btn_reset.clicked.connect(self.reset)
        text_area = TextEdit()
        text_area.setReadOnly(True)
        text_area.setMinimumHeight(ui_config.get_option('module', 'text_area_min_width'))
        text_area.setMaximumHeight(ui_config.get_option('module', 'text_area_max_width'))

        hbox = QHBoxLayout()
        hbox.addWidget(btn_start, Qt.AlignmentFlag.AlignLeft)
        hbox.addWidget(btn_cancel, Qt.AlignmentFlag.AlignLeft)
        hbox.addStretch()
        hbox.addWidget(btn_reset, Qt.AlignmentFlag.AlignRight)

        vbox = QVBoxLayout()
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
        cwd = os.path.abspath(self.module_dir)

        items = [vbox.itemAt(i) for i in range(vbox.count())]
        for item in items:
            if widget_or_layout := (item.widget() or item.layout()):
                widget_or_layout.deleteLater()
            vbox.removeItem(item)
        self.values.clear()

        for section, options in self.config.items():
            box = QGroupBox(section.capitalize())
            layout = QFormLayout()
            for option, var in options.items():
                label = BodyLabel(option.capitalize())
                label.setFixedWidth(self.ui_config.get_option('module', 'label_width'))
                label.setFixedHeight(self.ui_config.get_option('module', 'label_height'))
                widget = get_input_widget(var, cwd, self)
                layout.addRow(label, widget)
                self.values.append([var, label, widget])
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
        if code == 0:
            for var, label, widget in self.values:
                widget.update_value()

    def on_cancel(self):
        self.thread.force_stop()

    def on_message(self, line):
        self.text_area.append(line)

    def reset(self):
        for var, label, widget in self.values:
            var.reset()
        self.init()

    def parse(self):
        validates = []
        for var, label, widget in self.values:
            validate = widget.validate()
            validates.append(validate)
            if validate:
                label.setStyleSheet('')
                var.set_value(widget.get_value())
            else:
                label.setStyleSheet(f'border: 1px solid {self.ui_config.get_option("module", "label_warning_color")};')
        validate = all(validates)
        if validate:
            self.config.dump_ini(self.config_path)
        return validate

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
        if self.parse():
            self.run_in_background()
