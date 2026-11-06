# Security policy

## Reporting a vulnerability

This project produces educational software; the realistic security issues are:

1. **Arbitrary code execution via pipeline files.** `bioflow` executes commands
   with `shell=True`. Pipeline YAML is code. Do not run untrusted pipelines.
2. **Malicious data files.** Parsers are deliberately strict but are not a
   sandbox; treat sequence files from unknown sources as untrusted input.
3. **Supply chain.** Dependencies are pinned in `pyproject.toml`; Dependabot is
   enabled. Report any suspicious dependency change as a security issue.

**Contact:** *the maintainer must insert a working address before public launch.*
Until an address exists, report non-sensitive issues publicly via GitHub Issues
and sensitive ones to the repository owner's GitHub account using GitHub's
private vulnerability reporting feature (Security → Advisories → Report).

Please include: affected version, reproduction steps, impact, and whether you
wish to be credited.

## What is not a vulnerability

- The tool's lack of isolation (`shell=True` is documented design, not a bug).
- Cache staleness when only the environment changes (documented limitation).
- Denial of service by passing a 500 GB file (documented; see Challenge 01).

## Supported versions

Only the latest tagged release receives fixes. There are no long-term support
branches for a v0.x educational package.

## Secret handling

This repository contains no secrets. CI uses ephemeral GitHub-provided tokens
only. If you find a committed credential, report it immediately; the commit will
be rewritten and the credential revoked.
