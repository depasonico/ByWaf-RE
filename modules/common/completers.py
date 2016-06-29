"""

Contains any classes used for tab completion.


Reference - http://stackoverflow.com/questions/5637124/tab-completion-in-pythons-raw-input

"""

# Import Modules
import readline
import commands
import re
import os

class none(object):
    def complete(self, args):
        return [None]

class MainMenuCompleter(object):
    """
    Class used for tab completion of the main Controller menu

    Takes a list of available commands, and loaded payload modules.

    """
    def __init__(self, cmds, payloads):
        self.commands = [cmd for (cmd,desc) in cmds]
        self.payloads = payloads

    def complete_use(self, args):
        """Complete payload/module"""

        res = []
        payloads = []

        for (name, payload) in self.payloads:
            payloads.append(name)

        # return all payloads if we just have "use"
        if len(args[0].split("/")) == 1:
            res = [ m for m in payloads if m.startswith(args[0])] + [None]

        else:
            # get the language
            lang = args[0].split("/")[0]
            # get the rest of the paths
            rest = "/".join(args[0].split("/")[1:])

            payloads = []
            for (name, payload) in self.payloads:

                parts = name.split("/")

                # iterate down the split parts so we can handle the nested payload structure
                for x in xrange(len(parts)):

                    # if the first part of the iterated payload matches the language, append it
                    if parts[x] == lang:
                        payloads.append("/".join(parts[x+1:]))

                res = [ lang + '/' + m + ' ' for m in payloads if m.startswith(rest)] + [None]

        return res


    def complete_info(self, args):
        """Complete payload/module"""

        res = []
        payloads = []

        for (name, payload) in self.payloads:
            payloads.append(name)

        # return all payloads if we just have "use"
        if len(args[0].split("/")) == 1:
            res = [ m for m in payloads if m.startswith(args[0])] + [None]

        else:
            # get the language
            lang = args[0].split("/")[0]
            # get the rest of the paths
            rest = "/".join(args[0].split("/")[1:])

            payloads = []
            for (name, payload) in self.payloads:

                parts = name.split("/")

                # iterate down the split parts so we can handle the nested payload structure
                for x in xrange(len(parts)):

                    # if the first part of the iterated payload matches the language, append it
                    if parts[x] == lang:
                        payloads.append("/".join(parts[x+1:]))

                res = [ lang + '/' + m + ' ' for m in payloads if m.startswith(rest)] + [None]

        return res


    def complete(self, text, state):

        "Generic readline completion entry point."
        buffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()

        # show all commands
        if not line:
            return [c + ' ' for c in self.commands][state]

        # account for last argument ending in a space
        RE_SPACE = re.compile('.*\s+$', re.M)
        if RE_SPACE.match(buffer):
            line.append('')

        # resolve command to the implementation functions (above)
        cmd = line[0].strip()
        if cmd in self.commands:
            impl = getattr(self, 'complete_%s' % cmd)
            args = line[1:]
            if args:
                return (impl(args) + [None])[state]
            return [cmd + ' '][state]

        results = [ c + ' ' for c in self.commands if c.startswith(cmd)] + [None]

        return results[state]


class PayloadCompleter(object):

    def __init__(self, cmds, payload):
        self.commands = [cmd for (cmd,desc) in cmds]
        self.payload = payload


    def _listdir(self, root):
        """
        Complete a directory path.
        """
        res = []
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isdir(path):
                name += os.sep
            res.append(name)
        return res

    def _complete_path(self, path=None):
        """
        Complete a file path.
        """
        if not path:
            return self._listdir('.')
        dirname, rest = os.path.split(path)
        tmp = dirname if dirname else '.'
        res = [os.path.join(dirname, p)
                for p in self._listdir(tmp) if p.startswith(rest)]
        # more than one match, or single match which does not exist (typo)
        if len(res) > 1 or not os.path.exists(path):
            return res
        # resolved to a single directory, so return list of files below it
        if os.path.isdir(path):
            return [os.path.join(path, p) for p in self._listdir(path)]
        # exact file match terminates this completion
        return [path + ' ']

    def complete_path(self, args):
        """
        Entry point for path completion.
        """
        if not args:
            return self._complete_path('.')
        # treat the last arg as a path and complete it
        return self._complete_path(args[-1])


    def complete_set(self, args):
        """
        Complete all options for the 'set' command.
        """

        res = []

        if hasattr(self.payload, 'required_options'):

            options = [k for k in sorted(self.payload.required_options.iterkeys())]

            if args[0] != "":
                if args[0].strip() == "RHOST":
                    # autocomplete the IP for LHOST
                    res = [commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:]] + [None]
                elif args[0].strip() == "RPORT":
                    # autocomplete the common HTTP port of 80 for RPORT
                    res = ["80"] + [None]
                elif args[0].strip() == "original_exe":
                    # tab-complete a file path for an exe
                    res = self.complete_path(args)
                elif args[0].strip().endswith("_source"):
                    # tab-complete a file path for an exe
                    res = self.complete_path(args)
                # elif args[0].strip() == "other path-needing option":
                #     # tab-complete a file path
                #     res = self.complete_path(args)
                else:
                    # complete the command in the list ONLY if it's partially completed
                    res = [ o + ' ' for o in options if (o.startswith(args[0]) and o != args[0] )] + [None]
            else:
                # return all required_options available to 'set'
                res = [ o + ' ' for o in options] + [None]

        return res


    def complete(self, text, state):
        """
        Generic readline completion entry point.
        """

        buffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()

        # show all commands
        if not line:
            return [c + ' ' for c in self.commands][state]

        # account for last argument ending in a space
        RE_SPACE = re.compile('.*\s+$', re.M)
        if RE_SPACE.match(buffer):
            line.append('')

        # resolve command to the implementation functions (above)
        cmd = line[0].strip()
        if cmd in self.commands:
            impl = getattr(self, 'complete_%s' % cmd)
            args = line[1:]
            if args:
                return (impl(args) + [None])[state]
            return [cmd + ' '][state]

        results = [ c + ' ' for c in self.commands if c.startswith(cmd)] + [None]

        return results[state]



class IPCompleter(object):
    """
    Class used for tab completion of local IP for RHOST.

    """
    def __init__(self):
        pass

    """
    If blank line, fill in the local IP
    """
    def complete(self, text, state):

        buffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()

        if not line:
            ip = [commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1]] + [None]
            return ip[state]
        else:
            return text[state]


class MSFPortCompleter(object):
    """
    Class used for tab completion of the default port (80) for MSF payloads

    """
    def __init__(self):
        pass

    """
    If blank line, fill in 80
    """
    def complete(self, text, state):

        buffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()

        if not line:
            port = ["80"] + [None]
            return port[state]
        else:
            return text[state]


class PathCompleter(object):
    """
    Class used for tab completion of files on the local path.
    """
    def __init__(self):
        pass

    def _listdir(self, root):
        res = []
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isdir(path):
                name += os.sep
            res.append(name)
        return res

    def _complete_path(self, path=None):
        if not path:
            return self._listdir('.')
        dirname, rest = os.path.split(path)
        tmp = dirname if dirname else '.'
        res = [os.path.join(dirname, p)
                for p in self._listdir(tmp) if p.startswith(rest)]
        # more than one match, or single match which does not exist (typo)
        if len(res) > 1 or not os.path.exists(path):
            return res
        # resolved to a single directory, so return list of files below it
        if os.path.isdir(path):
            return [os.path.join(path, p) for p in self._listdir(path)]
        # exact file match terminates this completion
        return [path + ' ']

    def complete_path(self, args):
        if not args:
            return self._complete_path('.')
        # treat the last arg as a path and complete it
        return self._complete_path(args[-1])

    def complete(self, text, state):

        buffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()

        return (self.complete_path(line) + [None])[state]
