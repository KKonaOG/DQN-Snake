from game import Game as SnakeGame
import matplotlib.pyplot as plt

if __name__ == "__main__":
    snakeGame = SnakeGame()
    record = 0
    number_games = 0
    total_scores = []
    display = False
    forceDisplay = False
    scores = []
    while True:
        number_games += 1
        if (forceDisplay):
            display = True
            forceDisplay = False
        else:
            display = False
            
        snakes = snakeGame.play(display)
        for snake in snakes:
            if (snake.length > record):
                print(f"New Record: {snake.length}")
                best_snake = snake
            record = max(record, snake.length)
            snake.model.save(f"models/snake_{snake.id}.model")
        
        scores.append(sum([snake.length for snake in snakes])/2)
        
        # Print Game Information
        if (not display):
            print(f"Game #: {number_games} Record: {record} Turns: {snakeGame.turn}")
            for snake in snakes:
                print(f"Snake {snake.id} Score: {snake.length}")
        
    
        # Plot average scores every 10 games
        if number_games % 100 == 0:
            forceDisplay = True
            total_scores.append(sum(scores)/len(scores))
            scores = []
            plt.clf()
            plt.plot(total_scores)
            plt.ylabel('Average Score')
            plt.xlabel('Number of Games (100 games per point)')
            plt.savefig("scores.png")