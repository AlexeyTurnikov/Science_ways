import gmsh
import sys
import numpy as np

gmsh.initialize()
gmsh.model.add("1.1")

lc = 0.05
points_tags_global = []
points_coord_global = []


def find_points(point_coord, point_coord_new):
    for i in range(0, len(point_coord)):
        if point_coord[i:i + len(point_coord_new)] == point_coord_new:
            return True, i
    return False, 0


def create_point(x, y, z):
    global points_coord_global
    tag = gmsh.model.geo.addPoint(x, y, z, lc)
    what_happened, j = find_points(points_coord_global, [x, y, z])
    if not what_happened:
        points_tags_global.append(tag)
        points_coord_global += [x, y, z]
        return tag
    if what_happened:
        return points_tags_global[j // 3]


def arc(rad, phi, z):
    point_tags = []
    point_tags.append(create_point(0, 0, z))
    point_tags.append(create_point(rad * np.cos(phi), rad * np.sin(phi), z))
    point_tags.append(create_point(rad * np.cos(phi + np.pi / 2), rad * np.sin(phi + np.pi / 2), z))
    return gmsh.model.geo.addCircleArc(point_tags[1], point_tags[0], point_tags[2])


def perp_arc(rad1, rad2, phi, z, direction):
    point_tags = []
    if direction == 1 or direction == 2:
        point_tags.append(create_point(rad1 * np.cos(phi), rad1 * np.sin(phi), z - rad2))
        point_tags.append(create_point(rad1 * np.cos(phi), rad1 * np.sin(phi), z))
        if direction == 1:
            point_tags.append(create_point((rad1 + rad2) * np.cos(phi), (rad1 + rad2) * np.sin(phi), z - rad2))
        if direction == 2:
            point_tags.append(create_point((rad1 - rad2) * np.cos(phi), (rad1 - rad2) * np.sin(phi), z - rad2))
    if direction == -1 or direction == -2:
        point_tags.append(create_point(rad1 * np.cos(phi), rad1 * np.sin(phi), z))
        if direction == -1:
            point_tags.append(create_point((rad1 + rad2) * np.cos(phi), (rad1 + rad2) * np.sin(phi), z))
        if direction == -2:
            point_tags.append(create_point((rad1 - rad2) * np.cos(phi), (rad1 - rad2) * np.sin(phi), z))
        point_tags.append(create_point(rad1 * np.cos(phi), rad1 * np.sin(phi), z - rad2))

    return gmsh.model.geo.addCircleArc(point_tags[1], point_tags[0], point_tags[2])


def part_torus(rad1, rad2, phi, z0):
    curve_part = []

    # Наружная часть
    curve_part.append((arc(rad1, phi, rad2 * 2 + z0)))
    curve_part.append((arc(rad1 + rad2, phi, rad2 + z0)))
    curve_part.append((arc(rad1, phi, z0)))
    curve_part.append(perp_arc(rad1, rad2, phi, rad2 * 2 + z0, 1))
    curve_part.append(perp_arc(rad1, rad2, phi + np.pi / 2, rad2 * 2 + z0, 1))
    curve_part.append(perp_arc(rad1, rad2, phi, rad2 + z0, -1))
    curve_part.append(perp_arc(rad1, rad2, phi + np.pi / 2, rad2 + z0, -1))

    # Внутренняя часть
    curve_part.append((arc(rad1 - rad2, phi, rad2 + z0)))
    curve_part.append(perp_arc(rad1, rad2, phi, rad2 * 2 + z0, 2))
    curve_part.append(perp_arc(rad1, rad2, phi + np.pi / 2, rad2 * 2 + z0, 2))
    curve_part.append(perp_arc(rad1, rad2, phi, rad2 + z0, -2))
    curve_part.append(perp_arc(rad1, rad2, phi + np.pi / 2, rad2 + z0, -2))

    # Построения круглых поверхностей
    curve_part.append(gmsh.model.geo.addCurveLoop([curve_part[0], curve_part[4], -curve_part[1], -curve_part[3]]))
    curve_part.append(gmsh.model.geo.addCurveLoop([curve_part[1], curve_part[6], -curve_part[2], -curve_part[5]]))
    curve_part.append(gmsh.model.geo.addCurveLoop([curve_part[0], curve_part[9], -curve_part[7], -curve_part[8]]))
    curve_part.append(gmsh.model.geo.addCurveLoop([curve_part[7], curve_part[11], -curve_part[2], -curve_part[10]]))
    s1 = gmsh.model.geo.addSurfaceFilling([curve_part[-4]])
    s2 = gmsh.model.geo.addSurfaceFilling([curve_part[-3]])
    s3 = gmsh.model.geo.addSurfaceFilling([curve_part[-2]])
    s4 = gmsh.model.geo.addSurfaceFilling([curve_part[-1]])
    # Точки для боковой поверхности
    p1 = create_point(rad1 * np.cos(phi), rad1 * np.sin(phi), rad2 * 2 + z0)
    p2 = create_point((rad1 + rad2) * np.cos(phi), (rad1 + rad2) * np.sin(phi), rad2 + z0)
    p3 = create_point((rad1 - rad2) * np.cos(phi), (rad1 - rad2) * np.sin(phi), rad2 + z0)
    p4 = create_point(rad1 * np.cos(phi), rad1 * np.sin(phi), z0)
    c1 = curve_part[3]
    c2 = curve_part[5]
    c3 = curve_part[8]
    c4 = curve_part[10]
    return [s1, s2, s3, s4, p1, p2, p3, p4, c1, c2, c3, c4]
    # наружная верхняя, наружная нижняя, внутренняя верхняя, внутренняя нижняя


radius1 = 10
radius21 = 2.5
radius22 = 1.5
surfaces = []

# Внешний тор
surfaces += part_torus(radius1, radius21, 0, 0)
surfaces += part_torus(radius1, radius21, np.pi / 2, 0)
surfaces += part_torus(radius1, radius21, np.pi, 0)
surfaces += part_torus(radius1, radius21, 1.5 * np.pi, 0)

# Внутренний тор
surfaces += part_torus(radius1, radius22, 0, radius21 - radius22)
surfaces += part_torus(radius1, radius22, np.pi / 2, radius21 - radius22)
surfaces += part_torus(radius1, radius22, np.pi, radius21 - radius22)
surfaces += part_torus(radius1, radius22, 1.5 * np.pi, radius21 - radius22)

# Прямые для боковых поверхностей
lines = []
for i in range(0, len(surfaces) // 2, 12):
    i += 4
    lines.append(gmsh.model.geo.addLine(surfaces[i + 1], surfaces[i + 49]))
    lines.append(gmsh.model.geo.addLine(surfaces[i], surfaces[i + 48]))
    lines.append(gmsh.model.geo.addLine(surfaces[i + 3], surfaces[i + 51]))
    lines.append(gmsh.model.geo.addLine(surfaces[i + 1], surfaces[i + 49]))
    lines.append(gmsh.model.geo.addLine(surfaces[i + 2], surfaces[i + 50]))
    lines.append(gmsh.model.geo.addLine(surfaces[i], surfaces[i + 48]))
    lines.append(gmsh.model.geo.addLine(surfaces[i + 3], surfaces[i + 51]))
    lines.append(gmsh.model.geo.addLine(surfaces[i + 2], surfaces[i + 50]))

for k in range(4):
    del surfaces[4:len(surfaces):12 - k]

curves = []

for i in range(0, len(surfaces) // 2, 8):
    j = i
    for k in range(0, 4):
        cl = gmsh.model.geo.addCurveLoop([surfaces[i + 4], lines[j + 2 * k], -surfaces[i + 36], -lines[j + 2 * k + 1]])
        curves.append(gmsh.model.geo.addSurfaceFilling([cl]))
        i += 1

for k in range(4):
    del surfaces[4:len(surfaces):8 - k]

for i in range(0, len(surfaces) // 2, 4):
    print(i)
    sl1 = gmsh.model.geo.addSurfaceLoop([surfaces[i], surfaces[i + 1], surfaces[i + 3], surfaces[i + 2]])
    sl2 = gmsh.model.geo.addSurfaceLoop(
        [surfaces[i + 16], surfaces[i + 1 + 16], surfaces[i + 3 + 16], surfaces[i + 2 + 16]])
    if i == 12:
        sl3 = gmsh.model.geo.addSurfaceLoop([curves[i], curves[i + 1], curves[i + 3], curves[i + 2]])
        sl4 = gmsh.model.geo.addSurfaceLoop([curves[0], curves[1], curves[3], curves[2]])
    else:
        sl3 = gmsh.model.geo.addSurfaceLoop([curves[i], curves[i + 1], curves[i + 3], curves[i + 2]])
        sl4 = gmsh.model.geo.addSurfaceLoop([curves[i + 4], curves[i + 5], curves[i + 7], curves[i + 6]])

    gmsh.model.geo.addVolume([sl1, sl2, sl3, sl4])

gmsh.model.geo.synchronize()
gmsh.model.mesh.generate(2)
gmsh.write("1.1.msh")
if '-nopopup' not in sys.argv:
    gmsh.fltk.run()
gmsh.finalize()
