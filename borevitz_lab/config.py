from attrs import frozen, field, Factory as F
from typing_extensions import Self
from os.path import expanduser
from tabulate import tabulate
from typing import Optional
from os.path import exists
from os import makedirs
from json import load
import os

build_from_out_dir = F(lambda s: f'{s.out_dir}/queries.json', takes_self=True)
_out = expanduser('~/Documents/BorevitzLab-Outputs')
_tmp = expanduser('~/Downloads/BorevitzLab-Tmp')
@frozen
class Config:
    out_dir: str = _out
    tmp_dir: str = _tmp
    hash_file: str = field(default=build_from_out_dir)
    email: Optional[str] = None
    tern_api_key: Optional[str] = None

    def __post_init__(s: Self):
        makedirs(s.out_dir, exist_ok=True)
        makedirs(s.tmp_dir, exist_ok=True)

    def __str__(s: Self):
        return tabulate(
            [
                ['out_dir', s.out_dir],
                ['tmp_dir', s.tmp_dir],
                ['hash_file', s.hash_file],
                ['email', s.email if bool(s.email) else 'NOT SET'],
                ['tern_api_key', 'SET' if bool(s.tern_api_key) else 'NOT SET']
            ]
        )

def _env(*names, default=None):
    """First set environment variable among names (legacy PADDOCKTS_* last)."""
    for name in names:
        value = os.getenv(name)
        if value is not None:
            return value
    return default

_out = _env("BOREVITZ_LAB_OUTDIR", "PADDOCKTS_OUTDIR", default=_out)
_tmp = _env("BOREVITZ_LAB_TMPDIR", "PADDOCKTS_TMPDIR", default=_tmp)
_email = _env("BOREVITZ_LAB_EMAIL", "PADDOCKTS_EMAIL") # default None
_tern_api_key = _env("BOREVITZ_LAB_TERN_KEY", "PADDOCKTS_TERN_KEY") # default None
_default = Config(_out, _tmp, email=_email, tern_api_key=_tern_api_key)

# First existing config file wins: env override, then the new name,
# then the legacy PaddockTS name.
_confpaths = [
    _env("BOREVITZ_LAB_CONFIG", "PADDOCKTS_CONFIG"),
    os.path.expanduser('~/.config/BorevitzLab.json'),
    os.path.expanduser('~/.config/PaddockTS.json'),
]
confpath = next((p for p in _confpaths if p and exists(p)), None)
config = Config(**load(open(confpath))) if confpath else _default


if __name__ == '__main__':
    _config = Config(_out, _tmp)
    print(_config)
