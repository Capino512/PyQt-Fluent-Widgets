

import os
import sys
import importlib

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QWidget, QFormLayout, QGroupBox, QVBoxLayout, QTabWidget, QHBoxLayout, \
    QListWidgetItem, QFileDialog, QSizePolicy, QAbstractScrollArea
from qfluentwidgets import LineEdit, BodyLabel, ComboBox, CheckBox, PrimaryPushButton, ListWidget, SingleDirectionScrollArea, \
    TextEdit, PushButton, IndeterminateProgressBar, Slider, setFont, TabBar, OpacityAniStackedWidget, TabCloseButtonDisplayMode
from qframelesswindow import FramelessMainWindow
from typed import *
from utils.module import parse_module_config, parse_input_config
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
        stack = OpacityAniStackedWidget()
        vbox = QVBoxLayout()
        vbox.addWidget(tab_bar)
        vbox.addWidget(stack)
        self.setLayout(vbox)
        self.tab_bar = tab_bar
        self.stack = stack

    def close_tab(self, index):
        self.tab_bar.removeTab(index)
        self.stack.removeWidget(self.stack.widget(index))
        self.stack.setCurrentIndex(self.tab_bar.currentIndex())

    def add_tab(self, name, widget, icon=None):

        def on_click():
            self.stack.setCurrentIndex(self.tab_bar.currentIndex())

        self.stack.addWidget(widget)
        self.tab_bar.addTab(name, name, icon, onClick=on_click)
        self.tab_bar.setCurrentIndex(self.stack.count() - 1)
        self.stack.setCurrentIndex(self.stack.count() - 1)



if __name__ == '__main__':

    W = 720
    H = 640

    app = QApplication(sys.argv)

    demo = TabWidget()
    demo.add_tab('xxx', PrimaryPushButton('xxx'))
    demo.add_tab('yyy', PrimaryPushButton('yyy'))
    demo.add_tab('zzz', PrimaryPushButton('zzz'))
    demo.tab_bar.adjustSize()
    demo.show()

    app.exec()
