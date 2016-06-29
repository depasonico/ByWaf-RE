"""

This is the first payload/tool/plugin to test the functionality and compatibility with Veil-Evasion.
We used Veil's template.

Author: Rafael Gil depasonico@gmail.com

"""

# framework import to access common helper methods, including randomization
from modules.common import helpers


# the main config file
import settings

# Main class must be titled "Payload"
class Payload:

    def __init__(self):
        # required options
        self.description = "This payload is to extract all the headers form the Web server"
        self.language = "Python"
        self.rating = "Test"
        self.extension = "py"

        # options we require user ineraction for- format is {OPTION : [Value, Description]]}
        # the code logic will parse any of these out and require the user to input a value for them
        self.required_options = {
                                    "RHOST" : ["", "IP or Domain Name from the target"],
                                    "RPORT"   : ["80", "Terget's port"],
                                    "SSL"   : ["Y", "Use SSL connection"]
                                }

        # an option note to be displayed to the user after payload generation
        # i.e. additional compile notes, or usage warnings
        self.notes = "This payload to understad how ByWaf Payloads work"

    # main method that returns the generated payload code
    def generate(self):

        import requests
        
        if self.required_options["SSL"][0].lower() == "y":
            
            url = "https://"+self.required_options["RHOST"][0].lower()+":"+self.required_options["RPORT"][0].lower()
            
        else:
            
            url = "http://"+self.required_options["RHOST"][0].lower()+":"+self.required_options["RPORT"][0].lower()
        
        try:
            r = requests.get(url, verify=False)
            print "\n"
            for k, v in r.headers.iteritems():
                print "Header: "+k+ " : "+v
                
        except:
            print helpers.color("\n [!] Something went wrong.\n", warning=True)
            
        print helpers.color("\n [!] Returning...\n", yellow=True)

        # return everything
        return
