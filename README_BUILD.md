# Spanish Pronunciation Deck Creator - Build Instructions

This directory contains the build system for the Spanish Pronunciation Deck Creator Anki addon.

## Quick Start

```bash
# Build the addon (creates .ankiaddon file)
python build_addon.py

# Build with version increment
python build_addon.py --version patch

# Build with custom name
python build_addon.py --name my_custom_addon

# Verify existing package
python build_addon.py --verify-only
```

## Build Script Features

### 🔧 **Automated Building**
- Validates source directory and required files
- Creates properly formatted .ankiaddon zip files
- Automatic file exclusion (no temp files, cache, etc.)
- Package integrity verification

### 📦 **Version Management**
```bash
python build_addon.py --version major   # 1.2.1 → 2.0.0
python build_addon.py --version minor   # 1.2.1 → 1.3.0  
python build_addon.py --version patch   # 1.2.1 → 1.2.2
```

### 🧹 **Cleanup & Organization**
- Automatically cleans up old .ankiaddon files (keeps 3 most recent)
- Validates package contents and structure
- UTF-8 encoding handling throughout

### 🔍 **Verification**
- Tests zip file integrity
- Validates manifest.json structure
- Confirms all required files are present
- Reports package size and file count

## Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--source` | `-s` | Source directory (default: spanish_pronunciation_addon) |
| `--output` | `-o` | Output directory (default: current directory) |
| `--name` | `-n` | Custom output filename |
| `--version` | `-v` | Increment version: major/minor/patch |
| `--no-clean` | | Don't clean up old package files |
| `--verify-only` | | Only verify existing package, don't build |

## Project Structure

```
spanish_pronunciation_addon/           # Source directory
├── __init__.py                       # Main addon code
├── manifest.json                     # Addon metadata (REQUIRED)
├── config.json                       # Configuration settings (REQUIRED)
├── logger.py                         # Logging utilities (REQUIRED)
├── config.md                         # Configuration docs (optional)
└── README.md                         # Documentation (optional)

build_addon.py                        # Build script
spanish_pronunciation_deck_creator_v*.ankiaddon  # Generated packages
```

## Required Files

The build script validates these files exist:
- ✅ `__init__.py` - Main addon functionality
- ✅ `manifest.json` - Anki addon metadata
- ✅ `config.json` - Default configuration
- ✅ `logger.py` - Enhanced logging system

## Build Process

1. **Validation** - Checks source directory and required files
2. **Version Management** - Optionally increments version number
3. **File Collection** - Gathers all addon files (excludes temp/cache files)
4. **Package Creation** - Creates compressed .ankiaddon file
5. **Verification** - Validates package integrity and structure
6. **Cleanup** - Removes old package files (keeps 3 most recent)

## Usage Examples

### Basic Build
```bash
python build_addon.py
# Output: spanish_pronunciation_deck_creator_v1.2.1.ankiaddon
```

### Release Build
```bash
# Increment version and build
python build_addon.py --version minor
# Output: spanish_pronunciation_deck_creator_v1.3.0.ankiaddon
```

### Custom Build
```bash
# Custom name, no cleanup
python build_addon.py --name "debug_version" --no-clean
# Output: debug_version.ankiaddon
```

### Verification Only
```bash
# Check existing package without rebuilding
python build_addon.py --verify-only
```

## Output

The build script provides detailed output:
- ✅ File validation results
- 📁 Files included in package
- 📊 Package size and file count
- 🔍 Verification results
- 🧹 Cleanup operations

## Error Handling

The script validates:
- Source directory exists
- Required files are present
- Manifest.json is valid JSON with required fields
- Package creation succeeds
- Package contents are correct

If any step fails, the script exits with an error message and non-zero exit code.

## Integration

This build script can be integrated into:
- **Development workflow** - Build and test iterations
- **CI/CD pipelines** - Automated builds and releases
- **Release process** - Version management and distribution
- **Testing** - Package verification and validation