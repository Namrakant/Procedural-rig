"""
########################################################################################################################
# Title        : Leg rig module
# Author       : Namrakant Tamrakar
# Created on   : 2/28/2021
# Updated on   : 4/9/2021 (latest update)
# Description  : The function will create the leg controls, FK/IK switch and connect it together.
                 Note: The constants will be replaced in the UI creation process using pyside2 by May 15, 2021
########################################################################################################################
"""

import maya.cmds as mc

from ..base import module
from ..base import controllers

from ..utils import joint
from ..utils import name

def build(
        legJoints,
        pvLocator,
        FKIK_locator,
        topToeJoints = None,
        pelvisJnt = None,
        prefix = 'L_leg',
        rigScale = 1.0,
        baseRig = None
        ):

    """
    Create the leg controls, FK/IK switch and connect it together

    @param legJoints: list(str), shoulder - elbow - ankle - ball - end toe
    @param pvLocator: str, reference locator for position of Pole Vector control
    @param FKIK_locator: str, reference to locator for position of FK IK switch control
    @param topToeJoints: list(str), top metacarpal toe joints
    @param pelvisJnt: str, optional, pelvis joint, parent of top leg joint
    @param prefix: str, prefix to name new objects
    @param rigScale: float, scale factor for size of controls
    @param baseRig: baseRig, instance of base.module.Base class
    @return: dictionary with rig module objects
    """

    # make rig module

    rigmodule = module.Module( prefix = prefix, baseObj = baseRig )

    # make attach groups

    bodyAttachGrp = mc.group( n = prefix + 'BodyAttach_grp', em = 1, p = rigmodule.partsGrp )
    baseAttachGrp = mc.group( n = prefix + 'BaseAttach_grp', em = 1, p = rigmodule.partsGrp )

    # make IK controls for pelvis (quadruped), foot, ball, fingers

    if pelvisJnt:

        pelvisCtrl_IK = controllers.Controllers( prefix = prefix + 'pelvis' , translateTo= pelvisJnt, rotateTo= pelvisJnt,
                                               scale = rigScale * 3.5, parent= rigmodule.controlsGrp, shape= "sphere",
                                               lockChannels= ['ty','rx', 'rz','s', 'v' ] )
    
    footCtrl_IK = controllers.Controllers( prefix =  prefix + 'Foot', translateTo= legJoints[2], scale =  rigScale * 3 ,
                                        parent= rigmodule.controlsGrp, shape='circleY', lockChannels= ['s'] )

    if len(legJoints) > 3: 
        ballCtrl_IK = controllers.Controllers( prefix =  prefix + 'Ball', translateTo= legJoints[3], rotateTo= legJoints[3], scale =  rigScale * 2 ,
                                            parent= rigmodule.controlsGrp, shape='circleX', lockChannels= ['s'] )
                                        
    poleVectorCtrl = controllers.Controllers( prefix =  prefix + 'PV', translateTo= pvLocator, scale =  rigScale  ,
                                        parent= rigmodule.controlsGrp, shape='sphere', lockChannels= ['s'] )
    
    if topToeJoints:
        toeIKControls = []

        for topToeJnt in topToeJoints:
            
            toePrefix = name.removeSuffix( topToeJnt )[:-1]
            toeEndJnt = mc.listRelatives( topToeJnt, ad = 1, type = 'joint' )[0] # ad = all descendants

            toeIKCtrl = controllers.Controllers( prefix = toePrefix, translateTo= toeEndJnt, scale = rigScale*0.5, 
                                                parent = footCtrl_IK.ctrlObject, shape= 'circleY' )

            toeIKControls.append( toeIKCtrl )
    
    # make FK controls for foot, knee, ankle, ball, fingers
    
    hipCtrl_FK = controllers.Controllers( prefix = prefix + 'hip_FK', translateTo= legJoints[0], rotateTo= legJoints[0], scale= rigScale * 4,
                                          parent= rigmodule.controlsGrp, shape='circleX', lockChannels= ['t','s', 'v'] )
                                          
    kneeCtrl_FK = controllers.Controllers( prefix = prefix + 'knee_FK', translateTo= legJoints[1], rotateTo= legJoints[1], scale= rigScale * 2.7,
                                          parent= hipCtrl_FK.ctrlObject, shape='circleX', lockChannels= ['t','s', 'rx','ry', 'v'] )
                                          
    ankleCtrl_FK = controllers.Controllers( prefix = prefix + 'ankle_FK', translateTo= legJoints[2], scale= rigScale * 2.3,
                                          parent= kneeCtrl_FK.ctrlObject, shape='circleY', lockChannels= ['t','s', 'v'] )
                                          
    ballCtrl_FK = controllers.Controllers( prefix = prefix + 'ball_FK', translateTo= legJoints[3], rotateTo= legJoints[3], scale= rigScale * 2.3,
                                          parent= ankleCtrl_FK.ctrlObject, shape='circleX', lockChannels= ['t','s', 'v'] )

    if topToeJoints: 
        toeFKControls = []
        i = 1   
        for topToeJnt in topToeJoints:
            if i > 3:
                continue

            toePrefix = name.removeSuffix( topToeJnt )[i]

            toeFKCtrl = controllers.Controllers(prefix = toePrefix + '_FK', translateTo= topToeJnt[i], rotateTo= topToeJnt[i], scale= rigScale,
                                                parent= ankleCtrl_FK.ctrlObject, shape= 'circleX', lockChannels= ['t','s', 'v'] )

            i = i + 1

    # make IK handles for pelvis (quadruped), foot, ball, fingers

    if pelvisJnt:

        pelvisIK = mc.ikHandle( n= prefix + 'pelvis_ikh', sol = 'ikSCsolver', sj = pelvisJnt, ee = legJoints[0] )[0]
        mc.hide( pelvisIK )

    legIK = mc.ikHandle( n = prefix + 'Main_ikh', sol = 'ikRPsolver', sj = legJoints[0], ee = legJoints[2])[0] # sj = start joint, ee= end effector
    
    if len(legJoints) > 3: 
        ballIK = mc.ikHandle( n = prefix + 'Ball_ikh', sol = 'ikRPsolver', sj = legJoints[2], ee = legJoints[3], dh = True )[0] #  dh = disable handle
        mainToeIK = mc.ikHandle( n = prefix + 'MainToe_ikh', sol = 'ikRPsolver', sj = legJoints[3], ee = legJoints[4], dh = True )[0] # eh = enable handle
        mc.hide( ballIK, mainToeIK )

    mc.hide( legIK )

    if topToeJoints:

        for i, topToeJnt in enumerate( topToeJoints ): # enumerate function gives both the name of object and index
            toePrefix = name.removeSuffix( topToeJnt )[:-1]
            toeJoints = joint.listHierarchy( topToeJnt )

            toeIK = mc.ikHandle( n = toePrefix + '_ikh', sol = 'ikSCsolver', sj = toeJoints[1], ee = toeJoints[-1] )[0]

            mc.hide( toeIK )
            mc.parent( toeIK, toeIKControls[i].ctrlObject )

    # attach IK controls to Pole vector

    mc.parentConstraint( bodyAttachGrp, poleVectorCtrl.ctrlOffset, mo = 1 )
    
    if pelvisJnt:

        mc.parentConstraint( baseAttachGrp, pelvisCtrl_IK.ctrlOffset, mo = 1 )
    
    # attach IK objects to controls

    mc.parent( legIK, footCtrl_IK.ctrlObject )
    
    if len(legJoints) > 3: 
        mc.parent( ballIK, mainToeIK, ballCtrl_IK.ctrlObject )
        mc.parent( ballCtrl_IK.ctrlOffset, footCtrl_IK.ctrlObject )

    mc.poleVectorConstraint( poleVectorCtrl.ctrlObject, legIK )
    mc.orientConstraint( footCtrl_IK.ctrlObject, legJoints[-1], mo = 1 )

    if pelvisJnt:

        mc.parent( pelvisIK, pelvisCtrl_IK.ctrlObject )
        mc.pointConstraint( pelvisCtrl_IK.ctrlObject, pelvisJnt )
       
    # FK IK switch Control and connection

    FKIK_ctrl = controllers.Controllers(  prefix= prefix + '_FKIK', scale= rigScale, translateTo= FKIK_locator, parent= rigmodule.controlsGrp , 
                                          shape='circleY', lockChannels= ['t', 'r', 's']  )

    mc.parentConstraint( legJoints[2] , FKIK_ctrl.ctrlOffset , mo = 1)
    mc.addAttr( FKIK_ctrl.ctrlObject, ln = 'FK_IK_Switch', at = 'enum' , enumName = 'FK:IK', k = 1, dv = 0) # ln= long name, k=keyable, dv= default value

    # attach FK controls to the joints
    
    mc.orientConstraint( hipCtrl_FK.ctrlObject, legJoints[0], mo = 1 )
    mc.orientConstraint( kneeCtrl_FK.ctrlObject, legJoints[1], mo = 1  )
    mc.orientConstraint( ankleCtrl_FK.ctrlObject, legJoints[2], mo = 1  )
    mc.orientConstraint( ballCtrl_FK.ctrlObject, legJoints[3], mo = 1  )

    # make pole vector connection line

    pvLinePos1 = mc.xform( legJoints[1], q = 1, t = 1, ws = 1 ) # q = query, t=template, ws = world space
    pvLinePos2 = mc.xform( pvLocator, q = 1, t = 1, ws = 1 ) # q = query, t=template, ws = world space
    poleVectorCrv = mc.curve( n = prefix + 'Pv_crv', d = 1 , p = [pvLinePos1, pvLinePos2]) # d = degree, p = position
    mc.cluster( poleVectorCrv + '.cv[0]', n = prefix + 'Pv1_cls', wn = [ legJoints[1], legJoints[1] ], bs = True  ) # wn = weighted node option for cluster, 
    mc.cluster( poleVectorCrv + '.cv[1]', n = prefix + 'Pv2_cls', wn = [ poleVectorCtrl.ctrlObject, poleVectorCtrl.ctrlObject ], bs = True  ) # bs = bind state through so it doesn't offset the cluster
    mc.parent( poleVectorCrv, rigmodule.controlsGrp )
    mc.setAttr( poleVectorCrv + '.template', 1 )
    mc.setAttr( poleVectorCrv + '.inheritsTransform', 0, l = 1 )

    # FK Switch - set driven key

    mc.setAttr( FKIK_ctrl.ctrlObject + '.FK_IK_Switch', 0 )

    mc.setAttr( hipCtrl_FK.ctrlOffset + '.v', 1 )
    mc.setAttr( poleVectorCtrl.ctrlOffset + '.v', 0 )
    mc.setAttr( footCtrl_IK.ctrlOffset + '.v', 0 )
    mc.setAttr( poleVectorCrv + '.v', 0 )
    
    mc.setAttr( legIK + '.ikBlend', 0 )      # ikBlend to 0, i.e. FK
    
    if len(legJoints) > 3:
        mc.setAttr( ballIK + '.ikBlend', 0 )     
        mc.setAttr( mainToeIK + '.ikBlend', 0 )  
        mc.setDrivenKeyframe( ballIK + '.ikBlend'  , cd = FKIK_ctrl.ctrlObject + '.FK_IK_Switch'  ) #cd = current driver
        mc.setDrivenKeyframe( mainToeIK + '.ikBlend'  , cd = FKIK_ctrl.ctrlObject + '.FK_IK_Switch'  )

    mc.setDrivenKeyframe( hipCtrl_FK.ctrlOffset + '.v'  , cd = FKIK_ctrl.ctrlObject + '.FK_IK_Switch'  ) 
    mc.setDrivenKeyframe( poleVectorCtrl.ctrlOffset + '.v'  , cd = FKIK_ctrl.ctrlObject + '.FK_IK_Switch'  ) 
    mc.setDrivenKeyframe( footCtrl_IK.ctrlOffset + '.v'  , cd = FKIK_ctrl.ctrlObject + '.FK_IK_Switch'  ) 
    mc.setDrivenKeyframe( legIK + '.ikBlend'  , cd = FKIK_ctrl.ctrlObject + '.FK_IK_Switch'  ) 
    mc.setDrivenKeyframe( poleVectorCrv + '.v'  , cd = FKIK_ctrl.ctrlObject + '.FK_IK_Switch'  ) 
    
    # IK Switch - set driven key

    mc.setAttr( FKIK_ctrl.ctrlObject + '.FK_IK_Switch', 1 )

    mc.setAttr( hipCtrl_FK.ctrlOffset + '.v', 0 )
    mc.setAttr( poleVectorCtrl.ctrlOffset + '.v', 1 )
    mc.setAttr( footCtrl_IK.ctrlOffset + '.v', 1 )
    mc.setAttr( poleVectorCrv + '.v', 1 )
    
    mc.setAttr( legIK + '.ikBlend', 1 )     # ikBlend to 1, i.e. IK

    if len(legJoints) > 3:
        mc.setAttr( ballIK + '.ikBlend', 1 )     
        mc.setAttr( mainToeIK + '.ikBlend', 1 )  
        mc.setDrivenKeyframe( ballIK + '.ikBlend'  , cd = FKIK_ctrl.ctrlObject + '.FK_IK_Switch'  ) 
        mc.setDrivenKeyframe( mainToeIK + '.ikBlend'  , cd = FKIK_ctrl.ctrlObject + '.FK_IK_Switch'  ) 

    mc.setDrivenKeyframe( hipCtrl_FK.ctrlOffset + '.v'  , cd = FKIK_ctrl.ctrlObject + '.FK_IK_Switch'  ) 
    mc.setDrivenKeyframe( poleVectorCtrl.ctrlOffset + '.v'  , cd = FKIK_ctrl.ctrlObject + '.FK_IK_Switch'  ) 
    mc.setDrivenKeyframe( footCtrl_IK.ctrlOffset + '.v'  , cd = FKIK_ctrl.ctrlObject + '.FK_IK_Switch'  ) 
    mc.setDrivenKeyframe( legIK + '.ikBlend'  , cd = FKIK_ctrl.ctrlObject + '.FK_IK_Switch'  ) 
    mc.setDrivenKeyframe( poleVectorCrv + '.v'  , cd = FKIK_ctrl.ctrlObject + '.FK_IK_Switch'  )

    # parenting and cleanup

    mc.parent( pvLocator, rigmodule.partsNoTransGrp )
    mc.parent( FKIK_locator, rigmodule.partsNoTransGrp )
    mc.hide( pvLocator, FKIK_locator )

    return { 'module':rigmodule, 'baseAttachGrp':baseAttachGrp, 'bodyAttachGrp':bodyAttachGrp }