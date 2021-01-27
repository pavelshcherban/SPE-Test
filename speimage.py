from pyWinSpec.winspec import SpeFile
from WinSpecFrame import WinSpecFrame

class SpeImage(SpeFile):
  @property
  def frame_i(self):
    return self._frame_i

  @frame_i.setter
  def frame_i(self, i):
    if i>=0 and i<=self.header.NumFrames:
      self._frame_i = i
      self.__frame = WinSpecFrame(self.data[i], self.header.exp_sec)
    else:
      print("frame index out of bounds")

  def get_frame(self):
    return self.__frame

  def __init__(self, filename):
    super().__init__(filename)
    self.frame_i = 0