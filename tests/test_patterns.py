from orbispanora_lib.anvil import Block
from orbispanora_lib.patterns.cube import Cube
from orbispanora_lib.patterns.figure import Figure
from orbispanora_lib.patterns.pyramid import Pyramid
from orbispanora_lib.patterns.sphere import Sphere
from orbispanora_lib.patterns.spiral import Spiral


class TestPatterns:

    def test_figure_init(self):
        blocks = [Block('stone'), Block('dirt')]
        point = (0, 0, 0)
        size = (10, 10, 10)

        figure = Figure(blocks, point, size)

        assert figure.blocks == blocks
        assert figure.point == point
        assert figure.size == size

    def test_figure_empty_not_implemented(self):
        figure = Figure([Block('stone')], (0, 0, 0), (10, 10, 10))

        try:
            figure.empty()
            assert False, "Should have raised NotImplementedError"
        except NotImplementedError:
            pass

    def test_figure_filled_not_implemented(self):
        figure = Figure([Block('stone')], (0, 0, 0), (10, 10, 10))

        try:
            figure.filled()
            assert False, "Should have raised NotImplementedError"
        except NotImplementedError:
            pass

    def test_cube_init(self):
        blocks = [Block('stone')]
        point = (0, 0, 0)
        size = (5, 5, 5)

        cube = Cube(blocks, point, size)

        assert cube.blocks == blocks
        assert cube.point == point
        assert cube.size == size

    def test_cube_empty_returns_dict(self):
        cube = Cube([Block('stone')], (0, 0, 0), (5, 5, 5))
        result = cube.empty()

        assert isinstance(result, dict)

    def test_cube_empty_hollow(self):
        cube = Cube([Block('stone')], (0, 0, 0), (5, 5, 5))
        result = cube.empty()

        assert (2, 2, 2) not in result
        assert (0, 0, 0) in result

    def test_cube_filled_returns_dict(self):
        cube = Cube([Block('stone')], (0, 0, 0), (5, 5, 5))
        result = cube.filled()

        assert isinstance(result, dict)

    def test_cube_filled_contains_all_blocks(self):
        size = (5, 5, 5)
        cube = Cube([Block('stone')], (0, 0, 0), size)
        result = cube.filled()

        expected_count = size[0] * size[1] * size[2]
        assert len(result) == expected_count
        assert (2, 2, 2) in result

    def test_cube_with_offset(self):
        cube = Cube([Block('stone')], (10, 20, 30), (3, 3, 3))
        result = cube.filled()

        assert (10, 20, 30) in result
        assert (12, 22, 32) in result

    def test_cube_multiple_blocks(self):
        blocks = [Block('stone'), Block('dirt'), Block('wood')]
        cube = Cube(blocks, (0, 0, 0), (4, 4, 4))
        result = cube.filled()

        for block in result.values():
            assert block.id in ['stone', 'dirt', 'wood']

    def test_pyramid_init(self):
        blocks = [Block('sandstone')]
        point = (0, 0, 0)
        size = (10, 5, 10)

        pyramid = Pyramid(blocks, point, size)

        assert pyramid.blocks == blocks
        assert pyramid.point == point
        assert pyramid.size == size

    def test_pyramid_empty_returns_dict(self):
        pyramid = Pyramid([Block('sandstone')], (0, 0, 0), (10, 5, 10))
        result = pyramid.empty()

        assert isinstance(result, dict)

    def test_pyramid_filled_returns_dict(self):
        pyramid = Pyramid([Block('sandstone')], (0, 0, 0), (10, 5, 10))
        result = pyramid.filled()

        assert isinstance(result, dict)

    def test_pyramid_decreases_with_height(self):
        pyramid = Pyramid([Block('sandstone')], (0, 0, 0), (10, 5, 10))
        result = pyramid.filled()

        bottom_blocks = [k for k in result.keys() if k[1] == 0]
        top_blocks = [k for k in result.keys() if k[1] == 4]

        assert len(bottom_blocks) > len(top_blocks)

    def test_pyramid_with_offset(self):
        pyramid = Pyramid([Block('sandstone')], (5, 10, 15), (8, 4, 8))
        result = pyramid.filled()

        assert len(result) > 0
        for pos in result.keys():
            assert pos[0] >= 5
            assert pos[1] >= 10
            assert pos[2] >= 15

    def test_sphere_init(self):
        blocks = [Block('glass')]
        point = (0, 0, 0)
        size = (10, 10, 10)

        sphere = Sphere(blocks, point, size)

        assert sphere.blocks == blocks
        assert sphere.point == point
        assert sphere.size == size

    def test_sphere_empty_returns_dict(self):
        sphere = Sphere([Block('glass')], (0, 0, 0), (10, 10, 10))
        result = sphere.empty()

        assert isinstance(result, dict)

    def test_sphere_filled_returns_dict(self):
        sphere = Sphere([Block('glass')], (0, 0, 0), (10, 10, 10))
        result = sphere.filled()

        assert isinstance(result, dict)

    def test_sphere_empty_is_hollow(self):
        sphere = Sphere([Block('glass')], (0, 0, 0), (10, 10, 10))
        result = sphere.empty()

        assert (5, 5, 5) not in result

    def test_sphere_filled_has_more_blocks_than_empty(self):
        size = (12, 12, 12)
        sphere_empty = Sphere([Block('glass')], (0, 0, 0), size)
        sphere_filled = Sphere([Block('glass')], (0, 0, 0), size)

        result_empty = sphere_empty.empty()
        result_filled = sphere_filled.filled()

        assert len(result_filled) > len(result_empty)

    def test_sphere_ellipsoid(self):
        sphere = Sphere([Block('glass')], (0, 0, 0), (10, 5, 10))
        result = sphere.filled()

        assert len(result) > 0

    def test_sphere_with_offset(self):
        sphere = Sphere([Block('glass')], (20, 30, 40), (8, 8, 8))
        result = sphere.filled()

        assert len(result) > 0
        for pos in result.keys():
            assert pos[0] >= 20
            assert pos[1] >= 30
            assert pos[2] >= 40

    def test_spiral_init(self):
        blocks = [Block('gold_block')]
        point = (0, 0, 0)
        size = (20, 30, 20)

        spiral = Spiral(blocks, point, size)

        assert spiral.blocks == blocks
        assert spiral.point == point
        assert spiral.size == size

    def test_spiral_empty_returns_dict(self):
        spiral = Spiral([Block('gold_block')], (0, 0, 0), (20, 30, 20))
        result = spiral.empty()

        assert isinstance(result, dict)

    def test_spiral_filled_returns_dict(self):
        spiral = Spiral([Block('gold_block')], (0, 0, 0), (20, 30, 20))
        result = spiral.filled()

        assert isinstance(result, dict)

    def test_spiral_generates_blocks(self):
        spiral = Spiral([Block('gold_block')], (0, 0, 0), (20, 30, 20))
        result = spiral.filled()

        assert len(result) > 0

    def test_spiral_get_path(self):
        spiral = Spiral([Block('gold_block')], (0, 0, 0), (20, 30, 20))
        path = spiral.get_path()

        assert isinstance(path, str)
        assert len(path) > 0
        assert 'spiral.py' in path.lower()

    def test_spiral_with_different_sizes(self):
        spiral1 = Spiral([Block('gold_block')], (0, 0, 0), (10, 50, 10))
        result1 = spiral1.filled()
        assert len(result1) > 0

        spiral2 = Spiral([Block('gold_block')], (0, 0, 0), (30, 10, 30))
        result2 = spiral2.filled()
        assert len(result2) > 0

    def test_spiral_with_offset(self):
        spiral = Spiral([Block('gold_block')], (10, 20, 30), (20, 30, 20))
        result = spiral.filled()

        assert len(result) > 0
        for pos in result.keys():
            assert pos[0] >= 10
            assert pos[1] >= 20
            assert pos[2] >= 30

    def test_spiral_empty_equals_filled(self):
        spiral = Spiral([Block('gold_block')], (0, 0, 0), (20, 30, 20))
        result_empty = spiral.empty()
        result_filled = spiral.filled()

        assert len(result_empty) == len(result_filled)

    def test_all_patterns_with_same_parameters(self):
        blocks = [Block('stone')]
        point = (0, 0, 0)
        size = (10, 10, 10)

        cube = Cube(blocks, point, size)
        pyramid = Pyramid(blocks, point, size)
        sphere = Sphere(blocks, point, size)
        spiral = Spiral(blocks, point, size)

        assert len(cube.filled()) > 0
        assert len(pyramid.filled()) > 0
        assert len(sphere.filled()) > 0
        assert len(spiral.filled()) > 0

    def test_patterns_return_valid_blocks(self):
        blocks = [Block('diamond_block'), Block('emerald_block')]
        patterns = [
            Cube(blocks, (0, 0, 0), (5, 5, 5)),
            Pyramid(blocks, (0, 0, 0), (8, 4, 8)),
            Sphere(blocks, (0, 0, 0), (6, 6, 6)),
            Spiral(blocks, (0, 0, 0), (10, 15, 10))
        ]

        for pattern in patterns:
            result = pattern.filled()
            for block in result.values():
                assert isinstance(block, Block)
                assert block.id in ['diamond_block', 'emerald_block']

    def test_patterns_respect_boundaries(self):
        blocks = [Block('iron_block')]
        point = (5, 10, 15)
        size = (8, 8, 8)

        patterns = [
            Cube(blocks, point, size),
            Pyramid(blocks, point, size),
            Sphere(blocks, point, size),
            Spiral(blocks, point, size)
        ]

        for pattern in patterns:
            result = pattern.filled()
            for pos in result.keys():
                assert pos[0] >= point[0]
                assert pos[1] >= point[1]
                assert pos[2] >= point[2]
                assert pos[0] < point[0] + size[0]
                assert pos[1] < point[1] + size[1]
                assert pos[2] < point[2] + size[2]
