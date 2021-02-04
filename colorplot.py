import tkinter as tk
from math import ceil, sqrt

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import ImageGrid
from scipy import ndimage


class colorplot():
  def onclick(self, event):
    """Registers the selection of a colormap plot"""
    if event.inaxes:
      cmap = event.inaxes.get_title()
      # print('inaxes=%s' %(cmap))
      self.file['cmap'].set(cmap)

  def __init__(self, file, window, cmaps, cmap_category):
    self.file = file
    self.frame = np.fliplr(ndimage.median_filter(self.file['img'].data[self.file['frame_i']], size=3)/self.file['img'].header.exp_sec)
    nrows = ceil(sqrt(len(cmaps)))

    self.fig = Figure()
    self.canvas = FigureCanvasTkAgg(self.fig, master=window['toplevel'])
    self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    self.toolbar = NavigationToolbar2Tk(self.canvas, window['toplevel'])
    self.toolbar.update()
    self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    self.grid = ImageGrid(self.fig, 111, nrows_ncols=(nrows, nrows), axes_pad=(0.1,0.3))
    self.fig.suptitle(cmap_category + ' colormaps')

    for ax, name in zip(self.grid, cmaps):
        ax.imshow(self.frame, cmap=plt.get_cmap(name), origin='lower')
        ax.set_title(name, fontsize=10)
        ax.set_axis_off()

    # # temporary
    # # update_mask()

    self.canvas.mpl_connect('button_press_event', lambda event:self.canvas._tkcanvas.focus_set())
    self.canvas.mpl_connect("button_press_event", self.onclick)
    
    self.canvas.draw_idle()
    self.canvas.flush_events()
