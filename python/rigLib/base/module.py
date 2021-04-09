"""
########################################################################################################################
# Title        : Class for making top rig structure and rig module
# Author       : Namrakant Tamrakar
# Created on   : 2/1/2021
# Updated on   : 4/9/2021 (latest update)
# Description  : The "Base" class will create the base hierarchy of the rig groups and call the "Controllers" class  
                 to create global controls and main control for controlling the visibility of the rig and the geometry.
                 The "Module" class will create the hierarchy for the modules such as spine, leg, arm, neck.
                 Note: The constants will be replaced in the UI creation process using pyside2 by May 15, 2021
########################################################################################################################
"""

import maya.cmds as mc

from . import controllers

#global variable and constants
sceneObjectType = 'rig'

class Base():
    """
    Class for building top rig (base) structure 
    """

    def __init__(
                 self,
                 characterName = 'new',
                 scale = 1.0,
                 mainCtrlAttachObj = ''
                 ):
        """
        Creating the rig hierachy, global and main controls to manage the visibility of the imported base rig and mesh

        @param characterName: str, character name
        @param scale: float, general scale of the rig
        @return: None
        """

        # create group hierarchy

        self.topGrp = mc.group(n =characterName + '_grp', em = 1) # em = empty
        self.rigGrp = mc.group(n = 'rig_grp', em =1, p = self.topGrp) # p= parent
        self.modelGrp = mc.group(n = 'model_grp', em=1, p = self.topGrp) 

        characterNameAt = 'characterName'  # name of our custom attribute
        sceneObjectTypeAt = 'sceneObjectType'  # name of our custom attribute
 
        for at in [ characterNameAt, sceneObjectTypeAt ]: # at = attribute
            mc.addAttr( self.topGrp, ln = at, dt = 'string' ) # ln = long name, dt = data type

        mc.setAttr( self.topGrp + '.' + characterNameAt, characterName, type = 'string', l = 1) # l = lock attribute
        mc.setAttr( self.topGrp + '.' + sceneObjectTypeAt, characterName, type = 'string', l = 1) # l = lock attribute

        # make global control

        globalCtrl1 = controllers.Controllers(
                                                prefix= 'global1',
                                                scale= scale * 20,
                                                parent= self.rigGrp,
                                                lockChannels=['v']
                                            )
     
        globalCtrl2 = controllers.Controllers(
                                                 prefix= 'global2',
                                                 scale = scale * 18,
                                                 parent= globalCtrl1.ctrlObject,
                                                 lockChannels= ['s','v']
                                            )

        # flatten the shape of the global control 

        self._flattenGlobalCtrlShape( globalCtrl1.ctrlObject )
        self._flattenGlobalCtrlShape( globalCtrl2.ctrlObject )

        for axis in ['y','z']:
            mc.connectAttr( globalCtrl1.ctrlObject + '.sx', globalCtrl1.ctrlObject + '.s' + axis )
            mc.setAttr( globalCtrl1.ctrlObject + '.s' + axis, k = 0) # k = keyable, 0 = false

        # make more groups for joints, modules, parts

        self.jointGrp = mc.group( n ='joints_grp', em = 1, p = globalCtrl2.ctrlObject)
        self.modulegrp = mc.group( n = 'modules_grp', em =1, p = globalCtrl2.ctrlObject)

        self.partGrp = mc.group( n = 'parts_grp', em = 1, p = self.rigGrp )
        mc.setAttr( self.partGrp + '.it', 0, l = 1 ) # .it= inherit transform, 0 = false, l = lock

        # make main control, adjust its shape and connect it to custom attributes

        mainCtrl = controllers.Controllers(
                                           prefix= 'main',
                                           scale= scale*2,
                                           parent= globalCtrl2.ctrlObject,
                                           translateTo= mainCtrlAttachObj,
                                           lockChannels= ['t', 'r', 's', 'v']
                                        )
        
        self._adjustMainCtrlShape( mainCtrl, scale )

        if mc.objExists( mainCtrlAttachObj ):

            mc.parentConstraint( mainCtrlAttachObj, mainCtrl.ctrlOffset, mo = 1 ) # off= offset, mo= maintain offset

        mainVisAts = ['modelVis', 'jointVis']
        mainDispAts = ['modelDisp', 'jointDisp']
        mainObjList = [self.modelGrp, self.jointGrp]
        mainObjVisDvList = [0,1]    # default value

        # add rig visibility connections (off:on)

        for at, obj, dfVal in zip( mainVisAts, mainObjList, mainObjVisDvList):                           # dfval= default value

            mc.addAttr( mainCtrl.ctrlObject, ln = at, at = 'enum', enumName = 'off:on', k = 1, dv = 1 ) # ln= long name, k=keyable
            mc.setAttr( mainCtrl.ctrlObject + '.' + at, cb = 1 ) # channel box
            mc.connectAttr( mainCtrl.ctrlObject + '.' + at, obj + '.v' ) #v=visibility
            
        # add display type connections (normal:template:reference)

        for at, obj in zip( mainDispAts, mainObjList):

            mc.addAttr( mainCtrl.ctrlObject, ln = at, at = 'enum', enumName = 'normal:template:reference', k = 1, dv = 2 )
            mc.setAttr( mainCtrl.ctrlObject + '.' + at, cb = 1 ) # channel box
            mc.setAttr( obj + '.ove', 1 ) # ove = override enable
            mc.connectAttr( mainCtrl.ctrlObject + '.' + at, obj + '.ovdt' ) # ovdt=override 
            
    def _adjustMainCtrlShape( self, ctrl, scale ):
        """
        Adjusting the shape of the main control
        """

        ctrlShapes = mc.listRelatives( ctrl.ctrlObject, s = 1, type = 'nurbsCurve' ) # s=shape
        cls = mc.cluster(ctrlShapes )[1]
        mc.setAttr(cls + '.ry', 90)
        mc.delete( ctrlShapes , ch = 1 ) # ch= construction history

        mc.move( scale * 3, ctrl.ctrlOffset, moveY = True, relative = True )

    def _flattenGlobalCtrlShape( self, ctrlObject ):
        """
        Flatten the global control object shape
        """
        
        ctrlShapes = mc.listRelatives( ctrlObject, s = 1, type = 'nurbsCurve' ) # s=shape
        cls = mc.cluster(ctrlShapes )[1]
        mc.setAttr(cls + '.rz', 90)
        mc.delete( ctrlShapes, ch = 1 ) # ch= construction history

class Module():
    """
    Class for building module rig structure
    """

    def __init__(
                 self,
                 prefix = 'new',
                 baseObj = None
                 ):
    
        """
        Creating the rig hierachy for modules such as spine, neck, leg, arm

        @param prefix: str, prefix to name new objects
        @param baseObj: instance of base.module.Base class
        @return: None
        """

        self.topGrp = mc.group(n = prefix + 'Module_grp', em = 1) #em = empty

        self.controlsGrp = mc.group(n = prefix + 'Controls_grp', em = 1, p = self.topGrp) #em = empty, p=parent
        self.jointsGrp = mc.group(n = prefix + 'Joints_grp', em = 1, p = self.topGrp) #em = empty, p=parent
        self.partsGrp = mc.group(n = prefix + 'Parts_grp', em = 1, p = self.topGrp)
        self.partsNoTransGrp = mc.group(n = prefix + 'PartsNoTrans_grp', em = 1, p = self.topGrp)

        mc.setAttr( self.partsNoTransGrp + '.it', 0, l = 1 ) #.it=inhert transform, l=lock

        # parent module

        if baseObj:

            mc.parent( self.topGrp, baseObj.modulegrp ) 