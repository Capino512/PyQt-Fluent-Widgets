# coding:utf-8
import json
import os
import sys
import time
from datetime import datetime
from contextlib import contextmanager
import PySide6
import subprocess
from PySide6.QtCore import Qt, QEventLoop, QTimer, QSize
from PySide6 import QtCore, QtGui
from PySide6.QtGui import QIcon, QPixmap, QFontDatabase
from PySide6.QtWidgets import QApplication, QLabel, QHBoxLayout, QVBoxLayout, QStackedLayout, QWidget, QTabWidget, \
    QTabBar, QTreeWidgetItem, QFrame, QDialog, QLineEdit, QPushButton, QFormLayout, QFileDialog

from qfluentwidgets import SplashScreen, PixmapLabel, ImageLabel, CardWidget, IconWidget, TextWrap, FluentIcon, \
    ToolButton, FlowLayout, CommandBar, CommandBarView, Action, ListWidget, TreeView, TabBar, TreeWidget, ProgressBar, \
    IndeterminateProgressBar, PushButton, LineEdit, TransparentDropDownPushButton, setFont, RoundMenu, BodyLabel, \
    ComboBox, Dialog, MessageBox

from qframelesswindow import FramelessWindow, StandardTitleBar
from src.config import modules, get_function, walk
from PIL import Image
# import locale
# locale.setlocale(locale.LC_CTYPE,"chinese")


class Thread(QtCore.QThread):
    on_finished = QtCore.Signal(bool)
    on_progress = QtCore.Signal(int)
    on_message = QtCore.Signal(str)

    def __init__(self, cmd, cwd=None, parent=None):
        super(Thread, self).__init__(parent)
        self.cmd = cmd
        self.cwd = cwd
        self.process = None
        self.cancel = None

    def force_stop(self):
        self.process.kill()
        self.cancel = True

    def run(self):
        self.cancel = False
        # print(self.cmd)
        process = subprocess.Popen(self.cmd, cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        self.process = process
        while (code := process.poll()) is None:

            # try:
            #     line = line.decode("utf-8").strip()
            # except:
            #     continue
                # try:
                #     line = (line.decode("gbk").strip())
                #     print('gbk', line)
                # except:
                #     continue
            # line = process.stdout.readline().strip()
            try:
                line = process.stdout.readline().strip()
                # print(line)
            except:
                continue
            if line:
                print(line)
                if line.startswith('[Progress]'):
                    self.on_progress.emit(float(line.removeprefix('[Progress]').strip()))
                for s in ['[Info]', '[Warning]', '[Error]']:
                    if line.startswith(s):
                        self.on_message.emit(line.removeprefix(s).strip())
        success = code == 0 and not self.cancel
        self.on_finished.emit(success)


@contextmanager
def hbox_layout(parent=None):
    layout = QHBoxLayout(parent)
    yield layout


@contextmanager
def vbox_layout(parent=None):
    layout = QVBoxLayout(parent)
    yield layout


class Algo:
    def __init__(self, config):
        self.name = config['name']
        self.description = config['description']
        self.work_dir = config['work_dir']
        self.executable = config['executable']
        self.outputs = config['outputs']


class FunctionDialog(QDialog):
    on_show_result = QtCore.Signal(list)
    def __init__(self, config, parent=None):
        super(FunctionDialog, self).__init__(parent)
        self.setWindowTitle(config['name'])
        algorithms = [Algo(algo) for algo in config['algorithms']]
        self.algorithms = algorithms

        combo_box = ComboBox()
        combo_box.currentIndexChanged.connect(self.on_select_algo)
        for algo in algorithms:
            combo_box.addItem(algo.name, userData=algo)

        form = QFormLayout()
        form.addRow(BodyLabel('算法：'), combo_box)

        self.input_param = LineEdit()
        # self.input_param.setText(r'D:\03\python\04\PyQt-Fluent-Widgets\dev\2023-10-30_15-55-35_算法1.txt')
        self.output_params = []
        with hbox_layout() as layout:
            layout.addWidget(self.input_param )
            layout.addWidget(btn:=PushButton(f'选择'))
            btn.clicked.connect(lambda: self.on_select_file(self.input_param, '*.txt'))
            form.addRow(BodyLabel('输入参数 (*.txt)：'), layout)

        self.form = form
        self.algo = algorithms[0]
        desc_label = BodyLabel()
        desc_label.setStyleSheet('border: 1px solid rgba(0, 0, 0, 15);')
        desc_label.setFixedWidth(160)
        desc_label.setAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignTop)
        desc_label.setWordWrap(True)
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

    def on_select_file(self, target, filters, save=False):
        global CURRENT_DIR
        f, _ = (QFileDialog.getSaveFileName if save else QFileDialog.getOpenFileName)(self, '选择文件', CURRENT_DIR, filters)
        if f:
            target.setText(f)
            CURRENT_DIR = os.path.dirname(f)

    def on_select_algo(self, index=None):
        self.input_param.clear()
        self.input_param.setText('D:/03/python/04/PyQt-Fluent-Widgets/dev/module_2/01_模拟仿真子平台/01_敏感性分析/01_局部敏感性分析/01_角度/01_局部敏感性分析（入射角）/angle_input.txt')
        if index is not None:
            self.algo = self.algorithms[index]

        form = self.form
        for i in range(2, form.count()):
            form.removeRow(2)
        self.output_params.clear()

        algo = self.algo
        for _name, postfix, flag in algo.outputs:
            with hbox_layout() as layout:
                layout.addWidget(param := LineEdit())
                param.setText('D:/03/python/04/PyQt-Fluent-Widgets/dev/module_2/01_模拟仿真子平台/01_敏感性分析/01_局部敏感性分析/01_角度/01_局部敏感性分析（入射角）/out.png')
                layout.addWidget(btn:=PushButton(f'选择'))
                btn.clicked.connect(lambda *, _param=param, _postfix=postfix: self.on_select_file(_param, f'*{_postfix}', True))
                form.addRow(BodyLabel(f'{_name} (*{postfix})：'), layout)
                self.output_params.append([_name, param])

        self.desc_label.setText("<p style='line-height:24px;white-space:pre-wrap'>%s</p>" % f'<strong>算法描述</strong>\n{algo.description}')

    def check_params(self):
        return all([param.text() for param in ([self.input_param] + [x[1] for x in self.output_params])])

    def make_param_file(self):
        path = os.path.join(SAVE_DIR, datetime.now().strftime(f'%Y-%m-%d_%H-%M-%S_{self.algo.name}.txt'))
        with open(path, 'wt', encoding='utf-8') as f:
            f.write('\n'.join([f'{name}：{param.text()}' for name, param in self.output_params]))
        return path

    def on_run(self):
        if self.check_params() is False:
            return

        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.progress_label.setText('开始执行...')
        algo = self.algo

        cmd = f'"{algo.executable}" "{self.input_param.text()}" "{self.make_param_file()}"'
        thread = Thread(cmd, self.algo.work_dir, self)
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
            self.progress_bar.setValue(100)
            self.progress_label.setText('执行成功')
            ret = []
            for i, (_, param) in enumerate(self.output_params):
                ret.append([param.text(), *self.algo.outputs[i]])

            # with open(os.path.splitext(self.input_param.text())[0] + '.pro', 'wt', encoding='utf-8') as f:
            #     json.dump(ret, f, ensure_ascii=False)

            self.on_show_result.emit(ret)
        else:
            self.progress_bar.setValue(0)
            self.progress_label.setText('执行失败')
        self.close()


class Frame(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 8, 0, 0)
        self.setObjectName('frame')
        self.setStyleSheet('''
        #frame { border: 1px solid rgba(0, 0, 0, 15); 
        border-radius: 5px; 
        background-color: transparent;
        }''')

    def addWidget(self, widget):
        self.hBoxLayout.addWidget(widget)


class TreeFrame(Frame):
    on_run = QtCore.Signal(dict)

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.tree = TreeWidget(self)
        self.addWidget(self.tree)
        self.add_data(data)
        self.tree.expandAll()
        self.tree.setHeaderHidden(True)
        self.tree.itemDoubleClicked.connect(self.on_double_click)

    def on_double_click(self, item, _):
        if __custom_data := getattr(item, '__custom_data', None):
            self.on_run.emit(__custom_data)

    def add_data(self, data):
        def fn(data_, parent_=None):
            for value in data_:
                if len(value['algorithms']) > 0:
                    item = QTreeWidgetItem([self.tr(value['name'])])
                    setattr(item, '__custom_data', value)
                    if parent_ is None:
                        self.tree.addTopLevelItem(item)
                    else:
                        parent_.addChild(item)
                else:
                    item = QTreeWidgetItem([self.tr(value['name'])])
                    if parent_ is None:
                        self.tree.addTopLevelItem(item)
                    else:
                        parent_.addChild(item)
                    fn(value['functions'], item)
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
    def __init__(self, config, parent=None):
        super(SubModule, self).__init__(parent)
        self.commandBar = CommandBar(self)
        self.commandBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.commandBar.addWidget(self.createDropDownButton())
        self.commandBar.addSeparator()
        self.commandBar.addWidget(self.createDropDownButton2())
        self.commandBar.addSeparator()
        self.commandBar.addAction(Action(FluentIcon.QUESTION, '帮助', triggered=lambda: os.startfile(r'.\resource\使用手册.pdf')))
        self.commandBar.addSeparator()
        self.commandBar.addAction(Action(FluentIcon.PHONE, '联系我们', triggered=self.on_show_contact))
        v_layout = QVBoxLayout()
        self.setLayout(v_layout)

        h_layout = QHBoxLayout()
        h_layout.addWidget(file_list := ListWidget())
        # file_list.setStyleSheet('border: 1px solid rgba(0, 0, 0, 15);font:24pt')
        file_list.setStyleSheet('border: 1px solid rgba(0, 0, 0, 15)')
        file_list.setMinimumWidth(240)
        file_list.setMaximumWidth(270)
        # file_list.addItem('xxx')
        # file_list.addItem('yyy')
        # file_list.setFixedWidth(240)
        # file_list.itemActivated.connect(self.on_show_select)
        file_list.itemSelectionChanged.connect(self.on_show_select)
        self.file_list = file_list
        h_layout.addWidget(display_area := QLabel())
        display_area.setStyleSheet('border: 1px solid rgba(0, 0, 0, 15);background-color:#eeeeee')
        h_layout.addWidget(tool_box:=QTabWidget())
        setFont(tool_box, 14)
        tool_box.setTabShape(PySide6.QtWidgets.QTabWidget.TabShape.Triangular)
        self.display_area = display_area

        for sub_module in config:
            tree = TreeFrame(sub_module['functions'])
            tree.on_run.connect(self.on_run_function)
            tool_box.addTab(tree, sub_module['name'])
        tool_box.setMinimumWidth(240)
        tool_box.setMaximumWidth(270)
        tool_box.setTabsClosable(False)
        v_layout.addWidget(self.commandBar)
        v_layout.addLayout(h_layout)

        self.files = []

    def on_run_function(self, data):
        # print(data)
        dialog = FunctionDialog(data, self)
        dialog.on_show_result.connect(self.show_result)
        dialog.exec()

    def show_result(self, data):
        count = 0
        # print(data)

        for path, name, postfix, flag in data:
            if flag:
                self.files.append(path)
                self.file_list.addItem(os.path.basename(path))
                if count == 0:
                    self.file_list.setCurrentRow(self.file_list.count() - 1)
                    self.display(path)
                count += 1


    def display(self, path: str):
        if path.endswith('.txt'):
            self.display_area.setAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignTop | PySide6.QtCore.Qt.AlignmentFlag.AlignLeft)
            self.display_area.setText(open(path).read())
        else:
            max_w, max_h = 800, 600
            img = Image.open(path)
            w = img.width
            h = img.height
            if w > max_w or h > max_h:
                if w / max_w > h / max_h:
                    k = w / max_w
                    w = max_w
                    h = int(h / k)
                else:
                    k = h / max_h
                    h = max_h
                    w = int(w / k)
                img = img.resize([w, h], resample=Image.Resampling.BICUBIC)
            self.display_area.setAlignment(PySide6.QtCore.Qt.AlignmentFlag.AlignCenter)
            self.display_area.setPixmap(img.toqpixmap())

    def createDropDownButton(self):
        button = TransparentDropDownPushButton('文件', self, FluentIcon.FOLDER)
        button.setFixedHeight(34)
        setFont(button, 12)

        menu = RoundMenu(parent=self)
        menu.addActions([
            Action(FluentIcon.DOCUMENT, '打开'),
            Action(FluentIcon.SAVE, '保存'),
        ])

        button.setMenu(menu)
        return button

    def createDropDownButton2(self):
        button = TransparentDropDownPushButton('功能', self, FluentIcon.DEVELOPER_TOOLS)
        button.setFixedHeight(34)
        setFont(button, 12)

        menu = RoundMenu(parent=self)

        data = [
            ['局部敏感性分析-角度', ['模拟仿真子平台', '敏感性分析', '局部敏感性分析', '角度']],
            # ['全局敏感性分析', ['模拟仿真子平台', '敏感性分析', '全局敏感性分析']],
            ['模拟验证-地面验证', ['模拟仿真子平台', '模拟验证', '地面尺度验证']],
            # ['模拟验证-全球尺度验证', ['模拟仿真子平台', '模拟验证', '全球尺度验证']],
            ['模型模拟-点尺度', ['模拟仿真子平台', '模型模拟', '点尺度']],
            # ['模型模拟-全球模拟', ['模拟仿真子平台', '模型模拟', '全球模拟']],
            ['载荷指标论证-灵敏度指标', ['模拟仿真子平台', '载荷指标论证', '灵敏度指标']],
            # ['载荷指标论证-全球模拟', ['模拟仿真子平台', '载荷指标论证', '稳定度与定标精度指标']],
        ]
        actions = []
        for name, values in data:
            action = Action(FluentIcon.DOCUMENT, name, triggered=lambda *, _values=values: self.on_run_function(get_function(*_values)))
            actions.append(action)
        menu.addActions(actions)

        button.setMenu(menu)
        return button

    def on_show_contact(self):
        title = '联系方式'
        content = \
"""
Email: liugj@mail.bnu.edu.cn
"""
        w = Dialog(title, content, self)
        w.setTitleBarVisible(False)
        w.cancelButton.hide()
        w.exec()

    def on_show_select(self, *args):
        path = self.files[self.file_list.currentRow()]
        self.display(path)


class Demo(FramelessWindow):

    def __init__(self):
        super().__init__()
        self.resize(W, H)
        self.setTitleBar(StandardTitleBar(self))
        h = self.titleBar.height()
        self.setWindowTitle(TITLE)
        self.setWindowIcon(QIcon(FluentIcon.IOT.path()))
        self.setContentsMargins(0, h, 0, 0)
        self.setResizeEnabled(False)
        self.titleBar.maxBtn.setEnabled(False)

        layout = QStackedLayout()
        self.setLayout(layout)

        layout_btn = QVBoxLayout()
        layout_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_btn.addSpacing(240)

        widget_bg = QWidget()
        bg = PixmapLabel(widget_bg)
        bg.setPixmap(QPixmap(BG_IMG_PATH).scaled(W, H - h, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.SmoothTransformation))
        widget_bg.setLayout(layout_btn)
        layout.addWidget(widget_bg)

        for i, module in enumerate(modules):
            btn = SampleCard(QIcon(FluentIcon.IOT.path()), module['name'], '', 0, 0)
            btn.clicked.connect(lambda *, _i=i: self.switch_page(_i + 1))
            layout_btn.addWidget(btn)
            layout.addWidget(SubModule(module['sub_modules']))

    def switch_page(self, idx):
        if idx == 0:
            self.resize(W, H)
            self.setResizeEnabled(False)
            self.titleBar.maxBtn.setEnabled(False)
        else:
            self.setResizeEnabled(True)
            self.titleBar.maxBtn.setEnabled(True)
        self.layout().setCurrentIndex(idx)


if __name__ == '__main__':

    W = 1100
    H = 700
    # W = int(1920 * 0.6)
    # H = int(1080 * 0.6)


    SAVE_DIR = r"D:\01\temp\bsd"
    # SAVE_DIR = r"./"
    BG_IMG_PATH = './resource/bg.jpg'
    TITLE = '冰冻圈关键要素模型模拟与反演平台'
    CURRENT_DIR = '.'

    os.makedirs(SAVE_DIR, exist_ok=True)
    walk('./module_2')

    app = QApplication(sys.argv)
    main_win = Demo()
    main_win.show()
    # print(QFontDatabase.families())

    app.exec()
