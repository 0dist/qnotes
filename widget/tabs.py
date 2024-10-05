




from main import *






























class FlowLayout(QLayout):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setContentsMargins(QMargins())

		self.itemList = []
		self.currMoving = None
		self.anim = True
		self.keepWidth = False
		self.prevWidth = 0


	def addItem(self, item):
		# self.anim = False
		self.keepWidth = False
		self.itemList.insert(-1, item)

	def count(self):
		return len(self.itemList)

	def itemAt(self, index):
		if index >= 0 and index < len(self.itemList):
			return self.itemList[index]

	def insertItem(self, index, item):
		self.update()
		self.itemList.insert(index, item)


	def takeAt(self, index):
		if index >= 0 and index < len(self.itemList):
			self.update()
			return self.itemList.pop(index)

	def removeWidget(self, widget):
		self.keepWidth = True
		self.takeAt(self.indexOf(widget)).widget().deleteLater()

	def sizeHint(self):
		return self.minimumSize()

	def minimumSize(self):
		return QSize(0,0)

	def contentsRect(self):
		return self.rect

	




	def setGeometry(self, rect):
		if self.itemList:
			rect = self.rect = rect.adjusted((m := self.contentsMargins()).left(), m.top(), -m.right(), -m.bottom())
			baseWidth = rect.width() - elem["tabBar"].newTab.width()
			itemWidth = self.itemList[0].widget().maximumWidth()
			totalLen = len(self.itemList) - 1 # -1 last button
			x = rect.x()
			remainder = 0




			if itemWidth * totalLen > baseWidth:
				itemWidth, remainder = divmod(baseWidth, totalLen)

			for n, item in enumerate(self.itemList):
				width = itemWidth + (1 if n < remainder else 0) if not self.keepWidth else item.geometry().width()
				itemRect = QRect(x, rect.y(), width, rect.height())


				if item != self.currMoving:
					# if self.prevWidth == baseWidth and self.anim:
					# 	self.animate(item.widget(), itemRect)
					# else:
					item.setGeometry(itemRect)
				else:
					# fill the width gap from the previous item's width
					item.widget().resize(width, item.geometry().height())


				# if (widget := item.widget()).isHidden():
				# 	widget.show()
				x += width
			# self.anim = True
			self.prevWidth = baseWidth



	# def animate(self, widget, rect):
	# 	widget.anim.setStartValue(widget.geometry())
	# 	widget.anim.setEndValue(rect)
	# 	widget.anim.start()

























class Tab(QWidget):
	def __init__(self, path):
		super().__init__()
		self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
		self.setObjectName("tab")
		self.setMouseTracking(True)
		self.setAcceptDrops(True)


		self.layout = QHBoxLayout()
		self.layout.setContentsMargins(QMargins())
		self.layout.setSpacing(0)




		self.label = QLabel()
		self.label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.label.setMouseTracking(True)
		self.label.paintEvent = self.paintLabel
		self.setTabTitle = lambda text: self.label.setText(text[:PARAM["tabNameLen"]]) if text else self.label.setText("Untitled")





		self.close = QPushButton(ICON["close"])
		self.close.setObjectName("close-tab")
		self.close.clicked.connect(lambda: self.parent().closeTab(self))


		self.layout.addWidget(self.label)
		self.layout.addWidget(self.close)
		self.setLayout(self.layout)



		self.lastPos = 0
		self.setPath(path)














	def showEvent(self, e):
		self.setMaximumWidth(int(PREFS["fontSize"] * SC_FACTOR["tabWidth"]))

	def paintEvent(self, e):
		p = QPainter(self)
		layout = self.parent().layout
		rect = self.rect()
		background = COLOR["background" if PREFS["matchTab"] else "hovered"]


		if not layout.itemAt(layout.indexOf(self) + 1).widget() == self.parent().currentTab:
			p.setPen(QColor(COLOR["mid"]))
			p.drawLine(QLine(QPoint(rect.right(), PARAM["bdRadius"]), QPoint(rect.right(), rect.height() - PARAM["bdRadius"] - 1)))


		if self.parent().currentTab == self:
			p.setRenderHint(QPainter.RenderHint.Antialiasing)
			p.setPen(Qt.PenStyle.NoPen)
			p.setBrush(QBrush(QColor(background), Qt.BrushStyle.SolidPattern))

			p.drawRoundedRect(rect, PARAM["bdRadius"], PARAM["bdRadius"])
			p.fillRect(rect.adjusted(0,PARAM["bdRadius"],0,0), QColor(background))
		p.end()










	def paintLabel(self, e):
		p = QPainter(self.label)
		margin = PARAM["margin"]
		rect = self.label.rect().adjusted(margin, margin, -margin, 0)
		x, y, width, height = rect.getRect()

		isImg = str(self.path).lower().endswith(tuple(PARAM["imgType"]))
		hasIcon = self.path in DATA.get("fileIcons", [])




		if PREFS["matchTab"] and self.parent().currentTab == self:
			p.setPen(QColor(COLOR["foreground-text"]))


		if isImg or hasIcon:
			imgFont = QFont(PARAM["iconName"], int(PREFS["fontSize"] / SC_FACTOR["imgIconScale"]))
			iconWidth = QFontMetrics(imgFont).height() + margin 

		if isImg:
			x = self.drawTabIcon(p, imgFont, ICON["img"], x, y, iconWidth, height - margin)

		if hasIcon:
			icon = chr(int(DATA["fileIcons"][self.path], 16))
			x = self.drawTabIcon(p, QFont("Material Symbols Outlined"), icon, x, y, iconWidth, height - margin)




		elided = QFontMetrics(p.font()).elidedText(self.label.text(), Qt.TextElideMode.ElideRight, width - x + margin)
		p.drawText(x, y, width, height, Qt.AlignmentFlag.AlignTop, elided)
		p.end()







	def drawTabIcon(self, p, font, icon, x, y, iconWidth, height):
		p.save()
		p.setFont(font)
		p.drawText(x, y, iconWidth, height, Qt.AlignmentFlag.AlignVCenter, icon)
		p.restore()

		return x + iconWidth









	def setPath(self, path):
		self.path = os.path.normpath(path) if path else None
		self.label.setText(os.path.splitext(os.path.basename(path))[0] if path else "Untitled")

		tabPane = elem["tabBar"].tabStack.widget(elem["tabBar"].layout.indexOf(self))
		if tabPane:
			tabPane.textWidget.path = path




	def enterEvent(self, e):
		super().enterEvent(e)
		self.update()
		self.close.show()

	def leaveEvent(self, e):
		super().leaveEvent(e)
		self.update()
		self.close.hide()

	def dragEnterEvent(self, e):
		e.accept()
		self.parent().selectTab(self)



	def event(self, e):
		if e.type() == QEvent.Type.ToolTip and (tip := self.parent().tip).isHidden():
			tip.updateTooltip(self.path or self.label.text())
		return super().event(e)









	def mousePressEvent(self, e):
		super().mousePressEvent(e)
		self.parent().tip.hide()
		if e.buttons() == Qt.MouseButton.LeftButton:
			self.parent().selectTab(self)
			self.dragStartPos = e.pos()
			# self.anim.stop()
			self.offset = e.position().toPoint().x()
			self.raise_()
			# self.setFocus()









	def mouseMoveEvent(self, e):
		super().mouseMoveEvent(e)
		if (tip := self.parent().tip).isVisible():
			tip.updateTooltip(self.path or self.label.text())

		if hasattr(self, 'dragStartPos'):
			if e.buttons() == Qt.MouseButton.LeftButton and (e.pos() - self.dragStartPos).manhattanLength() > 5:
				parent = self.parent()
				# prevent wobbly/clipping edges while moving
				parent.setUpdatesEnabled(False)
				self.dragStartPos = QPoint()
				# self.anim.stop()



				currX = e.scenePosition().toPoint().x()
				index = (layout := parent.layout).indexOf(self)


				# capture moving direction
				left = max(0, min(1, self.lastPos - currX))

				if (item := layout.itemAt(index - (1 if left else -1))):
					itemHalf = item.widget().x() + item.widget().width() // 2
					if (self.x() < itemHalf if left else self.x() + self.width() > itemHalf):
						takeAt = index - (1 if left else -1)
						# layout.itemAt(takeAt).widget().anim.stop()

						layout.currMoving = layout.takeAt(index)
						layout.insertItem(takeAt, layout.currMoving)
						parent.tabStack.insertWidget(index, parent.tabStack.widget(takeAt))




				minX, maxX = layout.contentsRect().x(), layout.itemList[-1].widget().x() - self.width()
				x = self.mapToParent(e.position().toPoint()).x() - self.offset
				self.move(max(minX, min(x, maxX)), self.y())
				self.lastPos = currX
				parent.setUpdatesEnabled(True)





	def mouseReleaseEvent(self, e):
		self.parent().layout.currMoving = None
		self.parent().layout.update()

		if hasattr(self, 'dragStartPos'):
			del self.dragStartPos 
		super().mouseReleaseEvent(e)







	def contextMenuEvent(self, e):
		if self.rect().contains(e.pos()):
			menu = ContextMenu(self)
			parent = self.parent()
			index = parent.layout.indexOf(self)



			menu.addRow("Close tab", ICON["close"], lambda: parent.closeTab(self))
			menu.addRow("Close other tabs", ICON["close"], lambda: self.closeTabs([i for i in parent.layout.itemList[:-1] if i.widget() != self]))
			menu.addRow("Close tabs to the right", ICON["close"], lambda: self.closeTabs(parent.layout.itemList[index + 1:-1]))

			if not (tabPane := parent.tabStack.widget(index)).img:
				menu.addSeparator()
				menu.addRow("Save", ICON["save"], lambda: parent.saveNote(self.path, tabPane.textWidget, self, shortcut=True))

			if self.path:
				menu.addSeparator()
				menu.addRow("Copy file path", ICON["copy"], lambda: elem["app"].clipboard().setText(self.path))

				if elem["main"].validDir():
					menu.addSeparator()
					menu.addRow("Show in sidebar", ICON["showInTree"], self.scrollToIndex)
					menu.addRow("Show in folder", ICON["showInFolder"], lambda: elem["tree"].revealItem(self.path))

					menu.addSeparator()
					menu.addRow("Set icon", ICON["addIcon"], lambda: IconPicker(self, e.globalPos(), self.path))
					if self.path in DATA.get("fileIcons", []):
						menu.addRow("Remove icon", ICON["removeIcon"], lambda: (
							DATA["fileIcons"].pop(self.path), 
							elem["tabBar"].update(), 
							elem["tree"].update())
						)

					menu.addSeparator()
					menu.addRow("Rename file", ICON["rename"], lambda: self.scrollToIndex(rename=True))
					menu.addSeparator()
					menu.addRow("Delete file", ICON["delete"], lambda: elem["tree"].deleteItems(self.path))
			menu.exec(e.globalPos())






	def closeTabs(self, tabList):
		if tabList and self.parent().getTabState(save=True, tabList=tabList):
			[self.parent().closeTab(i.widget(), ignoreSave=True) for i in tabList]




	def scrollToIndex(self, rename=False):
		tree = elem["tree"]
		tree.focused = tree.model().index(self.path)

		if not rename:
			tree.revealTime.start()
		else:
			tree.editNewIndex = tree.focused
		tree.scrollTo(tree.focused, QAbstractItemView.ScrollHint.EnsureVisible)
		tree.update()

































class TabBar(QWidget):
	def __init__(self):
		super().__init__()
		elem["tabBar"] = self
		self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
		self.setObjectName("tabs")


		self.layout = FlowLayout()

		self.newTab = QPushButton(ICON["plus"])
		self.newTab.clicked.connect(self.addTab)
		self.newTab.setObjectName("new-tab")
		self.newTab.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)



		self.tip = DragTooltip()
		self.currentTab = QWidget()
		self.setMouseTracking(True)
	

		self.layout.addWidget(self.newTab)
		self.setLayout(self.layout)





		for seq, func in [
		("Ctrl+Tab", self.switchTab),
		("Ctrl+Shift+Tab", lambda: self.switchTab(isNext=False)),
		(QKeySequence.StandardKey.Close, lambda: self.closeTab(self.currentTab)),
		(QKeySequence.StandardKey.AddTab, self.addTab),
		(QKeySequence.StandardKey.New, self.addTab),
		]:
			(s := QShortcut(seq, self)).setAutoRepeat(False)
			s.activated.connect(lambda func=func: func() if not elem["settings"].isVisible() else None)

	











	def showEvent(self, e):
		self.setFixedHeight(int(PREFS["fontSize"] * SC_FACTOR["tabHeight"]))

		margin = PARAM["margin"]
		self.layout.setContentsMargins(0,margin,0,0)
		self.newTab.setFixedWidth(self.height() - margin)

		for i in self.layout.itemList[:-1]:
			i.widget().showEvent(None)
		self.tabStack.currentWidget().textWidget.showEvent(None)



	def mouseMoveEvent(self, e):
		super().mouseMoveEvent(e)
		if not self.childAt(e.pos()) or self.childAt(e.pos()) == self.newTab:
			self.tip.hide()

	def leaveEvent(self, e):
		super().leaveEvent(e)
		self.tip.hide()
		self.layout.keepWidth = False
		self.layout.update()



	def resizeEvent(self, e):
		super().resizeEvent(e)
		if self.layout.keepWidth:
			self.leaveEvent(QEvent(QEvent.Type.Leave))










	def addTab(self, path=None):
		self.layout.addWidget(Tab(path or None))
		self.tabStack.addWidget(TabPane(path or None))
		self.selectTab(self.layout.itemList[-2].widget())



	def selectTab(self, widget):
		for i in [self.currentTab, widget]:
			i.update()
			# redraw tab separator
			if (item := self.layout.itemAt(self.layout.indexOf(i) - 1)):
				item.widget().update()


		self.currentTab.leaveEvent(None)
		widget.enterEvent(None)
		self.tabStack.setCurrentIndex(index := self.layout.indexOf(widget))

		if index >= 0:
			self.tabStack.widget(index).textWidget.setFocus()

			if elem["main"].validDir():
				elem["tree"].update()
			self.currentTab = widget










	def setCurrentTab(self, path):
		index = self.layout.indexOf(self.currentTab)
		if not self.saveNote(self.currentTab.path, self.tabStack.widget(index).textWidget):
			return

		self.addTab(path)
		self.closeTab(self.layout.itemList[index].widget(), ignoreSave=True)

		takeAt = len(self.layout.itemList) - 2
		self.layout.insertItem(index, self.layout.takeAt(takeAt))
		self.tabStack.insertWidget(index, self.tabStack.widget(takeAt))

		self.leaveEvent(QEvent(QEvent.Type.Leave))
		self.selectTab(self.layout.itemList[index].widget())






	def switchTab(self, isNext=True):
		index = self.layout.indexOf(self.currentTab)
		self.selectTab(self.layout.itemList[(index + (1 if isNext else -1)) % (len(self.layout.itemList) - 1)].widget())
	









	def closeTab(self, widget, ignoreSave=False):
		if (tabPane := self.tabStack.widget(index := self.layout.indexOf(widget))).img:
			tabPane.img = None
		else:
			if not ignoreSave and not self.saveNote(widget.path, tabPane.textWidget, widget):
				return

		self.layout.removeWidget(widget)
		self.tabStack.removeWidget(tabPane)
		tabPane.deleteLater()


		itemLen = len(self.layout.itemList) - 1
		if not itemLen:
			self.addTab()
			index = 0
		elif itemLen == index:
			self.leaveEvent(QEvent(QEvent.Type.Leave))
			index = -2

		# if animation
		# (nextWidget := self.layout.itemList[index].widget()).enterEvent(None)
		if widget == self.currentTab:
			self.selectTab(self.layout.itemList[index].widget())











	def getTabState(self, save=False, tabList=False):
		if not save:
			tabState = DATA["tabState"] if "tabState" in DATA and DATA["tabState"] else [None]
			[self.addTab(i if i and os.path.exists(i) else None) for i in tabState]
		else:
			for i in (tabList or self.layout.itemList[:-1]):
				if not self.saveNote(i.widget().path, self.tabStack.widget(self.layout.indexOf(i)).textWidget, i.widget()):
					return False

			if not tabList:
				DATA["tabState"] = [os.path.normpath(path) if (path := i.widget().path) else None for i in self.layout.itemList[:-1]]
			return True





	def saveNote(self, path, textWidget, tab=False, shortcut=False):
		if not textWidget.parent().img:
			if re.search("\S", textWidget.toPlainText()) or shortcut:
				if not path or not os.path.exists(path):
					tab = tab or self.currentTab
					if not shortcut:
						if (result := Dialog(self, tab.label.text()).result()) != 2:
							return result


					root = DATA["folderPath"] if elem["main"].validDir() else ""
					path, _ = QFileDialog.getSaveFileName(self, "Save As", os.path.join(root, f"{tab.label.text()}.md"), "Markdown (*.md *.markdown *.mdown);;Plain Text (*.txt);;All Files (*.*)")
					if path:
						self.writeContents(path, textWidget)


						# close duplicate tab if user has overwritten the file
						for n, i in enumerate(self.layout.itemList[:-1]):
							paneWidget = self.tabStack.widget(n).textWidget

							if i.widget().path and os.path.normpath(i.widget().path) == os.path.normpath(path) and not paneWidget == textWidget:
								self.closeTab(i.widget())
								break
						tab.setPath(path)

					else:
						return False
		return True





	def writeContents(self, path, textWidget):
		# text = ""
		# for i in range(textWidget.document().blockCount()):
		#     block = textWidget.document().findBlockByNumber(i)

		#     if block.isVisible() and not block.userState() == 10:
		#         if block.text() == "\ufffc":
		#         text += textWidget.document().findBlockByNumber(i).text() + "\n"

		with open(path, "w", encoding="utf-8") as f:
			# skip over ￼ character that replaces an image
			f.write("\n".join([line for line in textWidget.toPlainText().splitlines() if line != "\ufffc"]))






















class Tabs(QWidget):
	def __init__(self):
		super().__init__()
		elem["tabs"] = self
		self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

		layout = QVBoxLayout()
		layout.setContentsMargins(QMargins())
		layout.setSpacing(0)


		tabBar = TabBar()
		tabBar.tabStack = QStackedWidget()

		layout.addWidget(tabBar)
		layout.addWidget(tabBar.tabStack)
		layout.addWidget(FindText(self))
		# layout.addWidget(ReplaceText(self))
		self.setLayout(layout)

		tabBar.getTabState()























































class ReplaceInput(QLineEdit):
	def __init__(self, parent):
		super().__init__(parent)
		self.contextMenuEvent = lambda _: None


	def paintEvent(self, e):
		super().paintEvent(e)

		if not self.text():
			(p := QPainter(self)).setPen(QColor(COLOR["mid"]))
			p.drawText(self.rect().translated(3 + PARAM["margin"],0), Qt.AlignmentFlag.AlignVCenter, f"Replace with")
			p.end()










class SearchInput(QLineEdit):
	def __init__(self, parent):
		super().__init__(parent)
		self.contextMenuEvent = lambda _: None
		self.prevWidth = 0



	def paintEvent(self, e):
		super().paintEvent(e)
		p = QPainter(self)
		text = f"{self.parent().count + 1} / {len(self.parent().selections)}"
		p.drawText(self.rect().adjusted(0,0,-PARAM["margin"],0), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, text)

		width = p.fontMetrics().horizontalAdvance(text) + PARAM["margin"]
		if self.prevWidth != width:
			self.setTextMargins(0,0,width,0)
			self.prevWidth = width
		p.end()

















class FindText(QWidget):
	def __init__(self, parent):
		super().__init__(parent)
		self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
		self.setObjectName("findText")
		elem["findText"] = self


		separator = lambda: (s := QFrame()).setObjectName("separator-fixed") or s.setFixedWidth(1) or s


		self.layout = QHBoxLayout()
		self.layout.setSpacing(0)
		self.layout.setContentsMargins(QMargins())

		self.textWidget = QWidget()





		self.case = QPushButton(ICON["case"])
		self.regex = QPushButton(ICON["regex"])
		for i in (self.case, self.regex):
			i.setCheckable(True)
			i.toggled.connect(self.searchText)


		self.search = SearchInput(self)
		self.search.setObjectName("input")
		self.search.textChanged.connect(lambda _: self.debounce.start())

		self.debounce = QTimer(self)
		self.debounce.setSingleShot(True)
		self.debounce.setInterval(300)
		self.debounce.timeout.connect(self.searchText)







		self.replace = ReplaceInput(self)
		self.replace.setObjectName("input")
		self.replace.returnPressed.connect(lambda: self.replaceSelection(False))

		for i in (replaceOne := QPushButton(ICON["replace"]), replaceAll := QPushButton(ICON["replaceAll"])):
			i.clicked.connect(lambda e, i=i: self.replaceSelection(i == replaceAll))


		self.replaceElems = [
		self.replace, 
		replaceOne, 
		replaceAll, 
		(line := separator()), 
		]

		self.showReplace = lambda: (
			self.showSearch(), 
			[i.show() for i in self.replaceElems], 
			self.replace.setFocus(), 
			self.replace.selectAll())






		for i in (prevBtn := QPushButton(ICON["prev"]), nextBtn := QPushButton(ICON["next"])):
			i.clicked.connect(lambda e, i=i: self.focusSelection(i == nextBtn))


		(close := QPushButton(ICON["close"])).clicked.connect(self.hide)

		for i in (
			self.case, 
			self.regex, 
			self.search,
			self.replace,
			replaceOne,
			replaceAll,
			line,
			prevBtn, 
			nextBtn, 
			close
			):
			if i not in [self.search, line, self.replace]:
				i.setObjectName("icon-button")
			self.layout.addWidget(i)


		self.setLayout(self.layout)
		self.hide()




		[QShortcut(s, self).activated.connect(lambda: self.focusSelection(True)) for s in ("Ctrl+G", "F3")]
		[QShortcut(s, self).activated.connect(lambda: self.focusSelection(False)) for s in ("Ctrl+Shift+G", "Shift+F3")]
		QShortcut("Ctrl+Alt+Return", self.replace).activated.connect(lambda: self.replaceSelection(True))












	def showEvent(self, e):
		self.layout.setContentsMargins(margin := PARAM["margin"],margin,margin,margin)
		self.layout.setSpacing(margin)


	def showSearch(self):
		self.show()
		for i in self.replaceElems:
			i.hide()


		self.textWidget = elem["tabBar"].tabStack.currentWidget().textWidget
		if isinstance(self.textWidget, QTextEdit) and (cursor := self.textWidget.textCursor()).hasSelection():
			self.search.setText(cursor.selectedText())
			
		self.search.setFocus()
		self.search.selectAll()
		self.searchText()









	def searchText(self):
		canSearch = isinstance(self.textWidget, QTextEdit)
		self.count = -1
		self.selections = []




		if (text := self.search.text()) and canSearch:
			text = QRegularExpression(text) if self.regex.isChecked() else text
			flags = QTextDocument.FindFlag.FindCaseSensitively if self.case.isChecked() else QTextDocument.FindFlag(0)



			cursorMatch = lambda pos: self.textWidget.document().find(text, pos, flags)
			match = cursorMatch(0)
			while not match.isNull() and match.hasSelection():
				self.selections.append(self.extraSelection(match))
				match = cursorMatch(match.selectionEnd())

			self.textWidget.setExtraSelections(self.selections)
			if self.selections:
				self.focusSelection(True)


		elif not text and canSearch:
			self.textWidget.setExtraSelections([])
		self.search.update()
		self.textWidget.update()






	def extraSelection(self, cursor):
		selection = QTextEdit.ExtraSelection() 
		selection.format.setBackground(QColor(COLOR["highlight"]))
		selection.cursor = cursor
		return selection










	def focusSelection(self, focusNext):
		if self.selections:
			try:
				textWidget = self.textWidget
				self.count = (self.count + (1 if focusNext else -1 if self.count >= 0 else 0)) % len(self.selections)


				cursor = self.selections[self.count].cursor
				rect = textWidget.cursorRect(cursor)

				scroll = textWidget.verticalScrollBar()
				scroll.setValue(rect.y() + scroll.value() - (textWidget.viewport().height() // 2) + (rect.height() // 2))
				textWidget.setTextCursor(cursor)

			# if tab becomes deleted
			except:
				self.searchText()

		self.search.update()
		self.textWidget.update()








	def replaceSelection(self, all):
		if self.selections:
			if not all:
				self.selections.pop(self.count).cursor.insertText(self.replace.text())
				self.count -= 1
				try:
					self.textWidget.setExtraSelections(self.selections)
				except:
					pass
				self.focusSelection(True)


			else:
				while self.selections:
					cursor = self.selections.pop(0).cursor
					cursor.joinPreviousEditBlock()
					cursor.insertText(self.replace.text())
					cursor.endEditBlock()
				self.searchText()






	def hide(self):
		self.setVisible(False)

		for i in elem["tabBar"].layout.itemList[:-1]:
			if not (tabPane := elem["tabBar"].tabStack.widget(elem["tabBar"].layout.indexOf(i))).img:
				tabPane.textWidget.setExtraSelections([])
		try:
			self.textWidget.setFocus()
		except:
			pass
















































class TabPane(QWidget):
	def __init__(self, path):
		super().__init__()

		if str(path).lower().endswith(tuple(PARAM["imgType"])):
			self.textWidget = QWidget(self)
			self.img = QImage(path)
			self.img = self.img.scaledToWidth(min(self.img.width(), self.width()), Qt.TransformationMode.SmoothTransformation)
			self.zoom = 0

			if not self.img.isNull():
				self.paintEvent = self.drawImage
			self.pos = QPoint()


		else:
			self.img = None

			self.layout = QVBoxLayout()
			self.layout.setContentsMargins(QMargins())
			self.layout.setSpacing(0)

			self.textWidget = Text(self, path)
			self.layout.addWidget(self.textWidget)
			self.setLayout(self.layout)









	def wheelEvent(self, e):
		if self.img:
			self.zoom = self.zoom or 1
			factor = 1.15

			self.zoom = max(0.1, min(self.zoom * (factor if e.angleDelta().y() > 0 else 1 / factor), 10.0))
			self.update()
		super().wheelEvent(e)


	def resizeEvent(self, e):
		self.zoom = 0
		self.pos = QPoint()
		super().resizeEvent(e)





	def mousePressEvent(self, e):
		if self.img and not self.img.isNull():
			self.startPos = e.pos()
			self.imgPos = self.imgRect.center()

	def mouseMoveEvent(self, e):
		if self.img and not self.img.isNull():
			self.pos = e.pos()
			self.update()
		
		
	def drawImage(self, e):
		p = QPainter(self)
		rect = self.rect()
		self.imgRect = imgRect = self.img.rect()

		imgWidth = min(imgRect.width(), rect.width())
		imgHeight = min(imgRect.height(), rect.height())



		if not self.zoom:
			if imgWidth >= rect.width():
				imgRect.setSize(QSize(imgWidth, int(imgWidth * (imgRect.height() / imgRect.width()))))

			if imgRect.height() >= rect.height():
				imgRect.setSize(QSize(int(imgHeight * (imgRect.width() / imgRect.height())), imgHeight))

		else:
			imgWidth = int(imgWidth * self.zoom)
			imgRect.setSize(QSize(imgWidth, int(imgWidth * (imgRect.height() / imgRect.width()))))



		imgRect.moveCenter(rect.center() if not self.pos else self.pos - (self.startPos - self.imgPos))
		p.drawImage(imgRect, self.img)
		p.end()








