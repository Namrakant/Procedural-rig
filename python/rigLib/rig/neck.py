"""
########################################################################################################################
# Title        : Neck rig module
# Author       : Namrakant Tamrakar
# Created on   : 2/21/2021
# Updated on   : 4/9/2021 (latest update)
# Description  : The function will create the neck and head controls, FK and connect it together.
                 Note: The constants will be replaced in the UI creation process using pyside2 by May 15, 2021
########################################################################################################################
"""

import maya.cmds as mc

from ..base import module
from ..base import controllers

def build(
            neckJoints,
            headJnt,
            neckCurve,
            prefix = 'neck',
            rigScale = 1.0,
            baseRig = None
            ):

    """
    Create the neck and head controls, FK and connect it together

    @param neckJoints: list( str ), list of neck joints
    @param jeadJnt: str, head joint
    @param neckCurve: str, name of neck cubic curve with 5 CVs matching first 5 neck joints
    @param prefix: str, prefix to name new objects
    @param rigScale: float, scle factor for size of controls
    @param baseRig: instance of bsae.module.Base class
    @return: dictionary with rig module objects
    """

    # make rig module

    rigmodule = module.Module( prefix = prefix, baseObj = baseRig )

    # make attach groups

    bodyAttachGrp = mc.group( n = prefix + 'BodyAttach_grp', em =1, p =  rigmodule.partsGrp )
    baseAttachGrp = mc.group( n = prefix + 'BaseAttach_grp', em =1, p =  rigmodule.partsGrp )
    
    mc.delete( mc.pointConstraint( neckJoints[0] , baseAttachGrp ) )

    # make neck and head controls

    headLocalCtrl = controllers.Controllers( prefix = prefix + 'HeadLocal', translateTo= headJnt , rotateTo= headJnt, 
                                             scale= rigScale * 6, parent = rigmodule.controlsGrp, shape='circle' )

    middleCtrl = controllers.Controllers( prefix = prefix + 'Middle', translateTo= neckJoints[0] , rotateTo= neckJoints[0], 
                                          scale= rigScale * 3, parent = rigmodule.controlsGrp, shape='circleX' )

    # attach controls

    mc.parentConstraint( 'spine_end_JNT', middleCtrl.ctrlOffset, mo = 1 )
    mc.parentConstraint( neckJoints[0], headLocalCtrl.ctrlOffset, mo = 1 )

    # attach joints

    mc.parentConstraint( headLocalCtrl.ctrlObject, headJnt, mo = 1 )
    mc.parentConstraint( middleCtrl.ctrlObject, neckJoints[0], mo = 1 )
    
    return { 'module':rigmodule, 'baseAttachGrp':baseAttachGrp, 'bodyAttachGrp':bodyAttachGrp }
