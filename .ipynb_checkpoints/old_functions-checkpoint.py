from nilearn import plotting
from nilearn.image import load_img, resample_to_img, mean_img
import numpy as np

from joblib import Parallel, delayed
from PIL import Image
from io import BytesIO

%matplotlib inline
import ipywidgets as widgets
from ipywidgets import VBox,HBox,Box,Layout,Label
from IPython.display import display

def log_progress(sequence, every=None, size=None, name='Items'):
    from ipywidgets import IntProgress, HTML, VBox
    from IPython.display import display

    is_iterator = False
    if size is None:
        try:
            size = len(sequence)
        except TypeError:
            is_iterator = True
    if size is not None:
        if every is None:
            if size <= 200:
                every = 1
            else:
                every = int(size / 200)     # every 0.5%
    else:
        assert every is not None, 'sequence is iterator, set every'

    if is_iterator:
        progress = IntProgress(min=0, max=1, value=1)
        progress.bar_style = 'info'
    else:
        progress = IntProgress(min=0, max=size, value=0)
    label = HTML()
    box = VBox(children=[label, progress])
    display(box)

    index = 0
    try:
        for index, record in enumerate(sequence, 1):
            if index == 1 or index % every == 0:
                if is_iterator:
                    label.value = '{name}: {index} / ?'.format(
                        name=name,
                        index=index
                    )
                else:
                    progress.value = index
                    label.value = u'{name}: {index} / {size}'.format(
                        name=name,
                        index=index,
                        size=size
                    )
            yield record
    except:
        progress.bar_style = 'danger'
        raise
    else:
        progress.bar_style = 'success'
        progress.value = index
        label.value = "{name}: {index}".format(
            name=name,
            index=str(index or '?')
        )
        
def slice_image(Plot):
    fh = BytesIO()
    plop = Plot.axes.popitem()[1]
    extent = plop.ax.get_window_extent().transformed(plop.ax.axes.figure.dpi_scale_trans.inverted())
    plop.ax.figure.savefig(fh, bbox_inches=extent)
    data = fh.getvalue()
    fh.seek(0)
    fh.close()
    return data


def find_middle_value(List):
    return list(List)[round(len(List)/2)]

def display_images(data_name,
                  dimensions = {
                           "x_dim":(300,350),
                           "y_dim":(275,350),
                           "z_dim":(275,350)
                  }):
    """
    Displays saved nilearn data object
    
    Args:
        data_name = file name for data object
        dimensions = size of widget Boxes
    """
    images = data_name

    boxlist = []  # for displaying widgets
    layout = Layout(height="300px",width='300px')

    if "y" in images.keys():
        y_im = widgets.Image(
            value = images['y'][find_middle_value(images['y'].keys())],
            format='png',
            layout=layout
        )

        def y(i): y_im.value = images['y'][i['new']]

        y_slider = widgets.SelectionSlider(
            value = find_middle_value(images['y'].keys()),
            options = sorted(list(images['y'].keys())),
            disabled = False,
            continuous_update = True,
            orientation="horizontal",
            readout=False)


        y_box = VBox([Box(children=[y_im]), Box(children=[y_slider])])
        boxlist.append(y_box)
        y_slider.observe(y,names='value')
        
    
    if "x" in images.keys():
        x_im = widgets.Image(
            value = images['x'][find_middle_value(images['x'].keys())],
            format='png',
            layout=layout
        )

        def x(i): x_im.value = images['x'][i['new']]

        x_slider = widgets.SelectionSlider(
            value = find_middle_value(images['x'].keys()),
            options = sorted(list(images['x'].keys())),
            disabled = False,
            continuous_update = True,
            orientation="horizontal",
            readout=False)


        x_box = VBox([Box(children=[x_im]), Box(children=[x_slider])])
        boxlist.append(x_box)
        x_slider.observe(x,names='value')

    
    if "z" in images.keys():
        z_im = widgets.Image(
            value = images['z'][find_middle_value(images['z'].keys())],
            format='png',
            layout=layout
        )

        def z(i): z_im.value = images['z'][i['new']]

        z_slider = widgets.SelectionSlider(
            value = find_middle_value(images['z'].keys()),
            options = sorted(list(images['z'].keys())),
            disabled = False,
            continuous_update = True,
            orientation="horizontal",
            readout=False)


        z_box = VBox([Box(children=[z_im]), Box(children=[z_slider])])
        boxlist.append(z_box)
        z_slider.observe(z,names='value')
        
    
    box = VBox([HBox(boxlist)],layout=Layout(height="100%",width="100%"))
    display(box)
    

def ProcessImage(image,_dim,
                 step,
                _plot_func,
                _plot_args,
                _layer_func,
                _layer_args):
    
    layer_methods = {"add_contours":plotting.displays.BaseSlicer.add_contours,
                    "add_edges":plotting.displays.BaseSlicer.add_edges,
                    "add_overlay":plotting.displays.BaseSlicer.add_overlay}
    
    if type(image) is str:
        image = load_img(image)

    bounds = np.int16([list(_) for _ in plotting.find_cuts._get_auto_mask_bounds(image)])
    cut_coords = {}
    
    # make a preplot to extract a colorabr if there is one
    
    for dim, vals in zip(['x','y','z'], bounds):
        cut_coords[dim] = list(range(vals[0],vals[1],step))
    ims = {}
    
    if _plot_func.__name__ == "plot_stat_map":
        if "threshold" in _plot_args.keys():
            th = _plot_args['threshold']
        else:
            th = 'auto'

    
    for dim in list(_dim):
        print("Generating {} cuts".format(dim))
        plot = _plot_func(image,display_mode = dim,
                  cut_coords = cut_coords[dim],colorbar=False,**_plot_args)
        if _layer_func is not None:
            if not np.array_equal(_layer_args['img'].shape,image):
                _layer_args['img'] = resample_to_img(_layer_args['img'],image)
            
            layer_func = layer_methods[_layer_func]
            layer_func(plot,**_layer_args)
        
        plot.close()
        ims[dim] = {}
        for cut in log_progress(range(len(plot.axes))):
            ims[dim][cut] = slice_image(plot)
    display_images(ims)