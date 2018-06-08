import configparser
import logging


class ConfigReaderException(Exception):
    def __init__(self, msg):
        self.err_msg = msg

    def __str__(self):
        return "Config Reader Error : {msg}".format(msg=self.err_msg)


class ConfigReader:
    def __init__(self, file_path):
        self.config = configparser.ConfigParser()
        try:
            if not self.config.read(file_path):
                raise ConfigReaderException("Node Configuration file is non-existent")
        except Exception as e:
            raise ConfigReaderException("Node Configuration file is corrupt")

    def get_config(self, section, option, fallback=None):
        if self.config.has_section(section):
            if self.config.has_option(section, option):
                value = self.config.get(section=section,
                                        option=option)
                if value.isdigit():
                    value = int(value)
                if not value:
                    raise ConfigReaderException("No value defined for configuration "
                                                "option {opt} in section {sec}".
                                                format(sec=section, opt=option))
                return value
            else:
                logging.error("Error reading Config : option {opt} missing "
                              "in section {sec}".format(opt=option, sec=section))
        else:
            logging.error("Error reading Config : section {sec} missing".
                          format(sec=section))
        if fallback:
            logging.info("Default value {d} being returned for option "
                         "{opt} in section {sec}".format(opt=option, sec=section, d=fallback))
            return fallback
        else:
            raise ConfigReaderException("No Fallback defined for configuration "
                                        "option {opt} in section {sec}".
                                        format(sec=section, opt=option))
