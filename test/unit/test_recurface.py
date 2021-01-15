from pygame import Surface, Rect

from ...recurface import Recurface


def test_no_position_on_first_render_returns_no_rects():
    surface_bg = Surface((800, 600))
    surface_1 = Surface((300, 200))

    recurface = Recurface(surface_1)
    rects = recurface.render(surface_bg)

    assert rects == []


def test_first_valid_render_returns_correct_rects():
    surface_bg = Surface((800, 600))
    surface_1 = Surface((300, 200))

    recurface = Recurface(surface_1, (10, 20))
    rects = recurface.render(surface_bg)

    assert rects == [Rect(10, 20, 300, 200)]


def test_position_none_after_rendered_returns_correct_rects():
    surface_bg = Surface((800, 600))
    surface_1 = Surface((300, 200))

    recurface = Recurface(surface_1, (10, 20))
    recurface.render(surface_bg)

    recurface.position = None
    rects = recurface.render(surface_bg)

    assert rects == [Rect(10, 20, 300, 200)]


def test_new_surface_after_rendered_returns_correct_rects():
    surface_bg = Surface((800, 600))
    surface_1 = Surface((300, 200))
    surface_2 = Surface((200, 400))

    recurface = Recurface(surface_1, (10, 20))
    recurface.render(surface_bg)

    recurface.surface = surface_2
    rects = recurface.render(surface_bg)

    assert rects == [Rect(10, 20, 300, 200), Rect(10, 20, 200, 400)]


def test_new_surface_and_position_after_rendered_returns_correct_rects():
    surface_bg = Surface((800, 600))
    surface_1 = Surface((300, 200))
    surface_2 = Surface((200, 400))

    recurface = Recurface(surface_1, (10, 20))
    recurface.render(surface_bg)

    recurface.surface = surface_2
    recurface.position = (40, 30)
    rects = recurface.render(surface_bg)

    assert rects == [Rect(10, 20, 300, 200), Rect(40, 30, 200, 400)]


def test_add_update_rects_are_returned_next_render():
    surface_bg = Surface((800, 600))
    surface_1 = Surface((300, 200))

    recurface = Recurface(surface_1, (10, 20))
    recurface.add_update_rects([Rect(1, 2, 3, 4)])
    rects = recurface.render(surface_bg)

    assert rects == [Rect(1, 2, 3, 4), Rect(10, 20, 300, 200)]

    recurface.add_update_rects([Rect(1, 2, 3, 4)], update_position=True)
    rects = recurface.render(surface_bg)

    assert rects == [Rect(11, 22, 3, 4)]


def test_add_child_after_child_updated_returns_correct_rects():
    surface_bg = Surface((800, 600))
    surface_1 = Surface((300, 200))
    surface_2 = Surface((100, 80))

    recurface_1 = Recurface(surface_1, (10, 20))
    recurface_2 = Recurface(surface_2, (30, 40))
    recurface_2.render(surface_bg)
    recurface_2.position = (40, 50)

    recurface_1.add_child(recurface_2)  # This will reset recurface_2
    rects = recurface_1.render(surface_bg)

    assert rects == [Rect(50, 70, 100, 80), Rect(10, 20, 300, 200)]


def test_remove_child_after_child_updated_returns_correct_rects():
    surface_bg = Surface((800, 600))
    surface_1 = Surface((300, 200))
    surface_2 = Surface((100, 80))

    recurface_1 = Recurface(surface_1, (10, 20))
    recurface_2 = Recurface(surface_2, (30, 40))
    recurface_1.add_child(recurface_2)
    recurface_1.render(surface_bg)

    recurface_2.position = (40, 50)
    recurface_1.remove_child(recurface_2)
    rects = recurface_1.render(surface_bg)

    assert rects == [Rect(40, 60, 100, 80)]


def test_unlink_ties_children_to_parent():
    surface_bg = Surface((800, 600))
    surface_1 = Surface((300, 200))
    surface_2 = Surface((100, 80))
    surface_3 = Surface((70, 60))

    recurface_1 = Recurface(surface_1, (10, 20))
    recurface_2 = Recurface(surface_2, (30, 40))
    recurface_3 = Recurface(surface_2, (50, 60))

    recurface_1.add_child(recurface_2)
    recurface_2.add_child(recurface_3)

    assert [*recurface_1.children] == [recurface_2] and [*recurface_2.children] == [recurface_3]

    recurface_2.unlink()

    assert [*recurface_1.children] == [recurface_3] and recurface_3.parent == recurface_1
