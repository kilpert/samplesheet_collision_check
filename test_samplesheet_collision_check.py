import pandas as pd
import pytest
from samplesheet_collision_check import detect_collision

def test_no_collision():
    """Tests an input without collisions (unique indices per lane)."""
    df = pd.DataFrame({
        'Lane': ['1', '1', '2'],
        'Sample_ID': ['S1', 'S2', 'S3'],
        'Index': ['AAAA', 'TTTT', 'AAAA'],
        'Index2': ['CCCC', 'GGGG', 'CCCC']
    })
    
    result = detect_collision(df)
    assert result.empty, "No collisions should be detected."

def test_with_collision():
    """Tests an input with collisions (same indices for different samples on the same lane)."""
    df = pd.DataFrame({
        'Lane': ['1', '1', '1'],
        'Sample_ID': ['S1', 'S2', 'S3'],  # S1 and S2 have identical indices on Lane 1
        'Index': ['AAAA', 'AAAA', 'TTTT'],
        'Index2': ['CCCC', 'CCCC', 'GGGG']
    })
    
    result = detect_collision(df)
    
    assert len(result) == 2, "Exactly 2 colliding entries should be found."
    assert set(result['Sample_ID']) == {'S1', 'S2'}, "The colliding Sample_IDs should be S1 and S2."
    assert 'S3' not in result['Sample_ID'].values, "S3 should not be marked as a collision."
