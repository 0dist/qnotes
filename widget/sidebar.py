




from main import *





























class DelegateTree(QStyledItemDelegate):
	def initStyleOption(self, option, index):
		super().initStyleOption(option, index)
		option.decorationSize = QSize(0,0)

		self.closeEditor.connect(lambda editor, hint: (setattr(self.parent(), "focused", QModelIndex()), self.parent().update()) if hint in (QAbstractItemDelegate.EndEditHint.NoHint, QAbstractItemDelegate.EndEditHint.RevertModelCache) else None)





	def sizeHint(self, option, index):
		size = super().sizeHint(option, index)
		return QSize(size.width(), int(PREFS["fontSize"] * SC_FACTOR["rowHeight"]))


	def createEditor(self, parent, option, index):
		editor = QLineEdit(parent)
		editor.contextMenuEvent = lambda e: None
		editor.setTextMargins(-2,0,0,0)
		return editor


	def updateEditorGeometry(self, editor, option, index):
		try:
			editor.setGeometry(rect := option.rect.adjusted(self.parent().visibleIndexes[index]["xText"], 0, -self.parent().viewMargin, 0))
			editor.setFixedWidth(rect.width())
		# out of the viewport
		except:
			pass


	def paint(self, p, option, index):
		pass
			

















class TreeModel(QFileSystemModel):
	def __init__(self):
		super().__init__()
		self.setReadOnly(False)
		self.setRootPath(DATA["folderPath"])

		self.setNameFilters([f"*.{i}" for i in ["md", "markdown", "mdown", "txt", *PARAM["imgType"]]])
		self.setNameFilterDisables(False)





	def data(self, index, role):
		if role in (0,2):
			return self.fileInfo(index).completeBaseName() if not self.isDir(index) else self.fileInfo(index).fileName()
		return super().data(index, role)



	# initialize the index handle after the file has been created and sorted, then, in drawing, enter renaming mode
	def sort(self, column, order):
		super().sort(column, order)


		if (tree := elem["tree"]).editNewIndex:
			index = self.index(tree.editNewIndex)
			if tree.isExpanded(index.parent()) or tree.rootIndex() == index.parent():

				tree.scrollTo(index, QAbstractItemView.ScrollHint.EnsureVisible)
				tree.focused = tree.editNewIndex = index
			else:
				tree.editNewIndex = False























class FolderTree(QTreeView):
	def __init__(self):
		super().__init__()
		self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
		self.setObjectName("tree")
		elem["tree"] = self



		# self.installEventFilter(self)


		self.setItemDelegate(DelegateTree(self))
		self.setUniformRowHeights(True)
		self.setHeaderHidden(True)
		self.setDragEnabled(True)
		self.setExpandsOnDoubleClick(False)
		self.setUniformRowHeights(True)
		self.setDropIndicatorShown(False)
		self.setIndentation(0)

		self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
		self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
		self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)



		self.tooltip = DragTooltip(self)

		self.setModel(model := TreeModel())
		self.setRootIndex(model.index(DATA["folderPath"]))
		self.root = self.rootIndex()
		[self.hideColumn(i) for i in range(1,4,1)]


		model.layoutChanged.connect(lambda: self.setUpdatesEnabled(True) if not self.restore and not self.restoreLast else None)
		model.directoryLoaded.connect(self.updateOnLoad)


		self.getActiveTabs = lambda: [(path, tab) for i in elem["tabBar"].layout.itemList[:-1] if (path := (tab := i.widget()).path) and os.path.exists(path)]





		self.lastPressed = QModelIndex()
		self.focused = QModelIndex()
		self.dragged = QModelIndex()



		self.restore = []
		self.restoreLast = False
		self.restoreNote = []
		self.restoreIcons = []

		self.rowsToDraw = []
		self.selectedItems = []


		# expand folder on hover while dragging
		self.expandTime = QTimer(self)
		self.expandTime.setInterval(1000)
		self.expandTime.timeout.connect(lambda: (self.expand(self.indexAt(self.mapFromGlobal(QCursor.pos()))), self.expandTime.stop()))


		self.revealTime = QTimer(self)
		self.revealTime.setInterval(1200)
		self.revealTime.setSingleShot(True)
		self.revealTime.timeout.connect(lambda: (setattr(self, "focused", QModelIndex()), self.update()))





		self.editNewIndex = False

		self.scrollDecay = 0.6
		self.delta = 0
		self.scrollTimer = QTimer(self)
		self.scrollTimer.timeout.connect(self.scroll)
		self.setAutoScroll(False)


		self.getTreeState()




















	def showEvent(self, e):
		self.viewMargin = PARAM["margin"]


		fontSize = PREFS["fontSize"]
		iconMargin = int(fontSize / SC_FACTOR["treeIconMrgn"])
		iconFont = QFont(PARAM["iconName"], int(fontSize / SC_FACTOR["treeIconScale"]))

		self.iconMetrics = {
		"iconWidth": QFontMetrics(iconFont).height() + iconMargin,
		"iconFont": iconFont,
		"imgFont": QFont(PARAM["iconName"], int(fontSize / SC_FACTOR["imgIconScale"])),
		"materialFont": QFont("Material Symbols Outlined")
		}








	def wheelEvent(self, e):
		# scroll length
		self.delta += e.angleDelta().y() / 5
		# scroll speed
		self.scrollTimer.start(10)


	def scroll(self):
		self.verticalScrollBar().setValue(int(self.verticalScrollBar().value() - self.delta))

		self.delta *= self.scrollDecay
		if abs(self.delta) < 1:
			self.scrollTimer.stop()












	def mouseReleaseEvent(self, e):
		index = self.indexAt(e.position().toPoint())
		if e.button() == Qt.MouseButton.LeftButton:			
			if (key := elem["app"].keyboardModifiers()):


				if key == Qt.KeyboardModifier.ControlModifier:
					if self.selectedItems or self.model().isDir(index):
						self.selectedItems = list(set(self.selectedItems) ^ {index})
						self.lastPressed = index
						print("selected", len(self.selectedItems))
					else:
						self.checkDuplicateTab(index, newTab=True)



				elif key == Qt.KeyboardModifier.ShiftModifier and self.rowHeight(self.lastPressed):
					isBelow = self.visualRect(index).y() > self.visualRect(self.lastPressed).y()
					getIndex = self.indexBelow if isBelow else self.indexAbove

					self.selectedItems = [self.lastPressed]
					if self.lastPressed != index:
						nextIndex = self.lastPressed
						while nextIndex := getIndex(nextIndex):
							self.selectedItems.append(nextIndex)
							if nextIndex == index:
								break

			else:
				self.selectedItems = []
				if self.model().isDir(index):
					self.setExpanded(index, not self.isExpanded(index))
				else:
					self.checkDuplicateTab(index)



				self.lastPressed = index
		self.viewport().update()




	def checkDuplicateTab(self, index, newTab=False, path=False):
		filePath = path or self.model().filePath(index)
		for path, tab in self.getActiveTabs():
			if os.path.samefile(filePath, path):
				elem["tabBar"].selectTab(tab)
				break
		else:
			elem["tabBar"].addTab(filePath) if newTab else elem["tabBar"].setCurrentTab(filePath)











	def mousePressEvent(self, e):
		if e.buttons() == Qt.MouseButton.LeftButton:
			self.dragStartPos = e.pos()

		self.focused = QModelIndex()
		self.viewport().update()



	def mouseMoveEvent(self, e):
		if e.buttons() == Qt.MouseButton.LeftButton and (e.pos() - self.dragStartPos).manhattanLength() > QApplication.startDragDistance():
			self.setState(QTreeView.State.DraggingState)

			
			drag = QDrag(self)
			mimeData = QMimeData()
			index = self.indexAt(self.dragStartPos)

			if self.selectedItems:
				mimeData.setUrls([QUrl.fromLocalFile(self.model().filePath(index)) for index in self.selectedItems])
			else:
				self.dragged = index
				mimeData.setUrls([QUrl.fromLocalFile(self.model().filePath(index))])

			drag.setMimeData(mimeData)
			try:
				drag.exec()
			finally:
				self.setState(QTreeView.State.NoState)
				self.dragStartPos = QPoint()
				self.dragged = QModelIndex()





	def dragEnterEvent(self, e):
		e.accept() if e.mimeData().hasUrls() and self.state() == QTreeView.State.DraggingState else e.ignore()
		self.viewport().update()

	def dragLeaveEvent(self, e):
		self.viewport().update()

	def dragMoveEvent(self, e):
		e.ignore() if not self.indexAt(e.position().toPoint()) in self.visibleIndexes else e.accept()
		self.viewport().update()









	def dropEvent(self, e):
		if e.buttons() == Qt.MouseButton.NoButton:
			dropPath = self.model().filePath(self.dropIndex)
			paths = [os.path.normpath(u.toLocalFile()) for u in e.mimeData().urls()]

			for url in e.mimeData().urls():
				dropFrom = os.path.normpath(url.toLocalFile())
				dropTo = os.path.join(dropPath, url.fileName())

				# move only parent folder if its children are selected
				parent = dropFrom
				while (parent := os.path.dirname(parent)) != DATA["folderPath"] and parent:
					if parent in paths:
						break
				else:
					# and if not moving into itself
					if not os.path.exists(dropTo) and os.path.commonpath([dropFrom, dropTo]) != dropFrom:
						self.renameFile(dropFrom, dropTo, self.model().index(dropFrom))

			self.selectedItems = []






	def commitData(self, editor):
		model = self.model()

		oldPath = os.path.normpath(model.filePath(index := self.focused))
		fileName = f"{editor.text()}.{model.fileInfo(index).suffix()}" if not model.isDir(index) else editor.text()
		newPath = os.path.join(model.filePath(index.parent()), fileName)

		self.renameFile(oldPath, newPath, index)
		self.focused = QModelIndex()







	def renameFile(self, oldPath, newPath, index):
		if not os.path.exists(newPath):
			try:
				self.checkExpanded(index, oldPath, newPath)
				shutil.move(oldPath, newPath)


				for path, tab in self.restoreNote:
					tab.setPath(path)
				for oldPath, newPath, icon in self.restoreIcons:
					DATA["fileIcons"][os.path.normpath(newPath)] = icon
					DATA["fileIcons"].pop(oldPath, None)



			except OSError as e:
				print(e)
				# if locked by another process
				if os.path.exists(newPath):
					if os.path.isdir(newPath):
						shutil.copytree(newPath, oldPath, dirs_exist_ok=True)
						shutil.rmtree(newPath)
					else:
						os.remove(newPath)
				self.setUpdatesEnabled(True)
				self.restore = []
			self.restoreNote, self.restoreIcons = [], []









	def checkExpanded(self, index, oldPath, newPath):
		# disalbe updates to prevent potential flickering animations, then re-enable on layoutChanged/updateOnLoad
		if self.isExpanded(self.model().index(parent := os.path.dirname(newPath))) or os.path.samefile(parent, DATA["folderPath"]):
			self.setUpdatesEnabled(False)


		checkPaths = []
		checkPaths.append((oldPath, newPath))





		if self.model().isDir(index):
			makePath = lambda parent, dir: os.path.join(os.path.dirname(parent), os.path.basename(dir))

			pattern = makePath(oldPath, oldPath)
			replace = makePath(oldPath if os.path.samefile(os.path.dirname(oldPath), os.path.dirname(newPath)) else newPath, newPath)



			newDirs = []
			for root, dirs, files in os.walk(oldPath):
				for f in files:
					filePath = os.path.join(root, f)
					newFilePath = filePath.replace(pattern, replace)
					checkPaths.append((filePath, newFilePath))


				for d in dirs:
					dirPath = os.path.join(root, d)
					newDirPath = dirPath.replace(pattern, replace)

					if self.isExpanded(self.model().index(dirPath)):
						newDirs.append(newDirPath)
					checkPaths.append((dirPath, newDirPath))


			if self.isExpanded(index) and os.listdir(oldPath):
				self.restore = [newPath, *newDirs]





		for oldPath, newPath in checkPaths:
			for path, tab in self.getActiveTabs():
				if os.path.samefile(oldPath, path):
					self.restoreNote.append((newPath, tab))

			if oldPath in DATA.get("fileIcons", []):
				self.restoreIcons.append((oldPath, newPath, DATA["fileIcons"][oldPath]))














	def updateOnLoad(self, path):
		if os.path.exists(path):
			if self.restoreLast:
				if os.path.samefile(self.restoreLast, path):
					self.restoreLast = False
					self.setUpdatesEnabled(True)

			if self.restore:
				self.expand(self.model().index(path := self.restore.pop(0)))
				if not self.restore:
					self.restoreLast = path
	




















	def drawRow(self, p, option, index):
		self.rowsToDraw.append(index)



	def drawRows(self, painter=False):
		p = painter or QPainter(self.viewport())

		indexStart = self.indexAt(QPoint(0,0))
		fontSize = PREFS["fontSize"]
		guides = []




		[self.selectedItems.remove(i) for i in self.selectedItems if not self.rowHeight(i)]
		# unite selections
		if not painter:
			viewport = self.viewport().rect().adjusted(0, -fontSize, 0, fontSize)
			selections = [self.visualRect(i) for i in sorted(self.selectedItems, key=lambda index: self.visualRect(index).y()) if viewport.intersects(self.visualRect(i))]
			if selections:
				combRect = selections[0]
				for rect in selections[1:]:
					if combRect.intersects(rect.adjusted(0,-1,0,0)):
						combRect = combRect.united(rect)
					else:
						self.paintSelection(p, combRect)
						combRect = rect
				self.paintSelection(p, combRect)






		for index in self.rowsToDraw:
			rect = self.visualRect(index)
			lvl = self.indexLevel(index)
			filePath = os.path.normpath(self.model().filePath(index))


			if index == indexStart:
				self.visibleIndexes = {}

			[self.paintSelection(p, rect, focus=b) for i, b in ((self.focused, True), (self.dragged, False)) if i == index]

			if (tabPath := elem["tabBar"].currentTab.path) and filePath == os.path.normpath(tabPath):
					self.paintSelection(p, rect)






			# p.drawRect(rect)
			iconWidth = self.iconMetrics["iconWidth"]
			x = xIcon = self.viewMargin + (iconWidth * lvl)
			y = rect.y()
			height = rect.height()



			if PREFS["treeGuides"]:
				guides.extend(QLineF(xGuide := x - iconWidth * (i + 1.5), y, xGuide, y + height) for i in range(lvl - 1))


			if self.model().isDir(index):
				p.save()
				p.setFont(self.iconMetrics["iconFont"])

				x = xIcon = self.viewMargin + (iconWidth * (lvl - 1))
				p.drawText(QRectF(x, y, iconWidth, height), Qt.AlignmentFlag.AlignCenter, ICON["collapsed" if not self.isExpanded(index) else "expanded"])

				x += iconWidth
				p.restore()




			if str(filePath).lower().endswith(tuple(PARAM["imgType"])):
				x = self.drawIcon(p, self.iconMetrics["imgFont"], ICON["img"], x, y, iconWidth, height)


			if filePath in DATA.get("fileIcons", []):
				icon = chr(int(DATA["fileIcons"][filePath], 16))
				x = self.drawIcon(p, self.iconMetrics["materialFont"], icon, x, y, iconWidth, height)



			# prevent text stacking since edit input has transparent background
			if self.state() != QAbstractItemView.State.EditingState or index != self.focused:
				elided = p.fontMetrics().elidedText(index.data(0), Qt.TextElideMode.ElideRight, rect.width() - x - self.viewMargin);
				p.drawText(QRectF(x, y, rect.width(), height), Qt.AlignmentFlag.AlignVCenter, elided)



			if index.isValid():
				self.visibleIndexes[index] = {"x": xIcon, "xText": x, "iconWidth": iconWidth}

				if index == self.editNewIndex:
					self.edit(index)
					self.editNewIndex = False
			self.rowsToDraw = []



		p.setPen(QColor(COLOR["hovered"]))
		p.drawLines(guides)
		p.end() if not painter else None


















	def indexLevel(self, index):
		lvl = 1
		while (index := index.parent()) != self.root:
			lvl += 1
		return lvl



	def drawIcon(self, p, font, icon, x, y, iconWidth, height):
	    p.save()
	    p.setFont(font)
	    p.drawText(QRectF(x, y, iconWidth, height), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, icon)
	    p.restore()

	    return x + iconWidth




	def paintSelection(self, p, rect, focus=False):
		p.save()
		p.setRenderHint(QPainter.RenderHint.Antialiasing)
		if not focus:
			p.setPen(Qt.PenStyle.NoPen)
			p.setBrush(QBrush(QColor(COLOR["hovered"]), Qt.BrushStyle.SolidPattern))
		else:
			p.setPen(QPen(QColor(COLOR["hovered"]), 2))


		# adjust rectange according to the pen's width
		shift = p.pen().width() // 2
		p.drawRoundedRect(rect.adjusted(self.viewMargin + shift, shift, -self.viewMargin - shift, -shift), PARAM["bdRadius"], PARAM["bdRadius"])
		p.restore()























	def paintEvent(self, e):
		super().paintEvent(e)
		self.drawRows()
		if self.state() == QAbstractItemView.State.DraggingState:
			p = QPainter(self.viewport())
			p.setRenderHint(QPainter.RenderHint.Antialiasing)
			p.setPen(Qt.PenStyle.NoPen)

			dropColor = QColor(COLOR["foreground"])
			dropColor.setAlphaF(PARAM["dropAlpha"])
			p.setBrush(QBrush(dropColor, Qt.BrushStyle.SolidPattern))



			rect = self.visualRect(index := self.indexAt(pos := self.mapFromGlobal(QCursor.pos())))

			if not self.viewport().rect().contains(rect):
				self.scrollTo(index, QAbstractItemView.ScrollHint.EnsureVisible)



			if index in self.visibleIndexes:
				self.dropIndex = index
				if pos.x() < self.viewMargin:
					self.drawParentRows(p, self.root, root=True)
				else:
					if self.model().isDir(index):
						if not self.isExpanded(index):
							if self.checkHoverLimit(pos, index):
								self.hoverParent(p, index)
							else:
								p.drawRoundedRect(rect.adjusted(self.visibleIndexes[index]["x"], 0, -self.viewMargin, 0), PARAM["bdRadius"], PARAM["bdRadius"])
								self.expandTime.start()
						else:
							self.drawParentRows(p, index, rect) if not self.checkHoverLimit(pos, index) else self.hoverParent(p, index)
					else:
						self.hoverParent(p, index)



				self.tooltip.updateTooltip()
			else:
				self.tooltip.hide()
			p.end()

			


		elif self.tooltip.isVisible() and self.state() != QAbstractItemView.State.DraggingState:
			self.tooltip.hide()
			self.expandTime.stop()







	def checkHoverLimit(self, pos, index):
		return pos.x() < self.visibleIndexes[index]["x"]


	def hoverParent(self, p, index):
		parentIndex = index.parent()
		if parentIndex != self.root:
			if parentIndex in self.visibleIndexes:
				self.drawParentRows(p, parentIndex, self.visualRect(parentIndex))
			else:
				# validate the "x" reference that is out of the viewport
				self.rowsToDraw = [parentIndex]
				self.drawRows(p)
				self.drawParentRows(p, parentIndex, fromTop=True)
		else:
			self.drawParentRows(p, self.root, root=True)








	def drawParentRows(self, p, index=False, rect=False, fromTop=False, root=False):
		self.dropIndex = index


		x = self.visibleIndexes[index]["x"] if not root else 0
		xText = (x + self.visibleIndexes[index]["iconWidth"]) if not root else 0
		rect = self.visualRect(index := self.indexAt(QPoint(0,0))) if fromTop or root else rect


		endIndex = self.indexAt(QPoint(0, self.viewport().rect().bottom()))
		rows = 0
		while index != endIndex:
			if not (index := self.indexBelow(index)).isValid():
				break
			if not root:
				if xText >= self.visibleIndexes[index]["xText"]:
					break
			rows += 1
		p.drawRoundedRect(rect.adjusted(x, 0, -self.viewMargin, rect.height() * rows), PARAM["bdRadius"], PARAM["bdRadius"])


















	def contextMenuEvent(self, e):
		if (index := self.indexAt(e.pos())).isValid():
			if self.revealTime.isActive():
				self.revealTime.stop()
			self.focused = index


			
			menu = ContextMenu(self)
			path = os.path.normpath(self.model().filePath(index))


			if single := (len(self.selectedItems) < 2):
				if isDir := (self.model().isDir(self.indexAt(e.pos()))):
					menu.addRow("New note", ICON["newNote"], lambda: self.createItem(path))
					menu.addRow("New folder", ICON["newFolder"], lambda: self.createItem(path, folder=True))
					menu.addSeparator()
					

				menu.addRow("Rename", ICON["rename"], lambda: self.edit(index))
				if not isDir:
					menu.addRow("Duplicate", ICON["duplicate"], lambda: self.duplicateFile(path)) 
					menu.addSeparator()
					menu.addRow("Open in new tab", ICON["openInTab"], lambda: self.checkDuplicateTab(index, newTab=True))
				menu.addSeparator()
				menu.addRow("Show in folder", ICON["showInFolder"], lambda: self.revealItem(path))

				menu.addSeparator()
				menu.addRow("Set icon", ICON["addIcon"], lambda: IconPicker(self, e.globalPos(), path))
				if path in DATA.get("fileIcons", []):
					menu.addRow("Remove icon", ICON["removeIcon"], lambda: (DATA["fileIcons"].pop(path), elem["tabBar"].update()))
				menu.addSeparator()



			menu.addRow("Delete", ICON["delete"], lambda: self.deleteItems(path if single else None))
			menu.exec(e.globalPos())
			if self.state() == QTreeView.State.NoState:
				self.focused = QModelIndex()












	def createItem(self, path, folder=False):
		try:
			newPath = self.getNewName(path, f"Untitled{'.md' if not folder else ''}")
			open(newPath, "w").close() if not folder else os.makedirs(self.getNewName(path, newPath))
			self.editNewIndex = newPath

		except Exception as e:
			print(e)









	def duplicateFile(self, path):
		try:
			shutil.copy2(path, self.getNewName(os.path.dirname(path), os.path.basename(path)))
		except Exception as e:
			print(e)


	def getNewName(self, path, name):
		name, suffix = os.path.splitext(name)
		makePath = lambda i: os.path.join(path, f"{name}{' ' if i else ''}{i or ''}{suffix}")

		i = 0
		while os.path.exists(item := makePath(i)):
			i += 1
		else:
			return item






	def revealItem(self, path):
		path = os.path.normpath(path)
		match elem["platform"]:
			case "win32":
				subprocess.Popen(f'explorer /select, "{path}"')
			case "darwin":
				try:
					subprocess.run(["open", "-R", path], check=True)
				except subprocess.CalledProcessError as e:
					print(e)
					# open without selection
					subprocess.run(["open", os.path.dirname(path)])
			case "linux":
				try:
					subprocess.run(["xdg-open", "--select", path], check=True)
				except subprocess.CalledProcessError as e:
					print(e)
					subprocess.run(["xdg-open", os.path.dirname(path)])






	def deleteItems(self, filePath):
		activeTabs = self.getActiveTabs()
		model = self.model()
		filePaths = []


		for path in (paths := [os.path.normpath(filePath)] if filePath else [os.path.normpath(model.fileInfo(i).filePath()) for i in self.selectedItems]):
			
			# find a root folder in the selection if it has one
			parent = path
			while (parent := os.path.dirname(parent)) != DATA["folderPath"]:
				if parent in paths:
					break
			else:
				if model.isDir(index := model.index(path)):
					# delete every folder in the root folder
					folder = [path]
					for root, dirs, files in os.walk(path):
						for f in files:
							filePaths.append(os.path.normpath(os.path.join(root, f)))
						for d in dirs:
							folder.append(os.path.normpath(os.path.join(root, d)))

					while folder:
						print(len(folder))
						if not QFile.moveToTrash(folder.pop())[0]:
							break


				else:
					if QFile.moveToTrash(path)[0]:
						if index in self.selectedItems:
							self.selectedItems.remove(index)
						filePaths.append(path)



		for path in filePaths:
			if not os.path.exists(path):
				for tabPath, tab in activeTabs:
					if path == os.path.normpath(tabPath):
						elem["tabBar"].closeTab(tab, ignoreSave=True)
		if not filePath:
			self.selectedItems = []

















	def getTreeState(self, save=False):
		cTime = lambda path: int(str(os.path.getctime(path)).split(".")[1])

		if not save:
			state = DATA.get("treeState", [])
			for root, dirs, _ in os.walk(DATA["folderPath"]):
				for d in dirs:
					index = self.model().index(path := os.path.join(root, d))
					if cTime(path) in state:
						self.expand(index)
		else:
			state = []
			index = self.model().index(0,0, self.root)

			while index.isValid():
				path = self.model().filePath(index)

				if os.path.exists(path) and self.isExpanded(index):
					state.append(cTime(path))
				index = self.indexBelow(index)
				
			DATA["treeState"] = state














	# def eventFilter(self, obj, e):
	# 	if e.type() == QEvent.Type.KeyPress:
	# 		if e.key() == Qt.Key.Key_1:
	# 			pass
			





	# 	return False

























class InitFolder(QPushButton):
	def __init__(self):
		super().__init__()
		self.setObjectName("init-folder")
		self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
		self.setCursor(Qt.CursorShape.PointingHandCursor)
		self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

		self.setText("Select or Drop directory")
		self.setAcceptDrops(True)


		self.clicked.connect(lambda: self.setPath(path) if (path := QFileDialog.getExistingDirectory(self, "Select directory")) else None)
		self.dropEvent = lambda e: self.setPath(e.mimeData().urls()[0].toLocalFile())





	def dragEnterEvent(self, e):
		urls = e.mimeData().urls()
		if len(urls) == 1 and os.path.isdir(url := urls[0].toLocalFile()):
			self.setStyleSheet(f"background-color: {COLOR['mid']}")
			e.accept()

	def dragLeaveEvent(self, e):
		super().dragLeaveEvent(e)
		self.setStyleSheet("")


	def setPath(self, path):
		DATA["folderPath"] = os.path.normpath(path)
		elem["sidebar"].setFolder()


















class Sidebar(QWidget):
	def __init__(self):
		super().__init__()
		elem["sidebar"] = self
		self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
		self.setObjectName("sidebar")


		self.setFixedWidth(DATA.get("sidebarWidth", 300))
		if DATA.get("hideSidebar"):
			self.hide()



		self.wrapGrid = QGridLayout()
		self.wrapGrid.setContentsMargins(QMargins())








		self.grip = grip = QWidget()
		grip.setMinimumWidth(3)
		grip.setCursor(Qt.CursorShape.SplitHCursor)
		grip.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

		grip.mouseMoveEvent = self.resizeSidebar
		grip.enterEvent = lambda e: grip.setStyleSheet(f"background-color: {COLOR['mid']}")
		grip.leaveEvent = lambda e: grip.setStyleSheet("background-color: transparent")
		self.wrapGrid.addWidget(grip,0,0, Qt.AlignmentFlag.AlignRight)
	
		self.setLayout(self.wrapGrid)
		self.setFolder()









	def setFolder(self):
		for i in range(self.wrapGrid.count()):
			if (widget := self.wrapGrid.itemAt(i).widget()) != self.grip:
				if widget == elem.get("tree"):
					elem["tree"].model().deleteLater()
				widget.deleteLater()


		self.wrapGrid.addWidget(FolderTree() if elem["main"].validDir() else InitFolder(),0,0)
		self.grip.raise_()

		elem["main"].saveData()
		if "settings" in elem:
			elem["settings"].updateLabel()





	def resizeSidebar(self, e):
		x = self.mapFromGlobal(e.globalPosition().toPoint()).x()
		self.hide() if x < PREFS["fontSize"] * 2 else self.show()

		minWidth = PREFS["fontSize"] * SC_FACTOR["sidebarMin"]
		self.setFixedWidth(int(x := max(minWidth, min(x, minWidth * 2))))
		DATA.update(sidebarWidth=x, hideSidebar=not self.isVisible())








