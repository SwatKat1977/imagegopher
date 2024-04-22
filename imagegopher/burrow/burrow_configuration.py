'''
Copyright 2014-2023 Integrated Test Management Suite

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from shared.configuration.configuration import Configuration
from shared.singleton import Singleton

class BurrowConfiguration(Configuration, metaclass = Singleton):
    """ Singleton for the config """

    @property
    def logging_log_level(self) -> str:
        """ Configuration property : Logging | log level """
        return BurrowConfiguration().get_entry("logging", "log_level")

    @property
    def database_filename(self) -> str:
        """ Configuration property : Database | filename """
        return BurrowConfiguration().get_entry("database", "filename")

    @property
    def gatherer_host(self) -> str:
        """ Configuration property : Gatherer host """
        return BurrowConfiguration().get_entry("gatherer", "gatherer_host")

    @property
    def gatherer_port(self) -> int:
        """ Configuration property : Gatherer port """
        return BurrowConfiguration().get_entry("gatherer", "gatherer_port")

    @property
    def gatherer_wait_for_ok(self) -> int:
        """ Configuration property : Wait for Gatherer to be ready """
        return BurrowConfiguration().get_entry("gatherer", "wait_for_ok")

    @property
    def gatherer_wait_for_ok_retries(self) -> int:
        """ Configuration property : Wait for Gatherer to be ready retries """
        return BurrowConfiguration().get_entry("gatherer",
                                               "wait_for_ok_retries")
