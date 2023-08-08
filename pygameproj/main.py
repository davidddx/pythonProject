# # Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# import pygame, sys, os;
# from pytmx.util_pygame import load_pygame;
#
# #Plan: make a map class to do this spritegroup stuff and have 2 spritegroups for collidable and noncollidable sprites
#
# print("Current Working Dir: ", os.getcwd())
#
# true = True;
# false = False;
#
#
# class Map():
#     def __init__(self, collidablegroup, noncollidablegroup, tmxdata, fullspritegroup):
#         self.collidablegroup = collidablegroup;
#         self.noncollidablegroup = noncollidablegroup;
#         self.tmxdata = tmxdata;
#         self.fullspritegroup = fullspritegroup
#         # self.fullspritegroup = self.setfullspritegroup(collidablegroup, noncollidablegroup);
#         self.tilelist = []
#     # def setfullspritegroup(self, cgroup, noncgroup):
#     #     spritegroup = pygame.sprite.Group();
#     #     for atile in cgroup:
#     #         spritegroup.add(atile);
#     #     for atile in noncgroup:
#     #         spritegroup.add(atile);
#     #     return spritegroup
#     def printallproperties(self):
#         print("tilelist", self.tilelist);
#         print("fullspritegroup", self.fullspritegroup);
#         print("collidablegroup", self.collidablegroup);
#         print("noncollidablegroup", self.noncollidablegroup);
#         print("tmxdata", self.tmxdata);
#
# class Tile(pygame.sprite.Sprite):
#     def __init__(self, pos, surf, groups, tile_id, collidable):
#         super().__init__(groups);
#         self.image = surf;
#         self.rect = self.image.get_rect(topleft = pos);
#         self.tile_id = tile_id;
#         self.collidable = collidable;
#
# class Plr(pygame.sprite.Sprite):
#     def __init__(self, plrpos, plrsurf):
#         pygame.sprite.Sprite.__init__(self);
#         self.image = plrsurf;
#         self.rect = self.image.get_rect(topleft = plrpos);
#         self.velocity = 0;
#         self.acceleration = 0;
#         self.jumpheight = 0;
#         self.gravity = 0;
#         self.onground = true;
#
#     def setplrphysics(self, acceleration, jumpheight, gravity, onground):
#         self.acceleration = acceleration;
#         self.jumpheight = jumpheight;
#         self.gravity = gravity;
#         self.onground = onground;
#
#
#
#
# cwd = str(os.getcwd());
# lightmaploc = cwd + '/Maps/testmap/testmappygame1.tmx';
# darkmaploc = cwd + '/Maps/testmap/testmappygame2.tmx';
# plrspriteloc = cwd + '/tiles/plrsprite.png'
# print("my testmap loc: ", lightmaploc);
# print("darkmap: ", darkmaploc)
#
#
# #====================code after pygame.init() below=====================
#
#
# pygame.init();
#
# clock = pygame.time.Clock()
#
# screenwidth = 1200;
# screenheight = 700;
# screen = pygame.display.set_mode((screenwidth, screenheight));
#
# plrx = 8;
# plry = 3;
# plr = Plr(plrpos = (plrx * 64, plry * 64), plrsurf = pygame.image.load(plrspriteloc))
# plr.setplrphysics(acceleration = 0.05, jumpheight = -10, gravity = 0.3, onground = false)
#
# camxpos = 0
# camypos = 0
# camvelocity = 0.5
# camonplayer = true
# cooldown = 1000;  # cooldown is in MILLISECONDS
# timelastpressed = 0;
#
# lighttmxdata = load_pygame(lightmaploc);
# darktmxdata = load_pygame(darkmaploc);
# lightmap = Map(collidablegroup = pygame.sprite.Group(), noncollidablegroup = pygame.sprite.Group(), tmxdata = lighttmxdata, fullspritegroup = pygame.sprite.Group());
# darkmap = Map(collidablegroup = pygame.sprite.Group(), noncollidablegroup = pygame.sprite.Group(), tmxdata = darktmxdata, fullspritegroup = pygame.sprite.Group());
#
# def initializetiles(mapinst):
#     instmap = mapinst
#     layerindex = -1;
#     groupc = []
#     groupn = []
#     spritegroup = mapinst.fullspritegroup;
#     for layer in mapinst.tmxdata.layers:
#         layerindex+=1;
#         # print("layer.name: ", layer.name);
#         # print("layer.index: ", lightlayerindex);
#
#         for x,y,surf in layer.tiles():
#             pos = (64*x, 64*y);
#             props = mapinst.tmxdata.get_tile_properties(x, y, layerindex)
#             tile_id = props["id"]
#             collidable = "no"
#             if ((tile_id >= 4 and tile_id <= 7) or tile_id == 19 or tile_id == 18):
#                 collidable = "yes"
#
#             print("props: ", props);
#             print("props(""id""): ", props["id"])
#             # print("collidable?: ", collidable)
#             tile_info = {
#                 "pos": pos,
#                 "surf": surf,
#                 "groups": spritegroup,
#                 "tile_id": tile_id,
#                 "collidable": collidable
#             }
#             tileinstance = Tile(**tile_info)
#             if collidable == "yes":
#                 groupc.append(tileinstance)
#             else:
#                 groupn.append(tileinstance)
#
#             instmap.tilelist.append(tileinstance);
#     instmap.noncollidablegroup.add(groupn);
#     instmap.collidablegroup.add(groupc);
#     instmap.fullspritegroup.add(groupn);
#     instmap.fullspritegroup.add(groupc)
#     return instmap;
#
# def collisionchecker(plrr, map, camoffx, camoffy):
#     fx = 3
#     collgroup = map.collidablegroup
#     # print("plrrectx", plrr.rect.x, " plr.rect.y", plrr.rect.y);
#     for sprite in collgroup:
#         sprite.rect.x+=camoffx;
#         sprite.rect.y+=camoffy - plr.rect.y;
#         # print("spriterectx + camoffx: ", sprite.rect.x + camoffx);
#         # print("spriterecty + camoffy: ", sprite.rect.y + camoffy);
#     if pygame.sprite.spritecollideany(plrr, collgroup):
#         print("collided")
#         plr.rect.y -= plr.velocity;
#         plr.velocity = 0;
#         plr.onground = true;
#     for sprite in collgroup:
#         sprite.rect.x = sprite.rect.x - camoffx;
#         sprite.rect.y = sprite.rect.y - (camoffy - plr.rect.y);
#
# #changetomodenight is executed by pressing the "r" key.
#
# def changemap(currmap):
#     if currmap == lightmap:
#         currmap = darkmap;
#         return currmap;
#     else:
#         currmap = lightmap;
#         return currmap;
#
# xpressedalready = false;
# movable = true;
#
# def keystrokechecker(cd): #cd is cooldown param
#     key = pygame.key.get_pressed();
#     timenow = pygame.time.get_ticks();
#     global timelastpressed;
#     global camonplayer;
#     global camxpos;
#     global camypos;
#     global camxposinst;
#     global camyposinst;
#     global xpressedalready;
#     global movable;
#     global currmap;
#     global plr;
#     if key[pygame.K_x] and timenow - timelastpressed >= cooldown: #press x to unlock camera
#         if camonplayer == true:
#             print("cam will now be in free mode");
#             xpressedalready = true;
#             camxposinst = camxpos;
#             camyposinst = camypos;
#             movable = false;
#         else:
#             print("cam will pan on player")
#             if xpressedalready:
#                 camxpos = camxposinst;
#                 camypos = camyposinst;
#                 movable = true;
#                 # print ("pressed already!")
#         camonplayer = not camonplayer;
#
#         timelastpressed = timenow;
#     if key[pygame.K_r]:
#         if timenow - timelastpressed >= cooldown:
#             currmap = changemap(currmap);
#             timelastpressed = timenow;
#
#     if movable:
#         if key[pygame.K_a]:
#             camxpos+=camvelocity;
#             # print("x: ", camxpos);
#         if key[pygame.K_d]:
#             camxpos-=camvelocity;
#             # print("x: ", camxpos);
#         if key[pygame.K_w]:
#             if plr.onground:
#                 camypos += camvelocity;
#                 plr.velocity = plr.jumpheight;
#                 plr.onground = false
#             # print("y: ", camypos);
#         # if key[pygame.K_s]:
#         #     camypos-=camvelocity;
#         #     # print("y: ", camypos);
#
#     if key[pygame.K_ESCAPE]:
#         pygame.quit();
#         sys.exit();
#
#
#
# lightmap = initializetiles(lightmap);
#
# darkmap = initializetiles(darkmap);
# plrsprite = pygame.image.load(plrspriteloc);
#
# camoffsetxinst = 0;
# camoffsetyinst = 0;
# camxposinst = 0;
# camyposinst = 0;
#
#
# def updatescreenpos(camoffx, camoffy, thismap):
#     global camoffsetxinst;
#     global camoffsetyinst;
#     spritegroup = thismap.fullspritegroup;
#
#     for sprite in spritegroup:
#         screen.blit(sprite.image, (sprite.rect.x + camoffx, sprite.rect.y + camoffy - plr.rect.y))
#     if camonplayer:
#         plrgrav = plr.gravity
#         if not plr.onground:
#             plr.velocity += plrgrav + plr.acceleration;
#         else:
#             print("onground = false")
#             plr.velocity += plrgrav;
#
#         plr.rect.y += plr.velocity;
#         screen.blit(plr.image, (plr.rect.x + camoffx, plr.rect.y + camoffy));
#         camoffsetxinst = camera_offset_x;
#         camoffsetyinst = camera_offset_y;
#     else:
#         screen.blit(plr.image, (plr.rect.x + camoffx - camoffsetxinst, plr.rect.y + camoffy - camoffsetyinst))
#
#
#
#
# # GAME LOOP BELOW
# camera_offset_x = 0;
# camera_offset_y = 0;
# currmap = darkmap
# # lightmap.printallproperties();
# # darkmap.printallproperties();
# # currmap.printallproperties();
# running = true;
# while running:
#     clock.tick(60)
#     collisionchecker(plr, lightmap, camera_offset_x, camera_offset_y);
#     keystrokechecker(cooldown);
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             pygame.quit();
#             sys.exit();
#     camera_offset_x = camxpos * 64;
#     camera_offset_y = camypos * 64;
#     screen.fill((0,0,0));
#
#     updatescreenpos(camera_offset_x, camera_offset_y, currmap);
#
#     pygame.display.update();

#====================================================New Code Version===========================================

# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import pygame, sys, os, pymunk;
from settings import *
from classes import *
from pytmx.util_pygame import load_pygame;



print("Current Working Dir: ", os.getcwd())






#====================code after pygame.init() below=====================


pygame.init();

clock = pygame.time.Clock()
screen = pygame.display.set_mode((screenwidth, screenheight));
lighttmxdata = load_pygame(lightmaploc);
darktmxdata = load_pygame(darkmaploc);
lightmap = Map(collidablegroup = pygame.sprite.Group(), noncollidablegroup = pygame.sprite.Group(), tmxdata = lighttmxdata, fullspritegroup = pygame.sprite.Group());
darkmap = Map(collidablegroup = pygame.sprite.Group(), noncollidablegroup = pygame.sprite.Group(), tmxdata = darktmxdata, fullspritegroup = pygame.sprite.Group());



plrx = 8;
plry = 3;
plr = Plr(plrpos = (plrx * 64, plry * 64), plrsurf = pygame.image.load(plrspriteloc))
current_level = Level(currentmap = lightmap, plr = plr);
current_map = current_level.currentmap


camxpos = 0
camypos = 0
camvelocity = 0.5
camonplayer = true
cooldown = 1000;  # cooldown is in MILLISECONDS
timelastpressed = 0;

#changetomodenight is executed by pressing the "r" key.
camoffsetxinst = 0;
camoffsetyinst = 0;
camxposinst = 0;
camyposinst = 0;


def updatescreenpos(thismap):
    spritegroup = thismap.fullspritegroup;

    for sprite in spritegroup:
        screen.blit(sprite.image, (sprite.rect.x, sprite.rect.y - 64*6))

    screen.blit(plr.image, (plr.rect.x, plr.rect.y - 64*6));




# GAME LOOP BELOW
# lightmap.printallproperties();
# darkmap.printallproperties();
# currmap.printallproperties();
running = true;
while running:
    clock.tick(60)
    # plr.update(current_map)
    current_level.run()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit();
    screen.fill((0,0,0));

    updatescreenpos(current_map);

    pygame.display.update();


