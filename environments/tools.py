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

def find_channels(signal, channel_list):
    for channels in channels_list:
        try:
            for key in channels.keys():
                signal[key]
            return channels
        except KeyError:
            pass
    raise ValueError('No compatible channels found for signal {} amongst {}'.format(signal, channel_list))


def uniformize_signal(signal, channels):
    """ Uniformize a signal between 0.0 and 1.0
        Requires every channel to have bounds, or be discretized.
    """
    uni_signal = {}
    for c in channels:
        factor = 1.0
        if c.bounds[0] != c.bounds[1]:
            assert c.bounds[0] < c.bounds[1]
            factor = c.bounds[1] - c.bounds[0]
        uni_signal[c.name] = (signal[c.name]-c.bounds[0])/factor
    return uni_signal

def restore_signal(uni_signal, channels):
    """ Uniformize a signal between 0.0 and 1.0
        Requires every channel to have bounds, or be discretized.
    """
    signal = {}
    for c in channels:
        factor = 1.0
        if c.bounds[0] != c.bounds[1]:
            assert c.bounds[0] < c.bounds[1]
            factor = c.bounds[1] - c.bounds[0]
        signal[c.name] = uni_signal[c.name]*factor + c.bounds[0]
    return signal
