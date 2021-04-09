"""
########################################################################################################################
# Title        : Tranform utility module
# Author       : Namrakant Tamrakar
# Created on   : 2/7/2021
# Updated on   : 4/9/2021 (latest update)
# Description  : Functions to manipulate and create transforms
                 Note: The constants will be replaced in the UI creation process using pyside2 by May 15, 2021
########################################################################################################################
"""

import maya.cmds as mc

from . import name

def makeOffsetGrp( object, prefix = ''):
    """ 
    Make offset group for given object

    @param object: transform object to get offset group
    @param prefix: str, prefix to name new objects
    @return: str, name of new offset group
    """

    # create offset group

    if not prefix:

        prefix = name.removeSuffix( object )

    offsetGrp = mc.group( n = prefix + 'Offset_grp', em = 1) # em= empty

    objectParents = mc. listRelatives( object, p = 1 )

    if objectParents:

        mc.parent( offsetGrp,objectParents[0] )
    
    # match object transform

    mc.delete( mc.parentConstraint( object, offsetGrp) )
    mc.delete( mc.scaleConstraint( object, offsetGrp) )

    # parent object under offset group

    mc.parent( object, offsetGrp )

    return offsetGrp