# PyTwig
A simple template engine modeled after TWIG in pure Python.

I made this for a personal project, and it works for basic templating. It also allows for more tags/functions to be added. It's syntax is based off of TWIG's, just with missing functionality. If you need some, feel free to add it and PR.

There's a lot of improvements that could be made, but it works for basic templates.

## Usage
Use PyTwig to parse and render a template using data.
```
from pytwig import render_template

data = {
    'number': 10,
    'text': 'Hello World',
    'rows': [
        {
            'text': 'Hello Row 1',
            'value': 1,
        }
    ],
}
result = render_template('path/to/template/template.html', data)
```
