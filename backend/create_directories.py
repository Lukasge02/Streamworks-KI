#!/usr/bin/env python3
"""
Script to create necessary directories for StreamWorks-KI
"""
import os

def create_directories():
    """Create training data directories"""
    directories = [
        "data",
        "data/training_data", 
        "data/training_data/help_data",
        "data/training_data/stream_templates"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    print("✅ All directories created successfully!")

if __name__ == "__main__":
    create_directories()