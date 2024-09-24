




from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

import sys, ctypes, os, re, json, random, shutil, sass, subprocess, threading, time









try:
	with open("data.json", "r") as file:
		DATA = json.load(file)
except:
	DATA = {}

elem = {}
elem["platform"] = sys.platform








ICON = {
	"sidebar": "\uE000",
	"newNote": "\uE001",
	"newFolder": "\uE002",
	"expandTree": "\uE003",
	"collapseTree": "\uE004",
	"settings": "\uE005",

	"img": "\uE008",
	"expanded": "\uE007",
	"collapsed": "\uE006",

	"rename": "\uE00F",
	"duplicate": "\uE010",
	"openInTab": "\uE011",
	"showInFolder": "\uE012",
	"delete": "\uE009",

	"close": "\uE013",
	"showInTree": "\uE014",
	"save": "\uE015",
	# "copyPath": "\uE000",

	"undo": "\uE017",
	"redo": "\uE018",
	"cut": "\uE019",
	"copy": "\uE016",
	"paste": "\uE01A",
	"selectAll": "\uE01B",
	"copyUrl": "\uE01C",
	"openUrl": "\uE01D",

	"plus": "\uE00A",
	"minus": "\uE00B",
	"reset": "\uE00C",
	"invert": "\uE00D",
	"grip": "\uE00E",

	"case": "\uE01E",
	"regex": "\uE01F",
	"prev": "\uE020",
	"next": "\uE021",
	"replace": "\uE022",
	"replaceAll": "\uE023",
}





SC_FACTOR = {
	"margin": 2.5,
	"treeMargin": 1,
	"numsMargin": 0.8,
	"numsScale": 1.1,
	"rowHeight": 1.9,
	"settViewMargin": 10,

	"iconScale": 1.5,
	"treeIconScale": 1.2,
	"imgIconScale": 1.4,

	"ctxIconMrgn": 3.6,
	"ctxYPos": 1.3,
	"treeIconMrgn": 5.5,
	"tabHeight": 2.5,
	"tabWidth": 9,
	"iconTab": 0.7,
	"radius": 3.3,

	"sidebarMin": 12,
	"fontView": 16,

}












PARAM = {
	"dropAlpha": 0.2,
	"settAlpha": 0.8,
	"imgType": ["png", "jpg", "jpeg", "gif", "bmp", "tiff", "svg", "ico", "webp"],
	"tabNameLen": 20,
	"settMargin": 250,
	"iconName": "qnotes-icons"

}


colorParam = {
	"foreground": "#4e4e4e",
	"foreground-text": "#3f3f3f",
	"background": "#fbfbfb",
	"background-sidebar": "#f3f3f3",
	"background-titlebar": "#f3f3f3",
	"background-ribbon": "#f3f3f3",
	"background-2nd": "#f0f0f0",

	"link": "#6d6dfa",
	"highlight": "#fcd914",

}



prefParam = {
	"fontSize": 16,
	"textFontSize": 16,
	"textMargin": 40,
	"tabSize": 50,
	"cursorWidth": 2,
	"pairBrackets": True,
	"lineNums": False,
	"indentGuides": True,
	"matchTab": True,
	"imgFolder": "Images",
	"imgFormat": "jpg",
	"smoothScroll": True,
	"pairMarkdown": True,

}



PARAM.update(colorParam | prefParam)

COLOR = {key: DATA.get(key, PARAM[key]) for key in colorParam}
PREFS = {key: DATA.get(key, PARAM[key]) for key in prefParam}






def setFontConf():
	general = QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont).family()
	fixed = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont).family()
	for key, val in [("font", general), ("textFont", general), ("codeFont", fixed)]:
		PARAM[key] = val
		PREFS[key] = DATA.get(key, val)

























from widget.ribbon import *
from widget.sidebar import *
from widget.text import *
from widget.tabs import *
from widget.settings import *

if (isWin := elem["platform"] == "win32"):
	from widget.frameless import *































class Main(Frameless if isWin else QWidget): 
	def __init__(self):
		super().__init__()
		elem["main"] = self
		self.setWindowTitle(" ")
		self.setObjectName("main")

		QFontDatabase.addApplicationFont(f"resource/{PARAM['iconName']}.ttf")
		self.updateStylesheet()

		self.validDir = lambda: os.path.exists(DATA.get("folderPath", ""))
		self.flashTime = app.cursorFlashTime()







		layout = QHBoxLayout()
		layout.setContentsMargins(QMargins())
		layout.setSpacing(0)



		layout.addWidget(Ribbon())
		layout.addWidget(Sidebar())
		layout.addWidget(Tabs())
	
		
		# elem["sidebar"].hide()
		# elem["ribbon"].hide()
		# elem["tabBar"].hide()


		if isWin:
			wrap = QVBoxLayout()
			wrap.setContentsMargins(QMargins())
			wrap.setSpacing(0)

			wrap.addWidget(Titlebar(self))
			wrap.addLayout(layout)
			layout = wrap

		
		

		self.setLayout(layout)
		Settings(self)
		self.setAppGeometry()




	
		for seq, func in [
		(QKeySequence.StandardKey.ZoomIn, self.scaleInterface),
		("Ctrl+=", self.scaleInterface),
		(QKeySequence.StandardKey.ZoomOut, lambda: self.scaleInterface(zoomOut=True)),
		("Ctrl+,", elem["settings"].show),
		(QKeySequence.StandardKey.Cancel, lambda: (elem["findText"].hide() if elem["settings"].isHidden() else None, elem["settings"].hide())),
		(QKeySequence.StandardKey.Find, elem["findText"].showSearch),
		(QKeySequence.StandardKey.Replace, elem["findText"].showReplace),
		]:
			(s := QShortcut(seq, self)).setAutoRepeat(False)
			s.activated.connect(func)

	













	def setAppGeometry(self):
		geom = DATA.get("appGeometry", {})

		self.setGeometry(QRect(*geom["rect"])) if geom.get("rect") else self.resize(self.screen().availableGeometry().size() / 1.5)
		if geom.get("max"):
			self.showMaximized()



	def scaleInterface(self, zoomOut=False):
		PREFS["fontSize"] = max(8, min(PREFS["fontSize"] + (1 if not zoomOut else -1), 40))
		self.updateStylesheet()







	def closeEvent(self, e):
		DATA["appGeometry"] = {"rect": self.geometry().getRect() if not self.isMaximized() else DATA.get("appGeometry", {}).get("rect"), "max": self.isMaximized()}

		if self.validDir():
			elem["tree"].getTreeState(save=True)
		if not elem["tabBar"].getTabState(save=True):
			e.ignore()
			return



		DATA.update(PREFS)

		[COLOR.pop(i, None) for i in ("mid", "hovered", "background-selection", "mid-text")]
		DATA.update(COLOR)
		self.saveData()






	def saveData(self):
		with open("data.json", "w") as f:
			json.dump(DATA, f)









	def updateStylesheet(self):
		PARAM["margin"] = int(PREFS["fontSize"] / SC_FACTOR["margin"])
		PARAM["iconSize"] = int(PREFS["fontSize"] / SC_FACTOR["iconScale"])
		PARAM["bdRadius"] = int(PREFS["fontSize"] / SC_FACTOR["radius"])


		# init relative colors
		for base, key, val in [
			("foreground", "mid", 122), 
			("background-sidebar", "hovered", 30), 
			("background", "background-selection", 30),
			("background", "mid-text", 50),
			]:
			(color := QColor(COLOR[base])).setHsv(color.hue(), color.saturation() ,(v := color.value()) + (val if v <= 255 - val else -val))
			COLOR[key] = color.name()





		values = [
			(PREFS, "fontSize"),
			(PARAM, "margin"),
			(PARAM, "bdRadius"),
			(PREFS, "font"),
			(COLOR, "foreground"),
			(COLOR, "foreground-text"),
			(COLOR, "background"),
			(COLOR, "background-2nd"),
			(COLOR, "background-selection"),
			(COLOR, "background-sidebar"),
			(COLOR, "background-titlebar"),
			(COLOR, "background-ribbon"),
			(COLOR, "mid"),
			(COLOR, "hovered")
		]

		with open("resource/style.css", "r") as f:
			css = f.read()
			for dictName, key in values:
				css = css.replace(f"{{{key}}}", str(dictName[key]))
		app.setStyleSheet(sass.compile(string=css, output_style="compressed"))



		for _, item in elem.items():
			if hasattr(item, "showEvent"):
				item.showEvent(None)































if __name__ == "__main__":
	app = QApplication([])
	setFontConf()
	elem["app"] = app
	app.setWindowIcon(QIcon("resource/logo.ico"))
	app.setEffectEnabled(Qt.UIEffect.UI_AnimateMenu, False)


	if isWin:
		ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("qnotes")




	main = Main()
	main.show()
	sys.exit(app.exec())