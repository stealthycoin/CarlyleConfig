Plugins
=======

ArgParsePlugin
--------------


Plugin to load configuration values from command line arguments.

All of the arguments will be proxied directly to ``add_argument``.


.. py:function:: from_argparse

   :param name: Name of the parameter. This is forwarded directly to argparse.
   :type name: str

   :param *kwargs: *kwargs that are proxied directly to argparses' ``add_argument``.
   :type *kwargs: Dict[str, Any]


.. py:function:: bind_parser

   Bind the plugin to an instance of an ``argparse.ArgumentParser``. This will
   inject all of the arguments by proxying all of the arguments to ``add_argument``.

   Once this method has been called on an argument parser it intercept the ``parse_args()``
   and obtain a copy of the parsed arguments.

   :param parser: ArgumentParser instance to bind this plugin to.
   :type parser: ArgumentParser


SecretsManagerPlugin
--------------------

Plugin to load configuration values from AWS Secrets Manager.

This plugin must be created manually and added to the `ConfigEnvironment``.

.. py:function:: __init__

   Initialize a secretsmanager plugin.

   :param client: A boto3 secrets manager client. If not provided a client will be
		  created for you using ``boto3.client("secretsmanager")``.
   :type client: Optional[SecretFetcher]

.. py:function:: from_secrets_manager

   Load a configuration value from AWS Secrets Manager.

   :param name: SecretID of the AWS Secrets Manager secret to load.
   :type name: str

   :param key: Key to load from the secret. If not provided the full
	       value of the secret is used.
   :type key: Optional[str]

   :param cast: Optional function to convert the loaded value into another
		python data type. If not provided then the identity function
		is used and the value is taken as-is.
   :type cast: Optional[[Callable[str], Any]]

   :param require_key: Boolean to ensure that the secret loaded from SecretsManager has
		       the ``key``. This allows you to error out in teh case where the
		       secret exists but is incorrectly formatted by missing a required
		       key.
   :type require_key: bool


ConstantPlugin
--------------

Plugin to load configuration from a constant value.

.. py:function:: from_constant

   Load a config value from a constant value.
   This is normally used to provide a default value if no other plugins
   loaded a value.

   :param value: The value to return.
   :type value: Any


EnvVarPlugin
------------

Plugin to load configuration from environment variables.

.. py:function:: from_env_var

   :param name: Name of the environment variable to load.
   :type name: str

   :param cast: Optional function to convert the loaded env var into another
		python data type. If not provided then the env var will be
		loaded as a ``str``.
   :type cast: Optional[[Callable[str], Any]]


FilePlugin
----------

Plugin to load values from configuration files.

.. py:function:: from_file

   Load a config value from a file.

   :param filename: Path to the file to load.
   :type filename: str

   :param parser: Parsing function to be executed on the file contents.
		  By default this is the identity function which will return
		  the entire contents of the file unaltered.
   :type parser: Callable[[str], Any]

   :param selector: Selection function that operates on the output of the parser.
		    Once the file is parsed it is passed to the selector function
		    to select a value out of the parsed data. By default this is
		    the identity function which will return the output of the
		    parser function unaltered.
   :type selector: Callable[[Any], Any]


.. py:function:: from_json_file

   Load a config value from a JSON formatted file.

   :param filename: Path to the JSON file to load.
   :type filename: str

   :param jmespath: JMESPath expression to run on the file contents. The result
		    will be used as the loaded config value.
   :type jmespath: Optional[str]


SSMPlugin
---------

Load a config value from AWS Systems Manager Parameter Store.

This plugin must be created manually and added to the `ConfigEnvironment``.


.. py:function:: __init__

   Initialize a SSM plugin.

   :param prefix: Prefix to add before parameter names.
   :type prefix: str

   :param client: A boto3 ssm client. If not provided a client will be
		  created for you using ``boto3.client("ssm")``.
   :type client: Optional[ParameterFetcher]


.. py:function:: from_ssm_parameter

   :param name: Name of the parameter from parameter store to load. This is combined with
		the prefix from the plugin to get the full name of the parameter.
   :type name: str

   :param cast: Optional function to convert the loaded parameter into another
		python data type. If not provided then the parameter will be
		loaded as a ``str``.
   :type cast: Optional[[Callable[str], Any]]


    .. code-block::
       :caption: example

       from carlyleconfig import deriveconfig, derive
       from carlyleconfig.plugins import SSMPlugin
       derive.add_plugin(SSMPlugin(prefix="/app/"))

       @deriveconfig
       class Config:
	   # Password will be loaded from SSM Parameter `/app/password`
	   password: str = (
	       derive.field(sensitive=True)
	       .from_ssm_parameter("password")
	   )
