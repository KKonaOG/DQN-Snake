from game import Game as SnakeGame
import matplotlib.pyplot as plt
import copy

if __name__ == "__main__":
    snakeGame = SnakeGame()
    record = 0
    number_games = 0
    total_scores = []
    total_turns = []
    display = False
    forceDisplay = False
    scores = []
    turns = []
    
    
    best_snake = None
    while True:
        number_games += 1
        snakes = snakeGame.play(display)
        
        total_length = sum([snake.length for snake in snakes])
            
        if (total_length > record):
            print(f"New Record: {total_length}")
            record = total_length
            
            # Save snake models
            for snake in snakes:
                snake.model.save(f"models/snake_{snake.id}.model")
                
        scores.append(sum([snake.length for snake in snakes]) / len(snakes))
        turns.append(snakeGame.turn)
        
        # Print Game Information
        if (not display):
            print(f"Game #: {number_games} Record: {record} Turns: {snakeGame.turn}")
            for snake in snakes:
                print(f"Snake {snake.id} Score: {snake.length}")
        
        # Plot average scores every 100 games
        if number_games % 100 == 0:
            forceDisplay = True
            total_scores.append(sum(scores)/len(scores))
            total_turns.append(sum(turns)/len(turns))
            
            turns = []
            scores = []
            
            plt.clf()
            plt.plot(total_scores)
            plt.ylabel('Average Snake Length')
            plt.xlabel('Number of Games (100 games per point)')
            plt.savefig("scores.png")
            
            plt.clf()
            plt.plot(total_turns)
            plt.ylabel('Average Turns Per Game')
            plt.xlabel('Number of Games (100 games per point)')
            plt.savefig("turns.png")
            
            
            