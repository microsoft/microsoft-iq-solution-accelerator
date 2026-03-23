# Cloning a Private Microsoft GitHub Repo

## Problem
Cloning a repo from the `microsoft` organization fails with a 403 SAML SSO error:
```
fatal: unable to access '...': The requested URL returned error: 403
remote: The 'microsoft' organization has enabled or enforced SAML SSO.
```

## Steps to Resolve the Problem and Clone the Repo

**Step 1** — Re-authorize GitHub CLI for org access:
```powershell
gh auth refresh -s read:org
```

**Step 2** — It shows a one-time code and opens a browser. In the browser:
- Go to **https://github.com/login/device**
- Enter the one-time code
- Sign in and **authorize SAML SSO** for the `microsoft` organization

**Step 3** — Clone using GitHub CLI (not `git clone`):
```powershell
cd C:YourLocalDir
gh repo clone microsoft/repo-name-solution-accelerator
```

