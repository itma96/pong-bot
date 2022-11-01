# General imports
from copy import copy
from random import choice, random
from argparse import ArgumentParser

# Global variables
import globals

# Game functions
from pong import *

def epsilon_greedy(Q, state, legal_actions, epsilon):
    if random() < epsilon:
        action = choice(legal_actions)
        if (state, action) not in Q:
            Q[(state, action)] = 0.0
        return action
    else:
        return best_action(Q, state, legal_actions)

def best_action(Q, state, legal_actions):
    best_action = None
    max_value = -99999
    for action in legal_actions:
        if (state, action) not in Q:
            Q[(state, action)] = 0.0
        if Q[(state, action)] > max_value:
            max_value = Q[(state, action)]
            best_action = action
    return best_action

def q_learning():
    Q = {}
    train_scores = []
    eval_scores = []
    games_won = 0
    games_lost = 0
    
    # for each episode ...
    for train_ep in range(0, globals.args.train_episodes):
    
        print("Episode %6d / %6d" % (train_ep, globals.args.train_episodes))
    
        # ... get the initial state,
        score = 0
        agent_score = 0
        adversary_score = 0
        max_allowed_steps = 300
        state = get_initial_state()
            
        # while current state is not terminal
        while not is_final_state(state, score) and max_allowed_steps > 0:
        
            # display current state and sleep
            if globals.args.verbose:
                if globals.args.term:
                    print_board(state)
                else:
                    display_state(Q, state, agent_score, adversary_score, games_won, games_lost)
                time.sleep(globals.args.sleep)

            # choose one of the legal actions
            actions = get_legal_actions(state)
            
            if globals.args.agent_strategy == "random":
                agent_action = choice(actions)
            elif globals.args.agent_strategy == "greedy":
                agent_action = best_action(Q, state, actions)
            elif globals.args.agent_strategy == "epsilon_greedy":
                agent_action = epsilon_greedy(Q, state, actions, globals.args.epsilon)

            if globals.args.adversary_strategy == "random":
                adversary_action = choice(actions)
            elif globals.args.adversary_strategy == "greedy":          
                mirrored_state = get_mirrored_state(state)
                adversary_action = best_action(Q, mirrored_state, get_legal_actions(mirrored_state))
            elif globals.args.adversary_strategy == "almost_perfect":
                if random() < 0.3:
                    adversary_action = choice(actions)
                else:
                    ball_x, ball_y = state[0], state[1]
                    velocity_x, velocity_y = state[2], state[3]
                    paddle1_x, paddle1_y = state[4], state[5]
                    if ball_y + velocity_y > paddle1_y:
                        adversary_action = "DOWN"
                    elif ball_y + velocity_y < paddle1_y:
                        adversary_action = "UP"
                    else:
                        adversary_action = "STAY"
            
            # apply action and get the next state and the reward
            next_state, reward = apply_actions(state, agent_action, adversary_action)
            score += reward
            
            if reward == WIN_REWARD:
                games_won += 1
                agent_score += 1
            
            if reward == LOSE_REWARD:
                games_lost += 1
                adversary_score += 1
                
            if globals.args.agent_strategy == "greedy" or globals.args.agent_strategy == "epsilon_greedy":
                max_a = best_action(Q, next_state, actions)
                Q[(state, agent_action)] = Q[(state, agent_action)] + globals.args.learning_rate * (reward + globals.args.discount * Q[(next_state, max_a)] - Q[(state, agent_action)])

            # update current state
            state = next_state
            
            max_allowed_steps -= 1

        train_scores.append(score)

        # evaluate the greedy policy
        if train_ep % globals.args.eval_every == 0:
            avg_score = .0
            scores = []
            for eval_ep in range(0, globals.args.eval_episodes):
                state = get_initial_state()
                score = 0
                max_allowed_steps = 300
                while not is_final_state(state, score) and max_allowed_steps > 0:
                    # choose one of the legal actions
                    actions = get_legal_actions(state)                
                    
                    if globals.args.agent_strategy == "random":
                        agent_action = choice(actions)
                    else:
                        agent_action = best_action(Q, state, actions)
                        
                    if globals.args.adversary_strategy == "random":
                        adversary_action = choice(actions)
                    elif globals.args.adversary_strategy == "greedy":           
                        mirrored_state = get_mirrored_state(state)
                        adversary_action = best_action(Q, mirrored_state, get_legal_actions(mirrored_state))
                    elif globals.args.adversary_strategy == "almost_perfect":
                        if random() < 0.3:
                            adversary_action = choice(actions)
                        else:
                            ball_x, ball_y = state[0], state[1]
                            velocity_x, velocity_y = state[2], state[3]
                            paddle1_x, paddle1_y = state[4], state[5]
                            if ball_y + velocity_y > paddle1_y:
                                adversary_action = "DOWN"
                            elif ball_y + velocity_y < paddle1_y:
                                adversary_action = "UP"
                            else:
                                adversary_action = "STAY"
                    state, reward = apply_actions(state, agent_action, adversary_action)
                    score += reward
                    
                    max_allowed_steps -= 1
                
                scores.append(score)
            avg_score = sum(scores)/float(len(scores))
            eval_scores.append(avg_score)
    
    if globals.args.final_show:
        agent_score = 0
        adversary_score = 0
        for _ in range(globals.args.eval_episodes):
            score = 0
            max_allowed_steps = 500
            state = get_initial_state()
            while not is_final_state(state, score) and max_allowed_steps > 0:
                # display current state and sleep
                if globals.args.term:
                    print_board(Q, state, agent_score, adversary_score, games_won, games_lost, True)
                else:
                    display_state(Q, state, agent_score, adversary_score, games_won, games_lost, True)
                time.sleep(globals.args.sleep)
                
                # choose one of the legal actions
                actions = get_legal_actions(state)                
                
                if globals.args.agent_strategy == "random":
                    agent_action = choice(actions)
                else:
                    agent_action = best_action(Q, state, actions)
                if globals.args.adversary_strategy == "random":
                    adversary_action = choice(actions)
                elif globals.args.adversary_strategy == "greedy":       
                    mirrored_state = get_mirrored_state(state)
                    adversary_action = best_action(Q, mirrored_state, get_legal_actions(mirrored_state))
                elif globals.args.adversary_strategy == "almost_perfect":
                    if random() < 0.3:
                        adversary_action = choice(actions)
                    else:
                        ball_x, ball_y = state[0], state[1]
                        velocity_x, velocity_y = state[2], state[3]
                        paddle1_x, paddle1_y = state[4], state[5]
                        if ball_y + velocity_y > paddle1_y:
                            adversary_action = "DOWN"
                        elif ball_y + velocity_y < paddle1_y:
                            adversary_action = "UP"
                        else:
                            adversary_action = "STAY"
                state, reward = apply_actions(state, agent_action, adversary_action)
                
                if reward == WIN_REWARD:
                    agent_score += 1
                if reward == LOSE_REWARD:
                    adversary_score += 1
                
                score += reward
                
                max_allowed_steps -= 1
                
    if globals.args.plot_scores:
        from matplotlib import pyplot as plt
        import numpy as np
        plt.xlabel("Episode")
        plt.ylabel("Average score")
        plt.plot(
            np.linspace(1, globals.args.train_episodes, globals.args.train_episodes),
            np.convolve(train_scores, [0.2,0.2,0.2,0.2,0.2], "same"),
            linewidth = 1.0, color = "blue"
        )
        plt.plot(
            np.linspace(globals.args.eval_every, globals.args.train_episodes, len(eval_scores)),
            eval_scores, linewidth = 2.0, color = "red"
        )
        plt.show()
        
if __name__ == "__main__":
    parser = ArgumentParser()
    
	# Board Parameters
    parser.add_argument("--board_width", type = int, default = 41,
                        help = "Board width")
    parser.add_argument("--board_height", type = int, default = 21,
                        help = "Board height")
    parser.add_argument("--paddle_size", type = int, default = 3,
                        help = "Paddle size")

    # Meta-parameters
    parser.add_argument("--agent_strategy", type = str, default = "random",
                        help = "Strategy used by agent")
    parser.add_argument("--adversary_strategy", type = str, default = "random",
                        help = "Strategy used by opponent")                        
    parser.add_argument("--learning_rate", type = float, default = 0.2,
                        help = "Learning rate")
    parser.add_argument("--discount", type = float, default = 0.9,
                        help = "Value for the discount factor")
    parser.add_argument("--epsilon", type = float, default = 0.1,
                        help = "Probability to choose a random action.")     
                        
    # Training and evaluation episodes
    parser.add_argument("--train_episodes", type = int, default = 1000,
                        help = "Number of episodes")
    parser.add_argument("--eval_every", type = int, default = 10,
                        help = "Evaluate policy every ... games.")
    parser.add_argument("--eval_episodes", type = int, default = 5,
                        help = "Number of games to play for evaluation.")
                        
    # Display
    parser.add_argument("--verbose", dest="verbose",
                        action = "store_true", help = "Print each state")
    parser.add_argument("--term", dest="term",
                        action = "store_true", help = "Print to terminal")                        
    parser.add_argument("--plot", dest="plot_scores", action="store_true",
                        help = "Plot scores in the end")
    parser.add_argument("--sleep", type = float, default = 0.1,
                        help = "Seconds to 'sleep' between moves.")
    parser.add_argument("--final_show", dest = "final_show",
                        action = "store_true",
                        help = "Demonstrate final strategy.")
                        
    globals.args = parser.parse_args()
    q_learning()
    
    