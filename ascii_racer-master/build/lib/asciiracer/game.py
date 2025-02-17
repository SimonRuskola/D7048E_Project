import curses
import socket
from . import environment
from .environment import draw_background, draw_tracks, draw_statusbar, \
                    draw_debris, draw_horizon, draw_car, draw_money
from . import hud
from .hud import draw_hud
from .mechanics import update_state
from .config import GAME_SIZE, FPS, BASE_SPEED
from .misc import limit_fps



SCENE = [draw_statusbar, draw_hud, draw_horizon, draw_tracks,
         draw_debris, draw_car, draw_money, draw_background]
state = {'frames': 0,
         'time': 0.0,  # seconds
         'speed': BASE_SPEED,  # coord per frame
         'car': None,
         'car_x': 0,  # range -1:1
         'car_steer_tuple': None,
         'car_speed_tuple': None,
         'debris': [],  # debris objects drawn in scene
         'money': [],  # money objects drawn in scene
         'score': 0,
         'pdb': False}  # for testing


@limit_fps(fps=FPS)
def draw_scene(screen):
    for draw_element in reversed(SCENE):
        draw_element(screen, state)
    screen.refresh()

global roll

def main(screen):
    
    roll = 0

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 65432))

    screen.resize(*GAME_SIZE)
    screen.nodelay(True)
    environment.init(screen)
    hud.init(screen)
    while True:
        draw_scene(screen)
        key = screen.getch()
        if key == ord('q'):
            break
        elif key == ord('p'):
            state['pdb'] = True
        else:
            try:
                roll = float(client_socket.recv(1024).decode())
            except ValueError:
                pass
            update_state(key, state, roll)
        state['frames'] += 1
        state['time'] += 1/FPS
    screen.clear()
    screen.getkey()
    client_socket.close()


def run():
    curses.wrapper(main)
