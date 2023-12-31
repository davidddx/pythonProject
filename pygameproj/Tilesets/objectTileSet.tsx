<?xml version="1.0" encoding="UTF-8"?>
<tileset version="1.10" tiledversion="1.10.2" name="objectTileSet" tilewidth="512" tileheight="256" tilecount="9" columns="0">
 <grid orientation="orthogonal" width="1" height="1"/>
 <tile id="2" type="Door">
  <properties>
   <property name="backgroundtype" value="zero"/>
   <property name="name" value="door"/>
  </properties>
  <image width="192" height="256" source="../tiles/door.png"/>
 </tile>
 <tile id="3" type="OutOfBounds">
  <properties>
   <property name="name" value="OutOfBounds"/>
  </properties>
  <image width="512" height="128" source="../tiles/OutOfBounds.png"/>
 </tile>
 <tile id="4" type="plrspawner">
  <properties>
   <property name="name" value="plrspawn"/>
  </properties>
  <image width="256" height="256" source="../tiles/PlrSpawnPoint.png"/>
 </tile>
 <tile id="5" type="enemyspawner">
  <properties>
   <property name="name" value="BlueEnemySpawner"/>
  </properties>
  <image width="128" height="128" source="../tiles/BlueEnemySpawner.png"/>
 </tile>
 <tile id="6" type="enemyspawner">
  <properties>
   <property name="name" value="RedEnemySpawner"/>
  </properties>
  <image width="128" height="128" source="../tiles/RedEnemySpawner.png"/>
 </tile>
 <tile id="7" type="enemyspawner">
  <properties>
   <property name="name" value="GreenEnemySpawner"/>
  </properties>
  <image width="128" height="128" source="../tiles/useAsTiledSpawners/greenenemyspawner.png"/>
 </tile>
 <tile id="8" type="enemyspawner">
  <properties>
   <property name="name" value="BlackEnemySpawner"/>
  </properties>
  <image width="128" height="128" source="../tiles/useAsTiledSpawners/camoenemyspawner.png"/>
 </tile>
 <tile id="9" type="enemyspawner">
  <properties>
   <property name="name" value="PurpleEnemySpawner"/>
  </properties>
  <image width="128" height="128" source="../tiles/useAsTiledSpawners/purpleenemyspawner.png"/>
 </tile>
 <tile id="10" type="enemyspawner">
  <properties>
   <property name="name" value="GrayEnemySpawner"/>
  </properties>
  <image width="128" height="128" source="../tiles/useAsTiledSpawners/grayenemyspawner.png"/>
 </tile>
</tileset>
