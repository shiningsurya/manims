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

from numpy import sin, cos, arctan

def pvm_pa ( zeta : float, alpha : float, phi_o : float, phi_0 : float, phi : float, theta : float, psi : float, pa0 : float ):
    """
    actual big pa formula

    zeta, alpha, phio, phi0, phi, theta, psi

    this is with phi,theta,psi
    _tpa = (sin(alpha)*sin(phi - phi_o)*cos(phi_0 + psi) + sin(alpha)*sin(phi_0 + psi)*cos(theta)*cos(phi - phi_o) - sin(theta)*cos(alpha)*cos(phi - phi_o))/(sin(alpha)*sin(theta)*sin(zeta)*sin(phi_0 + psi) + sin(alpha)*sin(phi - phi_o)*sin(phi_0 + psi)*cos(theta)*cos(zeta) - sin(alpha)*cos(zeta)*cos(phi - phi_o)*cos(phi_0 + psi) - sin(theta)*sin(phi - phi_o)*cos(alpha)*cos(zeta) + sin(zeta)*cos(alpha)*cos(theta))

    this is with psi,theta,phi
    _tpa = (-sin(alpha)*sin(phi + phi_0)*cos(theta)*cos(phi_o - psi) + sin(alpha)*sin(phi_o - psi)*cos(phi + phi_0) + sin(theta)*cos(alpha)*cos(phi_o - psi))/(-sin(alpha)*sin(theta)*sin(zeta)*sin(phi + phi_0) + sin(alpha)*sin(phi + phi_0)*sin(phi_o - psi)*cos(theta)*cos(zeta) + sin(alpha)*cos(zeta)*cos(phi + phi_0)*cos(phi_o - psi) - sin(theta)*sin(phi_o - psi)*cos(alpha)*cos(zeta) - sin(zeta)*cos(alpha)*cos(theta))
    """
    #_tpa = (sin(alpha)*sin(phi - phi_o)*cos(phi_0 + psi) + sin(alpha)*sin(phi_0 + psi)*cos(theta)*cos(phi - phi_o) - sin(theta)*cos(alpha)*cos(phi - phi_o))/(sin(alpha)*sin(theta)*sin(zeta)*sin(phi_0 + psi) + sin(alpha)*sin(phi - phi_o)*sin(phi_0 + psi)*cos(theta)*cos(zeta) - sin(alpha)*cos(zeta)*cos(phi - phi_o)*cos(phi_0 + psi) - sin(theta)*sin(phi - phi_o)*cos(alpha)*cos(zeta) + sin(zeta)*cos(alpha)*cos(theta))
    _tpa = (-sin(alpha)*sin(phi + phi_0)*cos(theta)*cos(phi_o - psi) + sin(alpha)*sin(phi_o - psi)*cos(phi + phi_0) + sin(theta)*cos(alpha)*cos(phi_o - psi))/(-sin(alpha)*sin(theta)*sin(zeta)*sin(phi + phi_0) + sin(alpha)*sin(phi + phi_0)*sin(phi_o - psi)*cos(theta)*cos(zeta) + sin(alpha)*cos(zeta)*cos(phi + phi_0)*cos(phi_o - psi) - sin(theta)*sin(phi_o - psi)*cos(alpha)*cos(zeta) - sin(zeta)*cos(alpha)*cos(theta))
    _pa  = np.arctan ( _tpa )
    return np.arctan ( np.tan ( pa0 - _pa ) )

class PPStar(VGroup, metaclass=ConvertToOpenGL):
    """
    one object to control them all

    all the surfaces
    everything computed once.

    projected one. no need for the star
    """
    def __init__ (self, lines, zeta, phi, theta, psi, **kwargs):
        """
        lines is Sequence[Map[key,value]]
        alpha <-- some vector co-latitude.
        phi <-- some vector co-latitude or euler angle
        theta <-- euler angle
        psi <-- euler angle

        euler notation ZXZ

        first compute the 3D vectors.
        then compute projection 
        normal of the sky-projected frame is [0,sin(zeta),cos(zeta)]

        z-axis is rotating about
        x-axis is towards left? forms a RHS 
        y-axis is coming out of the screen

        let us test theta,psi = 0
        zeta     = pi/2
        self.rot = Rz(phi)
        normal   = [0,1,0]

        vec      = (alpha, phi0) = [salpha*cphi0, salpha*sphi0, calpha]
        rec      = (alpha, phi+phi0)
                 = [salpha*CPHI, salpha*SPHI, calpha]

        dot      = rec @ normal = szeta*salpha*SPHI + czeta*calpha
                 ~ salpha*SPHI
        proj     = [0, szeta*szeta*salpha*SPHI + szeta*czeta*calpha, czeta*szeta*salpha*SPHI + czeta*czeta*calpha]
                 ~ [0, salpha*SPHI, 0]
        perp     = rec - proj
                 = [salpha*CPHI]
                 ~ [salpha*CPHI, 0, calpha]

        only take XZ-component
        """
        ##
        ## plane normal
        # self.normal    = np.array ( [ 0, np.sin(zeta), np.cos(zeta) ] )
        zphi           = np.pi
        self.normal    = np.array ( [ np.sin(zeta)*np.cos(zphi), np.sin(zeta)*np.sin(zphi), np.cos(zeta) ] )
        ## [-szeta, 0, czeta]

        ## 
        ## euler rotation
        cphi, sphi     = np.cos ( phi ), np.sin ( phi )
        ctheta, stheta = np.cos ( theta ), np.sin ( theta )
        cpsi, spsi     = np.cos ( psi ), np.sin ( psi )
        ## phi, theta, psi
        # self.rot = np.array ( [
            # [cphi*cpsi - sphi*ctheta*spsi, -cphi*spsi - sphi*ctheta*cpsi, sphi*stheta ],
            # [sphi*cpsi + cphi*ctheta*spsi, -sphi*spsi + cphi*ctheta*cpsi, -cphi*stheta],
            # [stheta*spsi, stheta*cpsi, ctheta]
        # ])
        ## psi, theta, phi
        self.rot = np.array ( [
            [cpsi*cphi - spsi*ctheta*sphi, -cpsi*sphi - spsi*cphi*ctheta, spsi*stheta],
            [sphi*cpsi*ctheta + spsi*cphi, -sphi*spsi +cphi*cpsi*ctheta, -stheta*cpsi],
            [sphi*stheta, stheta*cphi, ctheta]

        ] )
        self.irot = np.linalg.inv (self.rot)

        # self.normal = self.irot @ self.normal

        ## in plane component of spin/ang-momentum vector
        czeta, szeta = np.cos(zeta), np.sin(zeta)
        inplane_1   = np.array ( [ czeta*szeta, 0, szeta**2 ] )
        ## normal x inplane_1
        inplane_2   = np.cross ( self.normal, inplane_1 )
        inplane_2   = inplane_2 / np.linalg.norm ( inplane_2 )

        ##
        ## 
        ## call before
        super().__init__(**kwargs)

        for line in lines:
            ### this minus sign here is because of some weird notation
            _end  = self.get_projection ( alpha=-line['alpha'], phi=line['phi'], radius=line['radius'] )
            pa    = -np.arctan ( np.dot ( inplane_2, _end ) / np.dot ( inplane_1, _end ) )
            # pa    = -pvm_pa ( zeta, line['alpha'], zphi, line['phi'], phi, theta, psi, 0.0  )
            _rnd  = line['radius'] * np.array ( [np.sin(pa), np.cos(pa), 0] )
            ## if vector is behind the screen, 
            ## just pass
            # if np.abs ( np.mod(phi,TAU) - line['phi'] ) > PI:
            # if np.arccos( np.cos ( phi - line['phi'] ) ) < PI/2:
                # continue
            ##
            ## pa is angle between _end and [0,1,0]
            ## _end is unit vector [0,1,0] is unit
            line['pa'].set_value ( pa )
            ## get arrow
            _a    = Arrow ( start=ORIGIN, end=_rnd, color=line['color'], buff=0 )
            _b    = Arrow ( start=ORIGIN, end=-_rnd, color=line['color'], buff=0 )
            _t_a  = Tex("$"+f"{np.rad2deg(pa):.1f}"+"^\\circ$").move_to ( _rnd, DOWN )
            _t_b  = Tex("$"+f"{np.rad2deg(pa):.1f}"+"^\\circ$").move_to ( -_rnd, UP )
            _s_a  = Sector ( 0.5,  angle=-pa, start_angle=0.5*PI, color=line['color'])
            _s_b  = Sector ( 0.5, angle=-pa, start_angle=1.5*PI, color=line['color'])
            ## add sector
            # print ( f" here.pa = {pa:.2f}" )
            # print ( f"start = ", _a.get_start() )
            self.add ( _a, _b, _t_a, _t_b, _s_a, _s_b )

    def get_projection (self, alpha=0., phi=0., radius=1., rot=True):
        """
        return start-end
        return in plane component

        start is always origin

        z-axis = [0,0,1]
        normal = [-szeta, 0, czeta]
        rec    = [0,0,1]
        dot    = czeta
        perp   = [0,0,1] - czeta*[-szeta, 0, czeta]
        [-czeta*szeta, 0, 1 - czeta**2]

        """
        ##
        cphi, sphi     = np.cos(phi), np.sin(phi)
        calpha, salpha = np.cos(alpha), np.sin(alpha)
        vec    = radius * np.array ( [ salpha*cphi, salpha*sphi, calpha ] )
        if rot:
            rec    = self.rot @ vec
            # rec  = self.irot @ vec
        else:
            rec  = vec
        ## dot product
        dot    = np.dot ( rec, self.normal )
        perp   = rec - dot*self.normal
        perp   = perp / np.linalg.norm (perp)
        # perp   = dot*self.normal
        # print (f" there.pa = {measured_pa:.2f}")
        ##
        # return perp[[0,2,1]]
        return perp

class TestE(Scene):
    ZETA  = PI/3
    ALPHA = PI/4
    PHI   = PI
    def construct (self):

        _phi   = ValueTracker ( 0. )
        _theta = ValueTracker ( 0. )
        _psi   = ValueTracker ( 0. )

        lines  = [ dict(alpha=self.ALPHA, phi=self.PHI, color=BLACK, opacity=1., radius=3.0, pa=ValueTracker(0.)) ]

        e = always_redraw (  lambda : PPStar ( lines, self.ZETA, phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value()) )

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

        self.play ( 
            _phi.animate.set_value ( 2*TAU ), 
            # _psi.animate.set_value ( 2*TAU ),
            rate_func=linear,
            run_time=8
        )

class ProjectedRVM(Scene):
    ZETA  = PI/2
    ALPHA = PI/4
    PHI   = PI
    def construct (self):

        _phi   = ValueTracker ( 0. )
        _theta = ValueTracker ( 0. )
        _psi   = ValueTracker ( 0. )

        lines  = [ dict(alpha=self.ALPHA, phi=self.PHI, color=BLACK, opacity=1., radius=3.0, pa=ValueTracker(0.)) ]

        e = always_redraw (  lambda : PPStar ( lines, self.ZETA, phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value()) )

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

        self.play ( 
            _phi.animate.set_value ( 4*TAU ), 
            # _psi.animate.set_value ( 2*TAU ),
            rate_func=linear,
            run_time=12
        )

class ProjectedPVM(Scene):
    ZETA  = PI/2
    ALPHA = PI/4
    PHI   = PI
    def construct (self):
        _phi   = ValueTracker ( PI/4 )
        _theta = ValueTracker ( PI/8 )
        _psi   = ValueTracker ( 0. )

        lines  = [ dict(alpha=self.ALPHA, phi=self.PHI, color=BLACK, opacity=1., radius=3.0, pa=ValueTracker(0.)) ]

        e = always_redraw (  lambda : PPStar ( lines, self.ZETA, phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value()) )

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

        self.wait (duration=2.0)

        ## show rotation to rotation
        ## one rotation = 0.2 precession
        ## five rotations is one precession
        r_phi  = _phi.get_value () + 1.0 * TAU
        r_psi  = 0.2 * TAU

        for i in range(6):
            self.play ( 
                _phi.animate.set_value ( r_phi ), 
                # self.camera.phi_tracker.animate.set_value( 4*PI/6 ),
                _psi.animate.set_value ( r_psi ),
                rate_func=linear,
                run_time=4
            )
            self.wait ( duration=2.0 )
            ##
            r_phi += 1.0 * TAU
            r_psi += 0.2 * TAU

class ProjectedFastPVM(Scene):
    ZETA  = PI/2
    ALPHA = PI/4
    PHI   = PI
    def construct (self):
        _phi   = ValueTracker ( PI/4 )
        _theta = ValueTracker ( PI/8 )
        _psi   = ValueTracker ( 0. )

        lines  = [ dict(alpha=self.ALPHA, phi=self.PHI, color=BLACK, opacity=1., radius=3.0, pa=ValueTracker(0.)) ]

        e = always_redraw (  lambda : PPStar ( lines, self.ZETA, phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value()) )

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

        self.wait (duration=2.0)

        ## show rotation to rotation
        ## one rotation = 0.2 precession
        ## five rotations is one precession
        r_phi  = _phi.get_value () + 10.0 * TAU
        r_psi  = _psi.get_value () + 1.0 * TAU

        for i in range(6):
            self.play ( 
                _phi.animate.set_value ( r_phi ), 
                # self.camera.phi_tracker.animate.set_value( 4*PI/6 ),
                _psi.animate.set_value ( r_psi ),
                rate_func=linear,
                run_time=4
            )
            self.wait ( duration=2.0 )
            ##
            r_phi += 10.0 * TAU
            r_psi += 1.0 * TAU
