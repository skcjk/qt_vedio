from qfluentwidgets import (PushSettingCard, ComboBoxSettingCard, SwitchSettingCard, SettingCard, 
                            OptionsConfigItem, TextEdit, DoubleSpinBox, OptionsValidator, InfoBar,
                            InfoBarPosition)
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QSpacerItem, QSizePolicy, 
                             QHBoxLayout)
from PyQt6.QtSerialPort import QSerialPortInfo

from common.config import cfg, qconfig
from SerialThread import serialThread
from qfluentwidgets import FluentIcon as FIF
from PyQt6.QtGui import QIcon
from typing import Union
from common.icon import FluentIconBase
from PyQt6.QtCore import Qt, pyqtSignal

def refreshSerialPort():

    cfg.availablPorts = QSerialPortInfo.availablePorts()
    portList = sorted([port.portName() for port in cfg.availablPorts if port.portName().startswith('COM') and port.portName()[3:].isdigit()], key=lambda x: int(x[3:]))
    if len(portList) == 0:
         portList =  [""]
    if portList != cfg.portList:
        cfg.portList = portList
        cfg.port = OptionsConfigItem("Serial", "COM", portList[0], OptionsValidator(cfg.portList))
        return True
    else:
        return False

class DoubleSpinBoxSettingCard(SettingCard):
    """ Setting card with a DoubleSpin box """

    valueChanged = pyqtSignal(int)

    def __init__(self, configItem, icon: Union[str, QIcon, FluentIconBase], title, content=None,  decimals=1, width=200, parent=None):
        super().__init__(icon, title, content, parent)
        self.configItem = configItem
        self.doubleSpinBox = DoubleSpinBox(self)

        self.doubleSpinBox.setRange(*configItem.range)
        self.doubleSpinBox.setValue(configItem.value)
        self.doubleSpinBox.setDecimals(decimals)
        self.doubleSpinBox.setFixedWidth(width)
        self.doubleSpinBox.setFixedHeight(26)
        self.setFixedHeight(40)
        self.titleLabel.setFixedWidth(100)

        self.hBoxLayout.addWidget(self.doubleSpinBox, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(8)

        configItem.valueChanged.connect(self.setValue)
        self.doubleSpinBox.valueChanged.connect(self.__onValueChanged)

    def __onValueChanged(self, value: int):
        """ doubleSpinBox value changed slot """
        self.setValue(value)
        self.valueChanged.emit(value)

    def setValue(self, value):
        qconfig.set(self.configItem, value)
        self.doubleSpinBox.setValue(value)

class MainWindowInterface(QFrame):
    def __init__(self, parent=None):
            super().__init__(parent=parent)
            self.setObjectName("mainWindowInterface")

            # 创建主布局
            mainLayout = QVBoxLayout(self)

            self.glideTimeCard = DoubleSpinBoxSettingCard(
                configItem=cfg.glideTimeCard,
                icon=FIF.MORE,
                title='滑翔次数',
                content='',
                decimals=0, 
                width=150,
                parent=self
            )
            self.cmdCard = DoubleSpinBoxSettingCard(
                configItem=cfg.cmdCard,
                icon=FIF.CHAT,
                title='命令(1-8)',
                content='',
                decimals=0, 
                width=150,
                parent=self
            )
            self.sliderDownCard = DoubleSpinBoxSettingCard(
                configItem=cfg.sliderDownCard,
                icon=FIF.DOWN,
                title='滑块下潜位置',
                content='',
                decimals=0, 
                width=150,
                parent=self
            )
            self.sliderUpCard = DoubleSpinBoxSettingCard(
                configItem=cfg.sliderUpCard,
                icon=FIF.UP,
                title='滑块上浮位置',
                content='',
                decimals=0, 
                width=150,
                parent=self
            )
            self.sliderSpeedCard = DoubleSpinBoxSettingCard(
                configItem=cfg.sliderSpeedCard,
                icon=FIF.SPEED_MEDIUM,
                title='滑块移动速度',
                content='',
                decimals=0, 
                width=150,
                parent=self
            )
            self.oilDownCard = DoubleSpinBoxSettingCard(
                configItem=cfg.oilDownCard,
                icon=FIF.DOWN,
                title='油缸下潜',
                content='',
                decimals=0, 
                width=150,
                parent=self
            )
            self.oilUpCard = DoubleSpinBoxSettingCard(
                configItem=cfg.oilUpCard,
                icon=FIF.UP,
                title='油缸上浮',
                content='',
                decimals=0, 
                width=150,
                parent=self
            )
            self.sliderAngelCard = DoubleSpinBoxSettingCard(
                configItem=cfg.sliderAngelCard,
                icon=FIF.SYNC,
                title='滑块旋转角度',
                content='',
                decimals=0, 
                width=150,
                parent=self
            )
            self.timeIntervalCard = DoubleSpinBoxSettingCard(
                configItem=cfg.timeIntervalCard,
                icon=FIF.STOP_WATCH,
                title='时间间隔',
                content='',
                decimals=0, 
                width=150,
                parent=self
            )
            self.throwDepthCard = DoubleSpinBoxSettingCard(
                configItem=cfg.throwDepthCard,
                icon=FIF.BACKGROUND_FILL    ,
                title='抛载深度',
                content='',
                decimals=0, 
                width=150,
                parent=self
            )

            self.serialSwitchCard = SwitchSettingCard(
                FIF.PLAY,
                self.tr('打开串口'),
                self.tr(''),
                parent=self
            )
            self.serialSwitchCard.setFixedWidth(250)
            self.COMCard = ComboBoxSettingCard(
                cfg.port,
                FIF.CONNECT,
                self.tr('串口号'),
                self.tr(''),
                texts=cfg.portList,
                parent=self
            )
            self.COMCard.setFixedWidth(250)
            self.baudrateCard = ComboBoxSettingCard(
                cfg.baudrate,
                FIF.SPEED_MEDIUM,
                self.tr('波特率'),
                self.tr(''),
                texts=['4800', '9600', '14400', '19200', '38400', '43000', '57600', '76800', '115200'],
                parent=self
            )
            self.baudrateCard.setFixedWidth(250)
            self.setCard = PushSettingCard(
                self.tr('设置'),
                FIF.SETTING,
                self.tr("设置"),
                None,
                self
            )
            self.setCard.setFixedWidth(250)

            self.textEdit = TextEdit()
            self.textEdit.setReadOnly(True)

            # 创建上部的垂直布局
            topLayout = QHBoxLayout()
            mainLayout.addLayout(topLayout, 3) 

            # 创建上部左侧和右侧布局
            topLeftLayout = QVBoxLayout()
            topMidLayout = QVBoxLayout()
            topRightLayout = QVBoxLayout()
            topLayout.addLayout(topLeftLayout, 3)
            topLayout.addLayout(topMidLayout, 3) 
            topLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)) 
            topLayout.addLayout(topRightLayout, 2)  

            # 创建下部的水平布局
            bottomLayout = QHBoxLayout()
            mainLayout.addLayout(bottomLayout, 2)  

            # 在布局中添加控件
            topLeftLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
            topLeftLayout.addWidget(self.glideTimeCard, 0, Qt.AlignmentFlag.AlignCenter)
            topLeftLayout.addSpacing(5)
            topLeftLayout.addWidget(self.cmdCard, 0, Qt.AlignmentFlag.AlignCenter)
            topLeftLayout.addSpacing(5)
            topLeftLayout.addWidget(self.sliderDownCard, 0, Qt.AlignmentFlag.AlignCenter)
            topLeftLayout.addSpacing(5)
            topLeftLayout.addWidget(self.sliderUpCard, 0, Qt.AlignmentFlag.AlignCenter)
            topLeftLayout.addSpacing(5)
            topLeftLayout.addWidget(self.sliderSpeedCard, 0, Qt.AlignmentFlag.AlignCenter)
            topLeftLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
            topMidLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
            topMidLayout.addWidget(self.oilDownCard, 0, Qt.AlignmentFlag.AlignCenter)
            topMidLayout.addSpacing(5)
            topMidLayout.addWidget(self.oilUpCard, 0, Qt.AlignmentFlag.AlignCenter)
            topMidLayout.addSpacing(5)
            topMidLayout.addWidget(self.sliderAngelCard, 0, Qt.AlignmentFlag.AlignCenter)
            topMidLayout.addSpacing(5)
            topMidLayout.addWidget(self.timeIntervalCard, 0, Qt.AlignmentFlag.AlignCenter)
            topMidLayout.addSpacing(5)
            topMidLayout.addWidget(self.throwDepthCard, 0, Qt.AlignmentFlag.AlignCenter)
            topMidLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
            topRightLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
            topRightLayout.addWidget(self.serialSwitchCard, 0, Qt.AlignmentFlag.AlignCenter)
            topRightLayout.addSpacing(5)
            topRightLayout.addWidget(self.COMCard, 0, Qt.AlignmentFlag.AlignCenter)
            topRightLayout.addSpacing(5)
            topRightLayout.addWidget(self.baudrateCard, 0, Qt.AlignmentFlag.AlignCenter)
            topRightLayout.addSpacing(5)
            topRightLayout.addWidget(self.setCard, 0, Qt.AlignmentFlag.AlignCenter)
            topRightLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
            bottomLayout.addWidget(self.textEdit)

            self.setLayout(mainLayout)

            self.__connectSignalToSlot()

    def __connectSignalToSlot(self):
            self.serialSwitchCard.checkedChanged.connect(lambda checked: self.startStopSerialThread(checked))
            self.COMCard.comboBox.clicked.connect(self.__refreshSerialPort)
            serialThread.errorMessage.connect(self.__createCOMErrorInfoBar)
            serialThread.successMessage.connect(self.__createCOMSuccessInfoBar)
            serialThread.dataReceived.connect(self.__receivedData)

            self.glideTimeCard.doubleSpinBox.editingFinished.connect(lambda: self.__sendData('glideTime', cfg.glideTimeCard.value))
            self.cmdCard.doubleSpinBox.editingFinished.connect(lambda: self.__sendData('cmd', cfg.cmdCard.value))
            self.sliderDownCard.doubleSpinBox.editingFinished.connect(lambda: self.__sendData('sliderDown', cfg.sliderDownCard.value))
            self.sliderUpCard.doubleSpinBox.editingFinished.connect(lambda: self.__sendData('sliderUp', cfg.sliderUpCard.value))
            self.sliderSpeedCard.doubleSpinBox.editingFinished.connect(lambda: self.__sendData('sliderSpeedCard', cfg.sliderSpeedCard.value))
            self.oilDownCard.doubleSpinBox.editingFinished.connect(lambda: self.__sendData('oilDown', cfg.oilDownCard.value))
            self.oilUpCard.doubleSpinBox.editingFinished.connect(lambda: self.__sendData('oilUp', cfg.oilUpCard.value))
            self.sliderAngelCard.doubleSpinBox.editingFinished.connect(lambda: self.__sendData('sliderAngelCard', cfg.sliderAngelCard.value))
            self.timeIntervalCard.doubleSpinBox.editingFinished.connect(lambda: self.__sendData('timeIntervalCard', cfg.timeIntervalCard.value))
            self.throwDepthCard.doubleSpinBox.editingFinished.connect(lambda: self.__sendData('throwDepthCard', cfg.throwDepthCard.value))

    def startStopSerialThread(self, checked):

        if checked == True:
            serialThread.port = self.COMCard.comboBox.currentText()
            serialThread.baudrate = self.baudrateCard.comboBox.currentText()
            serialThread.start()
        else:
            try:
                serialThread.serial.reset_input_buffer()
            except:
                pass
            serialThread.stop()
            self.COMCard.comboBox.setEnabled(True)
            self.baudrateCard.comboBox.setEnabled(True)

    def __refreshSerialPort(self):

        if refreshSerialPort():
            self.COMCard.configItem=cfg.port
            self.COMCard.comboBox.clear()

            self.COMCard.optionToText={o: t for o, t in zip(self.COMCard.configItem.options, cfg.portList)}
            for text, option in zip(cfg.portList, self.COMCard.configItem.options):
                self.COMCard.comboBox.addItem(text, userData=option)

            self.COMCard.comboBox.setCurrentText(self.COMCard.optionToText[cfg.get(cfg.port)])
            self.COMCard.comboBox.currentIndexChanged.connect(self.COMCard._onCurrentIndexChanged)
            self.COMCard.configItem.valueChanged.connect(self.COMCard.setValue)

    def __createCOMErrorInfoBar(self, errorStr):

        if errorStr[0] == '0':
            errorStr = errorStr[1:]
        else:
            self.serialSwitchCard.switchButton.setChecked(False)
        InfoBar.error(
            title='错误',
            content=errorStr,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=5000,    # won't disappear automatically
            parent=self.parent()
        )

    def __createCOMSuccessInfoBar(self, portStr):

        if portStr[0] == '0':
            portStr = portStr[1:]
            InfoBar.success(
                title='成功',
                content=portStr,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                # position='Custom',   # NOTE: use custom info bar manager
                duration=1500,
                parent=self.parent()
            )
        else:
            self.COMCard.comboBox.setEnabled(False)
            self.baudrateCard.comboBox.setEnabled(False)
            InfoBar.success(
                title='成功',
                content="成功打开串口 "+portStr+".",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                # position='Custom',   # NOTE: use custom info bar manager
                duration=1500,
                parent=self.parent()
            )

    def __receivedData(self, data):
        self.textEdit.moveCursor(self.textEdit.textCursor().MoveOperation.End)
        try:
            self.textEdit.insertPlainText(data.decode('gb2312', errors='ignore'))
        except UnicodeDecodeError:
            pass

    def closeEvent(self, event):
        serialThread.stop()  # 停止线程
        super().closeEvent(event)

    def __sendData(self, key, value):
        serialThread.send_data(f'set {key} {int(value)}\r\n')
            