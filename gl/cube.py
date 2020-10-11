from lib import *
from sphere import *
from math import *
from intersect import Intersect


class Cube(object):
  def __init__(self, lengths, material, rotation='y', rotation_normal=1):
    self.x = min(lengths[0])
    self.x_end = max(lengths[0])
    self.y = min(lengths[1])
    self.y_end = max(lengths[1])
    self.z = min(lengths[2])
    self.z_end = max(lengths[2])
    self.material = material

  def ray_intersect(self, orig, direction):
    try:
        invdir = V3(1 / direction.x, 1/direction.y, 1/direction.z)
    except:
        return None
    if invdir.x >= 0:
        tmin = (self.x - orig.x) * invdir.x
        tmax = (self.x_end - orig.x) * invdir.x
    else:
        tmin = (self.x_end - orig.x) * invdir.x
        tmax = (self.x - orig.x) * invdir.x
    if invdir.y >= 0:
        tymin = (self.y - orig.y) * invdir.y
        tymax = (self.y_end - orig.y) * invdir.y
    else:
        tymin = (self.y_end - orig.y) * invdir.y
        tymax = (self.y - orig.y) * invdir.y

    if ((tmin > tymax) or (tymin > tmax)):
        return None
    if (tymin > tmin):
        tmin = tymin
    if (tymax < tmax):
        tmax = tymax
    
    if invdir.z >=0:
        tzmin = (self.z - orig.z) * invdir.z
        tzmax = (self.z_end - orig.z) * invdir.z
    else: 
        tzmin = (self.z_end - orig.z) * invdir.z
        tzmax = (self.z - orig.z) * invdir.z

    if (tmin > tzmax) or (tzmin > tmax):
        return None
    if (tzmin > tmin):
        tmin = tzmin
    if (tzmax < tmax):
        tmax = tzmax
    
    t = tmin

    if t<0:
        t=tmax
    if t<0:
        return None
    

    x_center = (self.x + self.x_end) /2
    y_center = (self.y + self.y_end) /2
    z_center = (self.z + self.z_end) /2
    center = V3(x_center, y_center, z_center)
    hit = sum(orig, mul(direction, t))
    normal = norm(sub(hit, center))
    return intersect.Intersect(
      distance=t,
      point=hit,
      normal = normal
    )
