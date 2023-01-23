import pygame
import pickle

from settings import *
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


class BubbleMessage():
    """ Show floating info bubbles
        Meant to linger - 10 seconds between each message 
    """
    def __init__(self, screen: pygame.display, msg: str, player: pygame.sprite.Sprite) -> None:
        self.screen = screen
        self.msg = msg
        self.player = player
        self.active = False  
        self.expired = False
        self.min_delay = 1000*10  # 10 seconds
        self.last_time = -self.min_delay  # just to make sure we run the first time without delay
        self.start_time = 0
        self.duration = 5000
        self.font_size = 32
        self.font = pygame.font.Font("assets/font/m5x7.ttf", self.font_size)  # 16, 32, 48
        
        self.half_screen = pygame.display.get_surface().get_size()[0] // 2

        self.msg_list = msg.splitlines()  # splitting the msg into a list of lines

        self.x_size = 10  # start padded
        self.y_size = 10
        y_padding = 10
        for line in self.msg_list:
            self.x_size += pygame.font.Font.size(self.font, line)[0]
            self.y_size += pygame.font.Font.size(self.font, line)[1]
            self.y_size += y_padding

    def _display_msg(self) -> None:
            # TODO: BLIT ONTO A SPRITE BIG ENOUGH FOR RECT AND CIRCLES FIRST, THEN WE CAN USE THE SPRITE TO MOVE THE BUBBLE OVER TIME
            # ALSO MAKE QUARTERR SIZE, SCALE UP, TO GET PIXEL ART EFFECT, OR REDUCE RESOLUTION EVERYWHERE AND SCALE UP!!
            padding_x = 10
            padding_y = 10

            grey = (128,128,128)
            black = (0,0,0)
            white = (255,255,255)

            # Create and fill a rectangle transparent gray
            surf = pygame.Surface((self.x_size, self.y_size)).convert_alpha()
            pygame.Surface.fill(surf, grey)
            line_size = 3

            for row, msg_text in enumerate(self.msg_list):
                text_img = self.font.render(msg_text, True, white)
                surf.blit(text_img, (padding_x,padding_y + row * pygame.font.Font.size(self.font, msg_text)[1]))
            
            y = self.player.rect.top - self.y_size
            if self.player.rect.centerx < self.half_screen:
                x = self.player.rect.centerx
            else:
                self.screen.blit(surf, (self.player.rect.centerx - self.x_size, self.player.rect.top - self.y_size))
                x = self.player.rect.centerx - self.x_size
            
            # Draw another rectangle + two half circles behind as a frame
            pygame.draw.rect(self.screen, black, (x-line_size,y-line_size, self.x_size+line_size*2, self.y_size+line_size*2))
            pygame.draw.circle(self.screen, black, (x ,y + self.y_size/2), self.y_size/2+line_size, \
                draw_top_right=False, draw_bottom_right=False, draw_top_left=True, draw_bottom_left = True)
            pygame.draw.circle(self.screen, black, (x + self.x_size, y + self.y_size/2), self.y_size/2+line_size, \
                draw_top_right=True, draw_bottom_right=True, draw_top_left=False, draw_bottom_left = False)

            # Draw surface + two half circles on each end to round off - this is the inner part - in grey
            self.screen.blit(surf, (x, y))
            pygame.draw.circle(self.screen, grey, (x,y + self.y_size/2), self.y_size/2, \
                draw_top_right=False, draw_bottom_right=False, draw_top_left=True, draw_bottom_left = True)
            pygame.draw.circle(self.screen, grey, (x+self.x_size,y + self.y_size/2), self.y_size/2, \
                draw_top_right=True, draw_bottom_right=True, draw_top_left=False, draw_bottom_left = False)


    def show(self):
        # we compensate for scrolling
        now = pygame.time.get_ticks()
        if now > self.last_time + self.min_delay and not self.active:
            self._display_msg()
            self.active = True
            pygame.time.wait(50)

            self.last_time = now
            self.start_time = now
        elif self.active and now < self.start_time + self.duration:
            self._display_msg()
        else:
            self.active = False
            self.expired = True

        

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
        self.panel_bg = pygame.image.load('assets/panel/game-panel.png').convert_alpha()
        self.panel_highlight_fx = pygame.mixer.Sound('assets/sound/game/panel_highlight.wav')


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
        self.panel_highlight_fx.play()
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
            pygame.time.wait(75)

            self.screen.blit(screen_cpy, (0,0))  # starting over
            pygame.display.update()
            pygame.time.wait(75)

        
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
