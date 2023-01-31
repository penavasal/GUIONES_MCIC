from abaqus import *
from abaqusConstants import *
backwardCompatibility.setValues(includeDeprecated=True,
                                reportDeprecated=False)


import part
import math
jobname = "laminaScordelis2"
modelname = jobname
modelo  = mdb.Model(name=jobname)
seccion = modelo.ConstrainedSketch(name='perfil', sheetSize=200.0)
R = 25
ANG = 40
ANGR = ANG*math.pi/180.
ANGR2 = ANGR/2
Long = 50.
Long2 = Long/2.
Origen = (0,0)
espesor = 0.25
OAM = (0,R)
OMM = (R*math.sin(ANGR2),R*math.cos(ANGR2))
OBM = (R*math.sin(ANGR),R*math.cos(ANGR))
RT = R + 0.5*espesor
OAT = (0,RT)
OMT = (RT*math.sin(ANGR2),RT*math.cos(ANGR2))
OBT = (RT*math.sin(ANGR),RT*math.cos(ANGR))
RB = R - 0.5*espesor
OAB = (0,RB)
OMB = (RB*math.sin(ANGR2),RB*math.cos(ANGR2))
OBB = (RB*math.sin(ANGR),RB*math.cos(ANGR))
seccion.Line(point1=OAB, point2=OAT)
seccion.ArcByCenterEnds(center=Origen, point1=OAT, point2=OBT, direction=CLOCKWISE)
seccion.Line(point1=OBT, point2=OBB)
seccion.ArcByCenterEnds(center=Origen, point1=OBB, point2=OAB, direction=COUNTERCLOCKWISE)

nombreparte = 'parte'
p = modelo.Part(name=nombreparte, dimensionality=THREE_D, type=DEFORMABLE_BODY)
p.BaseSolidExtrude(sketch=seccion, depth=Long2)
seccion.unsetPrimaryObject()

import material

modYoung = 432.e6
coefPoisson = 0.
gamma = 360
nombremat = 'matname'
material1 = mdb.models[modelname].Material(name=nombremat)
material1.Elastic(table=((modYoung, coefPoisson), ))
import section
nombreseccion = 'seccionmat'
seccion = modelo.HomogeneousSolidSection(name='seccionmat', material=nombremat)
region = (p.cells,)
p.SectionAssignment(region=region, sectionName='seccionmat')

import assembly

# Create a part instance.
myAssembly = modelo.rootAssembly
nombreinstancia = 'laminainstancia'
myInstance = myAssembly.Instance(name=nombreinstancia, part=p, dependent=ON)

#-------------------------------------------------------

import step

modelo.StaticStep(name='cargas', previous='Initial', description='Cargas en la lamina.')

#-------------------------------------------------------

import load


OM3 = (OMB[0],OMB[1],0.0)
AMB  = myInstance.edges.findAt((OM3,) )
endRegion = (AMB,)
modelo.DisplacementBC(name='Apoyo', createStepName='cargas', region=endRegion, u1=0., u2=0.) 


OE3 = (OAM[0],OAM[1],Long2/2)
AEC  = myInstance.faces.findAt((OE3,) )
endRegion = (AEC,)
modelo.XsymmBC(name='Plano de simetria YZ',createStepName='cargas', region=endRegion)

OF3 = (OMM[0],OMM[1],Long2)
CFD  = myInstance.faces.findAt((OF3,) )
endRegion = (CFD,)
modelo.ZsymmBC(name='Plano de simetria XY',createStepName='cargas', region=endRegion)

# Peso propio 
f2 = myInstance.cells
cells2 = f2.getByBoundingBox(-1000,-1000,-1000,1000,1000,1000)
region = (cells2,)
modelo.BodyForce(name='Peso Propio', createStepName='cargas', region=region, comp2=-gamma)


#-------------------------------------------------------

import mesh


region = (p.cells,)
elemType = mesh.ElemType(elemCode=C3D8I, elemLibrary=STANDARD,hourglassControl=DEFAULT)
p.setElementType(regions=region, elemTypes=(elemType,))
p.seedPart(size=2)
p.generateMesh()

#-------------------------------------------------------

import job


jobName = jobname
myJob = mdb.Job(name=jobName, model=jobname, description='Scordelis lamina')
myJob.submit()
myJob.waitForCompletion()
mdb.saveAs(pathName=jobname+".cae")

#-------------------------------------------------------


