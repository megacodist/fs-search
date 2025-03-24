#
#
#

from megacodist.settings import AppSettings


class FsAppSettings(AppSettings):
    """
    Settings for the fs-search application.
    """
    # App window size & position...
    win_x = 100
    win_y = 100
    win_width = 800
    win_height = 450
    # Columns width...
    item_col_width = 100
    path_col_width = 200
    # Panes width...
    search_pane_width = 180
    results_pane_width = 500
    
    
