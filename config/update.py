#!/usr/bin/python

import platform, os, sys, pwd

"""

Take an options dictionary and update /etc/bywaf/settings.py

"""
def generateConfig(options):

    config = """#!/usr/bin/python

##################################################################################################
#
# ByWaf configuration file
#
# Run update.py to automatically set all these options to their defaults.
#
##################################################################################################



#################################################
#
# General system options
#
#################################################

"""
    print "\n ByWaf configuration:"

    config += '# OS to use (Kali/Backtrack/Debian/Windows)\n'
    config += 'OPERATING_SYSTEM="' + options['OPERATING_SYSTEM'] + '"\n\n'
    print "\n [*] OPERATING_SYSTEM = " + options['OPERATING_SYSTEM']

    config += '# Terminal clearing method to use (use "false" to disable it)\n'
    config += 'TERMINAL_CLEAR="' + options['TERMINAL_CLEAR'] + '"\n\n'
    print " [*] TERMINAL_CLEAR = " + options['TERMINAL_CLEAR']

    config += '# Path to temporary directory\n'
    config += 'TEMP_DIR="' + options["TEMP_DIR"] + '"\n\n'
    print " [*] TEMP_DIR = " + options["TEMP_DIR"]


    config += """
#################################################
#
# ByWaf specific options
#
#################################################

"""
    config += '# ByWAf install path\n'
    config += 'BYWAF_PATH="' + options['BYWAF_PATH'] + '"\n\n'
    print " [*] BYWAF_PATH = " + options['BYWAF_PATH']

    config += """
#################################################
#
# ByWaf config file completed
#
#################################################

"""
    if platform.system() == "Linux":
        # create the output compiled path if it doesn't exist
        if not os.path.exists("/etc/bywaf/"):
            # os.makedirs("/etc/veil/")
            os.system("sudo mkdir /etc/bywaf/")
            os.system("sudo touch /etc/bywaf/settings.py")
            os.system("sudo chmod 777 /etc/bywaf/settings.py")
            print " [*] Path '/etc/bywaf/' Created"
        f = open("/etc/bywaf/settings.py", 'w')
        f.write(config)
        f.close()
        print " Configuration File Written To '/etc/bywaf/settings.py'\n"
    else:
        print " [!] ERROR: PLATFORM NOT CURRENTLY SUPPORTED"
        sys.exit()
    


if __name__ == '__main__':

    options = {}

    if platform.system() == "Linux":

        # check /etc/issue for the exact linux distro
        issue = open("/etc/issue").read()

        if issue.startswith("Kali"):
            options["OPERATING_SYSTEM"] = "Kali"
            options["TERMINAL_CLEAR"] = "clear"
        elif issue.startswith("BackTrack"):
            options["OPERATING_SYSTEM"] = "BackTrack"
            options["TERMINAL_CLEAR"] = "clear"
        else:
            options["OPERATING_SYSTEM"] = "Linux"
            options["TERMINAL_CLEAR"] = "clear"

        # last of the general options
        options["TEMP_DIR"] = "/tmp/"

        # ByWaf specific options
        bywaf_path = "/".join(os.getcwd().split("/")[:-1]) + "/"
        options["BYWAF_PATH"] = bywaf_path
        options["GENERATE_HANDLER_SCRIPT"] = "True"

    # unsupported platform...
    else:
        print " [!] ERROR: PLATFORM NOT CURRENTLY SUPPORTED"
        sys.exit()

    generateConfig(options)
