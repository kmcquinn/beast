#!/usr/bin/env python
"""
Code to test if the BEAST output files are the same between to runs
KDG - 28 Dec 2016
"""

from __future__ import print_function, division
import os.path
import h5py
import numpy as np
import astropy.io.fits as fits

class hdf5diff_results():
    def __init__(self):
        self.identical = None
        self.missing_groups = []
        self.missing_datasets = []
        self.nonzero_matchs = []
        self.missing_names = []

    def add_missing_group(self, mkey):
        self.missing_groups.append(mkey)

    def add_missing_dataset(self, mkey, mdataset):
        self.missing_datasets.append(mkey+'_'+mdataset)

    def add_nonzero_match(self, desc):
        self.nonzero_matchs.append(desc)

    def add_missing_name(self, desc):
        self.missing_names.append(desc)
        
def hdf5diff(fname1, fname2):

    hdfa = h5py.File(fname1, 'r')
    hdfb = h5py.File(fname2, 'r')

    hd = hdf5diff_results()
    for sname in hdfa.keys():
        if sname not in hdfb.keys():
            hd.add_missing_group(sname)
        else:
            is_dataset = isinstance(hdfa[sname], h5py.Dataset)
            if is_dataset:
                cvalue = hdfa[sname]
                cvalueb = hdfb[sname]
                all_names = hdfa[sname].dtype.names
                all_namesb = hdfb[sname].dtype.names
                if all_names == None:
                    if hdfa[sname].dtype.isbuiltin:
                        if np.sum(hdfa[sname].value - hdfb[sname].value) != 0:
                            hd.add_nonzero_match(sname)
                else:
                    for cname in all_names:
                        if cname in all_namesb:
                            if np.sum(hdfa[sname][cname]
                                      - hdfb[sname][cname]) != 0:
                                hd.add_nonzero_match(sname+'/'+cname)
                                print(hdfa[sname][cname])
                                print(hdfb[sname][cname])
                        else:
                            hd.add_missing_name(sname+'/'+cname)
            else:
                for cname, cvalue in hdfa[sname].items():
                    if cname not in hdfb[sname].keys():
                        hd.add_missing_dataset(sname,cname)
                    else:
                        cvalueb = hdfb[sname][cname]
                        if np.sum(cvalue.value - cvalueb.value) > 0:
                            hd.add_nonzero_match(sname+'_'+cname)
                    
    if (len(hd.missing_groups)
        + len(hd.missing_datasets)
        + len(hd.nonzero_matchs)
        + len(hd.missing_names)) > 0:
        hd.identical = False
    else:
        hd.identical = True

    return hd
    
if __name__ == '__main__':

    basename = 'beast_example_phat'

    # check the FITS files
    fits_files = ['stats','pdf1d']
    for cfile in fits_files:
        file1 = basename+'/'+basename+'_'+cfile+'.fits'
        if os.path.isfile(file1):
            fd = fits.FITSDiff(file1,
                               basename+'_good/'+basename+'_'+cfile+'.fits')
            print(cfile, fd.identical)
        else:
            print(cfile, 'does not exist, not checking')
      
    # check the HDF5 files
    hdf5_files = ['lnp','seds.grid','seds_trim.grid',
                  'noisemodel','noisemodel_trim.grid']
    for cfile in hdf5_files:
        file1 = basename+'/'+basename+'_'+cfile+'.hd5'
        if os.path.isfile(file1):
            hd = hdf5diff(file1,
                          basename+'_good/'+basename+'_'+cfile+'.hd5')
            print(cfile, hd.identical)
            if not hd.identical:
                if len(hd.missing_groups) > 0:
                    print('missing groups')
                    print(hd.missing_groups)
                if len(hd.missing_datasets) > 0:
                    print('missing datasets')
                    print(hd.missing_datasets)
                if len(hd.nonzero_matchs) > 0:
                    print('nonzero matchs')
                    print(hd.nonzero_matchs)
                if len(hd.missing_names) > 0:
                    print('missing names in a dataset')
                    print(hd.missing_names)
        else:
            print(cfile, 'does not exist, not checking')
