#
# 
#

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory
from pathlib import Path
from queue import Queue, Empty
import threading

from utils.fs_search.bfs_search import SearchOptions, SearchLocation, SearchMatch, BfsTreeSearch


class SearchWin(tk.Tk):
    def __init__(self):
        super().__init__()
        # Setting window properties...
        self.title("File Manager")
        self.geometry("800x600")  # Increased initial size
        self.resizable(True, True)
        # Declaring variables...
        self._q: Queue[SearchLocation | SearchMatch]
        self._bfs = BfsTreeSearch()
        """The BFS search object."""
        self._searchThread: threading.Thread | None = None
        self._INTVL_AFTER = 150
        self._afterId_search: str | None = None
        self._afterId_stop: str | None = None
        # Creating GUI...
        self._initGui()
        # Setting event handlers...
        self._btn_browseDir.config(command=self._selectFolder)
        self._btn_searchStop.config(command=self._onSearchStopClicked)

    def _initGui(self) -> None:
        # Main PanedWindow
        self._pwin = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self._pwin.pack(fill="both", expand=True)
        # Left Pane (Search Options)
        self._frm_searchOptions = ttk.Frame(self._pwin)
        self._pwin.add(self._frm_searchOptions, weight=1)  # Allow resizing
        # Middle Pane (Empty for now)
        self._frm_middle = ttk.Frame(self._pwin)
        self._pwin.add(self._frm_middle, weight=3)  # Allow resizing
        # Right Pane (Empty for now)
        self._frm_right = ttk.Frame(self._pwin)
        self._pwin.add(self._frm_right, weight=3)  # Allow resizing
        # Configure left pane grid
        self._frm_searchOptions.columnconfigure(0, weight=1)
        self._frm_searchOptions.columnconfigure(1, weight=0)
        for i in range(11):
            self._frm_searchOptions.rowconfigure(i, weight=0)
        # Search Label and Button
        self._lbl_search = ttk.Label(
            self._frm_searchOptions,
            text="Search:")
        self._lbl_search.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        #
        self._btn_searchStop = ttk.Button(
            self._frm_searchOptions,
            text="Search")
        self._btn_searchStop.grid(row=0, column=1, padx=5, pady=5, sticky="e")
        # Search Entry
        self._txbx_search = ttk.Entry(self._frm_searchOptions)
        self._txbx_search.grid(
            row=1,
            column=0,
            columnspan=2,
            padx=5, pady=5,
            sticky="ew")
        # Folder Label and Browse Button
        self._lbl_folder = ttk.Label(
            self._frm_searchOptions,
            text="Folder:")
        self._lbl_folder.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        #
        self._btn_browseDir = ttk.Button(
            self._frm_searchOptions,
            text="Browse")
        self._btn_browseDir.grid(row=2, column=1, padx=5, pady=5, sticky="e")
        # Folder Entry
        self._txbx_folder = ttk.Entry(
            self._frm_searchOptions,
            state="disabled")
        self._txbx_folder.grid(
            row=3,
            column=0,
            columnspan=2,
            padx=5,
            pady=5,
            sticky="ew")
        # Match Case Checkbox
        self._bvar_matchCase = tk.BooleanVar(value=False)
        self._chbx_matchCase = ttk.Checkbutton(
            self._frm_searchOptions,
            text="Match case",
            variable=self._bvar_matchCase,)
        self._chbx_matchCase.grid(
            row=4,
            column=0,
            columnspan=2,
            padx=5,
            pady=5,
            sticky="w")
        # Match Whole Word Checkbox
        self._bvar_matchWhole = tk.BooleanVar(value=False)
        self._chbx_matchWhole = ttk.Checkbutton(
            self._frm_searchOptions,
            text="Match whole word",
            variable=self._bvar_matchWhole)
        self._chbx_matchWhole.grid(
            row=5,
            column=0,
            columnspan=2,
            padx=5,
            pady=5,
            sticky="w")
        # Include Files Checkbox
        self._bvar_includeFiles = tk.BooleanVar(value=True)
        self._chbx_includeFiles = ttk.Checkbutton(
            self._frm_searchOptions,
            text="Include files",
            variable=self._bvar_includeFiles)
        self._chbx_includeFiles.grid(
            row=6,
            column=0,
            columnspan=2,
            padx=5,
            pady=5,
            sticky="w")
        # Include Folders Checkbox
        self._bvar_includeFolders = tk.BooleanVar(value=True)
        self._chbx_includeFolders = ttk.Checkbutton(
            self._frm_searchOptions,
            text="Include folders",
            variable=self._bvar_includeFolders)
        self._chbx_includeFolders.grid(
            row=7,
            column=0,
            columnspan=2,
            padx=5,
            pady=5,
            sticky="w")
        # Algorithm Label
        self._lbl_algorithm = ttk.Label(
            self._frm_searchOptions,
            text="Algorithm:")
        self._lbl_algorithm.grid(row=8, column=0, padx=5, pady=5, sticky="w")
        # Algorithm Combobox
        self._cmb_algorithm = ttk.Combobox(
            self._frm_searchOptions,
            values=["BFS", "DFS"])
        self._cmb_algorithm.current(0)  # Default to BFS
        self._cmb_algorithm.grid(
            row=9,
            column=0,
            columnspan=2,
            padx=5,
            pady=5,
            sticky="ew")
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

    def _getSearchOptions(self) -> SearchOptions:
        """
        Returns the user selected search options in the GUI as a
        SearchOptions enumeration.
        """
        options = SearchOptions.NONE
        if self._bvar_matchCase.get():
            options |= SearchOptions.MATCH_CASE
        if self._bvar_matchWhole.get():
            options |= SearchOptions.MATCH_WHOLE
        return options

    def _selectFolder(self, event=None):
        folder_selected = askdirectory()
        if folder_selected:
            self._txbx_folder.config(state="normal")
            self._txbx_folder.delete(0, tk.END)
            self._txbx_folder.insert(0, folder_selected)
            self._txbx_folder.config(state="disabled")

    def _clearResultsVw(self) -> None:
        # for item in self._resultsVw.get_children():
        #     self._resultsVw.delete(item)
        pass

    def _onSearchStopClicked(self):
        match self._btn_searchStop["text"]:
            case "Search":
                self._startSearch()
            case "Stop":
                self._stopSearch()

    def _startSearch(self) -> None:
        # Validating folder...
        folder = self._txbx_folder.get()
        if not Path(folder).is_dir():
            self._lbl_status.config(text="Invalid folder.")
            return
        # Validating search text...
        search = self._txbx_search.get()
        if not search:
            self._lbl_status.config(text="Search text is empty.")
            return
        # Updating the GUI...
        self._clearResultsVw()
        self._updateGui_searching()
        # Starting the search thread...
        self._q = Queue[SearchLocation | SearchMatch]()
        self._searchThread = threading.Thread(
            target=self._runSearch,
            args=(
                folder,
                search,
                self._q,
                self._getSearchOptions(),),
            daemon=True,)
        self._searchThread.start()
        # Polling the results...
        self._afterId_search = self.after(
            self._INTVL_AFTER,
            self._pollSearching)
    
    def _stopSearch(self) -> None:
        self._bfs.cancel()
        self._updateGui_stopping()
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
            q: Queue[SearchLocation | SearchMatch],
            options: SearchOptions,
            ) -> None:
        try:
            self._bfs.searchBfs(root_dir, search, q, options)
        except RuntimeError as err:
            print(err)

    def _pollSearching(self):
        # Reading search results...
        try:
            while True:
                item = self._q.get_nowait()
                if isinstance(item, SearchLocation):
                    self._lbl_status.config(text=f"Searching in: {item.path}")
                    print(f'<{len(item.path.parents)}> {item.path}')
                elif isinstance(item, SearchMatch):
                    # self._resultsVw.insert(
                    #     parent="",
                    #     index="end",
                    #     values=(item.path.name, item.path.parent,),
                    # )
                    pass
        except Empty:
            pass
        # Checking if search finished...
        if self._searchThread is None or not self._searchThread.is_alive():
            self._updateGui_ready()
            self._afterId_search = None
            self._searchThread = None
            return
        # Scheduling next poll...
        self._afterId_search = self.after(
            self._INTVL_AFTER,
            self._pollSearching,)
    
    def _pollStopping(self) -> None:
        # Checking if search finished...
        if self._searchThread is None or not self._searchThread.is_alive():
            self._updateGui_ready()
            self._afterId_stop = None
            self._searchThread = None
            return
        # Scheduling next poll...
        self._afterId_stop = self.after(
            self._INTVL_AFTER,
            self._pollStopping,)
    
    def _updateGui_ready(self) -> None:
        """Updates the GUI to show the app is ready to perform BFS search."""
        self._lbl_status.config(text="Ready")
        self._btn_searchStop.config(text="Search", state=tk.NORMAL)
        self._btn_browseDir.configure(state=tk.NORMAL)
        self._txbx_search.config(state=tk.NORMAL)
        self._chbx_matchCase.config(state=tk.NORMAL)
        self._chbx_matchWhole.config(state=tk.NORMAL)
        self._chbx_includeFiles.config(state=tk.NORMAL)
        self._chbx_includeFolders.config(state=tk.NORMAL)
        self._cmb_algorithm.config(state=tk.NORMAL)

    def _updateGui_searching(self) -> None:
        """Updates the GUI to show the app is performing BFS search."""
        self._lbl_status.config(text="Searching...")
        self._btn_searchStop.config(text="Stop", state=tk.NORMAL)
        self._btn_browseDir.configure(state=tk.DISABLED)
        self._txbx_search.config(state=tk.DISABLED)
        self._chbx_matchCase.config(state=tk.DISABLED)
        self._chbx_matchWhole.config(state=tk.DISABLED)
        self._chbx_includeFiles.config(state=tk.DISABLED)
        self._chbx_includeFolders.config(state=tk.DISABLED)
        self._cmb_algorithm.config(state=tk.DISABLED)

    def _updateGui_stopping(self) -> None:
        """Updates the GUI to show the app is stopping BFS search."""
        self._lbl_status.config(text="Stopping...")
        self._btn_searchStop.config(text="Stopping", state=tk.DISABLED)
        self._btn_browseDir.configure(state=tk.DISABLED)
        self._txbx_search.config(state=tk.DISABLED)
        self._chbx_matchCase.config(state=tk.DISABLED)
        self._chbx_matchWhole.config(state=tk.DISABLED)
        self._chbx_includeFiles.config(state=tk.DISABLED)
        self._chbx_includeFolders.config(state=tk.DISABLED)
        self._cmb_algorithm.config(state=tk.DISABLED)
