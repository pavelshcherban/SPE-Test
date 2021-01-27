from speimage import SpeImage
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
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

class SpeProcessor:

  def select_files(self):
      self.filenames = filedialog.askopenfilenames(initialdir=".", title="Select a File", filetypes=(("Text files","*.SPE"), ("all files","*.*")))
      self.read_files()
      self.set_label_filenames()


  def set_label_filenames(self):
      # self.label_filenames.set(self.filenames[0])
      self.label_filenames.set("\n".join(self.filenames))
      # self.label_image = 
      for filename in self.filenames:
        ttk.Radiobutton(self.frame, text=filename, variable=self.label_image, value=filename)


  def show_colormaps(self):
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

    wsf = self.images[self.image_i].get_frame()
    figs = []

    def onclick(event):
      cmap = event.inaxes.get_title()
      print('%s click: inaxes=%s, button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
            ('double' if event.dblclick else 'single', cmap, event.button,
            event.x, event.y, event.xdata, event.ydata))
      self.label_cmap_fnir.set(cmap)
      for fig in figs:
        plt.close(fig)

    def plot_color_gradients(cmap_category, cmap_list):
      nrows = ceil(sqrt(len(cmap_list)))
      fig = plt.figure()
      fig.suptitle(cmap_category + ' colormaps')
      grid = ImageGrid(fig, 111, nrows_ncols=(nrows, nrows), axes_pad=(0.1,0.3))

      for ax, name in zip(grid, cmap_list):
          ax.imshow(wsf.image_raw(), cmap=plt.get_cmap(name))
          ax.set_title(name, fontsize=10)
          ax.set_axis_off()

      cid = fig.canvas.mpl_connect('button_press_event', onclick)
      figs.append(fig)

    for cmap_category, cmap_list in cmaps:
      plot_color_gradients(cmap_category, cmap_list)

    plt.show()


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
      plt.imsave(out_path, img_cm)
    

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

    ax[0].imshow(image, cmap='jet')
    ax[0].set_title('Original image')

    ax[1].imshow(binary, cmap='jet')
    ax[1].set_title('Result')

    for a in ax:
        a.axis('off')

    plt.show()


  def read_files(self):
    self.images = []
    # Extract SPE files to img array
    for filename in self.filenames:
      img = SpeImage(filename)
      self.images.append(img)
      print('File: ', img.path)
      print(' - dtype:', img.get_frame().image_raw().dtype)
      print(' - min:', img.get_frame().min_val())
      print(' - max:', img.get_frame().max_val())
    self.label_image.set(self.filenames[self.image_i])


  def matplot(self):
    def redraw_threshold():
      ax_xgraph.clear()
      ax_xgraph.set_ylim([wsf.min_val(), wsf.max_val()])
      ax_xgraph.plot(wsf.xgraph())
      ax_xgraph.axhline(y=wsf.threshold, linestyle = '-', linewidth=2, color='firebrick')
    
    def redraw_xpixel():
      ax_xpixel.clear()
      ax_xpixel.imshow(wsf.image_raw(), cmap=self.label_cmap_fnir.get())
      ax_xpixel.axhline(y=wsf.x_co, linestyle = '-', linewidth=2, color='firebrick')

    def redraw_mod():
      ax_mod.clear()
      sm = cm.ScalarMappable(cmap=self.label_cmap_fnir.get())
      img = sm.to_rgba(wsf.image_raw_mod())
      ax_mod.imshow(img)
      # ax_mod.imshow(wsf.image_raw(), cmap='jet', clim=(wsf.threshold, wsf.max_val()))

    def update_xpixel(val):
      print("Updating xpixel to ", val)
      wsf.x_co = val
      redraw_threshold()
      redraw_xpixel()

    def update_threshold(val):
      print("Updating threshold to ", val)
      wsf.threshold = val
      redraw_threshold()
      redraw_mod()

    def update_mask():
      print("Updating map to ")
      wsf.mask_poly = np.array((
        (100,100),
        (200,100),
        (200,200),
      ))
      redraw_mod()

    wsf = self.images[self.image_i].get_frame()

    # create initial plot
    fig, (ax_xpixel, ax_xgraph, ax_mod) = plt.subplots(1, 3)
    fig.tight_layout(h_pad=2)

    # plot slider
    spixel = Slider(ax_xpixel, "x pixel", 0, wsf.width()-1, valinit=wsf.x_co, valstep=1, orientation='vertical')
    threshold = Slider(ax_xgraph, "threshold", ceil(wsf.min_val()), floor(wsf.max_val()), valinit=wsf.threshold, valstep=1, orientation='vertical')

    # temporary
    # update_mask()

    redraw_mod()
    redraw_threshold()
    redraw_xpixel()
    
    spixel.on_changed(update_xpixel)
    threshold.on_changed(update_threshold)

    plt.show()


  def __init__(self, root):
    root.title("SPE File Analysis")

    self.mainframe = ttk.Frame(root, padding="3 3 12 12")
    self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # properties
    # self.filenames = ['images\Mouse2_CTXDSPHICG_full_t20h_fNIR.SPE', 'images\Mouse2_CTXDSPHICG_full_t48h_fNIR.SPE', 'images\Mouse2_CTXDSPHICG_full_t96h_fNIR.SPE']
    self.filenames = []
    self.images = []
    self.image_i = 0
    # self.read_files()

    # label variables
    self.label_filenames = StringVar()
    self.set_label_filenames()
    self.label_image = StringVar()
    self.label_cmap_bnir = StringVar()
    self.label_cmap_bnir.set('gray')
    self.label_cmap_fnir = StringVar()
    self.label_cmap_fnir.set('viridis')
    self.label_threshold = StringVar()
    self.label_threshold.set('minimum')

    ttk.Button(self.mainframe, text="Select Files", command=self.select_files).grid(row=1, column=1, sticky=W)
    ttk.Label(self.mainframe, textvariable=self.label_filenames).grid(row=1, column=2, sticky=W)
    ttk.Label(self.mainframe, textvariable=self.label_image).grid(row=1, column=3, sticky=W)
    self.frame = ttk.Frame(self.mainframe).grid(row=1, column=4, sticky=W)
    ttk.Button(self.mainframe, text="Plot Thrsholds",command=self.show_thresholds).grid(row=2, column=1, sticky=W)
    ttk.Button(self.mainframe, text="Apply Threshold",command=self.apply_threshold).grid(row=3, column=1, sticky=W)
    ttk.Label(self.mainframe, textvariable=self.label_threshold).grid(row=3, column=2, sticky=W)
    ttk.Button(self.mainframe, text="Show Colormaps",command=self.show_colormaps).grid(row=4, column=1, sticky=W)
    ttk.Label(self.mainframe, textvariable=self.label_cmap_bnir).grid(row=4, column=2, sticky=W)
    ttk.Label(self.mainframe, textvariable=self.label_cmap_fnir).grid(row=4, column=3, sticky=W)
    ttk.Button(self.mainframe, text="MatPlot", command=self.matplot).grid(row=5, column=1, sticky=W)
    ttk.Button(self.mainframe, text="Output All tiff",command=self.output_all_tiff).grid(row=6, column=1, sticky=W)

    for child in self.mainframe.winfo_children():
      child.grid_configure(padx=5, pady=5)
 

root = Tk()
SpeProcessor(root)
root.mainloop()
