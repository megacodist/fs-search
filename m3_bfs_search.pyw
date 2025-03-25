#
# 
#

from pathlib import Path
from megacodist.console import Spinner, SpinnerStyle
from megacodist.exceptions import InvalidFileContentError


spinner = Spinner(SpinnerStyle.BLOCK)
"""The spinner object to ensute the user of background tasks on the
terminal.
"""
# Getting application dir...
_APP_DIR = Path(__file__).resolve().parent
"""The root directory of the application."""


def main() -> None:
    global spinner
    # Loading FS searchers...
    from utils.fs_search import loadFsSearchers
    searchers = loadFsSearchers(Path('megacodist/fs'))
    print(searchers)
    # Loading application settings...
    #spinner.start(_('LOADING_SETTINGS'))
    from utils.settings import FsAppSettings
    settings = FsAppSettings()
    try:
        settings.load(_APP_DIR / 'config.bin')
    except InvalidFileContentError:
        #spinner.stop(_('BAD_SETTINGS_FILE'))
        pass
    else:
        #spinner.stop(_("SETTINGS_LOADED"))
        pass
    # Running the app...
    from widgets.search_win import SearchWin
    try:
        app = SearchWin(settings, searchers)
        app.mainloop()
    finally:
        settings.save()


if __name__ == "__main__":
    main()
