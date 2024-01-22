

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QFileDialog, QWidget, QVBoxLayout, QButtonGroup
from qfluentwidgets import LineEdit, BodyLabel, ComboBox, CheckBox, ToolButton, Slider, PasswordLineEdit, TextEdit, \
    FluentIcon, RadioButton, SwitchButton
from typed import *


CURRENT_DIR = '.'


class _InputWidget:
    def validate(self):
        return True

    def get_value(self):
        raise NotImplementedError

    def update_value(self):
        pass


class LineEditWidget(LineEdit, _InputWidget):

    def __init__(self, var, parent=None):
        super(LineEditWidget, self).__init__(parent)
        self.setToolTip(var.desc)
        self.setClearButtonEnabled(True)
        if var.has_value():
            self.setText(str(var))
        self.var = var

    def validate(self):
        return self.var.validate(self.text())

    def get_value(self):
        return self.var(self.text())


class PasswordLineEditWidget(PasswordLineEdit, _InputWidget):
    def __init__(self, var, parent=None):
        super(PasswordLineEditWidget, self).__init__(parent)
        self.setToolTip(var.desc)
        self.setClearButtonEnabled(True)
        if var.has_value():
            self.setText(str(var))
        self.var = var

    def validate(self):
        return self.var.validate(self.text())

    def get_value(self):
        return self.var(self.text())


class CheckBoxWidget(CheckBox, _InputWidget):
    def __init__(self, var, parent=None):
        super(CheckBoxWidget, self).__init__(parent)
        self.setToolTip(var.desc)
        if var.has_value():
            self.setChecked(var.get_value())
        else:
            self.setCheckState(Qt.CheckState.PartiallyChecked)
        self.var = var

    def validate(self):
        return self.checkState() is not Qt.CheckState.PartiallyChecked

    def get_value(self):
        return self.checkState() is Qt.CheckState.Checked


class SwitchButtonWidget(SwitchButton, _InputWidget):
    def __init__(self, var, parent=None):
        super(SwitchButtonWidget, self).__init__(parent)
        self.setToolTip(var.desc)
        self.setChecked(var.has_value() and var.get_value())
        self.var = var

    def get_value(self):
        return self.isChecked()


class ComboBoxWidget(ComboBox, _InputWidget):
    def __init__(self, var, parent=None):
        super(ComboBoxWidget, self).__init__(parent)
        self.setToolTip(var.desc)
        self.addItems(var.values_as_string)
        if var.has_value():
            self.setText(str(var))
        self.var = var

    def get_value(self):
        return self.var.values[self.currentIndex()]


class RadioButtonWidget(QWidget, _InputWidget):
    def __init__(self, var, parent=None):
        super(RadioButtonWidget, self).__init__(parent)
        self.setToolTip(var.desc)
        hbox = QHBoxLayout(self)
        btns = QButtonGroup(self)
        default = var.get_value()
        for i, (value, value_as_string) in enumerate(zip(var.values, var.values_as_string)):
            btn = RadioButton(value_as_string)
            if var.has_value() and value == default:
                btn.setChecked(True)
            btns.addButton(btn, i)
            hbox.addWidget(btn)
        self.var = var
        self.btns = btns

    def get_value(self):
        return self.var.values[self.btns.checkedId()]


class SliderWidget(QWidget, _InputWidget):
    def __init__(self, var, parent=None):
        super(SliderWidget, self).__init__(parent)

        lower = var.minimum
        upper = var.maximum
        is_float = isinstance(var, FloatSlider)
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

        label = BodyLabel()
        label.setFixedWidth(60)  # todo

        slider = Slider()
        slider.setToolTip(var.desc)
        slider.setOrientation(Qt.Orientation.Horizontal)
        slider.setRange(minimum, maximum)
        slider.valueChanged.connect(update_label)
        if var.has_value():
            slider.setValue(var2slider(var.get_value()))

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


class FileDirWidget(QWidget, _InputWidget):
    def __init__(self, var, parent=None):
        super(FileDirWidget, self).__init__(parent)
        is_file = isinstance(var, File)
        is_input = is_file and var.is_input
        is_editable_text = is_file and var.is_editable_text
        filters = var.filters if is_file else ''

        def _dialog():
            selected = dialog(is_file, is_input, filters, parent)
            if selected:
                line.setText(selected)
            if self.is_input and self.is_editable_text:
                self.load_text()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        line = LineEdit()
        line.setToolTip(var.desc)
        if var.has_value():
            line.setText(str(var))

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

        self.line = line
        self.var = var
        self.is_file = is_file
        self.is_input = is_input
        self.is_editable_text = is_editable_text

        if is_editable_text:
            text = TextEdit()
            if not is_input:
                text.setReadOnly(True)
            v_layout = QVBoxLayout()
            v_layout.setContentsMargins(0, 0, 0, 0)
            v_layout.addLayout(layout)
            v_layout.addWidget(text)
            self.setLayout(v_layout)
            self.text = text
            if is_input:
                self.load_text()
        else:
            self.setLayout(layout)

    def get_input_path(self):
        path = self.line.text()
        if not os.path.isabs(path):
            path = os.path.join(self.var.cwd, path)
        return path

    def open_dir(self):
        path = self.get_input_path()
        if os.path.isfile(path) if self.is_file else os.path.isdir(path):
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
        if self.is_editable_text and not self.is_input:
            self.load_text()


def get_input_widget(var, cwd, parent=None):
    if isinstance(var, Check):
        widget = CheckBoxWidget
    elif isinstance(var, Switch):
        widget = SwitchButtonWidget
    elif isinstance(var, Password):
        widget = PasswordLineEditWidget
    elif isinstance(var, Combo):
        widget = ComboBoxWidget
    elif isinstance(var, Radio):
        widget = RadioButtonWidget
    elif isinstance(var, (IntSlider, FloatSlider)):
        widget = SliderWidget
    elif isinstance(var, (File, Dir)):
        var.cwd = cwd
        widget = FileDirWidget
    else:
        widget = LineEditWidget
    return widget(var, parent)
