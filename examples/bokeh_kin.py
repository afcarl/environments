"""Just a little function to visualize the posture of a two-dimensional arm."""
from __future__ import division

import numbers
import random

import numpy as np
from bokeh import plotting

from environments import tools


def bokeh_kin(kin_env, m_signal, color='#DF4949', alpha=1.0, **kwargs):

    m_vector = tools.to_vector(m_signal, kin_env.m_channels)
    s_signal = kin_env._multiarm.forward_kin(m_vector)

    xs, ys = [0.0], [0.0]
    for i in range(kin_env.cfg.dim):
        xs.append(s_signal['x{}'.format(i+1)])
        ys.append(s_signal['y{}'.format(i+1)])
    xs, ys = ys, xs # we swap x and y for a more symmetrical look

    if isinstance(kin_env.cfg.lengths, numbers.Real):
        total_length = kin_env.cfg.lengths*kin_env.cfg.dim
    else:
        total_length = sum(kin_env.cfg.lengths)
    total_length += 0.0

    kwargs ={'plot_height' : int(350*1.60),
             'plot_width'  : int(350*1.60),
             'x_range'     : [-1.0, 1.0],
             'y_range'     : [-1.0, 1.0],
             'line_color'  : color,
             'line_alpha'  : alpha,
             'fill_color'  : color,
             'fill_alpha'  : alpha,
             'title':''
            }

    plotting.hold()
    plotting.line(xs, ys, **kwargs)
    plotting.grid().grid_line_color = None
    plotting.xaxis().major_tick_in   = 0
    plotting.ygrid().grid_line_color = None
    plotting.yaxis().major_tick_in   = 0

    plotting.circle(xs[  : 1], ys[  : 1], radius=0.015, **kwargs)
    plotting.circle(xs[ 1:-1], ys[ 1:-1], radius=0.008, **kwargs)
    plotting.circle(xs[-1:  ], ys[-1:  ], radius=0.01, color='red')
    plotting.hold(False)


if __name__ == '__main__':
    from environments import Environment
    from environments.envs import KinematicArm2D

    # Arm with same length segments
    cfg = KinematicArm2D.defcfg._deepcopy()
    cfg.dim = 20
    cfg.limits = (-150.0, 150.0)
    cfg.lengths = 1/cfg.dim
    cfg.full_sensors = True
    kin_env = Environment.create(cfg)

    # Arm with decreasing lenghts segments
    cfg2 = cfg._deepcopy()
    cfg2.lengths = np.array([0.9**i for i in range(cfg2.dim)])
    #cfg2.lengths = np.array([random.random() for i in range(cfg2.dim)])
    cfg2.lengths = cfg2.lengths/sum(cfg2.lengths)
    kin_env2 = Environment.create(cfg2)

    m_signals = [{'j0': -31.23, 'j1': -44.21, 'j2': -20.18, 'j3': +31.55, 'j4': +35.66, 'j5':  +5.19, 'j6': +17.34, 'j7': +24.51, 'j8':  -2.69, 'j9': +26.52, 'j10': -34.87, 'j11': +10.72, 'j12': -19.38, 'j13': -33.49, 'j14': +13.78, 'j15': -22.43, 'j16': +33.61, 'j17': -28.95, 'j18': +34.31, 'j19':   45.75},
                 {'j0': -53.66, 'j1': -56.20, 'j2': -56.67, 'j3': -34.83, 'j4': -20.29, 'j5':  +7.51, 'j6': +20.92, 'j7': +25.51, 'j8': -17.59, 'j9':  +6.51, 'j10':  -9.65, 'j11': +45.70, 'j12': +20.88, 'j13': +24.25, 'j14': +28.65, 'j15': -42.79, 'j16': +34.45, 'j17': -39.90, 'j18':  +2.74, 'j19':  -11.12},
                 {'j0': +58.13, 'j1': +45.43, 'j2': -21.01, 'j3':  +2.35, 'j4': -38.90, 'j5': -39.23, 'j6': +45.14, 'j7': -57.58, 'j8': +39.49, 'j9': +29.01, 'j10':  -0.09, 'j11': -56.19, 'j12': +56.07, 'j13':  +5.91, 'j14': +36.61, 'j15': -52.65, 'j16': -58.60, 'j17': +32.45, 'j18': +43.69, 'j19': -120.77},
                 {'j0': +53.09, 'j1': +55.83, 'j2': -51.08, 'j3': +41.44, 'j4': +44.43, 'j5':  +4.67, 'j6':  +2.15, 'j7': +37.23, 'j8':  -3.77, 'j9': -46.70, 'j10': +56.41, 'j11': -21.08, 'j12': +13.73, 'j13': +47.23, 'j14':  +7.94, 'j15': -27.26, 'j16': +56.54, 'j17':  -7.77, 'j18': -18.98, 'j19': +149.46}]

    plotting.output_file('arm_vizu.html')

    for i, m_signal in enumerate(m_signals):
        bokeh_kin(kin_env, m_signal, alpha=0.2 + i*0.15)
        plotting.hold(True)
        bokeh_kin(kin_env2, m_signal, color='#91C46C', alpha=0.2 + i*0.15)
        plotting.hold(True)

    plotting.xaxis().minor_tick_line_color = None
    plotting.xaxis().major_tick_in = 0
    plotting.yaxis().minor_tick_line_color = None
    plotting.yaxis().major_tick_in = 0

    plotting.show()
