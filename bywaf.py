#!/usr/bin/env python2

"""
Front end launcher for ByWaf.

Handles command line switches for all options.
A modules.commoncontroller.Controller() object is instantiated with the
appropriate switches, or the interactive menu is triggered if no switches
are provided.
"""

# Import Modules
import sys, argparse, time, os, base64, socket, shlex
try:
    import requests
except ImportError:
    print '========================================================================='
    print ' Necessary component missing'
    print ' Please run: bash %s -s' % os.path.abspath("setup/setup.sh")
    print '========================================================================='
    sys.exit()

from modules.common import controller
from modules.common import messages
from modules.common import helpers



if __name__ == '__main__':
    try:
        # keep bywaf.pyc from appearing?
        sys.dont_write_bytecode = True

        parser = argparse.ArgumentParser()
        parser.add_argument('--update', action='store_true', help='Update the ByWaf.')
        parser.add_argument('--version', action="store_true", help='Displays version and quits.')

        args = parser.parse_args()

        # Print version
        if args.version:
            messages.title()
            sys.exit()


        # Print main title
        messages.title()

        # instantiate the main controller object
        controller = controller.Controller(oneRun=False)

        # call the update functionality for Veil and then exit
        if args.update:
            controller.UpdateVeil(interactive=False)
            sys.exit()


        # use interactive menu if not arguments
        controller.MainMenu(args=args)

    # Catch ctrl + c interrupts from the user
    except KeyboardInterrupt:
        print helpers.color("\n\n [!] Exiting...\n", warning=True)

    except EOFError:
        print helpers.color("\n\n [!] Exiting...\n", warning=True)
