# This file is under MIT license. The license file can be obtained in the root directory of this module.

import copy, importlib, math, pathlib, re, sacn, time
from PyQt6.QtGui import QBrush, QColor, QGuiApplication, QPainter, QPen
from PyQt6.QtCore import QPoint, QRect, QSize, QTimer, QXmlStreamReader, QXmlStreamWriter
from PyQt6.QtWidgets import QInputDialog, QLabel, QMessageBox, QRubberBand
from PyQt6.QtCore import QThread
from CustomDialogs import *
from xPyScript import version
from enum import Enum

class Effect(object):
   def __init__(self, color, startTime, endTime):
      self.color = color
      self.startTime = startTime
      self.endTime = endTime

class ExportFrame(object):
   def __init__(self):
      self.nodeColors = []
      self.timeStamp = None

class ModelNode(object):
   def __init__(self, center = None, color = None):
      self.center = center
      self.color = color

class NodeIdMode(Enum):
   OFF = 1
   MULTIPLE = 2
   WINDOW = 3

class ModelView(QLabel):
   def __init__(self, parent=None):
      super().__init__(parent)
      self.author = None
      self.backgroundColor = None
      self.bExport = False
      self.bHideOffNodes = False
      self.bMulticast = True
      self.bOutputLights = False
      self.bPlaying = False
      self.channelsPerNode = 3
      self.comment = None
      self.displayMargin = 15
      self.email = None
      self.exportFrames = []
      self.exportLength = None
      self.exportTimeRef = None
      self.fileName = None
      self.ipAddress = "192.168.1.50"
      self.mainWindow = None
      self.masterBrightness = 1.0
      self.nodeIdMode =  NodeIdMode.OFF
      self.modelName = None
      self.modelNodes = []
      self.modelPath = None
      self.moduleSequence = None
      self.nodeDiameter = 18
      self.nodeIdColor = QColor(0xFFFFFF)
      self.nodeMap = []
      self.nodeMapRanges = []
      self.playTimeRef = None
      self.playTimer = QTimer()
      self.playTimer.timeout.connect(self.playTimeout)
      self.rotation = 0.0
      self.rubberBand = QRubberBand(QRubberBand.Shape.Rectangle, self)
      self.sacnSender = None
      self.stretch = 1.0
      self.universe = {}

   def appSettings(self):
      dlg = AppSettingsDlg(self.displayMargin, self.nodeDiameter, self.bHideOffNodes,
         self.backgroundColor, self.offNodeColor, self.bMulticast, self.ipAddress, self)
      if dlg.exec()== QDialog.DialogCode.Accepted:
         self.nodeDiameter = dlg.nodeDiameter
         self.bHideOffNodes = dlg.bHideOffNodes
         self.backgroundColor = dlg.backgroundColor
         self.offNodeColor = dlg.offNodeColor
         bReconnectE131 = self.bOutputLights and \
            ((self.bMulticast != dlg.bMulticast) or (self.ipAddress != dlg.ipAddress))
         self.bMulticast = dlg.bMulticast
         self.ipAddress = dlg.ipAddress
         if bReconnectE131:
            self.connectE131()
            self.outputLights()
         if self.displayMargin != dlg.displayMargin:
            self.displayMargin = dlg.displayMargin
            self.createModel()
         self.writeAppSettings()

   def cancelExport(self):
      self.stop()
      self.bExport = False

   def connectE131(self):
      self.bOutputLights = True
      if self.sacnSender is not None:
         self.sacnSender.stop()  # return to default state
      self.sacnSender = sacn.sACNsender()
      self.sacnSender.start()
      for nUniverse in list(self.universe.keys()):
         self.sacnSender.activate_output(nUniverse)
         self.sacnSender[nUniverse].destination = self.ipAddress
         self.sacnSender[nUniverse].multicast = self.bMulticast

   def createModel(self):
      if self.modelPath is None:
         return
      self.modelNodes.clear()
      with open(self.modelPath) as f:
         lines = f.readlines()
         modelName = lines[2].split('"')
         for index, key in enumerate(modelName):
            if key.startswith("name="):
               self.modelName = modelName[index + 1]
               break
         customModel = lines[2].split()
         for key in customModel:
            if key.startswith("CustomModel="):
               nodeNumbers = re.findall(r'[^,;"\s]+', key)
               self.modelNodes = [ModelNode() for _ in range(len(nodeNumbers) - 1)]
               x = y = 0
               data = key[13:-1]
               modelLines = data.split(";")
               for modelLine in modelLines:
                  nodes = modelLine.split(",")
                  for node in nodes:
                     if node:
                        # center here is a tuple in .xmodel grid coordinates
                        self.modelNodes[int(node)-1].center = (x * self.stretch, y)
                     x += 1   
                  x = 0
                  y += 1
               break
         for node in self.modelNodes:
            node.center = (self.rotatePoint(node.center[0], node.center[1], self.rotation))
         xMin = min([node.center[0] for node in self.modelNodes])
         xMax = max([node.center[0] for node in self.modelNodes])
         yMin = min([node.center[1] for node in self.modelNodes])
         yMax = max([node.center[1] for node in self.modelNodes])
         deltaX = xMax - xMin
         deltaY = yMax - yMin
         size = self.size() # screen window size
         scaleX = (size.width() - self.displayMargin * 2 - self.nodeDiameter) / deltaX
         scaleY = (size.height() - self.displayMargin * 2 - self.nodeDiameter) / deltaY
         nodeRadius = int(self.nodeDiameter / 2.0)
         if scaleX > scaleY:
            imageWidth = int(deltaX * scaleY + self.nodeDiameter)
            offsetX = int(((size.width() - imageWidth) / 2) + nodeRadius)
            for node in self.modelNodes:
               x = int((node.center[0] - xMin) * scaleY + offsetX)
               y = int((node.center[1] - yMin) * scaleY + self.displayMargin + nodeRadius)
               # center here is in screen device units
               node.center = QPoint(x, y)
         else:
            imageHeight = int(deltaY * scaleX + self.nodeDiameter)
            offsetY = int(((size.height() - imageHeight) / 2) + nodeRadius)
            for node in self.modelNodes:
               x = int((node.center[0] - xMin) * scaleX + self.displayMargin + nodeRadius)
               y = int((node.center[1] - yMin) * scaleX + offsetY)
               # center here is in screen device units
               node.center = QPoint(x, y)

   def createNodeMap(self):
      self.nodeMap.clear()
      self.universe.clear()
      # create all universes used in all strings & initialize them to 0x00000 (off)
      for nodeMapRange in self.nodeMapRanges:
         startChannelAbs = nodeMapRange[0]
         endChannelAbs = nodeMapRange[1]
         startUniverse = startChannelAbs // 510 + 1
         endUniverse = endChannelAbs // 510 + 1
         for nUniverse in range(startUniverse, endUniverse + 1):
            if nUniverse not in self.universe:
               self.universe[nUniverse] = [ 0x000000 ] * 512
         # create nodeMap to map node to universe/channel
         for nChannel in range(startChannelAbs, endChannelAbs + 1, self.channelsPerNode):
            universe = nChannel // 510 + 1
            channel = nChannel % 510
            self.nodeMap.append((universe, channel))
      if self.bOutputLights: # activate appropriate outputs
         self.connectE131()

   def disconnectE131(self):
      self.bOutputLights = False
      self.sacnSender.stop()
      self.sacnSender = None

   def drawFrame(self, painter):
      painter.fillRect(self.rect(), QBrush(self.backgroundColor))
      painter.setRenderHint(QPainter.RenderHint.Antialiasing)
      painter.setPen(QPen(Qt.PenStyle.NoPen))
      painter.setBrush(self.offNodeColor)
      radius = int(self.nodeDiameter / 2)
      painter.setBrush(self.offNodeColor)
      blackColor = QColor(Qt.GlobalColor.black)
      if not self.bPlaying or not self.bHideOffNodes:
         for modelNode in self.modelNodes:
            if (modelNode.color is None) or (modelNode.color == blackColor):
               painter.drawEllipse(modelNode.center, radius, radius)
      for modelNode in self.modelNodes:
         if (modelNode.color is not None) and (modelNode.color != blackColor):
            painter.setBrush(modelNode.color)
            painter.drawEllipse(modelNode.center, radius, radius)

   def enableCommands(self):
      bOpen = (self.modelPath != None)
      self.mainWindow.ui.actionAppSettings.setEnabled(bOpen and not self.bPlaying)
      self.mainWindow.ui.actionExport.setEnabled(bOpen and not self.bPlaying)
      self.mainWindow.ui.actionFileSettings.setEnabled(bOpen and not self.bPlaying)
      self.mainWindow.ui.actionInteractiveColor.setEnabled(bOpen and not self.bPlaying)
      self.mainWindow.ui.actionNew.setEnabled(not self.bPlaying)
      self.mainWindow.ui.actionNodeIdMultiple.setEnabled(bOpen and not self.bPlaying)
      self.mainWindow.ui.actionNodeIdOff.setEnabled(bOpen and not self.bPlaying)
      self.mainWindow.ui.actionNodeIdWindow.setEnabled(bOpen and not self.bPlaying)
      self.mainWindow.ui.actionOpen.setEnabled(not self.bPlaying)
      self.mainWindow.ui.actionRun.setEnabled(bOpen and not self.bPlaying)
      self.mainWindow.ui.actionStop.setEnabled(self.bPlaying and not self.bExport)
      for action in self.mainWindow.mruActions:
         action.setEnabled(not self.bPlaying)

   def exit(self):
      if self.bPlaying:
         self.stop()
      if self.bOutputLights:
         self.disconnectE131() 

   def export(self):
      self.exportLength, ok = QInputDialog.getDouble(self, "Export Sequence Length",
         "Sequence length (seconds):", 30.00, 0.00, 3600.00, 3)
      if ok:
         self.bExport = True
         self.exportFrames.clear()
         self.exportTimeRef = time.perf_counter()
         dlg = ExportProgressDlg(self.exportLength, self)
         dlg.rejected.connect(self.cancelExport)
         dlg.show()
         self.run()

   def fileSettings(self):
      dlg = FileSettingsDlg(self.rotation, self.stretch, self.author, self.email, self.comment, \
         len(self.modelNodes), self.nodeMapRanges, self)
      if dlg.exec()== QDialog.DialogCode.Accepted:
         self.author = dlg.author
         self.email = dlg.email
         self.comment = dlg.comment
         if (abs(self.stretch - dlg.stretch) > .0001) or (abs(self.rotation - dlg.rotation) > .0001):
            self.rotation = dlg.rotation
            self.stretch = dlg.stretch
            self.createModel()
         if self.nodeMapRanges != dlg.ranges:   
            self.nodeMapRanges = dlg.ranges
            self.createNodeMap()
            if self.bOutputLights:
               self.connectE131()
         self.saveFile()

   def help(self):
      dlg = HelpDlg(self)
      dlg.exec()

   # returns the index of the modelNode that contains the point
   def hitTestPoint(self, point):
      for index, modelNode in enumerate(self.modelNodes):
         topLeft = QPoint(int(modelNode.center.x() - self.nodeDiameter / 2),
            int(modelNode.center.y() - self.nodeDiameter / 2))
         rectNode = QRect(topLeft, QSize(self.nodeDiameter, self.nodeDiameter))
         if rectNode.contains(point):
            return(index)
      return(None)

   # returns a list of indexes of the modelNodes completely enclosed in the rect
   def hitTestRect(self, rect):
      nodeIndex = []
      for index, modelNode in enumerate(self.modelNodes):
         topLeft = QPoint(int(modelNode.center.x() - self.nodeDiameter / 2),
            int(modelNode.center.y() - self.nodeDiameter / 2))
         rectNode = QRect(topLeft, QSize(self.nodeDiameter, self.nodeDiameter))
         if rect.contains(rectNode):
            nodeIndex.append(index)
      return(nodeIndex)

   def interactiveColor(self):
      self.nodeIdOff()
      self.masterBrightness = 1.0
      initialColor = QColor(0x7FFFFF)
      dlg = QColorDialog(initialColor, self)
      self.interactiveColorUpdate(initialColor)
      dlg.currentColorChanged.connect(self.interactiveColorUpdate)
      if dlg.exec() == QDialog.DialogCode.Accepted:
          color = dlg.selectedColor().name().upper().replace("#", "0x")
          QGuiApplication.clipboard().setText(color)
      self.interactiveColorUpdate(None)

   def interactiveColorUpdate(self, color):
      for node in self.modelNodes:
         node.color = color
      self.update()

   def moduleFromFile(self, moduleName, filePath):
      spec = importlib.util.spec_from_file_location(moduleName, filePath)
      module = importlib.util.module_from_spec(spec)
      spec.loader.exec_module(module)
      return(module)

   def mouseMoveEvent(self, event):
      if event.buttons() & Qt.MouseButton.LeftButton:
         if self.nodeIdMode == NodeIdMode.WINDOW:
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())
         elif self.nodeIdMode == NodeIdMode.MULTIPLE:
            nModelNode = self.hitTestPoint(event.pos())
            if nModelNode is not None:
               if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                  self.modelNodes[nModelNode].color = None
               else:
                  self.modelNodes[nModelNode].color = self.nodeIdColor
               self.updateNodeIdsStatus()
               self.update()

   def mousePressEvent(self, event):
      if event.button() == Qt.MouseButton.LeftButton:
         if self.nodeIdMode == NodeIdMode.WINDOW:
            self.origin = event.pos()
            self.rubberBand.setGeometry(QRect(self.origin, self.origin))
            self.rubberBand.show()
         elif self.nodeIdMode == NodeIdMode.MULTIPLE:
            nModelNode = self.hitTestPoint(event.pos())
            if nModelNode is not None:
               if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                  self.modelNodes[nModelNode].color = None
               else:
                  self.modelNodes[nModelNode].color = self.nodeIdColor
               self.updateNodeIdsStatus()
               self.update()

   def mouseReleaseEvent(self, event):
      if event.button() == Qt.MouseButton.LeftButton:
         if self.nodeIdMode == NodeIdMode.WINDOW:
            self.rubberBand.hide()
            selected_rect = self.rubberBand.geometry()
            nModelNodes = self.hitTestRect(selected_rect)
            if nModelNodes is not None:
               if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                  for index in nModelNodes:
                     self.modelNodes[index].color = None
               else:
                  for index in nModelNodes:
                     self.modelNodes[index].color = self.nodeIdColor
               self.updateNodeIdsStatus()
               self.update()

   def new(self):
      self.nodeIdOff()
      dlg = NewSequenceDlg(self)
      if dlg.exec()== QDialog.DialogCode.Accepted:
         self.fileName = dlg.fileName
         self.modelPath = dlg.modelPath
         self.createModel()
         self.nodeMapRanges = [ (1, len(self.modelNodes) * self.channelsPerNode)]
         self.createNodeMap()
         self.saveFile()
         self.mainWindow.setWindowTitle("xPyScript - " + self.fileName)
         self.mainWindow.addToMru(self.fileName)
         self.mainWindow.updateMruMenu()
         self.update()
         self.moduleSequence = None
         self.enableCommands()
         classFile = self.fileName.replace(".xscr", ".py")
         with open(classFile, 'w') as f:
            f.write("from SeqBase import SequenceBase\n\n")
            f.write("class Sequence(SequenceBase):\n")
            f.write("   def setup(self):\n")
            f.write("     # put your setup code here, to run once:\n")
            f.write("     pass\n\n")
            f.write("   def loop(self):\n")
            f.write("     # put your main code here, to run repeatedly:\n")
            f.write("     pass\n")

   def nodeIdMultiple(self):
      self.nodeIdMode = NodeIdMode.MULTIPLE

   def nodeIdOff(self):
      self.nodeIdMode = NodeIdMode.OFF
      self.mainWindow.ui.actionNodeIdOff.setChecked(True)
      for node in self.modelNodes:
         node.color = None
      self.update()

   def nodeIdWindow(self):
      self.nodeIdMode = NodeIdMode.WINDOW

   def open(self, fName = None):
      self.nodeIdOff()
      if not fName:
         self.fileName, ok = QFileDialog.getOpenFileName(self, 'Choose xPyScript file',
            '', 'xSexPyScriptuence file(*.xscr)') 
         if not ok:
            return
      else:
         self.fileName = fName
      file = QFile(self.fileName)
      file.open(QIODevice.OpenModeFlag.ReadOnly)
      self.nodeMapRanges.clear()
      xmlReader = QXmlStreamReader(file)
      if xmlReader.readNextStartElement():
         if xmlReader.name() == "xPyScript":
            while xmlReader.readNextStartElement():
               if xmlReader.name() == "head":
                  while xmlReader.readNextStartElement():
                     if xmlReader.name() == "version":
                        self.version = xmlReader.readElementText()
                     elif xmlReader.name() == "author":
                        self.author = xmlReader.readElementText()
                     elif xmlReader.name() == "email":
                        self.email = xmlReader.readElementText()
                     elif xmlReader.name() == "comment":
                        self.comment = xmlReader.readElementText()
                     elif xmlReader.name() == "model":
                        self.modelPath = xmlReader.readElementText()
                     elif xmlReader.name() == "rotation":
                        self.rotation = float(xmlReader.readElementText())
                     elif xmlReader.name() == "stretch":
                        self.stretch = float(xmlReader.readElementText())
                        self.createModel()
                     else:
                        xmlReader.skipCurrentElement()
               elif xmlReader.name() == "NodeMap":
                  while xmlReader.readNextStartElement():
                     if xmlReader.name() == "String":
                        nString = int(xmlReader.attributes().value("number"))
                        startChannel = int(xmlReader.attributes().value("startChannel"))
                        endChannel = int(xmlReader.attributes().value("endChannel"))
                        self.nodeMapRanges.append((startChannel, endChannel))
                        xmlReader.skipCurrentElement()
                     else:
                        xmlReader.skipCurrentElement()
               else:
                  xmlReader.skipCurrentElement()
      file.close()
      self.createNodeMap()
      self.mainWindow.setWindowTitle("xPyScript - " + self.fileName)
      self.mainWindow.addToMru(self.fileName)
      self.mainWindow.updateMruMenu()
      self.enableCommands()
      self.update()
      
   def outputLights(self):
      if self.bOutputLights:
         for nNode, node in enumerate(self.modelNodes):
            universe, channel = self.nodeMap[nNode]
            r, g, b, a = node.color.getRgb() if node.color != None else (0, 0, 0, 0)
            r = int(r * self.masterBrightness)
            g = int(g * self.masterBrightness)
            b = int(b * self.masterBrightness)
            self.universe[universe][channel - 1] = r
            self.universe[universe][channel] = g
            self.universe[universe][channel + 1] = b
         for nUniverse in list(self.universe.keys()):
            self.sacnSender[nUniverse].dmx_data = self.universe[nUniverse]

   def outputToLights(self):
      if self.mainWindow.ui.actionOutput.isChecked():
         self.connectE131()
         self.outputLights()
      else:
         self.disconnectE131()

   def paintEvent(self, event):
      super().paintEvent(event) 
      self.drawFrame(QPainter(self))
      self.outputLights()

   def playTimeout(self):
      elapsed = time.perf_counter() - self.playTimeRef
      text = f"Playing - {elapsed:.2f} seconds"
      self.mainWindow.statusBar().showMessage(text, 500)

   def readAppSettings(self):
      self.nodeDiameter = self.mainWindow.settings.value("NodeDiameter", 18)
      self.displayMargin = self.mainWindow.settings.value("DisplayMargin", 15)
      self.backgroundColor = self.mainWindow.settings.value("BackgroundColor",
         QColor(0x00, 0x00, 0x00))
      self.offNodeColor = self.mainWindow.settings.value("OffNodeColor",
         QColor(0x60, 0x60, 0x60))
      bHideOffNodes = self.mainWindow.settings.value("HideOffNodes", False)
      self.bHideOffNodes = True if bHideOffNodes == "true" else False
      bMulticast = self.mainWindow.settings.value("Multicast", True)
      self.bMulticast = False if bMulticast == "false" else True
      self.ipAddress = self.mainWindow.settings.value("IPAddress", "192.168.1.50")

   def resizeEvent(self, event):
      self.createModel()

   def rotatePoint(self, x, y, angleDegrees): # rotate point around (0, 0)
      angleRadians = math.radians(angleDegrees)
      xRot = x * math.cos(angleRadians) - y * math.sin(angleRadians)
      yRot = x * math.sin(angleRadians) + y * math.cos(angleRadians)
      return(xRot, yRot)

   def run(self):
      self.nodeIdOff()
      self.thread = QThread()
      sequenceName = pathlib.Path(self.fileName).stem
      filePath = self.fileName.replace(".xscr", ".py")
      try:
         if self.moduleSequence is not None:
            del(self.moduleSequence)
            self.moduleSequence = None
         self.moduleSequence = self.moduleFromFile(sequenceName, filePath)
      except Exception as e:
         QMessageBox.warning(self, "Error", f"Unable to run sequence!\n{e}")
         return
      self.worker = self.moduleSequence.Sequence(len(self.modelNodes))
      self.worker.moveToThread(self.thread)
      self.thread.started.connect(self.worker.run)
      self.worker.finished.connect(self.thread.quit)
      self.worker.finished.connect(self.worker.deleteLater)
      self.thread.finished.connect(self.thread.deleteLater)
      self.worker.showSignal.connect(self.show)
      self.worker.masterBrightnessSignal.connect(self.setMasterBrightness)
      self.worker.exceptionSignal.connect(self.workerException)
      self.masterBrightness = 1.0
      self.thread.start()
      self.bPlaying = True
      self.playTimeRef = time.perf_counter()
      self.playTimer.start(50)
      self.enableCommands()

   def saveFile(self):
      file = QFile(self.fileName)
      file.open(QIODevice.OpenModeFlag.WriteOnly)
      xmlWriter = QXmlStreamWriter(file)
      xmlWriter.setAutoFormatting(True)
      xmlWriter.setAutoFormattingIndent(2)
      xmlWriter.writeStartDocument()
      xmlWriter.writeStartElement("xPyScript")
      xmlWriter.writeStartElement("head")
      xmlWriter.writeTextElement("version", version)
      xmlWriter.writeTextElement("author", self.author)
      xmlWriter.writeTextElement("email", self.email)
      xmlWriter.writeTextElement("comment", self.comment)
      xmlWriter.writeTextElement("model", self.modelPath)
      xmlWriter.writeTextElement("rotation", f"{self.rotation:0.2f}")
      xmlWriter.writeTextElement("stretch", f"{self.stretch:0.4f}")
      xmlWriter.writeEndElement()  # End head element
      xmlWriter.writeStartElement("NodeMap")
      for nMapRange, mapRange in enumerate(self.nodeMapRanges):
         xmlWriter.writeStartElement("String")
         xmlWriter.writeAttribute("number", str(nMapRange + 1))
         xmlWriter.writeAttribute("startChannel", str(mapRange[0]))
         xmlWriter.writeAttribute("endChannel", str(mapRange[1]))
         xmlWriter.writeEndElement()  # End Port element
      xmlWriter.writeEndElement()  # End NodeMap element
      xmlWriter.writeEndElement()  # End xPyScript element
      xmlWriter.writeEndDocument()
      file.close()

   def setMasterBrightness(self, brightness):
      self.masterBrightness = min(1.0, max(0, brightness))

   def show(self, nodeColors):
      for nNode in range(len(nodeColors)):
         self.modelNodes[nNode].color = nodeColors[nNode]
      if self.bExport:
         timeStamp = time.perf_counter()
         if (timeStamp - self.exportTimeRef) > self.exportLength:
            self.bExport = False
            self.stop()
            self.writeExport()
         else:
            exportFrame = ExportFrame()
            exportFrame.timeStamp = timeStamp
            exportFrame.nodeColors = nodeColors
            self.exportFrames.append(exportFrame)
      self.update()

   def stop(self):
      self.thread.requestInterruption()
      self.thread.quit()
      self.thread.wait()
      self.bPlaying = False
      self.playTimer.stop()
      self.enableCommands()

   def updateNodeIdsStatus(self):
      selectedChannels = [ index + 1 for index, node in enumerate(self.modelNodes) \
         if node.color != None ]
      selectedChannels.sort()
      selectedChannelsText = ",".join(map(str, selectedChannels))
      statusbarWidth = self.mainWindow.statusBar().width()
      labelWidth = self.mainWindow.versionLabel.width() 
      availableWidth = statusbarWidth - labelWidth - 30 # Approx. width of grip area is 30
      metrics = QFontMetrics(self.mainWindow.statusBar().font())
      elidedText = metrics.elidedText(selectedChannelsText,
         Qt.TextElideMode.ElideRight, availableWidth)
      self.mainWindow.statusBar().showMessage(elidedText)
      QGuiApplication.clipboard().setText(selectedChannelsText)

   def workerException(self, exceptionMsg):
      self.stop()
      QMessageBox.warning(self, "Error in sequence", exceptionMsg)

   def writeAppSettings(self):
      self.mainWindow.settings.setValue("NodeDiameter", self.nodeDiameter)
      self.mainWindow.settings.setValue("DisplayMargin", self.displayMargin)
      self.mainWindow.settings.setValue("HideOffNodes", self.bHideOffNodes)
      self.mainWindow.settings.setValue("BackgroundColor", self.backgroundColor)
      self.mainWindow.settings.setValue("OffNodeColor", self.offNodeColor)
      self.mainWindow.settings.setValue("Multicast", self.bMulticast)
      self.mainWindow.settings.setValue("IPAddress", self.ipAddress)

   def writeExport(self):
      # create list to hold modelNodes effects - frameEffects[0] corresponds to modelNodes[0]
      frameEffects = [[] for _ in range(len(self.modelNodes))]
      effectColors = [] # list of rgb QColors used in all effects
      nLastFrame = len(self.exportFrames) - 1
      for nFrame, frame in enumerate(self.exportFrames):
         startTime = (int)((frame.timeStamp - self.exportTimeRef) * 1000) if nFrame > 0 else 0
         endTime = (int)((self.exportLength if nFrame == nLastFrame else \
            (self.exportFrames[nFrame + 1].timeStamp - self.exportTimeRef)) * 1000)
         for nNode, nodeColor in enumerate(frame.nodeColors):
            if (nodeColor is not None) and (nodeColor != QColor(0x000000)):
               frameEffects[nNode].append(Effect(nodeColor, startTime, endTime))
               if nodeColor not in effectColors:
                  effectColors.append(nodeColor)

      # combine node frameEffects across frames where possible
      effects = [[] for _ in range(len(self.modelNodes))]
      for nNode, nodeEffects in enumerate(frameEffects):
         if len(nodeEffects) > 0:
            currentEffect = None
            for nodeEffect in nodeEffects:
               if currentEffect is None:
                  currentEffect = Effect(nodeEffect.color, nodeEffect.startTime, \
                     nodeEffect.endTime)
               elif currentEffect.color != nodeEffect.color or \
                  currentEffect.endTime != nodeEffect.startTime:
                  effects[nNode].append(currentEffect)
                  currentEffect = Effect(nodeEffect.color, nodeEffect.startTime,
                     nodeEffect.endTime)
               else:
                  currentEffect.endTime = nodeEffect.endTime
            effects[nNode].append(currentEffect)

      file = QFile(self.fileName[:-4] + "xsq")
      file.open(QIODevice.OpenModeFlag.WriteOnly)
      xmlWriter = QXmlStreamWriter(file)
      xmlWriter.setAutoFormatting(True)
      xmlWriter.setAutoFormattingIndent(2)
      xmlWriter.writeStartDocument()
      xmlWriter.writeStartElement("xsequence")
      xmlWriter.writeAttribute("FixedPointTiming", "1")
      xmlWriter.writeStartElement("head")
      xmlWriter.writeTextElement("version", "2025.04")
      xmlWriter.writeTextElement("author", self.author)
      xmlWriter.writeTextElement("author-email", self.email)
      xmlWriter.writeTextElement("comment", self.comment)
      xmlWriter.writeTextElement("sequenceTiming", "25 ms")
      xmlWriter.writeTextElement("sequenceType", "Animation")
      xmlWriter.writeTextElement("sequenceDuration", f"{self.exportLength:.3f}")
      xmlWriter.writeEndElement()  # End head element

      stdXLightPalette = [QColor(0xFFFFFF), QColor(0xFF0000), QColor(0x00FF00),
         QColor(0x0000FF), QColor(0xFFFF00), QColor(0x000000), QColor(0x00FFFF),
         QColor(0xFF00FF)]
      xmlWriter.writeStartElement("ColorPalettes")
      for color in effectColors:
         if color in stdXLightPalette:
            nCheckBox = stdXLightPalette.index(color) + 1
            element = (f"C_BUTTON_Palette1=#FFFFFF,C_BUTTON_Palette2=#FF0000,"
               f"C_BUTTON_Palette3=#00FF00,C_BUTTON_Palette4=#0000FF,"
               f"C_BUTTON_Palette5=#FFFF00,C_BUTTON_Palette6=#000000,"
               f"C_BUTTON_Palette7=#00FFFF,C_BUTTON_Palette8=#FF00FF,"
               f"C_CHECKBOX_Palette{nCheckBox}=1")
         else:
            element = (f"C_BUTTON_Palette1={color.name().upper()},C_CHECKBOX_Palette1=1")
         xmlWriter.writeTextElement("ColorPalette", element)
      xmlWriter.writeEndElement()  # End ColorPalettes element

      xmlWriter.writeStartElement("DisplayElements")
      xmlWriter.writeStartElement("Element")
      xmlWriter.writeAttribute("type", "timing")
      xmlWriter.writeAttribute("name", "25ms")
      xmlWriter.writeAttribute("visible", "1")
      xmlWriter.writeAttribute("active", "1")
      xmlWriter.writeEndElement()  # End Element element
      xmlWriter.writeStartElement("Element")
      xmlWriter.writeAttribute("type", "model")
      xmlWriter.writeAttribute("name", self.modelName)
      xmlWriter.writeAttribute("visible", "1")
      xmlWriter.writeEndElement()  # End Element element
      xmlWriter.writeEndElement()  # End DisplayElements element
      xmlWriter.writeStartElement("ElementEffects")
      xmlWriter.writeStartElement("Element")
      xmlWriter.writeAttribute("type", "timing")
      xmlWriter.writeAttribute("name", "25ms")
      xmlWriter.writeAttribute("fixed", "25")
      xmlWriter.writeEndElement()  # End Element element
      xmlWriter.writeStartElement("Element")
      xmlWriter.writeAttribute("type", "model")
      xmlWriter.writeAttribute("name", self.modelName)
      xmlWriter.writeStartElement("Strand")
      xmlWriter.writeAttribute("index", "0")

      for nNode, node in enumerate(self.modelNodes):
         if len(effects[nNode]) > 0:
            xmlWriter.writeStartElement("Node")
            xmlWriter.writeAttribute("index", str(nNode))
            xmlWriter.writeAttribute("name", f"Node {nNode + 1}")
            for effect in effects[nNode]:
               xmlWriter.writeStartElement("Effect")
               xmlWriter.writeAttribute("name", "On")
               xmlWriter.writeAttribute("startTime", str(effect.startTime))
               xmlWriter.writeAttribute("endTime", str(effect.endTime))
               xmlWriter.writeAttribute("palette", str(effectColors.index(effect.color)))
               xmlWriter.writeEndElement()  # End Effect element
            xmlWriter.writeEndElement()  # End Node element

      xmlWriter.writeEndElement()  # End Strand element
      xmlWriter.writeEndElement()  # End Element element
      xmlWriter.writeEndElement()  # End ElementEffects element
      xmlWriter.writeEndElement()  # End xsequence element
      xmlWriter.writeEndDocument()
      file.close()