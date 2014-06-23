# -- FILE: features/steps/example_steps.py
import os
import logging
logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s',
                    level=logging.INFO)
from gi.repository import GLib
from behave import then, step
from time import sleep
#from subprocess import Popen, PIPE
from dogtail.tree import root, SearchError
from dogtail.rawinput import keyCombo
from dogtail.utils import doDelay
#from ConfigParser import ConfigParser
#, step


@step(u'Press "{sequence}"')
def press_button_sequence(context, sequence):
    keyCombo(sequence)
    sleep(0.5)


def wait_for_app_to_appear(context, app):
    # Waiting for a window to appear
    for attempt in xrange(0, 10):
        try:
            context.app.instance = root.application(app.lower())
            context.app.instance.child(roleName='frame')
            break
        except (GLib.GError, SearchError):
            sleep(1)
            if attempt == 6:
                # Cleanup and restart app processes if we reached 30
                # seconds wait
                keyCombo("<Enter>")
                os.system("python cleanup.py")
                os.system("pkill -f %s 2&> /dev/null" % app.lower())
                context.execute_steps(u"* Start %s via command" % app)
            continue


@step(u'Start {app:w} via {type:w}')
def start_app_via_command(context, app, type):
    for attempt in xrange(0, 10):
        try:
            if type == 'command':
                context.app.startViaCommand()
            if type == 'menu':
                context.app.startViaMenu()
            break
        except GLib.GError:
            sleep(1)
            if attempt == 6:
                # Killall the app processes if we reached 30 seconds wait
                os.system("pkill -f %s 2&> /dev/null" % app.lower())
            continue


@step(u'Make sure that {app:w} is running')
def ensure_app_running(context, app):
    start_app_via_command(context, app, 'menu')
    wait_for_app_to_appear(context, app)
    logging.debug("app = %s", root.application(app.lower()))


@then(u'{app:w} should start')
def test_app_started(context, app):
    wait_for_app_to_appear(context, app)


@then(u"{app:w} shouldn't be running anymore")
def test_app_dead(context, app):
    app = app.lower()
    doDelay(3)
    logging.debug("app = %s", app)
    try:
        context.app.instance = root.application(app)
        logging.debug("root instance = %s", app)
        context.app.instance.child(roleName='frame')
    except (GLib.GError, SearchError):
        # We SHOULD fail here, because app shouldn't be found
        logging.debug("Exception fired!")
        return True
    else:
        # Bad, app is still running
        logging.debug("No exception!")
        return False
