try:
    from .local_settingsq import LocalSettings as Settings
except ImportError:
    from Original_sin.global_settings import GlobalSettings as Settings

globals().update(Settings().get_settings())
