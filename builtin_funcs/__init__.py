import os
from glob import glob
from importlib import import_module

from .base import BuiltInFuncs  # noqa

names = os.path.join(os.path.dirname(__file__), '*.py')
for filename in glob(names):
    filename = filename.split('/')[-1]
    model = filename.split('.')[0]
    if model not in ('__init__', 'base'):
        import_module('.{}'.format(model), 'builtin_funcs')
