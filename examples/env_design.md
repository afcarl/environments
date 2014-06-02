
# `environments` - first steps

The `environments` module expose two classes: `Channel` and `Environment`.

### Channels


    from environments import Channel, Environment

A `Channel` describes a scalar communication channel. It has a name, and,
optionnally, bounds, that describe - but don't enforce - maximum and minimum on
the value the scalar described can take.


    ch_x = Channel('x', bounds=(0, 10))
    ch_y = Channel('y', bounds=(5, 15))
    ch_a = Channel('a', bounds=(5, 25))

Lists of channels describe signals. For instance, if we consider `ch_x` and
`ch_y` to be motor channels, and `ch_a` a sensory channels, we can create motor
and sensory signals:


    m_channels = [ch_x, ch_y]
    s_channels = [ch_a]
    
    # a motor signal
    {'x': 4, 'y': 11}
    # a sensory signal
    {'a': 15}




    {'a': 15}



### Environments

An `Environment` instance possesses two attributes, `m_channels` and
`s_channels` describing its motor and sensory channels respectively, and a
method `execute`, that receives a motor signal and returns environmental
feedback. The environmental feedback contains the executed motor_signal, the
resulting sensory signal, and an uuid - an unique identifier.


    # an environmental feedback, also called 'observation'.
    {'m_signal': {'x': 4, 'y': 11},
     's_signal': {'a': 15},
     'uuid'    : 0}




    {'m_signal': {'x': 4, 'y': 11}, 's_signal': {'a': 15}, 'uuid': 0}



To inherit from `Environment`, one only needs to overrides the method
`_execute`, that is expected to receive a motor signal and return a sensory
signal. This method is called by `Environment.execute`, that assign an uuid
automatically to the feedback using the standart library `uuid` module. Let's
create a simple environment.


    class Sum(Environment):
        """Compute the sum of its motor signal"""
        
        def __init__(self, cfg):
            """Declare `m_channels` and `s_channels`"""
            super(Sum, self).__init__(cfg)
            self.m_channels = [ch_x, ch_y]
            self.s_channels = [ch_a]
            
        def _execute(self, m_signal, meta=None):
            """Return a sensory signal"""
            return {'a': m_signal['x'] + m_signal['y']}

We can now execute motor commands on the environment.


    sum_env = Sum({})
    
    sum_env.execute({'x': 2, 'y': 11})




    {'m_signal': {'x': 2, 'y': 11},
     's_signal': {'a': 13},
     'uuid': UUID('d70e8c88-ebea-4c86-8568-c03b4e182477')}



### Details

#### `__init__()`'s `cfg` parameter
The ``__init__()`` method of an environment expects a `cfg` argument, which
provides configuration parameters to the environment. If you call
`Environment.__init__()`, it expects `cfg` to be a dictionnary or a
`forest.Tree` instance. In the former case, it will be converted to a
`forest.Tree` instance and set as the `self.cfg`.

#### `_execute`'s `meta` parameter
The `_execute` command accepts an additional argument, `meta`. If not `None`, it
is assumed to be dictionnary, that can be both use for providing additional
information on how to execute the command, or by the execution add logs and
metadata about how the motor command was executed.

#### `close()` method
Any cleanup needed stopping the environement should be done in the `close()`
method. The best way to create an environment and execute orders is to use a
`try: ... finally:` construction, so that any error or exception still cleans-up
open ports, connections, stops motors, etc.:


    try:
        sum_env = Sum({})
        sum_env.execute({'x': 2, 'y': 11})
    finally:
        sum_env.close()