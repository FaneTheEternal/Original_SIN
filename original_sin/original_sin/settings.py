import os
import logging

logger = logging.getLogger(__name__)


try:
    from .local_settings import LocalSettings as Settings
    logger.warning('Loaded local settings')
except ImportError:
    if 'LOAD_DJANGO_SETTINGS' in os.environ:
        from .global_settings import EnvironmentLoadSettings as Settings
        logger.warning('Loaded env settings')
    else:
        from .global_settings import GlobalSettings as Settings
        logger.warning('Loaded default settings')

globals().update(Settings().get_settings())
