import inspect
import pkgutil
from importlib import import_module
from pathlib import Path
import logging
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type

from pkg_resources import iter_entry_points

from app.db_engine_specs.base import BaseEngineSpec
from app.db_engine_specs.postgres import PostgresqlEngineSpec

logger = logging.getLogger(__name__)


def is_engine_spec(attr: Any) -> bool:
    return (
        inspect.isclass(attr)
        and issubclass(attr, BaseEngineSpec)
        and attr != BaseEngineSpec
    )


def get_engine_specs() -> Dict[str, Type[BaseEngineSpec]]:
    engine_specs = load_engine_specs()

    # build map from name/alias -> spec
    engine_specs_map: Dict[str, Type[BaseEngineSpec]] = {}
    for engine_spec in engine_specs:
        names = [engine_spec.engine]
        if engine_spec.engine_aliases:
            names.extend(engine_spec.engine_aliases)

        for name in names:
            engine_specs_map[name] = engine_spec

    return engine_specs_map


def load_engine_specs() -> List[Type[BaseEngineSpec]]:
    engine_specs: List[Type[BaseEngineSpec]] = []

    # load standard engines
    db_engine_spec_dir = str(Path(__file__).parent)
    for module_info in pkgutil.iter_modules([db_engine_spec_dir], prefix="."):
        module = import_module(module_info.name, package=__name__)
        engine_specs.extend(
            getattr(module, attr)
            for attr in module.__dict__
            if is_engine_spec(getattr(module, attr))
        )

    # load additional engines from external modules
    for ep in iter_entry_points("app.db_engine_specs"):
        try:
            engine_spec = ep.load()
        except Exception:  # pylint: disable=broad-except
            logger.warning("Unable to load DB engine spec: %s", engine_spec)
            continue
        engine_specs.append(engine_spec)

    return engine_specs
