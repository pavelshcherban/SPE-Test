import tkinter as tk
from math import ceil, floor

import numpy as np
from matplotlib import cm
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure
from matplotlib.widgets import Button as mpButton
from matplotlib.widgets import Slider
from scipy import ndimage


class spematplot():
  def update_frame_next(self, event):
    """Updates the frame selection for the file to the next frame."""
    if self.file['frame_i'] < self.file['img'].header.NumFrames-1:
      print("Updating to next frame", self.file['frame_i']+1)
      self.file['frame_i'] += 1
      self.redraw_frame()
    else:
      print("Last frame already selected")

  def update_frame_prev(self, event):
    """Updates the frame selection for the file to the previous frame."""
    if self.file['frame_i'] > 0:
      print("Updating to prev frame", self.file['frame_i']-1)
      self.file['frame_i'] -= 1
      self.redraw_frame()
    else:
      print("First frame already selected")

  def draw_figure(self):
    """Draws the Figure on the tk canvas."""
    self.canvas.draw_idle()
    self.canvas.flush_events()

  def redraw_threshold(self):
    # print("redraw_threshold")
    self.ax_xgraph.clear()
    self.ax_xgraph.set_ylim([np.amin(self.frame), np.amax(self.frame)])
    self.ax_xgraph.plot(self.frame[self.file['x_i']])
    self.ax_xgraph.axhline(y=self.file['threshold'].get(), linestyle = '-', linewidth=2, color='firebrick')
    # print("redraw_threshold")
  
  def redraw_orig(self):
    # print("redraw_frame")
    self.ax_orig.clear()
    self.ax_orig.set_title("Frame #"+str(self.file['frame_i']))
    self.ax_orig.imshow(self.frame, cmap=self.file['cmap'].get(), origin='lower')
    self.ax_orig.axhline(y=self.file['x_i'], linestyle = '-', linewidth=2, color='firebrick')
    # print("redraw_frame")
  
  def redraw_mod(self):
    # print("redraw_mod")
    self.ax_mod.clear()
    sm = cm.ScalarMappable(cmap=self.file['cmap'].get())
    img = sm.to_rgba(self.frame)
    self.ax_mod.imshow(img, origin='lower')
    # ax_mod.imshow(wsf.image_raw(), cmap='jet', clim=(wsf.threshold, wsf.max_val()), origin='lower')
    # print("redraw_mod")

  def redraw_frame(self):
    # print("redraw_frame")
    self.frame = np.fliplr(ndimage.median_filter(self.file['img'].data[self.file['frame_i']], size=3)/self.file['img'].header.exp_sec)
    self.redraw_orig()
    self.redraw_threshold()
    self.redraw_mod()
    self.draw_figure()

  def update_orig(self, val):
    print("Updating x_i to ", val)
    self.file['x_i'] = val
    self.redraw_orig()
    self.redraw_threshold()

  def update_threshold(self, val):
    print("Updating threshold to ", val)
    self.file['threshold'].set(val)
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

  # def show(self):
  #   self.fig.show()

  def on_key_press(self, event):
    if event.inaxes:
      print(event.inaxes.get_title())
    # key_press_handler(event, canvas, toolbar)

  def __init__(self, file, window):
    self.file = file
    self.frame = np.fliplr(ndimage.median_filter(self.file['img'].data[self.file['frame_i']], size=3)/self.file['img'].header.exp_sec)
    self.iwidth, self.iheight = self.frame.shape

    self.fig = Figure()
    self.canvas = FigureCanvasTkAgg(self.fig, master=window['toplevel'])
    self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    self.toolbar = NavigationToolbar2Tk(self.canvas, window['toplevel'])
    self.toolbar.update()
    self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # create initial plot
    (self.ax_orig, self.ax_xgraph, self.ax_mod) = self.fig.subplots(1,3)
    self.ax_xgraph.set_title("Strength at x=" + str(file['x_i']))
    self.ax_mod.set_title("Modified Image")
    self.ax_pframe = self.fig.add_axes([0.7, 0.05, 0.1, 0.075])
    self.ax_nframe = self.fig.add_axes([0.81, 0.05, 0.1, 0.075])
    # self.fig.tight_layout(h_pad=2)

    # plot slider
    self.b_nframe = mpButton(self.ax_nframe, 'Next Frame')
    self.b_pframe = mpButton(self.ax_pframe, 'Previous Frame')
    self.x_i = Slider(self.ax_orig, "Original Image - Frame" + str(file['frame_i']), 0, self.iwidth-1, valinit=file['x_i'], valstep=1, orientation='vertical')
    self.threshold = Slider(self.ax_xgraph, "threshold", ceil(np.amin(self.frame)), floor(np.amax(self.frame)), valinit=file['threshold'].get(), valstep=1, orientation='vertical')

    # # temporary
    # # update_mask()

    self.redraw_mod()
    self.redraw_threshold()
    self.redraw_orig()
    
    self.b_nframe.on_clicked(self.update_frame_next)
    self.b_pframe.on_clicked(self.update_frame_prev)
    self.x_i.on_changed(self.update_orig)
    self.threshold.on_changed(self.update_threshold)

    # self.canvas.mpl_connect('button_press_event', lambda event:self.canvas._tkcanvas.focus_set())
    # self.canvas.mpl_connect("button_press_event", self.on_key_press)
    
    self.draw_figure()
