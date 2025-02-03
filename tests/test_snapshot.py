"""Tests for the snapshot module."""

import os
from pathlib import Path

import pytest
from llm_auto_context.config import SnapshotConfig
from llm_auto_context.snapshot import create_code_snapshot, should_include_file

@pytest.fixture
def sample_config(tmp_path):
    """Create a sample configuration for testing."""
    return SnapshotConfig(
        directories=[str(tmp_path / "src")],
        output_file="snapshot.md",
        include_extensions=[".py"],
        exclude_dirs=["__pycache__"],
        exclude_files=["excluded.py"]
    )

@pytest.fixture
def setup_test_files(tmp_path):
    """Create test files and directories."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    
    # Create test files
    (src_dir / "test1.py").write_text("print('test1')")
    (src_dir / "test2.py").write_text("print('test2')")
    (src_dir / "excluded.py").write_text("print('excluded')")
    (src_dir / "test.txt").write_text("not included")
    
    # Create excluded directory
    pycache_dir = src_dir / "__pycache__"
    pycache_dir.mkdir()
    (pycache_dir / "cache.py").write_text("print('cache')")
    
    return tmp_path

def test_should_include_file(sample_config, setup_test_files):
    """Test file inclusion logic."""
    base_dir = setup_test_files
    src_dir = base_dir / "src"
    
    # Should include regular Python file
    assert should_include_file(src_dir / "test1.py", sample_config, base_dir)
    
    # Should exclude non-Python file
    assert not should_include_file(src_dir / "test.txt", sample_config, base_dir)
    
    # Should exclude file in excluded directory
    assert not should_include_file(src_dir / "__pycache__" / "cache.py", sample_config, base_dir)
    
    # Should exclude specifically excluded file
    assert not should_include_file(src_dir / "excluded.py", sample_config, base_dir)

def test_create_code_snapshot(sample_config, setup_test_files):
    """Test code snapshot creation."""
    base_dir = setup_test_files
    os.chdir(base_dir)  # Change to test directory
    
    output_path = create_code_snapshot(sample_config)
    assert output_path.exists()
    
    content = output_path.read_text()
    
    # Check content includes correct files
    assert "test1.py" in content
    assert "test2.py" in content
    
    # Check content excludes correct files
    assert "excluded.py" not in content
    assert "test.txt" not in content
    assert "cache.py" not in content

def test_create_code_snapshot_nonexistent_dir(sample_config, setup_test_files):
    """Test handling of nonexistent directories."""
    base_dir = setup_test_files
    os.chdir(base_dir)
    
    # Add nonexistent directory to config
    sample_config.directories.append("nonexistent")
    
    # Should still work but log warning
    output_path = create_code_snapshot(sample_config)
    assert output_path.exists()
    
    content = output_path.read_text()
    assert "test1.py" in content  # Should still process existing directories 