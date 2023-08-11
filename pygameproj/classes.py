import pygame, sys, os
from settings import *
from pytmx.util_pygame import load_pygame;

#next move: make an enemy system

class Map():
    def __init__(self, collidablegroup, noncollidablegroup, tmxdata, fullspritegroup):
        self.collidablegroup = collidablegroup;
        self.noncollidablegroup = noncollidablegroup;
        self.tmxdata = tmxdata;
        self.fullspritegroup = fullspritegroup
        self.tilelist = []
    def printallproperties(self):
        print("tilelist", self.tilelist);
        print("fullspritegroup", self.fullspritegroup);
        print("collidablegroup", self.collidablegroup);
        print("noncollidablegroup", self.noncollidablegroup);
        print("tmxdata", self.tmxdata);


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

class physics():
    def __init__(self, gravity, onground, plrxvel, jumppow):
        self.gravity = gravity;
        self.onground = onground;

        self.plrxvelocity = plrxvel;
        self.jumppow = jumppow;
        self.direction = pygame.math.Vector2(1,0);
class Plr(pygame.sprite.Sprite):
    def __init__(self, plrpos, plrsurf):
        pygame.sprite.Sprite.__init__(self);
        self.image = plrsurf;
        self.rect = self.image.get_rect(topleft = plrpos);
        self.timelastpressedx = 0;
        self.movable = true;
        self.onground = false;
        self.physics = physics(gravity = 0.5, onground = false, plrxvel = 30, jumppow = -15);
        self.facingright = true;
        self.jumpcounter = 0;
        self.timelastjump = 0;

    def update(self, currmap):
        self.inputmap()
    def inputmap(self):
        plrvelx = 2;
        jumpheight = 10;
        pausecooldown = 100;
        jumpcooldown = 1100;
        key = pygame.key.get_pressed();
        timenow = pygame.time.get_ticks();
        if key[pygame.K_x] and timenow - self.timelastpressedx >= pausecooldown:  # press x to unlock camera
            self.movable = not self.movable;

            self.timelastpressedx = timenow;
        if self.movable:
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
                self.jump();
                self.onground = false;
            if key[pygame.K_s]:
                self.physics.direction.y+=1;

        if key[pygame.K_ESCAPE]:
            pygame.quit();
            sys.exit();

    def applygravity(self):
        self.physics.direction.y += self.physics.gravity
        self.rect.y += self.physics.direction.y


    def jump(self):
        if self.onground:
            self.physics.direction.y = self.physics.jumppow

class Enemy(pygame.sprite.Sprite):
    #pos is the enemy position
    def __init__(self, surface, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = surface
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





    def update(self):
        self.jump()


class Level:

    def __init__(self, currentmap, plr):
        self.currentmap = self.inittiles(currentmap);
        self.playeronground = false;
        self.player = plr;
        self.plrspawnpoint = pygame.math.Vector2(0,0)
        self.world_shift = 0
        self.current_x = 0
        self.enemies = self.findenemies(currentmap)
        self.markers = self.findmarkers(currentmap)
        self.timeplrlastcollidedwithenemy = 0
        self.door = self.finddoor(currentmap)

    def finddoor(self, mapinst):
        door = 0
        doorlayer = mapinst.tmxdata.get_layer_by_name("Door")
        for door in doorlayer:
            # print(dir(door))
            # print(door.properties)
            # print(door.parent)
            if door.name == "door":

                print("line 150 reached")
                door = Door(surface = door.image, pos = (door.x, door.y))
        return door


    def findenemies(self, mapinst):
        enemygroup = pygame.sprite.Group()
        enemyimage = pygame.image.load(enemyspriteloc)
        enemyspawnpointlayer = mapinst.tmxdata.get_layer_by_name("EnemySpawnPoints")

        for aobject in enemyspawnpointlayer:
            print(dir(aobject))
            thisenemy = Enemy(surface = enemyimage, pos = (aobject.x, aobject.y))
            enemygroup.add(thisenemy)

        return enemygroup

# we will use the markers object.x and object.y property for logic and stuff
#
    def findmarkers(self, mapinst):
        markerlist = []
        markerlayer = mapinst.tmxdata.get_layer_by_name("Markers")
        for aobject in markerlayer:

            if aobject.name == "PlayerSpawnPoint":
                self.plrspawnpoint.x = aobject.x
                self.plrspawnpoint.y = aobject.y
            markerlist.append(aobject)

        return markerlist

    def getplrspawnx(self):
        print("set plr pos")
        return self.plrspawnpoint.x
    def getplrspawny(self):
        return self.plrspawnpoint.y


    #func below inits tiles and enemies
    def inittiles(self, mapinst):
        instmap = mapinst
        layerindex = -1;
        groupc = []
        groupn = []
        enemylist = []
        spritegroup = mapinst.fullspritegroup;
        visiblelayers = mapinst.tmxdata.visible_layers
        for layer in visiblelayers:
            if not hasattr(layer, "data"):
                continue;

            layerindex+=1;
            # print("layer.name: ", layer.name);
            # print("layer.index: ", lightlayerindex);

            for x,y,surf in layer.tiles():
                pos = (64*x, 64*y);
                props = mapinst.tmxdata.get_tile_properties(x, y, layerindex)
                tile_id = props["id"]
                collidable = "no"
                if ((tile_id >= 4 and tile_id <= 7) or tile_id == 19 or tile_id == 18):
                    collidable = "yes"

                print("props: ", props);
                print("props(""id""): ", props["id"])
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
        instmap.fullspritegroup.add(groupn);
        instmap.fullspritegroup.add(groupc);
        return instmap;

    def get_player_on_ground(self):
        if self.player.onground:
            self.playeronground = True
        else:
            self.playeronground = False

#detect horizontal movement collision
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

#detect vertical movement collision for players and enemies
    def vertmovecoll(self):
        player = self.player;
        player.applygravity()
        for sprite in self.currentmap.collidablegroup.sprites():
            if sprite.rect.colliderect(player.rect):
                if -player.physics.direction.y < 0:
                    self.player.onground = true
                    player.rect.bottom = sprite.rect.top
                    player.physics.direction.y = 0;
                elif -player.physics.direction.y > 0:
                    player.rect.top = sprite.rect.bottom
                    player.physics.direction.y = 0;

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
                print("enemy player collision has occured")
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

    def checkdoorplrcoll(self):
        plr = self.player
        door = self.door
        if plr.rect.colliderect(door):
            print("plr has collided with door")

    def scroller(self):
        player = self.player;
        plrxvel = 15
        playerx = player.rect.centerx
        directionx = player.physics.direction.x
        mapscrollconst = 3
        if playerx < screenwidth/mapscrollconst and directionx < 0:
            self.world_shift = plrxvel
            self.player.physics.plrxvelocity = 0;
        elif playerx > screenwidth - (screenwidth / mapscrollconst) and directionx > 0:
            self.world_shift = -plrxvel
            self.player.physics.plrxvelocity = 0
        else:
            self.world_shift = 0
            self.player.physics.plrxvelocity = plrxvel

    def updatetilepos(self, xscroll):
        for sprite in self.currentmap.fullspritegroup.sprites():
            sprite.rect.x += xscroll
        for enemy in self.enemies.sprites():
            enemy.rect.x+=xscroll
        self.door.rect.x+=xscroll

    def jumpenemy(self):
        for enemy in self.enemies:
            enemy.update()


    def run(self):
        #Level
        self.scroller();
        self.updatetilepos(self.world_shift)
        #PLAYER
        self.player.update(self.currentmap)
        self.horizontalmovecoll()
        self.vertmovecoll()
        self.checkplrenemycoll()
        self.checkdoorplrcoll()
        #Enemy
        self.jumpenemy()
        self.enemygroundcoll()
        self.enemywallcoll()
