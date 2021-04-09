"""
########################################################################################################################
# Title        : Joint utility module
# Author       : Namrakant Tamrakar
# Created on   : 2/7/2021
# Updated on   : 4/9/2021 (latest update)
# Description  : Functions to list joints and joint related operations
                 Note: The constants will be replaced in the UI creation process using pyside2 by May 15, 2021
########################################################################################################################
"""

import maya.cmds as mc

def listHierarchy( topJoint, withEndJoints = True ):
    """
    List joint hierarchy starting wtih top joint

    @param topJoint: str, joint to get listed with its join hierarchy
    @param withEndJoints: bool, list hierarchy including end joints
    @return: list(str), listed joints starting with top joint 
    """

    listedJoints = mc.listRelatives( topJoint, type = 'joint', ad = True ) # ad= all descendants
    listedJoints.append( topJoint )
    listedJoints.reverse()

    completeJoints = listedJoints[:]    # copying the whole list, not an instance copy

    if not withEndJoints:

        completeJoints = [ j for j in listedJoints if mc.listRelatives( j, c=1, type = 'joint' ) ] # c= child

    return completeJoints