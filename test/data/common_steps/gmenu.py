# -*- coding: UTF-8 -*-
import logging
logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s',
                    level=logging.INFO)
from behave import step
from dogtail import tree
from dogtail.utils import doDelay
from dogtail.predicate import GenericPredicate


# GApplication menu steps
@step(u'I open GApplication menu')
def get_gmenu(context):
    gs = tree.root.application('gnome-shell')
    logging.debug("gs = %s", gs)
    quit_element = gs.child(roleName='menu', label='Quit')
    logging.debug("quit_element = %s", quit_element)
    if not quit_element.showing:
        gnome_menu = gs.child(roleName='menu')
        logging.debug("gnome_menu = %s", gnome_menu)
        gnome_menu.click()
        doDelay(2)
    return gs.child(roleName='menu', label='Quit').parent.parent.parent.\
        parent.parent


@step(u'I close GApplication menu')
def close_gmenu(context):
    gs = tree.root.application('gnome-shell')
    gs.child(roleName='menu').click()
    doDelay(2)


@step(u'I click menu "{name}" in GApplication menu')
def click_gmenu(context, name):
    logging.debug("context = %s", context)
    gmenu = get_gmenu(context)
    logging.debug("gmenu = %s", gmenu)
    menu_item = gmenu.childLabelled(name)
    logging.debug("menu_item = %s", menu_item)
    menu_item.click()
    doDelay(2)


@step(u'I get submenus from GApplication')
def get_submenus_from_gmenu(context, name):
    return get_gmenu(context).childLabelled(name).parent.findChildren(
        GenericPredicate(roleName='menu item'))
