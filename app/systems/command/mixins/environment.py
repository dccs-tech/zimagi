from django.conf import settings

from data.environment.models import Environment
from data.state.models import State
from .base import DataMixin


class EnvironmentMixin(DataMixin):

    schema = {
        'state': {
            'model': State
        },
        'env': {
            'full_name': 'environment',
            'plural': 'environments',
            'model': Environment,
            'provider': True,
            'name_default': 'curr_env_name',
            'system_fields': (
                'type',
                'config',
                'variables',
                'state_config',
                'created',
                'updated'
            )
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.facade_index['00_env'] = self._env
        self.facade_index['01_state'] = self._state


    @property
    def curr_env_name(self):
        return self._env.get_env()


    def parse_env_repo(self, optional = False, help_text = 'environment runtime repository'):
        self.parse_variable('repo', optional, str, help_text,
            value_label = 'HOST',
            default = settings.DEFAULT_RUNTIME_REPO
        )

    @property
    def env_repo(self):
        return self.options.get('repo', None)

    def parse_env_image(self, optional = False, help_text = 'environment runtime image ({})'.format(settings.DEFAULT_RUNTIME_IMAGE)):
        self.parse_variable('image', optional, str, help_text,
            value_label = 'REFERENCE',
            default = settings.DEFAULT_RUNTIME_IMAGE
        )

    @property
    def env_image(self):
        image = self.options.get('image', None)
        if not image:
            image = settings.DEFAULT_RUNTIME_IMAGE
        return image


    def get_env(self, name = None):
        if not name:
            name = self._env.get_env()
        return self.get_instance(self._env, name, required = False)

    def set_env(self, name = None, repo = None, image = None):
        self._env.set_env(name, repo, image)
        self.success("Successfully updated current environment")

    def delete_env(self):
        self._state.clear()
        self._env.delete_env()
        self.success("Successfully removed environment")


    def get_state(self, name, default = None):
        instance = self.get_instance(self._state, name, required = False)
        if instance:
            return instance.value
        return default

    def set_state(self, name, value = None):
        self._state.store(name, value = value)

    def delete_state(self, name = None):
        if not self._state.delete(name):
            self.error("Environment state change failed")