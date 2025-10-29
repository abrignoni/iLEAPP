#!/usr/bin/env python3
"""
Memory Optimization Verification Script

This script helps verify that memory optimizations are working correctly.
It monitors memory usage during artifact processing and compares with baseline.

Usage:
    python tests/test_memory_optimization.py --artifact photosMetadata --data-path /path/to/extraction
    python tests/test_memory_optimization.py --artifact BeReal --data-path /path/to/extraction
"""

import sys
import os
import psutil
import tracemalloc
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import memory_profiler
    HAS_MEMORY_PROFILER = True
except ImportError:
    HAS_MEMORY_PROFILER = False
    print("Certificate: Install memory_profiler for detailed profiling: pip install memory-profiler")


def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # Convert to MB


def test_photos_metadata_memory(data_path, report_folder):
    """Test photosMetadata artifact memory usage"""
    print("\n" + "="*60)
    print("Testing photosMetadata Memory Optimization")
    print("="*60)
    
    from scripts.ilapfuncs import open_sqlite_db_readonly
    from scripts.artifacts.photosMetadata import get_photosMetadata
    
    # Find Photos.sqlite file
    photos_db = None
    for root, dirs, files in os.walk(data_path):
        for file in files:
            if file == 'Photos.sqlite':
                photos_db = os.path.join(root, file)
                break
        if photos_db:
            break
    
    if not photos_db:
        print(f"ERROR: Photos.sqlite not found in {data_path}")
        return False
    
    print(f"Found Photos.sqlite: {photos_db}")
    
    # Start memory tracking
    tracemalloc.start()
    initial_memory = get_memory_usage()
    print(f"\nInitial Memory: {initial_memory:.2f} MB")
    
    # Count rows in database first
    try:
        db = open_sqlite_db_readonly(photos_db)
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM ZGENERICASSET")
        row_count = cursor.fetchone()[0]
        db.close()
        print(f"Total rows in database: {row_count:,}")
    except Exception as e:
        print(f"Warning: Could not count rows: {e}")
        row_count = 0
    
    # Test the optimized function
    try:
        start_time = time.time()
        seeker = None  # You may need to implement a mock seeker
        
        # Simulate file discovery
        files_found = [photos_db]
        
        get_photosMetadata(files_found, report_folder, seeker, False, 0)
        
        processing_time = time.time() - start_time
        peak_memory = get_memory_usage()
        
        # Get tracemalloc stats
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"\nResults:")
        print(f"  Processing Time: {processing_time:.2f} seconds")
        print(f"  Peak Memory (psutil): {peak_memory:.2f} MB")
        print(f"  Peak Memory (tracemalloc): {peak / 1024 / 1024:.2f} MB")
        print(f"  Memory Increase: {peak_memory - initial_memory:.2f} MB")
        
        if row_count > 0:
            memory_per_row = (peak_memory - initial_memory) / row_count
            print(f"  Memory per row: {memory_per_row * 1024:.2f} KB")
        
        # Success criteria: Memory should not exceed reasonable limits
        # For 10,000 rows, should use < 500MB
        expected_max_memory = min(500, 50 + (row_count * 0.05))  # 50MB base + 50KB per row
        if peak_memory < expected_max_memory:
            print(f"\n✓ PASS: Memory usage ({peak_memory:.2f} MB) is below expected maximum ({expected_max_memory:.2f} MB)")
            return True
        else:
            print(f"\n✗ FAIL: Memory usage ({peak_memory:.2f} MB) exceeds expected maximum ({expected_max_memory:.2f} MB)")
            return False
            
    except Exception as e:
        tracemalloc.stop()
        print(f"\nERROR during processing: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bereal_memory(data_path, report_folder):
    """Test BeReal artifacts memory usage"""
    print("\n" + "="*60)
    print("Testing BeReal Memory Optimization")
    print("="*60)
    
    from scripts.ilapfuncs import get_file_path
    from scripts.artifacts.BeReal import bereal_messages, bereal_chat_list
    
    # Find bereal-chat.sqlite
    import glob
    bereal_db_pattern = os.path.join(data_path, '**/bereal-chat.sqlite*')
    bereal_dbs = glob.glob(bereal_db_pattern, recursive=True)
    
    if not bereal_dbs:
        print(f"WARNING: bereal-chat.sqlite not found in {data_path}")
        return None
    
    print(f"Found {len(bereal_dbs)} BeReal database(s)")
    
    for db_path in bereal_dbs:
        print(f"\nTesting: {db_path}")
        
        # Start memory tracking
        tracemalloc.start()
        initial_memory = get_memory_usage()
        print(f"Initial Memory: {initial_memory:.2f} MB")
        
        # Count rows
        try:
            import sqlite3
            db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            cursor = db.cursor()
            cursor.execute("SELECT COUNT(*) FROM ZMESSAGEMO")
            msg_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM ZCONVERSATIONMO")
            conv_count = cursor.fetchone()[0]
            db.close()
            print(f"Messages: {msg_count:,}, Conversations: {conv_count:,}")
        except Exception as e:
            print(f"Warning: Could not count rows: {e}")
            msg_count = conv_count = 0
        
        # Test functions
        try:
            start_time = time.time()
            files_found = [db_path]
            
            # Test messages
            bereal_messages(files_found, report_folder, None, False, 0)
            messages_memory = get_memory_usage()
            
            # Test chat list
            bereal_chat_list(files_found, report_folder, None, False, 0)
            
            processing_time = time.time() - start_time
            peak_memory = get_memory_usage()
            
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            print(f"\nResults:")
            print(f"  Processing Time: {processing_time:.2f} seconds")
            print(f"  Peak Memory: {peak_memory:.2f} MB")
            print(f"  Memory Increase: {peak_memory - initial_memory:.2f} MB")
            
            # Success criteria
            expected_max = min(200, 30 + (msg_count * 0.01))  # 30MB base + 10KB per message
            if peak_memory < expected_max:
                print(f"✓ PASS: Memory usage is acceptable")
                return True
            else:
                print(f"✗ FAIL: Memory usage exceeds expected")
                return False
                
        except Exception as e:
            tracemalloc.stop()
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True


def verify_code_changes():
    """Verify that code changes are in place"""
    print("\n" + "="*60)
    print("Verifying Code Changes")
    print("="*60)
    
    checks = {
        "photosMetadata.py uses cursor iteration": False,
        "BeReal.py uses cursor iteration": False,
        "ilapfuncs.py has helper functions": False,
    }
    
    # Check photosMetadata.py
    try:
        with open('scripts/artifacts/photosMetadata.py', 'r') as f:
            content = f.read()
            if 'for row in cursor:' in content and 'fetchall()' not in content.split('for row in cursor:')[1].split('#')[0]:
                checks["photosMetadata.py uses cursor iteration"] = True
    except:
        pass
    
    # Check BeReal.py
    try:
        with open('scripts/artifacts/BeReal.py', 'r') as f:
            content = f.read()
            if 'for record in cursor:' in content and 'open_sqlite_db_readonly' in content:
                checks["BeReal.py uses cursor iteration"] = True
    except:
        pass
    
    # Check ilapfuncs.py
    try:
        with open('scripts/ilapfuncs.py', 'r') as f:
            content = f.read()
            if 'get_sqlite_db_cursor_iter' in content:
                checks["ilapfuncs.py has helper functions"] = True
    except:
        pass
    
    all_passed = True
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
        if not passed:
            all_passed = False
    
    return all_passed


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Test memory optimizations')
    parser.add_argument('--artifact', choices=['photosMetadata', 'BeReal', 'all', 'verify'],
                       default='verify', help='Artifact to test')
    parser.add_argument('--data-path', help='Path to iOS extraction data')
    parser.add_argument('--report-folder', default='/tmp/ileapp_test_report',
                       help='Temporary report folder')
    
    args = parser.parse_args()
    
    # Always verify code changes first
    if not verify_code_changes():
        print("\n⚠ WARNING: Some code changes not detected. Memory optimizations may not be active.")
    else:
        print("\n✓ All code changes verified!")
    
    if args.artifact == 'verify':
        print("\nTo test with actual data, run:")
        print("  python tests/test_memory_optimization.py --artifact photosMetadata --data-path /path/to/extraction")
        return
    
    if not args.data_path:
        print("ERROR: --data-path required for artifact testing")
        return
    
    # Create report folder
    os.makedirs(args.report_folder, exist_ok=True)
    
    results = []
    
    if args.artifact in ['photosMetadata', 'all']:
        results.append(test_photos_metadata_memory(args.data_path, args.report_folder))
    
    if args.artifact in ['BeReal', 'all']:
        results.append(test_bereal_memory(args.data_path, args.report_folder))
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    if all(results):
        print("✓ All tests PASSED")
    else:
        print("✗ Some tests FAILED")
    
    print(f"\nTip: Monitor memory in real-time with:")
    print(f"  watch -n 1 'ps aux | grep python | grep ileapp'")


if __name__ == '__main__':
    main()
