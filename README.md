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

### The Render Pipeline

Recurface objects each store a render pipeline which dictates the steps carried out in that specific object's render process. The default
pipeline simply applies the surfaces from child recurfaces to the current object's surface, and then caches that composited surface for re-use
next frame if no changes which affect the rendered image are made in the interim; this will not require customisation in most cases.

Through this rendering pipeline it is possible to apply filters which make last-minute modifications to a recurface's surface when it is being
rendered - this can include pasting additional layers onto the working copy of the surface, scaling and rotating it, etc.

<img src="res/render_pipeline.png" alt="A diagram of an example configuration for a render pipeline, showing how each item in the pipeline is applied to the stored surface in order during rendering. Featured pipeline items are visual filters, flags to cache the working surface, and a flag to apply the child recurfaces">

Filters can be created by importing the PipelineFilter class, and passing a function which receives and returns a surface object into its constructor:

```python
from recurfaces import Recurface, PipelineFilter, PipelineFlag


def red_fill(surface):
    surface.fill("red")
    return surface


# Filter is deterministic because this particular function will always modify a given surface in the exact same way
filter_red_fill = PipelineFilter(red_fill, is_deterministic=True)

my_recurface = Recurface(
    render_pipeline = [PipelineFlag.APPLY_CHILDREN, filter_red_fill, PipelineFlag.CACHE_SURFACE]
)
```

- Since the render pipeline is applied to the recurface's stored surface, any recurfaces which themselves have no surface will not implement
  their pipeline during rendering

## General Guidelines

The recurfaces library is designed such that when a top-level recurface is rendered to a destination, the entire chain underneath it is
handled automatically. In order for this to function seamlessly, it is highly recommended to observe the following rules:

- Only one chain of recurfaces should be rendered to each external destination. If you have two or more separate chains
  that you want to render to a single destination, merge them by making a new blank recurface
  (no surface, and a `.render_position` of `(0, 0)`) and adding them both as children of that recurface
- If, during runtime, you wish to change the render destination of a top-level recurface to a new destination, or wish to make visual modifications
  to the render destination through means other than via that recurface chain (resizing it, rendering other surfaces to it etc.),
  call `.flag_destination()` on the top-level recurface to notify it of the changes to its destination before its next render
  - This is not necessary if you are attaching a previously top-level recurface as a child on a different recurface chain, rather than directly rendering that
    recurface to a new destination
  - Once a recurface is no longer rendering to a destination, that destination will have to be managed manually from that point onwards if it remains in use. 
    If (for example) a new recurface will be rendered to it, the destination must first be cleared and updated manually
- If you are modifying a recurface's stored surface in place (rather than replacing it outright), call `.flag_surface()` on that recurface to notify it
  of these modifications before it is next rendered

## Optimisation Tips

- In cases where a large amount of moving recurfaces are being rendered, and a portion of them will be offscreen in any given frame,
  it is highly recommended to determine which will be offscreen on the next frame and set them not to render at all (this can be done by
  setting `.do_render` to False). 
  Similarly, it is highly recommended to break up singular very large surfaces which will frequently be even partially offscreen into
  multiple smaller surfaces if possible, and implement the same offscreen checks to determine which should be set to not render
  - Because recurfaces composite their surfaces during rendering by copying their stored surfaces or cached surfaces, there is some overhead
    associated with rendering images even when they are mostly or fully offscreen, and this overhead becomes significant for large amounts
    of offscreen surface area (whether through singularly large surfaces, or through many smaller surfaces). 
    This makes it very important to implement smart usage of `.do_render` to prevent offscreen objects from tanking performance
- To make the best use of the surface caching system, it is recommended to organise a recurface chain into branches
  such that each branch contains a set of surfaces which are unlikely to frequently change relative to one another
  - In the recurface chain represented by the illustration in [Structuring your Recurfaces](#structuring-your-recurfaces),
    There are 3 branches under the 'root' top-level recurface. The first branch (skybox and mountains) contains only
    surfaces which both do not move at all during gameplay, and so can be cached together. The second branch (forest and ground)
    contains surfaces which scroll when the location of the player changes, but are both scrolled together and thus do not
    move relative to one another, so can be cached together. The third branch contains only the player, as the player's surface
    always changes in a way which does not match the other surfaces in the scene, and so does not benefit from being cached alongside them.
  - Fewer and larger branches is better *as long as* none of the surfaces in a particular branch frequently move in relation to
    the other surfaces contained in that branch, or frequently change when the others remain static, as larger branches allow
    more surfaces to be cached together; in each branch of a chain, any frequently updated surface represents a caching bottleneck
    for all of its parents further up that chain - the goal should be to have the fewest and largest branches as possible *after*
    separating out these bottlenecks
  - This approach to structuring recurface chains yields its biggest returns when it is used to separate out small,
    frequently modified/moved surfaces from branches which contain large, infrequently modified surfaces. The bigger the
    differences in size and update frequency between these surfaces, the larger the performance boost
  - Since recurfaces which do not have a stored surface do not cache a surface, in order for sibling recurfaces to be cached together
    they must be under a mutual parent somewhere further up the chain which has a surface of its own. This can even be a completely
    blank surface, although adding an additional blank surface into the chain will come with associated overhead (particularly if
    that surface is much larger than the surfaces being pasted onto it) and may be worse for performance than not caching
    the sibling recurfaces together at all. The optimal approach will vary depending on each use case
