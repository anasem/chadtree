from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from dataclasses import dataclass
from json import dump, load
from os import makedirs
from os.path import dirname
from typing import Any, Callable, Optional, TypeVar, cast

from .consts import folder_mode

T = TypeVar("T")


def merge(ds1: Any, ds2: Any, replace: bool = False) -> Any:
    if type(ds1) is dict and type(ds2) is dict:
        append = {k: merge(ds1.get(k), v, replace) for k, v in ds2.items()}
        return {**ds1, **append}
    if type(ds1) is list and type(ds2) is list:
        if replace:
            return ds2
        else:
            return [*ds1, *ds2]
    else:
        return ds2


def merge_all(ds1: Any, *dss: Any, replace: bool = False) -> Any:
    res = ds1
    for ds2 in dss:
        res = merge(res, ds2, replace=replace)
    return res


def or_else(thing: Optional[T], default: T) -> T:
    return default if thing is None else thing


def constantly(val: T) -> Callable[..., T]:
    def ret(*args: Any, **kwargs: Any) -> T:
        return val

    return ret


@dataclass(frozen=True)
class ProcReturn:
    code: int
    out: str
    err: str


async def call(prog: str, *args: str) -> ProcReturn:
    proc = await create_subprocess_exec(prog, *args, stdout=PIPE, stderr=PIPE)
    stdout, stderr = await proc.communicate()
    code = cast(int, proc.returncode)
    return ProcReturn(code=code, out=stdout.decode(), err=stderr.decode())


def load_json(path: str) -> Any:
    with open(path) as fd:
        return load(fd)


def dump_json(path: str, json: Any) -> None:
    parent = dirname(path)
    makedirs(parent, mode=folder_mode, exist_ok=True)
    with open(path, "w") as fd:
        return dump(json, fd, ensure_ascii=False, indent=2)
