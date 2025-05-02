# This file is under MIT license. The license file can be obtained in the root directory of this module.

from PyQt6.QtCore import pyqtSignal, QObject, QThread, QTime
from PyQt6.QtGui import QColor
import colorsys, random, time, traceback

class ThreadBreak(Exception):
    pass

class SequenceBase(QObject):
   exceptionSignal = pyqtSignal(str)
   finished = pyqtSignal()
   masterBrightnessSignal = pyqtSignal(float)
   showSignal = pyqtSignal(list)

   def __init__(self, nNodes):
      super().__init__()
      self.nNodes = nNodes
      self.doEveryTimeRef = {}
      self.nodeColors = [ None ] * nNodes

   def choice(self, myList):
      return(random.choice(myList))

   def clear(self, nNodeNumbers):
      if type(nNodeNumbers) is int:
         self.nodeColors[nNodeNumbers - 1] = None
      else: # list of nodeNumbers
         for nNodeNumber in nNodeNumbers:
            self.nodeColors[nNodeNumber - 1] = None

   def clearAll(self):
      for index in range(len(self.nodeColors)):
         self.nodeColors[index] = None

   def delay(self, ms):
      return(time.sleep(ms / 1000.0))

   def doEveryMillis(self, idKey, period):
      currentTime = QTime.currentTime()
      if idKey not in self.doEveryTimeRef:
         self.doEveryTimeRef[idKey] = currentTime
      else:
         deltaMillis = self.doEveryTimeRef[idKey].msecsTo(currentTime)
         if deltaMillis >= period:
            self.doEveryTimeRef[idKey] = currentTime
            return(True)
      return(False)

   def doEverySeconds(self, idKey, period):
      currentTime = QTime.currentTime()
      if idKey not in self.doEveryTimeRef:
         self.doEveryTimeRef[idKey] = currentTime
      else:
         deltaSeconds = self.doEveryTimeRef[idKey].msecsTo(currentTime) / 1000.0
         if deltaSeconds >= period:
            self.doEveryTimeRef[idKey] = currentTime
            return(True)
      return(False)
  
   def random(self, max):
      return(random.randint(0, max-1))

   def randomRange(self, min, max):
      return(random.randint(min, max-1))
   
   def run(self):
      try:
         self.setup()
         while True:
            self.loop()
            if QThread.currentThread().isInterruptionRequested():
               break
            time.sleep(.001) # limit thread's CPU usage
      except ThreadBreak as e:
         pass
      except Exception as e:
         tb = traceback.extract_tb(e.__traceback__)
         filename, lineno, _, text = tb[-1]
         if filename.find("SeqBase.py") != -1:
            filename, lineno, _, text = tb[-2]
         exceptionMsg = f"{e.args[0]}\n\n{filename}, line {lineno}\n{text}"
         self.exceptionSignal.emit(exceptionMsg)
      # clear screen/model and exit
      self.clearAll()
      self.showSignal.emit(self.nodeColors.copy())
      self.finished.emit()

   def setHsv(self, nNodeNumbers, hue, saturation, value):
      color = QColor.fromHsv(hue, saturation, value)
      if type(nNodeNumbers) is int:
         self.nodeColors[nNodeNumbers - 1] = color
      else: # list of nodeNumbers
         for nNodeNumber in nNodeNumbers:
            self.nodeColors[nNodeNumber - 1] = color

   def setHsvAll(self, hue, saturation, value):
      color = QColor.fromHsv(hue, saturation, value)
      for index in range(len(self.nodeColors)):
         self.nodeColors[index] = color

   def setMasterBrightness(self, scale):
      self.masterBrightnessSignal.emit(scale)

   def setRgb(self, nNodeNumbers, rgb):
      color = QColor(rgb)
      if type(nNodeNumbers) is int:
         self.nodeColors[nNodeNumbers - 1] = color
      else: # list of nodeNumbers
         for nNodeNumber in nNodeNumbers:
            self.nodeColors[nNodeNumber - 1] = color

   def setRgbAll(self, rgb):
      color = QColor(rgb)
      for index in range(len(self.nodeColors)):
         self.nodeColors[index] = color

   def setRgb3(self, nNodeNumbers, red, green, blue):
      color = QColor(red, green, blue)
      if type(nNodeNumbers) is int:
         self.nodeColors[nNodeNumbers - 1] = color
      else: # list of nodeNumbers
         for nNodeNumber in nNodeNumbers:
            self.nodeColors[nNodeNumber - 1] = color

   def setRgb3All(self, red, green, blue):
      color = QColor(red, green, blue)
      for index in range(len(self.nodeColors)):
         self.nodeColors[index] = color

   def show(self):
      self.showSignal.emit(self.nodeColors.copy())
      if QThread.currentThread().isInterruptionRequested():
         raise(ThreadBreak("Sequence thread interrupted"))
