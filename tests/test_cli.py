"""Tests for the CLI module."""

import json
from pathlib import Path
from typing import List

import pytest
from typer.testing import CliRunner
from llm_auto_context.cli import app

runner = CliRunner()

@pytest.fixture
def config_file(tmp_path):
    """Create a sample config file."""
    config = {
        "directories": ["src"],
        "output_file": "snapshot.md",
        "include_extensions": [".py"],
        "exclude_dirs": ["__pycache__"],
        "exclude_files": []
    }
    config_path = tmp_path / ".codesnapshot.json"
    config_path.write_text(json.dumps(config))
    return config_path

@pytest.fixture
def test_files(tmp_path):
    """Create test files and directories."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    
    # Create test files
    (src_dir / "test.py").write_text("print('test')")
    return tmp_path

def test_cli_help():
    """Test CLI help output."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Generate code snapshots with configurable settings" in result.stdout

def test_cli_with_config(config_file, test_files):
    """Test CLI with config file."""
    with runner.isolated_filesystem():
        # Copy config and test files to isolated filesystem
        Path(".codesnapshot.json").write_text(config_file.read_text())
        src_dir = Path("src")
        src_dir.mkdir()
        (src_dir / "test.py").write_text("print('test')")
        
        result = runner.invoke(app)
        assert result.exit_code == 0
        assert "Created snapshot at:" in result.stdout
        assert Path("snapshot.md").exists()

def test_cli_with_overrides(config_file, test_files):
    """Test CLI with command line overrides."""
    with runner.isolated_filesystem():
        # Setup test environment
        Path(".codesnapshot.json").write_text(config_file.read_text())
        src_dir = Path("src")
        src_dir.mkdir()
        (src_dir / "test.py").write_text("print('test')")
        
        # Test with overrides
        result = runner.invoke(app, [
            "-d", "src",
            "-o", "custom.md",
            "--include", ".py",
            "--exclude-dir", "__pycache__"
        ])
        assert result.exit_code == 0
        assert "Created snapshot at:" in result.stdout
        assert Path("custom.md").exists()

def test_cli_missing_config():
    """Test CLI behavior with missing config file."""
    with runner.isolated_filesystem():
        result = runner.invoke(app)
        assert result.exit_code == 1
        assert "Error:" in result.stdout

def test_cli_invalid_directory():
    """Test CLI behavior with invalid directory."""
    with runner.isolated_filesystem():
        result = runner.invoke(app, ["-d", "nonexistent"])
        assert result.exit_code == 1
        assert "Error:" in result.stdout 