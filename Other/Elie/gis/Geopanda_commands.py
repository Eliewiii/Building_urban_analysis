## https://www.earthdatascience.org/workshops/gis-open-source-python/intro-vector-data-python/

from random import random
import os
import os
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry.point import Point
import shapely
from shapely.ops import transform

from PIL import Image, ImageEnhance

# shape = gpd.read_file("C://Users//eliem//Documents//PhD_Technion//Programming//Extract_GIS//GIS_files//Israel//hotosm_isr_buildings_polygons.shp")
shape = gpd.read_file("D://Elie//PhD//Programming//GIS//Building_type//North_Tel_Aviv//double_z//sample_1//double_z.shp")
# print(shape.head(100))
# print(shape.columns)
#
# # for i in range(214) :
# #     print(shape['geometry'][i])
#
# ### Polygon
# # print(shape['geometry'][214-27])
#
# print(len(shape['geometry']))
# print(shape['geometry'][1])
# print(shape['geometry'][0].exterior.__geo_interface__['coordinates'][0])

# print(type(shape['Shape_Area'][0]))



### multi Poligon
# print(type(shape['geometry'][214-27]))
# a=type(shape['geometry'][214-27])
# print(isinstance(shape['geometry'][214-27], shapely.geometry.multipolygon.MultiPolygon))
# # print(type(shape['geometry'][214-27]) == a)
# print(len(shape['geometry'][214-27-5-10-12-5].geoms))
# print(shape['geometry'][214-27].geoms[0].exterior.__geo_interface__['coordinates'])
#
# print(shape['geometry'][214-27].geoms[3].contains(shape['geometry'][214-27].geoms[0]))
#
# p1 = shape['geometry'][214-27-5-10-12-5].geoms[1].exterior.__geo_interface__['coordinates'][0]
#
# p1=Point(p1[0],p1[1])
# print(p1)
#
# # print(shape['geometry'][214-27-5-10-12-5].geoms[0].coutain(p1))
# ## Show
#
#
#
# data=shape.loc[[0],'geometry']
# # data=shape['geometry'][0]
#
#
# x,y=shape['geometry'][0].exterior.xy
#
#
# plt.plot(x,y)
#
#
# # data.plot()
#
# plt.axis('off')
# plt.savefig("D://Elie//PhD//test.png", bbox_inches=0,dpi=300)
# plt.show()
#
# file = "D://Elie//PhD//test.png"
# img = Image.open(file)
#
# img = img.convert("L")
# img.save("D://Elie//PhD//test.png")
#

# print(type(data))


# print(data.exterior.__geo_interface__['coordinates'])
# data.exterior.__geo_interface__['coordinates']= ((1,1),(2,2),(1,2))
#
# print(data.exterior.__geo_interface__['coordinates'])

# def zob(x,y,z=None) :
#     return tuple(filter(None, [x+1, y+1]))
#
# data=shape['geometry'][0]
# new= transform(zob,data)
# print(new.__geo_interface__['coordinates'])