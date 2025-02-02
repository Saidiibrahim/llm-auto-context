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