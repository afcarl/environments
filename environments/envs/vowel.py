"""Implementation of a model of vowel generation and perception by de Boer:
de Boer, B. "The Origin of Vowel Systems", Oxford: Oxford University Press

Formant equations :

F_1 = (  p**2 * (( -392 +  392*r)*h**2 + (  596 -  668*r)*h + ( -146 +  166*r))
       + p    * ((  348 -  348*r)*h**2 + ( -494 -  606*r)*h + (  141 -  175*r))
       +        ((  340 -   72*r)*h**2 + ( -796 +  108*r)*h + (  708 -   38*r)))

F_2 = (  p**2 * ((-1200 + 1208*r)*h**2 + ( 1320 - 1328*r)*h + (  118 -  158*r))
       + p    * (( 1864 - 1488*r)*h**2 + (-2644 + 1510*r)*h + ( -561 +  221*r))
       +        (( -670 +  490*r)*h**2 + ( 1355 -  697*r)*h + ( 1517 -  117*r)))

F_3 = (  p**2 * ((  604 -  604*r)*h**2 + ( 1038 - 1178*r)*h + (  246 +  566*r))
       + p    * ((-1150 + 1262*r)*h**2 + (-1443 + 1313*r)*h + ( -317 -  483*r))
       +        (( 1130 -  836*r)*h**2 + ( -315 +   44*r)*h + ( 2427 -  127*r)))

F_4 = (  p**2 * ((-1120 +   16*r)*h**2 + ( 1696 -  180*r)*h + (  500 +  522*r))
       + p    * (( -140 +  240*r)*h**2 + ( -578 +  214*r)*h + ( -692 -  419*r))
       +        (( 1480 -  602*r)*h**2 + (-1220 +  289*r)*h + ( 3678 -  178*r)))

Cochlea model :

C_1 = F_1
C_2 = | F_2                          if F_3 - F_2 >  c
      | ((2 - w_1)*F_2 + w_1*F_3)/2  if F_3 - F_2 <= c and F_4 - F_2 >= c
      | (w_2*F_2 + (2 - w_2)*F_3)/2  if F_4 - F_2 <= c and F_3 - F_2 <= F_4 - F_3
      | ((2 + w_2)*F_3 - w_2*F_4)/2  if F_4 - F_2 <= c and F_3 - F_2 >= F_4 - F_3

with w_1 = (c - (F_3 - F_2))/2
     w_2 = ((F_4 - F_3) - (F_3 - F_2))/(F_4 - F_2)
"""
from __future__ import print_function, division, absolute_import

from ..environment import Channel, Environment
from .. import tools


defcfg = Environment.defcfg._deepcopy()
defcfg.classname = 'environments.envs.VowelModel'


class VowelModel(Environment):

    defcfg = defcfg

    def __init__(self, cfg, **kwargs):
        """Initialization"""
        super(VowelModel, self).__init__(cfg)
        self.m_channels = [Channel('r', (0, 1)), Channel('h', (0, 1)), Channel('p', (0, 1))]
        self.s_channels = [Channel('C_1', (2, 8)), Channel('C_2', (7, 23))]
        # s_bounds ((2.4, 7.5), (7.4, 22.1))

    def __repr__(self):
        return "VowelModel"

    def _execute(self, m_signal, meta=None):
        """Execute a new order."""
        assert tools.in_bounds(m_signal, self.m_channels), "The motor signal was out of bounds."
        m_vector = tools.to_vector(m_signal, self.m_channels)
        self._pos = self._perceive(self._vocalize(m_vector))
        self._pos = (self._pos[0]/100, self._pos[1]/100)
        return tools.to_signal(self._pos, self.s_channels)

    def _vocalize(self, param):
        r, h, p = param
        F_1 = (  p**2 * (( -392 +  392*r)*h**2 + (  596 -  668*r)*h + ( -146 +  166*r))
               + p    * ((  348 -  348*r)*h**2 + ( -494 +  606*r)*h + (  141 -  175*r))
               +        ((  340 -   72*r)*h**2 + ( -796 +  108*r)*h + (  708 -   38*r)))

        F_2 = (  p**2 * ((-1200 + 1208*r)*h**2 + ( 1320 - 1328*r)*h + (  118 -  158*r))
               + p    * (( 1864 - 1488*r)*h**2 + (-2644 + 1510*r)*h + ( -561 +  221*r))
               +        (( -670 +  490*r)*h**2 + ( 1355 -  697*r)*h + ( 1517 -  117*r)))

        F_3 = (  p**2 * ((  604 -  604*r)*h**2 + ( 1038 - 1178*r)*h + (  246 +  566*r))
               + p    * ((-1150 + 1262*r)*h**2 + (-1443 + 1313*r)*h + ( -317 -  483*r))
               +        (( 1130 -  836*r)*h**2 + ( -315 +   44*r)*h + ( 2427 -  127*r)))

        F_4 = (  p**2 * ((-1120 +   16*r)*h**2 + ( 1696 -  180*r)*h + (  500 +  522*r))
               + p    * (( -140 +  240*r)*h**2 + ( -578 +  214*r)*h + ( -692 -  419*r))
               +        (( 1480 -  602*r)*h**2 + (-1220 +  289*r)*h + ( 3678 -  178*r)))
        return F_1, F_2, F_3, F_4

    def _perceive(self, formants):
        F_1, F_2, F_3, F_4 = formants
        C_1 = F_1
        C_2 = None
        c = 3.5 # Barks
        w_1 = (c - (F_3 - F_2))/c
        w_2 = ((F_4 - F_3) - (F_3 - F_2))/(F_4 - F_2)

        if F_3 - F_2 >  c:
            C_2 = F_2
        elif F_3 - F_2 <= c and F_4 - F_2 >= c:
            C_2 = ((2 - w_1)*F_2 + w_1*F_3)/2
        elif F_4 - F_2 <= c and F_3 - F_2 <= F_4 - F_3:
            C_2 = (w_2*F_2 + (2 - w_2)*F_3)/2
        elif F_4 - F_2 <= c and F_3 - F_2 >= F_4 - F_3:
            C_2 = ((2 + w_2)*F_3 - w_2*F_4)/2
        else:
            assert False
        return C_1, C_2

