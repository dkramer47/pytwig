
def call_pytwig_function(function_call : str, args):
    '''
    Calls the given function string with args and returns the result.
    '''
    if function_call not in _all_pytwig_functions:
        raise Exception("Error: the function being called does not exist.")

    return _all_pytwig_functions[function_call](args)

def _range(args):
    '''
    Creates a list with the given range of numbers. end is exclusive.
    '''
    start = int(args[0])
    end = int(args[1])
    return [*range(start, end)]

# I know this is probably done in a stupid way but I just want it to work right now.
def _number_format(args):
    '''
    Formats a number with the given arguments. Similar to PHP's number_format().
    '''
    args_len = len(args)

    num = float(args[0])
    decimals = 0
    decimal_separator = '.'
    thousands_separator = ','

    if args_len > 1:
        decimals = int(args[1])
    if args_len > 2:
        decimal_separator = str(args[2])
    if args_len > 3:
        thousands_separator = str(args[3])

    # Format then replace the original separators with the custom ones.
    formatted_split = f'{{:,.{decimals}f}}'.format(num).split('.')

    # Split and replace thousands on the decimal to avoid overwriting each other.
    formatted_split[0] = formatted_split[0].replace(',', thousands_separator)
    return decimal_separator.join(formatted_split)

_all_pytwig_functions = {
    'range': _range,
    'number_format': _number_format,
}