# Phflorg the Backstabber

Phflorg is one giant experiment in using pygame to create a 2D scroller. It was initially meant to be a side-scroller only, but I keep changing everything as I go and learn new tricks. 

## Various notes to self and other ramblings
The game world is obviously much larger than the screen. Whenever the player rect (x,y) reaches the left/right or top/bottom scroll threshold, the dx and/or dy values gets copied to `h_scroll` and `v_scroll` and every sprite position in the game gets updated from those values before they are reset to 0 again. 

This means that we need another way to keep track of the x and y of the player in the real world - to store the sums of `h_scroll` and `v_scroll`, and that's `self.world_x_pos` and `self.world_y_pos` which in practive contains the sum of all scrolling th eplayer sprite has done.

Additionally, as the player starts the level in different places each level, `self.v_scroll_initial` gives an initial, on-time, value to `v_scroll` for the screen to "catch up" with the player sprite position. 


self.world_x_pos = x + self.rects['player'].width / 2 # player center x position across the whole world, not just screen
        self.world_y_pos = y - self.rects['player'].height / 2 # player center y position across the whole world, not just screen (remember: up is negative y)
        self.v_scroll_initial = self.world_y_pos - V_SCROLL_THRESHOLD # just for the "camera" to see the player on the initial placement if he's not in the topleft screen


Game assets are credited in [credits.txt](credits.txt).



