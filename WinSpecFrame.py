import numpy as np
from skimage import color, util, exposure
from skimage.draw import polygon2mask
from scipy import ndimage
from math import ceil

class WinSpecFrame:
  def __init__(self, image, exp_sec):
    # private properties
    self.__width, self.__height = image.shape
    self.__exposure = exp_sec
    # is this median filtering useful?
    self.__image_raw = ndimage.median_filter(image, size=3)/exp_sec
    # self.__image_raw_mod
  
    #protected properties
    self._x_co = 50
    self._threshold = ceil(self.min_val())
    self._mask_poly = np.array((
      (0,0),
      (0, self.__height-1),
      (self.__width-1, self.__height-1),
      (self.__width-1, 0)
    ))

    self.update_mod()

  @property
  def x_co(self):
    return self._x_co

  @x_co.setter  
  def x_co(self, new_x):
    if new_x >= 0 and new_x <= self.__width-1:
      self._x_co = new_x
    else:
      raise Exception("value not within image width")
  
  @property
  def threshold(self):
    return self._threshold

  @threshold.setter
  def threshold(self, new_t):
    if new_t >= self.min_val() and new_t <= self.max_val():
      self._threshold = new_t
      self.update_mod()
    else:
      raise Exception("value not within max and min intensity")

  @property
  def mask_poly(self):
    return self._mask_poly

  @mask_poly.setter
  def mask_poly(self, poly):
    self._mask_poly = poly
    self.update_mod()

  def __str__(self):
    return self.__image_raw

  def update_mod(self):
    imod = self.__image_raw.copy()
    # apply threshold
    imod[imod < self._threshold] = self.min_val()
    # apply mask
    mask = polygon2mask(imod.shape, self._mask_poly)
    imod = imod * mask
    self.__image_raw_mod = imod * mask

  def xgraph(self):
    return self.__image_raw[self._x_co]

  def min_val(self):
    return np.amin(self.__image_raw)
    
  def max_val(self):
    return np.amax(self.__image_raw)
    
  def width(self):
    return self.__width
    
  def height(self):
    return self.__height

  def image_raw(self):
    return self.__image_raw

  def image_raw_mod(self):
    return self.__image_raw_mod