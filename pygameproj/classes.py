import pygame, sys, os
import globals
from settings import *
from pytmx.util_pygame import load_pygame;


class Map():
    def __init__(self, tmxdata):
        self.collidablegroup = pygame.sprite.Group();
        self.noncollidablegroup = pygame.sprite.Group();
        self.decorationgroup = pygame.sprite.Group();
        self.tmxdata = tmxdata;
        # self.fullspritegroup = pygame.sprite.Group();
        self.tilelist = []
    def printallproperties(self):
        print("tilelist", self.tilelist);
        # print("fullspritegroup", self.fullspritegroup);
        print("collidablegroup", self.collidablegroup);
        print("noncollidablegroup", self.noncollidablegroup);
        print("tmxdata", self.tmxdata);

    def clearmap(self):
        for tiles in self.collidablegroup:
            tiles.kill()
        for tiles in self.noncollidablegroup:
            tiles.kill()
        for tiles in self.decorationgroup:
            tiles.kill();
        # for tiles in self.fullspritegroup:
        #     tiles.kill()
        self.collidablegroup.empty()
        self.noncollidablegroup.empty()
        self.decorationgroup.empty();
        # self.fullspritegroup.empty()
        del self.tmxdata
        self.tmxdata = None
        self.tilelist.clear()
        self.tilelist = []
class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, tile_id, collidable):
        super().__init__(groups);
        self.image = surf;
        self.rect = self.image.get_rect(topleft = pos);
        self.tile_id = tile_id;
        self.collidable = collidable;
        self.isinrange = false;
class object(pygame.sprite.Sprite): #basically sprites that are not tiles
    def __init__(self, surface, pos, type, len, height):
        pygame.sprite.Sprite.__init__(self);
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos);
        self.inrange = false;
        self.inxrange = false;
        self.type = type;
        self.length = len;
        self.tall = height;
        self.speed = self.getspeed(type = type);
        self.direction = 0;
    def getspeed(self, type):
        #4-7 is background
        #0-3 is foreground objects
        if type == 0: #immovable
            return 0;
        elif type == 1:
            return 0.03;
        elif type == 2:
            return 0.10;
        elif type == 3:
            return 0.13;

        elif type == 4: #closer background is faster. higher backgroudn type = further
            return 0.28;
        elif type == 5:
            return 0.24;
        elif type == 6:
            return 0.20;
        elif type == 7:
            return 0.16;
        else:
            return 0;
    def delete(self):
        self.kill()
    def scroll(self, speed, direction, typefactor, x):
        x += speed * direction * typefactor; #direction refers to x axis
        return x;
    def update(self, direction, scrollspeed, plrx):
        if self.inrange:
            self.rect.x = self.scroll(speed = scrollspeed, direction = direction, typefactor = self.speed, x = self.rect.x);
        elif self.type != 0:
            # if direction == -1:
            #     self.rect.x = plrx + (screenwidth * direction)/2 - self.length/2;
            #
            # elif direction == 1:
            #     self.rect.x = plrx + (screenwidth * direction / 2);
            self.inxrange = true;
            self.rect.x = self.scroll(speed=scrollspeed, direction=direction, typefactor=self.speed, x=self.rect.x);
class physics():
    def __init__(self, gravity, onground, plrxvel, jumppow):
        self.gravity = gravity;
        self.onground = onground;
        self.plryvelocity = 0;
        self.plrxvelocity = plrxvel;
        self.jumppow = jumppow;
        self.direction = pygame.math.Vector2(1,0);
class projectile(pygame.sprite.Sprite):
    def __init__(self, surface, pos, throwerfacingright, initialxval, type):
        pygame.sprite.Sprite.__init__(self)
        self.initialxvalue = initialxval
        self.isinrange = false;
        self.type = type;
        self.hasphysics = self.checkifhasphysics(type);
        self.positionstate = "justthrown"
        if self.hasphysics:
            self.physics = physics(gravity = 1, onground = false, plrxvel = 30, jumppow = -20);
            self.yvelocity = 0

        self.projectileanimlist = self.initanimlist();
        self.projectileanimidx = 0;
        self.velocityx = 15;
        self.image = surface;
        self.projectilemaxdist = 64 * 18
        self.deletenextframe = false;
        if throwerfacingright:
            self.image = pygame.transform.flip(self.image, true, false)
            self.direction = 1;
            self.rect = self.image.get_rect(topleft=pos);
            self.rect.x += 60
        else:
            self.direction = -1;
            self.rect = self.image.get_rect(topleft=pos);
            self.rect.x -= 10
        self.rect.y += 60
    def checkifhasphysics(self, type):
        if not (type == "rock"):
            return false;
        return true;
    def initanimlist(self):
        animlist = []
        animlist.append(pygame.image.load(cwd + "/tiles/projectiles/" + self.type + "frame1.png"))
        animlist.append(pygame.image.load(cwd + "/tiles/projectiles/" + self.type + "frame2.png"))
        animlist.append(pygame.image.load(cwd + "/tiles/projectiles/" + self.type + "frame3.png"))
        animlist.append(pygame.image.load(cwd + "/tiles/projectiles/" + self.type + "frame4.png"))
        return animlist
    def checkdisttraveled(self, projectilemaxdist, initx, currx):
        if projectilemaxdist > abs(initx - currx):
            return None;
        else:
            self.deletenextframe = true;
            # print(self.traveledmaxdist)
    def update(self):
        self.rect.x += self.direction * self.velocityx;
        if self.hasphysics:
            #applies gravity
            if self.positionstate == "justthrown":
                self.yvelocity = self.physics.jumppow
                self.positionstate = "inair"
            self.yvelocity += self.physics.gravity
            self.rect.y += self.yvelocity;
        self.animate(self.projectileanimlist)
        self.checkdisttraveled(self.projectilemaxdist, self.initialxvalue, self.rect.x)
    def animate(self, animlist):
        idxstep = 0.5;
        if self.projectileanimidx > len(animlist) - idxstep:
            self.projectileanimidx = 0
        self.image = animlist[int(self.projectileanimidx)]
        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, true, false)
        self.projectileanimidx += idxstep
    def printvalues(self):
        print("self.rect.x: ", self.rect.x)
        print("self.rect.y: ", self.rect.y)
        print("self.direction: ", self.direction);
        print("self.velocity: ", self.velocityx)
class Plr(pygame.sprite.Sprite):
    def __init__(self, plrpos, plrsurf):
        pygame.sprite.Sprite.__init__(self);

        #animvars
            #regjump
        self.animatingjump = false
        self.jumpanimreversed = true
        self.plrjumpapex = pygame.image.load(cwd + '/tiles/plrjumpframe5.png')
        self.idleanim = plrsurf
        self.jumpanimlist = self.initjumpanimlist();
            #doublejump(dj)
        self.animatingdj = false;
        self.djanimreversed = false;
        self.djlistidx = 0;
        self.djanimlist = self.initdjanimlist();
            #landing
        self.finishedlandanim = false;
        self.landanimidx = 0;
        self.landanimlist = self.initlandanimlist();
        self.currentspriteidx = 0
            #walking
        self.walkanimlist = self.initwalkanimlist();
        self.walkanimidx = 0;
        self.moving = false;
            #dashing
        self.dashanimlist = self.initdashanimlist();
        self.dashanimidx = 0;
        self.dashfullyreversed = true;
        ###self.ondash is declared under "#dash, movement, camera vars" comment

        #image and physics vars
        self.image = plrsurf;
        self.rect = self.image.get_rect(topleft = plrpos);
        self.onground = false;
        self.onciel = false;
        archetypestats = archetypestatstorage(globals.archetype)
        self.physics = physics(gravity = archetypestats.gravity, onground = false,
                               plrxvel = archetypestats.plrxvel, jumppow = archetypestats.jumppow);
        self.statstorage = archetypestatstorage(globals.archetype)
        self.archetypespeed = self.statstorage.plrxvel;
        del self.statstorage;

        self.facingright = true;

        #jumping vars
        self.jumpcounter = 0;
        self.timelastjump = 0;
        self.belowplatform = false
        self.numjumpsinair = 0

        #dash, movement, camera vars
        self.timelastdashed = 0;
        self.defaultxvelocity = 15
        self.dashfactor = 30
        self.timelastran = 0
        self.ondash = false
        self.adjustcamerayfactor = 0
        self.adjustcameraxfactor = screenwidth / 2

        #cooldowns/lives/oob vars
        self.alreadypressedq = false
        self.alreadypressede = false
        self.isOob = false
        self.lives = archetypestats.lives
    def initjumpanimlist(self):
        thislist = []
        thislist.append(self.idleanim)
        thislist.append(pygame.image.load(cwd + '/tiles/plrjumpframe0.5.png'))
        thislist.append(pygame.image.load(cwd + '/tiles/plrjumpframe1.png'))
        thislist.append(pygame.image.load(cwd + '/tiles/plrjumpframe1.5.png'))
        thislist.append(pygame.image.load(cwd + '/tiles/plrjumpframe2.png'))
        thislist.append(pygame.image.load(cwd + '/tiles/plrjumpframe2.5.png'))
        thislist.append(pygame.image.load(cwd + '/tiles/plrjumpframe3.png'))
        thislist.append(pygame.image.load(cwd + '/tiles/plrjumpframe3.5.png'))
        thislist.append(pygame.image.load(cwd + '/tiles/plrjumpframe4.png'))
        thislist.append(pygame.image.load(cwd + '/tiles/plrjumpframe4.5.png'))
        thislist.append(self.plrjumpapex)
        return thislist
    def initdjanimlist(self):
        thislist = []
        thislist.append(self.plrjumpapex)
        thislist.append(pygame.image.load(cwd + '/tiles/plrdjframe1.png'))
        thislist.append(pygame.image.load(cwd + '/tiles/djframe2.png'))
        thislist.append(pygame.image.load(cwd + '/tiles/djframe3.png'))
        thislist.append(pygame.image.load(cwd + '/tiles/djframe4.png'))
        return thislist
    def initlandanimlist(self):
        thislist = [];
        thislist.append(pygame.image.load(cwd + '/tiles/plrlandframe1.png'))
        thislist.append(pygame.image.load(cwd + '/tiles/plrlandframe2.png'))
        thislist.append(pygame.image.load(cwd + '/tiles/plrlandframe3.png'))
        thislist.append(pygame.image.load(cwd + '/tiles/plrlandframe4.png'))
        thislist.append(pygame.image.load(cwd + '/tiles/plrlandframe5.png'))
        thislist.append(pygame.image.load(cwd + '/tiles/plrlandframe6.png'))
        return thislist;
    def initwalkanimlist(self):
        thislist = []
        thislist.append(pygame.image.load(cwd + '/tiles/walkframe1.png'))
        thislist.append(pygame.image.load(cwd + '/tiles/walkframe1.5.png'))
        thislist.append(pygame.image.load(cwd + '/tiles/walkframe2.png'))
        thislist.append(pygame.image.load(cwd + '/tiles/walkframe2.5.png'))
        thislist.append(pygame.image.load(cwd + '/tiles/walkframe3.png'))
        thislist.append(pygame.image.load(cwd + '/tiles/walkframe3.5.png'))
        thislist.append(pygame.image.load(cwd + '/tiles/walkframe4.png'))
        return thislist
    def initdashanimlist(self):
        thislist = [];
        thislist.append(pygame.image.load(cwd + '/tiles/plrdashframe1.png'));
        thislist.append(pygame.image.load(cwd + '/tiles/plrdashframe2.png'));
        thislist.append(pygame.image.load(cwd + '/tiles/plrdashframe3.png'));
        thislist.append(pygame.image.load(cwd + '/tiles/plrdashframe4.png'));
        thislist.append(pygame.image.load(cwd + '/tiles/plrdashframe5.png'));
        return thislist;
    def update(self, currmap):
        # print(f"{self.physics.plrxvelocity=}")
        if self.onground:
            self.numberjumpsinair = 0;
            if globals.archetype == "glider":
                if not self.ondash:

                    self.physics.plrxvelocity = self.archetypespeed;
        elif globals.archetype == "glider":
            if not self.belowplatform:
                if not self.physics.plrxvelocity >= 40:  # maxgliderspeed

                    self.physics.plrxvelocity += 0.4;
        self.animate()
        self.inputmap()
        self.checkifdashdone(timelastdashed = self.timelastdashed, dashfactor = self.dashfactor) #dashfactor is how much player's x velocity increases on dash
    def animate(self):

        self.animatejump();
        self.animatedj();
        self.animatewalk();
        self.animatedash();
    def animatejump(self):
        justswitched = false
        if self.animatingjump == true:
            # print("animating")
            if self.jumpanimreversed:
                idxstep = 1
                self.currentspriteidx+=idxstep
                self.image = self.jumpanimlist[int(self.currentspriteidx)]
                if self.currentspriteidx >= len(self.jumpanimlist) - idxstep:
                    self.animatingjump = false
                    self.jumpanimreversed = true
                    self.finishedlandanim = false;
                    justswitched = true
                if not self.facingright:
                    self.image = pygame.transform.flip(self.image, true, false)
        else:
            if justswitched:
                return None;
            if self.onground:
                self.currentspriteidx = 0
                self.animatelanding();

            else:
                currentspriteidx = len(self.jumpanimlist) - 1
                self.image = self.jumpanimlist[currentspriteidx]
                self.currentspriteidx = currentspriteidx
                if not self.facingright:
                    self.image = pygame.transform.flip(self.image, true, false)
    def animatelanding(self):
        if self.finishedlandanim:
            return None;
        idxstep = 1;
        self.landanimidx += idxstep;
        self.image = self.landanimlist[int(self.landanimidx)];
        if not self.facingright: #need this line every time i change an image in pygame
            self.image = pygame.transform.flip(self.image, true, false)
        if self.landanimidx >= len(self.landanimlist) - idxstep:
            self.image = self.idleanim;
            self.jumpanimreversed = true;
            if not self.facingright:
                self.image = pygame.transform.flip(self.image, true, false)
            self.finishedlandanim = true
            self.landanimidx = 0
            return None;
    def animatedj(self):
        justswitched = false
        if self.animatingdj:
            if self.djanimreversed:
                idxstep = 1
                self.djlistidx += idxstep
                if self.djlistidx >= len(self.djanimlist) - idxstep:
                    self.animatingdj = false
                    self.djanimreversed = false;
                    justswitched = true;
                self.image = self.djanimlist[int(self.djlistidx)]

                if not self.facingright:
                    self.image = pygame.transform.flip(self.image, true, false)
        else:
            if justswitched:
                return None;
            idxstep = -1
            if self.djlistidx < abs(idxstep):
                self.djanimreversed = true;
                self.djlistidx = 0;
                return None;
            self.djlistidx += idxstep
            self.image = self.djanimlist[int(self.djlistidx)]
            if not self.facingright:
                self.image = pygame.transform.flip(self.image, true, false)
    def animatedash(self):
        if self.ondash:

            idxstep = 1;
            if self.dashanimidx >= len(self.dashanimlist) - idxstep:
                self.dashanimidx -= idxstep;
            self.dashanimidx += idxstep;
            self.image = self.dashanimlist[int(self.dashanimidx)]
            if not self.facingright:
                self.image = pygame.transform.flip(self.image, true, false)
        else:
            if self.dashfullyreversed:
                return None;
            idxstep = 1;
            if self.dashanimidx < idxstep:
                self.dashfullyrversed = true;
                return None;
            elif self.dashanimidx < len(self.dashanimlist) - idxstep:
                self.dashanimidx += idxstep;
            else:
                self.dashanimidx -= idxstep;
            self.image = self.dashanimlist[int(self.dashanimidx)]
            if not self.facingright:
                self.image = pygame.transform.flip(self.image, true, false)
    def animatewalk(self):
        if self.moving:
            if not self.onground:
                return None;
            idxstep = 0.7;
            if self.walkanimidx >= len(self.walkanimlist) - idxstep:
                self.walkanimidx = 0;
            self.walkanimidx += idxstep;
            self.image = self.walkanimlist[int(self.walkanimidx)]
            if not self.facingright:
                self.image = pygame.transform.flip(self.image, true, false)
        else:
            if self.onground:
                if not self.finishedlandanim:
                    return None;

                self.image = self.idleanim
                if not self.facingright:
                    self.image = pygame.transform.flip(self.image, true, false)

#function restores plr to speed after dashed
    def checkifdashdone(self, timelastdashed, dashfactor):
        if not self.ondash:
            return None
        timenow = pygame.time.get_ticks();
        dashfinishcd = 300


        if timenow - timelastdashed >= dashfinishcd:
            # print("dash has finished")
            self.physics.plrxvelocity -= dashfactor
            self.ondash = false

############INPUT MAPPING BEGIN
    def inputmap(self):
        plrvelx = 2;
        jumpheight = 10;
        pausecooldown = 100;
        doublejumpcooldown = 500;
        dashcooldown = 500
        key = pygame.key.get_pressed();
        timenow = pygame.time.get_ticks();
        timelastdashed = self.timelastdashed

        if key[pygame.K_d]:
            self.moving = true;
            if not self.facingright:
                self.image = pygame.transform.flip(self.image, true, false)
                self.facingright = true;
            self.physics.direction.x = 1;
        elif key[pygame.K_a]:
            self.moving = true
            if self.facingright:
                self.image = pygame.transform.flip(self.image, true, false)
                self.facingright = false
            self.physics.direction.x = -1;
        else:
            self.physics.direction.x = 0;
            self.moving = false;
        if key[pygame.K_w]:
            self.jump(cooldown = doublejumpcooldown, timenow = timenow, timelastpressed = self.timelastjump);
            self.onground = false;
            self.belowplatform = false
        if key[pygame.K_s]:
            self.physics.plryvelocity+=1;
            self.physics.direction.y+=1;
        # q and e buttons cause the camera to go down or up
        if key[pygame.K_q]:
            if not self.alreadypressedq:
                self.adjustcamerayfactor -= 4 * 64

            self.alreadypressedq = true

        elif key[pygame.K_e]:
            if not self.alreadypressede:
                self.adjustcamerayfactor += 4 * 64
            self.alreadypressede = true
        else:
            self.alreadypressedq = false
            self.alreadypressede = false
            self.adjustcamerayfactor = 64*5
        if key[pygame.K_SPACE] and timenow - timelastdashed >= dashcooldown:
            #space causes dash
            self.ondash = true
            self.physics.plrxvelocity += self.dashfactor
            self.timelastdashed = timenow
        if key[pygame.K_ESCAPE]:
            pygame.quit();
            sys.exit();
############INPUT MAPPING END

    def applygravity(self):
        self.physics.plryvelocity += self.physics.gravity
        self.physics.direction.y = self.physics.plryvelocity
        self.rect.y += self.physics.plryvelocity
    def jump(self, cooldown, timenow, timelastpressed):
        #jump function assures doublejump capability and platform hanging when below platform block
        if self.onground:
            self.animatingjump = true;
            self.numjumpsinair = 1
            self.physics.plryvelocity = self.physics.jumppow
            self.physics.direction.y = self.physics.jumppow
            self.timelastjump = timenow
            return

        elif self.belowplatform:
            self.physics.plryvelocity = self.physics.jumppow
            self.physics.direction.y = self.physics.jumppow
            self.numjumpsinair = 0
            self.timelastjump = timenow
            return

        elif self.numjumpsinair < 2 and self.onground == false:
            if timenow - timelastpressed >= cooldown:
                self.numjumpsinair+=1
                self.physics.plryvelocity = self.physics.jumppow
                self.physics.direction.y = self.physics.jumppow
                self.animatingdj = true;
    def delete(self):
        self.kill()
class Enemy(pygame.sprite.Sprite):
    def __init__(self, surface, pos, shirtcolor):
        pygame.sprite.Sprite.__init__(self)
        self.image = surface
        self.isinrange = false
        self.shirtcolor = shirtcolor;
        self.gravity = 0.5
        self.direction = pygame.math.Vector2(-1,0);
        self.jumppow = -15
        self.rect = self.image.get_rect(topleft=pos);
        self.onground = false
        self.xvel = 4
        self.lastcoll = 0;
        self.canmove = self.checkifcanmove(shirtcolor)
        self.canjump = self.checkifcanjump(shirtcolor);
        self.hasprojectile = self.checkifhasprojectile(shirtcolor);
        if self.canjump:
            self.jumpanimlist = self.initjumpanimlist(shirtcolor);
            self.jumpanimidx = 0;
            self.animatingjump = false;
            self.landanimidx = 0
            self.landanimlist = self.initlandanimlist(shirtcolor);
            self.landed = false;
        if self.canmove:
            self.walkanimlist = self.initwalkanimlist(shirtcolor);
            self.walkanimidx = 0;
        if self.hasprojectile:
            self.projectilegroup = pygame.sprite.Group(); #list contains all thrown projectiles currently in the scene
            self.timeprojectilelastthrown = 0
            self.projectiletype = self.getprojectiletype(shirtcolor);
            self.imgprojectile = pygame.image.load(cwd + "/tiles/projectiles/" + self.projectiletype + ".png");
        self.haseyes = self.checkifhaseyes(shirtcolor);
        self.facingright = false;
    def animate(self, canjump, canwalk):
        if not (canjump or canwalk):
            return None;
        self.animatejump(canjump);
        self.animatewalk(canwalk);
        self.animateland(canjump);
    def animatejump(self, canjump):
        if not canjump:
            return None;
        if not self.animatingjump:
            return None
        idxstep = 0.5;
        if self.jumpanimidx >= len(self.jumpanimlist) - idxstep:
            self.landed = false;
            self.animatingjump = false;
            self.jumpanimidx = 0;
            return None;
        self.image = self.jumpanimlist[int(self.jumpanimidx)]
        self.jumpanimidx += idxstep
        if self.facingright:
            self.image = pygame.transform.flip(self.image, true, false)
        # print("animating jump")
    def animateland(self, canjump):
        if not canjump: return None;
        if not self.onground: return None;
        if self.landed: return None;
        idxstep = 0.5
        if self.landanimidx >= len(self.landanimlist) - idxstep:
            self.landed = true
            self.landanimidx = 0
            return None;
        self.image = self.landanimlist[int(self.landanimidx)]
        self.landanimidx += idxstep
        if self.facingright:
            self.image = pygame.transform.flip(self.image, true, false)
    def animatewalk(self, canwalk):
        if not (canwalk and self.shirtcolor == "green"):
            return None;
        idxstep = 0.5
        if self.walkanimidx >= len(self.walkanimlist) - idxstep:
            self.walkanimidx = 0
        self.image = self.walkanimlist[int(self.walkanimidx)]
        self.walkanimidx += idxstep;
        if self.facingright:
            self.image = pygame.transform.flip(self.image, true, false)
    def initlandanimlist(self, shirtcolor):
        if not (shirtcolor == "blue" or shirtcolor == "purple"):
            return None;
        landanimlist = []
        landanimlist.append(pygame.image.load(cwd + '/tiles/EnemySprites/' + shirtcolor + 'enemyjumpframe4.png'))
        landanimlist.append(pygame.image.load(cwd + '/tiles/EnemySprites/' + shirtcolor + 'enemyjumpframe3.png'))
        landanimlist.append(pygame.image.load(cwd + '/tiles/EnemySprites/' + shirtcolor + 'enemyjumpframe2.png'))
        landanimlist.append(pygame.image.load(cwd + '/tiles/EnemySprites/' + shirtcolor + 'enemyjumpframe1.png'))
        landanimlist.append(pygame.image.load(cwd + '/tiles/EnemySprites/idle' + shirtcolor + 'enemy.png'))

        return landanimlist;
    def initwalkanimlist(self, shirtcolor):
        if not shirtcolor == "green":
            return None;
        walkanimlist =[]
        walkanimlist.append(pygame.image.load(cwd + '/tiles/EnemySprites/' + shirtcolor + 'enemywalkframe1.png'))
        walkanimlist.append(pygame.image.load(cwd + '/tiles/EnemySprites/' + shirtcolor + 'enemywalkframe2.png'))
        walkanimlist.append(pygame.image.load(cwd + '/tiles/EnemySprites/' + shirtcolor + 'enemywalkframe3.png'))
        walkanimlist.append(pygame.image.load(cwd + '/tiles/EnemySprites/' + shirtcolor + 'enemywalkframe4.png'))
        walkanimlist.append(pygame.image.load(cwd + '/tiles/EnemySprites/' + shirtcolor + 'enemywalkframe5.png'))
        return walkanimlist;
    def initjumpanimlist(self, shirtcolor):
        if shirtcolor == "blue" or shirtcolor == "purple":
            jumpanimlist = []
            jumpanimlist.append(pygame.image.load(cwd + '/tiles/EnemySprites/' + shirtcolor + 'enemyjumpframe1.png'))
            jumpanimlist.append(pygame.image.load(cwd + '/tiles/EnemySprites/' + shirtcolor + 'enemyjumpframe2.png'))
            jumpanimlist.append(pygame.image.load(cwd + '/tiles/EnemySprites/' + shirtcolor + 'enemyjumpframe3.png'))
            jumpanimlist.append(pygame.image.load(cwd + '/tiles/EnemySprites/' + shirtcolor + 'enemyjumpframe4.png'))
            jumpanimlist.append(pygame.image.load(cwd + '/tiles/EnemySprites/' + shirtcolor + 'enemyjumpapex.png'))
        return jumpanimlist

    #boolcheckers below
    def checkifcanjump(self, shirtcolor):
        if not (shirtcolor == "blue" or shirtcolor == "purple"):
            return false;
        return true;
    def checkifcanmove(self, shirtcolor):
        if not (shirtcolor == "green" or shirtcolor == "purple"):
            return false;
        return true;
    def checkifhaseyes(self, shirtcolor):
        if not (shirtcolor == "green" or shirtcolor == "black" or shirtcolor == "gray"):
            return false;
        return true;
    def checkifhasprojectile(self, shirtcolor):
        if not (shirtcolor == "black" or shirtcolor == "gray"):
            return false;

        return true;

    #projectile stuff
    def updateprojectiles(self):
        for projectile in self.projectilegroup:
            projectile.update()
            if projectile.deletenextframe:
                projectile.kill()
        timenow = pygame.time.get_ticks();
        projectilethrowcd = 1000 #milliseconds
        if timenow - self.timeprojectilelastthrown < projectilethrowcd:
            return None;
        if self.isinrange:
            self.throwprojectile(timenow);
    def throwprojectile(self, timenow):
        self.projectilegroup.add(projectile(surface = self.imgprojectile, pos = (self.rect.x, self.rect.y), throwerfacingright = self.facingright, initialxval = self.rect.x, type = self.projectiletype));
        self.timeprojectilelastthrown = timenow;
    def getprojectiletype(self, shirtcolor):
        if shirtcolor == "black":
            return "shuriken"
        elif shirtcolor == "gray":
            return "rock"
    def applygravity(self):
        self.direction.y += self.gravity;
        self.rect.y += self.direction.y;
    def jump(self):
        if self.onground and self.canjump and self.landed:
            self.direction.y = self.jumppow
            self.onground = false
            self.animatingjump = true;
    def moveforward(self):
        if not self.canmove:
            return None;
        self.rect.x += self.direction.x * self.xvel
    def delete(self):
        self.kill()
    def update(self):
        if self.isinrange:
            self.jump();
            self.animate(self.canjump, self.canmove);
        if self.hasprojectile:
            self.updateprojectiles();
class enemyimages():
    black = pygame.image.load(cwd + '/tiles/EnemySprites/idleblackenemy.png')
    gray = pygame.image.load(cwd + '/tiles/EnemySprites/idlegrayenemy.png')
    blue = pygame.image.load(cwd + '/tiles/EnemySprites/idleblueenemy.png')
    red = pygame.image.load(cwd + '/tiles/EnemySprites/idleredenemy.png')
    green = pygame.image.load(cwd + '/tiles/EnemySprites/idlegreenenemy.png')
    purple = pygame.image.load(cwd + '/tiles/EnemySprites/idlepurpleenemy.png')
class Level:
    def __init__(self, currentmap, plr):
        self.lastframeplrxpos = 0
        self.levelcurrentlychanging = false
        self.currentmap = self.inittiles(currentmap);
        self.playeronground = false;
        self.player = plr;
        self.current_x = 0
        self.imgenemy = enemyimages()
        self.enemies = pygame.sprite.Group()
        self.door = 0
        self.oobpos = pygame.math.Vector2(0,0)
        self.background = [];
        for x in range(globals.numbackgrounds + 1):
            self.background.append(pygame.sprite.Group());
        self.setobjects(currentmap)
        self.timeplrlastcollidedwithenemy = 0
        self.nontiledobjects = self.groupnontiledobjects() #enemy is not included in this spritegroup
        self.doorcollisionoccured = false
        self.checkedenemieswitheyes = false;
        self.hasenemieswitheyes = false;

#setobject sets stuff on objectlayer in tiled
    def setobjects(self, mapinst):
        door = 0
        objlayer = mapinst.tmxdata.get_layer_by_name("Object Layer 1");
        imgenemy = self.imgenemy

        for obj in objlayer:
            props = obj.properties
            name = props["name"]
            # print(dir(obj))
            obj.apply_transformations()
            # print(props)
            if name == "door":
                self.door = object(surface = obj.image, pos = (obj.x, obj.y), type = props["backgroundtype"], len = obj.width, height = obj.height);
            elif name == "BlueEnemySpawner":
                enemyimage = imgenemy.blue
                enemyshirtcolor = "blue"
                thisenemy = Enemy(surface=enemyimage, pos=(obj.x, obj.y), shirtcolor=enemyshirtcolor);
                self.enemies.add(thisenemy)
            elif name == "RedEnemySpawner":
                enemyimage = imgenemy.red
                enemyshirtcolor = "red"
                thisenemy = Enemy(surface=enemyimage, pos=(obj.x, obj.y), shirtcolor=enemyshirtcolor);
                self.enemies.add(thisenemy)
            elif name == "GreenEnemySpawner":
                enemyimage = imgenemy.green
                enemyshirtcolor = "green"
                thisenemy = Enemy(surface=enemyimage, pos=(obj.x, obj.y), shirtcolor=enemyshirtcolor);
                self.enemies.add(thisenemy)
            elif name == "PurpleEnemySpawner":
                enemyimage = imgenemy.purple
                enemyshirtcolor = "purple"
                thisenemy = Enemy(surface=enemyimage, pos=(obj.x, obj.y), shirtcolor=enemyshirtcolor);
                self.enemies.add(thisenemy)
            elif name == "BlackEnemySpawner":
                enemyimage = imgenemy.black
                enemyshirtcolor = "black"
                thisenemy = Enemy(surface=enemyimage, pos=(obj.x, obj.y), shirtcolor=enemyshirtcolor);
                self.enemies.add(thisenemy)
            elif name == "GrayEnemySpawner":
                enemyimage = imgenemy.gray
                enemyshirtcolor = "gray"
                thisenemy = Enemy(surface=enemyimage, pos=(obj.x, obj.y), shirtcolor=enemyshirtcolor);
                self.enemies.add(thisenemy)
            elif name == "plrspawn":
                self.player.rect.x = obj.x
                self.player.rect.y = obj.y
            elif name == "OutOfBounds":
                self.oobpos.x = obj.x
                self.oobpos.y = obj.y
            elif name == "background":
                typebackground = props["backgroundtype"] #needed for multi layer parallax view
                objref = object(surface = obj.image, pos = (obj.x, obj.y),  type = typebackground, len = obj.width, height = obj.height);
                # print(dir(obj))
                self.background[globals.numbackgrounds - typebackground].add(objref); #reason i created a background list was to allow for priority rendering
            else:
                print("error occured while looping through object layer")

#besides backgrounds...:
    def groupnontiledobjects(self):
        #this function makes sure everything was in a spritegroup so that all sprites in a level could be deleted and changed properly
        nontiledobjectsgroup = pygame.sprite.Group()
        nontiledobjectsgroup.add(self.player)
        nontiledobjectsgroup.add(self.door)


        return nontiledobjectsgroup;

#func below inits tiles and enemies
    def inittiles(self, mapinst):
        # mapinst.fullspritegroup.empty();
        mapinst.collidablegroup.empty();
        mapinst.noncollidablegroup.empty();
        instmap = mapinst;
        layerindex = -1;
        groupc = [];
        groupn = [];
        groupd = [];
        enemylist = [];
        collidablegroup = mapinst.collidablegroup;
        noncollidablegroup = mapinst.noncollidablegroup;
        decorationgroup = mapinst.decorationgroup;
        visiblelayers = mapinst.tmxdata.visible_layers;
        for layer in visiblelayers:
            # print("hasattr(layer, 'data'", hasattr(layer, "data"))
            if not hasattr(layer, "data"):
                continue;

            layerindex+=1;
            # print("layer.name: ", layer.name);
            # print("layerindex: ", layerindex);

            for x,y,surf in layer.tiles():
                pos = (64*x, 64*y);
                props = mapinst.tmxdata.get_tile_properties(x, y, layerindex);
                tile_id = props["id"];
                tilecollidable = props["collidable"];
                tilename = props["name"];
                spritegroup = 0;
                if tilecollidable:
                    spritegroup = collidablegroup;
                else:
                    if tilename == "dec":
                        spritegroup = decorationgroup;
                    else:
                        spritegroup = noncollidablegroup;


                # print("props: ", props);
                # print("props(""id""): ", props["id"])
                # print("collidable?: ", collidable)
                tile_info = {
                    "pos": pos,
                    "surf": surf,
                    "groups": spritegroup,
                    "tile_id": tile_id,
                    "collidable": tilecollidable
                }
                tileinstance = Tile(**tile_info);
                if tilecollidable:
                    groupc.append(tileinstance);
                else:
                    if tilename == "dec":
                        groupd.append(tileinstance);
                    else:
                        groupn.append(tileinstance);

                instmap.tilelist.append(tileinstance);


        instmap.noncollidablegroup.add(groupn);
        instmap.collidablegroup.add(groupc);
        instmap.decorationgroup.add(groupd)
        # instmap.fullspritegroup.add(groupn);
        # instmap.fullspritegroup.add(groupc);
        return instmap;

#detect movement, wall, ground, and door collision for players and enemies
    def horizontalmovecoll(self):
        player = self.player
        player.rect.x += player.physics.direction.x * player.physics.plrxvelocity

        for sprite in self.currentmap.collidablegroup.sprites():
            if not sprite.isinrange:
                continue
            if sprite.rect.colliderect(player.rect):
                plrphysdirx = player.physics.direction.x
                if plrphysdirx < 0:
                    player.rect.left = sprite.rect.right
                elif plrphysdirx > 0:
                    player.rect.right = sprite.rect.left
    def vertmovecoll(self):
        player = self.player;
        player.applygravity()
        acollisionoccured = false;
        for sprite in self.currentmap.collidablegroup.sprites():
            if not sprite.isinrange: continue;
            if sprite.rect.colliderect(player.rect):
                acollisionoccured = true;
                if -player.physics.plryvelocity < 0:
                    self.player.onground = true
                    player.rect.bottom = sprite.rect.top
                    player.physics.plryvelocity = 0;
                elif -player.physics.plryvelocity > 0:
                    self.player.belowplatform = true
                    player.rect.top = sprite.rect.bottom
                    player.physics.plryvelocity = 0;
        # THE REASON WHY I USE -player.physics.direction.y INSTEAD OF player.physics.direction.y
        #in pygame, the Y-axis is oriented from top to bottom,
        # so positive values in the Y-direction mean moving
        # down on the screen, while negative values mean moving up.
    def checkplrenemycoll(self):
        timenow = pygame.time.get_ticks();
        player = self.player;
        cooldown = 3000; #planning to make invincibility 3 seconds
        enemygroup = self.enemies.sprites();
        for enemy in enemygroup:
            if enemy.rect.colliderect(player.rect) and timenow - self.timeplrlastcollidedwithenemy >= cooldown:
                self.player.lives -= 1;
                self.timeplrlastcollidedwithenemy = timenow;
            if not enemy.hasprojectile:
                continue;
            for projectile in enemy.projectilegroup:
                if not projectile.rect.colliderect(player.rect):
                    continue;
                if timenow - self.timeplrlastcollidedwithenemy >= cooldown:
                    self.player.lives -= 1;
                    self.timeplrlastcollidedwithenemy = timenow;
                projectile.deletenextframe = true
    def enemygroundcoll(self):
        for enemy in self.enemies.sprites():
            if not enemy.isinrange:
                continue;
            enemy.applygravity()
            diry = enemy.direction.y
            dirx = enemy.direction.x
            for sprite in self.currentmap.collidablegroup.sprites():
                if not sprite.isinrange: continue;
                if enemy.rect.colliderect(sprite.rect):
                    if -diry < 0:
                        enemy.rect.bottom = sprite.rect.top
                        enemy.direction.y = 0
                        enemy.onground = True
                    elif -diry > 0:
                        enemy.rect.top = sprite.rect.bottom
                        enemy.direction.y = 0
    def enemywallcoll(self):
        for enemy in self.enemies.sprites():
            if not enemy.canmove:
                continue;
            if not enemy.isinrange:
                continue

            dirx = enemy.direction.x;
            enemy.moveforward();
            collidedwithrect = false;
            for sprite in self.currentmap.collidablegroup.sprites():
                if not sprite.isinrange: continue;
                if enemy.rect.colliderect(sprite.rect):
                    collidedwithrect = true;
                    if dirx < 0:
                        enemy.rect.left = sprite.rect.right;
                        enemy.direction.x = -enemy.direction.x;
                        enemy.image = pygame.transform.flip(enemy.image, true, false)
                        enemy.facingright = not enemy.facingright;
                    elif dirx > 0:
                        enemy.rect.right = sprite.rect.left;
                        enemy.direction.x = -enemy.direction.x;
                        enemy.image = pygame.transform.flip(enemy.image, true, false)
                        enemy.facingright = not enemy.facingright;
    def enemyhaseyes(self):
        if not (self.hasenemieswitheyes or not self.checkedenemieswitheyes):
            return None; #this if statement is just to save the potential amount of times looping
        for enemy in self.enemies:
            if not enemy.haseyes:
                continue;
            self.hasenemieswitheyes = true;
            if self.player.rect.x > enemy.rect.x and not enemy.facingright:
                enemy.image = pygame.transform.flip(enemy.image, true, false);
                enemy.facingright = not enemy.facingright;
                enemy.direction.x = 1;
            elif self.player.rect.x < enemy.rect.x and enemy.facingright:
                enemy.image = pygame.transform.flip(enemy.image, true, false);
                enemy.facingright = not enemy.facingright;
                enemy.direction.x = -1
    def updateenemies(self):
        for enemy in self.enemies:
            enemy.update()
    def checkdoorplrcoll(self):
        plr = self.player
        door = self.door
        alreadycollided = self.doorcollisionoccured
        if plr.rect.colliderect(door) and not alreadycollided:
            self.doorcollisionoccured = true
            # print("plr has collided with door")
            # globals.levelhandler.changeleveltonext()

#oob logic
    def checkifplroob(self):
        if self.player.rect.y >= self.oobpos.y:
            self.player.lives -= 1
            # print("player is out of bounds, has lost one life. player.lives is now ", self.player.lives)
            self.player.isOob = true

#run function is what the level should check/do every frame while running
    def run(self):
        #PLAYER
        self.player.update(self.currentmap)
        self.horizontalmovecoll()
        self.vertmovecoll()
        self.checkplrenemycoll()
        self.checkdoorplrcoll()
        self.checkifplroob()
        #Enemy
        self.updateenemies()
        self.enemygroundcoll()
        self.enemywallcoll()
        self.enemyhaseyes();
        plrxpos = self.player.rect.x;
        #background
        if self.player.moving:
            if plrxpos == self.lastframeplrxpos:
                return;
            for layers in self.background:
                for images in layers:
                    images.update(direction = self.player.physics.direction.x, scrollspeed = self.player.physics.plrxvelocity, plrx = plrxpos);
        self.lastframeplrxpos = plrxpos

    def deletelevel(self):
        self.levelcurrentlychanging = true
        self.currentmap.clearmap()
        for objects in self.nontiledobjects.sprites():
            objects.delete();
        for layers in self.background:
            layers.empty();


        self.nontiledobjects.empty();
        for enemy in self.enemies.sprites():
            enemy.delete();
        self.enemies.empty();
class levelhandler:
    def __init__(self):
        self.levelnum = globals.savedlevelnum
        self.worldnum = globals.savedworldnum
        self.levelcomplete = false;
        self.timelastrestarted = 0;
        self.tmxdata = 0
        self.nextmap = 0
        self.deletedlevel = false;
        self.levels = [
            cwd + "/Maps/testmap/level1.tmx",
            cwd + "/Maps/testmap/level2.tmx",
            cwd + "/Maps/testmap/level3.tmx",
            cwd + '/Maps/testmap/level4.tmx',
        ]
        self.maxlevelnum = len(self.levels)
        self.currentlevel = self.initlevel(levelnum = self.levelnum)
        self.plrlives = self.currentlevel.player.lives #need to add gui element to plr lives
        self.heartsymbol = pygame.image.load(cwd + '/tiles/heartsymbol.png')
    def initlevel(self, levelnum):
        tmxdata = load_pygame(self.levels[self.levelnum]);
        map = Map(tmxdata = tmxdata);
        plr = Plr(plrpos=(0,0), plrsurf=pygame.image.load(plrspriteloc));
        level = Level(currentmap = map, plr = plr);
        return level;
#returns the next level
    def changeleveltonext(self):
        if not self.deletedlevel:
            self.currentlevel.deletelevel()
        self.deletedlevel = false;
        self.currentlevel = self.initlevel(levelnum = self.levelnum);
        # print("level has been changed!")
    def deletelevel(self):
        self.plrlives = self.currentlevel.player.lives;
        self.currentlevel.deletelevel();
        del self.currentlevel;
        self.currentlevel = 0;
        self.deletedlevel = true;
    def checkrestartlevel(self, plrisoob):
        key = pygame.key.get_pressed()
        if plrisoob or (key[pygame.K_r]):
            cd = 1000;
            if pygame.time.get_ticks() - self.timelastrestarted >= cd:
                self.restartlevel();
                self.timelastrestarted = pygame.time.get_ticks();
        # self.plrlives = self.currentlevel.player.lives
        # self.currentlevel.deletelevel()
        # del self.currentlevel
        # levelnum = self.levelnum
        # plrx = 18;
        # plry = 3;
        # plr = Plr(plrpos=(plrx * 64, plry * 64), plrsurf=pygame.image.load(plrspriteloc))
        # plr.lives = self.plrlives
        # self.tmxdata = load_pygame(self.levels[levelnum])
        # tmxdata = self.tmxdata
        # map = Map(tmxdata=tmxdata)
        # self.currentlevel = Level(currentmap=map, plr=plr)
    def restartlevel(self):
        self.plrlives = self.currentlevel.player.lives
        self.currentlevel.deletelevel()
        del self.currentlevel
        self.currentlevel = self.initlevel(self.levelnum);
    def checkifgameover(self, plrlives):
        if not plrlives <= 0:
            return None

        print("game over, you have lost all your lives. Exiting the application...")
        pygame.quit()
        sys.exit()
    def checklevelcomplete(self, level):
        if self.currentlevel.doorcollisionoccured:
            self.levelcomplete = true;
            self.levelnum += 1;

#levelhandler update function and render function just puts everything on the screen
    def render(self, thislevel, screen, adjustcamerayfactor, adjcamx):
        collgroup = thislevel.currentmap.collidablegroup;
        noncollgroup = thislevel.currentmap.noncollidablegroup;
        enemygroup = thislevel.enemies;
        otherobjgroup = thislevel.nontiledobjects;
        backgroundlist = thislevel.background;
        decgroup = thislevel.currentmap.decorationgroup;
        plr = thislevel.player;
        plrx = plr.rect.x;
        plry = plr.rect.y;
        door = thislevel.door;
        extrarendering = 64 * 6;
        viewleft = plrx - screenwidth / 2 - extrarendering;
        viewright = plrx + screenwidth / 2 + extrarendering;
        viewup = plry - screenheight / 2 - extrarendering;
        viewdown = plry + screenheight / 2 + extrarendering;
        for sprite in noncollgroup:
            spritex = sprite.rect.x;
            spritey = sprite.rect.y;
            if viewleft <= spritex <= viewright and viewup <= spritey <= viewdown:
                screen.blit(sprite.image, (spritex + adjcamx, spritey + adjustcamerayfactor));
        for layer in backgroundlist:
            for sprite in layer:
                x = sprite.rect.x;
                y = sprite.rect.y;
                w = sprite.length;
                h = sprite.tall;
                if viewleft - w <= x <= viewright + w:
                    sprite.inxrange = true;
                    if viewup - h <= y <= viewdown + h :
                        sprite.inrange = true;
                        screen.blit(sprite.image, (x + adjcamx, y + adjustcamerayfactor));
                    else:
                        sprite.inrange = false;
                else:
                    sprite.inrange = false;
                    sprite.inxrange = false;
        for sprite in decgroup:
            spritex = sprite.rect.x;
            spritey = sprite.rect.y;
            if viewleft <= spritex <= viewright and viewup <= spritey <= viewdown:
                screen.blit(sprite.image, (spritex + adjcamx, spritey + adjustcamerayfactor))

        for sprite in collgroup:
            spritex = sprite.rect.x;
            spritey = sprite.rect.y;
            if viewleft <= spritex <= viewright and viewup <= spritey <= viewdown:
                sprite.isinrange = true; #matters for performance
                screen.blit(sprite.image, (sprite.rect.x + adjcamx, sprite.rect.y + adjustcamerayfactor));
            else:
                sprite.isinrange = false;

        for enemy in enemygroup:
            enemyx = enemy.rect.x;
            enemyy = enemy.rect.y;
            if viewleft <= enemyx <= viewright and viewup <= enemyy <= viewdown:
                enemy.isinrange = true;
                screen.blit(enemy.image, (enemy.rect.x + adjcamx, enemy.rect.y + adjustcamerayfactor));
            else:
                enemy.isinrange = false
            if not enemy.hasprojectile: continue;
            if len(enemy.projectilegroup) != 0:
                for thisprojectile in enemy.projectilegroup:
                    # thisprojectile.printvalues();
                    projectilex = thisprojectile.rect.x;
                    projectiley = thisprojectile.rect.y;
                    if viewleft <= projectilex <= viewright and viewup <= projectiley <= viewdown:
                        thisprojectile.isinrange = true;
                        screen.blit(thisprojectile.image, (thisprojectile.rect.x + adjcamx, thisprojectile.rect.y + adjustcamerayfactor))
                    else:
                        thisprojectile.isinrange = false;

        for obj in otherobjgroup:
            objx = obj.rect.x;
            objy = obj.rect.y;
            if viewleft <= objx <= viewright and viewup <= objy <= viewdown:  # pygame has upward as negative so the inequality is up <= y <= down instead of down <= y <= up
                screen.blit(obj.image, (objx + adjcamx, obj.rect.y + adjustcamerayfactor))
        if not self.levelcomplete:
            # fontstring = "Helvetica"
            fontstring = "Times New Roman"
            fontsize = 64
            #displays lives
            livesfont = pygame.font.SysFont(fontstring, fontsize)
            newlivesfont = pygame.font.SysFont(fontstring, fontsize + 3)
            # print(pygame.font.get_fonts())
            livesimg = livesfont.render(str(plr.lives), 1, (0,0,0))
            livesbckgrnd = newlivesfont.render(str(plr.lives), 1, (230,230,230))
            screen.blit(self.heartsymbol, (0, 0))
            screen.blit(livesbckgrnd, (64, 3))
            screen.blit(livesimg, (64, 3))
    def update(self):
        screen = globals.screen
        adjustcamerayfactor = -(self.currentlevel.player.rect.y - self.currentlevel.player.adjustcamerayfactor);
        adjustcameraxfactor = -(self.currentlevel.player.rect.x - self.currentlevel.player.adjustcameraxfactor);
        self.currentlevel.run();
        screen.fill((0, 0, 0));
        thislevel = self.currentlevel;
        self.render(thislevel = thislevel, screen = screen, adjustcamerayfactor = adjustcamerayfactor, adjcamx = adjustcameraxfactor);
        self.checkrestartlevel(self.currentlevel.player.isOob);
        self.checkifgameover(self.currentlevel.player.lives);
        self.checklevelcomplete(self.currentlevel);
class dialoguebox:
    def __init__(self, type):
        self.type = type;
        self.width = 900;
        self.height = 200;
        yfactor = -200
        self.x = (screenwidth - self.width) // 2;
        self.y = (screenheight - self.height) // 2 - yfactor;
        if type == "outside":
            self.width = 420;
            self.height = 220;
class dialoguescene:
    def __init__(self, background, dialogueloc): #backgroundlocation, dialoguelocation):
        self.finishedline = false;
        self.state = "typing"
        # print("Dialogue scene being initialized....")
        self.background = pygame.image.load(background); #background represents a path to the image
        self.currenttext = "";
        self.currenttextlist = [];
        textfontstring = "Times New Roman"
        textfontsize = 32
        self.textfont = pygame.font.SysFont(textfontstring, textfontsize)
        self.innerbox = dialoguebox(type == "inside");
        self.outerbox = dialoguebox(type == "outside");
        self.fulltext = self.getfulltext(dialogueloc);
        self.fulltextidx = 0;
        self.currentline = self.fulltext[self.fulltextidx];
        self.maxfulltextidx = len(self.fulltext) - 1;
        self.charscrollingidx = 0;
        self.signalcontinue = false;
        self.rcooldown = 250  # milliseconds
        self.timelastpressedr = 0;
    def getfulltext(self, dialogueloc):
        # dialoguedir = cwd + '\dialogue\world1\dialoguetest.txt';
        fulltext = [];
        file = open(dialogueloc);
        for line in file:
            fulltext.append(line)
            # print(line)
        # print(fulltext)
        return fulltext;
    def update(self):
        # print("self.currentextlist: ", self.currenttextlist)
        if self.state == "done":
            if self.signalcontinue:
                # print("done!")
                return None;
        timenow = pygame.time.get_ticks()
        key = pygame.key.get_pressed();
        if key[pygame.K_x] and (self.rcooldown < timenow - self.timelastpressedr):
            self.timelastpressedr = timenow
            # print("self.state: ", self.state)
            # print("self.maxfulltextidx: ", self.maxfulltextidx)
            # print("self.fulltextidx: ", self.fulltextidx)
            if self.state == "typing":
                if self.finishedline:
                    self.signalcontinue = true;
                self.charscrollingidx = len(self.currentline) - 1;
                self.currenttextlist = self.scrolllist(self.currentline, self.currenttextlist);
                return None;
            else:
                self.signalcontinue = true;
                return None;
        elif key[pygame.K_g] and (self.rcooldown < timenow - self.timelastpressedr):
            self.state = "done"
            self.signalcontinue = true
            return None
        textfont = self.textfont;
        self.currenttext = self.scroll(self.currentline)
        self.currenttextlist = self.scrolllist(self.currentline, self.currenttextlist)
        # print("self.currenttext: ", self.currenttext);
        # print("self.currentline: ",self.currentline)
        # screen.blit(textrimg, )
        screen = globals.screen
        dialoguefontstring = "Times New Roman"
        dialoguefontsize = 64
        dialoguefont = pygame.font.SysFont(dialoguefontstring, dialoguefontsize)
        dialogueimg = dialoguefont.render("Dialogue Scene", 1, (50,50,50));
        # print(pygame.font.get_fonts())
        screen.fill((200, 200, 200));
        screen.blit(self.background, (0,0))
        screen.blit(dialogueimg, (64, 3))
        # textimg = textfont.render(self.currenttext, 1, (50,50,50));
        pygame.draw.rect(screen, (200,200,200), (self.outerbox.x,
                                            self.outerbox.y,
                                            self.outerbox.width,
                                            self.outerbox.height))

        pygame.draw.rect(screen, (100,100,100), (self.innerbox.x,
                                            self.innerbox.y,
                                            self.innerbox.width,
                                            self.innerbox.height))
        # screen.blit(textimg, (self.innerbox.x, self.innerbox.y))
        yfactor = 0;
        for element in self.currenttextlist:
            textimg = textfont.render(element, 1, (50, 50, 50));
            screen.blit(textimg, (self.innerbox.x, self.innerbox.y - yfactor))
            yfactor -= 30
        continueimg = textfont.render("press X to continue       press G to exit dialogue", 1, (50,50,50))
        screen.blit(continueimg, (self.innerbox.x, self.innerbox.y - 50))
        self.currentline = self.checklinestatus(currenttext=self.currenttext, currentline = self.currentline, idxcurrentline=self.fulltextidx, maxidx=self.maxfulltextidx, signalcontinue=self.signalcontinue);
    def checklinestatus(self, currenttext, currentline, idxcurrentline, maxidx, signalcontinue):
        # print('Current line idx: ', idxcurrentline)
        if currenttext != currentline:
            self.finishedline = false
            return currentline;
        elif idxcurrentline == maxidx:
            self.finishedline = true;
            self.state = "done";
            return currentline;
        else:
            self.finishedline = true;
            # print("equality!")
            if not signalcontinue:
                return currentline;
            self.signalcontinue = false;
            self.fulltextidx+= 1;
            currentline = self.fulltext[self.fulltextidx];
            self.charscrollingidx = 0;
            return currentline;
    def scroll(self, fulltext):
        currlen = len(fulltext);
        if self.charscrollingidx >= currlen:
            self.textdone = true;
            return fulltext;
        idxstep = 2; #character scrolling speed
        self.charscrollingidx+=idxstep;
        newtext = fulltext[0:int(self.charscrollingidx)]
        return newtext;
    def scrolllist(self, fulltext, currenttextlist):
        currlen = len(fulltext);
        if self.charscrollingidx > currlen:
            self.textdone = true;
            return currenttextlist;
        idxstep = 1.5; #character scrolling speed
        self.charscrollingidx+=idxstep;
        newtext = fulltext[0:int(self.charscrollingidx)]
        maxlinelen = 72;
        currentlinelist = [];
        writingfactor = 0;
        newstring = "";
        for character in newtext:
            newstring += character;
            if len(newstring) - writingfactor >= maxlinelen:
                currentlinelist.append(newstring)
                newstring = ""
                writingfactor *= 2;
        if newstring != "":

            currentlinelist.append(newstring);
        # print("currentlinelist: ", currentlinelist)
        # print("currentline: ", fulltext);
        return currentlinelist
    def delete(self):
        del self.background
        self.background = 0;
        del self.innerbox
        self.innerbox = 0;
        del self.outerbox
        self.outerbox = 0;
class dialoguehandler:
    def __init__(self):
        self.dialoguedir = cwd + "/dialogue";
        self.worldnum = 0;
        self.dialoguedone = false;
        # background = pygame.image.load(self.dialoguedir + '/world1/backgrounds/background0.png')
        self.dialoguescenenum = 0;
        self.innerbox = dialoguebox(type == "inside");
        self.outerbox = dialoguebox(type == "outside");
        self.backgrounds = [
            self.dialoguedir + '/world1/backgrounds/background0.png',
            self.dialoguedir + '/world1/backgrounds/background0.png',
            self.dialoguedir + '/world1/backgrounds/background0.png',
            self.dialoguedir + '/world1/backgrounds/background0.png',
            self.dialoguedir + '/world1/backgrounds/background0.png',
        ]
        self.dialoguelocations = [
            cwd + '\dialogue\world1\dialogue1.txt',
            cwd + '\dialogue\world1\dialogue2.txt',
            cwd + '\dialogue\world1\dialogue3.txt',
            cwd + '\dialogue\world1\dialogue4.txt',
            cwd + '\dialogue\world1\dialogue5.txt',
        ]
        self.scenestarted = true;
        self.currentscene = dialoguescene(background = self.backgrounds[self.dialoguescenenum], dialogueloc = self.dialoguelocations[self.dialoguescenenum]);
    def changescenetonext(self):
        self.dialoguedone = false;
        self.scenestarted = true;
        self.currentscene = dialoguescene(self.backgrounds[self.dialoguescenenum], self.dialoguelocations[self.dialoguescenenum])
    def deletecurrentscene(self):
        del self.currentscene;
        self.currentscene = 0;
    def update(self):
        if not self.scenestarted:
            return None;
        if self.currentscene.state == "done" and self.currentscene.signalcontinue:
            self.dialoguescenenum += 1;
            self.deletecurrentscene()
            self.dialoguedone = true;
            self.scenestarted = false;
            return None;
        self.currentscene.update()
class button:
    def __init__(self, text, type, x, y, desc="_"):
        width = 0
        height = 0;
        if type == "small":
            width = 150
            height = 2 * width
        elif type == "medium":
            width = 175
            height = 2 * width
            pass;
        elif type == "big":
            width = 190
            height = 2 * width
            pass;
        else: #default to medium
            width = 175
            height = 175
            pass;
        self.width = width;
        self.height = height;
        self.text = text;
        self.desctext = desc;
        self.desctextlist = self.desctexttolist(desctext=desc);
        self.x = x;
        self.y = y;
        self.pressed = false;
        fontstring = "Times New Roman"
        fontsize = 50
        descfontsize = 25
        # displays lives
        self.font = pygame.font.SysFont(fontstring, fontsize)
        self.buttontext = self.font.render(self.text, 1, (0,0,0))
        self.descfont = pygame.font.SysFont(fontstring, descfontsize)
        self.hover = false
        self.desctextimg = self.converttexttoimage(textlist=self.desctextlist);
    def checkmouseinrange(self, mousepos, buttonx, buttony, buttonwidth, buttonh):
        mouseposx = mousepos[0]
        mouseposy = mousepos[1]
        xlower = buttonx
        xhigher = buttonx + buttonwidth
        ylower = buttony
        yhigher = buttony + buttonh
        if xlower > mouseposx or xhigher < mouseposx:
            return None;
        if ylower > mouseposy or yhigher < mouseposy:
            return None;
        return true;
    def checkclicked(self, mousepress):
        if mousepress[0]: #element 0 is left click
            return true;
        return None
    def desctexttolist(self, desctext):
        checkcharactersize = len(desctext)
        textlist = []
        idx = 0
        bordercharsize = 16
        while checkcharactersize > -bordercharsize:
            textlist.append(desctext[idx:idx + bordercharsize])
            checkcharactersize -= bordercharsize
            idx += bordercharsize
        for string in textlist:
            pass
            # print(f"{string=}")
        return textlist
    def converttexttoimage(self, textlist):
        imglist = []
        for text in textlist:
            imglist.append(self.descfont.render(text, 1, (0,0,0)))

        return imglist
    def update(self):
        buttontext = self.buttontext
        if self.hover:
            if not self.desctext == "_":

                yadjust = -(len(self.desctextimg)-2)/2 * self.desctextimg[0].get_height()
                for desctext in self.desctextimg:
                    descrect = desctext.get_rect(center = (self.x, self.y))
                    globals.screen.blit(desctext, (descrect.x + self.width/2, descrect.y + self.height/2 + yadjust));
                    yadjust += desctext.get_height()
        else:
            textrect = buttontext.get_rect(center=(self.x, self.y))
            globals.screen.blit(buttontext, (textrect.x + self.width/2, textrect.y + self.height/2));
        if self.checkmouseinrange(mousepos = pygame.mouse.get_pos(),buttonx = self.x, buttony = self.y,
                                  buttonwidth = self.width, buttonh = self.height):
            self.hover = true
            # print("mouse is in range!")
            if self.checkclicked(pygame.mouse.get_pressed()):
                self.pressed = true;
        else:
            self.hover = false
class imagedbutton:
    def __init__(self, imagedir, x, y, toggle=false, startontrue=false):
        self.pressed = startontrue;
        self.toggle = toggle;
        self.image = pygame.image.load(imagedir);
        rect = self.image.get_rect()
        self.width = rect.width;
        self.height = rect.height
        self.hover = false;
        self.x = x - self.width/2;
        self.y = y - self.height/2;
    def checkmouseinrange(self, mousepos, buttonx, buttony, buttonwidth, buttonh):
        mouseposx = mousepos[0]
        mouseposy = mousepos[1]
        xlower = buttonx
        xhigher = buttonx + buttonwidth
        ylower = buttony
        yhigher = buttony + buttonh
        if xlower > mouseposx or xhigher < mouseposx:
            return None;
        if ylower > mouseposy or yhigher < mouseposy:
            return None;
        return true;
    def checkclicked(self, mousepress):
        if mousepress[0]: #element 0 is left click
            return true;
        return None
    def update(self):
        globals.screen.blit(self.image, (self.x, self.y))
        if self.checkmouseinrange(mousepos=pygame.mouse.get_pos(), buttonx=self.x, buttony=self.y,
                                  buttonwidth=self.width, buttonh=self.height):
            self.hover = true
            # print("mouse is in range!")
            if self.checkclicked(pygame.mouse.get_pressed()):
                if not self.toggle:
                    self.pressed = true;
                    return None;
                if self.pressed == true:
                    self.pressed = false;
                    return None;
                else:
                    self.pressed = true;
        else:
            self.hover = false;
class archetypestatstorage:
    def __init__(self, name):
        jumppow = 0
        gravity = 0
        plrxvel = 0
        lives = 0
        if name == "samurai":
            plrxvel = 27
            jumppow = 27
            gravity = 1.5
            lives = 5
        elif name == "tank":
            plrxvel = 18
            jumppow = 20
            gravity = 1.6
            lives = 50
        elif name == "glider":
            plrxvel = 20
            jumppow = 30
            gravity = 1
            lives = 5
        elif name == "ninja":
            plrxvel = 30
            jumppow = 30
            gravity = 1.25
            lives = 1
        elif name == "athlete":
            plrxvel = 25
            jumppow = 25
            gravity = 1.5
            lives = 10
        else:
            plrxvel = 20
            jumppow = 20
            gravity = 1.5
            lives = 5
        self.jumppow = -jumppow #because physics storage takes negative jumppower arg
        self.gravity = gravity
        self.plrxvel = plrxvel
        self.lives = lives
class archetypeselect:
    def __init__(self):
        #Buttons
        self.sceneinittime = pygame.time.get_ticks()
        backgrounddir = cwd + "/archetypeselect/background.png"
        self.background = pygame.image.load(backgrounddir)
        buttonslist = []
        buttonspacingfactor = 203;
        numbuttons = 5;
        buttonyfactor = -50
        # print("screenwidth: ", screenwidth);
        text = ["athlete", "samurai", "tank", "ninja", "glider"]
        desctext = [
            "slightly fast, slightly high jump, 10 health", #athlete
            "fast, high jump, 5 health", #samurai
            "slow, low jump, 50 health", #tank
            "very fast, very high jump, slightly floaty 5 health", #ninja
            "slow, slightly high jump, floaty, faster in air, 5 health," #glider
        ]
        for i in range(numbuttons):
            buttonslist.append(button(text = text[i], type = "big",
                                      x = (i * buttonspacingfactor), y = screenheight/2 + buttonyfactor, desc = desctext[i]  ));
        self.buttonslist = buttonslist;
        self.done = false;
        fontsize = 100
        fontstring = "Times New Roman"
        titlefont = pygame.font.SysFont(name=fontstring, size= fontsize)
        headingfont = pygame.font.SysFont(name = fontstring, size= 32)
        self.chooseanarchetype = titlefont.render("choose an archetype", 1, (0,0,0))
        self.hoveroverprompt = headingfont.render("Hover for more info on archetype", 1, (0,0,0))
        self.clickprompt = headingfont.render("Click the archetype you want to choose", 1, (0,0,0))
    def onbuttonsignal(self, button):
        timenow = pygame.time.get_ticks()
        cooldown = 1300
        if timenow - self.sceneinittime < cooldown:
            button.pressed = false
            return None;
        self.done = true;
        globals.archetype = button.text
        self.deletescene()
    def deletescene(self):
        del self.chooseanarchetype;
        del self.hoveroverprompt;
        del self.clickprompt;
        for button in self.buttonslist:
            del button;
        del self.buttonslist;
        del self.background;
        del self.sceneinittime;
    def update(self):
        globals.screen.blit(self.background, (0,0))
        globals.screen.blit(self.chooseanarchetype, (0,0))
        globals.screen.blit(self.hoveroverprompt, (0, 150))
        globals.screen.blit(self.clickprompt, (0, 210))
        keys = pygame.key.get_pressed()
        for button in self.buttonslist:
            # print("button.x: ", button.x);
            pygame.draw.rect(globals.screen, (255,255,255), (button.x, button.y, button.width, button.height));
            button.update()
            if button.pressed:
                self.onbuttonsignal(button = button);
                # print(f"{globals.archetype = }")
class titlescreen:
    def __init__(self):
        self.done = false
        backgrounddir = cwd + "/titlescreen/background.png"
        self.background = pygame.image.load(backgrounddir)
        playbuttondir = cwd + "/titlescreen/playbutton.png"
        playbuttonx = 0
        playbuttony = 0
        self.playbutton = imagedbutton(imagedir= playbuttondir, x = screenwidth/2, y = screenheight/2)

    def onbuttonsignal(self):
        self.done = true;
        self.deletescene();
    def deletescene(self):
        del self.background;
        self.background = None;
        del self.playbutton;
        self.playbutton = None;
    def update(self):
        screen = globals.screen
        screen.blit(self.background, (0,0))
        self.playbutton.update()
        if self.playbutton.pressed:
            self.onbuttonsignal()
class game:
    def __init__(self):
        self.gamescenenum = 0; #index for gamescenetypes
        self.gamescenetypes = [
            "dialogue",
            "level",
            "dialogue",
            "level",
            "dialogue",
            "level",
            "dialogue",
            "level",
            "dialogue",
            "gameover"
        ]
        self.numlevels = len(self.gamescenetypes)
        self.state = "on" + self.gamescenetypes[0];
        self.levelhandler = levelhandler();
        self.dialoguehandler = dialoguehandler();
        self.archetypeselect = archetypeselect();
        self.titlescreen = titlescreen();
    def checklevelstate(self, levelhandler):
        # print("hello world level");
        if not levelhandler.levelcomplete:
            return None;
        self.gamescenenum+=1;
            # print("reached")
        self.levelhandler.deletelevel()
        if self.gamescenetypes[self.gamescenenum] == "level":
            self.levelhandler.changeleveltonext();
            self.state = "onlevel";
        elif self.gamescenetypes[self.gamescenenum] == "dialogue":
            self.dialoguehandler.changescenetonext();
            self.state = "ondialogue";
        else:
            pygame.quit();
        levelhandler.levelcomplete = false;
    def gameover(self):
        sys.exit()
    def checkdialoguescenestate(self, dialoguehandler):
        if not dialoguehandler.dialoguedone:
            return None;
            # print("hello world dialogue");
        self.gamescenenum+=1;
        if self.gamescenetypes[self.gamescenenum] == "gameover":
            self.gameover()
        elif self.gamescenetypes[self.gamescenenum] == "dialogue":
            self.dialoguehandler.changescenetonext();
            self.state = "ondialogue";

        #have not put "else" because I might add another scene type
        elif self.gamescenetypes[self.gamescenenum] == "level":
            self.levelhandler.changeleveltonext();
            self.state = "onlevel";

    def run(self):
        if self.titlescreen:
            self.titlescreen.update();
            if self.titlescreen.done:
                del self.titlescreen;
                self.timeswitched = pygame.time.get_ticks();
                self.titlescreen = None;
            return None;

        if self.archetypeselect:
            #loading cooldown
            timenow = pygame.time.get_ticks();
            if timenow - self.timeswitched < 250:
                return None
            self.archetypeselect.update();
            if self.archetypeselect.done:
                del self.archetypeselect
                self.archetypeselect = None;
                # print("archetype select screen is done")
            return None;

        if self.state == "onlevel":
            self.levelhandler.update();
            self.checklevelstate(levelhandler = self.levelhandler);
            return None;
        elif self.state == "ondialogue":
            self.dialoguehandler.update();
            self.checkdialoguescenestate(dialoguehandler = self.dialoguehandler);


