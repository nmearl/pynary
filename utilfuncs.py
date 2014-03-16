from __future__ import division, print_function, absolute_import
__author__ = 'nmearl'

import numpy as np
import os
from astropy.io import fits
from utilities.savitzky_golay import savgol_filter
import ftplib

data_retrieve_progress = 0.0


def retrieve_fits(kid):
    if not os.path.exists("./data/{0}".format(kid)):
        os.mkdir("./data/{0}".format(kid))

    dirlist = os.listdir("./data/{0}".format(kid))

    kid = "{0:09d}".format(int(kid))
    kdir = kid[:4]
    server = 'archive.stsci.edu'
    path = '/pub/kepler/lightcurves/'+kdir+'/'+kid+'/'

    print('Retrieving data files for kid{0}...'.format(kid))

    ftp = ftplib.FTP(server)
    ftp.login("anonymous", "ph-getfits")
    ftp.cwd(path)

    flist = ftp.nlst()
    for i in range(len(flist)):
        filename = flist[i]

        global data_retrieve_progress
        data_retrieve_progress = ((i+1.0)/len(flist))

        if filename not in dirlist:
            ftp.retrbinary("RETR " + filename, open("./data/{0}/{1}".format(kid, filename), 'wb').write)

    ftp.quit()

    print('Done!')


def get_fits(kid, useslc=False):
    retrieve_fits(kid)

    listdir = [x for x in os.listdir("./data/{0}".format(kid)) if 'llc' in x]
    listdir = sorted(listdir)

    time, flags, flux, ferr, \
            = np.array([]), np.array([]), np.array([]), np.array([])

    for filename in listdir:
        fit = fits.open("./data/{0}/{1}".format(kid, filename))
        time = np.append(time, fit[1].data["TIME"])
        flags = np.append(flags, fit[1].data["SAP_QUALITY"])

        # Remove median from data
        med = np.median(fit[1].data["PDCSAP_FLUX"])

        flux = np.append(flux, fit[1].data["PDCSAP_FLUX"]/med)
        ferr = np.append(ferr, fit[1].data["PDCSAP_FLUX_ERR"]/med)

    # Remove bad data and adjust time
    # time = time[flags==0]
    # flux = flux[flags==0]
    # ferr = ferr[flags==0]

    time = time[~np.isnan(flux)]
    flags = flags[~np.isnan(flux)]

    ferr = ferr[~np.isnan(flux)]
    flux = flux[~np.isnan(flux)]

    # Redundancy to make sure the arrays are sorted correctly
    flux = flux[np.argsort(time)]
    ferr = ferr[np.argsort(time)]
    time = time[np.argsort(time)]

    time += (2454833.0 - 2455000.0)

    return time, flux, ferr


def mask(flux):
    pass


def nan_helper(y):
    return np.isnan(y), lambda z: z.nonzero()[0]


def detrend(kid, maskfile=''):
    x, y, e = get_fits(kid, './')
    # np.savetxt('stitched_{0}.txt'.format(kid), zip(x,y,e))

    # mask = np.loadtxt(maskfile)
    #
    # newy = np.copy(y)
    # for i in range(len(mask)):
    #     newy[(x > mask[i,0]) & (x < mask[i,1])] = np.nan
    #
    # nans, f = nan_helper(newy)
    # newy[nans] = np.interp(f(nans), f(~nans), newy[~nans])

    s = savgol_filter(y, 71, 4)

    # pylab.plot(x, y-s+1)
    # pylab.show()

    # np.savetxt('detrended_{0}.txt'.format(kid), zip(x, y-s+1, e))

    return y
