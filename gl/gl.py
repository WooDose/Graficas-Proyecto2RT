import struct
import pprint
import math
from lib import *
from sphere import *
from math import pi
import random
from light import Light
from plane import *
from cube import *
from pyramid import *


MAX_RECURSION_DEPTH = 3
AMBIENT_LIGHT = 0.15
TINT = (0.09,0.05,0.02)
def char(c):
    return struct.pack('=c', c.encode('ascii'))

def word(c):
    return struct.pack('=h', c)

def dword(c):
    return struct.pack('=l', c)

def color(r, g, b):
    return bytes([b, g, r])

class Render(object):
    def __init__(self, width, height, vpw, vph, vpx, vpy):
        self.width = width
        self.height = height
        self.framebuffer = []
        self.framebuffer_int = []
        self.clearColor = (0.61,0.85,0.944)

        self.glCreateWindow()
        self.glViewport(vpw, vph, vpx, vpy)
        self.drawColor = color(0,0,0)
        self.drawColor_int = (0,0,0)
        self.glClear()
        self.scene = []

    def glInit(self):
        pass
    
    def glCreateWindow(self):
        print(self.framebuffer)
        self.framebuffer = [
            [color(158,220,240) for x in range(self.width)]
             for y in range(self.height)
        ]
        self.framebuffer_int = [
            [(158,220,240) for x in range(self.width)]
             for y in range(self.height)
        ]

        #pprint.pprint(self.framebuffer)
    
    def glViewport(self, width, height, x, y):
        self.ViewportWidth = width
        self.ViewportHeight = height
        self.xNormalized = x
        self.yNormalized = y


    def glClear(self):
        self.framebuffer = [
            [color(158,220,240) for x in range(self.width)]
             for y in range(self.height)
        ]

    def glClearColor(self, r,g,b):
        self.clearColor = color(int(r*255),int(g*255),int(b*255))

    def glColor(self, r,g,b):
        self.drawColor = color(int(r*255),int(g*255),int(b*255))
        self.drawColor_int = (r,g,b)

    def point(self,x,y):
        self.framebuffer[x][y] = self.drawColor
        self.framebuffer_int[x][y] = self.drawColor_int

    def glVertex(self, x,y): 
        xW = int(((x+1)*(self.ViewportWidth/2))+self.xNormalized)
        yW = int(((y+1)*(self.ViewportHeight/2))+self.yNormalized)
        xW = (xW - 1) if xW == self.width else xW
        yW = (yW - 1) if yW == self.height else yW
        self.point(xW, yW)

    def glFinish(self, filename):
        f = open(filename, 'bw')

        ## Write file header
        # Header Field
        f.write(char('B'))
        f.write(char('M'))
        # Size in Bytes
        f.write(dword(14 + 40 + (self.width * self.height * 3)))
        #Reserved
        f.write(word(0))
        f.write(word(0))
        #Offset
        f.write(dword(14 + 40))

        # Image header 
        # Bytes in Header
        f.write(dword(40))
        # Width
        f.write(dword(self.width))
        # Height
        f.write(dword(self.height))
        # Color Planes
        f.write(word(1))
        # Bits/Pixel
        f.write(word(24))
        # Pixel array compression
        f.write(dword(0))
        # Size of raw bitmap
        f.write(dword(self.width * self.height * 3))
        #Colors in palette
        f.write(dword(0))
        #Important Colors
        f.write(dword(0))
        # Unused/Reserved
        f.write(dword(0))
        f.write(dword(0))

        # Pixel data
        
        print(self.framebuffer)
        for x in range(self.height):
            for y in range(self.width):
                f.write(self.framebuffer[y][x])
        f.close()
    
    # def point(self,x,y):
    #     self.framebuffer[x][y] = self.drawColor

    def scene_intersect(self, orig, direction):
        zbuffer = float('inf')
        material = None
        for obj in self.scene:
            intersect = obj.ray_intersect(orig, direction)
            if intersect is not None:
                # print("I intersect")
                if intersect.distance < zbuffer:
                    zbuffer = intersect.distance
                    material = obj.material
                    return True, material, intersect
        return False, None, intersect
        
    def cast_ray(self, orig, direction, recursion = 0, removed_channel=-999, pos=(0,0)):
        collision, material , impact = self.scene_intersect(orig, direction)

        if collision or recursion >= MAX_RECURSION_DEPTH:
            colour = (material.diffuse[0], material.diffuse[1], material.diffuse[2])
            for light in self.lights:
                light_dir = norm(sub(light.position, impact.point))
                light_distance = length(sub(light.position, impact.point))

                offset_normal = mul(impact.normal, 1.1)
                if dot(light_dir, impact.normal) < 0:
                    shadow_orig = sub(impact.point, offset_normal)
                else:
                    shadow_orig = sum(impact.point, offset_normal)
                # print(impact.normal)

                shadow_intersect, shadow_material, shadow_intersect_obj = self.scene_intersect(shadow_orig, light_dir)
                shadow_intensity = 0
                if shadow_intersect and light.is_anaglyph == False:
                    #in shadow
                    shadow_intensity = 0

                intensity = max(0,dot(light_dir, impact.normal)) * (1-shadow_intensity)

                reflection = reflect(light_dir, impact.normal)
                specular_intensity = light.intensity * (max(0, dot(reflection,direction))**material.spec)

                # if material.albedo[2] > 0:
                #     reflected_colour = 
                albedo = material.albedo
                # print(material, material.diffuse)
                colour = (colour[0]*intensity*albedo[0], colour[1]*intensity*albedo[0], colour[2]*intensity*albedo[0])
                specular = (light.color[0] * specular_intensity * material.albedo[1],light.color[1] * specular_intensity * material.albedo[1] ,light.color[2] * specular_intensity * material.albedo[1] )
                # reflected = (reflected_colour[0] * material_albedo[2]
                position = self.framebuffer_int[pos[0]][pos[1]]
                # rr = random.randint(0, 50)
                # if rr == 50:
                #     print(position)
                #     print(self.drawColor_int)


                ## ONLY WORKS FOR 3D STEREOGRAPH
                ## Color channel selection depending on render iteration.
                # red =  min(colour[0]+specular[0], 1) if (removed_channel == -1 or removed_channel is None) else 0
                # red = min(1, red+position[0])
                # green = min(colour[1]+specular[1], 1) if removed_channel is None else 0
                # blue = min(colour[2]+specular[2], 1)  if (removed_channel == 0 or removed_channel is None) else 0
                # blue = min(1, blue+position[2])

                #Apply ambient light
                colour = (min(0.99, colour[0]+(colour[0]*AMBIENT_LIGHT)), min(0.99, colour[1]+(colour[1]*AMBIENT_LIGHT)),min(0.99, colour[2]+(colour[2]*AMBIENT_LIGHT)))

                #Apply Tint
                colour = (min(0.99, colour[0]+(TINT[0])), min(0.99, colour[1]+(TINT[1])),min(0.99, colour[2]+(TINT[2])))
                # print(colour)
                # print (colour)
                if material.fuzzy:
                    enfuzzisize = True if (random.random() < material.fuzzy) else False
                    if enfuzzisize:
                        factor  = material.fuzzy + (material.fuzzy*0.1 if (random.random() < 0.5) else -material.fuzzy*0.1)
                        colour = (min(colour[0]*factor, 1), min(colour[1]*factor, 1), min(colour[2]*factor, 1))
                self.glColor(*colour)
            return True
        else:
            # print("i didn't hit")
            self.glColor(*self.clearColor)
            return False

    def render(self):
        fov = pi/2
        for y in range(self.height):
                for x in range(self.width):
                    flip = 1
                    if flip >= 1:
                        i =  (2*(x + 0.5)/self.width - 1)*math.tan(fov/2)*self.width/self.height
                        j = -(2*(y + 0.5)/self.height - 1)*math.tan(fov/2)

                        direction = norm(V3(i, j, -1))
                        hit = self.cast_ray(V3(0,0,0), direction, removed_channel=None, pos=(x,y))
                        if hit:
                            self.point(x,y) 

        # Render twice, once without red channel and once without blue, with a slightly different angle.
        # for angle in range(-1,1):
        #     for y in range(self.height):
        #         for x in range(self.width):
        #             flip = 1
        #             if flip >= 1:
        #                 i =  (2*(x + 0.5)/self.width - 1)*math.tan(fov/2)*self.width/self.height
        #                 j = -(2*(y + 0.5)/self.height - 1)*math.tan(fov/2)

        #                 direction = norm(V3(i, j, -1))
        #                 hit = self.cast_ray(V3(angle/5,0,0), direction, removed_channel=angle, pos=(x,y))
        #                 if hit:
        #                     self.point(x,y)


##Please for the love of God don't use non-4 multiples for your dimensions unless you want to absoultely do you know what to your you know what.

bitmap = Render(800,800,800,800, 0, 0)
# ivory = Material(diffuse=(1,1,1), albedo=(0.3,  0.7, 1), spec=50)
# rubber = Material(diffuse=(1,1,1), albedo=(1,  1, 0), spec=50)
# bllackpearl = Material(diffuse=(0.1, 0.1, 0.1), albedo=(0.1,  0.9, 1), spec=50)
# carrot = Material(diffuse=(1, 0, 0), albedo=(1,1, 0), spec=50)
# sapphire = Material(diffuse=(0, 0, 1), albedo=(0.7,  0.3, 1), spec=0.5)
# ruby = Material(diffuse=(1, 0, 0), albedo=(0.7,  0.3, 1), spec=0.5)
# fuzzytest = Material(diffuse=(210/255, 105/255, 30/255), albedo=(0.9,0.1, 0), spec=10, fuzzy=0.8)
# whitecloth =  Material(diffuse=(1,1,1), albedo=(1,0.1, 0), spec=10, fuzzy=0.8)
# sky = Material(diffuse=(0.9,0.9,1), albedo=(1,  1, 0), spec=0.1)
# water = Material(diffuse=(0,0,1), albedo=(1,  1, 0), spec=50, fuzzy=0.8)
grass = Material(diffuse=(0.48,0.98,0), albedo=(.75, .25), spec=50, fuzzy=0.8)
steel = Material(diffuse=(0.8,0.8,0.8), albedo=(.99, .35), spec=1)
dirt = Material(diffuse=(0.6,0.4,0.32), albedo=(.84, .16), spec=50, fuzzy=0.9)
rock = Material(diffuse=(0.8,0.8,0.8), albedo=(.84, .16), spec=50, fuzzy=0.9)
sun =  Material(diffuse=(0.93,0.55,0.22), albedo=(.84, .84), spec=50, fuzzy=0.9)
cloud = Material(diffuse=(0.99,0.9978,0.9878), albedo=(.90, .90), spec=1, fuzzy=0.9)

bitmap.lights = [
    Light(
    color=(1,1,1),
    position=V3(0,-2,2),
    intensity = 10,
    is_anaglyph=False
    ),

    Light(
    color=(1,1,1),
    position=V3(-1,-1,5),
    intensity = 1000,
    is_anaglyph=False    
    )

    # Light(
    # color=(1,1,1),
    # position=V3(2,0,-3),
    # intensity = 1000,
    # is_anaglyph=True
    # ),
    # Light(
    # color=(1,1,1),
    # position=V3(-2,-0,-3),
    # intensity = 1000,
    # is_anaglyph=True
    # )
]


##Snowman

# bitmap.scene = [
#     Sphere(V3(0.6, -2.0, -8), 0.15, rubber), # mouth dots upper right
#     Sphere(V3(-0.6, -2.0, -8), 0.15, rubber), # mouth dots upper left
#     Sphere(V3(0.3, -1.75, -8), 0.15, rubber), # mouth dots lower right
#     Sphere(V3(-0.3, -1.75, -8), 0.15, rubber), # mouth dots lower left
#     Sphere(V3(0, -2.5, -8), 0.3, carrot), # nose
#     Sphere(V3(-0.45, -2.9, -8), 0.08, rubber), # eye glare left
#     Sphere(V3(0.75, -2.9, -8), 0.08, rubber), # eye glare right
#     Sphere(V3(-0.6, -3, -8), 0.2, bllackpearl), # eye left
#     Sphere(V3(0.6, -3, -8), 0.2, bllackpearl), # eye right
#     Sphere(V3(0, 4, -8), 0.5, bllackpearl), # buttons lowest
#     Sphere(V3(0, 2, -8), 0.5, bllackpearl), # buttons mid
#     Sphere(V3(0, 0, -8), 0.5, bllackpearl), # buttons highest
#     Sphere(V3(0, -2.5, -8), 1.5, rubber), # tiny ball
#     Sphere(V3(0, 0, -8), 2, rubber), # middle ball
#     Sphere(V3(0, 3, -8), 3, rubber), # fat ball
# ]

# bitmap.scene = []
# i = 1
# for x in range(-3,3):
#     for y in range(-3,3):
#         x_ = float(x/3)
#         y_ = float(y/3)
#         z = 2 + i/4
#         i += 1
#         # print(x_,y_,float(z/10))
#         # print((1-abs(x_),1-abs(float(z/4)),1-abs(y_)))
#         bitmap.scene.append(Sphere(V3(x_,y_,-z), 0.5, ivory if x < 0  else rubber))

# bitmap.scene = [
#     Sphere(V3(0, 0, -8), 0.5, (1,1,1)),
#     Sphere(V3(0, 0, -7), 0.5, (0.8,0.6,0.1))

# ]



# Bears
bitmap.scene = [
    #Balls of steel
    Sphere(V3(-2.8, -0.5, -3.5), 0.4, material=steel),
    Sphere(V3(-2.0, 0, -3.5), 0.4, material=steel),
    Sphere(V3(-1.2, 0, -3.5), 0.4, material=steel),
    Sphere(V3(-0.4, 0, -3.5), 0.4, material=steel),
    Sphere(V3(0.4, 0, -3.5), 0.4, material=steel),
    Sphere(V3(1.2, 0, -3.5), 0.4, material=steel),
    Sphere(V3(2.0, 0, -3.5), 0.4, material=steel),
    Sphere(V3(2.8, -0.5, -3.5), 0.4, material=steel),
    # Clouds
    Cube(((-6,-2), (-5,-4), (-8, -7)), cloud ),
    Cube(((-1,3), (-5,-4), (-9, -8)), cloud ),
    # Mountains
    Pyramid([V3(-2, 2, -7), V3(-1.5, -2, -5), V3(-5.5, 2, -7), V3(2, 2, -5.5)], dirt),
    Pyramid([V3(2, 2, -7), V3(1.5, -3, -5), V3(5.5, 2, -7), V3(-2, 2, -5.5)], dirt),
    #Rocky Mountains
    Pyramid([V3(-4, 2, -7), V3(-2.5, -4, -5), V3(-9.5, 2, -7), V3(1, 2, -5.5)], rock),
    # Grass "plane"
    Cube(((-8, 8), (3, 2), (-8, -2)), grass ),


    #Sun
    Sphere(V3(0, -2, -16), 6, material=sun),

]
bitmap.render()


# bitmap.glFinish(r'snowman.bmp')

bitmap.glFinish(r'tests.bmp')


