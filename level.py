"""
WorldData (dataclass)               : basic world information
GameTile (Sprite class)             : the background tiles, including platforms
GameTileAnimation (GameTile class)  : animated background tiles (flames, torches etc.)
GamePanel(class)                    : contans the player information for the screen - score, health etc.
"""


import pygame
import logging
from random import random

from settings import *

from engine import import_csv_layout, import_tile_graphics, import_tile_sheet_graphics
from game_tiles import GameTile, GameTileAnimation, MovingGameTile
from level_data import levels, GameAudio
from player import Player, PlayerInOut
from monsters import Monster, Projectile, Spell, Drop
from decor_and_effects import ParallaxBackground, EnvironmentalEffects, BubbleMessage, LightEffect1, ParticleSystem
from monster_data import arrow_damage

class Level():
    def __init__(self,current_level,surface, health_max) -> None:
        logging.basicConfig(level=logging.DEBUG)
        self.last_log = ''  # we do this to only log when something _new_ happens

        # TESTING
        self.runoncetestflag = False

        from animation_data import anim  # we do this late, as we need to have display() up first
        self.anim = anim

        # general setup
        self.current_level = current_level
        self.level_complete = False
        self.screen = surface
        self.scroll = 0
        self.current_x = None

        self.arrow_damage = arrow_damage

        self.last_stomp = 0  # used to time player's stomp shadows (effect)
        self.previous_vel_y = 0  # keeping track of player falling for dust effects
        
        # tile data for current level
        level_data = levels[self.current_level]
        self.lvl_entry = (0,0)
        self.lvl_exit = (0,0)

        self.player_score = 0
        self.player_inventory = []
        self.health_max = health_max

        # audio for current level
        sounds = GameAudio(self.current_level)
        self.fx_key_pickup = sounds.key_pickup_fx
        self.fx_health_pickup = sounds.health_pickup_fx
        self.fx_player_stomp = sounds.player['stomp']
        self.fx_key_pickup.set_volume(0.5)
        self.fx_health_pickup.set_volume(0.5)
        self.fx_player_stomp.set_volume(0.5)

        # Import all the tile PNGs
        self.terrain_tile_list = import_tile_sheet_graphics('assets/spritesheets/tiles/terrain_tilesheet.png')
        self.decorations_tile_list = import_tile_graphics('assets/tile/decorations/*.png')
        self.hazards_tile_list = import_tile_graphics('assets/tile/hazards/*.png')
        self.pickups_tile_list = import_tile_graphics('assets/tile/pickups/*.png')
        self.triggered_objects_tile_list = import_tile_graphics('assets/tile/trigger-objects/*.png')
        self.monsters_tile_list = import_tile_graphics('assets/tile/monsters/*.png')
        self.player_tile_list = import_tile_graphics('assets/tile/player/*.png')

        # messages 
        self.bubble_list = []

        # player entry and exit points
        player_in_out_layout = import_csv_layout(level_data['player'])
        self.player_in_out_sprites = self.create_tile_group(player_in_out_layout,'player')

        # terrain setup
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout,'terrain')

        # decorations setup 
        decorations_layout = import_csv_layout(level_data['decorations'])
        self.decorations_sprites = self.create_tile_group(decorations_layout,'decorations')

        # hazards setup 
        hazards_layout = import_csv_layout(level_data['hazards'])
        self.hazards_sprites = self.create_tile_group(hazards_layout,'hazards')

        # pickups
        pickups_layout = import_csv_layout(level_data['pickups'])
        self.pickups_sprites = self.create_tile_group(pickups_layout,'pickups')

        # triggered_objects 
        triggered_objects_layout = import_csv_layout(level_data['triggered_objects'])
        self.triggered_objects_sprites = self.create_tile_group(triggered_objects_layout,'triggered_objects')

        # monsters 
        monsters_layout = import_csv_layout(level_data['monsters'])
        self.monsters_sprites = self.create_tile_group(monsters_layout,'monsters')

        # ---> Sprites not loaded from the map (projectiles, spels, panels etc.)

        # projectiles (no animation variety)
        self.arrow_img = pygame.image.load('assets/spritesheets/spells/arrow.png').convert_alpha()
        self.projectile_sprites = pygame.sprite.Group()

        # spells
        self.spell_sprites = pygame.sprite.Group()

        # drops (keys, health potions etc.)
        self.drops_sprites = pygame.sprite.Group()

        # load panel images 
        self.key_img = pygame.image.load('assets/panel/key.png').convert_alpha()

        # sky
        self.background = ParallaxBackground(self.current_level, self.screen)

        # environmental effects (leaves, snow etc.)
        self.env_sprites = EnvironmentalEffects(level_data['environmental_effect'], self.screen)  # 'leaves' for lvl1

        # stomp self image shadows and effect
        self.stomp_shadows = pygame.sprite.Group()
        self.stomp_effects = pygame.sprite.GroupSingle()  # only one stomp effect at a time

        # dust effects 
        self.dust_sprites = pygame.sprite.Group()

        # particle system
        self.particle_system = ParticleSystem()
        
        # player
        self.player = self.player_setup()
        self.player_sprites = pygame.sprite.GroupSingle()
        self.player_sprites.add(self.player)

        
    def _debug_show_state(self) -> None:
        """ DEBUG ZONE """
        if self.player.state['active'] == IDLE:
            pygame.draw.rect(self.screen, (0,255,0), (SCREEN_WIDTH - 50,0,50,50))
        if self.player.state['active'] == JUMPING:
            pygame.draw.rect(self.screen, (0,255,255), (SCREEN_WIDTH - 50,0,50,50))
        if self.player.state['active'] == ATTACKING:
            pygame.draw.rect(self.screen, (255,0,0), (SCREEN_WIDTH - 50,0,50,50))
        if self.player.state['active'] == WALKING:
            pygame.draw.rect(self.screen, (0,0,255), (SCREEN_WIDTH - 50,0,50,50))
        if self.player.state['active'] == DYING:
            pygame.draw.rect(self.screen, (0,0,0), (SCREEN_WIDTH - 50,0,50,50))
        if self.player.state['active'] == CASTING:
            pygame.draw.rect(self.screen, (255,255,0), (SCREEN_WIDTH - 50,0,50,50))
        if self.player.state['active'] == STOMPING:
            pygame.draw.rect(self.screen, (255,0,255), (SCREEN_WIDTH - 50,0,50,50))

    def create_tile_group(self,layout,type) -> pygame.sprite.Group:
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index,val in enumerate(row):
                if val != '-1':
                    # print(f'{row_index=} {col_index=}')  # DEBUG
                    x = col_index * TILE_SIZE_SCREEN
                    y = row_index * TILE_SIZE_SCREEN
                    bottom_pos = (1 + row_index) * (TILE_SIZE_SCREEN)  # this helps anchor sprites that are odd sizes, where we have to check they are on the ground
            

                    if type == 'terrain':  
                        list_of_solid_terrain = [0,1,2,3,4,5,6,7,8,11]  # only these terrain tiles will hold monsters and player up
                        list_of_moving_platforms = [11]

                        tile_surface = self.terrain_tile_list[int(val)]
                        (x_size, y_size) = tile_surface.get_size()
                        # As we need to scale sprites mostly 32x32px into our screen size, we need the following calculation:
                        # The allows us non-rectangular sprites, as long as they are a multiple of 32 in both directions
                        x_size = x_size * 2 + 3
                        y_size = y_size * 2 + 3
                        distance = 150
                        if int(val) in list_of_moving_platforms:
                            # We take two of the existing tiles and combine them into one:
                            img_left = self.terrain_tile_list[6]
                            img_right = self.terrain_tile_list[8]
                            img_comb = pygame.Surface((img_left.get_width() + img_right.get_width(), img_left.get_height()), pygame.SRCALPHA)

                            # Blit the first two surfaces onto the third.
                            img_comb.blit(img_left, (0, 0))
                            img_comb.blit(img_right, (img_left.get_width(), 0))

                            sprite = MovingGameTile(x_size * 2 ,y_size,x,y, 3,  distance,img_comb)  # Moving platform
                        else:
                            sprite = GameTile(x_size,y_size,x,y,tile_surface)  # Normal static terrain tiles
                        
                        if int(val) not in list_of_solid_terrain:  # Water mostly
                            sprite.solid = False
                        
                        
                    if type == 'decorations':
                        tile_surface = self.decorations_tile_list[int(val)]
                        (x_size, y_size) = tile_surface.get_size()
                        x_size = x_size * 2 + 3
                        y_size = y_size * 2 + 3
                        sprite = GameTile(x_size,y_size,x,y,tile_surface)
                        sprite.rect.bottom = bottom_pos

                    if type == 'hazards':
                        tile_surface = self.hazards_tile_list[int(val)]
                        (x_size, y_size) = tile_surface.get_size()
                        x_size = x_size * 2 + 3
                        y_size = y_size * 2 + 3
                        if int(val) == 0:  # fire
                            sprite = GameTileAnimation(x_size, y_size,x,y, self.anim['fire']['fire-hazard'])
                        if int(val) == 1:  # spikes
                            sprite = GameTileAnimation(x_size, y_size,x,y, self.anim['spikes']['spike-trap'])
                        sprite.rect.bottom = bottom_pos
                        
                    if type == 'pickups':
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
                        

                    if type == 'triggered_objects':
                        tile_surface = self.triggered_objects_tile_list[int(val)]
                        (x_size, y_size) = tile_surface.get_size()
                        x_size = x_size * 2 + 3
                        y_size = y_size * 2 + 3
                        if int(val) == 0:  # door at end of level
                            sprite = GameTileAnimation(x_size, y_size,x,y - 10 , self.anim['doors']['end-of-level'])
                            sprite.animation.active = False
                        sprite.rect.bottom = bottom_pos

                    if type == 'monsters':
                        tile_surface = self.monsters_tile_list[int(val)]
                        if int(val) == 0:  # minotaur
                            sprite = Monster(x,y,tile_surface, 'minotaur')
                        if int(val) == 1:  # elven-archer
                            sprite = Monster(x,y,tile_surface, 'elven-archer')
                        if int(val) == 2:  # skeleton-boss
                            sprite = Monster(x,y,tile_surface, 'skeleton-boss')
                        if int(val) == 3:  # elven-caster
                            sprite = Monster(x,y,tile_surface, 'elven-caster')
                        if int(val) == 4:  # elven-caster
                            sprite = Monster(x,y,tile_surface, 'beholder')
                        
                    if type == 'player':
                        _ = self.player_tile_list[int(val)]  # we don't draw the tiles, only used in map editor
                        if int(val) == 0:  # the level entrance tile
                            sprite = PlayerInOut(x, y, 'in')
                            self.lvl_entry = (x,y)
                        if int(val) == 1:  # the level exit tile
                            sprite = PlayerInOut(x, y, 'out')
                            self.lvl_exit = (x,y)

                    sprite_group.add(sprite)
        return sprite_group
    

  
    def player_setup(self) -> None:
        player = Player(self.lvl_entry[0], self.lvl_entry[0], self.screen, self.health_max)
        return player


    def check_player_stomp(self) -> None:
        if self.player.stomp_trigger == True and self.player.vel_y == 0:
            self.stomp_effects.add(LightEffect1(self.player.rects['hitbox'].centerx, self.player.rects['hitbox'].centery + 10))
            self.player.stomp_trigger = False
            self.player.stomp_counter = 0
            # TODO add dust
        for sprite in self.stomp_effects.sprites():
            if sprite.done == True:
                sprite.kill()

    def check_player_dust(self) -> None:
        if self.player.vel_y > 0:
            self.previous_vel_y = self.player.vel_y    
            
        if self.player.vel_y == 0 and self.previous_vel_y > (0.5 + 15):
            width = 52
            height = 16
            self.dust_jump = GameTileAnimation(width, height, self.player.rects['hitbox'].centerx - width, self.player.rects['hitbox'].bottom - (height + 4), self.anim['effects']['dust-landing'])
            self.dust_jump.animation.start_over()
            self.dust_sprites.add(self.dust_jump)
        
        # Housekeeping
        for sprite in self.dust_sprites.sprites():
            if sprite.animation.on_last_frame:
                sprite.kill()


    # --> CHECK ALL COLLISIONS <--
    # Note: use pygame.sprite.spritecollide() for sprite against group with low precision
    #       use pygame.Rect.colliderect() to compare two rects (high precision hitboxes intead of sprite)
    
    def check_player_attack(self) -> None:
        for monster in self.monsters_sprites.sprites():
            # --> We check if the player is attacking and if the attack hits a monster
            if self.player.state['active'] == ATTACKING and monster.state not in (DYING, DEAD) and monster.invulnerable == False:
                # Check if mob hit
                if pygame.Rect.colliderect(self.player.rects['attack'], monster.hitbox): 
                    # Add hit (blood) particles
                    self.particles_blood(monster.hitbox.centerx, monster.hitbox.centery, monster.data.blood_color, self.player.turned)
                    monster.data.hitpoints -= 1
                    logging.debug(f'{monster.data.monster} hit by player attack - hitpoints remaining: {monster.data.hitpoints}')
                    if self.player.turned:
                        direction = - 1
                    else:
                        direction = 1

                    if monster.data.hitpoints == 0: # monster is dying
                        self.player_score += monster.data.points_reward
                        self.player.stomp_counter += 1
                        """ Adding drops from player death """
                        # skeleton-boss is a key carrier
                        if monster.data.monster == 'skeleton-boss':
                            drop_key = Drop( monster.hitbox.centerx, monster.hitbox.centery - 25 , self.anim['pickups']['key'], turned = False, scale = 2, drop_type='key',)
                            self.drops_sprites.add(drop_key)
                            logging.debug(f'{monster.data.monster} dropped a key')
                        monster.state_change(DYING)  # we do this _after_ key drop, as the hitbox disappears when the mob enters DYING state

                    else:  # monster still has hitpoints left
                        monster.rect.centerx += 20 * (monster.data.speed_attacking + 1) * direction  # small bump back
                        monster.invulnerable = True
                        monster.inv_start = pygame.time.get_ticks()
                        self.player.rects['attack'] = pygame.Rect(0,0,0,0)  
                        # BLINK WHITE OR RED TODO
                        monster.state = WALKING
                        monster.state_change(ATTACKING)


    def check_player_win(self) -> None:
        # Player sprite reaches goal tile
        if pygame.sprite.spritecollide(self.player,self.player_in_out_sprites,False):
            if pygame.sprite.spritecollide(self.player,self.player_in_out_sprites,False)[0].inout == 'out':  # first colliding sprite
                logging.debug('WIN! Level complete')
                self.level_complete = True

    def check_player_fallen_off(self) -> None:
        if self.player.rects['player'].top > SCREEN_HEIGHT:
            self.player.health_current = 0
            self.player.state['active'] = DEAD  # insta-kill! 
            logging.debug('Oooops! Player fell off')


    def check_coll_player_hazard(self) -> None:
        # Player + hazard group collision 
        if pygame.sprite.spritecollide(self.player.hitbox_sprite,self.hazards_sprites,False) and self.player.state['active'] != DYING:
            self.player.hazard_damage(100, hits_per_second=10)
            self.bubble_list.append(BubbleMessage(self.screen, 'Ouch! Ouch!', 1000, 0, 'spikes', self.player))

    def check_coll_player_projectile(self) -> None:
    # Player + projectile collision (arrows etc.) AND player's attack collision (so attacking arrows in flight for example)
        if pygame.sprite.spritecollide(self.player.hitbox_sprite,self.projectile_sprites,False) and self.player.state['active'] != DYING:
            for projectile in pygame.sprite.spritecollide(self.player.hitbox_sprite,self.projectile_sprites,False):
                self.particles_blood(self.player.rects['hitbox'].centerx, self.player.rects['hitbox'].centery, RED, projectile.turned)  # add blood particles whne player is hit
                self.player.hit(self.arrow_damage, projectile.turned, self.terrain_sprites)
                projectile.kill()
        for projectile in self.projectile_sprites.sprites():
            # We can attack and destroy projectiles as well
            if self.player.state['active'] == ATTACKING:
                if  pygame.Rect.colliderect(self.player.rects['attack'], projectile.rect):
                    # play some sound # TODO
                    projectile.kill()

    # Player + spell collision
    def check_coll_player_spell(self) -> None:
        if pygame.sprite.spritecollide(self.player.hitbox_sprite,self.spell_sprites,False) and self.player.state['active'] != DYING:
            for _ in pygame.sprite.spritecollide(self.player,self.spell_sprites,False):
                self.player.hazard_damage(100, hits_per_second=2)

    # Animated objects pickup / collision
    def check_coll_player_pickup(self) -> None:
        if pygame.sprite.spritecollide(self.player.hitbox_sprite,self.pickups_sprites,False) and self.player.state['active'] != DYING:
            for pickup in pygame.sprite.spritecollide(self.player,self.pickups_sprites,False):
                if pickup.name == 'health potion':
                    self.fx_health_pickup.play()
                    self.player.heal(500)
                    pickup.kill()
                if pickup.name == 'stomp potion':
                    self.fx_health_pickup.play()
                    self.player.stomp_counter = PLAYER_STOMP
                    pickup.kill()
                if pickup.name == 'mana potoion':
                    self.fx_health_pickup.play()
                    pass
                    pickup.kill()



    def check_coll_player_triggered_objects(self) -> None:
        if pygame.sprite.spritecollide(self.player.hitbox_sprite,self.triggered_objects_sprites,False) and self.player.state['active'] != DYING:
            for t_object in pygame.sprite.spritecollide(self.player,self.triggered_objects_sprites,False):
                if any('key' in sublist for sublist in self.player_inventory): # do we have key?
                    t_object.animation.active = True
                    self.bubble_list.append(BubbleMessage(self.screen, 'And that was the lock...', 3000, 0, 'exit', self.player))
                else:
                    self.player.hit(0, -1, self.terrain_sprites)
                    self.bubble_list.append(BubbleMessage(self.screen, 'I\'m missing a key!', 3000, 0, 'exit', self.player))

    # Dropped objects pickup / collision
    def check_coll_player_drops(self) -> None:
        if pygame.sprite.spritecollide(self.player.hitbox_sprite,self.drops_sprites,False) and self.player.state['active'] != DYING:
            for drop in pygame.sprite.spritecollide(self.player.hitbox_sprite,self.drops_sprites,False):
                if drop.drop_type == 'key':
                    self.player_inventory.append(('key', self.key_img))  # inventory of items and their animations
                    self.fx_key_pickup.play()            
                    drop.kill()
                    self.bubble_list.append(BubbleMessage(self.screen, 'A key! All I need now is a lock.', 5000, 3000, 'key', self.player))
               
                logging.debug(f'PICKUP: {drop.drop_type}')
                logging.debug(f'Inventory: {self.player_inventory}')   

    def check_coll_stomp_monster(self) -> None:
        # Mobs caught in stomp blast effect
        if self.stomp_effects.sprite:
            stomp_collision = pygame.sprite.spritecollide(self.stomp_effects.sprite, self.monsters_sprites,False)
            if stomp_collision:
                for monster in stomp_collision:
                    if monster.state not in (DYING, DEAD):
                        if pygame.Rect.colliderect(self.stomp_effects.sprite.rect, monster.hitbox): 
                            monster.state_change(DYING)
                            self.player_score += monster.data.points_reward
                            self.player.stomp_counter += 1
                            logging.debug(f'{monster.data.monster} killed by player stomp')

    def check_coll_player_monster(self) -> None:
        # Player + mobs group collision
        monster_collisions = pygame.sprite.spritecollide(self.player.hitbox_sprite, self.monsters_sprites,False)
        if monster_collisions and self.player.state['active'] not in (DYING, STOMPING):
            for monster in monster_collisions:
                if monster.state != DYING and monster.state != DEAD:  # we only deal with the living
                    if pygame.Rect.colliderect(self.player.rects['hitbox'], monster.hitbox):  # sprite collision not enough, we now check hitboxes
                       if monster.state not in (DYING, STOMPING):  # check to avoid repeat damage
                            # Player gets bumped _away_ from mob:
                            self.player.hit(100, monster.turned, self.terrain_sprites)  # bump player _away_ from monster

    def check_monsters(self) -> None:
        # Monsters can be up to several things, which we check for here
        now = pygame.time.get_ticks()
        for monster in self.monsters_sprites.sprites():
            if monster.state != DYING and monster.state != DEAD:  # only dealing with the living
                #  --> casting spells=
                if monster.cast_anim_list:
                    for spell in monster.cast_anim_list:
                        if spell[0] == 'fire':
                            x, y = spell[1:3]
                            self.spell_sprites.add(Spell(x,y, self.anim['fire']['fire-spell'], False, scale=1))
                    monster.cast_anim_list = []

                # --> detecting (or no longer detecting) the player and switch to/from ATTACK mode
                if pygame.Rect.colliderect(self.player.rects['hitbox'], monster.rect_detect) and self.player.state['active'] not in (DYING, DEAD):
                    if monster.state == WALKING:
                        monster.state_change(ATTACKING)    
                else:  # Mob not detecting player
                    if monster.state == ATTACKING:
                        monster.state_change(WALKING)  # if we move out of range, the mob will stop attacking

                # --> attacking the player and hitting or not the player's hitbox (or launching arrow or not)                
                if pygame.Rect.colliderect(self.player.rects['hitbox'], monster.rect_attack) and monster.state == ATTACKING and self.player.state['active'] != STOMPING:
                    if monster.data.attack_instant_damage:  
                        self.player.hit(monster.data.attack_damage, monster.turned, self.terrain_sprites)  # melee hit
                        self.particles_blood(self.player.rects['hitbox'].centerx, self.player.rects['hitbox'].centery, RED, monster.turned)  # add blood particles whne player is hit
                    elif now - monster.last_arrow > monster.data.attack_delay:  # launching projectile 
                        arrow = Projectile(monster.hitbox.centerx, monster.hitbox.centery, self.arrow_img, turned = monster.turned, scale = 4)
                        # We only add the arrow once the bow animation is complete (and we know we're ATTACKING, so attack anim is active)
                        if monster.animation.on_last_frame:
                            self.projectile_sprites.add(arrow)
                            monster.last_arrow = now


    def show_bubbles(self) -> None:
        msg_types = []
        for bubble in self.bubble_list:
            if bubble.msg_type in msg_types or bubble.expired:  # we already have a bubble message of this type in the list, or it's expired
                self.bubble_list.remove(bubble)
            else:
                msg_types.append(bubble.msg_type)
                bubble.show()


       
    def particles_blood(self, x, y, color, turned) -> None:
        if turned is True:
            direction = -1 
        else: 
            direction = 1

        for _ in range(50):   
            self.particle_system.add({
                'center': [x + random() * 30, y + random() * 30],
                'velocity': [random() * 10 * direction , random() * -10],
                'radius': random() * 5,
                'color': color
            })
                

    def run(self) -> None:
        """ 
        Runs the entire level
        """
        # --> UPDATE BACKGROUND <---
        self.background.update(self.scroll)
        self.background.draw(self.screen)

        # --> UPDATE ALL SPRITE GROUPS <---

        # terrain
        self.terrain_sprites.update(self.scroll)
        self.terrain_sprites.draw(self.screen)

        # decorations  
        self.decorations_sprites.update(self.scroll)
        self.decorations_sprites.draw(self.screen)

        # hazards  
        self.hazards_sprites.update(self.scroll)
        self.hazards_sprites.draw(self.screen)

        # pickups
        self.pickups_sprites.update(self.scroll)
        self.pickups_sprites.draw(self.screen)

        # drops
        self.drops_sprites.update(self.scroll)
        self.drops_sprites.draw(self.screen)

        # projectiles
        self.projectile_sprites.update(self.scroll, self.terrain_sprites)
        self.projectile_sprites.draw(self.screen)

        # spells
        self.spell_sprites.update(self.scroll)
        self.spell_sprites.draw(self.screen)

        # triggered_objects 
        self.triggered_objects_sprites.update(self.scroll)
        self.triggered_objects_sprites.draw(self.screen)

        # monsters 
        self.monsters_sprites.update(self.scroll, self.terrain_sprites, self.player)
        self.monsters_sprites.draw(self.screen)

        # stomp shadows
        self.stomp_shadows.update(self.scroll)
        self.stomp_shadows.draw(self.screen)

        # stomp effect
        self.stomp_effects.update(self.scroll)
        self.stomp_effects.draw(self.screen)

        # dust
        self.dust_sprites.update(self.scroll)
        self.dust_sprites.draw(self.screen)

        # player 
        self.scroll = self.player.update(self.terrain_sprites)
        self.player_sprites.draw(self.screen)

        # entry and exit points
        self.player_in_out_sprites.update(self.scroll)  
        #self.player_in_out_sprites.draw(self.screen)  # normally we do not draw these, but good to have for debugging

        # environmental effects
        self.env_sprites.update(self.scroll)
        self.env_sprites.draw(self.screen)

        # particle system
        self.particle_system.update(self.scroll)
        self.particle_system.draw(self.screen)

        """ DEMO ZONE """
        # Testing player casting
        if len(self.player.cast_active):
            for cast in self.player.cast_active:
                cast.update(self.scroll)
                cast.draw(self.screen)
                if cast.done:
                    self.player.cast_active.remove(cast)

        # DEBUGGING
        self._debug_show_state()

        # --> Check player condition and actions <--
        self.check_player_fallen_off()
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
        
        # --> Check effects and particle system <--
        self.show_bubbles()
        
        # --> Log status if in the right mode
        log_mob_msg = f'{len(self.monsters_sprites.sprites())} monsters left in the sprite group'
        if log_mob_msg != self.last_log:
            logging.debug(log_mob_msg)
        self.last_log = log_mob_msg
