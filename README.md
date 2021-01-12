# recurfaces

###### A pygame framework used to organise Surfaces into a chain structure

### Example Game Boilerplate
```python
import pygame
from recurfaces import Recurface


# pygame setup
pygame.init()
window = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Creating some recurfaces to display
bg__surface = pygame.Surface((800, 600))
bg__surface.fill("#FFFFFF")
scene = Recurface(bg__surface, (0, 0))  # This will be the top-level recurface

red_square__surface = pygame.Surface((64, 64))
red_square__surface.fill("#FF0000")
red_square = Recurface(red_square__surface, (100, 100))

scene.add_child(red_square)

# Game loop
move = [0, 0]
while True:
    clock.tick(60)

    # Moving the red square based on input
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                move[1] -= 1
            elif event.key == pygame.K_DOWN:
                move[1] += 1
            elif event.key == pygame.K_LEFT:
                move[0] -= 1
            elif event.key == pygame.K_RIGHT:
                move[0] += 1

    red_square.x += move[0]
    red_square.y += move[1]
    move = [0, 0]

    # Rendering the updated recurfaces
    updated_rects = scene.render(window)
    pygame.display.update(updated_rects)
```
