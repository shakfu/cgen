"""
CGen C Code Generator

Integrated and extended version of cfile specifically for CGen intelligence layer.
Provides enhanced C code generation with intelligence-aware optimizations.
"""

from .core import *
from .factory import CGenFactory
from .writer import CGenWriter
from .style import StyleOptions

# Aliases for convenience
Define = DefineDirective
Include = IncludeDirective
SysInclude = IncludeDirective

__all__ = [
    # Core elements
    'Element', 'Sequence', 'Declaration', 'Statement', 'Block',
    'Function', 'Variable', 'FunctionCall', 'Type', 'DefineDirective',
    'IncludeDirective', 'LineComment', 'BlockComment',

    # Aliases
    'Define', 'Include', 'SysInclude',

    # Factory and writer
    'CGenFactory', 'CGenWriter', 'StyleOptions'
]