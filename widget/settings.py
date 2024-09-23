








from main import *









# class NavButton(QPushButton):
# 	def __init__(self, text, icon):
# 		super().__init__()
# 		self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
# 		self.setObjectName("nav-btn")

# 		self.text = text
# 		self.icon = icon


# 	def paintEvent(self, e):
# 		super().paintEvent(e)
# 		p = QPainter(self)
# 		if elem["settings"].viewStack.currentIndex() == elem["settings"].btnLayout.indexOf(self):
# 			p.save()
# 			p.setRenderHint(QPainter.RenderHint.Antialiasing)
# 			p.setPen(Qt.PenStyle.NoPen)
# 			p.setBrush(QBrush(QColor(COLOR["select"]), Qt.BrushStyle.SolidPattern))
# 			p.drawRoundedRect(self.rect(), PARAM["bdRadius"], PARAM["bdRadius"])
# 			p.restore()



# 		margin = PARAM["margin"]
# 		iconWidth = QFontMetrics(iconFont := QFont("qicons", PARAM["iconSize"])).height()

# 		p.save()
# 		p.setFont(iconFont)
# 		p.drawText(QRectF(margin, 0, iconWidth, self.height()), Qt.AlignmentFlag.AlignVCenter, self.icon)
# 		p.restore()


# 		x = int(margin * SC_FACTOR["ctxIconMrgn"]) + iconWidth
# 		textRect = QRect(QPoint(x, 0), QFontMetrics(self.font()).size(0, self.text)).adjusted(0, 0, margin, margin * 2)

# 		p.drawText(textRect, Qt.AlignmentFlag.AlignVCenter, self.text)
# 		p.end()
# 		if self.minimumSize() != (newSize := QSize(textRect.right(), textRect.height())):
# 			self.setMinimumSize(newSize)
# 			elem["settings"].showEvent(None)























class FramelessDialog(QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
		self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
		self.installEventFilter(self)



		wrapLayout = QGridLayout()
		wrapLayout.setContentsMargins(QMargins())
		wrapLayout.addWidget(frame := QFrame(), 0,0)
		frame.setObjectName("dialog")


		self.layout = QVBoxLayout()
		self.layout.setSpacing(margin := PARAM["margin"])
		self.layout.setContentsMargins(margin,margin,margin,margin)

		self.addWidget = lambda w: self.layout.addWidget(w)
		self.addLayout = lambda l: self.layout.addLayout(l)
		self.setResizable = lambda: wrapLayout.addWidget(SizeGrip(self), 0,0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)



		frame.setLayout(self.layout)
		self.setLayout(wrapLayout)






	def eventFilter(self, obj, e):
		if e.type() == QEvent.Type.WindowDeactivate:
			self.deleteLater()
		return False






























class ColorPicker(FramelessDialog):
	def __init__(self, color, keys, btns):
		super().__init__(elem["settings"])
		self.keys = keys
		self.btns = btns



		colors = QHBoxLayout()
		colors.setSpacing(0)
		colors.setContentsMargins(QMargins())

		self.colorWindow = QWidget()
		self.colorWindow.setFixedSize(QSize(255,255))
		self.colorWindow.paintEvent = self.paintWindow
		self.colorWindow.mouseMoveEvent = self.mouseColor
		self.colorWindow.mousePressEvent = self.mouseColor
		self.colorWindow.mouseReleaseEvent = self.setNewColor



		self.hueRange = QWidget()
		self.hueRange.setFixedWidth(PREFS["fontSize"])
		self.hueRange.paintEvent = self.paintHues
		self.hueRange.mouseMoveEvent = self.mouseHues
		self.hueRange.mousePressEvent = self.mouseHues
		self.hueRange.mouseReleaseEvent = self.setNewColor


		colors.addWidget(self.colorWindow)
		colors.addWidget(self.hueRange)





		self.colorName = QLineEdit()
		self.colorName.contextMenuEvent = lambda e: None
		self.colorName.textEdited.connect(lambda text: (self.initColor(c), self.setNewColor()) if (c := QColor(text)).isValid() else None)
		self.colorName.setObjectName("input")



		self.addLayout(colors)
		self.addWidget(self.colorName)

		self.initColor(color)
		self.moveWidget()
		self.show()











	def moveWidget(self):
		btn = self.btns[0]
		pos = btn.mapToGlobal(self.parent().pos()) + QPoint(0, btn.sizeHint().height() - 1)
		self.move(pos)


	def initColor(self, color):
		self.color = QColor(color)
		self.hue = max(self.color.hueF(), 0)
		# 255 fixed width
		self.posColor = QPoint(self.color.saturation(), 255 - self.color.value())

		self.hueRange.repaint()
		self.colorWindow.repaint()




	def setNewColor(self, e=False):
		for key, btn in zip(self.keys, self.btns):
			COLOR[key] = (color := self.color.name())
			btn.setStyleSheet(f"background-color: {color}")
		elem["main"].updateStylesheet()









	def mouseColor(self, e):
		rect = self.colorWindow.rect()
		self.posColor = QPoint(
			max(0, min(e.pos().x(), rect.width())), 
			max(0, min(e.pos().y(), rect.height())))
		self.colorWindow.repaint()


	def mouseHues(self, e):
		height = self.hueRange.rect().height()
		self.hue = max(0, min(e.pos().y(), height)) / height

		self.hueRange.repaint()
		self.colorWindow.repaint()








	def paintHues(self, e):
		p = QPainter(self.hueRange)
		height = (rect := self.hueRange.rect()).height()

		hue = QLinearGradient(0,0, 0,height)
		deg = 30
		hues = int(360 / deg)

		color = QColor()
		for i in range(hues + 1):
			color.setHsvF((deg * i) / 360, 1, 1)
			hue.setColorAt(i / hues, color)
		p.fillRect(rect, hue)




		p.setPen(QPen(QColor("black"), 2))
		y = max(0, min(self.hue * height, height - 2)) + 1
		p.drawLine(QPointF(0, y), QPointF(rect.width(), y))
		p.end()











	def paintWindow(self, e):
		p = QPainter(self.colorWindow)
		p.setRenderHint(QPainter.RenderHint.Antialiasing)
		height = (rect := self.colorWindow.rect()).height()


		self.color.setHsvF(self.hue, 1, 1)
		horiz = QLinearGradient(0,0, rect.width(),0)
		horiz.setColorAt(0, QColor("white"))
		horiz.setColorAt(1, self.color)

		vert = QLinearGradient(0,0, 0,height)
		vert.setColorAt(0, QColor("transparent"))
		vert.setColorAt(1, QColor("black"))


		p.fillRect(rect, horiz)
		p.fillRect(rect, vert)



		self.color.setHsvF(self.hue, self.posColor.x() / rect.width(), (height - self.posColor.y()) / height)
		invert = QColor(*[255 - i for i in self.color.getRgb()[:-1]])
		p.setPen(QPen(invert, 2))
		p.drawEllipse(self.posColor, 5, 5)
		p.end()




		self.colorName.setStyleSheet(f"background-color: {self.color.name()}; color: {invert.name()}")
		self.colorName.setText(self.color.name())






































class SizeGrip(QLabel):
	def __init__(self, parent):
		super().__init__(ICON["grip"])
		self.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.setObjectName("size-grip")
		self.setCursor(Qt.CursorShape.SizeFDiagCursor)

		self.parent = parent
		self.mousePressEvent = lambda e: setattr(self, "startPos", e.pos())


	def mouseMoveEvent(self, e):
		if e.buttons() == Qt.MouseButton.LeftButton:
			delta = e.pos() - self.startPos
			rect = self.parent.geometry()

			rect.setBottomRight(rect.bottomRight() + delta)
			self.parent.setGeometry(rect)
	









class FontSearch(QLineEdit):
	def __init__(self, fonts):
		super().__init__()
		self.contextMenuEvent = lambda e: None
		self.fonts = fonts


	def paintEvent(self, e):
		super().paintEvent(e)

		if not self.text():
			(p := QPainter(self)).setPen(QColor(COLOR["mid"]))
			p.drawText(self.rect().translated(2,0), Qt.AlignmentFlag.AlignVCenter, f"Search {str(self.fonts.count())} fonts")
			p.end()


	def keyPressEvent(self, e):
		super().keyPressEvent(e)
		if e.key() == Qt.Key.Key_Down and (item := self.fonts.itemAt(0, 0)):
			self.fonts.setFocus()
			self.fonts.setCurrentItem(item, QItemSelectionModel.SelectionFlag.Select)
	















class FontView(FramelessDialog):
	def __init__(self, keys, btns):
		super().__init__(elem["settings"])
		self.setResizable()

		
		self.keys = keys
		self.btns = btns


		self.fonts = QListWidget()
		self.fonts.setObjectName("font-list")
		self.fonts.setUniformItemSizes(True)
		self.fonts.setWordWrap(True)
		self.fonts.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.fonts.itemClicked.connect(self.setNewFont)
		self.fonts.itemActivated.connect(self.setNewFont)


		search = FontSearch(self.fonts)
		search.textEdited.connect(self.searchFonts)
		search.setObjectName("search-font")




		self.addWidget(search)
		self.addWidget(self.fonts)


		self.setSizes()
		self.show()
		threading.Thread(target=self.populateFonts).start()








	def setSizes(self):
		btn = self.btns[0]
		pos = btn.mapToGlobal(self.parent().pos()) + QPoint(0, btn.sizeHint().height() - 1)
		size = QSize(PREFS["fontSize"], PREFS["fontSize"]) * SC_FACTOR["fontView"]
		self.setGeometry(QRect(pos, size))





	def populateFonts(self):
		for i in QFontDatabase.families(QFontDatabase.WritingSystem.Any):
			(item := QListWidgetItem(i)).setFont(QFont(i))
			self.fonts.addItem(item)


	def searchFonts(self, text):
		text = text.casefold()
		for i in range(self.fonts.count()):
			(item := self.fonts.item(i)).setHidden(text not in item.text().casefold())




	def setNewFont(self, item):
		if (font := item.text()) != PREFS[self.keys[0]]:
			for key, btn in zip(self.keys, self.btns):
				PREFS[key] = font
				btn.setText(font)

		elem["main"].updateStylesheet()
























class Toggle(QPushButton):
	def __init__(self, dictName, key):
		super().__init__()
		self.setCheckable(True)

		self.clicked.connect(lambda: (
			dictName.update({key: not dictName[key]}),
			self.toggleAnimation()))

		elem["settings"].settingsShown.connect(lambda: self.setFixedWidth(int(PREFS["fontSize"] * 2.5)))
		self.setChecked(dictName[key])



		self.knobX = int(dictName[key])
		self.anim = QPropertyAnimation(self, b"knobPos")
		self.anim.setDuration(50)
		self.anim.setStartValue(0)
		self.anim.setEndValue(1)

		self.anim.finished.connect(lambda: QTimer.singleShot(1, elem["main"].updateStylesheet))







	def toggleAnimation(self):
		self.anim.setDirection(QPropertyAnimation.Direction.Forward if self.isChecked() else QPropertyAnimation.Direction.Backward)
		self.anim.start()


	@pyqtProperty(float)
	def knobPos(self):
		return self.knobX

	@knobPos.setter
	def knobPos(self, val):
		self.knobX = val
		self.update()






	def paintEvent(self, e):
		p = QPainter(self)
		p.setPen(Qt.PenStyle.NoPen)
		p.setRenderHint(QPainter.RenderHint.Antialiasing)
		p.save()

		rect = self.rect().toRectF()
		bdHalf = 1/2 # fixed 1px border
		r = rect.height() // 2



		if (on := self.isChecked()):
			p.setBrush(QBrush(QColor(COLOR["hovered"]), Qt.BrushStyle.SolidPattern))

		p.setPen(QColor(COLOR["mid"]))
		p.drawRoundedRect(rect.adjusted(bdHalf,bdHalf,-bdHalf,-bdHalf), r, r)


		p.restore()
		width = rect.width() - rect.height()
		x = self.knobX * width

		p.setBrush(QBrush(QColor(COLOR["mid"]), Qt.BrushStyle.SolidPattern))
		p.drawRoundedRect(rect.adjusted(x, 0, x - width, 0), r, r)
		p.end()























class View(QScrollArea):
	def __init__(self):
		super().__init__()
		self.setWidgetResizable(True)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.installEventFilter(self)

		container = QWidget()
		self.layout = QVBoxLayout()
		self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

		container.setLayout(self.layout)
		self.setWidget(container)



	





	def showEvent(self, e):
		self.layout.setContentsMargins(margin := PARAM["margin"] * SC_FACTOR["settViewMargin"],margin,margin,margin)
		self.layout.setSpacing(PARAM["margin"])

		widgets = []
		height = 0
		for i in range(self.layout.count()):
				(widget := self.layout.itemAt(i).widget()).layout().setSpacing(PARAM["margin"])

				height = max(height, widget.sizeHint().height())
				widgets.append(widget)

		for i in widgets:
			i.setFixedHeight(height)







	def addRow(self, text, widgets=[], section=False):
		row = QWidget()
		rowLayout = QHBoxLayout()
		rowLayout.setContentsMargins(QMargins())


		label = QLabel(text)
		rowLayout.addWidget(label)

		if section:
			label.setObjectName("label-section")
			label.setText(f"<b>{label.text()}</b>")
			
			(line := Separator()).setObjectName("ctx-separator")
			line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
			rowLayout.addWidget(line)
		else:
			rowLayout.addStretch()
			[rowLayout.addWidget(i) for i in widgets]

		row.setLayout(rowLayout)
		self.layout.addWidget(row)






























class Settings(QWidget):
	settingsShown = pyqtSignal()

	def __init__(self, parent):
		super().__init__(parent)
		elem["settings"] = self
		self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
		self.setObjectName("settings")



		self.wrap = QGridLayout()



		main = QWidget()
		main.setObjectName("settings-wrap")

		self.layout = QGridLayout()
		self.layout.setContentsMargins(QMargins())
		self.layout.setSpacing(0)

		self.view = View()
		self.generalSect()
		self.editorSect()
		self.appearSect()
		self.layout.addWidget(self.view,0,0)
		main.setLayout(self.layout)



		self.wrap.addWidget(main,0,0)
		self.setLayout(self.wrap)






		parent.installEventFilter(self)
		self.hide()


		self.mouseReleaseEvent = lambda e: self.hide() if self.childAt(e.pos()) is None else None















	def eventFilter(self, obj, e):
		if self.isVisible() and e.type() == QEvent.Type.Resize:
			self.resize(self.parent().size())
		return False



	def showEvent(self, e):
		self.eventFilter(False, QEvent(QEvent.Type.Resize))
		self.setFocus()
		margin = PARAM["margin"]


		m = PARAM["settMargin"] - PREFS["fontSize"] * margin
		self.wrap.setContentsMargins(m,m,m,m)
		self.setStyleSheet(f"""QWidget#settings{{background-color: rgba({','.join(str(i) for i in QColor(COLOR['background-2nd']).getRgb()[:-1])}, {PARAM['settAlpha']})}}""")

		self.settingsShown.emit()
		for i in range(self.layout.count()):
			self.layout.itemAt(i).widget().showEvent(None)




















	def generalSect(self):
		self.view.addRow("General", section=True)




		newFolder = QPushButton()
		newFolder.setObjectName("option-label")
		newFolder.setCursor(Qt.CursorShape.PointingHandCursor)

		newFolder.clicked.connect(lambda: (
			DATA.update(folderPath=os.path.normpath(path)),
			elem["sidebar"].setFolder())
			if (path := QFileDialog.getExistingDirectory(self, "Set directory")) else None)



		self.updateLabel = lambda: (newFolder.setText(os.path.basename(DATA["folderPath"])[:PARAM["tabNameLen"]] if elem["main"].validDir() else "Set directory"))
		self.updateLabel()



		delFolder = QPushButton(ICON["delete"])
		delFolder.setObjectName("icon-button")

		delFolder.clicked.connect(lambda: (
			DATA.pop("folderPath", None),
			DATA.pop("treeState", None),
			elem["sidebar"].setFolder())
			if elem["main"].validDir() else None)

		self.view.addRow("Directory", [newFolder, delFolder])











		scale = QLabel()
		self.updateScale = lambda: scale.setText(f"{int((PREFS['fontSize'] * 100) / PARAM['fontSize'])}%")
		self.settingsShown.connect(self.updateScale)


		for i in (scaleBtns := [QPushButton(ICON[i]) for i in ("minus", "plus")]):
			i.clicked.connect(lambda _, i=i: (elem["main"].scaleInterface(zoomOut=i == scaleBtns[0]), self.updateScale()))
			i.setObjectName("icon-button")

		scaleBtns.insert(1, scale)
		self.view.addRow("UI scale", scaleBtns)



























	def editorSect(self):
		self.view.addRow("Editor", section=True)






		viewRange = self.slider(5, 900, viewLabel := QLabel(), "textMargin")
		self.view.addRow("View spacing", [viewLabel, viewRange, self.resetBtn("textMargin", viewRange)])






		tabRange = self.slider(10, 150, tabLabel := QLabel(), "tabSize")
		self.view.addRow("Tab width", [tabLabel, tabRange, self.resetBtn("tabSize", tabRange)])






		self.view.addRow("Pair brackets", [Toggle(PREFS, "pairBrackets")])
		self.view.addRow("Pair Markdown", [Toggle(PREFS, "pairMarkdown")])




		cursorRange = self.slider(1, 10, cursorLabel := QLabel(), "cursorWidth")
		self.view.addRow("Cursor width", [cursorLabel, cursorRange, self.resetBtn("cursorWidth", cursorRange)])





		self.view.addRow("Indent guides", [Toggle(PREFS, "indentGuides")])
		self.view.addRow("Line numbers", [Toggle(PREFS, "lineNums")])
		self.view.addRow("Smooth scroll", [Toggle(PREFS, "smoothScroll")])







		self.imgFolder = folder = QLineEdit(PREFS["imgFolder"])
		folder.setObjectName("input")
		folder.contextMenuEvent = lambda e: None
		folder.adjustInput = lambda: folder.setMaximumWidth(folder.fontMetrics().horizontalAdvance(folder.text()) + 7 + PARAM["margin"] * 2)
		self.settingsShown.connect(folder.adjustInput)


		folder.textEdited.connect(lambda text: (PREFS.update(imgFolder=os.path.normpath(text)), folder.adjustInput()))

		self.view.addRow("Pasted image location", [folder, self.resetBtn("imgFolder", folder)])









		for i in (imgBtns := [QPushButton(i) for i in ("jpg", "png")]):
			i.setCheckable(True)
			i.setChecked(i.text() == PREFS["imgFormat"])
			i.setObjectName("option-label") 
			i.clicked.connect(lambda _, i=i: (PREFS.update(imgFormat=i.text()), [btn.setChecked(i == btn) for btn in imgBtns]))

		self.view.addRow("Pasted image format", imgBtns)






















	def slider(self, min, max, label, key):
		slider = QSlider(Qt.Orientation.Horizontal)
		slider.wheelEvent = lambda _: None
		slider.setObjectName("slider")
		slider.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
		slider.setRange(min, max)
		slider.setSingleStep(10)

		label.setObjectName("label-section")


		updateText = lambda val: (
			label.setText(str(val)),
			PREFS.update({key: val}),
			elem["tabBar"].tabStack.currentWidget().textWidget.showEvent(None)
		)

		slider.valueChanged.connect(lambda val: updateText(val))
		slider.setValue(PREFS[key])
		# force update, won't set value if PREFS matches min. range
		updateText(PREFS[key])
		return slider








	def resetBtn(self, key, widget, theme=False):
		btn = QPushButton(ICON["reset"])
		btn.setObjectName("icon-button")


		def resetAction():
			if isinstance(widget, QSlider):
				widget.setValue(PARAM[key])

			elif isinstance(widget, QLineEdit):
				widget.setText(PARAM[key])
				widget.textEdited.emit(widget.text())

			elif isinstance(widget, QPushButton):
				if not theme:
					PREFS[key] = PARAM[key]
					widget.setText(PARAM[key])
				else:
					COLOR.update({k: PARAM[k] for k in COLOR if k in PARAM})
				elem["main"].updateStylesheet()


		btn.clicked.connect(resetAction)
		return btn























	def appearSect(self):
		self.view.addRow("Appearance", section=True)




		(themeBtn := QPushButton(ICON["invert"])).setObjectName("icon-button")
		themeBtn.clicked.connect(self.setTheme)

		self.view.addRow("Theme", [themeBtn, self.resetBtn("darkTheme", themeBtn, theme=True)])















		includeKey = {
			"font": ["textFont"],
			"foreground": ["foreground-text"],
			"background-sidebar": ["background-ribbon", "background-titlebar"]
		}

		getKeys = lambda dictName, key: [key] + [i for i in includeKey.get(key, []) if dictName[i] == dictName[key]]
	




		fontElems = {key: (QPushButton(PREFS[key]), text) for key, text in [
			("font", "Application"), 
			("textFont", "Editor"), 
			("codeFont", "Monospace")
			]}	


		for key, (btn, text) in fontElems.items():
			btn.setObjectName("option-label")
			btn.setCursor(Qt.CursorShape.PointingHandCursor)

			btn.clicked.connect(lambda _, key=key: FontView(keys := getKeys(PREFS, key), [fontElems[i][0] for i in keys]))
			
			self.view.addRow(f"{text} font", [btn, self.resetBtn(key, btn)])









		colorElems = {key: (QPushButton(), text) for key, text in [
			("foreground", "Application text"), 
			("foreground-text", "Editor text"), 
			("background", "Editor background"), 
			("background-sidebar", "Sidebar background"), 
			("background-ribbon", "Ribbon background"), 
			("background-ribbon", "Ribbon background"), 
			("background-titlebar", "Title bar background"), 
			("background-2nd", "Secondary background"),
			("highlight", "Editor highlight"), 
			("link", "Editor link"), 
			]}	

		self.settingsShown.connect(lambda: [btn.setStyleSheet(f"background-color: {COLOR[key]}") for key, (btn, _) in colorElems.items()])



		for key, (btn, text) in colorElems.items():
			if elem["platform"] == "win32" or not "title" in key:
				btn.setObjectName("option-label")
				btn.setCursor(Qt.CursorShape.PointingHandCursor)
				btn.setStyleSheet(f"background-color: {COLOR[key]}")

				btn.clicked.connect(lambda _, key=key: ColorPicker(COLOR[key], keys := getKeys(COLOR, key), [colorElems[i][0] for i in keys]))
				self.view.addRow(f"{text} color", [btn])












		self.view.addRow("Match current tab with editor colors", [Toggle(PREFS, "matchTab")])
















	def setTheme(self):
		val = 20
		for key in [
			"foreground", 
			"foreground-text", 
			"background", 
			"background-sidebar", 
			"background-titlebar", 
			"background-ribbon", 
			"background-2nd",
			]:
			(color := QColor(COLOR[key])).setHsv(color.hue(), color.saturation(), (v := (255 - color.value())) + (val if v <= 255 - val else -val))

			COLOR[key] = color.name()
		elem["main"].updateStylesheet()

























































