#!/usr/bin/env python3
#
# Battenberg of errors
#
from __future__ import division, print_function
import os
import sys
import myokit
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


#
# Check input arguments
#
base = os.path.splitext(os.path.basename(__file__))[0]
args = sys.argv[1:]
if len(args) not in (1, 2):
    print('Syntax: ' + base + ' <cell|combined|all> <variant>')
    sys.exit(1)

if args[0] == 'all':
    cell_list = list(range(1, 10)) + ['combined']
elif args[0] == 'combined':
    cell_list = ['combined']
else:
    cell_list = [int(args[0])]

variant = False
if len(args) == 2:
    variant = args[1] == 'variant'
if variant:
    print('Creating method 1b variant figure')

#
# Run
#
for cell in cell_list:

    # Load rms errors
    d = os.path.join('..', '..', 'validation')
    if cell == 'combined':
        print('Selected combined cells')
        fname = 'rms-errors'
    else:
        print('Selected cell ' + str(cell))
        fname = 'rms-errors-cell-' + str(cell)
    if variant:
        fname += '-with-1b'
    d = myokit.DataLog.load_csv(os.path.join(d, fname + '.csv'))

    fmat = '{:<1.1f}' if cell == 'combined' else '{:<1.2f}'

    cmap = matplotlib.cm.get_cmap('plasma_r')

    targs = {
        'horizontalalignment': 'center',
        'verticalalignment': 'center',
    }

    def row(axes, y, data, std=None):
        colour = np.array(data) - 1
        colour /= 2.2 * np.max(colour)
        for i, e in enumerate(data):
            x = 2 * i
            w, h = 2, 1
            r = plt.Rectangle(
                (x, y), w, h, facecolor=cmap(colour[i]), alpha=0.6)
            ax.add_patch(r)

            text = fmat.format(e).strip()
            if std:
                text += ' (' + fmat.format(std[i]).strip() + ')'
            plt.text(x + w / 2, y + h / 2, text, **targs)

    plt.figure(figsize=(4.6, 2.5))
    plt.subplots_adjust(0.01, 0.01, 0.99, 0.99)

    plt.xlim(-4.2, 8)
    plt.ylim(0, 6)

    ax = plt.subplot(1, 1, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    plt.text(-2.1, 4.5, 'AP validation', **targs)
    plt.text(-2.1, 3.5, 'Method 1 RMSE', **targs)
    plt.text(-2.1, 2.5, 'Cross-validation M2', **targs)
    plt.text(-2.1, 1.5, 'Cross-validation M3', **targs)
    plt.text(-2.1, 0.5, 'Cross-validation M4', **targs)

    plt.text(1, 5.5, 'Method 1b' if variant else 'Method 1', **targs)
    plt.text(3, 5.5, 'Method 2', **targs)
    plt.text(5, 5.5, 'Method 3', **targs)
    plt.text(7, 5.5, 'Method 4', **targs)

    label = 'All cells' if cell == 'combined' else 'Cell ' + str(cell)

    plt.text(-1.75, 5.5, label, {'weight': 'normal', 'size': 14}, **targs)

    if cell == 'combined':
        row(ax, 4, d['rms5_rel'], d['rms5_rel_std'])
        row(ax, 3, d['rms1_rel'], d['rms1_rel_std'])
        row(ax, 2, d['rms2_rel'], d['rms2_rel_std'])
        row(ax, 1, d['rms3_rel'], d['rms3_rel_std'])
        row(ax, 0, d['rms4_rel'], d['rms4_rel_std'])
    else:
        row(ax, 4, d['rms5_rel'])
        row(ax, 3, d['rms1_rel'])
        row(ax, 2, d['rms2_rel'])
        row(ax, 1, d['rms3_rel'])
        row(ax, 0, d['rms4_rel'])

    plt.axhline(5, color='#dddddd')
    plt.axvline(0, color='#dddddd')
    plt.axhline(4, color='#555555')
    plt.axhline(3, color='#555555')

    name = '-combined' if cell == 'combined' else ('-cell-' + str(cell))
    if variant:
        name += '-with-1b'
    plt.savefig(base + name + '.pdf')
    plt.savefig(base + name + '.png')
    plt.close()

#plt.show()
