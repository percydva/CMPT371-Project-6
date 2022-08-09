import pygame
from network import Network


class Player():
    def __init__(self, startx, starty, width, height, color):
        self.x = startx
        self.y = starty
        self.width = width
        self.height = height
        self.velocity = 3
        self.color = color
        self.rect = (startx, starty, width, height)

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
        self.net = Network()
        self.width = w
        self.height = h
        self.player = Player(50, 50, 50, 50, (255, 0 ,0))
        self.player2 = Player(100, 100, 50, 50, (0, 255, 0))
        self.player3 = Player(0, 0, 50, 50, (0, 0, 255))
        self.player4 = Player(0, 50, 50, 50, (0, 0, 0))
        self.canvas = Canvas(self.width, self.height, "Testing...")


    def run(self):
        clock = pygame.time.Clock()
        run = True
        self.player = self.net.getID()
        while run:
            clock.tick(60)
            self.player2 = self.net.send(self.player)
            self.player3 = self.net.send(self.player)
            self.player4 = self.net.send(self.player)
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

            # Send Network Stuff
            # self.player2.x, self.player2.y = self.parse_data(self.send_data())

            # Update Canvas
            self.canvas.draw_background()
            self.player.draw(self.canvas.get_canvas())
            for obj2 in self.player2:
                obj2.draw(self.canvas.get_canvas())
            for obj3 in self.player3:
                obj3.draw(self.canvas.get_canvas())
            for obj4 in self.player4:
                print('obj4 is draw at:', obj4)
                obj4.draw(self.canvas.get_canvas())
            
            # self.player2.draw(self.canvas.get_canvas())
            # self.player3.draw(self.canvas.get_canvas())
            # self.player4.draw(self.canvas.get_canvas())
            self.canvas.update()

        pygame.quit()

    

    # def send_data(self):
    #     """
    #     Send position to server
    #     :return: None
    #     """
    #     data = str(self.net.id) + ":" + str(self.player.x) + "," + str(self.player.y)
    #     reply = self.net.send(data)
    #     return reply

    # @staticmethod
    # def parse_data(data):
    #     try:
    #         d = data.split(":")[1].split(",")
    #         return int(d[0]), int(d[1])
    #     except:
    #         return 0,0


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
