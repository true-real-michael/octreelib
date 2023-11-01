from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, List, Optional

import numpy as np

from octreelib.internal.box import Box
from octreelib.internal.point import RawPoint, RawPointCloud
from octreelib.internal.voxel import StoringVoxel

__all__ = ["OctreeConfigBase", "OctreeBase", "OctreeNodeBase"]


@dataclass
class OctreeConfigBase(ABC):
    """
    Config for OcTree

    debug: debug mode is enabled
    """

    debug: bool = True


class OctreeNodeBase(StoringVoxel, ABC):
    """
    points: stores points of a node

    children: stores children of a node

    has_children: node stores children instead of points

    When subdivided, all points are **transferred** to children
    and are not stored in the parent node.
    """

    _points: RawPointCloud
    _children: Optional[List["OctreeNodeBase"]]
    _has_children: bool

    def __init__(self, corner: RawPoint, edge_length: np.float_):
        super().__init__(corner, edge_length)
        self._points: RawPointCloud = self._empty_point_cloud
        self._children = []
        self._has_children = False

    @property
    @abstractmethod
    def n_nodes(self):
        """
        :return: number of nodes
        """
        pass

    @property
    @abstractmethod
    def n_leaves(self):
        """
        :return: number of leaves a.k.a. number of nodes which have points
        """
        pass

    @property
    @abstractmethod
    def n_points(self):
        """
        :return: number of points in the octree node
        """
        return

    @abstractmethod
    def filter(self, filtering_criteria: List[Callable[[RawPointCloud], bool]]):
        """
        Filter nodes with points by filtering criteria
        :param filtering_criteria: List of filtering criteria functions
        """
        pass

    @abstractmethod
    def map_leaf_points(self, function: Callable[[RawPointCloud], RawPointCloud]):
        """
        transform point cloud in the node using the function
        :param function: transformation function RawPointCloud -> RawPointCloud
        """
        pass

    @abstractmethod
    def get_points_inside_box(self, box: Box) -> RawPointCloud:
        """
        Returns points that occupy the given box
        :param box: tuple of two points representing min and max points of the box
        :return: points which are inside the box.
        """

    @abstractmethod
    def get_leaf_points(self) -> List[StoringVoxel]:
        """
        :return: List of voxels where each voxel represents a leaf node with points.
        """
        pass

    @abstractmethod
    def subdivide(self, subdivision_criteria: List[Callable[[RawPointCloud], bool]]):
        """
        Subdivide node based on the subdivision criteria.
        :param subdivision_criteria: list of criteria for subdivision
        """
        pass


class OctreeBase(StoringVoxel, ABC):
    """
    Octree stores points of a **single** pos.

    root: root node of an octree
    """

    _node_type = OctreeNodeBase

    def __init__(
        self,
        octree_config: OctreeConfigBase,
        corner: RawPoint,
        edge_length: np.float_,
    ):
        super().__init__(corner, edge_length)
        self._config = octree_config
        self._root = self._node_type(self.corner, self.edge_length)

    @property
    @abstractmethod
    def n_nodes(self):
        """
        :return: number of nodes
        """
        pass

    @property
    @abstractmethod
    def n_leaves(self):
        """
        :return: number of leaves a.k.a. number of nodes which have points
        """
        pass

    @property
    @abstractmethod
    def n_points(self):
        """
        :return: number of points in the octree
        """
        pass

    @abstractmethod
    def filter(self, filtering_criteria: List[Callable[[RawPointCloud], bool]]):
        """
        filter nodes with points by criterion
        :param filtering_criteria:
        """
        pass

    @abstractmethod
    def map_leaf_points(self, function: Callable[[RawPointCloud], RawPointCloud]):
        """
        transform point cloud in each node using the function
        :param function: transformation function PointCloud -> PointCloud
        """
        pass

    @abstractmethod
    def get_points_in_box(self, box: Box) -> RawPointCloud:
        """
        Returns points that occupy the given box
        :param box: tuple of two points representing min and max points of the box
        :return: PointCloud
        """
        pass

    @abstractmethod
    def get_leaf_points(self) -> List[StoringVoxel]:
        """
        :return: List of PointClouds where each PointCloud
        represents points in a separate leaf node
        """
        pass

    @abstractmethod
    def subdivide(self, subdivision_criteria: List[Callable[[RawPointCloud], bool]]):
        """
        Subdivide node based on the subdivision criteria.
        :param subdivision_criteria: list of criteria for subdivision
        """
        pass
