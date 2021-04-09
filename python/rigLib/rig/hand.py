"""
########################################################################################################################
# Title        : Hand rig module
# Author       : Namrakant Tamrakar
# Created on   : 2/28/2021
# Updated on   : 4/9/2021 (latest update)
# Description  : The function will create the hand controls, FK/IK switch and connect it together.
                 Note: The constants will be replaced in the UI creation process using pyside2 by May 15, 2021
########################################################################################################################
"""

import maya.cmds as mc

from ..base import module
from ..base import controllers

from ..utils import joint
from ..utils import name

def build(
        handJoints,
        pvLocator,
        FKIK_locator,
        topfingerJoints = None,
        scapulaJnt = None,
        prefix = 'L_hand',
        rigScale = 1.0,
        baseRig = None
        ):

    """
    Create the hand controls, FK/IK switch and connect it together

    @param handJoints: list(str), shoulder - elbow - wrist
    @param pvLocator: str, reference locator for position of Pole Vector control
    @param FKIK_locator: str, reference to locator for position of FK IK switch control
    @param topfingerJoints: list(str), top metacarpal finger joints
    @param scapulaJnt: str, optional, scapula joint, parent of top hand joint
    @param prefix: str, prefix to name new objects
    @param rigScale: float, scale factor for size of controls
    @param baseRig: baseRig, instance of base.module.Base class
    @return: dictionary with rig module objects
    """

    # make rig module

    rigmodule = module.Module( prefix = prefix, baseObj = baseRig )

    # make attach groups and set their pivot to the respective objects

    bodyAttachGrp = mc.group( n = prefix + 'BodyAttach_grp', em = 1, p = rigmodule.partsGrp )
    baseAttachGrp = mc.group( n = prefix + 'BaseAttach_grp', em = 1, p = rigmodule.partsGrp )
    fingerControlGrp = mc.group( n = prefix + 'Fingers_grp', em = 1, p = rigmodule.partsGrp )
    fingerIKControlGrp = mc.group( n = prefix + 'Fingers_IK_grp', em = 1, p = fingerControlGrp )
    fingerFKControlGrp = mc.group( n = prefix + 'Fingers_FK_grp', em = 1, p = fingerControlGrp )
    
    mc.delete( mc.parentConstraint( 'L_wrist_JNT', fingerControlGrp, mo = 0 ) )
    mc.delete( mc.parentConstraint( 'L_wrist_JNT', fingerIKControlGrp, mo = 0 ) )
    mc.delete( mc.parentConstraint( 'L_wrist_JNT', fingerFKControlGrp, mo = 0 ) )
    
    # make IK controls for scapula, wrist, fingers

    scapulaCtrl_IK = controllers.Controllers( prefix = prefix + 'Scapula_IK' , translateTo= scapulaJnt, rotateTo= scapulaJnt,
                                               scale = rigScale * 3.5, parent= rigmodule.controlsGrp, shape= "sphere",
                                               lockChannels= ['ty','rx', 'rz','s', 'v' ] )
    
    wristCtrl_IK = controllers.Controllers( prefix =  prefix + 'wrist_IK', translateTo= handJoints[2], rotateTo=handJoints[2], scale =  rigScale * 3 ,
                                        parent= rigmodule.controlsGrp, shape='circleX', lockChannels= ['s'] )
                     
    poleVectorCtrl = controllers.Controllers( prefix =  prefix + 'IK_PV', translateTo= pvLocator, scale =  rigScale  ,
                                        parent= rigmodule.controlsGrp, shape='sphere', lockChannels= ['s'] )
    
    if topfingerJoints:
        fingerIKControls = []

        for topfingerJnt in topfingerJoints:
            
            fingerPrefix = name.removeSuffix( topfingerJnt )[:-1]
            fingerEndJnt = mc.listRelatives( topfingerJnt, ad = 1, type = 'joint' )[0] # ad = all descendants

            fingerIKCtrl = controllers.Controllers( prefix = fingerPrefix + 'IK', translateTo= fingerEndJnt, rotateTo=fingerEndJnt,  scale = rigScale*0.5, 
                                                parent = fingerIKControlGrp, shape= 'circleX', lockChannels= ['r','s'] )

            fingerIKControls.append( fingerIKCtrl )
    
    # make FK controls for upperarm, elbow, wrist, fingers
    
    upperArmCtrl_FK = controllers.Controllers( prefix = prefix + 'upperArm_FK', translateTo= handJoints[0], rotateTo= handJoints[0], scale= rigScale * 3,
                                          parent= scapulaCtrl_IK.ctrlObject, shape='circleX', lockChannels= ['t','s'] )
                                          
    elbowCtrl_FK = controllers.Controllers( prefix = prefix + 'elbow_FK', translateTo= handJoints[1], rotateTo= handJoints[1], scale= rigScale * 2,
                                          parent= upperArmCtrl_FK.ctrlObject, shape='circleX', lockChannels= ['t','s', 'rx','ry'] )
                                          
    wristCtrl_FK = controllers.Controllers( prefix = prefix + 'wrist_FK', translateTo= handJoints[2], rotateTo=handJoints[2],  scale= rigScale * 2,
                                          parent= elbowCtrl_FK.ctrlObject, shape='circleX', lockChannels= ['t','s'] )
               
    if topfingerJoints: 
        fingerFKControls = []
        fingerJoints = []

        for topfingerJnt in topfingerJoints:
            
            finger_parent_grp = fingerFKControlGrp
            fingerJoints = mc.listRelatives( topfingerJnt, ad = 1, type = 'joint' ) # ad = all descendants
            fingerJoints.reverse()
            i = 0
            fingerscale = rigScale*0.8

            for fingerJnt in fingerJoints:
                fingerscale = fingerscale - 0.1
                if i == len(fingerJoints) - 1: 
                    i = i + 1
                    continue
                
                fingerPrefix = name.removeSuffix( fingerJnt )[:-1]
                    
                fingerFKCtrl = controllers.Controllers(prefix = fingerPrefix + str(i) + 'FK', translateTo= fingerJnt, rotateTo= fingerJnt, scale= fingerscale,
                                                    parent= finger_parent_grp, shape= 'circleX', lockChannels= ['t','s'] )

                fingerFKControls.append( fingerFKCtrl )
                mc.orientConstraint( fingerFKCtrl.ctrlObject, fingerJnt , mo = 1 )

                i = i + 1

                finger_parent_grp = fingerFKCtrl.ctrlObject

    # FK IK switch control and attribute

    FKIK_ctrl = controllers.Controllers(  prefix= prefix + '_FKIK', scale= rigScale, translateTo= FKIK_locator, parent= rigmodule.controlsGrp , 
                                          shape='circleX', lockChannels= ['t', 'r', 's']  )

    mc.parentConstraint( handJoints[2]  , FKIK_ctrl.ctrlOffset , mo = 1)
    mc.addAttr( FKIK_ctrl.ctrlObject, ln = 'Arm_FK_IK_Switch', at = 'enum' , enumName = 'FK:IK', k = 1, dv = 0) #ln= long name, k=keyable, dv= default value for display type, 2=reference

    if topfingerJoints:

        for i, topfingerJnt in enumerate( topfingerJoints ): # enumerate function gives both the name of object and index
            fingerPrefix = name.removeSuffix( topfingerJnt )[:-1]
            
            mc.addAttr( FKIK_ctrl.ctrlObject, ln = fingerPrefix + 'FK_IK_Switch', at = 'enum' , enumName = 'FK:IK', k = 1, dv = 0) #ln= long name, k=keyable, dv= default value for display type, 2=reference

    # make IK handles for scapula, hand, fingers

    scapulaIK = mc.ikHandle( n= prefix + 'Scapula_ikh', sol = 'ikSCsolver', sj = scapulaJnt, ee = handJoints[0] )[0]
    mc.hide( scapulaIK )

    handIK = mc.ikHandle( n = prefix + 'Main_ikh', sol = 'ikRPsolver', sj = handJoints[0], ee = handJoints[2])[0] #sj = start joint

    mc.hide( handIK )

    if topfingerJoints:

        for i, topfingerJnt in enumerate( topfingerJoints ): # enumerate function gives both the name of object and index
            fingerPrefix = name.removeSuffix( topfingerJnt )[:-1]
            fingerJoints = joint.listHierarchy( topfingerJnt )

            fingerIK = mc.ikHandle( n = fingerPrefix + 'ikh', sol = 'ikSCsolver', sj = fingerJoints[1], ee = fingerJoints[-1] )[0]

            mc.hide( fingerIK )
            mc.parent( fingerIK, fingerIKControls[i].ctrlObject )

    # attach IK controls

    mc.parentConstraint( bodyAttachGrp, poleVectorCtrl.ctrlOffset, mo = 1 )
    
    if scapulaJnt:

        mc.parentConstraint( baseAttachGrp, scapulaCtrl_IK.ctrlOffset, mo = 1 )
    
    # attach IK objects to controls

    mc.parent( handIK, wristCtrl_IK.ctrlObject )

    mc.poleVectorConstraint( poleVectorCtrl.ctrlObject, handIK )
    wristCtrl_IK_orient = mc.orientConstraint( wristCtrl_IK.ctrlObject, handJoints[-1], mo = 1 )

    if scapulaJnt:

        mc.parent( scapulaIK, scapulaCtrl_IK.ctrlObject )
        mc.pointConstraint( scapulaCtrl_IK.ctrlObject, scapulaJnt )
       
    # attach FK controls 
    
    mc.orientConstraint( upperArmCtrl_FK.ctrlObject, handJoints[0], mo = 1 )
    mc.orientConstraint( elbowCtrl_FK.ctrlObject, handJoints[1], mo = 1  )
    wristCtrl_FK_orient = mc.orientConstraint( wristCtrl_FK.ctrlObject, handJoints[2], mo = 1  )
    
    # make pole vector connection line

    pvLinePos1 = mc.xform( handJoints[1], q = 1, t = 1, ws = 1 ) #q = query, t=template, ws = world space
    pvLinePos2 = mc.xform( pvLocator, q = 1, t = 1, ws = 1 ) #q = query, t=template, ws = world space
    poleVectorCrv = mc.curve( n = prefix + 'Pv_crv', d = 1 , p = [pvLinePos1, pvLinePos2]) # d = degree, p = position
    mc.cluster( poleVectorCrv + '.cv[0]', n = prefix + 'Pv1_cls', wn = [ handJoints[1], handJoints[1] ], bs = True  ) #wn = weighted node option for cluster, bs = bind state through so it doesn't offset the cluster
    mc.cluster( poleVectorCrv + '.cv[1]', n = prefix + 'Pv2_cls', wn = [ poleVectorCtrl.ctrlObject, poleVectorCtrl.ctrlObject ], bs = True  ) #wn = weighted node option for cluster, bs = bind state through so it doesn't offset the cluster
    mc.parent( poleVectorCrv, rigmodule.controlsGrp )
    mc.setAttr( poleVectorCrv + '.template', 1 )
    mc.setAttr( poleVectorCrv + '.inheritsTransform', 0, l = 1 )
               
    wrist_FK_IK_fingers_follow = mc.parentConstraint( wristCtrl_IK.ctrlObject, wristCtrl_FK.ctrlObject , fingerControlGrp, mo = 1 )

    # IK Switch - set driven key

    mc.setAttr( FKIK_ctrl.ctrlObject + '.Arm_FK_IK_Switch', 1 )

    mc.setAttr( upperArmCtrl_FK.ctrlOffset + '.v', 0 )
    mc.setAttr( poleVectorCtrl.ctrlOffset + '.v', 1 )
    mc.setAttr( wristCtrl_IK.ctrlOffset + '.v', 1 )
    mc.setAttr( poleVectorCrv + '.v', 1 )
    mc.setAttr( wrist_FK_IK_fingers_follow[0] + '.' + wristCtrl_IK.ctrlObject + 'W0', 1 )
    mc.setAttr( wrist_FK_IK_fingers_follow[0] + '.' + wristCtrl_FK.ctrlObject + 'W1', 0 )
    mc.setAttr( wristCtrl_FK_orient[0] + '.' + wristCtrl_IK.ctrlObject + 'W0', 1 )
    mc.setAttr( wristCtrl_FK_orient[0] + '.' + wristCtrl_FK.ctrlObject + 'W1', 0 )
    
    mc.setAttr( handIK + '.ikBlend', 1 )     # ikBlend to 1, i.e. IK
        
    if topfingerJoints:

        for i, topfingerJnt in enumerate( topfingerJoints ): # enumerate function gives both the name of object and index
            fingerPrefix = name.removeSuffix( topfingerJnt )[:-1]
            
            mc.setAttr( FKIK_ctrl.ctrlObject + '.' + fingerPrefix + 'FK_IK_Switch', 1 )
            mc.setAttr( fingerPrefix  + 'ikh.ikBlend', 1 )    
            mc.setAttr( fingerPrefix + 'IKOffset_grp.v', 1 ) 
            mc.setAttr( fingerPrefix + '0FKOffset_grp.v', 0 )
   
    mc.setDrivenKeyframe( upperArmCtrl_FK.ctrlOffset + '.v'  , cd = FKIK_ctrl.ctrlObject + '.Arm_FK_IK_Switch'  ) #cd = current driver
    mc.setDrivenKeyframe( poleVectorCtrl.ctrlOffset + '.v'  , cd = FKIK_ctrl.ctrlObject + '.Arm_FK_IK_Switch'  )
    mc.setDrivenKeyframe( wristCtrl_IK.ctrlOffset + '.v'  , cd = FKIK_ctrl.ctrlObject + '.Arm_FK_IK_Switch'  )  
    mc.setDrivenKeyframe( poleVectorCrv + '.v'  , cd = FKIK_ctrl.ctrlObject + '.Arm_FK_IK_Switch'  )  
    mc.setDrivenKeyframe( handIK + '.ikBlend'  , cd = FKIK_ctrl.ctrlObject + '.Arm_FK_IK_Switch'  )  
    mc.setDrivenKeyframe( wrist_FK_IK_fingers_follow[0] + '.'+ wristCtrl_IK.ctrlObject + 'W0' , cd = FKIK_ctrl.ctrlObject + '.Arm_FK_IK_Switch'  )  
    mc.setDrivenKeyframe( wrist_FK_IK_fingers_follow[0] + '.'+ wristCtrl_FK.ctrlObject + 'W1' , cd = FKIK_ctrl.ctrlObject + '.Arm_FK_IK_Switch'  )  
    mc.setDrivenKeyframe( wristCtrl_FK_orient[0] + '.'+ wristCtrl_IK.ctrlObject + 'W0' , cd = FKIK_ctrl.ctrlObject + '.Arm_FK_IK_Switch'  )  
    mc.setDrivenKeyframe( wristCtrl_FK_orient[0] + '.'+ wristCtrl_FK.ctrlObject + 'W1' , cd = FKIK_ctrl.ctrlObject + '.Arm_FK_IK_Switch'  )  

    if topfingerJoints:

        for i, topfingerJnt in enumerate( topfingerJoints ): # enumerate function gives both the name of object and 
      
            fingerPrefix = name.removeSuffix( topfingerJnt )[:-1]
            
            mc.setDrivenKeyframe( fingerPrefix + 'ikh.ikBlend'  , cd = FKIK_ctrl.ctrlObject + '.' + fingerPrefix + 'FK_IK_Switch'  )  
            mc.setDrivenKeyframe( fingerPrefix + 'IKOffset_grp.v'   , cd = FKIK_ctrl.ctrlObject + '.' + fingerPrefix + 'FK_IK_Switch'  )  
            mc.setDrivenKeyframe( fingerPrefix + '0FKOffset_grp.v'  , cd = FKIK_ctrl.ctrlObject + '.' + fingerPrefix + 'FK_IK_Switch'  )  
            
            
    # FK Switch - set driven key

    mc.setAttr( FKIK_ctrl.ctrlObject + '.Arm_FK_IK_Switch', 0 )

    mc.setAttr( upperArmCtrl_FK.ctrlOffset + '.v', 1 )
    mc.setAttr( poleVectorCtrl.ctrlOffset + '.v', 0 )
    mc.setAttr( wristCtrl_IK.ctrlOffset + '.v', 0 )
    mc.setAttr( poleVectorCrv + '.v', 0 )
    mc.setAttr( wrist_FK_IK_fingers_follow[0] + '.' + wristCtrl_IK.ctrlObject + 'W0', 0 )
    mc.setAttr( wrist_FK_IK_fingers_follow[0] + '.' + wristCtrl_FK.ctrlObject + 'W1', 1 )
    mc.setAttr( wristCtrl_FK_orient[0] + '.' + wristCtrl_IK.ctrlObject + 'W0', 0 )
    mc.setAttr( wristCtrl_FK_orient[0] + '.' + wristCtrl_FK.ctrlObject + 'W1', 1 )
        
    mc.setAttr( handIK + '.ikBlend', 0 )    

    if topfingerJoints:

        for i, topfingerJnt in enumerate( topfingerJoints ): # enumerate function gives both the name of object and index
            fingerPrefix = name.removeSuffix( topfingerJnt )[:-1]

            mc.setAttr( FKIK_ctrl.ctrlObject + '.' + fingerPrefix + 'FK_IK_Switch', 0 )
            
            mc.setAttr( fingerPrefix  + 'ikh.ikBlend', 0 )    
            mc.setAttr( fingerPrefix + 'IKOffset_grp.v', 0 ) 
            mc.setAttr( fingerPrefix + '0FKOffset_grp.v', 1 )
              
    mc.setDrivenKeyframe( upperArmCtrl_FK.ctrlOffset + '.v'  , cd = FKIK_ctrl.ctrlObject + '.Arm_FK_IK_Switch'  )  
    mc.setDrivenKeyframe( poleVectorCtrl.ctrlOffset + '.v'  , cd = FKIK_ctrl.ctrlObject + '.Arm_FK_IK_Switch'  )  
    mc.setDrivenKeyframe( wristCtrl_IK.ctrlOffset + '.v'  , cd = FKIK_ctrl.ctrlObject + '.Arm_FK_IK_Switch'  )  
    mc.setDrivenKeyframe( poleVectorCrv + '.v'  , cd = FKIK_ctrl.ctrlObject + '.Arm_FK_IK_Switch'  )  
    
    mc.setDrivenKeyframe( handIK + '.ikBlend'  , cd = FKIK_ctrl.ctrlObject + '.Arm_FK_IK_Switch'  )  
    mc.setDrivenKeyframe( wrist_FK_IK_fingers_follow[0] + '.'+ wristCtrl_IK.ctrlObject + 'W0' , cd = FKIK_ctrl.ctrlObject + '.Arm_FK_IK_Switch'  )  
    mc.setDrivenKeyframe( wrist_FK_IK_fingers_follow[0] + '.'+ wristCtrl_FK.ctrlObject + 'W1' , cd = FKIK_ctrl.ctrlObject + '.Arm_FK_IK_Switch'  )  
    mc.setDrivenKeyframe( wristCtrl_FK_orient[0] + '.'+ wristCtrl_IK.ctrlObject + 'W0' , cd = FKIK_ctrl.ctrlObject + '.Arm_FK_IK_Switch'  )  
    mc.setDrivenKeyframe( wristCtrl_FK_orient[0] + '.'+ wristCtrl_FK.ctrlObject + 'W1' , cd = FKIK_ctrl.ctrlObject + '.Arm_FK_IK_Switch'  )  

    if topfingerJoints:

        for i, topfingerJnt in enumerate( topfingerJoints ): # enumerate function gives both the name of object and index
            fingerPrefix = name.removeSuffix( topfingerJnt )[:-1]
       
            mc.setDrivenKeyframe( fingerPrefix + 'ikh.ikBlend'  , cd = FKIK_ctrl.ctrlObject + '.' + fingerPrefix + 'FK_IK_Switch'  )  
            mc.setDrivenKeyframe( fingerPrefix + 'IKOffset_grp.v'   , cd = FKIK_ctrl.ctrlObject + '.' + fingerPrefix + 'FK_IK_Switch'  )  
            mc.setDrivenKeyframe( fingerPrefix + '0FKOffset_grp.v'  , cd = FKIK_ctrl.ctrlObject + '.' + fingerPrefix + 'FK_IK_Switch'  )  
            
    # Parenting and cleanup
     
    mc.parent( pvLocator, rigmodule.partsNoTransGrp )
    mc.parent( FKIK_locator, rigmodule.partsNoTransGrp )
    mc.hide( pvLocator, FKIK_locator )

    return { 'module':rigmodule, 'baseAttachGrp':baseAttachGrp, 'bodyAttachGrp':bodyAttachGrp }