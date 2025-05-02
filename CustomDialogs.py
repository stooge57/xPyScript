# This file is under MIT license. The license file can be obtained in the root directory of this module.

import copy, helpResource, time
from PyQt6.QtGui import QFontMetrics, QIntValidator
from PyQt6.QtCore import QFile, QIODevice, Qt, QTextStream, QTimer, QUrl
from PyQt6.QtWidgets import QApplication, QColorDialog, QDialog, QFileDialog, QHBoxLayout, \
   QLineEdit, QMessageBox, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget
from AppSettingsDlg import Ui_AppSettingsDlg
from ExportProgressDlg import Ui_ExportProgressDlg
from FileSettingsDlg import Ui_FileSettingsDlg
from HelpDlg import Ui_HelpDlg
from NewSequenceDlg import Ui_NewSequenceDlg

class AppSettingsDlg(QDialog):
   def __init__(self, margin, nodeDiameter, bHideOffNodes, backgroundColor, offNodeColor,
         bMulticast, ipAddress, parent=None):
      super().__init__(parent)
      self.ui = Ui_AppSettingsDlg()
      self.ui.setupUi(self)
      self.displayMargin = margin
      self.nodeDiameter = nodeDiameter
      self.bHideOffNodes = bHideOffNodes
      self.backgroundColor = backgroundColor
      self.offNodeColor = offNodeColor
      self.bMulticast = bMulticast
      self.ipAddress = ipAddress
      self.ui.nodeDiameter.setValue(nodeDiameter)
      self.ui.hideOffNodes.setChecked(bHideOffNodes)
      self.ui.displayMargin.setValue(margin)
      self.ui.backgroundColorTb.color = backgroundColor
      self.ui.offNodeColorTb.color = offNodeColor
      self.ui.multicast.setChecked(bMulticast)
      self.ui.ipAddress.setText(ipAddress)
      self.ui.label_4.setEnabled(not bMulticast)
      self.ui.ipAddress.setEnabled(not bMulticast)
      self.ui.backgroundColorTb.clicked.connect(self.chooseBackgroundColor)
      self.ui.multicast.stateChanged.connect(self.checkboxChange)
      self.ui.offNodeColorTb.clicked.connect(self.chooseOffNodeColor)

   def accept(self):
      super().accept()
      self.nodeDiameter = self.ui.nodeDiameter.value()
      self.displayMargin = self.ui.displayMargin.value()
      self.bHideOffNodes = self.ui.hideOffNodes.isChecked()
      self.bMulticast = self.ui.multicast.isChecked()
      self.ipAddress = self.ui.ipAddress.text()

   def checkboxChange(self, state):
      bEnabled = (state == Qt.CheckState.Unchecked.value)
      self.ui.label_4.setEnabled(bEnabled)
      self.ui.ipAddress.setEnabled(bEnabled)
   
   def chooseBackgroundColor(self):
      color = QColorDialog.getColor(self.backgroundColor, self, "Choose background color")
      if color.isValid():
         self.backgroundColor = color
         self.ui.backgroundColorTb.color = color

   def chooseOffNodeColor(self):
      color = QColorDialog.getColor(self.offNodeColor, self, "Choose off node color")
      if color.isValid():
         self.offNodeColor = color
         self.ui.offNodeColorTb.color = color

class ExportProgressDlg(QDialog):
   def __init__(self, exportLength, parent=None):
      super().__init__(parent)
      self.ui = Ui_ExportProgressDlg()
      self.ui.setupUi(self)
      self.exportLength = exportLength
      self.progressTimeRef = time.perf_counter()
      self.progressTimer = QTimer()
      self.progressTimer.timeout.connect(self.progressTimeout)
      self.progressTimer.start(50)

   def progressTimeout(self):
      elapsed = time.perf_counter() - self.progressTimeRef
      elapsedPercent = min(100, round((elapsed / self.exportLength) * 100))
      self.ui.progressBar.setValue(elapsedPercent)
      if elapsed >= self.exportLength:
         self.accept()

class FileSettingsDlg(QDialog):
   def __init__(self, rotation, stretch, author, email, comment, numPixels, ranges, parent=None):
      super().__init__(parent)
      self.ui = Ui_FileSettingsDlg()
      self.ui.setupUi(self)
      self.channelsPerUniverse = 510
      self.channelsPerPixel = 3
      self.numPorts = 48
      self.rotation = rotation
      self.stretch = stretch
      self.author = author
      self.email = email
      self.comment = comment
      self.numPixels = numPixels
      self.ranges = ranges.copy()
      self.ui.rotation.setValue(self.rotation)
      self.ui.stretchFactor.setValue(self.stretch)
      self.ui.author.setText(self.author)
      self.ui.email.setText(self.email)
      self.ui.comment.setPlainText(self.comment)
      self.ui.numPortsSpinBox.valueChanged.connect(self.onNumPortsValueChanged)
      self.ui.numPixelsLineEdit.setText(str(numPixels))
      self.createStringTable()
      self.updateStringTable()

   def accept(self):
      if not self.checkEmptyFields():
         self.ui.tabWidget.setCurrentIndex(1)
         QMessageBox.warning(self, "Mapping Error", "There are empty fields!")
         return
      self.validateFocus()
      if self.numPixelsMapped() != self.numPixels:
         self.ui.tabWidget.setCurrentIndex(1)
         QMessageBox.warning(self, "Mapping Error",
            "'Num Pixels' mapped does not equal 'Total number of pixels'!")
         return
      if self.calculateRanges():
         self.ui.tabWidget.setCurrentIndex(1)
         QMessageBox.warning(self, "Mapping Error",
            "There is a channel overlap between strings!")
         return
      self.rotation = self.ui.rotation.value()
      self.stretch = self.ui.stretchFactor.value()
      self.author = self.ui.author.text()
      self.email = self.ui.email.text()
      self.comment = self.ui.comment.toPlainText()
      super().accept()

   def calculateEndUniverseAndChannels(self):
      nPorts = int(self.ui.numPortsSpinBox.text())
      for nString in range(nPorts):
         startUniverseText = self.getObject(f"StartUniverseLineEdit_{nString+1}").text()
         startChannelText = self.getObject(f"StartChannelLineEdit_{nString+1}").text()
         numPixelsText = self.getObject(f"NumPixelsLineEdit_{nString+1}").text()
         if (not startUniverseText) or (not startChannelText) or (not numPixelsText):
            self.getObject(f"EndUniverseLineEdit_{nString+1}").clear()
            self.getObject(f"EndChannelLineEdit_{nString+1}").clear()
            continue
         startUniverse = int(startUniverseText)
         startChannel = int(startChannelText)
         numChannels = int(numPixelsText) * self.channelsPerPixel
         startChannelAbs = (startUniverse - 1) * self.channelsPerUniverse + startChannel
         endChannelAbs = startChannelAbs + numChannels - 1
         endUniverse = (endChannelAbs - 1) // self.channelsPerUniverse + 1
         endChannel = (endChannelAbs - 1) % self.channelsPerUniverse + 1
         self.getObject(f"EndUniverseLineEdit_{nString+1}").setText(str(endUniverse))
         self.getObject(f"EndChannelLineEdit_{nString+1}").setText(str(endChannel))

   def calculateRanges(self):
      self.ranges.clear()
      nPorts = int(self.ui.numPortsSpinBox.text())
      for nString in range(nPorts):
         startUniverse = int(self.getObject(f"StartUniverseLineEdit_{nString+1}").text())
         startChannel = int(self.getObject(f"StartChannelLineEdit_{nString+1}").text())
         numPixels = int(self.getObject(f"NumPixelsLineEdit_{nString+1}").text())
         totalChannels = numPixels * self.channelsPerPixel
         absoluteStart = (startUniverse - 1) * self.channelsPerUniverse + (startChannel)
         absoluteEnd = absoluteStart + totalChannels - 1
         self.ranges.append((absoluteStart, absoluteEnd))

      # Check for overlaps
      for i in range(len(self.ranges)):
         for j in range(i + 1, len(self.ranges)):
            start1, end1 = self.ranges[i]
            start2, end2 = self.ranges[j]
            if not ((end1 < start2) or (end2 < start1)):
               self.ranges.clear()
               return(True)  # overlap detected
      return(False)  # no overlaps

   def checkEmptyFields(self):
      nPorts = int(self.ui.numPortsSpinBox.text())
      for nString in range(nPorts):
         startUniverse = self.getObject(f"StartUniverseLineEdit_{nString+1}").text()
         startChannel = self.getObject(f"StartChannelLineEdit_{nString+1}").text()
         numPixels = self.getObject(f"NumPixelsLineEdit_{nString+1}").text()
         if (not startUniverse) or (not startChannel) or (not numPixels):
            return(False)
      return(True)

   def createStringTable(self):
      self.vBox = QVBoxLayout()   # main layout for all rows
      self.ui.scrollAreaWidgetContents.setLayout(self.vBox)
      for nString in range(self.numPorts):
         container = QWidget()  # create a container widget to hold the hBox
         container.setObjectName(f"StringRow_{nString+1}")
         hBox = QHBoxLayout(container)  # horizontal layout for row line edits
         hBox.setContentsMargins(0, 0, 0, 0)

         # add the line edit widgets to the row
         lineEdit = QLineEdit()
         lineEdit.setEnabled(False)
         lineEdit.setObjectName(f"StringLineEdit_{nString+1}")
         lineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
         lineEdit.setText(f"String{nString+1}")
         hBox.addWidget(lineEdit)

         lineEdit = QLineEdit()
         lineEdit.setMaxLength(5)
         lineEdit.setObjectName(f"StartUniverseLineEdit_{nString+1}")
         lineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
         lineEdit.setValidator(QIntValidator())
         lineEdit.editingFinished.connect(lambda lineEdit=lineEdit: self.validate(lineEdit))
         hBox.addWidget(lineEdit)

         lineEdit = QLineEdit()
         lineEdit.setMaxLength(3)
         lineEdit.setObjectName(f"StartChannelLineEdit_{nString+1}")
         lineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
         lineEdit.setValidator(QIntValidator())
         lineEdit.editingFinished.connect(lambda lineEdit=lineEdit: self.validate(lineEdit))
         hBox.addWidget(lineEdit)

         lineEdit = QLineEdit()
         lineEdit.setMaxLength(4)
         lineEdit.setObjectName(f"NumPixelsLineEdit_{nString+1}")
         lineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
         lineEdit.setValidator(QIntValidator())
         lineEdit.editingFinished.connect(lambda lineEdit=lineEdit: self.validate(lineEdit))
         hBox.addWidget(lineEdit)

         lineEdit = QLineEdit()
         lineEdit.setEnabled(False)
         lineEdit.setObjectName(f"EndUniverseLineEdit_{nString+1}")
         lineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
         hBox.addWidget(lineEdit)

         lineEdit = QLineEdit()
         lineEdit.setEnabled(False)
         lineEdit.setObjectName(f"EndChannelLineEdit_{nString+1}")
         lineEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
         hBox.addWidget(lineEdit)
         self.vBox.addWidget(container)
      spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
      self.vBox.addItem(spacer)

   def getObject(self, objectName):
      return(self.findChild(QWidget, objectName))

   def numPixelsMapped(self):
      numPixels = 0
      nPorts = int(self.ui.numPortsSpinBox.text())
      for nString in range(nPorts):
         numPixels += int(self.getObject(f"NumPixelsLineEdit_{nString+1}").text())
      return(numPixels)   

   def onNumPortsValueChanged(self, nPorts):
      self.showStringRows(nPorts)

   def showStringRows(self, nStrings):
      for nRow in range(nStrings):
         self.getObject(f"StringRow_{nRow+1}").setVisible(True)
      for nRow in range(nStrings, self.numPorts):
         self.getObject(f"StringRow_{nRow+1}").setVisible(False)

   def validate(self, lineEdit):
      objName = lineEdit.objectName()
      if objName.startswith("StartUniverseLineEdit"):
         universe = int(lineEdit.text())
         universe = max(1, min(universe, 63999))  # Clamp result to valid range
         lineEdit.setText(str(universe))
      elif objName.startswith("StartChannelLineEdit"):
         channel = int(lineEdit.text())
         remainder = channel % self.channelsPerPixel
         if remainder == 0:
            channel = channel + 1  # Round up
         elif remainder == 2:
            channel = channel - 1  # Round down
         channel = max(1, min(channel, 508))  # Clamp result to valid range
         lineEdit.setText(str(channel))
      elif objName.startswith("NumPixelsLineEdit"):
         numPixels = int(lineEdit.text())
         numPixels = max(1, min(numPixels, 9999))  # Clamp result to valid range
         lineEdit.setText(str(numPixels))
      self.calculateEndUniverseAndChannels()

   def updateStringTable(self):
      nStrings = len(self.ranges)
      self.showStringRows(nStrings)
      self.ui.numPortsSpinBox.setValue(nStrings)
      for nString in range(nStrings):
         absoluteStartChannel = self.ranges[nString][0]
         absoluteEndChannel = self.ranges[nString][1]
         startUniverse = (absoluteStartChannel // self.channelsPerUniverse) + 1
         startChannel = absoluteStartChannel % self.channelsPerUniverse
         numPixels = ((absoluteEndChannel - absoluteStartChannel) // self.channelsPerPixel) + 1
         self.getObject(f"StartUniverseLineEdit_{nString+1}").setText(str(startUniverse))
         self.getObject(f"StartChannelLineEdit_{nString+1}").setText(str(startChannel))
         self.getObject(f"NumPixelsLineEdit_{nString+1}").setText(str(numPixels))
      self.calculateEndUniverseAndChannels()

   def validateFocus(self):
      focusedWidget = QApplication.focusWidget()
      if isinstance(focusedWidget, QLineEdit):
         self.validate(focusedWidget)

class HelpDlg(QDialog):
   def __init__(self, parent=None):
      super().__init__(parent)
      self.ui = Ui_HelpDlg()
      self.ui.setupUi(self)
      f = QFile(":xPyScriptHelp.html")
      f.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text)
      istream = QTextStream(f)
      self.ui.textEdit.setHtml(istream.readAll())
      f.close()

class NewSequenceDlg(QDialog):
   def __init__(self, parent=None):
      super().__init__(parent)
      self.ui = Ui_NewSequenceDlg()
      self.ui.setupUi(self)
      self.fileName = ""
      self.modelPath = ""
      self.ui.pushButton1.clicked.connect(self.chooseSequenceName)
      self.ui.pushButton2.clicked.connect(self.chooseXlightsModel)
 
   def chooseSequenceName(self):
      fileName, ok = QFileDialog.getSaveFileName(self, "Choose sequence name",
         self.fileName, "xPyScript file(*.xscr)")
      if ok:
         self.fileName = fileName
         metrics = QFontMetrics(self.ui.lineEdit1.font())
         elidedText = metrics.elidedText(self.fileName,
            Qt.TextElideMode.ElideLeft, self.ui.lineEdit1.width())
         self.ui.lineEdit1.setPlaceholderText(elidedText)

   def chooseXlightsModel(self):
      fileName, ok = QFileDialog.getOpenFileName(self, "Choose xLight model",
         self.modelPath, "xLight model(*.xmodel)")
      if ok:
         self.modelPath = fileName
         metrics = QFontMetrics(self.ui.lineEdit2.font())
         elidedText = metrics.elidedText(self.modelPath,
            Qt.TextElideMode.ElideLeft, self.ui.lineEdit2.width())
         self.ui.lineEdit2.setPlaceholderText(elidedText)