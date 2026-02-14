from litemapy import Schematic, Region, BlockState
from os import walk
from constants import *
import helper
from tempfile import TemporaryDirectory
import nbtlib
import nbtlib.tag

AIR = BlockState("minecraft:air")

valid_files = []
for directory, child_directory, file_names in walk(VALID_LITEMATIC_DIRECTORY):
    for file_name in file_names:
        valid_files.append(path.join(directory, file_name))


def test_valid_litematics_do_not_raise_exception_when_loaded():
    for file_path in valid_files:
        Schematic.load(file_path)


def test_regions_have_accurate_sizes():
    sch = Schematic()
    assert sch.width == 0
    assert sch.height == 0
    assert sch.length == 0
    reg1 = Region(0, 0, 0, 10, 10, 10)
    reg2 = Region(90, 0, 0, 10, 10, 10)
    reg3 = Region(50, 0, 0, 10, 10, 10)
    reg4 = Region(49, 0, 0, -10, 10, 10)
    sch.regions["a"] = reg1
    assert sch.width == 10
    assert sch.height == 10
    assert sch.length == 10
    sch.regions["b"] = reg2
    assert sch.width == 100
    sch.regions["c"] = reg3
    assert sch.width == 100
    del sch.regions["b"]
    assert sch.width == 60
    sch.regions["c"] = reg4
    assert sch.width == 50


def test_region_min_and_max_are_accurate():
    reg = Region(0, 0, 0, 10, 20, 30)
    assert reg.min_schem_x() == 0
    assert reg.max_schem_x() == 9
    assert reg.min_schem_y() == 0
    assert reg.max_schem_y() == 19
    assert reg.min_schem_z() == 0
    assert reg.max_schem_z() == 29
    assert reg.min_x() == 0
    assert reg.max_x() == 9
    assert reg.min_y() == 0
    assert reg.max_y() == 19
    assert reg.min_z() == 0
    assert reg.max_z() == 29
    reg = Region(0, 0, 0, -10, -20, -30)
    assert reg.min_schem_x() == -9
    assert reg.max_schem_x() == 0
    assert reg.min_schem_y() == -19
    assert reg.max_schem_y() == 0
    assert reg.min_schem_z() == -29
    assert reg.max_schem_z() == 0
    assert reg.min_x() == -9
    assert reg.max_x() == 0
    assert reg.min_y() == -19
    assert reg.max_y() == 0
    assert reg.min_z() == -29
    assert reg.max_z() == 0
    reg = Region(10, 10, 10, 10, 10, 10)
    assert reg.min_schem_x() == 10
    assert reg.max_schem_x() == 19
    assert reg.min_schem_y() == 10
    assert reg.max_schem_y() == 19
    assert reg.min_schem_z() == 10
    assert reg.max_schem_z() == 19
    assert reg.min_x() == 0
    assert reg.max_x() == 9
    assert reg.min_y() == 0
    assert reg.max_y() == 9
    assert reg.min_z() == 0
    assert reg.max_z() == 9
    reg = Region(-10, -10, -10, 10, 10, 10)
    assert reg.min_schem_x() == -10
    assert reg.max_schem_x() == -1
    assert reg.min_schem_y() == -10
    assert reg.max_schem_y() == -1
    assert reg.min_schem_z() == -10
    assert reg.max_schem_z() == -1
    assert reg.min_x() == 0
    assert reg.max_x() == 9
    assert reg.min_y() == 0
    assert reg.max_y() == 9
    assert reg.min_z() == 0
    assert reg.max_z() == 9
    reg = Region(-10, -10, -10, -10, -10, -10)
    assert reg.min_schem_x() == -19
    assert reg.max_schem_x() == -10
    assert reg.min_schem_y() == -19
    assert reg.max_schem_y() == -10
    assert reg.min_schem_z() == -19
    assert reg.max_schem_z() == -10
    assert reg.min_x() == -9
    assert reg.max_x() == 0
    assert reg.min_y() == -9
    assert reg.max_y() == 0
    assert reg.min_z() == -9
    assert reg.max_z() == 0


def test_are_random_schematics_preserved_when_reading_and_writing():
    temporary_directory = TemporaryDirectory()
    for i in range(10):
        write_schematic = helper.randomschematic()
        file_path = path.join(temporary_directory.name, write_schematic.name + ".litematic")
        write_schematic.save(file_path)
        read_schematic = Schematic.load(file_path)

        # Assert metadata is equals
        assert write_schematic.name == read_schematic.name
        assert write_schematic.author == read_schematic.author
        assert write_schematic.description == read_schematic.description
        assert write_schematic.width == read_schematic.width
        assert write_schematic.height == read_schematic.height
        assert write_schematic.length == read_schematic.length
        assert len(write_schematic.regions) == len(read_schematic.regions)
        for name, write_region in write_schematic.regions.items():
            read_region = read_schematic.regions[name]

            # Assert computed values are equal
            assert write_region.min_x() == read_region.min_x()
            assert write_region.max_x() == read_region.max_x()
            assert write_region.min_y() == read_region.min_y()
            assert write_region.max_y() == read_region.max_y()
            assert write_region.min_z() == read_region.min_z()
            assert write_region.max_z() == read_region.max_z()
            assert write_region.min_schem_x() == read_region.min_schem_x()
            assert write_region.max_schem_x() == read_region.max_schem_x()
            assert write_region.min_schem_y() == read_region.min_schem_y()
            assert write_region.max_schem_y() == read_region.max_schem_y()
            assert write_region.min_schem_z() == read_region.min_schem_z()
            assert write_region.max_schem_z() == read_region.max_schem_z()

            # Assert all blocks are equal
            for x, y, z in write_region.allblockpos():
                ws = write_region[x, y, z]
                rs = read_region[x, y, z]
                assert ws == rs

            assert_valid_palette(write_region)

    temporary_directory.cleanup()


def test_region_filter():
    def do_filter(before_schematic, after_schematic, function):
        print(f"Comparing litematic files {before_schematic} and {after_schematic}")
        before_schematic = path.join(FILTER_LITEMATIC_DIRECTORY, before_schematic)
        after_schematic = path.join(FILTER_LITEMATIC_DIRECTORY, after_schematic)
        before_schematic = Schematic.load(before_schematic)
        after_schematic = Schematic.load(after_schematic)
        assert len(before_schematic.regions) == 1, "Invalid test litematic"
        assert len(after_schematic.regions) == 1, "Invalid test litematic"
        (before_schematic,) = before_schematic.regions.values()
        (after_schematic,) = after_schematic.regions.values()
        assert before_schematic.width == after_schematic.width, "Invalid test litematic"
        assert before_schematic.height == after_schematic.height, "Invalid test litematic"
        assert before_schematic.length == after_schematic.length, "Invalid test litematic"
        before_schematic.filter(function)
        for x in before_schematic.range_x():
            for y in before_schematic.range_y():
                for z in before_schematic.range_z():
                    state_1 = before_schematic[x, y, z]
                    state_2 = after_schematic[x, y, z]
                    assert state_1 == state_2
        assert_valid_palette(before_schematic)

    def all_blue_filter(b: BlockState):
        return BlockState("minecraft:light_blue_concrete")

    do_filter('rainbow-line.litematic', 'blue-line.litematic', all_blue_filter)

    red = BlockState("minecraft:red_concrete")
    blue = BlockState("minecraft:blue_concrete")

    def black_red_white_blue(b: BlockState):
        if b.id == "minecraft:black_concrete":
            return red
        if b.id == "minecraft:white_concrete":
            return blue
        return b

    do_filter('black-white.litematic', 'red-blue.litematic', black_red_white_blue)

    def glassify(state: BlockState):
        if "water" in state.id:
            return BlockState("minecraft:blue_stained_glass")
        elif state.id == "minecraft:sand":
            return BlockState('minecraft:yellow_stained_glass')
        elif state.id == "minecraft:dirt":
            return BlockState("minecraft:brown_stained_glass")
        elif state.id == "minecraft:stone":
            return BlockState("minecraft:light_gray_stained_glass")
        elif state.id in ("minecraft:grass_block", "minecraft:birch_leaves"):
            return BlockState("minecraft:green_stained_glass")
        elif state.id == "minecraft:birch_log":
            return BlockState("minecraft:white_stained_glass")
        elif state.id == "minecraft:copper_ore":
            return BlockState("minecraft:orange_stained_glass")
        elif state.id == "minecraft:grass":
            return BlockState("minecraft:green_stained_glass_pane", east="true", north="true", south="true",
                              west="true", waterlogged="false")
        return state

    do_filter('tree.litematic', 'tree-glass.litematic', glassify)

    def wool_to_concrete(b: BlockState):
        return b.with_id(b.id.replace('wool', 'concrete'))

    do_filter('concrete-wool.litematic', 'concrete-full.litematic', wool_to_concrete)


def assert_valid_palette(region: Region):
    palette = region.palette

    assert palette[0] == AIR, "Palette does not have air at index 0"

    entries = set()
    for entry in palette:
        assert entry not in entries, f"Palette has duplicate entry: {entry}"
        entries.add(entry)

    blocks = {region[p] for p in region.block_positions()}
    for entry in palette:
        if entry == AIR:
            continue
        assert entry in blocks, f"Palette contains an unused entry"


def test_unused_palette_entries_get_pruned():
    region = Region(0, 0, 0, 10, 10, 10)
    region[0, 0, 0] = BlockState("minecraft:stone")
    region[0, 0, 0] = AIR
    assert_valid_palette(region)


def test_region_getitem_setitem():
    region = Region(0, 0, 0, 1, 1, 1)
    stone = BlockState("minecraft:stone")
    region[0, 0, 0] = stone
    assert region[0, 0, 0] == stone


def test_region_in():
    region = Region(0, 0, 0, 10, 10, 10)
    stone = BlockState("minecraft:stone")
    assert stone not in region
    region[0, 0, 0] = stone
    assert stone in region
    region[0, 0, 0] = AIR
    assert stone not in region


def test_replace():
    region = Region(0, 0, 0, 10, 10, 10)
    stone = BlockState("minecraft:stone")
    log = BlockState("minecraft:oak_log")
    grass = BlockState("minecraft:grass_block")
    region[1, 0, 0] = stone
    region[2, 0, 0] = log
    assert region[0, 0, 0] == AIR
    region.replace(AIR, grass)
    assert region[0, 0, 0] == grass
    assert region.palette[0] == AIR
    region.replace(log, stone)
    assert region[2, 0, 0] == stone


def test_subversion():
    schematic = Schematic.load(path.join(VALID_LITEMATIC_DIRECTORY, "Subversion.litematic"))
    assert schematic.lm_subversion == 1
    with TemporaryDirectory() as temp:
        schematic.lm_subversion = 1337
        name = path.join(temp, "Subversion.litematic")
        schematic.save(name)
        schematic = Schematic.load(name)
    assert schematic.lm_subversion == 1337


def test_v6_and_v7_support():
    """Test that both Litematica v6 and v7 formats are supported."""
    # Create a test region with some blocks
    reg = Region(0, 0, 0, 5, 5, 5)
    reg[0, 0, 0] = BlockState("minecraft:stone")
    reg[1, 1, 1] = BlockState("minecraft:oak_planks")
    reg[2, 2, 2] = BlockState("minecraft:glass")

    with TemporaryDirectory() as temp:
        # Test v6
        schem_v6 = Schematic(
            name="Test v6",
            author="Test",
            description="Testing v6",
            regions={"main": reg},
            lm_version=6
        )
        assert schem_v6.lm_version == 6

        v6_path = path.join(temp, "test_v6.litematic")
        schem_v6.save(v6_path)

        # Load v6 schematic
        loaded_v6 = Schematic.load(v6_path)
        assert loaded_v6.lm_version == 6
        assert loaded_v6.name == "Test v6"
        assert "main" in loaded_v6.regions
        loaded_reg_v6 = loaded_v6.regions["main"]
        assert loaded_reg_v6[0, 0, 0] == BlockState("minecraft:stone")
        assert loaded_reg_v6[1, 1, 1] == BlockState("minecraft:oak_planks")
        assert loaded_reg_v6[2, 2, 2] == BlockState("minecraft:glass")

        # Test v7
        schem_v7 = Schematic(
            name="Test v7",
            author="Test",
            description="Testing v7",
            regions={"main": reg},
            lm_version=7
        )
        assert schem_v7.lm_version == 7

        v7_path = path.join(temp, "test_v7.litematic")
        schem_v7.save(v7_path)

        # Load v7 schematic
        loaded_v7 = Schematic.load(v7_path)
        assert loaded_v7.lm_version == 7
        assert loaded_v7.name == "Test v7"
        assert "main" in loaded_v7.regions
        loaded_reg_v7 = loaded_v7.regions["main"]
        assert loaded_reg_v7[0, 0, 0] == BlockState("minecraft:stone")
        assert loaded_reg_v7[1, 1, 1] == BlockState("minecraft:oak_planks")
        assert loaded_reg_v7[2, 2, 2] == BlockState("minecraft:glass")


def test_unsupported_version_raises_error():
    """Test that unsupported Litematica versions raise an error."""
    from litemapy.schematic import CorruptedSchematicError
    from nbtlib.tag import Compound, Int

    # Create a mock NBT with unsupported version
    nbt = Compound()
    nbt["Version"] = Int(4)  # Unsupported version (v4 is not supported)
    nbt["SubVersion"] = Int(0)
    nbt["MinecraftDataVersion"] = Int(2975)

    metadata = Compound()
    metadata["Name"] = nbtlib.tag.String("Test")
    metadata["Author"] = nbtlib.tag.String("Test")
    metadata["Description"] = nbtlib.tag.String("Test")
    metadata["TimeCreated"] = nbtlib.tag.Long(0)
    metadata["TimeModified"] = nbtlib.tag.Long(0)
    metadata["RegionCount"] = Int(0)
    metadata["TotalBlocks"] = Int(0)
    metadata["TotalVolume"] = Int(0)

    enclosing = Compound()
    enclosing["x"] = Int(0)
    enclosing["y"] = Int(0)
    enclosing["z"] = Int(0)
    metadata["EnclosingSize"] = enclosing

    nbt["Metadata"] = metadata
    nbt["Regions"] = Compound()

    # This should raise CorruptedSchematicError
    try:
        Schematic.from_nbt(nbt)
        assert False, "Expected CorruptedSchematicError for unsupported version"
    except CorruptedSchematicError as e:
        assert "Unsupported Litematica version" in str(e)
        assert "4" in str(e)
