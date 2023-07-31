# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import pygame, sys, os;
from pytmx.util_pygame import load_pygame;

#Plan: make a map class to do this spritegroup stuff and have 2 spritegroups for collidable and noncollidable sprites

print("Current Working Dir: ", os.getcwd())


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, tile_id, collidable):
        super().__init__(groups);
        self.image = surf;
        self.rect = self.image.get_rect(topleft = pos);
        self.tile_id = tile_id;
        self.collidable = collidable;


class Plr(pygame.sprite.Sprite):

    def __init__(self, plrpos, plrsurf):
        pygame.sprite.Sprite.__init__(self);
        self.image = plrsurf;
        self.rect = self.image.get_rect(topleft = plrpos);


cwd = str(os.getcwd());
maploc = cwd + '/Maps/testmap/testmappygame1.tmx';
darkmaploc = cwd + '/Maps/testmap/testmappygame2.tmx';
plrspriteloc = cwd + '/tiles/plrsprite.png'
print("my testmap loc: ", maploc);
print("darkmap: ", darkmaploc)

true = True;
false = False;

#====================code after pygame.init() below=====================


pygame.init();

screenwidth = 1200;
screenheight = 700;
screen = pygame.display.set_mode((screenwidth, screenheight));

tmxdata = load_pygame(maploc);
darktmxdata = load_pygame(darkmaploc);
spritegroup = pygame.sprite.Group();
collidablespritegroup = pygame.sprite.Group();

plrsprite = pygame.image.load(plrspriteloc);
plrx = 8;
plry = 3;
plr = Plr((plrx * 64, plry * 64), plrsprite)

running = true;
camxpos = 0
camypos = 0
camvelocity = 0.5
camonplayer = true

cooldown = 1000;  # cooldown is in MILLISECONDS
timelastpressed = 0;
lighttiles = [];
darktiles = [];
inittiles = false;
gametheme = "light"


def initializetiles():
    global inittiles;
    lightlayerindex = -1;
    darklayerindex = -1;
    if not inittiles:
        for layer in tmxdata.layers:
            lightlayerindex+=1;
            # print("layer.name: ", layer.name);
            # print("layer.index: ", lightlayerindex);

            for x,y,surf in layer.tiles():
                pos = (64*x, 64*y);
                props = tmxdata.get_tile_properties(x, y, lightlayerindex)
                tile_id = props["id"]
                collidable = "no"
                if ((tile_id >= 4 and tile_id <= 7) or tile_id == 19 or tile_id == 18):
                    collidable = "yes"

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
                lighttiles.append(Tile(**tile_info));

        for layer in darktmxdata.layers:
            darklayerindex+=1;
            # print("layer.name: ", layer.name);
            # print("layer.index: ", darklayerindex);

            for x,y,surf in layer.tiles():
                pos = (64*x, 64*y);
                props = darktmxdata.get_tile_properties(x, y, darklayerindex)
                tile_id = props["id"]
                collidable = "no"
                # print("props(""id""): ", props["id"])
                # print("props: ", props);
                if ((tile_id >= 4 and tile_id <= 7) or tile_id == 19 or tile_id == 18):
                    collidable = "yes"
                tile_info = {
                    "pos": pos,
                    "surf": surf,
                    "groups": spritegroup,
                    "tile_id": tile_id,
                    "collidable": collidable
                }

                darktiles.append(Tile(**tile_info));
                # print("pos: ", pos, " surf: ", surf, " groups: ", spritegroup, " tile_id: ", tile_id)
        spritegroup.empty();
        spritegroup.add(lighttiles);
        inittiles = true;


#changetomodenight is executed by pressing the "r" key.


def changetomodenight():
    global gametheme;
    global spritegroup;
    if gametheme == "light":
        gametheme = "dark";
        spritegroup.empty();
        spritegroup.add(darktiles);
        return;
    if gametheme == "dark":
        gametheme = "light";
        spritegroup.empty()
        spritegroup.add(lighttiles);


xpressedalready = false;

movable = true;


def keystrokechecker(cd): #cd is cooldown param
    key = pygame.key.get_pressed();
    timenow = pygame.time.get_ticks();
    global timelastpressed;
    global camonplayer;
    global camxpos;
    global camypos;
    global camxposinst;
    global camyposinst;
    global xpressedalready;
    global movable;
    if key[pygame.K_x] and timenow - timelastpressed >= cooldown: #press x to unlock camera
        if camonplayer == true:
            print("cam will now be in free mode");
            xpressedalready = true;
            camxposinst = camxpos;
            camyposinst = camypos;
        else:
            print("cam will pan on player")
            if xpressedalready:
                camxpos = camxposinst;
                camypos = camyposinst;
                # print ("pressed already!")
        camonplayer = not camonplayer;

        timelastpressed = timenow;
    if key[pygame.K_r]:
        if timenow - timelastpressed >= cooldown:
            changetomodenight();
            timelastpressed = timenow;

    if movable:
        if key[pygame.K_a]:
            camxpos+=camvelocity;
            # print("x: ", camxpos);
        if key[pygame.K_d]:
            camxpos-=camvelocity;
            # print("x: ", camxpos);
        if key[pygame.K_w]:
            camypos+=camvelocity;
            # print("y: ", camypos);
        if key[pygame.K_s]:
            camypos-=camvelocity;
            # print("y: ", camypos);

    if key[pygame.K_ESCAPE]:
        pygame.quit();
        sys.exit();


initializetiles();

plrsprite = pygame.image.load(plrspriteloc);

camoffsetxinst = 0;
camoffsetyinst = 0;
camxposinst = 0;
camyposinst = 0;


def updatescreenpos(camoffx, camoffy):
    global camoffsetxinst;
    global camoffsetyinst;
    for sprite in spritegroup:
        screen.blit(sprite.image, (sprite.rect.x + camoffx, sprite.rect.y + camoffy))
    if camonplayer:
        screen.blit(plr.image, (plr.rect.x, plr.rect.y))
        camoffsetxinst = camera_offset_x;
        camoffsetyinst = camera_offset_y;
    else:
        screen.blit(plr.image, (plr.rect.x + camoffx - camoffsetxinst, plr.rect.y + camoffy - camoffsetyinst))


# GAME LOOP BELOW


while running:
    keystrokechecker(cooldown);
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit();


    camera_offset_x = camxpos * 64
    camera_offset_y = camypos * 64
    screen.fill((255,255,255))

    updatescreenpos(camera_offset_x, camera_offset_y);
    # for tile in
    # if plr.rect.colliderect()

    pygame.display.update();



