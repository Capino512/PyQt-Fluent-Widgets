

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QFileDialog, QWidget, QVBoxLayout
from qfluentwidgets import LineEdit, BodyLabel, ComboBox, CheckBox, ToolButton, Slider, PasswordLineEdit, TextEdit, \
    FluentIcon
from typed import *


CURRENT_DIR = '.'


class _InputWidget:
    def validate(self):
        return True

    def get_value(self):
        raise NotImplementedError

    def update_value(self):
        pass


class DefaultInputWidget(LineEdit, _InputWidget):

    def __init__(self, var, parent=None):
        super(DefaultInputWidget, self).__init__(parent)
        self.setClearButtonEnabled(True)
        self.setToolTip(var.get_desc())
        if var.has_value():
            self.setText(var.to_string())
        self.var = var

    def validate(self):
        return self.var.validate(self.text())

    def get_value(self):
        return self.var(self.text())


class PasswordInputWidget(PasswordLineEdit, _InputWidget):
    def __init__(self, var, parent=None):
        super(PasswordInputWidget, self).__init__(parent)
        self.setClearButtonEnabled(True)
        self.setToolTip(var.get_desc())
        if var.has_value():
            self.setText(var.to_string())
        self.var = var

    def validate(self):
        return self.var.validate(self.text())

    def get_value(self):
        return self.var(self.text())


class CheckInputWidget(CheckBox, _InputWidget):
    def __init__(self, var, parent=None):
        super(CheckInputWidget, self).__init__(parent)
        self.setToolTip(var.get_desc())
        if var.has_value():
            self.setChecked(var.get_value())
        else:
            self.setCheckState(Qt.CheckState.PartiallyChecked)
        self.var = var

    def validate(self):
        return self.checkState() is not Qt.CheckState.PartiallyChecked

    def get_value(self):
        return self.checkState() is Qt.CheckState.Checked


class ComboInputWidget(ComboBox, _InputWidget):
    def __init__(self, var, parent=None):
        super(ComboInputWidget, self).__init__(parent)
        self.addItems(var.values_as_string)
        self.setToolTip(var.get_desc())
        if var.has_value():
            self.setText(var.to_string())
        self.var = var

    def get_value(self):
        return self.var.values[self.currentIndex()]


class SliderInputWidget(QWidget, _InputWidget):
    def __init__(self, var, parent=None):
        super(SliderInputWidget, self).__init__(parent)

        lower = var.lower
        upper = var.upper
        is_float = isinstance(var, FloatRangeVar)
        steps = var.steps if is_float else (upper - lower)
        minimum, maximum = (0, steps) if is_float else (lower, upper)
        fmt = f'%.{var.precision}f' if is_float else '%d'

        def var2slider(x):
            return round((x - lower) / (upper - lower) * steps) if is_float else x

        def slider2var(x):
            return (x / steps * (upper - lower) + lower) if is_float else x

        def update_label(x):
            label.setText(fmt % slider2var(x))

        layout = QHBoxLayout()

        slider = Slider()
        slider.setToolTip(var.get_desc())
        slider.setOrientation(Qt.Orientation.Horizontal)
        slider.setRange(minimum, maximum)
        slider.valueChanged.connect(update_label)
        if var.has_value():
            slider.setValue(var2slider(var.get_value()))

        label = BodyLabel()
        label.setFixedWidth(var.value_display_width)
        update_label(slider.value())

        layout.addWidget(slider)
        layout.addWidget(label)
        self.setLayout(layout)

        self.slider = slider
        self.var = var
        self.slider2var = slider2var

    def get_value(self):
        return self.slider2var(self.slider.value())


def dialog(is_file, is_input, filters='', parent=None):
    global CURRENT_DIR
    if is_file:
        method = QFileDialog.getOpenFileName if is_input else QFileDialog.getSaveFileName
        selected, _ = method(parent, '选择文件', CURRENT_DIR, filters)
        dir_ = os.path.dirname(selected)
    else:
        selected = dir_ = QFileDialog.getExistingDirectory(parent, '选择文件夹', CURRENT_DIR)
    if selected:
        CURRENT_DIR = dir_
    return selected


class FileOrDirInputWidget(QWidget, _InputWidget):
    def __init__(self, var, parent=None):
        super(FileOrDirInputWidget, self).__init__(parent)

        is_file = isinstance(var, FileVar)
        is_input = isinstance(var, InputFileOrDir)
        filters = var.filters if is_file else ''

        def _dialog():
            selected = dialog(is_file, is_input, filters, parent)
            if selected:
                line.setText(selected)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        line = LineEdit()
        line.setToolTip(var.get_desc())
        if var.has_value():
            line.setText(var.to_string())

        icon = QIcon(FluentIcon.MORE.path())
        btn = ToolButton()
        btn.setIcon(icon)
        btn.setFixedWidth(btn.sizeHint().height())
        btn.clicked.connect(_dialog)

        icon = QIcon(FluentIcon.FOLDER.path())
        btn2 = ToolButton()
        btn2.setIcon(icon)
        btn2.setFixedWidth(btn.sizeHint().height())
        btn2.clicked.connect(self.open_dir)

        layout.addWidget(line)
        layout.addWidget(btn)
        self.setLayout(layout)

        self.line = line
        self.var = var
        self.is_file = is_file

    def get_input_path(self):
        path = self.line.text()
        if not os.path.isabs(path):
            path = os.path.join(self.var.cwd, path)
        return path

    def open_dir(self):
        path = self.get_input_path()
        if os.path.isfile(path) if self.is_file else os.path.isdir(path):
            os.startfile(os.path.dirname(path))

    def validate(self):
        return self.var.validate(self.line.text())

    def get_value(self):
        return self.var(self.line.text())


class TextFileInputWidget(QWidget, _InputWidget):
    def __init__(self, var, parent=None):
        super(TextFileInputWidget, self).__init__(parent)

        is_input = isinstance(var, InputFileOrDir)
        filters = var.filters

        def _dialog():
            selected = dialog(True, is_input, filters, parent)
            if selected:
                line.setText(selected)
                if self.is_input:
                    self.load_text()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        line = LineEdit()
        line.setToolTip(var.get_desc())
        if var.has_value():
            line.setText(var.to_string())

        icon = QIcon(FluentIcon.MORE.path())
        btn = ToolButton()
        btn.setIcon(icon)
        btn.setFixedWidth(btn.sizeHint().height())
        btn.clicked.connect(_dialog)

        icon = QIcon(FluentIcon.FOLDER.path())
        btn2 = ToolButton()
        btn2.setIcon(icon)
        btn2.setFixedWidth(btn.sizeHint().height())
        btn2.clicked.connect(self.open_dir)

        layout.addWidget(line)
        layout.addWidget(btn)
        layout.addWidget(btn2)

        text = TextEdit()
        if not is_input:
            text.setReadOnly(True)
        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.addLayout(layout)
        v_layout.addWidget(text)
        self.setLayout(v_layout)

        self.line = line
        self.text = text
        self.var = var
        self.is_input = is_input

        if is_input:
            self.load_text()

    def get_input_path(self):
        path = self.line.text()
        if not os.path.isabs(path):
            path = os.path.join(self.var.cwd, path)
        return path

    def open_dir(self):
        if os.path.isfile(path := self.get_input_path()):
            os.startfile(os.path.dirname(path))

    def load_text(self):
        if os.path.isfile(path := self.get_input_path()):
            with open(path, 'rt', encoding='utf-8') as f:
                self.text.setText(f.read())

    def validate(self):
        return self.var.validate(self.line.text())

    def get_value(self):
        if self.is_input:
            if os.path.isfile(path := self.get_input_path()):
                with open(path, 'wt', encoding='utf-8') as f:
                    f.write(self.text.toPlainText())
        return self.var(self.line.text())

    def update_value(self):
        if not self.is_input:
            self.load_text()


def get_input_widget(var, cwd, parent=None):
    if isinstance(var, BoolVar):
        widget = CheckInputWidget
    elif isinstance(var, PasswordVar):
        widget = PasswordInputWidget
    elif isinstance(var, ComboVar):
        widget = ComboInputWidget
    elif isinstance(var, RangeVar):
        widget = SliderInputWidget
    elif isinstance(var, (FileVar, DirVar)):
        setattr(var, 'cwd', cwd)
        if isinstance(var, TextFile):
            widget = TextFileInputWidget
        else:
            widget = FileOrDirInputWidget
    else:
        widget = DefaultInputWidget
    return widget(var, parent)
