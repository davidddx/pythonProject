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
class Plr(pygame.sprite.Sprite):
    def __init__(self, plrpos, plrsurf):
        pygame.sprite.Sprite.__init__(self);
        self.animating = true
        self.spritelist = []
        self.spritelist.append(plrsurf)
        self.spritelist.append(pygame.image.load(cwd + '/tiles/plrjumpframe0.5.png'))
        self.spritelist.append(pygame.image.load(cwd + '/tiles/plrjumpframe1.png'))
        self.spritelist.append(pygame.image.load(cwd + '/tiles/plrjumpframe1.5.png'))
        self.spritelist.append(pygame.image.load(cwd + '/tiles/plrjumpframe2.png'))
        self.spritelist.append(pygame.image.load(cwd + '/tiles/plrjumpframe2.5.png'))
        self.spritelist.append(pygame.image.load(cwd + '/tiles/plrjumpframe3.png'))
        self.spritelist.append(pygame.image.load(cwd + '/tiles/plrjumpframe3.5.png'))
        self.spritelist.append(pygame.image.load(cwd + '/tiles/plrjumpframe4.png'))
        self.spritelist.append(pygame.image.load(cwd + '/tiles/plrjumpframe4.5.png'))
        self.spritelist.append(pygame.image.load(cwd + '/tiles/plrjumpframe5.png'))

        self.currentspriteidx = 0
        self.image = plrsurf;
        self.rect = self.image.get_rect(topleft = plrpos);
        self.onground = false;
        self.physics = physics(gravity = 1, onground = false, plrxvel = 30, jumppow = -30);
        self.facingright = true;
        self.jumpcounter = 0;
        self.timelastjump = 0;
        self.belowplatform = false
        self.numjumpsinair = 0
        self.timelastdashed = 0;
        self.defaultxvelocity = 15
        self.dashfactor = 30
        self.timelastran = 0
        self.ondash = false
        self.adjustcamerayfactor = 0
        self.adjustcameraxfactor = screenwidth / 2
        self.alreadypressedq = false
        self.alreadypressede = false
        self.isOob = false
        self.lives = 5

    def update(self, currmap):
        if self.onground:
            self.numberjumpsinair = 0;
        self.animatejump()
        self.inputmap()
        self.checkifdashdone(timelastdashed = self.timelastdashed, dashfactor = self.dashfactor) #dashfactor is how much player's x velocity increases on dash

    def animatejump(self):
        if self.animating == true:
            # print("animating")
            idxstep = 1
            self.currentspriteidx+=idxstep
            self.image = self.spritelist[int(self.currentspriteidx)]
            if self.currentspriteidx >= len(self.spritelist) - idxstep:
                self.animating = false
                self.currentspriteidx = 0
            if not self.facingright:
                self.image = pygame.transform.flip(self.image, true, false)
        else:
            if self.onground:

                self.image = self.spritelist[0] #change to 0 when back on ground
            else:
                self.image = self.spritelist[len(self.spritelist) - 1]
            if not self.facingright:
                self.image = pygame.transform.flip(self.image, true, false)



#function restores plr to speed after dashed
    def checkifdashdone(self, timelastdashed, dashfactor):
        if not self.ondash:
            return None
        timenow = pygame.time.get_ticks();
        dashfinishcd = 200
        if timenow - timelastdashed >= dashfinishcd:
            # print("dash has finished")
            self.physics.plrxvelocity -= dashfactor
            self.ondash = false

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
            if not self.facingright:
                self.image = pygame.transform.flip(self.image, true, false)
                self.facingright = true;
            self.physics.direction.x = 1;
        elif key[pygame.K_a]:
            if self.facingright:
                self.image = pygame.transform.flip(self.image, true, false)
                self.facingright = false
            self.physics.direction.x = -1;
        else:
            self.physics.direction.x = 0;
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
    def applygravity(self):
        self.physics.plryvelocity += self.physics.gravity
        self.physics.direction.y = self.physics.plryvelocity
        self.rect.y += self.physics.plryvelocity
    def jump(self, cooldown, timenow, timelastpressed):
        #jump function assures doublejump capability and platform hanging when below platform block
        if self.onground:
            self.animating = true;
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
                self.animating = true
                self.animatejump()
                self.numjumpsinair+=1
                self.physics.plryvelocity = self.physics.jumppow
                self.physics.direction.y = self.physics.jumppow
    def delete(self):
        self.kill()

class Enemy(pygame.sprite.Sprite):
    #pos is the enemy position
    def __init__(self, surface, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = surface
        self.enemyisinrange = false
        self.gravity = 0.5
        self.direction = pygame.math.Vector2(-1,0);
        self.jumppow = -15
        self.rect = self.image.get_rect(topleft=pos);
        self.onground = false
        self.xvel = 4
    def applygravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y
    def jump(self):
        if self.onground:
            self.direction.y = self.jumppow
            self.onground = false
    def delete(self):
        self.kill()
    def update(self):
        if self.enemyisinrange:
            self.jump()
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
                print("door.properties: ", door.properties)
                print("door created")
                door = Door(surface = door.image, pos = (door.x, door.y))
        return door
    def groupnontiledobjects(self):
        #this function makes sure everything was in a spritegroup so that all sprites in a level could be deleted and changed properly
        nontiledobjectsgroup = pygame.sprite.Group()
        nontiledobjectsgroup.add(self.player)
        nontiledobjectsgroup.add(self.door)


        return nontiledobjectsgroup
    def findenemies(self, mapinst):
        enemygroup = pygame.sprite.Group()
        enemyimage = pygame.image.load(enemyspriteloc)
        enemyspawnpointlayer = mapinst.tmxdata.get_layer_by_name("EnemySpawnPoints")

        for aobject in enemyspawnpointlayer:
            thisenemy = Enemy(surface = enemyimage, pos = (aobject.x, aobject.y))
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
                if ((tile_id >= 4 and tile_id <= 7) or tile_id == 19 or tile_id == 18):
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
        timenow = pygame.time.get_ticks()
        player = self.player
        cooldown = 3000; #planning to make invincibility 3 seconds
        enemygroup = self.enemies.sprites()
        for enemy in enemygroup:
            if enemy.rect.colliderect(player.rect) and timenow - self.timeplrlastcollidedwithenemy >= cooldown:
                #enemy collision now works
                self.player.lives -= 1
                print("enemy player collision has occured. plr has lost 1 life. plr lives are now ", self.player.lives)
                self.timeplrlastcollidedwithenemy = timenow
                # if player.rect.x <= enemy.rect.x:
                #     player.rect.x -= 128
                # else:
                #     player.rect.x += 128
    def enemygroundcoll(self):
        for enemy in self.enemies.sprites():
            enemy.applygravity()
            diry = enemy.direction.y
            dirx = enemy.direction.x
            for sprite in self.currentmap.collidablegroup.sprites():
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
            if not enemy.enemyisinrange:
                continue

            dirx = enemy.direction.x
            enemy.rect.x += enemy.direction.x * enemy.xvel
            collidedwithrect = false
            for sprite in self.currentmap.collidablegroup.sprites():
                if enemy.rect.colliderect(sprite.rect):
                    collidedwithrect = true
                    if dirx < 0:
                        enemy.rect.left = sprite.rect.right
                        enemy.direction.x = 1
                    elif dirx > 0:
                        enemy.rect.right = sprite.rect.left

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
            print("player is out of bounds, has lost one life. player.lives is now ", self.player.lives)
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
        self.levelnum = globals.savedlevelnum
        self.nextlevel = globals.savedlevelnum + 1
        self.worldnum = globals.savedworldnum
        self.changinglevel = false
        self.tmxdata = 0
        self.nextmap = 0
        self.tmxdatalocs = [
            cwd + '/Maps/testmap/testmappygame1.tmx',
            cwd + '/Maps/testmap/level1.tmx',
            cwd + '/Maps/testmap/testmappygame2.tmx',
            cwd + '/Maps/testmap/testmappygame3.tmx',
        ] #contains locations of all map data
        self.maxlevelnum = len(self.tmxdatalocs)
        self.currentlevel = self.initlevel(levelnum = self.levelnum)
        self.plrlives = self.currentlevel.player.lives #need to add gui element to plr lives
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
        print(self.plrlives)
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
        print("level has been changed!")
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
                screen.blit(sprite.image, (sprite.rect.x + adjcamx, sprite.rect.y + adjustcamerayfactor))
        for sprite in noncollgroup:
            spritex = sprite.rect.x
            spritey = sprite.rect.y
            if viewleft <= spritex <= viewright and viewup <= spritey <= viewdown:
                screen.blit(sprite.image, (sprite.rect.x + adjcamx, sprite.rect.y + adjustcamerayfactor))

        for enemy in enemygroup:
            enemyx = enemy.rect.x
            enemyy = enemy.rect.y
            if viewleft <= enemyx <= viewright and viewup <= enemyy <= viewdown:
                enemy.enemyisinrange = true
                screen.blit(enemy.image, (enemy.rect.x + adjcamx, enemy.rect.y + adjustcamerayfactor))
            else:
                enemy.enemyisinrange = false
        for obj in otherobjgroup:
            objx = obj.rect.x
            objy = obj.rect.y
            if viewleft <= objx <= viewright and viewup <= objy <= viewdown:  # pygame has upward as negative so the inequality is up <= y <= down instead of down <= y <= up
                screen.blit(obj.image, (objx + adjcamx, obj.rect.y + adjustcamerayfactor))
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
