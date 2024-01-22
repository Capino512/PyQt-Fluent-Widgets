

from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from qfluentwidgets import TabBar, TabCloseButtonDisplayMode


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
