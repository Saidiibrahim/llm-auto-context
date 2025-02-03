

# ======= File: src/llm_auto_context/__init__.py =======

"""
LLM Auto Context - A CLI tool for generating code snapshots for LLM context windows.
"""

__version__ = "1.0.0" 

# ======= File: src/llm_auto_context/cli.py =======

"""CLI interface for code snapshot generation."""

import json
import sys
from pathlib import Path
from typing import List, Optional

import typer
from typing_extensions import Annotated

from .config import SnapshotConfig
from .snapshot import create_code_snapshot

app = typer.Typer(help="Generate code snapshots with configurable settings")
DEFAULT_CONFIG = ".codesnapshot.json"

def load_config(config_path: Path) -> SnapshotConfig:
    """Load config from file or return defaults."""
    if config_path.exists():
        return SnapshotConfig.model_validate(json.loads(config_path.read_text()))
    return SnapshotConfig()

@app.command()
def main(
    config: Annotated[
        Path,
        typer.Option(
            "--config",
            help="Path to config file",
            exists=False,
        )
    ] = Path(DEFAULT_CONFIG),
    directories: Annotated[
        Optional[List[str]],
        typer.Option(
            "--directory", "-d",
            help="Override directories to scan"
        )
    ] = None,
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output", "-o",
            help="Override output file path"
        )
    ] = None,
    include: Annotated[
        Optional[List[str]],
        typer.Option(
            "--include",
            help="Override file extensions to include"
        )
    ] = None,
    exclude_dir: Annotated[
        Optional[List[str]],
        typer.Option(
            "--exclude-dir",
            help="Additional directories to exclude"
        )
    ] = None,
    exclude_file: Annotated[
        Optional[List[str]],
        typer.Option(
            "--exclude-file",
            help="Additional files to exclude"
        )
    ] = None,
) -> None:
    """Generate code snapshots with configurable settings."""
    try:
        cfg = load_config(config)
        
        # Override config with CLI options
        if directories:
            cfg.directories = list(directories)
        if output:
            cfg.output_file = str(output)
        if include:
            cfg.include_extensions = list(include)
        if exclude_dir:
            cfg.exclude_dirs.extend(exclude_dir)
        if exclude_file:
            cfg.exclude_files.extend(exclude_file)

        # Create snapshot
        output_path = create_code_snapshot(cfg)
        typer.echo(f"Created snapshot at: {output_path}")

    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app() 

# ======= File: src/llm_auto_context/config.py =======

"""Configuration handling for code snapshot generation."""

from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field

class SnapshotConfig(BaseModel):
    """Configuration model for code snapshot generation."""
    
    directories: List[str] = Field(
        default=["src"],
        description="List of directories to scan for code files"
    )
    output_file: str = Field(
        default="code_snapshot.txt",
        description="Path to output file"
    )
    include_extensions: List[str] = Field(
        default=[".swift", ".py", ".js"],
        description="File extensions to include"
    )
    exclude_dirs: List[str] = Field(
        default=["node_modules", ".git", "build"],
        description="Directories to exclude"
    )
    exclude_files: List[str] = Field(
        default=[],
        description="Specific files to exclude"
    )

    def get_output_path(self, base_dir: Optional[Path] = None) -> Path:
        """Get absolute output path, optionally relative to base_dir."""
        path = Path(self.output_file)
        if base_dir and not path.is_absolute():
            path = base_dir / path
        return path.resolve()

    class Config:
        json_schema_extra = {
            "example": {
                "directories": ["src", "lib"],
                "output_file": "snapshot.md",
                "include_extensions": [".py", ".js", ".ts"],
                "exclude_dirs": ["node_modules", ".git"],
                "exclude_files": ["secrets.env"]
            }
        } 

# ======= File: src/llm_auto_context/snapshot.py =======

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
    rel_path = file_path.relative_to(base_dir)
    if str(rel_path) in config.exclude_files:
        return False

    # Check if file is in excluded directory
    for exclude_dir in config.exclude_dirs:
        if exclude_dir in str(rel_path).split(os.sep):
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