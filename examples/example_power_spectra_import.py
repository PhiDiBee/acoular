from acoular import PowerSpectraImport
from pylab import figure, imshow, colorbar, linspace, diag, zeros, array


from os import path
from acoular import __file__ as bpath, config, MicGeom, WNoiseGenerator, PointSource,\
 Mixer, WriteH5, TimeSamples, PowerSpectra, RectGrid, SteeringVector,\
 BeamformerBase, L_p, BeamformerEig, BeamformerOrth, BeamformerCleansc, \
     UncorrelatedNoiseSource, PowerSpectraImport, ImportGrid
from pylab import figure, plot, axis, imshow, colorbar, show, title, subplot
import numpy as np

# set up the parameters
sfreq = 51200 
blocksize = 128
f = 8000
fftfreq = linspace(0,sfreq/2,int(blocksize/2+1))
micgeofile = path.join(path.split(bpath)[0],'xml','array_64.xml')


# source positions and rms values of three sources
loc1=(-0.1,-0.1,0.3) 
loc2=(0.15,0,0.3) 
loc3=(0,0.1,0.3)
rms=array([1,0.7,0.5])


# generate test data, in real life this would come from an array measurement
mg = MicGeom( from_file=micgeofile )
rg = RectGrid( x_min=-0.2, x_max=0.2, y_min=-0.2, y_max=0.2, z=0.3, \
increment=0.01 )
st = SteeringVector(grid=rg, mics=mg)

# obtain the transfer function
st2 = SteeringVector(
    grid=ImportGrid(gpos_file=array([loc1,loc2,loc3]).T), 
    mics=mg)
H = st2.transfer(f).T # transfer functions for 8000 Hz
H_h = H.transpose().conjugate() # H hermetian
Q = diag(rms)**2 # matrix containing the source strength 

# create full csm
csm = zeros((int(blocksize/2+1),mg.num_mics,mg.num_mics),dtype=complex)
csm[fftfreq.searchsorted(f),:,:] = H@Q.astype(complex)@H_h # calculate csm
ps_import = PowerSpectraImport(csm=csm.copy(), sample_freq=sfreq)

bb = BeamformerBase( freq_data=ps_import, steer=st, r_diag=False, cached=False )
pm = bb.synthetic( f, 0 )
Lm = L_p( pm )

# show map
figure()
imshow( Lm.T, origin='lower', vmin=Lm.max()-10, extent=rg.extend(), \
interpolation='bicubic')
colorbar()
