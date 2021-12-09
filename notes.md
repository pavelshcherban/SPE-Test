## Thoughts
- Rescaling intensity values: https://scikit-image.org/docs/stable/user_guide/data_types.html:
- do you have to factor exposure time into the values?
- shuold be using median filtering? https://www.mathworks.com/help/images/ref/medfilt2.html
- Use tags in tkinter to react to buttons, instead of passing filename?

## Bugs
- Slider for Threshold doesnt always work to update ax_mod, when DRAGGING Slider.
- Mousewheel scrolling may only work on Windows: https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar

## Features
- save chosen datapoints to csv
    - convert absolute time to relative in seconds
    - have to account for date rollover

- regional intensities by manual selection
    - then sum the intensities and presnet csv output over time, like single point selection
- region calculation from intensities
- statistical significance (p-value)
- combining images
- change median filtering with toggle to reduce noise in 'virdis' colormap.
- remove old region when selecting new one.
- consider frame change and affects on Poly components