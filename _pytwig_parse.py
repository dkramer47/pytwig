import re
from ._pytwig_functions import call_pytwig_function

class PyTwigRegex:
    SAY_DO_REGEX = re.compile(r'(?:{%|{{)\s*((?:.|\s)+?)\s*(?:%}|}})') # Matches a "say" or "do": {{ something }}
    FUNCTION_REGEX = re.compile(r'(.+?)\((.*?)\)') # Matches functions: something()
    PARAMS_REGEX = re.compile(r',(?=(?:[^"\']*["\'][^"\']*["\'])*[^"\']*$)') # Matches all of the commas in a function's params.

    STRING_REGEX = re.compile(r'^(["\'])((?:\\1|(?:(?!\1)).)*)(\1)$') # Matches any one single or double quoted string: "something"
    INT_REGEX = re.compile(r'^\d+$') # Matches any one whole integer: 137
    FLOAT_REGEX = re.compile(r'^\d+\.\d+$') # Matches any one float value: 137

def parse_pytwig_template(template : str, context : dict):
    # Search the template for code using a while loop so that template changes are taken into account.
    match = PyTwigRegex.SAY_DO_REGEX.search(template)
    while match is not None:
        # Update the context with the template and match information.
        context['template'] = template
        context['match'] = match

        # Parse says and dos based on the opening brackets.
        code = match.group()
        if code[:2] == '{{':
            template = parse_say(match, context)
        elif code[:2] == '{%':
            template = parse_do(match, context)
        
        # Find the next match starting from the start position of this one, since it won't change with the updates being made.
        match = PyTwigRegex.SAY_DO_REGEX.search(template, match.start())
    
    return template

def parse_say(match : re.Match, context : dict):
    '''
    Parses the given "say" and returns the updated text.
    '''
    template = context['template']

    # Get the raw text inside of the brackets.
    say_text = match.group(1)
    output = say_text

    # TODO: Right now you can have a function, or a value with no other logic. This is where improvements would be made.
    output = parse_value(say_text, context)

    # Substitute the say code for the parsed value in the text.
    return template[:match.start()] + str(output) + template[match.end():]

def parse_do(match : re.Match, context : dict):
    '''
    Parses the given "do" and returns the updated text.
    '''

    # Get the text for the do.
    do_text = match.group(1)
    tags = re.split(r'\s', do_text)

    # Import the tag function here to avoid a circular dependency.
    from ._pytwig_tags import call_pytwig_tag
    return call_pytwig_tag(tags, context)

def parse_value(text : str, context : dict):
    '''
    Parses and returns the result of any objects inside of a text.
    '''
    text = str.strip(text)
    template_data = context['data']

    # TODO: Check the value syntax to make sure there are no invalid characters and that it doesn't start with an underscore.

    # Check if function.
    function_match = PyTwigRegex.FUNCTION_REGEX.match(text)
    if function_match is not None:
        # Parses the function. This will make a recursive call to parse_value to get the value of the functions parameters.
        function_call = function_match.group(1)

        # Splits the params on commas NOT inside strings... Pretty important.
        split_params = PyTwigRegex.PARAMS_REGEX.split(function_match.group(2))
        params = [
            parse_value(value, context)
            for value in split_params
        ]
        return call_pytwig_function(function_call, params)

    # Check if string.
    str_match = PyTwigRegex.STRING_REGEX.match(text)
    if str_match is not None:
        # Second group in this regex is the string value.
        return str_match.group(2)
    
    # Check if int.
    int_match = PyTwigRegex.INT_REGEX.match(text)
    if int_match is not None:
        return int(int_match.group())

    # Check if float.
    float_match = PyTwigRegex.FLOAT_REGEX.match(text)
    if float_match is not None:
        return float(float_match.group())

    # Otherwise treat it like an object.
    obj = str.split(text, '.')

    # Check the for depth to see if it should check the for loop data for values.
    if context['for_depth'] > 0:
        for_loop_value = _get_value_recursively(obj, template_data['_for_data'])
        if for_loop_value is not None:
            return for_loop_value

    return _get_value_recursively(obj, template_data)

def _get_value_recursively( obj_keys : list, obj : dict, depth = 0):
    key = obj_keys[depth]

    # Check to make sure the key is in the given dict.
    if key in obj:
        new_obj = obj[key]
    
        # If we're at end of the given keys, return the item.
        if depth == len(obj_keys) - 1:
            return new_obj
        
        # Otherwise continue digging.
        return _get_value_recursively(obj_keys, new_obj, depth + 1)
    
    return None