#
# 
#

import tkinter as tk
from tkinter import NO, ttk
from pathlib import Path
import os
import platform
import subprocess
import logging
from typing import Callable

class ResultsView(ttk.Frame):
    """
    A custom widget to display search results in a Treeview with scrollbars.
    """

    def __init__(
            self,
            parent,
            on_item_double_click: Callable[[Path], None] | None = None,
            ) -> None:
        super().__init__(parent)
        self._mpIidPath: dict[str, Path] = {}
        """
        The mapping between items' ID and their path objects:
        `iid -> Path`
        """
        self._onItemDoubleClicked = on_item_double_click
        self._initGui()

    def _initGui(self):
        # Configure grid layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        # Create Treeview
        self._treevw = ttk.Treeview(
            self, columns=("Item", "Path"),
            show="headings",)
        self.setColumnsSize(100, 200)
        self._treevw.heading("Item", text="Item")
        self._treevw.heading("Path", text="Path")
        # Create scrollbars
        self._vsb = ttk.Scrollbar(
            self, orient="vertical",
            command=self._treevw.yview,)
        self._hsb = ttk.Scrollbar(
            self, orient="horizontal",
            command=self._treevw.xview,)
        self._treevw.configure(
            yscrollcommand=self._vsb.set,
            xscrollcommand=self._hsb.set,)
        # Place widgets
        self._treevw.grid(row=0, column=0, sticky="nsew")
        self._vsb.grid(row=0, column=1, sticky="ns")
        self._hsb.grid(row=1, column=0, sticky="ew")
        # Bind double-click event
        self._treevw.bind("<Double-1>", self._onDoubleClick)

    def clear(self):
        """Clears all items from the Treeview."""
        for item in self._treevw.get_children():
            self._treevw.delete(item)
        self._mpIidPath.clear()

    def add(self, path: Path):
        """Adds a Path object to the Treeview."""
        iid = self._treevw.insert(
            parent="",
            index="end",
            values=(path.name, str(path.parent)))
        self._mpIidPath[iid] = path

    def setColumnsSize(
            self,
            item_width: int,
            path_width: int,
            ) -> None:
        self._treevw.column("Item", width=item_width, stretch=tk.NO)
        self._treevw.column("Path", width=path_width, stretch=tk.NO)
    
    def getColumnsSize(self) -> tuple[int, int]:
        """
        Returns a 2-tuple of widths for the Item and Path columns
        respectively. Raises `TypeError` if something goes wrong.
        """
        itemColWidth = self._treevw.column("Item")["width"] # type: ignore
        pathColWidth = self._treevw.column("Path")["width"] # type: ignore
        return itemColWidth, pathColWidth

    def _onDoubleClick(self, event: tk.Event) -> None:
        """Handles the double-click event on a Treeview item."""
        iid = self._treevw.identify_row(event.y)
        if iid and self._onItemDoubleClicked:
            self._onItemDoubleClicked(self._mpIidPath[iid])

