"""
########################################################################################################################
# Title        : Character rig setup
# Author       : Namrakant Tamrakar
# Created on   : 3/5/2021
# Updated on   : 4/9/2021 (latest update)
# Description  : This contains the rig creation related functions such as make control setup to create the controls for 
                 spine, neck, legs, arms. We call the separate modules which handles the functionality of 
                 creating IK, FK, ikSpline, constraints, etc.
                 Note: The constants will be replaced in the UI creation process using pyside2 by May 15, 2021
########################################################################################################################
"""

from rigLib.base import controllers
from rigLib.base import module
from rigLib.rig import spine
from rigLib.rig import neck
from rigLib.rig import hand, leg

from . import character_deform
from . import  project

import maya.cmds as mc

#global variable and constants
sceneScale = project.sceneScale

modelFilePath = '%s/scenes/model/%s_model.ma'
rigFilePath = '%s/scenes/rig/%s_rig.ma'

rootJnt = 'pelvis_JNT'
headJnt = 'head_1_JNT'
headEndJnt = 'head_end_JNT'
spine_end_JNT = 'spine_end_JNT'

def build( characterName, mainProjectPath ):
    """
    main function to build character rig:
    Takes character name and main project path as inputs and creates the procedural rig 
    """

    # new scene
    mc.file( new = True, f = True) # f=force?

    # import rig  
    rigFile = rigFilePath % (mainProjectPath, characterName ) 
    mc.file( rigFile, i = 1 ) #i = import

    # make base (base group structure and global controls)
    baseRig = module.Base( characterName = characterName, scale = sceneScale, mainCtrlAttachObj = headEndJnt ) #baseRig is an instance of Base class

    # import model
    modelFile = modelFilePath % (mainProjectPath, characterName )
    mc.file( modelFile, i = 1 ) #i = import

    # parent model
    modelGrp = '%s_model_grp' % characterName
    mc.parent( modelGrp, baseRig.modelGrp )

    # parent skeleton
    skelGrp = '%s_skel_grp' % characterName
    mc.parent( rootJnt, baseRig.jointGrp )

    # deform setup
    character_deform.build( baseRig, characterName, mainProjectPath )

    # control setup
    makeControlSetup( baseRig )


def makeControlSetup( baseRig ):
    """
    Make control setup:
    This method will call the modules to build spine, neck, legs, arms
    """

    # spine

    spineJoints = [ 'spine_1_JNT', 'spine_2_JNT', 'spine_3_JNT', 'spine_4_JNT', 'spine_5_JNT']

    spineRig = spine.build(
                            spineJoints =spineJoints ,
                            rootJnt = rootJnt,
                            spineCurve = 'spine_CRV',
                            bodyLocator = 'body_LOC',
                            chestLocator = 'chest_LOC',
                            pelvisLocator = 'pelvis_LOC',
                            prefix = 'spine',
                            rigScale = sceneScale,
                            baseRig = baseRig
                            )

    # neck

    neckJoints = [ 'neck_1_JNT' ]

    neckRig = neck.build(
                        neckJoints = neckJoints,
                        headJnt = headJnt,
                        neckCurve = 'neck_CRV',
                        prefix = 'neck',
                        rigScale = 1.0,
                        baseRig = baseRig
                        )

    mc.parentConstraint( spine_end_JNT, neckRig['baseAttachGrp'], mo = 1 )

    # left leg

    l_legJoints = [ 'L_hip_JNT', 'L_knee_JNT', 'L_ankle_JNT', 'L_ball_JNT', 'L_toe_JNT' ]
    #l_topToeJoints = [ '' ]  # for leg fingers

    l_leg_rig = leg.build( 
                legJoints = l_legJoints,
                pvLocator = 'L_Knee_PV_LOC',
                FKIK_locator = 'L_Leg_FKIK_LOC',
                topToeJoints = None,
                pelvisJnt = '',
                prefix = 'L_leg',
                rigScale = 1.0,
                baseRig = baseRig
            )

    mc.parentConstraint( 'spinePelvis_ctrl', 'L_leghip_FKOffset_grp', mo = 1 )   
  
    # right leg

    r_legJoints = [ 'R_hip_JNT', 'R_knee_JNT', 'R_ankle_JNT', 'R_ball_JNT', 'R_toe_JNT' ]
    #r_topToeJoints = [ '' ]  # for leg fingers

    r_leg_rig = leg.build( 
                legJoints = r_legJoints,
                pvLocator = 'R_Knee_PV_LOC',
                FKIK_locator = 'R_Leg_FKIK_LOC',
                topToeJoints = None,
                pelvisJnt = '',
                prefix = 'R_leg',
                rigScale = 1.0,
                baseRig = baseRig
            )

    mc.parentConstraint( 'spinePelvis_ctrl', 'R_leghip_FKOffset_grp', mo = 1 )   

    # left IK arm
 
    l_armJoints = [ 'L_upperArm_JNT', 'L_elbow_JNT', 'L_wrist_JNT' ]
    l_topFingerJoints = [ 'L_thumb_1_JNT', 'L_index_0_JNT', 'L_middle_0_JNT', 'L_ring_0_JNT', 'L_pinky_0_JNT' ]  

    l_arm_rig = hand.build( 
                handJoints = l_armJoints,
                pvLocator = 'L_elbow_PV_LOC',
                FKIK_locator = 'L_hand_FKIK_LOC',
                topfingerJoints = l_topFingerJoints,
                scapulaJnt = 'L_clavicle_JNT',
                prefix = 'L_arm',
                rigScale = 1.0,
                baseRig = baseRig
            )

    mc.parentConstraint( spine_end_JNT, l_arm_rig['baseAttachGrp'], mo = 1 )       

    # right IK arm

    r_armJoints = [ 'R_upperArm_JNT', 'R_elbow_JNT', 'R_wrist_JNT' ]
    r_topFingerJoints = [ 'R_thumb_1_JNT', 'R_index_0_JNT', 'R_middle_0_JNT', 'R_ring_0_JNT', 'R_pinky_0_JNT' ]  

    r_arm_rig = hand.build( 
                handJoints = r_armJoints,
                pvLocator = 'R_elbow_PV_LOC',
                FKIK_locator = 'R_hand_FKIK_LOC',
                topfingerJoints = r_topFingerJoints,
                scapulaJnt = 'R_clavicle_JNT',
                prefix = 'R_arm',
                rigScale = 1.0,
                baseRig = baseRig
            )

    mc.parentConstraint( spine_end_JNT, r_arm_rig['baseAttachGrp'], mo = 1 )   