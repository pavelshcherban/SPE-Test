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

    def update(self):
        self.orig_title.set_text("Frame #" + str(self.file['frame_i']))
        # self.x_i_line.set_ydata(np.full((self.iwidth,),self.file['x_i']))
        self.x_i_line.set_ydata(self.file['x_i'])
        self.xgraph_plot.set_ydata(self.img[self.file['x_i']])
        self.xgraph_line.set_ydata(self.file['threshold'].get())
        self.xgraph_title.set_text("Strength at x=" + str(self.file['x_i']))
        self.bm.update()

    def draw_figure(self):
        """Draws the Figure on the tk canvas."""
        self.draw_frame()
        self.draw_x_i()
        self.draw_threshold()
        self.draw_mod()
        self.canvas.draw()
        self.canvas.flush_events()
        time.sleep(0.1)
        # print("bm Update")
        self.update()

    def draw_frame(self):
        # self.ax_orig.clear()
        self.orig_title = self.ax_orig.set_title(
            "",
            animated = True,
        )
        self.bm.add_artist(self.orig_title)
        self.ax_orig.imshow(
            self.img,
            cmap = self.file['cmap'].get(),
            origin = 'lower',
        )

    def draw_x_i(self):
        self.x_i_line = self.ax_orig.axhline(
            y = self.file['x_i'],
            linestyle = '-',
            linewidth = 2,
            color = 'firebrick',
            animated = True,
        )
        self.bm.add_artist(self.x_i_line)

    def draw_threshold(self):
        # self.ax_xgraph.clear()
        self.ax_xgraph.set_ylim([np.amin(self.img), np.amax(self.img)])
        (self.xgraph_plot,) = self.ax_xgraph.plot(
            self.img[self.file['x_i']],
            animated = True,
        )
        self.bm.add_artist(self.xgraph_plot)
        self.xgraph_line = self.ax_xgraph.axhline(
            y = self.file['threshold'].get(), 
            linestyle = '-', 
            linewidth = 2, 
            color = 'firebrick',
            animated = True,
        )
        self.bm.add_artist(self.xgraph_line)

    def draw_mod(self):
        # self.ax_mod.clear()
        sm = cm.ScalarMappable(cmap=self.file['cmap'].get())
        img = sm.to_rgba(self.img)
        self.ax_mod.imshow(img, origin='lower')
        # self.ax_mod.imshow(self.threshold_poly)
        # ax_mod.imshow(wsf.image_raw(), cmap='jet', clim=(wsf.threshold, wsf.max_val()), origin='lower')

    # def update_frame_next(self, event):
    #     """Updates the frame selection for the file to the next frame."""
    #     if self.file['frame_i'] < self.file['spefile'].header.NumFrames-1:
    #         print("Updating to next frame", self.file['frame_i']+1)
    #         self.file['frame_i'] += 1
    #         self.file['img'] = process_image(self.file)
    #         self.redraw_frame()
    #     else:
    #         print("Last frame already selected")

    # def update_frame_prev(self, event):
    #     """Updates the frame selection for the file to the previous frame."""
    #     if self.file['frame_i'] > 0:
    #         print("Updating to prev frame", self.file['frame_i']-1)
    #         self.file['frame_i'] -= 1
    #         self.file['img'] = process_image(self.file)
    #         self.redraw_frame()
    #     else:
    #         print("First frame already selected")

    def redraw_frame(self):
        # print("redraw_frame")
        self.img = self.file['img']
        self.draw_orig()
        self.draw_threshold()
        self.draw_mod()
        self.draw_figure()

    # def update_orig(self, val):
    #     print("Updating x_i to ", val)
    #     self.file['x_i'] = val
    #     self.draw_orig()
    #     self.draw_threshold()

    # def update_threshold(self, val):
    #     print("Updating threshold to ", val)
    #     self.file['threshold'].set(val)
    #     self.draw_threshold()
    #     self.draw_mod()

    def update_mask(self):
        print("Updating map to ")
        self.wsf.mask_poly = np.array((
            (100, 100),
            (200, 100),
            (200, 200),
        ))
        self.draw_mod()

    # def show(self):
    #   self.fig.show()

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
        self.img = self.file['img']
        self.iwidth, self.iheight = self.img.shape

        self.fig = Figure()
        self.canvas = FigureCanvasTkAgg(self.fig, master=window['toplevel'])
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.toolbar = NavigationToolbar2Tk(self.canvas, window['toplevel'])
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # create initial plot
        self.bm = BlitManager(self.canvas)
        (self.ax_orig, self.ax_xgraph, self.ax_mod) = self.fig.subplots(1, 3)
        self.xgraph_title = self.ax_xgraph.set_title(
            '',
            animated = True,
        )
        self.bm.add_artist(self.xgraph_title)
        self.ax_mod.set_title("Modified Image")
        self.ax_pframe = self.fig.add_axes([0.7, 0.05, 0.1, 0.075])
        self.ax_nframe = self.fig.add_axes([0.81, 0.05, 0.1, 0.075])
        # self.fig.tight_layout(h_pad=2)

        # plot slider
        self.b_nframe = mpButton(self.ax_nframe, 'Next Frame')
        self.b_pframe = mpButton(self.ax_pframe, 'Previous Frame')
        self.x_i = Slider(
            self.ax_orig,
            "",
            0,
            self.iwidth-1,
            valinit=file['x_i'],
            valstep=1,
            orientation='vertical',
            fill = False,
        )
        self.threshold = Slider(
            self.ax_xgraph,
            "", 
            ceil(np.amin(self.img)),
            floor(np.amax(self.img)),
            valinit=file['threshold'].get(),
            valstep=1,
            orientation='vertical',
            fill = False,
        )

        # # temporary
        # # update_mask()

        # self.draw_mod()
        # self.draw_threshold()
        # self.draw_orig()

        # self.b_nframe.on_clicked(self.update_frame_next)
        # self.b_pframe.on_clicked(self.update_frame_prev)
        # self.x_i.on_changed(self.update_orig)
        # self.threshold.on_changed(self.update_threshold)

        self.draw_figure()
