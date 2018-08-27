import ipywidgets as pw
from IPython.display import display

def find_middle_value(List):
    return list(List)[round(len(List)/2)]

def display_images(images):
    boxlist = []

    y_im = pw.widgets.Image(
        value = images['y'][find_middle_value(images['y'].keys())],
        format = 'png'
    )

    def y(i): y_im.value = images['y'][i['new']]

    y_slider = pw.widgets.SelectionSlider(
        value = find_middle_value(images['y'].keys()),
        options = sorted(list(images['y'].keys())),
        disabled = False,
        continuous_update = True,
        orientation = 'horizontal',
        readout= False
    )

    y_box = pw.VBox([pw.Box(children=[y_im]), pw.Box(children=[y_slider])])
    boxlist.append(y_box)
    y_slider.observe(y,names='value')


    
    x_im = pw.widgets.Image(
        value = images['x'][find_middle_value(images['x'].keys())],
        format = 'png'
    )

    def x(i): x_im.value = images['x'][i['new']]

    x_slider = pw.widgets.SelectionSlider(
        value = find_middle_value(images['x'].keys()),
        options = sorted(list(images['x'].keys())),
        disabled = False,
        continuous_update = True,
        orientation = 'horizontal',
        readout= False
    )

    x_box = pw.VBox([pw.Box(children=[x_im]), pw.Box(children=[x_slider])])
    boxlist.append(x_box)
    x_slider.observe(x,names='value')

    
    
    z_im = pw.widgets.Image(
        value = images['z'][find_middle_value(images['z'].keys())],
        format = 'png'
    )

    def z(i):z_im.value = images['z'][i['new']]

    z_slider = pw.widgets.SelectionSlider(
        value = find_middle_value(images['z'].keys()),
        options = sorted(list(images['z'].keys())),
        disabled = False,
        continuous_update = True,
        orientation = 'horizontal',
        readout= False
    )

    z_box = pw.VBox([pw.Box(children=[z_im]), pw.Box(children=[z_slider])])
    boxlist.append(z_box)
    z_slider.observe(z,names='value')

    
    
    box = pw.VBox([pw.HBox(boxlist)],layout=pw.Layout(height="100%",width="100%"))
    display(box)