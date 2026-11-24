"""Graph mechanism study: reuse the trusted evaluator, isolate adaptive expansion.

No changes to production or existing ablation algorithms. Python 3.12+.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import random
import sys
import tempfile
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO/'evaluation/core'))
sys.path.insert(0, str(HERE.parent))
import eval_core as e
import adapters
from compare_ablation_results import extract_checked

PROTOCOL = 'graph-mechanism-120-v1'
ARMS = ('graph_off', 'graph_on')
METRICS = ('ai_correctness', 'ai_completeness', 'ai_evidence_support',
           'gold_citation_group_recall', 'citation_locator_metadata_match',
           'citation_url_metadata_match', 'elapsed_ms')


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def config_for_arm(base, method):
    if method not in ARMS:
        raise ValueError('Choose graph_on or graph_off')
    cfg = base.model_copy(deep=True)
    # Preserve deployed exact/profile shortcuts and alternative retrieval paths.
    # Both arms use cold per-request retrieval cache, not shared response caches.
    cfg.retrieval.request_cache_enabled = False
    cfg.graph.enabled = method == 'graph_on'
    return cfg


class GraphAdapter(adapters.ProjectAdapter):
    def __init__(self, method, settings, manifest, out):
        from vn_labor_online.pipeline import OnlinePipeline
        from common import redact
        self.method, self.settings = method, settings
        self.cfg = config_for_arm(adapters.config_for_bundle(settings, manifest, out), method)
        if self.cfg.graph.mode != 'adaptive':
            raise ValueError('This study isolates adaptive Graph expansion, not forced fixed expansion')
        if self.cfg.adjudication.mode == 'deterministic':
            raise ValueError('A generative adjudicator is required')
        self.pipe = OnlinePipeline(self.cfg)
        adapters.verify_store(self.pipe.store, manifest)
        self.effective = redact(self.cfg.model_dump(mode='json'))

    def prepare(self):
        result = super().prepare()
        result['ablation_semantics'] = {'graph_study': 'ONLY_GRAPH_ENABLED_DIFFERS',
            'shared_channels': 'exact/profile, case/community, issue anchors, reranker and agents retained'}
        return result


def register(scope="all120"):
    """Process-local registration; never patch the source of the shared suite."""
    original_create = adapters.create
    original_hashes = e.source_tree
    original_load_bundle = e.load_bundle
    spec = e.read(HERE/'question_groups.json')
    if scope not in spec['cohorts']: raise ValueError('Invalid graph_study_scope')
    allowed = set(spec['cohorts'][scope])
    def load_bundle(path):
        manifest,questions,corpus = original_load_bundle(path)
        return manifest,[q for q in questions if q['id'] in allowed],corpus
    e.load_bundle = load_bundle
    def create(method, task, settings, manifest, corpus, out, baseline=False):
        if method in ARMS:
            if baseline or task != 'qa': raise ValueError('Graph arms are QA only')
            Path(out).mkdir(parents=True, exist_ok=True)
            return GraphAdapter(method, settings, manifest, out)
        return original_create(method, task, settings, manifest, corpus, out, baseline)
    def source_tree():
        return original_hashes() | {str(p.relative_to(REPO)): e.sha(p)
            for p in sorted(HERE.iterdir()) if p.suffix in {'.py', '.ipynb', '.json'} and p.is_file()}
    adapters.ABLATIONS = ARMS
    adapters.create = create
    e.source_tree = source_tree


def freeze(bundle):
    manifest, questions, _ = e.load_bundle(bundle)  # validates actual IDs and evidence groups
    spec = e.read(HERE / 'question_groups.json')
    if manifest['gold_source_sha256'] != spec['gold_source_sha256']:
        raise ValueError('Gold ZIP changed; review input-only grouping before a new protocol version')
    actual = {q['id']: q for q in questions}
    if len(actual) != 120 or len(actual) != len(questions): raise ValueError('Expected 120 unique questions')
    if set(actual) != {q['id'] for q in spec['questions']}: raise ValueError('Question IDs changed')
    for q in spec['questions']:
        if any(actual[q['id']][k] != q[k] for k in ('question', 'query_date')):
            raise ValueError('Question text/date changed: ' + q['id'])
    frozen = dict(spec, questions_sha256=manifest['questions_sha256'],
        corpus_fingerprint=manifest['corpus_fingerprint'], grouping_sha256=e.sha(HERE/'question_groups.json'))
    path = Path(bundle) / 'graph_groups.json'
    if path.exists() and e.read(path) != frozen: raise ValueError('Frozen grouping changed')
    e.dump(path, frozen)
    return frozen


def graph_exposure(record):
    trace = record.get('result', {}).get('trace') or {}
    rounds = trace.get('graph_round_details')
    if not isinstance(rounds, list):
        return {'trace_available': False, 'expanded': None, 'accepted_ids': [],
                'selected_ids': [], 'cited_ids': [], 'claim_support_ids': []}
    accepted = {uid for r in rounds for uid in r.get('accepted_ids', [])}
    candidates = {uid for r in rounds for uid in r.get('candidate_ids', [])}
    result = record.get('result', {})
    selected = {uid for event in trace.get('events', []) if event.get('event') == 'selection'
                for uid in event.get('evidence_ids', [])}
    cited = {c['evidence_id'] for c in result.get('citations', []) if c.get('evidence_id')}
    claims = {uid for claim in result.get('claims', []) for uid in claim.get('evidence_ids', [])}
    return {'trace_available': True, 'expanded': bool(rounds), 'rounds': len(rounds),
        'candidate_ids': sorted(candidates), 'accepted_ids': sorted(accepted),
        'selected_ids': sorted(accepted & selected), 'cited_ids': sorted(accepted & cited),
        'claim_support_ids': sorted(accepted & claims),
        'provenance_limit': 'Traversed/accepted and later used; not proof that only Graph could retrieve it.'}


def load_archive(path, destination):
    extract_checked(Path(path), Path(destination))
    manifests = list(Path(destination).rglob('run_manifest.json'))
    if len(manifests) != 1: raise ValueError('Expected exactly one run manifest per input')
    manifest = e.read(manifests[0])
    if manifest.get('comparison_key') != e.fingerprint(manifest.get('comparison_controls')):
        raise ValueError('Comparison controls fingerprint mismatch')
    rows = e.rows(manifests[0].parent / 'responses.jsonl')
    seen = set()
    for row in rows:
        key = (row['id'], row.get('repeat', 1))
        if key in seen: raise ValueError('Duplicate attempt')
        if row['id'] not in manifest['selected_ids'] or row['method'] not in manifest['methods']:
            raise ValueError('Foreign response')
        if not 1 <= row.get('repeat', 1) <= manifest['repeats']: raise ValueError('Invalid repeat')
        seen.add(key)
    return manifest, rows, manifests[0].parent


def audit(archive, out):
    out = Path(out)
    if out.exists(): raise FileExistsError('Use a new audit output folder')
    out.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix='graph_audit_') as temp:
        manifest, records, _ = load_archive(archive, Path(temp)/'input')
        spec = {q['id']: q for q in e.read(HERE/'question_groups.json')['questions']}
        rows = []
        for row in records:
            exposure = graph_exposure(row)
            rows.append({'id': row['id'], 'question': row.get('question'), 'repeat': row.get('repeat', 1),
                'status': row['status'], 'group': spec.get(row['id'], {}).get('group', 'UNCLASSIFIED'), **exposure})
        e.dump(out/'graph_usage.json', rows)
        csv_rows = [{k: ';'.join(v) if isinstance(v, list) else v for k, v in r.items()} for r in rows]
        e.csv_write(out/'graph_usage.csv', csv_rows)
        summary = {'source_zip_sha256': e.sha(archive), 'records': len(records),
            'expanded': sum(r['expanded'] is True for r in rows),
            'accepted_extra_candidates': sum(bool(r['accepted_ids']) for r in rows),
            'accepted_and_selected': sum(bool(r['selected_ids']) for r in rows),
            'accepted_and_cited': sum(bool(r['cited_ids']) for r in rows),
            'accepted_and_claim_support': sum(bool(r['claim_support_ids']) for r in rows),
            'unknown_trace': sum(not r['trace_available'] for r in rows),
            'interpretation': 'POST_HOC_DESCRIPTIVE_ONLY_NOT_PROOF_OF_CAUSAL_BENEFIT',
            'method': manifest['methods'], 'comparison_key': manifest['comparison_key']}
        e.dump(out/'summary.json', summary)
    return summary


def numeric(record, metric):
    if record is None or record.get('status') != 'OK': return None
    value = record.get('elapsed_ms') if metric == 'elapsed_ms' else record.get('metrics', {}).get(metric)
    if metric.startswith('ai_') and record.get('judge', {}).get('status') != 'AI_JUDGED': return None
    if isinstance(value, bool) or not isinstance(value, (int, float)): return None
    import math
    return float(value) if math.isfinite(value) else None


def interval(values, repeats=2000):
    if len(values) < 2: return [None, None]
    rng = random.Random(42)
    samples = sorted(sum(rng.choices(values, k=len(values))) / len(values) for _ in range(repeats))
    return [samples[int(.025*repeats)], samples[min(repeats-1, int(.975*repeats))]]


def comparison(on_archive, off_archive, out):
    out = Path(out)
    if out.exists(): raise FileExistsError('Use a new comparison output folder')
    out.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix='graph_compare_') as temp:
        on_m, on, on_dir = load_archive(on_archive, Path(temp)/'on')
        off_m, off, off_dir = load_archive(off_archive, Path(temp)/'off')
        if on_m['methods'] != ['graph_on'] or off_m['methods'] != ['graph_off']:
            raise ValueError('Old full/without_graph ablations switch multiple channels; not this pure contrast')
        if on_m['comparison_key'] != off_m['comparison_key']:
            raise ValueError('Code/data/models/prompts/hardware controls differ; comparison blocked')
        specs = []
        for directory, manifest, arm in ((on_dir,on_m,'graph_on'),(off_dir,off_m,'graph_off')):
            bundle_path = directory.parents[1]/'bundle120'
            spec = e.read(bundle_path/'graph_groups.json')
            if spec['questions_sha256'] != manifest['bundle']['questions_sha256']:
                raise ValueError('Group labels do not match measured Gold')
            specs.append(spec)
            init = e.read(directory/'methods'/arm/'initialization.json')['details']['effective_config']
            init = {k:v for k,v in init.items() if k not in ('cache_dir','trace_dir','artifact_source')}
            if init['graph']['enabled'] != (arm == 'graph_on'): raise ValueError('Wrong effective Graph flag')
            init['graph'] = dict(init['graph'], enabled=True)
            if arm == 'graph_on': effective_on = init
            elif init != effective_on: raise ValueError('Effective configurations differ beyond graph.enabled')
        if specs[0] != specs[1]: raise ValueError('Grouping differs')
        spec = {q['id']:q for q in specs[0]['questions']}
        on_rows = {(r['id'],r.get('repeat',1)):r for r in on}
        off_rows = {(r['id'],r.get('repeat',1)):r for r in off}
        detail = []
        for qid in on_m['selected_ids']:
            for rep in range(1,on_m['repeats']+1):
                a,b = on_rows.get((qid,rep)),off_rows.get((qid,rep))
                row = {'id':qid,'repeat':rep,'group':spec[qid]['group'],'question':spec[qid]['question'],
                    'on_status': a.get('status') if a else 'NOT_RUN', 'off_status': b.get('status') if b else 'NOT_RUN',
                    'on_answer': (a or {}).get('result',{}).get('answer'),
                    'off_answer': (b or {}).get('result',{}).get('answer'),
                    'on_citations': (a or {}).get('result',{}).get('citations',[]),
                    'off_citations': (b or {}).get('result',{}).get('citations',[]),
                    'on_graph_exposure': graph_exposure(a or {})}
                for metric in METRICS:
                    av,bv = numeric(a,metric),numeric(b,metric)
                    row[metric] = {'on':av,'off':bv,'delta':av-bv if av is not None and bv is not None else None}
                detail.append(row)
        summary=[]
        for group in ['all'] + sorted({q['group'] for q in spec.values()}):
            selected = [r for r in detail if group=='all' or r['group']==group]
            if not selected: continue
            for metric in METRICS:
                paired = defaultdict(list)
                for r in selected:
                    v = r[metric]
                    if v['delta'] is not None: paired[r['id']].append(v)
                # Query is the resampling unit, not a repeat or an LLM call.
                means = [{k:sum(v[k] for v in vals)/len(vals) for k in ('on','off','delta')} for vals in paired.values()]
                deltas=[v['delta'] for v in means]
                ci=interval(deltas)
                summary.append({'group':group,'metric':metric,'scheduled_queries':len({r['id'] for r in selected}),
                    'paired_scored_queries':len(means),'paired_attempts':sum(map(len,paired.values())),
                    'on_errors':sum(r['on_status']=='ERROR' for r in selected),
                    'off_errors':sum(r['off_status']=='ERROR' for r in selected),
                    'on_not_run':sum(r['on_status']=='NOT_RUN' for r in selected),
                    'off_not_run':sum(r['off_status']=='NOT_RUN' for r in selected),
                    'on_mean':sum(v['on'] for v in means)/len(means) if means else None,
                    'off_mean':sum(v['off'] for v in means)/len(means) if means else None,
                    'delta_on_minus_off':sum(deltas)/len(deltas) if deltas else None,
                    'ci95_low':ci[0],'ci95_high':ci[1],
                    'on_better_queries':sum(v<0 if metric=='elapsed_ms' else v>0 for v in deltas),
                    'off_better_queries':sum(v>0 if metric=='elapsed_ms' else v<0 for v in deltas),
                    'tied_queries':sum(v==0 for v in deltas)})
        e.dump(out/'question_by_question.json', detail)
        e.dump(out/'group_comparison.json', summary)
        e.csv_write(out/'group_comparison.csv',summary)
        e.csv_write(out/'question_by_question.csv',[{k:canonical(v) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in detail])
        e.dump(out/'provenance.json',{'protocol':PROTOCOL,'on_zip_sha256':e.sha(on_archive),'off_zip_sha256':e.sha(off_archive),
            'comparison_key':on_m['comparison_key'],'scope':specs[0]['evaluation_scope'],
            'label_status':on_m['bundle']['label_status'],
            'notes':['AI judge is not legal certification','Group comparisons are exploratory; no multiplicity-adjusted significance claim',
                     'Missing/errors never treated as zero or PASS','Graph traversal/citation does not establish exclusive necessity']})
        def fmt(x): return 'N/A' if x is None else f'{x:.4f}'
        lines=['# Graph ON / OFF: mở rộng Graph theo chỗ thiếu', '',
            'Nhãn DRAFT; tập phát triển đã sử dụng trước đây. CI là bootstrap theo câu hỏi; không phải chứng nhận đúng luật.', '',
            '| Nhóm | Chỉ số | Câu ghép / dự kiến | OFF | ON | ON − OFF | CI 95% |',
            '|---|---|---:|---:|---:|---:|---|']
        lines += [f"| {r['group']} | {r['metric']} | {r['paired_scored_queries']}/{r['scheduled_queries']} | {fmt(r['off_mean'])} | {fmt(r['on_mean'])} | {fmt(r['delta_on_minus_off'])} | [{fmt(r['ci95_low'])}, {fmt(r['ci95_high'])}] |" for r in summary]
        (out/'comparison.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return summary


def package(output):
    paths = set(REPO.glob('src/**/*.py'))
    paths |= set((REPO/'evaluation/core').glob('*.py'))
    paths |= set((REPO/'evaluation/suite').glob('*.py'))
    paths |= set((REPO/'config').glob('*.yaml'))
    paths |= {REPO/'pyproject.toml',REPO/'evaluation/core/settings.example.json',REPO/'evaluation/core/requirements.txt',
              REPO/'evaluation/gold/PhapDienAI_Gold_120_Labor_v0_2.zip'}
    paths |= {p for p in HERE.iterdir() if p.suffix in {'.py','.json','.ipynb','.md'}}
    inventory={p.relative_to(REPO).as_posix():e.sha(p) for p in sorted(paths) if p.is_file()}
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
        import base64
        # Kaggle recursively extracts nested .zip uploads. Transport the original
        # bytes as base64 text, then restore and verify the ORIGINAL ZIP hash.
        for name in inventory:
            if name.endswith('.zip'):
                z.writestr(name+'.b64.txt',base64.b64encode((REPO/name).read_bytes()))
            else:
                z.write(REPO/name,name)
        z.writestr('GRAPH_CODE_SHA256.json',json.dumps(inventory,ensure_ascii=False,indent=2))
    print(output)


def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in {'audit','freeze','compare','package'}:
        p=argparse.ArgumentParser(description=__doc__)
        sub=p.add_subparsers(dest='action',required=True)
        a=sub.add_parser('audit');a.add_argument('--zip',required=True);a.add_argument('--out',required=True)
        f=sub.add_parser('freeze');f.add_argument('--bundle',required=True)
        c=sub.add_parser('compare');c.add_argument('--on',required=True);c.add_argument('--off',required=True);c.add_argument('--out',required=True)
        g=sub.add_parser('package');g.add_argument('--output',required=True)
        args=p.parse_args(argv)
        if args.action=='audit': print(canonical(audit(args.zip,args.out)))
        elif args.action=='freeze': print('Frozen:',len(freeze(args.bundle)['questions']),'questions')
        elif args.action=='compare': comparison(args.on,args.off,args.out);print(Path(args.out)/'comparison.md')
        else:package(args.output)
        return 0
    if argv and argv[0]=='run':
        if '--bundle' not in argv: raise ValueError('--bundle is required')
        freeze(argv[argv.index('--bundle')+1])
    scope='all120'
    if argv and argv[0]=='run' and '--config' in argv:
        scope=e.read(argv[argv.index('--config')+1]).get('graph_study_scope','all120')
    register(scope)
    sys.argv=[sys.argv[0]]+argv
    return e.main()


if __name__=='__main__': raise SystemExit(main())
