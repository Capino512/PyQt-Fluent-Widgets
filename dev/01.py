# coding:utf-8
import os
import sys
import time

from contextlib import contextmanager
import PySide6
import subprocess
from PySide6.QtCore import Qt, QEventLoop, QTimer, QSize
from PySide6 import QtCore, QtGui
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QHBoxLayout, QVBoxLayout, QStackedLayout, QWidget, QTabWidget, \
    QTabBar, QTreeWidgetItem, QFrame, QDialog, QLineEdit, QPushButton, QFormLayout

from qfluentwidgets import SplashScreen, PixmapLabel, ImageLabel, CardWidget, IconWidget, TextWrap, FluentIcon, \
    ToolButton, FlowLayout, CommandBar, CommandBarView, Action, ListWidget, TreeView, TabBar, TreeWidget, ProgressBar, \
    IndeterminateProgressBar, PushButton, LineEdit, TransparentDropDownPushButton, setFont, RoundMenu, BodyLabel, \
    ComboBox

from qframelesswindow import FramelessWindow, StandardTitleBar


class Thread(QtCore.QThread):
    on_finished = QtCore.Signal(bool)
    on_progress = QtCore.Signal(int)
    on_message = QtCore.Signal(str)

    def __init__(self, cmd, parent=None):
        super(Thread, self).__init__(parent)
        self.cmd = cmd
        self.p = None
        self.cancel = None

    def force_stop(self):
        self.p.kill()
        self.cancel = True

    def run(self):
        print('start', self.cmd)
        self.cancel = False
        p = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        self.p = p
        while (code := p.poll()) is None:
            line = p.stdout.readline().strip()
            print(line)
            # try:
            #     line = line.decode("utf-8").strip()
            # except:
            #     continue
                # try:
                #     line = (line.decode("gbk").strip())
                #     print('gbk', line)
                # except:
                #     continue
            if line:
                # print(f'info: {line}')
                if line.startswith('[Progress]'):
                    value = int(line.removeprefix('[Progress]').strip())
                    self.on_progress.emit(value)
                    self.on_message.emit('%d%%' % value)
                for s in ['[Info]', '[Warning]', '[Error]']:
                    if line.startswith(s):
                        self.on_message.emit(line.removeprefix(s).strip())
        success = code == 0 and not self.cancel
        print('finish', success)
        self.on_finished.emit(success)
        # time.sleep(1)


@contextmanager
def h_layout(parent=None):
    layout = QHBoxLayout(parent)
    yield layout


class FuncDialog(QDialog):
    def __init__(self, title, show_label=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.show_label = show_label

        layout = QVBoxLayout()
        # layout = QFormLayout()

        algo_list = ComboBox()
        algo_list.addItem('DMRT')
        algo_list.addItem('DMRT')
        algo_list.addItem('DMRT')

        # layout.addRow('算法：', algo_list)

        with h_layout() as layout_tmp:
            layout_tmp.addWidget(algo_list, stretch=1)
            layout_tmp.addWidget(BodyLabel(' 选择算法 '), stretch=0)

        layout.addLayout(layout_tmp)

        layout_1 = QHBoxLayout()
        layout_1.addWidget(LineEdit())
        layout_1.addWidget(PushButton('选择参数文件'))
        layout.addLayout(layout_1)
        layout.addSpacing(8)

        layout_2 = QHBoxLayout()
        layout_2.addWidget(LineEdit())
        layout_2.addWidget(PushButton('选择输出路径'))
        layout.addLayout(layout_2)
        layout.addSpacing(8)

        # layout_3 = QHBoxLayout()
        label = BodyLabel()
        progress_bar = ProgressBar()
        progress_bar.hide()
        self.label = label
        self.progress_bar = progress_bar
        # progress_bar.setValue(50)
        layout.addWidget(label)
        layout.addWidget(progress_bar)
        layout.addSpacing(8)

        layout_3 = QHBoxLayout()
        layout_3.addWidget(run_btn_:=PushButton('运行'))
        run_btn_.clicked.connect(lambda : progress_bar.show() or self.run())
        run_btn_.setMaximumWidth(100)
        layout.addStretch(1)
        layout.addLayout(layout_3)

        layout_0 = QHBoxLayout()
        layout_0.addLayout(layout)
        label_desc = BodyLabel('算法描述：\nxxx')
        label_desc.setStyleSheet('border: 1px solid rgba(0, 0, 0, 15);')
        label_desc.setFixedWidth(150)
        label_desc.setAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignTop)
        layout_0.addWidget(label_desc)

        self.setLayout(layout_0)
        self.resize(700, 500)

    def run(self):
        executable = './fake.exe'
        file_func = 'xxx.txt'
        cmd = f'"{executable}" "{file_func}"'
        thread = Thread(cmd, self)
        thread.on_progress.connect(lambda value: self.progress_bar.setValue(value))
        thread.on_message.connect(lambda value: self.label.setText(value))
        thread.on_finished.connect(self.show_ret)
        thread.start()
        # return thread, file_out

    def show_ret(self, success):
        print('sen_res_Global', self.show_label, success)
        if success:
            # print(os.path.exists('./sen_res_Global.png'))
            # img = QtGui.QPixmap('./d71516bf5da3224ac9b128ea1dafeda6.png') #.\
                # scaled(640, 480, aspectMode=QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                #        mode=QtCore.Qt.TransformationMode.SmoothTransformation)
            # print(img)
            # self.show_label.setPixmap('./d71516bf5da3224ac9b128ea1dafeda6.jpeg')
            # self.show_label.setText('XXX')
            # .setScaledContents(True)
            # self.show_label.setPixmap(QPixmap('d71516bf5da3224ac9b128ea1dafeda6.jpeg').scaled(700, 600))
            self.show_label.setPixmap(QPixmap('sen_res.png').scaled(700, 600))


class Frame(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 8, 0, 0)

        self.setObjectName('frame')
        # StyleSheet.VIEW_INTERFACE.apply(self)
        self.setStyleSheet('''
        #frame {
    border: 1px solid rgba(0, 0, 0, 15);
    border-radius: 5px;
    background-color: transparent;
}''')

    def addWidget(self, widget):
        self.hBoxLayout.addWidget(widget)

class TreeFrame(Frame):

    def __init__(self, data, label, parent=None, enableCheck=False):
        super().__init__(parent)
        self.tree = TreeWidget(self)
        self.addWidget(self.tree)
        self.add_data(data)
        self.tree.expandAll()
        self.tree.setHeaderHidden(True)
        self.show_label = label

        # self.tree.currentItemChanged.connect(self.func_changed)
        self.tree.itemDoubleClicked.connect(self.func_changed)

    def func_changed(self, item, _):
        print(item, _, getattr(item, '__custom_data', None))
        if __custom_data := getattr(item, '__custom_data', None):
            FuncDialog(__custom_data, self.show_label, self).exec()
        # if (count := getattr(item, 'bind_count', -1)) >= 0:
        #     self.stack.setCurrentIndex(count)

        # self.setFixedSize(300, 380)

        # if enableCheck:
        #     it = QTreeWidgetItemIterator(self.tree)
        #     while(it.value()):
        #         it.value().setCheckState(0, Qt.Unchecked)
        #         it += 1

    def add_data(self, data):
        def fn(data_, parent_=None):
            if isinstance(data_, (list, tuple)):
                print(data_)
                for key, idx in data_:
                    item = QTreeWidgetItem([self.tr(key)])
                    setattr(item, '__custom_data', idx)
                    parent_.addChild(item)
            else:
                for key, values in data_.items():
                    item = QTreeWidgetItem([self.tr(key)])
                    if parent_ is None:
                        self.tree.addTopLevelItem(item)
                    else:
                        parent_.addChild(item)
                    fn(values, item)
        fn(data)



class SampleCard(CardWidget):
    """ Sample card """

    def __init__(self, icon, title, content, routeKey, index, parent=None):
        super().__init__(parent=parent)
        self.index = index
        self.routekey = routeKey

        self.iconWidget = IconWidget(icon, self)
        # self.titleLabel = QLabel(title, self)
        self.titleLabel = QLabel(TextWrap.wrap(title, 45, False)[0], self)
        self.titleLabel.setStyleSheet("QLabel{color:black;font:24pt;background-color:rgb(0,0,0,0);}")

        # self.contentLabel = QLabel(TextWrap.wrap(content, 45, False)[0], self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedSize(360, 90)
        self.iconWidget.setFixedSize(48, 48)

        self.hBoxLayout.setSpacing(28)
        self.hBoxLayout.setContentsMargins(20, 0, 0, 0)
        self.vBoxLayout.setSpacing(2)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)

        self.hBoxLayout.setAlignment(Qt.AlignVCenter)
        self.hBoxLayout.addWidget(self.iconWidget)
        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.titleLabel)
        # self.vBoxLayout.addWidget(self.contentLabel)
        self.vBoxLayout.addStretch(1)

        self.titleLabel.setObjectName('titleLabel')
        # self.contentLabel.setObjectName('contentLabel')


class SubModule(QWidget):
    def __init__(self, parent=None):
        super(SubModule, self).__init__(parent)
        self.commandBar = CommandBar(self)
        self.commandBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        # self.commandBar.addAction(Action(FluentIcon.FOLDER, '文件', triggered=self.onEdit))
        self.commandBar.addWidget(self.createDropDownButton())
        self.commandBar.addSeparator()
        self.commandBar.addWidget(self.createDropDownButton2())
        # self.commandBar.addAction(Action(FluentIcon.DEVELOPER_TOOLS, '功能', triggered=self.onEdit))
        self.commandBar.addSeparator()
        self.commandBar.addAction(Action(FluentIcon.QUESTION, '帮助', triggered=self.onEdit))
        self.commandBar.addSeparator()
        self.commandBar.addAction(Action(FluentIcon.PHONE, '联系我们', triggered=self.onEdit))
        v = QVBoxLayout()
        self.setLayout(v)

        h2 = QHBoxLayout()
        h2.addWidget(lw:=ListWidget())
        # self.
        # help(self.addDockWidget)
        # for i in range(100):
        #     lw.addItem(f'{i + 1}')
        lw.setStyleSheet('border:1px solid #aaaaaa;font:24pt')
        lw.setMaximumWidth(200)
        lw.itemActivated.connect(lambda *args: print(args))
        # lw.itemDoubleClicked.connect(lambda *args: print(args))
        h2.addWidget(label:=QLabel())
        # label.setStyleSheet('border:1px solid #aaaaaa;background-color:#eeeeee')
        h2.addWidget(tw:=QTabWidget())
        tw.setTabShape(PySide6.QtWidgets.QTabWidget.TabShape.Triangular)
        # setFont(tw, 14)
        print(dir(PySide6.QtWidgets.QTabWidget.TabShape))
        self.show_label = label
        self.show_label.setAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignCenter)
        # self.show_label.resize(1000, H-32)
        # self.show_label.setScaledContents(True)
        # self.show_label.setC
        # self.show_label.setPixmap(QPixmap('d71516bf5da3224ac9b128ea1dafeda6.jpeg').scaled(700, 600))

        # tw.setTab
        data = {
            '模拟仿真': [('全球尺度', '全球尺度'), ('区域尺度', '区域尺度'), ('点尺度', '点尺度'), ('模拟数据库构建', '模拟数据库构建')],
            '模拟验证': [('时间序列验证', '时间序列验证'), ('空间尺度验证', '空间尺度验证')],
            '敏感性分析': [('全局敏感性分析', '全局敏感性分析'), ('局部敏感性分析', '局部敏感性分析')],
            '载荷指标论证': [('灵敏度指标', '灵敏度指标'), ('稳定度与定标精度', '稳定度与定标精度')],
        }
        tw.addTab(TreeFrame(data, label), '积雪')
        tw.addTab(TreeFrame(data, label), '土壤')
        tw.addTab(TreeFrame(data, label), '冻土')
        tw.addTab(TreeFrame(data, label), '极地冰盖')
        tw.addTab(TreeFrame(data, label), '冰川')
        # p = PySide6.QtWidgets.QSizePolicy(PySide6.QtWidgets.QSizePolicy.Minimum, PySide6.QtWidgets.QSizePolicy.Minimum)
        # print(PySide6.QtWidgets.QSizePolicy.Minimum)
        # tw.setSizePolicy(p)
        # tw.setTabMinimumWidth(10)
        # tw.addTab('1', '积雪')
        # tw.addTab('2', '土壤')
        # tw.addTab('3', '冻土')
        # tw.addTab('4', '极地冰盖')
        # tw.addTab('5', '冰川')
        tw.setMaximumWidth(270)
        # tw.setSizeAdjustPolicy(PySide6.QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContentsOnFirstShow)
        tw.setTabsClosable(False)
        # tw.setAddButtonVisible(False)
        # tw.ad/
        v.addWidget(self.commandBar)
        v.addLayout(h2)

    def createDropDownButton(self):
        button = TransparentDropDownPushButton('文件', self, FluentIcon.FOLDER)
        button.setFixedHeight(34)
        setFont(button, 12)

        menu = RoundMenu(parent=self)
        menu.addActions([
            Action(FluentIcon.DOCUMENT, '打开'),
            Action(FluentIcon.SAVE, '保存'),
            # Action(FluentIcon.PASTE, 'Paste'),
            # Action(FluentIcon.CANCEL, 'Cancel'),
            # Action('Select all'),
        ])
        button.setMenu(menu)
        return button

    def createDropDownButton2(self):
        button = TransparentDropDownPushButton('功能', self, FluentIcon.DEVELOPER_TOOLS)
        button.setFixedHeight(34)
        setFont(button, 12)

        menu = RoundMenu(parent=self)
        menu.addActions(actions:=[
            Action(FluentIcon.DOCUMENT, '前向模型模拟', triggered=lambda : FuncDialog('算法', self.show_label, self).exec()),
            Action(FluentIcon.DOCUMENT, '模拟验证', triggered=lambda : FuncDialog('算法', self.show_label, self).exec()),
            Action(FluentIcon.DOCUMENT, '敏感性分析', triggered=lambda : FuncDialog('算法', self.show_label, self).exec()),
            Action(FluentIcon.DOCUMENT, '载荷指标论证', triggered=lambda : FuncDialog('算法', self.show_label, self).exec()),
            # Action(FluentIcon.PASTE, 'Paste'),
            # Action(FluentIcon.CANCEL, 'Cancel'),
            # Action('Select all'),
        ])

        button.setMenu(menu)
        return button

    def onEdit(self, *args):
        print(args)

class Demo(FramelessWindow):

    def __init__(self):
        super().__init__()
        self.resize(W, H)
        self.setTitleBar(StandardTitleBar(self))
        h = self.titleBar.height()
        self.setWindowTitle('冰冻圈关键要素模型模拟与反演平台')
        self.setWindowIcon(QIcon(FluentIcon.IOT.path()))
        self.setContentsMargins(0, h, 0, 0)

        # self.commandBar = CommandBar(self)
        # self.commandBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        # self.commandBar.addAction(Action(FluentIcon.EDIT, 'Edit', triggered=self.onEdit))
        # self.commandBar.addSeparator()
        # self.commandBar.addAction(Action(FluentIcon.EDIT, 'Edit2', triggered=self.onEdit))
        # self.commandBar.addSeparator()
        # self.commandBar.addAction(Action(FluentIcon.EDIT, 'Edit3', triggered=self.onEdit))
        #
        # self.hBoxLayout = QHBoxLayout(self)
        #
        # self.hBoxLayout.addWidget(self.commandBar)


        # bg_img_path = 'D:/02/02-个人/背景图片/clouds-3840x2160-water-river-green-4k-23339.jpg'
        bg_img_path = 'bg.jpeg'
        # bg_img_path = 'd71516bf5da3224ac9b128ea1dafeda6.jpeg'
        # self.bg = PixmapLabel(self)
        # self.bg.setPixmap(QPixmap('埃罗芒阿老师.jpg').scaled(700, 600 - h, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.SmoothTransformation))
        # self.bg.move(0, h)
        self.setResizeEnabled(False)
        self.titleBar.maxBtn.setEnabled(False)

        layout = QStackedLayout()

        self.setLayout(layout)

        btn1 = SampleCard(QIcon(FluentIcon.IOT.path()), '模拟仿真子平台', 'yyy', 0, 0)
        btn2 = SampleCard(QIcon(FluentIcon.IOT.path()), '数据处理子平台', 'yyy', 0, 0)

        btn1.clicked.connect(lambda: self.switch_page(1))
        btn2.clicked.connect(lambda: self.switch_page(2))

        layout_btn = QVBoxLayout()
        layout_btn.addWidget(btn1)
        layout_btn.addWidget(btn2)
        layout_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)

        w = QWidget()
        # w.setStyleSheet(
        #     f"border-image: url({bg_img_path}) 0 0 0 0 stretch stretch;"
        #     # "background-repeat: no-repeat; "
        #     # "background-position: center; "
        #     # "background-size: 100%;"
        # # "height: 100%; width: 100%; background-size:cover; position:absolute; left:0; top:0;"
        # )

        bg = PixmapLabel(w)
        bg.setPixmap(QPixmap(bg_img_path).scaled(W, H - h, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.SmoothTransformation))

        w.setLayout(layout_btn)
        layout.addWidget(w)
        layout.addWidget(SubModule())
        # layout.addWidget(SubModule())

        # layout.addWidget(QLabel('xxx'))
        w2 = QWidget()
        la = FlowLayout(needAni=False, isTight=False)
        # la = QVBoxLayout()
        w2.setLayout(la)
        layout.addWidget(w2)
        # la.addWidget(QLabel('yyy'))
        for x in FluentIcon:
            btn = ToolButton(x)
            btn.clicked.connect(lambda *, _=x: print(_))
            la.addWidget(btn)


    def switch_page(self, idx):
        if idx == 0:
            # self.bg.hide()
            self.resize(W, H)
            self.setResizeEnabled(False)
            self.titleBar.maxBtn.setEnabled(False)
        else:

            # self.bg.show()
            self.setResizeEnabled(True)
            self.titleBar.maxBtn.setEnabled(True)
        self.layout().setCurrentIndex(idx)


if __name__ == '__main__':

    W = 1100
    H = 700

    # QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    main_win = Demo()
    main_win.show()
    app.exec()