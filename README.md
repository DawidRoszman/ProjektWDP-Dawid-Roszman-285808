Podstawa projektu - https://github.com/techwithtim/Network-Game-Tutorial

Grafika - https://opengameart.org/content/space-shooter-art

Inspiracja na grę - https://www.youtube.com/watch?v=AlCJc05nkwc

![Pomysł na gre](320744117_5722551721127289_3582924636103691263_n.png)

# Instruction

## Keybinds

- W - move up
- D - move right
- S - move down
- A - move left
- LMB - shoot ( not impelemnted yet )
- RMB, Space - Dash ( not impelented yet )

## Running Game

One computer on local network must run server.py and the others need to execute run.py
It is recommended to use virtualenv and install packages using pip install -r requirements.txt.

## Game Description

In this game, players can earn points by shooting the second player. The player with the highest score at the end of the round is declared the winner. If a player is killed, a new round begins on a randomly selected map. The game continues until one player reaches 5 points, at which point they are declared the winner.
