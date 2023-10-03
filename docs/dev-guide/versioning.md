# Versioning

Hallux follows [PEP 440](https://peps.python.org/pep-0440/) versioning scheme composed from git tag and the distance. 

For example:

- git tag: 0.2
- distance: 10 commits since tag
- version: 0.2.10

## Tagging

Currently tagging is a manual process decided by maintainers based on development milestones.

```bash
git tag -a -m "Introduce tag versioning" 0.2
git push origin --tags
```

## Publishing a new version

Currently publishing a new version to a PyPI registry is a manual process decided by maintainers based on development milestones.

```bash
# Build source distribution
./scripts/build-package.sh

# Publish to PyPI
python3 -m twine upload --repository pypi dist/*
```
