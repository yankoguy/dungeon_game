import math

def on_object(object_x, object_y, object_width, object_height, object_to_check_x, object_to_check_y, object_to_check_width, object_to_check_height) -> bool:
    """
    Returns True if object is on object to check else return False
    """
    if (object_to_check_y <= object_y <= object_to_check_y + object_to_check_height or (object_y <= object_to_check_y <= object_y + object_height)) \
            and ((object_to_check_x <= object_x <= object_to_check_x + object_to_check_width) or (object_x <= object_to_check_x <= object_x + object_width)):
        return True
    return False
