from qfluentwidgets import (ScrollArea, ExpandLayout, OptionsConfigItem, OptionsValidator,
                            SettingCardGroup, SwitchSettingCard,
                            OptionsSettingCard, CustomColorSettingCard,
                            setTheme, InfoBar, ComboBoxSettingCard,
                            setThemeColor, InfoBarPosition)
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtSerialPort import QSerialPortInfo
from qfluentwidgets import FluentIcon as FIF
from common.config import cfg
from PyQt6.QtCore import Qt
from common.style_sheet import StyleSheet

# SettingInterface class inherits from ScrollArea and provides a settings interface
class SettingInterface(ScrollArea):

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
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.zoomCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.personalGroup)

    def __connectSignalToSlot(self):

        cfg.appRestartSig.connect(self.__showRestartTooltip)

        # personalization
        self.themeCard.optionChanged.connect(lambda ci: setTheme(cfg.get(ci)))
        self.themeColorCard.colorChanged.connect(lambda c: setThemeColor(c))

    def __showRestartTooltip(self):
        
        InfoBar.success(
            self.tr('设置成功'),
            self.tr('重启软件生效'),
            duration=1500,
            parent=self
        )


    # def __createCOMErrorInfoBar(self, errorStr):

    #     if errorStr[0] == '0':
    #         errorStr = errorStr[1:]
    #     else:
    #         self.serialSwitchCard.switchButton.setChecked(False)
    #     InfoBar.error(
    #         title='错误',
    #         content=errorStr,
    #         orient=Qt.Orientation.Horizontal,
    #         isClosable=True,
    #         position=InfoBarPosition.BOTTOM_RIGHT,
    #         duration=5000,    # won't disappear automatically
    #         parent=self.parent()
    #     )

    # def __createCOMSuccessInfoBar(self, portStr):

    #     if portStr[0] == '0':
    #         portStr = portStr[1:]
    #         InfoBar.success(
    #             title='成功',
    #             content=portStr,
    #             orient=Qt.Orientation.Horizontal,
    #             isClosable=True,
    #             # position='Custom',   # NOTE: use custom info bar manager
    #             duration=1500,
    #             parent=self.parent()
    #         )
    #     else:
    #         self.COMCard.comboBox.setEnabled(False)
    #         self.baudrateCard.comboBox.setEnabled(False)
    #         InfoBar.success(
    #             title='成功',
    #             content="成功打开串口 "+portStr+".",
    #             orient=Qt.Orientation.Horizontal,
    #             isClosable=True,
    #             # position='Custom',   # NOTE: use custom info bar manager
    #             duration=1500,
    #             parent=self.parent()
    #         )