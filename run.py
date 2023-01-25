import game

if __name__ == "__main__":
    host = input("\nEnter host address (leave blank for default): ")
    g = game.Game(1000, 800, host)
    g.run()
