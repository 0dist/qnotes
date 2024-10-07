



from main import *





























class Ribbon(QWidget):
	def __init__(self):
		super().__init__()
		elem["ribbon"] = self
		self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
		self.setObjectName("ribbon")

		separator = lambda: (s := QFrame()).setObjectName("separator-fixed") or s.setFixedHeight(1) or s





		self.layout = QVBoxLayout()
		self.btns = (
			sidebar := QPushButton(ICON["sidebar"]),
			newFile := QPushButton(ICON["newNote"]), 
			newFolder := QPushButton(ICON["newFolder"]), 
			treeState := QPushButton(),
			settings := QPushButton(ICON["settings"])
		)

		self.updateIcon = lambda: treeState.setText(ICON["collapseTree" if self.expanded else "expandTree"])



		self.threshold = QTimer(self)
		self.threshold.setInterval(200)
		self.threshold.setSingleShot(True)




		sidebar.clicked.connect(lambda: (
			(side := elem["sidebar"]).setVisible(side.isHidden()),
			DATA.update(hideSidebar=side.isHidden()),
			))




		[i.clicked.connect(lambda e, i=i: self.createItem(i == newFolder)) for i in (newFile, newFolder)]

		treeState.clicked.connect(lambda: self.toggleTree() if elem["main"].validDir() else None)
		settings.clicked.connect(lambda: (elem["tabs"].clearFocus(), elem["settings"].show()))




		for i in self.btns:
			self.layout.addWidget(i)

			if i == sidebar:
				self.layout.addWidget(separator())
			elif i == treeState:
				self.layout.addStretch()
			i.setObjectName("icon-button")
		self.setLayout(self.layout)


















	def showEvent(self, e):
		self.expanded = self.anyExpanded()
		self.updateIcon()

		self.layout.setContentsMargins(margin := PARAM["margin"],margin,margin,margin)
		self.layout.setSpacing(margin)




	def anyExpanded(self):
		if elem["main"].validDir():
			index = (tree := elem["tree"]).model().index(0,0, tree.root)

			while index.isValid():
				if tree.isExpanded(index):
					return True
					break
				index = tree.indexBelow(index)









	def createItem(self, folder):
		if not self.threshold.isActive() and elem["main"].validDir():
			elem["tree"].createItem(DATA["folderPath"], folder=folder)
			self.threshold.start()




	def toggleTree(self):
		elem["tree"].collapseAll() if self.expanded else elem["tree"].expandAll()
		self.expanded = not self.expanded
		self.updateIcon()














