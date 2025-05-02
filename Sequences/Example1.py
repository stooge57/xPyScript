from SeqBase import SequenceBase

class Sequence(SequenceBase):
   def setup(self):
      self.rows = [ [ 20, 21, 27, 28 ], [ 18, 19, 26, 29 ], [ 22, 30 ], [ 17, 25 ], \
         [ 23, 24, 31 ], [ 13, 16, 32, 35 ], [ 9, 10, 12, 14, 15, 33, 34, 36, 38, 39 ], \
         [ 8, 11, 37, 40 ], [ 7, 47, 48 ], [ 6, 41 ], [ 5, 46 ], [ 3, 4, 42, 43 ], \
         [ 1, 2, 44, 45 ] ]
      self.columns = [ [ 12 ], [ 10, 11, 13 ], [ 4, 14, 19 ], [ 2, 9, 20 ], \
         [ 3, 18 ], [ 5, 15, 22 ], [ 1, 6, 8, 16, 17, 21 ], [ 7, 23 ], [ 24, 48 ], \
         [ 31, 47 ], [ 25, 27, 32, 40, 41, 45 ], [ 30, 39, 46 ], [ 26, 42 ], \
         [ 28, 33, 44 ], [ 29, 38, 43 ], [ 34, 35, 37 ], [ 36 ] ]
      self.branches = [ [ 17, 18, 19, 20, 21, 22, 23 ], [ 25, 26, 27, 28, 29, 30, 31 ], \
         [ 33, 34, 35, 36, 37, 38, 39 ], [ 41, 42, 43, 44, 45, 46, 47 ], \
         [ 1, 2, 3, 4, 5, 6, 7 ], [ 9, 10, 11, 12, 13, 14, 15 ] ]
      self.rings = [ [ 7, 8, 15, 16, 23, 24, 31, 32, 39, 40, 47, 48 ], \
         [ 6, 9, 17, 25, 33, 41 ], [ 5, 14, 22, 30, 38, 46 ], [ 3, 10, 18, 26, 34, 42 ], \
         [ 1, 2, 4, 11, 12, 13, 19, 20, 21, 27, 28, 29, 35, 36, 37, 43, 44, 45 ] ]
      self.delayMs = 250
      
      self.colors = [ 0xFF0000, 0x00FF00, 0x0000FF, 0xFF00FF, 0x00FFFF, 0xFFFF00 ]
#      self.colors = [ 0xFF0000, 0x00FF00 ]
#      self.colors = [ 0x0000FF, 0xFFFFFF ]
#      self.colors = [ 0xFF0000, 0xFFFFFF, 0x0000FF ]

      self.nBarHeight = 1
      self.pattern = [color for color in self.colors for _ in range(self.nBarHeight)]
      self.nIndex = 0
      self.setMasterBrightness(1)

   def loop(self):
      if self.doEveryMillis(1, self.delayMs):
         for nRing in range(len(self.rings)):
            self.setRgb(self.rings[nRing], self.pattern[(self.nIndex + nRing) % len(self.pattern)])
         self.show()
         self.nIndex = self.nIndex + 1
         if self.nIndex >= len(self.pattern):
            self.nIndex = 0
            self.nBarHeight = self.randomRange(1, 3)
            self.pattern = [color for color in self.colors for _ in range(self.nBarHeight)]