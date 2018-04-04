# coding: utf-8
import os
import htmlPy
from PySide import QtCore


# Initial confiurations
base_dir = os.path.abspath(os.path.dirname(__file__))
if os.name == 'nt':
	import win_inet_pton
	base_dir = base_dir.replace('\\','/')+'/'

# GUI initializations
#app = htmlPy.AppGUI(title=u"openfans clouddesk", width=1366, height=768, plugins=True, developer_mode=True)
app = htmlPy.AppGUI(title=u"openfans clouddesk", plugins=False, developer_mode=False, maximized=True)
# GUI configurations
app.static_path = os.path.join(base_dir, "static/")
app.template_path = os.path.join(base_dir, "tpl/")
#屏蔽窗体右键和文本选择
app.right_click_setting(0)
app.text_selection_setting(0)
#最大化
app.window.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)
app.window.setWindowFlags(QtCore.Qt.FramelessWindowHint)
#禁止调整窗口大小
app.window.setFixedSize(app.window.width(), app.window.height());

# Import back-end functionalities
from html2py import opdc
# Register back-end functionalities
app.bind(opdc(app))
# Instructions for running application
if __name__ == "__main__":
	app.start()