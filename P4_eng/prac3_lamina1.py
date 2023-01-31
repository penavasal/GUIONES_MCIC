from abaqus import *
from abaqusConstants import *
backwardCompatibility.setValues(includeDeprecated=True,
                                reportDeprecated=False)


import part
import math
jobname = "laminaScordelis1"
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
OA = (0,R)
OM = (R*math.sin(ANGR2),R*math.cos(ANGR2))
OB = (R*math.sin(ANGR),R*math.cos(ANGR))
seccion.ArcByCenterEnds(center=Origen, point1=OA, point2=OB, direction=CLOCKWISE)
nombreparte = 'parte'
p = modelo.Part(name=nombreparte, dimensionality=THREE_D, type=DEFORMABLE_BODY)
p.BaseShellExtrude(sketch=seccion, depth=Long2)
seccion.unsetPrimaryObject()

import material


# material
modYoung = 432.e6
coefPoisson = 0.
gamma = 360
espesor = 0.25
nombremat = 'matname'
matlamina = modelo.Material(name=nombremat)
matlamina.Elastic(table=((modYoung, coefPoisson), ))

import section
nombreseccion = 'seccionmat'
seccion = modelo.HomogeneousShellSection(name=nombreseccion,
        preIntegrate=ON, material=nombremat, thicknessType=UNIFORM,
        thickness=espesor, thicknessField='', nodalThicknessField='',
        idealization=NO_IDEALIZATION, poissonDefinition=DEFAULT,
        thicknessModulus=None, useDensity=OFF)

region = (p.faces,)
p.SectionAssignment(region=region, sectionName=nombreseccion, offset=0.0,
        offsetType=MIDDLE_SURFACE, offsetField='',
        thicknessAssignment=FROM_SECTION)


import assembly

# Create a part instance.

myAssembly = modelo.rootAssembly
nombreinstancia = 'laminainstancia'
myInstance = myAssembly.Instance(name=nombreinstancia,
    part=p, dependent=ON)

#-------------------------------------------------------

import step

modelo.StaticStep(name='cargas', previous='Initial',
    description='Cargas en la lamina.')

#-------------------------------------------------------

import load


OM3 = (OM[0],OM[1],0.0)
AMB  = myInstance.edges.findAt((OM3,) )
endRegion = (AMB,)
modelo.DisplacementBC(name='Apoyo', createStepName='cargas',region=endRegion, u1=0., u2=0.)

OE3 = (OA[0],OA[1],Long2/2)
AEC  = myInstance.edges.findAt((OE3,) )
endRegion = (AEC,)
modelo.XsymmBC(name='Plano de simetria YZ',createStepName='cargas', region=endRegion)

OF3 = (OM[0],OM[1],Long2)
CFD  = myInstance.edges.findAt((OF3,) )
endRegion = (CFD,)
modelo.ZsymmBC(name='Plano de simetria XY',createStepName='cargas', region=endRegion)

# Peso propio 
f2 = myInstance.faces
faces2 = f2.getByBoundingBox(-1000,-1000,-1000,1000,1000,1000)
region = (faces2,)
modelo.BodyForce(name='Peso Propio', createStepName='cargas', region=region, comp2=-gamma)


#-------------------------------------------------------

import mesh

region = (p.faces,)
elemType = mesh.ElemType(elemCode=S4R5, elemLibrary=STANDARD,hourglassControl=DEFAULT)
p.setElementType(regions=region, elemTypes=(elemType,))

OF3 = (OM[0],OM[1],Long2)
CFD  = p.edges.findAt((OF3,) )
p.seedEdgeByNumber(edges=CFD, number=16, constraint=FIXED)
OE3 = (OA[0],OA[1],Long2/2)
AEC  = p.edges.findAt((OE3,) )
p.seedEdgeByNumber(edges=AEC, number=16, constraint=FIXED)

p.generateMesh()

#-------------------------------------------------------

import job


jobName = jobname
myJob = mdb.Job(name=jobName, model=jobname,
    description='Scordelis lamina')


myJob.submit()
myJob.waitForCompletion()

mdb.saveAs(pathName=jobname+".cae")

#-------------------------------------------------------


