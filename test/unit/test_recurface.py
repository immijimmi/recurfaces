import pytest
from pygame import Surface, Rect

from recurfaces import Recurface


@pytest.fixture
def res():
    class RecurfaceResources:
        surface_bg = Surface((800, 600))
        surface_1 = Surface((300, 200))
        surface_2 = Surface((100, 300))
        surface_3 = Surface((70, 60))

        recurface_no_position = Recurface(surface_1)
        recurface_1 = Recurface(surface=surface_1, position=(10, 20))
        recurface_2 = Recurface(surface=surface_2, position=(30, 40))
        recurface_3 = Recurface(surface=surface_3, position=(50, 60))
        recurface_no_surface = Recurface(position=(10, 20))

    return RecurfaceResources


class TestRecurface:
    def test_no_position_on_first_render_returns_no_rects(self, res):
        rects = res.recurface_no_position.render(res.surface_bg)

        assert rects == []

    def test_first_valid_render_returns_correct_rects(self, res):
        rects = res.recurface_1.render(res.surface_bg)

        assert rects == [Rect(10, 20, 300, 200)]

    def test_move_position_after_render_returns_correct_rects(self, res):
        res.recurface_1.render(res.surface_bg)

        res.recurface_1.move_render_position(15, 30)
        res.recurface_1.x_render_position += 3
        res.recurface_1.y_render_position += 6
        rects = res.recurface_1.render(res.surface_bg)

        assert rects == [Rect(10, 20, 300, 200), Rect(28, 56, 300, 200)]

    def test_position_none_after_render_returns_correct_rects(self, res):
        res.recurface_1.render(res.surface_bg)

        res.recurface_1.render_position = None
        rects = res.recurface_1.render(res.surface_bg)

        assert rects == [Rect(10, 20, 300, 200)]

    def test_new_surface_after_render_returns_correct_rects(self, res):
        res.recurface_1.render(res.surface_bg)

        res.recurface_1.surface = res.surface_2
        rects = res.recurface_1.render(res.surface_bg)

        assert rects == [Rect(10, 20, 300, 200), Rect(10, 20, 100, 300)]

    def test_new_contained_surface_after_render_returns_correct_rects(self, res):
        res.recurface_1.render(res.surface_bg)

        res.recurface_1.surface = res.surface_3
        rects = res.recurface_1.render(res.surface_bg)

        assert rects == [Rect(10, 20, 300, 200)]

    def test_new_attributes_after_render_returns_correct_rects(self, res):
        res.recurface_1.render(res.surface_bg)

        res.recurface_1.surface = res.surface_2
        res.recurface_1.render_position = (40, 30)
        res.recurface_1.add_child_recurface(res.recurface_2)
        rects = res.recurface_1.render(res.surface_bg)

        assert rects == [Rect(10, 20, 300, 200), Rect(40, 30, 100, 300)]

    def test_add_update_rects_are_returned_next_render(self, res):
        res.recurface_1.render(res.surface_bg)

        res.recurface_1.add_update_rects(Rect(1, 2, 3, 4))
        rects = res.recurface_1.render(res.surface_bg)

        assert rects == [Rect(1, 2, 3, 4)]

        res.recurface_1.add_update_rects(Rect(1, 2, 3, 4), do_update_position=True)
        rects = res.recurface_1.render(res.surface_bg)

        assert rects == [Rect(11, 22, 3, 4)]

    def test_add_child_after_child_updated_returns_correct_rects(self, res):
        res.recurface_1.render(res.surface_bg)

        res.recurface_2.render(res.surface_bg)
        res.recurface_2.render_position = (40, 50)

        res.recurface_1.add_child_recurface(res.recurface_2)  # This will reset recurface_2
        rects = res.recurface_1.render(res.surface_bg)

        assert rects == [Rect(50, 70, 100, 150)]

    def test_remove_child_after_child_updated_returns_correct_rects(self, res):
        res.recurface_1.add_child_recurface(res.recurface_2)
        res.recurface_1.render(res.surface_bg)

        res.recurface_2.render_position = (40, 50)  # Should have no effect on returned rects, since this has not been rendered yet
        res.recurface_1.remove_child_recurface(res.recurface_2)
        rects = res.recurface_1.render(res.surface_bg)

        assert rects == [Rect(40, 60, 100, 160)]

    def test_unlink_ties_children_to_parent(self, res):
        res.recurface_1.add_child_recurface(res.recurface_2)
        res.recurface_2.add_child_recurface(res.recurface_3)

        assert [*res.recurface_1.child_recurfaces] == [res.recurface_2] and [*res.recurface_2.child_recurfaces] == [res.recurface_3]

        res.recurface_2.unlink()

        assert [*res.recurface_1.child_recurfaces] == [res.recurface_3] and res.recurface_3.parent_recurface == res.recurface_1

    def test_unlink_returns_correct_rects(self, res):
        res.recurface_1.render(res.surface_bg)

        res.recurface_1.add_child_recurface(res.recurface_2)
        res.recurface_2.add_child_recurface(res.recurface_3)
        res.recurface_2.move_render_position(4, 5)

        res.recurface_2.unlink()
        rects = res.recurface_1.render(res.surface_bg)

        assert rects == [Rect(94, 125, 70, 60)]

    def test_no_surface_on_first_render_returns_no_rects(self, res):
        rects = res.recurface_no_surface.render(res.surface_bg)

        assert rects == []

    def test_copy_surface_with_no_surface_raises_valueerror(self, res):
        assert pytest.raises(ValueError, res.recurface_no_surface.generate_surface_copy)
