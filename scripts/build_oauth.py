"""Build only reviewed OAuth information sources; never deploy or use credentials."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'oauth-public'
OUTPUT = ROOT / 'dist' / 'oauth-public'
FILES = frozenset({
    'index.html', 'gbp-automation/index.html', 'privacy/index.html',
    '404.html', 'assets/site.css', '_headers', 'robots.txt',
})


def check_source(source):
    if source.is_symlink():
        raise ValueError('SOURCE_SYMLINK')
    entries = list(source.rglob('*'))
    if any(p.is_symlink() for p in entries):
        raise ValueError('SOURCE_SYMLINK')
    actual = {p.relative_to(source).as_posix() for p in entries if p.is_file()}
    if actual != FILES:
        raise ValueError('PUBLIC_FILE_ALLOWLIST_MISMATCH: ' + repr(sorted(actual ^ FILES)))


def build(source=SOURCE, output=OUTPUT):
    check_source(source)
    # The destination is deliberately fixed; no CLI path can target existing HP files.
    if output != OUTPUT:
        raise ValueError('OUTPUT_MUST_BE_FIXED')
    if output.is_symlink() or output.parent.is_symlink():
        raise ValueError('OUTPUT_SYMLINK')
    if output.exists():
        shutil.rmtree(output)
    for name in sorted(FILES):
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, target)
    print('Built 7 allowlisted files in dist/oauth-public (draft, no deployment).')


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 1:
        raise SystemExit('No release/deploy mode. Resolve docs/phase-a-release-checklist.md first.')
    build()
