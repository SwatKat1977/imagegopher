'''
Copyright (C) 2022 delivery-exchange.com
Unauthorized copying of this file, via any medium is strictly prohibited.
Proprietary and confidential.  All Rights Reserveds
'''
from shared.configuration import configuration_setup

CONFIGURATION_LAYOUT = configuration_setup.ConfigurationSetup(
    {
        "logging": [
            configuration_setup.ConfigurationSetupItem(
                "log_level", configuration_setup.ConfigItemDataType.STRING,
                valid_values=['DEBUG', 'INFO'], default_value="INFO")
        ],
        "database": [
            configuration_setup.ConfigurationSetupItem(
                "filename", configuration_setup.ConfigItemDataType.STRING,
                is_required=True)
        ]
    }
)
