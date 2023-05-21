## Customize the Metadata

By default the Template Title, Description, Author and similar is set to my
details. Changing this is very easy though, and there are 2 ways you can do.

### Manually

Metadata is stored in the `config/metadata.py` file and this
can be edited by hand if desired:

```python
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
        "name": "Grant Ramsay (seapagan)",
        "url": "https://www.gnramsay.com",
    },
    email="seapagan@gmail.com",
    year="2023"
)
```

You can change the values in this dictionary as needed. You should also change
the name, description and authors in the `pyproject.toml` file.

For the License URL, you can find a list in the
`config/helpers.py`

### Using the provided configuration tool

The `api-admin` command can also do this for you, asking for the values at the
command line and automatically updating both files:

```console
$ ./api-admin custom metadata

API-Template : Customize application Metadata

Enter your API title [API Template]:
Enter the description [Run 'api-admin custom metadata' to change this information.]:
Version Number (use * to reset to '0.0.1') [1.3.1]:
URL to your Repository [https://github.com/seapagan/fastapi-template]:

Choose a license from the following options:
Apache2, BSD3, BSD2, GPL, LGPL, MIT, MPL2, CDDL, EPL
Your Choice of License? [MIT]:

Author name or handle [Grant Ramsay (seapagan)]:
Contact Email address [seapagan@gmail.com]:
Author Website [https://www.gnramsay.com]:

You have entered the following data:
Title       : API Template
Description : Run 'api-admin custom metadata' to change this information.
Version     : 1.3.1
Repository  : https://github.com/seapagan/fastapi-template
License     : MIT
Author      : Grant Ramsay (seapagan)
Email       : seapagan@gmail.com
Website     : https://www.gnramsay.com
(C) Year    : 2023

Is this Correct? [Y/n]: y

-> Writing out Metadata .... Done!
```

This will also put in the correct License URL link automatically.
