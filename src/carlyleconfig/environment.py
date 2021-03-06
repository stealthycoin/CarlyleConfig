from dataclasses import dataclass, field
from typing import List

from carlyleconfig.plugins.base import BasePlugin
from carlyleconfig.plugins.envvar import EnvVarPlugin
from carlyleconfig.plugins.constant import ConstantPlugin
from carlyleconfig.plugins.fileparse import FilePlugin
from carlyleconfig.key import ConfigKey


@dataclass
class ConfigEnvironment:
    default_plugins: List[BasePlugin] = field(
        default_factory=lambda: [
            EnvVarPlugin(),
            ConstantPlugin(),
            FilePlugin(),
        ]
    )
    plugins: List[BasePlugin] = field(default_factory=lambda: [])

    def field(self, sensitive=False) -> ConfigKey:
        key = ConfigKey(sensitive=sensitive)
        self._inject_plugin_methods(self.default_plugins, key)
        self._inject_plugin_methods(self.plugins, key)
        return key

    def _inject_plugin_methods(self, plugins: List[BasePlugin], key: ConfigKey):
        for plugin in plugins:
            plugin.inject_factory_method(key)
