import pygame
from network import Network as net


class Player():
    def __init__(self, startx, starty, width, height, color):
        self.x = startx
        self.y = starty
        self.width = width
        self.height = height
        self.velocity = 3
        self.color = color
        self.rect = (startx, starty, width, height)
        self.player.id = -1 # Initialize at invalid value, gets updated when player connects

    def draw(self, g):
        pygame.draw.rect(g, self.color , self.rect)

    def move(self, dirn):
        """
        :param dirn: 0 - 3 (right, left, up, down)
        :return: None
        """

        if dirn == 0:
            self.x += self.velocity
        elif dirn == 1:
            self.x -= self.velocity
        elif dirn == 2:
            self.y -= self.velocity
        else:
            self.y += self.velocity
        self.update()
        
    def update(self):
        self.rect = (self.x, self.y, self.width, self.height)


class Game:

    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.player1 = Player(50, 50, 50, 50, (255, 0 ,0))
        self.player2 = Player(100, 100, 50, 50, (0, 255, 0))
        self.player3 = Player(150, 150, 50, 50, (0, 0, 255))
        self.player4 = Player(200, 200, 50, 50, (255, 0, 255))
        self.canvas = Canvas(self.width, self.height, "Testing...")

    def run(self):
        clock = pygame.time.Clock()
        run = True
        while run:
            clock.tick(60)
            self.send_data()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.K_ESCAPE:
                    run = False

            keys = pygame.key.get_pressed()

            if keys[pygame.K_RIGHT]:
                if self.player.x <= self.width - self.player.velocity:
                    self.player.move(0)

            if keys[pygame.K_LEFT]:
                if self.player.x >= self.player.velocity:
                    self.player.move(1)

            if keys[pygame.K_UP]:
                if self.player.y >= self.player.velocity:
                    self.player.move(2)

            if keys[pygame.K_DOWN]:
                if self.player.y <= self.height - self.player.velocity:
                    self.player.move(3)

            # Update Canvas
            self.canvas.draw_background()
            self.player1.draw(self.canvas.get_canvas())
            self.player2.draw(self.canvas.get_canvas())
            self.player3.draw(self.canvas.get_canvas())
            self.player4.draw(self.canvas.get_canvas())
            self.canvas.update()

        pygame.quit()

    def send_data(self):
        """
        Send position to server
        Gets location of other players in response
        """
        data = str(self.player.id) + ":" + str(self.player.x) + "," + str(self.player.y)
        players = self.net.send(data)
        
        # Probably a cleaner way to do this!
        # The server just got the update we sent to it, and has probably
        # finished updating this player's position before we get the response
        # back. Can we just set the position of all 4 players?
        # Concerned that might cause some stuttering for the player, 
        # or maybe some other negative effects, depending on order things happen.
        # This *is* safer, just looks a little messy.
        if self.player.id == 0:
            self.player2 = players[1]
            self.player3 = players[2]
            self.player4 = players[3]
        elif self.player.id == 1:
            self.player1 = players[0]
            self.player3 = players[2]
            self.player4 = players[3]
        elif self.player.id == 2:
            self.player1 = players[0]
            self.player2 = players[1]
            self.player4 = players[3]
        elif self.player.id == 2:
            self.player1 = players[0]
            self.player2 = players[1]
            self.player3 = players[2]
        else:
            print("ERROR [game.py]: Player ID not found!")
            print()

    @staticmethod
    def parse_data(data):
        try:
            d = data.split(":")[1].split(",")
            return int(d[0]), int(d[1])
        except:
            return 0,0


class Canvas:

    def __init__(self, w, h, name="None"):
        self.width = w
        self.height = h
        self.screen = pygame.display.set_mode((w,h))
        pygame.display.set_caption(name)

    @staticmethod
    def update():
        pygame.display.update()

    def draw_text(self, text, size, x, y):
        pygame.font.init()
        font = pygame.font.SysFont("comicsans", size)
        render = font.render(text, 1, (0,0,0))

        self.screen.draw(render, (x,y))

    def get_canvas(self):
        return self.screen

    def draw_background(self):
        self.screen.fill((255,255,255))
