# -*- coding: UTF-8 -*-

import os
from common_steps.helpers import dummy, App
from gi.repository import Gio
from dogtail.config import config
import logging
logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s',
                    level=logging.INFO)
from time import sleep


def before_all(context):
    """Setup empathy stuff
    Being executed before all features
    """

    # Reset GSettings
    schemas = [x for x
               in Gio.Settings.list_schemas() if 'empathy' in x.lower()]
    for schema in schemas:
        os.system("gsettings reset-recursively %s" % schema)

    # Skip warning dialog
    #os.system("gsettings set org.gnome.empathy.shell skip-wrnng-dialog true")

    # Wait for things to settle
    sleep(0.5)

    # Skip dogtail actions to print to stdout
    config.logDebugToStdOut = False
    config.typingDelay = 0.2

    # Include assertion object
    context.assertion = dummy()

    context.app = App('empathy',
                      # Store evo output in the empathy.log
                      parameters='> empathy.log 2>&1',
                      clean_dirs=['~/.local/share/Empathy',
                        '~/.local/share/telepathy',
                        '~/.local/share/telepathy-logger',
                        '~/.cache/Empathy', '~/.cache/telepathy',
                        '~/.config/Empathy'])


def before_tag(context, tag):
    """Setup for scenarios marked with tag
    If tag contains 'goa', then setup a goa account:
    google_goa will setup Google account etc.
    """
    try:
        if 'goa' in tag:
            context.execute_steps(
                u"* Add %s account via GOA" % tag.split('_')[1].capitalize())
    except Exception as e:
        print("error in before_tag(%s): %s" % (tag, e.message))
        raise RuntimeError


def after_step(context, step):
    """Teardown after each step.
    Here we make screenshot and embed it (if one of formatters supports it)
    """
    try:
        # Make screnshot if step has failed
        if hasattr(context, "embed"):
            os.system("gnome-screenshot -f /tmp/screenshot.jpg")
            context.embed('image/jpg', open("/tmp/screenshot.jpg", 'r').read())

        if step.status == 'failed' and os.environ.get('DEBUG_ON_FAILURE'):
            import ipdb
            ipdb.set_trace()

    except Exception:
        #print("Error in after_step: %s" % e)
        pass


def after_scenario(context, scenario):
    """Teardown for each scenario
    Kill empathy (in order to make this reliable we send sigkill)
    """
    try:
        # Stop empathy
        os.system("pkill -f empathy &> /dev/null")

        # Attach logs
        if hasattr(context, "embed"):
            context.embed('text/plain', open("empathy.log", 'r').read())
            os.system("rm -rf empathy.log")

        # Make some pause after scenario
        sleep(10)
    except Exception:
        # Stupid behave simply crashes in case exception has occurred
        pass
