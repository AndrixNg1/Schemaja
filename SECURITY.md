# Security Policy

## Reporting a vulnerability

If you find a security issue in Holocron, please report it privately rather than opening a public issue — use GitHub's [private vulnerability reporting](https://github.com/VictoireNdala/Holocron/security/advisories/new) if enabled on this repository, or contact the repository owner directly.

Please include:
- A description of the issue and its potential impact
- Steps to reproduce it
- Any relevant logs or screenshots (with sensitive data redacted)

## Project context

Holocron is an academic platform originally built for a closed campus network (not internet-facing). Some security trade-offs reflect that context and are documented in the project's internal history rather than being oversights — but the repository is now public, which changes what matters:

- **Credentials in version control**: earlier commits (and, until rotated, some current configuration) contain real deployment credentials in `docker-compose.yml` and related files. Making the repository public does not erase this from Git history. If you're reusing this project, rotate every credential before deploying, and avoid committing secrets going forward (use a non-committed `.env` file instead).
- **JWT handling**: the backend requires `JWT_SECRET` to be set via environment variable and fails to start otherwise — there is no insecure default baked into the code.
- **Per-user storage access**: file operations always authenticate with the connected user's own Nextcloud credentials, never a shared admin client, to avoid privilege-escalation across accounts.

## Supported scope

This is a student project under active development, not a maintained security-critical product. Fixes are best-effort. If you're deploying a fork of this project, treat the current `main` branch as a starting point requiring your own security review, not a hardened baseline.
