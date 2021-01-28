from speimage import SpeImage
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.widgets import Button as mpButton
import matplotlib.image as mpimg
from matplotlib import cm
from skimage.draw import polygon, polygon2mask
from skimage import color, util
from skimage import filters
from WinSpecFrame import WinSpecFrame
from tkinter import *
from tkinter import filedialog, ttk
from os import path
from math import sqrt, ceil, floor
from mpl_toolkits.axes_grid1 import ImageGrid

class spematplot():
  def redraw_threshold(self):
    self.ax_xgraph.clear()
    self.ax_xgraph.set_ylim([self.wsf.min_val(), self.wsf.max_val()])
    self.ax_xgraph.plot(self.wsf.xgraph())
    self.ax_xgraph.axhline(y=self.wsf.threshold, linestyle = '-', linewidth=2, color='firebrick')
  
  def redraw_xpixel(self):
    self.ax_xpixel.clear()
    self.ax_xpixel.set_title("Frame #"+str(self.image.frame_i))
    self.ax_xpixel.imshow(self.wsf.image_raw(), cmap=self.cmap, origin='lower')
    self.ax_xpixel.axhline(y=self.wsf.x_co, linestyle = '-', linewidth=2, color='firebrick')
  
  def redraw_mod(self):
    self.ax_mod.clear()
    sm = cm.ScalarMappable(cmap=self.cmap)
    img = sm.to_rgba(self.wsf.image_raw_mod())
    self.ax_mod.imshow(img, origin='lower')
    # ax_mod.imshow(wsf.image_raw(), cmap='jet', clim=(wsf.threshold, wsf.max_val()), origin='lower')

  def redraw_frame(self):
      self.wsf = self.image.get_frame()
      self.redraw_xpixel()
      self.redraw_threshold()
      self.redraw_mod()

  def frame_next(self, event):
    if self.image.frame_i < self.image.header.NumFrames-1:
      print("Updating to next frame",)
      self.image.frame_i += 1
      self.redraw_frame()
    else:
      print("Last frame already selected")

  def frame_prev(self, event):
    if self.image.frame_i > 0:
      print("Updating to prev frame",)
      self.image.frame_i -= 1
      self.redraw_frame()
    else:
      print("First frame already selected")

  def update_xpixel(self, val):
    print("Updating xpixel to ", val)
    self.wsf.x_co = val
    self.redraw_xpixel()
    self.redraw_threshold()

  def update_threshold(self, val):
    print("Updating threshold to ", val)
    self.wsf.threshold = val
    self.redraw_threshold()
    self.redraw_mod()

  def update_mask(self):
    print("Updating map to ")
    self.wsf.mask_poly = np.array((
      (100,100),
      (200,100),
      (200,200),
    ))
    self.redraw_mod()

  def show(self):
    plt.show()

  def __init__(self, image, cmap):
    self.cmap = cmap
    self.image = image
    self.wsf = self.image.get_frame()

    # create initial plot
    self.fig, (self.ax_xpixel, self.ax_xgraph, self.ax_mod) = plt.subplots(1, 3)
    self.axprev = plt.axes([0.7, 0.05, 0.1, 0.075])
    self.axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
    self.fig.tight_layout(h_pad=2)

    # plot slider
    self.bnext = mpButton(self.axnext, 'Next')
    self.bprev = mpButton(self.axprev, 'Previous')
    self.spixel = Slider(self.ax_xpixel, "x pixel", 0, self.wsf.width()-1, valinit=self.wsf.x_co, valstep=1, orientation='vertical')
    self.threshold = Slider(self.ax_xgraph, "threshold", ceil(self.wsf.min_val()), floor(self.wsf.max_val()), valinit=self.wsf.threshold, valstep=1, orientation='vertical')

    # temporary
    # update_mask()

    self.redraw_mod()
    self.redraw_threshold()
    self.redraw_xpixel()
    
    self.bnext.on_clicked(self.frame_next)
    self.bprev.on_clicked(self.frame_prev)
    self.spixel.on_changed(self.update_xpixel)
    self.threshold.on_changed(self.update_threshold)

    # plt.show()
