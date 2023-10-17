import numpy as np
import pytest

from octreelib.grid import GridWithPoints, GridWithPointsConfig
from octreelib.octree import Octree, OctreeConfig


def points_are_same(points_a, points_b):
    return set(map(str, list(points_a))) == set(map(str, list(points_b)))


@pytest.fixture()
def generated_grid():
    grid = GridWithPoints(
        GridWithPointsConfig(
            octree_type=Octree, octree_config=OctreeConfig(), min_voxel_size=5
        )
    )
    points_0 = [
        np.array([0, 0, 1]),  # voxel 0,0,0
        np.array([0, 0, 2]),  # voxel 0,0,0
        np.array([0, 0, 3]),  # voxel 0,0,0
        np.array([9, 9, 8]),  # voxel 5,5,5
        np.array([9, 9, 9]),  # voxel 5,5,5
    ]
    grid.insert_points(0, points_0)
    points_1 = [
        np.array([1, 0, 1]),  # voxel 0,0,0
        np.array([4, 0, 2]),  # voxel 0,0,0
        np.array([0, 2, 3]),  # voxel 0,0,0
        np.array([9, 3, 8]),  # voxel 5,0,5
        np.array([5, 9, 9]),  # voxel 5,5,5
    ]
    grid.insert_points(1, points_1)

    return grid, [points_0, points_1]


def test_n_leafs(generated_grid):
    grid, pose_points = generated_grid

    assert 2 == grid.n_leafs(0)
    assert 3 == grid.n_leafs(1)
    grid.subdivide([lambda points: len(points) > 2])
    assert 9 == grid.n_leafs(0)
    assert 10 == grid.n_leafs(1)


def test_n_points(generated_grid):
    grid, pose_points = generated_grid

    assert 5 == grid.n_points(0)
    assert 5 == grid.n_points(1)
    grid.subdivide([lambda points: len(points) > 2])
    assert 5 == grid.n_points(0)
    assert 5 == grid.n_points(1)


def test_n_nodes(generated_grid):
    grid, pose_points = generated_grid

    assert 2 == grid.n_nodes(0)
    assert 3 == grid.n_nodes(1)
    grid.subdivide([lambda points: len(points) > 2])
    assert 17 == grid.n_nodes(0)
    assert 18 == grid.n_nodes(1)


@pytest.mark.parametrize(
    "subdivision_criteria, nodes_expected, leafs_expected",
    [
        ([lambda points: len(points) > 2], [17, 18], [9, 10]),
        ([lambda points: len(points) > 3], [2, 3], [2, 3]),
    ],
)
def test_subdivide(
    generated_grid, subdivision_criteria, nodes_expected, leafs_expected
):
    grid, pose_points = generated_grid

    grid.subdivide(subdivision_criteria)
    assert nodes_expected == [grid.n_nodes(0), grid.n_nodes(1)]
    assert leafs_expected == [grid.n_leafs(0), grid.n_leafs(1)]


def test_map_leaf_points(generated_grid):
    grid, pose_points = generated_grid

    assert grid.n_points(0) > grid.n_leafs(0)
    assert grid.n_points(1) > grid.n_leafs(1)
    grid.map_leaf_points(lambda cloud: [cloud[0]])
    assert grid.n_points(0) == grid.n_leafs(0)
    assert grid.n_points(1) == grid.n_leafs(1)
