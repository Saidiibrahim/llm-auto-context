"""Tests for the config module."""

import json
from pathlib import Path

import pytest
from llm_auto_context.config import SnapshotConfig

def test_default_config():
    """Test default configuration values."""
    config = SnapshotConfig()
    assert config.directories == ["src"]
    assert config.output_file == "code_snapshot.txt"
    assert set(config.include_extensions) == {".swift", ".py", ".js"}
    assert set(config.exclude_dirs) == {"node_modules", ".git", "build"}
    assert config.exclude_files == []

def test_custom_config():
    """Test custom configuration values."""
    config = SnapshotConfig(
        directories=["test_dir"],
        output_file="output.md",
        include_extensions=[".py"],
        exclude_dirs=["venv"],
        exclude_files=["secrets.py"]
    )
    assert config.directories == ["test_dir"]
    assert config.output_file == "output.md"
    assert config.include_extensions == [".py"]
    assert config.exclude_dirs == ["venv"]
    assert config.exclude_files == ["secrets.py"]

def test_get_output_path(tmp_path):
    """Test output path resolution."""
    config = SnapshotConfig(output_file="output.md")
    
    # Test relative path
    base_dir = tmp_path / "project"
    base_dir.mkdir()
    output_path = config.get_output_path(base_dir)
    assert output_path == (base_dir / "output.md").resolve()
    
    # Test absolute path
    abs_path = tmp_path / "absolute" / "output.md"
    config.output_file = str(abs_path)
    output_path = config.get_output_path(base_dir)
    assert output_path == abs_path.resolve()

def test_config_validation():
    """Test configuration validation."""
    with pytest.raises(ValueError):
        SnapshotConfig(directories=["nonexistent"], output_file="") 