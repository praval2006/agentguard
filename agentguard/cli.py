"""Explicit-input verification CLI; core components own validation and verdicts."""
import argparse
import json
from pathlib import Path
import sys

from .acceptance import run_acceptance
from .grounding import ground_scenarios
from .planner import MAX_TEXT_CHARS, plan_acceptance
from .providers.openai_provider import OpenAIProvider
from .reviewed_workflow import (prepare_review, resume_reviewed, validate_review,
                                MAX_ARTIFACT_CHARS)
from .acceptance_contract import build_contract
from .acceptance_report import build_acceptance_report, format_acceptance_report, report_json

EXIT_CODES = {'PASS': 0, 'FAIL': 1, 'UNVERIFIED': 2}


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


def _read_text(path):
    with Path(path).open(encoding='utf-8') as stream:
        text = stream.read(MAX_TEXT_CHARS + 1)
    if not text.strip():
        raise ValueError('Empty input')
    if len(text) > MAX_TEXT_CHARS:
        raise ValueError('Input exceeds character limit')
    return text


def _display(value):
    # Escape terminal control sequences in model/evidence strings.
    return json.dumps(value, ensure_ascii=True, allow_nan=False)


def _result_lines(envelope, indent=''):
    result = envelope['result']
    lines = [f"{indent}[{result['verdict']}] {_display(result['name'])}"]
    for assertion in result['assertions']:
        details = [assertion['type']]
        for key in ('path', 'expected', 'observed', 'observed_type',
                    'expected_truncated', 'observed_truncated'):
            if key in assertion:
                details.append(f'{key}={_display(assertion[key])}')
        lines.append(f"{indent}  Evidence [{assertion['verdict']}]: " + '; '.join(details))
        if assertion.get('reason'):
            lines.append(f"{indent}    Reason: {_display(assertion['reason'])}")
    for key in ('expected', 'observed', 'check_id', 'coverage_id'):
        if key in result:
            lines.append(f'{indent}  {key}: {_display(result[key])}')
    if result.get('reason'):
        lines.append(f"{indent}  Reason: {_display(result['reason'])}")
    execution_reason = envelope.get('execution', {}).get('reason')
    if execution_reason and execution_reason != result.get('reason'):
        lines.append(f'{indent}  Execution: {_display(execution_reason)}')
    for child in result.get('children', []):
        lines.extend(_result_lines(child, indent + '  '))
    return lines


def format_report(task_path, plan, grounded, result, *, show_reasoning=False):
    lines = ['AgentGuard', '==========', '', 'Task:', str(_display(task_path)), '',
             'Acceptance scenarios:', str(len(grounded)), '']
    if show_reasoning:
        for key, title in (('explicit_requirements', 'Explicit requirements'),
                           ('inferred_behaviors', 'Inferred behaviors'),
                           ('ambiguities', 'Ambiguities')):
            lines.append(title + ':')
            lines.extend('  ' + _display(item) for item in plan[key])
            if not plan[key]:
                lines.append('  (none)')
        lines.append('Grounded action types:')
        lines.extend(f"  {_display(s['name'])}: {s['action']['type']}" for s in grounded)
        lines.append('')
    for envelope in result['results']:
        lines.extend(_result_lines(envelope))
    lines.extend(['', 'Overall: ' + result['verdict']])
    return '\n'.join(lines)


def _read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key')
            result[key] = value
        return result
    def constant(value):
        raise ValueError('Nonfinite JSON value')
    with Path(path).open(encoding='utf-8') as stream:
        text = stream.read(MAX_ARTIFACT_CHARS + 1)
    if len(text) > MAX_ARTIFACT_CHARS:
        raise ValueError('Artifact exceeds input bound')
    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


def format_review(artifact, contract=None):
    """Display model interpretation distinctly from human decisions and evidence."""
    plan = artifact['proposal']
    reviews = artifact['reviews'] if contract is None else contract['reviews']
    lines = ['AgentGuard reviewed workflow', 'Proposal: ' + artifact['revision']]
    for field, title in (('explicit_requirements', 'EXPLICIT'),
                         ('inferred_behaviors', 'AGENTGUARD SUGGESTION'),
                         ('ambiguities', 'AMBIGUITY')):
        lines.append(title + ' (planner interpretation):')
        lines.extend('  ' + _display(text) for text in plan[field])
        if not plan[field]:
            lines.append('  (none)')
    lines.append('SCENARIO REVIEW (no requirement-list mapping implied):')
    for item in reviews:
        label = 'EXPLICIT' if item['source'] == 'explicit' else 'AGENTGUARD SUGGESTION'
        state = item['review_state'] or 'INCLUDED'
        lines.extend([f"{label} / {state} / {item['scenario_id']}",
                      '  Name: ' + _display(item['name']),
                      '  Behavior: ' + _display(item['behavior']),
                      '  Model rationale (not verified evidence): ' + _display(item['reason'])])
    return '\n'.join(lines)


def _reviewed_main(args):
    stage = 'reviewed context input'
    try:
        context = _read_text(args.context)
        if args.command == 'review':
            stage = 'review task input'
            task = _read_text(args.task)
            stage = 'review output path'
            if Path(args.output).exists():
                raise ValueError('Refusing to overwrite a review')
            stage = 'review provider configuration'
            provider = OpenAIProvider()
            stage = 'planning or review validation'
            artifact = prepare_review(task, context, reasoning_provider=provider)
            stage = 'saving review artifact'
            with Path(args.output).open('x', encoding='utf-8') as stream:
                json.dump(artifact, stream, ensure_ascii=True, allow_nan=False, indent=2)
                stream.write('\n')
            print(format_review(artifact))
            print('Review saved. Stopped before grounding or execution.')
            return 0
        stage = 'review artifact and human decisions'
        artifact = _read_json(args.review)
        decisions = _read_json(args.decisions)
        proposal = validate_review(artifact, context)
        if type(decisions) is not list:
            raise ValueError('Decision file must contain a list')
        build_contract(proposal, decisions)
        stage = 'report configuration'
        task_text = _read_text(args.task) if args.task else None
        if args.report_json and Path(args.report_json).exists():
            raise ValueError('Refusing to overwrite a report')
        stage = 'reviewed provider configuration'
        provider = OpenAIProvider()
        stage = 'reviewed grounding or acceptance execution'
        outcome = resume_reviewed(artifact, decisions, context, grounding_provider=provider,
                                  base_url=args.base_url)
        stage = 'acceptance report construction'
        report = build_acceptance_report(outcome, task_text=task_text)
        rendered = format_acceptance_report(report)
        if args.report_json:
            stage = 'saving acceptance report'
            serialized = report_json(report)
            with Path(args.report_json).open('x', encoding='utf-8') as stream:
                stream.write(serialized)
        print(rendered)
        return EXIT_CODES[outcome['verification']['verdict']]
    except Exception:
        print(f'AgentGuard error: {stage} failed. No acceptance verdict reported.', file=sys.stderr)
        return 3


def main(argv=None):
    parser = _Parser(prog='agentguard', description='Verify explicitly supplied task and context using existing AgentGuard policies.')
    commands = parser.add_subparsers(dest='command', required=True)
    verify = commands.add_parser('verify', help='Plan, ground, then execute acceptance checks (two model requests).')
    verify.add_argument('--task', required=True, help='UTF-8 task file, nonblank, at most 32000 characters')
    verify.add_argument('--context', required=True, help='Explicit UTF-8 context file, nonblank, at most 32000 characters')
    verify.add_argument('--base-url', help='HTTP target; existing executor policy applies')
    verify.add_argument('--show-reasoning', action='store_true', help='Show structured requirements, ambiguities and action types')
    review = commands.add_parser('review', help='Prepare human review; planner only, no verification.')
    review.add_argument('--task', required=True)
    review.add_argument('--context', required=True)
    review.add_argument('--output', required=True, help='New review JSON file; refuses overwrite')
    reviewed = commands.add_parser('verify-reviewed', help='Verify explicit and human-accepted scenarios only.')
    reviewed.add_argument('--review', required=True)
    reviewed.add_argument('--decisions', required=True, help='JSON list of Phase-1 human decisions; [] is valid')
    reviewed.add_argument('--context', required=True)
    reviewed.add_argument('--base-url')
    reviewed.add_argument('--report-json', help='New bounded acceptance report JSON file; refuses overwrite')
    reviewed.add_argument('--task', help='Optional original task text for reporting; not revision-bound')
    stage = 'arguments'
    try:
        args = parser.parse_args(argv)
        if args.command != 'verify':
            return _reviewed_main(args)
        stage = 'task input (requires readable, nonblank UTF-8 text within 32000 characters)'
        task = _read_text(args.task)
        stage = 'context input (requires readable, nonblank UTF-8 text within 32000 characters)'
        context = _read_text(args.context)
        stage = 'provider configuration (check OPENAI_API_KEY and AGENTGUARD_MODEL)'
        provider = OpenAIProvider()
        stage = 'planning or planner validation'
        plan = plan_acceptance(task, context, reasoning_provider=provider)
        stage = 'grounding or grounding validation'
        grounded = ground_scenarios(plan, context, grounding_provider=provider)
        stage = 'acceptance execution'
        result = run_acceptance(grounded, base_url=args.base_url)
        stage = 'result formatting'
        code = EXIT_CODES[result['verdict']]
        report = format_report(args.task, plan, grounded, result, show_reasoning=args.show_reasoning)
        print(report)
        return code
    except Exception:
        # Exception text may contain model output, application data or credentials.
        print(f'AgentGuard error: {stage} failed. No acceptance verdict reported.', file=sys.stderr)
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
