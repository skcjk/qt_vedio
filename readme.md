# 在conda中配置环境
```bash
conda create -n qt_vedio python=3.10.14
conda activate qt_vedio
pip install PyQt6-Fluent-Widgets -i https://pypi.org/simple/
pip install ...
```
# 使用pyinstaller打包
安装pyinstaller
```bash
pip install pyinstaller
```
打包
```bash
pyinstaller main.spec
```
将根目录下`recouce`,`ffmpeg`文件夹和`mediamtx.exe`,`mediamtx.yml`,`index.html`文件复制到`dist/gliderGUI/`中

ffmpeg下载地址：https://ffmpeg.org/download.html

mediamtx下载地址：https://github.com/bluenviron/mediamtx/releases/