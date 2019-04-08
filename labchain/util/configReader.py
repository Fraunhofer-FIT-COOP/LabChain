import configparser
import logging

logger = logging.getLogger(__name__)


class ConfigReaderException(Exception):
    def __init__(self, msg):
        self.err_msg = msg

    def __str__(self):
        return "Config Reader Error : {msg}".format(msg=self.err_msg)


class ConfigReader:
    def __init__(self, file_path):
        """Initialize ConfigReader

        Parameters
        ----------
        file_path : String
            The path of the config file to parse

        Attributes
        ----------
        config : Instance of ConfigParser, has the configuration

        """
        self.config = configparser.ConfigParser()
        try:
            if not self.config.read(file_path):
                raise ConfigReaderException("Node Configuration file is non-existent")
        except ConfigReaderException:
            raise
        except Exception:
            raise ConfigReaderException("Node Configuration file is corrupt")

    def get_config(self, section, option, fallback=None):
        """Returns the config for the section and option as saved in the
        configuration

        Parameters
        ----------
        section: String
            The name of the Section to return from
        option: String
            The name of the option to return
        fallback: String/Integer
            If option not found in section, return this value
        """
        if self.config.has_section(section):
            if self.config.has_option(section, option):
                value = self.config.get(section=section,
                                        option=option)
                if value.isdigit():
                    value = int(value)
                elif not value:
                    if fallback:
                        value = fallback
                    else:
                        raise ConfigReaderException("Option {opt} in section {sec} "
                                                    "defined without any value".\
                                                    format(opt=option, sec=section))
                return value
            else:
                logger.error("Error reading Config : option {opt} missing "
                             "in section {sec}".format(opt=option, sec=section))
        else:
            logger.error("Error reading Config : section {sec} missing".
                         format(sec=section))
        if fallback:
            logger.info("Default value {d} being returned for option "
                        "{opt} in section {sec}".format(opt=option, sec=section, d=fallback))
            return fallback
        else:
            raise ConfigReaderException("No Fallback defined for configuration "
                                        "option {opt} in section {sec}".
                                        format(sec=section, opt=option))
