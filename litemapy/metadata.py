"""
Metadata for litematica schematics.

This module provides a class for reading schematic metadata without loading
the full schematic contents, similar to rustmatica's LitematicMetadata.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import nbtlib


@dataclass
class LitematicMetadata:
    """
    Metadata for a litematica schematic.

    This class contains the metadata section of a litematica schematic
    without requiring the full schematic to be loaded.

    Attributes:
        name: The name of this schematic
        description: The description of this schematic
        author: The author of this schematic
        version: The litematica format version this schematic was created with
        sub_version: An optional litematica format subversion
        minecraft_data_version: The Minecraft data version used for blocks and entities
        time_created: The datetime of when this schematic was created
        time_modified: The datetime of when this schematic was last modified
        region_count: The number of regions in this schematic
        total_volume: The total volume of all regions combined
        total_blocks: The total number of blocks all regions combined
        enclosing_size: The size of the box enclosing all regions
        preview_image_data: Optional raw ARGB preview image data (140x140 pixels)
    """

    name: str
    description: str
    author: str
    version: int
    sub_version: Optional[int]
    minecraft_data_version: int
    time_created: datetime
    time_modified: datetime
    region_count: int
    total_volume: int
    total_blocks: int
    enclosing_size: tuple[int, int, int]
    preview_image_data: Optional[list[int]]

    @classmethod
    def read_file(cls, filename: str | Path) -> "LitematicMetadata":
        """
        Load schematic metadata from a file.

        Args:
            filename: Path to the .litematic file

        Returns:
            LitematicMetadata object containing the schematic's metadata
        """
        nbt = nbtlib.load(str(filename), compressed=True)
        return cls.from_nbt(nbt)

    @classmethod
    def from_bytes(cls, data: bytes) -> "LitematicMetadata":
        """
        Load schematic metadata from raw bytes.

        Args:
            data: Raw NBT data (gzip compressed)

        Returns:
            LitematicMetadata object containing the schematic's metadata
        """
        nbt = nbtlib.File.parse(data)
        return cls.from_nbt(nbt)

    @classmethod
    def from_nbt(cls, nbt: nbtlib.File) -> "LitematicMetadata":
        """
        Create LitematicMetadata from NBT data.

        Args:
            nbt: Parsed NBT file

        Returns:
            LitematicMetadata object
        """
        meta_section = nbt["Metadata"]
        return cls(
            name=meta_section["Name"],
            description=meta_section["Description"],
            author=meta_section["Author"],
            version=nbt["MinecraftDataVersion"],
            sub_version=nbt.get("Version", nbt.get("MinecraftDataVersion")),
            minecraft_data_version=nbt["MinecraftDataVersion"],
            time_created=datetime.fromtimestamp(meta_section["TimeCreated"] / 1000),
            time_modified=datetime.fromtimestamp(meta_section["TimeModified"] / 1000),
            region_count=meta_section["RegionCount"],
            total_volume=meta_section["TotalVolume"],
            total_blocks=meta_section["TotalBlocks"],
            enclosing_size=tuple(meta_section["EnclosingSize"]),
            preview_image_data=list(meta_section["PreviewImageData"])
            if "PreviewImageData" in meta_section
            else None,
        )
