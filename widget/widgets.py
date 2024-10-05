

from main import *




















class Separator(QFrame):
	def paintEvent(self, e):
		(p := QPainter(self)).drawLine(0, y := self.height() // 2, self.width(), y)
		p.end()

























class Dialog(QDialog):
	def __init__(self, parent, fileName):
		super().__init__(parent)
		self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
		self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)



		wrapLayout = QVBoxLayout()
		wrapLayout.setContentsMargins(QMargins())
		wrapLayout.addWidget(frame := QFrame())
		frame.setObjectName("dialog")

		self.layout = QVBoxLayout()




		self.msg = QLabel(f'Save changes to "<b>{fileName}</b>" before closing?')

		self.btnLayout = QHBoxLayout()
		self.btnLayout.addStretch()

		for n, i in enumerate(btns := [QPushButton(i) for i in ("Save", "Don't save", "Cancel")]):
			self.btnLayout.addWidget(i)
			i.clicked.connect(lambda _, n=n: self.done(len(btns) - 1 - n))
			i.setObjectName("dialog-btn")




		self.layout.addWidget(self.msg)
		self.layout.addLayout(self.btnLayout)

		frame.setLayout(self.layout)
		self.setLayout(wrapLayout)
		self.exec()









	def showEvent(self, e):
		self.layout.setContentsMargins(margin := PARAM["margin"],margin,margin,margin)
		self.layout.setSpacing(margin)

		self.msg.setMargin(margin * 2)
		self.btnLayout.setSpacing(margin)































class ContextRow(QPushButton):
	def __init__(self, parent, text, icon):
		super().__init__(parent)
		self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
		self.setObjectName("context-item")

		self.text = text
		self.icon = icon





	def showEvent(self, e):
		self.iconFont = QFont(PARAM["iconName"], PARAM["iconSize"])
		iconWidth = QFontMetrics(self.iconFont).height()
		margin = PARAM["margin"]


		x = int(margin * SC_FACTOR["ctxIconMrgn"]) + iconWidth
		self.textRect = QRect(QPoint(x, 0), QFontMetrics(self.font()).size(0, self.text)).adjusted(0, 0, margin, margin * 2)


		self.setMinimumSize(QSize(self.textRect.right(), self.textRect.height()))
		self.parent().layout().setContentsMargins(margin,margin,margin,margin)
		self.iconRect = QRectF(margin, 0, iconWidth, self.height())




	def paintEvent(self, e):
		p = QPainter(self)

		p.save()
		p.setFont(self.iconFont)
		p.drawText(self.iconRect, Qt.AlignmentFlag.AlignVCenter, self.icon)
		p.restore()

		p.drawText(self.textRect, Qt.AlignmentFlag.AlignVCenter, self.text)
		p.end()













class ContextMenu(QMenu):
	def __init__(self, parent):
		super().__init__(parent)
		self.setWindowFlags(self.windowFlags() | Qt.WindowType.NoDropShadowWindowHint| Qt.WindowType.FramelessWindowHint)
		self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
		self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
		self.setObjectName("context")

		# self.lines = []
		wrapLayout = QVBoxLayout()
		wrapLayout.setContentsMargins(QMargins())
		wrapLayout.addWidget(frame := QFrame())
		# frame.paintEvent = lambda e: self.drawSeparator(frame, e)

		self.itemLayout = QVBoxLayout()
		self.itemLayout.setSpacing(0)
		frame.setLayout(self.itemLayout)
		self.setLayout(wrapLayout)






	def paintEvent(self, e):
		super().paintEvent(e)
		if self.geometry().bottom() > self.screen().size().height():
			self.move(self.x(), self.y() - self.height())


	def addRow(self, title, icon, func):
		row = ContextRow(self, title, icon)
		row.clicked.connect(lambda: (self.close(), func()))
		self.itemLayout.addWidget(row)


	def addSeparator(self):
		(line := Separator()).setObjectName("ctx-separator")
		self.itemLayout.addWidget(line)
		# self.lines.append(line)



	# def drawSeparator(self, frame, e):
	# 	p = QPainter(frame)
	# 	for i in self.lines:
	# 		p.fillRect(QRectF(0, i.y() - 1 + i.height() / 2, frame.width(), 1), QBrush(QColor(COLOR["foreground"]), Qt.BrushStyle.SolidPattern))
	# 	p.end()


































class DragTooltip(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.ToolTip)
		self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
		self.setObjectName("tooltip")


		layout = QHBoxLayout()
		layout.setContentsMargins(QMargins())

		self.label = QLabel()
		layout.addWidget(self.label)
		self.setLayout(layout)




	def updateTooltip(self, text=False):
		self.label.setMargin(PARAM["margin"])
		self.label.setText(text or f"Move to <b>{self.parent().dropIndex.data(0)}</b>")
		
		pos = QCursor.pos()
		self.move(pos.x(), pos.y() + int(PREFS["fontSize"] * SC_FACTOR["ctxYPos"]))

		self.adjustSize()
		self.show() if self.isHidden() else None



























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

