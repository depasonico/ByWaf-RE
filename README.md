==ByWaf==

ByWaf is back this time we used a framework called Veil this helps us to do the main core of the system for this reason the new ByWaf is called ByWaf RE (requiem) 

==Introduction==

This framework is a platform to create, store and execute python tools for Web application penetration testing.
The main concept was to create something similar to metasploit.


==Description==

As part of this framework different components are provided to help contributors to add their own tools and execute them through ByWaf RE.

==Setup==

You need to run setup.sh to configure the tool and environment under: setup/setup.sh
ByWaf Re is portable using python standard libraries however for Windows environment some components and functionality is limited.

  ./setup

      -c|--clean    = Force Clean Install Of Any Dependencies
      -s|--silent   = Automates the installation
      -h|--help     = Show This Help Menu 


==Execution==

ByWaf Re has two modes to operate one is a simple command line execution where the functionality is just informational.

  --update Update ByWaf to the latest version at github
  --version Displays version and quits

The second mode is the interactive mode in order to run it:

   ./bywaf.py or python bywaf.py

==Features==

[+] Auto-tab

[+] Auto-fill

[+] Internal commands:
   [-] info
   [-] options