# Publishing checklist

This repository is ready to push. Nothing needs to be configured through files for the organization profile itself; the following settings must be changed in GitHub's web interface.

## Organization settings

1. Set the organization display name to **The Open Browser Company** (it currently reads "The open web browser").
2. Set the organization description to: *An independent software company building open-source browsers and tools for a better web.*
3. Upload the organization avatar from `assets/branding/organization-avatar/organization-avatar-512.png`.
4. GitHub organization pages do not have a separate banner upload. The banner is used by `profile/README.md`; it becomes visible once this repository is public and named `.github`.
5. If you have a real website, location, or social account, add it to the organization profile. No such details were supplied, so none are assumed here.

## Repository settings

1. Publish this repository as public under the name `.github` in the `OpenBrowserCompany` organization. The profile README must stay at `profile/README.md`.
2. Enable **Issues** if you want the organization-wide issue templates in `.github/ISSUE_TEMPLATE/` to be offered in repositories that do not define their own.
3. Set the repository's social preview image to `assets/branding/company-banner/social-preview-1280x640.png`.
4. Enable **private vulnerability reporting** so the SECURITY.md reporting path works.
5. Decide and add a repository license if you want one. No license was supplied for this repository, so none was created.
6. If you publish FUNDING.yml later, use only funding accounts you actually control. No funding links were supplied, so the file is intentionally absent.

## Decisions still needed

- Add a real private contact method to `CODE_OF_CONDUCT.md` (replace the marked placeholder).
- Add a real security contact to `SECURITY.md`, or confirm that private vulnerability reporting alone is sufficient.
- Confirm how much of the existing public catalog should be featured on the profile. Only `CATOPTRIC` is highlighted because it is the browser repository; the other public repositories are discoverable through the all-repositories link.

## Verify after pushing

```bash
python3 scripts/check_markdown.py
```

Then open `https://github.com/OpenBrowserCompany` and check the profile banner, the footer mark in both light and dark themes, and every link.
