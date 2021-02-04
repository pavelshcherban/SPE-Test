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
from skimage import color, filters, util
from skimage.draw import polygon, polygon2mask

from colorplot import colorplot
from pyWinSpec.winspec import SpeFile
from spematplot import spematplot
from WinSpecFrame import WinSpecFrame

# global variables
cmaps = [('Perceptually Uniform Sequential', [
        'viridis', 'plasma', 'inferno', 'magma', 'cividis']),
      ('Sequential', [
        'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
        'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
        'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']),
      ('Sequential (2)', [
        'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
        'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
        'hot', 'afmhot', 'gist_heat', 'copper']),
      ('Diverging', [
        'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
        'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']),
      ('Cyclic', ['twilight', 'twilight_shifted', 'hsv']),
      ('Miscellaneous', [
        'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
        'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
        'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar'])]

class SpeAnalyzer:

  def select_files(self):
    """Allows user to manually select SPE files."""
    filenames = filedialog.askopenfilenames(initialdir=".", title="Select a File", filetypes=(("Text files","*.SPE"), ("all files","*.*")))
    self.read_files(filenames)

  def read_files(self, filenames):
    """Extract SPE files to img array."""
    for filename in filenames:
      self.windows[filename] = {}
      self.files[filename] = {
        'img': SpeFile(filename),
        'threshold': tk.IntVar(),
        'cmap': tk.StringVar(),
        'NIR': "",
        'frame_i': 0,
        "x_i": 0,
        }
      self.files[filename]['threshold'].set(self.label_threshold.get())
      if filename.endswith('bNIR.SPE'):
        self.files[filename]['cmap'].set(self.label_cmap_bnir.get())
        self.files[filename]['NIR'] = 'bright field'
      else:
        self.files[filename]['cmap'].set(self.label_cmap_fnir.get())
        self.files[filename]['NIR'] = 'flourescence'
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
      ttk.Label(details, text="Current threshold: ").grid(row=2, column=0)
      ttk.Label(details, textvariable=f['threshold']).grid(row=2, column=1)
      ttk.Label(details, text="Current colormap: ").grid(row=3, column=0)
      # ttk.Label(details, textvariable=f['cmap']).grid(row=3, column=1)
      cm = ttk.Combobox(details, textvariable=f['cmap'], values=self.cmap_combo)
      cm.grid(row=3, column=1)
      cm.state(['readonly'])
      ttk.Button(details, text="Select from Colorplots", command=lambda f=filename: self.show_colorplots(f)).grid(row=3, column=2)
      
      for child in details.winfo_children():
        child.grid_configure(padx=5, pady=5, sticky=tk.W)

      buttons = ttk.Frame(self.listframe)
      buttons.grid(row=r, column=1)
      ttk.Button(buttons, text="Show Matplot", command=lambda f=filename: self.show_matplot(f)).grid(row=0, column=0)

      for child in buttons.winfo_children():
        child.grid_configure(padx=5, pady=5, sticky=tk.N+tk.W)

      ttk.Separator(self.listframe, orient=tk.HORIZONTAL).grid(row=r+1, column=0, sticky=tk.W+tk.E)

  def show_matplot(self, filename):
    """Displays matplot based on spe file."""
    # first check to see if there are any windows for this file.
    if 'spematplot' in self.windows[filename]:
      self.windows[filename]['spematplot']['toplevel'].lift()
    else:
      self.windows[filename]['spematplot'] = {}
      self.windows[filename]['spematplot']['toplevel'] = tk.Toplevel(root)
      self.windows[filename]['spematplot']['toplevel'].title(filename)
      self.windows[filename]['spematplot']['toplevel'].protocol("WM_DELETE_WINDOW", lambda f=filename: self.destroy_window(f,'spematplot'))

      self.windows[filename]['spematplot']['matplot'] = spematplot(self.files[filename], self.windows[filename]['spematplot'])
  
  def show_colorplots(self, filename):
    """Displays colormap matplots based on spe file."""
    for cmap_category, cmap_list in cmaps:
      # first check to see if there are any windows for this file.
      if cmap_category in self.windows[filename]:
        self.windows[filename][cmap_category]['toplevel'].lift()
      else:
        self.windows[filename][cmap_category] = {}
        self.windows[filename][cmap_category]['toplevel'] = tk.Toplevel(root)
        self.windows[filename][cmap_category]['toplevel'].title(filename +' -- ' + cmap_category)
        self.windows[filename][cmap_category]['toplevel'].protocol("WM_DELETE_WINDOW", lambda f=filename, c=cmap_category: self.destroy_window(f,c))

        self.windows[filename][cmap_category]['matplot'] = colorplot(self.files[filename], self.windows[filename][cmap_category], cmap_list, cmap_category)

  def destroy_window(self, filename, window):
    """Destroys tkinter window."""
    self.windows[filename][window]['toplevel'].destroy()
    del self.windows[filename][window]

  def on_key_press(self, event):
    if event.inaxes:
      print(event.inaxes.get_title())
    # key_press_handler(event, canvas, toolbar)
  
  def output_all_tiff(self):
    for img in self.images:
      filehead, filename = path.split(img.path)
      if filename.endswith('bNIR.SPE'):
        cmap = self.label_cmap_bnir.get()
      else:
        cmap = self.label_cmap_fnir.get()
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
    filters.try_all_threshold(wsf.image_raw(), figsize=(10, 8), verbose=True)
    plt.show()


  def apply_threshold(self):
    thresh_map = {
      'minimum': filters.threshold_minimum,
      'yen': filters.threshold_yen,
    }
    image = self.images[self.image_i].get_frame().image_raw()
    thresh = thresh_map[self.label_threshold.get()](image)
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
    self.label_cmap_bnir = tk.StringVar()
    self.label_cmap_fnir = tk.StringVar()
    self.label_threshold = tk.IntVar()

    self.label_cmap_bnir.set('gray')
    self.label_cmap_fnir.set('gist_earth')
    self.label_threshold.set(0)

    # Root Window Setup
    root.title("SPE File Analyzer")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # Main function frame
    self.mainframe = ttk.Frame(root, padding='5', relief='ridge')
    self.mainframe.grid(row=0, column=0, sticky=tk.N+tk.W)
    # ttk.Separator(self.mainframe, orient=VERTICAL)

    ttk.Button(self.mainframe, text="Select Files", command=self.select_files).grid(row=0, column=0)
    # ttk.Button(self.mainframe, text="Select Fluorescent Colormap",command=self.show_colormaps).grid(row=1, column=0)
    ttk.Label(self.mainframe, textvariable=self.label_cmap_bnir).grid(row=1, column=1)
    ttk.Label(self.mainframe, textvariable=self.label_cmap_fnir).grid(row=1, column=2)
    ttk.Button(self.mainframe, text="Show MatPlots", command=self.show_matplots).grid(row=2, column=0)
    ttk.Button(self.mainframe, text="Output All tiff",command=self.output_all_tiff).grid(row=3, column=0)

    ttk.Button(self.mainframe, text="Unfinished - Plot Thresholds",command=self.show_thresholds).grid(row=100, column=0)
    ttk.Button(self.mainframe, text="Unfinished - Apply Threshold",command=self.apply_threshold).grid(row=101, column=0)
    ttk.Label(self.mainframe, textvariable=self.label_threshold).grid(row=101, column=1)

    for child in self.mainframe.winfo_children():
      child.grid_configure(padx=5, pady=5, sticky=tk.W)

    # File listing frame
    self.listframe = ttk.Frame(root, padding='5', relief='ridge')
    self.listframe.grid(row=0, column=1, sticky=tk.N+tk.W) 

    # self.create_cmap_combo()
    self.cmap_combo = [ cm for group, cms in cmaps for cm in cms ]
    self.cmap_combo.sort()


root = tk.Tk()
SpeAnalyzer(root)
root.mainloop()
