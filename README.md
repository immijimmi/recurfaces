# recurfaces

###### A pygame framework used to organise Surfaces into a chain structure

## Quickstart

Below is an example of recurfaces being used in a basic game loop.
The screen will display a red square on a white background, movable by tapping the arrow keys.

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
scene = Recurface(surface=bg_surface, position=(0, 0))  # This will be the top-level recurface

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

    red_square.x_render_position += move[0]
    red_square.y_render_position += move[1]
    move = [0, 0]

    # Rendering the updated recurfaces
    updated_rects = scene.render(window)
    pygame.display.update(updated_rects)
```

## Functionality

### Properties

Recurface.**surface**  
&nbsp;&nbsp;&nbsp;&nbsp;Returns a reference to the recurface's stored surface.  
&nbsp;&nbsp;&nbsp;&nbsp;This surface does not get altered by Recurface - a working copy of it is made on each render.  
&nbsp;

Recurface.**render_position**
&nbsp;&nbsp;&nbsp;&nbsp;Returns a tuple of the surface's display position within its container.  
&nbsp;&nbsp;&nbsp;&nbsp;This can be set to `None` in order to stop displaying the surface entirely.  
&nbsp;

Recurface.**x_render_position**, Recurface.**y_render_position**
&nbsp;&nbsp;&nbsp;&nbsp;These properties access their respective indexes of `.render_position`.

*Note: If `.render_position` is currently set to `None`, accessing these will throw a ValueError.*
&nbsp;

Recurface.**parent_recurface**
&nbsp;&nbsp;&nbsp;&nbsp;Returns the container recurface, or `None` if this recurface is top-level.  
&nbsp;&nbsp;&nbsp;&nbsp;Can be set to a new parent recurface, or `None` to make the current recurface top-level.  
&nbsp;&nbsp;&nbsp;&nbsp;Equivalent to calling `remove_child_recurface()` on the current parent and
&nbsp;&nbsp;&nbsp;&nbsp;`add_child_recurface()` on the new parent.
&nbsp;

Recurface.**child_recurfaces**
&nbsp;&nbsp;&nbsp;&nbsp;Returns a frozenset containing all child recurfaces of the accessed recurface. Read-only.

### Methods

Recurface.**add_child_recurface**(*self, child: Recurface*)
&nbsp;&nbsp;&nbsp;&nbsp;Adds the provided recurface to the current recurface's children.  
&nbsp;&nbsp;&nbsp;&nbsp;Equivalent to setting `.parent_recurface` on the child recurface equal to the current recurface.
&nbsp;

Recurface.**remove_child_recurface**(*self, child: Recurface*)
&nbsp;&nbsp;&nbsp;&nbsp;Removes the provided recurface from the current recurface's children.  
&nbsp;&nbsp;&nbsp;&nbsp;Equivalent to setting `.parent_recurface` on the child recurface equal to `None`.

*Note: This will make the child top-level; It will be garbage collected if there are no references to it elsewhere.*  
&nbsp;

Recurface.**move_render_position**(*self, x_offset: int = 0, y_offset: int = 0*)
&nbsp;&nbsp;&nbsp;&nbsp;Adds the provided offset values to the recurface's current position.  
&nbsp;&nbsp;&nbsp;&nbsp;Returns a tuple representing the updated `.position`.

*Note: If `.render_position` is currently set to `None`, this will throw a ValueError.*
&nbsp;

Recurface.**add_update_rects**(*self, rects: Iterable[Optional[Rect]], update_position: bool = False*)
&nbsp;&nbsp;&nbsp;&nbsp;Stores the provided pygame rects to be returned by this recurface on the next `render()` call.  
&nbsp;&nbsp;&nbsp;&nbsp;Used internally to handle removing child objects.  
&nbsp;&nbsp;&nbsp;&nbsp;If `update_position` is `True`, the provided rects will be offset by the position of `.__rect` before storing.  
&nbsp;

Recurface.**render**(*self, destination: Surface*)
&nbsp;&nbsp;&nbsp;&nbsp;Draws all child surfaces to a copy of `.surface`, then draws the copy to the provided destination.  
&nbsp;&nbsp;&nbsp;&nbsp;Returns a list of pygame rects representing updated areas of the provided destination.

*Note: This function should be called on top-level (parent-less) recurfaces once per game tick, and `pygame.display.update()` should be passed all returned rects.*  
&nbsp;

Recurface.**unlink**(*self*)
&nbsp;&nbsp;&nbsp;&nbsp;Detaches the recurface from its parent and children.  
&nbsp;&nbsp;&nbsp;&nbsp;If there is a parent recurface, all children are added to the parent.  
&nbsp;&nbsp;&nbsp;&nbsp;This effectively removes the recurface from its place in the chain without leaving the chain broken.  
&nbsp;
