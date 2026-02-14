import pytest
import litemapy.storage as storage
import math
from nbtlib import LongArray

TEST_VALUES = 0, 0, 0, 12, 13, 0, 4, 0, 2, 4, 1, 3, 3, 7, 65, 9


def test_write_read_to_litematica_bit_array():
    nbits = math.ceil(math.log(max(TEST_VALUES), 2)) + 1
    arr = storage.LitematicaBitArray(len(TEST_VALUES), nbits)
    for i, e in enumerate(TEST_VALUES):
        arr[i] = e
    for i, e in enumerate(TEST_VALUES):
        print(i, e)
        assert e == arr[i]


def test_invalid_access_to_litematica_bit_array_raises_exceptions():
    arr = storage.LitematicaBitArray(10, 4)
    with pytest.raises(IndexError):
        arr[-1] = 0
    with pytest.raises(IndexError):
        arr[10] = 0
    with pytest.raises(ValueError):
        arr[0] = -1
    with pytest.raises(ValueError):
        arr[0] = 16


def test_litematica_bit_array_in():
    nbits = math.ceil(math.log(max(TEST_VALUES), 2)) + 1
    array = storage.LitematicaBitArray(len(TEST_VALUES), nbits)
    for i, e in enumerate(TEST_VALUES):
        array[i] = e
    assert 13 in array
    assert 15 not in array


def test_basic_set_get():
    def discriminator(k, v):
        print("Discriminating ", type(k), k, "=>", type(v), v)
        return v >= 0, "Need pos"

    discriminating_dictionary = storage.DiscriminatingDictionary(discriminator)
    discriminating_dictionary["0"] = 0
    assert discriminating_dictionary["0"] == 0
    assert "0" in discriminating_dictionary
    assert "0" in discriminating_dictionary.keys()
    assert 0 in discriminating_dictionary.values()
    assert discriminating_dictionary.get("1") is None
    with pytest.raises(storage.DiscriminationError):
        discriminating_dictionary['-1'] = -1
    other_dictionary = {"1": 1, "2": 2}
    discriminating_dictionary.update(other_dictionary)
    assert "1" in discriminating_dictionary
    assert "2" in discriminating_dictionary
    with pytest.raises(storage.DiscriminationError):
        discriminating_dictionary.update({"-1": -1})
    other_dictionary = {"1": 1, "2": 2}
    discriminating_dictionary = storage.DiscriminatingDictionary(lambda k, v: (v >= 0, "Need pos"), other_dictionary)
    assert "1" in discriminating_dictionary
    assert "2" in discriminating_dictionary
    discriminating_dictionary = storage.DiscriminatingDictionary(lambda k, v: (v >= 0, "Need pos"), a=1, b=2)
    assert "a" in discriminating_dictionary
    assert "b" in discriminating_dictionary


def test_discriminating_dictionary_onadd():
    class Counter:

        def __init__(self):
            self.counter = 0

        def on_add(self, k, v):
            self.counter += v

    c = Counter()
    dictionary = storage.DiscriminatingDictionary(
        lambda k, v: (v >= 0, "Need pos"),
        onadd=c.on_add,
        x=10
    )
    dictionary["a"] = 1
    assert c.counter == 1
    dictionary.update({"b": 2, "c": 3})
    assert c.counter == 6
    dictionary.setdefault("d", 4)
    assert c.counter == 10


def test_discriminating_dictionary_onremove():
    class Counter:
        def __init__(self):
            self.counter = 0

        def on_remove(self, k, v):
            self.counter += v

    c = Counter()
    dictionary = storage.DiscriminatingDictionary(
        lambda k, v: (v >= 0, "Need pos"),
        onremove=c.on_remove,
        a=1, b=2, c=3, d=4, x=10
    )
    del dictionary["a"]
    assert c.counter == 1
    dictionary.pop("b")
    assert c.counter == 3
    dictionary.pop("c")
    assert c.counter == 6
    dictionary.pop("d")
    assert c.counter == 10
    dictionary.popitem()
    assert c.counter == 20
    c = Counter()
    dictionary = storage.DiscriminatingDictionary(
        lambda k, v: (v >= 0, "Need pos"),
        onremove=c.on_remove,
        a=1, b=2, c=3, d=4, x=10
    )
    dictionary.clear()
    assert c.counter == 20


def test_discriminating_dictionary_onadd_onremove():
    class Counter:
        def __init__(self):
            self.added = 0
            self.removed = 0

        def on_remove(self, k, v):
            self.removed += v

        def on_add(self, k, v):
            self.added += v

    c = Counter()
    dictionary = storage.DiscriminatingDictionary(
        lambda k, v: (v >= 0, "Need pos"),
        onadd=c.on_add,
        onremove=c.on_remove,
        a=1, b=2, c=3, d=4, x=10
    )
    dictionary["c"] = 7
    assert c.added == 7
    assert c.removed == 3
    dictionary.update({"x": 100, "d": 500, "y": 200})
    assert c.added == 807
    assert c.removed == 17


# ============================================================================
# LitematicaBitArray Advanced Methods Tests
# ============================================================================

def test_litematica_bit_array_from_nbt_long_array():
    """Test creating LitematicaBitArray from NBT LongArray."""
    # Create array and populate with test values
    nbits = math.ceil(math.log(max(TEST_VALUES), 2)) + 1
    arr1 = storage.LitematicaBitArray(len(TEST_VALUES), nbits)
    for i, e in enumerate(TEST_VALUES):
        arr1[i] = e

    # Convert to NBT LongArray and back
    nbt_long_array = arr1._to_nbt_long_array()
    arr2 = storage.LitematicaBitArray.from_nbt_long_array(nbt_long_array, len(TEST_VALUES), nbits)

    # Verify all values match
    for i, e in enumerate(TEST_VALUES):
        assert arr2[i] == e


def test_litematica_bit_array_from_nbt_long_array_invalid_length():
    """Test from_nbt_long_array raises ValueError for incorrect array length."""
    # Create a LongArray with wrong length
    # For 100 elements at 8 bits: expected = ceil(100 * 8 / 64) = ceil(12.5) = 13
    # But we provide only 5 longs, which is too short
    wrong_length_array = LongArray([0, 0, 0, 0, 0])

    with pytest.raises(ValueError) as exc_info:
        storage.LitematicaBitArray.from_nbt_long_array(wrong_length_array, 100, 8)

    assert "does not match" in str(exc_info.value)


def test_litematica_bit_array_to_long_list():
    """Test _to_long_list() conversion."""
    nbits = 8
    arr = storage.LitematicaBitArray(8, nbits)
    for i in range(8):
        arr[i] = i * 10

    long_list = arr._to_long_list()
    assert isinstance(long_list, list)
    assert all(isinstance(val, int) for val in long_list)


def test_litematica_bit_array_to_nbt_long_array():
    """Test _to_nbt_long_array() conversion."""
    nbits = 4
    arr = storage.LitematicaBitArray(10, nbits)
    for i in range(10):
        arr[i] = i

    nbt_arr = arr._to_nbt_long_array()
    assert isinstance(nbt_arr, LongArray)


def test_litematica_bit_array_nbt_roundtrip():
    """Test complete NBT round-trip conversion preserves all data."""
    # Test with various bit widths
    for nbits in [1, 2, 4, 8, 16]:
        max_val = (1 << nbits) - 1
        size = 20
        arr1 = storage.LitematicaBitArray(size, nbits)

        # Fill with test pattern
        for i in range(size):
            arr1[i] = (i * 7) % (max_val + 1)

        # Round-trip through NBT
        nbt_arr = arr1._to_nbt_long_array()
        arr2 = storage.LitematicaBitArray.from_nbt_long_array(nbt_arr, size, nbits)

        # Verify all values preserved
        for i in range(size):
            assert arr1[i] == arr2[i], f"Mismatch at index {i} with nbits={nbits}"


def test_litematica_bit_array_iter():
    """Test __iter__() iteration protocol."""
    nbits = math.ceil(math.log(max(TEST_VALUES), 2)) + 1
    arr = storage.LitematicaBitArray(len(TEST_VALUES), nbits)

    for i, e in enumerate(TEST_VALUES):
        arr[i] = e

    # Test iteration
    result = list(arr)
    assert result == list(TEST_VALUES)

    # Test iteration in for loop
    count = 0
    for i, value in enumerate(arr):
        assert value == TEST_VALUES[i]
        count += 1
    assert count == len(TEST_VALUES)


def test_litematica_bit_array_reversed():
    """Test __reversed__() method."""
    values = [1, 2, 3, 4, 5, 6, 7, 8]
    nbits = 4
    arr1 = storage.LitematicaBitArray(len(values), nbits)

    for i, val in enumerate(values):
        arr1[i] = val

    # Reverse the array
    arr2 = reversed(arr1)

    # Verify reversed values
    for i, val in enumerate(values):
        assert arr2[i] == values[len(values) - i - 1]

    # Original should be unchanged
    for i, val in enumerate(values):
        assert arr1[i] == val


def test_litematica_bit_array_iter_with_different_bit_widths():
    """Test iteration works correctly with various bit widths."""
    test_cases = [
        (1, [0, 1, 0, 1, 1, 0, 1, 0]),  # 1-bit
        (2, [0, 1, 2, 3, 0, 1, 2, 3]),  # 2-bit
        (4, [0, 5, 10, 15, 7, 3, 12, 1]),  # 4-bit
        (8, [0, 127, 255, 128, 64, 32, 16, 8]),  # 8-bit
    ]

    for nbits, values in test_cases:
        arr = storage.LitematicaBitArray(len(values), nbits)
        for i, val in enumerate(values):
            arr[i] = val

        # Test iteration yields correct values
        iterated_values = list(arr)
        assert iterated_values == values, f"Failed for nbits={nbits}"


def test_litematica_bit_array_reversed_single_element():
    """Test reversing single-element array."""
    arr1 = storage.LitematicaBitArray(1, 8)
    arr1[0] = 42

    arr2 = reversed(arr1)
    assert arr2[0] == 42


def test_litematica_bit_array_reversed_empty_behavior():
    """Test reversing empty (all zeros) array."""
    arr1 = storage.LitematicaBitArray(10, 4)
    # Leave all as 0

    arr2 = reversed(arr1)
    for i in range(10):
        assert arr2[i] == 0
