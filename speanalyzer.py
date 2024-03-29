import tkinter as tk
from math import floor
from os import path
import time
from tkinter import IntVar, filedialog, ttk
from tkinter.constants import ANCHOR

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.backend_bases import button_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure
from matplotlib.widgets import Button as mpButton
from matplotlib.widgets import PolygonSelector, Slider
from matplotlib.path import Path as mpPath
from mpl_toolkits.axes_grid1 import ImageGrid
from scipy import ndimage
from skimage import color, filters, util
from skimage.feature import peak_local_max
from skimage.draw import polygon, polygon2mask
from scipy.signal import argrelmax

from colorplot import colorplot
from pyWinSpec.winspec import SpeFile
from spematplot import spematplot
from WinSpecFrame import WinSpecFrame
from output import Output
import argparse


# global variables
CMAPS = [
    ('Perceptually Uniform Sequential', [
        'viridis', 'plasma', 'inferno', 'magma', 'cividis'
    ]),
    ('Sequential', [
        'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
        'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
        'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn'
    ]),
    ('Sequential (2)', [
        'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
        'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
        'hot', 'afmhot', 'gist_heat', 'copper'
    ]),
    ('Diverging', [
        'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
        'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic'
    ]),
    ('Cyclic', [
        'twilight', 'twilight_shifted', 'hsv'
    ]),
    ('Miscellaneous', [
        'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
        'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
        'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar'
    ]),
]


class SpeAnalyzer:

    @staticmethod
    def process_image(spe_data, frame_i):
        """Processes raw spe data into a frame array for analysis."""
        # Reduce noise in image.
        img = ndimage.median_filter(spe_data.data[frame_i], size=3)
        # Correct mirror orientation of image and correct for exposure.
        img = np.fliplr(img/spe_data.header.exp_sec)
        return img

    def update_mod(self, filename):
        f = self.files[filename]
        img = f['img']
        mod = np.where(img > f['threshold'].get(), img, 0)
        # For displaying selected polygon instead
        # mod = img * f['polyMask']
        f['mod'] = mod
        # ax_mod.imshow(wsf.image_raw(),
        #  cmap='jet', 
        # clim=(wsf.threshold, wsf.max_val()), origin='lower')

        
    def select_files(self):
        """Allows user to manually select SPE files."""
        filenames = filedialog.askopenfilenames(
            initialdir=".",
            title="Select a File",
            filetypes=(("Text files", "*.SPE"), ("all files", "*.*"))
        )
        self.read_files(filenames)

    def draw_matplot(self, filename):
        """Update matplot if it is available."""
        if 'spematplot' in self.windows[filename]:
                self.windows[filename]['spematplot']['matplot'].draw_figure()

    def update_frame(self, filename):
        """Update frame-related components."""
        file = self.files[filename]
        # First update the image.
        file['img'] = SpeAnalyzer.process_image(
            file['spefile'], 
            file['frame_i'].get()
        )
        # Update image dependant stats.
        # image_max = ndimage.maximum_filter(file['img'], size=50, mode='constant')
        file['relmax'] = peak_local_max(
            file['img'], 
            min_distance = 5,
            threshold_rel = 0.2,
            num_peaks = 10,
        )
        # file['relmax'] = argrelmax(file['img'], order=100)
        # print(file['relmax'][0].shape)
        # print(file['relmax'][1].shape)
        # print(file['img'][file['relmax'][0]][file['relmax'][1]])
        stren = floor(np.amax(file['img']))
        file['max_strength'].set(stren)
        frameSum = np.sum(file['img'])
        file['frameSum'].set(frameSum)
        ind = np.argmax(file['img'])
        x,y = np.unravel_index(ind, file['img'].shape)
        file['max_x'].set(x)
        file['max_y'].set(y)
        file['y_i'].set(y)
        file['x_i'].set(x)
        # Recalculate mods and plots.
        self.update_mod(filename)
        self.draw_matplot(filename)

    def apply_default_cmap(self, filename):
        """Sets colormap for one loaded file based on default."""
        f = self.files[filename]
        if filename.endswith('bNIR.SPE'):
            f['cmap'].set(self.root_cmap_bnir.get())
        else:
            f['cmap'].set(self.root_cmap_fnir.get())

    def apply_default_cmaps(self):
        """Sets colormaps for all loaded files based on defaults."""
        for f in self.files:
            self.apply_default_cmap(f)

    def read_files(self, filenames):
        """Extract SPE files to spe object."""
        files_added = []
        for filename in filenames:
            if filename not in self.files:
                files_added.append(filename)
                spefile = SpeFile(filename)
                frame_i = tk.IntVar()
                # xgrpah = img[45]
                # xtest = np.full((256,), 45)
                threshold = tk.IntVar()
                cmap = tk.StringVar()
                sel_strength = tk.IntVar()
                x_i = tk.IntVar()
                y_i = tk.IntVar()
                max_strength = tk.IntVar()
                max_x = tk.IntVar()
                max_y = tk.IntVar()
                order = tk.IntVar()
                frameSum = tk.IntVar()
                polySum = tk.IntVar()
                # Update instance dicts.
                self.windows[filename] = {}
                self.files[filename] = {
                    'spefile': spefile,
                    'threshold': threshold,
                    'cmap': cmap,
                    'NIR': '',
                    'frame_i': frame_i,
                    'sel_strength' : sel_strength,
                    'x_i': x_i,
                    'y_i': y_i,
                    'order': order,
                    'max_strength' : max_strength,
                    'max_x' : max_x,
                    'max_y' : max_y,
                    'frameSum': frameSum,
                    'polyMask': np.ones((320, 256), dtype=np.uint8),
                    'polySum': polySum,
                }
                x_i.trace_add(
                    'write',
                    lambda p0,p1,p2,f=filename: self.update_x_i(f)
                )
                frame_i.trace_add(
                    'write',
                    lambda p0,p1,p2,f=filename: self.update_frame(f)
                )
                frame_i.set(0)
                # threshold_poly = np.zeros_like(self.files[filename]['img'])
                # self.files[filename]['threshold_poly'] = threshold_poly
                threshold.set(self.root_threshold.get())
                threshold.trace_add(
                    'write',
                    lambda p0,p1,p2,f=filename: self.post_update_threshold(f)
                )
                if filename.endswith('bNIR.SPE'):
                    self.files[filename]['NIR'] = 'bright field'
                else:
                    self.files[filename]['NIR'] = 'flourescence'
                self.apply_default_cmap(filename)
                cmap.trace_add(
                    'write',
                    lambda p0,p1,p2,f=filename: self.draw_matplot(f)
                )
                order.set(len(self.files) - 1)
                order.trace_add(
                    'write',
                    lambda p0,p1,p2: self.set_grid_order()
                )
        if len(files_added) > 0:
            self.create_listframe(files_added)

    def change_order(self, filename, old_order, new_order):
        self.remove_order(old_order)
        self.insert_order(new_order)
        self.files[filename]['order'].set(new_order)
        
    def insert_order(self, order):
        for f in self.files.values():
            if f['order'].get() >= order:
                f['order'].set(f['order'].get() + 1)

    def remove_order(self, order):
        for f in self.files.values():
            if f['order'].get() > order:
                f['order'].set(f['order'].get() - 1)

    def set_grid_order(self):
        for f in self.files.values():
            order = f['order'].get()
            f['fileframe'].grid(row=order, column=0, sticky=tk.N+tk.W)

    def create_listframe(self, files_added):
        """Creates tk Frame for currently selected SPE files."""
        for filename in files_added:
            f = self.files[filename]
            # Create overall frame for file.
            fileframe = ttk.Frame(self.listframe, padding='5', relief='ridge')

            # Create subframe for file details
            details = ttk.Frame(fileframe)
            details.grid(row=0, column=0)
            ttk.Label(details, text="File: "
                ).grid(row=0, column=0)
            ttk.Label(details, text=filename
                ).grid(row=0, column=1, columnspan=5)
            ttk.Label(details, text="SPE type: "
                ).grid(row=1, column=0)
            ttk.Label(details, text=f['NIR']
                ).grid(row=1, column=1)
            ttk.Label(details, text="Current Frame: "
                ).grid(row=2, column=0)
            ttk.Entry(details, textvariable=f['frame_i'], state="readonly"
                ).grid(row=2, column=1)
            ttk.Label(details, text="Whole Frame Sum: "
                ).grid(row=2, column=2)
            # ttk.Label(details, textvariable=f['frameSum']
            #     ).grid(row=2, column=3)
            ttk.Entry(details, textvariable=f['frameSum'], state="readonly"
                ).grid(row=2, column=3)
            ttk.Label(details, text="Current threshold: "
                ).grid(row=3, column=0)
            ttk.Entry(details, textvariable=f['threshold'], state="readonly"
                ).grid(row=3, column=1)
            ttk.Label(details, text="Selected Region Sum: "
                ).grid(row=3, column=2)
            ttk.Entry(details, textvariable=f['polySum'], state="readonly"
                ).grid(row=3, column=3)
            ttk.Label(details, text="Max Strength: "
                ).grid(row=4, column=0)
            ttk.Entry(details, textvariable=f['max_strength'], state="readonly"
                ).grid(row=4, column=1)
            ttk.Label(details, text="Max x_index: "
                ).grid(row=4, column=2)
            ttk.Entry(details, textvariable=f['max_x'], state="readonly"
                ).grid(row=4, column=3)
            ttk.Label(details, text="Max y_index: "
                ).grid(row=4, column=4)
            ttk.Entry(details, textvariable=f['max_y'], state="readonly"
                ).grid(row=4, column=5)
            ttk.Label(details, text="Selected Strength: "
                ).grid(row=5, column=0)
            ttk.Entry(details, textvariable=f['sel_strength'], state="readonly"
                ).grid(row=5, column=1)
            ttk.Label(details, text="Selected x_index: "
                ).grid(row=5, column=2)
            ttk.Entry(details, textvariable=f['x_i'], state="readonly"
                ).grid(row=5, column=3)
            ttk.Label(details, text="Selected y_index: "
                ).grid(row=5, column=4)
            ttk.Entry(details, textvariable=f['y_i'], state="readonly"
                ).grid(row=5, column=5)
            ttk.Label(details, text="Current colormap: "
                ).grid(row=7, column=0)
            # ttk.Label(details, textvariable=f['cmap']
            #   ).grid(row=3, column=1)
            cm = ttk.Combobox(
                details,
                textvariable=f['cmap'],
                values=self.cmap_combo
            )
            cm.grid(row=7, column=1)
            cm.state(['readonly'])
            button_color = ttk.Button(
                details,
                text="Select from Colorplots",
                command=lambda f=filename: self.show_colorplots(f),
            )
            button_color.grid(row=7, column=2)

            for child in details.winfo_children():
                child.grid_configure(padx=5, pady=1, sticky=tk.W)
            
            # Create subframe for file actions.
            buttons = ttk.Frame(fileframe)
            buttons.grid(row=0, column=1)
            button_discard = ttk.Button(
                buttons,
                text="Discard File",
                command=lambda f=filename: self.discard_file(f),
            )
            button_discard.grid(row=0, column=0)
            button_matplot = ttk.Button(
                buttons,
                text="Show Matplot",
                command=lambda f=filename: self.show_matplot(f),
            )
            button_matplot.grid(row=1, column=0)

            for child in buttons.winfo_children():
                child.grid_configure(padx=5, pady=5, sticky=tk.N+tk.W)

            sep = ttk.Separator(fileframe, orient=tk.HORIZONTAL)
            sep.grid(row=1, column=0, sticky=tk.W+tk.E)

            self.files[filename]['fileframe'] = fileframe
        self.set_grid_order()

    # def matplot_press(self, event, filename):
    #     """Registers the selection of a polygon in Matplot"""
    #     matplot = self.windows[filename]['spematplot']['matplot']
    #     if event.inaxes is matplot.ax_mod:
    #         cmap = event.inaxes.get_title()
    #         # print('inaxes=%s' %(cmap))
    #         print(vars(event))
    #     # {'button': <MouseButton.LEFT: 1>, 'key': None, 'step': 0, 'dblclick': False, 'name': 'button_press_event', 'canvas': <matplotlib.backends.backend_tkagg.FigureCanvasTkAgg object at 0x000001E2AF80CA60>, 'guiEvent': <ButtonPress event num=1 x=488 y=220>, 'x': 488, 'y': 260, 'inaxes': <AxesSubplot:>, 'xdata': 101.07419354838692, 'ydata': 198.8083870967742}

    # def matplot_motion(self, event, filename):
    #     """Registers the selection of a polygon in Matplot"""
    #     matplot = self.windows[filename]['spematplot']['matplot']
    #     if event.inaxes is matplot.ax_mod:
    #         y = int(event.ydata)
    #         x = int(event.xdata)
    #         # self.files[filename]['threshold_poly'][y][x] = 1
    #         # self.threshold_poly = np.fliplr(self.file['threshold_poly'])
    #         # matplot.draw_threshold_poly()
    #         # print(vars(event))
    #     # {'button': None, 'key': None, 'step': 0, 'dblclick': False, 'name': 'motion_notify_event', 'canvas': <matplotlib.backends.backend_tkagg.FigureCanvasTkAgg object at 0x000001E2AF80CA60>, 'guiEvent': <Motion event x=488 y=220>, 'x': 488, 'y': 260, 'inaxes': <AxesSubplot:>, 'xdata': 101.07419354838692, 'ydata': 198.8083870967742}

    def update_frame_next(self, filename):
        """Update the frame selection for the file to the next frame."""
        f = self.files[filename]
        frame_i = f['frame_i'].get()
        if frame_i + 1 < f['spefile'].header.NumFrames:
            print("Updating to next frame", frame_i)
            f['frame_i'].set(frame_i + 1)
        else:
            print("Last frame already selected.")

    def update_frame_prev(self, filename):
        """Update the frame selection for the file to the previous frame."""
        f = self.files[filename]
        frame_i = f['frame_i'].get()
        if frame_i > 0:
            print("Updating to prev frame", frame_i)
            f['frame_i'].set(frame_i - 1)
        else:
            print("First frame already selected.")

    def update_poly(self, filename, vertices):
        f = self.files[filename]
        matplot = self.windows[filename]['spematplot']['matplot']
        # print(filename)
        # print(vertices)
        print("Saving Polygon vertices: ", vertices)
        f['poly_verts'] = vertices
        r = []
        c = []
        for (x,y) in vertices:
            r.append(x)
            c.append(y)
        npR = np.array(r)
        npC = np.array(c)
        rr, cc = polygon(npR, npC)
        polyMask = np.zeros((320, 256), dtype=np.uint8)
        polyMask[cc, rr] = 1
        f['polyMask'] = polyMask
        img = f['img']
        polySum = np.sum(img * polyMask)
        print("Updating Polygon sum: ", polySum)
        f['polySum'].set(polySum)
        # mod = np.where(img > f['threshold'].get(), img, 0)
        # print("polyMask: ", polyMask)
        # Save polygon and remove PolygonSelector.
        # Put in select_poly???
        # matplot.poly.disconnect_events()

    def select_poly(self, filename):
        """Launch Poly Selector and update poly."""
        matplot = self.windows[filename]['spematplot']['matplot']
        matplot.poly = PolygonSelector(
            matplot.ax_mod,
            lambda v, f=filename: self.update_poly(f,v),
        )
        # Prepopulate with existing verts.
        # matploy.poly.property = verts

    def update_x_i(self, filename):
        f = self.files[filename]
        x = f['x_i'].get()
        y = f['y_i'].get()
        f['sel_strength'].set(floor(f['img'][x][y]))
        self.draw_matplot(filename)

    def update_threshold(self, val, filename):
        f = self.files[filename]
        print("Updating threshold to ", val)
        f['threshold'].set(val)

    def post_update_threshold(self, filename):
        """Run post threshold update hooks."""
        self.update_mod(filename)
        self.draw_matplot(filename)

    def matplot_press(self, event, filename):
        """Register a mouse click on a matplot plot"""
        if event.inaxes:
            file = self.files[filename]
            matplot = self.windows[filename]['spematplot']['matplot']
            ax_orig, ax_xgraph, ax_mod =  matplot.axes
            ax_click = event.inaxes
            if ax_click == ax_orig:
                file['y_i'].set(floor(event.xdata))
                file['x_i'].set(floor(event.ydata))

    def show_matplot(self, filename):
        """Displays matplot based on spe file."""
        # First check to see if there are any windows for this file already.
        if 'spematplot' in self.windows[filename]:
            self.windows[filename]['spematplot']['toplevel'].lift()
        else:
            # Create tk window that will hold matplot.
            window = {'toplevel': tk.Toplevel(root)}
            window['toplevel'].title(filename)
            window['toplevel'].protocol(
                "WM_DELETE_WINDOW",
                lambda f=filename, c='spematplot': self.destroy_window(f, c)
            )
            self.windows[filename]['spematplot'] = window
            # Create Matplot and connect to backend.
            matplot = spematplot(
                self.files[filename],
                self.windows[filename]['spematplot']
            )
            # Bind in this class to access other frames of img data.
            matplot.b_nframe.on_clicked(
                lambda e, f=filename: self.update_frame_next(f)
            )
            matplot.b_pframe.on_clicked(
                lambda e, f=filename: self.update_frame_prev(f)
            )
            matplot.b_poly.on_clicked(
                lambda e, f=filename: self.select_poly(f)
            )
            matplot.canvas.mpl_connect(
                "button_press_event",
                lambda e, f=filename: self.matplot_press(e, f)
            )
            self.windows[filename]['spematplot']['matplot'] = matplot
            self.windows[filename]['spematplot']['connections'] = []
            self.connect_matplot(filename)

    # def disconnect_matplot(self, filename):
    #     """Disconnect the animated components of the matplot from the backend."""
    #     matplot = self.windows[filename]['spematplot']['matplot']
    #     connections = self.windows[filename]['spematplot']['connections']
    #     for id in connections:
    #         matplot.canvas.mpl_disconnect(id)
    #     connections.clear()

    def connect_matplot(self, filename):
        """Connect the animated components of the matplot to the backend."""
        matplot = self.windows[filename]['spematplot']['matplot']
        connections = self.windows[filename]['spematplot']['connections']
        # connections.append(matplot.x_i.on_changed(
        #     lambda v, f=filename: self.update_x_i(v, f)
        # ))
        connections.append(matplot.threshold.on_changed(
            lambda v, f=filename: self.update_threshold(v, f)
        ))

    def colorplot_press(self, event, filename):
        """Register the selection of a colormap plot"""
        if event.inaxes and event.inaxes.get_title():
            cmap = event.inaxes.get_title()
            print('inaxes=%s' %(cmap))
            self.files[filename]['cmap'].set(cmap)
            # Destroy any outstanding cmap windows.
            for cmap_category, cmap_list in CMAPS:
                if cmap_category in self.windows[filename]:
                    self.destroy_window(filename, cmap_category)

    def show_colorplots(self, filename):
        """Displays colormap matplots based on spe file."""
        for cmap_category, cmap_list in CMAPS:
            # first check to see if there are any windows for this file.
            if cmap_category in self.windows[filename]:
                self.windows[filename][cmap_category]['toplevel'].lift()
            else:
                # Create tk window that will hold matplot.
                window = {'toplevel': tk.Toplevel(root)}
                window['toplevel'].title(filename + ' -- ' + cmap_category)
                window['toplevel'].protocol(
                    "WM_DELETE_WINDOW",
                    lambda f=filename, c=cmap_category: self.destroy_window(f, c)
                )
                self.windows[filename][cmap_category] = window
                # Create Matplot and connect to backend.
                cplot = colorplot(
                    self.files[filename], 
                    self.windows[filename][cmap_category], 
                    cmap_list, 
                    cmap_category
                )
                # matplot.canvas.mpl_connect(
                #     'button_press_event', 
                #     lambda event: self.canvas._tkcanvas.focus_set()
                # )
                cplot.canvas.mpl_connect(
                    "button_press_event",
                    lambda e, f=filename: self.colorplot_press(e, f)
                )
                self.windows[filename][cmap_category]['matplot'] = cplot

    def destroy_window(self, filename, windowname):
        """Destroys tkinter window."""
        window = self.windows[filename][windowname]
        window['toplevel'].destroy()
        # del window['matplot']
        del self.windows[filename][windowname]

    def discard_file(self, filename):
        """Discard File from analyzer."""
        for window in self.windows[filename].values():
            window['toplevel'].destroy()
        del self.windows[filename]
        self.files[filename]['fileframe'].grid_forget()
        self.files[filename]['fileframe'].destroy()
        order = self.files[filename]['order'].get()
        del self.files[filename]
        self.remove_order(order)

    def on_key_press(self, event):
        if event.inaxes:
            print(event.inaxes.get_title())
        # key_press_handler(event, canvas, toolbar)

    def show_thresholds(self):
        wsf = self.images[self.image_i].get_frame()
        filters.try_all_threshold(
            wsf.image_raw(), figsize=(10, 8), verbose=True)
        plt.show()

    def apply_threshold(self):
        thresh_map = {
            'minimum': filters.threshold_minimum,
            'yen': filters.threshold_yen,
        }
        image = self.images[self.image_i].get_frame().image_raw()
        thresh = thresh_map[self.root_threshold.get()](image)
        binary = image > thresh

        fig, axes = plt.subplots(ncols=2, figsize=(8, 3))
        ax = axes.ravel()

        ax[0].imshow(image, cmap='jet', origin='lower')
        ax[0].set_title('Original image')

        ax[1].imshow(binary, cmap='jet', origin='lower')
        ax[1].set_title('Result')

        for a in ax:
            a.axis('off')

        plt.show()

    def show_matplots(self):
        for file in self.files.keys():
            self.show_matplot(file)

    def resize_listframe(self, e):
        bb = self.listcanvas.bbox("all")
        self.listcanvas.configure(
                scrollregion = bb,
                width = bb[2]-bb[0],
            )

    def on_mousewheel(self, event):
        self.listcanvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def __init__(self, root, filenames=None):
        # properties
        self.files = {}
        self.windows = {}
        self.cmap_combo = [cm for group, cms in CMAPS for cm in cms]
        self.cmap_combo.sort()

        # Root Window label variables
        self.label_filenames = tk.StringVar()
        self.root_cmap_bnir = tk.StringVar()
        self.root_cmap_fnir = tk.StringVar()
        self.root_threshold = tk.IntVar()

        self.root_cmap_bnir.set('gray')
        self.root_cmap_fnir.set('bone')
        self.root_threshold.set(0)

        # Root Window Setup
        root.title("SPE File Analyzer")
        root.columnconfigure(0, weight=0)
        root.rowconfigure(0, weight=1)

        # Main function frame
        self.mainframe = ttk.Frame(root, padding='5', relief='ridge')
        self.mainframe.grid(row=0, column=0, sticky=tk.N+tk.W+tk.S+tk.E)
        # ttk.Separator(self.mainframe, orient=VERTICAL)

        ttk.Button(
            self.mainframe,
            text="Select Files",
            command=self.select_files
        ).grid(row=0, column=0, columnspan=2)
        # ttk.Button(self.mainframe, text="Select Fluorescent Colormap",command=self.show_colormaps).grid(row=1, column=0)
        ttk.Button(
            self.mainframe,
            text="Show MatPlots",
            command=self.show_matplots
        ).grid(row=1, column=0, columnspan=2)
        ttk.Button(
            self.mainframe,
            text="Output CSV",
            command=lambda: Output.output_csv(self.files),
        ).grid(row=2, column=0, columnspan=2)
        ttk.Separator(
            self.mainframe,
            orient=tk.HORIZONTAL,
            ).grid(row=10, column=0, sticky=tk.W+tk.E)
        ttk.Label(
            self.mainframe,
            text = "Tiff image output options"
        ).grid(row=11, column=0, columnspan=2)
        ttk.Button(
            self.mainframe,
            text="Originals only",
            command=lambda: Output.output_all_tiff(self.files, style='img'),
        ).grid(row=12, column=0)
        ttk.Button(
            self.mainframe,
            text="Originals only to Folder",
            command=lambda: Output.output_all_tiff(self.files, style='img', folder=True),
        ).grid(row=12, column=1)
        ttk.Button(
            self.mainframe,
            text="Modified only",
            command=lambda: Output.output_all_tiff(self.files, style='mod'),
        ).grid(row=13, column=0)
        ttk.Button(
            self.mainframe,
            text="Modified only to Folder",
            command=lambda: Output.output_all_tiff(self.files, style='mod', folder=True),
        ).grid(row=13, column=1)
        ttk.Button(
            self.mainframe,
            text="Both",
            command=lambda: Output.output_all_tiff(self.files),
        ).grid(row=14, column=0)
        ttk.Button(
            self.mainframe,
            text="Both to Folder",
            command=lambda: Output.output_all_tiff(self.files, folder=True),
        ).grid(row=14, column=1)
        ttk.Separator(
            self.mainframe,
            orient=tk.HORIZONTAL,
            ).grid(row=15, column=0, sticky=tk.W+tk.E)
        # ttk.Button(
        #     self.mainframe,
        #     text="Unfinished - Plot Thresholds",
        #     command=self.show_thresholds
        # ).grid(row=100, column=0)
        # ttk.Button(
        #     self.mainframe,
        #     text="Unfinished - Apply Threshold",
        #     command=self.apply_threshold
        # ).grid(row=101, column=0)
        ttk.Label(
            self.mainframe,
            text = "Default min strength threshold"
        ).grid(row=101, column=0)
        ttk.Label(
            self.mainframe,
            textvariable=self.root_threshold
        ).grid(row=101, column=1)
        ttk.Label(
            self.mainframe,
            text = "Default bright field colormap:"
        ).grid(row=102, column=0)
        cm_bnir = ttk.Combobox(
            self.mainframe,
            textvariable=self.root_cmap_bnir,
            values=self.cmap_combo
        )
        cm_bnir.grid(row=102, column=1)
        cm_bnir.state(['readonly'])
        ttk.Label(
            self.mainframe,
            text = "Default flourescence colormap:"
        ).grid(row=103, column=0)
        cm_fnir = ttk.Combobox(
            self.mainframe,
            textvariable=self.root_cmap_fnir,
            values=self.cmap_combo
        )
        cm_fnir.grid(row=103, column=1)
        cm_fnir.state(['readonly'])
        ttk.Button(
            self.mainframe,
            text = "Apply to loaded files",
            command = self.apply_default_cmaps
        ).grid(row=102, column=2, rowspan=2)

        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5, sticky=tk.W)

        # Scrollable File listing 
        # Make this a canvas to support scrollability for many files.
        self.listcanvas = tk.Canvas(root, background='blue')
        self.listcanvas.grid(row=0, column=1, sticky=tk.N+tk.W+tk.S+tk.E)
        root.columnconfigure(1, weight=1)
        self.listvscroll = ttk.Scrollbar(
            root, 
            orient = tk.VERTICAL,
            command = self.listcanvas.yview,
        )
        self.listvscroll.grid(row=0, column=2, sticky=(tk.N+tk.S))
        self.listframe = ttk.Frame(self.listcanvas, relief = 'ridge')
        self.listframe.grid(row=0, column=1, sticky=tk.N+tk.W)

        # Change scrollable region whenever canvas content changes.
        self.listframe.bind('<Configure>',self.resize_listframe)
        self.listcanvas.create_window(
            (0,0),
            window = self.listframe,
            anchor = "nw",
        )
        self.listcanvas.configure(yscrollcommand=self.listvscroll.set)
        root.bind_all('<MouseWheel>', self.on_mousewheel)
        
        if filenames:
            self.read_files(filenames)

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] [FILE]...",
        description="Analyze SPE files."
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version = f"{parser.prog} version 0.1.0"
    )
    parser.add_argument('files', nargs='*')
    return parser

if __name__ == "__main__":
    parser = init_argparse()
    args = parser.parse_args()
    root = tk.Tk()
    if not args.files:
        SpeAnalyzer(root)
    else:
        SpeAnalyzer(root, args.files)
    root.mainloop()
