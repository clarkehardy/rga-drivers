from datetime import datetime

def generate_filename(prefix):
    """Generate a filename by adding a prefix to a string
    with the current date and time.

    Args:
        prefix (str): file prefix

    Returns:
        str: a filename containing the prefix and the date and time
    """
    # Get the current date and time
    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create the filename with the prefix and current time
    filename = f'{prefix}_{current_time}.dat'

    return filename