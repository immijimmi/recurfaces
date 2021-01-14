from pygame import Surface

from ...recurface import Recurface


def test_no_position_on_first_render_returns_no_rects():
    surface_bg = Surface((800, 600))
    surface_1 = Surface((300, 300))

    recurface = Recurface(surface_1)
    rects = recurface.render(surface_bg)

    assert rects == []


def test_first_valid_render_returns_correct_rect():
    surface_bg = Surface((800, 600))
    surface_1 = Surface((300, 300))

    recurface = Recurface(surface_1, (0, 0))
    rects = recurface.render(surface_bg)

    assert rects == [surface_1.get_rect()]


def test_no_position_once_rendered_returns_previous_rect():
    surface_bg = Surface((800, 600))
    surface_1 = Surface((300, 300))

    recurface = Recurface(surface_1, (0, 0))
    recurface.render(surface_bg)

    recurface.position = None
    rects = recurface.render(surface_bg)

    assert rects == [surface_1.get_rect()]


def test_new_surface_once_rendered_returns_both_surface_rects():
    surface_bg = Surface((800, 600))
    surface_1 = Surface((300, 300))
    surface_2 = Surface((200, 200))

    recurface = Recurface(surface_1, (0, 0))
    recurface.render(surface_bg)

    recurface.surface = surface_2
    rects = recurface.render(surface_bg)

    assert rects == [surface_1.get_rect(), surface_2.get_rect()]
