from lib import *
from intersect import Intersect

class Plane(object):
    def __init__(self, position, normal, material):
        self.position = position
        self.normal = norm(normal)
        self.material = material

    def ray_intersect(self, orig, dir):

        div = dot(dir, self.normal)

        if abs(div) > 0.0001:
            t = dot(self.normal, sub(self.position, orig)) / div
            if t > 0:
                hit = sum(orig, mul(dir, t))

                return Intersect(distance = t,
                                 point = hit,
                                 normal = self.normal)

        return None