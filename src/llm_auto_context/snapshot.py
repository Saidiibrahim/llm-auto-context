"""Core functionality for generating code snapshots."""

import os
from pathlib import Path
from typing import Set

from .config import SnapshotConfig

def should_include_file(
    file_path: Path,
    config: SnapshotConfig,
    base_dir: Path
) -> bool:
    """Check if a file should be included in the snapshot."""
    # Check if file is in exclude list
    rel_path = str(file_path.relative_to(base_dir))
    if any(exclude in rel_path for exclude in config.exclude_files):
        return False

    # Check if file is in excluded directory
    for exclude_dir in config.exclude_dirs:
        if exclude_dir in rel_path.split(os.sep):
            return False

    # Check file extension
    return file_path.suffix.lower() in config.include_extensions

def create_code_snapshot(config: SnapshotConfig) -> Path:
    """Create a code snapshot based on configuration."""
    base_dir = Path.cwd()
    output_path = config.get_output_path(base_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    processed_files: Set[Path] = set()

    with open(output_path, "w", encoding="utf-8") as out_f:
        for directory in config.directories:
            dir_path = Path(directory).resolve()
            if not dir_path.exists():
                print(f"Warning: Directory {directory} does not exist, skipping.")
                continue

            # Walk through directory structure
            for root, _, files in os.walk(dir_path):
                root_path = Path(root)
                
                # Sort files for consistency
                for file_name in sorted(files):
                    file_path = root_path / file_name
                    
                    # Skip if already processed or shouldn't be included
                    if (file_path in processed_files or
                        file_path.name.startswith('.') or
                        not should_include_file(file_path, config, base_dir)):
                        continue

                    # Write file header and content
                    rel_path = file_path.relative_to(base_dir)
                    out_f.write(f"\n\n# ======= File: {rel_path} =======\n\n")
                    
                    try:
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        out_f.write(content)
                        processed_files.add(file_path)
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")

    return output_path 