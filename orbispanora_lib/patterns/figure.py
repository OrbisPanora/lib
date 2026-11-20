"""Figure: the base class of the block patterns."""

from orbispanora_lib.anvil.block import Block


class Figure:
    """
    Base class for geometric patterns.
    Provides interface for empty and filled shapes.
    """
    blocks : list[Block]
    size : tuple[int, int, int]
    point : tuple[int, int, int]

    def __init__(self, blocks : list[Block], point : tuple[int, int, int], size : tuple[int, int, int]):
        """
        Initialize a Figure object.
        Parameters
        ----------
        blocks : list[Block]
            List of block types
        point : tuple[int, int, int]
            Starting point (x, y, z)
        size : tuple[int, int, int]
            Size of the figure
        """
        self.point = point
        self.blocks = blocks
        self.size = size

    def empty(self):
        """
        Abstract method for empty shape generation.
        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def filled(self):
        """
        Abstract method for filled shape generation.
        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError("Subclasses must implement this method.")
