"""
########################################################################################################################
# Title        : Character deformation setup
# Author       : Namrakant Tamrakar
# Created on   : 3/5/2021
# Updated on   : 4/9/2021 (latest update)
# Description  : This contains the deformation related functions such as save skin weights, load skin weights
                 Note: The constants will be replaced in the UI creation process using pyside2 by May 15, 2021
########################################################################################################################
"""
import maya.cmds as mc
import maya.mel as mm
import os

from . import  project
from rigLib.utils import name
from rigTools import bSkinSaver

#global variable and constants
skinWeightsDir = 'scenes/weights/'
swExt = '.swt' # skin weights extension

def build( baseRig, characterName, mainProjectPath ):
    """
    Character deformation "build()" function will take baseRig, character name and main project path as inputs and 
    will create twist joint, load the skin weights if present in the skin weights directory 
    """

    modelGrp = '%s_model_grp' % characterName

    # make twist joints
    refTwistJoints = ['L_hip_JNT', 'R_hip_JNT']  
    makeTwistJoints( baseRig, refTwistJoints )

    # load skin weights
    geoList = _getModelGeoObjects( modelGrp )
    wtdir = os.path.join( mainProjectPath, skinWeightsDir )

    if os.path.isdir(wtdir):
        loadSkinWeights( characterName, mainProjectPath, geoList = [] )

def _getModelGeoObjects( modelGrp ):
    """
    Function to get the list of geometry in the model group so that it can be skinned if weight files are present
    Returns the list of geometries
    """

    geoList = [ mc.listRelatives( o , p = 1)[0] for o in mc.listRelatives( modelGrp, ad = 1, type = 'mesh' ) ] #ad = all descendants, o=object, p=parent
    return geoList

def makeTwistJoints( baseRig, parentJoints ):
    """
    Create twist joints for the joints present in the input - parentJoints
    """

    twistJointsMainGroup = mc.group( n = 'twistJoints_grp', p = baseRig.jointGrp, em = 1 ) #p = parent, em = empty

    for parentJnt in parentJoints:
        prefix = name.removeSuffix( parentJnt )
        prefix = prefix[:-1]
        parentJntChild = mc.listRelatives( parentJnt, c = 1, type = 'joint')[0] # c = child

        # make twist joints

        twistJntsGrp = mc.group( n = prefix + 'TwistJoint_grp', p = twistJointsMainGroup, em = 1 )
        twistParentJnt = mc.duplicate( parentJnt, n = prefix + 'Twist1_jnt', parentOnly = True )[0]
        twistChildJnt = mc.duplicate( parentJntChild, n = prefix + 'Twist2_jnt', parentOnly = True )[0]
        
        # adjust twist joints

        origJntRadius = mc.getAttr( parentJnt + '.radius')

        for j in [ twistParentJnt, twistChildJnt ]:

            mc.setAttr( j + '.radius', origJntRadius * 2 )
            mc.color( j , ud = 1 ) # ud= user defined- same as display->wireframe color

        mc.parent( twistChildJnt, twistParentJnt )
        mc.parent( twistParentJnt, twistJntsGrp )

        # attach twist joints
        mc.pointConstraint( parentJnt, twistParentJnt )

        # make IK handle
        twistIK = mc.ikHandle( n = prefix + 'TwistJoint_ikh', sol = 'ikSCsolver', sj = twistParentJnt, ee = twistChildJnt )[0] #sj=start joint, ee = effector  
        mc.hide( twistIK )
        mc.parent( twistIK, twistJntsGrp )
        mc.parentConstraint( parentJntChild, twistIK )

def saveSkinWeights( characterName, mainProjectPath, geoList = [] ):
    """
    Save skin weights for character geometry objects
    """

    for obj in geoList:

        # weight file
        wtFile = os.path.join( mainProjectPath, skinWeightsDir, obj + swExt )

        # save skin weight file
        mc.select( obj )
        bSkinSaver.bSaveSkinValues( wtFile )

def loadSkinWeights( characterName, mainProjectPath, geoList = []  ):
    """
    Load skin weights for character geometry objects
    """

    # weights folder
    wtDir = os.path.join( mainProjectPath, skinWeightsDir )
    wtFiles = os.listdir( wtDir )

    # load skin weights

    for wtFile in wtFiles:
        extRes = os.path.splitext(wtFile)

        # check extension format
        if not extRes > 1:
            continue

        # check skin weight file
        if not extRes[1] == swExt:
            continue

        # check geometry list
        if geoList and not extRes[0] in geoList:
            continue

        # check if object exist
        if not mc.objExists( extRes[0] ):
            continue

        fullPathWtFile = os.path.join( wtDir, wtFile )
        bSkinSaver.bLoadSkinValues( loadOnSelection = False, inputFile = fullPathWtFile )