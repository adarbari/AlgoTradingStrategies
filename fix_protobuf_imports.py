#!/usr/bin/env python3
"""
Script to fix protobuf imports for compatibility with protobuf 3.20.0
"""

import os
import re

def fix_protobuf_file(file_path):
    """Fix a single protobuf file by removing runtime_version imports."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Remove the runtime_version import
    content = re.sub(
        r'from google\.protobuf import runtime_version as _runtime_version\n',
        '# from google.protobuf import runtime_version as _runtime_version  # Removed for compatibility\n',
        content
    )
    
    # Remove the runtime_version validation
    content = re.sub(
        r'_runtime_version\.ValidateProtobufRuntimeVersion\(\s*_runtime_version\.Domain\.PUBLIC,\s*\d+,\s*\d+,\s*\d+,\s*[\'"]*[\'"],\s*[\'"].*[\'"]\s*\)',
        '# _runtime_version.ValidateProtobufRuntimeVersion(...)  # Removed for compatibility',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Write the fixed content back
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed: {file_path}")

def main():
    """Fix all protobuf files in the rithmic proto directory."""
    proto_dir = "src/data/providers/vendors/rithmic/proto"
    
    if not os.path.exists(proto_dir):
        print(f"Directory not found: {proto_dir}")
        return
    
    # Get all .py files in the proto directory
    for filename in os.listdir(proto_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            file_path = os.path.join(proto_dir, filename)
            try:
                fix_protobuf_file(file_path)
            except Exception as e:
                print(f"Error fixing {file_path}: {e}")
    
    print("Protobuf import fixes completed!")

if __name__ == "__main__":
    main() 