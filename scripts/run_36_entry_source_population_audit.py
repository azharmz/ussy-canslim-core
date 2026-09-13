from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--observations', required=True)
    p.add_argument('--out', required=True)
    args = p.parse_args()

    counts = Counter()
    total = 0
    eligible_ids = set()
    breakout_ids = set()
    securities = set()

    with open(args.observations, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            total += 1
            stage = row.get('candidate_stage') or 'MISSING'
            counts[stage] += 1
            if stage == 'CANSLIM_ELIGIBLE':
                eligible_ids.add(row.get('candidate_id'))
                securities.add(row.get('security_id'))
            if stage == 'BREAKOUT_CONFIRMED':
                breakout_ids.add(row.get('candidate_id'))

    summary = {
        'contract': '36-entry-source-population-audit-v1',
        'canonical_v35_run_id': 34763920536,
        'source_observations': total,
        'stage_counts': dict(sorted(counts.items())),
        'canslim_eligible_observations': counts.get('CANSLIM_ELIGIBLE', 0),
        'canslim_eligible_unique_candidates': len({x for x in eligible_ids if x}),
        'canslim_eligible_unique_securities': len({x for x in securities if x}),
        'breakout_confirmed_observations': counts.get('BREAKOUT_CONFIRMED', 0),
        'breakout_confirmed_unique_candidates': len({x for x in breakout_ids if x}),
        'primary_variant_comparison_gate': (
            'OPEN' if counts.get('CANSLIM_ELIGIBLE', 0) > 0
            else 'BLOCKED_ON_ELIGIBLE_POPULATION'
        ),
        'performance_metrics_inspected': False,
        'governance_note': (
            'Do not widen the preregistered actionable population after observing the zero-source count. '
            'Any BREAKOUT_CONFIRMED-only study must be separately preregistered as diagnostic research.'
        ),
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
