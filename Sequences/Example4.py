from SeqBase import SequenceBase
from enum import Enum
from PyQt6.QtGui import QColor

class Direction(Enum):
   UP = 1
   DOWN = 2

class Sequence(SequenceBase):
   def setup(self):
      self.percentage = 80
      self.incrementValue = 8
      self.rangeLow = 20
      self.rangeHigh = 180
      self.nodeDirection = [Direction.UP] * self.nNodes
      self.setRgbAll(0x000000)
      # self.palette = [ 0xFF0000, 0x00FF00, 0x0000FF, 0xFFFFFF, 0xFF00FF, 0xFFFF00, 0x00FFFF ]
      self.palette = [ 0xFF0000, 0x00FF00 ]

   def loop(self):
      for nNode, nodeColor in enumerate(self.nodeColors):
         hue, saturation, value, _ = nodeColor.getHsv()     
         if value == 0:
            continue  # skip off pixels
         elif self.nodeDirection[nNode] == Direction.UP:   # brighten
            if self.rangeHigh - value > self.incrementValue:
               value += self.incrementValue
            else:
               value = self.rangeHigh
               self.nodeDirection[nNode] = Direction.DOWN
            self.nodeColors[nNode] = QColor.fromHsv(hue, saturation, value)
         else:  # darken
            if value - self.rangeLow > self.incrementValue:
               value -= self.incrementValue
            else:
               value = 0  # turn off
            self.nodeColors[nNode] = QColor.fromHsv(hue, saturation, value)

      # Randomly choose an off pixel and 'bump' it up a little.
      # It will start getting brighter over time.
      offNodes = [nNode for nNode, nodeColor in enumerate(self.nodeColors) if nodeColor.value() == 0]
      percentage = int(((self.nNodes - len(offNodes)) / self.nNodes) * 100)
      if (percentage < self.percentage) and offNodes:
         i = self.choice(offNodes)
         self.nodeColors[i] = QColor(self.choice(self.palette))
         hue, saturation, _, _ = self.nodeColors[i].getHsv()     
         self.nodeColors[i] = QColor.fromHsv(hue, saturation, self.incrementValue)
         self.nodeDirection[i] = Direction.UP

      self.show()
      self.delay(50)