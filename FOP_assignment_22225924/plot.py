import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from math import sqrt   # only used for the √3 constant

sqrt3 = np.sqrt(3.0) # pre-compute √3 for hex-grid maths
                        # (hex height  = sqrt(3)/2 × cell-row)

#
# HIVE-VIEW RENDERER
#
def plot_hive(honeyhold, beetlejuices, hexslot, ax, eve=None):
    # 1️  Draw the hive background as an image
    #     extent = align cell *centres* with integer coordinates
    ax.imshow(honeyhold,
              origin='lower',  # row 0 at bottom
              cmap='YlOrBr',   # yellow-orange-brown palette
              vmin=0, vmax=10,  # scale full palette range
              extent=[-0.5, honeyhold.shape[1]-0.5,
                      -0.5, honeyhold.shape[0]-0.5])

    # 2️  Overlay the three comb cells as proper hexagons
    for c in hexslot:
        r, c_ = c.posrawhoney  # grid coords of this comb
        offset = 0.5 * (r % 2)   # every second row indents by 0.5
        poly = patches.RegularPolygon(
            xy=(c_ + offset, r * sqrt3 / 2.0), # centre of hex
            radius=0.45,                  # fit in grid cell
            numVertices=6,
            orientation=np.radians(30),       # flat-top hex
            facecolor=c.hexslotcolour(),     # colour depends on fill level
            edgecolor='darkgoldenrod'
        )
        ax.add_patch(poly)

    # 3️  Bees that are inside the hive
    bx, by = [], []
    for b in beetlejuices:
        if b.alive and b.inhoneyhold: # skip dead or outdoor bees
            bx.append(b.pos[1]) #       x = col
            by.append(b.pos[0])         # y = row
    if bx:
        ax.scatter(bx, by, s=30, marker='o', c='black')

    # 4️  Plot the queen (optional)
    if eve is not None and eve.alive:
        ax.scatter([eve.pos[1]], [eve.pos[0]], marker='*', s=100, c='purple')
    # 5️  Remove tick labels for a cleaner look
    ax.set_xticks([])
    ax.set_yticks([])

#
# plotting the world
#
def plot_world(humanity, beetlejuices, stacies, goatis, ax, entrance):
    """
       Draw the outside world on Axes `ax`.

       Parameters
       ----------
       humanity       : 2-D NumPy array of world tile codes (water, trees, …)
       beetlejuices   : list of Worker objects
       stacies        : list of Flower objects
       goatis         : list of Wasp objects
       ax             : Matplotlib Axes to draw on
       entrance       : (row, col) tuple marking the hive-world doorway
       """
    rows, cols = humanity.shape  # grid size for extents

    # 1️  Background image of the terrain
    ax.imshow(humanity,
              origin='lower',
              cmap='Greens',   # house/pool/tree codes mapped in this palette
              vmin=0, vmax=15,
              extent=[-0.5, cols-0.5, -0.5, rows-0.5])

    # 2️  Flowers (triangle marker, colour chosen by each flower.colour())
    fx, fy, fc = [], [], []
    for fl in stacies:
        fx.append(fl.pos[1])   # x = col
        fy.append(fl.pos[0])     # y = row
        fc.append(fl.colour())   # RGB tuple or CSS colour
    if fx:
        ax.scatter(fx, fy, marker='v', s=40, c=fc)

    # 3️  Bees that are **outside** the hive
    bx, by = [], []
    for b in beetlejuices:
        if b.alive and not b.inhoneyhold:
            bx.append(b.pos[1])
            by.append(b.pos[0])
    if bx:
        ax.scatter(bx, by, marker='o', s=30, c='black')

    # 4️  Wasps (red × markers)
    wx, wy = [], []
    for w in goatis:
        if w.alive:
            wx.append(w.pos[1])
            wy.append(w.pos[0])
    if wx:
        ax.scatter(wx, wy, marker='x', s=50, c='red')

    # 5️  Highlight the hive-world entrance cell (yellow square)
    ax.scatter([entrance[1]], [entrance[0]], marker='s', s=60, c='yellow')

    # 6  Set world bounds and remove ticks

    ax.set_xlim(-0.5, cols-0.5)
    ax.set_ylim(-0.5, rows-0.5)
    ax.set_xticks([])
    ax.set_yticks([])












