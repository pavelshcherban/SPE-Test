from blitmanager import BlitManager
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
import time

class spematplot():

    # def redraw_mod(self):
    #     """Redraw the modified image animated element"""
    #     # self.ax_mod.clear()
    #     sm = cm.ScalarMappable(cmap=self.file['cmap'].get())
    #     img = sm.to_rgba(self.img)
    #     self.mod.make_image(img)
    #     # self.ax_mod.imshow(self.threshold_poly)

    def draw_figure(self):
        """Draw the Figure on the tk canvas and set blitting.

        This should be called when the original img frame changes.
        It is more expensive than update(), which uses blitting to redraw
        everything else.
        """
        self.img = self.file['img']
        # self.bm = BlitManager(self.canvas)
        # self.clear_axes()
        self.draw_frame()
        self.draw_threshold()
        self.draw_mod()
        self.update()
        # self.canvas.draw_idle()
        self.canvas.draw()
        self.canvas.flush_events()
        # time.sleep(0.1)
        # self.bm.on_draw()
        # self.update()

    # def clear_axes(self):
    #     """Clear all axes in the matplot."""
    #     for axis in self.axes:
    #         axis.clear()

    def draw_frame(self):
        """Draw the original image frame, pre-blitting."""
        self.orig_title = self.ax_orig.set_title(
            "",
            # animated = True,
        )
        # self.bm.add_artist(self.orig_title)
        if hasattr(self, 'orig'):
            self.orig.remove()
        self.orig = self.ax_orig.imshow(
            self.img,
            cmap = self.file['cmap'].get(),
            origin = 'lower',
        )

    def draw_threshold(self):
        """Draw the threshold graph axis, pre-blitting."""
        self.xgraph_title = self.ax_xgraph.set_title(
            '',
            # animated = True,
        )
        # self.threshold.poly.draw(self.canvas.get_renderer())
        # self.bm.add_artist(self.xgraph_title)
        self.ax_xgraph.set_ylim([np.amin(self.img), np.amax(self.img)])
        if hasattr(self, 'xgraph_plot'):
            self.xgraph_plot.set_ydata(self.img[self.file['x_i'].get()])
        else:
            (self.xgraph_plot,) = self.ax_xgraph.plot(
                self.img[self.file['x_i'].get()],
                # animated = True,
            )
        # self.bm.add_artist(self.xgraph_plot)
        # self.xgraph_line = self.ax_xgraph.axhline(
        #     y = self.file['threshold'].get(), 
        #     linestyle = '-', 
        #     linewidth = 2, 
        #     color = 'firebrick',
        #     animated = True,
        # )
        # self.bm.add_artist(self.xgraph_line)

    def draw_mod(self):
        """Draw the modified image, pre-blitting."""
        mod = self.file['mod']
        # Store location of 0 values for alpha later.
        zeroes = (mod == 0)
        sm = cm.ScalarMappable(cmap=self.file['cmap'].get())
        mod = sm.to_rgba(mod)
        # Set alpha to 0 for excluded values.
        mod[zeroes, 3] = 0
        if hasattr(self, 'mod'):
            self.mod.remove()
        self.mod = self.ax_mod.imshow(
            mod, 
            origin = 'lower', 
            # animated = True,
        )
        # self.bm.add_artist(self.mod)
        # self.ax_mod.imshow(self.threshold_poly)

    def update(self):
        """Redraw the animated elements of the matplot"""
        self.orig_title.set_text("Frame #" + str(self.file['frame_i'].get()))
        self.xgraph_plot.set_ydata(self.img[self.file['x_i'].get()])
        # self.xgraph_line.set_ydata(self.file['threshold'].get())
        self.xgraph_title.set_text("Strength at x=" + str(self.file['x_i'].get()))
        # self.redraw_mod()
        # self.bm.update()

    def update_mask(self):
        print("Updating map to ")
        self.wsf.mask_poly = np.array((
            (100, 100),
            (200, 100),
            (200, 200),
        ))
        self.draw_mod()

    # def onclick(self, event):
    #     """Registers the selection of a polygon"""
    #     if event.inaxes == self.ax_mod:
    #         cmap = event.inaxes.get_title()
    #         # print('inaxes=%s' %(cmap))
    #         print(vars(event))
    #     # {'button': <MouseButton.LEFT: 1>, 'key': None, 'step': 0, 'dblclick': False, 'name': 'button_press_event', 'canvas': <matplotlib.backends.backend_tkagg.FigureCanvasTkAgg object at 0x000001E2AF80CA60>, 'guiEvent': <ButtonPress event num=1 x=488 y=220>, 'x': 488, 'y': 260, 'inaxes': <AxesSubplot:>, 'xdata': 101.07419354838692, 'ydata': 198.8083870967742}

    # def ondrag(self, event):
    #     """Registers the selection of a polygon"""
    #     if event.inaxes == self.ax_mod:
    #         self.file['threshold_poly'][int(event.ydata)][int(event.xdata)] = 1
    #         self.threshold_poly = np.fliplr(self.file['threshold_poly'])
    #         self.draw_mod()
    #         self.draw_figure()
    #         print(vars(event))
    #     # {'button': None, 'key': None, 'step': 0, 'dblclick': False, 'name': 'motion_notify_event', 'canvas': <matplotlib.backends.backend_tkagg.FigureCanvasTkAgg object at 0x000001E2AF80CA60>, 'guiEvent': <Motion event x=488 y=220>, 'x': 488, 'y': 260, 'inaxes': <AxesSubplot:>, 'xdata': 101.07419354838692, 'ydata': 198.8083870967742}

    def __init__(self, file, window):
        self.file = file
        self.iwidth, self.iheight = file['img'].shape

        self.fig = Figure()
        self.canvas = FigureCanvasTkAgg(self.fig, master=window['toplevel'])
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.toolbar = NavigationToolbar2Tk(self.canvas, window['toplevel'])
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # create initial plot
        self.axes = self.fig.subplots(1, 3)
        (self.ax_orig, self.ax_xgraph, self.ax_mod) = self.axes
        self.ax_mod.set_title("Modified Image")
        self.ax_pframe = self.fig.add_axes([0.12, 0.05, 0.1, 0.05])
        self.ax_nframe = self.fig.add_axes([0.23, 0.05, 0.1, 0.05])
        self.ax_poly = self.fig.add_axes([0.7, 0.05, 0.2, 0.05])
        self.poly = None
        # self.fig.tight_layout(h_pad=2)

        # plot slider
        self.x_i = Slider(
            self.ax_orig,
            "",
            0,
            self.iwidth - 1,
            valinit = self.file['x_i'].get(),
            valstep = 1,
            orientation = 'vertical',
            fill = False,
            linestyle = '-',
            linewidth = 2,
            color = 'firebrick',
        )
        self.threshold = Slider(
            self.ax_xgraph,
            "", 
            # these need to be changed based on Frame?
            0,
            floor(np.amax(file['img'])),
            valinit = self.file['threshold'].get(),
            valstep = 1,
            orientation = 'vertical',
            fill = False,
            linestyle = '-', 
            linewidth = 2, 
            color = 'firebrick',    
        )
        self.b_nframe = mpButton(self.ax_nframe, 'Next Frame')
        self.b_pframe = mpButton(self.ax_pframe, 'Prev Frame')
        self.b_poly = mpButton(self.ax_poly, 'Select Region')

        self.draw_figure()
