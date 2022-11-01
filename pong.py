import os, time, pygame

from copy import copy
from random import choice

# Global variables
import globals

ACTIONS = ["UP", "STAY", "DOWN"]
ACTIONS_EFFECTS = {
    "UP": -1,
    "STAY": 0,
    "DOWN": 1
}

NO_REWARD = 0.0
MOVE_REWARD = -0.01
HIT_REWARD = 1.0
WIN_REWARD = 10.0
LOSE_REWARD = -10.0

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def get_initial_state():
    ball_x, ball_y = globals.args.board_width / 2, globals.args.board_height / 2
    velocity_x, velocity_y = choice([-1, 1]), choice([-1, 1])
    paddle1_x, paddle1_y = 0, globals.args.board_height / 2
    paddle2_x, paddle2_y = globals.args.board_width - 1, globals.args.board_height / 2

    return (ball_x, ball_y, velocity_x, velocity_y, paddle1_x, paddle1_y, paddle2_x, paddle2_y)

def get_legal_actions(state):
    return copy(ACTIONS)

def is_final_state(state, score):
    ball_x = state[0]
    
    if ball_x == 0 or ball_x == globals.args.board_width-1 or score < -40:
        return True

def apply_actions(state, agent_action, adversary_action):
    
    ball_x, ball_y = state[0], state[1]
    velocity_x, velocity_y = state[2], state[3]
    paddle1_x, paddle1_y = state[4], state[5]
    paddle2_x, paddle2_y = state[6], state[7]
    
    # Apply Opponent action
    paddle1_x_new, paddle1_y_new = paddle1_x, paddle1_y    
    if paddle1_y + ACTIONS_EFFECTS[adversary_action] - globals.args.paddle_size >= 0 and paddle1_y + ACTIONS_EFFECTS[adversary_action] <= globals.args.board_height - 1:
        paddle1_y_new = paddle1_y + ACTIONS_EFFECTS[adversary_action]
        
    # Apply Player action
    paddle2_x_new, paddle2_y_new = paddle2_x, paddle2_y        
    if paddle2_y + ACTIONS_EFFECTS[agent_action] - globals.args.paddle_size >= 0 and paddle2_y + ACTIONS_EFFECTS[agent_action] <= globals.args.board_height - 1:
        paddle2_y_new = paddle2_y + ACTIONS_EFFECTS[agent_action]
        
    # Move ball
    ball_x_new, ball_y_new = ball_x, ball_y
    ball_x_new += velocity_x
    ball_y_new += velocity_y
    
    # Bounce off top / bottom wall
    velocity_x_new, velocity_y_new = velocity_x, velocity_y
    if ball_y_new == 0 or ball_y_new == globals.args.board_height - 1:
        velocity_y_new *= - 1
        
    if ball_x_new == 0:
        if ball_y_new < paddle1_y_new - globals.args.paddle_size or ball_y_new > paddle1_y_new:         
            return (ball_x_new, ball_y_new, velocity_x_new, velocity_y_new, paddle1_x_new, paddle1_y_new, paddle2_x_new, paddle2_y_new), WIN_REWARD   # Opponent Miss
        else:
            velocity_x_new *= -1
            ball_x_new += velocity_x_new
            return (ball_x_new, ball_y_new, velocity_x_new, velocity_y_new, paddle1_x_new, paddle1_y_new, paddle2_x_new, paddle2_y_new), MOVE_REWARD    # Opponent Hit
                
    if ball_x_new == globals.args.board_width - 1:
        if ball_y_new < paddle2_y_new - globals.args.paddle_size or ball_y_new > paddle2_y_new:
            return (ball_x_new, ball_y_new, velocity_x_new, velocity_y_new, paddle1_x_new, paddle1_y_new, paddle2_x_new, paddle2_y_new), LOSE_REWARD  # Player Miss
        else:
            velocity_x_new *= -1       
            ball_x_new += velocity_x_new
            return (ball_x_new, ball_y_new, velocity_x_new, velocity_y_new, paddle1_x_new, paddle1_y_new, paddle2_x_new, paddle2_y_new), HIT_REWARD     # Player Hit
            
    return (ball_x_new, ball_y_new, velocity_x_new, velocity_y_new, paddle1_x_new, paddle1_y_new, paddle2_x_new, paddle2_y_new), MOVE_REWARD      # Move reward

def print_board(Q, state, agent_score, adversary_score, games_won, games_lost, debug=False):

    os.system('clear')
    
    print "G: " + str(games_won + games_lost) + " W: " + str(games_won) + " L: " + str(games_lost)
    print "Alpha: " + str(globals.args.learning_rate)
    print "Gamma: " + str(globals.args.discount)
    print "Epsilon: " + str(globals.args.epsilon)
    print "Agent strategy: " + str(globals.args.agent_strategy)
    print "Adversary strategy: " + str(globals.args.adversary_strategy)
    
    if debug:
        if (state, "UP") in Q:
            print "UP: " + str(Q[(state, "UP")])
        else:
            print "UP: 0.0"
        if (state, "STAY") in Q:
            print "STAY: " + str(Q[(state, "STAY")])
        else:
            print "STAY: 0.0"      
        if (state, "UP") in Q:
            print "DOWN: " + str(Q[(state, "DOWN")])
        else:
            print "DOWN: 0.0"      
    
    ball_x = state[0]
    ball_y = state[1]
    paddle1_x = state[4]
    paddle1_y = state[5]
    paddle2_x = state[6]
    paddle2_y = state[7]
    
    s = ' ' * globals.args.board_width * globals.args.board_height
    s = list(s)

    # left paddle
    for i in range(globals.args.paddle_size):
        s[(paddle1_y-i) * globals.args.board_width + paddle1_x] = '|'

    # right paddle
    for i in range(globals.args.paddle_size):
        s[(paddle2_y-i) * globals.args.board_width + paddle2_x] = '|'

    # ball
    s[ball_y * globals.args.board_width + ball_x] = 'o'

    board = ""
    board += '*' * globals.args.board_width + '\n'   # top wall
    for line in range(globals.args.board_height):
        for col in range(globals.args.board_width):
            board += str(s[line * globals.args.board_width + col])
        board += '\n'        
    board += '*' * globals.args.board_width + '\n'   # bottom wall

    print board
    
def get_mirrored_state(state):
    ball_x, ball_y = state[0], state[1]
    velocity_x, velocity_y = state[2], state[3]
    paddle1_x, paddle1_y = state[4], state[5]
    paddle2_x, paddle2_y = state[6], state[7]
    return (globals.args.board_width - 1 - ball_x, ball_y, -velocity_x, velocity_y, paddle1_x, paddle2_y, paddle2_x, paddle1_y)
    
def display_state(Q, state, agent_score, adversary_score, games_won, games_lost, debug=False):
    ball_x, ball_y = state[0], state[1]
    velocity_x, velocity_y = state[2], state[3]
    paddle1_x, paddle1_y = state[4], state[5]
    paddle2_x, paddle2_y = state[6], state[7]

    scale_factor = 10
    window_width = (globals.args.board_width - 1) * scale_factor
    window_height = globals.args.board_height * scale_factor
    
    # draw canvas
    pygame.init()
    canvas = pygame.display.set_mode((window_width, window_height))  

    canvas.fill(BLACK)
    pygame.draw.line(canvas, WHITE, [window_width / 2, 0],[window_width / 2, window_height], 1)
        
    # draw ball
    pygame.draw.rect(
        canvas,
        WHITE,
        [ball_x * scale_factor, ball_y * scale_factor, scale_factor, scale_factor]
    )
    
    # draw paddle 1
    pygame.draw.polygon(
        canvas,
        WHITE,
        [
            [paddle1_x * scale_factor, (paddle1_y - globals.args.paddle_size) * scale_factor],
            [(paddle1_x + 1) * scale_factor, (paddle1_y - globals.args.paddle_size) * scale_factor], 
            [(paddle1_x + 1) * scale_factor, paddle1_y * scale_factor],
            [paddle1_x * scale_factor, paddle1_y * scale_factor],
        ],
        0
    )
    
    # draw paddle 2
    pygame.draw.polygon(
        canvas,
        WHITE,
        [
            [(paddle2_x - 1) * scale_factor, (paddle2_y - globals.args.paddle_size) * scale_factor],
            [paddle2_x * scale_factor, (paddle2_y - globals.args.paddle_size) * scale_factor], 
            [paddle2_x * scale_factor, paddle2_y * scale_factor],            
            [(paddle2_x - 1) * scale_factor, paddle2_y * scale_factor],
        ],
        0
    )
    
    very_small = pygame.font.SysFont("Sitka", int(1.5 * scale_factor))
    big = pygame.font.SysFont("Sitka", 4 * scale_factor)
    
    left_score = big.render(str(adversary_score), 1, WHITE)
    canvas.blit(left_score, (window_width / 2 - 3 * scale_factor, scale_factor))
    
    right_score = big.render(str(agent_score), 1, WHITE)
    canvas.blit(right_score, (window_width / 2 + 2 * scale_factor, scale_factor))
    
    train_results = very_small.render("G: " + str(games_won + games_lost) + " W: " + str(games_won) + " L: " + str(games_lost), 1, WHITE)
    canvas.blit(train_results, (0, 0))

    learning_rate = very_small.render("Alpha: " + str(globals.args.learning_rate), 1, WHITE)
    canvas.blit(learning_rate, (0, 10))

    epsilon = very_small.render("Gamma: " + str(globals.args.discount), 1, WHITE)
    canvas.blit(epsilon, (0, 20))

    gamma = very_small.render("Epsilon: " + str(globals.args.epsilon), 1, WHITE)
    canvas.blit(gamma, (0, 30))   

    agent_strategy = very_small.render("Agent strategy: " + str(globals.args.agent_strategy), 1, WHITE)
    canvas.blit(agent_strategy, (0, 40))           
    
    agent_strategy = very_small.render("Adversary strategy: " + str(globals.args.adversary_strategy), 1, WHITE)
    canvas.blit(agent_strategy, (0, 50))  
    
    if debug:
        if (state, "UP") in Q:
            up = very_small.render("UP: " + str(Q[(state, "UP")]), 1, WHITE)
        else:
            up = very_small.render("UP: 0.0", 1, WHITE)
        if (state, "STAY") in Q:
            stay = very_small.render("STAY: " + str(Q[(state, "STAY")]), 1, WHITE)
        else:
            stay = very_small.render("STAY: 0.0", 1, WHITE)        
        if (state, "UP") in Q:
            down = very_small.render("DOWN: " + str(Q[(state, "DOWN")]), 1, WHITE)
        else:
            down = very_small.render("DOWN: 0.0", 1, WHITE)
        
        canvas.blit(up, (0, 60))
        canvas.blit(stay, (0, 70))
        canvas.blit(down, (0, 80))
        
    pygame.display.update()         