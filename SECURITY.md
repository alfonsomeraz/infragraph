# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a vulnerability in InfraGraph, email **security@infragraph.dev** with:

1. A description of the vulnerability and its potential impact
2. Steps to reproduce the issue
3. Any proof-of-concept code (if applicable)

You will receive an acknowledgement within **48 hours** and a detailed response within **7 days** indicating the next steps.

We ask that you:
- Give us reasonable time to fix the issue before any public disclosure
- Avoid accessing or modifying data belonging to other users
- Avoid degrading the service for others (no DoS testing)

## Scope

InfraGraph processes Terraform plan and state JSON files, which may contain sensitive infrastructure details (IP addresses, resource names, tags). Key security considerations:

- **File upload handling**: Uploaded files are parsed in-memory; only resource metadata is stored in the database. Raw file content is not persisted.
- **No authentication**: The current v0.1.0 API has no authentication or authorization. Do not expose the API to untrusted networks without a reverse proxy/auth layer.
- **Database**: The database stores resource metadata, relationship graphs, and findings. Protect your PostgreSQL instance with appropriate network rules and credentials.
- **Terraform secrets**: Terraform state files can contain sensitive values (passwords, API keys). InfraGraph stores all JSONB attributes — ensure your database is appropriately secured.

## Disclosure Policy

Once a reported vulnerability is fixed, we will:

1. Publish a patched release
2. Add an entry to [CHANGELOG.md](CHANGELOG.md)
3. Credit the reporter (unless they prefer to remain anonymous)
