## Customize the Templates

There are several HTML templates used at this time, all are stored in the
`templates/` folder or a subfolder of this.

- `templates/index.html` - This template is shown when the root of
the API is visited using a web browser instead of an API call. Use it to display
vasic details about your API and usage instructions, point to the documentation
etc. The default output is below for an example:

![Default Index
Page](https://github.com/seapagan/fastapi-template/raw/main/static/images/html_index.png)

- `templates/email` - this folder contains HTML Email templates, **currently
only basic placeholders**.
- `welcome.html`. This is sent to a new User when they sign up
