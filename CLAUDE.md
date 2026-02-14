# Litemapy - Claude Development Guide

## Project Overview

Litemapy is a Python library for reading and editing Litematica schematic files. Litematica is a Minecraft mod by maruohon that allows players to create and manage schematic files for building structures.

**Repository**: https://github.com/SmylerMC/litemapy
**Documentation**: https://litemapy.readthedocs.io
**Python Version**: >=3.9
**License**: GNU General Public License v3 (GPLv3)

## Project Purpose

Litemapy provides an easy-to-use Python API for:
- Reading and writing `.litematic` files
- Managing regions within schematics
- Handling block states, entities, and tile entities
- Working with Minecraft block data programmatically

## Project Structure

```
litemapy/
├── litemapy/              # Main package directory
│   ├── __init__.py       # Package exports: Schematic, Region, BlockState, Entity, TileEntity
│   ├── schematic.py      # Core classes: Schematic and Region
│   ├── minecraft.py      # Minecraft-specific classes: BlockState, Entity, TileEntity
│   ├── storage.py        # Data storage utilities: LitematicaBitArray, DiscriminatingDictionary
│   ├── boxes.py          # 3D box/coordinate utilities
│   ├── info.py           # Version constants and metadata
│   └── deprecation.py    # Deprecation warning utilities
├── tests/                # Test suite
│   ├── test_schematics.py    # Schematic loading/saving tests
│   ├── test_storage.py       # Storage utilities tests
│   ├── test_boxes.py         # Box utilities tests
│   ├── test_minecraft.py     # Minecraft data tests
│   ├── test_deprecation.py   # Deprecation warnings tests
│   ├── constants.py          # Test constants
│   ├── helper.py             # Test helper functions
│   └── litematics/           # Test schematic files
│       ├── valid/            # Valid test schematics
│       └── filter/           # Filter test schematics
├── examples/             # Usage examples
│   ├── example1.py      # Basic planet creation example
│   └── filter.py        # Block filtering example
├── docs/                # Sphinx documentation
│   └── source/          # Documentation source files
├── setup.py             # Package setup and installation
├── README.md            # User-facing documentation
├── CONTRIBUTING.md      # Contribution guidelines
└── CHANGELOG.md         # Version history
```

## Key Concepts

### Schematic
The main class representing a `.litematic` file. Contains:
- Metadata (name, author, description, timestamps)
- One or more named regions
- Preview image data (optional)
- Version information (Litematica version, Minecraft data version)

### Region
A 3D rectangular area containing blocks. Each region has:
- Position coordinates (x, y, z)
- Size dimensions (width, height, length)
- Block data stored in a compact bit array format
- Optional entities and tile entities
- Block palette mapping

### BlockState
Represents a Minecraft block with properties. Examples:
- `minecraft:stone`
- `minecraft:oak_stairs[facing=north,half=top]`
- `minecraft:chest[facing=south,type=single,waterlogged=false]`

### Entity
Represents a Minecraft entity (mobs, items, etc.) with NBT data.

### TileEntity
Represents a block entity (chests, signs, etc.) with additional data.

## Development Setup

### Installation for Development

```bash
# Clone the repository
git clone https://github.com/SmylerMC/litemapy.git
cd litemapy

# Install in development mode
pip install -e .

# Install dependencies
pip install nbtlib>=2.0.3 typing_extensions
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_schematics.py

# Run with verbose output
python -m pytest -v tests/
```

### Building Documentation

```bash
cd docs
pip install -r requirements.txt
make html
# Output will be in docs/build/html/
```

## Dependencies

- **nbtlib** (>=2.0.3): NBT (Named Binary Tag) format parsing for Minecraft data
- **typing_extensions**: Extended typing support for Python
- **numpy**: Array operations for block storage (imported in schematic.py)

## Important Implementation Details

### Block Storage

Blocks are stored using a custom bit array implementation (`LitematicaBitArray` in storage.py:1) that compacts block palette indices into the minimum number of bits needed. This matches the Litematica file format specification.

### Coordinate System

- Regions have local coordinates starting at (0, 0, 0)
- Regions can be positioned anywhere in world coordinates
- The coordinate system follows Minecraft's conventions (Y is vertical)

### File Format

Litemapy uses the NBT (Named Binary Tag) format via the `nbtlib` library. The `.litematic` file structure is defined by the Litematica mod and includes:
- Metadata section
- Regions dictionary
- Block palettes per region
- Compressed block data

## Common Development Tasks

### Adding a New Feature

1. Implement the feature in the appropriate module (schematic.py, minecraft.py, etc.)
2. Add tests in the `tests/` directory
3. Update documentation in `docs/source/`
4. Update CHANGELOG.md
5. Ensure all tests pass

### Handling Block Data

The block storage system uses palette-based compression:
1. Each unique block state gets a palette index
2. Indices are stored in a bit array with minimal bit width
3. Use `Region[x, y, z]` to get/set blocks at coordinates

### Working with NBT Data

NBT tags are provided by `nbtlib`:
- `Compound`: Dictionary-like tag
- `List`: List tag
- `String`, `Int`, `Long`, `Short`, `Byte`: Primitive types
- `IntArray`, `ByteArray`: Array types

## Testing Strategy

Tests are organized by module:
- **test_schematics.py**: Schematic creation, loading, saving, region management
- **test_storage.py**: Bit array storage, palette systems
- **test_boxes.py**: 3D coordinate and box utilities
- **test_minecraft.py**: Block state parsing, entity handling
- **test_deprecation.py**: Deprecated API warnings

Test data in `tests/litematics/` includes:
- Real-world schematic files for validation
- Edge cases and specific feature tests

## Code Style and Conventions

- Python 3.9+ syntax and features
- Type hints used throughout (see schematic.py for examples)
- Docstrings follow standard Python conventions
- Class attributes declared with type hints at class level
- Methods return types are annotated

## Version Management

- Version defined in `litemapy/info.py`
- Follows semantic versioning
- Currently in Beta (Development Status :: 4 - Beta)

## Known Limitations

From README.md:
- **Full support**: Regions, block storage, basic metadata
- **Partial support**: Entities, tile entities, pending block updates, preview images

## Working with Examples

The `examples/` directory contains:
- **example1.py**: Creates a sphere of light blue concrete blocks (planet)
- **filter.py**: Demonstrates filtering blocks by type or properties

Run examples from the repository root:
```bash
python examples/example1.py
```

## Debugging Tips

1. Use `Schematic.load()` to inspect existing .litematic files
2. Check block palettes with `region.palette`
3. Verify region bounds with `region.xrange()`, `region.yrange()`, `region.zrange()`
4. Print block states: `print(region[x, y, z])`
5. NBT data can be inspected directly: `.nbt` attributes exist on many objects

## Contributing

See CONTRIBUTING.md and the full documentation at https://litemapy.readthedocs.io/en/latest/contributing.html

## Support

- **Issues**: https://github.com/SmylerMC/litemapy/issues
- **Documentation**: https://litemapy.readthedocs.io
- **PyPI**: https://pypi.org/project/litemapy/
