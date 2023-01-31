"""
WorldData (dataclass)               : basic world information
GameTile (Sprite class)             : the background tiles, including platforms
GameTileAnimation (GameTile class)  : animated background tiles (flames, torches etc.)
GamePanel(class)                    : contans the player information for the screen - score, health etc.
"""


import pygame
import logging

from settings import *

from engine import import_csv_layout, import_tile_graphics,BubbleMessage
from game_tiles import GameTile, GameTileAnimation, MovingGameTile
from level_data import levels, GameAudio
from player import Player, PlayerInOut
from monsters import Monster, Projectile, Spell, Drop
from decor_and_effects import Sky, EnvironmentalEffects, ExpandingCircle
from monster_data import arrow_damage

class Level():
    def __init__(self,current_level,surface, health_max) -> None:
        logging.basicConfig(level=logging.DEBUG)
        self.last_log = ''  # we do this to only log when something _new_ happens


        from animation_data import anim  # we do this late, as we need to have display() up first
        self.anim = anim

        # general setup
        self.current_level = current_level
        self.level_complete = False
        self.screen = surface
        self.scroll = 0
        self.current_x = None

        self.arrow_damage = arrow_damage
        
        # tile data for current level
        level_data = levels[self.current_level]
        self.lvl_entry = (0,0)
        self.lvl_exit = (0,0)

        self.player_dead = False
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
        self.sky = Sky(self.current_level, self.screen)

        # test expanding circle TODO: TEST TEST DEBUG
        self.exp_circle1 = ExpandingCircle(1000, 500, WHITE, 30, 300,10)
        self.exp_circle2 = ExpandingCircle(1100, 450, WHITE, 30, 200,10)
        self.exp_circle3 = ExpandingCircle(800, 600, WHITE, 30, 100,10)


        # environmental effects (leaves, snow etc.)
        self.env_sprites = EnvironmentalEffects(level_data['environmental_effect'], self.screen)  # 'leaves' for lvl1


        # player
        self.player = self.player_setup()
        self.player_sprites = pygame.sprite.GroupSingle()
        self.player_sprites.add(self.player)


    def create_tile_group(self,layout,type) -> pygame.sprite.Group:
        sprite_group = pygame.sprite.Group()

        # Import all the tile PNGs 
        terrain_tile_list = import_tile_graphics('assets/tile/terrain/*.png')
        decorations_tile_list = import_tile_graphics('assets/tile/decorations/*.png')
        hazards_tile_list = import_tile_graphics('assets/tile/hazards/*.png')
        pickups_tile_list = import_tile_graphics('assets/tile/pickups/*.png')
        triggered_objects_tile_list = import_tile_graphics('assets/tile/trigger-objects/*.png')
        monsters_tile_list = import_tile_graphics('assets/tile/monsters/*.png')
        player_tile_list = import_tile_graphics('assets/tile/player/*.png')

        
        for row_index, row in enumerate(layout):
            for col_index,val in enumerate(row):
                if val != '-1':
                    # print(f'{row_index=} {col_index=}')  # DEBUG
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE
                    bottom_pos = (1 + row_index) * (TILE_SIZE)  # this helps anchor sprites that are odd sizes, where we have to check they are on the ground
            

                    if type == 'terrain':  
                        list_of_solid_terrain = [0,1,2,3,4,5,6,7,8,11]  # only these terrain tiles will hold monsters and player up
                        list_of_moving_platforms = [11]

                        tile_surface = terrain_tile_list[int(val)]
                        (x_size, y_size) = tile_surface.get_size()
                        # As we need to scale sprites mostly 64x64px into our screen size, we need the following calculation:
                        # The allows us non-rectangular sprites, as long as they are a multiple of 64 in both directions
                        x_size = x_size * 2 + 3
                        y_size = y_size * 2 + 3
                        distance = 150
                        if int(val) in list_of_moving_platforms:
                            sprite = MovingGameTile(x_size,y_size,x,y, 3,  distance,tile_surface)  # Moving platform
                        else:
                            sprite = GameTile(x_size,y_size,x,y,tile_surface)  # Normal static terrain tiles
                        
                        if int(val) not in list_of_solid_terrain:  # Water mostly
                            sprite.solid = False
                        
                        
                    if type == 'decorations':
                        tile_surface = decorations_tile_list[int(val)]
                        (x_size, y_size) = tile_surface.get_size()
                        x_size = x_size * 2 + 3
                        y_size = y_size * 2 + 3
                        sprite = GameTile(x_size,y_size,x,y,tile_surface)
                        sprite.rect.bottom = bottom_pos

                    if type == 'hazards':
                        tile_surface = hazards_tile_list[int(val)]
                        (x_size, y_size) = tile_surface.get_size()
                        x_size = x_size * 2 + 3
                        y_size = y_size * 2 + 3
                        if int(val) == 0:  # fire
                            sprite = GameTileAnimation(x_size, y_size,x,y,tile_surface, self.anim['fire']['fire-hazard'])
                        if int(val) == 1:  # spikes
                            sprite = GameTileAnimation(x_size, y_size,x,y,tile_surface, self.anim['spikes']['spike-trap'])
                        sprite.rect.bottom = bottom_pos
                        
                    if type == 'pickups':
                        tile_surface = pickups_tile_list[int(val)]
                        (x_size, y_size) = tile_surface.get_size()
                        x_size = x_size * 2 + 3
                        y_size = y_size * 2 + 3
                        if int(val) == 0:  # health potion
                            sprite = GameTileAnimation(x_size, y_size,x,y,tile_surface, self.anim['pickups']['health-potion'])
                        sprite.rect.bottom = bottom_pos

                    if type == 'triggered_objects':
                        tile_surface = triggered_objects_tile_list[int(val)]
                        (x_size, y_size) = tile_surface.get_size()
                        x_size = x_size * 2 + 3
                        y_size = y_size * 2 + 3
                        if int(val) == 0:  # door at end of level
                            sprite = GameTileAnimation(x_size, y_size,x,y - 10 ,tile_surface, self.anim['doors']['end-of-level'])
                            sprite.animation.active = False
                        sprite.rect.bottom = bottom_pos

                    if type == 'monsters':
                        tile_surface = monsters_tile_list[int(val)]
                        if int(val) == 0:  # minotaur
                            sprite = Monster(x,y,tile_surface, 'minotaur')
                        if int(val) == 1:  # ogre-archer
                            sprite = Monster(x,y,tile_surface, 'ogre-archer')
                        if int(val) == 2:  # skeleton-boss
                            sprite = Monster(x,y,tile_surface, 'skeleton-boss')
                        if int(val) == 3:  # elven-caster
                            sprite = Monster(x,y,tile_surface, 'elven-caster')
                        
                    if type == 'player':
                        _ = player_tile_list[int(val)]  # we don't draw the tiles, only used in map editor
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

    # --> CHECK ALL COLLISIONS <--
    # Note: use pygame.sprite.spritecollide() for sprite against group with low precision
    #       use pygame.Rect.colliderect() to compare two rects (high precision hitboxes intead of sprite)
    
    def check_player_attack(self) -> None:
        for monster in self.monsters_sprites.sprites():
            # --> We check if the player is attacking and if the attack hits a monster
            if self.player.state == ATTACKING and monster.state != DYING and monster.state != DEAD:
                # Check if mob hit
                if pygame.Rect.colliderect(self.player.attack_rect, monster.hitbox): 
                    
                    logging.debug(f'{monster.data.monster} killed by player attack')
                    monster.data.direction = -self.player.turned
                    self.player_score += monster.data.points_reward
                    """ Adding drops from player death """
                    # skeleton-boss is a key carrier
                    if monster.data.monster == 'skeleton-boss':
                        drop_key = Drop( monster.hitbox.centerx, monster.hitbox.centery - 25 , self.anim['pickups']['key'], turned = False, scale = 2, drop_type='key',)
                        self.drops_sprites.add(drop_key)
                        logging.debug(f'{monster.data.monster} dropped a key')

                    monster.state_change(DYING)  # we do this _after_ key drop, as the hitbox disappears when the mob enters DYING state


    def check_player_win(self) -> None:
        # Player sprite reaches goal tile
        if pygame.sprite.spritecollide(self.player,self.player_in_out_sprites,False):
            if pygame.sprite.spritecollide(self.player,self.player_in_out_sprites,False)[0].inout == 'out':  # first colliding sprite
                logging.debug('WIN! Level complete')
                self.level_complete = True

    def check_player_fallen_off(self) -> None:
        if self.player.rect.top > SCREEN_HEIGHT:
            self.player.state = DYING
            self.player_dead = True
            logging.debug('Oooops! Player fell off')


    def check_coll_player_hazard(self) -> None:
        # Player + hazard group collision 
        if pygame.sprite.spritecollide(self.player.hitbox_sprite,self.hazards_sprites,False) and self.player.state != DYING:
            self.player.hazard_damage(100, hits_per_second=10)
            self.bubble_list.append(BubbleMessage(self.screen, 'Ouch! Ouch!', 1000, 'spikes', self.player))

    def check_coll_player_projectile(self) -> None:
    # Player + projectile collision (arrows etc.) AND player's attack collision (so attacking arrows in flight for example)
        if pygame.sprite.spritecollide(self.player.hitbox_sprite,self.projectile_sprites,False) and self.player.state != DYING:
            for projectile in pygame.sprite.spritecollide(self.player.hitbox_sprite,self.projectile_sprites,False):
                self.player.hit(self.arrow_damage, projectile.turned, self.terrain_sprites)  # TODO: separate sprite group for solid terrain
                projectile.kill()
        for projectile in self.projectile_sprites.sprites():

            if self. player.state == ATTACKING:
                if  pygame.Rect.colliderect(self.player.attack_rect, projectile.rect):
                    # play some sound # TODO
                    projectile.kill()

    # Player + spell collision
    def check_coll_player_spell(self) -> None:
        if pygame.sprite.spritecollide(self.player.hitbox_sprite,self.spell_sprites,False) and self.player.state != DYING:
            for _ in pygame.sprite.spritecollide(self.player,self.spell_sprites,False):
                self.player.hazard_damage(100, hits_per_second=2)

    # Animated objects pickup / collision
    def check_coll_player_pickup(self) -> None:
        if pygame.sprite.spritecollide(self.player.hitbox_sprite,self.pickups_sprites,False) and self.player.state != DYING:
            for pickup in pygame.sprite.spritecollide(self.player,self.pickups_sprites,False):
                # TODO: more types than just health potion
                self.fx_health_pickup.play()
                self.player.heal(500)
                pickup.kill()

    def check_coll_player_triggered_objects(self) -> None:
        if pygame.sprite.spritecollide(self.player.hitbox_sprite,self.triggered_objects_sprites,False) and self.player.state != DYING:
            for t_object in pygame.sprite.spritecollide(self.player,self.triggered_objects_sprites,False):
                if any('key' in sublist for sublist in self.player_inventory): # do we have key?
                    t_object.animation.active = True
                    self.bubble_list.append(BubbleMessage(self.screen, 'Level complete!\nCongratualations!', 5000, 'exit', self.player))
                else:
                    self.player.hit(0, -1, self.terrain_sprites)
                    self.bubble_list.append(BubbleMessage(self.screen, 'Come back when you have a key!', 5000, 'exit', self.player))

    # Dropped objects pickup / collision
    def check_coll_player_drops(self) -> None:
        if pygame.sprite.spritecollide(self.player.hitbox_sprite,self.drops_sprites,False) and self.player.state != DYING:
            for drop in pygame.sprite.spritecollide(self.player.hitbox_sprite,self.drops_sprites,False):
                if drop.drop_type == 'key':
                    self.player_inventory.append(('key', self.key_img))  # inventory of items and their animations
                    self.fx_key_pickup.play()            
                    drop.kill()
                    self.bubble_list.append(BubbleMessage(self.screen, 'You have found a key!\nWhere could it possibly fit?', 5000, 'key', self.player))
                if drop.drop_type == 'health-potion':
                    self.fx_health_pickup.play()
                    self.player.heal(500)
                logging.debug(f'PICKUP: {drop.drop_type}')
                logging.debug(f'Inventory: {self.player_inventory}')   

    def check_coll_player_monster(self) -> None:
        # Player + mobs group collision -> stomp means kill, otherwise player damage
        monster_collisions = pygame.sprite.spritecollide(self.player.hitbox_sprite, self.monsters_sprites,False)
        if monster_collisions and self.player.state != DYING:
            for monster in monster_collisions:
                if monster.state != DYING and monster.state != DEAD:  # we only deal with the dead
                    if pygame.Rect.colliderect(self.player.hitbox, monster.hitbox):  # sprite collision not enough, we now check hitboxes
                        if monster.rect.top < self.player.rect.bottom < monster.rect.centery and \
                            self.player.vel_y >= 0 and monster.data and monster.data.boss == False:  #stomp!! Doesn't work on bosses!
                            monster.state = DYING
                            self.fx_player_stomp.play()
                            self.player.vel_y = -10
                        elif monster.state != DYING:  # check to avoid repeat damage
                            # Player gets bumped _away_ from mob:
                            self.player.hit(100, monster.turned, self.terrain_sprites)  # bump player _away_ from monster

    def check_monsters(self) -> None:
        # Monsters can be up to several things, which we check for here
        now = pygame.time.get_ticks()
        for monster in self.monsters_sprites.sprites():
            if monster.state == DEAD:
                monster.kill()
            if monster.state != DYING and monster.state != DEAD:  # only dealing with the living
                #  --> casting spells=
                if monster.cast_anim_list:
                    for spell in monster.cast_anim_list:
                        if spell[0] == 'fire':
                            x, y = spell[1:3]
                            self.spell_sprites.add(Spell(x,y, self.anim['fire']['fire-spell'], False, scale=1))
                    monster.cast_anim_list = []

                # --> detecting (or no longer detecting) the player and switch to/from ATTACK mode
                if pygame.Rect.colliderect(self.player.hitbox, monster.rect_detect):
                    if monster.state == WALKING:
                        monster.state_change(ATTACKING)    
                else:  # Mob not detecting player
                    if monster.state == ATTACKING:
                        monster.state_change(WALKING)  # if we move out of range, the mob will stop attacking

                # --> attacking the player and hitting or not the player's hitbox (or launching arrow or not)                
                if pygame.Rect.colliderect(self.player.hitbox, monster.rect_attack) and monster.state == ATTACKING:
                    if monster.data.attack_instant_damage:  
                        self.player.hit(monster.data.attack_damage, monster.turned, self.terrain_sprites)  # melee hit
                    elif now - monster.last_arrow > monster.data.attack_delay:  # launching projectile 
                        arrow = Projectile(monster.hitbox.centerx, monster.hitbox.centery, self.arrow_img, turned = monster.turned, scale = 2)
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
                

    def run(self) -> None:
        """ 
        Runs the entire level
        """

        # --> UPDATE BACKGROUND <---
        self.sky.update(self.scroll)
        self.sky.draw(self.screen)

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

        # player 
        self.scroll = self.player.update(self.terrain_sprites)
        self.player_sprites.draw(self.screen)
        if self.player.state == DEAD:
            self.player_dead = True

        # entry and exit points
        self.player_in_out_sprites.update(self.scroll)  
        #self.player_in_out_sprites.draw(self.screen)  # normally we do not draw these, but good to have for debugging

        # environmental effects
        self.env_sprites.update(self.scroll)
        self.env_sprites.draw(self.screen)

        """ DEMO ZONE """
        # TEST-CIRCLES
        self.exp_circle1.update(self.scroll)
        self.exp_circle1.draw(self.screen)
        self.exp_circle2.update(self.scroll)
        self.exp_circle2.draw(self.screen)
        self.exp_circle3.update(self.scroll)
        self.exp_circle3.draw(self.screen)

        # --> Check collisions <--
        self.check_player_attack()
        self.check_player_win()
        self.check_coll_player_hazard()
        self.check_coll_player_projectile()
        self.check_coll_player_spell()
        self.check_coll_player_pickup()
        self.check_coll_player_triggered_objects()
        self.check_coll_player_drops()
        self.check_coll_player_monster()
        self.check_monsters()  # this check mob detection + attack as well as player attack against all mobs
        self.check_player_fallen_off()
        self.show_bubbles()
        
        # --> Log status if in the right mode
        log_mob_msg = f'{len(self.monsters_sprites.sprites())} monsters left in the sprite group'
        if log_mob_msg != self.last_log:
            logging.debug(log_mob_msg)
        self.last_log = log_mob_msg
