from __future__ import annotations

from abc import ABC, abstractmethod
import enum
from queue import Queue
from pathlib import Path


class SearchLocation:
    """
    Represents a folder in the search that is currently being searched for
    a match.
    """

    def __init__(self, path: Path) -> None:
        self.path = path

    def __repr__(self) -> str:
        return f"<BfsFolder path={self.path}>"


class SearchMatch:
    """Represents a match in the search process."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def __repr__(self) -> str:
        return f"<BfsFile path={self.path}>"


class SearchOptions(enum.IntFlag):
    """Represents the search options."""
    NONE = 0x00
    MATCH_CASE = 0x01
    MATCH_WHOLE = 0x02
    FILES_INCLUDED = 0x04
    DIRS_INCLUDED = 0x08


class ISearchable(ABC):
    """Interface for searchable objects."""

    @abstractmethod
    def searchBfs(
            self,
            root_dir: str,
            search: str,
            q: Queue[SearchLocation | SearchMatch],
            options: SearchOptions = SearchOptions.NONE
            ) -> None:
        """
        Performs a breadth-first search for the filename.

        Args:
            root_dir: The root directory to start the search from.
            search: The string to search for.
            q: The queue to put the results in.
            options: The search options.
        """
        raise NotImplementedError
    
    @abstractmethod
    def cancel(self) -> None:
        """Cancels the current search."""
        raise NotImplementedError


class BfsNode:
    """Represents a node in the breadth-first search tree."""

    data: str
    """The data associated with this node."""
    parent: BfsNode | None
    """The parent node, or None if this is the root."""
    children: list[BfsNode]
    """The child nodes of this node."""

    def __init__(self, data: str, parent: BfsNode | None = None) -> None:
        self.data = data
        self.parent = parent
        self.children = []

    def getFullPath(self) -> Path:
        """Traverses from this node upwards and creates the full path."""
        pathParts = []
        currentNode = self
        while currentNode:
            pathParts.insert(0, currentNode.data)
            currentNode = currentNode.parent
        return Path(*pathParts)

    def hasChildren(self) -> bool:
        """Checks if the node has children."""
        return bool(self.children)

    def addChild(self, child: BfsNode) -> None:
        """Adds a child to this node."""
        self.children.append(child)

    def deleteChild(self, child: BfsNode) -> None:
        """Deletes a child from this node."""
        if child in self.children:
            self.children.remove(child)
        else:
            raise ValueError(
                f"Child {child.data} not found in children of {self.data}"
            )

    def __repr__(self) -> str:
        className = (
            f"{self.__module__}.{self.__class__.__name__}"
            if self.__module__
            else self.__class__.__name__
        )
        return f"<{className} data={self.data}>"


class BfsTreeSearch(ISearchable):
    """Represents a breadth-first search tree."""

    _root: BfsNode | None = None
    """The root folder of file system to start searching."""
    _search: str = ""
    """The string to search for."""
    _options: SearchOptions = SearchOptions.NONE
    """The search options."""
    _q: Queue[SearchLocation | SearchMatch]
    """The queue for reporting matches during the search."""
    _isRunning: bool = False
    """Specifies whether a search is currently running."""
    _isCancelled: bool = False
    """Specifies whether the search has been cancelled."""

    def __init__(self) -> None:
        self._root = None
        self._search = ""
        self._options = SearchOptions.NONE
        self._isRunning = False
        self._isCancelled = False

    def _matched(self, text: str) -> bool:
        """Checks if a given `text` matches the `search`."""
        text_ = text if SearchOptions.MATCH_CASE in self._options else text.lower()
        search_ = self._search if SearchOptions.MATCH_CASE in self._options else self._search.lower()
        if SearchOptions.MATCH_WHOLE in self._options:
            return text_ == search_
        else:
            return search_ in text_

    def _searchNode(self, node: BfsNode) -> None:
        """
        Searches for a search match within the file system represented by
        `node`.
        """
        #
        if self._isCancelled:
            return
        #
        fullPath: Path = node.getFullPath()
        if not fullPath.exists():
            return
        self._q.put(SearchLocation(fullPath))
        #
        for item in fullPath.iterdir():
            if self._isCancelled:
                return
            if item.is_file():
                if self._matched(item.name):
                    self._q.put(SearchMatch(item))
            elif item.is_dir():
                new_node = BfsNode(item.name, node)
                node.addChild(new_node)

    def _searchNextLevel(self, node: BfsNode) -> None:
        """
        Recursively traverses the tree to the leaves to inspect them for
        a match, add their folders to the tree if any otherwise remove them.
        """
        if self._isCancelled:
            return
        if node.hasChildren():
            cpyChildren = node.children.copy()
            for child in cpyChildren:
                self._searchNextLevel(child)
                if not child.hasChildren():
                    node.deleteChild(child)
        else:
            self._searchNode(node)

    def searchBfs(
            self,
            root_dir: str,
            search: str,
            q: Queue[SearchLocation | SearchMatch],
            options: SearchOptions = SearchOptions.NONE
            ) -> None:
        """
        Performs a breadth-first search for the filename.
        """
        # Implementing the thread-safety...
        if self._isRunning:
            raise RuntimeError("Another thread is running this object.")
        self._isRunning = True
        self._isCancelled = False
        # Saving arguments...
        self._root = BfsNode(root_dir)
        self._search = search
        self._q = q
        self._options = options
        #
        try:
            # Searching the level 0...
            self._searchNode(self._root)
            # Searching the rest of the levels...
            while self._root.hasChildren() and not self._isCancelled:
                self._searchNextLevel(self._root)
        finally:
            self._isRunning = False
            self._isCancelled = False

    def cancel(self) -> None:
        """Cancels the current search."""
        self._isCancelled = True
