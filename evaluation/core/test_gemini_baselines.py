from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

CORE = Path(__file__).resolve().parent
sys.path.insert(0, str(CORE))

from adapters import CommonReader, NoEvidenceRetriever, create
from eval_core import qa_metrics


class FakeProvider:
    context_tokens = 32768
    max_output_tokens = 6144

    def __init__(self, response):
        self.response = response
        self.calls = []

    def structured(self, system, user, schema):
        self.calls.append((system, json.loads(user), schema))
        return self.response

    def close(self):
        pass


class FakeRetriever:
    method = 'hybrid_rerank'

    def __init__(self, ids):
        self.ids = ids

    def prepare(self):
        return {'model_pins': {'retrieval': 'fixture'}}

    def run(self, request):
        return {'retrieved_ids': self.ids, 'llm_calls': 0}

    def close(self):
        pass


def answer(evidence_ids):
    return {
        'answer': 'Trả lời thử nghiệm.',
        'answer_status': 'ANSWERABLE',
        'claims': [{'text': 'Mệnh đề thử nghiệm.', 'evidence_ids': evidence_ids}],
        'questions': [],
    }


class GeminiBaselineTests(unittest.TestCase):
    def setUp(self):
        self.request = {
            'id': 'HD009',
            'question': 'Câu hỏi thử nghiệm',
            'query_date': '2026-09-15',
            'expected_status': 'ANSWERABLE',
            'reference_answer': 'Đáp án Gold không được gửi vào prompt.',
        }
        self.corpus = {
            'unit-1': {
                'display_text': 'Điều khoản luật mẫu.',
                'source_url': 'https://example.invalid/law',
                'valid_from': '2020-01-01',
                'valid_to': None,
                'article_number': '1',
                'clause_number': '1',
                'point_number': '',
                'document_number': '45/2019/QH14',
                'instrument_number': '45/2019/QH14',
            }
        }
        self.settings = {
            'reader': {'provider': 'gemini', 'model': 'gemini-test',
                       'temperature': 0, 'max_output_tokens': 6144, 'context_tokens': 32768},
            'reader_timeout_seconds': 45,
            'reader_k': 10,
            'context_char_limit': 24000,
        }

    def test_direct_mode_receives_only_question_and_date_without_evidence(self):
        provider = FakeProvider(answer([]))
        with patch('adapters.reader', return_value=provider):
            runner = CommonReader(NoEvidenceRetriever(), self.settings, self.corpus,
                                 direct=True, hide_question_metadata=True)
            result = runner.run(self.request)

        system, payload, _ = provider.calls[0]
        self.assertIn('pretrained knowledge only', system)
        self.assertNotIn('evidence', payload)
        self.assertEqual(payload['request'], {
            'question': 'Câu hỏi thử nghiệm',
            'query_date': '2026-09-15',
        })
        self.assertEqual(result['reader_context_ids'], [])
        self.assertEqual(result['citations'], [])
        metrics = qa_metrics(result, {
            'query_date': '2026-09-15',
            'required_groups': [['unit-1']],
            'expected_status': 'ANSWERABLE',
        }, self.corpus)
        self.assertEqual(metrics['gold_citation_group_recall'], 0)

    def test_same_evidence_mode_sends_retrieved_passage_and_binds_citation(self):
        provider = FakeProvider(answer(['unit-1']))
        with patch('adapters.reader', return_value=provider):
            runner = CommonReader(FakeRetriever(['unit-1']), self.settings, self.corpus,
                                 hide_question_metadata=True)
            result = runner.run(self.request)

        system, payload, _ = provider.calls[0]
        self.assertIn('ONLY supplied corpus excerpts', system)
        self.assertEqual(payload['request'], {
            'question': 'Câu hỏi thử nghiệm',
            'query_date': '2026-09-15',
        })
        self.assertEqual([item['id'] for item in payload['evidence']], ['unit-1'])
        self.assertEqual(result['citations'][0]['evidence_id'], 'unit-1')
        self.assertEqual(result['citations'][0]['official_url'], 'https://example.invalid/law')

    def test_direct_mode_rejects_model_generated_evidence_ids(self):
        provider = FakeProvider(answer(['fabricated-id']))
        with patch('adapters.reader', return_value=provider):
            runner = CommonReader(NoEvidenceRetriever(), self.settings, self.corpus,
                                 direct=True, hide_question_metadata=True)
            with self.assertRaisesRegex(ValueError, 'fabricated evidence ID'):
                runner.run(self.request)

    def test_runner_requires_gemini_key_and_qa_task_before_initialization(self):
        with tempfile.TemporaryDirectory() as output:
            with patch.dict(os.environ, {'GEMINI_API_KEY': ''}):
                with self.assertRaisesRegex(ValueError, 'GEMINI_API_KEY'):
                    create('gemini_direct', 'qa', self.settings, {}, self.corpus, output, baseline=True)
            with self.assertRaisesRegex(ValueError, 'QA-only'):
                create('gemini_direct', 'retrieval', self.settings, {}, self.corpus, output, baseline=True)


if __name__ == '__main__':
    unittest.main()
