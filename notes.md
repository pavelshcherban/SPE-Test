## Thoughts
- Rescaling intensity values: https://scikit-image.org/docs/stable/user_guide/data_types.html:
- do you have to factor exposure time into the values?
- shuold be using median filtering? https://www.mathworks.com/help/images/ref/medfilt2.html
- Use tags in tkinter to react to buttons, instead of passing filename?

## Bugs
- Slider for Threshold doesnt always work to update ax_mod, when DRAGGING Slider.
- Mousewheel scrolling may only work on Windows: https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar

## Features
- regional intensities by manual selection
- combining images
- region calculation from intensities
- max point decay over time
- axes values
- statistical significance (p-value)