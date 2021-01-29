from spematplot import spematplot
from speimage import SpeImage
from WinSpecFrame import WinSpecFrame

from os import path
from math import sqrt, ceil, floor

import numpy as np

import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.widgets import Slider, Button as mpButton
import matplotlib.image as mpimg
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import button_press_handler
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import ImageGrid

from skimage.draw import polygon, polygon2mask
from skimage import color, util
from skimage import filters

from tkinter import *
from tkinter import filedialog, ttk

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
      self.files[filename] = {
        'img': SpeImage(filename),
        'threshold': IntVar(),
        'cmap': StringVar(),
        'NIR': "",
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
      
      for child in details.winfo_children():
        child.grid_configure(padx=5, pady=5, sticky=W)

      buttons = ttk.Frame(self.listframe)
      buttons.grid(row=r, column=1)
      ttk.Button(buttons, text="Show Matplot", command=lambda f=filename: self.show_matplot(f)).grid(row=0, column=0)

      for child in buttons.winfo_children():
        child.grid_configure(padx=5, pady=5, sticky=N+W)

      ttk.Separator(self.listframe, orient=HORIZONTAL).grid(row=r+1, column=0, sticky=W+E)

  def show_matplot(self, filename):
    """Displays matplot based on spe file."""
    if filename in self.windows:
      self.windows[filename].lift()
    else:
      self.windows[filename] = Toplevel(root)
      self.windows[filename].title(filename)
      self.windows[filename].protocol("WM_DELETE_WINDOW", lambda f=filename: self.destroy_window(f))

      fig = Figure(figsize=(5, 4), dpi=100)
      t = np.arange(0, 3, .01)
      ax = fig.add_subplot(111)
      ax.plot(t, 2 * np.sin(2 * np.pi * t))
      ax.set_title("TAETABDG")

      canvas = FigureCanvasTkAgg(fig, master=self.windows[filename])
      canvas.draw()
      canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

      toolbar = NavigationToolbar2Tk(canvas, self.windows[filename])
      toolbar.update()
      canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

  def destroy_window(self, filename):
    self.windows[filename].destroy()
    del self.windows[filename]

  def show_colormaps(self):

    wsf = self.images[self.image_i].get_frame()
    figs = []

    def onclick(event):
      # fix "AttributeError: 'NoneType' object has no attribute 'get_title'"
      cmap = event.inaxes.get_title()
      print('%s click: inaxes=%s, button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
            ('double' if event.dblclick else 'single', cmap, event.button,
            event.x, event.y, event.xdata, event.ydata))
      self.label_cmap_fnir.set(cmap)
      for fig in figs:
        fig.destroy()

    def plot_color_gradients(cmap_category, cmap_list):
      nrows = ceil(sqrt(len(cmap_list)))
      tl = Toplevel(root)
      fig = Figure()
      fig.suptitle(cmap_category + ' colormaps')
      grid = ImageGrid(fig, 111, nrows_ncols=(nrows, nrows), axes_pad=(0.1,0.3))

      canvas = FigureCanvasTkAgg(fig, master=tl)  # A tk.DrawingArea.
      canvas.draw()
      canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

      toolbar = NavigationToolbar2Tk(canvas, tl)
      toolbar.update()
      canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

      for ax, name in zip(grid, cmap_list):
          ax.imshow(wsf.image_raw(), cmap=plt.get_cmap(name), origin='lower')
          ax.set_title(name, fontsize=10)
          ax.set_axis_off()

      cid = fig.canvas.mpl_connect('button_press_event', onclick)
      figs.append(tl)

    for cmap_category, cmap_list in cmaps:
      plot_color_gradients(cmap_category, cmap_list)


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
    t = Toplevel(root)

  def __init__(self, root):
    # properties
    self.files = {}
    self.windows = {}

    # Root Window label variables
    self.label_filenames = StringVar()
    self.label_cmap_bnir = StringVar()
    self.label_cmap_fnir = StringVar()
    self.label_threshold = IntVar()

    self.label_cmap_bnir.set('gray')
    self.label_cmap_fnir.set('gist_earth')
    self.label_threshold.set(0)

    # Root Window Setup
    root.title("SPE File Analyzer")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # Main function frame
    self.mainframe = ttk.Frame(root, padding='5', relief='ridge')
    self.mainframe.grid(row=0, column=0, sticky=N+W)
    # ttk.Separator(self.mainframe, orient=VERTICAL)

    ttk.Button(self.mainframe, text="Select Files", command=self.select_files).grid(row=0, column=0)
    ttk.Button(self.mainframe, text="Select Fluorescent Colormap",command=self.show_colormaps).grid(row=1, column=0)
    ttk.Label(self.mainframe, textvariable=self.label_cmap_bnir).grid(row=1, column=1)
    ttk.Label(self.mainframe, textvariable=self.label_cmap_fnir).grid(row=1, column=2)
    ttk.Button(self.mainframe, text="Show MatPlots", command=self.show_matplots).grid(row=2, column=0)
    ttk.Button(self.mainframe, text="Output All tiff",command=self.output_all_tiff).grid(row=3, column=0)

    ttk.Button(self.mainframe, text="Unfinished - Plot Thresholds",command=self.show_thresholds).grid(row=100, column=0)
    ttk.Button(self.mainframe, text="Unfinished - Apply Threshold",command=self.apply_threshold).grid(row=101, column=0)
    ttk.Label(self.mainframe, textvariable=self.label_threshold).grid(row=101, column=1)

    for child in self.mainframe.winfo_children():
      child.grid_configure(padx=5, pady=5, sticky=W)

    # File listing frame
    self.listframe = ttk.Frame(root, padding='5', relief='ridge')
    self.listframe.grid(row=0, column=1, sticky=N+W) 

    # self.create_cmap_combo()
    self.cmap_combo = [ cm for group, cms in cmaps for cm in cms ]
    self.cmap_combo.sort()


root = Tk()
SpeAnalyzer(root)
root.mainloop()
