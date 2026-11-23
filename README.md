# The Open Browser Company — GitHub organization

This repository configures the GitHub presence of The Open Browser Company. It is not an application repository.

- `profile/README.md` is the organization profile page shown at [github.com/OpenBrowserCompany](https://github.com/OpenBrowserCompany).
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, and `SUPPORT.md` are the organization-wide community health files.
- `.github/ISSUE_TEMPLATE/` and `.github/PULL_REQUEST_TEMPLATE.md` provide default templates for repositories that do not define their own.
- `assets/branding/` holds the supplied originals and generated derivatives.
- `docs/BRAND.md` documents the brand assets. `docs/PUBLISHING.md` lists the GitHub settings that still need to be done by hand.

To regenerate branding derivatives and check local references:

```bash
python3 scripts/generate-assets.py
python3 scripts/check_markdown.py
```
