#!/usr/bin/env python3
"""
Spanish Pronunciation Deck Creator - Addon Build Script
Automatically builds the .ankiaddon package from source files
"""

import os
import sys
import json
import zipfile
import shutil
import argparse
from datetime import datetime
from pathlib import Path

class AddonBuilder:
    def __init__(self, source_dir="spanish_pronunciation_addon", output_dir="."):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.required_files = [
            "__init__.py",
            "manifest.json", 
            "config.json",
            "logger.py"
        ]
        self.optional_files = [
            "config.md",
            "README.md"
        ]
        
    def validate_source_directory(self):
        """Validate that source directory exists and contains required files"""
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {self.source_dir}")
        
        missing_files = []
        for file in self.required_files:
            file_path = self.source_dir / file
            if not file_path.exists():
                missing_files.append(file)
        
        if missing_files:
            raise FileNotFoundError(f"Missing required files: {missing_files}")
        
        print(f"✓ Source directory validated: {self.source_dir}")
        return True
    
    def load_manifest(self):
        """Load and validate manifest.json"""
        manifest_path = self.source_dir / "manifest.json"
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            required_keys = ["package", "name", "version", "description"]
            missing_keys = [key for key in required_keys if key not in manifest]
            if missing_keys:
                raise ValueError(f"Missing required manifest keys: {missing_keys}")
            
            print(f"✓ Manifest loaded: {manifest['name']} v{manifest['version']}")
            return manifest
            
        except Exception as e:
            raise ValueError(f"Failed to load manifest.json: {e}")
    
    def increment_version(self, version_type="patch"):
        """Increment version in manifest.json"""
        manifest_path = self.source_dir / "manifest.json"
        manifest = self.load_manifest()
        
        version_parts = manifest["version"].split(".")
        if len(version_parts) != 3:
            raise ValueError(f"Invalid version format: {manifest['version']}")
        
        major, minor, patch = map(int, version_parts)
        
        if version_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif version_type == "minor":
            minor += 1
            patch = 0
        elif version_type == "patch":
            patch += 1
        else:
            raise ValueError(f"Invalid version type: {version_type}")
        
        new_version = f"{major}.{minor}.{patch}"
        manifest["version"] = new_version
        
        # Update mod timestamp
        manifest["mod"] = int(datetime.now().timestamp())
        
        # Write back to file
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=4)
        
        print(f"✓ Version incremented: {manifest['version']} → {new_version}")
        return new_version
    
    def collect_files(self):
        """Collect all files to include in the addon"""
        files_to_include = []
        
        # Add required files
        for file in self.required_files:
            file_path = self.source_dir / file
            if file_path.exists():
                files_to_include.append(file_path)
        
        # Add optional files
        for file in self.optional_files:
            file_path = self.source_dir / file
            if file_path.exists():
                files_to_include.append(file_path)
                print(f"✓ Including optional file: {file}")
        
        return files_to_include
    
    def create_package(self, output_name=None, exclude_patterns=None):
        """Create the .ankiaddon package"""
        manifest = self.load_manifest()
        
        if output_name is None:
            package_name = manifest["package"]
            version = manifest["version"]
            output_name = f"{package_name}_v{version}.ankiaddon"
        
        if not output_name.endswith('.ankiaddon'):
            output_name += '.ankiaddon'
        
        output_path = self.output_dir / output_name
        exclude_patterns = exclude_patterns or ['*.ankiaddon', '__pycache__', '*.pyc', '.git*']
        
        print(f"Creating package: {output_path}")
        
        files_added = []
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.source_dir):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if not any(
                    Path(d).match(pattern) for pattern in exclude_patterns
                )]
                
                for file in files:
                    # Filter out excluded files
                    if any(Path(file).match(pattern) for pattern in exclude_patterns):
                        continue
                    
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.source_dir)
                    file_size = file_path.stat().st_size
                    
                    zipf.write(file_path, arcname)
                    files_added.append((str(arcname), file_size))
                    print(f"  Added: {arcname} ({file_size} bytes)")
        
        package_size = output_path.stat().st_size
        print(f"\n✓ Package created successfully!")
        print(f"  File: {output_path}")
        print(f"  Size: {package_size:,} bytes")
        print(f"  Files: {len(files_added)}")
        
        return output_path, files_added
    
    def verify_package(self, package_path):
        """Verify the created package"""
        print(f"\nVerifying package: {package_path}")
        
        try:
            with zipfile.ZipFile(package_path, 'r') as zipf:
                # Test the zip file integrity
                bad_file = zipf.testzip()
                if bad_file:
                    raise zipfile.BadZipFile(f"Corrupt file in archive: {bad_file}")
                
                # Check required files are present
                file_list = zipf.namelist()
                missing_required = []
                for required_file in self.required_files:
                    if required_file not in file_list:
                        missing_required.append(required_file)
                
                if missing_required:
                    raise ValueError(f"Missing required files in package: {missing_required}")
                
                # Validate manifest.json in package
                try:
                    manifest_data = zipf.read("manifest.json")
                    manifest = json.loads(manifest_data.decode('utf-8'))
                    print(f"  ✓ Manifest: {manifest['name']} v{manifest['version']}")
                except Exception as e:
                    raise ValueError(f"Invalid manifest.json in package: {e}")
                
                print(f"  ✓ Package integrity verified")
                print(f"  ✓ Contains {len(file_list)} files")
                
                return True
                
        except Exception as e:
            print(f"  ✗ Package verification failed: {e}")
            return False
    
    def clean_old_packages(self, keep_count=3):
        """Clean up old package files, keeping only the most recent ones"""
        pattern = "*.ankiaddon"
        addon_files = list(self.output_dir.glob(pattern))
        
        if len(addon_files) <= keep_count:
            return
        
        # Sort by modification time, newest first
        addon_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        files_to_remove = addon_files[keep_count:]
        for file_path in files_to_remove:
            try:
                file_path.unlink()
                print(f"  Cleaned up: {file_path.name}")
            except Exception as e:
                print(f"  Warning: Could not remove {file_path.name}: {e}")
    
    def build(self, increment_version=None, output_name=None, clean=True):
        """Main build process"""
        print("Spanish Pronunciation Deck Creator - Addon Builder")
        print("=" * 55)
        
        try:
            # Validate source
            self.validate_source_directory()
            
            # Increment version if requested
            if increment_version:
                self.increment_version(increment_version)
            
            # Create package
            package_path, files_added = self.create_package(output_name)
            
            # Verify package
            if not self.verify_package(package_path):
                raise RuntimeError("Package verification failed")
            
            # Clean up old packages
            if clean:
                self.clean_old_packages()
            
            print(f"\n🎉 Build completed successfully!")
            print(f"   Package: {package_path}")
            
            return package_path
            
        except Exception as e:
            print(f"\n❌ Build failed: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Build Spanish Pronunciation Deck Creator addon")
    parser.add_argument("--source", "-s", default="spanish_pronunciation_addon",
                       help="Source directory (default: spanish_pronunciation_addon)")
    parser.add_argument("--output", "-o", default=".",
                       help="Output directory (default: current directory)")
    parser.add_argument("--name", "-n", 
                       help="Custom output filename (default: auto-generated)")
    parser.add_argument("--version", "-v", choices=["major", "minor", "patch"],
                       help="Increment version before building")
    parser.add_argument("--no-clean", action="store_true",
                       help="Don't clean up old package files")
    parser.add_argument("--verify-only", action="store_true",
                       help="Only verify existing package, don't build")
    
    args = parser.parse_args()
    
    builder = AddonBuilder(args.source, args.output)
    
    if args.verify_only:
        # Find most recent .ankiaddon file
        addon_files = list(Path(args.output).glob("*.ankiaddon"))
        if not addon_files:
            print("No .ankiaddon files found to verify")
            sys.exit(1)
        
        latest_file = max(addon_files, key=lambda x: x.stat().st_mtime)
        success = builder.verify_package(latest_file)
        sys.exit(0 if success else 1)
    
    # Build the addon
    builder.build(
        increment_version=args.version,
        output_name=args.name,
        clean=not args.no_clean
    )

if __name__ == "__main__":
    main()