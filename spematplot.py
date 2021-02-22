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

T10_PALETTE = {
    'tab:blue', 
    'tab:orange', 
    'tab:green', 
    'tab:red', 
    'tab:purple',
    'tab:brown', 
    'tab:pink', 
    'tab:gray', 
    'tab:olive', 
    'tab:cyan'
}


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
        # Needs to be redrawn since there is no set_data method.
        if hasattr(self, 'orig'):
            self.orig.remove()
        self.orig = self.ax_orig.imshow(
            self.img,
            cmap = self.file['cmap'].get(),
            origin = 'lower',
        )

        max_coor = self.file['relmax']
        x_i = self.file['x_i'].get()
        y_i = self.file['y_i'].get()
        sel_str = "Strength\n" + str(self.file['sel_strength'].get())
        str_x = float(x_i)/self.iwidth
        if hasattr(self, 'orig_relmax'):
            self.orig_relmax.set_data(max_coor[:, 1],max_coor[:, 0])
            self.orig_x.set_ydata(x_i)
            self.orig_x.set_label("Selected x=" + str(x_i))
            self.orig_y.set_xdata(y_i)
            self.orig_y.set_label("Selected y=" + str(y_i))
            self.orig_str.set_position((1.1,str_x))
            self.orig_str.set_text(sel_str)
        else:
            # max_x = self.file['max_x'].get()
            self.orig_x = self.ax_orig.axhline(
                y = x_i,
                linestyle='-',
                linewidth=1,
                color='tab:red',
                label = "Selected x=" + str(x_i),
                # animated = True,
            )
            self.orig_y = self.ax_orig.axvline(
                x = y_i,
                linestyle='-',
                linewidth=1,
                color='tab:red',
                label = "Selected y=" + str(y_i),
                # animated = True,
            )
            relmax = self.ax_orig.plot(
                max_coor[:, 1],
                max_coor[:, 0],
                'x',
                color = 'tab:pink',
                label = "Regional Maxima",
            )
            self.orig_relmax = relmax[0]
            self.orig_str = self.ax_orig.text(
                1.1,
                str_x,
                sel_str, 
                horizontalalignment = 'center',
                verticalalignment = 'center',
                transform = self.ax_orig.transAxes,
                bbox = dict(facecolor='tab:red', alpha=0.1),
                # xytext=(0.9, 1.1), 
                # str(sel_str),
                # xy = (y_i,x_i),
                # xycoords = 'data',
                # textcoords='axes fraction',
                # arrowprops = dict(facecolor='black', shrink=0.05),
                # horizontalalignment = 'right', 
                # verticalalignment = 'top',
            )
        # Needs to be redrawn every time to update.
        self.orig_legend = self.ax_orig.legend(
            loc='upper center', 
            bbox_to_anchor=(0.5,-0.1),
        )
        # self.ax_orig.set_axis_on()
        # self.ax_orig.set_yticks(np.arange(0,self.iwidth,100))
        # self.ax_orig.set_xticks(np.arange(0,self.iheight,100))
        # self.ax_orig.minorticks_on()


    def draw_threshold(self):
        """Draw the threshold graph axis, pre-blitting."""
        self.xgraph_title = self.ax_xgraph.set_title(
            '',
            # animated = True,
        )
        # self.threshold.poly.draw(self.canvas.get_renderer())
        # self.bm.add_artist(self.xgraph_title)
        self.ax_xgraph.set_ylim([np.amin(self.img), np.amax(self.img)])
        max_x = self.file['max_x'].get()
        x_i = self.file['x_i'].get()
        if hasattr(self, 'xgraph_plot'):
            self.xgraph_plot.set_ydata(self.img[x_i])
            self.xgraph_plot.set_label("Strength at x = " + str(x_i))
            self.xgraph_max.set_ydata(self.img[max_x])
        else:
            (self.xgraph_plot,) = self.ax_xgraph.plot(
                self.img[x_i],
                color = 'tab:red',
                label = "Strength at x = " + str(x_i),
                # animated = True,
            )
            (self.xgraph_max,) = self.ax_xgraph.plot(
                self.img[max_x],
                color = 'tab:blue',
                label = "Max Strength",
                # animated = True,
            )
            # self.ax_xgraph.set_box_aspect(self.iwidth/self.iheight)
            # self.ax_xgraph.set_axis_on()
            # self.ax_xgraph.set_yticks(np.arange(0,self.iwidth,100))
            # self.ax_xgraph.set_xticks(np.arange(0,self.iheight,100))
            # self.ax_xgraph.minorticks_on()
            self.ax_xgraph.set_box_aspect(self.iwidth/self.iheight)
        self.xgraph_legend = self.ax_xgraph.legend(
            loc='upper center', 
            bbox_to_anchor=(0.5,-0.05),
        )
        # self.bm.add_artist(self.xgraph_plot)
        # self.xgraph_line = self.ax_xgraph.axhline(
        #     y = self.file['threshold'].get(),
        #     linestyle = '-',
        #     linewidth = 2,
        #     color = 'tab:red',
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
            origin='lower',
            # animated = True,
        )
        # self.bm.add_artist(self.mod)
        # self.ax_mod.imshow(self.threshold_poly)

    def update(self):
        """Redraw the animated elements of the matplot"""
        self.orig_title.set_text("Frame #" + str(self.file['frame_i'].get()))
        self.xgraph_plot.set_ydata(self.img[self.file['x_i'].get()])
        # self.xgraph_line.set_ydata(self.file['threshold'].get())
        self.xgraph_title.set_text(
            "Sig Str across x")
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
        self.axes = self.fig.subplots(
            1, 
            3,
            gridspec_kw = {
                'wspace': 0.5,
            })
        (self.ax_orig, self.ax_xgraph, self.ax_mod) = self.axes
        self.ax_mod.set_title("Modified Image")
        self.ax_pframe = self.fig.add_axes([0.12, 0.05, 0.1, 0.05])
        self.ax_nframe = self.fig.add_axes([0.23, 0.05, 0.1, 0.05])
        self.ax_poly = self.fig.add_axes([0.7, 0.05, 0.2, 0.05])
        self.poly = None
        # self.fig.tight_layout(h_pad=2)

        # plot slider
        # self.x_i = Slider(
        #     self.ax_orig,
        #     "",
        #     0,
        #     self.iwidth - 1,
        #     valinit=self.file['x_i'].get(),
        #     valstep=1,
        #     orientation='vertical',
        #     fill=False,
        #     linestyle='-',
        #     linewidth=2,
        #     color='tab:red',
        # )
        str_max = floor(np.amax(file['img']))
        self.threshold = Slider(
            self.ax_xgraph,
            "",
            # these need to be changed based on Frame?
            0,
            str_max,
            valinit=self.file['threshold'].get(),
            valstep=1,
            orientation='vertical',
            fill=False,
            linestyle='-',
            linewidth=2,
            color='tab:red',
        )
        self.b_nframe = mpButton(self.ax_nframe, 'Next Frame')
        self.b_pframe = mpButton(self.ax_pframe, 'Prev Frame')
        self.b_poly = mpButton(self.ax_poly, 'Select Region')
        
        # Slider removes Axis ticks, so need to recreate.
        self.ax_orig.set_yticks(np.arange(0,self.iwidth,100))
        self.ax_orig.set_xticks(np.arange(0,self.iheight,100))
        self.ax_orig.minorticks_on()
        # self.x_i.valtext.set_visible(False)

        str_interval = str_max/3
        self.ax_xgraph.set_yticks(np.arange(0,str_max,str_interval))
        self.ax_xgraph.set_xticks(np.arange(0,self.iheight,100))
        self.ax_xgraph.minorticks_on()
        self.threshold.valtext.set_visible(False)
        
        self.ax_mod.set_yticks(np.arange(0,self.iwidth,100))
        self.ax_mod.set_xticks(np.arange(0,self.iheight,100))
        self.ax_mod.minorticks_on()

        self.draw_figure()
