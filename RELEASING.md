# Releasing a New Version

To publish a new version for HACS users to install or switch to:

1. **Update version** in `custom_components/leddmx/manifest.json`:
   ```json
   "version": "0.2.0"
   ```

2. **Update CHANGELOG.md** with the changes for this version.

3. **Commit and push**:
   ```bash
   git add custom_components/leddmx/manifest.json CHANGELOG.md
   git commit -m "Release v0.2.0"
   git push origin main
   ```

4. **Create and push a tag** (use the same version as manifest, with `v` prefix):
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

5. **(Optional)** Create a GitHub Release from the tag for release notes.

HACS will then show v0.2.0 as an available version. Users can switch versions via:
HACS -> Integrations -> LEDDMX BLE -> Reinstall -> Select version.
