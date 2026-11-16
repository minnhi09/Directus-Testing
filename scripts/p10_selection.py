"""Offline P10 selection guard. Does not create execution evidence or contact SUT."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'docs/coverage/baselines/M1-REGRESSION-13-v1/selection-manifest.json'


def validate(selection, baseline):
    pairs = [(t['canonical_test_id'], t['test_version']) for t in selection['tests']]
    expected = [(t['canonical_test_id'], t['test_version']) for t in baseline['tests']]
    if len(pairs) != 13 or len(set(pairs)) != 13 or pairs != expected:
        raise ValueError('Canonical selection differs from locked regression13')
    for key in ('baseline_id', 'denominator_revision', 'requirement_ids', 'inventory_ids',
                'unit', 'run_selection_policy', 'retry_policy', 'decision_id'):
        if selection[key] != baseline[key]:
            raise ValueError('Locked selection field changed: '+key)
    if len(selection['run_ids']) != 1 or len(selection['execution_ids']) != 13:
        raise ValueError('Predeclare one run and 13 unique execution IDs')
    if len(set(selection['execution_ids'])) != 13:
        raise ValueError('Duplicate execution ID')
    if not all(t['mandatory'] is True for t in selection['tests']):
        raise ValueError('Mandatory test removed')
    return {'valid':True,'canonical_selected':13,'execution_evidence_created':False,
            'coverage':'NOT_MEASURED'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('selection', type=Path)
    args = parser.parse_args()
    print(json.dumps(validate(json.loads(args.selection.read_text()), json.loads(BASE.read_text()))))
