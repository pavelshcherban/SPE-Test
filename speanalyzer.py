import tkinter as tk
from os import path
from tkinter import filedialog, ttk

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.backend_bases import button_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure
from matplotlib.widgets import Button as mpButton
from matplotlib.widgets import Slider
from mpl_toolkits.axes_grid1 import ImageGrid
from scipy import ndimage
from skimage import color, filters, util
from skimage.draw import polygon, polygon2mask

from colorplot import colorplot
from pyWinSpec.winspec import SpeFile
from spematplot import spematplot
from WinSpecFrame import WinSpecFrame

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

    def select_files(self):
        """Allows user to manually select SPE files."""
        filenames = filedialog.askopenfilenames(
            initialdir=".",
            title="Select a File",
            filetypes=(("Text files", "*.SPE"), ("all files", "*.*"))
        )
        self.read_files(filenames)

    def read_files(self, filenames):
        """Extract SPE files to spe object."""
        for filename in filenames:
            spefile = SpeFile(filename)
            frame_i = 0
            img = SpeAnalyzer.process_image(spefile, frame_i)
            # xgrpah = img[45]
            # xtest = np.full((256,), 45)
            threshold_poly = np.zeros_like(img)
            threshold = tk.IntVar()
            threshold.set(self.root_threshold.get())
            cmap = tk.StringVar()
            if filename.endswith('bNIR.SPE'):
                cmap.set(self.root_cmap_bnir.get())
                nir = 'bright field'
            else:
                cmap.set(self.root_cmap_fnir.get())
                nir = 'flourescence'
            # Update instance dicts.
            self.windows[filename] = {}
            self.files[filename] = {
                'spefile': spefile,
                'img': img,
                'threshold': threshold,
                'threshold_poly': threshold_poly,
                'cmap': cmap,
                'NIR': nir,
                'frame_i': frame_i,
                "x_i": 0,
            }
        self.create_listframe()

    def create_listframe(self):
        """Creates tk Frame for currently selected SPE files."""
        for ind, (filename, f) in enumerate(self.files.items()):
            r = 2*ind
            details = ttk.Frame(self.listframe)
            details.grid(row=r, column=0)
            ttk.Label(details, text="File: ").grid(row=0, column=0)
            ttk.Label(details, text=filename).grid(row=0, column=1)
            ttk.Label(details, text="SPE type: ").grid(row=1, column=0)
            ttk.Label(details, text=f['NIR']).grid(row=1, column=1)
            ttk.Label(details, text="Current threshold: ").grid(
                row=2, column=0)
            ttk.Label(details, textvariable=f['threshold']).grid(
                row=2, column=1)
            ttk.Label(details, text="Current colormap: ").grid(row=3, column=0)
            # ttk.Label(details, textvariable=f['cmap']).grid(row=3, column=1)
            cm = ttk.Combobox(
                details,
                textvariable=f['cmap'],
                values=self.cmap_combo
            )
            cm.grid(row=3, column=1)
            cm.state(['readonly'])
            button_color = ttk.Button(
                details,
                text="Select from Colorplots",
                command=lambda f=filename: self.show_colorplots(f),
            )
            button_color.grid(row=3, column=2)

            for child in details.winfo_children():
                child.grid_configure(padx=5, pady=5, sticky=tk.W)

            buttons = ttk.Frame(self.listframe)
            buttons.grid(row=r, column=1)
            button_matplot = ttk.Button(
                buttons,
                text="Show Matplot",
                command=lambda f=filename: self.show_matplot(f),
            )
            button_matplot.grid(row=0, column=0)

            for child in buttons.winfo_children():
                child.grid_configure(padx=5, pady=5, sticky=tk.N+tk.W)

            sep = ttk.Separator(self.listframe, orient=tk.HORIZONTAL)
            sep.grid(row=r+1, column=0, sticky=tk.W+tk.E)

    def matplot_press(self, event, filename):
        """Registers the selection of a polygon in Matplot"""
        matplot = self.windows[filename]['spematplot']['matplot']
        if event.inaxes is matplot.ax_mod:
            cmap = event.inaxes.get_title()
            # print('inaxes=%s' %(cmap))
            print(vars(event))
        # {'button': <MouseButton.LEFT: 1>, 'key': None, 'step': 0, 'dblclick': False, 'name': 'button_press_event', 'canvas': <matplotlib.backends.backend_tkagg.FigureCanvasTkAgg object at 0x000001E2AF80CA60>, 'guiEvent': <ButtonPress event num=1 x=488 y=220>, 'x': 488, 'y': 260, 'inaxes': <AxesSubplot:>, 'xdata': 101.07419354838692, 'ydata': 198.8083870967742}

    def matplot_motion(self, event, filename):
        """Registers the selection of a polygon in Matplot"""
        matplot = self.windows[filename]['spematplot']['matplot']
        if event.inaxes is matplot.ax_mod:
            y = int(event.ydata)
            x = int(event.xdata)
            self.files[filename]['threshold_poly'][y][x] = 1
            # self.threshold_poly = np.fliplr(self.file['threshold_poly'])
            # matplot.draw_threshold_poly()
            print(vars(event))
        # {'button': None, 'key': None, 'step': 0, 'dblclick': False, 'name': 'motion_notify_event', 'canvas': <matplotlib.backends.backend_tkagg.FigureCanvasTkAgg object at 0x000001E2AF80CA60>, 'guiEvent': <Motion event x=488 y=220>, 'x': 488, 'y': 260, 'inaxes': <AxesSubplot:>, 'xdata': 101.07419354838692, 'ydata': 198.8083870967742}

    def update_frame_next(self, filename):
        """Updates the frame selection for the file to the next frame."""
        f = self.files[filename]
        if f['frame_i'] + 1 < f['spefile'].header.NumFrames:
            f['frame_i'] += 1
            print("Updating to next frame", f['frame_i'])
            img = SpeAnalyzer.process_image(f['spefile'], f['frame_i'])
            f['img'] = img
            self.windows[filename]['spematplot']['matplot'].update()
        else:
            print("Last frame already selected.")

    def update_frame_prev(self, filename):
        """Updates the frame selection for the file to the previous frame."""
        f = self.files[filename]
        if f['frame_i'] > 0:
            f['frame_i'] -= 1
            print("Updating to prev frame", f['frame_i'])
            img = SpeAnalyzer.process_image(f['spefile'], f['frame_i'])
            f['img'] = img
            self.windows[filename]['spematplot']['matplot'].update()
        else:
            print("First frame already selected.")

    def update_x_i(self, val, filename):
        f = self.files[filename]
        print("Updating x_i to ", val)
        f['x_i'] = val
        self.windows[filename]['spematplot']['matplot'].update()

    def update_threshold(self, val, filename):
        f = self.files[filename]
        print("Updating threshold to ", val)
        f['threshold'].set(val)
        self.windows[filename]['spematplot']['matplot'].update()

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
                lambda w=window: self.destroy_window(w)
            )
            self.windows[filename]['spematplot'] = window
            # Create Matplot and connect to backend.
            matplot = spematplot(
                self.files[filename],
                self.windows[filename]['spematplot']
            )
            matplot.b_nframe.on_clicked(
                lambda e, f=filename: self.update_frame_next(f)
            )
            matplot.b_pframe.on_clicked(
                lambda e, f=filename: self.update_frame_prev(f)
            )
            matplot.x_i.on_changed(
                lambda v, f=filename: self.update_x_i(v, f)
            )
            matplot.threshold.on_changed(
                lambda v, f=filename: self.update_threshold(v, f)
            )
            # matplot.canvas.mpl_connect('button_press_event', lambda event: self.canvas._tkcanvas.focus_set())
            matplot.canvas.mpl_connect(
                "button_press_event",
                lambda e, f=filename: self.matplot_press(e, f)
            )
            matplot.canvas.mpl_connect(
                "motion_notify_event",
                lambda e, f=filename: self.matplot_motion(e, f)
            )
            self.windows[filename]['spematplot']['matplot'] = matplot

    def show_colorplots(self, filename):
        """Displays colormap matplots based on spe file."""
        for cmap_category, cmap_list in CMAPS:
            # first check to see if there are any windows for this file.
            if cmap_category in self.windows[filename]:
                self.windows[filename][cmap_category]['toplevel'].lift()
            else:
                self.windows[filename][cmap_category] = {}
                self.windows[filename][cmap_category]['toplevel'] = tk.Toplevel(
                    root)
                self.windows[filename][cmap_category]['toplevel'].title(
                    filename + ' -- ' + cmap_category)
                self.windows[filename][cmap_category]['toplevel'].protocol(
                    "WM_DELETE_WINDOW", lambda f=filename, c=cmap_category: self.destroy_window(f, c))

                self.windows[filename][cmap_category]['matplot'] = colorplot(
                    self.files[filename], self.windows[filename][cmap_category], cmap_list, cmap_category)

    def destroy_window(self, window):
        """Destroys tkinter window."""
        window['toplevel'].destroy()
        del window

    def on_key_press(self, event):
        if event.inaxes:
            print(event.inaxes.get_title())
        # key_press_handler(event, canvas, toolbar)

    def output_all_tiff(self):
        for img in self.images:
            filehead, filename = path.split(img.path)
            if filename.endswith('bNIR.SPE'):
                cmap = self.root_cmap_bnir.get()
            else:
                cmap = self.root_cmap_fnir.get()
            out_path = path.splitext(img.path)[0] + '-' + cmap + '.tiff'
            sm = cm.ScalarMappable(cmap=cmap)
            img_cm = sm.to_rgba(img.get_frame().image_raw_mod())
            print("Outputing ", out_path, " ...")
            plt.imsave(out_path, img_cm, origin='lower')

    def output_comb_tiff(self):
        return

    def output_combalph_tiff(self):
        return

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
        # for mp in self.matplots:
        #   mp.show()
        t = tk.Toplevel(root)

    def __init__(self, root):
        # properties
        self.files = {}
        self.windows = {}

        # Root Window label variables
        self.label_filenames = tk.StringVar()
        self.root_cmap_bnir = tk.StringVar()
        self.root_cmap_fnir = tk.StringVar()
        self.root_threshold = tk.IntVar()

        self.root_cmap_bnir.set('gray')
        self.root_cmap_fnir.set('gist_earth')
        self.root_threshold.set(0)

        # Root Window Setup
        root.title("SPE File Analyzer")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Main function frame
        self.mainframe = ttk.Frame(root, padding='5', relief='ridge')
        self.mainframe.grid(row=0, column=0, sticky=tk.N+tk.W)
        # ttk.Separator(self.mainframe, orient=VERTICAL)

        ttk.Button(
            self.mainframe,
            text="Select Files",
            command=self.select_files
        ).grid(row=0, column=0)
        # ttk.Button(self.mainframe, text="Select Fluorescent Colormap",command=self.show_colormaps).grid(row=1, column=0)
        ttk.Label(
            self.mainframe,
            textvariable=self.root_cmap_bnir
        ).grid(row=1, column=1)
        ttk.Label(
            self.mainframe,
            textvariable=self.root_cmap_fnir
        ).grid(row=1, column=2)
        ttk.Button(
            self.mainframe,
            text="Show MatPlots",
            command=self.show_matplots
        ).grid(row=2, column=0)
        ttk.Button(
            self.mainframe,
            text="Output All tiff",
            command=self.output_all_tiff
        ).grid(row=3, column=0)
        ttk.Button(
            self.mainframe,
            text="Unfinished - Plot Thresholds",
            command=self.show_thresholds
        ).grid(row=100, column=0)
        ttk.Button(
            self.mainframe,
            text="Unfinished - Apply Threshold",
            command=self.apply_threshold
        ).grid(row=101, column=0)
        ttk.Label(
            self.mainframe,
            textvariable=self.root_threshold
        ).grid(row=101, column=1)

        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5, sticky=tk.W)

        # File listing frame
        self.listframe = ttk.Frame(root, padding='5', relief='ridge')
        self.listframe.grid(row=0, column=1, sticky=tk.N+tk.W)

        # self.create_cmap_combo()
        self.cmap_combo = [cm for group, cms in CMAPS for cm in cms]
        self.cmap_combo.sort()


root = tk.Tk()
SpeAnalyzer(root)
root.mainloop()
