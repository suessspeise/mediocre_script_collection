'''
hernan
This plots vertical profiles from my torus test
'''

import os
#import cdo as cdo_lib 
#cdo = cdo_lib.Cdo()
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt; plt.rcdefaults()
cmap = plt.cm.viridis
cmap = plt.get_cmap('Greys')

def motivation(verbous=True):
    """
    Returns variables of focus (as stated by Daniel on Mattermost), 
    and (optionally) prints motivation behind these plots and 

    Parameters
    ----------
    verbous : bool
        whether to print the message

    Returns
    -------
    describe : list
        list of str, with shortnames of variables of focus
    """
    if verbous:
        print(
        "Daniel says:\nGenau, erst ein horizontales Mittel zb, wie Rene es beschrieben hat und \
        dann Zeit vs Hoehe (wobei die hoechste Zahl bei den Leveln unten ist). Sinnvolle Variablen \
        waeren Wolkeneis+Wolkenwasser... evtl. noch Niederschlag\n"
        )
        print('Wolkeneis:    cli, long_name: specific cloud ice content')
        print('Wolkenwasser: clw, long_name: specific cloud water content')
        print('Niederschlag: qr,  long_name: specific rain content')
    interest = ['cli', 'clw', 'qr']
    return interest

def get_long_name(key):
    """This is function foo

    Parameters
    ----------
    key : str
        short name of NetCDF variable

    Returns
    -------
    long_name : str
        long name, that matches given short name. if not found returns short name unaltered.
    """
    long_names={
        'cli' : 'specific cloud ice content',
        'clw' : 'specific cloud water content',
        'hus' : 'specific humidity',
        'qr'  : 'specific rain content',
        'qs'  : 'specific snow content',
        'qh'  : 'specific hail content',
        'qg'  : 'specific graupel content'
    }
    long_name = long_names.get(key)

    if long_name:
        return long_name
    else:
        return key

def get_dirlist(implementation, 
                basedir='/work/mh0926/m300872/git/forpy_refactor00/build/experiments/2mom_torus_',
                mask=['.nc', '2mom_torus_', '_3d_'],
                verbous=True,
                sort=True):
    """filters a directory and provides a list of files

    Parameters
    ----------
    implementation : str
        key of used accretion implementation
    basedir : str
        incomplete path, missing the implementation
    mask : list[str]
        elements to be contained in the filename
    verbous : bool
        print out information, default=False
    sort : bool
        return a sorted list, default=True
    Returns
    -------
    directory : str
        complete path
    dirlist_matched : list[str]
        list of filenames in the directory, that fit the mask
    """
    
    directory = basedir + implementation + '/'
    dirlist = os.listdir(path=directory)
    dirlist_matched = [file for file in os.listdir(path=directory) if all(x in file for x in mask)]
    if sort:
        dirlist_matched.sort()
    if verbous:
        print(implementation + ", mask: " , mask , " matches ", len(dirlist_matched), " of ", len(dirlist), " files" )
        
    return directory, dirlist_matched

def plot_vertical_profile(ax, implementation, variable, color=(0.0,0.0,0.0), xlabel=True, verbous=False):
    directory, dirlist = get_dirlist(implementation, verbous=verbous)

    ax.xaxis.tick_top()
    if xlabel:
        ax.set_xlabel(get_long_name(variable))
    ax.set_ylabel('height level')
    ax.invert_yaxis()
    ax.title.set_text(implementation)

    height = (40,70)
    iterator = range(len(dirlist))
#    iterator = range(10) # quicker, for testing
    for i in iterator:
        ifile = directory + dirlist[i]
        d = xr.open_dataset(ifile)
        x = np.asarray(range(*height))
        y = d[variable].mean(dim='ncells').mean(dim='time').values[height[0]:height[1]]
        c = (*color,  float(i)/len(iterator)) # 70 shades of grey
        ax.plot(y,x, color=c, linewidth=1)

def stacked_line_plots(variable):
    fig, axs = plt.subplots(2, 1, sharex=True)
    plot_vertical_profile(axs[0], 'fortran', variable, xlabel=False, color=(1.0,0.0,0.0))
    plot_vertical_profile(axs[1], 'python', variable, color=(0.0,0.0,1.0))

def extract_timestamp(path):
    """extract_timestamp

    Parameters
    ----------
    path : str
        filename of ICON output

    Returns
    -------
    timestamp : str
        just the substring containing the timestamp

    Examples
    --------
    >>> print extract_timestamp('2mom_torus_test_atm_2d_ml_20080801T000200Z')
    000200
    >>> print timestamp2timestring(extract_timestamp('2mom_torus_test_atm_2d_ml_20080801T000200Z'))
    00:02:00
    """
    example_filename = '2mom_torus_test_atm_2d_ml_20080801T000200Z.nc'
    #path = example_filename
    return path.split('_')[-1].split('.')[0].split('T')[-1].split('Z')[0]

def timestamp2timestring(stamp):
    """timestamp2timestring

    Parameters
    ----------
    stamp : str
        a string with 6 integer digits, representing a time (hhmmss)

    Returns
    -------
    timestamp : str
        string (hh:mm:ss)

    Examples
    --------
    >>> print timestamp2timestring(000200)
    00:02:00
    """
    return stamp[:2] + ':' + stamp[2:4] + ':' + stamp[4:]
  
def generate_2d_data(implementation, variable, verbous=True):
    """generate_2d_data

    Parameters
    ----------
    implementation : str
        key for used implementation (e.g. 'fortran', 'python')
    variable : str
        short name of the variable, to be extracted
    verbous : bool
        print iformation on processed data
    Returns
    -------
    array_2d : numpy.ndarray[float]
        2D data set, primary axis being time, secondary is height
    labels : list[str]
        list of timestamps, corresponding to array entries
    """
    # get paths
    directory, dirlist = get_dirlist(implementation, verbous=verbous)
    iterator = range(len(dirlist))
    set_2d = []
    labels = []
    for path in dirlist:
        ifile = directory + path #dirlist[i]
        labels.append(extract_timestamp(path))        
        data = xr.open_dataset(ifile)
        column = data[variable].mean(dim='ncells').mean(dim='time').values
        set_2d.append(column)
    # to see orientation of data in plot:
    #end = np.ones(len(column))
    #set_2d.append(end)
    array_2d = np.asarray(set_2d)
    if verbous:
        print('2d data set:', len(set_2d), 'columns,', len(set_2d[0]), 'elements/colummn')
    return array_2d, labels

def plot_colormap(fig, ax, implementation, variable, zrange=False, xlabel=True, verbous=False, colorbar=False, cmap='magma'):
    """plot_colormap
    
    add a colormap plot to the given ax.
    no return value.

    Parameters
    ----------
    fig : :class: matplotlib.figure.Figure
        figure object to apply colorbar
    ax: :class: atplotlib.axes._subplots.AxesSubplot
        ax object to plot data into
    implementation : str
        key for used implementation (e.g. 'fortran', 'python')
    variable : str
        short name of the variable, to be extracted
    zrange : tuple[float]
        lower and upper limit on z scale, used for colorbar
    xlabel: bool, defaults to True
        display labels on x-axis
    verbous : bool, defaults to False
        print iformation on processed data
    colorbar: bool, defaults to False
        whether colorbar on z-scale is included
    cmap: str, defaults to 'magma'
        used colormap, see https://matplotlib.org/stable/tutorials/colors/colormaps.html
    """
    if implementation == 'diff':
        d1, ticks = generate_2d_data('fortran', variable, verbous=verbous)
        d2, ticks = generate_2d_data('python', variable, verbous=verbous)
        data = abs(d2 - d1)
    else:
        data, ticks = generate_2d_data(implementation, variable, verbous=verbous)
    
    ax.set_ylabel('height level')
    ax.title.set_text(implementation)
    #ax.invert_yaxis() # ax.set_ylim does this job
    ax.set_ylim([70-1,40])
    
    input_dict = { # input data managed before function for schrodingers zrange
        'X'             : data.transpose(),
        'cmap'          : cmap, 
        'interpolation' : 'nearest'}
    if zrange: # if a range is given
        input_dict['vmin']=zrange[0]
        input_dict['vmax']=zrange[1]
    pp = ax.imshow(**input_dict)
    
    if colorbar:
        fig.colorbar(pp,ax=ax)
    if xlabel:
        old_ticks = ax.get_xticks()
        new_ticks=['']
        for i in range(1,len(old_ticks)-1):
            new_ticks.append(timestamp2timestring(ticks[int(old_ticks[i])])[:-3])
        new_ticks.append('')
        ax.set_xticklabels(new_ticks)
        ax.set_xlabel('model time (hh:mm)')
    else:
        ax.set_xticklabels([])
    
def plot_colormap_comparison(variable, colorbar=False, cmap='magma'):
    """plot_colormap
    
    produces a colormap comparison plot for python vs. fortran

    Parameters
    ----------
    variable : str
        short name of the variable, to be extracted
    colorbar: bool, defaults to False
        whether colorbar on z-scale is included
    cmap: str, defaults to 'magma'
        used colormap, see https://matplotlib.org/stable/tutorials/colors/colormaps.html
    """
    fig, axs = plt.subplots(3, 1, sharex=True)
    fig.suptitle('2mom torus test: ' + get_long_name(variable), fontsize=12)
    d1, dummy = generate_2d_data('python', variable)
    d2, dummy = generate_2d_data('fortran', variable)
    #zmax = max(np.maximum(d1), np.maximum(d2))
    print('type(d1)',type(d1), 'd1.shape', d1.shape )
    print('np.max(d1)', np.max(d1), np.max(d2))
    #zrange=(0,zmax)
    zrange=False
    print('zrange', zrange)
    plot_colormap(fig, axs[0], 'fortran', variable, zrange=zrange, colorbar=colorbar, cmap=cmap, xlabel=False)
    plot_colormap(fig, axs[1], 'python',  variable, zrange=zrange, colorbar=colorbar, cmap=cmap, xlabel=False)
    plot_colormap(fig, axs[2], 'diff',    variable, zrange=zrange, colorbar=colorbar, cmap=cmap)

def todo():
    print('additional plot with differences')

# precipitation: qr,qs,qh,qg
# contents: cli, clw, hus
plot_colormap_comparison('qr', cmap='Blues', colorbar=True)
plt.show()
