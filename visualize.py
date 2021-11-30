"""
Visualization module providing utility functions to plot maps
"""
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation
import matplotlib.cm as cm
import numpy as np
import osm_tiles


def get_cmap(df, color_col):
    """Get the normalized colormap based on the maximum value of df

    :param df: Dataframe of values
    :param color_col: Columns from which to plot colors
    :return: Normalized colormap function or None if there is no color_col
    """
    if color_col:
        cmap = cm.rainbow
        norm = Normalize(vmax=df[color_col].max())
        return lambda x: cmap(norm(x))
    return None


def get_subplot_grid_size(nb_groups):
    """Utility function to  compute the best grid size

    :param nb_groups: total number of plots
    :return: dimension of the grid
    """
    diag_size = int(np.sqrt(nb_groups))
    return diag_size, diag_size + 1


def add_tile_rects(df, ax, cmap_norm_func, color_col, discrete=True):
    """Utility function that adds Rectangle artists to an axis based on values in df

    :param df: Dataframe of values
    :param ax: axis of the plot
    :param cmap_norm_func: normalized colormap function
    :param color_col: column from which the color is inferred
    :param discrete: whether to plot discreet colors ('C0', 'C1', ...)
    """
    for r_idx, tile in df.iterrows():
        if discrete:
            color = f'C{int(tile[color_col])}'
        else:
            color = cmap_norm_func(tile[color_col]) if cmap_norm_func else 'b'
        tile_rect = Rectangle((tile.ll_x, tile.ur_y),  # anchor
                              (tile.ur_x - tile.ll_x),  # width
                              (tile.ll_y - tile.ur_y),  # height
                              ec='k',
                              fill=True,
                              fc=color,
                              alpha=0.5
                              )
        ax.add_patch(tile_rect)


def plot_all_tiles_on_map(df, stitched_map, bbox, map_size, color_col=None):
    """Plot all tiles with their color given by color_col on one map

    :param df: Dataframe with tiles info
    :param stitched_map: background map
    :param bbox: bounding box of the map
    :param map_size: number of map tiles in the background map
    :param color_col: column to use for the coloring of the data tiles
    """
    use_discrete = False
    if color_col == 'class':
        use_discrete = True
    cmap_func = get_cmap(df, color_col)
    aspect = osm_tiles.compute_aspect(bbox, map_size)
    fig, ax = plt.subplots(figsize=(15, 15), dpi=100)
    add_tile_rects(df, ax, cmap_func, color_col, discrete=use_discrete)
    ax.imshow(stitched_map, zorder=0, extent=bbox, aspect=aspect)
    plt.show()


def plot_tiles_on_map_by_groups(df, stitched_map, bbox, map_size, group_col=None):
    """Plot tiles on different plots based on the group_col argument

    :param df: Dataframe with tiles info
    :param stitched_map: background map
    :param bbox: bounding box of the map
    :param map_size: number of map tiles in the background map
    :param group_col: column to use for the different plots
    """
    cmap_func = get_cmap(df, group_col)
    aspect = osm_tiles.compute_aspect(bbox, map_size)
    nb_groups = len(df[group_col].unique())
    rows, cols = get_subplot_grid_size(nb_groups)
    fig, axes = plt.subplots(figsize=(15, 12), nrows=rows, ncols=cols, dpi=100)
    for (group, sub_df), ax in zip(df.groupby(group_col), axes.flatten()):
        add_tile_rects(sub_df, ax, cmap_func, group_col)
        ax.imshow(stitched_map, zorder=0, extent=bbox, aspect=aspect)
    for ax in axes.flatten()[nb_groups:]:
        ax.clear()
        ax.remove()
    fig.tight_layout()
    plt.show()

    
def animated_plot(fig, ax, df, stitched_map, bbox, map_size, columns):
    """Create an animated plot based on the columns parameter

    :param fig: figure
    :param ax: axis
    :param df: Dataframe of the values
    :param stitched_map: background map
    :param bbox: bounding box
    :param map_size: map size
    :param columns: column to use for the animation
    :return: animation object
    """
    rects = []

    def init():
        aspect = osm_tiles.compute_aspect(bbox, map_size)
        for r_idx, tile in df.iterrows():
            tile_rect = Rectangle((tile.ll_x, tile.ur_y),  # anchor
                                  (tile.ur_x - tile.ll_x),  # width
                                  (tile.ll_y - tile.ur_y),  # height
                                  fill=True,
                                  fc='b',
                                  alpha=0.5
                                  )
            ax.add_patch(tile_rect)
            rects.append(tile_rect)
        ax.imshow(stitched_map, zorder=0, extent=bbox, aspect=aspect)
        return ax
    
    def anim_func(i):
        cmap_func = get_cmap(df, i)
        ax.set_title(i)
        for idx, r in enumerate(rects):
            r.set(color=cmap_func(df.iloc[idx][i]))

    anim = FuncAnimation(fig,
                         init_func=init,
                         func=anim_func,
                         frames=columns,
                         interval=150)
    fig.tight_layout()
    return anim
