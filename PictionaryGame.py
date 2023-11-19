# Inspired by PyQt5 Creating Paint Application In 40 Minutes
#  https://www.youtube.com/watch?v=qEgyGyVA1ZQ

# NB If the menus do not work then click on another application and then click back
# and they will work https://python-forum.io/Thread-Tkinter-macOS-Catalina-and-Python-menu-issue

# PyQt documentation links are prefixed with the word 'documentation' in the code below and can be accessed automatically
#  in PyCharm using the following technique https://www.jetbrains.com/help/pycharm/inline-documentation.html

from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QDockWidget, QPushButton, QVBoxLayout, \
    QLabel, QMessageBox, QSlider, QColorDialog, QComboBox, QSizePolicy
from PyQt6.QtGui import QIcon, QPainter, QPen, QAction, QPixmap, QFont
import sys
import csv, random
from PyQt6.QtCore import Qt, QPoint


class PictionaryGame(QMainWindow):  # documentation https://doc.qt.io/qt-6/qwidget.html
    '''
    Painting Application class
    '''

    def __init__(self):
        super().__init__()

        # set window title
        self.setWindowTitle("Pictionary Game - A2 Template")

        # set the windows dimensions
        top = 400
        left = 400
        width = 800
        height = 600
        self.setGeometry(top, left, width, height)

        # set the icon
        # windows version
        self.setWindowIcon(
            QIcon("./icons/paint-brush.png"))  # documentation: https://doc.qt.io/qt-6/qwidget.html#windowIcon-prop
        # mac version - not yet working
        # self.setWindowIcon(QIcon(QPixmap("./icons/paint-brush.png")))

        # image settings (default)
        self.image = QPixmap("./icons/canvas.png")  # documentation: https://doc.qt.io/qt-6/qpixmap.html
        self.image.fill(Qt.GlobalColor.white)  # documentation: https://doc.qt.io/qt-6/qpixmap.html#fill
        mainWidget = QWidget()
        mainWidget.setMaximumWidth(300)

        # draw settings (default)
        self.drawing = False
        self.brushSize = 3
        self.brushColor = Qt.GlobalColor.black  # documentation: https://doc.qt.io/qt-6/qt.html#GlobalColor-enum

        # This is an extra feature
        # ----------------------------------------------------------------------------
        # Set the font for the entire application
        self.setFont(QFont("Roboto", 12))

        # Set the color scheme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QMenuBar {
                background-color: #2c3e50;
                color: white;
                font-size: 15px;
                font: "Roboto";
            }
            QMenuBar::item {
                background-color: #2c3e50;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #34495e;
            }
            QMenu {
                background-color: #2c3e50;
                color: white;
            }
            QMenu::item {
                background-color: #2c3e50;
                color: white;
            }
            QMenu::item:selected {
                background-color: #34495e;
            }
            QLabel {
                color: #333333;
            }
            QSlider {
                background-color: #2c3e50;
                color: white;
            }
            QSlider::groove:horizontal {
                border: 1px solid #2c3e50;
                height: 10px;
                background: #34495e;
            }
            QSlider::handle:horizontal {
                background: white;
                border: 1px solid #2c3e50;
                width: 20px;
                margin: -5px 0;
            }
            QDockWidget {
                background-color: #f0f0f0;
            }
        """)

        # ----------------------------------------------------------------------------------------

        # reference to last point recorded by mouse
        self.lastPoint = QPoint()  # documentation: https://doc.qt.io/qt-6/qpoint.html

        # keeping track of the game, scores and turn
        self.currentTurn = 1
        self.p1score = 0
        self.p2score = 0
        self.gameStarted = False

        # Brush size slider
        self.brushSizeSlider = QSlider(Qt.Orientation.Horizontal)
        self.brushSizeSlider.setMinimum(1)
        self.brushSizeSlider.setMaximum(10)
        self.brushSizeSlider.setValue(self.brushSize)
        self.brushSizeSlider.valueChanged.connect(self.changeBrushSize)

        # set up menus
        mainMenu = self.menuBar()  # create a menu bar
        mainMenu.setNativeMenuBar(False)
        fileMenu = mainMenu.addMenu(" File")  # add the file menu to the menu bar, the space is required as "File" is reserved in Mac
        brushSizeMenu = mainMenu.addMenu(" Brush Size")  # add the "Brush Size" menu to the menu bar
        brushColorMenu = mainMenu.addMenu(" Brush Colour")  # add the "Brush Colour" menu to the menu bar

        # save menu item
        saveAction = QAction(QIcon("./icons/save.png"), "Save", self)  # create a save action with a png as an icon, documentation: https://doc.qt.io/qt-6/qaction.html
        saveAction.setShortcut("Ctrl+S")  # connect this save action to a keyboard shortcut, documentation: https://doc.qt.io/qt-6/qaction.html#shortcut-prop
        fileMenu.addAction(saveAction)  # add the save action to the file menu, documentation: https://doc.qt.io/qt-6/qwidget.html#addAction
        saveAction.triggered.connect(self.save)  # when the menu option is selected or the shortcut is used the save slot is triggered, documentation: https://doc.qt.io/qt-6/qaction.html#triggered

        # copy menu item
        copyAction = QAction(QIcon("./icons/copy.png"), "Copy", self)  # create a copy action with a png as an icon
        copyAction.setShortcut("Ctrl+F")  # connect this copy action to a keyboard shortcut
        fileMenu.addAction(copyAction)  # add the copy action to the file menu
        copyAction.triggered.connect(
            self.copy)  # when the menu option is selected or the shortcut is used the copy slot is triggered

        # cut menu item
        cutAction = QAction(QIcon("./icons/cut.png"), "Cut", self)  # create a cut action with a png as an icon
        cutAction.setShortcut("Ctrl+X")  # connect this cut action to a keyboard shortcut
        fileMenu.addAction(cutAction)  # add the cut action to the file menu
        cutAction.triggered.connect(
            self.cut)  # when the menu option is selected or the shortcut is used the cut slot is triggered

        # paste menu item
        pasteAction = QAction(QIcon("./icons/paste.png"), "Paste", self)  # create a paste action with a png as an icon
        pasteAction.setShortcut("Ctrl+V")  # connect this paste action to a keyboard shortcut
        fileMenu.addAction(pasteAction)  # add the paste action to the file menu
        pasteAction.triggered.connect(
            self.paste)  # when the menu option is selected or the shortcut is used the paste slot is triggered

        # new menu item
        newAction = QAction(QIcon("./icons/new.png"), "New", self)  # create a new action with a png as an icon
        newAction.setShortcut("Ctrl+N")  # connect this new action to a keyboard shortcut
        fileMenu.addAction(newAction)  # add the new action to the file menu
        newAction.triggered.connect(
            self.new)  # when the new option is selected or the shortcut is used the new slot is triggered

        # exit menu item
        exitAction = QAction(QIcon("./icons/exit.png"), "Exit", self)  # create an exit action with a png as an icon
        exitAction.setShortcut("Ctrl+Q")  # connect this exit action to a keyboard shortcut
        fileMenu.addAction(exitAction)  # add the exit action to the file menu
        exitAction.triggered.connect(
            self.close)  # when the new option is selected or the shortcut is used the exit slot is triggered

        # save as menu item
        saveAsAction = QAction(QIcon("./icons/saveas.png"), "Save As...",
                               self)  # create a save as action with a png as an icon
        saveAsAction.setShortcut("Ctrl+Shift+S")  # connect this save as action to a keyboard shortcut
        fileMenu.addAction(saveAsAction)  # add the save as action to the file menu
        saveAsAction.triggered.connect(
            self.saveAs)  # when the save as option is selected or the shortcut is used the save as slot is triggered

        # clear
        clearAction = QAction(QIcon("./icons/clear.png"), "Clear", self)  # create a clear action with a png as an icon
        clearAction.setShortcut("Ctrl+C")  # connect this clear action to a keyboard shortcut
        fileMenu.addAction(clearAction)  # add this action to the file menu
        clearAction.triggered.connect(self.clear)  # when the menu option is selected or the shortcut is used the clear slot is triggered

        # brush thickness
        threepxAction = QAction(QIcon("./icons/threepx.png"), "3px", self)
        threepxAction.setShortcut("Ctrl+3")
        brushSizeMenu.addAction(threepxAction)  # connect the action to the function below
        threepxAction.triggered.connect(self.threepx)

        fivepxAction = QAction(QIcon("./icons/fivepx.png"), "5px", self)
        fivepxAction.setShortcut("Ctrl+5")
        brushSizeMenu.addAction(fivepxAction)
        fivepxAction.triggered.connect(self.fivepx)

        sevenpxAction = QAction(QIcon("./icons/sevenpx.png"), "7px", self)
        sevenpxAction.setShortcut("Ctrl+7")
        brushSizeMenu.addAction(sevenpxAction)
        sevenpxAction.triggered.connect(self.sevenpx)

        ninepxAction = QAction(QIcon("./icons/ninepx.png"), "9px", self)
        ninepxAction.setShortcut("Ctrl+9")
        brushSizeMenu.addAction(ninepxAction)
        ninepxAction.triggered.connect(self.ninepx)

        # brush colors
        blackAction = QAction(QIcon("./icons/black.png"), "Black", self)
        blackAction.setShortcut("Ctrl+B")
        brushColorMenu.addAction(blackAction);
        blackAction.triggered.connect(self.black)

        redAction = QAction(QIcon("./icons/red.png"), "Red", self)
        redAction.setShortcut("Ctrl+R")
        brushColorMenu.addAction(redAction);
        redAction.triggered.connect(self.red)

        greenAction = QAction(QIcon("./icons/green.png"), "Green", self)
        greenAction.setShortcut("Ctrl+G")
        brushColorMenu.addAction(greenAction);
        greenAction.triggered.connect(self.green)

        yellowAction = QAction(QIcon("./icons/yellow.png"), "Yellow", self)
        yellowAction.setShortcut("Ctrl+Y")
        brushColorMenu.addAction(yellowAction);
        yellowAction.triggered.connect(self.yellow)

        colorPickerAction = QAction(QIcon("./icons/color-picker.png"), "Color Picker", self)
        brushColorMenu.addAction(colorPickerAction)
        colorPickerAction.triggered.connect(self.colorPicker)

        # Side Dock
        self.dockInfo = QDockWidget()
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockInfo)

        # Create a widget to display the player information and game controls
        self.playerInfo = QWidget()

        # Set the layout of the widget to a vertical box layout
        self.vbdock = QVBoxLayout()
        self.playerInfo.setLayout(self.vbdock)

        # Set the maximum size of the widget to fit the dock
        self.playerInfo.setMaximumSize(100, self.height())
        self.playerInfo.setMaximumSize(135, self.width())

        # Add a label to show the current player turn
        self.playerTurn = QLabel("Player Turn: " + str(self.currentTurn))
        self.vbdock.addWidget(self.playerTurn)
        self.vbdock.addSpacing(10)

        # Add a label to show the scores
        self.vbdock.addWidget(QLabel("Scores:"))

        # Add labels to show the scores of player 1 and 2
        self.P1ScoreLabel = QLabel("Player 1: " + str(self.p1score))
        self.P2ScoreLabel = QLabel("Player 2: " + str(self.p2score))

        # Add the score labels to the widget
        self.vbdock.addWidget(self.P1ScoreLabel)
        self.vbdock.addWidget(self.P2ScoreLabel)

        # Add a stretch to fill the remaining space
        self.vbdock.addStretch(1)

        # Add a label and a combo box to select the mode
        self.modeLabel = QLabel("Select mode:")
        self.selectMode = QComboBox()
        self.selectMode.addItem("easy")
        self.selectMode.addItem("hard")

        # Add a button to start the game
        self.btnStart = QPushButton("Start ")

        # Add a button to mark the guess as submit
        self.btnGuessed = QPushButton("Submit")

        # Add the mode label, combo box, and buttons to the widget
        self.vbdock.addWidget(self.modeLabel)
        self.vbdock.addWidget(self.selectMode)
        self.vbdock.addSpacing(10)
        self.vbdock.addWidget(self.btnStart)
        self.vbdock.addSpacing(5)
        self.vbdock.addWidget(self.btnGuessed)
        self.vbdock.addSpacing(5)
        # Widget to change the size of the brush
        self.vbdock.addWidget(self.brushSizeSlider)

        # Connect the button clicks to the corresponding functions
        self.btnStart.clicked.connect(self.start)
        self.btnGuessed.clicked.connect(lambda: self.guessedCorrectly())

        # Connect the mode selection to the corresponding function
        self.selectMode.currentIndexChanged.connect(self.chooseMode)

        # Set the background color of the widget to gray
        self.playerInfo.setAutoFillBackground(True)
        p = self.playerInfo.palette()
        p.setColor(self.playerInfo.backgroundRole(), Qt.GlobalColor.gray)
        self.playerInfo.setPalette(p)

        # Set the widget as the content of the dock
        self.dockInfo.setWidget(self.playerInfo)

        # Get the list of words for the game
        self.getList("easy")
        self.currentWord = self.getWord()

    # event handlers
    def mousePressEvent(self, event):  # when the mouse is pressed, documentation: https://doc.qt.io/qt-6/qwidget.html#mousePressEvent
        if event.button() == Qt.MouseButton.LeftButton:  # if the pressed button is the left button
            self.drawing = True  # enter drawing mode
            self.lastPoint = event.pos()  # save the location of the mouse press as the lastPoint
            print(self.lastPoint)  # print the lastPoint for debugging purposes

    def mouseMoveEvent(self, event):  # when the mouse is moved, documenation: documentation: https://doc.qt.io/qt-6/qwidget.html#mouseMoveEvent
        if self.drawing:
            painter = QPainter(self.image)  # object which allows drawing to take place on an image
            # allows the selection of brush colour, brish size, line type, cap type, join type. Images available here http://doc.qt.io/qt-6/qpen.html
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawLine(self.lastPoint, event.pos())  # draw a line from the point of the orginal press to the point to where the mouse was dragged to
            self.lastPoint = event.pos()  # set the last point to refer to the point we have just moved to, this helps when drawing the next line segment
            self.update()  # call the update method of the widget which calls the paintEvent of this class

    def mouseReleaseEvent(self, event):  # when the mouse is released, documentation: https://doc.qt.io/qt-6/qwidget.html#mouseReleaseEvent
        if event.button() == Qt.MouseButton.LeftButton:  # if the released button is the left button, documentation: https://doc.qt.io/qt-6/qt.html#MouseButton-enum ,
            self.drawing = False  # exit drawing mode

    # paint events
    def paintEvent(self, event):
        # you should only create and use the QPainter object in this method, it should be a local variable
        canvasPainter = QPainter(self)  # create a new QPainter object, documentation: https://doc.qt.io/qt-6/qpainter.html
        canvasPainter.drawPixmap(QPoint(), self.image)  # draw the image , documentation: https://doc.qt.io/qt-6/qpainter.html#drawImage-1

    # resize event - this function is called
    def resizeEvent(self, event):
        self.image = self.image.scaled(self.width(), self.height())

        # This function allows the user to Change brush size

    def changeBrushSize(self, value):
        self.brushSize = value

    def colorPicker(self):  # This function allows the user to choose a color from a dialog box
        color = QColorDialog.getColor()  # Get the color selected by the user
        if color.isValid():  # Check if the color is valid
            self.brushColor = color  # Set the brush color to the selected color

    # slots
    def save(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                  "PNG(*.png);;JPG(*.jpg *.jpeg);;All Files (*.*)")
        if filePath == "":  # if the file path is empty
            return  # do nothing and return
        self.image.save(filePath)  # save file image to the file path

    def clear(self):
        self.image.fill(
            Qt.GlobalColor.white)  # fill the image with white, documentation: https://doc.qt.io/qt-6/qimage.html#fill-2
        self.update()  # call the update method of the widget which calls the paintEvent of this class

    def new(self):
        self.image.fill(Qt.GlobalColor.white)  # Fills the image with white color
        self.brushSize = 3  # Sets the brush size to 3
        self.brushColor = Qt.GlobalColor.black  # Sets the brush color to black
        self.update()  # Updates the GUI

    def copy(self):
        self.image.save("./temp/copy.png")  # save the current image to a temporary file named copy.png
        self.update()  # Updates the GUI

    def cut(self):
        self.image.save("./temp/cut.png")  # save the current image to a temporary file named cut.png
        self.image.fill(Qt.GlobalColor.white)  # Sets the brush color to white
        self.update()  # Updates the GUI

    def paste(self):
        self.image.load("./temp/copy.png")  # load the image from the temporary file named copy.png
        self.update()  # Updates the GUI

    def saveAs(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image As...", "",
                                                  "PNG(*.png);;JPG(*.jpg *.jpeg);;All Files (*.*)")
        if filePath == "":  # if the file path is empty
            return  # do nothing and return
        self.image.save(filePath)  # save file image to the file path
    def threepx(self):  # the brush size is set to 3
        self.brushSize = 3

    def fivepx(self):
        self.brushSize = 5

    def sevenpx(self):
        self.brushSize = 7

    def ninepx(self):
        self.brushSize = 9

    def black(self):  # the brush color is set to black
        self.brushColor = Qt.GlobalColor.black

    def black(self):
        self.brushColor = Qt.GlobalColor.black

    def red(self):
        self.brushColor = Qt.GlobalColor.red

    def green(self):
        self.brushColor = Qt.GlobalColor.green

    def yellow(self):
        self.brushColor = Qt.GlobalColor.yellow

        # easy mode

    def easyMode(self):
        self.getList("easy")
        self.currentWord = self.getWord()

        # hard mode

    def hardMode(self):
        self.getList("hard")
        self.currentWord = self.getWord()

        # choose mode, easy or hard word

    def chooseMode(self):
        if self.selectMode.currentText() == "easy":
            self.easyMode()
        else:
            self.hardMode()

        # start function

    def start(self):
        # checks if game has started
        if self.gameStarted:
            print("Turn Skipped")
            # switches turn from 1 to 2 when turn is skipped
            if self.currentTurn == 1:
                self.currentTurn = 2

                # Updating the current turn label
                self.playerTurn.setText("Player Turn: " + str(self.currentTurn))
                self.playerTurn.update()
            else:
                self.currentTurn = 1

                # Updating the current turn label
                self.playerTurn.setText("Player's Turn: " + str(self.currentTurn))
                self.playerTurn.update()

            # getting word
            self.chooseMode()

            # message box with player word and instructions
            msg = QMessageBox(self)
            msg.setWindowTitle("Pictionary")
            msg.setText("Turn skipped!\n\n Player " + str(self.currentTurn) + " word:")
            msg.setInformativeText("Don't let others see, Press details!")
            msg.setDetailedText(self.currentWord)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.show()
            self.clear()
            self.update()

        else:
            self.gameStarted = True
            # changes start button to Skip Turn
            self.btnStart.setText("Skip Turn")

            # getting the words
            self.chooseMode()

            # Message box with word and instructions
            msg = QMessageBox(self)
            msg.setWindowTitle("Pictionary")
            msg.setText("Player " + str(self.currentTurn) + " See your word")
            msg.setInformativeText("Don't let others see, Press Details")
            msg.setDetailedText(self.currentWord)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.show()
            self.clear()
            self.update()

        # Adding scores if guessed correctly

    def guessedCorrectly(self):
        self.clear()
        if self.gameStarted:
            print("Guessed correctly")
            if self.currentTurn == 1:

                # Add to score
                # extra scores are added if mode is hard
                if self.selectMode.currentText() == "easy":
                    self.p1score += 2
                    self.p2score += 1
                else:
                    self.p1score += 3
                    self.p2score += 2

                # update the score label
                self.P1ScoreLabel.setText("Player 1: " + str(self.p1score))
                self.P2ScoreLabel.setText("Player 2: " + str(self.p2score))
                self.P1ScoreLabel.update()
                self.P2ScoreLabel.update()

                # switch turn to player 2
                self.currentTurn = 2

                # update the turn label
                self.playerTurn.setText("Player Turn: " + str(self.currentTurn))
                self.playerTurn.update()

                # get the words
                self.chooseMode()

                # message box with word and instructions
                msg = QMessageBox(self)
                msg.setWindowTitle("Pictionary")
                # Extra feature Set a larger font for the main text
                font = QFont()
                font.setPointSize(16)  # Set your desired font size
                msg.setFont(font)
                msg.setText("Player " + str(self.currentTurn) + " See your word")
                msg.setInformativeText("Don't let others see, Press Details")
                msg.setDetailedText(self.currentWord)
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.show()
                self.clear()
                self.update()

            else:
                # Add to score
                # extra scores are added if mode is hard
                if self.selectMode.currentText() == "easy":
                    self.p1score += 1
                    self.p2score += 2
                else:
                    self.p1score += 2
                    self.p2score += 3

                # update the label
                self.P1ScoreLabel.setText("Player 1: " + str(self.p1score))
                self.P2ScoreLabel.setText("Player 2: " + str(self.p2score))
                self.P1ScoreLabel.update()
                self.P2ScoreLabel.update()

                # switch turn to player 1
                self.currentTurn = 1

                # update the turn label
                self.playerTurn.setText("Player Turn: " + str(self.currentTurn))
                self.playerTurn.update()

                # get the words
                self.chooseMode()

                # message box with word and instructions
                msg = QMessageBox(self)
                msg.setWindowTitle("Pictionary")
                msg.setText("Player " + str(self.currentTurn) + " See your word")
                msg.setInformativeText("Don't let others see, Press Details")
                msg.setDetailedText(self.currentWord)
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.show()
                self.clear()
                self.update()

    #Get a random word from the list read from file
    def getWord(self):
        randomWord = random.choice(self.wordList)
        print(randomWord)
        return randomWord

    #read word list from file
    def getList(self, mode):
        with open(mode + 'mode.txt') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                #print(row)
                self.wordList = row
                line_count += 1
            #print(f'Processed {line_count} lines.')

    # open a file
    def open(self):
        '''
        This is an additional function which is not part of the tutorial. It will allow you to:
         - open a file dialog box,
         - filter the list of files according to file extension
         - set the QImage of your application (self.image) to a scaled version of the file)
         - update the widget
        '''
        filePath, _ = QFileDialog.getOpenFileName(self, "Open Image", "",
                                                  "PNG(*.png);;JPG(*.jpg *.jpeg);;All Files (*.*)")
        if filePath == "":  # if not file is selected exit
            return
        with open(filePath, 'rb') as f:  # open the file in binary mode for reading
            content = f.read()  # read the file
        self.image.loadFromData(content)  # load the data into the file
        width = self.width()  # get the width of the current QImage in your application
        height = self.height()  # get the height of the current QImage in your application
        self.image = self.image.scaled(width, height)  # scale the image from file and put it in your QImage
        self.update()  # call the update method of the widget which calls the paintEvent of this class


# this code will be executed if it is the main module but not if the module is imported
#  https://stackoverflow.com/questions/419163/what-does-if-name-main-do
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Roboto", 14))
    app.setStyleSheet("QMessageBox { min-width: 500px; min-height: 300px; }")
    window = PictionaryGame()
    window.show()
    app.exec()  # start the event loop running
