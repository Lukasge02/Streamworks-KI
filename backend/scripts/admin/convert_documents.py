#!/usr/bin/env python3
"""
Document Conversion CLI Tool - PostgreSQL-optimiert
"""
import asyncio
import logging
import argparse
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.document_service import document_service
from app.utils.batch_converter import batch_converter, PostgreSQLBatchConverter

# Setup detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def convert_single_file(file_path: str):
    """Convert a single file with detailed progress logging"""
    
    logger.info(f"🔄 Converting single file: {file_path}")
    
    file_obj = Path(file_path)
    if not file_obj.exists():
        logger.error(f"❌ File not found: {file_path}")
        return False
    
    # Validate file type
    allowed_extensions = {'.pdf', '.txt', '.md'}
    if file_obj.suffix.lower() not in allowed_extensions:
        logger.error(f"❌ Unsupported file type: {file_obj.suffix}")
        logger.info(f"📋 Supported formats: {', '.join(allowed_extensions)}")
        return False
    
    try:
        # Read file with progress indication
        logger.info(f"📖 Reading file: {file_obj.name}")
        with open(file_obj, 'rb') as f:
            content = f.read()
        
        file_size_mb = len(content) / 1024 / 1024
        logger.info(f"📏 File size: {file_size_mb:.2f} MB")
        
        if file_size_mb > 50:
            logger.error(f"❌ File too large: {file_size_mb:.2f} MB (max 50 MB)")
            return False
        
        # Convert with progress tracking
        logger.info(f"⚙️ Starting conversion...")
        result = await document_service.convert_and_save(file_path, content)
        
        if result.success:
            logger.info(f"✅ Conversion successful!")
            logger.info(f"   📄 Document ID: {result.document_id}")
            logger.info(f"   📁 Output path: {result.output_path}")
            logger.info(f"   ⏱️ Processing time: {result.processing_time:.2f}s")
            logger.info(f"   📖 Pages processed: {result.pages_processed}")
            logger.info(f"   📏 Output size: {result.file_size} characters")
            return True
        else:
            logger.error(f"❌ Conversion failed: {result.error_message}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during conversion: {e}")
        return False

async def convert_batch(source_dir: str, overwrite: bool = False):
    """Convert all files in a directory with progress tracking"""
    
    logger.info(f"🚀 Starting batch conversion")
    logger.info(f"📂 Source directory: {source_dir}")
    logger.info(f"🔄 Overwrite mode: {overwrite}")
    
    try:
        # Create converter instance
        if source_dir:
            converter = PostgreSQLBatchConverter(source_dir)
        else:
            converter = batch_converter
            
        logger.info(f"🔍 Scanning for PDF and TXT files...")
        
        # Execute batch conversion with detailed progress
        result = await converter.convert_all_documents(overwrite=overwrite)
        
        if "error" in result:
            logger.error(f"❌ Batch conversion failed: {result['error']}")
            return False
        else:
            # Display comprehensive results
            logger.info(f"🎉 Batch conversion completed!")
            logger.info(f"")
            logger.info(f"📊 FINAL STATISTICS:")
            logger.info(f"   📄 Total files found: {result.get('stats', {}).get('total_found', 0)}")
            logger.info(f"   ✅ Successfully converted: {result.get('stats', {}).get('newly_converted', 0)}")
            logger.info(f"   ⏭️ Already converted: {result.get('stats', {}).get('already_converted', 0)}")
            logger.info(f"   ❌ Failed conversions: {result.get('stats', {}).get('conversion_errors', 0)}")
            logger.info(f"   📈 Success rate: {result.get('success_rate', 0):.1f}%")
            logger.info(f"   ⏱️ Total processing time: {result.get('batch_processing_time', 0):.2f}s")
            logger.info(f"   ⚡ Average per file: {result.get('average_processing_time', 0):.2f}s")
            
            # Show individual results if requested
            if logger.level <= logging.DEBUG:
                logger.debug(f"")
                logger.debug(f"🔍 DETAILED RESULTS:")
                for file_result in result.get('results', []):
                    status = "✅" if file_result.get('success') else "❌"
                    logger.debug(f"   {status} {file_result.get('file', 'Unknown')}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Batch conversion error: {e}")
        return False

async def show_stats():
    """Display comprehensive conversion statistics"""
    
    logger.info(f"📊 DOCUMENT SERVICE STATISTICS")
    logger.info(f"=" * 50)
    
    try:
        # Get service statistics
        stats = document_service.get_stats()
        
        # Basic statistics
        success_rate = (stats.successful_conversions / max(stats.total_files, 1) * 100)
        
        logger.info(f"📄 FILES PROCESSED:")
        logger.info(f"   Total files: {stats.total_files}")
        logger.info(f"   Successful: {stats.successful_conversions}")
        logger.info(f"   Failed: {stats.failed_conversions}")
        logger.info(f"   Success rate: {success_rate:.1f}%")
        logger.info(f"")
        logger.info(f"⏱️ PERFORMANCE METRICS:")
        logger.info(f"   Total processing time: {stats.total_processing_time:.2f}s")
        logger.info(f"   Average per file: {stats.average_processing_time:.2f}s")
        logger.info(f"   Total data processed: {stats.total_size_mb:.2f} MB")
        
        if stats.total_files > 0:
            throughput = stats.total_size_mb / stats.total_processing_time if stats.total_processing_time > 0 else 0
            logger.info(f"   Throughput: {throughput:.2f} MB/s")
        
        logger.info(f"")
        logger.info(f"💾 STORAGE INFORMATION:")
        logger.info(f"   Storage system: unified_storage")
        logger.info(f"   Database: PostgreSQL")
        logger.info(f"   Supported formats: PDF, TXT, MD")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error retrieving statistics: {e}")
        return False

def validate_arguments(args):
    """Validate command line arguments"""
    
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            logger.error(f"❌ File does not exist: {args.file}")
            return False
        if not file_path.is_file():
            logger.error(f"❌ Path is not a file: {args.file}")
            return False
    
    if args.batch:
        batch_path = Path(args.batch)
        if not batch_path.exists():
            logger.error(f"❌ Directory does not exist: {args.batch}")
            return False
        if not batch_path.is_dir():
            logger.error(f"❌ Path is not a directory: {args.batch}")
            return False
    
    return True

def setup_logging(verbose: bool, quiet: bool):
    """Setup logging based on verbosity flags"""
    
    if quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        # Add more detailed formatting for debug mode
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        for handler in logging.getLogger().handlers:
            handler.setFormatter(formatter)
    else:
        logging.getLogger().setLevel(logging.INFO)

def main():
    """Main CLI entry point with comprehensive argument parsing"""
    
    parser = argparse.ArgumentParser(
        description="PostgreSQL Document Conversion Tool for StreamWorks-KI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --file document.pdf              # Convert single PDF file
  %(prog)s --batch ./documents --overwrite  # Batch convert with overwrite
  %(prog)s --stats                          # Show conversion statistics
  %(prog)s --batch ./docs --verbose         # Batch convert with debug output
        """
    )
    
    # Main actions (mutually exclusive)
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        "--file", 
        help="Convert single file (PDF, TXT, or MD)"
    )
    action_group.add_argument(
        "--batch", 
        help="Batch convert directory (searches for PDF and TXT files)"
    )
    action_group.add_argument(
        "--stats", 
        action="store_true", 
        help="Show conversion statistics"
    )
    
    # Options
    parser.add_argument(
        "--overwrite", 
        action="store_true", 
        help="Overwrite existing conversions (default: skip)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true", 
        help="Enable debug output with detailed logging"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true", 
        help="Only show errors (suppresses info and debug)"
    )
    
    args = parser.parse_args()
    
    # Setup logging based on flags
    setup_logging(args.verbose, args.quiet)
    
    logger.info(f"🚀 StreamWorks-KI Document Conversion Tool")
    logger.info(f"⚙️ PostgreSQL-optimized with unified storage")
    logger.info(f"")
    
    # Validate arguments
    if not validate_arguments(args):
        sys.exit(1)
    
    # Execute requested action
    success = False
    
    try:
        if args.stats:
            success = asyncio.run(show_stats())
        elif args.file:
            success = asyncio.run(convert_single_file(args.file))
        elif args.batch:
            success = asyncio.run(convert_batch(args.batch, args.overwrite))
            
    except KeyboardInterrupt:
        logger.info(f"")
        logger.info(f"⏹️ Operation cancelled by user")
        sys.exit(130)  # Standard exit code for Ctrl+C
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            logger.debug(f"Full traceback:")
            logger.debug(traceback.format_exc())
        sys.exit(1)
    
    # Exit with appropriate code
    if success:
        logger.info(f"")
        logger.info(f"🎉 Operation completed successfully!")
        sys.exit(0)
    else:
        logger.error(f"")
        logger.error(f"❌ Operation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()