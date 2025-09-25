from dataclasses import dataclass, field

from carlyleconfig.plugins.base import BasePlugin
from carlyleconfig.plugins.envvar import EnvVarPlugin
from carlyleconfig.plugins.constant import ConstantPlugin
from carlyleconfig.plugins.fileparse import FilePlugin
from carlyleconfig.plugins.argparse import ArgParsePlugin
from carlyleconfig.plugins.default_factory import DefaultFactoryPlugin
from carlyleconfig.key import ConfigKey


@dataclass
class ConfigEnvironment:
    """Collection of plugins to derive configuration values from.

    By default ``carlyleconfig.derive`` is a pre-configured ConfigEnvironment
    with all of the following plugins enabled:

    * EnvVarPlugin
    * ConstantPlugin
    * FilePlugin
    * ArgParsePlugin
    * DefaultFactoryPlugin"""

    plugins: dict[str, BasePlugin] = field(
        default_factory=lambda: {
            EnvVarPlugin.name(): EnvVarPlugin(),
            ConstantPlugin.name(): ConstantPlugin(),
            FilePlugin.name(): FilePlugin(),
            ArgParsePlugin.name(): ArgParsePlugin(update_help=True),
            DefaultFactoryPlugin.name(): DefaultFactoryPlugin(),
        }
    )

    def field(self, sensitive: bool = False) -> ConfigKey:
        """Create a ConfigKey field.

        :param sensitive: Setting this to true causes the value to be
        replaced with ***** when getting a __repr__ of the
        config object.
        :type sensitive: bool
        """
        key = ConfigKey(sensitive=sensitive)
        self._inject_plugin_methods(self.plugins, key)
        return key

    def get_plugin(self, plugin: BasePlugin) -> BasePlugin:
        """Get a plugin from the environment."""
        return self.plugins[plugin.name()]

    def add_plugin(self, plugin: BasePlugin) -> None:
        """Add a plugin to the environment.

        If another plugin of the same class already exists it
        will be replaced.
        """
        self.plugins[plugin.name()] = plugin

    def _inject_plugin_methods(
        self, plugins: dict[str, BasePlugin], key: ConfigKey
    ) -> None:
        for plugin in plugins.values():
            plugin.inject_factory_method(key)
