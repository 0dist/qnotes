



from main import *

























class ImageObject(QObject, QTextObjectInterface):
	def __init__(self, parent, path):
		super().__init__(parent)
		self.path = path
		self.removed = False
		self.initImg()


	def initImg(self):
		self.img = QImage(self.path)
		self.img = self.img.scaledToWidth(min(self.img.width(), self.parent().viewport().width()), Qt.TransformationMode.SmoothTransformation)





	def intrinsicSize(self, doc, pos, format):
		if self.removed:
			self.initImg()
			print("init img from object")
			self.parent().highlighter.imgs.append({"block": (block := doc.findBlock(pos)), "pathBlock": block.previous(), "object": self, "path": self.path})
			self.removed = False


		if not self.img.isNull():
			width = self.img.width()
			newWidth = min(width, self.parent().viewport().width())
			return QSizeF(newWidth, int(newWidth * (self.img.height() / width)))
		else:
			return QSizeF(min(100, self.parent().viewport().width()),100)



	def drawObject(self, p, rect, doc, pos, format):
		if not self.img.isNull():
			p.drawImage(rect, self.img)
		else:
			p.drawRect(rect)
			p.drawText(rect, Qt.AlignmentFlag.AlignCenter, "\ufffd")
















class Syntax(QSyntaxHighlighter):
	def __init__(self, parent, doc):
		super().__init__(doc)
		self.textEdit = parent




		self.imgLink = "!\[(?:.+|)\]\((.+)\)$"
		self.img = f"file:\/\/\/(.*)|{self.imgLink}"
		self.imgs = []



		self.code = "\`(.*?)\`"

		self.orderList = "((^|^\t+)(\d+)[.)])\s(.*)"
		self.unorderList = "((^|^\t+)(\*|\-|\+))\s(.*)"

		self.horizRule = "^-( *-){2,}|^_( *_){2,}|^\*( *\*){2,}"



		self.rules = {
		"h1": "^#\s.*",
		"h2": "^##\s.*",
		"h3": "^###\s.*", 
		"highlight": "\=\=(.*?)\=\=", 
		"italic": "\*(.*?)\*|\_(.*?)\_", 
		"bold": "\*\*(.*?)\*\*|\__(.*?)\__", 
		"code": self.code,
		"strike": "\~\~(.*?)\~\~",
		"link": "\\b((?:http(?:|s)\:|www\.)[^\s]+)",
		"refLink": "\[.*?\]\((.+)\)",
		"imgLink": self.imgLink,
		"list": self.orderList,
		"unorderList": self.unorderList,
		"rule": self.horizRule,
		"superscript": "\^(.+?)\^",
		"subscript": "(?<!\~)\~(?!\~)(.*?)(?<!\~)\~(?!\~)"
		}






		self.hScale = {"h1": 2, "h2": 1.5, "h3": 1.17}
		self.headings = []


		# rehighlight colored formats only when the pref value has changed
		self.rehighlight = {
		"codeFont": {"dict": PREFS, "keys": ["code"], "prevVal": None},
		"highlight": {"dict": COLOR, "keys": ["highlight"], "prevVal": None},
		"link": {"dict": COLOR, "keys": ["link", "refLink", "imgLink"], "prevVal": None},
		"mid-text": {"dict": COLOR, "keys": ["list"], "prevVal": None},
		}


		parent.fontSizeChanged.connect(self.rehighlightFormats)
















	def rehighlightFormats(self, val=None):
		for i in self.headings:
			self.rehighlightBlock(i)
		


		for key, items in self.rehighlight.items():
			if (val := items["dict"][key]) != items["prevVal"]:
				items["prevVal"] = val

				pattern = re.compile("|".join(self.rules[key] for key in  items["keys"]))
				for i in range(self.parent().blockCount()):
					if re.search(pattern, (block := self.parent().findBlockByNumber(i)).text()):
						self.rehighlightBlock(block)









	def charStyle(self, style, link=False):
		char = QTextCharFormat()
		font = QFont(PREFS["textFont"])

		match style:
			case "h1" | "h2" | "h3":
				font.setPixelSize(int(PREFS["textFontSize"] * self.hScale[style]))
				char.setFont(font)
				char.setFontWeight(QFont.Weight.Bold)
			case "highlight":
				char.setBackground(QColor(COLOR["highlight"]))
			case "code":
				char.setFont(QFont(PREFS["codeFont"]))
				char.setBackground(QColor("transparent"))
				char.clearProperty(8193)
				char.clearProperty(8195)
				char.clearProperty(8196)
			case "italic":
				char.setFontItalic(True)
			case "bold":
				char.setFontWeight(QFont.Weight.Bold)
			case "strike":
				char.setFontStrikeOut(True)
			case "link" | "refLink" | "imgLink":
				char.setAnchorHref(link)
				char.setForeground(QColor(COLOR["link"]))
				char.setFontUnderline(True)
			case "list":
				char.setForeground(QColor(COLOR["mid-text"]))
			case "unorderList" | "rule":
				char.setForeground(QColor("transparent"))
			case "superscript":
				char.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSuperScript)
			case "subscript":
				char.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSubScript)
		return char













	def highlightBlock(self, text):
		block = self.currentBlock()
		prevBlock = block.previous()
		nextBlock = block.next()

		cursor = QTextCursor(block)



		formats = []
		for style, rx in self.rules.items():
			for match in re.finditer(rx, text, re.IGNORECASE):
				start, end = match.span()

				if style in ("list", "unorderList"):
					end = len(match.group(1))

				if style in ("h1","h2","h3") and block not in self.headings:
					self.headings.append(block)
				


				

				char = self.charStyle(style, match.group(1) if style in ("link", "refLink", "imgLink") else None)
				formats.append([char, (start, end)])




		if formats:
			# incrementally arrange all possible format segments in the text block, then merge if one intersects another

			# format ranges in the block:
			# 10 - 71 bold
			# 21 - 44 highlight
			# 28 - 59 italic

			# output:
			# 10 - 21 bold
			# 21 - 28 bold highlight
			# 28 - 44 bold highlight italic
			# 44 - 59 bold italic
			# 59 - 71 bold

			segments = sorted(pos for span in formats for pos in span[1])


			for start, end in zip(segments, segments[1:]):
				newFormat = QTextCharFormat()

				for charFormat, (formStart, formEnd) in formats:
					if formStart < end and formEnd > start:
						newFormat.merge(charFormat)
				self.setFormat(start, end - start, newFormat)















		if (match := re.search(self.img, text)) and not self.textEdit.isImage(nextBlock):
	

			path = os.path.normpath(f"{'' if elem['platform'] == 'win32' else '/'}{(isRaw := match.group(1)) or match.group(2)}")
			exists = block in [i["pathBlock"] for i in self.imgs]





			if not exists and os.path.exists(path) and str(path).lower().endswith(tuple(PARAM["imgType"])):

				self.document().documentLayout().registerHandler(id := int(str(random.random())[2:10]), imgObject := ImageObject(self.textEdit, path))


				# print("img", path)
				imgFormat = QTextCharFormat()
				imgFormat.setProperty(10, True)
				imgFormat.setObjectType(id)


				cursor.joinPreviousEditBlock()
				if isRaw:
					cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, match.start())
					cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
					cursor.insertText(f"![]({path})")
					self.highlightBlock(cursor.block().text())



				cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
				cursor.insertBlock()
				cursor.insertText("\ufffc", imgFormat)
				cursor.endEditBlock()
				self.imgs.append({"block": cursor.block(), "pathBlock": cursor.block().previous(), "object": imgObject, "path": path})













		if self.textEdit.viewport().isVisible() and self.textEdit.viewport().width():
			for i in self.imgs:
				rect = self.textEdit.blockRect(i["block"])
				match = re.search(self.imgLink, i["block"].previous().text())
		
				if not rect or not match or not os.path.normpath(match.group(1)) == os.path.normpath(i["path"]):
					self.removeImage(i["block"], rect)





			for i in self.headings:
				if not re.search("^#+\s.*", i.text()):
					self.headings.remove(i)













	def removeImage(self, imgBlock, rect=True):
		update = {"img": QImage(), "removed": True}

		[([setattr(i["object"], var, val) for var, val in update.items()], self.imgs.remove(i)) for i in self.imgs if i["block"] == imgBlock]


		print("remove img")
		if rect:
			cursor = QTextCursor(imgBlock)
			cursor.joinPreviousEditBlock()
			cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
			cursor.removeSelectedText()
			cursor.endEditBlock()












































class LineNumbers(QWidget): 
	def __init__(self, parent):
		super().__init__(parent)
		self.prevWidth = 0
		self.blocks = []




	def paintEvent(self, e):
		if self.isVisible():
			p = QPainter(self)
			p.translate(0, -self.parent().verticalScrollBar().value())
			p.setPen(QColor(COLOR["mid-text"]))

			(font := QFont(PREFS["codeFont"])).setPixelSize(int(PREFS["textFontSize"] / SC_FACTOR["numsScale"]))
			p.setFont(font)



			metrics = QFontMetrics(font)
			bottomWidth = metrics.horizontalAdvance(str(self.parent().document().lastBlock().blockNumber() + 1))
			width = (margin := int(PREFS["textFontSize"] * SC_FACTOR["numsMargin"])) * 2 + bottomWidth


			if width != self.prevWidth:
				(m := self.parent().viewportMargins()).setLeft(PREFS["textMargin"] + width)
				self.parent().setViewportMargins(m)
				self.prevWidth = width



			for i in self.blocks:
				height = (layout := i.layout()).lineAt(0).height()

				p.drawText(QRectF(0, layout.position().y(), width - margin, height), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, str(i.blockNumber() + 1))



			p.end()
			self.setGeometry((view := self.parent().viewport()).x() - width, view.y(), width, view.height())















class ScrollBar(QScrollBar):
	def __init__(self, parent):
		super().__init__()
		self.textWidget = parent


	def paintEvent(self, e):
		super().paintEvent(e)
		if selections := self.textWidget.extraSelections():
			p = QPainter(self)
			p.setBrush(QBrush(QColor(COLOR["highlight"]), Qt.BrushStyle.SolidPattern))


			docHeight = self.textWidget.document().size().height()
			width, height = self.width(), self.height()
			rects = []
			prevY = None
			for i in selections:
				line = (layout := i.cursor.block().layout()).lineForTextPosition(i.cursor.positionInBlock())
				lineY = (line.y() + layout.position().y()) / docHeight * height

				if lineY != prevY:
					rects.append(QRectF(-1, lineY, width + 1, 2))
				prevY = lineY

			p.drawRects(rects)
			p.end()


















class Text(QTextEdit): 
	fontSizeChanged = pyqtSignal()

	def __init__(self, parent, path):
		super().__init__(None)


		self.path = path
		self.setAcceptRichText(False)
		self.document().setDocumentMargin(0)
		self.document().setUseDesignMetrics(True)

		# for highlighting selections
		self.setVerticalScrollBar(ScrollBar(self))
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.installEventFilter(self)









		self.prevCursor = self.textCursor()
		self.keepCursor = False



		self.lineNums = LineNumbers(self)
		self.verticalScrollBar().valueChanged.connect(self.lineNums.update)
		self.document().documentLayout().documentSizeChanged.connect(self.lineNums.update)

	


		self.blockRect = lambda block: self.document().documentLayout().blockBoundingRect(block).toRect()
		self.isImage = lambda block: QTextCursor(block).charFormat().property(10)
		

		self.canPairBrackets = lambda: PREFS["pairBrackets"] and not elem["app"].keyboardModifiers() == Qt.KeyboardModifier.ControlModifier

	




		self.highlighter = Syntax(self, self.document())

		if path:
			with open(path, "r", encoding="utf-8") as f:
				self.setPlainText(f.read())




		self.textChanged.connect(self.onTextChanged)
		self.cursorPositionChanged.connect(self.cursorChanged)










		self.flashTimer = QTimer()
		self.flashTimer.setInterval(100)
		self.flashTimer.setSingleShot(True)
		self.flashTimer.timeout.connect(lambda: elem["app"].setCursorFlashTime(elem["main"].flashTime))



		self.scrollDecay = 0.6
		self.delta = 0
		self.scrollTimer = QTimer(self)
		self.scrollTimer.timeout.connect(self.scroll)





		self.keyPairs = {
		Qt.Key.Key_ParenLeft: ("(", ")"),
		Qt.Key.Key_BracketLeft: ("[", "]"),
		Qt.Key.Key_BraceLeft: ("{", "}"),
		
		Qt.Key.Key_QuoteDbl: '"',
		Qt.Key.Key_Apostrophe: "'",
		Qt.Key.Key_Asterisk: "*",
		Qt.Key.Key_Underscore: "_",
		Qt.Key.Key_QuoteLeft: "`",
		Qt.Key.Key_Equal: "=",
		Qt.Key.Key_AsciiTilde: "~",
		Qt.Key.Key_AsciiCircum: "^",

		Qt.Key.Key_ParenRight: ")",
		Qt.Key.Key_BracketRight: "]",
		Qt.Key.Key_BraceRight: "}",
		} 

		self.bracketPairs = {
		"(": ")",
		"[": "]",
		"{": "}",
		'"': '"',
		"'": "'",
		}
		self.markdownPairs = {c: c for c in "*_`=~^"}







		shortcut = lambda seq, func: (s := QShortcut(seq, self)).activated.connect(lambda: func() if self.hasFocus() else None) or s


		shortcut(QKeySequence.StandardKey.Save, lambda: elem["tabBar"].saveNote(self.path, self, shortcut=True))

		shortcut("Ctrl+K", self.insertLinkFormat)
		shortcut(QKeySequence.StandardKey.Italic, self.shortcutFormat)
		shortcut(QKeySequence.StandardKey.Bold, lambda: self.shortcutFormat(bold=True))



















	def showEvent(self, e):
		self.lineNums.setVisible(PREFS["lineNums"])

		self.setFontSize()
		self.setTabStopDistance(PREFS["tabSize"])
		self.setViewportMargins((self.lineNums.width() if PREFS["lineNums"] else 0) + PREFS["textMargin"], PREFS["fontSize"], PREFS["textMargin"], 0)
		self.setCursorWidth(PREFS["cursorWidth"])

		self.charPairs = (self.bracketPairs if PREFS["pairBrackets"] else {}) | (self.markdownPairs if PREFS["pairMarkdown"] else {})






	def setFontSize(self):
		font = QFont(PREFS["textFont"])
		font.setPixelSize(PREFS["textFontSize"])
		self.setFont(font)
		self.viewport().setFont(font)

		# adjust layout
		self.document().size()
		self.fontSizeChanged.emit()








	def wheelEvent(self, e):
		if elem["app"].keyboardModifiers() == Qt.KeyboardModifier.ControlModifier:
			PREFS["textFontSize"] = max(8, min(PREFS["textFontSize"] + (1 if e.angleDelta().y() > 0 else -1), 60))


			cursor = self.textCursor()
			midCursosRect = self.cursorRect(midCursor := self.cursorForPosition(QPoint(0, int(self.viewport().rect().height() / 2))))
			self.setFontSize()
			self.setTextCursor(midCursor)


			offset = self.cursorRect(self.textCursor()).y() - midCursosRect.y()
			val = (scroll := self.verticalScrollBar()).value() + offset
			self.setTextCursor(cursor)
			scroll.setValue(val)



		else:
			if PREFS["smoothScroll"]:
				# scroll length
				self.delta += e.angleDelta().y() / 5
				# scroll speed
				self.scrollTimer.start(10)
				return
			super().wheelEvent(e)




	def scroll(self):
		self.verticalScrollBar().setValue(int(self.verticalScrollBar().value() - self.delta))

		self.delta *= self.scrollDecay
		if abs(self.delta) < 1:
			self.scrollTimer.stop()













	def insertFromMimeData(self, data):
		super().insertFromMimeData(data)
		if data.hasImage():
			try:
				if not os.path.exists(imgFolder := os.path.join(DATA["folderPath"], PREFS["imgFolder"])):
					os.makedirs(imgFolder)

				data.imageData().save(path := os.path.join(imgFolder, f'{str(int(time.time_ns() / 1000000))}.{PREFS["imgFormat"]}'))
				(cursor := self.textCursor()).beginEditBlock()
				cursor.insertText(f"![]({path})")
				cursor.endEditBlock()
			except:
				self.textCursor().insertText("Couldn't save the pasted image. Verify the folder path or its permissions.")








	def shortcutFormat(self, bold=False):
		cursor = self.textCursor()
		char = "*" if not bold else "**"
		step = len(char)


		if cursor.hasSelection():
			self.pairSelection(cursor, step, char, char)
		else:
			cursor.insertText(char * 2)
			cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, step)
			self.setTextCursor(cursor)




	def insertLinkFormat(self):
		(cursor := self.textCursor()).insertText("[]()")
		cursor.movePosition(QTextCursor.MoveOperation.Left)
		self.setTextCursor(cursor)






	def dragMoveEvent(self, e):
		if self.isImage(self.cursorForPosition(e.position().toPoint()).block()):
			e.ignore()
		else:
			super().dragMoveEvent(e)












	def onTextChanged(self):
		if not self.path:
			elem["tabBar"].currentTab.setTabTitle(self.document().find(QRegularExpression("[^\\s\\n]"), 0).block().text().strip())







	def cursorChanged(self):
		cursor = self.textCursor()
		block = self.textCursor().block()

		elem["app"].setCursorFlashTime(0)
		self.flashTimer.start()





		if self.isImage(block):
			if cursor.hasSelection():
				cursor.movePosition(QTextCursor.MoveOperation.PreviousCharacter, QTextCursor.MoveMode.KeepAnchor)
			else:
				if not block.next().isValid():
					cursor.movePosition(QTextCursor.MoveOperation.Up)
				else:
					down = cursor.blockNumber() > self.prevCursor.blockNumber()
					cursor.movePosition(QTextCursor.MoveOperation.Down if down else QTextCursor.MoveOperation.Up)
			self.setTextCursor(cursor)


		if not self.isImage(block):
			self.prevCursor = cursor





































	def paintEvent(self, e):
		p = QPainter(self.viewport())
		blocks = self.getVisibleBlocks()



		if self.lineNums.isVisible():
			self.lineNums.blocks = blocks



		scrollPos = self.verticalScrollBar().value()
		tabHalf = (tabWidth := int(self.tabStopDistance())) // 2
		viewWidth = self.viewport().width()
		r = int(PREFS["textFontSize"] / SC_FACTOR["radius"])

		indents, codeRects, bulletPos, horRules = [], [], [], []
		bulletGlyph = None




		# p.save()
		# p.translate(0, -scrollPos)
		# draw = []
		# p.setBrush(QBrush(QColor("white"), Qt.BrushStyle.SolidPattern))
		# p.setPen(QPen(QColor("#C9C9C9"), 1))
		# for block in blocks:
		# 	draw.append(QRectF(self.blockRect(block).adjusted(0,0,-1,0)))
		# p.drawRects(draw)
		# p.restore()




		for block in blocks:
			text = block.text()



			if PREFS["indentGuides"] and (tabMatch := re.search("^\t+", text)):
				x = tabHalf
				y = (layout := block.layout()).position().y() - scrollPos
				height = layout.lineAt(0).height()

				for i in range(tabMatch.end()):
					if x + tabHalf > viewWidth:
						y += height
						x = 0 - tabHalf

					indents.append(QLineF(x, y, x, y + height - 1))
					x += tabWidth








			if listMatch := re.search(self.highlighter.unorderList, text):
				layout = block.layout()
				line = layout.lineForTextPosition(pos := len(listMatch.group(2)))
				glyphRun = line.glyphRuns(pos, 1, QTextLayout.GlyphRunRetrievalFlag.RetrieveGlyphPositions)[0]
				

				(pos := glyphRun.positions()[0]).setY(pos.y() + (layout.position().y() - scrollPos))
				bulletPos.append(pos)
				bulletGlyph = glyphRun
			








			for code in re.finditer(self.highlighter.code, text):
				layout = block.layout()
				codeRect = {"lines": []}


				start = layout.lineForTextPosition(code.start()).lineNumber()
				end = layout.lineForTextPosition(code.end()).lineNumber()
				for i in range(start, end + 1):
					rect = (line := layout.lineAt(i)).naturalTextRect()
					rect.moveTop(rect.y() + (layout.position().y() - scrollPos))


					if i == start:
						x = line.cursorToX(code.start())[0]
						codeRect["start"] = QRectF(x, rect.y(), r*2, rect.height())
						rect.setLeft(x + r)

					if i == end:
						x = line.cursorToX(code.end())[0]
						codeRect["end"] = QRectF(x - r*2, rect.y(), r*2, rect.height())
						rect.setRight(x - r)
					

					codeRect["lines"].append(rect)
				codeRects.append(codeRect)
		








			if re.search(self.highlighter.horizRule, text):
				layout = block.layout()
				line = layout.lineAt(0)

				y = (layout.position().y() - scrollPos) + line.y() + line.height() / 2
				horRules.append(QLineF(0, y, line.width(), y))














		for elems, pen in [(indents, 1), (horRules, 2)]:
			if elems:
				p.setPen(QPen(QColor(COLOR["mid-text"]), pen))
				p.drawLines(elems)





		if bulletGlyph:
			p.setPen(QColor(COLOR["mid-text"]))

			rawFont = bulletGlyph.rawFont()
			rawFont.setPixelSize(PREFS["textFontSize"] * SC_FACTOR["bulletGlyph"])
			
			bulletGlyph.setRawFont(rawFont)
			bulletGlyph.setPositions(bulletPos)
			bulletGlyph.setGlyphIndexes([bulletGlyph.rawFont().glyphIndexesForString("\u2022")[0]] * len(bulletPos))
			p.drawGlyphRun(QPointF(), bulletGlyph)





		if codeRects:
			p.setRenderHint(QPainter.RenderHint.Antialiasing)
			p.setBrush(QBrush(QColor(COLOR["mid-text"]), Qt.BrushStyle.SolidPattern))
			p.setPen(QPen(Qt.PenStyle.NoPen))


			(path := QPainterPath()).setFillRule(Qt.FillRule.WindingFill)
			for i in codeRects:
				path.addRoundedRect(i["start"], r, r)
				path.addRoundedRect(i["end"], r, r)
				for line in i["lines"]:
					path.addRect(line)

			p.drawPath(path)




		p.end()
		super().paintEvent(e)







	def getVisibleBlocks(self):
		blocks = []
		block = self.cursorForPosition(QPoint()).block()
		endBlock = self.cursorForPosition(QPoint(0, self.viewport().rect().bottom())).block().next()

		while block != endBlock:
			blocks.append(block)
			block = block.next()
		return blocks

































	def eventFilter(self, obj, e):
		if e.type() == QEvent.Type.KeyPress:
			cursor = self.textCursor()




			if e.key() in self.keyPairs and not elem["app"].keyboardModifiers() & Qt.KeyboardModifier.ControlModifier:
				leftChar, rightChar = c if (hasPair := isinstance((c := self.keyPairs[e.key()]), tuple)) else (c, c)
				pos = cursor.position()



				if not cursor.hasSelection():
					if charPairs := "".join(self.charPairs):
						charAt = self.document().characterAt
						posChar = charAt(pos)


						# skip over the char, no markdown chars for now
						if PREFS["pairBrackets"] and posChar == leftChar and posChar in "\"')]}":
							cursor.movePosition(QTextCursor.MoveOperation.Right)
							self.setTextCursor(cursor)
							return True




						if leftChar in charPairs:
							insertPair = lambda: (
								cursor.insertText(rightChar), 
								cursor.movePosition(QTextCursor.MoveOperation.Left),
								self.setTextCursor(cursor))


							samePairs = charPairs.replace("([{", "")
							if leftChar in samePairs:
								# \0 document start, \u2029 - paragraph
								if all(charAt(p) in " \t\u2029\0()[]{}" for p in (pos - 1, pos)):
									insertPair()
							else:
								if posChar in " \t\u2029)]}" + samePairs:
									insertPair()


				else:
					if leftChar in self.charPairs:
						self.pairSelection(cursor, 1, leftChar, rightChar)
						return True








			if elem["app"].keyboardModifiers() == Qt.KeyboardModifier.ControlModifier:
				if e.key() == Qt.Key.Key_BracketRight:
					self.indentText(cursor, self.insertIndent)


				elif e.key() == Qt.Key.Key_BracketLeft:
					removeIndent = lambda cursor: (
						cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock), 
						cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor),
						cursor.removeSelectedText() if cursor.selectedText() == "\t" else None) if cursor.block().text() else None

					self.indentText(cursor, removeIndent)










			if e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
				block = cursor.block()
				nextBlock = block.next()
				listMatch = self.getListMatch(block)




				if elem["app"].keyboardModifiers() & (Qt.KeyboardModifier.ShiftModifier | Qt.KeyboardModifier.KeypadModifier):
					if cursor.hasSelection():
						cursor.removeSelectedText()

					if not block.text():
						prevPos = cursor.position()
						cursor.insertBlock()
						cursor.setPosition(prevPos)
						self.setTextCursor(cursor)
					else:
						cursor.insertBlock()
					return True




				# insert new block
				# elif not block.text():
				# 	cursor.removeSelectedText() if cursor.hasSelection() else None
				# 	cursor.insertBlock()
				# 	self.setTextCursor(self.textCursor())
				# 	return True




				if not cursor.hasSelection():
					if self.isImage(nextBlock) and not cursor.atBlockStart() and not nextBlock == self.document().lastBlock():
						cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
						cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
						# remove image property
						cursor.setCharFormat(QTextCharFormat())
						cursor.insertBlock()
						self.setTextCursor(cursor)
						return True








					if listMatch and cursor.atBlockEnd():
						tabGroup = listMatch.group(2)
						numGroup = listMatch.group(3)
						textGroup = listMatch.group(4)
						# . or )
						delim = listMatch.group(1)[-1]


						if not textGroup and not tabGroup:
							cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock, QTextCursor.MoveMode.KeepAnchor)
							cursor.removeSelectedText()
						else:
							if not textGroup:
								cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
								cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor)
								cursor.removeSelectedText()
								if numGroup.isdigit():
									self.reorderListAround(len(tabGroup))


							else:
								cursor.insertBlock()
								if isNum := numGroup.isdigit():
									countFrom = int(numGroup) + 1

								cursor.insertText(f"{tabGroup}{str(countFrom)}{delim} " if isNum else f"{listMatch.group(1)} ")
								if isNum:
									self.reorderListDown(cursor.block(), len(tabGroup), countFrom)
						return True








				if tabMatch := re.search("^(\t+)(.*)", block.text()):
					if cursor.atBlockEnd():
						cursor.joinPreviousEditBlock()
						if tabMatch.group(2):
							cursor.insertBlock()
							cursor.insertText(tabMatch.group(1))
						else:
							cursor.movePosition(QTextCursor.MoveOperation.PreviousCharacter, QTextCursor.MoveMode.KeepAnchor)
							cursor.removeSelectedText()

						cursor.endEditBlock()
						return True



					elif not cursor.atBlockStart():
						cursor.joinPreviousEditBlock()
						if cursor.positionInBlock() < len(tabMatch.group(1)):
							prevText = tabMatch.group()[:cursor.positionInBlock()]
							cursor.insertBlock()
							cursor.insertText(prevText)
						else:
							cursor.insertBlock()
							cursor.insertText(tabMatch.group(1))

						cursor.endEditBlock()
						return True











			if e.key() == Qt.Key.Key_Tab:
				block = cursor.block()
				listMatch = self.getListMatch(block)



				if listMatch and not cursor.hasSelection():
					tabGroup = listMatch.group(2)
					numGroup = listMatch.group(3)

					self.insertIndent(cursor)
					if numGroup.isdigit():
						self.reorderListAround(len(tabGroup), tabBtn=True)
					return True

				else:
					self.indentText(cursor, self.insertIndent)
					return True









			if e.key() == Qt.Key.Key_Backspace:
				block = cursor.block()
				prevBlock = block.previous()
				cursorPos = cursor.position()




				# delete entire line
				if elem["app"].keyboardModifiers() == (Qt.KeyboardModifier.ShiftModifier | Qt.KeyboardModifier.ControlModifier):
					if cursor.hasSelection():
						cursor.removeSelectedText()
					else:
						if cursor.atBlockStart() and cursorPos:
							cursor.movePosition(QTextCursor.MoveOperation.Left)
							cursor.deleteChar()
						else:
							cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock, QTextCursor.MoveMode.KeepAnchor)
							cursor.removeSelectedText()

					return True




				if self.isImage(prevBlock) and cursor.atBlockStart() and not cursor.hasSelection():
					if not block.text():
						cursor.deleteChar()

					cursor.movePosition(QTextCursor.MoveOperation.PreviousBlock, QTextCursor.MoveMode.MoveAnchor, 2)
					cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
					self.setTextCursor(cursor)
					return True





				charAt = self.document().characterAt
				
				if (prevChar := charAt(cursorPos - 1)) in self.charPairs and charAt(cursorPos) == self.charPairs[prevChar]:
						cursor.deleteChar()




		return False













	def pairSelection(self, cursor, step, leftChar, rightChar):
		start, end = cursor.selectionStart() + step, cursor.selectionEnd() + step
		atEnd = cursor.position() + step == end


		cursor.insertText(f"{leftChar}{cursor.selectedText()}{rightChar}")

		cursor.setPosition(start if atEnd else end)
		cursor.setPosition(end if atEnd else start, QTextCursor.MoveMode.KeepAnchor)
		self.setTextCursor(cursor)







	def insertIndent(self, cursor):
		cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
		cursor.insertText("\t")



	def indentText(self, cursor, func):
		cursor.joinPreviousEditBlock()

		if cursor.hasSelection():
			cursor.setPosition(cursor.selectionStart())
			while cursor.position() <= self.textCursor().selectionEnd() - 1:
				func(cursor)
				if not cursor.movePosition(QTextCursor.MoveOperation.NextBlock):
					break
		else:
			func(cursor)
		cursor.endEditBlock()












	def getListMatch(self, block):
		any(match := re.search(i, block.text()) for i in (self.highlighter.orderList, self.highlighter.unorderList))
		return match




	def reorderListAround(self, tabCount, tabBtn=False):
		# move from right to left (left to right if tab button), top to bottom
		for hor in range(2):
			block = self.textCursor().block()
			countFrom = None
			tabCount += 0 if not hor else - (1 if not tabBtn else -1)


			for ver in range(2):
				blockVer = block
				while blockVer.isValid():
					blockVer = blockVer.previous() if not ver else blockVer.next()
					matchVer = re.search(self.highlighter.orderList, blockVer.text())


					if matchVer and not len(matchVer.group(2)) < tabCount:
						if tabCount == len(matchVer.group(2)):

							if not hor and not ver:
								countFrom = 0 if not tabBtn else int(matchVer.group(3))
							elif not hor and ver:
								countFrom = 0
							elif hor and ver:
								countFrom = 1
							else:
								countFrom = int(matchVer.group(3)) + 1
			 

							self.replaceListNum(block, countFrom)
							self.reorderListDown(block, tabCount, countFrom)
							break
					else:
						break
				if countFrom is not None:
					break

			if countFrom is None:
				self.replaceListNum(block, 1)








	def reorderListDown(self, block, tabCount, countFrom):
		while block.isValid():
			block = block.next()
			matchDown = re.search(self.highlighter.orderList, block.text())

			if matchDown and not len(matchDown.group(2)) < tabCount:
				if tabCount == len(matchDown.group(2)):
					countFrom += 1
					self.replaceListNum(block, countFrom)
			else:
				break





	def replaceListNum(self, block, num):
		cursor = QTextCursor(block)
		cursor.joinPreviousEditBlock()

		numMatch = re.search("\d+", block.text())
		cursor.setPosition(block.position() + numMatch.start())
		cursor.setPosition(block.position() + numMatch.end(), QTextCursor.MoveMode.KeepAnchor)

		cursor.insertText(str(num))
		cursor.endEditBlock()

































	def contextMenuEvent(self, e):
		cursor = self.textCursor()
		posCursor = self.cursorForPosition(e.pos())
		menu = ContextMenu(self)



		menu.addRow("Undo", ICON["undo"], self.undo)
		menu.addRow("Redo", ICON["redo"], self.redo)
		menu.addSeparator()
		menu.addRow("Cut", ICON["cut"], self.cut)
		menu.addRow("Copy", ICON["copy"], self.copy)
		menu.addRow("Paste", ICON["paste"], self.paste)
		menu.addSeparator()
		menu.addRow("Select all", ICON["selectAll"], self.selectAll)



		for i in posCursor.block().layout().formats():
			if i.format.anchorHref() and i.start <= posCursor.positionInBlock() <= i.start + i.length:
				link = i.format.anchorHref()
				imgLink = os.path.normpath(link)


				menu.addSeparator()
				for i in self.highlighter.imgs:
					if imgLink == os.path.normpath(i["path"]):
						menu.addRow("Open in new tab", ICON["openInTab"], lambda: elem["tree"].checkDuplicateTab(QModelIndex(), newTab=True, path=imgLink))
						menu.addSeparator()
						break

				menu.addRow("Copy URL", ICON["copyUrl"], lambda: elem["app"].clipboard().setText(link))
				menu.addRow("Open in browser", ICON["openUrl"], lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(link)))
				break

		if not cursor.selectionStart() <= posCursor.position() <= cursor.selectionEnd():
			self.setTextCursor(cursor := posCursor)


		menu.exec(e.globalPos())





	def focusOutEvent(self, e):
		if self.path and os.path.exists(self.path):
			elem["tabBar"].writeContents(self.path, self)



















