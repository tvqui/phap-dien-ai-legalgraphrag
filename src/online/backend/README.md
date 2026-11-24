# ONLINE backend

The `vn_labor_online` package is in `src/online/backend/src/vn_labor_online/`.
Runtime configuration, service scripts, Kaggle helpers, and backend tests live
in this directory. The frontend is a separate project at
`src/online/frontend/`.

From the repository root, use the configured local profile with:

```powershell
run.bat online-check
run.bat online
```

The launcher defaults to `src/online/backend/config/online.yaml`; select another
profile with `-Config`. The Kaggle workflow starts from
`kaggle/ONLINE_Backend.ipynb`. Artifact compatibility and fingerprints remain
required after the reorganization.
