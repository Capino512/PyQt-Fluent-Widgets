

import os
import sys
import importlib

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QListWidgetItem
from qfluentwidgets import ListWidget
from qframelesswindow import FramelessMainWindow, StandardTitleBar
from utils import init_main_config, init_module_config, parse_input_config
from widgets import TabWidget
from module import Module


class Demo(FramelessMainWindow):
    def __init__(self):
        super(Demo, self).__init__()

        config = init_main_config()
        # config.dump_ini('config.ini')
        config.load_ini('config.ini')
        self.config = config

        self.setTitleBar(StandardTitleBar(self))
        self.setWindowTitle(config.get_option('main_win', 'title'))
        self.setWindowIcon(QIcon(config.get_option('main_win', 'icon')))

        h = self.titleBar.height()
        self.setContentsMargins(0, h, 0, 0)
        widget = QWidget()

        h_layout = QHBoxLayout()
        module_list = ListWidget()
        module_list.setMinimumWidth(config.get_option('module_list', 'min_width'))
        module_list.setMaximumWidth(config.get_option('module_list', 'max_width'))
        module_list.itemDoubleClicked.connect(self.add_tab)

        tab_widget = TabWidget()
        h_layout.addWidget(module_list)
        h_layout.addWidget(tab_widget)
        widget.setLayout(h_layout)

        self.tab_widget = tab_widget
        self.setCentralWidget(widget)
        self.resize(config.get_option('main_win', 'win_width'), config.get_option('main_win', 'win_height'))
        self.center()

        for module in os.listdir('./extensions'):
            module_dir = os.path.join('./extensions', module)
            module_ini = os.path.join(module_dir, 'module.ini')
            module_pkg = f'extensions.{module}'
            if not os.path.exists(module_ini):
                continue
            module_config = init_module_config()
            module_config.load_ini(module_ini)
            module_name = module_config.get_option('module', 'name')
            item = QListWidgetItem(module_name)
            item.setData(Qt.ItemDataRole.UserRole, [module_dir, module_ini, module_pkg])
            module_list.addItem(item)

    def add_tab(self, item):
        module_dir, module_ini, module_pkg = item.data(Qt.ItemDataRole.UserRole)
        module_config = init_module_config()
        module_config.load_ini(module_ini)
        execute = module_config.get_option('module', 'execute')
        config_path = os.path.join(module_dir, module_config.get_option('module', 'config'))
        mode = 'r' if os.path.exists(config_path) else 'w'
        input_config = parse_input_config(importlib.import_module(module_pkg).init_config, config_path, mode)
        module = Module(module_dir, execute, config_path, input_config, self.config)
        self.tab_widget.add_tab(module_config.get_option('module', 'name'), module)

    def center(self):
        qr = self.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == '__main__':

    W = 960
    H = 640

    sys.path.append(os.path.dirname(os.path.abspath(sys.argv[0])))
    app = QApplication(sys.argv)

    demo = Demo()
    demo.show()

    app.exec()

    # conda activate PySide6-Fluent-Widgets
    # pyinstaller -F -w -p . main.py
