

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QFileDialog
from qfluentwidgets import LineEdit, BodyLabel, ComboBox, CheckBox, PushButton, Slider, PasswordLineEdit
from typed import *


CURRENT_DIR = '.'


def default_input_widget(value):
    w = (PasswordLineEdit if isinstance(value, PasswordVar) else LineEdit)()
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
        return state is Qt.CheckState.Checked

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


def get_input_widget(value, parent=None):
    if isinstance(value, ComboVar):
        w, get_value = combo_input_widget(value)
    elif isinstance(value, BoolVar):
        w, get_value = bool_input_widget(value)
    elif isinstance(value, (FileVar, DirVar)):
        w, get_value = file_input_widget(value, parent)
    elif isinstance(value, RangeVar):
        w, get_value = range_input_widget(value)
    else:
        w, get_value = default_input_widget(value)
    return w, get_value
