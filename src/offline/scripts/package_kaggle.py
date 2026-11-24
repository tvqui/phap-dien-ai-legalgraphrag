"""Build a private upload bundle and beginner Notebook; never uploads or runs models."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / 'build/kaggle'

BUNDLE_FOLDERS = [
    ('src', {'.py'}),
    ('src/offline/config', {'.yaml', '.json', '.owl'}),
    ('src/online/backend/config', {'.yaml', '.json'}),
    ('evaluation/gold/templates', {'.json', '.jsonl'}),
    ('src/offline/review/corrections', {'.txt', '.json'}),
    ('src/offline/kaggle', {'.py', '.txt'}),
    ('src/online/backend/kaggle', {'.py', '.txt'}),
    ('src/offline/tests', {'.py'}),
    ('src/online/backend/tests', {'.py'}),
]

BUNDLE_REQUIRED_FILES = [
    'docs/kaggle/offline-ai-enrichment.md',
    'docs/kaggle/guide.md',
    'docs/architecture/external-corpora-and-ontology.md',
    'docs/offline/artifact-layout.md',
    'pyproject.toml',
    'src/online/backend/scripts/prepare_dense_model.py',
    'src/offline/scripts/validate_outputs.py',
    'src/offline/scripts/package_kaggle.py',
    'src/offline/scripts/prepare_source_attachments.py',
    'src/offline/scripts/review_kaggle_extraction.py',
    'src/offline/scripts/source_links_workbook.py',
    'src/offline/scripts/audit_final_dataset.py',
    'src/offline/scripts/check_official_sources.py',
    'evaluation/scripts/evaluate_gold.py',
    'src/offline/scripts/prepare_review_inputs.py',
    'src/online/backend/scripts/pin_online_artifact.py',
    'src/offline/kaggle/bootstrap.py',
    'src/offline/kaggle/constraints.txt',
    'src/offline/kaggle/final_notebook.py',
    'src/offline/kaggle/remote.py',
    'src/offline/kaggle/aura_preflight.py',
    'src/offline/kaggle/offline_final_remote.py',
]


def collect_bundle_files(root=ROOT):
    files = {}
    for folder, suffixes in BUNDLE_FOLDERS:
        directory = root / folder
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob('*')):
            if (path.is_file() and not path.is_symlink()
                    and path.suffix.lower() in suffixes
                    and '__pycache__' not in path.parts):
                files[path.relative_to(root).as_posix()] = path

    missing = []
    for name in BUNDLE_REQUIRED_FILES:
        path = root / name
        if not path.is_file():
            missing.append(name)
        else:
            files[name] = path
    if missing:
        raise FileNotFoundError(
            'Required Kaggle bundle files are missing: ' + ', '.join(missing))
    return files


def make_notebook():
    import importlib.util
    source = ROOT / 'src/offline/kaggle/final_notebook.py'
    spec = importlib.util.spec_from_file_location('vn_labor_final_notebook', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.make_notebook()

def write_notebook():
    DEST.mkdir(parents=True, exist_ok=True)
    notebook = make_notebook()
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code':
            compile(''.join(cell['source']), f'cell-{i}', 'exec')
    destination = DEST / 'VN_Labor_Kaggle_V8.ipynb'
    payload=json.dumps(notebook, ensure_ascii=False, indent=2)
    destination.write_text(payload, encoding='utf-8')
    alias=DEST/'ai-v9-1.ipynb'; alias.write_text(payload,encoding='utf-8')
    for path in (destination,alias):
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        Path(str(path)+'.sha256').write_text(f'{digest}  {path.name}\n',encoding='ascii')
    import copy
    refresh=copy.deepcopy(notebook)
    for cell in refresh['cells']:
        if cell['cell_type']=='code':
            source=''.join(cell['source']).replace('RESUME_AI_ONLY = True','RESUME_AI_ONLY = False').replace(
                'REFRESH_EXTRACTION_QUALITY = False','REFRESH_EXTRACTION_QUALITY = True')
            compile(source,'quality-refresh-cell','exec');cell['source']=source.splitlines(keepends=True)
    refresh['cells'][0]['source']=('''# VN Labor — cập nhật extraction và dựng lại toàn bộ build

Bản này áp dụng page corrections mới, dựng lại structure/knowledge/graph/indexes,
kiểm tra link nguồn theo cấu hình mới, rồi chạy AI source-accounting-v2 và kiểm tra Aura. Dùng code ZIP mới và checkpoint
result_14-10. Đòi hỏi nhiều thời gian hơn bản AI-resume; không dùng lại index cũ
với text đã sửa. Technical checkpoint và recovery ZIP được xuất để tiếp tục khi cần.
GPU T4 x2, Internet, bốn Aura Secrets. Không tạo human legal approval tự động.
''').splitlines(keepends=True)
    full=DEST/'VN_Labor_Quality_Refresh.ipynb'
    full.write_text(json.dumps(refresh,ensure_ascii=False,indent=2),encoding='utf-8')
    Path(str(full)+'.sha256').write_text(f'{hashlib.sha256(full.read_bytes()).hexdigest()}  {full.name}\n',encoding='ascii')
    print(json.dumps({'notebook': str(destination), 'code_syntax': 'PASS', 'workflow': 'V8_1_CHECKPOINT_FIRST_REBUILD_AI_AURA'}, ensure_ascii=False, indent=2))
    return destination


def build():
    DEST.mkdir(parents=True, exist_ok=True)
    files = collect_bundle_files(ROOT)
    for folder, suffixes in [
            ('review/attachments', {'.pdf'}),
            ('data', {'.pdf', '.doc', '.docx', '.html', '.htm', '.txt', '.json'})]:
        directory = ROOT / folder
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob('*')):
            if (path.is_file() and not path.is_symlink()
                    and path.suffix.lower() in suffixes):
                files[path.relative_to(ROOT).as_posix()] = path
    converted = []
    stems = set()
    for raw in sorted((ROOT / 'data').rglob('*')):
        if raw.suffix.lower() != '.doc':
            continue
        if raw.stem.casefold() in stems:
            raise ValueError('DOC names collide; conversion cache needs a path-aware mapping first.')
        stems.add(raw.stem.casefold())
        cached = ROOT / 'artifacts/01_extracted/converted_docx' / (raw.stem + '.docx')
        if not cached.exists():
            raise FileNotFoundError(f'Convert this DOC locally before packaging: {raw.name}')
        seed = 'seed_converted/' + cached.name
        files[seed] = cached
        converted.append({'source': raw.relative_to(ROOT).as_posix(), 'seed': seed, 'output_name': cached.name})
    entries = []
    for name, p in sorted(files.items()):
        with p.open('rb') as f:
            sha = hashlib.file_digest(f, 'sha256').hexdigest()
        entries.append({'path': name, 'bytes': p.stat().st_size, 'sha256': sha})
    manifest = {'schema': 1, 'owner': 'qutrnvinh3', 'privacy': 'PRIVATE', 'bundle_revision': '20261027-source-links-v3',
                'corpus_files': sum(n.startswith('data/') for n in files),
                'converted_docs': converted, 'files': entries}
    archive = DEST / 'vn_labor_kaggle_v8.zip'
    temporary = archive.with_suffix('.tmp')
    with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as z:
        for name, p in sorted(files.items()):
            z.write(p, 'vn_labor_bundle/' + name)
        z.writestr('vn_labor_bundle/bundle_manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2))
    with zipfile.ZipFile(temporary) as z:
        bad = z.testzip()
        if bad:
            raise RuntimeError(f'Bad ZIP member: {bad}')
    try:
        temporary.replace(archive)
    except PermissionError:
        # A package created by another Windows identity may be locked/read-only.
        # Preserve the new build instead of deleting or overwriting it.
        archive = DEST / 'vn_labor_kaggle_v8_rebuilt.zip'
        temporary.replace(archive)
    write_notebook()
    with archive.open('rb') as stream:
        archive_sha256 = hashlib.file_digest(stream, 'sha256').hexdigest()
    sidecar = Path(str(archive) + '.sha256')
    sidecar.write_text(f'{archive_sha256}  {archive.name}\n', encoding='ascii')
    report = {'bundle_revision': '20261027-source-links-v3', 'bundle': archive.name, 'sha256': archive_sha256, 'sha256_file': sidecar.name,
              'workflow': 'V8_1_CHECKPOINT_FIRST_REBUILD_AI_AURA',
              'size_mb': round(archive.stat().st_size / 1e6, 2),
              'files': len(files), 'corpus_files': manifest['corpus_files'], 'converted_docs': len(converted),
              'zip_crc_check': 'PASS', 'notebook_code_syntax': 'PASS', 'uploaded': False, 'remote_execution_tested': False}
    (DEST / 'package_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--notebook-only', action='store_true')
    arguments = parser.parse_args()
    write_notebook() if arguments.notebook_only else build()
