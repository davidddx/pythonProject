import os

#pre Runtime
true = True
false = False
screenwidth = 1400;
screenheight = 900;
cwd = str(os.getcwd());
lightmaploc = cwd + '/Maps/testmap/testmappygame1.tmx';
darkmaploc = cwd + '/Maps/testmap/testmappygame2.tmx';
plrspriteloc = cwd + '/tiles/plrsprite.png'
enemyspriteloc = cwd + '/tiles/EnemySprite.png'
print("my testmap loc: ", lightmaploc);
print("darkmap: ", darkmaploc);
