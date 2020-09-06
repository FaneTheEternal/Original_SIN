try:
    from .local_settings import LocalSettings as Settings
except ImportError:
    from .global_settings import GlobalSettings as Settings

globals().update(Settings().get_settings())
