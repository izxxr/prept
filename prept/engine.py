# Copyright (C) Izhar Ahmad 2025-2026

from __future__ import annotations

from typing import Callable, TYPE_CHECKING
from collections import OrderedDict
from prept.errors import PreptCLIError, EngineNotFound
from prept.cli import outputs

import importlib
import pathspec

if TYPE_CHECKING:
    from prept.context import GenerationContext

    ProcessorFunctionT = Callable[[GenerationContext], bool | None]

__all__ = (
    'GenerationEngine',
)

class GenerationEngine:
    """Engine for dynamic operations at generation time.

    This class provides a rich interface for manipulating the generation
    time behavior.

    .. versionadded:: 0.2.0
    """
    def __init__(self) -> None:
        self._file_processors: OrderedDict[str, list[ProcessorFunctionT]] = OrderedDict()
        self._spec = None

    @classmethod
    def _resolve(cls, spec: str) -> GenerationEngine:
        parts = spec.split(':')
        if len(parts) != 2:
            raise EngineNotFound(spec, 'invalid spec format')

        mod, obj = parts
        try:
            module = importlib.import_module(mod)
        except ImportError:
            raise EngineNotFound(spec, f'failed to import {mod}')

        engine = getattr(module, obj, None)
        if engine is None:
            raise EngineNotFound(spec, f'{obj} could not be resolved from {mod} module')
        if not isinstance(engine, GenerationEngine):
            raise EngineNotFound(spec, f'{obj} ({engine}) is not a GenerationEngine instance')

        engine._spec = spec
        return engine

    def _wrapped_call_processor(self, proc: ProcessorFunctionT, ctx: GenerationContext) -> bool:
        try:
            result = proc(ctx)
        except Exception as e:
            if isinstance(e, PreptCLIError):
                raise
            raise outputs.wrap_exception(e, f'In processing of {ctx.current_file.path!r}, the following error occured:') from None
        else:
            # If processor function does not return any value, default it to True.
            return True if result is None else result

    def _call_processors(self, path: str, ctx: GenerationContext) -> bool:
        spec = pathspec.PathSpec.from_lines('gitwildmatch', self._file_processors.keys())
        result = spec.check_file(path)

        if result.index is None:
            # No processors registered for this path, return True.
            return True

        processors = list(self._file_processors.values())[result.index]
        for proc in processors:
            if not self._wrapped_call_processor(proc, ctx):
                return False

        # Returns boolean indicating whether context file should be generated or not.
        return True

    def add_processor(self, path: str, proc_func: ProcessorFunctionT) -> None:
        """Registers a processor function for given path.

        Processor function must take :class:`GenerationContext` as the
        only parameter.

        Parameters
        ~~~~~~~~~~
        path: :class:`str`
            The path or gitignore-like pattern for which processor is being defined.
            Files at this path will be processed through this processor.
        proc_func:
            The processor function.
        """
        if path not in self._file_processors:
            self._file_processors[path] = []

        self._file_processors[path].append(proc_func)

    def get_processors(self, path: str) -> tuple[ProcessorFunctionT, ...]:
        """Get the processors registered for the given path.

        Returns a tuple of processor function objects.
        """
        if path not in self._file_processors:
            return ()

        return tuple(self._file_processors[path])

    def remove_processor(self, path: str, proc_func: ProcessorFunctionT) -> None:
        """Registers a processor function for given path.

        Processor function must take :class:`GenerationContext` as the
        only parameter.

        ValueError is raised if no processor is registered for the given path.

        Parameters
        ~~~~~~~~~~
        path: :class:`str`
            The path or gitignore-like pattern for which processor is being defined.
            Files at this path will be processed through this processor.
        proc_func:
            The processor function.
        """
        try:
            self._file_processors[path].remove(proc_func)
        except (ValueError, KeyError):
            raise ValueError('No processor is registered for this path') from None

    def clear_processors(self, path: str) -> None:
        """Removes all processors for the given path."""
        if path not in self._file_processors:
            return

        del self._file_processors[path]

    def processor(self, path: str) -> Callable[[ProcessorFunctionT], ProcessorFunctionT]:
        """Decorator interface for :meth:`.add_processor`

        This decorator takes the same parameters as :meth:`.add_processor` method
        and the decorated function must take :class:`GenerationContext` as only
        parameter.
        """
        def __wrapper(func: ProcessorFunctionT):
            self.add_processor(path, func)
            return func

        return __wrapper
