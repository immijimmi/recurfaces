# recurfaces

###### A pygame framework used to organise Surfaces into a chain structure

## Quickstart

Below is an example of recurfaces being used in a basic game loop. When it is run, the game window will display a red square on a white background,
movable by tapping the arrow keys.

```python
import pygame

from recurfaces import Recurface


# pygame setup
pygame.init()
window = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Creating some recurfaces to display
bg_surface = pygame.Surface((800, 600))
bg_surface.fill("#FFFFFF")
scene = Recurface(surface=bg_surface)  # This is the top-level recurface, and also holds the background surface

red_square_surface = pygame.Surface((64, 64))
red_square_surface.fill("#FF0000")
red_square = Recurface(surface=red_square_surface, position=(100, 100))

scene.add_child_recurface(red_square)

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

    red_square.move_render_position(*move)
    move = [0, 0]

    # Rendering the updated recurfaces
    updated_rects = scene.render(window)
    pygame.display.update(updated_rects)
```

## Structuring Your Recurfaces

Recurfaces are designed to be linked together into chains, and organised broadly into an inverted tree shape; starting with a single
top-level recurface, and branching out at various points into multiple descendants. They are rendered top-down in this structure,
meaning that the parent's surface is rendered onto the window before (and therefore layered underneath) its direct childrens' surfaces.

Siblings under a common parent are rendered in order of their `.priority` attribute - if priority values which support rich comparison with each other
have not been set for all sibling recurfaces under a particular parent, their render order amongst each other will be arbitrary.

<img src="res/tree_structure.png" alt="A diagram of a branching structure of recurfaces, illustrating that recurfaces containing surfaces that are moved together should preside within the same branch">

A recurface's surface is confined to the area covered by its parent's surface - it can be repositioned out of bounds, or hold a larger
surface than its parent, but when it is rendered any part of it which is not within its parent's surface area will not appear onscreen.

Only one chain of recurfaces should be rendered to each external destination. If you have two or more separate chains  that you want to render
to a single destination, merge them by making a new blank recurface (no surface, and a `.render_position` of `(0, 0)`) and adding both chains
as children of that recurface.
