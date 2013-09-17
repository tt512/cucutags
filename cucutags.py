#!/usr/bin/python
import os
import io
import re
import logging
logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s',
                    level=logging.INFO)


# Press "{sequence}" [@./common_steps/app.py:17]
# Start {app:w} via {type:w} [@./common_steps/app.py:42]
# Make sure that {app:w} is running [@./common_steps/app.py:59]
# {app:w} should start [@./common_steps/app.py:66]
# folder select dialog with name "{name}" is displayed
# [@./common_steps/dialogs.py:8]
# folder select dialog is displayed [@./common_steps/dialogs.py:13]
# in folder select dialog I choose "{name}" [@./common_steps/dialogs.py:19]
# file select dialog with name "{name}" is displayed
# [@./common_steps/dialogs.py:24]
# file select dialog is displayed [@./common_steps/dialogs.py:29]
# in file select dialog I select "{name}" [@./common_steps/dialogs.py:35]
# in file save dialog I save file to "{path}" clicking "{button}"
# [@./common_steps/dialogs.py:54]
# I open GApplication menu [@./common_steps/gmenu.py:12]
# I close GApplication menu [@./common_steps/gmenu.py:27]
# I click menu "{name}" in GApplication menu [@./common_steps/gmenu.py:34]
# I get submenus from GApplication [@./common_steps/gmenu.py:45]


class Target(object):
    pattern = re.compile(r"^\s*@(step|when|then)\(u'(.*)'\)")
    result = 'targets'

    def __init__(self, text, filename, lineno):
        self.text = text
        self.filename = filename
        self.lineno = int(lineno)

    def __unicode__(self):
        return "%s [@%s:%d]" % (self.text, self.filename, self.lineno)

    def __str__(self):
        return self.__unicode__().encode("utf-8")

    def ismatch(self, feature):
        return True


# sed -n -e \
#     's/^\s\+\(\*\|[Ww]hen\|[Ss]tep\|[Tt]hen\|[Gg]iven\)\s\+\(.*\)\s*$/\2/p' \
#     "$1" |sort -u
class Feature(object):
    pattern = \
        re.compile(r'^\s+(\*|[Ww]hen|[Ss]tep|[Tt]hen|[Gg]iven)\s+(.*)\s*$')
    result = 'features'

    def __init__(self, text, filename, lineno):
        self.text = text

    def __unicode__(self):
        return self.text

    def __str__(self):
        return self.__unicode__().encode("utf-8")


def ishidden(filename):
    """Is file hidden on the given OS.

    Later we can add some magic for non-Unix filesystems.
    """
    return filename[0] == "."


def process_file(cdir, filename):
    PATTERNS = {'.py': Target, '.feature': Feature}
    out = {
        'targets': [],
        'features': []
    }
    file_ext = os.path.splitext(filename)[1]
    if file_ext in PATTERNS.keys():
        ftype = PATTERNS[file_ext]

        logging.debug("cdir = %s, file = %s", cdir, filename)
        ffname = os.path.join(cdir, filename)
        with io.open(ffname) as f:
            lineno = 0
            for line in f.readlines():
                lineno += 1
                matches = ftype.pattern.search(line)
                if matches:
                    logging.debug("key = %s", ftype.result)
                    logging.debug("value = %s", matches.group(2))
                    obj = ftype(matches.group(2), ffname, lineno)
                    out[ftype.result].append(obj)

    len_results = len(out['targets']) + len(out['features'])
    if len_results:
        logging.debug("len out = %d", len_results)

    return out


def walker(startdir):
    feature_list = []
    target_list = []

    for root, dirs, files in os.walk(startdir):
        for directory in dirs:
            if ishidden(directory):
                dirs.remove(directory)

        for f in files:
            new_out = process_file(root, f)
            feature_list.extend(new_out['features'])
            target_list.extend(new_out['targets'])

    return feature_list, target_list


def match(feat, targlist):
    for trg in targlist:
        if trg.ismatch(feat):
            return trg

    return None


def matcher(features, targets):
    out = []
    for feat in features:
        trg = match(feat, targets)
        if trg:
            out.append((feat, trg.filename, trg.lineno,))

    return out


if __name__ == "__main__":
    raw = walker(os.curdir)
    res = matcher(raw[0], raw[1])
    for r in res:
        print("%s\t%s\t%s" % r)
