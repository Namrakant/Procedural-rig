"""
########################################################################################################################
# Title        : Class for making rig controls
# Author       : Namrakant Tamrakar
# Created on   : 2/1/2021
# Updated on   : 4/9/2021 (latest update)
# Description  : This class will create a controller and its offset group, will color the controller based on the input.
                 It will also give a shape to the controller and can translate/rotate it to a specified object.
                 Note: The constants will be replaced in the UI creation process using pyside2 by May 15, 2021
########################################################################################################################
"""

import maya.cmds as mc

class Controllers():
    """
    Class for building the rig controls and offset group
    
    """

    def __init__(self, 
                 prefix = 'new', 
                 scale = 1.0, 
                 translateTo = '',
                 rotateTo = '',
                 parent = '',
                 shape = 'circle',
                 lockChannels = ['s','v']
                 ):
        
        """
        Creating the controller and its offset group, coloring it based on its name, changing the shape based on the input

        @param prefix: str, prefix to name new objects
        @param scale: float, general scale of the rig
        @param translateTo: str, reference object for control position
        @param rotateTo: str, reference object for control orientation
        @param parent: str, object to be parent of new control
        @param shape: str, controller shpe type
        @param lockChannels: list(str), list of channels on control to be locked and non-keyable
        @return: None
        """

        # creating the shape of the NURBS controls and parenting under the offset group

        ctrlObject = None
        circleNormal = [1,0,0]

        if shape in ['circle', 'circleX']:
            circleNormal = [1,0,0]
        elif shape == 'circleY':
            circleNormal = [0,1,0]
        elif shape == 'circleZ':
            circleNormal = [0,0,1]
        elif shape == 'sphere':
            ctrlObject = mc.circle( n = prefix + '_ctl', ch = False, normal = [1,0,0], radius = scale )[0]
            addShape = mc.circle( n = prefix + '_ctl', ch = False, normal = [0,0,1], radius = scale )[0]
            mc.parent( mc.listRelatives( addShape, s = 1 ), ctrlObject, r = 1, s = 1 )
            mc.delete( addShape )

        if not ctrlObject:

            ctrlObject = mc.circle( n = prefix + '_ctrl', ch = False, normal = circleNormal, radius = scale )[0] #ch = channel history

        ctrlOffset = mc.group( n = prefix + 'Offset_grp', em = 1 )
        mc.parent( ctrlObject, ctrlOffset )

        # color control

        ctrlShapes = mc.listRelatives( ctrlObject, s = 1) # s= shape
        [ mc.setAttr( s + '.ove', 1 ) for s in ctrlShapes ] # ove= override enable

        if prefix.startswith('L_'): # for naming convention and coloring based on that
            [ mc.setAttr( s + '.ovc', 6)  for s in ctrlShapes ] #ovc= override color, 6 = blue

        elif prefix.startswith('R_'):
            [ mc.setAttr( s +'.ovc', 13 )  for s in ctrlShapes ] #13 = red

        else:
            [ mc.setAttr( s + '.ovc', 22)  for s in ctrlShapes ] #22 = yellow

        # translate control

        if mc.objExists( translateTo ):
            mc.delete(mc.pointConstraint( translateTo, ctrlOffset ) )

        # rotate control

        if mc.objExists( rotateTo ):
            mc.delete(mc.orientConstraint( rotateTo, ctrlOffset ) )

        # parent control

        if mc.objExists( parent ):
            mc.parent( ctrlOffset, parent )

        # lock control channels

        singleAttributeLockList = []

        for lockChannel in lockChannels:
            if lockChannel in ['t','r','s']:
                for axis in ['x','y','z']:
                    at = lockChannel + axis
                    singleAttributeLockList.append(at)
            
            else:
                singleAttributeLockList.append( lockChannel )
            
        for at in singleAttributeLockList:
            mc.setAttr( ctrlObject + '.' + at, l = 1, k = 0) # l = lock, k = keyable
        

        # add public members for the control and its offset group

        self.ctrlObject = ctrlObject
        self.ctrlOffset = ctrlOffset