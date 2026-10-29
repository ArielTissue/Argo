"""Behavior tests across the same interface used by the CLI/host skill."""
from copy import deepcopy
from datetime import timedelta
from importlib.resources import files
import json
from pathlib import Path
import tempfile
import unittest

from argo.brokers import HostBroker
from argo.calendar import release_plan
from argo.context import portfolio_context
from argo.storage import ArgoError, atomic_write, child, digest, json_text, load, timestamp
from argo.workflow import apply, init_workspace, plan, prepare, stage

NOW = timestamp("2026-10-29T12:00:00Z")


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = init_workspace(Path(self.temp.name) / "user-workspace")

    def task_and_proposal(self):
        task = prepare(self.root, "AURX", NOW)
        proposal = json.loads(files("argo_examples").joinpath("proposal.json").read_text())
        proposal["run_id"] = task["run_id"]
        return task, proposal

    def test_end_to_end_preview_apply_and_idempotence(self):
        task, proposal = self.task_and_proposal()
        before = {p.name: digest(p) for p in (self.root / "knowledge").glob("*.md")}
        staged = stage(self.root, task["run_id"], proposal)
        self.assertEqual(staged["status"], "staged")
        self.assertFalse((self.root / "outputs").exists())
        result = apply(self.root, task["run_id"])
        self.assertEqual(result["status"], "applied")
        report = (self.root / task["output"]).read_text()
        self.assertIn("33.33%", report)
        self.assertIn("| Core | 63.2% | 50.0%–80.0% | Within band |", report)
        self.assertIn("| Technology theme | 40.0% | At most 35.0% | Over limit |", report)
        self.assertIn("P-SINGLE-STOCK", report)
        self.assertNotIn("```json", report.split("## Portfolio context")[1].split("## Decision support")[0])
        self.assertEqual((self.root / "outputs/calendar.md").read_text().count("| AURX-FY2026-Q3 |"), 1)
        self.assertEqual(apply(self.root, task["run_id"])["status"], "already_applied")
        self.assertEqual(before, {p.name: digest(p) for p in (self.root / "knowledge").glob("*.md")})
        self.assertEqual(next(e for e in plan(self.root, NOW) if e['symbol'] == 'AURX')['status'], 'reviewed')

    def test_after_market_release_is_not_an_available_report(self):
        status = {e['symbol']: e['status'] for e in plan(self.root, NOW)}
        self.assertEqual(status['HARB'], 'scheduled')
        with self.assertRaisesRegex(ArgoError, 'No verified'):
            prepare(self.root, 'HARB', NOW)
        self.assertFalse((self.root / 'outputs').exists())
        self.assertFalse((self.root / 'runs').exists())

    def test_expected_date_passing_does_not_establish_release(self):
        later = NOW + timedelta(days=1)
        self.assertEqual(next(e for e in plan(self.root, later) if e['symbol'] == 'HARB')['status'], 'release_unverified')

    def test_unknown_watchlist_event_remains_visible(self):
        watch = load(self.root / 'watchlist.json')
        watch['symbols'].append({'symbol': 'NEW', 'company': 'New Example', 'ir_url': 'https://example.org/new'})
        atomic_write(self.root / 'watchlist.json', json_text(watch))
        self.assertEqual(next(e for e in plan(self.root, NOW) if e['symbol'] == 'NEW')['status'], 'date_unknown')

    def test_unknown_portfolio_is_not_flat(self):
        (self.root / 'portfolio.json').unlink()
        task, proposal = self.task_and_proposal()
        self.assertEqual(task['portfolio']['status'], 'incomplete')
        proposal['decision']['stance'] = 'consider'
        with self.assertRaisesRegex(ArgoError, 'block additions|frozen theme'):
            stage(self.root, task['run_id'], proposal)

    def test_same_company_different_portfolio_changes_addition_gate(self):
        task, proposal = self.task_and_proposal()
        proposal['decision']['stance'] = 'consider'
        with self.assertRaisesRegex(ArgoError, 'block additions|frozen theme'):
            stage(self.root, task['run_id'], proposal)
        portfolio = load(self.root / 'portfolio.json')
        portfolio['positions'][1]['market_value'] = 5000
        policy = load(self.root / 'policy.json')
        policy['frozen_themes'] = []
        atomic_write(self.root / 'portfolio.json', json_text(portfolio))
        atomic_write(self.root / 'policy.json', json_text(policy))
        new_task, new_proposal = self.task_and_proposal()
        new_proposal['decision']['stance'] = 'consider'
        self.assertEqual(stage(self.root, new_task['run_id'], new_proposal)['status'], 'staged')

    def test_theme_freeze_is_candidate_specific(self):
        policy = load(self.root / 'policy.json')
        policy['single_stock_max'] = 1
        policy['theme_limits']['technology'] = 1
        atomic_write(self.root / 'policy.json', json_text(policy))
        # Freeze remains but the unrelated portfolio-level breaches are resolved.
        task, proposal = self.task_and_proposal()
        proposal['decision']['stance'] = 'consider'
        with self.assertRaisesRegex(ArgoError, 'frozen theme'):
            stage(self.root, task['run_id'], proposal)
        calendar = load(self.root / 'earnings.json')
        calendar['events'][1]['released_at'] = '2026-10-29T08:00:00Z'
        atomic_write(self.root / 'earnings.json', json_text(calendar))
        other = prepare(self.root, 'HARB', NOW)
        proposal.update(run_id=other['run_id'], symbol='HARB', event_id='HARB-FY2026-Q3')
        proposal['decision']['rationale'] = 'Industrial candidate has no exposure to the frozen technology theme.'
        self.assertEqual(stage(self.root, other['run_id'], proposal)['status'], 'staged')

    def test_exact_denominator_and_findings(self):
        policy, portfolio = load(self.root / 'policy.json'), load(self.root / 'portfolio.json')
        result = portfolio_context(portfolio, policy, NOW)
        self.assertEqual(result['investable_value'], 95000)
        self.assertEqual(result['account_value'], 100000)
        self.assertAlmostEqual(result['theme_weights']['technology'], .4)
        self.assertEqual({x['rule_id'] for x in result['findings']}, {'P-SINGLE-STOCK', 'P-THEME', 'P-FROZEN'})

    def test_input_change_blocks_stale_report_commit(self):
        task, proposal = self.task_and_proposal()
        stage(self.root, task['run_id'], proposal)
        with (self.root / 'knowledge/margin-of-safety.md').open('a') as f:
            f.write('\nChanged policy context.\n')
        with self.assertRaisesRegex(ArgoError, 'Inputs or knowledge changed'):
            apply(self.root, task['run_id'])
        self.assertFalse((self.root / 'outputs').exists())

    def test_concurrent_output_edit_is_not_overwritten(self):
        task, proposal = self.task_and_proposal()
        stage(self.root, task['run_id'], proposal)
        target = self.root / 'outputs/calendar.md'
        atomic_write(target, 'User-written note\n')
        with self.assertRaisesRegex(ArgoError, 'Output changed'):
            apply(self.root, task['run_id'])
        self.assertEqual(target.read_text(), 'User-written note\n')
        self.assertFalse((self.root / task['output']).exists())

    def test_bad_claim_reference_and_fake_rule_rejected(self):
        task, base = self.task_and_proposal()
        for mutation, message in [
            (lambda p: p['claims'][0].update(evidence_ids=['S999']), 'existing evidence'),
            (lambda p: p['decision'].update(policy_refs=['P-THEME.subclause']), 'exact rule IDs'),
        ]:
            proposal = deepcopy(base)
            mutation(proposal)
            with self.assertRaisesRegex(ArgoError, message):
                stage(self.root, task['run_id'], proposal)

    def test_knowledge_link_must_resolve(self):
        task, proposal = self.task_and_proposal()
        proposal['analysis']['business_quality'] = 'See [[invented-concept]].'
        with self.assertRaisesRegex(ArgoError, 'Unresolved knowledge'):
            stage(self.root, task['run_id'], proposal)

    def test_validation_budget_terminates_failed_repair_loop(self):
        task, proposal = self.task_and_proposal()
        proposal['claims'][0]['evidence_ids'] = ['missing']
        for _ in range(3):
            with self.assertRaises(ArgoError):
                stage(self.root, task['run_id'], proposal)
        with self.assertRaisesRegex(ArgoError, 'attempt limit'):
            stage(self.root, task['run_id'], proposal)

    def test_retrieval_can_happen_after_task_preparation(self):
        task, proposal = self.task_and_proposal()
        proposal['evidence'][0]['accessed_at'] = '2026-10-29T12:00:01Z'
        self.assertEqual(stage(self.root, task['run_id'], proposal)['status'], 'staged')

    def test_insufficient_evidence_does_not_require_made_up_valuation(self):
        task, proposal = self.task_and_proposal()
        proposal['decision']['stance'] = 'insufficient_evidence'
        proposal['decision']['rationale'] = 'Official disclosure could not be retrieved.'
        proposal['valuation'] = None
        proposal['claims'] = []
        proposal['evidence'] = []
        stage(self.root, task['run_id'], proposal)
        apply(self.root, task['run_id'])
        self.assertIn('no intrinsic value', (self.root / task['output']).read_text())

    def test_future_evidence_is_rejected(self):
        task, proposal = self.task_and_proposal()
        proposal['evidence'][0]['published_at'] = '2026-10-30T08:00:00Z'
        with self.assertRaisesRegex(ArgoError, 'after the task'):
            stage(self.root, task['run_id'], proposal)

    def test_staged_content_tampering_rejected(self):
        task, proposal = self.task_and_proposal()
        stage(self.root, task['run_id'], proposal)
        path = self.root / f"runs/{task['run_id']}/changes.json"
        changes = load(path)
        changes['knowledge/margin-of-safety.md'] = 'overwrite'
        atomic_write(path, json_text(changes))
        with self.assertRaisesRegex(ArgoError, 'Staged files changed'):
            apply(self.root, task['run_id'])
        self.assertFalse((self.root / 'outputs').exists())

    def test_symlink_write_target_rejected(self):
        task, proposal = self.task_and_proposal()
        stage(self.root, task['run_id'], proposal)
        outside = Path(self.temp.name) / 'outside'
        outside.mkdir()
        (self.root / 'outputs').symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ArgoError, 'symlinks'):
            apply(self.root, task['run_id'])
        self.assertEqual(list(outside.iterdir()), [])

    def test_broker_gateway_rejects_orders_before_call(self):
        calls = []
        gateway = HostBroker(lambda name, args: calls.append(name) or {'example': True})
        with self.assertRaisesRegex(ArgoError, 'not allowed'):
            gateway.read('create_order_instruction')
        self.assertEqual(calls, [])
        self.assertEqual(len(gateway.account_snapshot()), 3)
        self.assertEqual(set(calls), {'get_account_positions', 'get_account_balances', 'get_account_summary'})

    def test_duplicate_or_nonfinite_holdings_rejected(self):
        portfolio, policy = load(self.root / 'portfolio.json'), load(self.root / 'policy.json')
        portfolio['positions'].append(deepcopy(portfolio['positions'][0]))
        with self.assertRaisesRegex(ArgoError, 'Duplicate holding'):
            portfolio_context(portfolio, policy, NOW)
        portfolio['positions'].pop()
        portfolio['positions'][0]['market_value'] = float('nan')
        with self.assertRaisesRegex(ArgoError, 'finite number'):
            portfolio_context(portfolio, policy, NOW)

    def test_initializer_never_overwrites_existing_directory(self):
        with self.assertRaisesRegex(ArgoError, 'never overwritten'):
            init_workspace(self.root)


if __name__ == '__main__':
    unittest.main()
