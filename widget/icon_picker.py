


from main import *






























class GridLayout(QLayout):
	def __init__(self):
		super().__init__()
		self.setContentsMargins(QMargins())
		self.itemList = []
		self.baseHeight = 0



	def addItem(self, item):
		self.itemList.append(item)

	def count(self):
		return len(self.itemList)

	def itemAt(self, index):
		if index >= 0 and index < len(self.itemList):
			return self.itemList[index]

	def takeAt(self, index):
		if index >= 0 and index < len(self.itemList):
			return self.itemList.pop(index)

	def sizeHint(self):
		return self.minimumSize()

	def hasHeightForWidth(self):
		return True

	def minimumSize(self):
		return QSize(0,0)

	def heightForWidth(self, width):
		return self.baseHeight



	def setGeometry(self, rect):
		if self.itemList:
			rect.adjust((m := self.contentsMargins()).left(), m.top(), -m.right(), -m.bottom())
			baseWidth = rect.width()
			itemWidth = self.itemList[0].widget().sizeHint().width()
			x, y = rect.x(), rect.y()

			columns = round(baseWidth / itemWidth) if len(self.itemList) * itemWidth > baseWidth else len(self.itemList)


			width = (baseWidth + columns) / columns
			for item in self.itemList:
				# new row
				if x + width - m.right() > baseWidth + columns:
					x = rect.x()
					y += itemWidth - 1

				item.setGeometry(QRect(round(x), y, round(width), itemWidth))
				x += width - 1
			self.baseHeight = y + itemWidth + m.bottom()
















class IconView(QScrollArea):
	def __init__(self, parent, path):
		super().__init__()
		self.setWidgetResizable(True)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

		parent.iconLayout = layout = GridLayout()
		self.path = path

		container = QWidget()
		container.setLayout(layout)
		self.setWidget(container)



	def mouseReleaseEvent(self, e):
		if e.button() == Qt.MouseButton.LeftButton and (icon := self.viewport().childAt(e.pos()).property("icon")):
			DATA.setdefault("fileIcons", {})[self.path] = icon
			elem["tree"].update()
			elem["tabBar"].update()









class IconSearch(QLineEdit):
	def __init__(self):
		super().__init__()
		self.contextMenuEvent = lambda e: None


	def paintEvent(self, e):
		super().paintEvent(e)

		if not self.text():
			(p := QPainter(self)).setPen(QColor(COLOR["mid"]))
			p.drawText(self.rect().translated(2,0), Qt.AlignmentFlag.AlignVCenter, "Search icons")
			p.end()










	

class IconPicker(FramelessDialog): 
	def __init__(self, parent, pos, path):
		super().__init__(parent)
		self.move(pos)
		self.setResizable()



		self.icons = self.iconList = elem["main"].materialIcons
		self.pageCount = 100
		self.page = 0



		self.search = IconSearch()
		self.search.textChanged.connect(lambda _: self.debounce.start())

		self.debounce = QTimer()
		self.debounce.setSingleShot(True)
		self.debounce.setInterval(300)
		self.debounce.timeout.connect(self.searchIcons)






		self.navBtns = QHBoxLayout()
		self.countLabel = QLabel()
		self.countLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)



		for i in [prevPage := QPushButton(ICON["left"]), nextPage := QPushButton(ICON["right"])]:
			i.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
			i.setObjectName("icon-button")

		prevPage.clicked.connect(lambda: 
			(setattr(self, "page", max(0, self.page - self.pageCount)),
			self.populateLayout()))

		nextPage.clicked.connect(lambda: 
			(setattr(self, "page", min(math.ceil(len(self.iconList) // self.pageCount) * self.pageCount, self.page + self.pageCount)),
			self.populateLayout()))



		self.navBtns.addWidget(prevPage)
		self.navBtns.addWidget(self.countLabel)
		self.navBtns.addWidget(nextPage)





		self.view = IconView(self, path)

		self.layout.addWidget(self.search)
		self.layout.addWidget(self.view)
		self.layout.addLayout(self.navBtns)




		self.populateLayout()
		self.show()
		self.resize(QSize(PREFS["fontSize"], PREFS["fontSize"]) * SC_FACTOR["fontBoxSize"])












	def populateLayout(self):
		while self.iconLayout.count():
			self.iconLayout.takeAt(0).widget().deleteLater()


		for i in self.iconList[self.page : self.page + self.pageCount]:
			iconLabel = QLabel(chr(int(i["unicode"], 16)))
			iconLabel.setObjectName("icon-item")
			iconLabel.setProperty("icon", i["unicode"])
			iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
			self.iconLayout.addWidget(iconLabel)


		self.countLabel.setText(f"{str(self.page // self.pageCount + 1)} / {len(self.iconList) // self.pageCount + 1}")







	def searchIcons(self):
		self.page = 0

		if (text := self.search.text().lower()):
			self.iconList = [i for i in self.icons if text in i["name"].replace("_", " ").lower() or any(text in tag.lower() for tag in i["tags"])]
		else:
			self.iconList = self.icons
		self.populateLayout()
	
