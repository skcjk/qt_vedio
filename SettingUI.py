from qfluentwidgets import (ScrollArea, ExpandLayout, OptionsConfigItem, OptionsValidator,
                            SettingCardGroup, SwitchSettingCard,
                            OptionsSettingCard, CustomColorSettingCard,
                            setTheme, InfoBar, ComboBoxSettingCard,
                            setThemeColor, InfoBarPosition)
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtSerialPort import QSerialPortInfo
from qfluentwidgets import FluentIcon as FIF
from common.config import cfg
from SerialThread import serialThread
from PyQt6.QtCore import Qt
from common.style_sheet import StyleSheet

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

# SettingInterface class inherits from ScrollArea and provides a settings interface
class SettingInterface(ScrollArea):
    """
    A settings interface allowing users to customize application settings like theme, color, and zoom.

    Attributes:
        scrollWidget (QWidget): The widget contained within the scroll area.
        expandLayout (ExpandLayout): The layout managing the settings cards.
        settingLabel (QLabel): The label displaying the settings title.
        personalGroup (SettingCardGroup): Group of setting cards for personalization settings.
        themeCard (OptionsSettingCard): Card for selecting the application theme.
        themeColorCard (CustomColorSettingCard): Card for selecting the theme color.
        zoomCard (OptionsSettingCard): Card for selecting the interface zoom level.
    
    Args:
        parent (QWidget, optional): The parent widget. Defaults to None.
    
    Last modified: 2024-07-01 by 申凯诚
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.settingLabel = QLabel(self.tr("设置"), self)

        # personalization
        self.personalGroup = SettingCardGroup(
            self.tr('个性化'), self.scrollWidget)
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            self.tr('应用主题'),
            self.tr("调整你的应用外观"),
            texts=[
                self.tr('浅色'), self.tr('深色'),
                self.tr('跟随系统设置')
            ],
            parent=self.personalGroup
        )
        self.themeColorCard = CustomColorSettingCard(
            cfg.themeColor,
            FIF.PALETTE,
            self.tr('主题色'),
            self.tr('调整你的应用的主题色'),
            self.personalGroup
        )
        self.zoomCard = OptionsSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            self.tr("界面缩放"),
            self.tr("调整小部件和字体的大小"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("跟随系统设置")
            ],
            parent=self.personalGroup
        )
        self.serialGroup = SettingCardGroup(
            self.tr('串口'), self.scrollWidget)
        self.serialSwitchCard = SwitchSettingCard(
            FIF.PLAY,
            self.tr('打开串口'),
            self.tr(''),
            parent=self.serialGroup
        )
        self.COMCard = ComboBoxSettingCard(
            cfg.port,
            FIF.CONNECT,
            self.tr('串口号'),
            self.tr(''),
            texts=cfg.portList,
            parent=self.serialGroup
        )
        self.baudrateCard = ComboBoxSettingCard(
            cfg.baudrate,
            FIF.SPEED_MEDIUM,
            self.tr('波特率'),
            self.tr(''),
            texts=['4800', '9600', '14400', '19200', '38400', '43000', '57600', '76800', '115200'],
            parent=self.serialGroup
        )

        self.__initWidget()

    def __initWidget(self):
        """
        Initializes the widget properties, including size, scroll policies, margins, and stylesheet.

        Last modified: 2024-07-01 by 申凯诚
        """

        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface')

        # initialize style sheet
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        """
        Initializes the layout by positioning and adding setting cards to the expand layout.

        Last modified: 2024-07-01 by 申凯诚
        """

        self.settingLabel.move(36, 30)

        # add cards to group
        self.serialGroup.addSettingCard(self.serialSwitchCard)
        self.serialGroup.addSettingCard(self.COMCard)
        self.serialGroup.addSettingCard(self.baudrateCard)
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.zoomCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.serialGroup)
        self.expandLayout.addWidget(self.personalGroup)

    def __connectSignalToSlot(self):

        cfg.appRestartSig.connect(self.__showRestartTooltip)

        # personalization
        self.themeCard.optionChanged.connect(lambda ci: setTheme(cfg.get(ci)))
        self.themeColorCard.colorChanged.connect(lambda c: setThemeColor(c))

        # serial
        self.serialSwitchCard.checkedChanged.connect(lambda checked: self.startStopSerialThread(checked))
        self.COMCard.comboBox.clicked.connect(self.__refreshSerialPort)
        serialThread.errorMessage.connect(self.__createCOMErrorInfoBar)
        serialThread.successMessage.connect(self.__createCOMSuccessInfoBar)
        # serialThread.dataReceived.connect(self.__receivedData)

    def __showRestartTooltip(self):
        
        InfoBar.success(
            self.tr('设置成功'),
            self.tr('重启软件生效'),
            duration=1500,
            parent=self
        )

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