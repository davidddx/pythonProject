import pygame, sys, os
import globals
from settings import *
from pytmx.util_pygame import load_pygame;


#next idea is to use objects in tiled to add background to levels
class Map():
    def __init__(self, tmxdata):
        self.collidablegroup = pygame.sprite.Group();
        self.noncollidablegroup = pygame.sprite.Group();
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
        # for tiles in self.fullspritegroup:
        #     tiles.kill()
        self.collidablegroup.empty()
        self.noncollidablegroup.empty()
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
class Door(pygame.sprite.Sprite):
    def __init__(self, surface, pos):
        pygame.sprite.Sprite.__init__(self);
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)

    def delete(self):
        self.kill()
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
            self.targetx = globals.levelhandler.currentlevel.player.rect.x
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
        self.physics = physics(gravity = 2, onground = false, plrxvel = 30, jumppow = -35);
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
        self.lives = 50
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
        if self.onground:
            self.numberjumpsinair = 0;
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
class Level:
    def __init__(self, currentmap, plr):
        self.levelcurrentlychanging = false
        self.currentmap = self.inittiles(currentmap);
        self.playeronground = false;
        self.player = plr;
        self.current_x = 0
        self.oobpos = pygame.math.Vector2(0,0)
        self.enemies = self.findenemies(currentmap)
        self.markers = self.findmarkers(currentmap)
        self.timeplrlastcollidedwithenemy = 0
        self.door = self.finddoor(currentmap)
        self.nontiledobjects = self.groupnontiledobjects() #enemy is not included in this spritegroup
        self.doorcollisionoccured = false
        self.checkedenemieswitheyes = false;
        self.hasenemieswitheyes = false;

#finddoor, findenemies, findmarkers, etc functions find and return important info like spritelocs/positions/etc
    def finddoor(self, mapinst):
        door = 0
        doorlayer = mapinst.tmxdata.get_layer_by_name("Door")
        for door in doorlayer:
            props = door.properties
            doorname = props["name"]
            # print(dir(door))
            # print(door.parent)
            if doorname == "door":
                # print("door.properties: ", door.properties)
                # print("door created")
                door = Door(surface = door.image, pos = (door.x, door.y))
        return door
    def groupnontiledobjects(self):
        #this function makes sure everything was in a spritegroup so that all sprites in a level could be deleted and changed properly
        nontiledobjectsgroup = pygame.sprite.Group()
        nontiledobjectsgroup.add(self.player)
        nontiledobjectsgroup.add(self.door)


        return nontiledobjectsgroup
    def findenemies(self, mapinst):
        #think of this function as an enemy factory
        enemygroup = pygame.sprite.Group()
        enemyimage = pygame.image.load(enemyspriteloc)
        enemyshirtcolor = "blue"
        enemyspawnpointlayer = mapinst.tmxdata.get_layer_by_name("EnemySpawnPoints")

        for aobject in enemyspawnpointlayer:
            # print("aobject.properties: ", aobject.properties);
            props = aobject.properties;
            name = props["name"];
            if name == "BlueEnemySpawner":
                enemyimage = pygame.image.load(cwd + '/tiles/EnemySprites/idleblueenemy.png')
                enemyshirtcolor = "blue"
            elif name == "RedEnemySpawner":
                enemyimage = pygame.image.load(cwd + '/tiles/EnemySprites/idleredenemy.png')
                enemyshirtcolor = "red"
            elif name == "GreenEnemySpawner":
                enemyimage = pygame.image.load(cwd + '/tiles/EnemySprites/idlegreenenemy.png')
                enemyshirtcolor = "green"

            elif name == "PurpleEnemySpawner":
                enemyimage = pygame.image.load(cwd + '/tiles/EnemySprites/idlepurpleenemy.png')
                enemyshirtcolor = "purple"

            elif name == "BlackEnemySpawner":
                enemyimage = pygame.image.load(cwd + '/tiles/EnemySprites/idleblackenemy.png')
                enemyshirtcolor = "black"
            elif name == "GrayEnemySpawner":
                enemyimage = pygame.image.load(cwd + "/tiles/EnemySprites/idlegrayenemy.png");
                enemyshirtcolor = "gray"
            else:
                enemyimage = pygame.image.load(cwd + '/tiles/EnemySprites/idleredenemy.png')
                enemyshirtcolor = "red"


            thisenemy = Enemy(surface = enemyimage, pos = (aobject.x, aobject.y), shirtcolor = enemyshirtcolor);
            enemygroup.add(thisenemy)

        return enemygroup

#markers used for spawning plrs/enemys and setting oob
    def findmarkers(self, mapinst):
        markerlist = []
        markerlayer = mapinst.tmxdata.get_layer_by_name("Markers")
        for aobject in markerlayer:
            properties = aobject.properties
            objname = properties["name"]
            if objname == "plrspawn":
                self.setplrspawnpos(spawnpointx = aobject.x, spawnpointy = aobject.y)
            elif objname == "OutOfBounds":
                self.oobpos.x = aobject.x
                self.oobpos.y = aobject.y
            markerlist.append(aobject)

        return markerlist
    def setplrspawnpos(self, spawnpointx, spawnpointy):
        self.player.rect.x = spawnpointx
        self.player.rect.y = spawnpointy

#func below inits tiles and enemies
    def inittiles(self, mapinst):
        # mapinst.fullspritegroup.empty()
        mapinst.collidablegroup.empty()
        mapinst.noncollidablegroup.empty()
        instmap = mapinst
        layerindex = -1;
        groupc = []
        groupn = []
        enemylist = []
        collidablegroup = mapinst.collidablegroup
        noncollidablegroup = mapinst.noncollidablegroup
        visiblelayers = mapinst.tmxdata.visible_layers
        for layer in visiblelayers:
            # print("hasattr(layer, 'data'", hasattr(layer, "data"))
            if not hasattr(layer, "data"):
                continue;

            layerindex+=1;
            # print("layer.name: ", layer.name);
            # print("layerindex: ", layerindex);

            for x,y,surf in layer.tiles():
                pos = (64*x, 64*y);
                props = mapinst.tmxdata.get_tile_properties(x, y, layerindex)
                tile_id = props["id"]
                spritegroup = 0
                if ((tile_id >= 2 and tile_id <= 7) or tile_id == 19 or tile_id == 18 or tile_id == 13 or tile_id == 12):
                    collidable = "yes"
                    spritegroup = collidablegroup
                else:
                    collidable = "no"
                    spritegroup = noncollidablegroup


                # print("props: ", props);
                # print("props(""id""): ", props["id"])
                # print("collidable?: ", collidable)
                tile_info = {
                    "pos": pos,
                    "surf": surf,
                    "groups": spritegroup,
                    "tile_id": tile_id,
                    "collidable": collidable
                }
                tileinstance = Tile(**tile_info)
                if collidable == "yes":
                    groupc.append(tileinstance)
                else:
                    groupn.append(tileinstance)

                instmap.tilelist.append(tileinstance);


        instmap.noncollidablegroup.add(groupn);
        instmap.collidablegroup.add(groupc);
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
        for sprite in self.currentmap.collidablegroup.sprites():
            if not sprite.isinrange: continue;
            if sprite.rect.colliderect(player.rect):
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
            if enemy.hasprojectile:
                for projectile in enemy.projectilegroup:
                    if projectile.rect.colliderect(player.rect):
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
                if not enemy.hasprojectile:
                    continue;

                # need to change code below, it causes lag
                for projectile in enemy.projectilegroup:
                    if not projectile.isinrange: continue;
                    if projectile.rect.colliderect(sprite.rect):
                        projectile.deletenextframe = true;
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
            globals.levelhandler.changeleveltonext()

#oob logic
    def checkifplroob(self):
        if self.player.rect.y >= self.oobpos.y:
            self.player.lives -= 1
            # print("player is out of bounds, has lost one life. player.lives is now ", self.player.lives)
            self.player.isOob = true

# level scroller and tile position updates

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
    def deletelevel(self):
        self.levelcurrentlychanging = true
        self.currentmap.clearmap()
        for objects in self.nontiledobjects.sprites():
            objects.delete()

        self.nontiledobjects.empty()
        for enemy in self.enemies.sprites():
            enemy.delete()
        self.enemies.empty()
        self.markers.clear()
        self.markers = []
class levelhandler:
    def __init__(self):
        self.islevel = true
        self.levelnum = globals.savedlevelnum
        self.nextlevel = globals.savedlevelnum + 1
        self.worldnum = globals.savedworldnum
        self.changinglevel = false
        self.tmxdata = 0
        self.nextmap = 0
        self.tmxdatalocs = [
            cwd + '/Maps/testmap/level2.tmx',
            cwd + "/Maps/testmap/level1.tmx",
            cwd + '/Maps/testmap/testmappygame1.tmx',
            cwd + '/Maps/testmap/testmappygame2.tmx',
            cwd + '/Maps/testmap/testmappygame3.tmx',
        ] #contains locations of all map data
        self.maxlevelnum = len(self.tmxdatalocs)
        self.currentlevel = self.initlevel(levelnum = self.levelnum)
        self.plrlives = self.currentlevel.player.lives #need to add gui element to plr lives
        self.heartsymbol = pygame.image.load(cwd + '/tiles/heartsymbol.png')
    def initlevel(self, levelnum):
        tmxdata = load_pygame(self.tmxdatalocs[self.levelnum])
        map = Map(tmxdata = tmxdata)
        plr = Plr(plrpos=(0,0), plrsurf=pygame.image.load(plrspriteloc))
        level = Level(currentmap = map, plr = plr)
        return level

#will add stuff to getmaxlevelnum function when i have world and level organization situated
    def getmaxlevelnum(self):
        thismaxlevelnum = 0
        #whatever logic here
        #
        #
        #
        #
        #
        print("returned max level num for this world")
        return thismaxlevelnum;

#returns the next level
    def changeleveltonext(self):
        self.plrlives = self.currentlevel.player.lives
        # print("lives left: ", self.plrlives)
        self.currentlevel.deletelevel()
        del self.currentlevel
        self.currentlevel = 0
        self.levelnum+=1
        # maparr = self.maparray
        plrx = 18;
        plry = 3;
        plr = Plr(plrpos=(plrx * 64, plry * 64), plrsurf=pygame.image.load(plrspriteloc))
        plr.lives = self.plrlives
        self.tmxdata = load_pygame(self.tmxdatalocs[self.levelnum])
        tmxdata = self.tmxdata
        map = Map(tmxdata = tmxdata)
        self.currentlevel = Level(currentmap=map, plr=plr)
        # print("level has been changed!")
    def checkrestartlevel(self):
        if self.currentlevel.player.isOob == false:
            return None
        self.plrlives = self.currentlevel.player.lives
        self.currentlevel.deletelevel()
        del self.currentlevel
        levelnum = self.levelnum
        plrx = 18;
        plry = 3;
        plr = Plr(plrpos=(plrx * 64, plry * 64), plrsurf=pygame.image.load(plrspriteloc))
        plr.lives = self.plrlives
        self.tmxdata = load_pygame(self.tmxdatalocs[levelnum])
        tmxdata = self.tmxdata
        map = Map(tmxdata=tmxdata)
        self.currentlevel = Level(currentmap=map, plr=plr)
    def checkifgameover(self, plrlives):
        if not plrlives <= 0:
            return None

        print("game over, you have lost all your lives. Exiting the application...")
        pygame.quit()
        sys.exit()

#levelhandler update function and render function just puts everything on the screen

    def render(self, thislevel, screen, adjustcamerayfactor, adjcamx):
        collgroup = thislevel.currentmap.collidablegroup
        noncollgroup = thislevel.currentmap.noncollidablegroup
        enemygroup = thislevel.enemies
        otherobjgroup = thislevel.nontiledobjects
        plr = thislevel.player
        plrx = plr.rect.x
        plry = plr.rect.y
        door = thislevel.door
        extrarendering = 64 * 6
        viewleft = plrx - screenwidth / 2 - extrarendering
        viewright = plrx + screenwidth / 2 + extrarendering
        viewup = plry - screenheight / 2 - extrarendering
        viewdown = plry + screenheight / 2 + extrarendering

        for sprite in collgroup:
            spritex = sprite.rect.x
            spritey = sprite.rect.y
            if viewleft <= spritex <= viewright and viewup <= spritey <= viewdown:
                sprite.isinrange = true; #matters for performance
                screen.blit(sprite.image, (sprite.rect.x + adjcamx, sprite.rect.y + adjustcamerayfactor))
            else:
                sprite.isinrange = false
        for sprite in noncollgroup:
            spritex = sprite.rect.x
            spritey = sprite.rect.y
            if viewleft <= spritex <= viewright and viewup <= spritey <= viewdown:
                screen.blit(sprite.image, (sprite.rect.x + adjcamx, sprite.rect.y + adjustcamerayfactor))

        for enemy in enemygroup:
            enemyx = enemy.rect.x
            enemyy = enemy.rect.y
            if viewleft <= enemyx <= viewright and viewup <= enemyy <= viewdown:
                enemy.isinrange = true
                screen.blit(enemy.image, (enemy.rect.x + adjcamx, enemy.rect.y + adjustcamerayfactor))
            else:
                enemy.isinrange = false
            if enemy.hasprojectile and len(enemy.projectilegroup) != 0:
                for thisprojectile in enemy.projectilegroup:
                    # thisprojectile.printvalues();
                    projectilex = thisprojectile.rect.x
                    projectiley = thisprojectile.rect.y
                    if viewleft <= projectilex <= viewright and viewup <= projectiley <= viewdown:
                        projectile.isinrange = true
                        screen.blit(thisprojectile.image, (thisprojectile.rect.x + adjcamx, thisprojectile.rect.y + adjustcamerayfactor))
                    else:
                        projectile.isinrange = false

        for obj in otherobjgroup:
            objx = obj.rect.x
            objy = obj.rect.y
            if viewleft <= objx <= viewright and viewup <= objy <= viewdown:  # pygame has upward as negative so the inequality is up <= y <= down instead of down <= y <= up
                screen.blit(obj.image, (objx + adjcamx, obj.rect.y + adjustcamerayfactor))
        if not self.changinglevel:
            #displays lives
            livesfont = pygame.font.SysFont("Times New Roman", 64)
            livesimg = livesfont.render(str(plr.lives), 1, (255,255,255))
            screen.blit(self.heartsymbol, (0, 0))
            screen.blit(livesimg, (64, 0))
    def update(self):
        screen = globals.screen
        adjustcamerayfactor = -(self.currentlevel.player.rect.y - self.currentlevel.player.adjustcamerayfactor)
        adjustcameraxfactor = -(self.currentlevel.player.rect.x - self.currentlevel.player.adjustcameraxfactor)
        self.currentlevel.run();
        screen.fill((0, 0, 0));
        thislevel = self.currentlevel
        self.render(thislevel = thislevel, screen = screen, adjustcamerayfactor = adjustcamerayfactor, adjcamx = adjustcameraxfactor)
        self.checkrestartlevel()
        self.checkifgameover(self.currentlevel.player.lives)
