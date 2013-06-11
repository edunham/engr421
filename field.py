class Field():
    def __init__(self, dpi = 17):
        self.dpi = dpi
        self.board_size = [22.3125, 45]
        self.near_goal = (self.board_size[1] - 2) * dpi # 2"
        self.far_goal = 2 * dpi
        # "in" means visible + not scored
        # "out" means visible + scored
        # "off" means not visible
        self.triangle_state = "in"
        self.star_state = "in"
        self.triangle_pos = None
        self.star_pos = None
        #########################
        magic_near_inches = 11 ##
        magic_far_inches = 11  ##
        magic_oh_shit = 3
        #########################
        self.magic_near_distance = (self.board_size[1] - magic_near_inches) * dpi
        self.magic_far_distance = magic_far_inches * dpi
        self.magic_oh_shit = magic_oh_shit * dpi
    def get_min_pucks(self):
        # how many pucks should we be able to see?
        if self.triangle_state is "in"  and self.star_state is "in":
            return 2
        if self.triangle_state is not "off" or self.star_state is not "off":
            return 1

    def update_pucks(self, pucks):
        if len(pucks) == 0:
            print "why'd you pass update_pucks an empty list of pucks??"
            return
        if len(pucks) == 1:
            if self.triangle_state is "out" and self.star_state is not "off":
                # assume the triangle went off the board
                self.star_pos = pucks[0]
                print "Triangle is off the field"
                self.triangle_state = "off"
            elif self.star_state is "out" and self.triangle_state is not "off":
                # assume the star went off the board
                self.triangle_pos = pucks[0]
                print "Star is off the field"
                self.star_state = "off"
            return
        if pucks[0][1] > self.near_goal or pucks[0][1] < self.far_goal:
            # triangle y-pos says it's scored
            self.triangle_state = "out"
            print "Triangle scored a point"
        if pucks[1][1] > self.near_goal or pucks[1][1] < self.far_goal:
            self.star_state = "out"
            print "Star scored a point"
        self.triangle_pos = pucks[0]
        self.star_pos = pucks[1]

    def get_best_target_pos(self):
        """
        The best target is the only target if one puck is out of play.
        Otherwise, it's whichever is quite close to getting scored.
        Otherwise, it's the star.
        Yields false if neither puck is still in the game.
        """
        if self.star_state is "in" and self.star_pos[1] > self.magic_oh_shit:
            return self.star_pos
        if self.triangle_state is "in" and self.triangle_pos[1] > self.magic_oh_shit:
            return self.triangle_pos
        
        if self.triangle_state is "in" and self.star_state is "in":
            if self.triangle_pos[1] < self.magic_far_distance or self.triangle_pos[1] > self.magic_near_distance:
                # triangle first, assuming it takes more hits to move it
                return self.triangle_pos
            if self.star_pos[1] < self.magic_far_distance or self.star_pos[1] > self.magic_near_distance:
                return self.star_pos
            return self.star_pos
        if self.triangle_state is not "in":
            if self.star_state is "in":
                return self.star_pos
            return False
        elif self.star_state is not "in":
            if self.triangle_state is "in":
                return self.triangle_pos
            return False
