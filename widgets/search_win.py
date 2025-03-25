#
# 
#

import logging
import tkinter as tk
from tkinter import ttk

from pathlib import Path
from queue import Queue, Empty
import threading
import platform
import subprocess

from megacodist.fs import (
    FsSearchOptions, FsSearchLocation, FsSearchMatch, IFsSearchable)

from utils.settings import FsAppSettings
from widgets.results_view import ResultsView
from widgets.search_box import SearchBox, SearchTerms


class SearchWin(tk.Tk):
    def __init__(
            self,
            settings: FsAppSettings,
            searchers: dict[str, type[IFsSearchable]]):
        super().__init__()
        # Setting window properties...
        self.title("Megacodist FS Search")
        self.geometry(f"{settings.win_width}x{settings.win_height}"
            f"+{settings.win_x}+{settings.win_y}")
        self.resizable(True, True)
        # Declaring variables...
        self._settings = settings
        """The application settings object."""
        self._searchers = searchers
        """
        The mapping between FS searcher names and their class objects:
        `FS searcher names => FS searcher types`
        """
        self._searcher: IFsSearchable | None = None
        """The FS searcher which is currently using."""
        self._q: Queue[FsSearchLocation | FsSearchMatch]
        """The BFS search object."""
        self._searchThread: threading.Thread | None = None
        self._INTVL_AFTER = 150
        self._afterId_search: str | None = None
        self._afterId_stop: str | None = None
        # Creating GUI...
        self._initGui()
        self.update()
        self._pwin.sashpos(0, self._settings.search_pane_width)
        self._pwin.sashpos(1, self._settings.results_pane_width)
        self.update_idletasks()
        # Binding event handlers...
        self.protocol("WM_DELETE_WINDOW", self._onWinClosing)

    def _initGui(self) -> None:
        # Main PanedWindow
        self._pwin = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self._pwin.pack(fill="both", expand=True)
        # Left Pane (Search Options)
        #self._frm_searchOptions = ttk.Frame(self._pwin)
        # Search Box
        self._searchbx = SearchBox(
            self._pwin,
            list(self._searchers.keys()),
            self._startSearch,
            self._stopSearch)
        self._searchbx.pack(fill=tk.BOTH, expand=True)
        self._pwin.add(self._searchbx, weight=1)
        # Middle Pane (Results)
        self._frm_middle = ttk.Frame(self._pwin)
        self._pwin.add(self._frm_middle, weight=3)  # Allow resizing
        # Right Pane (Empty for now)
        self._frm_right = ttk.Frame(self._pwin)
        self._pwin.add(self._frm_right, weight=3)  # Allow resizing
        # Results View
        self._resvw = ResultsView(self._frm_middle, self._revealInExplorer)
        self._resvw.setColumnsSize(
            self._settings.item_col_width,
            self._settings.path_col_width)
        self._resvw.pack(fill="both", expand=True)
        # Status bar
        self._frm_statusBar = ttk.Frame(self)
        self._frm_statusBar.columnconfigure(0, weight=1)
        self._frm_statusBar.pack(fill="x", side="bottom")
        # Status label
        self._lbl_status = ttk.Label(
            self._frm_statusBar,
            text="Ready",
            relief="sunken",
            anchor="w",
            justify="left",
            padding=5,
        )
        self._lbl_status.grid(row=0, column=0, sticky="ew")
    
    def _onWinClosing(self) -> None:
        # Releasing images...
        #
        self._saveGeometry()
        # Saving panes widths...
        self._settings.path_col_width = self._pwin.sashpos(0)
        self._settings.results_pane_width = self._pwin.sashpos(1)
        # Saving columns widths...
        colsWidths = self._resvw.getColumnsSize()
        self._settings.item_col_width = colsWidths[0]
        self._settings.path_col_width = colsWidths[1]
        # Destroying the window...
        self.destroy()
    
    def _saveGeometry(self) -> None:
        """Saves the geometry of the window to the app settings object."""
        import re
        w_h_x_y = self.winfo_geometry()
        GEOMETRY_REGEX = r"""
            (?P<width>\d+)    # The width of the window
            x(?P<height>\d+)  # The height of the window
            \+(?P<x>\d+)      # The x-coordinate of the window
            \+(?P<y>\d+)      # The y-coordinate of the window"""
        match = re.search(
            GEOMETRY_REGEX,
            w_h_x_y,
            re.VERBOSE)
        if match:
            self._settings.win_width = int(match.group('width'))
            self._settings.win_height = int(match.group('height'))
            self._settings.win_x = int(match.group('x'))
            self._settings.win_y = int(match.group('y'))
        else:
            logging.error(
                'Cannot get the geometry of the window.',
                stack_info=True)


    def _clearResultsVw(self) -> None:
        self._resvw.clear()

    def _termsToOptions(self, terms: SearchTerms) -> FsSearchOptions:
        """Converts the search terms to a search options object."""
        options = FsSearchOptions.NONE
        if terms.matchCase:
            options |= FsSearchOptions.MATCH_CASE
        if terms.matchWhole:
            options |= FsSearchOptions.MATCH_WHOLE
        if terms.includeFiles:
            options |= FsSearchOptions.FILES_INCLUDED
        if terms.includeDirs:
            options |= FsSearchOptions.DIRS_INCLUDED
        return options

    def _startSearch(self, terms: SearchTerms) -> None:
        # Validating folder...
        folder = Path(terms.folder)
        if not (folder.exists() and folder.is_dir()):
            self._lbl_status.config(text="Invalid folder.")
            return
        # Validating search text...
        if not terms.search:
            self._lbl_status.config(text="Search text is empty.")
            return
        # Updating the GUI...
        self._clearResultsVw()
        self._searchbx.updateGui_searching()
        self._lbl_status.config(text="Searching...")
        # Starting the search thread...
        self._q = Queue[FsSearchLocation | FsSearchMatch]()
        self._searcher = self._searchers[terms.algorithm]()
        self._searchThread = threading.Thread(
            target=self._runSearch,
            args=(
                folder,
                terms.search,
                self._q,
                self._termsToOptions(terms),),
            daemon=True,)
        self._searchThread.start()
        # Polling the results...
        self._afterId_search = self.after(
            self._INTVL_AFTER,
            self._pollSearching)
    
    def _stopSearch(self) -> None:
        self._searcher.stopSearch() # type: ignore
        self._searchbx.updateGui_stopping()
        self._lbl_status.config(text="Stopping...")
        if self._afterId_search:
            self.after_cancel(self._afterId_search)
            self._afterId_search = None
        self._afterId_stop = self.after(
            self._INTVL_AFTER,
            self._pollStopping,)

    def _runSearch(
            self,
            root_dir: str,
            search: str,
            q: Queue[FsSearchLocation | FsSearchMatch],
            options: FsSearchOptions,
            ) -> None:
        try:
            self._searcher.search(root_dir, search, q, options) # type: ignore
        except RuntimeError as err:
            print(err)

    def _pollSearching(self):
        # Reading search results...
        try:
            while True:
                item = self._q.get_nowait()
                if isinstance(item, FsSearchLocation):
                    self._lbl_status.config(text=f"Searching in: {item.path}")
                    print(f'<{len(item.path.parents)}> {item.path}')
                elif isinstance(item, FsSearchMatch):
                    self._resvw.add(item.path)
        except Empty:
            pass
        # Checking if search finished...
        if self._searchThread is None or not self._searchThread.is_alive():
            self._searchbx.updateGui_ready()
            self._lbl_status.config(text="Ready")
            self._afterId_search = None
            self._searchThread = None
            self._searcher = None
            return
        # Scheduling next poll...
        self._afterId_search = self.after(
            self._INTVL_AFTER,
            self._pollSearching,)
    
    def _pollStopping(self) -> None:
        # Checking if search finished...
        if self._searchThread is None or not self._searchThread.is_alive():
            self._searchbx.updateGui_ready()
            self._lbl_status.config(text="Ready")
            self._afterId_stop = None
            self._searchThread = None
            return
        # Scheduling next poll...
        self._afterId_stop = self.after(
            self._INTVL_AFTER,
            self._pollStopping,)

    def _revealInExplorer(self, path: Path):
        """Opens the given path in the system's file explorer."""
        if platform.system() == "Windows":
            # Windows
            if path.is_file():
                subprocess.Popen(f'explorer /select,"{path}"')
            else:
                subprocess.Popen(f'explorer "{path}"')
        elif platform.system() == "Darwin":
            # macOS
            if path.is_file():
                subprocess.Popen(["open", "-R", str(path)])
            else:
                subprocess.Popen(["open", str(path)])
        elif platform.system() == "Linux":
            # Linux
            if path.is_file():
                subprocess.Popen(["xdg-open", str(path.parent)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
        else:
            logging.warning(f"Unsupported operating system: {platform.system()}")
