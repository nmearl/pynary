from __future__ import division, print_function, absolute_import
__author__ = 'nmearl'

import numpy as np
import os
from astropy.io import fits
from utilities.savitzky_golay import savgol_filter
import ftplib
from scipy.signal import lombscargle
import pylab


class DataGetter():

    def __init__(self, kid, use_pdc=False, signal=None):
        self.use_pdc = use_pdc
        self.signal = signal
        self.get_fits(kid)

    def retrieve_fits(self, kid):
        if not os.path.exists("./data"):
            os.mkdir("./data")

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

            if self.signal is not None:
                self.signal.emit(((i+1.0)/len(flist))*100)

            if filename not in dirlist:
                ftp.retrbinary("RETR " + filename, open("./data/{0}/{1}".format(kid, filename), 'wb').write)

        ftp.quit()

        print('Done!')

    def get_fits(self, kid, useslc=False):
        self.retrieve_fits(kid)

        listdir = [x for x in os.listdir("./data/{0}".format(kid)) if 'llc' in x]
        listdir = sorted(listdir)

        time, flags, flux, ferr, \
                = np.array([]), np.array([]), np.array([]), np.array([])

        pre_data = 'PDCSAP' if self.use_pdc else 'SAP'

        for filename in listdir:
            fit = fits.open("./data/{0}/{1}".format(kid, filename))
            time = np.append(time, fit[1].data["TIME"])
            flags = np.append(flags, fit[1].data["SAP_QUALITY"])

            # Remove median from data
            med = np.median(fit[1].data["{0}_FLUX".format(pre_data)])

            flux = np.append(flux, fit[1].data["{0}_FLUX".format(pre_data)]/med)
            ferr = np.append(ferr, fit[1].data["{0}_FLUX_ERR".format(pre_data)]/med)

        # Remove bad data and adjust time
        # time = time[flags==0]
        # flux = flux[flags==0]
        # ferr = ferr[flags==0]

        self.time = time[~np.isnan(flux)]
        self.flags = flags[~np.isnan(flux)]

        self.ferr = ferr[~np.isnan(flux)]
        self.flux = flux[~np.isnan(flux)]

        # Redundancy to make sure the arrays are sorted correctly
        self.flux = flux[np.argsort(time)]
        self.ferr = ferr[np.argsort(time)]
        self.time = time[np.argsort(time)]

        self.time += (2454833.0 - 2455000.0)


def mask(flux):
    pass


def nan_helper(y):
    return np.isnan(y), lambda z: z.nonzero()[0]


def get_period(time, flux):
    scaled_flux = (flux - flux.mean()) / flux.std()

    freqs = np.linspace(0, 100, len(time))[1:]
    power = lombscargle(time, scaled_flux, freqs)

    # Normalize
    # power = np.sqrt(4.0 * power / time.shape[0])

    # Calculate false alarm probability
    # fap = get_fap(freqs, time, power)

    # Get period
    period = 1. / (freqs / 2.0 / np.pi)

    print(period, power)

    return period, power#, fap


def detrend(kid, maskfile=''):
    pass
    # x, y, e = get_fits(kid, './')
    # np.savetxt('stitched_{0}.txt'.format(kid), zip(x,y,e))

    # mask = np.loadtxt(maskfile)
    #
    # newy = np.copy(y)
    # for i in range(len(mask)):
    #     newy[(x > mask[i,0]) & (x < mask[i,1])] = np.nan
    #
    # nans, f = nan_helper(newy)
    # newy[nans] = np.interp(f(nans), f(~nans), newy[~nans])

    # s = savgol_filter(y, 71, 4)

    # pylab.plot(x, y-s+1)
    # pylab.show()

    # np.savetxt('detrended_{0}.txt'.format(kid), zip(x, y-s+1, e))

    # return y


if __name__ == '__main__':
    time, flux, err = np.loadtxt('./data/kid007668648.Q99', unpack=True)
    period, power = get_period(time, flux)

    pylab.plot(period, power)
    pylab.show()