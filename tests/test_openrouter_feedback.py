import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from pydantic import ValidationError

from app.services.openrouter import generate_training_plan

VALID = json.dumps({'updated_training_days': [], 'updated_milestones': []})


def response(content, finish='stop'):
    return SimpleNamespace(choices=[SimpleNamespace(
        finish_reason=finish, message=SimpleNamespace(content=content))])


class FeedbackTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict('os.environ', OPENROUTER_KEY='fake', OPENROUTER_MODEL='fake')
        self.read = patch('app.services.openrouter.Path.read_text', return_value='Test instructions')
        self.sdk = patch('app.services.openrouter.OpenAI')
        self.env.start()
        self.read.start()
        self.client = self.sdk.start().return_value.__enter__.return_value
        self.addCleanup(self.env.stop)
        self.addCleanup(self.read.stop)
        self.addCleanup(self.sdk.stop)

    def run_plan(self):
        return generate_training_plan({'target_date': '2026-11-03'})

    def test_valid_first_response(self):
        self.client.chat.completions.create.return_value = response(VALID)
        self.assertEqual(self.run_plan().updated_training_days, [])
        self.assertEqual(self.client.chat.completions.create.call_count, 1)

    def test_json_then_schema_error_then_success(self):
        invalid = json.dumps({'updated_training_days': [], 'updated_milestones': [{
            'id_milestone': 'ms_5k', 'date_estimated': '2026-12-01',
            'milestone_type': 'distance', 'milestone_distance': 5}]})
        self.client.chat.completions.create.side_effect = [
            response('bad json'), response(invalid), response(VALID)]
        self.run_plan()
        calls = self.client.chat.completions.create.call_args_list
        self.assertEqual([len(c.kwargs['messages']) for c in calls], [2, 4, 6])
        self.assertEqual(calls[1].kwargs['messages'][2]['content'], 'bad json')
        self.assertIn('updated_milestones.0.id_milestone', calls[2].kwargs['messages'][-1]['content'])

    def test_date_error_feedback(self):
        old = json.dumps({'updated_training_days': [{'training_day_date': '2026-01-01', 'trainings': []}],
                          'updated_milestones': []})
        self.client.chat.completions.create.side_effect = [response(old), response(VALID)]
        self.run_plan()
        self.assertIn('before target_date', self.client.chat.completions.create.call_args.kwargs['messages'][-1]['content'])

    def test_stops_after_three_invalid_responses(self):
        self.client.chat.completions.create.return_value = response('invalid')
        with self.assertRaises(ValidationError):
            self.run_plan()
        self.assertEqual(self.client.chat.completions.create.call_count, 3)

    def test_api_error_is_not_corrected(self):
        self.client.chat.completions.create.side_effect = RuntimeError('API unavailable')
        with self.assertRaisesRegex(RuntimeError, 'API unavailable'):
            self.run_plan()
        self.assertEqual(self.client.chat.completions.create.call_count, 1)

    def test_empty_and_incomplete_responses_are_not_corrected(self):
        for result in [response(''), response(VALID, 'length'), SimpleNamespace(choices=[])]:
            with self.subTest(result=result):
                self.client.chat.completions.create.reset_mock()
                self.client.chat.completions.create.return_value = result
                with self.assertRaises(RuntimeError):
                    self.run_plan()
                self.assertEqual(self.client.chat.completions.create.call_count, 1)
