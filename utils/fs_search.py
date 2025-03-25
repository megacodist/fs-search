#
# 
#

from pathlib import Path
import logging

from megacodist.fs import IFsSearchable


def loadFsSearchers(relative_dir: Path) -> dict[str, type[IFsSearchable]]:
    """
    Loads all file system searcher modules from the specified relative
    directory and returns a dictionary mapping searcher names to their
    corresponding classes.

    Args:
        relative_dir:
            The relative path from application root directory to
            the directory containing the searcher modules.

    Returns:
        A dictionary where keys are searcher names and values are their
        corresponding classes.
    """
    # Declaring variables ---------------------------------
    from importlib import import_module
    from types import ModuleType
    modNames: list[Path]
    pthSearcher: Path
    modObj: ModuleType
    # Loading pages & wizards -----------------------------
    searchers: dict[str, type[IFsSearchable]] = {}
    # Initializing & loading the other module of commands package...
    modNames = [
        pthSearcher.relative_to(relative_dir)
        for pthSearcher in relative_dir.glob("*.py")
        if not pthSearcher.name.startswith("_")]
    dirDotted = ".".join(relative_dir.parts)
    for pthSearcher in modNames:
        try:
            # Path('a/b/c/d.py') => 'a.b.c.d'...
            modDotted = ".".join(pthSearcher.with_suffix("").parts)
            modObj = import_module(f"{dirDotted}.{modDotted}")
            for itemName in dir(modObj):
                itemObject = getattr(modObj, itemName)
                if (
                        isinstance(itemObject, type)
                        and issubclass(itemObject, IFsSearchable)
                        and itemObject.__module__ == modObj.__name__
                        ):
                    searchers[itemObject.name] = itemObject
        except Exception as e:
            logging.error("Error loading searcher module: "
                f"{(relative_dir / pthSearcher)}. Error: {e}")
            continue
    return searchers
