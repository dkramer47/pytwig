import re
from ._pytwig_parse import (
    parse_pytwig_template,
    parse_value,
)

def call_pytwig_tag(exploded_tags : list, context : dict):
    # Use the starting word to determine the tag.
    tag = exploded_tags[0]
    if tag not in _all_pytwig_tags:
        raise Exception(f'Error: PyTwig tag "{tag}" does not exist.')
    
    return _all_pytwig_tags[tag](exploded_tags, context)

def _start_for(exploded_tags : list, context : dict):

    # Retrieve current match object from the context.
    match : re.Match = context['match']

    # Initialize the context for a for loop if it doesn't exist.
    if 'for_vars' not in context:
        context['for_vars'] = []
        context['data']['_for_data'] = {}

    # Make sure that this variable name isn't being used by a parent loop.
    # TODO: Could probably go with more syntax checking here.
    loop_var = exploded_tags[1]
    if loop_var in context['for_vars']:
        raise Exception(f'Error: iterator name "{loop_var}" is a duplicate of a parent loop.')

    # Variable three should definitely be the 'in' tag, if not, then the syntax is wrong.
    if exploded_tags[2] != 'in':
        raise Exception('Error: invalid syntax in for loop.')

    # The rest of the items in the list can be put back together to be parsed as in iterator.
    loop_iter_text = ' '.join(exploded_tags[3:])
    loop_iter = parse_value(loop_iter_text, context)

    # Check to make sure the loop item is iterable.
    if not hasattr(loop_iter, '__iter__'):
        raise Exception(f'Error: for loop iterable is invalid type. Type {type(loop_iter)} given.')

    # Increase the for loop depth.
    context['for_depth'] += 1

    # Set the for start position to the end of the match.
    loop_start_pos = match.end()

    # Begin parsing the inside of the loop, everything up until this for loop's endfor will be returned.
    template = context['template']
    loop_text = template[loop_start_pos:]
    loop_text_length = len(loop_text)
    loop_result = ''

    for value in loop_iter:
        # Set the loop interator variable to the value of the next item in the list.
        context['data']['_for_data'][loop_var] = value
        loop_result += parse_pytwig_template(loop_text, context)

    # Exited the loop, decrease for loop depth.
    context['for_depth'] -= 1

    # Return the text without the for loop code.
    loop_end_pos = loop_start_pos + loop_text_length - context['excess_content_length']
    template = template[:match.start()] + loop_result + template[loop_end_pos:]
    return template

def _end_for(_ : list, context : dict):
    # Raise an exception if not inside an active for loop.
    if context['for_depth'] == 0:
        raise Exception('Error: endfor was called outside of an active for loop.')

    # Return everything in the given template up until here to complete the loop.
    match : re.Match = context['match']
    template = context['template']

    for_content = template[:match.start()]
    context['excess_content_length'] = len(template[match.end():])

    return for_content

_all_pytwig_tags = {
    'for': _start_for,
    'endfor': _end_for,
}