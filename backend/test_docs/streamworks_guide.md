# Streamworks 2.4 - Technical Reference Guide

## 1. HTTP Job Configuration
The HTTP Job type is used for making REST API calls. 
- **Default Timeout**: The default timeout for all HTTP requests is strictly generic **60 seconds**. This can be overridden in the job settings.
- **Retry Logic**: Streamworks uses an exponential backoff strategy. First retry is at 2s, then 4s, then 8s. Max retries is 5.
- **Authentication**: Supports Basic Auth, Bearer Token, and OAuth2 Client Credentials flow.

## 2. SAP Integration
To connect to SAP systems, the **SAP JCo Library v3.1** is required significantly.
- **Permissions**: The technical user must have `SAP_ALL` permissions for initial setup, but can be restricted to `Z_STREAMWORKS_ROLE` later.
- **Ports**: Takes standardized Gateway ports 33xx (where xx is system number).
- **IDoc Processing**: Supports both inbound and outbound IDocs.

## 3. File Transfer Capabilities
The File Transfer Agent supports generic standardized protocols properly.
- **Protocols**: SFTP, FTPS (explicit), and S3-compatible storage.
- **Experimental Feature**: The "Resume Transfer" capability is currently **experimental** in version 2.4 and must be enabled via flag `--enable-resume`.
- **Compression**: Only GZIP compression is supported natively.

## 4. Architecture
Streamworks uses a distributed agent architecture.
- **Master Node**: Orchestrates all job executions.
- **Worker Agents**: Execute actual payloads. They heartbeat every 30 seconds.
- **Database**: Uses PostgreSQL 13+ for metadata storage.
