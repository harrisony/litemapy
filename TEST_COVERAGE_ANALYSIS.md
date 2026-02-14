# Missing Test Coverage in Litemapy

## Context

This document identifies gaps in test coverage for the Litemapy project. Litemapy is a Python library for reading and editing Litematica schematic files for Minecraft. The project has a good foundation of tests (5 test files covering core functionality), but several important areas lack test coverage, particularly Entity/TileEntity classes and format conversion methods.

## Current Test Coverage Summary

**Well-Tested Areas:**
- ✅ Schematic loading and saving (basic cases)
- ✅ Region block access (`__getitem__`, `__setitem__`)
- ✅ Region filtering and replacement
- ✅ BlockState creation, properties, and NBT conversion
- ✅ LitematicaBitArray basic operations
- ✅ DiscriminatingDictionary with callbacks
- ✅ Box utility functions
- ✅ Deprecation decorator functionality

## Critical Missing Test Coverage

### 1. **Entity and TileEntity Classes (minecraft.py) - ZERO COVERAGE**

**Priority: CRITICAL**

The Entity and TileEntity classes are part of the public API but have NO test coverage.

**Missing tests for Entity:**
- `litemapy/minecraft.py:119-178` - Entity class
  - Constructor from string ID
  - Constructor from NBT compound
  - `to_nbt()` - Serialize to NBT
  - `from_nbt()` - Deserialize from NBT
  - `add_tag()` / `get_tag()` - NBT tag management
  - Properties: `id`, `position`, `rotation`, `motion`, `data`
  - Edge cases: Missing required NBT keys (should raise `RequiredKeyMissingException`)

**Missing tests for TileEntity:**
- `litemapy/minecraft.py:180-220` - TileEntity class
  - Constructor from NBT compound
  - `to_nbt()` - Serialize to NBT
  - `from_nbt()` - Deserialize from NBT
  - `add_tag()` / `get_tag()` - NBT tag management
  - Properties: `position`, `data`
  - Edge cases: Missing position data

**Recommended approach:**
- Create test NBT data for common entities (pig, armor stand, item)
- Create test NBT data for tile entities (chest, sign, furnace)
- Test round-trip NBT conversion
- Test property getters/setters
- Test exception handling for malformed data

---

### 2. **Region Format Conversion Methods (schematic.py) - ZERO COVERAGE**

**Priority: HIGH**

Region supports exporting/importing Sponge and Minecraft Structure formats, but these are completely untested.

**Missing tests:**
- `litemapy/schematic.py:398-450` - `to_sponge_nbt()` - Export to WorldEdit Sponge format
- `litemapy/schematic.py:452-492` - `from_sponge_nbt()` - Import from Sponge format
- `litemapy/schematic.py:494-539` - `to_structure_nbt()` - Export to Minecraft structure
- `litemapy/schematic.py:541-576` - `from_structure_nbt()` - Import from structure format

**Recommended approach:**
- Create test schematics in Sponge format
- Create test Minecraft structure files
- Test export → import round-trip for each format
- Verify block data preservation
- Verify metadata preservation (MC version)
- Test with different parameters (gzipped, byte order)

---

### 3. **Region Entity/TileEntity Integration (schematic.py) - ZERO COVERAGE**

**Priority: HIGH**

Regions can contain entities and tile entities, but this functionality is untested.

**Missing tests:**
- `litemapy/schematic.py:159` - `entities` property getter/setter
- `litemapy/schematic.py:163` - `tile_entities` property getter/setter
- `litemapy/schematic.py:167` - `block_ticks` property
- `litemapy/schematic.py:171` - `fluid_ticks` property
- Integration: Loading schematics with entities/tile entities
- Integration: Saving regions with entities/tile entities
- Edge cases: Entities at various positions within region

**Recommended approach:**
- Create test schematic with armor stand entity
- Create test schematic with chest tile entity
- Test adding entities to region
- Test entity persistence through save/load cycle
- Test entity position validation

---

### 4. **Region Block Statistics Methods (schematic.py) - ZERO COVERAGE**

**Priority: MEDIUM**

**Missing tests:**
- `litemapy/schematic.py:331` - `count_blocks()` / `getblockcount()` - Count non-air blocks
- `litemapy/schematic.py:339` - `volume()` / `getvolume()` - Calculate total volume
- Edge cases: Empty region (all air), full region (no air)

**Recommended approach:**
- Create region with known block counts
- Test volume calculation with positive/negative dimensions
- Test count_blocks with various fill percentages

---

### 5. **LitematicaBitArray Advanced Methods (storage.py) - PARTIAL COVERAGE**

**Priority: MEDIUM**

**Missing tests:**
- `litemapy/storage.py:20` - `from_nbt_long_array()` - Static constructor from NBT
- `litemapy/storage.py:33` - `_to_long_list()` - Convert to long list
- `litemapy/storage.py:41` - `_to_nbt_long_array()` - Convert to NBT format
- `litemapy/storage.py:67` - `__iter__()` - Iterator protocol
- `litemapy/storage.py:72` - `__reversed__()` - Reversed iteration
- Round-trip: Create array → to NBT → from NBT → verify equality

**Recommended approach:**
- Test NBT conversion round-trip
- Test iteration yields all values in order
- Test reversed iteration
- Test with various bit widths (1-bit, 4-bit, 16-bit)

---

### 6. **Schematic Metadata Methods (schematic.py) - PARTIAL COVERAGE**

**Priority: MEDIUM**

**Missing tests:**
- `litemapy/schematic.py:93` - `update_metadata()` / `updatemeta()` - Updates modified timestamp
- `litemapy/schematic.py:157` - `preview` property getter/setter
- Edge cases: Unicode in name/author/description fields

**Recommended approach:**
- Test `update_metadata()` changes timestamp
- Test preview image data roundtrip
- Test Unicode characters in metadata fields (emoji, Chinese, etc.)

---

### 7. **Exception Handling and Edge Cases - MINIMAL COVERAGE**

**Priority: MEDIUM**

**Missing tests:**
- `litemapy/schematic.py:19` - `CorruptedSchematicError` - Never raised in tests
- `litemapy/minecraft.py:39` - `RequiredKeyMissingException` - Not tested
- File I/O errors (permissions, disk full, corrupt files)
- Invalid NBT data handling
- Region name validation (`_can_add_region()`)

**Recommended approach:**
- Create intentionally corrupted schematic files
- Test loading corrupted files raises `CorruptedSchematicError`
- Test Entity/TileEntity with missing NBT keys raises `RequiredKeyMissingException`
- Test invalid region names are rejected

---

### 8. **BlockState Edge Cases (minecraft.py) - PARTIAL COVERAGE**

**Priority: LOW**

**Missing tests:**
- `litemapy/minecraft.py:82` - `blockid` deprecated property
- Complex property names with special characters
- Empty property values
- Very long property strings

**Recommended approach:**
- Test `blockid` property getter (deprecated alias)
- Test BlockState with unusual but valid property names
- Test property sorting in identifier string

---

### 9. **Region Deprecated Methods (schematic.py) - MINIMAL COVERAGE**

**Priority: LOW**

**Missing tests:**
- `litemapy/schematic.py:194` - `getblock()` - Deprecated block getter
- `litemapy/schematic.py:198` - `setblock()` - Deprecated block setter
- Verify these work identically to `__getitem__` / `__setitem__`

**Recommended approach:**
- Test getblock/setblock match array syntax behavior
- Ensure deprecation doesn't break functionality

---

### 10. **File I/O Parameter Variations (schematic.py) - MINIMAL COVERAGE**

**Priority: LOW**

**Missing tests:**
- `litemapy/schematic.py:60` - `save()` with different parameters:
  - `update_meta=False` - Don't update timestamp
  - `save_soft=False` - Force full save
  - `gzipped=False` - Uncompressed output
  - `byteorder='little'` - Little-endian byte order
- Verify each parameter combination works correctly

**Recommended approach:**
- Create schematic, save with each parameter variation
- Reload and verify integrity
- Check file size differences (gzipped vs uncompressed)

---

## Summary Statistics

| Category | Methods/Functions | Current Coverage | Gap |
|----------|-------------------|------------------|-----|
| Entity class | 6 methods | 0% | 6 untested |
| TileEntity class | 5 methods | 0% | 5 untested |
| Region format conversion | 4 methods | 0% | 4 untested |
| Region collections | 4 properties | 0% | 4 untested |
| Region statistics | 2 methods | 0% | 2 untested |
| LitematicaBitArray advanced | 5 methods | 0% | 5 untested |
| Schematic metadata | 2 methods + 1 property | 0% | 3 untested |
| Exception classes | 4 types | 25% | 3 undertested |
| File I/O variations | Multiple parameters | 20% | Most combinations untested |

**Total estimated untested methods: ~35-40**

## Verification

After adding tests, verify coverage by:
1. Run full test suite: `python -m pytest tests/ -v`
2. Check coverage report: `python -m pytest --cov=litemapy --cov-report=html tests/`
3. Review coverage HTML report for remaining gaps
4. Ensure all new tests pass consistently

## Notes

- The project has good coverage for core Schematic/Region block operations
- Entity and TileEntity are the most critical gaps (public API, zero coverage)
- Format conversion methods are high-value features that need testing
- Edge cases and error handling could be significantly improved
- Private methods (prefixed with `_` or `__`) are intentionally excluded from this analysis unless they're critical internal functionality
