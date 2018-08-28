# JMP 08/27/2018

from nilearn import plotting, image, input_data
import numpy as np
from joblib import Parallel, delayed
from io import BytesIO
from PIL import Image
import warnings

warnings.simplefilter("ignore")

def crop_images(plot,img):
    """
    crops slices from nilearn plot
    
    Args:
        plot = nilearn plot object
        img = Byte image of nilearn plot
    
    Returns:
        ims = ditionary of cropped slices
    """
    ims = {}
    for cut in range(len(plot.axes)):
        ix = len(plot.axes)
        plop = plot.axes.popitem()[1]
        extent = plop.ax.get_window_extent()
        i = img.crop((extent.xmin,0,extent.xmax,img.size[1]))
        fh = BytesIO()
        i.save(fh,format='PNG')        
        ims[ix] = fh.getvalue()
        fh.seek(0)
        fh.close()
    return ims

def process_dimensions(image,
                       dim,
                       cutdict,
                       plotfunc,
                       layerfunc = None,
                       layerArgs = {},
                       **kwargs):
    """
    generates all slices for x,y,z dimensions
    
    Args:
        image = 3D nifti nilearn image
        dim = x,y,z
        cutdict = dictionary of cut coordinates
        
    Returns:
        dictionary containing all axes' slices
    """
    
    plotting_funcs = {
        'plot_img': plotting.plot_img,
        'plot_anat': plotting.plot_anat,
        'plot_roi': plotting.plot_roi,
        'plot_stat_map': plotting.plot_stat_map
    }
    
    layerfuncs = {
        'add_contours': plotting.displays.BaseSlicer.add_contours,
        'add_edges' : plotting.displays.BaseSlicer.add_edges,
        'add_overlay': plotting.displays.BaseSlicer.add_overlay
    }
    
    plt = plotting_funcs[plotfunc](image,
                                   display_mode = dim,
                                   cut_coords=cutdict[dim],
                                   **kwargs)
    
    if layerfunc is not None:
        layerfuncs[layerfunc](self=plt,**layerArgs)
    
    plt.close()
    fh = BytesIO()
    plt.savefig(fh)
    data = fh.getvalue()
    fh.seek(0)
    fh.close()
    img = Image.open(BytesIO(data))
    
    return {dim: crop_images(plt,img)}

def generate_all_images(image,step = 1,
                        plotfunc = 'plot_img',
                        layerfunc = None,
                        layerArgs = {},
                        **kwargs):
    
    # generate cut coordinates for xyz axes
    bounds = np.int16([list(dim) for dim in plotting.find_cuts._get_auto_mask_bounds(image)])
    
    cut_coords = {}
    for dim, bound in zip(['x','y','z'],bounds):
        cut_coords[dim] = list(range(bound[0],bound[1],step))
        
    # generate all images quickly
    Images = {}
    for d in Parallel(n_jobs = 3)(delayed(process_dimensions)(image,dim,cut_coords,plotfunc,layerfunc,layerArgs,**kwargs) for dim in cut_coords.keys()):
        Images.update(d)

    return Images
