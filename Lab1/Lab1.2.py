import gmsh
import math
import os
import sys

gmsh.initialize()


def createGeometryAndMesh():
    # Clear all models and merge an STL mesh that we would like to remesh (from
    # the parent directory):
    gmsh.clear()
    path = os.path.dirname(os.path.abspath(__file__))
    gmsh.merge(os.path.join(path, 'Amongas_key.STL'))
    # gmsh.merge(os.path.join(path, 't13_data.stl'))
    # We first classify ("color") the surfaces by splitting the original surface
    # along sharp geometrical features. This will create new discrete surfaces,
    # curves and points.

    # Angle between two triangles above which an edge is considered as sharp,
    # retrieved from the ONELAB database (see below):
    angle = 0.1

    # For complex geometries, patches can be too complex, too elongated or too
    # large to be parametrized; setting the following option will force the
    # creation of patches that are amenable to reparametrization:
    forceParametrizablePatches = True

    # For open surfaces include the boundary edges in the classification
    # process:
    includeBoundary = False

    # Force curves to be split on given angle:
    curveAngle = 180
    gmsh.model.mesh.removeDuplicateNodes()
    gmsh.model.mesh.classifySurfaces(angle * math.pi / 180., includeBoundary,
                                     forceParametrizablePatches,
                                     curveAngle * math.pi / 180, False)

    # Create a geometry for all the discrete curves and surfaces in the mesh, by
    # computing a parametrization for each one
    gmsh.model.mesh.createGeometry()

    # Create a volume from all the surfaces
    s = gmsh.model.getEntities(2)
    l = gmsh.model.geo.addSurfaceLoop([e[1] for e in s])

    gmsh.model.geo.addVolume([l])

    gmsh.model.geo.synchronize()

    gmsh.model.mesh.generate(3)
    gmsh.write('1.2.msh')


# Create the geometry and mesh it:
createGeometryAndMesh()

if "-nopopup" not in sys.argv:
    gmsh.fltk.initialize()
    while gmsh.fltk.isAvailable():
        gmsh.fltk.wait()

gmsh.finalize()
