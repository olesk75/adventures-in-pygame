import pygame
import pickle

from monsters import Drop


# --- Draw on screen ---
def draw_text(text, font, text_col, x, y)-> None:
    """ Output text on screen """
    img = font.render(text, True, text_col)
    pygame.display.get_surface().blit(img, (x, y))


# --- Manage high scores ---
def load_high_score() -> int:
    """ Load high score from file """
    with open('highscore.dat', 'rb') as high_score_file:
        try:
            high_score = pickle.load(high_score_file)
        except EOFError:  # In case file does not exist with valid high score already
            return(0)
    return(high_score)

def save_high_score(high_score: int) -> None:
    """ Save high score to file """
    with open('highscore.dat', 'wb') as save_file:
        pickle.dump(high_score, save_file)    



class GamePanel():
    """ Class to show a panel on top left corner of the screen """
    def __init__(self, screen: pygame.display, player)-> None:
        self.screen = screen
        self.window_size = pygame.display.get_window_size()# screen.get_window_size()
        self.player = player

        # Define fonts
        self.font_small = pygame.font.SysFont('Lucida Sans', 40)
        self.font_big = pygame.font.SysFont('Lucida Sans', 60)

        self.blink_counter = 0
        self.blink = False
        self.last_health = 0
        self.old_inv = []  # track changes in player in ventory to highlight

        # Panel background image
        self.panel_bg = pygame.image.load('assets/game-panel.png').convert_alpha()

    def _blink_bar(self, duration) -> None:
        if self.blink == True:
            if self.blink_counter < duration:
                self.blink_counter += 1
                pygame.draw.rect(self.screen, (255,0,0), (20,40,self.player.health_bar_max_length+4,20) ,2 )
            else:
                self.blink_counter = 0
                self.blink = False
        else:
            if self.player.health_current < self.last_health: 
                self.blink = True

    def _flash_show(self, img, x,y):
        opacity = 128
        img2 = img
        img2.fill((100, 100, 100, 0), special_flags=pygame.BLEND_RGBA_ADD)
        
    
        surf = pygame.Surface(pygame.display.get_window_size())
        surf.set_alpha(opacity)  
        surf.fill((0,0,0)) # fill the entire surface
        self.screen.blit(surf, (0,0))  # blit to screen
        pygame.display.update()
        screen_cpy = self.screen.copy()
        pygame.time.wait(250)
        

        for _ in range(10):
            self.screen.blit(img2, (x,y))
            pygame.display.update()
            pygame.time.wait(100)

            self.screen.blit(screen_cpy, (0,0))  # starting over
            pygame.display.update()
            pygame.time.wait(100)

        
    def draw(self) -> None:
        # first the panel background
        self.screen.blit(self.panel_bg, (0,0))

        # score in the top left
        WHITE = (255, 255, 255)
        draw_text(f'SCORE: {self.player.score}', self.font_small, WHITE, self.window_size[0]/100, self.window_size[1]/100)  # score

        # health bar, white and semi transparent
        bar_frame = pygame.Surface((self.player.health_bar_max_length+4,20), pygame.SRCALPHA)   # per-pixel alpha
        bar_frame.fill((255,255,255,128))                         # notice the alpha value in the color
        self.screen.blit(bar_frame, (20,40))

        self._blink_bar(10)  # blink if we should

        ratio = self.player.health_bar_length / self.player.health_bar_max_length
        GREEN = 255 * ratio
        RED = 255 * (1-ratio)
        BLUE = 0

        health_bar = pygame.Surface((self.player.health_bar_length,16), pygame.SRCALPHA)   # per-pixel alpha
        health_bar.fill((RED,GREEN,BLUE,200))                         # notice the alpha value in the color
        self.screen.blit(health_bar, (22,42))
    
        self.last_health = self.player.health_current

        # player inventory top right
        key_x = self.window_size[0] * 0.8
        key_y = self.window_size[1] * 0.02


        for items in self.player.inventory:
            if items[0] == 'key':
                img = pygame.transform.scale(items[1], (40,50))
                self.screen.blit(img, (key_x,key_y))

        if len(self.player.inventory) > len(self.old_inv):  # new items! 
            new_items = [x for x in self.player.inventory if x not in self.old_inv]
            for items in new_items:
                if items[0] == 'key':
                    img = pygame.transform.scale(items[1], (40,50))
                    self._flash_show(img, key_x, key_y)

            self.old_inv = self.player.inventory
