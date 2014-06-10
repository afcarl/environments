import collections
import random
import importlib


def _load_class(classname):
    """Load a class from a string"""
    module_name, class_name = classname.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)

def to_vector(signal, channels=None):
    """Convert a signal to a vector"""
    if channels is None:
        # we need consistent ordering
        assert isinstance(signal, collections.OrderedDict)
        return tuple(signal.values())
    else:
        return tuple(signal[c.name] for c in channels)

def to_signal(vector, channels):
    """Convert a vector to a signal"""
    assert len(vector) == len(channels), "the lenght of the vector ({}) doesn't match the length of the channels ({})".format(len(vector), len(channels))
    return {c_i.name: v_i for c_i, v_i in zip(channels, vector)}

def random_signal(channels, bounds=None):
    if bounds is None:
        return {c.name: c.fixed if c.fixed is not None else random.uniform(*c.bounds)
                for c in channels}
    else:
        return {c.name: c.fixed if c.fixed is not None else random.uniform(*b)
                for c, b in zip(channels, bounds)}

def in_bounds(signal, channels):
    legal = True
    for c in channels:
        if c in signal:
            legal = legal and c.bounds[0] <= signal[c.name] <= c.bounds[1]
    return legal
