from configparser import ConfigParser

import toml
import sys


class Config:

    config: ConfigParser

    def __init__(self, path, overrides={}):
        self.path = path
        self.config = ConfigParser()
        self.config.read(self.path)
        self._parse_config()
        self._apply_overrides(overrides)

    def validate_config(self):
        try:
            assert self.action in ['DEFER', 'REJECT'], "Action must be either DEFER or REJECT"
            assert self.strategy in ['fixed-window', 'sliding-window', 'moving-window'], "Currently only fixed-window, sliding-window, and moving-window strategies are supported"
            assert self.field in ['sender', 'client_address', 'sasl_username'], "Field must be one of sender, client_address, sasl_username"
        except AssertionError as e:
            print(f"Configuration error: {e}")    
            sys.exit(1)

    def _parse_config(self):
        """Parse and validate the configuration."""
        # Get global settings
        self.address = self.config.get('server', 'address', fallback='localhost')
        self.port = int(self.config.get('server', 'port', fallback=4455))
        self.field = self.config.get('server', 'field', fallback='sender')
        self.default_limit = self.config.get('server', 'default_limit', fallback='10/hour')
        self.storage = self.config.get('server', 'storage', fallback='memory://')
        self.strategy = self.config.get('server', 'strategy', fallback='fixed-window')
        self.action = self.config.get('server', 'action', fallback='DEFER')
        self.action_text = self.config.get('server', 'action_text', fallback='4.5.3 Limit ({limit}) exceeded for {field}={key}')
        self.dump_period = int(self.config.get('server', 'dump_period', fallback=3600))
        self.dump_file = self.config.get('server', 'dump_file', fallback=None)
        self.log_file = self.config.get('server', 'log_file', fallback=None)
        self.transparent = self.config.getboolean('server', 'transparent', fallback=False)

        self.validate_config()

        # Parse per-field limits
        self.limits = {}
        if 'limits' in self.config:
            for key, value in self.config['limits'].items():
                self.limits[key] = value

    def _apply_overrides(self, overrides):
        for key, val in overrides.items():
            if hasattr(self, key):
                print(f"Overriding config: {key}={val}")
                setattr(self, key, val)
            else:
                print(f"Warning: Unknown config option '{key}' in overrides")

    def get_limit(self, value):
        """
        Get limit and period for a specific value (e.g., email address).
        Returns {'limit': int, 'period': int} or None if not found.
        """
        return self.limits.get(value)

    def __repr__(self):
        return (f"Config(address={self.address}, port={self.port}\n"
                f"  field={self.field}\n"
                f"  default_limit={self.default_limit}\n"
                f"  storage={self.storage}\n"
                f"  strategy={self.strategy}\n"
                f"  limits={len(self.limits)}\n"
                f"  log={self.log_file}\n"
                f"  dump_file={self.dump_file}\n"
                f"  dump_period={self.dump_period}\n"
                f"  transparent={self.transparent}\n"
                )