# coding:utf-8
import os
import sys
import time
from datetime import datetime
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
        self.process = None
        self.cancel = None

    def force_stop(self):
        self.process.kill()
        self.cancel = True

    def run(self):
        self.cancel = False
        process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        self.process = process
        while (code := process.poll()) is None:
            line = process.stdout.readline().strip()
            if line:
                print(line)
                if line.startswith('[Progress]'):
                    self.on_progress.emit(int(line.removeprefix('[Progress]').strip()))
                for s in ['[Info]', '[Warning]', '[Error]']:
                    if line.startswith(s):
                        self.on_message.emit(line.removeprefix(s).strip())
        success = code == 0 and not self.cancel
        self.on_finished.emit(success)


@contextmanager
def h_layout(parent=None):
    layout = QHBoxLayout(parent)
    yield layout


@contextmanager
def hbox_layout(parent=None):
    layout = QHBoxLayout(parent)
    yield layout


@contextmanager
def vbox_layout(parent=None):
    layout = QVBoxLayout(parent)
    yield layout


def new_label(text, font=None):
    label = BodyLabel(text)
    # setFont(label, font)
    return label


class Algo:
    def __init__(self, config):
        config = dict(
            id='id',
            name='name',
            description='description',
            executable='executable',
            outputs=[('name', 'postfix', 'flag')],
        )
        self.id = config['id']
        self.name = config['name']
        self.description = config['description']
        self.executable = config['executable']
        self.outputs = config['outputs']


class FunctionDialog(QDialog):
    def __init__(self, name, algo_list, display_widget, parent=None):
        super(FunctionDialog, self).__init__(parent)
        self.setWindowTitle(name)
        self.algo_list = algo_list
        self.display_widget = display_widget

        combo_box = ComboBox()
        combo_box.currentIndexChanged.connect(self.on_select_algo)
        for algo in algo_list:
            combo_box.addItem(algo.name, userData=algo)

        form = QFormLayout()
        form.addRow(BodyLabel('算法：'), combo_box)

        self.input_param = LineEdit()
        self.output_params = []
        with hbox_layout() as layout:
            layout.addWidget(self.input_param )
            layout.addWidget(PushButton('选择'))
            form.addRow(BodyLabel('输出参数文件：', 14), layout)

        self.form = form
        self.algo = algo_list[0]
        desc_label = BodyLabel()
        desc_label.setStyleSheet('border: 1px solid rgba(0, 0, 0, 15);')
        desc_label.setFixedWidth(160)
        desc_label.setAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignTop)
        self.desc_label = desc_label
        self.on_select_algo()

        progress_label = BodyLabel()
        message_label = BodyLabel()
        message_label.setAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignRight)
        progress_bar = ProgressBar()
        progress_bar.hide()
        self.progress_label = progress_label
        self.message_label = message_label
        self.progress_bar = progress_bar

        with vbox_layout() as layout:
            layout.addLayout(form)
            with hbox_layout() as _layout:
                _layout.addWidget(progress_label)
                _layout.addWidget(message_label)

            layout.addSpacing(8)
            layout.addLayout(_layout)
            layout.addWidget(progress_bar)

            with hbox_layout() as _layout:
                _layout.addWidget(btn := PushButton('运行'))
                btn.clicked.connect(self.on_run)
                btn.setMaximumWidth(100)
                layout.addStretch(1)
                layout.addLayout(_layout)

        with hbox_layout() as main_layout:
            main_layout.addLayout(layout)
            main_layout.addWidget(desc_label)

        self.setLayout(main_layout)
        self.resize(700, 500)

    def on_select_algo(self, index=None):
        if index is not None:
            self.algo = self.algo_list[index]

        form = self.form
        for i in range(2, form.count()):
            form.removeRow(i)
        self.output_params.clear()

        algo = self.algo
        with hbox_layout() as layout:
            for _name, postfix, flag in algo['outputs']:
                layout.addWidget(param := LineEdit())
                layout.addWidget(PushButton('选择'))
                form.addRow(BodyLabel(f'{_name}：'), layout)
                self.output_params.append(param)
        self.desc_label.setText(f'算法描述：\n{algo.description}')

    def check_params(self):
        return all([param.text() for param in ([self.input_param] + self.output_params)])

    def make_param_file(self):
        path = datetime.now().strftime(f'%Y-%m-%d_%H-%M-%S_{self.algo.id}.txt')
        with open(path, 'wt') as f:
            f.write('\n'.join([param.text() for param in [self.input_param] + self.output_params]))
        return path

    def on_run(self):
        if self.check_params() is False:
            return

        self.progress_bar.setValue(0)
        self.progress_bar.show()
        algo = self.algo

        cmd = f'"{algo.executable}" "{self.make_param_file()}"'
        thread = Thread(cmd, self)
        thread.on_progress.connect(self.on_progress)
        thread.on_message.connect(self.on_message)
        thread.on_finished.connect(self.on_finished)
        thread.start()

    def on_progress(self, value):
        self.progress_bar.setValue(value)
        self.progress_label.setText('%d%%' % value)

    def on_message(self, text):
        self.message_label.setText(text)

    def on_finished(self, success):
        if success:
            self.display_widget.setPixmap(QPixmap('sen_res.png').scaled(600, 500))


# 平台 功能 算法

class FuncDialog(QDialog):
    def __init__(self, title, show_label=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.show_label = show_label

        layout = QVBoxLayout()
        layout_form = QFormLayout()
        layout.addLayout(layout_form)

        algo_list = ComboBox()
        algo_list.addItem('DMRT')
        algo_list.addItem('DMRT')
        algo_list.addItem('DMRT')

        layout_form.addRow(new_label('算法：', 14), algo_list)


        layout_1 = QHBoxLayout()
        layout_1.addWidget(LineEdit())
        layout_1.addWidget(PushButton('选择'))
        layout_form.addRow(new_label('输出参数文件：', 14), layout_1)


        layout_2 = QHBoxLayout()
        layout_2.addWidget(LineEdit())
        layout_2.addWidget(PushButton('选择'))
        layout_form.addRow(new_label('输出路径：', 14), layout_2)


        # layout_3 = QHBoxLayout()
        label_progress = BodyLabel()
        label_message = BodyLabel()
        label_message.setAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignRight)
        progress_bar = ProgressBar()
        progress_bar.hide()
        self.label_progress = label_progress
        self.label_message = label_message
        self.progress_bar = progress_bar
        # progress_bar.setValue(50)
        with h_layout() as tmp_layout:
            tmp_layout.addWidget(label_progress)
            tmp_layout.addWidget(label_message)
        layout.addSpacing(8)
        layout.addLayout(tmp_layout)
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
        label_desc = BodyLabel('算法描述：\n描述内容...')
        label_desc.setStyleSheet('border: 1px solid rgba(0, 0, 0, 15);')
        label_desc.setFixedWidth(160)
        label_desc.setAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignTop)
        layout_0.addWidget(label_desc)

        self.setLayout(layout_0)
        self.resize(700, 500)

    def run(self):
        executable = './module/fake.exe'
        file_func = 'xxx.txt'
        cmd = f'"{executable}" "{file_func}"'
        thread = Thread(cmd, self)
        thread.on_progress.connect(self.on_progress)
        thread.on_message.connect(lambda value: self.label_message.setText(value))
        thread.on_finished.connect(self.show_ret)
        thread.start()
        # return thread, file_out

    def on_progress(self, value):
        self.progress_bar.setValue(value)
        self.label_progress.setText('%d%%' % value)

    def show_ret(self, success):
        if success:
            self.show_label.setPixmap(QPixmap('sen_res.png').scaled(600, 500))


class Frame(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 8, 0, 0)

        self.setObjectName('frame')
        # StyleSheet.VIEW_INTERFACE.apply(self)
        self.setStyleSheet('''
        #frame { border: 1px solid rgba(0, 0, 0, 15); 
        border-radius: 5px; 
        background-color: transparent;
        }''')

    def addWidget(self, widget):
        self.hBoxLayout.addWidget(widget)


class TreeFrame(Frame):

    def __init__(self, data, label, parent=None):
        super().__init__(parent)
        self.tree = TreeWidget(self)
        self.addWidget(self.tree)
        self.add_data(data)
        self.tree.expandAll()
        self.tree.setHeaderHidden(True)
        self.show_label = label
        self.tree.itemDoubleClicked.connect(self.func_changed)

    def func_changed(self, item, _):
        if __custom_data := getattr(item, '__custom_data', None):
            FuncDialog(__custom_data, self.show_label, self).exec()

    def add_data(self, data):
        def fn(data_, parent_=None):
            if isinstance(data_, (list, tuple)):
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


[
    dict(
        name='模拟仿真子平台',
        funcs=[
            dict(
                name='模拟仿真',
                funcs=[
                    dict(
                        name='全球尺度',
                        algos=[
                            dict(
                                id='id',
                                name='name',
                                description='description',
                                executable='executable',
                                outputs=[('name', 'postfix', 'flag')],
                            )
                        ] * 3,
                    )
                ] * 3,
            )
        ] * 2,
    )
]


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
        lw.setStyleSheet('border: 1px solid rgba(0, 0, 0, 15);font:24pt')
        lw.setMaximumWidth(200)
        lw.itemActivated.connect(lambda *args: print(args))
        # lw.itemDoubleClicked.connect(lambda *args: print(args))
        h2.addWidget(label:=QLabel())
        label.setStyleSheet('border: 1px solid rgba(0, 0, 0, 15);background-color:#eeeeee')
        h2.addWidget(tw:=QTabWidget())
        tw.setTabShape(PySide6.QtWidgets.QTabWidget.TabShape.Triangular)
        # setFont(tw, 14)
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
        bg_img_path = './resource/bg.jpeg'
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