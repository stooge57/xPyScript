# This file is under MIT license. The license file can be obtained in the root directory of this module.

import os, sys
from PyQt6.QtGui import QAction, QActionGroup
from PyQt6.QtCore import QEvent, QSettings, Qt
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QMenu, QStyleFactory
from collections import deque
from MainWindow import Ui_MainWindow

version = "0.1"

class MainWindow(QMainWindow, Ui_MainWindow):
   def __init__(self, parent=None):
      super().__init__(parent)
      self.ui = Ui_MainWindow()
      self.ui.setupUi(self)
      self.setCentralWidget(self.ui.modelView)      
      self.ui.modelView.mainWindow = self
      self.settings = QSettings("RCH_Software", "xPyScript")
      self.ui.modelView.readAppSettings()
      self.mruList = deque(maxlen=10)
      self.loadMruList()
      self.updateMruMenu()

      actionGroupNodeID = QActionGroup(self)
      actionGroupNodeID.setExclusive(True)
      actionGroupNodeID.addAction(self.ui.actionNodeIdOff)
      actionGroupNodeID.addAction(self.ui.actionNodeIdMultiple)
      actionGroupNodeID.addAction(self.ui.actionNodeIdWindow)

      self.ui.actionAppSettings.triggered.connect(self.ui.modelView.appSettings)
      self.ui.actionExit.triggered.connect(self.close)
      self.ui.actionExport.triggered.connect(self.ui.modelView.export)
      self.ui.actionFileSettings.triggered.connect(self.ui.modelView.fileSettings)
      self.ui.actionHelp.triggered.connect(self.ui.modelView.help)
      self.ui.actionInteractiveColor.triggered.connect(self.ui.modelView.interactiveColor)
      self.ui.actionNew.triggered.connect(self.ui.modelView.new)
      self.ui.actionNodeIdMultiple.triggered.connect(self.ui.modelView.nodeIdMultiple)
      self.ui.actionNodeIdOff.triggered.connect(self.ui.modelView.nodeIdOff)
      self.ui.actionNodeIdWindow.triggered.connect(self.ui.modelView.nodeIdWindow)
      self.ui.actionOpen.triggered.connect(self.ui.modelView.open)
      self.ui.actionOutput.triggered.connect(self.ui.modelView.outputToLights)
      self.ui.actionRun.triggered.connect(self.ui.modelView.run)
      self.ui.actionStop.triggered.connect(self.ui.modelView.stop)

      # add version label to statusbar
      self.versionLabel = QLabel()
      self.versionLabel.setAlignment(Qt.AlignmentFlag.AlignRight |
         Qt.AlignmentFlag.AlignVCenter)
      self.versionLabel.setText("  v" + version)
      self.ui.statusbar.addPermanentWidget(self.versionLabel, 0)

      self.ui.modelView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
      self.ui.modelView.customContextMenuRequested.connect(self.showContextMenu)
      self.ui.modelView.enableCommands()

   def addToMru(self, filePath):
      try:
         self.mruList.remove(filePath)
      except ValueError:
         pass
      self.mruList.appendleft(filePath)
      self.saveMruList()

   def closeEvent(self, event):
      self.ui.modelView.exit()
      event.accept()

   def event(self, event):
      # Disable status tip events so they don't show in the status bar
      if event.type() == QEvent.Type.StatusTip:
         return(True)  # return True to block the event
      return(super().event(event))
   
   def loadMruList(self):
      mru = self.settings.value("mruList")
      if mru:
         self.mruList.extend(mru)

   def openMruFile(self, filePath):
      if os.path.isfile(filePath):
         self.addToMru(filePath)
         self.ui.modelView.open(filePath)
      else:
         try:
            self.mruList.remove(filePath)
         except ValueError:
            pass
      self.updateMruMenu()

   def saveMruList(self):
      self.settings.setValue("mruList", list(self.mruList))

   def showContextMenu(self, pos):
      menu = QMenu(self)
      menu.addAction(self.ui.actionRun)
      menu.addAction(self.ui.actionStop)
      menu.addSeparator()
      menu.addAction(self.ui.actionOutput)
      menu.exec(self.ui.modelView.mapToGlobal(pos))

   def updateMruMenu(self):
      # clear mru files in menu
      for action in self.ui.menuFile.actions()[5:]:
         if action.isSeparator():
            break
         self.ui.menuFile.removeAction(action)
      # add new order of mru files in menu
      self.mruActions=[]
      for i, filePath in enumerate(self.mruList):
         mruAction = QAction(f"&{i + 1} {filePath}", self)
         mruAction.triggered.connect(lambda _, path=filePath: self.openMruFile(path))
         self.mruActions.append(mruAction)
      self.ui.menuFile.insertActions(action, self.mruActions)

if __name__ == '__main__':
   app = QApplication(sys.argv)
   app.setStyle(QStyleFactory.create('Fusion'))
   mainWnd = MainWindow()
   mainWnd.show()
   sys.exit(app.exec())