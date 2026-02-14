import pytest

from litemapy import BlockState, Entity, TileEntity
from litemapy.minecraft import is_valid_identifier
from litemapy.minecraft import InvalidIdentifier, RequiredKeyMissingException
from litemapy.schematic import AIR
from nbtlib.tag import Int, Double, String, List, Compound


def test_blockstate_initialization():
    prop = {"test1": "testval", "test2": "testval2"}
    b = BlockState("minecraft:stone", **prop)
    assert len(prop) == len(b)
    for k, v in prop.items():
        assert b[k] == v


def test_cannot_create_blockstate_with_invalid_id():
    ids = (
        "",
        "minecraft stone",
        "stone",
        "minecraft:stone[property=value]",
    )
    for id_ in ids:
        with pytest.raises(InvalidIdentifier):
            BlockState(id_, prop="val")
        with pytest.raises(InvalidIdentifier):
            AIR.with_id(id_)


def test_blockstate_nbt_is_identity():
    prop = {"test1": "testval", "test2": "testval2"}
    blockstate_1 = BlockState("minecraft:stone", **prop)
    nbt = blockstate_1.to_nbt()
    blockstate_2 = BlockState.from_nbt(nbt)
    assert blockstate_1 == blockstate_2


def test_blockstate_with_properties():
    prop = {"test1": "testval1", "test2": "testval2"}
    blockstate_1 = BlockState("minecraft:stone", **prop)
    blockstate_2 = blockstate_1.with_properties(test3="testval3", test4="testval4")
    assert blockstate_2.to_block_state_identifier() == "minecraft:stone[test1=testval1,test2=testval2,test3=testval3,test4=testval4]"

    blockstate_3 = blockstate_2.with_properties(test4=None)
    assert blockstate_3.to_block_state_identifier() == "minecraft:stone[test1=testval1,test2=testval2,test3=testval3]"


def test_blockstate_properties_iter():
    prop = {"test1": "testval1", "test2": "testval2"}
    blockstate = BlockState("minecraft:stone", **prop)
    rebuilt = {}
    for p, v in blockstate.properties():
        rebuilt[p] = v
    assert rebuilt == prop


def test_blockstate_contains():
    blockstate_1 = BlockState("minecraft:stone", test1="testval1")
    assert "test1" in blockstate_1
    assert "test2" not in blockstate_1


def test_blockstate_is_hashable():
    state1 = BlockState("minecraft:air")
    state2 = BlockState("minecraft:air")
    assert state1 == state2
    assert hash(state1) == hash(state2)
    assert hash(state1) == hash(state1)


def test_is_valid_identifier():
    assert is_valid_identifier("minecraft:air")
    assert is_valid_identifier("minecraft:stone_cutter")
    assert is_valid_identifier("terramap:path/is/allowed_slashes.png")
    assert is_valid_identifier("weird.mod-id:both_are_allowed-dashes-and_underscores.and.dots")

    assert not is_valid_identifier("")
    assert not is_valid_identifier(" ")
    assert not is_valid_identifier("minecraft:minecraft:stone")
    assert not is_valid_identifier("minecraft:oak_stairs[facing=north]")
    assert not is_valid_identifier("minecraft")


# ============================================================================
# Entity Tests
# ============================================================================

def test_entity_constructor_from_string():
    """Test creating an Entity from a string ID."""
    entity = Entity("minecraft:pig")
    assert entity.id == "minecraft:pig"
    assert entity.position == (0.0, 0.0, 0.0)
    assert entity.rotation == (0.0, 0.0)
    assert entity.motion == (0.0, 0.0, 0.0)


def test_entity_constructor_from_nbt():
    """Test creating an Entity from NBT compound."""
    nbt = Compound({
        'id': String('minecraft:armor_stand'),
        'Pos': List[Double]([Double(10.5), Double(64.0), Double(-20.5)]),
        'Rotation': List[Double]([Double(90.0), Double(0.0)]),
        'Motion': List[Double]([Double(0.1), Double(-0.05), Double(0.2)])
    })
    entity = Entity(nbt)
    assert entity.id == "minecraft:armor_stand"
    assert entity.position == (10.5, 64.0, -20.5)
    assert entity.rotation == (90.0, 0.0)
    assert entity.motion == (0.1, -0.05, 0.2)


def test_entity_missing_id_raises_exception():
    """Test that Entity without 'id' raises RequiredKeyMissingException."""
    nbt = Compound({
        'Pos': List[Double]([Double(0.0), Double(0.0), Double(0.0)])
    })
    with pytest.raises(RequiredKeyMissingException) as exc_info:
        Entity(nbt)
    assert exc_info.value.key == 'id'


def test_entity_missing_optional_fields_uses_defaults():
    """Test that Entity creates default values for missing optional fields."""
    nbt = Compound({
        'id': String('minecraft:chicken')
    })
    entity = Entity(nbt)
    assert entity.position == (0.0, 0.0, 0.0)
    assert entity.rotation == (0.0, 0.0)
    assert entity.motion == (0.0, 0.0, 0.0)


def test_entity_to_nbt():
    """Test Entity serialization to NBT."""
    entity = Entity("minecraft:zombie")
    nbt = entity.to_nbt()

    assert 'id' in nbt
    assert 'Pos' in nbt
    assert 'Rotation' in nbt
    assert 'Motion' in nbt
    assert str(nbt['id']) == 'minecraft:zombie'


def test_entity_from_nbt():
    """Test Entity.from_nbt() static method."""
    nbt = Compound({
        'id': String('minecraft:creeper'),
        'Pos': List[Double]([Double(5.0), Double(70.0), Double(5.0)]),
        'Rotation': List[Double]([Double(180.0), Double(0.0)]),
        'Motion': List[Double]([Double(0.0), Double(0.0), Double(0.0)])
    })
    entity = Entity.from_nbt(nbt)
    assert entity.id == "minecraft:creeper"
    assert entity.position == (5.0, 70.0, 5.0)


def test_entity_fromnbt_deprecated():
    """Test Entity.fromnbt() deprecated alias."""
    nbt = Compound({
        'id': String('minecraft:skeleton'),
        'Pos': List[Double]([Double(1.0), Double(2.0), Double(3.0)]),
        'Rotation': List[Double]([Double(0.0), Double(0.0)]),
        'Motion': List[Double]([Double(0.0), Double(0.0), Double(0.0)])
    })
    entity = Entity.fromnbt(nbt)
    assert entity.id == "minecraft:skeleton"


def test_entity_nbt_roundtrip():
    """Test Entity NBT round-trip conversion."""
    nbt1 = Compound({
        'id': String('minecraft:item'),
        'Pos': List[Double]([Double(100.5), Double(50.0), Double(-100.5)]),
        'Rotation': List[Double]([Double(45.0), Double(-15.0)]),
        'Motion': List[Double]([Double(0.5), Double(-0.1), Double(0.3)]),
        'Item': Compound({
            'id': String('minecraft:diamond'),
            'Count': Int(64)
        })
    })
    entity1 = Entity(nbt1)
    nbt2 = entity1.to_nbt()
    entity2 = Entity.from_nbt(nbt2)

    assert entity1.id == entity2.id
    assert entity1.position == entity2.position
    assert entity1.rotation == entity2.rotation
    assert entity1.motion == entity2.motion
    assert 'Item' in entity2.data


def test_entity_id_property():
    """Test Entity.id property getter and setter."""
    entity = Entity("minecraft:pig")
    assert entity.id == "minecraft:pig"

    entity.id = "minecraft:cow"
    assert entity.id == "minecraft:cow"
    assert str(entity.data['id']) == "minecraft:cow"


def test_entity_position_property():
    """Test Entity.position property getter and setter."""
    entity = Entity("minecraft:villager")
    assert entity.position == (0.0, 0.0, 0.0)

    entity.position = (15.5, 65.0, -30.5)
    assert entity.position == (15.5, 65.0, -30.5)
    assert list(float(x) for x in entity.data['Pos']) == [15.5, 65.0, -30.5]


def test_entity_rotation_property():
    """Test Entity.rotation property getter and setter."""
    entity = Entity("minecraft:enderman")
    assert entity.rotation == (0.0, 0.0)

    entity.rotation = (270.0, 45.0)
    assert entity.rotation == (270.0, 45.0)
    assert list(float(x) for x in entity.data['Rotation']) == [270.0, 45.0]


def test_entity_motion_property():
    """Test Entity.motion property getter and setter."""
    entity = Entity("minecraft:arrow")
    assert entity.motion == (0.0, 0.0, 0.0)

    entity.motion = (1.0, 0.5, -0.5)
    assert entity.motion == (1.0, 0.5, -0.5)
    assert list(float(x) for x in entity.data['Motion']) == [1.0, 0.5, -0.5]


def test_entity_data_property():
    """Test Entity.data property getter and setter."""
    entity = Entity("minecraft:sheep")
    assert isinstance(entity.data, Compound)
    assert 'id' in entity.data

    new_data = Compound({
        'id': String('minecraft:wolf'),
        'Pos': List[Double]([Double(20.0), Double(70.0), Double(20.0)]),
        'Rotation': List[Double]([Double(0.0), Double(0.0)]),
        'Motion': List[Double]([Double(0.0), Double(0.0), Double(0.0)]),
        'Owner': String('PlayerName')
    })
    entity.data = new_data
    assert entity.id == 'minecraft:wolf'
    assert entity.position == (20.0, 70.0, 20.0)
    assert 'Owner' in entity.data


def test_entity_add_tag():
    """Test Entity.add_tag() method."""
    entity = Entity("minecraft:horse")

    # Add custom tag
    entity.add_tag('CustomName', String('{"text":"My Horse"}'))
    assert 'CustomName' in entity.data

    # Update position via add_tag
    entity.add_tag('Pos', List[Double]([Double(5.0), Double(5.0), Double(5.0)]))
    assert entity.position == (5.0, 5.0, 5.0)

    # Update rotation via add_tag
    entity.add_tag('Rotation', List[Double]([Double(90.0), Double(0.0)]))
    assert entity.rotation == (90.0, 0.0)

    # Update motion via add_tag
    entity.add_tag('Motion', List[Double]([Double(0.2), Double(0.0), Double(0.0)]))
    assert entity.motion == (0.2, 0.0, 0.0)

    # Update id via add_tag
    entity.add_tag('id', String('minecraft:donkey'))
    assert entity.id == 'minecraft:donkey'


def test_entity_get_tag():
    """Test Entity.get_tag() method."""
    nbt = Compound({
        'id': String('minecraft:bat'),
        'Pos': List[Double]([Double(0.0), Double(0.0), Double(0.0)]),
        'Rotation': List[Double]([Double(0.0), Double(0.0)]),
        'Motion': List[Double]([Double(0.0), Double(0.0), Double(0.0)]),
        'CustomTag': String('CustomValue')
    })
    entity = Entity(nbt)

    assert str(entity.get_tag('id')) == 'minecraft:bat'
    assert str(entity.get_tag('CustomTag')) == 'CustomValue'

    # Test KeyError for missing tag
    with pytest.raises(KeyError):
        entity.get_tag('NonExistentTag')


# ============================================================================
# TileEntity Tests
# ============================================================================

def test_tileentity_constructor():
    """Test creating a TileEntity from NBT compound."""
    nbt = Compound({
        'x': Int(10),
        'y': Int(64),
        'z': Int(-20),
        'id': String('minecraft:chest'),
        'Items': List[Compound]([])
    })
    tile_entity = TileEntity(nbt)
    assert tile_entity.position == (10, 64, -20)
    assert 'id' in tile_entity.data
    assert 'Items' in tile_entity.data


def test_tileentity_missing_position_uses_defaults():
    """Test TileEntity creates default position for missing coordinates."""
    nbt = Compound({
        'id': String('minecraft:sign')
    })
    tile_entity = TileEntity(nbt)
    assert tile_entity.position == (0, 0, 0)


def test_tileentity_partial_position():
    """Test TileEntity with only some position coordinates."""
    nbt = Compound({
        'x': Int(5),
        'id': String('minecraft:furnace')
    })
    tile_entity = TileEntity(nbt)
    assert tile_entity.position == (5, 0, 0)


def test_tileentity_to_nbt():
    """Test TileEntity serialization to NBT."""
    nbt = Compound({
        'x': Int(1),
        'y': Int(2),
        'z': Int(3),
        'id': String('minecraft:barrel')
    })
    tile_entity = TileEntity(nbt)
    nbt_output = tile_entity.to_nbt()

    assert 'x' in nbt_output
    assert 'y' in nbt_output
    assert 'z' in nbt_output
    assert int(nbt_output['x']) == 1
    assert int(nbt_output['y']) == 2
    assert int(nbt_output['z']) == 3


def test_tileentity_from_nbt():
    """Test TileEntity.from_nbt() static method."""
    nbt = Compound({
        'x': Int(15),
        'y': Int(70),
        'z': Int(25),
        'id': String('minecraft:hopper')
    })
    tile_entity = TileEntity.from_nbt(nbt)
    assert tile_entity.position == (15, 70, 25)


def test_tileentity_fromnbt_deprecated():
    """Test TileEntity.fromnbt() deprecated alias."""
    nbt = Compound({
        'x': Int(7),
        'y': Int(8),
        'z': Int(9),
        'id': String('minecraft:dispenser')
    })
    tile_entity = TileEntity.fromnbt(nbt)
    assert tile_entity.position == (7, 8, 9)


def test_tileentity_nbt_roundtrip():
    """Test TileEntity NBT round-trip conversion."""
    nbt1 = Compound({
        'x': Int(100),
        'y': Int(64),
        'z': Int(-50),
        'id': String('minecraft:chest'),
        'CustomName': String('{"text":"Storage"}'),
        'Items': List[Compound]([
            Compound({
                'Slot': Int(0),
                'id': String('minecraft:diamond'),
                'Count': Int(64)
            })
        ])
    })
    tile_entity1 = TileEntity(nbt1)
    nbt2 = tile_entity1.to_nbt()
    tile_entity2 = TileEntity.from_nbt(nbt2)

    assert tile_entity1.position == tile_entity2.position
    assert 'CustomName' in tile_entity2.data
    assert 'Items' in tile_entity2.data


def test_tileentity_position_property():
    """Test TileEntity.position property getter and setter."""
    nbt = Compound({
        'x': Int(0),
        'y': Int(0),
        'z': Int(0),
        'id': String('minecraft:beacon')
    })
    tile_entity = TileEntity(nbt)
    assert tile_entity.position == (0, 0, 0)

    tile_entity.position = (50, 100, -75)
    assert tile_entity.position == (50, 100, -75)
    assert int(tile_entity.data['x']) == 50
    assert int(tile_entity.data['y']) == 100
    assert int(tile_entity.data['z']) == -75


def test_tileentity_data_property():
    """Test TileEntity.data property getter and setter."""
    nbt = Compound({
        'x': Int(5),
        'y': Int(10),
        'z': Int(15),
        'id': String('minecraft:chest')
    })
    tile_entity = TileEntity(nbt)
    assert isinstance(tile_entity.data, Compound)

    new_data = Compound({
        'x': Int(20),
        'y': Int(30),
        'z': Int(40),
        'id': String('minecraft:shulker_box'),
        'Color': Int(5)
    })
    tile_entity.data = new_data
    assert tile_entity.position == (20, 30, 40)
    assert 'Color' in tile_entity.data


def test_tileentity_add_tag():
    """Test TileEntity.add_tag() method."""
    nbt = Compound({
        'x': Int(1),
        'y': Int(2),
        'z': Int(3),
        'id': String('minecraft:sign')
    })
    tile_entity = TileEntity(nbt)

    # Add custom tag
    tile_entity.add_tag('Text1', String('{"text":"Line 1"}'))
    assert 'Text1' in tile_entity.data

    # Update position via add_tag
    tile_entity.add_tag('x', Int(10))
    assert tile_entity.position == (10, 2, 3)

    tile_entity.add_tag('y', Int(20))
    assert tile_entity.position == (10, 20, 3)

    tile_entity.add_tag('z', Int(30))
    assert tile_entity.position == (10, 20, 30)


def test_tileentity_get_tag():
    """Test TileEntity.get_tag() method."""
    nbt = Compound({
        'x': Int(5),
        'y': Int(10),
        'z': Int(15),
        'id': String('minecraft:furnace'),
        'BurnTime': Int(200),
        'CookTime': Int(100)
    })
    tile_entity = TileEntity(nbt)

    assert int(tile_entity.get_tag('x')) == 5
    assert int(tile_entity.get_tag('BurnTime')) == 200
    assert int(tile_entity.get_tag('CookTime')) == 100

    # Test KeyError for missing tag
    with pytest.raises(KeyError):
        tile_entity.get_tag('NonExistentTag')
