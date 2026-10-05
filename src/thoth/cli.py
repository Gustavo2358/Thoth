from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from thoth.artifacts import export
from thoth.embeddings import LocalEmbedder
from thoth.llm import ManualChatGPTAdapter, OpenAIAdapter, PendingResponse
from thoth.pipeline import ingest, policy_from_file, reprocess
from thoth.storage import Store
from thoth.teaching import teaching_state


def main(argv=None):
    parser = argparse.ArgumentParser(prog='thoth', description='Compile learning conversations into the next teacher prompt')
    parser.add_argument('--db', type=Path, default=Path('data/thoth.db'))
    parser.add_argument('--artifacts', type=Path, default=Path('artifacts'))
    parser.add_argument('--policy', type=Path)
    sub = parser.add_subparsers(dest='command', required=True)
    command = sub.add_parser('ingest')
    command.add_argument('file', type=Path)
    command.add_argument('--date', default=date.today().isoformat(), help='Actual session date; default today')
    command.add_argument('--reprocess', action='store_true', help='Replay ALL stored conversations atomically with this exchange')
    command.add_argument('--provider', choices=['manual', 'openai'], default='manual')
    command.add_argument('--model', default='ChatGPT / unspecified')
    command.add_argument('--exchange', type=Path, default=Path('data/exchange'))
    command.add_argument('--interactive', action='store_true')
    for name in ['state', 'patterns', 'prepare', 'teaching']:
        sub.add_parser(name)
    command = sub.add_parser('goals')
    actions = command.add_subparsers(dest='goal_action')
    actions.add_parser('add').add_argument('text')
    actions.add_parser('remove').add_argument('id')
    command = sub.add_parser('import', help='Import original internal LLM responses named <request-hash>.txt')
    command.add_argument('directory', type=Path)
    command.add_argument('--exchange', type=Path, default=Path('data/exchange'))
    command.add_argument('--model', default='ChatGPT / unspecified')
    args = parser.parse_args(argv)
    try:
        if args.command == 'import':
            print(ManualChatGPTAdapter(args.exchange, args.model).import_responses(args.directory))
            return 0
        policy = policy_from_file(args.policy)
        with Store(args.db) as store:
            if args.command == 'ingest':
                raw = args.file.read_bytes().decode('utf-8')
                date.fromisoformat(args.date)
                llm = ManualChatGPTAdapter(args.exchange, args.model, args.interactive) if args.provider == 'manual' else OpenAIAdapter(args.model)
                if args.reprocess:
                    if not store.existing(raw, args.date):
                        raise ValueError('Reprocessing requires an existing unchanged conversation and its original date')
                    result = reprocess(store, LocalEmbedder(), llm, policy)
                else:
                    result = ingest(raw, args.date, store, LocalEmbedder(), llm, policy)
                export(args.artifacts, store, policy)
                print(json.dumps(result))
                return 0
            if args.command == 'goals':
                with store.db:
                    if args.goal_action == 'add':
                        store.add_goal(args.text)
                    elif args.goal_action == 'remove':
                        if not store.db.execute('DELETE FROM goals WHERE id=?', (args.id,)).rowcount:
                            raise ValueError('Unknown goal ID')
            state = export(args.artifacts, store, policy)
            if args.command == 'prepare':
                # stdout is only the pasteable artifact, so redirecting works.
                print((args.artifacts / 'teacher-prompt.md').read_text(), end='')
            elif args.command == 'patterns':
                print(json.dumps(state['patterns'], indent=2, ensure_ascii=False))
            elif args.command == 'teaching':
                print(json.dumps(teaching_state(store), indent=2, ensure_ascii=False))
            elif args.command == 'goals':
                print(json.dumps(store.goals(), indent=2, ensure_ascii=False))
            else:
                print((args.artifacts / 'learner-state.md').read_text())
        return 0
    except PendingResponse as error:
        print('Pending: ' + str(error), file=sys.stderr)
        return 2
    except (ValueError, OSError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
