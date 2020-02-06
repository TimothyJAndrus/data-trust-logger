import os
import json

class ConfigurationError(Exception):
    pass


class Configuration(object):
    def find_json_config_file(self):
        """Find JSON configuration file.
        Locate the JSON configuration relative to the application path.
        Returns:
            str: Configuration file.
        Raises:
            ConfigurationError: If the configuration file cannot be found.
        """

        absolute_path = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(absolute_path, 'config.json')

        if os.path.exists(config_file) and os.path.isfile(config_file):
            return config_file
        else:
            raise ConfigurationError(
                'Cannot find configuration file in path {}.'.format(absolute_path))

    def load_json_config(self, config_file: str):
        """Load application configuration from JSON file.
        Args:
            config_file (str): The path and name of the configuration file to load.
        Returns:
            dict: Configuration object.
        Raises:
            ConfigurationError: If the configuration file doesn't exist or
                cannot be loaded because of a syntax error.
        """

        if not os.path.exists(config_file) or not os.path.isfile(config_file):
            raise ConfigurationError(
                'Error loading configuration file {}.'.format(config_file))

        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
            return data
        except Exception:
            raise ConfigurationError(
                'Failed to load configuration file {}. Please check the configuration file.'.format(config_file))

    def from_json(self, environment='development'):
        """Load application configuration from JSON object based on the configuration type.
        Args:
            environment (str): The environment to load.
        Raises:
            ConfigurationError: If the JSON configuration cannot be loaded.
        """

        config_file = self.find_json_config_file()
        data = self.load_json_config(config_file)
        if environment in data.keys():
            fields = data[environment]
            try:
                self.dr_url = fields['data_resources']['dr_url']
                self.dr_psql_user = fields['data_resources']['dr_psql_user']
                self.dr_psql_password = fields['data_resources']['dr_psql_password']
                self.dr_psql_hostname = fields['data_resources']['dr_psql_hostname']
                self.dr_psql_port = fields['data_resources']['dr_psql_port']
                self.dr_psql_database = fields['data_resources']['dr_psql_database']

                self.mci_url = fields['master_client_index']['mci_url']
                self.mci_psql_user = fields['master_client_index']['mci_psql_user']
                self.mci_psql_password = fields['master_client_index']['mci_psql_password']
                self.mci_psql_hostname = fields['master_client_index']['mci_psql_hostname']
                self.mci_psql_port = fields['master_client_index']['mci_psql_port']
                self.mci_psql_database = fields['master_client_index']['mci_psql_database']

                self.client_id = fields['auth_access']['client_id']
                self.client_secret = fields['auth_access']['client_secret']
                self.audience = fields['auth_access']['audience']
                self.oauth2_url = fields['auth_access']['oauth2_url']

                self.environment = environment
                self.debug = True
                self.testing = True
            except Exception:
                raise ConfigurationError(
                    'Invalid key in JSON configuration. Please check the configuration.')
            else:
                self.dr_psql_uri = 'postgresql://{}:{}@{}:{}/{}'.format(
                    self.dr_psql_user,
                    self.dr_psql_password,
                    self.dr_psql_hostname,
                    self.dr_psql_port,
                    self.dr_psql_database
                )

                self.mci_psql_uri = 'postgresql://{}:{}@{}:{}/{}'.format(
                    self.mci_psql_user,
                    self.mci_psql_password,
                    self.mci_psql_hostname,
                    self.mci_psql_port,
                    self.mci_psql_database
                )

        else:
            raise ConfigurationError(
                'Cannot find environment \'{}\' in JSON configuration.')

class LocalConfiguration(Configuration):
    """Development configuration class."""
    def __init__(self):
        self.from_json()
        self.debug = True
        self.testing = True

class DevelopmentTestingConfiguration(Configuration):
    """Development configuration class."""

    def __init__(self):
        self.from_json()
        self.debug = True
        self.testing = False

class ProductionConfiguration(Configuration):
    """Production configuratuon class."""

    def __init__(self):
        self.from_env()
        self.debug = False
        self.testing = False

class ConfigurationFactory(object):
    @staticmethod
    def get_config(config_type: str):
        if config_type.upper() == 'LOCAL':
            return LocalConfiguration()
        if config_type.upper() == 'DEVELOPMENT_TESTING':
            return DevelopmentTestingConfiguration()
        if config_type.upper() == 'PRODUCTION':
            return ProductionConfiguration()

    @staticmethod
    def from_env():
        """Retrieve configuration based on environment settings.
        Provides a configuration object based on the settings found in the `APP_ENV` variable. Defaults to the `development`
        environment if the variable is not set.
        Returns:
            object: Configuration object based on the configuration environment found in the `APP_ENV` environment variable.
        """
        environment = os.getenv('APP_ENV', 'LOCAL')

        return ConfigurationFactory.get_config(environment)