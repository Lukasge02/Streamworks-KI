# 🛠️ StreamWorks-KI Scripts Documentation

## Overview

The scripts directory contains organized utilities for development, administration, and deployment of the StreamWorks-KI system. Scripts are categorized into logical groups for better maintainability and clarity.

## Directory Structure

```
backend/scripts/
├── dev/                    # Development Scripts
│   ├── setup_dev_env.py   # Development Environment Setup
│   ├── migrate_to_postgres.py # Database Migration
│   └── update_config_imports.py # Configuration Updates
├── admin/                  # Administration Scripts  
│   ├── convert_documents.py # Document Conversion
│   ├── load_training_data_e5.py # Training Data Loading
│   ├── enrich_training_data_with_citations.py # Citation Enrichment
│   └── manage_analytics.py # Analytics Management
├── deployment/            # Deployment Scripts
│   ├── deploy.sh          # Production Deployment
│   └── health_check.py    # System Health Validation
└── README.md              # This documentation
```

## Script Categories

### 🔧 Development Scripts (`dev/`)

Scripts for setting up and maintaining the development environment.

#### `setup_dev_env.py`
- **Purpose**: Initialize development environment with proper database and directory setup
- **Usage**: `python backend/scripts/dev/setup_dev_env.py`
- **Features**:
  - Database table creation
  - Required directory setup
  - Environment validation
  - Comprehensive error handling with detailed logging

#### `migrate_to_postgres.py`
- **Purpose**: Migrate data from SQLite to PostgreSQL database
- **Usage**: `python backend/scripts/dev/migrate_to_postgres.py`
- **Features**:
  - Data migration with integrity checks
  - Backup creation before migration
  - Progress tracking and error recovery

#### `update_config_imports.py`
- **Purpose**: Update import statements across codebase for configuration changes
- **Usage**: `python backend/scripts/dev/update_config_imports.py`
- **Features**:
  - Automated import statement updates
  - File validation and backup
  - Comprehensive coverage of all modules

### 👨‍💼 Administration Scripts (`admin/`)

Scripts for data management, document processing, and system administration.

#### `convert_documents.py`
- **Purpose**: Convert documents to various formats for processing
- **Usage**: `python backend/scripts/admin/convert_documents.py`
- **Features**:
  - Multiple format support (PDF, TXT, MD, DOCX, XLSX)
  - Batch processing capabilities
  - PostgreSQL integration for logging

#### `load_training_data_e5.py`
- **Purpose**: Load training data into ChromaDB with E5 embeddings
- **Usage**: `python backend/scripts/admin/load_training_data_e5.py`
- **Features**:
  - E5 multilingual embedding model integration
  - Intelligent chunking for Q&A pairs
  - Comprehensive error handling and logging
  - Alternative file location detection
  - Collection management and testing

#### `enrich_training_data_with_citations.py`
- **Purpose**: Add citation metadata to existing training data
- **Usage**: `python backend/scripts/admin/enrich_training_data_with_citations.py`
- **Features**:
  - Automated metadata mapping
  - Source type classification
  - Database integrity verification
  - Progress tracking and validation

#### `manage_analytics.py`
- **Purpose**: Analytics data management and report generation
- **Usage**: 
  - Generate report: `python backend/scripts/admin/manage_analytics.py report --days 30`
  - Export CSV: `python backend/scripts/admin/manage_analytics.py export --output analytics.csv`
  - Cleanup old data: `python backend/scripts/admin/manage_analytics.py cleanup --days 90`
  - System health: `python backend/scripts/admin/manage_analytics.py health`
- **Features**:
  - Usage report generation
  - CSV export for scientific analysis
  - Data cleanup and maintenance
  - System health monitoring

### 🚀 Deployment Scripts (`deployment/`)

Scripts for production deployment and system validation.

#### `deploy.sh`
- **Purpose**: Production deployment automation
- **Usage**: `bash backend/scripts/deployment/deploy.sh`
- **Features**:
  - Environment setup
  - Service orchestration
  - Health check integration
  - Rollback capabilities

#### `health_check.py`
- **Purpose**: Comprehensive system health validation
- **Usage**: 
  - Basic check: `python backend/scripts/deployment/health_check.py`
  - Custom URL: `python backend/scripts/deployment/health_check.py --url http://prod-server:8000`
  - Save results: `python backend/scripts/deployment/health_check.py --output health_report.json`
- **Features**:
  - API endpoint validation
  - Database connectivity checks
  - Q&A system functionality testing
  - File upload validation
  - JSON report generation
  - Exit codes for CI/CD integration

## Common Standards

### Error Handling
All scripts implement comprehensive error handling:
- Try-catch blocks for all critical operations
- Detailed error logging with context
- Graceful degradation where possible
- Proper exit codes for automation

### Logging
Standardized logging across all scripts:
- Structured logging format with timestamps
- Multiple log levels (INFO, WARNING, ERROR)
- Clear progress indicators and status messages
- File and console output support

### Import Structure
Consistent import organization:
- Standard library imports first
- Third-party imports second
- Local application imports last
- Absolute imports only (no relative imports)
- Proper sys.path configuration for script location independence

### Configuration
Environment-aware configuration:
- Unified settings system integration
- Environment variable support
- Default value fallbacks
- Validation and error reporting

## Usage Examples

### Development Workflow
```bash
# Set up development environment
python backend/scripts/dev/setup_dev_env.py

# Load training data for testing
python backend/scripts/admin/load_training_data_e5.py

# Check system health
python backend/scripts/deployment/health_check.py --url http://localhost:8000
```

### Production Deployment
```bash
# Deploy to production
bash backend/scripts/deployment/deploy.sh

# Validate deployment
python backend/scripts/deployment/health_check.py --url https://prod.streamworks-ki.com

# Generate analytics report
python backend/scripts/admin/manage_analytics.py report --days 7
```

### Maintenance Tasks
```bash
# Update configuration imports after changes
python backend/scripts/dev/update_config_imports.py

# Export analytics for analysis
python backend/scripts/admin/manage_analytics.py export --output monthly_analytics.csv --days 30

# Clean up old analytics data
python backend/scripts/admin/manage_analytics.py cleanup --days 90
```

## Exit Codes

All scripts follow standard exit code conventions:
- `0`: Success
- `1`: General error
- `2`: Warning (for health checks)

## Dependencies

Scripts utilize the unified application dependencies:
- **Core**: Python 3.9+, asyncio, pathlib
- **Database**: SQLAlchemy 2.0, asyncpg (PostgreSQL)
- **AI/ML**: sentence-transformers, chromadb
- **Web**: requests, fastapi
- **Utilities**: logging, argparse, csv

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure scripts are run from the project root or backend directory
2. **Database Connection**: Verify DATABASE_URL environment variable is set correctly
3. **File Permissions**: Ensure scripts have execute permissions (`chmod +x script.sh`)
4. **Path Issues**: Scripts use absolute paths and sys.path manipulation to be location-independent

### Debug Mode
Enable detailed logging by setting the LOG_LEVEL environment variable:
```bash
export LOG_LEVEL=DEBUG
python backend/scripts/admin/load_training_data_e5.py
```

### Health Check Debugging
Use verbose health checks to diagnose issues:
```bash
python backend/scripts/deployment/health_check.py --timeout 60 --output debug_health.json
```

## Contributing

When adding new scripts:

1. **Category Placement**: Place scripts in the appropriate category directory
2. **Naming Convention**: Use descriptive names with underscores (snake_case)
3. **Documentation**: Include comprehensive docstrings and comments
4. **Error Handling**: Implement proper try-catch blocks and logging
5. **Testing**: Test scripts in development environment before deployment
6. **Standards**: Follow the established patterns for imports, logging, and configuration

## Security Considerations

- Scripts never log sensitive information (passwords, tokens)
- Configuration files are read securely with proper error handling
- Database connections use environment variables, not hardcoded credentials
- File operations include proper validation and sanitization
- Scripts run with minimal required permissions

---

**Last Updated**: 2025-07-23  
**Maintainer**: StreamWorks-KI Development Team  
**Status**: Production Ready ✅