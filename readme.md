# 在conda中配置环境
```bash
conda create -n gliderGUI python=3.10.14
conda activate gliderGUI
pip install PyQt6-Fluent-Widgets -i https://pypi.org/simple/
pip install pyserial
```
# 使用pyinstaller打包
安装pyinstaller
```bash
pip install pyinstaller
```
打包
```bash
pyinstaller gliderGUI.spec
```
将更目录下`recouce`文件夹复制到`dist/gliderGUI/`中