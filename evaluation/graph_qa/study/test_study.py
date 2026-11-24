import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
NOTEBOOK=HERE.parents[1]/'notebooks/Kaggle_Graph_120.ipynb'
spec=importlib.util.spec_from_file_location('graph120_study',HERE/'run.py')
study=importlib.util.module_from_spec(spec);spec.loader.exec_module(study)

class GraphStudyTests(unittest.TestCase):
    def test_only_graph_flag_changes_and_shortcuts_remain(self):
        from vn_labor_online.config import OnlineConfig
        base=OnlineConfig(artifact_source="synthetic")
        base.retrieval.request_cache_enabled=True
        a=study.config_for_arm(base,'graph_on').model_dump()
        b=study.config_for_arm(base,'graph_off').model_dump()
        self.assertTrue(a['retrieval']['exact_lookup'])
        self.assertEqual(a['retrieval'],b['retrieval'])
        self.assertTrue(a['graph']['enabled']);self.assertFalse(b['graph']['enabled'])
        b['graph']['enabled']=True
        self.assertEqual(a,b)
        self.assertEqual(base.retrieval.request_cache_enabled,True)

    def test_120_ids_all_retained(self):
        spec=study.e.read(HERE/'question_groups.json')
        self.assertEqual(len(spec['questions']),120)
        self.assertEqual(len({q['id'] for q in spec['questions']}),120)
        self.assertEqual(spec['selection'],'ALL_120_NO_GRAPH_WINNER_SELECTION')
        self.assertIn('single_provision_controls',{q['group'] for q in spec['questions']})
        self.assertIn('relationship_hypothesis',{q['group'] for q in spec['questions']})

    def test_missing_trace_unknown_not_false_and_citations_need_intersection(self):
        self.assertIsNone(study.graph_exposure({})['expanded'])
        record={'result':{'trace':{'graph_round_details':[{'candidate_ids':['a','b'],'accepted_ids':['b']}],
            'events':[{'event':'selection','evidence_ids':['b']}]},
            'citations':[{'evidence_id':'a'},{'evidence_id':'b'}], 'claims':[{'evidence_ids':['a']}]}}
        result=study.graph_exposure(record)
        self.assertEqual(result['cited_ids'],['b'])
        self.assertEqual(result['selected_ids'],['b'])
        self.assertEqual(result['claim_support_ids'],[])

    def test_failed_or_unjudged_scores_excluded(self):
        row={'status':'OK','metrics':{'ai_correctness':1},'judge':{'status':'ERROR'}}
        self.assertIsNone(study.numeric(row,'ai_correctness'))
        row['judge']['status']='AI_JUDGED'
        self.assertEqual(study.numeric(row,'ai_correctness'),1)
        row['status']='ERROR'
        self.assertIsNone(study.numeric(row,'ai_correctness'))
        self.assertEqual(study.interval([1]),[None,None])

    def test_freeze_blocks_changed_gold_or_text(self):
        spec=study.e.read(HERE/'question_groups.json')
        questions=[dict(q) for q in spec['questions']]
        manifest={'gold_source_sha256':spec['gold_source_sha256'],'questions_sha256':'q','corpus_fingerprint':'c'}
        with tempfile.TemporaryDirectory() as tmp, patch.object(study.e,'load_bundle',return_value=(manifest,questions,{})):
            study.freeze(tmp)
            questions[0]['question']='changed'
            with self.assertRaises(ValueError):study.freeze(tmp)

    def _archive(self,path,arm,control='same',extra_change=False):
        groups=study.e.read(HERE/'question_groups.json');qid=groups['questions'][0]['id']
        groups.update(questions_sha256='gold',corpus_fingerprint='corpus')
        controls={'identity':control}
        manifest={'methods':[arm],'selected_ids':[qid],'repeats':1,'comparison_controls':controls,
            'comparison_key':study.e.fingerprint(controls),'bundle':{'questions_sha256':'gold','label_status':'DRAFT'}}
        cfg={'graph':{'enabled':arm=='graph_on'},'retrieval':{'exact_lookup':True}}
        if extra_change:cfg['retrieval']['exact_lookup']=False
        record={'id':qid,'repeat':1,'method':arm,'status':'OK','metrics':{'ai_correctness':.8 if arm=='graph_on' else .5},
            'elapsed_ms':20,'judge':{'status':'AI_JUDGED'},'result':{'answer':'test','citations':[]}}
        with zipfile.ZipFile(path,'w') as z:
            prefix='runs/'+arm+'/'
            z.writestr(prefix+'run_manifest.json',json.dumps(manifest))
            z.writestr(prefix+'responses.jsonl',json.dumps(record)+'\n')
            z.writestr(prefix+'methods/'+arm+'/initialization.json',json.dumps({'details':{'effective_config':cfg}}))
            z.writestr('bundle120/graph_groups.json',json.dumps(groups))

    def test_compare_complete_pair_and_fail_on_changed_controls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);a=root/'on.zip';b=root/'off.zip'
            self._archive(a,'graph_on');self._archive(b,'graph_off')
            table=study.comparison(a,b,root/'comparison')
            score=next(r for r in table if r['group']=='all' and r['metric']=='ai_correctness')
            self.assertAlmostEqual(score['delta_on_minus_off'],.3)
            self.assertIsNone(score['ci95_low'])
            self._archive(b,'graph_off',control='different')
            with self.assertRaises(ValueError):study.comparison(a,b,root/'blocked')

    def test_compare_blocks_multiple_effective_config_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);a=root/'on.zip';b=root/'off.zip'
            self._archive(a,'graph_on');self._archive(b,'graph_off',extra_change=True)
            with self.assertRaises(ValueError):study.comparison(a,b,root/'comparison')

    def test_notebook_cells_compile_and_are_clean(self):
        n=json.loads(NOTEBOOK.read_text(encoding='utf-8'))
        for i,c in enumerate(n['cells']):
            if c['cell_type']=='code':
                compile(''.join(c['source']),f'cell{i}','exec')
                self.assertFalse(c.get('outputs'))
                self.assertIsNone(c.get('execution_count'))
        source=''.join(''.join(c['source']) for c in n['cells'])
        self.assertIn("SOURCE='attached_zip'",source)
        self.assertIn("ARM='graph_on'",source)
        self.assertNotIn("METHODS=('full'",source)

    def test_focused_cohort_fixed_without_model_result_filter(self):
        import random
        spec=study.e.read(HERE/'question_groups.json')
        questions=spec['questions']
        controls=sorted(q['id'] for q in questions if q['group']=='single_provision_controls')
        sampled=set(random.Random(42).sample(controls,12))
        expected=sampled|{q['id'] for q in questions if q['group'] in {
            'relationship_hypothesis','conditions_hypothesis','behavioral_controls'}}
        self.assertEqual(set(spec['cohorts']['focused']),expected)
        self.assertEqual(len(expected),47)

    def test_notebook_accepts_both_zip_and_auto_extracted_code(self):
        import hashlib
        notebook=json.loads(NOTEBOOK.read_text(encoding='utf-8'))
        source=''.join(notebook['cells'][3]['source'])
        start=source.index("if SOURCE=='github':")
        end=source.index("if not (ROOT/'evaluation/core/retry_failed.py').exists():",start)
        block=source[start:end]
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            for extracted in (False,True):
                input_dir=base/('input_dir' if extracted else 'input_zip');input_dir.mkdir()
                payload=b'# synthetic code snapshot\n'
                name='evaluation/graph_qa/study/run.py';inventory={name:hashlib.sha256(payload).hexdigest()}
                if extracted:
                    path=input_dir/name;path.parent.mkdir(parents=True);path.write_bytes(payload)
                    (input_dir/'GRAPH_CODE_SHA256.json').write_text(json.dumps(inventory))
                else:
                    with zipfile.ZipFile(input_dir/'Graph_Study_Code.zip','w') as z:
                        z.writestr(name,payload);z.writestr('GRAPH_CODE_SHA256.json',json.dumps(inventory))
                target=base/('target_dir' if extracted else 'target_zip')
                env={'SOURCE':'attached_zip','CODE_ARCHIVE':'auto','ROOT':target,'Path':Path,'json':json}
                exec(compile(block.replace('/kaggle/input',input_dir.as_posix()),'bootstrap','exec'),env)
                self.assertEqual((target/name).read_bytes(),payload)

    def test_nested_gold_transport_and_legacy_dataset_recovery(self):
        import base64,hashlib
        notebook=json.loads(NOTEBOOK.read_text(encoding='utf-8'))
        source=''.join(notebook['cells'][3]['source'])
        block=source[source.index("if SOURCE=='github':"):source.index("if not (ROOT/'evaluation/core/retry_failed.py').exists():")]
        gold='evaluation/gold/PhapDienAI_Gold_120_Labor_v0_2.zip'
        payload=b'PK original gold archive bytes'
        main='evaluation/graph_qa/study/run.py';code=b'# code'
        inventory={main:hashlib.sha256(code).hexdigest(),gold:hashlib.sha256(payload).hexdigest()}
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp)
            for mode in ('zip','extracted','legacy_supplement','bad_sha'):
                inputs=base/(mode+'_input');inputs.mkdir()
                if mode=='zip':
                    with zipfile.ZipFile(inputs/'Graph_Study_Code.zip','w') as z:
                        z.writestr(main,code);z.writestr(gold+'.b64.txt',base64.b64encode(payload))
                        z.writestr('GRAPH_CODE_SHA256.json',json.dumps(inventory))
                else:
                    dataset=inputs/'code';(dataset/Path(main).parent).mkdir(parents=True)
                    (dataset/main).write_bytes(code)
                    (dataset/'GRAPH_CODE_SHA256.json').write_text(json.dumps(inventory))
                    parent=dataset/Path(gold).parent if mode=='extracted' else inputs/'supplement'
                    parent.mkdir(parents=True,exist_ok=True)
                    (parent/(Path(gold).name+'.b64.txt')).write_bytes(base64.b64encode(payload if mode!='bad_sha' else b'changed'))
                target=base/(mode+'_root')
                env={'SOURCE':'attached_zip','CODE_ARCHIVE':'auto','ROOT':target,'Path':Path,'json':json}
                program=compile(block.replace('/kaggle/input',inputs.as_posix()),'bootstrap','exec')
                if mode=='bad_sha':
                    with self.assertRaisesRegex(RuntimeError,'checksum mismatch'):exec(program,env)
                else:
                    exec(program,env)
                    self.assertEqual((target/gold).read_bytes(),payload)
                    self.assertEqual(hashlib.sha256((target/gold).read_bytes()).hexdigest(),inventory[gold])

if __name__=='__main__':unittest.main()
