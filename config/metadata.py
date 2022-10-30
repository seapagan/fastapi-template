"""This file contains Custom Metadata for your API Project.

Be aware, this will be re-generated any time you run the
'api-admin custom metadata' command!
"""
from config.helpers import MetadataBase

custom_metadata = MetadataBase(
    title="API Template",
    description="Run 'api-admin custom metadata' to change this information.",
    repository="https://github.com/seapagan/fastapi-template",
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    contact={
        "name": "Grant Ramsay",
        "url": "https://www.gnramsay.com",
    },
    email="seapagan@gmail.com",
)
