

from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QApplication, QGridLayout, QTextEdit, QVBoxLayout, QSizeGrip, QFrame, QHBoxLayout, QSplitter, QTreeView, QFileSystemModel, QStyledItemDelegate, QAbstractItemView, QMenu, QLineEdit, QColorDialog, QShortcut, QStackedWidget, QSizePolicy, QSlider, QListWidget, QProxyStyle, QStyle, QScrollArea
from PyQt5.QtCore import Qt, QSettings, QSize, QDir, QFile, QEvent, QItemSelectionModel, QRect, QUrl
from PyQt5.QtGui import QKeyEvent, QKeySequence, QColor, QCursor, QTextCharFormat, QPen, QPainterPath, QFontDatabase, QSyntaxHighlighter, QFont, QPainter, QIcon

import sys, time, subprocess, re, math, os, shutil, ctypes







SETTINGS = QSettings("QNotes", "App")

NOTE_PATH = SETTINGS.value("dir")
NOTE = SETTINGS.value("note")



def returnVal(val, c):
    return val if val else c

defaultColor =  ["#f8f8f8", "#efefef", "#2d2d2d", "#4b4b4b", "#eaeaea", "#393939", "#f5d105"]

TITLE_COLOR = returnVal(SETTINGS.value("colTitle"), defaultColor[0])

TREE_COLOR = returnVal(SETTINGS.value("colTree"), defaultColor[1])
TREE_TEXT_COLOR = returnVal(SETTINGS.value("colTreeText"), defaultColor[2])

ICON_COLOR = returnVal(SETTINGS.value("colIcon"), defaultColor[3])

EDITOR_COLOR = returnVal(SETTINGS.value("colEditor"), defaultColor[4])
EDITOR_TEXT_COLOR = returnVal(SETTINGS.value("colEditorText"), defaultColor[5])
EDITOR_HIGHLIGHT = returnVal(SETTINGS.value("colEditHighlight"), defaultColor[6])

EDITOR_MARGIN = returnVal(SETTINGS.value("editMargin"), 20)
EDIT_FONT_FAMILY = returnVal(SETTINGS.value("editFontFamily"), "")
EDITOR_FONT_SIZE = returnVal(SETTINGS.value("editFontSize"), 11)

FONT_FAMILY = returnVal(SETTINGS.value("fontFamily"), "")
FONT_SIZE = returnVal(SETTINGS.value("fontSize"), 13)

TITLE_HEIGHT = 28
ICON_SIZE = 13






        

class Grips(QWidget):
    global sideGrips
    sideGrips = [QVBoxLayout(), QHBoxLayout()]

    def __init__(self, parent, edge):
        super().__init__(parent)
        handleSize = 4

        match edge:
            case "top":
                self.setCursor(Qt.SizeVerCursor)
                self.setFixedHeight(handleSize)
                sideGrips[0].addWidget(self)
                sideGrips[0].addStretch(1)

                self.resize = self.resizeTop

            case "left":
                self.setCursor(Qt.SizeHorCursor)
                self.setFixedWidth(handleSize)
                sideGrips[1].addWidget(self)
                sideGrips[1].addStretch(1)

                self.resize = self.resizeLeft

            case "bottom":
                self.setCursor(Qt.SizeVerCursor)
                self.setFixedHeight(handleSize)
                sideGrips[0].addWidget(self)

                self.resize = self.resizeBottom

            case "right":
                self.setCursor(Qt.SizeHorCursor)
                self.setFixedWidth(handleSize)
                sideGrips[1].addWidget(self)

                self.resize = self.resizeRight


    def setGrips(parent, grid):
        global cornerGrips
        vBox = [QVBoxLayout() for i in range(2)]
        cornerGrips = [QSizeGrip(parent) for i in range(4)]

        [g.setStyleSheet("background: transparent; width: 4; height: 4;") for g in cornerGrips]

        vBox[0].addWidget(cornerGrips[0], 0, Qt.AlignRight | Qt.AlignTop)
        vBox[0].addWidget(cornerGrips[1], 0, Qt.AlignRight | Qt.AlignBottom)
        vBox[1].addWidget(cornerGrips[2], 0, Qt.AlignLeft | Qt.AlignTop)
        vBox[1].addWidget(cornerGrips[3], 0, Qt.AlignLeft | Qt.AlignBottom)

        grid.setContentsMargins(0,0,0,0)
        for i in [vBox[0], vBox[1], sideGrips[0], sideGrips[1]]:
            grid.addLayout(i, 0, 0)


    def toggleGripVisibility(parent):
        if parent.isMaximized() is True:
            for i in range(4):
                cornerGrips[i].hide()
                if i%2 == 0:
                    for box in sideGrips:
                        box.itemAt(i).widget().hide()
        else:
            for i in range(4):
                cornerGrips[i].show()
                if i%2 == 0:
                    for box in sideGrips:
                        box.itemAt(i).widget().show()

    def raiseGrips():
        for i in range(4):
            if i%2 == 0:
                for box in sideGrips:
                    box.itemAt(i).widget().raise_()
        for i in cornerGrips:
            i.raise_()


    def mouseMoveEvent(self, e):
        window = self.window()
        self.resize(e.pos(), window, window.geometry())

    def resizeTop(self, pos, window, geo):
        if window.height() == window.minimumHeight() and pos.y() > 0:
            pass
        else:
            geo.setTop(QCursor.pos().y())
            window.setGeometry(geo)

    def resizeRight(self, pos, window, geo):
        window.resize(geo.width() + pos.x(), geo.height())

    def resizeBottom(self, pos, window, geo):
        window.resize(geo.width(), geo.height() + pos.y())

    def resizeLeft(self, pos, window, geo):
        if window.width() == window.minimumWidth() and pos.x() > 0:
            pass
        else:
            geo.setLeft(QCursor.pos().x())
            window.setGeometry(geo)












class Titlebar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        global titleBar
        titleBar = self

        self.clickPos = None
        self.setFixedHeight(TITLE_HEIGHT)
        self.setAttribute(Qt.WA_StyledBackground)

        buttonWrap = QHBoxLayout()
        buttonWrap.setContentsMargins(0,0,0,0)
        buttonWrap.setSpacing(0)

        tButtons = [QPushButton("\uE000"), QPushButton("\uE001"), QPushButton("\uE002"), QPushButton("\uE003"), QPushButton("\uE004"), QPushButton("\uE005")]

        for i in tButtons:
            buttonWrap.addWidget(i)
            if i == tButtons[2]:
                buttonWrap.addStretch(1)


        tButtons[0].clicked.connect(lambda: Main.toggleSidebar(self.parent()))
        tButtons[1].clicked.connect(lambda: self.createFile(NOTE_PATH, "Untitled", ".md"))
        tButtons[2].clicked.connect(lambda: self.createFile(NOTE_PATH, "Untitled", ""))

        tButtons[3].clicked.connect(lambda: parent.showMinimized())
        tButtons[4].clicked.connect(self.toggleFullscreen)
        tButtons[5].clicked.connect(lambda: parent.close())

        self.setLayout(buttonWrap)
        self.updateStylesheet()


    def updateStylesheet(self):
        self.setStyleSheet("QWidget{background-color: "+TITLE_COLOR+";}QPushButton{font-family: qicons; border: none; color: "+ICON_COLOR+"; font-size: "+str(ICON_SIZE)+"px; width: "+str(TITLE_HEIGHT)+"px; height: "+str(TITLE_HEIGHT)+"px;}QPushButton:pressed{color: "+Main.iconColor()+";}")


    def createFile(self, path, name, suffix):
        if NOTE_PATH:
            base = "\\" + name + suffix
            i = 0

            while True:
                i += 1
                if QDir().exists(path + base) is False:
                    if suffix:
                        with open(path + base, "w") as file:
                            break
                    else:
                        QDir().mkdir(path + base)
                        break
                else:
                    pass
                base = "\\" + name + f" {i}" + suffix


    def toggleFullscreen(self):
        parent = self.window()
        if parent.isMaximized() is False:
            parent.showMaximized()
        else:
            parent.showNormal()

        Grips.toggleGripVisibility(parent)


    def mousePressEvent(self, e):
        if not self.window().isMaximized():
            self.clickPos = e.localPos().toPoint()

    def mouseMoveEvent(self, e):
        if self.clickPos:
            self.window().move(e.globalPos() - self.clickPos)

    def mouseReleaseEvent(self, e):
        self.clickPos = None

    def mouseDoubleClickEvent(self, e):
        self.toggleFullscreen()














# class BorderStyle(QProxyStyle):
#     def drawPrimitive(self, element, option, painter, widget):
#         if element == QStyle.PE_IndicatorItemViewItemDrop:
#             pen = QPen()
#             pen.setWidth(2)
#             painter.setPen(pen)
#             painter.setRenderHints(QPainter.Antialiasing)
#             painter.drawRoundedRect(option.rect, 3, 3)

 



class DelegateTree(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)

        option.text = self.getName(index)
        option.decorationSize = QSize(0,0)


    def setEditorData(self, line, index):
        super().setEditorData(line, index)
        line.setMaxLength(200)
        line.setText(self.getName(index))
        line.setAlignment(Qt.AlignLeft)

    def updateEditorGeometry(self, line, option, index):
        super().updateEditorGeometry(line, option, index)
        line.setContentsMargins(0,0,10,0)
        line.setFixedWidth(fileTree.visualRect(index).width())

    def getName(self, index):
        if not index.model().isDir(index):
            return index.model().fileInfo(index).completeBaseName()
        else:
            return index.model().fileInfo(index).fileName()





class Model(QFileSystemModel):
    def __init__(self):
        super().__init__()
        self.setReadOnly(False)
        self.setRootPath(NOTE_PATH)
        self.setNameFilters(["*.txt", "*.md"])
        self.setNameFilterDisables(False)

        self.layoutChanged.connect(self.updateTree)
        self.rowsRemoved.connect(self.updateLockedTree)


    def updateTree(self, p, f):
        if not fileTree.updatesEnabled():
            fileTree.setUpdatesEnabled(True)

    def updateLockedTree(self, p, f, l):
        if not fileTree.updatesEnabled() and not fileTree.editIndex:
            fileTree.setUpdatesEnabled(True)

    def dropMimeData(self, mime, drop, row, column, parent):
        for url in mime.urls():
            src = url.toLocalFile()
            index = self.index(src)
            dst = self.fileInfo(parent).filePath() + "/" + self.fileInfo(index).fileName()


            if not QDir().exists(dst) and not QUrl.fromLocalFile(self.fileInfo(index.parent()).filePath()) in mime.urls():
                if self.isDir(index):
                        fileTree.moveFolder(src, dst, index, self)
                else:
                    global NOTE
                    if NOTE == src:
                        NOTE = dst
                        SETTINGS.setValue("note", NOTE)

                    shutil.copy2(src, dst)
                    self.remove(index)
        return False







class Tree(QTreeView):
    def __init__(self):
        super().__init__()
        global fileTree
        fileTree = self
        self.setItemDelegate(DelegateTree(self))
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.setStyle(BorderStyle())

        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setUniformRowHeights(True)
        self.setIndentation(15)
        self.setExpandsOnDoubleClick(False)


        model = Model()

        self.setModel(model)
        self.setRootIndex(model.index(NOTE_PATH))
        self.restoreTreeState()
        for i in range(1,4,1):
            self.hideColumn(i)


        self.editIndex = None
        self.expandState = False
        self.noFile = True
        self.selectionModel().selectionChanged.connect(self.keepSelection)
        self.keepSelection(self.selectionModel().selection(), "")
        self.updateStylesheet()


    def updateStylesheet(self):
        c = QColor(TREE_COLOR)
        if c.value() > 25:
            selection = QColor().fromHsv(c.hue(),c.saturation(),c.value() - 25).name()
        else:
            selection = QColor().fromHsv(c.hue(),c.saturation(),c.value() + 25).name()
        selected = Main.selectedColor()

        self.setStyleSheet("QTreeView, QHeaderView::section, QScrollBar:vertical, QScrollBar::sub-page:vertical, QScrollBar::add-page:vertical{background-color: "+TREE_COLOR+";}QTreeView::item{height: "+str(FONT_SIZE + 10)+"px; border-radius: 3px; color: "+TREE_TEXT_COLOR+"}QLineEdit{selection-background-color: "+selection+"; selection-color: "+TREE_TEXT_COLOR+"; background:"+selected+"; color: "+TREE_TEXT_COLOR+"}QTreeView::item, QTreeView, QLineEdit, QHeaderView::section{outline: 0; border: none;}QTreeView::item:selected{background-color: "+selected+"; color: "+TREE_TEXT_COLOR+";}QAbstractItemView{margin-left: 8px;}QHeaderView::section{height: 10px; color: transparent;}QScrollBar:vertical{margin: 0; width: 10px; border: none;}QScrollBar::handle:vertical{border-radius: 5px; background-color: "+selected+"; min-height: 30px;}QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical{height: 0; background-color: none;}QLineEdit{margin-left: 1px;}QMenu{background-color: "+TREE_COLOR+"; border: 1px solid "+selection+"; color: "+TREE_TEXT_COLOR+";}QMenu::separator{background-color: "+selection+"; height: 1px; margin: 4px 8px;}")

    def restoreTreeState(self):
        try:
            n = 0
            for root, dirs, files in os.walk(NOTE_PATH):
                for d in dirs:
                    pIndex = self.model().index(os.path.join(root, d))
                    if int(SETTINGS.value("treeState")[n]):
                        self.expand(pIndex)
                    n += 1
        except:
            pass

    def keepSelection(self, select, deselect):
        if not select.indexes() and self.updatesEnabled():
            self.selectionModel().select(self.model().index(NOTE), QItemSelectionModel.Select)

        if self.expandState:
            model = self.model()

            if not self.noFile:
                self.expand(model.index(self.dst))
                n = 0
                for root, dirs, files in os.walk(self.dst):
                    for d in dirs:
                        if self.expandedFolder[n]:
                            self.expand(model.index(os.path.join(root, d)))
                        n += 1

            self.expandState  = False
            self.noFile = True


    def commitData(self, line):
        model = self.model()
        index = self.editIndex
        newName = line.text()
        src = model.fileInfo(index).filePath()

        if not any(c in ["<",">",":",'"',"/","\\","|","?","*"] for c in newName):
                if model.isDir(index):
                    dst = model.fileInfo(index).path() + "/" + newName
                    if not QDir().exists(dst):
                        self.moveFolder(src, dst, index, model)

                else:
                    dst = model.fileInfo(index).path() + "/" + newName + "." + model.fileInfo(index).suffix()
                    if not QDir().exists(dst):
                        self.setUpdatesEnabled(False)
                        QDir().rename(src, dst)

                        global NOTE
                        if NOTE == src:
                            NOTE = dst
                            SETTINGS.setValue("note", NOTE)


    def moveFolder(self, src, dst, index, model):
        self.dst = dst
        self.setUpdatesEnabled(False)
        self.expandedFolder = []

        if self.isExpanded(index):
            self.expandState = True
            for root, dirs, files in os.walk(src):
                for d in dirs:
                    self.expandedFolder.append(self.isExpanded(model.index(os.path.join(root, d))))

                for f in files:
                    self.noFile = False

        self.checkNotePresence(src, dst)
        shutil.copytree(src, dst)
                
        i = 0
        while QDir().exists(src):
            if i == 4:
                self.folderIsLocked(src, dst)
                self.checkNotePresence(dst, src)
                model.remove(model.index(dst))
                self.editIndex = None
                break

            model.remove(index)
            i += 1


    def folderIsLocked(self, src, dst):
        for root, dirs, files in os.walk(dst):
            for d in dirs:
                path = QDir.fromNativeSeparators(root + "/" + d)
                prev = src + re.sub(dst, "", path)
                if not QDir().exists(prev):
                    try:
                        shutil.copytree(path, prev)
                    except:
                        pass

            for f in files:
                path = QDir.fromNativeSeparators(root + "/" + f)
                prev = src + re.sub(dst, "", path)
                if not QDir().exists(prev):
                    try:
                        shutil.copy2(path, prev)
                    except:
                        pass


    def checkNotePresence(self, src, dst):
        global NOTE
        for root, dirs, files in os.walk(src):
            for f in files:
                if QDir.fromNativeSeparators(root + "/" + f) == NOTE:
                    NOTE = dst + re.sub(src, "", NOTE)
                    SETTINGS.setValue("note", NOTE)
                    break


    def edit(self, index, *args):
        for i in args:
            if i == 31:
                self.editIndex = index
        return super().edit(index, *args)


    def mouseReleaseEvent(self, e):
        if e.button() == 1:
            if self.indexAt(e.pos()).isValid() and len(self.selectedIndexes()) == 1:
                index = self.indexAt(e.pos())
                model = self.model()
                if model.isDir(index):
                    if not self.isExpanded(index):
                        self.expand(index)
                    else:
                        self.collapse(index)
                else:
                    textEdit.saveNote()

                    global NOTE
                    NOTE = model.fileInfo(index).filePath()
                    textEdit.openNote()
                    SETTINGS.setValue("note", NOTE)

        super().mouseReleaseEvent(e)


    def contextMenuEvent(self, context):
        row = self.indexAt(context.pos())
        rows = self.selectedIndexes()
        model = self.model()

        if row.isValid():
            menu = QMenu()

            if len(rows) == 1:
                if model.isDir(row):
                    path = model.fileInfo(row).filePath()
                    menu.addAction("New note", lambda: Titlebar.createFile("", path, "Untitled", ".md"))
                    menu.addAction("New folder", lambda: Titlebar.createFile("", path, "Untitled", ""))

                menu.addAction("Show in Explorer", lambda: subprocess.Popen("explorer /select, "+QDir.toNativeSeparators(model.fileInfo(row).filePath())+""))
                menu.addAction("Rename", lambda: self.edit(row))
                menu.addAction("Delete", lambda: self.deleteFile(row, model))

            else:
                menu.addAction("Delete", lambda: self.deleteFile(rows, model))

            menu.setStyleSheet("QMenu{background-color: "+TREE_COLOR+"; margin: 0; padding: 0; color: "+TREE_TEXT_COLOR+"; border: 1px solid "+Main.selectedColor()+"; font-size: "+str(FONT_SIZE)+"px; font-family: "+FONT_FAMILY+";}")
            menu.exec(QCursor.pos())


    def deleteFile(self, index, model):
        global NOTE
        if not isinstance(index, list):
            if model.index(NOTE) == index:
                NOTE = ""
                textEdit.setPlainText("")
                SETTINGS.remove("note")

            QFile.moveToTrash(model.fileInfo(index).filePath())
        else:
            for i in index:
                QFile.moveToTrash(model.fileInfo(i).filePath())



    def drawBranches(self, painter, rect, index):
        if self.model().isDir(index):
            rect = QRect(rect.x() - 2, rect.y(), rect.width(), rect.height())
            font = QFont()
            font.setPointSize(int(math.pow(FONT_SIZE, 0.8)))
            font.setFamily("qicons")
            painter.setPen(QColor(ICON_COLOR))
            painter.setFont(font)

            if not self.isExpanded(index):
                painter.drawText(rect, Qt.AlignCenter | Qt.AlignRight, "\uE006")
            else:
                painter.drawText(rect, Qt.AlignCenter | Qt.AlignRight, "\uE007")
      
















class Syntax(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.updateCharStyle()


    def updateCharStyle(self):
        self.rules = [("^#\s.*", self.charStyle("h1")), ("^##\s.*", self.charStyle("h2")), ("^###\s.*", self.charStyle("h3")), ("\*.*?\*", self.charStyle("italic")), ("\*{2}.*?\*{2}", self.charStyle("bold")), ("\~{2}.*?\~{2}", self.charStyle("strike")), ("\={2}.*?\={2}", self.charStyle("highlight")), ("\`.*?\`", self.charStyle("code")), ("\<\!\-{2}.*?\-{2}\>", self.charStyle("comment"))]

    def charStyle(self, e):
        char = QTextCharFormat()

        match e:
            case "h1":
                char.setFontPointSize(EDITOR_FONT_SIZE * 2)
                char.setFontWeight(QFont.DemiBold)
            case "h2":
                char.setFontPointSize(int(EDITOR_FONT_SIZE * 1.5))
                char.setFontWeight(QFont.DemiBold)
            case "h3":
                char.setFontPointSize(int(EDITOR_FONT_SIZE * 1.17))
                char.setFontWeight(QFont.DemiBold)
            case "italic":
                char.setFontItalic(True)
            case "bold":
                char.setFontWeight(QFont.DemiBold)
            case "strike":
                char.setFontStrikeOut(True)
            case "highlight":
                char.setBackground(QColor(EDITOR_HIGHLIGHT))
            case "code":
                char.setBackground(QColor(Main.selectionColor()))
                char.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
                char.setFontPointSize(EDITOR_FONT_SIZE)
            case "comment":
                char.setForeground(QColor(Main.selectionColor()))

        return char


    def highlightBlock(self, text):
        for rx, char in self.rules:
            for match in re.finditer(rx, text):
                self.setFormat(match.start(), match.end() - match.start(), char)







class Text(QTextEdit):
    def __init__(self):
        super().__init__()
        global textEdit
        textEdit = self

        self.initHighlighter()
        self.textChanged.connect(self.updateFontSize)

        self.openNote() if NOTE else None
        self.installEventFilter(self)
        self.setAcceptRichText(False)
        self.setTabStopDistance(20)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ctrl = False

        save = QShortcut(QKeySequence("Ctrl+S"), self)
        save.activated.connect(self.saveNote)

        self.updateMargins()
        self.updateStylesheet()


    def initHighlighter(self):
        global highlighter
        highlighter = Syntax(self.document())

    def updateMargins(self):
        self.setViewportMargins(EDITOR_MARGIN, 0, EDITOR_MARGIN, 0)

    def updateStylesheet(self):
        selection = Main.selectionColor()
        self.resizeFont()

        self.setStyleSheet("QTextEdit{background-color: "+EDITOR_COLOR+";color: "+EDITOR_TEXT_COLOR+"; border: none; selection-background-color: "+selection+"; selection-color: "+EDITOR_TEXT_COLOR+"; font-family:"+EDIT_FONT_FAMILY+";}QScrollBar:vertical{margin: 0; width: 10px; border: none;}QScrollBar::handle:vertical{border-radius: 5px; background-color: "+selection+"; min-height: 30px;}QScrollBar:vertical, QScrollBar::sub-page:vertical, QScrollBar::add-page:vertical{background-color: "+EDITOR_COLOR+";}QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical{height: 0; background-color: none;}QMenu{background-color: "+EDITOR_COLOR+"; border: 1px solid "+selection+"; color: "+EDITOR_TEXT_COLOR+";}QMenu::separator{background-color: "+selection+"; height: 1px; margin: 4px 8px;}")


    def openNote(self):
        try:
            with open(NOTE, "r", encoding="utf-8") as f:
                self.setPlainText(f.read())
        except:
            pass

    def saveNote(self):
        global NOTE
        if NOTE:
            if not QDir().exists(NOTE):
                NOTE = ""
                SETTINGS.remove("note")
            else:
                with open(NOTE, "w", encoding="utf-8") as f:
                    f.write(self.toPlainText())


    def eventFilter(self, obj, e):
        if self.toPlainText():
            if e.type() == QEvent.KeyPress:
                if e.key() == 16777249:
                    self.setReadOnly(True)
                    self.ctrl = True

                if self.ctrl and e.key() != 16777249:
                    self.setReadOnly(False)


            elif self.ctrl and e.type() == QEvent.Wheel:
                global EDITOR_FONT_SIZE
                if e.angleDelta().y() > 0 and EDITOR_FONT_SIZE < 40:
                    EDITOR_FONT_SIZE += 1
                    self.zoomIn(2)
            
                elif e.angleDelta().y() < 0 and EDITOR_FONT_SIZE > 10:
                    EDITOR_FONT_SIZE -= 1

                highlighter.updateCharStyle()
                self.resizeFont()

        return False

    def resizeFont(self):
        cursor = self.textCursor()
        self.selectAll()
        self.setFontPointSize(EDITOR_FONT_SIZE)
        self.setTextCursor(cursor)

        SETTINGS.setValue("editFontSize", EDITOR_FONT_SIZE)

    def updateFontSize(self):
        if not self.toPlainText():
            self.updateStylesheet()

    def keyReleaseEvent(self, e):
        if e.key() == 16777249:
            self.setReadOnly(False)
            self.ctrl = False


















class FontBox(QListWidget):
    def __init__(self, fontButton, widget):
        super().__init__()
        self.setUniformItemSizes(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        for i in QFontDatabase().families(QFontDatabase.Any):
            if i != "qicons":
                self.addItem(i)

        if fontButton.text() != "None":
            # if removed externally
            try:
                self.setCurrentRow(self.row(self.findItems(fontButton.text(), Qt.MatchExactly)[0]))
            except:
                pass

        self.currentTextChanged.connect(lambda t: self.rowClicked(t, fontButton, widget))
        self.itemPressed.connect(lambda i: self.setCurrentRow(self.row(i)))


    def rowClicked(self, t, fontButton, widget):
        global EDIT_FONT_FAMILY, FONT_FAMILY

        if widget != textEdit:
            FONT_FAMILY = t
            main.updateStylesheet()
            SETTINGS.setValue("fontFamily", t)
        else:
            EDIT_FONT_FAMILY = t
            textEdit.updateStylesheet()
            SETTINGS.setValue("editFontFamily", t)

        fontButton.setText(t)


    def hideEvent(self, e):
        parent = settingsWidget.stackLayout
        button = self.sender()

        if button:
            if button.property("index"):
                parent.removeWidget(self)
                self.deleteLater()
                parent.setCurrentIndex(button.property("index"))
        else:
            parent.removeWidget(self)
            self.deleteLater()
            for i in settingsWidget.buttons:
                if i.isChecked():
                    parent.setCurrentIndex(i.property("index"))








class Settings(QWidget):
    def __init__(self):
        super().__init__()
        self.buttonSize = 26
        self.buttonMargin = 10
        self.layoutMargin = 20

        centerWrap = QHBoxLayout()

        centerWid = QWidget()
        centerWid.setObjectName("center")
        centerWid.setFixedSize(500, 350)


        centerGrid = QGridLayout()
        bLayout = QVBoxLayout()
        self.stackLayout = QStackedWidget()


        layouts = [(QPushButton("General"), self.genLayout()), (QPushButton("Editor"), self.editLayout()), (QPushButton("Appearance"), self.appearLayout())]
        self.buttons = []

        for i, l in enumerate(layouts):
            b = l[0]
            self.buttons.append(b)
            bLayout.addWidget(b)
            self.stackLayout.addWidget(l[1])

            # needed when switching from fontbox
            b.setProperty("index", i)

            b.setObjectName("left")
            b.setCheckable(True)
            b.clicked.connect(lambda: self.setChecked(layouts))
            b.clicked.connect(lambda x, i=i: self.stackLayout.setCurrentIndex(i))


        layouts[0][0].setChecked(True)
        bLayout.addStretch(1)
        bLayout.setSpacing(self.buttonMargin)
        bLayout.setContentsMargins(self.layoutMargin,self.layoutMargin,0,self.layoutMargin)


        centerGrid.addLayout(bLayout, 0, 0)
        centerGrid.addWidget(self.stackLayout, 0, 1)
        centerGrid.setContentsMargins(0,0,0,0)
        centerGrid.setSpacing(0)

        centerWid.setLayout(centerGrid)
        centerWrap.addWidget(centerWid, Qt.AlignCenter)

        self.setLayout(centerWrap)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setObjectName("main")
        self.updateStylesheet()


    def updateStylesheet(self):
        treeC = QColor(TREE_COLOR)
        if treeC.value() < 200:
            borderC = QColor().fromHsv(treeC.hue(),treeC.saturation(),treeC.value() + 20).name()
        else:
            borderC = QColor().fromHsv(treeC.hue(),treeC.saturation(),treeC.value() - 20).name()

        includeBorder = self.buttonSize - 4
        selected = Main.selectedColor()


        self.setStyleSheet("QWidget{color: "+TREE_TEXT_COLOR+";background-color: "+TREE_COLOR+";}QWidget#main{background-color: rgba(0,0,0, 0.8);}QWidget#center, QStackedWidget, QWidget#tab, QScrollArea{border-radius: 3px;}QPushButton{border: none;}QPushButton#left{padding: 0 "+str(self.layoutMargin)+"px; text-align: left;}QListWidget, QScrollArea{border: none;}QPushButton#reset{font-family: qicons; font-size: "+str(ICON_SIZE)+"px; color: "+ICON_COLOR+"; width: "+str(self.buttonSize)+"px;}QPushButton#reset:pressed{color: "+Main.iconColor()+";}QSlider::groove:horizontal{background: "+borderC+"; height: 2px;}QSlider::handle:horizontal{background: "+ICON_COLOR+"; width: 12px; margin: -5px 0; border-radius: 6px;}QPushButton{height: "+str(self.buttonSize)+"px;}QPushButton#left:checked{border-radius: 3px; background-color: "+selected+";}QListWidget{outline: none; padding: "+str(self.layoutMargin)+"px;}QListWidget::item:selected{background-color: "+selected+"; color: "+TREE_TEXT_COLOR+";}QListWidget::item:hover{background-color: transparent;}QListWidget::item:selected:hover{background-color: "+selected+";}QScrollBar:vertical{margin: 0; width: 10px; border: none;}QScrollBar::handle:vertical{border-radius: 5px; background-color: "+selected+"; min-height: 30px;}QScrollBar:vertical, QScrollBar::sub-page:vertical, QScrollBar::add-page:vertical{background-color: "+TREE_COLOR+";}QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical{height: 0; background-color: none;}QPushButton#color{width: "+str(includeBorder)+"px;  height: "+str(includeBorder)+"px; border-radius: "+str(self.buttonSize / 2)+"px; border: 2px solid "+borderC+";}")


    def setChecked(self, buttons):
        for i in range(len(buttons)):
            b = buttons[i][0]
            b.setChecked(False)
            if b == self.sender():
                b.setChecked(True)

    def mousePressEvent(self, e):
        if self.childAt(e.pos()) is None:
            self.hide()




    def genLayout(self):
        row1Ws = [QLabel("Note directory"), QPushButton("\uE009")]
        row1Ws[1].clicked.connect(self.removeDir)



        row2Ws = [QLabel("Font size"), QSlider(Qt.Horizontal), QPushButton("\uE009")]
        slider = row2Ws[1]
        slider.setRange(8, 18)
        slider.actionTriggered.connect(lambda a: self.disableSliderClick(a, slider))

        slider.setValue(FONT_SIZE)
        slider.valueChanged.connect(self.setFontSize)
        row2Ws[2].clicked.connect(lambda: self.resetFontSize(slider))



        row3Ws = [QLabel("Font family"), QPushButton("None"), QPushButton("\uE009")]
        fontButton = row3Ws[1]

        fontButton.setText(returnVal(FONT_FAMILY, "None"))
        fontButton.clicked.connect(lambda: self.addFontBox(fontButton, main))
        row3Ws[2].clicked.connect(lambda: self.resetFontFamily(fontButton, main))
       

        [b.setObjectName("reset") for b in [row1Ws[1], row2Ws[2], row3Ws[2]]]

        rowWs = [row1Ws, row2Ws, row3Ws]
        row = [QHBoxLayout() for i in range(len(rowWs))]
        for n, i in enumerate(rowWs):
            for w in i:
                if w == i[1]:
                    row[n].addStretch(1)
                row[n].addWidget(w)


        gWidget = QWidget()
        vLayout = self.returnLayout()
        for i in row:
            vLayout.addLayout(i)

        vLayout.addStretch(1)
        gWidget.setLayout(vLayout)
        gWidget.setObjectName("tab")
        return gWidget


    def returnLayout(self):
        vLayout = QVBoxLayout()
        vLayout.setSpacing(self.buttonMargin)
        vLayout.setContentsMargins(self.layoutMargin,self.layoutMargin,self.layoutMargin,self.layoutMargin)
        return vLayout

    def addFontBox(self, button, widget):
        fBox = FontBox(button, widget)
        self.stackLayout.addWidget(fBox)
        self.stackLayout.setCurrentWidget(fBox)

    def disableSliderClick(self, action, slider):
        if action < 7:
            slider.setSliderPosition(slider.value())


    def setFontSize(self, val):
        global FONT_SIZE

        FONT_SIZE = val
        main.updateStylesheet()
        if NOTE_PATH:
            fileTree.updateStylesheet()
        SETTINGS.setValue("fontSize", val)

    def resetFontSize(self, slider):
        global FONT_SIZE

        if FONT_SIZE:
            FONT_SIZE = 13
            main.updateStylesheet()
            slider.setValue(13)
            SETTINGS.remove("fontSize")

    def resetFontFamily(self, button, widget):
        global EDIT_FONT_FAMILY, FONT_FAMILY

        if widget != textEdit and FONT_FAMILY:
            FONT_FAMILY = ""
            main.updateStylesheet()
            SETTINGS.remove("fontFamily")

        elif EDIT_FONT_FAMILY:
            EDIT_FONT_FAMILY = ""
            textEdit.updateStylesheet()
            SETTINGS.remove("editFontFamily")

        button.setText("None")


    def removeDir(self):
        global NOTE_PATH, NOTE
        if NOTE_PATH:
            if QDir().exists(NOTE_PATH):
                fileTree.deleteLater()
                textEdit.setPlainText("")
                sidebarGrid.addWidget(SidebarDir(), 0, 0)

            [SETTINGS.remove(x) for x in ["dir", "note", "treeState"]]
            NOTE_PATH = NOTE = ""




    def editLayout(self):
        row1Ws = [QLabel("Viewport margin"), QSlider(Qt.Horizontal), QPushButton("\uE009")]
        slider = row1Ws[1]
        slider.setRange(1, 300)
        slider.setValue(EDITOR_MARGIN)

        slider.valueChanged.connect(self.setViewportMs)
        slider.actionTriggered.connect(lambda a: self.disableSliderClick(a, slider))

        row1Ws[2].clicked.connect(lambda: self.resetMargins(slider))



        row2Ws = [QLabel("Font family"), QPushButton("None"), QPushButton("\uE009")]
        fontButton = row2Ws[1]

        fontButton.setText(returnVal(EDIT_FONT_FAMILY, "None"))
        fontButton.clicked.connect(lambda: self.addFontBox(fontButton, textEdit))
        row2Ws[2].clicked.connect(lambda: self.resetFontFamily(fontButton, textEdit))



        [b.setObjectName("reset") for b in [row1Ws[2], row2Ws[2]]]

        rowWs = [row1Ws, row2Ws]
        row = [QHBoxLayout() for i in range(len(rowWs))]
        for n, i in enumerate(rowWs):
            for w in i:
                if w == i[1]:
                    row[n].addStretch(1)
                row[n].addWidget(w)


        eWidget = QWidget()
        vLayout = self.returnLayout()
        for i in row:
            vLayout.addLayout(i)

        vLayout.addStretch(1)
        eWidget.setLayout(vLayout)
        eWidget.setObjectName("tab")
        return eWidget


    def setViewportMs(self, val):
        global EDITOR_MARGIN
        EDITOR_MARGIN = val
        textEdit.updateMargins()

        SETTINGS.setValue("editMargin", val)


    def resetMargins(self, slider):
        global EDITOR_MARGIN
        margin = 20

        if EDITOR_MARGIN != margin:
            EDITOR_MARGIN = margin
            textEdit.updateMargins()
            slider.setValue(margin)

            SETTINGS.remove("editMargin")




    def appearLayout(self):
        row1Ws = [QLabel("Theme"), QPushButton("\uE00A"), QPushButton("\uE009")]
        invertB = row1Ws[1]
        resetB = row1Ws[2]
        [(b.setObjectName("reset"), b.clicked.connect(lambda x, f=f: self.invertTheme(f))) for b, f in [(invertB, ""), (resetB, "reset")]]


        row2Ws = [QLabel("Title"), QPushButton()]

        row3Ws = [QLabel("Sidebar"), QPushButton()]

        row4Ws = [QLabel("Global text"), QPushButton()]

        row5Ws = [QLabel("Icons"), QPushButton()]

        row6Ws = [QLabel("Editor"), QPushButton()]

        row7Ws = [QLabel("Editor text"), QPushButton()]

        row8Ws = [QLabel("Editor highlight text"), QPushButton()]



        rowWs = [row1Ws, row2Ws, row3Ws, row4Ws, row5Ws, row6Ws, row7Ws, row8Ws]
        row = [QHBoxLayout() for i in range(len(rowWs))]
        self.cPickers = []


        for n, i in enumerate(rowWs):
            if i != row1Ws:
                self.cPickers.append(i[1])

            for w in i:
                if w == i[1]:
                    row[n].addStretch(1)
                row[n].addWidget(w)

        for n, p in enumerate(self.cPickers):
            p.setStyleSheet("background-color: "+self.layoutColors()[n]+";")
            p.clicked.connect(self.openColor)
            p.setObjectName("color")


        aWidget = QWidget()
        vLayout = self.returnLayout()
        for i in row:
            vLayout.addLayout(i)

        vLayout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        aWidget.setLayout(vLayout)
        scroll.setWidget(aWidget)
        aWidget.setObjectName("tab")
        return scroll



    def layoutColors(self):
        return [TITLE_COLOR, TREE_COLOR, TREE_TEXT_COLOR, ICON_COLOR, EDITOR_COLOR, EDITOR_TEXT_COLOR, EDITOR_HIGHLIGHT]

    def invertTheme(self, func):
        for n, p in enumerate(self.cPickers):
            var = self.layoutColors()[n]

            if not func:
                if var != EDITOR_HIGHLIGHT:
                    c = QColor(var)
                    h = c.hue()

                    color = QColor().fromHsl(h + 180 if h < 180 else h - 180, c.saturation(), 255 - c.lightness()).name()
                    self.getNewColor(color, p, var)
            else:
                self.getNewColor(defaultColor[n], p, var)



    def openColor(self):
        button = self.sender()
        var = button.palette().button().color().name()

        color = QColorDialog()
        color.setCurrentColor(QColor(var))
        # color.setOption(QColorDialog.DontUseNativeDialog)

        color.colorSelected.connect(lambda c: self.getNewColor(c.name(), button, var))
        color.exec()

    def getNewColor(self, c, button, var):
        global TITLE_COLOR, TREE_COLOR, TREE_TEXT_COLOR, ICON_COLOR, EDITOR_COLOR, EDITOR_TEXT_COLOR, EDITOR_HIGHLIGHT

        if var == TITLE_COLOR:
            TITLE_COLOR = c
            titleBar.updateStylesheet()
            SETTINGS.setValue("colTitle", c)

        elif var == TREE_COLOR:
            TREE_COLOR = c

            if NOTE_PATH:
                fileTree.updateStylesheet()
            sidebarPanel.updateStylesheet()
            settingsWidget.updateStylesheet()
            SETTINGS.setValue("colTree", c)

        elif var == ICON_COLOR:
            ICON_COLOR = c
            titleBar.updateStylesheet()
            sidebarPanel.updateStylesheet()
            settingsWidget.updateStylesheet()
            SETTINGS.setValue("colIcon", c)

        elif var == TREE_TEXT_COLOR:
            TREE_TEXT_COLOR = c

            if NOTE_PATH:
                fileTree.updateStylesheet()
            settingsWidget.updateStylesheet()
            sidebarPanel.updateStylesheet()
            SETTINGS.setValue("colTreeText", c)

        elif var == EDITOR_COLOR:
            EDITOR_COLOR = c
            textEdit.updateStylesheet()
            highlighter.deleteLater()
            textEdit.initHighlighter()
            SETTINGS.setValue("colEditor", c)

        elif var == EDITOR_TEXT_COLOR:
            EDITOR_TEXT_COLOR = c
            textEdit.updateStylesheet()
            SETTINGS.setValue("colEditorText", c)

        elif var == EDITOR_HIGHLIGHT:
            EDITOR_HIGHLIGHT = c
            highlighter.deleteLater()
            textEdit.initHighlighter()
            SETTINGS.setValue("colEditHighlight", c)

        button.setStyleSheet("background-color: "+c+";")

















class SidebarDir(QPushButton):
    def __init__(self):
        super().__init__()
        self.setText("Drop directory here")
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        self.url = e.mimeData().urls()[0].toLocalFile()
        i = 0
        for f in e.mimeData().urls():
            i += 1
        if i == 1 and QDir(self.url).exists():
            e.accept()
        else:
            pass

    def dropEvent(self, e):
        global NOTE_PATH
        NOTE_PATH = self.url

        SETTINGS.setValue("dir", self.url)
        sidebarGrid.addWidget(Tree(), 0, 0)
        self.deleteLater()








class Sidebar(QWidget):
    def __init__(self, grid):
        super().__init__()
        global sidebarGrid, sidebarPanel, settingsWidget, cog
        sidebarPanel = self

        self.setAttribute(Qt.WA_StyledBackground)
        self.setMinimumWidth(180)
        self.setMaximumWidth(550)


        sidebarGrid = QGridLayout()
        sidebarGrid.setSpacing(0)
        sidebarGrid.setContentsMargins(0,0,0,0)

        treePanel = QHBoxLayout()
        cogwheel = QPushButton("\uE008")
        cogwheel.clicked.connect(lambda: self.showSettings(grid))
        cogwheel.setObjectName("cogwheel")

        treePanel.addWidget(cogwheel)
        treePanel.addStretch(1)
        cog = cogwheel


        settingsWidget = Settings()
        self.activeSettings = False


        if NOTE_PATH:
            if not QDir().exists(NOTE_PATH):
                sidebarGrid.addWidget(SidebarDir(), 0, 0)
                settingsWidget.removeDir()
            else:
                sidebarGrid.addWidget(Tree(), 0, 0)
        else:
            sidebarGrid.addWidget(SidebarDir(), 0, 0)


        sidebarGrid.addLayout(treePanel, 1, 0)
        self.setLayout(sidebarGrid)
        self.updateStylesheet()


    def updateStylesheet(self):
        self.setStyleSheet("QWidget{background-color: "+TREE_COLOR+";}QPushButton{border: none; color: "+TREE_TEXT_COLOR+"}QPushButton#cogwheel{font-family: qicons; font-size: "+str(ICON_SIZE)+"px; color: "+ICON_COLOR+"; width: "+str(TITLE_HEIGHT)+"px; height: "+str(TITLE_HEIGHT)+"px;}QPushButton#cogwheel:pressed{color: "+Main.iconColor()+";}")

    def showSettings(self, grid):
        # button background flash, temporary delay fix
        time.sleep(0.02)
        main.setUpdatesEnabled(False)
        if not self.activeSettings:
            grid.addWidget(settingsWidget, 1, 0)
            Grips.raiseGrips()
            self.activeSettings = True
        else:
            settingsWidget.show()
        main.setUpdatesEnabled(True)


        

        









class Main(QWidget): 
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        QFontDatabase().addApplicationFont("icons/qicons.ttf")

        baseGrid = QGridLayout()
        innerGrid = QGridLayout()


        self.hSplitter = QSplitter()
        self.hSplitter.addWidget(Sidebar(innerGrid))
        self.hSplitter.addWidget(Text())

        self.hSplitter.setHandleWidth(0)
        self.hSplitter.setStretchFactor(1, 1)
        self.hSplitter.splitterMoved.connect(self.handleMove)

        innerGrid.setSpacing(0)
        innerGrid.addWidget(Titlebar(self), 0, 0)
        innerGrid.addWidget(self.hSplitter, 1, 0)

        baseGrid.addLayout(innerGrid, 0, 0)
        self.setLayout(baseGrid)


        grips = [Grips(self, "top"), Grips(self, "left"), Grips(self, "bottom"), Grips(self, "right")]
        Grips.setGrips(self, baseGrid)
        Grips.toggleGripVisibility(self)


        self.sidebarWidth = SETTINGS.value("geoTree") if SETTINGS.value("geoTree") is not None else 256
        try:
            self.hSplitter.setSizes([self.sidebarWidth, 1])
        except:
            pass

        self.restoreGeometry(bytearray(SETTINGS.value("geo"))) if SETTINGS.value("geo") else self.resize(self.screen().availableGeometry().size() / 2)

        self.updateStylesheet()
     

    def updateStylesheet(self):
        self.setStyleSheet("font-size: "+str(FONT_SIZE)+"px;font-family: "+returnVal(FONT_FAMILY, app.font().family())+";")

    def iconColor():
        c = QColor(ICON_COLOR)
        if c.value() > 50:
            return QColor().fromHsv(c.hue(),c.saturation(),c.value() - 50).name()
        else:
            return QColor().fromHsv(c.hue(),c.saturation(),c.value() + 50).name()

    def selectedColor():
        c = QColor(TREE_COLOR)
        if c.value() < 240:
            return QColor().fromHsv(c.hue(),c.saturation(),c.value() + 10).name()
        else:
            return QColor().fromHsv(c.hue(),c.saturation(),c.value() - 10).name()

    def selectionColor():
        c = QColor(EDITOR_COLOR)
        if c.value() > 127:
            return QColor().fromHsv(c.hue(),c.saturation(),c.value() - 40).name()
        else:
            return QColor().fromHsv(c.hue(),c.saturation(),c.value() + 40).name()


    def handleMove(self, pos):
        self.sidebarWidth = pos

    def toggleSidebar(self):
        if self.hSplitter.sizes()[0] != 0:
            self.hSplitter.setSizes([0,
             1])
        elif self.sidebarWidth == 0:
            self.hSplitter.setSizes([255, 1])
        else:
            self.hSplitter.setSizes([self.sidebarWidth, 1])

    def closeEvent(self, e):
        textEdit.saveNote()
        SETTINGS.setValue("geo", self.saveGeometry())
        SETTINGS.setValue("geoTree", self.hSplitter.sizes()[0])

        if NOTE_PATH:
            treeState = []
            for root, dirs, files in os.walk(NOTE_PATH):
                for d in dirs:
                    if fileTree.isExpanded(fileTree.model().index(os.path.join(root, d))):
                        treeState.append(1)
                    else:
                        treeState.append(0)
            SETTINGS.setValue("treeState", treeState)






if __name__ == "__main__":
    app = QApplication([])

    app.setWindowIcon(QIcon("icons/icon.ico"))
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('app')

    main = Main()
    main.show()
    sys.exit(app.exec())


            

        