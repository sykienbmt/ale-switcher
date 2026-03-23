"""GUI entry point for AleSwitcher."""

import sys


def main():
    debug = '--debug' in sys.argv
    from ale_switcher.gui.app import start_app

    start_app(debug=debug)


if __name__ == '__main__':
    main()
