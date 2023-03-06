"""
WorldData (dataclass)               : basic world information
GameTile (Sprite class)             : the background tiles, including platforms
GameTileAnimation (GameTile class)  : animated background tiles (flames, torches etc.)
GamePanel(class)                    : contans the player information for the screen - score, health etc.
"""

import pygame as pg
import logging
import random

from game_data.settings import *
from decor_and_effects import *
from game_functions import *

from game_tiles import GameTile, GameTileAnimation, MovingGameTile
from game_data.level_data import levels, GameAudio
from game_data.monster_data import known_monsters
from player import Player, PlayerInOut
from monsters import Monster, Projectile, Spell, Drop

from game_data.monster_data import arrow_damage

class Level():
    def __init__(self, surface, game_state) -> None:
        
        self.gs = game_state
        self.last_log = ''  # we do this to only log when something _new_ happens

        from game_data.animation_data import anim  # we do this late, as we need to have display() up first
        self.anim = anim

        # general setup
        self.screen = surface
        self.h_scroll = 0
        self.v_scroll = 0

        self.first_run = True   # we need to update all tile positions in the y-direction to scroll down to the player spawn point

        self.arrow_damage = arrow_damage

        self.last_stomp = 0  # used to time player's stomp shadows (effect)
        self.previous_vel_y = 0  # keeping track of player falling for dust effects
        
        # tile data for current level
        self.level_data = levels[self.gs.level_current]
        self.lvl_entry = (0,0)
        self.lvl_exit = (0,0)

        # audio for current level
        self.audio = GameAudio(self.gs.level_current)  # used here and sent to player on creation as well

        # Import all the tile PNGs
        self.terrain_tilesheet_list = import_tile_sheet_graphics(self.level_data['terrain_ts'])  # these are the new format tiles
        self.decorations_tile_list = import_tile_graphics('assets/tile/decorations/*.png')
        self.hazards_tile_list = import_tile_graphics('assets/tile/hazards/*.png')
        self.pickups_tile_list = import_tile_graphics('assets/tile/pickups/*.png')
        self.triggered_objects_tile_list = import_tile_graphics('assets/tile/trigger-objects/*.png')
        self.monsters_tile_list = import_tile_graphics('assets/tile/monsters/*.png')
        self.player_tile_list = import_tile_graphics('assets/tile/player/*.png')

        # messages 
        self.bubble_list = []

        # player entry and exit points
        player_in_out_layout = import_csv_layout(self.level_data['pos_player'])
        self.player_in_out_sprites = self.create_tile_group(player_in_out_layout,'pos_player')

        # terrain setup
        terrain_layout = import_csv_layout(self.level_data['pos_terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout,'pos_terrain')
        #self.terrain_surface = self.create_terrain_surface(terrain_layout)

        # decorations setup 
        decorations_layout = import_csv_layout(self.level_data['pos_decorations'])
        self.decorations_sprites = self.create_tile_group(decorations_layout,'pos_decorations')

        # hazards setup 
        hazards_layout = import_csv_layout(self.level_data['pos_hazards'])
        self.hazards_sprites = self.create_tile_group(hazards_layout,'pos_hazards')

        # pickups
        pickups_layout = import_csv_layout(self.level_data['pos_pickups'])
        self.pickups_sprites = self.create_tile_group(pickups_layout,'pos_pickups')

        # triggered_objects 
        self.out_portal_coordinates = None
        triggered_objects_layout = import_csv_layout(self.level_data['pos_triggered_objects'])
        self.triggered_objects_sprites = self.create_tile_group(triggered_objects_layout,'pos_triggered_objects')

        # monsters 
        monsters_layout = import_csv_layout(self.level_data['pos_monsters'])
        self.monsters_sprites = self.create_tile_group(monsters_layout,'pos_monsters')
        self.monsters_nearby = pg.sprite.Group()

        # ---> Composite map groups
        # group of all (potential) collision sprites for monsters - mostly terrain, but also things like doors, barriers and hazards
        self.collision_sprites = pg.sprite.Group()
        self.collision_sprites.add(self.terrain_sprites.sprites() + self.triggered_objects_sprites.sprites() + self.hazards_sprites.sprites())

        # ---> Sprites not loaded from the map (projectiles, spels, panels etc.)

        # projectiles (no animation variety)
        self.arrow_img = pg.image.load('assets/sprites/arrow.png').convert_alpha()
        self.projectile_sprites = pg.sprite.Group()

        # spells
        self.spell_sprites = pg.sprite.Group()

        # drops (keys, health potions etc.)
        self.drops_sprites = pg.sprite.Group()

        # load panel images 
        self.key_img = pg.image.load('assets/panel/key.png').convert_alpha()

        # sky
        self.background = ParallaxBackground(self.gs.level_current, self.screen)

        # environmental effects (leaves, snow etc.)
        self.gs.level_weather = self.level_data['environmental_effect']
        self.env_sprites = EnvironmentalEffects(self.level_data['environmental_effect'], self.screen)  # 'leaves' for lvl1
        
        self.weather_effets = Weather(self.gs.level_weather)
        
        # ambient audio
        if self.gs.level_weather:
            self.audio.ambient[self.gs.level_weather].set_volume(0.3)
            self.audio.ambient[self.gs.level_weather].play(loops=-1)

        # stomp self image shadows and effect
        self.stomp_shadows = pg.sprite.Group()
        self.stomp_effects = pg.sprite.GroupSingle()  # only one stomp effect at a time

        # player dust 
        self.effect_sprites = pg.sprite.Group()

        # information pop-ups
        self.info_sprites = pg.sprite.Group()

        # particle system
        self.particle_system = ParticleSystem()

        
        # player
        self.player = self.player_setup()
        self.player_sprites = pg.sprite.GroupSingle()
        self.player_sprites.add(self.player)

        

        # debugging
        logging.debug(f"Level created {levels[self.gs.level_current]['size_x']} by {levels[self.gs.level_current]['size_y']} tiles large, or {levels[self.gs.level_current]['size_x']*TILE_SIZE_SCREEN} by {levels[self.gs.level_current]['size_y']*TILE_SIZE_SCREEN} pixels")
  
    def _debug_show_state(self) -> None:
        """ DEBUG ZONE """
        if self.player.state['active'] == IDLE:
            pg.draw.rect(self.screen, (0,255,0), (SCREEN_WIDTH - 50,0,50,50))
        if self.player.state['active'] == JUMPING:
            pg.draw.rect(self.screen, (0,255,255), (SCREEN_WIDTH - 50,0,50,50))
        if self.player.state['active'] == ATTACKING:
            pg.draw.rect(self.screen, (255,0,0), (SCREEN_WIDTH - 50,0,50,50))
        if self.player.state['active'] == WALKING:
            pg.draw.rect(self.screen, (0,0,255), (SCREEN_WIDTH - 50,0,50,50))
        if self.player.state['active'] == DYING:
            pg.draw.rect(self.screen, (0,0,0), (SCREEN_WIDTH - 50,0,50,50))
        if self.player.state['active'] == CASTING:
            pg.draw.rect(self.screen, (255,255,0), (SCREEN_WIDTH - 50,0,50,50))
        if self.player.state['active'] == STOMPING:
            pg.draw.rect(self.screen, (255,0,255), (SCREEN_WIDTH - 50,0,50,50))

# --> Checking functions
    def check_arena_spawns(self) -> None:
        # Checks if player in the arena has requestd monster spawns
        if self.gs.level_current == 0 and len(self.gs.monster_spawn_queue):
            for count, monster in enumerate(self.gs.monster_spawn_queue):
                if monster < len(known_monsters) + 1:
                    try:
                        self.monsters_nearby.add(Monster(SCREEN_WIDTH * 0.8, SCREEN_HEIGHT * 0.8, self.screen, known_monsters[monster-1]))
                    except KeyError:
                        logging.error(f'Tried to call {known_monsters[monster-1]}')
                self.gs.monster_spawn_queue.pop(count)

    def check_player_stomp(self) -> None:
        if self.player.stomp_trigger is True and self.player.vel_y == 0:
            self.stomp_effects.add(LightEffect1(self.player.rects['hitbox'].centerx, self.player.rects['hitbox'].centery + 10))
            self.player.stomp_trigger = False
            self.player.stomp_counter = 0
            self.gs.game_slowmo = True
            # TODO add dust
        for sprite in self.stomp_effects.sprites():
            if sprite.done is True:
                sprite.kill()

    def check_player_dust(self) -> None:
        if self.player.vel_y > 0:
            self.previous_vel_y = self.player.vel_y
            
        if self.player.vel_y == 0 and self.previous_vel_y > STOMP_SPEED * 0.8 and not self.player.on_slope:
            width = 52
            height = 16
            self.dust_jump = GameTileAnimation(width, height, self.player.rects['hitbox'].centerx - width, self.player.rects['hitbox'].bottom - (height + 4), self.anim['effects']['dust-landing'])
            self.dust_jump.name = 'dust'
            self.dust_jump.animation.start_over()
            self.previous_vel_y = 0  # to avoid dupes
            self.effect_sprites.add(self.dust_jump)
        
        # Housekeeping
        for sprite in self.effect_sprites.sprites():
            if sprite.name == 'dust' and sprite.animation.on_last_frame:
                sprite.kill()
    
    def check_player_attack(self) -> None:
        for monster in self.monsters_nearby.sprites():
            # --> We check if the player is attacking and if the attack hits a monster
            if self.player.state['active'] == ATTACKING \
                and monster.state not in (DYING, DEAD) \
                and monster.invulnerable is False \
                and pg.Rect.colliderect(self.player.rects['attack'], monster.hitbox): 
                    # Add hit (blood) particles
                    self.particles_blood(monster.hitbox.centerx, monster.hitbox.centery, monster.data.blood_color, self.player.turned)
                    monster.data.hitpoints -= 1
                    logging.debug(f'{monster.data.monster} hit by player attack - hitpoints remaining: {monster.data.hitpoints}')

                    if monster.data.hitpoints == 0: # monster is dying
                        self.gs.player_score += monster.data.points_reward
                        self.gs.player_stomp_counter += 1
                        """ Adding drops from player death """
                        if monster.data.monster == 'skeleton-keybearer':
                            drop_key = Drop( monster.hitbox.centerx, monster.hitbox.centery - 25 , self.anim['pickups']['key'], turned = False, scale = 2, drop_type='key',)
                            self.drops_sprites.add(drop_key)
                            logging.debug(f'{monster.data.monster} dropped a key')
                            monster.state_change(DYING)  # we do this _after_ key drop, as the hitbox disappears when the mob enters DYING state
                        else:
                            monster.state_change(STUNNED, player_pos=self.player.rect.center, deadly=True)
                        

                    else:  # monster still has hitpoints left
                        monster.state_change(STUNNED, player_pos=self.player.rect.center)
                        self.player.rects['attack'] = pg.Rect(0,0,0,0)
                        self.player.state['next'] = IDLE

    def check_player_win(self) -> None:
        # Player sprite reaches goal tile
        if pg.sprite.spritecollide(self.player,self.player_in_out_sprites,False) \
            and pg.sprite.spritecollide(self.player,self.player_in_out_sprites,False)[0].inout == 'out':  # first colliding sprite
                logging.debug('WIN! Level complete')
                self.gs.level_complete = True

    def check_coll_player_hazard(self) -> None:
        # Player + hazard group collision 
        if pg.sprite.spritecollide(self.player.hitbox_sprite,self.hazards_sprites,False) and self.player.state['active'] not in (DYING, DEAD):
            self.player.hazard_damage(100, hits_per_second=10)
            self.bubble_list.append(BubbleMessage(self.screen, 'Ouch! Ouch!', 1000, 0, 'spikes', self.player))

    def check_coll_player_projectile(self) -> None:
    # Player + projectile collision (arrows etc.) AND player's attack collision (so attacking arrows in flight for example)
        if pg.sprite.spritecollide(self.player.hitbox_sprite,self.projectile_sprites,False) and self.player.state['active'] != DYING:
            for projectile in pg.sprite.spritecollide(self.player.hitbox_sprite,self.projectile_sprites,False):
                self.particles_blood(self.player.rects['hitbox'].centerx, self.player.rects['hitbox'].centery, RED, projectile.turned)  # add blood particles whne player is hit
                self.player.hit(self.arrow_damage, projectile.turned, self.terrain_sprites)
                projectile.kill()
        for projectile in self.projectile_sprites.sprites():
            # We can attack and destroy projectiles as well
            if self.player.state['active'] == ATTACKING \
            and pg.Rect.colliderect(self.player.rects['attack'], projectile.rect):
                    # play some sound # TODO
                    projectile.kill()

    def check_coll_player_spell(self) -> None:
        # Player + spell collision
        if pg.sprite.spritecollide(self.player.hitbox_sprite,self.spell_sprites,False) and self.player.state['active'] != DYING:
            for _ in pg.sprite.spritecollide(self.player,self.spell_sprites,False):
                self.player.hazard_damage(100, hits_per_second=2)
    
    def check_coll_player_pickup(self) -> None:
        # Animated objects pickup / collision
        if pg.sprite.spritecollide(self.player.hitbox_sprite,self.pickups_sprites,False) and self.player.state['active'] != DYING:
            for pickup in pg.sprite.spritecollide(self.player,self.pickups_sprites,False):
                if pickup.name == 'health potion':
                    self.audio.pickups['health'].play()
                    self.player.heal(500)
                    pickup.kill()
                if pickup.name == 'stomp potion':
                    self.audio.pickups['stomp'].play()
                    self.gs.player_stomp_counter = PLAYER_STOMP
                    pickup.kill()
                if pickup.name == 'mana potion':
                    self.audio.pickups['mana'].play()
                    self.player.mana += 100
                    pickup.kill()

    def check_coll_player_triggered_objects(self) -> None:
        if pg.sprite.spritecollide(self.player.hitbox_sprite,self.triggered_objects_sprites,False) and self.player.state['active'] != DYING:
            for sprite in pg.sprite.spritecollide(self.player,self.triggered_objects_sprites,False):
                if sprite.name in ('door-left', 'door-right', 'end-of-level'):
                        if any('key' in sublist for sublist in self.gs.player_inventory): # do we have key?
                            sprite.animation.frame_number = 0
                            self.bubble_list.append(BubbleMessage(self.screen, 'And that was the lock...', 3000, 0, 'exit', self.player))
                        else:
                            self.player.bounce(-10, 0, -self.player.turned, self.terrain_sprites)
                            self.bubble_list.append(BubbleMessage(self.screen, 'I\'m missing a key!', 3000, 0, 'exit', self.player))
                            #self.info_sprites.add(InfoPopup('Locked door', sprite.rect.centerx, sprite.rect.centery))
                elif sprite.name == 'chest':
                    # play some sound effect
                    sprite.animation.active = True
                elif sprite.name == 'IN portal':
                    self.audio.triggers['portal'].play()

                    #print(self.out_portal_coordinates)
                    self.player.destination = self.out_portal_coordinates

                elif sprite.name == 'OUT portal':
                    pass  # we ignore the out portals
                else:
                    logging.error(f'Triggered object "{sprite.name} not know - aborting...')
                    exit(1)

    def check_coll_player_drops(self) -> None:
    # Dropped objects pickup / collision
        if pg.sprite.spritecollide(self.player.hitbox_sprite,self.drops_sprites,False) and self.player.state['active'] != DYING:
            for drop in pg.sprite.spritecollide(self.player.hitbox_sprite,self.drops_sprites,False):
                if drop.drop_type == 'key':
                    self.gs.player_inventory.append(('key', self.key_img))  # inventory of items and their animations
                    self.audio.pickups['key'].play()
                    drop.kill()
                    self.bubble_list.append(BubbleMessage(self.screen, 'A key! All I need now is a lock.', 3000, 3000, 'key', self.player))
               
                logging.debug(f'PICKUP: {drop.drop_type}')
                logging.debug(f'Inventory: {self.gs.player_inventory}')   

    def check_coll_stomp_monster(self) -> None:
        # Mobs caught in stomp blast effect
        if self.stomp_effects.sprite:
            stomp_collision = pg.sprite.spritecollide(self.stomp_effects.sprite, self.monsters_nearby,False)
            if stomp_collision:
                for monster in stomp_collision:
                    if monster.state not in (DYING, DEAD) and pg.Rect.colliderect(self.stomp_effects.sprite.rect, monster.hitbox): 
                            monster.state_change(STUNNED, player_pos=self.player.rect.center, deadly=True)
                            self.gs.player_score += monster.data.points_reward
                            self.player.stomp_counter += 1
                            logging.debug(f'{monster.data.monster} killed by player stomp')

    def check_coll_player_monster(self) -> None:
        # Player + mobs group collision
        monster_collisions = pg.sprite.spritecollide(self.player.hitbox_sprite, self.monsters_nearby,False)
        if monster_collisions and self.player.state['active'] not in (DYING, STOMPING):
            for monster in monster_collisions:
                if monster.state not in (DYING, DEAD, STOMPING) \
                    and pg.Rect.colliderect(self.player.rects['hitbox'], monster.hitbox):
                        self.player.hit(100, monster.turned, self.terrain_sprites)  # bump player _away_ from monster

    def check_monsters(self) -> None:
        # Monsters can be up to several things, which we check for here
        now = pg.time.get_ticks()
        for monster in self.monsters_nearby.sprites():
            if monster.state not in (DYING , DEAD):  # only dealing with the living
                #  --> casting spells=
                if monster.cast_anim_list:
                    for spell in monster.cast_anim_list:
                        if spell[0] == 'fire':
                            x, y = spell[1:3]
                            self.spell_sprites.add(Spell(x,y, self.anim['fire']['fire-spell'], False, scale=1))
                    monster.cast_anim_list = []

                # --> detecting (or no longer detecting) the player and switch to/from ATTACK mode
                if pg.Rect.colliderect(self.player.rects['hitbox'], monster.rect_detect) and self.player.state['active'] not in (DYING, DEAD):
                    if monster.state == WALKING:
                        monster.state_change(ATTACKING)    
                else:  # Mob not detecting player
                    if monster.state == ATTACKING:
                        monster.state_change(WALKING)  # if we move out of range, the mob will stop attacking

                # --> attacking the player and hitting or not the player's hitbox (or launching arrow or not)                
                if pg.Rect.colliderect(self.player.rects['hitbox'], monster.rect_attack) and monster.state == ATTACKING and self.player.state['active'] != STOMPING:
                    if monster.data.attack_instant_damage:  
                        self.player.hit(monster.data.attack_damage, monster.turned, self.terrain_sprites)  # melee hit
                        self.particles_blood(self.player.rects['hitbox'].centerx, self.player.rects['hitbox'].centery, RED, monster.turned)  # add blood particles when player is hit
                    elif now - monster.last_arrow > monster.data.attack_delay:  # launching projectile 
                        arrow = Projectile(monster.hitbox.centerx, monster.hitbox.centery-10, self.arrow_img, turned = monster.turned, scale = 3) 
                        # We only add the arrow once the bow animation is complete (and we know we're ATTACKING, so attack anim is active)
                        if monster.animation.on_last_frame:
                            self.projectile_sprites.add(arrow)
                            monster.last_arrow = now


                



    def create_tile_group(self,layout,type) -> pg.sprite.Group:
        sprite_group = pg.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index,val in enumerate(row):
                if val != '-1':
                    # print(f'{row_index=} {col_index=}')  # DEBUG
                    # Calculate the on screen coordinates, given that width of each tile, which gives TILE_SIZE_SCREEN many tiles acriss the screen
                    x = col_index * TILE_SIZE_SCREEN
                    y = row_index * TILE_SIZE_SCREEN
                    bottom_pos = (1 + row_index) * (TILE_SIZE_SCREEN)  # this helps anchor sprites that are odd sizes, where we have to check they are on the ground
            

                    if type == 'pos_terrain':  
                        """ Loading terrain tiles
                            NOTE: there is really no limit to size - the program can accept any size of level,
                        """

                        tile_surface = self.terrain_tilesheet_list[int(val)]
                        
                        (x_size, y_size) = tile_surface.get_size()
                        if not x_size == y_size == TILE_SIZE:
                            logging.debug(f'Terrain tiles are of size {x_size}x{y_size}, but we have TILE_SIZE {TILE_SIZE} in settings')
                        
                        # Tile scaling - 1 is original size
                        x_size = x_size * 2
                        y_size = y_size * 2


                        if int(val) in self.level_data['moving_horiz']:  # TODO: for now only accepts single tiles
                            distance = 100
                            sprite = MovingGameTile(x_size ,y_size,x,y, 3,  distance,tile_surface)  # Moving platform
                        else:
                            slope = 0
                            slope_pos = None  # only used for multi-tile slopes where we need to know if it's the first or second tile
                            slope_tiles = self.level_data['sloping_tiles']
                            if int(val) in slope_tiles['down_in_1']:
                                slope = 1
                            if int(val) in slope_tiles['down_in_2']:
                                slope = 2
                                slope_pos = -1 # default, this tile is the left in the pair
                                if int(row[col_index-1]) in slope_tiles['down_in_2']:  # check if previous tile was first or if this tile is
                                    slope_pos = 1  # nope, there was another to our left
                            if int(val) in slope_tiles['up_in_1']:
                                slope = -1
                            if int(val) in slope_tiles['up_in_2']:
                                slope = -2
                                slope_pos = 1 # default, this tile is the right in the pair
                                if int(row[col_index+1]) in slope_tiles['up_in_2']:  # check if if tile to the right is same type, then this is the first
                                    slope_pos = -1
                            sprite = GameTile(x_size,y_size,x,y,tile_surface, slope=slope, slope_pos=slope_pos)  # Normal static terrain tiles
                        if int(val) not in self.level_data['solid_tiles']:  # Water mostly
                            sprite.solid = False
                        
                    if type == 'pos_decorations':
                        tile_surface = self.decorations_tile_list[int(val)]
                        (x_size, y_size) = tile_surface.get_size()
                        x_size = x_size * 2 + 3
                        y_size = y_size * 2 + 3
                        sprite = GameTile(x_size,y_size,x,y,tile_surface)
                        sprite.rect.bottom = bottom_pos

                    if type == 'pos_hazards':
                        tile_surface = self.hazards_tile_list[int(val)]
                        (x_size, y_size) = tile_surface.get_size()
                        x_size = x_size * 2 + 3
                        y_size = y_size * 2 + 3
                        if int(val) == 0:  # fire
                            sprite = GameTileAnimation(x_size, y_size,x,y, self.anim['fire']['fire-hazard'])
                        if int(val) == 1:  # spikes
                            sprite = GameTileAnimation(x_size, y_size,x,y, self.anim['spikes']['spike-trap'])
                        sprite.rect.bottom = bottom_pos
                        
                    if type == 'pos_pickups':
                        tile_surface = self.pickups_tile_list[int(val)]
                        (x_size, y_size) = tile_surface.get_size()
                        x_size = x_size * 2 + 3
                        y_size = y_size * 2 + 3
                        if int(val) == 0:  # health potion
                            sprite = GameTileAnimation(x_size, y_size,x,y, self.anim['pickups']['health-potion'])
                            sprite.name = 'health potion'
                        if int(val) == 1:  # stomp potion
                            sprite = GameTileAnimation(x_size, y_size,x,y, self.anim['pickups']['stomp-potion'])
                            sprite.name = 'stomp potion'
                        if int(val) == 2:  # mana potion
                            sprite = GameTileAnimation(x_size, y_size,x,y, self.anim['pickups']['mana-potion'])
                            sprite.name = 'mana potion'
                        

                        sprite.rect.bottom = bottom_pos
                        

                    if type == 'pos_triggered_objects':
                        try:
                            tile_surface = self.triggered_objects_tile_list[int(val)]
                        except IndexError:
                            logging.error(f'Triggered object with index {val} not recognized at position {col_index}, {row_index}, aborting...')
                            exit(1)
                        (x_size, y_size) = tile_surface.get_size()
                        x_size = x_size * 2 + 3
                        y_size = y_size * 2 + 3
                        if int(val) == 0:  # door at end of level
                            sprite = GameTileAnimation(x_size, y_size,x,y - 10 , self.anim['doors']['end-of-level'])
                            sprite.animation.active = False
                            sprite.name = 'enf-of-level'
                        if int(val) == 1:  # treasure chest
                            sprite = GameTileAnimation(x_size, y_size,x,y, self.anim['objects']['chest'])
                            sprite.animation.active = False
                            sprite.name = 'chest'
                            sprite.solid = False
                        if int(val) == 2:  # IN portal (teleports)
                            sprite = GameTileAnimation(x_size, y_size,x,y, self.anim['objects']['portal'])
                            sprite.animation.active = True
                            sprite.hidden = False  # we can link this to boss death later
                            sprite.name = 'IN portal'
                        if int(val) == 3:  # IN portal (teleports)
                            sprite = GameTileAnimation(x_size, y_size,x,y, self.anim['objects']['portal'])
                            sprite.animation.active = True
                            sprite.hidden = False  # we can link this to boss death later
                            sprite.name = 'OUT portal'
                            self.out_portal_coordinates = (x + TILE_SIZE//2, y + TILE_SIZE//2 )
                        if int(val) == 4:  # Door facing RIGHT
                            sprite = GameTileAnimation(x_size, y_size,x,y, self.anim['doors']['right-wood'])
                            sprite.animation.active = False
                            sprite.animation.frame_number = 1  # Closed
                            sprite.hidden = False  # we can link this to boss death later
                            sprite.name = 'door-right'
                        if int(val) == 5:  # Door facing LEFT
                            sprite = GameTileAnimation(x_size, y_size,x,y, self.anim['doors']['left-wood'])
                            sprite.animation.active = False
                            sprite.animation.frame_number = 1  # Closed
                            sprite.hidden = False  # we can link this to boss death later
                            sprite.name = 'door-left'
                            

                        sprite.rect.bottom = bottom_pos

                    if type == 'pos_monsters':
                        tile_surface = self.monsters_tile_list[int(val)]
                        if int(val) == 0:
                            sprite = Monster(x,y,tile_surface, 'beholder')
                            sprite.name = 'beholder'
                        elif int(val) == 1:
                            sprite = Monster(x,y,tile_surface, 'elven-archer')
                            sprite.name = 'elven-archer'
                        elif int(val) == 2:
                            sprite = Monster(x,y,tile_surface, 'skeleton-keybearer')
                            sprite.name = 'skeleton-keybearer'
                        else:
                            logging.error(f'Tile value {int(val)} for tile type "{type}" not recognized during level import')
                            exit(1)
                        
                    if type == 'pos_player':
                        _ = self.player_tile_list[int(val)]  # we don't draw the tiles, only used in map editor
                        if int(val) == 0:  # the level entrance tile
                            sprite = PlayerInOut(x, y, 'in')
                            self.lvl_entry = (x,y)
                        if int(val) == 1:  # the level exit tile
                            sprite = PlayerInOut(x, y, 'out')
                            self.lvl_exit = (x,y)

                    
                    try:
                        sprite_group.add(sprite)
                    except UnboundLocalError:
                        logging.error(f'Tile type "{type}" not recognized during level import')
                        exit(1)
        return sprite_group

# --> Effect funtions 
    def particles_blood(self, x, y, color, turned) -> None:
        direction = -1 if turned is True else 1
        for _ in range(50):   
            self.particle_system.add({
                'center': [x + random() * 30, y + random() * 30],
                'velocity': [random() * 10 * direction , random() * -10],
                'radius': random() * 5,
                'color': color
            })
                
    def show_bubbles(self) -> None:
        msg_types = []
        for bubble in self.bubble_list:
            if bubble.msg_type in msg_types or bubble.expired:  # we already have a bubble message of this type in the list, or it's expired
                self.bubble_list.remove(bubble)
            else:
                msg_types.append(bubble.msg_type)
                bubble.show()

# --> Main functions
    def player_setup(self) -> Player:
        player = Player(self.lvl_entry[0], self.lvl_entry[1], self.screen, self.audio, self.level_data, self.gs)
        logging.debug(f'Player spawned at ({self.lvl_entry[0]}, {self.lvl_entry[1]})')
        return player

    def run(self) -> None:
        """ 
        Runs the entire level
        """

        if self.first_run:
            self.v_scroll = - (self.player.world_y_pos - 600)  # we scroll the "world", including the player, to move the "camera"
            self.player.rects['player'].centery += self.v_scroll  # the player doesn't respond to self.v_scroll, so we need to update the vertical rect pos manually
            self.first_run = False

        # --> UPDATE BACKGROUND <---
        self.background.update(self.h_scroll)  # only scroll horizontally
        self.background.draw(self.screen)

        # --> PULL MONSTERS FROM ALL-MONSTER SPRITE GROUP, TO NEARBY MONSTERS SPRITE GROUP
        self.monsters_nearby = pg.sprite.Group()  # we empty every iteration
        self.monsters_nearby = self.monsters_sprites  # TODO: for later. for now we implemented proximity checks in the Monster class

        # --> UPDATE ALL SPRITE GROUPS <---

        # terrain
        self.terrain_sprites.update(self.h_scroll, self.v_scroll)
        self.terrain_sprites.draw(self.screen)
        #self.screen.blit(self.terrain_surface, (0,0))

        # decorations  
        self.decorations_sprites.update(self.h_scroll, self.v_scroll)
        self.decorations_sprites.draw(self.screen)

        # hazards  
        self.hazards_sprites.update(self.h_scroll, self.v_scroll)
        self.hazards_sprites.draw(self.screen)

        # pickups
        self.pickups_sprites.update(self.h_scroll, self.v_scroll)
        self.pickups_sprites.draw(self.screen)

        # drops
        self.drops_sprites.update(self.h_scroll, self.v_scroll)
        self.drops_sprites.draw(self.screen)

        # projectiles
        self.projectile_sprites.update(self.h_scroll, self.v_scroll, self.terrain_sprites)
        self.projectile_sprites.draw(self.screen)

        # spells
        self.spell_sprites.update(self.h_scroll, self.v_scroll)
        self.spell_sprites.draw(self.screen)

        # triggered_objects 
        self.triggered_objects_sprites.update(self.h_scroll, self.v_scroll)
        self.triggered_objects_sprites.draw(self.screen)

        # monsters 
        self.monsters_nearby.update(self.h_scroll, self.v_scroll, self.collision_sprites, self.player)
        self.monsters_nearby.draw(self.screen)

        # stomp shadows
        self.stomp_shadows.update(self.h_scroll, self.v_scroll)
        self.stomp_shadows.draw(self.screen)

        # stomp effect
        self.stomp_effects.update(self.h_scroll, self.v_scroll)
        self.stomp_effects.draw(self.screen)

        # dust
        self.effect_sprites.update(self.h_scroll, self.v_scroll)
        self.effect_sprites.draw(self.screen)
        
        # info pop-ups
        self.info_sprites.update(self.h_scroll, self.v_scroll)
        self.info_sprites.draw(self.screen)

        # entry and exit points
        self.player_in_out_sprites.update(self.h_scroll, self.v_scroll)  
        #self.player_in_out_sprites.draw(self.screen)  # normally we do not draw these, but good to have for debugging

        # environmental effects
        self.env_sprites.update(self.h_scroll, self.v_scroll)
        self.env_sprites.draw(self.screen)

        # particle system
        self.particle_system.update(self.h_scroll, self.v_scroll)
        self.particle_system.draw(self.screen)

        # weather
        self.weather_effets.update_and_draw(self.h_scroll, self.v_scroll, self.screen)

        # player 
        self.h_scroll, self.v_scroll = self.player.update(self.terrain_sprites)
        self.player_sprites.draw(self.screen)

        """ DEMO ZONE """
        # Testing player casting
        if len(self.player.cast_active):
            for cast in self.player.cast_active:
                cast.update(self.h_scroll, self.v_scroll)
                cast.draw(self.screen)
                if cast.done:
                    self.player.cast_active.remove(cast)
   
        if DEBUG_HITBOXES:
            pg.draw.rect(self.screen, (255,255,255), self.player.rect, 4 )  # self.rect - WHITE
            if self.player.rects['hitbox']:
                pg.draw.rect(self.screen, (128,128,128), self.player.rects['hitbox'], 2 )  # Hitbox rect (grey)
            if self.player.rects['attack']:
                pg.draw.rect(self.screen, (255, 0, 0), self.player.rects['attack'], 4 )  # attack rect - RED
            if self.player.collision_sprite.rect:
                pg.draw.rect(self.screen, ('#e75480'), self.player.collision_sprite.rect, 2 )  # Collsion rect - PINK

        # --> Check player condition and actions <--
        self.check_player_attack()
        self.check_player_stomp()
        self.check_player_dust()
        self.check_player_win()

        # --> Check collisions <--
        self.check_coll_player_hazard()
        self.check_coll_player_projectile()
        self.check_coll_player_spell()
        self.check_coll_player_pickup()
        self.check_coll_player_triggered_objects()
        self.check_coll_player_drops()
        self.check_coll_stomp_monster()  # we need this to be called before player/monster collision check
        self.check_coll_player_monster()

        # --> Check monster condition and actions <--
        self.check_monsters()  # this check mob detection + attack as well as player attack against all mobs

        # --> Check if we're in the arena and player has requested monster spawns
        self.check_arena_spawns() 
        
        # --> Check effects and particle system <--
        self.show_bubbles()
