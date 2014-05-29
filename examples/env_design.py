# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# `environments` - first steps

# <markdowncell>

# The `environments` module expose two classes: `Channel` and `Environment`.

# <codecell>

from environments import Channel, Environment

# <markdowncell>

# A `Channel` describes a scalar communication channel. It has a name, and, optionnally, bounds, that describe - but don't enforce - maximum and minimum on the value the scalar described can take. 

# <codecell>

ch_x = Channel('x', bounds=(0, 10))
ch_y = Channel('y', bounds=(5, 15))
ch_a = Channel('a', bounds=(5, 25))

# <markdowncell>

# Lists of channels describe signals. For instance, if we consider `ch_x` and `ch_y` to be motor channels, and `ch_a` a sensory channels, we can create motor and sensory signals:

# <codecell>

m_channels = [ch_x, ch_y]
s_channels = [ch_a]

# a motor signal
{'x': 4, 'y': 11}
# a sensory signal
{'a': 15}

# <markdowncell>

# An `Environment` instance possesses two attributes, `m_channels` and `s_channels` describing its motor and sensory channels respectively, and a method `execute`, that receives a motor signal and returns environmental feedback. The environmental feedback contains the executed motor_signal, the resulting sensory signal, and an uuid - an unique identifier.

# <codecell>

# an environmental feedback, also called 'observation'.
{'m_signal': {'x': 4, 'y': 11},
 's_signal': {'a': 15},
 'uuid'    : 0}

# <markdowncell>

# To inherit from `Environment`, one only needs to overrides the method `_execute`, that is expected to receive a motor signal and return a sensory signal. This method is called by `Environment.execute`, that assign an uuid automatically to the feedback using the standart library `uuid` module. Let's create a simple environment.

# <codecell>

class Sum(Environment):
    """Compute the sum of its motor signal"""
    
    def __init__(self, cfg):
        """Declare `m_channels` and `s_channels`"""
        self.m_channels = [ch_x, ch_y]
        self.s_channels = [ch_a]
        
    def _execute(self, m_signal, meta=None):
        """Return a sensory signal"""
        return {'a': m_signal['x'] + m_signal['y']}

# <markdowncell>

# We can now execute motor commands on the environment.

# <codecell>

sum_env = Sum()

sum_env.execute({'x': 2, 'y': 11})

# <markdowncell>

# ### TODO
# * `meta` in `execute`
# * `cfg`
# * Environment class
# * `close` and `try: ... finally:`
# * environments without `s_channels`

# <codecell>


