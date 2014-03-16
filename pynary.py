from __future__ import division, print_function, absolute_import
__author__ = 'nmearl'

import utilfuncs


def main():
    time, flux, ferr = utilfuncs.get_fits('005897826')
    print(time)

if __name__ == '__main__':
    main()