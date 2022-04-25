import argparse
import logging
import os
from com.ankamagames.jerakine.logger.Logger import Logger
from . import ui
import webbrowser

logger = logging.getLogger("labot")


def main(capture_file=None):
    ui.init(capture_file)
    ui.async_start()


if __name__ == "__main__":

    logger.debug("Starting sniffer as __main__")
    parser = argparse.ArgumentParser(
        description="Start the sniffer either from a file or from live capture."
    )
    parser.add_argument(
        "--capture", "-c", metavar="PATH", type=str, help="Path to capture file"
    )
    parser.add_argument(
        "--debug", "-d", action="store_true", help="show logger debug messages"
    )

    args = parser.parse_args()

    if args.debug:
        logger.setLevel("DEBUG")
    else:
        logger.setLevel("INFO")

    if args.capture:
        logger.debug("Starting sniffer with capture file")
        main(args.capture)
    else:
        logger.debug("Starting sniffer on live interface")
        main()
        bpath = os.environ.get("WEB_BROWSER") + " %s"
        if bpath:
            webbrowser.get(bpath).open_new("http://127.0.0.1:8888")
