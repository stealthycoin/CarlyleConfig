from dataclasses import dataclass, field
from typing import List, ClassVar, Dict

from carlyleconfig.plugins.base import BasePlugin
from carlyleconfig.plugins.envvar import EnvVarPlugin
from carlyleconfig.plugins.constant import ConstantPlugin
from carlyleconfig.plugins.fileparse import FilePlugin
from carlyleconfig.plugins.argparse import ArgParsePlugin
from carlyleconfig.plugins.ssmplugin import SSMPlugin
from carlyleconfig.plugins.awssecretsmanager import SecretsManagerPlugin
from carlyleconfig.key import ConfigKey


@dataclass
class ConfigEnvironment:

    plugins: Dict[str, BasePlugin] = field(
        default_factory=lambda: {
            EnvVarPlugin.name(): EnvVarPlugin(),
            ConstantPlugin.name(): ConstantPlugin(),
            FilePlugin.name(): FilePlugin(),
            ArgParsePlugin.name(): ArgParsePlugin(update_help=True),
        }
    )

    def field(self, sensitive=False) -> ConfigKey:
        key = ConfigKey(sensitive=sensitive)
        self._inject_plugin_methods(self.plugins, key)
        return key

    def get_plugin(self, plugin: BasePlugin) -> BasePlugin:
        return self.plugins[plugin.name()]

    def add_plugin(self, plugin: BasePlugin):
        self.plugins[plugin.name()] = plugin

    def _inject_plugin_methods(self, plugins: Dict[str, BasePlugin], key: ConfigKey):
        for plugin in plugins.values():
            plugin.inject_factory_method(key)
