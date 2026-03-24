from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def test_required_files_exist():
    required = [
        BASE / 'instruction.md',
        BASE / 'task.toml',
        BASE / 'environment' / 'Dockerfile',
        BASE / 'environment' / 'skill_config.toml',
        BASE / 'environment' / 'io_config.json',
        BASE / 'solution' / 'solve.sh',
        BASE / 'solution' / 'solution.md',
        BASE / 'test' / 'test.sh',
        BASE / 'test' / 'test_state.py',
    ]
    for p in required:
        assert p.exists(), f'Missing file: {p}'


def test_instruction_has_problem_and_requirements():
    text = (BASE / 'instruction.md').read_text(encoding='utf-8')
    assert '问题' in text
    assert '开发要求' in text
    assert '验收标准' in text


def test_task_toml_has_core_sections():
    text = (BASE / 'task.toml').read_text(encoding='utf-8')
    for key in ['[metadata]', '[verifier]', '[agent]', '[environment]']:
        assert key in text

