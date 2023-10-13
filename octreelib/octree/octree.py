import itertools

from dataclasses import dataclass
from typing import Callable, List, Generic

import numpy as np

from octreelib.internal.geometry import point_is_inside_box
from octreelib.internal import PointCloud, Point, T
from octreelib.internal.typing import Box
from octreelib.octree.octree_base import OctreeBase, OctreeNodeBase, OctreeConfigBase

__all__ = ["OctreeNode", "Octree", "OctreeConfig"]


@dataclass
class OctreeConfig(OctreeConfigBase):
    pass


class OctreeNode(OctreeNodeBase):
    def get_points_inside_box(self, box: Box) -> PointCloud:
        if self.has_children:
            return sum(
                [child.get_points_inside_box(box) for child in self.children], []
            )

        return list(filter(lambda point: point_is_inside_box(point, box), self.points))

    def subdivide(self, subdivision_criteria: List[Callable[[PointCloud], bool]]):
        if any([criterion(self.points) for criterion in subdivision_criteria]):
            child_edge_length = self.edge_length / np.float_(2)
            children_corners_offsets = itertools.product(
                [0, child_edge_length], repeat=3
            )
            self.children = [
                OctreeNode(self.corner + offset, child_edge_length)
                for offset in children_corners_offsets
            ]
            self.has_children = True
            self.insert_points(self.points.copy())
            self.points = []
            for child in self.children:
                child.subdivide(subdivision_criteria)

    def get_points(self) -> PointCloud:
        return (
            sum([child.get_points() for child in self.children], [])
            if self.has_children
            else self.points
        )

    def insert_points(self, points: PointCloud):
        if self.has_children:
            for point in points:
                for child in self.children:
                    if point_is_inside_box(point, child.bounding_box):
                        child.insert_points([point])
        else:
            self.points.extend(points)

    def filter(self, filtering_criteria: List[Callable[[PointCloud], bool]]):
        if self.has_children:
            for child in self.children:
                child.filter(filtering_criteria)
            if all([child.n_points == 0 for child in self.children]):
                self.children = []
                self.has_children = False
        elif not all([criterion(self.points) for criterion in filtering_criteria]):
            self.points = []

    def map_leaf_points(self, function: Callable[[PointCloud], PointCloud]):
        if self.has_children:
            for child in self.children:
                child.map_leaf_points(function)
        elif self.points:
            self.points = function(self.points.copy())

    def get_leaf_node_points(self) -> List[PointCloud]:
        if self.has_children:
            return [child.get_leaf_node_points() for child in self.children]
        return [self.get_points()]

    @property
    def bounding_box(self):
        return self.corner, self.corner + np.ones(3) * self.edge_length

    @property
    def n_leafs(self):
        return (
            sum([child.n_leafs for child in self.children]) if self.has_children else 1
        )

    @property
    def n_nodes(self):
        return len(self.children) if self.has_children else 0

    @property
    def n_points(self):
        return (
            sum([child.n_points for child in self.children])
            if self.has_children
            else len(self.points)
        )


class Octree(OctreeBase, Generic[T]):
    _node_type = OctreeNode

    def get_points_in_box(self, box: Box) -> PointCloud:
        return self.root.get_points_inside_box(box)

    def subdivide(self, subdivision_criteria: List[Callable[[PointCloud], bool]]):
        self.root.subdivide(subdivision_criteria)

    def get_points(self) -> PointCloud:
        return self.root.get_points()

    def insert_points(self, points: PointCloud):
        self.root.insert_points(points)

    def filter(self, filtering_criteria: List[Callable[[PointCloud], bool]]):
        self.root.filter(filtering_criteria)

    def map_leaf_points(self, function: Callable[[PointCloud], PointCloud]):
        self.root.map_leaf_points(function)

    def get_leaf_node_points(self) -> List[PointCloud]:
        return self.root.get_leaf_node_points

    @property
    def n_points(self):
        return self.root.n_points

    @property
    def n_leafs(self):
        return self.root.n_leafs

    @property
    def n_nodes(self):
        return self.root.n_node
