"""
########################################################################################################################
# Title        : Spine rig module
# Author       : Namrakant Tamrakar
# Created on   : 2/15/2021
# Updated on   : 4/9/2021 (latest update)
# Description  : The function will create the spine control, ikspline handle, curve, cluster and connect it together.
                 Note: The constants will be replaced in the UI creation process using pyside2 by May 15, 2021
########################################################################################################################
"""

import maya.cmds as mc

from ..base import module
from ..base import controllers

def build(
            spineJoints,
            rootJnt,
            spineCurve,
            bodyLocator,
            chestLocator,
            pelvisLocator,
            prefix = 'spine',
            rigScale = 1.0,
            baseRig = None
            ):

    """
    Create the spine control, ikspline handle, curve, cluster and connect it

    @param spineJoints: list( str ), list of spine joints
    @param rootJnt: str, root joint
    @param spineCurve: str, name of spine cubic curve with 5 CVs matching first 5 spine joints
    @param bodyLocator: str, reference transform for position of body control
    @param chestLocator: str, reference transform for position of chest control
    @param pelvisLocator: str, reference transform for position of pelvis control
    @param prefix: str, prefix to name new objects
    @param rigScale: float, scle factor for size of controls
    @param baseRig: instance of bsae.module.Base class
    @return: dictionary with rig module objects
    """

    # make rig module

    rigmodule = module.Module( prefix = prefix, baseObj = baseRig )

    # make spine curve clusters

    spineCurveCVs = mc.ls( spineCurve + '.cv[*]', fl = 1 ) # fl= flatten flag
    numSpineCVs = len( spineCurveCVs )
    spineCurveClusters = []

    for i in range( numSpineCVs ):

        cls = mc.cluster( spineCurveCVs[i] , n=prefix + 'Cluster%d' %(i+1))[1]
        spineCurveClusters.append(cls)
    
    mc.hide( spineCurveClusters )

    # parent spine curve

    mc.parent( spineCurve, rigmodule.partsNoTransGrp )

    # make controls

    bodyCtrl = controllers.Controllers( prefix = prefix + 'Body', translateTo= bodyLocator, scale=rigScale*8,
                                        parent=rigmodule.controlsGrp, shape='circleY'  )
                                        
    chestCtrl = controllers.Controllers( prefix = prefix + 'Chest', translateTo= chestLocator, scale=rigScale*5.5,
                                        parent=bodyCtrl.ctrlObject, shape='circleY' )
                                        
    pelvisCtrl = controllers.Controllers( prefix = prefix + 'Pelvis', translateTo= bodyLocator, scale=rigScale*6,
                                        parent=bodyCtrl.ctrlObject, shape='circleY' )

    middleCtrl = controllers.Controllers( prefix = prefix + 'Middle', translateTo= spineCurveClusters[1], scale=rigScale*4.5,
                                        parent=bodyCtrl.ctrlObject, shape='circleY', lockChannels=[ 'ty', 'r','s','v' ]   )

    # attach controls (middle control)

    mc.parentConstraint( chestCtrl.ctrlObject, pelvisCtrl.ctrlObject , middleCtrl.ctrlOffset, sr = ['x', 'y', 'z'], mo = 1 ) # sr=skip rotation, mo = maintain offset

    # attach clusters (this part is tricky- will depend on the spine curve created in rig)

    mc.parent( spineCurveClusters[2:], chestCtrl.ctrlObject )
    mc.parent( spineCurveClusters[2], middleCtrl.ctrlObject )
    mc.parent( spineCurveClusters[:2], pelvisCtrl.ctrlObject )

    # make IK handle, parent it and hide it

    spineIK = mc.ikHandle( n = prefix + '_ikh', sol = 'ikSplineSolver', sj = spineJoints[0], ee = spineJoints[-1],
                            c = spineCurve, ccv = 0, parentCurve = 0 )[0] # st = start joint, ee=end effector, ccv = create curve
    
    mc.hide( spineIK )
    mc.parent( spineIK, rigmodule.partsNoTransGrp )

    # attach root joint and hide the locators

    mc.parentConstraint( pelvisCtrl.ctrlObject, rootJnt, mo = 1 ) # mo=maintain offset
    mc.orientConstraint( chestCtrl.ctrlObject, 'spine_end_JNT', mo = 1)

    mc.parent( chestLocator, bodyLocator, pelvisLocator, rigmodule.partsNoTransGrp )
    mc.hide( chestLocator, bodyLocator, pelvisLocator )

    return { 'module':rigmodule, 'bodyCtrl':bodyCtrl }