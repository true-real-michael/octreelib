import numpy as np

from octreelib.grid import StaticGrid, StaticGridConfig
from octreelib.octree import Octree, OctreeConfig

__all__ = ["test_basic_flow"]


def test_basic_flow():
    grid = StaticGrid(StaticGridConfig(Octree, OctreeConfig()))
    points_0 = [
        np.array([0, 0, 1]),
        np.array([0, 0, 2]),
        np.array([0, 0, 3]),
        np.array([9, 9, 8]),
        np.array([9, 9, 9]),
    ]
    grid.insert_points(0, points_0)
    points_1 = [
        np.array([1, 0, 1]),
        np.array([4, 0, 2]),
        np.array([0, 2, 3]),
        np.array([9, 3, 8]),
        np.array([5, 9, 9]),
    ]
    grid.insert_points(1, points_1)

    assert 1 == grid.octrees[0].n_leafs
    assert 1 == grid.octrees[1].n_leafs

    grid.subdivide([lambda points: len(points) > 2])

    assert 22 == grid.octrees[0].n_leafs
    assert 15 == grid.octrees[1].n_leafs

    p0 = grid.get_points(0)
    p1 = grid.get_points(1)

    assert set(map(str, list(p0))) == set(map(str, list(points_0)))
    assert set(map(str, list(p1))) == set(map(str, list(points_1)))


def test_get_leaf_points():
    grid = StaticGrid(StaticGridConfig(Octree, OctreeConfig()))
    points_0 = [
        np.array([0, 0, 1]),
        np.array([9, 9, 9]),
    ]
    grid.insert_points(0, points_0)
    points_1 = [
        np.array([1, 0, 1]),
        np.array([5, 9, 9]),
    ]
    grid.insert_points(1, points_1)

    grid.subdivide([lambda points: len(points) > 1])

    assert set(map(str, list(grid.get_leaf_points(0)))) == set(map(str, list([
        [np.array([0, 0, 1])],
        [np.array([9, 9, 9])],
    ])))
    assert set(map(str, list(grid.get_leaf_points(1)))) == set(map(str, list([
        [np.array([1, 0, 1])],
        [np.array([5, 9, 9])],
    ])))
