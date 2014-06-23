#!/usr/bin/python
"""
Library for basic acceptance tests
Author: Martin Simon <msimon@redhat.com>
Version: 2 (2012-04-13)
"""
import sys
import re
import os
import logging
from dogtail.tree import root, SearchError
from dogtail.rawinput import keyCombo, click, typeText, absoluteMotion
from dogtail.predicate import GenericPredicate
from subprocess import Popen, PIPE
from iniparse import ConfigParser
from time import sleep, time

# Create a dummy unittest class to have nice assertions
import unittest


class dummy(unittest.TestCase):
    def runTest(self):
        assert True


def timeout(func, args=(), expected=True, equals=True,
            timeout=30, period=0.25):
    """This function waits until specified function returns required result"""
    mustend = int(time()) + timeout
    while int(time()) < mustend:
        res = func.__call__(args)
        if equals:
            if res == expected:
                return True
        else:
            if res != expected:
                return True
        sleep(period)
    return False


def check_for_errors(context):
    """Check that no error is displayed on Evolution UI"""
    # Don't try to check for errors on dead app
    if not context.app.instance or context.app.instance.dead:
        return
    alerts = context.app.instance.findChildren(
        GenericPredicate(roleName='alert'))
    if not alerts:
        # alerts can also return None
        return
    alerts = filter(lambda x: x.showing, alerts)
    if len(alerts) > 0:
        labels = alerts[0].findChildren(GenericPredicate(roleName='label'))
        messages = [x.name for x in labels]

        if alerts[0].name != 'Error' and alerts[0].showing:
            # Erase the configuration and start all over again
            #return Popen("pkill -u `whoami` -9 " + self.appCommand,
            os.system("pkill -u `whoami` /*%s* &> /dev/null" %
                      context.app.appCommand)
            sleep(3)
            os.system("pkill -u `whoami` -9 /*%s* &> /dev/null" %
                      context.app.appCommand)

            # Remove previous data
            for folder in context.app.clean_dirs:
                os.system("rm -rf %s > /dev/null" % folder)

            raise RuntimeError("Error occurred: %s" % messages)
        else:
            print("Error occurred: %s" % messages)


def getMiniaturesPosition(name):
    """Get a position of miniature on Overview"""
    miniatures = []

    over = root.application('gnome-shell').child(name='Overview')
    mini = over.parent.children[-1]
    if mini == over:
        #print "Overview is not active"
        return miniatures
    widgets = mini.findChildren(GenericPredicate(name=name, roleName='label'))

    for widget in widgets:
        (x, y) = widget.position
        (a, b) = widget.size
        miniatures.append((x + a / 2, y + b / 2 - 100))
    return miniatures


def getDashIconPosition(name):
    """Get a position of icon on Overview dash"""
    over = root.application('gnome-shell').child(name='Overview')
    button = over[2].child(name=name)
    (x, y) = button.position
    (a, b) = button.size
    return (x + a / 2, y + b / 2)


class App():
    """
    Does all basic events with app
    """
    def __init__(self, appName, critical=None, shortcut='<Control><Q>',
                 quitButton=None, timeout=10, forceKill=True,
                 parameters='', clean_dirs=None, polkit=False):
        """
        Initialize object App
        appName     command to run the app
        critical    what's the function we check? {start,quit}
        shortcut    default quit shortcut
        timeout     timeout for starting and shuting down the app
        forceKill   is the app supposed to be kill before/after test?
        parameters  has the app any params needed to start?
                    (only for startViaCommand)
        """
        self.appCommand = appName.lower()
        self.shortcut = shortcut
        self.timeout = timeout
        self.forceKill = forceKill
        self.critical = critical
        self.quitButton = quitButton
        # the result remains false until the correct result is verified
        self.result = False
        self.updateCorePattern()
        self.parameters = parameters
        self.internCommand = self.appCommand.lower()
        self.polkit = polkit
        self.polkitPass = 'redhat'
        self.clean_dirs = clean_dirs or []

        """
            Getting all necessary data from *.desktop file of the app
        """
        cmd = "rpm -qlf $(which %s)" % appName
        #cmd2 = "grep %s.desktop" % self.appCommand
        #is it enough to search for .desktop?; vhumpa: no
        cmd += '|grep "^/usr/share/applications/.*\%s.desktop$"' % appName
        logging.debug("cmd = %s", cmd)
        proc = Popen(cmd, shell=True, stdout=PIPE)
        #have to check if the command and its desktop file exist
        #raise Exception, "*.desktop file of the app not found"
        #print("*.desktop file of the app not found")
        output = proc.communicate()[0].rstrip()
        logging.debug("output = %s", output)
        self.desktopConfig = ConfigParser()
        self.desktopConfig.read(output)

    def end(self):
        """
        Ends the test with correct return value
        """
        if self.result:
            #print "PASS"
            sys.exit(0)
        else:
            sys.exit("FAIL")

    def updateResult(self, result):
        self.result = result

    def getName(self):
        return self.desktopConfig.get('Desktop Entry', 'name')

    def getCategories(self):
        return self.desktopConfig.get('Desktop Entry', 'categories')

    def getMenuGroups(self):
        """
        Convert group list to the one correct menu group
        """
        groupsList = self.getCategories().split(';')
        groupsList.reverse()
        groupConversionDict = {
            'Accessibility': 'Universal Access',
            'System': 'System Tools',
            'Development': 'Programming',
            'Network': 'Internet',
            'Office': 'Office',
            'Graphics': 'Graphics',
            'Game': 'Games',
            'Education': 'Education',
            'Utility': 'Accessories',
            'AudioVideo': 'Sound &amp; Video'
        }

        for i in groupsList:
            if i in groupConversionDict:
                return groupConversionDict[i]

    def isRunning(self):
        """
        Is the app running?
        """
        #print "*** Checking if '%s' is running" % self.internCommand
        app = root

        apps = root.applications()
        for i in apps:
            if i.name.lower() == self.internCommand:
                app = i
                break

        if app.isChild(roleName='frame', recursive=False):
            #print "*** The app '%s' is running" % self.internCommand
            return True
        else:
            #print "*** The app '%s' is not running" % self.internCommand
            return False

    def kill(self):
        """
        Kill the app via 'killall'
        """
        #print "*** Killing all '%s' instances" % self.appCommand
        #return Popen("killall " + self.appCommand, shell = True).wait()
        return Popen("pkill -u `whoami` -9 " + self.appCommand,
                     shell=True).wait()

    def updateCorePattern(self):
        """
        Update string in /proc/sys/kernel/core_pattern to catch
        possible return code
        """
        #Popen("sudo rm -rf /tmp/cores", shell = True).wait()
        #Popen("mkdir /tmp/cores", shell = True).wait()
        #Popen("chmod a+rwx /tmp/cores", shell = True).wait()
        #Popen("echo \"/tmp/cores/core.%e.%s.%p\" \
        #       | sudo tee /proc/sys/kernel/core_pattern", shell = True).wait()
        pass

    def existsCoreDump(self):
        """
        Check if there is core dump created
        """
        #dirPath = "/tmp/cores/"
        #files = os.listdir(dirPath)
        #regexp = "core\.%s\.[0-9]{1,3}\.[0-9]*" % self.appCommand
        #for f in files:
        #    if re.match(regexp, f):
        #        return int(f.split(".")[2])
        return 0

    def startViaMenu(self):
        """
        Start the app via Gnome Shell menu
        """
        internCritical = (self.critical == 'start')

        #check if the app is running
        if self.forceKill and self.isRunning():
            self.kill()
            sleep(2)
            if self.isRunning():
                if internCritical:
                    self.updateResult(False)
                #print "!!! The app is running but it shouldn't be"
                return False
            else:
                #print "*** The app has been killed succesfully"
                pass

        try:
            #panel button Activities
            gnomeShell = root.application('gnome-shell')
            activities = gnomeShell.child(name='Activities', roleName='label')
            activities.click()
            sleep(6)  # time for overview to appear

            #menu Applications
            x, y = getDashIconPosition('Show Applications')
            absoluteMotion(x, y)
            sleep(1)
            click(x, y)
            sleep(4)  # time for all the oversized app icons to appear

            #submenu that contains the app
            submenu = gnomeShell.child(name=self.getMenuGroups(),
                                       roleName='list item')
            submenu.click()
            sleep(4)

            #the app itself
            app = gnomeShell.child(name=self.getName(), roleName='label')
            app.click()

            #if there is a polkit
            if self.polkit:
                sleep(3)
                typeText(self.polkitPass)
                keyCombo('<Enter>')

            sleep(self.timeout)

            if self.isRunning():
                #print "*** The app started successfully"
                if internCritical:
                    self.updateResult(True)
                return True
            else:
                #print "!!! The app is not running but it should be"
                if internCritical:
                    self.updateResult(False)
                return False
        except SearchError:
            #print "!!! Lookup error while passing the path"
            if internCritical:
                self.updateResult(False)
            return False

    def startViaCommand(self):
        """
        Start the app via command
        """
        internCritical = (self.critical == 'start')
        if self.forceKill and self.isRunning():
            self.kill()
            sleep(2)
            if self.isRunning():
                if internCritical:
                    self.updateResult(False)
                #print "!!! The app is running but it shouldn't be"
                return False
            else:
                pass
                #print "*** The app has been killed succesfully"

        returnValue = 0
        command = "%s %s &" % (self.appCommand, self.parameters)
        import os
        os.system(command)
        returnValue = 1
        #returnValue = utilsRun(command, timeout = 1, dumb = True)

        #if there is a polkit
        if self.polkit:
            sleep(3)
            typeText(self.polkitPass)
            keyCombo('<Enter>')

        start_time = 0
        while start_time < self.timeout:
            if self.isRunning():
                break
            sleep(0.5)
            start_time += 0.5

        #check the returned values
        if returnValue is None:
            if internCritical:
                self.updateResult(False)
            #print "!!! The app command could not be found"
            return False
        else:
            if self.isRunning():
                if internCritical:
                    self.updateResult(True)
                #print "*** The app started successfully"
                return True
            else:
                if internCritical:
                    self.updateResult(False)
                    #print "!!! The app did not started despite " \
                    #        + "the fact that the command was found"
                return False

    def closeViaShortcut(self):
        """
        Close the app via shortcut
        """
        internCritical = (self.critical == 'quit')

        if not self.isRunning():
            if internCritical:
                self.updateResult(False)
            #print "!!! The app does not seem to be running"
            return False

        keyCombo(self.shortcut)
        sleep(self.timeout)

        if self.isRunning():
            if self.forceKill:
                self.kill()
            if internCritical:
                self.updateResult(False)
            #print "!!! The app is running but it shouldn't be"
            return False
        else:
            if self.existsCoreDump() != 0:
                if internCritical:
                    self.updateResult(False)
                # print "!!! The app closed with core dump created. Signal %d"\
                #        % self.existsCoreDump()
                return False
            if internCritical:
                self.updateResult(True)
            #print "*** The app was successfully closed"
            return True

    def closeViaMenu(self):
        """
        Close app via menu button
        """
        internCritical = (self.critical == 'quit')

        if not self.isRunning():
            if internCritical:
                self.updateResult(False)
            #print "!!! The app does not seem to be running"
            return False

        #bind to the right app
        app = root
        apps = root.applications()
        for i in apps:
            if i.name.lower() == self.internCommand:
                app = i
                break
        app = app  # variable app is not used FIXME

        #try to bind the menu and the button
        try:
            firstSubmenu = self.getMenuNth(0)
            firstSubmenu.click()
            length = len(firstSubmenu.children)
            closeButton = firstSubmenu.children[length - 1]
            if self.quitButton is None:
                while re.search('(Close|Quit|Exit)', closeButton.name) is None:
                    length = length - 1
                    closeButton = firstSubmenu.children[length]
                    if length < 0:
                        if internCritical:
                            self.update(False)
                        #print "!!! The app quit button coldn't be found"
                        return False
            else:
                closeButton = firstSubmenu.child(self.quitButton)
        except SearchError:
            if internCritical:
                self.updateResult(False)
            #print "!!! The app menu bar or the quit button could'n be found"
            if self.forceKill:
                self.kill()
            return False

        sleep(2)  # timeout until menu appear
        #print "*** Trying to click to '%s'" % closeButton
        closeButton.click()
        sleep(self.timeout)

        if self.isRunning():
            if self.forceKill:
                self.kill()
            if internCritical:
                self.updateResult(False)
            #print "!!! The app is running but it shouldn't be"
            return False
        else:
            if self.existsCoreDump() != 0:
                if internCritical:
                    self.updateResult(False)
                # print "!! The app closed with core dump created. Signal %d" \
                # % self.existsCoreDump()
                return False
            if internCritical:
                self.updateResult(True)
            #print "*** The app was successfully closed"
            return True

    def getMenuNamed(self, menuName):
        """
        Return submenu with name specified with 'menuName'
        """
        #bind to the right app
        app = root
        apps = root.applications()
        for i in apps:
            if i.name.lower() == self.internCommand:
                app = i
                break

        #try to bind the menu and the button
        try:
            appMenu = app.child(roleName='menu bar')
            return appMenu.child(name=menuName)
        except:
            return None

    def getMenuNth(self, nth):
        """
        Return nth submenu
        """
        #bind to the right app
        app = root
        apps = root.applications()
        for i in apps:
            if i.name.lower() == self.internCommand:
                app = i
                break

        #try to bind the menu and the button
        try:
            appMenu = app.child(roleName='menu bar')
            return appMenu.children[nth]
        except:
            return None

    def getGnomePanelMenu(self):
        """
        Return object of gnome-panel menu of the app
        """
        try:
            app = root.application('gnome-shell')
            menu = app.child(roleName='menu')
            return menu.child(self.getName(), roleName='label')
        except:
            raise Exception("Gnome-panel menu of the app could not be found!")

    def openGnomePanelMenu(self):
        """
        Click to the gnome-panel menu
        """
        menu = self.getGnomePanelMenu()
        if menu is not None:
            menu.click()
        else:
            raise Exception("Gnome-panel menu of the app could not be found!")

    def getGnomePanelMenuItems(self):
        """
        Return a list of objects in gnome-panel app menu
        """
        quitButton = self.getGnomePanelQuit()
        if quitButton is None:
            return []
        else:
            return quitButton.get_parent().children

    def getGnomePanelQuit(self):
        """
        Return object of Quit button in gnome-panel menu
        It's the only way how to find out the gnome-panel menu...
        """
        try:
            return root.application('gnome-shell').child('Quit')
        except:
            raise Exception("Quit menu item at gnome-panel menu" +
                            " could not be found!")

    def closeViaGnomePanel(self):
        """
        Close the app via menu at gnome-panel
        """
        internCritical = (self.critical == 'quit')

        if not self.isRunning():
            if internCritical:
                self.updateResult(False)
            #print "!!! The app does not seem to be running"
            return False

        self.openGnomePanelMenu()
        closeButton = self.getGnomePanelQuit()

        sleep(2)  # timeout until menu appear
        #print "*** Trying to click to '%s'" % closeButton
        closeButton.click()
        sleep(self.timeout)

        if self.isRunning():
            if self.forceKill:
                self.kill()
            if internCritical:
                self.updateResult(False)
            #print "!!! The app is running but it shouldn't be"
            return False
        else:
            if self.existsCoreDump() != 0:
                if internCritical:
                    self.updateResult(False)
                # print "!!! The app closed with core dumps. Signal %d" % \
                #        self.existsCoreDump()
                return False
            if internCritical:
                self.updateResult(True)
            #print "*** The app was successfully closed"
            return True
