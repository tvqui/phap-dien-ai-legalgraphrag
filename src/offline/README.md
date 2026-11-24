# OFFLINE pipeline

The `vn_labor_offline` package is in `src/offline/src/vn_labor_offline/`.
Configuration, scripts, Kaggle helpers, human-review files, and tests are kept
alongside the package in this directory.

From the repository root, initialize the project environment and run the
pipeline with:

```powershell
run.bat setup-full
run.bat offline
run.bat validate
```

The default configuration is `src/offline/config/pipeline.yaml`. Source
documents and generated artifacts are local inputs/outputs; they are not moved
or included in Git by this package layout.
