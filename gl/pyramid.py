from lib import *
from sphere import *
from math import *
from intersect import Intersect


class Pyramid(object):
  def __init__(self, arrVec, material):
    self.arrVec = arrVec
    self.material = material

  def face(self, v0, v1, v2, orig, direction):
    v0v1 = sub(v1, v0)
    v0v2 = sub(v2, v0)

    N = mul(cross(v0v1, v0v2),1)
    ray_dir = dot(N, direction)

    #Check if projection doesn't hit
    if abs(ray_dir) < 0.00001:
        return None
    
    d = dot(N, v0)
    t = (dot(N, orig) + d)/ray_dir
    
    #Check if face is not behind the camera
    if t < 0:
      return None

    P = sum(orig, mul(direction, t))
    X, Y, Z = barycentric(v0, v1, v2, P)

    # Check point is within triangle
    if X<0 or Y<0 or Z<0:
      return None
    else: 
      return Intersect(distance = d,
                      point = P,
                      normal = norm(N))


  def ray_intersect(self, orig, direction):
    v0, v1, v2, v3 = self.arrVec
    faces = [
    self.face(v0, v3, v2, orig, direction),
    self.face(v0, v1, v2, orig, direction),
    self.face(v1, v3, v2, orig, direction),
    self.face(v0, v1, v3, orig, direction)
    ]


    t = float('inf') ## Assume infinite distance
    intersect = None

    for face in faces:
        if face is not None:
            if face.distance < t:
                t = face.distance
                intersect = face

    if intersect is None:
        return None

    return Intersect(distance = intersect.distance,
                     point = intersect.point,
                     normal = intersect.normal)