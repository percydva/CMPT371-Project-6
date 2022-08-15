import pygame
import socket
import time

from config import POOL_WIDTH, POOL_HEIGHT
from session import Session

STATUS_PANEL_WIDTH = 400
WIDTH, HEIGHT = POOL_WIDTH + STATUS_PANEL_WIDTH, POOL_HEIGHT

class Bubble:

    def __str__(self):
        #Client 
        return str({
            'id': self.id,
            'position': self.position,
            'radius': self.radius,
            'color': self.color,
            'locked': self.locked,
            'locked_by': self.locked_by,
            'locked_by_others': self.locked_by_others,
        })
    
    #Client initialize player id, position, radius, color, locked, locked_by, locked_by_others
    def __init__(self, config):
        self.id = config['id']
        self.position = config['position']
        self.radius = config['radius']
        self.color = config['color']
        self.locked = False
        self.locked_by_others = False
        self.locked_by = None
    
    #Client draw bubbles on screen with pygame.draw.circle
    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            self.position,
            self.radius)
        if self.locked:
            pygame.draw.circle(
                screen,
                'red' if self.locked_by_others else 'green',
                self.position,
                self.radius,
                2)
    
class BubblePanel:
    '''
    Manage bubbles
    '''
    #Client initialize bubbles with config.py file
    def __init__(self, surface):
        self.bubbles = {}
        self.surface = surface

    #draw all bubbles on screen
    def draw(self):
        '''
        draw all bubbles
        '''
        for b in self.bubbles.values():
            b.draw(self.surface)

#######
def in_bubble(position, bubble):
    pos1 = position
    pos2 = bubble.position
    radius = bubble.radius
    return (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2 <= radius ** 2

#Centering the selected windows in the centered of the screen.
def centered(parent, target):
    x = (parent.get_width() - target.get_width()) / 2
    y = (parent.get_height() - target.get_height()) / 2
    return x, y

#Class status panel
class StatusPanel:
    #Client initialize status panel 
    def __init__(self, client, surface):
        self.client = client
        self.surface = surface
        self.color = (50, 50, 50)
        self.font = pygame.font.Font(None, 30)
    
    #render player_id (ip address) and player_score (score) and delay (delay)
    def draw(self):
        self.surface.fill(self.color)
        position = (10, 10)
        for player_id, player_score in self.client.get_status():
            text = self.font.render(f'{player_id}: {player_score}', True, 'white')
            self.surface.blit(text, position)
            position = (position[0], position[1] + 30)
        delay_text = self.font.render(f'delay: {self.client.get_delay()}ms', True, 'white')
        self.surface.blit(delay_text, (10, self.surface.get_height() - 30))

#Client initialize client with server_address and screen
class Client:
    def __init__(self, server_addr, screen):
        self.socket = socket.socket()
        self.socket.connect(server_addr)
        self.input_messages = []
        self.session = Session(self.socket, server_addr, self.handle_message)
        self.player_id = None
        self.player_score = 0
        self.players = {}
        self.delay = 0

        self.login()

        self.screen = screen
        self.bubble_panel = BubblePanel(self.screen.subsurface((0, 0, POOL_WIDTH, POOL_HEIGHT)))
        self.status_panel = StatusPanel(self, self.screen.subsurface((POOL_WIDTH, 0, STATUS_PANEL_WIDTH, HEIGHT)))

        self.sync_delay = 0

    #get delay function from session class
    def get_delay(self):
        return int(self.delay * 1000)

    #Client login
    def login(self):
        self.session.write_message({
            'action': 'login'
        })

    #Handle message fucntion by reading message from socket using jason
    def handle_message(self, session, message):
        action = message.get('action', None)
        #delay message which is passed from server to client
        if action == 'ping':
            self.delay = time.time() - message['timestamp']
        #player_id message which is passed from server to client
        elif action == 'login':
            self.player_id = message['player_id']
        #bubble message which is passed from server to client
        elif action == 'bubble_added':
            bubble = Bubble(message)
            self.bubble_panel.bubbles[bubble.id] = bubble
        #bubble expired message which is passed from server to client
        elif action == 'bubble_expired':
            bubble_id = message['bubble_id']
            if bubble_id in self.bubble_panel.bubbles:
                del self.bubble_panel.bubbles[message['bubble_id']]
        #bubble locked message which is passed from server to client
        elif action == 'bubble_locked':
            for bubble_id in self.bubble_panel.bubbles:
                bubble = self.bubble_panel.bubbles[bubble_id]
                if bubble_id == message['bubble_id']:
                    bubble.locked = True
                    bubble.locked_by_others = message['player_id'] != self.player_id
                    bubble.locked_by = message['player_id']
                elif bubble.locked_by == message['player_id']:
                    bubble.locked = False
                    bubble.locked_by_others = False
                    bubble.locked_by = None
        #bubble consumed message which is passed from server to client
        elif action == 'bubble_consumed':
            bubble_id = message['bubble_id']
            del self.bubble_panel.bubbles[bubble_id]
        #bubble lock failed message which is passed from server to client
        elif action == 'bubble_lock_failed':
            pass
        #player status message which is passed from server to client
        elif action == 'status':
            self.players = message['players']
        else:
            print('unknown message:', message)
    
    #Client send message to server for server to handle
    def write_message(self, message):
        self.session.write_message(message)

    #update function to keep server updated
    def update(self, tick_in_ms):
        self.sync_delay += tick_in_ms
        if self.sync_delay >= 1000:
            self.sync_delay = 0
            self.write_message({
                'action': 'status'
            })
            self.write_message({
                'action': 'ping',
                'timestamp': time.time()
            })
    #draw function to initialize status panel and bubble panel and set the background to black
    def draw(self):
        self.screen.fill('black')
        self.status_panel.draw()
        self.bubble_panel.draw()
    
    #get bubble function to get bubble from bubble panel
    def get_bubble_at(self, pos):
        for b in self.bubble_panel.bubbles.values():
            if in_bubble(pos, b):
                return b
        return None
    
    #locking bubble function to lock bubble from bubble panel
    def lock_bubble(self, bubble):
        print(f'lock bubble: {bubble.id}')
        self.write_message({
            'action': 'lock',
            'bubble_id': bubble.id,
            'player_id': self.player_id,
        })

    #get status to show player id and the player score.
    def get_status(self):
        status = []
        for player_id in self.players:
            status.append((player_id, self.players[player_id]['score']))
        return status
#main function to initialize client and run the game
def main(server_address):
    pygame.init()

    pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Client")

    screen = pygame.display.get_surface()
    client = Client(server_address, screen)

    #setting up FPS for each frame the client will be updated
    FPS = 60
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            #using mouse click to get the position of the mouse and get the bubble at the position
            elif event.type == pygame.MOUSEBUTTONDOWN:
                position = pygame.mouse.get_pos()
                bubble = client.get_bubble_at(position)
                if bubble:
                    client.lock_bubble(bubble)

        tick_in_ms = clock.tick(FPS)
        client.update(tick_in_ms)
        client.draw()
        pygame.display.update()
    #quit the game
    pygame.quit()

#setting up --port by connecting to server using the default port and ip address
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('server', nargs='?', default='localhost')
    parser.add_argument('--port', default=80, type=int)
    args = parser.parse_args()
    main((args.server, args.port))
