import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QButtonGroup
from qfluentwidgets import RadioButton


class Demo(QWidget):

    def __init__(self):
        super().__init__()
        self.hBoxLayout = QHBoxLayout(self)
        button1 = RadioButton('Option 1')
        button2 = RadioButton('Option 2')
        button3 = RadioButton('Option 3')

        btns = QButtonGroup(self)
        btns.addButton(button1, 0)
        btns.addButton(button2, 1)
        btns.addButton(button3, 2)
        self.hBoxLayout.addWidget(button1)
        self.hBoxLayout.addWidget(button2)
        self.hBoxLayout.addWidget(button3)

        def fn(_, flag):
            if flag:
                print(btns.checkedId())
                print(btns.button(btns.checkedId()).text())



        btns.buttonToggled.connect(fn)
        # btns.buttonToggled.connect(lambda *args: print(args))
        # btns.buttonClicked.connect(lambda *args: print(args))

        # self.vBoxLayout.addWidget(self.button1, 0, Qt.AlignCenter)
        # self.vBoxLayout.addWidget(self.button2, 0, Qt.AlignCenter)
        # self.vBoxLayout.addWidget(self.button3, 0, Qt.AlignCenter)
        self.resize(300, 150)
        self.setStyleSheet('Demo{background:white}')


if __name__ == '__main__':

    print('{:0{width}d}'.format(10, width=4))
    exit()

    app = QApplication(sys.argv)
    w = Demo()
    w.show()
    app.exec()
