import os

try:
    from .local_settings import LocalSettings as Settings
except ImportError:
    if 'LOAD_DJANGO_SETTINGS' in os.environ:
        from .global_settings import EnvironmentLoadSettings as Settings
    else:
        from .global_settings import GlobalSettings as Settings

globals().update(Settings().get_settings())
