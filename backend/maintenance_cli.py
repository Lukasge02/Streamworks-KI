#!/usr/bin/env python3
"""
StreamWorks Maintenance CLI Tool
Command-line interface for system maintenance and cleanup operations
"""

import asyncio
import logging
import sys
import json
from datetime import datetime
from typing import Optional

import click
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import settings
from services.maintenance_service import MaintenanceService
from services.di_container import initialize_container

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def get_db_session() -> AsyncSession:
    """Create database session"""
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return async_session()


@click.group()
def cli():
    """StreamWorks Maintenance CLI"""
    pass


@cli.command()
@click.option('--fix', is_flag=True, help='Actually fix issues (default: dry run)')
@click.option('--output', type=click.File('w'), help='Save report to file')
def check_vectors(fix: bool, output: Optional[click.File]):
    """Check vector store consistency"""
    
    async def _check_vectors():
        try:
            # Initialize services
            await initialize_container()
            db = await get_db_session()
            
            maintenance = MaintenanceService()
            
            click.echo(f"🔍 Checking vector consistency {'with fixes' if fix else '(dry run)'}...")
            
            report = await maintenance.check_vector_consistency(db, fix_issues=fix)
            
            # Display summary
            stats = report["stats"]
            click.echo("\n📊 Vector Consistency Report:")
            click.echo(f"   Database Documents: {stats['database_documents']}")
            click.echo(f"   Database Chunks: {stats['database_chunks']}")
            click.echo(f"   Vector Documents: {stats['vector_documents']}")
            click.echo(f"   Vector Chunks: {stats['vector_chunks']}")
            
            if stats['consistency_issues']:
                click.echo(f"\n⚠️  Issues Found:")
                click.echo(f"   Orphaned Vector Documents: {stats['orphaned_vector_documents']}")
                click.echo(f"   Orphaned Vector Chunks: {stats['orphaned_vector_chunks']}")
                click.echo(f"   Orphaned Doc References: {stats['orphaned_document_references']}")
                
                if fix and report.get('fixes_applied'):
                    fixes = report['fixes_applied']
                    click.echo(f"\n✅ Fixes Applied:")
                    click.echo(f"   Deleted Orphaned Documents: {fixes['deleted_orphaned_documents']}")
                    click.echo(f"   Deleted Orphaned Chunks: {fixes['deleted_orphaned_chunks']}")
                    
                    if fixes['errors']:
                        click.echo(f"\n❌ Errors during cleanup:")
                        for error in fixes['errors']:
                            click.echo(f"   - {error}")
                elif not fix:
                    click.echo(f"\n💡 Run with --fix to clean up these issues")
            else:
                click.echo("\n✅ No consistency issues found!")
            
            # Save report if requested
            if output:
                json.dump(report, output, indent=2, default=str)
                click.echo(f"\n📄 Full report saved to {output.name}")
            
            await db.close()
            
        except Exception as e:
            click.echo(f"❌ Error: {str(e)}", err=True)
            sys.exit(1)
    
    asyncio.run(_check_vectors())


@cli.command()
@click.option('--fix', is_flag=True, help='Actually fix issues (default: dry run)')
@click.option('--output', type=click.File('w'), help='Save report to file')
def check_chunks(fix: bool, output: Optional[click.File]):
    """Check database chunk consistency"""
    
    async def _check_chunks():
        try:
            await initialize_container()
            db = await get_db_session()
            
            maintenance = MaintenanceService()
            
            click.echo(f"🔍 Checking database chunks {'with fixes' if fix else '(dry run)'}...")
            
            report = await maintenance.cleanup_orphaned_database_chunks(db, dry_run=not fix)
            
            # Display results
            if report.get('dry_run', True):
                orphaned = report.get('orphaned_chunks_found', 0)
                if orphaned > 0:
                    click.echo(f"\n⚠️  Found {orphaned} orphaned database chunks")
                    click.echo(f"   Total size: {report.get('total_size_bytes', 0)} bytes")
                    click.echo(f"\n💡 Run with --fix to clean up these chunks")
                else:
                    click.echo("\n✅ No orphaned database chunks found!")
            else:
                cleaned = report.get('cleaned_chunks', 0)
                click.echo(f"\n✅ Cleaned up {cleaned} orphaned database chunks")
            
            # Save report if requested
            if output:
                json.dump(report, output, indent=2, default=str)
                click.echo(f"\n📄 Report saved to {output.name}")
            
            await db.close()
            
        except Exception as e:
            click.echo(f"❌ Error: {str(e)}", err=True)
            sys.exit(1)
    
    asyncio.run(_check_chunks())


@cli.command()
@click.option('--output', type=click.File('w'), help='Save report to file')
def health_report(output: Optional[click.File]):
    """Generate comprehensive system health report"""
    
    async def _health_report():
        try:
            await initialize_container()
            db = await get_db_session()
            
            maintenance = MaintenanceService()
            
            click.echo("🏥 Generating system health report...")
            
            report = await maintenance.get_system_health_report(db)
            
            # Display summary
            click.echo(f"\n📊 System Health Report ({report['timestamp']}):")
            click.echo(f"   Status: {report['health_status'].upper()}")
            
            db_stats = report['database']
            click.echo(f"\n💾 Database:")
            click.echo(f"   Documents: {db_stats['documents']}")
            click.echo(f"   Chunks: {db_stats['chunks']}")
            
            vector_stats = report['vector_store']
            click.echo(f"\n🔍 Vector Store:")
            click.echo(f"   Total Chunks: {vector_stats['total_chunks']}")
            click.echo(f"   Total Documents: {vector_stats['total_documents']}")
            click.echo(f"   Collection: {vector_stats['collection_name']}")
            
            consistency = report['consistency']
            if consistency['consistency_issues']:
                click.echo(f"\n⚠️  Consistency Issues:")
                click.echo(f"   Orphaned Vector Chunks: {consistency['orphaned_vector_chunks']}")
                click.echo(f"   Orphaned Vector Documents: {consistency['orphaned_vector_documents']}")
            else:
                click.echo(f"\n✅ Consistency: All good!")
            
            if report['recommendations']:
                click.echo(f"\n💡 Recommendations:")
                for rec in report['recommendations']:
                    click.echo(f"   - {rec}")
            
            # Save full report if requested
            if output:
                json.dump(report, output, indent=2, default=str)
                click.echo(f"\n📄 Full report saved to {output.name}")
            
            await db.close()
            
        except Exception as e:
            click.echo(f"❌ Error: {str(e)}", err=True)
            sys.exit(1)
    
    asyncio.run(_health_report())


@cli.command()
@click.option('--fix', is_flag=True, help='Actually fix issues (default: dry run)')
@click.option('--output', type=click.File('w'), help='Save report to file')
def full_cleanup(fix: bool, output: Optional[click.File]):
    """Perform comprehensive system cleanup"""
    
    async def _full_cleanup():
        try:
            await initialize_container()
            db = await get_db_session()
            
            maintenance = MaintenanceService()
            
            click.echo(f"🧹 Starting full system cleanup {'with fixes' if fix else '(dry run)'}...")
            
            report = await maintenance.full_system_cleanup(db, dry_run=not fix)
            
            # Display summary
            summary = report['summary']
            click.echo(f"\n📊 Cleanup Summary:")
            click.echo(f"   Total Issues Found: {summary['total_issues_found']}")
            
            if fix:
                click.echo(f"   Issues Fixed: {summary['issues_fixed']}")
                click.echo(f"\n✅ Cleanup completed!")
            else:
                click.echo(f"   💡 Run with --fix to resolve these issues")
            
            # Show detailed results
            db_cleanup = report.get('database_cleanup', {})
            if db_cleanup.get('orphaned_chunks_found', 0) > 0:
                click.echo(f"\n💾 Database Chunks:")
                if fix:
                    click.echo(f"   Cleaned: {db_cleanup.get('cleaned_chunks', 0)}")
                else:
                    click.echo(f"   Orphaned Found: {db_cleanup['orphaned_chunks_found']}")
            
            vector_cleanup = report.get('vector_cleanup', {})
            vector_stats = vector_cleanup.get('stats', {})
            if vector_stats.get('consistency_issues'):
                click.echo(f"\n🔍 Vector Store:")
                click.echo(f"   Orphaned Documents: {vector_stats.get('orphaned_vector_documents', 0)}")
                click.echo(f"   Orphaned Chunks: {vector_stats.get('orphaned_vector_chunks', 0)}")
                
                if fix:
                    fixes = vector_cleanup.get('fixes_applied', {})
                    click.echo(f"   Fixed Documents: {fixes.get('deleted_orphaned_documents', 0)}")
                    click.echo(f"   Fixed Chunks: {fixes.get('deleted_orphaned_chunks', 0)}")
            
            # Save report if requested
            if output:
                json.dump(report, output, indent=2, default=str)
                click.echo(f"\n📄 Full report saved to {output.name}")
            
            await db.close()
            
        except Exception as e:
            click.echo(f"❌ Error: {str(e)}", err=True)
            sys.exit(1)
    
    asyncio.run(_full_cleanup())


if __name__ == '__main__':
    cli()