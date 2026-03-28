# Security policy

## Supported versions

Security fixes are applied to the latest commit on the default branch of this repository. There are no long-term support branches unless noted in the README.

## Reporting a vulnerability

Please **do not** open a public GitHub issue for undisclosed security vulnerabilities.

Instead, report details privately to the repository maintainers (use GitHub **Security Advisories** if enabled for this repo, or contact information listed in the repository profile / README once added).

Include:

- A short description of the issue and its impact
- Steps to reproduce (proof-of-concept if possible)
- Affected component (backend API, Nuxt frontend, Docker image, etc.)

We will acknowledge receipt as soon as we can and coordinate a fix and disclosure timeline.

## Scope

This project is a demonstration / research-oriented dashboard. It calls third-party public APIs (NASA POWER, ISRIC SoilGrids) and does not store credentials for NASA Earthdata in the default configuration. Operational security (authentication, private networks, WAF, rate limits at the edge) remains the deployer’s responsibility.
