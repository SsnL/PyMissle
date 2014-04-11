import pygame
from pygame.locals import *
from sys import exit
from modules.vector2 import *
from math import sin,cos,pi,atan2,sqrt
from copy import deepcopy
from random import random,randint

def set_ship(i,x,y):
    ship_file = 'ship_'+str(i)+'.png'
    ship=Ships(ship_file,str(i),1,i,0.2)
    ship.set_pos(x, y)
    ship.set_speed(150.)
    ship.set_acc(400.,1,10.,1)
    ship.set_angle(0.)
    ship.set_angle_speed(200.)
    return ship
    
def generateMap(planet_h,x,y):
    planet=[]
    count=0
    while count<8000:
        tx=random()
        ty=random()
        tr=random()
        tx*=986
        tx+=19
        ty*=730
        ty+=19
        tr*=105
        tr+=70
        count+=1
        q=True
        for x in planet:
            if (Vector2(x[0])-Vector2(tx,ty)).get_length()<=tr+x[1]+145:
                q=False
                break
        if q:
            for x in planet_h:
                if (Vector2(x[0])-Vector2(tx,ty)).get_length()<=tr+x[1]+70:
                    q=False
                    break
        if q:
            tx=int(tx)
            ty=int(ty)
            tr=int(tr)
            tp=pygame.image.load('image/planet.png').convert_alpha()
            tp=pygame.transform.rotozoom(tp, 0,(tr*2.)/341)
            planet.append([(tx,ty),tr,(randint(0,255), randint(0,255), randint(0,255)),tp])
    return planet

def generateBonus(name,drot):
    while True:
        tx=random()
        ty=random()
        tx*=980
        tx+=22
        ty*=724
        ty+=22
        tr=25
        q=True
        for x in planet:
            if (Vector2(x[0])-Vector2(tx,ty)).get_length()<=tr+x[1]+15:
                q=False
                break
        if q:
            for x in ship:
                if (x.position-Vector2(tx,ty)).get_length()<=tr+65:
                    q=False
                    break
        if q:
            tx=int(tx)
            ty=int(ty)
            tr=int(tr)
            tp=Bonus(Vector2(tx,ty),name,drot)
            return tp
    
def showMissilePower(num):
    if ship[num].missile_power<4.5:
        ship[num].missile_power+=time_passed*2
    if ship[num].missile_power>0.6:
        rp = ship[num].position-Vector2(50,58)
        rs = Vector2(100*ship[num].missile_power/4.5,6)
        pygame.draw.rect(screen, (140,129,206), Rect(rp, rs))

def keyEvents(pressed_keys):
        if pressed_keys[K_LEFT]:
            ship[0].rotation = +1.
        if pressed_keys[K_RIGHT]:
            ship[0].rotation = -1.
        if pressed_keys[K_UP]:
            ship[0].direction = +1.
        if pressed_keys[K_DOWN]:
            ship[0].direction = -1.
        if pressed_keys[K_a]:
            ship[1].rotation = +1.
        if pressed_keys[K_d]:
            ship[1].rotation = -1.
        if pressed_keys[K_w]:
            ship[1].direction = +1.
        if pressed_keys[K_s]:
            ship[1].direction = -1.
        if pressed_keys[K_m]:
            if not ship[0].tele:
                ship[0].tele=Teleport()
        if pressed_keys[K_1]:
            if not ship[1].tele:
                ship[1].tele=Teleport()
        if pressed_keys[K_n]:
            if ship[0].ori_shield==1:
                ship[0].shield=Shield(0)
                ship[0].ori_shield=0
        if pressed_keys[K_2]:
            if ship[1].ori_shield==1:
                ship[1].shield=Shield(1)
                ship[1].ori_shield=0

def isCollisionPlanet(Apos,a,AsizeX,AsizeY, BposX, BposY, Br):
    t=Vector2(sin(a*pi/180.)*AsizeX,cos(a*pi/180.)*AsizeY)/2
    ax,ay=Apos+t
    bx,by=Apos-t
    if (ax-BposX)**2+(ay-BposY)**2<=Br**2 or\
       (bx-BposX)**2+(by-BposY)**2<=Br**2:
        return True
    else:
        return False
    
def isInsidePlanet(Apos,BposX, BposY, Br):
    ax,ay=Apos
    if (ax-BposX)**2+(ay-BposY)**2<Br**2:
        return True
    else:
        return False
    
def isGetBonus(Apos,isShield,Bpos):
    iSh=0
    if isShield:
        iSh=1
    ax,ay=Apos
    bx,by=Bpos
    if (ax-bx)**2+(ay-by)**2<(60+13*iSh)**2:
        return True
    else:
        return False
    
def set_missile(ship):
    sound_launch_missile.play()
    v=ship.speed+110+ship.missile_power*115.
    missile_file = 'missile'+str(ship.num)+'.png'
    missile=Missiles(missile_file,1)
    missile.position=(0,0)
    missile.rotate_im(ship.angle)
    s=ship.position
    missile.set_pos(s.x,s.y)
    missile.set_speed(v)
    return missile

def get_angle(v):
    if v.y==0:
        return 0
    return atan2(v.y,v.x)/pi*180

class Obj(pygame.sprite.Sprite):
    def __init__(self,filename="",alpha=0,size=1):
        pygame.sprite.Sprite.__init__(self)
        if filename:
            if alpha:
                self.surface=pygame.image.load('image/'+filename).convert_alpha()
            else:
                self.surface=pygame.image.load(filename).convert()
            if size!=1:
                self.surface=pygame.transform.rotozoom(self.surface, 0,size)
            Obj.get_size(self)
            self.ori=self.surface
            self.angle=0
            self.cVelocity=Vector2(0,0)
            self.ori_acc=0
            self.direction=1
            self.dead=0
            self.explode=None
            
    def update(self):
        self.get_size()
        self.get_velo()
        self.get_current_velo()
            
    def get_size(self):
        self.wid,self.hei=self.surface.get_size()
        self.size=(self.wid,self.hei)
        self.ori_h=self.hei
        return self.size
        
    def set_speed(self,v):
        self.speed=v
        self.get_velo()
        return self.speed
    
    def get_velo(self):
        self.velocity=Vector2(sin(self.angle*pi/180.),cos(self.angle*pi/180.))*self.speed
        return self.velocity
    
    def set_current_speed(self,cv):
        self.cSpeed=cv
        return self.cSpeed
    
    def get_current_velo(self):
        self.cVelocity=Vector2(sin(self.angle*pi/180.),cos(self.angle*pi/180.))*self.cSpeed
        return self.cVelocity
    
    def set_acc(self,a,d,da,ini=0):
        if ini:
            self.ori_acc=a
            self.ori_dacc=da
        if d!=0:
            self.acc=Vector2(sin(self.angle*pi/180.),cos(self.angle*pi/180.))*d*a
        else:
            self.acc=-self.cVelocity.normalise()*da
        return self.acc
        
    def set_angle_speed(self,av):
        self.angleSpeed=av
        return self.angleSpeed
        
    def set_pos(self,x,y):
        self.position=Vector2((x,y))
        return self.position
        
    def set_angle(self,t):
        self.angle=t
        return self.angle
        
    def rotate(self,dw):
        dwr=time_passed*dw*self.angleSpeed
        self.angle+=dwr 
        self.surface=pygame.transform.rotate(self.ori, self.angle)
        Obj.get_size(self)
        return self.angle
    
class Ships(Obj):
    def __init__(self,filename,name,alpha,num,size):
        Obj.__init__(self,filename,alpha,size)
        self.direction=0
        self.rotation=0
        self.missile_power=0.2
        self.num=num
        self.name=name
        self.tele=None
        self.shield=None
        self.ori_shield=1
        self.missile_list=[]
        
    def move_smooth(self,d):
        self.get_velo()
        self.position+=self.velocity*time_passed*d
        return self.position
    
    def make_missile(self):
        self.missile_list.append(set_missile(self))
        self.missile_power=0.2 
    
    def update_missiles(self):
        for k in xrange(len(self.missile_list)-1,-1,-1):
            i=self.missile_list[k] 
            if i.dead==1:
                self.missile_list.remove(i)
                continue
            elif i.dead==0:
                i.update()
            if i.dead==-1: 
                i.explode=MissileExplode()
                i.dead=-2
            elif i.dead==-2:
                i.explode.update(i)
    
    def update(self):
        if fweapon:
            if isGetBonus(self.position,self.shield,fweapon.position):
                fweapon.used=1
                for i in xrange(30):
                    self.angle+=12
                    self.missile_list.append(set_missile(self))
        if not self.shield and fshield:
            if isGetBonus(self.position,0,fshield.position):
                fshield.used=1
                self.shield=Shield(self.num)
        self.update_missiles()
        if self.tele:
            if not self.tele.update(self):
                self.tele=None
        if self.dead: return None
        self.move_smooth(self.direction)
        if self.position.x<0:
            self.position.x=0
        elif self.position.x>1024:
            self.position.x=1024
        if self.position.y<0:
            self.position.y=0
        elif self.position.y>768:
            self.position.y=768
        for p in planet:
            px,py=p[0]
            if isInsidePlanet(self.position,px,py,p[1]+12):
                ang=get_angle(self.position-p[0])*pi/180.
                self.position=p[0]+Vector2(cos(ang),sin(ang))*(p[1]+12)
                break
        self.rotate(self.rotation)
        draw_pos=Vector2(self.position.x-self.wid/2, self.position.y-self.hei/2)
        screen.blit(self.surface, draw_pos)
        if self.shield:
            self.shield.update(self)
    
class Missiles(Obj):
    def move(self,ax=0,ay=0):
        self.position+=(self.velocity+Vector2(ax,ay)/2)*time_passed
        final_v=self.velocity+Vector2(ax,ay)*time_passed
        self.rotate_im(90-get_angle(final_v+Vector2(ax,ay)*time_passed))
        self.velocity=final_v
        return self.position
    
    def rotate_im(self,dwr):
        self.angle=dwr 
        self.surface=pygame.transform.rotate(self.ori, dwr)
        Obj.get_size(self)
        return self.angle
    
    def update(self):
        w,h=Vector2(self.size)
        for j in ship:
            if self in j.missile_list or j.dead:
                continue
            sx,sy=j.position
            r=35
            if j.shield:
                r+=13
            if isCollisionPlanet(self.position,self.angle,w,h,sx,sy,r):
                self.dead=-1
                if j.shield:
                    j.shield=None
                else:
                    j.dead=-1
        for p in planet:
            px,py=p[0]
            if isCollisionPlanet(self.position,self.angle,w,h,px,py,p[1]-8):
                self.dead=-1
        if self.dead==0:
            ap=Vector2(0,0)
            for p in planet:
                px,py=(Vector2(p[0])-self.position)
                ap+=(p[1]**2*860./(px**2+py**2))*(Vector2(p[0])-self.position).normalise()
            ax,ay=ap
            self.move(ax,ay)
            draw_pos=self.position-Vector2(self.wid,self.hei)/2
            screen.blit(self.surface, draw_pos)
        return 0

class Animation(pygame.sprite.Sprite):
    images = []
    at=0
    def __init__(self,name,order,width,height,rate,number,rotate=0):
        self.width = width #384
        self.height = height #192
        self._rate = rate #0.05
        self._number = number #18
        self.order=order
        pygame.sprite.Sprite.__init__(self)
        self.surface=pygame.image.load('image/'+name+'.png').convert_alpha()
        if rotate:
            self.images= [pygame.transform.rotate(self.surface.subsurface(Rect(self.order[i], (self.width, self.height))),rotate) for i in xrange(len(self.order))]
        else:
            self.images= [self.surface.subsurface(Rect(self.order[i], (self.width, self.height))) for i in xrange(len(self.order))]
        self.image = self.images[self.at]
        self.passed_time = 0
        self.isTele=0
        self.rect = Rect(0, 0, self.width, self.height)
 
class Teleport(Animation):
    def __init__(self):
        order = [(0, 0), (576, 0), 
                 (0, 192), (576, 192), 
                 (0, 384), (576, 384), 
                 (0, 576), (576, 576), 
                 (0, 768), (576, 768), 
                 (0, 960), (576, 960), 
                 (0, 1152), (576, 1152), 
                 (0, 1344), (576, 1344),
                 (0, 1536), (576, 1536)]
        Animation.__init__(self,'teleport copy',order,384,192,0.05,18,90)
 
    def update(self,ship):
        self.passed_time += time_passed
        self.at = ( self.passed_time / self._rate ) % self._number
        x=True
        self.at=int(self.at)
        if self.at == 0 and self.passed_time > self._rate: 
            x=False
        else:
            if self.at==10 and self.isTele==0:
                ship.position+=240*Vector2(sin(ship.angle*pi/180.),cos(ship.angle*pi/180.))
                self.isTele=1
            self.image = self.images[self.at]
            s=deepcopy(ship.position)
            self.surface1=self.image
            self.surface1=pygame.transform.rotate(self.image, ship.angle)
            w,h=self.surface1.get_size()
            s+=132*Vector2(sin((ship.angle)*pi/180.),cos((ship.angle)*pi/180.))
            s-=Vector2(w,h)/2
            if self.at>=10:
                s-=240*Vector2(sin(ship.angle*pi/180.),cos(ship.angle*pi/180.))
            screen.blit(self.surface1, (s.x,s.y))
        return x
 
class Explode(Animation):
    def __init__(self):
        order = [(0, 0), (96, 0), 
                 (0, 96), (96, 96), 
                 (0, 192), (96, 192), 
                 (0, 288), (96, 288), 
                 (0, 384), (96, 384), 
                 (0, 480), (96, 480), 
                 (0, 576), (96, 576), 
                 (0, 672), (96, 672), 
                 (0, 768), (96, 768), 
                 (0, 864), (96, 864), 
                 (0, 960), (96, 960), 
                 (0, 1056), (96, 1056)]
        Animation.__init__(self,'explode',order,96,96,0.05,24)
        sound_ship_explode.play()
 
    def update(self,ship):
        self.passed_time += time_passed
        self.at = ( self.passed_time / self._rate ) % self._number
        self.at=int(self.at)
        if self.at == 0 and self.passed_time > self._rate: 
            ship.dead=1
        else:
            screen.blit(self.images[self.at], ship.position-Vector2(self.width,self.height)/2)

class MissileExplode(Animation):
    def __init__(self):
        order =[(0, 0), (48, 0), 
                (96, 0), (144, 0), 
                (192, 0), (0, 48), 
                (48, 48), (96, 48), 
                (144, 48), (192, 48), 
                (0, 96), (48, 96)]
        Animation.__init__(self,'missile_explode',order,48,48,0.05,12)
        sound_missile_explode.play()
 
    def update(self,missile):
        self.passed_time += time_passed
        self.at = ( self.passed_time / self._rate ) % self._number
        self.at=int(self.at)
        if self.at == 0 and self.passed_time > self._rate: 
            missile.dead=1
        else:
            screen.blit(self.images[self.at], missile.position-Vector2(self.width,self.height)/2)
            
class Shield(Animation):
    def __init__(self,num):
        order =[(0, 0), (192, 0), (384, 0), (576, 0), (768, 0), 
                (0, 192), (192, 192), (384, 192), (576, 192), (768, 192), 
                (0, 384), (192, 384), (384, 384), (576, 384), (768, 384)]
        Animation.__init__(self,'shield_'+str(num),order,192,192,0.06,15)
 
    def update(self,ship):
        self.passed_time += time_passed
        self.at = ( self.passed_time / self._rate ) % self._number
        self.at=int(self.at)
        if self.at == 0 and self.passed_time > self._rate:
            self.passed_time = 0
        screen.blit(self.images[self.at], ship.position-Vector2(self.width,self.height)/2)

class Bonus(Obj):
    def __init__(self,pos,name,drot):
        Obj.__init__(self,name+'.png',1)
        self.angleSpeed=300
        self.drot=drot
        self.angle=0
        self.used=0
        self.position=pos
    
    def update(self):
        dwr=time_passed*self.angleSpeed*self.drot
        self.angle+=dwr 
        self.surface=pygame.transform.rotate(self.ori, self.angle)
        Obj.get_size(self)
        draw_pos=Vector2(self.position.x-self.wid/2, self.position.y-self.hei/2)
        screen.blit(self.surface, draw_pos)
    
class Sound(pygame.mixer.Sound):
    def __init__(self,filename,volume=0):
        pygame.mixer.Sound.__init__(self,'sound/'+filename)
        if volume: self.set_volume(volume)
      
class MenuDisplay(): 
    def __init__(self, *options): 
        self.options = options 
        self.x = 0
        self.y = 0
        self.option = 0
        self.width = 1
        self.color = [0, 0, 0] 
        self.hcolor = [0, 0, 0] 
  
    def draw(self, surface): 
        i=0
        for o in self.options: 
            if i==self.option: 
                clr = self.hcolor 
            else: 
                clr = self.color 
            text = o[0] 
            stri = self.font.render(text, 1, clr) 
            surface.blit(stri, (self.x-stri.get_width()/2., self.y + i*self.line_height-stri.get_height()/2.)) 
            i+=1
       
    def update(self, events): 
        for e in events: 
            if e.type == pygame.KEYDOWN: 
                if e.key == pygame.K_DOWN: 
                    self.option += 1
                if e.key == pygame.K_UP: 
                    self.option -= 1
                if e.key == pygame.K_RETURN: 
                    if self.options[self.option][0]=="Exit": exit()
                    try:
                        self.options[self.option][1]() 
                    except:
                        pass
        if self.option > len(self.options)-1: 
            self.option = 0
        if self.option < 0: 
            self.option = len(self.options)-1
  
    def set_pos(self, x, y, dh=0): 
        self.x = x 
        self.y = y 
        self.line_height+=dh
   
    def set_font(self, font): 
        self.font = font 
        self.line_height=self.font.get_height() 
        self.height = len(self.options)*self.line_height
        
    def set_highlight_color(self, color): 
        self.hcolor = color 
        
    def set_normal_color(self, color):  
        self.color = color    
 
screen_mode=[HWSURFACE | FULLSCREEN | DOUBLEBUF,DOUBLEBUF]
screen_mode_num=1
planet_h=[]
planet_h.append([(100.,350.),50.])
planet_h.append([(900.,350.),50.])
pygame.mixer.pre_init(44100, -16, 2, 4096)
pygame.init()
my_font = pygame.font.Font("font/Amputa2.ttf", 24)
l_font = pygame.font.Font("font/Amputa2.ttf", 48)
xl_font = pygame.font.Font("font/Chalkduster.ttf", 64)
pause_screen=l_font.render("PAUSE", True, (20,20,20))
pause_screen_ins=my_font.render("Press P to continue", True, (20,20,20))
screen = pygame.display.set_mode((1024, 768), screen_mode[screen_mode_num], 32)
background = pygame.image.load('image/space.jpg').convert()
status = pygame.image.load('image/board.png').convert_alpha()

def inMenu():
    global exitMenu
    global isIns
    global choose
    global screen
    global screen_mode_num
    
    def choosePlay():
        global choose
        choose=1
    
    def singlePlay():
        global exitMenu
        exitMenu=1
    
    def twoPlay():
        global exitMenu
        exitMenu=2
        
    def displayIns():
        global isIns
        isIns=1
        
    pygame.mixer.music.load('sound/menu.ogg') 
    pygame.mixer.music.play(-1)
    exitMenu=0     
    isIns=0
    choose=0
    menuTitle = MenuDisplay( 
        ["Gravity War"]
        ) 
          
    menu = MenuDisplay( 
        ["Play",choosePlay], 
        ["Help",displayIns], 
        ["Exit",exit] 
        ) 
    
    playMenu = MenuDisplay(
        #["Single Player", singlePlay],
        ["Two Players", twoPlay]
        )
  
    menuTitle.set_font(pygame.font.Font("font/Starcraft.ttf", 82)) 
    menuTitle.set_pos(512, 185) 
    menuTitle.set_highlight_color((255, 255, 255)) 
      
    menu.set_font(pygame.font.Font("font/Transformers.ttf", 64)) 
    menu.set_pos(512, 375,25) 
    menu.set_highlight_color((255, 255, 255)) 
    menu.set_normal_color((0, 0, 0))  
      
    playMenu.set_font(pygame.font.Font("font/Transformers.ttf", 64)) 
    playMenu.set_pos(512, 375,25) 
    playMenu.set_highlight_color((255, 255, 255)) 
    playMenu.set_normal_color((0, 0, 0))  
    
    insTitle = MenuDisplay( 
        ["Instruction"]) 
          
    insText = MenuDisplay( 
        ["This is a two player game."],
        ["Each player controls a spaceship."],
        ["Your goal is to destroy your enemy's spaceship using missiles on your ship."],
        ["You two are in a dual with each other in a strange space."],
        ["Gravity here behaves weirdly."],
        ["Planets pull missiles with great force,"],
        ["But your ships won't be affected."],
        ["Every certain amount of time, "],
        ["shields and powerful weapons are randomly scattered on the map."],
        ["Your spaceships have two special abilities:"],
        ["Teleport: White/Black uses key 'M'/'1' to teleport."],
        ["Shield: Each ship begins play with one shield, White/Black uses key 'N'/'2' to trigger it."],
        ["White/Black should use Arrow Keys/WASD to rotate and move your spaceship."],
        ["White/Black uses Spacebar/LeftShift to launch missiles."],
        ["Note that the longer you press the key, the higher speed the missile will be."],
        ["And power of bonus weapons is also dependent on this time."],
        ["While playing, press 'P' to pause the game."], 
        ["Press 'J' to check how many games each player wins."], 
        ["Press 'F' to switch between window and fullscreen mode."], 
        ["You may press ESC at any time to go back to menu."], 
        ) 
  
    insTitle.set_font(pygame.font.Font("font/Amputa2.ttf", 63)) 
    insTitle.set_pos(512, 95) 
    insTitle.set_highlight_color((255, 255, 255)) 
      
    insText.set_font(pygame.font.Font("font/Chalkduster.ttf", 19)) 
    insText.set_pos(512,165,5) 
    insText.set_highlight_color((255, 255, 255)) 
    insText.set_normal_color((0, 0, 0))  
    while not exitMenu:    
        events = pygame.event.get() 
        #Deal with Keys
        for event in events:
            if event.type == QUIT:
                exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if isIns:
                        isIns=0
                    elif choose:
                        choose=0
                    else:
                        exit()
                if event.key == K_f:
                    screen_mode_num=1-screen_mode_num
                    screen = pygame.display.set_mode((1024, 768), screen_mode[screen_mode_num], 32)
        #Draw Background
        screen.blit(background, (0,0))
        if isIns:
            insText.update(events) 
            insText.draw(screen) 
            insTitle.draw(screen) 
        elif choose:
            playMenu.update(events)
            playMenu.draw(screen)
            menuTitle.draw(screen)
        else:
            menu.update(events) 
            menu.draw(screen) 
            menuTitle.draw(screen) 
        pygame.display.flip()
    pygame.mixer.music.load('sound/playing.ogg') 
    pygame.mixer.music.play(-1)
    return exitMenu

playMode=inMenu()

pygame.mixer.set_num_channels(64)
sound_launch_missile= Sound('launch_missile.ogg',0.2)
sound_missile_explode= Sound('missile_explode.wav',0.27)
sound_ship_explode= Sound('ship_explode.ogg',0.6)
back2menu=0
dead=[0,0]

while True:   
    if back2menu:
        dead=[0,0]
        back2menu=0
        playMode=inMenu()     
    isPause=0  
    isStatus=0 
    pauseTime=0
    clock = pygame.time.Clock()
    ship=[]
    enemy=[]
    ship.append(set_ship(0,100.,350.))
    if playMode==2:
        ship.append(set_ship(1,900.,350.))
    else:
        for i in xrange(15):
            enemy.append(set_ship(i,random()*1000+12,random()*744+12))
    planet= generateMap(planet_h,1024,768)
    inst=[]
    time=0.
    back2menu=0
    hit=False
    gameOver=False
    gameStatus=''
    fweapon=None
    fshield=None
    
    while not gameOver:
        #Time 
        time_passed = clock.tick()/1000.
        
        #Deal with Keys
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    back2menu=1
                if event.key == K_j:
                    if isStatus:
                        isStatus=0
                    else:
                        isStatus=-1
                if event.key == K_p and not isStatus:
                    isPause=1-isPause
                if event.key == K_f:
                    screen_mode_num=1-screen_mode_num
                    screen = pygame.display.set_mode((1024, 768), screen_mode[screen_mode_num], 32)
            if not isPause and not isStatus:
                if event.type == KEYUP:
                    if event.key == K_SPACE:
                        ship[0].make_missile()
                    if event.key == K_LSHIFT:
                        ship[1].make_missile()
        #back2menu
        if back2menu:
            break
        
        #If show status
        if isStatus==1:
            continue
        
        #Draw Background
        screen.blit(background, (0,0))
        
        #If pause
        if isPause: 
            screen.blit(pause_screen,(417.5,340))
            screen.blit(pause_screen_ins,(346.5, 402))
            if isStatus==-1:
                status_info=xl_font.render(str(dead[0])+" : "+str(dead[1]), True, (200,200,200))
                screen.blit(status,(256,192))
                screen.blit(status_info,Vector2(512,384)-Vector2(status_info.get_width(),status_info.get_height())/2.)
            pygame.display.flip() 
            continue
        
        #Draw Planet
        for i in planet:
            rc = i[2]
            rp = i[0]
            x,y=rp
            rr = i[1]
            pygame.draw.circle(screen, rc,rp, rr)
            screen.blit(i[3],(x-rr,y-rr))
        pressed_keys = pygame.key.get_pressed()
        
        #Ship motion initialize
        for j in ship: 
            j.direction=0
            j.rotation=0  
        
        #Keys
        keyEvents(pressed_keys)
        
        #Time
        time+=time_passed
        tt=int(time)
        
        #Missile Power
        if pressed_keys[K_SPACE]:
            showMissilePower(0)
        if pressed_keys[K_LSHIFT]:
            showMissilePower(1)
        
        #Weapon Bonus
        if fweapon and fweapon.used:
            fweapon=None
        if tt%20==10 and not fweapon:
            fweapon=generateBonus('weapon',1)
        if fweapon:
            fweapon.update()
            
        #Shield Bonus
        if fshield and fshield.used:
            fshield=None
        if tt%20==15 and not fshield:
            fshield=generateBonus('shield',-1)
        if fshield:
            fshield.update()
        
        #Ship Issue
        for j in ship:
            if j.dead==1:
                gameOver=j.name
                dead[1-j.num]+=1
                ship.remove(j)
                continue
            elif j.dead==0:
                j.update()
            if j.dead==-1:
                j.explode=Explode()
                j.dead=-2
            elif j.dead==-2:
                j.explode.update(j)
                
        if isStatus==-1:
            isStatus=1
            status_info=xl_font.render(str(dead[0])+" : "+str(dead[1]), True, (200,200,200))
            screen.blit(status,(256,192))
            screen.blit(status_info,Vector2(512,384)-Vector2(status_info.get_width(),status_info.get_height())/2.)
                
        #Update display
        pygame.display.flip() 
playMode=inMenu()
