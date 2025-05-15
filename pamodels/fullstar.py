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

class EEStar(VGroup, metaclass=ConvertToOpenGL):
    """
    one object to control them all

    all the surfaces
    everything computed once.
    """
    def __init__ (self, lines, phi, theta, psi, radius_p, radius_e, ures=12, vres=12, **kwargs):
        """
        lines is Sequence[Map[key,value]]
        alpha <-- some vector co-latitude.
        phi <-- some vector co-latitude or euler angle
        theta <-- euler angle
        psi <-- euler angle

        euler notation ZXZ
        """

        ## 
        ## euler rotation
        cphi, sphi     = np.cos ( phi ), np.sin ( phi )
        ctheta, stheta = np.cos ( theta ), np.sin ( theta )
        cpsi, spsi     = np.cos ( psi ), np.sin ( psi )
        ## phi, theta, psi
        ## this is shit
        # self.rot = np.array ( [
            # [cphi*cpsi - sphi*ctheta*spsi, -cphi*spsi - sphi*ctheta*cpsi, sphi*stheta ],
            # [sphi*cpsi + cphi*ctheta*spsi, -sphi*spsi + cphi*ctheta*cpsi, -cphi*stheta],
            # [stheta*spsi, stheta*cpsi, ctheta]
        # ])
        ## psi, theta, phi
        ## this is right precessional period
        self.rot = np.array ( [
            [cpsi*cphi - spsi*ctheta*sphi, -cpsi*sphi - spsi*cphi*ctheta, spsi*stheta],
            [sphi*cpsi*ctheta + spsi*cphi, -sphi*spsi +cphi*cpsi*ctheta, -stheta*cpsi],
            [sphi*stheta, stheta*cphi, ctheta]
        ] )

        ##
        ## 
        ## call before
        super().__init__(**kwargs)

        ##
        star  = self.get_star (radius_p=radius_p, radius_e=radius_e, ures=ures, vres=vres)
        star.set_fill ( color=BLUE, opacity=1.0 )
        star.set_stroke ( color=BLUE, opacity=0.5, width=0.5 )
        self.add(*star)

        for line in lines:
            _line = self.get_arrow_line ( alpha=line['alpha'], phi=line['phi'], height=line['height'])
            _line.set_fill ( color=line['color'], opacity=line['opacity'] )
            _line.set_stroke ( color=line['color'], opacity=line['opacity'], width=0.5 )
            self.add ( *_line )

    def get_star (self, ures=10, vres=10, radius=0.025, radius_p=1., radius_e=1.35 ):
        uranges = np.linspace ( 0., TAU, ures )
        vranges = np.linspace ( 0., PI, vres )
        uu,vv   = np.meshgrid ( uranges, vranges )
        # xx, yy, zz (pre-rotated)
        xx    = radius_e * np.cos ( uu ) * np.sin ( vv )
        yy    = radius_e * np.sin ( uu ) * np.sin ( vv )
        zz    = -radius_p * np.cos ( vv )
        # rx, ry, rz (rotated)
        rx  = ( self.rot[0,0] * xx ) + ( self.rot[0,1] * yy ) + ( self.rot[0,2] * zz )
        ry  = ( self.rot[1,0] * xx ) + ( self.rot[1,1] * yy ) + ( self.rot[1,2] * zz )
        rz  = ( self.rot[2,0] * xx ) + ( self.rot[2,1] * yy ) + ( self.rot[2,2] * zz )
        
        faces = VGroup()
        # work loop
        for iu in range ( ures - 1 ):
            for iv in range ( vres - 1 ):
                face = ThreeDVMobject()
                # a square from 
                # BL BR TR TL BL
                face.set_points_as_corners(
                    [
                        [rx[iu,iv], ry[iu,iv], rz[iu,iv]],
                        [rx[iu+1,iv], ry[iu+1,iv], rz[iu+1,iv]],
                        [rx[iu+1,iv+1], ry[iu+1,iv+1], rz[iu+1,iv+1]],
                        [rx[iu,iv+1], ry[iu,iv+1], rz[iu,iv+1]],
                        [rx[iu,iv], ry[iu,iv], rz[iu,iv]]
                    ],
                )
                faces.add(face)
        return faces
        # faces.set_fill ( color=BLUE, opacity=1.0 )
        # faces.set_stroke ( color=BLUE, opacity=0.5, width=0.5 )
        # self.add(*faces)

    def get_line (self, alpha=0., phi=0., hres=10, pres=10, radius=0.02, height=3.0):
        """
        returns a VGroup
        """
        afaces = VGroup ()
        ## arrow-physics
        hrange = np.linspace ( 0, height, hres )
        prange = np.linspace ( 0, TAU, pres )
        hh,pp  = np.meshgrid ( hrange, prange )
        xx     = radius * np.cos ( pp ) 
        yy     = radius * np.sin ( pp ) 
        zz     = hh
        ##
        cphi, sphi     = np.cos(phi), np.sin(phi)
        calpha, salpha = np.cos(alpha), np.sin(alpha)
        rot    = np.array ( [
            [ cphi, -sphi*calpha, sphi*salpha ],
            [ sphi, cphi*calpha, -cphi*salpha ],
            [0, salpha, calpha],
        ] )
        rot    = self.rot @ rot
        ## rx, ry, rz (rotated)
        rx  = ( rot[0,0] * xx ) + ( rot[0,1] * yy ) + ( rot[0,2] * zz )
        ry  = ( rot[1,0] * xx ) + ( rot[1,1] * yy ) + ( rot[1,2] * zz )
        rz  = ( rot[2,0] * xx ) + ( rot[2,1] * yy ) + ( rot[2,2] * zz )
        for iu in range ( hres - 1 ):
            for iv in range ( pres - 1 ):
                face = ThreeDVMobject()
                ## a square from 
                ## BL BR TR TL BL
                face.set_points_as_corners(
                    [
                        [rx[iu,iv], ry[iu,iv], rz[iu,iv]],
                        [rx[iu+1,iv], ry[iu+1,iv], rz[iu+1,iv]],
                        [rx[iu+1,iv+1], ry[iu+1,iv+1], rz[iu+1,iv+1]],
                        [rx[iu,iv+1], ry[iu,iv+1], rz[iu,iv+1]],
                        [rx[iu,iv], ry[iu,iv], rz[iu,iv]]
                    ],
                )
                afaces.add(face)
        return afaces

    def get_arrow_line (self, alpha=0., phi=0., hres=10, pres=10, cres=8, radius=0.02, height=3.0, cheight=0.25, ctheta=PI/8):
        """
        returns a VGroup

        arrow means there is a cone at the end
        cone is radius and phi

        Rz(phi) * Rx(alpha)
        [cp, -sp, 0]   [1,    0, 0]
        [sp,  cp, 0] x [0, ca, -sa]
        [0,    0, 1]   [0, sa,  ca]
        ---- or ----
        Rx(alpha) * Rz(phi)
        [1,  0,   0]   [cp, -sp, 0]
        [0, ca, -sa] x [sp,  cp, 0]
        [0, sa,  ca]   [0,    0, 1]
        =
        [cp,      -sp,   0]
        [ca*sp, ca*cp, -sa]
        [sa*sp, sa*cp,  ca]

        -- 
        Rz(phi) * Ry(alpha)
        [cp, -sp, 0]   [ca, 0, -sa]
        [sp,  cp, 0] x [0,  1,   0]
        [0,    0, 1]   [sa, 0,  ca]
        =
        [cp*ca, -sp, -cp*sa]
        [sp*ca,  cp, -sp*sa]
        [sa,      0,     ca]


        """
        afaces = VGroup ()
        ##
        cphi, sphi     = np.cos(phi), np.sin(phi)
        calpha, salpha = np.cos(alpha), np.sin(alpha)
        irot    = np.array ( [
            [ cphi*calpha, -sphi, -cphi*salpha ],
            [ sphi*calpha, cphi,  -sphi*salpha ],
            [salpha, 0, calpha],
        ] )
        # irot    = np.array ( [
            # [ cphi, -sphi*calpha, sphi*salpha ],
            # [ sphi, cphi*calpha, -cphi*salpha ],
            # [0, salpha, calpha],
        # ] )
        # irot   = np.array ( [
            # [ cphi,  -sphi,  0 ],
            # [ calpha*sphi, calpha*cphi, -salpha ],
            # [salpha*sphi, salpha*cphi, calpha]
        # ] )
        rot    = self.rot @ irot
        # rot    = irot @ self.rot
        ## line-physics
        hrange = np.linspace ( 0, height, hres, endpoint=True )
        prange = np.linspace ( 0, TAU, pres, endpoint=True )
        hh,pp  = np.meshgrid ( hrange, prange )
        xx     = radius * np.cos ( pp ) 
        yy     = radius * np.sin ( pp ) 
        zz     = hh
        """
        for the arrow tip
        x,y,z  = -radius, 0, height
        rx, ry, rz = -rot[?,0]*radius + rot[?,2]*height
        """
        ## rx, ry, rz (rotated)
        rx  = ( rot[0,0] * xx ) + ( rot[0,1] * yy ) + ( rot[0,2] * zz )
        ry  = ( rot[1,0] * xx ) + ( rot[1,1] * yy ) + ( rot[1,2] * zz )
        rz  = ( rot[2,0] * xx ) + ( rot[2,1] * yy ) + ( rot[2,2] * zz )
        ###
        _h    = height + 0.15
        # _oox  = -rot[0,0]*radius + rot[0,2]*_h
        _oox  = rot[0,2]*_h
        _ooy  = rot[1,2]*_h
        _ooz  = rot[2,2]*_h
        for iu in range ( hres - 1 ):
            for iv in range ( pres - 1 ):
                face = ThreeDVMobject()
                ## a square from 
                ## BL BR TR TL BL
                face.set_points_as_corners(
                    [
                        [rx[iu,iv], ry[iu,iv], rz[iu,iv]],
                        [rx[iu+1,iv], ry[iu+1,iv], rz[iu+1,iv]],
                        [rx[iu+1,iv+1], ry[iu+1,iv+1], rz[iu+1,iv+1]],
                        [rx[iu,iv+1], ry[iu,iv+1], rz[iu,iv+1]],
                        [rx[iu,iv], ry[iu,iv], rz[iu,iv]]
                    ],
                )
                afaces.add(face)
        ## arrow-physics
        rrange = np.linspace ( 0, cheight, cres, endpoint=True )
        prange = np.linspace ( 0, TAU, cres )
        rr,cp  = np.meshgrid ( rrange, prange )
        xx     = rr * np.sin ( ctheta ) * np.cos ( cp )
        yy     = rr * np.sin ( ctheta ) * np.sin ( cp )
        zz     = -rr * np.cos ( ctheta )
        ## rx, ry, rz (rotated)
        rx  = ( rot[0,0] * xx ) + ( rot[0,1] * yy ) + ( rot[0,2] * zz )
        ry  = ( rot[1,0] * xx ) + ( rot[1,1] * yy ) + ( rot[1,2] * zz )
        rz  = ( rot[2,0] * xx ) + ( rot[2,1] * yy ) + ( rot[2,2] * zz )
        # 
        rx += _oox
        ry += _ooy
        rz += _ooz
        for iu in range ( cres - 1 ):
            for iv in range ( cres - 1 ):
                face = ThreeDVMobject()
                ## a square from 
                ## BL BR TR TL BL
                face.set_points_as_corners(
                    [
                        [rx[iu,iv], ry[iu,iv], rz[iu,iv]],
                        [rx[iu+1,iv], ry[iu+1,iv], rz[iu+1,iv]],
                        [rx[iu+1,iv+1], ry[iu+1,iv+1], rz[iu+1,iv+1]],
                        [rx[iu,iv+1], ry[iu,iv+1], rz[iu,iv+1]],
                        [rx[iu,iv], ry[iu,iv], rz[iu,iv]]
                    ],
                )
                afaces.add(face)
        return afaces

class TestE(ThreeDScene):
    def construct (self):
        self.set_camera_orientation(phi=PI/3, theta=PI/3)

        _phi   = ValueTracker ( 0. )
        _theta = ValueTracker ( PI / 8 )
        _psi   = ValueTracker ( 0. )

        e = always_redraw (  lambda : EEStar ( alpha=PI/4, phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value() , radius_p=1.5, radius_e=2.2 ) )

        azz  = Arrow3D ( start=ORIGIN, end=[0,0, 1.5*2.2], color=GREEN )

        self.add ( e, azz )
        # self.wait (1)

        self.play ( 
            _phi.animate.set_value ( 8*TAU ), 
            _psi.animate.set_value ( 2*TAU ),
            rate_func=linear,
            run_time=16
        )


class RVM(ThreeDScene):
    """
    this is simple RVM

    make two animations. one isometric view. one projective view
    """
    ZETA  = PI/2
    ALPHA = PI/4
    PHI   = PI
    def construct (self):
        self.set_camera_orientation(phi=self.ZETA, theta=0)

        _phi   = ValueTracker ( 0. )
        _theta = ValueTracker ( 0. )
        _psi   = ValueTracker ( 0. )

        lines  = [ dict(alpha=self.ALPHA, phi=self.PHI, height=2.8, color=ORANGE, opacity=1.) ]

        e = always_redraw (  lambda : EEStar ( lines, phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value() , radius_p=2.0, radius_e=2.0, ures=30, vres=30 ) )

        azz  = Arrow3D ( start=ORIGIN, end=[0,0, 3.5], color=GREEN )

        self.add ( e, azz )
        # self.wait (1)

        ## rotation speed
        ## 2 rotations / second

        self.play ( 
            _phi.animate.set_value ( 4*TAU ), 
            # self.camera.phi_tracker.animate.set_value( 4*PI/6 ),
            # _psi.animate.set_value ( 2*TAU ),
            rate_func=linear,
            run_time=12
        )

class WTF:
    def wtf():
        self.play ( 
            _phi.animate.set_value ( 5*TAU ), 
            self.camera.phi_tracker.animate.set_value( 2*PI/6 ),
            # _psi.animate.set_value ( 2*TAU ),
            rate_func=linear,
            run_time=2
        )

        self.play ( 
            _phi.animate.set_value ( 9*TAU ), 
            # self.camera.phi_tracker.animate.set_value( 3*PI/6 ),
            # _psi.animate.set_value ( 2*TAU ),
            rate_func=linear,
            run_time=8
        )

        self.play ( 
            _phi.animate.set_value ( 10*TAU ), 
            self.camera.phi_tracker.animate.set_value( 3*PI/6 ),
            # _psi.animate.set_value ( 2*TAU ),
            rate_func=linear,
            run_time=2
        )

        self.play ( 
            _phi.animate.set_value ( 14*TAU ), 
            # self.camera.phi_tracker.animate.set_value( 3*PI/6 ),
            # _psi.animate.set_value ( 2*TAU ),
            rate_func=linear,
            run_time=8
        )

class PrecessionSetup(ThreeDScene):
    """
    this is simple PVM
    """
    ZETA  = PI/2
    ALPHA = PI/4
    PHI   = PI
    def construct (self):
        self.set_camera_orientation(phi=self.ZETA, theta=PI)

        _phi   = ValueTracker ( 0. )
        _theta = ValueTracker ( 0. )
        _psi   = ValueTracker ( 0. )

        lines  = [ 
            dict(alpha=self.ALPHA, phi=self.PHI, height=2.8, color=ORANGE, opacity=1.),
            dict(alpha=0, phi=0, height=2.8, color=RED, opacity=1.),
        ]

        e = always_redraw (  lambda : EEStar ( lines, phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value() , radius_p=1.4, radius_e=2.0, ures=30, vres=30 ) )

        azz  = Arrow3D ( start=ORIGIN, end=[0,0, 3.5], color=GREEN )

        self.add ( e, azz )
        # self.wait (1)

        # first do rotation
        self.play ( 
            _phi.animate.set_value ( 1*TAU ), 
            # self.camera.phi_tracker.animate.set_value( 4*PI/6 ),
            # _psi.animate.set_value ( 2*TAU ),
            rate_func=linear,
            run_time=3
        )

        # bring theta
        # 4 rotations
        self.play ( 
            _phi.animate.set_value ( 4*TAU ), 
            _theta.animate.set_value ( PI/8. ),
            rate_func=linear,
            run_time=9
        )

        # start precession
        # 5 rotations
        self.play ( 
            _phi.animate.set_value ( 9*TAU ), 
            _psi.animate.set_value ( 4.5*TAU ),
            rate_func=linear,
            run_time=15
        )

class PVM(ThreeDScene):
    """
    this is simple RVM

    make two animations. one isometric view. one projective view
    """
    ZETA  = PI/2
    ALPHA = PI/4
    PHI   = PI
    def construct (self):
        self.set_camera_orientation(phi=self.ZETA, theta=PI)

        ## initial phi is not 0
        _phi   = ValueTracker ( PI/4. )
        _theta = ValueTracker ( PI/8. )
        _psi   = ValueTracker ( 0. )

        lines  = [ 
            dict(alpha=self.ALPHA, phi=self.PHI, height=2.8, color=ORANGE, opacity=1.),
            dict(alpha=0, phi=0, height=2.8, color=RED, opacity=1.),
        ]

        e = always_redraw (  lambda : EEStar ( lines, phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value() , radius_p=1.4, radius_e=2.0, ures=30, vres=30 ) )

        azz  = Arrow3D ( start=ORIGIN, end=[0,0, 3.5], color=GREEN )

        self.add ( e, azz )
        self.wait (duration=2.0)

        ## show rotation to rotation
        ## one rotation = 0.05 precession
        ## five rotations is one precession
        r_phi  = _phi.get_value () + 1.0 * TAU
        r_psi  = 0.05 * TAU

        for i in range(20):
            self.play ( 
                _phi.animate.set_value ( r_phi ), 
                # self.camera.phi_tracker.animate.set_value( 4*PI/6 ),
                _psi.animate.set_value ( r_psi ),
                rate_func=linear,
                run_time=1
            )
            self.wait ( duration=0.5 )
            ##
            r_phi += 1.0 * TAU
            r_psi += 0.05 * TAU

class FastPVM(ThreeDScene):
    """
    this is simple RVM

    make two animations. one isometric view. one projective view
    """
    ZETA  = PI/2
    ALPHA = PI/4
    PHI   = PI
    def construct (self):
        self.set_camera_orientation(phi=self.ZETA, theta=PI)

        ## initial phi is not 0
        _phi   = ValueTracker ( PI/4. )
        _theta = ValueTracker ( PI/8. )
        _psi   = ValueTracker ( 0. )

        lines  = [ 
            dict(alpha=self.ALPHA, phi=self.PHI, height=2.8, color=ORANGE, opacity=1.),
            dict(alpha=0, phi=0, height=2.8, color=RED, opacity=1.),
        ]

        e = always_redraw (  lambda : EEStar ( lines, phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value() , radius_p=1.4, radius_e=2.0, ures=30, vres=30 ) )

        azz  = Arrow3D ( start=ORIGIN, end=[0,0, 3.5], color=GREEN )

        self.add ( e, azz )
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
