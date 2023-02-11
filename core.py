from ._pytwig_parse import parse_pytwig_template

# TODO: Create custom package exceptions instead of using generic.

def render_template(template_path, data : dict = None):

    # TODO: Check the data for any invalid variable names. Specifically ones that start with an underscore, as that's used to store internal data.

    # Create the initial context.
    context = {
        'data': data,
        'length_offset': 0,
        'for_depth': 0,
    }

    with open(template_path, 'r') as template_file:
        # Load in the whole file, it's easier to do regex this way and it's probably small. Maybe I'll improve it if I want to.
        template = template_file.read()
        template = parse_pytwig_template(template, context)
        return template