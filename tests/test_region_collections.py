"""
Tests for Region entity, tile entity, and tick collection management.
Tests the integration of entities, tile entities, block ticks, and fluid ticks
within Region objects and their persistence through save/load cycles.
"""

import pytest
from tempfile import TemporaryDirectory
import os

from litemapy import Schematic, Region, BlockState, Entity, TileEntity
from litemapy.minecraft import RequiredKeyMissingException
from nbtlib import Compound, Int, String, Double, List


class TestRegionEntityCollection:
    """Tests for Region.entities property and entity management."""

    def test_region_entities_property_returns_list(self):
        """Test that entities property returns a list."""
        region = Region(0, 0, 0, 10, 10, 10)
        assert isinstance(region.entities, list)
        assert len(region.entities) == 0

    def test_region_entities_property_getter(self):
        """Test that entities property getter returns entities list."""
        region = Region(0, 0, 0, 10, 10, 10)
        entity = Entity("minecraft:zombie")
        region.entities.append(entity)

        entities = region.entities
        assert len(entities) == 1
        assert entities[0].id == "minecraft:zombie"
        assert entities[0].position == (0.0, 0.0, 0.0)  # Default position

    def test_region_entities_multiple_entities(self):
        """Test that multiple entities can be added to a region."""
        region = Region(0, 0, 0, 10, 10, 10)

        entity1 = Entity("minecraft:zombie")
        entity1.position = (1.0, 2.0, 3.0)
        entity2 = Entity("minecraft:skeleton")
        entity2.position = (4.0, 5.0, 6.0)
        entity3 = Entity("minecraft:spider")
        entity3.position = (7.0, 8.0, 9.0)

        region.entities.extend([entity1, entity2, entity3])

        assert len(region.entities) == 3
        assert region.entities[0].id == "minecraft:zombie"
        assert region.entities[1].id == "minecraft:skeleton"
        assert region.entities[2].id == "minecraft:spider"
        assert region.entities[0].position == (1.0, 2.0, 3.0)
        assert region.entities[1].position == (4.0, 5.0, 6.0)
        assert region.entities[2].position == (7.0, 8.0, 9.0)

    def test_region_entities_with_nbt_compound(self):
        """Test creating entity from NBT compound and adding to region."""
        region = Region(0, 0, 0, 10, 10, 10)

        nbt = Compound(
            {
                "id": String("minecraft:villager"),
                "Pos": List[Double]([Double(15.0), Double(64.0), Double(20.0)]),
                "Rotation": List[Double]([Double(45.0), Double(0.0)]),
                "Motion": List[Double]([Double(0.0), Double(0.0), Double(0.0)]),
            }
        )
        entity = Entity(nbt)
        region.entities.append(entity)

        assert len(region.entities) == 1
        assert region.entities[0].id == "minecraft:villager"
        assert region.entities[0].position == (15.0, 64.0, 20.0)


class TestRegionTileEntityCollection:
    """Tests for Region.tile_entities property and tile entity management."""

    def test_region_tile_entities_property_returns_list(self):
        """Test that tile_entities property returns a list."""
        region = Region(0, 0, 0, 10, 10, 10)
        assert isinstance(region.tile_entities, list)
        assert len(region.tile_entities) == 0

    def test_region_tile_entities_property_getter(self):
        """Test that tile_entities property getter returns tile entities list."""
        region = Region(0, 0, 0, 10, 10, 10)

        nbt = Compound(
            {
                "x": Int(1),
                "y": Int(2),
                "z": Int(3),
                "id": String("minecraft:chest"),
                "Items": List[Compound]([]),
            }
        )
        tile_entity = TileEntity.from_nbt(nbt)
        region.tile_entities.append(tile_entity)

        tile_entities = region.tile_entities
        assert len(tile_entities) == 1
        assert tile_entities[0].position == (1, 2, 3)

    def test_region_tile_entities_multiple_tile_entities(self):
        """Test that multiple tile entities can be added to a region."""
        region = Region(0, 0, 0, 10, 10, 10)

        nbt1 = Compound(
            {
                "x": Int(1),
                "y": Int(2),
                "z": Int(3),
                "id": String("minecraft:chest"),
                "Items": List[Compound]([]),
            }
        )
        nbt2 = Compound(
            {
                "x": Int(4),
                "y": Int(5),
                "z": Int(6),
                "id": String("minecraft:chest"),
                "Items": List[Compound]([]),
            }
        )
        nbt3 = Compound(
            {
                "x": Int(7),
                "y": Int(8),
                "z": Int(9),
                "id": String("minecraft:chest"),
                "Items": List[Compound]([]),
            }
        )

        tile_entity1 = TileEntity(nbt1)
        tile_entity2 = TileEntity(nbt2)
        tile_entity3 = TileEntity(nbt3)

        region.tile_entities.extend([tile_entity1, tile_entity2, tile_entity3])

        assert len(region.tile_entities) == 3
        assert region.tile_entities[0].position == (1, 2, 3)
        assert region.tile_entities[1].position == (4, 5, 6)
        assert region.tile_entities[2].position == (7, 8, 9)

    def test_region_set_block_entity(self):
        """Test set_block_entity method."""
        region = Region(0, 0, 0, 10, 10, 10)

        nbt = Compound(
            {
                "x": Int(1),
                "y": Int(2),
                "z": Int(3),
                "id": String("minecraft:chest"),
                "Items": List[Compound]([]),
            }
        )
        tile_entity = TileEntity(nbt)
        region.set_block_entity(tile_entity)

        assert len(region.tile_entities) == 1
        assert region.tile_entities[0].position == (1, 2, 3)

    def test_region_get_block_entity(self):
        """Test get_block_entity method returns tile entity at position."""
        region = Region(0, 0, 0, 10, 10, 10)

        nbt = Compound(
            {
                "x": Int(1),
                "y": Int(2),
                "z": Int(3),
                "id": String("minecraft:chest"),
                "Items": List[Compound]([]),
            }
        )
        tile_entity = TileEntity(nbt)
        region.set_block_entity(tile_entity)

        retrieved = region.get_block_entity((1, 2, 3))
        assert retrieved is not None
        assert retrieved.position == (1, 2, 3)

    def test_region_get_block_entity_not_found(self):
        """Test get_block_entity returns None when no tile entity at position."""
        region = Region(0, 0, 0, 10, 10, 10)

        nbt = Compound(
            {
                "x": Int(1),
                "y": Int(2),
                "z": Int(3),
                "id": String("minecraft:chest"),
                "Items": List[Compound]([]),
            }
        )
        tile_entity = TileEntity(nbt)
        region.set_block_entity(tile_entity)

        retrieved = region.get_block_entity((5, 6, 7))
        assert retrieved is None

    def test_region_remove_block_entity(self):
        """Test remove_block_entity method removes tile entity at position."""
        region = Region(0, 0, 0, 10, 10, 10)

        nbt = Compound(
            {
                "x": Int(1),
                "y": Int(2),
                "z": Int(3),
                "id": String("minecraft:chest"),
                "Items": List[Compound]([]),
            }
        )
        tile_entity = TileEntity(nbt)
        region.set_block_entity(tile_entity)

        assert len(region.tile_entities) == 1

        removed = region.remove_block_entity((1, 2, 3))
        assert removed is not None
        assert isinstance(removed, TileEntity)
        assert removed.position == (1, 2, 3)
        assert len(region.tile_entities) == 0

    def test_region_remove_block_entity_not_found(self):
        """Test remove_block_entity returns None when no tile entity at position."""
        region = Region(0, 0, 0, 10, 10, 10)

        nbt = Compound(
            {
                "x": Int(1),
                "y": Int(2),
                "z": Int(3),
                "id": String("minecraft:chest"),
                "Items": List[Compound]([]),
            }
        )
        tile_entity = TileEntity(nbt)
        region.set_block_entity(tile_entity)

        removed = region.remove_block_entity((5, 6, 7))
        assert removed is None
        assert len(region.tile_entities) == 1


class TestRegionBlockTicks:
    """Tests for Region.block_ticks property."""

    def test_region_block_ticks_property_returns_list(self):
        """Test that block_ticks property returns a list."""
        region = Region(0, 0, 0, 10, 10, 10)
        assert isinstance(region.block_ticks, list)
        assert len(region.block_ticks) == 0

    def test_region_block_ticks_add_tick(self):
        """Test adding block ticks to a region."""
        region = Region(0, 0, 0, 10, 10, 10)

        tick = Compound(
            {
                "i": Int(0),  # Block state index
                "x": Int(1),
                "y": Int(2),
                "z": Int(3),
                "t": Int(100),  # Tick time
                "p": Int(0),  # Priority
            }
        )
        region.block_ticks.append(tick)

        assert len(region.block_ticks) == 1
        assert region.block_ticks[0]["i"] == 0
        assert region.block_ticks[0]["x"] == 1
        assert region.block_ticks[0]["y"] == 2
        assert region.block_ticks[0]["z"] == 3
        assert region.block_ticks[0]["t"] == 100
        assert region.block_ticks[0]["p"] == 0

    def test_region_block_ticks_multiple_ticks(self):
        """Test multiple block ticks in a region."""
        region = Region(0, 0, 0, 10, 10, 10)

        tick1 = Compound(
            {
                "i": Int(0),
                "x": Int(1),
                "y": Int(2),
                "z": Int(3),
                "t": Int(100),
                "p": Int(0),
            }
        )
        tick2 = Compound(
            {
                "i": Int(1),
                "x": Int(4),
                "y": Int(5),
                "z": Int(6),
                "t": Int(200),
                "p": Int(1),
            }
        )

        region.block_ticks.extend([tick1, tick2])

        assert len(region.block_ticks) == 2
        assert region.block_ticks[0]["t"] == 100
        assert region.block_ticks[1]["t"] == 200
        assert region.block_ticks[0]["x"] == 1
        assert region.block_ticks[1]["x"] == 4


class TestRegionFluidTicks:
    """Tests for Region.fluid_ticks property."""

    def test_region_fluid_ticks_property_returns_list(self):
        """Test that fluid_ticks property returns a list."""
        region = Region(0, 0, 0, 10, 10, 10)
        assert isinstance(region.fluid_ticks, list)
        assert len(region.fluid_ticks) == 0

    def test_region_fluid_ticks_add_tick(self):
        """Test adding fluid ticks to a region."""
        region = Region(0, 0, 0, 10, 10, 10)

        tick = Compound(
            {
                "i": Int(0),
                "x": Int(1),
                "y": Int(2),
                "z": Int(3),
                "t": Int(100),
                "p": Int(0),
            }
        )
        region.fluid_ticks.append(tick)

        assert len(region.fluid_ticks) == 1
        assert region.fluid_ticks[0]["i"] == 0
        assert region.fluid_ticks[0]["x"] == 1
        assert region.fluid_ticks[0]["y"] == 2
        assert region.fluid_ticks[0]["z"] == 3
        assert region.fluid_ticks[0]["t"] == 100
        assert region.fluid_ticks[0]["p"] == 0

    def test_region_fluid_ticks_multiple_ticks(self):
        """Test multiple fluid ticks in a region."""
        region = Region(0, 0, 0, 10, 10, 10)

        tick1 = Compound(
            {
                "i": Int(0),
                "x": Int(1),
                "y": Int(2),
                "z": Int(3),
                "t": Int(100),
                "p": Int(0),
            }
        )
        tick2 = Compound(
            {
                "i": Int(1),
                "x": Int(4),
                "y": Int(5),
                "z": Int(6),
                "t": Int(200),
                "p": Int(1),
            }
        )

        region.fluid_ticks.extend([tick1, tick2])

        assert len(region.fluid_ticks) == 2
        assert region.fluid_ticks[0]["t"] == 100
        assert region.fluid_ticks[1]["t"] == 200
        assert region.fluid_ticks[0]["x"] == 1
        assert region.fluid_ticks[1]["x"] == 4


class TestRegionWithEntitiesFromLitematic:
    """Tests for loading litematic files with entities and tile entities."""

    def test_armorstand_litematic_has_entity(self):
        """Test loading ArmorStand.litematic which has an entity."""
        sch = Schematic.load("tests/litematics/valid/ArmorStand.litematic")
        assert "ArmorStand" in sch.regions

        region = sch.regions["ArmorStand"]
        assert len(region.entities) > 0
        assert region.entities[0].id == "minecraft:armor_stand"

    def test_axolotl_litematic_has_entities_and_tile_entities(self):
        """Test loading axolotl.litematic which has both entities and tile entities."""
        sch = Schematic.load("tests/litematics/valid/axolotl.litematic")
        assert "box" in sch.regions

        region = sch.regions["box"]
        assert len(region.entities) > 0
        assert len(region.tile_entities) > 0


class TestRegionEntityPersistence:
    """Tests for persistence of entities, tile entities, and ticks through save/load."""

    def test_entity_persists_through_save_load(self):
        """Test that entities persist when saving and loading a schematic."""
        with TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.litematic")

            # Create schematic with entity
            sch = Schematic(name="Test", author="TestAuthor")
            sch.regions["test"] = Region(0, 0, 0, 10, 10, 10)
            region = sch.regions["test"]

            entity = Entity("minecraft:zombie")
            entity.position = (5.5, 64.0, 7.5)
            region.entities.append(entity)

            sch.save(filepath)

            # Load and verify
            loaded_sch = Schematic.load(filepath)
            loaded_region = loaded_sch.regions["test"]

            assert len(loaded_region.entities) == 1
            assert loaded_region.entities[0].id == "minecraft:zombie"
            assert loaded_region.entities[0].position == (5.5, 64.0, 7.5)

    def test_multiple_entities_persist_through_save_load(self):
        """Test that multiple entities persist through save/load cycle."""
        with TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.litematic")

            sch = Schematic(name="Test", author="TestAuthor")
            sch.regions["test"] = Region(0, 0, 0, 10, 10, 10)
            region = sch.regions["test"]

            entity1 = Entity("minecraft:zombie")
            entity1.position = (1.0, 2.0, 3.0)
            entity2 = Entity("minecraft:skeleton")
            entity2.position = (4.0, 5.0, 6.0)
            entity3 = Entity("minecraft:spider")
            entity3.position = (7.0, 8.0, 9.0)

            region.entities.extend([entity1, entity2, entity3])
            sch.save(filepath)

            loaded_sch = Schematic.load(filepath)
            loaded_region = loaded_sch.regions["test"]

            assert len(loaded_region.entities) == 3
            assert loaded_region.entities[0].id == "minecraft:zombie"
            assert loaded_region.entities[1].id == "minecraft:skeleton"
            assert loaded_region.entities[2].id == "minecraft:spider"
            assert loaded_region.entities[0].position == (1.0, 2.0, 3.0)
            assert loaded_region.entities[1].position == (4.0, 5.0, 6.0)
            assert loaded_region.entities[2].position == (7.0, 8.0, 9.0)

    def test_tile_entity_persists_through_save_load(self):
        """Test that tile entities persist through save/load cycle."""
        with TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.litematic")

            sch = Schematic(name="Test", author="TestAuthor")
            sch.regions["test"] = Region(0, 0, 0, 10, 10, 10)
            region = sch.regions["test"]

            nbt = Compound(
                {
                    "x": Int(5),
                    "y": Int(6),
                    "z": Int(7),
                    "id": String("minecraft:chest"),
                    "Items": List[Compound]([]),
                }
            )
            tile_entity = TileEntity(nbt)
            region.tile_entities.append(tile_entity)

            sch.save(filepath)

            loaded_sch = Schematic.load(filepath)
            loaded_region = loaded_sch.regions["test"]

            assert len(loaded_region.tile_entities) == 1
            assert loaded_region.tile_entities[0].position == (5, 6, 7)

    def test_multiple_tile_entities_persist_through_save_load(self):
        """Test that multiple tile entities persist through save/load cycle."""
        with TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.litematic")

            sch = Schematic(name="Test", author="TestAuthor")
            sch.regions["test"] = Region(0, 0, 0, 10, 10, 10)
            region = sch.regions["test"]

            nbt1 = Compound(
                {
                    "x": Int(1),
                    "y": Int(2),
                    "z": Int(3),
                    "id": String("minecraft:chest"),
                    "Items": List[Compound]([]),
                }
            )
            nbt2 = Compound(
                {
                    "x": Int(4),
                    "y": Int(5),
                    "z": Int(6),
                    "id": String("minecraft:furnace"),
                    "Items": List[Compound]([]),
                }
            )
            nbt3 = Compound(
                {
                    "x": Int(7),
                    "y": Int(8),
                    "z": Int(9),
                    "id": String("minecraft:hopper"),
                    "Items": List[Compound]([]),
                }
            )

            tile_entity1 = TileEntity(nbt1)
            tile_entity2 = TileEntity(nbt2)
            tile_entity3 = TileEntity(nbt3)

            region.tile_entities.extend([tile_entity1, tile_entity2, tile_entity3])
            sch.save(filepath)

            loaded_sch = Schematic.load(filepath)
            loaded_region = loaded_sch.regions["test"]

            assert len(loaded_region.tile_entities) == 3
            assert loaded_region.tile_entities[0].position == (1, 2, 3)
            assert loaded_region.tile_entities[1].position == (4, 5, 6)
            assert loaded_region.tile_entities[2].position == (7, 8, 9)

    def test_block_ticks_persist_through_save_load(self):
        """Test that block ticks persist through save/load cycle."""
        with TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.litematic")

            sch = Schematic(name="Test", author="TestAuthor")
            sch.regions["test"] = Region(0, 0, 0, 10, 10, 10)
            region = sch.regions["test"]

            tick = Compound(
                {
                    "i": Int(0),
                    "x": Int(5),
                    "y": Int(6),
                    "z": Int(7),
                    "t": Int(100),
                    "p": Int(0),
                }
            )
            region.block_ticks.append(tick)

            sch.save(filepath)

            loaded_sch = Schematic.load(filepath)
            loaded_region = loaded_sch.regions["test"]

            assert len(loaded_region.block_ticks) == 1
            assert loaded_region.block_ticks[0]["x"] == 5
            assert loaded_region.block_ticks[0]["y"] == 6
            assert loaded_region.block_ticks[0]["z"] == 7
            assert loaded_region.block_ticks[0]["t"] == 100
            assert loaded_region.block_ticks[0]["p"] == 0

    def test_fluid_ticks_persist_through_save_load(self):
        """Test that fluid ticks persist through save/load cycle."""
        with TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.litematic")

            sch = Schematic(name="Test", author="TestAuthor")
            sch.regions["test"] = Region(0, 0, 0, 10, 10, 10)
            region = sch.regions["test"]

            tick = Compound(
                {
                    "i": Int(0),
                    "x": Int(5),
                    "y": Int(6),
                    "z": Int(7),
                    "t": Int(100),
                    "p": Int(0),
                }
            )
            region.fluid_ticks.append(tick)

            sch.save(filepath)

            loaded_sch = Schematic.load(filepath)
            loaded_region = loaded_sch.regions["test"]

            assert len(loaded_region.fluid_ticks) == 1
            assert loaded_region.fluid_ticks[0]["x"] == 5
            assert loaded_region.fluid_ticks[0]["y"] == 6
            assert loaded_region.fluid_ticks[0]["z"] == 7
            assert loaded_region.fluid_ticks[0]["t"] == 100
            assert loaded_region.fluid_ticks[0]["p"] == 0

    def test_entities_and_tile_entities_together_persist(self):
        """Test that entities and tile entities together persist through save/load."""
        with TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.litematic")

            sch = Schematic(name="Test", author="TestAuthor")
            sch.regions["test"] = Region(0, 0, 0, 10, 10, 10)
            region = sch.regions["test"]

            entity = Entity("minecraft:zombie")
            entity.position = (5.5, 64.0, 7.5)
            region.entities.append(entity)

            nbt = Compound(
                {
                    "x": Int(2),
                    "y": Int(3),
                    "z": Int(4),
                    "id": String("minecraft:chest"),
                    "Items": List[Compound]([]),
                }
            )
            tile_entity = TileEntity(nbt)
            region.tile_entities.append(tile_entity)

            sch.save(filepath)

            loaded_sch = Schematic.load(filepath)
            loaded_region = loaded_sch.regions["test"]

            assert len(loaded_region.entities) == 1
            assert loaded_region.entities[0].id == "minecraft:zombie"
            assert loaded_region.entities[0].position == (5.5, 64.0, 7.5)

            assert len(loaded_region.tile_entities) == 1
            assert loaded_region.tile_entities[0].position == (2, 3, 4)

    def test_all_collections_together_persist(self):
        """Test that all collections (entities, tile entities, ticks) persist together."""
        with TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.litematic")

            sch = Schematic(name="Test", author="TestAuthor")
            sch.regions["test"] = Region(0, 0, 0, 10, 10, 10)
            region = sch.regions["test"]

            entity = Entity("minecraft:zombie")
            entity.position = (1.5, 62.0, 3.5)
            region.entities.append(entity)

            nbt = Compound(
                {
                    "x": Int(5),
                    "y": Int(6),
                    "z": Int(7),
                    "id": String("minecraft:chest"),
                    "Items": List[Compound]([]),
                }
            )
            tile_entity = TileEntity(nbt)
            region.tile_entities.append(tile_entity)

            block_tick = Compound(
                {
                    "i": Int(0),
                    "x": Int(2),
                    "y": Int(3),
                    "z": Int(4),
                    "t": Int(100),
                    "p": Int(0),
                }
            )
            region.block_ticks.append(block_tick)

            fluid_tick = Compound(
                {
                    "i": Int(1),
                    "x": Int(3),
                    "y": Int(4),
                    "z": Int(5),
                    "t": Int(200),
                    "p": Int(1),
                }
            )
            region.fluid_ticks.append(fluid_tick)

            sch.save(filepath)

            loaded_sch = Schematic.load(filepath)
            loaded_region = loaded_sch.regions["test"]

            assert len(loaded_region.entities) == 1
            assert loaded_region.entities[0].position == (1.5, 62.0, 3.5)

            assert len(loaded_region.tile_entities) == 1
            assert loaded_region.tile_entities[0].position == (5, 6, 7)

            assert len(loaded_region.block_ticks) == 1
            assert loaded_region.block_ticks[0]["x"] == 2
            assert loaded_region.block_ticks[0]["t"] == 100

            assert len(loaded_region.fluid_ticks) == 1
            assert loaded_region.fluid_ticks[0]["x"] == 3
            assert loaded_region.fluid_ticks[0]["t"] == 200
