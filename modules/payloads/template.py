"""

Description of the payload.


Addtional notes, sources, links, etc.


Author of the module.

"""

# framework import to access general messages
from modules.common import messages

# framework import to access common helper methods, including randomization
from modules.common import helpers

# framework import to access completer function (tab)
from modules.common import completers

# the main config file
import settings

# Main class must be titled "Payload"
class Payload:

    def __init__(self):
        # not required options
        self.description = "description"
        self.language = "python/cs/powershell/whatever"
        self.rating = "Poor/Normal/Good/Excellent"
        self.extension = "py/cs/c/etc."

        # options we require user ineraction for- format is {OPTION : [Value, Description]]}
        # the code logic will parse any of these out and require the user to input a value for them
        self.required_options = {
                                    "RHOST" : ["127.0.0.1", "Target's IP address"],
                                    "RPORT"   : ["80", "Target's port number"]
                                }

        # an option note to be displayed to the user after payload generation
        # i.e. additional compile notes, or usage warnings
        self.notes = "...additional notes to user..."

    # main method that returns the generated payload code
    def generate(self):
        
        '''
        All the funcional code and all the ouputs.
        
        see http_headers.py for example
        
        '''

        # example of how to check the internal options
        if self.required_options["SSL"][0].lower() == "y":
            function1 = function1

        # return to payload menu
        return 
