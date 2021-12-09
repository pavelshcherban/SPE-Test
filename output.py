from tkinter import filedialog
from os import path, stat
import time
import matplotlib.pyplot as plt
from matplotlib import cm

from tkinter import filedialog
import tkinter as tk
import csv


class Output:

    HEADERS = ("exp_sec", "date", "ExperimentTimeLocal",
           "ExperimentTimeUTC", "ReadoutTime",)

    @staticmethod
    def output_all_tiff(files, style=None, folder=False):
        base = None
        if folder:
            base = filedialog.askdirectory(
                initialdir=".",
                title="Save All to Folder",
                mustexist=True,
            )
        for filename, file in files.items():
            head, tail = path.split(filename)
            if folder:
                head = base
            name, ext = path.splitext(tail)
            cm = files[filename]['cmap'].get()
            name += '-' + cm
            if style:
                Output.output_tiff(files, filename, head, name, style)
            else:
                Output.output_tiff(files, filename, head, name, 'img')
                Output.output_tiff(files, filename, head, name, 'mod')
            # plt.imsave(out_path, img_cm, origin='lower')

    @staticmethod
    def add_timeext(filename):
        timeext = time.strftime("%Y-%m-%d_%H-%M-%S%z", time.localtime())
        return filename + '_' + timeext

    @staticmethod
    def output_tiff(files, filename, head, name, style):
            # Build image data
            img = files[filename][style]
            zeroes =  None
            if style == 'mod':
                # Store location of 0 values for alpha later.
                zeroes = (img == 0)
            sm = cm.ScalarMappable(cmap=files[filename]['cmap'].get())
            img = sm.to_rgba(img)
            if style == 'mod':
                # Set alpha to 0 for excluded values.
                img[zeroes, 3] = 0

            # Build final file path
            name += '-' + style
            name = Output.add_timeext(name)
            name += '.tiff'
            dest = path.join(head,name)
            print("Outputing ", dest, " ...")
            plt.imsave(
                dest,
                img, 
                origin = 'lower',
            )

    @staticmethod
    def read_headers(files, filename):
        f = files[filename]
        head = {
            'filename':filename,
            'selected_strength':f['sel_strength'].get(),
            'selected_x':f['x_i'].get(),
            'selected_y':f['y_i'].get(),
            }
        header = f['spefile'].header
        for field_name in Output.HEADERS:
            head[field_name] = getattr(header, field_name)
        return head

    @staticmethod
    def get_file_headers(files):
        headers = []
        for filename in files:
                head = Output.read_headers(files, filename)
                headers.append(head)
        return headers

    @staticmethod
    def headers_to_csv(headers, csv_columns):
        csvfile = filedialog.asksaveasfile(
                initialdir=".",
                title="Save As",
                initialfile=Output.add_timeext("speanalyzer-"),
                defaultextension='.csv',
        )
        if not csvfile:
            return
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns, lineterminator='\n')
        writer.writeheader()
        for data in headers:
            writer.writerow(data)
        csvfile.close()
    
    @staticmethod
    def get_csv_columns():
        csv_columns = ['filename','selected_strength','selected_x','selected_y']
        for field_name in Output.HEADERS:
            csv_columns.append(field_name)
        return csv_columns

    @staticmethod
    def clean_headers(headers):
        for head in headers:
            head["date"] = head["date"].decode('UTF-8')
            etl = head["ExperimentTimeLocal"].decode('UTF-8')
            head["ExperimentTimeLocal"] = etl[:2]+':'+etl[2:4]+':'+etl[4:]
            etu = head["ExperimentTimeUTC"].decode('UTF-8')
            head["ExperimentTimeUTC"] = etu[:2]+':'+etu[2:4]+':'+etu[4:]

    @staticmethod
    def output_csv(files):
        headers = Output.get_file_headers(files)
        Output.clean_headers(headers)
        csv_columns = Output.get_csv_columns()
        Output.headers_to_csv(headers, csv_columns)
