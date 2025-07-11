import os
import pickle
from typing import Dict, List
from datetime import datetime
from dataclasses import dataclass


@dataclass
class FeatureFileMetadata:
    """Metadata for a feature file."""
    symbol: str
    start_timestamp: datetime
    end_timestamp: datetime
    file_path: str  # Now stores only the filename, not the full path
    feature_count: int
    created_at: datetime


class FeatureStoreMetadata:
    """Manages metadata for feature files."""
    
    def __init__(self, metadata_file: str = "feature_cache/metadata.pkl"):
        self.metadata_file = metadata_file
        self._metadata: Dict[str, List[FeatureFileMetadata]] = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, List[FeatureFileMetadata]]:
        """Load metadata from disk."""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Error loading metadata: {e}")
        return {}
    
    def _save_metadata(self):
        """Save metadata to disk."""
        os.makedirs(os.path.dirname(self.metadata_file), exist_ok=True)
        with open(self.metadata_file, 'wb') as f:
            pickle.dump(self._metadata, f)
    
    def add_file_metadata(self, symbol: str, metadata: FeatureFileMetadata):
        """Add metadata for a feature file."""
        if symbol not in self._metadata:
            self._metadata[symbol] = []
        self._metadata[symbol].append(metadata)
        self._save_metadata()
    
    def get_file_metadata(self, symbol: str) -> List[FeatureFileMetadata]:
        """Get metadata for all files of a symbol."""
        return self._metadata.get(symbol, [])
    
    def remove_file_metadata(self, symbol: str, file_path: str):
        """Remove metadata for a specific file.
        
        Args:
            symbol: Trading symbol
            file_path: Filename (not full path) to remove from metadata
        """
        if symbol in self._metadata:
            self._metadata[symbol] = [
                meta for meta in self._metadata[symbol] 
                if meta.file_path != file_path
            ]
            self._save_metadata()
    
    def clear_symbol_metadata(self, symbol: str):
        """Clear all metadata for a symbol."""
        if symbol in self._metadata:
            del self._metadata[symbol]
            self._save_metadata()
    
    def migrate_to_relative_paths(self):
        """Migrate existing metadata from absolute paths to relative filenames.
        
        This method converts any existing metadata that stores full file paths
        to store only filenames, making the metadata portable.
        """
        migrated = False
        for symbol in list(self._metadata.keys()):
            for metadata in self._metadata[symbol]:
                if os.path.isabs(metadata.file_path):
                    # Convert absolute path to filename only
                    old_path = metadata.file_path
                    metadata.file_path = os.path.basename(old_path)
                    print(f"Migrated metadata for {symbol}: {old_path} -> {metadata.file_path}")
                    migrated = True
        
        if migrated:
            self._save_metadata()
            print("Metadata migration completed.")
        else:
            print("No metadata migration needed.") 