#!/usr/bin/env python3
"""
Analytics Management Script
Manages analytics data and generates reports for StreamWorks-KI
"""
import os
import sys
import logging
import asyncio
import csv
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.settings import settings
from app.models.database import DatabaseManager
from app.services.analytics_service import AnalyticsService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AnalyticsManager:
    """Analytics data management and reporting"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.analytics_service = AnalyticsService()
    
    async def generate_usage_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate usage report for the last N days"""
        try:
            logger.info(f"📊 Generating usage report for last {days} days...")
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            async with self.db_manager.get_session() as session:
                # Query system metrics
                query = """
                    SELECT 
                        DATE(created_at) as date,
                        metric_name,
                        COUNT(*) as count,
                        AVG(value) as avg_value,
                        MAX(value) as max_value
                    FROM system_metrics 
                    WHERE created_at >= ? AND created_at <= ?
                    GROUP BY DATE(created_at), metric_name
                    ORDER BY date DESC, metric_name
                """
                
                result = await session.execute(query, (start_date, end_date))
                metrics = result.fetchall()
                
                report = {
                    "period": f"{start_date.date()} to {end_date.date()}",
                    "total_metrics": len(metrics),
                    "metrics_by_date": {}
                }
                
                for metric in metrics:
                    date = metric[0]
                    if date not in report["metrics_by_date"]:
                        report["metrics_by_date"][date] = {}
                    
                    report["metrics_by_date"][date][metric[1]] = {
                        "count": metric[2],
                        "avg_value": metric[3],
                        "max_value": metric[4]
                    }
                
                logger.info(f"✅ Generated report with {len(metrics)} metric entries")
                return report
                
        except Exception as e:
            logger.error(f"❌ Failed to generate usage report: {e}")
            raise
    
    async def export_analytics_csv(self, output_path: str, days: int = 30) -> bool:
        """Export analytics data to CSV for scientific analysis"""
        try:
            logger.info(f"📤 Exporting analytics to CSV: {output_path}")
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            async with self.db_manager.get_session() as session:
                query = """
                    SELECT 
                        id,
                        metric_name,
                        value,
                        metadata,
                        created_at
                    FROM system_metrics 
                    WHERE created_at >= ? AND created_at <= ?
                    ORDER BY created_at DESC
                """
                
                result = await session.execute(query, (start_date, end_date))
                metrics = result.fetchall()
                
                # Write to CSV
                with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Header
                    writer.writerow(['id', 'metric_name', 'value', 'metadata', 'created_at'])
                    
                    # Data
                    for metric in metrics:
                        writer.writerow(metric)
                
                logger.info(f"✅ Exported {len(metrics)} metrics to {output_path}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to export analytics CSV: {e}")
            return False
    
    async def cleanup_old_metrics(self, days: int = 90) -> int:
        """Clean up metrics older than specified days"""
        try:
            logger.info(f"🧹 Cleaning up metrics older than {days} days...")
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            async with self.db_manager.get_session() as session:
                result = await session.execute(
                    "DELETE FROM system_metrics WHERE created_at < ?",
                    (cutoff_date,)
                )
                
                deleted_count = result.rowcount
                await session.commit()
                
                logger.info(f"✅ Cleaned up {deleted_count} old metric records")
                return deleted_count
                
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old metrics: {e}")
            raise
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get current system health metrics"""
        try:
            logger.info("🔍 Checking system health...")
            
            async with self.db_manager.get_session() as session:
                # Check recent metrics
                recent_query = """
                    SELECT 
                        metric_name,
                        COUNT(*) as count,
                        AVG(value) as avg_value,
                        MAX(created_at) as last_update
                    FROM system_metrics 
                    WHERE created_at >= datetime('now', '-1 hour')
                    GROUP BY metric_name
                """
                
                result = await session.execute(recent_query)
                recent_metrics = dict(result.fetchall())
                
                # Check total metrics
                total_result = await session.execute("SELECT COUNT(*) FROM system_metrics")
                total_metrics = total_result.fetchone()[0]
                
                health = {
                    "status": "healthy" if recent_metrics else "warning",
                    "total_metrics": total_metrics,
                    "recent_activity": recent_metrics,
                    "checked_at": datetime.now().isoformat()
                }
                
                logger.info(f"✅ System health check completed")
                return health
                
        except Exception as e:
            logger.error(f"❌ Failed to check system health: {e}")
            raise


async def main():
    """Main analytics management interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analytics Management for StreamWorks-KI')
    parser.add_argument('action', choices=['report', 'export', 'cleanup', 'health'], 
                       help='Action to perform')
    parser.add_argument('--days', type=int, default=30, 
                       help='Number of days for report/export/cleanup')
    parser.add_argument('--output', type=str, 
                       help='Output file path for export')
    
    args = parser.parse_args()
    
    manager = AnalyticsManager()
    
    try:
        if args.action == 'report':
            report = await manager.generate_usage_report(args.days)
            print(f"\n📊 Usage Report ({report['period']}):")
            print(f"Total metrics: {report['total_metrics']}")
            
            for date, metrics in report['metrics_by_date'].items():
                print(f"\n{date}:")
                for metric_name, data in metrics.items():
                    print(f"  {metric_name}: {data['count']} entries, avg: {data['avg_value']:.2f}")
        
        elif args.action == 'export':
            if not args.output:
                args.output = f"analytics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            success = await manager.export_analytics_csv(args.output, args.days)
            if success:
                print(f"✅ Analytics exported to: {args.output}")
            else:
                print("❌ Export failed")
                sys.exit(1)
        
        elif args.action == 'cleanup':
            deleted = await manager.cleanup_old_metrics(args.days)
            print(f"✅ Cleaned up {deleted} old metric records")
        
        elif args.action == 'health':
            health = await manager.get_system_health()
            print(f"\n🔍 System Health Status: {health['status']}")
            print(f"Total metrics: {health['total_metrics']}")
            print(f"Recent activity: {len(health['recent_activity'])} metric types")
            print(f"Checked at: {health['checked_at']}")
        
    except Exception as e:
        logger.error(f"❌ Operation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())