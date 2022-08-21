from typing import List

from ..hw_interface.definitions import MessageMovementCommandReply



def sample_data(samples:List[MessageMovementCommandReply]):
    """Samples data from a list of MessageMovementCommandReply - objects.
    Returns 3-tuple with current mean value, mid pos and mid millis (time stamp).
    
    Params: 
    - samples: List[MessageMovementCommandReply]"""
    current_mean = sum([i.current for i in samples]) / len(samples)

    if len(samples) % 2 == 0:
        #even number of elements
        lower_index = int( len(samples) / 2 -1 )
        item_lower, item_upper = samples[lower_index: lower_index + 2]

        pos = (item_lower.position + item_upper.position) / 2
        millis = (item_lower.millis + item_upper.millis) / 2
    else:
        #uneven
        index = int(len(samples) / 2)
        pos, millis = samples[index].position, samples[index].millis

    return current_mean, pos, millis
