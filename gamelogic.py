'''
Created on 2012-12-02

@author: Sebastien Ouellet sebouel@gmail.com
'''
try:
    import numpypy
except ImportError:
    pass
import numpy

import math

plotting = False
if plotting:
    from matplotlib import pyplot
    from matplotlib import cm

####### Parameters #######

viewed = False

influence_decay = 1.0
influence_formation = 1.0
influence_range = 1

tick_limit = 200

width = 50
height = 50

waypoint1 = (10,25)
waypoint2 = (35,25)
waypoint3 = (25,35)


c_len = 13
"""
chromosome = [random.randint(-10,10) for _ in xrange(c_len*4)]

chromosome =[1 for _ in xrange(52)]
chromosome[4] = 3
chromosome[1] = 2
chromosome[5] = -10
chromosome[19] = 10
chromosome[33] = 10
chromosome[47] = 10
#for i in xrange(0,4):
#    chromosome[5+(i*c_len):8+(i*c_len)] = [-10, 5, 5, -10]
#    chromosome[0+(i*c_len)] = 10
"""
##########################

class InfluenceMap():
    """ Influence map used by attackers """
    def __init__(self, world, dna):
        self.owner = None
        self.grid = numpy.zeros((width, height))
        self.world = world
        self.dna = dna
        self.waypoints = [waypoint1,waypoint2,waypoint3]
        self.generate()

    def generate(self):
        """ Generates an influence map for a given attacker given a set of parameters """
        i = 0
        indexes = [self.world.flag, self.world.base]+[w for w in self.waypoints]+[c.position for c in self.world.circles]+[s.position for s in self.world.squares]
        for index in indexes:
            amount = self.dna[i]
            if amount > 0:
                self.grid[index] = min(amount, self.grid[index]+(amount*influence_formation))
                #self.grid[index[0]-influence_range:index[0]+influence_range+1, index[1]-influence_range:index[1]+influence_range+1]
            else:
                self.grid[index] = max(amount, self.grid[index]+(amount*influence_formation))
            i += 1

    def update(self):
        """ Updates the influence of moving entities """
        #self.grid = self.grid*influence_decay
        #self.grid = numpy.clip(self.grid,-10,10)
        pasts = [c.past_location for c in self.world.circles]+[s.past_location for s in self.world.squares]
        for past in pasts:
            self.grid[past] = 0

        i = 5
        indexes = [c.position for c in self.world.circles]+[s.position for s in self.world.squares]
        for index in indexes:
            amount = self.dna[i]
            if amount > 0:
                self.grid[index] = min(amount, self.grid[index]+(amount*influence_formation))
                #self.grid[index[0]-influence_range:index[0]+influence_range+1, index[1]-influence_range:index[1]+influence_range+1]
            else:
                self.grid[index] = max(amount, self.grid[index]+(amount*influence_formation))
            i += 1

class World():
    """ Takes care of the flag """
    def __init__(self, circles, squares):
        self.circles = circles
        self.squares = squares
        self.width = width
        self.height = height
        self.real_flag = Flag((25,25))
        self.flag = self.real_flag.position
        self.base = (45,25)
        self.space = numpy.zeros((width, height))

    def update_flag(self):
        """ Updates the flag and allows players to find it """
        self.real_flag.update()
        self.flag = self.real_flag.position

    def update(self):
        """ Update the world map
        Useless for actual game """
        #self.space = numpy.zeros((width, height))
        for circle in self.circles:
            self.space[circle.position] = 1
        for square in self.squares:
            self.space[square.position] = 2
        self.space[self.flag] = 3
        self.space[self.base] = 4

class Flag():
    """ Flag which can be grabbed and passed by attackers """
    def __init__(self, position, owner=None):
        self.owner = owner
        self.position = position
        self.past = position
        
    def update(self):
        if self.owner:
            self.past = self.position
            self.position = self.owner.position
            if not self.owner.alive:
                self.owner = None

class Square():
    """ Defends the flag """
    def __init__(self, position, id, circles):
        self.starting_position = position
        self.position = position
        self.id = id
        self.speed = 0.5
        self.health = 4
        self.aggression = 7
        self.past_location = position
        self.circles = circles
        self.goal = self.starting_position
        self.direction = (0,0)
        self.range = 2
        self.alive = True
        self.target = None
            
    def find_goal(self):
        """ Finds the nearest attacker within range """
        nearest = None
        min_distance = width*2
        for circle in self.circles:
            if circle.alive:
                d = distance(self.position, circle.position)
                if d < min_distance:
                    nearest = circle
                    min_distance = d
        if min_distance < self.aggression:
            self.goal = nearest.position
            if min_distance < self.range:
                self.target = nearest
            else:
                self.target = None
        else:
            self.goal = self.starting_position
            self.target = None

    def set_direction(self):
        """ Sets a vector toward an acquired goal """
        v = (self.goal[0]-self.position[0],self.goal[1]-self.position[1])
        length = math.sqrt(v[0]**2+v[1]**2)
        if length < 1:
            pass
        else:
            self.direction = (v[0]/length*self.speed, v[1]/length*self.speed)

    def move(self):
        i = 0
        xy = [0,0]
        while i < 2:
            xy[i] = self.position[i]+self.direction[i]
            if xy[i] < 0:
                xy[i] = 0
            elif xy[i] > width-1:
                xy[i] = width-1
            i += 1

        self.past_location = self.position
        self.position = (xy[0],xy[1])
    
    def is_alive(self):
        if self.health < 1:
            self.alive = False
            self.target = None
        elif self.health > 0:
            self.alive = True
    
    def attack(self): 
        """ Reduces health of an acquired target """
        if self.target != None:
            self.target.health += -1
            #print "Square attack", self.target.health
    
    def update(self, world):
        self.is_alive()
        if self.alive:
            self.find_goal()
            self.set_direction()
            self.move()
            self.attack()
        
class Circle():
    """ Captures the flag """
    def __init__(self, position, id):
        self.position = position
        self.id = id
        self.influence_map = None
        self.speed = 0.5
        self.goal = None
        self.health = 2
        self.range = 2
        self.direction = (0,0)
        self.past_location = position
        self.alive = True
        self.squares = None
        self.reach = 2
        self.flag_throw = 6
        
    def generate_influence_map(self, world, chromosome):
        """ Produces its influence map """
        dna = chromosome[c_len*(self.id-1):c_len*self.id]
        self.influence_map = InfluenceMap(world, dna)

    def find_goal(self):
        """ Finds the location with the highest influence """
        index = self.influence_map.grid.argmax()
        x = index/width
        y = index-(x*width)
        self.goal = (x,y)

    def set_direction(self):
        """ Sets a vector toward an acquired goal """
        v = (self.goal[0]-self.position[0],self.goal[1]-self.position[1])
        length = math.sqrt(v[0]**2+v[1]**2)
        if length < 1:
            pass
        else:
            self.direction = (v[0]/length*self.speed, v[1]/length*self.speed)

    def move(self):
        i = 0
        xy = [0,0]
        while i < 2:
            xy[i] = self.position[i]+self.direction[i]
            if xy[i] < 0:
                xy[i] = 0
            elif xy[i] > width-1:
                xy[i] = width-1
            i += 1

        self.past_location = self.position
        self.position = (xy[0],xy[1])

    def is_alive(self):
        if self.health < 1:
            self.alive = False
        elif self.health > 0:
            self.alive = True

    def attack(self):
        """ Finds nearest defender and reduces its health """
        nearest = None
        min_distance = width*2
        for square in self.squares:
            if square.alive:
                d = distance(self.position, square.position)
                if d < min_distance:
                    nearest = square
                    min_distance = d
        if min_distance < self.range:
            nearest.health += -1
            #print "Attack!", nearest.health
    
    def grab_flag(self, world):
        """ Looks if the flag is within reach to become its owner """
        d = distance(self.position, world.real_flag.position)
        if d <= self.reach:
            if world.real_flag.owner == None:
                world.real_flag.owner = self
    
    def pass_flag(self, world):
        """ Looks if a teammate is nearer than itself to the base to change ownership of the flag """
        if world.real_flag.owner == self:
            far = distance(self.position, world.base)
            for circle in world.circles:
                if circle.alive and circle.id != self.id:
                    base_distance = distance(circle.position, world.base)
                    if base_distance < far:
                        throw_distance = distance(self.position, circle.position)
                        if throw_distance < self.flag_throw:
                            world.real_flag.owner = circle
                            break
                    
    def update(self, world):
        """ Manages all actions of the attacker.
        Test for lifeness is after the behavior given that attackers act last in the update cycle """
        if self.alive:
            self.influence_map.update()
            self.find_goal()
            self.set_direction()
            self.move()
            self.attack()
            self.grab_flag(world)
            self.pass_flag(world)
        self.is_alive()
        
        
def distance(reference, target):
    """ Calculates the Euclidean distance between two objects """
    return math.sqrt((target[0]-reference[0])**2+(target[1]-reference[1])**2)

def calculate_score(world, won, tick):
    score = 200
    if world.flag != (25,25):
        score += -30
        score += distance(world.flag, world.base)
        if won:
            score += -150
    score += tick/10
        
    
    for circle in world.circles:
        if circle.alive:
            score += -1  
        
    return score   

def simulate(influence_dna):
    if viewed:
        import graphics
    
    run = True

    c1 = Circle((10,0), 1)
    c2 = Circle((20,0), 2)
    c3 = Circle((30,0), 3)
    c4 = Circle((40,0), 4)
    circles = [c1,c2,c3,c4]
    
    s1 = Square((22,22), 5, circles)
    s2 = Square((28,28), 6, circles)
    s3 = Square((22,28), 7, circles)
    s4 = Square((28,22), 8, circles)

    squares = [s1,s2,s3,s4]
    for circle in circles:
        circle.squares = squares
    
    world = World(circles, squares)

    for circle in circles:
        circle.generate_influence_map(world, influence_dna)

    everything = squares+circles

    for thing in everything:
        thing.update(world)
    #world.update()

    if viewed:
        graphics.pygame.init()
        screen = graphics.pygame.display.set_mode((graphics.screen_width, graphics.screen_height))
        graphics.pygame.display.set_caption('This is a video game')
        screen.fill(graphics.white)
        graphics.pygame.display.flip()

        pygame_clock = graphics.pygame.time.Clock()
        
        all_sprites = graphics.pygame.sprite.OrderedUpdates()
        
        graphics.update_sprites(all_sprites, [world.flag, world.base,squares,circles])    
        
    if plotting:    
        pyplot.imsave("world.png", c1.influence_map.grid, cmap=cm.RdBu, vmin=-10, vmax=10)
    tick = 0
    won = 0
    while run:            
        if tick > tick_limit:
            run = False
        if distance(world.flag, world.base) < 1.5:
            run = False 
            won = True
        dead = 0
        for circle in circles:
            if not circle.alive:
                dead += 1
        if dead == 4:
            run = False            
            
        for thing in everything:
            thing.update(world)
            #print thing.id, thing.health, thing.speed
        world.update_flag()
        #world.update()
            
        if viewed:
            pygame_clock.tick(graphics.framerate)
            if graphics.input():
                run = False
            screen.fill(graphics.white)
            graphics.update_sprites(all_sprites, [world.flag, world.base, squares, circles])
            all_sprites.draw(screen)
            graphics.pygame.display.flip()

        if plotting:
            pyplot.imsave("images/c1influence"+str(tick)+".png", c1.influence_map.grid, cmap=cm.RdBu, vmin=-10, vmax=10)
            if tick == tick_limit-1:
                pyplot.imsave("c1influence.png", c1.influence_map.grid, cmap=cm.RdBu, vmin=-10, vmax=10)
                pyplot.imsave("c2influence.png", c2.influence_map.grid, cmap=cm.RdBu, vmin=-10, vmax=10)
                pyplot.imsave("world"+str(tick)+".png", world.space)
                numpy.savetxt("bla.txt",c1.influence_map.grid, fmt="%0.2f")
        tick += 1
        
    if viewed:
        print "Press Escape to quit"
        while not graphics.input():
            pass
        graphics.pygame.quit()
    
    score = calculate_score(world, won, tick)
    return score

