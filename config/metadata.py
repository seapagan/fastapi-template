"""This file contains Custom Metadata for your API Project.

Be aware, this will be re-generated any time you run the
'api-admin custom metadata' command!
"""
from config.structure import MetadataBase

custom_metadata = MetadataBase(
    title="API Template",
    description="A Clean API template with JTW Auth and User control baked in.",
    repository="https://github.com/seapagan/fastapi-template",
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    contact={
        "name": "Grant Ramsay",
        "url": "https://www.gnramsay.com",
    },
)
