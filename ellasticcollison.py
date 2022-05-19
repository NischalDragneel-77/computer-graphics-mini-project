from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random

# Size of the screen 
WIDTH = 800
HEIGHT = 600

NUM_BALLS = 10
RADIUS = 1
MAX_VELOCITY = 0.005
COLOR_ON = True             
CUBE_SIZE_HALF = 7          

ballList = []

# Function to draw the Cube
def Cube():
    vertices = (
        ( CUBE_SIZE_HALF,-CUBE_SIZE_HALF,-CUBE_SIZE_HALF),
        ( CUBE_SIZE_HALF, CUBE_SIZE_HALF,-CUBE_SIZE_HALF),
        (-CUBE_SIZE_HALF, CUBE_SIZE_HALF,-CUBE_SIZE_HALF),
        (-CUBE_SIZE_HALF,-CUBE_SIZE_HALF,-CUBE_SIZE_HALF),
        ( CUBE_SIZE_HALF,-CUBE_SIZE_HALF, CUBE_SIZE_HALF),
        ( CUBE_SIZE_HALF, CUBE_SIZE_HALF, CUBE_SIZE_HALF),
        (-CUBE_SIZE_HALF,-CUBE_SIZE_HALF, CUBE_SIZE_HALF),
        (-CUBE_SIZE_HALF, CUBE_SIZE_HALF, CUBE_SIZE_HALF)
        )

    # Edges of the cube
    edges = (
        (0,1),
        (0,3),
        (0,4),
        (2,1),
        (2,3),
        (2,7),
        (6,3),
        (6,4),
        (6,7),
        (5,1),
        (5,4),
        (5,7)
        )
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

# Class Ball (for each ball)
class Ball:
    center = []
    velocity = [] 
    color = [1.0,1.0,1.0,1.0]
    lastCollision = -1
    def __init__(self, center, velocity, color, RADIUS):        
        self.center = center
        self.velocity = velocity
        self.color = color
        self.RADIUS = RADIUS
    def changePosition(self):
        for i in range(3):
            self.center[i] = self.center[i] + self.velocity[i]
    def setLastCollision(self, lastCollision):
        self.lastCollision = lastCollision
    def getLastCollision(self):
        return self.lastCollision

# Determines the Dot Product between 2 vectors (vec_1 . vec_2)
def dotProduct(vec_1, vec_2):
    return (vec_1[0] * vec_2[0] + vec_1[1] * vec_2[1] + vec_1[2] * vec_2[2])

# Calculates the Magnitude of a vector
def sizeVector(vec_1):
    return (math.sqrt( vec_1[0] ** 2 + vec_1[1] ** 2 + vec_1[2] ** 2 ))

# calculates the relative distance between two points (x1,y1,z1) and (x2,y2,z2)
def distPoints(vec_1, vec_2):
    return (math.sqrt((vec_1[0] - vec_2[0]) ** 2 + (vec_1[1] - vec_2[1]) **2 + (vec_1[2] - vec_2[2]) ** 2 ))

# Function to determine the orthogonal projection of a vector1(vec_1) onto vector2(vec_2)
def orthogonalProjection(vec_1, vec_2):
    alfa = dotProduct(vec_1, vec_2) / sizeVector(vec_2) ** 2
    vector = []
    for i in range(len(vec_2)): 
        vector.append(vec_2[i] * alfa)
    return vector

# Function to determine the subtraction between two vectors (vec_1 - vec_2)
def subVector(vec_1, vec_2):
    vector = []
    if len(vec_1) == len(vec_2):
        for i in range(len(vec_1)):
            vector.append(vec_1[i] - vec_2[i])
        return vector
    else:
        print("Impossible to subtract vectors of different sizes")

# Function to handdle collision with balls
def ballCollision(i, j):
    global ballList
    collisionDirection = []
    for x in range(3):
        collisionDirection.append( ballList[j].center[x] - ballList[i].center[x] )
    w1 = orthogonalProjection(ballList[i].velocity, collisionDirection)
    w2 = orthogonalProjection(ballList[j].velocity, collisionDirection)
    u1 = subVector(ballList[i].velocity , w1)
    u2 = subVector(ballList[j].velocity, w2)
    for x in range(3):
        ballList[i].velocity[x] = u1[x] + w2[x]
        ballList[j].velocity[x] = u2[x] + w1[x]

# Function to initialize OpenGL, called after the window is created
def initializeGl():
    glClearColor(0.,0.,0.,1.)                               
    glShadeModel(GL_SMOOTH)                                 
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    lightZeroColor = [1.0,1.0,1.0,1.0]                      # White light      
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)        
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)       
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
    glEnable(GL_LIGHT0)

# Function to handle if the screen is resized
def screenResize(WIDTH, HEIGHT):
    if HEIGHT == 0:						# Prevent A Divide By Zero If The Window Is Too Small
        HEIGHT = 1
    glViewport(0, 0, WIDTH, HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(WIDTH)/float(HEIGHT), 0.1, 6*CUBE_SIZE_HALF)
    glMatrixMode(GL_MODELVIEW)

# Function to check collisions and update the position of the balls
def update():
    global ballList
    for i in range(len(ballList)):
        ballList[i].changePosition()

    # Test if each ball is colliding with other balls
    # The 'x' thing is to not check collision with the same balls two times in a row
    x = 1
    for i in range(len(ballList)):
        for j in range(len(ballList) - x):
            if((distPoints(ballList[i].center, ballList[j + x].center)) <= ballList[i].RADIUS + ballList[j+x].RADIUS) and ((ballList[i].getLastCollision() != (j+x)) or (ballList[j+x].getLastCollision() != i)):
                ballCollision(i, j+x)
                ballList[i].setLastCollision(j+x)
                ballList[j+x].setLastCollision(i)
        x +=1
    # Test the collision of the balls with the walls of the cube
    for i in range(len(ballList)):
        if (ballList[i].center[0] - ballList[i].RADIUS < -CUBE_SIZE_HALF or ballList[i].center[0] + ballList[i].RADIUS > CUBE_SIZE_HALF):   # x
            ballList[i].velocity[0] *= -1
            ballList[i].setLastCollision(-1)
        if (ballList[i].center[1] - ballList[i].RADIUS < -CUBE_SIZE_HALF or ballList[i].center[1] + ballList[i].RADIUS > CUBE_SIZE_HALF):   # y
            ballList[i].velocity[1] *= -1
            ballList[i].setLastCollision(-1)
        if (ballList[i].center[2] - ballList[i].RADIUS < -CUBE_SIZE_HALF or ballList[i].center[2] + ballList[i].RADIUS > CUBE_SIZE_HALF):   # z
            ballList[i].velocity[2] *= -1
            ballList[i].setLastCollision(-1)

    # Function to print text on the screen
def printText( x,  y, z, text):
    glColor3f(1,1,1)
    glWindowPos3f(x,y,z)
    for ch in text :
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15 , ctypes.c_int(ord(ch)))

# GLUT Display function
def display():
    global ballList
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    # Update ball position and check collisions
    update()
    # Draw the Cube
    glPushMatrix()
    color = [1.0,1.0,1.0,1.0]
    glMaterialfv(GL_FRONT,GL_AMBIENT,color)
    glMaterialfv(GL_FRONT,GL_EMISSION,[0.0, 0.0, 0.0, 0.0])
    Cube()
    glPopMatrix()   
    # Draw Balls
    for i in range(len(ballList)):
        glPushMatrix()
        glMaterialfv(GL_FRONT,GL_DIFFUSE,ballList[i].color)
        glMaterialfv(GL_FRONT,GL_AMBIENT,[0.0, 0.0, 0.0, 0.0])
        glTranslatef(ballList[i].center[0],ballList[i].center[1],ballList[i].center[2])
        glutSolidSphere(ballList[i].RADIUS, 20, 20)
        glPopMatrix()
    kineticEnergy = 0.00
    for i in range(len(ballList)):
        kineticEnergy += float((sizeVector(ballList[i].velocity) ** 2) / 2.0)
    glPushMatrix()
    printText( 1 , 1 , -1 , "K = " + str(round(kineticEnergy, 12)))
    printText(1, 17, -1, "Balls: " + str(NUM_BALLS) + "  RADIUS: " + str(RADIUS))
    printText(1, 33, -1, "Size of the Cube: " + str(2*CUBE_SIZE_HALF))
    glPopMatrix()
    glutSwapBuffers()
    return

# Function to create the balls in different positions, with different velocities and different collors
def inicializeBalls():
    centerList = randomCenter(NUM_BALLS)
    for i in range(NUM_BALLS):
        ballList.append(Ball(centerList[i], randomVelocity(), randomColor(), RADIUS))

# Function to give the balls the start center position
def randomCenter(NUM_BALLS):
    vector = []
    qBall = int((CUBE_SIZE_HALF / RADIUS))
    qBall3 = qBall ** 3
    if(qBall3 >= NUM_BALLS):
        for j in range (NUM_BALLS):  # For all the balls
            pos = newPos(qBall)
            while (checkBallInside(vector, pos)):
                pos = newPos(qBall)
            vector.append(pos)
    else: 
        print("Selected number of balls cannot be distributed in the cube so increase cube size or decrease number of balls")
        quit()
    return vector

# Function to generate a new position for the list in randomCenter() Function
def newPos(qBall):
    pos = []
    if (qBall == 2):
        for i in range(3):  # X, Y, Z ( 3 times )
            randomNumber = random.choice( [-1,1] )
            pos.append(randomNumber * RADIUS)
    elif not (qBall % 2):    # Even number
        for i in range(3):  # X, Y, Z ( 3 times )
            randomNumber = random.randint( -qBall / 2 , qBall / 2 )
            if (randomNumber > 0): 
                pos.append(randomNumber * 2 * RADIUS - RADIUS)
            elif (randomNumber < 0):
                pos.append(randomNumber * 2 * RADIUS + RADIUS)
            else:   # randomNumber == 0
                randomNumber = random.choice( [-1,1] )
                pos.append(randomNumber * RADIUS)
    else:                   # Odd number
        for i in range(3):  # X, Y, Z ( 3 times )
            randomNumber = random.randint( int(-qBall / 2) , int(qBall / 2 ))
            pos.append(randomNumber * 2 *RADIUS)
    return pos

# Function to determine how many balls in the vector created on the randomCenter() function  are inside each other 
def checkBallInside(vector, pos):
    # The 'x' thing is to not check the same balls two times in a row
    for i in range(len(vector)):
        if(vector[i][0] == pos[0]) and (vector[i][1] == pos[1]) and (vector[i][2] == pos[2]):
            return True
    return False

# Function to give a ball the start velocity
def randomVelocity():
    vector = [] 
    for i in range(3):
        vector.append( round(random.uniform( -MAX_VELOCITY , MAX_VELOCITY  ), 4) )
    return vector

# Function to give a ball a random color
def randomColor():
    if(COLOR_ON):
        color = [random.choice( [0.0,1.0] ), random.choice( [0.0,1.0] ), random.choice( [0.0,1.0] ), 1.0]
        while (color[0] == 0.0) and (color[1] == 0.0) and (color[2] == 0.0):
            color = [random.choice( [0.0,1.0] ), random.choice( [0.0,1.0] ), random.choice( [0.0,1.0] ), 1.0]
    else:
        color = [1.0,1.0,1.0,1.0]
    return color

def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)                                                                       
    glutInitWindowPosition(0, 0)                                                                               
    glutCreateWindow('Ellastic Collision with balls')                                                        
    glutDisplayFunc(display)                                                                                
    glutIdleFunc(display)                                                                                     
    glutReshapeFunc(screenResize)                                                                            
    inicializeBalls()
    initializeGl()
    gluLookAt(0,0,4*CUBE_SIZE_HALF,
              0,0,0,
              1,1,0)
    glPushMatrix()
    glutMainLoop()

if __name__ == "__main__":
    main()