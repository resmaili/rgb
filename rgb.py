# -*- coding: utf-8 -*-
"""
@Description: 
This code will produce true color RGB, dust RGB, and natural RGB; results are saved as a png.
Input datasets can be accessed from NOAA class: www.class.noaa.gov.
Requires ABI channels 1-3, 5, 11, 14, and 15 (depending on which imagery you wish to produce).
    
@author: bekah@umd.edu

project_path = ""
input_path = project_path + "CMIP\\"
output_path = project_path + "results\\"

# Truecolor RGB ------------------------------------------------------------------------------------------------
# Open channels 1-3 from CMIP files
Blue = getRefl(input_path + 'channel1-file.nc', adjustGamma=True)
Red = getRefl(input_path + 'channel2-file.nc',  adjustGamma=True, rebin=True)
Veggie = getRefl(input_path + 'channel3-file.nc', adjustGamma=True)

Green = getGreen(Blue, Red, Veggie)

saveCompositeRGB(output_path + "truecolor_rgb.png", Red, Green, Blue)

del Veggie

# Dust RGB ------------------------------------------------------------------------------------------------
# Uses differencing from channels 11, 14, 15
btC11 = getRefl(input_path + 'channel11-file.nc')
btC14 = getRefl(input_path + 'channel14-file.nc')
btC15 = getRefl(input_path + 'channel15-file.nc')

Red = convert2DustRGB(btC15-btC14, 1.0, (-4.0, 2.0))
Green = convert2DustRGB(btC14-btC11, 2.5, (-4.0, 5.0))
Blue = convert2DustRGB(btC14, 1.0, (261.0, 289.0))

saveCompositeRGB(output_path + "dust_rgb.png", Red, Green, Blue)

del btC11, btC14, btC15

# Natural RGB ------------------------------------------------------------------------------------------------
# Open channels 2,3,5 
reflC02 = getRefl(input_path +'channel2-file', rebin=True)
reflC03 = getRefl(input_path +'channel3-file.nc')
reflC05 = getRefl(input_path +'channel5-file.nc')

Red = convert2NRGB(reflC05)
Green = convert2NRGB(reflC03)
Blue = convert2NRGB(reflC02)

saveCompositeRGB(output_path + "natural_rgb.png", Red, Green, Blue)

del reflC02, reflC03, reflC05

# Helper functions ------------------------------------------------------------------------------------------------
from netCDF4 import Dataset
import matplotlib.image as mpimg
import numpy as np, numpy.ma as ma
from skimage.exposure import adjust_gamma, rescale_intensity
# ------------------------------------------------------------------------------------------------
conus_dims=[3000, 5000]

def getRefl(fname, rebin=False, adjustGamma=False):
    g16nc = Dataset(fname, 'r')
    refl = g16nc.variables['CMI'][:]
    
    if (rebin == True):
        refl = refl[::2, ::2]
        
    if (adjustGamma == True):
        refl = adjust_gamma(refl, 0.5)
        
    return refl

def getGreen(blue, red, veggie):
    return 0.48358168*red + 0.45706946*blue + 0.06038137*veggie

def convert2DustRGB(img, gamma_val, in_range):
    img = rescale_intensity(img, in_range=in_range, out_range=(0, 1))
    if ( img.min() < 0):
        img = img + abs(img.min())
    return adjust_gamma(img, gamma_val)

colorCurve = [ \
    0,  2,  4,  7,  9, 11, 13,   16, 18, 20, 22, 25, 27, 29, 31, 33, 36, 38, 40, 42, \
    44, 47, 49, 51, 53, 55, 57,  60, 62, 64, 66, 68, 70, 72, 74, 77, 79, 81, 83, 85, \
    87, 89, 91, 93, 95, 97, 99, 101,103,105,107,109,111,113,115,117,119,120,122,124, \
    126,128,130,131,133,135,137,138,140,142,144,145,147,149,150,152,153,155,157,158, \
    160,161,163,164,166,167,168,170,171,173,174,175,177,178,179,181,182,183,184,186, \
    187,188,189,190,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207, \
    208,209,210,211,212,213,214,214,215,216,217,218,218,219,220,221,221,222,223,224, \
    224,225,226,226,227,228,228,229,229,230,231,231,232,232,233,233,234,235,235,236, \
    236,237,237,237,238,238,239,239,240,240,240,241,241,242,242,242,243,243,243,244, \
    244,244,245,245,245,246,246,246,246,247,247,247,248,248,248,248,248,249,249,249, \
    249,249,250,250,250,250,250,251,251,251,251,251,251,251,252,252,252,252,252,252, \
    252,252,253,253,253,253,253,253,253,253,253,253,254,254,254,254,254,254,254,254, \
    254,254,254,254,254,254,254,255,255,255,255,255,255,255,255,255 ]

rgb2nrgb = {float(i) : float(colorCurve[i]) for i in range(0,256)}
del colorCurve

def convert2NRGB(a):
    aScaled=rescale_intensity(a, in_range=(0, 1), out_range=(0, 256))
    aNRGB = np.copy(aScaled)
    for key, val in rgb2nrgb.items(): aNRGB[aScaled==key] = val
    aNRGB = rescale_intensity(aNRGB, in_range=(0, 255), out_range=(0, 1))
    return aNRGB

def saveCompositeRGB(fname, Red, Green, Blue):
    Red=ma.filled(Red, fill_value=0)
    Green=ma.filled(Green, fill_value=0)
    Blue=ma.filled(Blue, fill_value=0)
    rgb = np.stack([Red, Green, Blue], axis=2)
    mpimg.imsave(fname, rgb)