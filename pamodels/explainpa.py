"""

follow Surface approach

add individual faces. 
add vectors as needed. 

this way, i compute everything only once.

i control the speed
i am speed

"""
import time
import numpy as np

from manim import *
from manim.mobject.opengl.opengl_compatibility import ConvertToOpenGL

class PA(VGroup, metaclass=ConvertToOpenGL):
    """
    """
    def __init__ (self, pa, radius=3.0, color=BLACK, **kwargs):
        """
        """

        pa    = np.arctan ( np.tan ( pa ) )

        super().__init__(**kwargs)

        _rnd  = radius *  np.array ( [np.sin(pa), np.cos(pa), 0] )
        ## get arrow
        _a    = Arrow ( start=ORIGIN, end=_rnd, color=color, buff=0 )
        _b    = Arrow ( start=ORIGIN, end=-_rnd, color=color, buff=0 )
        _t_a  = Tex("$"+f"{np.rad2deg(pa):.1f}"+"^\\circ$").move_to ( _rnd, DOWN )
        _t_b  = Tex("$"+f"{np.rad2deg(pa):.1f}"+"^\\circ$").move_to ( -_rnd, UP )
        _s_a  = Sector ( 0.5,  angle=-pa, start_angle=0.5*PI, color=color)
        _s_b  = Sector ( 0.5, angle=-pa, start_angle=1.5*PI, color=color)
        ## add sector
        # print ( f" here.pa = {pa:.2f}" )
        # print ( f"start = ", _a.get_start() )
        self.add ( _a, _b, _t_a, _t_b, _s_a, _s_b )

class EVPA(Scene):
    def construct (self):
        _pa    = ValueTracker ( 0. )

        e = always_redraw ( lambda  : PA ( _pa.get_value() ) )

        azz_up    = Arrow ( start=ORIGIN, end=3.0*UP, color=GREEN, buff=0 )
        _t_up     = Tex("$0^\\circ$").move_to(azz_up.get_end(), DOWN)
        azz_down  = Arrow ( start=ORIGIN, end=3.0*DOWN, color=GREEN, buff=0 )
        _t_down   = Tex("$0^\\circ$").move_to(azz_down.get_end(), UP)

        left      = Arrow ( start=ORIGIN, end=3.0*LEFT, color=RED, buff=0 )
        _t_left   = Tex("$-90^\\circ$").move_to ( left.get_end(), RIGHT )
        right     = Arrow ( start=ORIGIN, end=3.0*RIGHT, color=BLUE, buff=0 )
        _t_right  = Tex("$90^\\circ$").move_to ( right.get_end(), LEFT )

        self.add ( e, azz_up, azz_down, left, right, _t_left, _t_right, _t_up, _t_down )
        # self.wait (1)

        ANG       = [PI/8, PI/4, PI/3, PI/2, 2*PI/3, 3*PI/4, PI]
        ## 22.5, 45, 60, 90, 120, 135, 180, 


        for a in ANG:
            self.play (
                _pa.animate.set_value (a),
                rate_func=linear,
                run_time=1
            )
            self.wait ( duration=2.0 )
