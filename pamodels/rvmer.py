"""
RVM animation

In axes
"""
import numpy as np

from manim import *

from fullstar import EEStar

class RVM(Scene):
    ALPHA    = PI / 4
    ZETA     = PI / 6
    PHI0     = 0.
    PA0      = 0.

    def get_rvm ( self, longdeg, alpha, zeta, phi0, pa0 ):
        long = np.deg2rad ( longdeg )
        nr  = np.sin ( alpha ) * np.sin ( long - phi0 )
        dr  = ( np.sin ( zeta ) * np.cos ( alpha ) ) - ( np.cos( zeta ) * np.sin ( alpha ) * np.cos ( long - phi0 ) )
        pa  = pa0 - np.arctan ( nr / dr )
        pa  = np.arctan ( np.tan ( pa ) )
        return np.rad2deg ( pa )

    def construct(self):

        axes = Axes ( x_range=(-180, 180, 360), y_range=(-90, 90, 180), tips=False )
        graph = axes.plot ( lambda x : self.get_rvm ( x, RVM.ALPHA, RVM.ZETA, RVM.PHI0, RVM.PA0 ) )

        ## dot
        dot       = Dot (color=BLUE, radius=1.)
        dot_value = ValueTracker ( -180. )
        dot       = f_always ( dot.move_to, lambda : axes.i2gp ( dot_value.get_value(), graph ) )

        self.add ( axes, graph, dot )

        self.play ( dot_value.animate.set_value ( 180 ), rate_func=linear, run_time=8  )


