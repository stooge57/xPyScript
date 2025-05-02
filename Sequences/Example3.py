from SeqBase import SequenceBase
from enum import Enum
from PyQt6.QtGui import QColor

class Direction(Enum):
   UP = 1
   DOWN = 2

class SparkleNode(object):
   def __init__(self, nNode):
      self.nNode = nNode
      self.nodeDirection = Direction.UP

class Sequence(SequenceBase):
   def setup(self):
      self.percentage = 20
      self.incrementValue = 8
      self.rangeLow = 20
      self.rangeHigh = 100
      self.sparkleNodes = []
      self.sparkleColor = 0xFFFFFF
      self.setRgbAll(0x0000FF)

   def loop(self):
      for nSparkleNode, sparkleNode in enumerate(self.sparkleNodes):
         nNode = sparkleNode.nNode
         hue, saturation, value, _ = self.nodeColors[nNode].getHsv()     
         if sparkleNode.nodeDirection == Direction.UP:   # brighten
            if self.rangeHigh - value > self.incrementValue:
               value += self.incrementValue
            else:
               value = self.rangeHigh
               sparkleNode.nodeDirection = Direction.DOWN
            self.nodeColors[nNode] = QColor.fromHsv(hue, saturation, value)
         else:  # darken
            if value - self.rangeLow > self.incrementValue:
               value -= self.incrementValue
               self.nodeColors[nNode] = QColor.fromHsv(hue, saturation, value)
            else: # turn off sparkle
               del self.sparkleNodes[nSparkleNode]
               self.nodeColors[nNode] = QColor(0x0000FF)

      percentage = int((len(self.sparkleNodes) / self.nNodes) * 100)
      if (percentage < self.percentage):
         i = self.random(self.nNodes)
         self.sparkleNodes.append(SparkleNode(i))
         self.nodeColors[i] = QColor(self.sparkleColor)
         hue, saturation, _, _ = self.nodeColors[i].getHsv()     
         self.nodeColors[i] = QColor.fromHsv(hue, saturation, self.incrementValue)

      self.show()
      self.delay(30)