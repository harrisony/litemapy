"""
Structured tick types for litematica schematics.

This module provides structured classes for pending block and fluid ticks,
replacing raw NBT data with type-safe representations.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nbtlib.tag import Compound


@dataclass
class PendingBlockTick:
    """
    Represents a pending block tick in a region.

    Attributes:
        block: The block that will be ticked
        priority: The tick priority (lower is higher priority)
        sub_tick: The sub-tick value
        time: The time until the tick occurs
        x, y, z: The position of the tick
    """

    block: str
    priority: int
    sub_tick: int
    time: int
    x: int
    y: int
    z: int

    @classmethod
    def from_nbt(cls, nbt: "Compound") -> "PendingBlockTick":
        """Create a PendingBlockTick from NBT data."""
        return cls(
            block=nbt["block"],
            priority=nbt["priority"],
            sub_tick=nbt["sub_tick"],
            time=nbt["time"],
            x=nbt["x"],
            y=nbt["y"],
            z=nbt["z"],
        )

    def to_nbt(self) -> "Compound":
        """Convert this tick to NBT data."""
        from nbtlib.tag import Compound

        return Compound(
            {
                "block": self.block,
                "priority": self.priority,
                "sub_tick": self.sub_tick,
                "time": self.time,
                "x": self.x,
                "y": self.y,
                "z": self.z,
            }
        )


@dataclass
class PendingFluidTick:
    """
    Represents a pending fluid tick in a region.

    Attributes:
        fluid: The fluid that will be ticked
        priority: The tick priority (lower is higher priority)
        sub_tick: The sub-tick value
        time: The time until the tick occurs
        x, y, z: The position of the tick
    """

    fluid: str
    priority: int
    sub_tick: int
    time: int
    x: int
    y: int
    z: int

    @classmethod
    def from_nbt(cls, nbt: "Compound") -> "PendingFluidTick":
        """Create a PendingFluidTick from NBT data."""
        return cls(
            fluid=nbt["fluid"],
            priority=nbt["priority"],
            sub_tick=nbt["sub_tick"],
            time=nbt["time"],
            x=nbt["x"],
            y=nbt["y"],
            z=nbt["z"],
        )

    def to_nbt(self) -> "Compound":
        """Convert this tick to NBT data."""
        from nbtlib.tag import Compound

        return Compound(
            {
                "fluid": self.fluid,
                "priority": self.priority,
                "sub_tick": self.sub_tick,
                "time": self.time,
                "x": self.x,
                "y": self.y,
                "z": self.z,
            }
        )
