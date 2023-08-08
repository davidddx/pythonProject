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
        self.timelastpressed = 0;
        self.movable = true;
        self.onground = false;
        self.physics = physics(gravity = 0.5, onground = false, plrxvel = 30, jumppow = -15);
        self.facingright = true;

    def update(self, currmap):
        self.inputmap()


    def inputmap(self):
        plrvelx = 2;
        jumpheight = 10;
        cooldown = 1;
        key = pygame.key.get_pressed();
        timenow = pygame.time.get_ticks();
        if key[pygame.K_x] and timenow - self.timelastpressed >= cooldown:  # press x to unlock camera
            self.movable = not self.movable

            timelastpressed = timenow;
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
            if key[pygame.K_s]:
                self.physics.direction.y+=1;

        if key[pygame.K_ESCAPE]:
            pygame.quit();
            sys.exit();

    def applygravity(self):
        self.physics.direction.y += self.physics.gravity
        self.rect.y += self.physics.direction.y


    def jump(self):
        self.physics.direction.y = self.physics.jumppow





class Level:

    def __init__(self, currentmap, plr):
        self.currentmap = self.inittiles(currentmap);
        self.playeronground = false;
        self.player = plr;
        self.world_shift = 0
        self.current_x = 0

    def inittiles(self, mapinst):
        instmap = mapinst
        layerindex = -1;
        groupc = []
        groupn = []
        spritegroup = mapinst.fullspritegroup;
        for layer in mapinst.tmxdata.layers:
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
        instmap.fullspritegroup.add(groupc)
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

#detect vertical movement collision
    def vertmovecoll(self):

        player = self.player;
        player.applygravity()
        for sprite in self.currentmap.collidablegroup.sprites():
            if sprite.rect.colliderect(player.rect):
                if -player.physics.direction.y < 0:
                    player.rect.bottom = sprite.rect.top
                    player.physics.direction.y = 0;
                elif -player.physics.direction.y > 0:
                    player.rect.top = sprite.rect.bottom
                    player.physics.direction.y = 0;
        # THE REASON WHY I USE -player.physics.direction.y INSTEAD OF player.physics.direction.y
        #in pygame, the Y-axis is oriented from top to bottom,
        # so positive values in the Y-direction mean moving
        # down on the screen, while negative values mean moving up.


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


    def run(self):
        #Level
        self.scroller();
        self.updatetilepos(self.world_shift)

        #PLAYER
        self.player.update(self.currentmap)
        self.horizontalmovecoll()
        self.vertmovecoll()