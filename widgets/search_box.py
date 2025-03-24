#
#
#

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory
from typing import Callable

from utils.fs_search.bfs_search import SearchOptions


class SearchTerms:
    """Represents the search terms."""

    def __init__(
            self,
            search: str,
            folder: str,
            algorithm: str,
            match_case: bool,
            match_whole: bool,
            include_files: bool,
            include_dirs: bool,
            ) -> None:
        self.search = search
        self.folder = folder
        self.algorithm = algorithm
        self.matchCase = match_case
        self.matchWhole = match_whole
        self.includeFiles = include_files
        self.includeDirs = include_dirs


class SearchBox(ttk.Frame):
    def __init__(
            self,
            parent,
            on_search: Callable[[SearchTerms], None],
            on_stop: Callable[[], None],
            ) -> None:
        super().__init__(parent)
        self._onSearch = on_search
        self._onStop = on_stop
        # Declaring variables...
        self._bvar_matchCase = tk.BooleanVar(value=False)
        self._bvar_matchWhole = tk.BooleanVar(value=False)
        self._bvar_includeFiles = tk.BooleanVar(value=True)
        self._bvar_includeFolders = tk.BooleanVar(value=True)
        self._svar_search = tk.StringVar(value="")
        self._svar_folder = tk.StringVar(value="")
        self._svar_algorithm = tk.StringVar(value="BFS")
        # Creating GUI...
        self._initGui()
        # Setting event handlers...
        self._btn_browseDir.config(command=self._selectFolder)
        self._btn_searchStop.config(command=self._onSearchStopClicked)

    def _initGui(self) -> None:
        # 
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        for i in range(11):
            self.rowconfigure(i, weight=0)
        # Search Label and Button
        self._lbl_search = ttk.Label(self, text="Search:")
        self._lbl_search.grid(
            row=0,
            column=0,
            padx=4,
            pady=(7, 1,),
            sticky=tk.W,)
        #
        self._btn_searchStop = ttk.Button(self, text="Search")
        self._btn_searchStop.grid(
            row=0,
            column=1,
            padx=4,
            pady=(7, 1,),
            sticky=tk.E,)
        # Search Entry
        self._txbx_search = ttk.Entry(
            self, textvariable=self._svar_search
        )
        self._txbx_search.grid(
            row=1,
            column=0,
            columnspan=2,
            padx=4,
            pady=(1, 7,),
            sticky=tk.NSEW,)
        # Folder Label and Browse Button
        self._lbl_folder = ttk.Label(self, text="Folder:")
        self._lbl_folder.grid(
            row=2,
            column=0,
            padx=4,
            pady=(7, 1,),
            sticky=tk.W,)
        #
        self._btn_browseDir = ttk.Button(self, text="Browse")
        self._btn_browseDir.grid(
            row=2,
            column=1,
            padx=4,
            pady=(7, 1,),
            sticky=tk.E,)
        # Folder Entry
        self._txbx_folder = ttk.Entry(
            self,
            state="disabled",
            textvariable=self._svar_folder,)
        self._txbx_folder.grid(
            row=3,
            column=0,
            columnspan=2,
            padx=4,
            pady=(1, 7,),
            sticky=tk.NSEW,)
        # Match Case Checkbox
        self._chbx_matchCase = ttk.Checkbutton(
            self,
            text="Match case",
            variable=self._bvar_matchCase,
        )
        self._chbx_matchCase.grid(
            row=4,
            column=0,
            columnspan=2,
            padx=4,
            pady=(7, 1,),
            sticky=tk.W,
        )
        # Match Whole Word Checkbox
        self._chbx_matchWhole = ttk.Checkbutton(
            self,
            text="Match whole word",
            variable=self._bvar_matchWhole,
        )
        self._chbx_matchWhole.grid(
            row=5,
            column=0,
            columnspan=2,
            padx=4,
            pady=(1, 1,),
            sticky=tk.W,
        )
        # Include Files Checkbox
        self._chbx_includeFiles = ttk.Checkbutton(
            self,
            text="Include files",
            variable=self._bvar_includeFiles,
        )
        self._chbx_includeFiles.grid(
            row=6,
            column=0,
            columnspan=2,
            padx=4,
            pady=(1, 1,),
            sticky=tk.W,
        )
        # Include Folders Checkbox
        self._chbx_includeFolders = ttk.Checkbutton(
            self,
            text="Include folders",
            variable=self._bvar_includeFolders,
        )
        self._chbx_includeFolders.grid(
            row=7,
            column=0,
            columnspan=2,
            padx=4,
            pady=(1, 7,),
            sticky=tk.W,
        )
        # Algorithm Label
        self._lbl_algorithm = ttk.Label(self, text="Algorithm:")
        self._lbl_algorithm.grid(
            row=8,
            column=0,
            columnspan=2,
            padx=4,
            pady=(7, 1,),
            sticky=tk.W)
        # Algorithm Combobox
        self._cmbx_algorithm = ttk.Combobox(
            self,
            values=["BFS", "DFS"],
            state="readonly",
            textvariable=self._svar_algorithm,)
        self._cmbx_algorithm.current(0)  # Default to BFS
        self._cmbx_algorithm.grid(
            row=9,
            column=0,
            columnspan=2,
            padx=4,
            pady=(1, 7,),
            sticky=tk.NSEW,
        )

    def _getSearchTerms(self) -> SearchTerms:
        """
        Returns the user selected search terms in the GUI as a
        SearchTerms object.
        """
        return SearchTerms(
            search=self._svar_search.get(),
            folder=self._svar_folder.get(),
            algorithm=self._svar_algorithm.get(),
            match_case=self._bvar_matchCase.get(),
            match_whole=self._bvar_matchWhole.get(),
            include_files=self._bvar_includeFiles.get(),
            include_dirs=self._bvar_includeFolders.get(),
        )

    def _selectFolder(self, event=None):
        folder_selected = askdirectory()
        if folder_selected:
            self._txbx_folder.config(state="normal")
            self._txbx_folder.delete(0, tk.END)
            self._txbx_folder.insert(0, folder_selected)
            self._svar_folder.set(folder_selected)
            self._txbx_folder.config(state="disabled")

    def _onSearchStopClicked(self):
        match self._btn_searchStop["text"]:
            case "Search":
                self._onSearch(self._getSearchTerms())
            case "Stop":
                self._onStop()

    def get_folder(self) -> str:
        return self._svar_folder.get()

    def get_search_text(self) -> str:
        return self._svar_search.get()

    def updateGui_ready(self) -> None:
        """Updates the GUI to show the app is ready to perform BFS search."""
        self._btn_searchStop.config(text="Search", state=tk.NORMAL)
        self._btn_browseDir.configure(state=tk.NORMAL)
        self._txbx_search.config(state=tk.NORMAL)
        self._chbx_matchCase.config(state=tk.NORMAL)
        self._chbx_matchWhole.config(state=tk.NORMAL)
        self._chbx_includeFiles.config(state=tk.NORMAL)
        self._chbx_includeFolders.config(state=tk.NORMAL)
        self._cmbx_algorithm.config(state=tk.NORMAL)

    def updateGui_searching(self) -> None:
        """Updates the GUI to show the app is performing BFS search."""
        self._btn_searchStop.config(text="Stop", state=tk.NORMAL)
        self._btn_browseDir.configure(state=tk.DISABLED)
        self._txbx_search.config(state=tk.DISABLED)
        self._chbx_matchCase.config(state=tk.DISABLED)
        self._chbx_matchWhole.config(state=tk.DISABLED)
        self._chbx_includeFiles.config(state=tk.DISABLED)
        self._chbx_includeFolders.config(state=tk.DISABLED)
        self._cmbx_algorithm.config(state=tk.DISABLED)

    def updateGui_stopping(self) -> None:
        """Updates the GUI to show the app is stopping BFS search."""
        self._btn_searchStop.config(text="Stopping", state=tk.DISABLED)
        self._btn_browseDir.configure(state=tk.DISABLED)
        self._txbx_search.config(state=tk.DISABLED)
        self._chbx_matchCase.config(state=tk.DISABLED)
        self._chbx_matchWhole.config(state=tk.DISABLED)
        self._chbx_includeFiles.config(state=tk.DISABLED)
        self._chbx_includeFolders.config(state=tk.DISABLED)
        self._cmbx_algorithm.config(state=tk.DISABLED)
