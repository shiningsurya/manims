"""
rotation and precession
"""
import time
import numpy as np

from manim import *
from manim.mobject.opengl.opengl_compatibility import ConvertToOpenGL

class CCStar(VGroup, metaclass=ConvertToOpenGL):
    """
    one object to control them all

    all the surfaces
    everything computed once.
    """
    def __init__ (self, lines, masks, phi, theta, psi, radius_p, radius_e, nu=32, nv=32,  **kwargs):
        """
        lines is Sequence[Map[key,value]]
        masks is Sequence[Map[region, mask, color, etc]]
        alpha <-- some vector co-latitude.
        phi <-- some vector co-latitude or euler angle
        theta <-- euler angle
        psi <-- euler angle

        euler notation ZXZ

        nu, nv: samples in urange and vrange
        """

        ## 
        ## euler rotation
        cphi, sphi     = np.cos ( phi ), np.sin ( phi )
        ctheta, stheta = np.cos ( theta ), np.sin ( theta )
        cpsi, spsi     = np.cos ( psi ), np.sin ( psi )
        ## psi, theta, phi
        ## correct scheme
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
        ## u is colatitude like
        ## v is azimuth like
        # uranges = np.linspace ( 0., PI, nu)
        uranges = np.linspace ( PI, 0.,  nu)
        vranges = np.linspace ( 0., TAU, nv)
        ### do default logic yourself

        for prop in masks:
            star  = self.get_star (uranges[ prop['uslice'] ], vranges [ prop['vslice'] ], radius_p=radius_p, radius_e=radius_e)
            star.set_fill ( color=prop['color'], opacity=1.0 )
            star.set_stroke ( color=prop['color'], opacity=0.5, width=0.5 )
            self.add(*star)

        for line in lines:
            _line = self.get_arrow_line ( alpha=line['alpha'], phi=line['phi'], height=line['height'])
            _line.set_fill ( color=line['color'], opacity=line['opacity'] )
            _line.set_stroke ( color=line['color'], opacity=line['opacity'], width=0.5 )
            self.add ( *_line )

    def get_star (self, uranges, vranges, radius=0.025, radius_p=1., radius_e=1.35 ):
        uu,vv   = np.meshgrid ( vranges, uranges )
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
        for iu in range ( uranges.size - 1 ):
            for iv in range ( vranges.size - 1 ):
                face = ThreeDVMobject()
                # a square from 
                # BL BR TR TL BL
                # print ( f" {iu} {iv} start ... ", end='' )
                face.set_points_as_corners(
                    [
                        [rx[iu,iv], ry[iu,iv], rz[iu,iv]],
                        [rx[iu+1,iv], ry[iu+1,iv], rz[iu+1,iv]],
                        [rx[iu+1,iv+1], ry[iu+1,iv+1], rz[iu+1,iv+1]],
                        [rx[iu,iv+1], ry[iu,iv+1], rz[iu,iv+1]],
                        [rx[iu,iv], ry[iu,iv], rz[iu,iv]]
                    ],
                )
                # print ( )
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

def uslice_from_deg ( u1, u2, nu=32 ):
    """
    degree range to index
    u ranges from 0 to PI
    or from 0 to 180 deg

    u1 * 32 / 180
    need to flip it fore some reason

    32 - (u1 * 32) / 180
    """
    return slice ( int ( np.floor ( u1 * nu / 180. ) ), int ( np.ceil ( u2 * nu / 180. ) )  )
    # return slice ( int ( np.floor ( nu - (u1 * nu / 180. ) ) ), int ( np.ceil ( nu - (u2 * nu / 180. ) )  ) ) 

def vslice_from_deg ( u1, u2, nu=32 ):
    """
    degree range to index
    u ranges from 0 to TAU
    or from 0 to 360 deg

    u1 * 32 / 360
    """
    return slice ( int ( np.floor ( u1 * nu / 360. ) ), int ( np.ceil ( u2 * nu / 360. ) )  )

class Test(ThreeDScene):
    ZETA  = PI/2
    ALPHA = PI/4
    PHI   = PI
    def construct (self):
        self.set_camera_orientation(phi=self.ZETA, theta=PI)

        _phi   = ValueTracker ( 0. )
        _theta = ValueTracker ( PI / 8 )
        _psi   = ValueTracker ( 0. )

        lines  = [ 
            dict(alpha=self.ALPHA, phi=self.PHI, height=2.8, color=ORANGE, opacity=1.),
            dict(alpha=0, phi=0, height=2.8, color=RED, opacity=1.),
        ]

        masks = [
            ## main body
            {
                'uslice':slice(None, None),
                'vslice':slice(None, None),
                'color':BLUE,
            },
            {
                'uslice':slice(15, 18),
                'vslice':slice(20, 25),
                'color':RED,
            },
        ]

        e = always_redraw (  lambda : CCStar ( lines,masks, phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value() , radius_p=1.5, radius_e=2.2 ) )

        azz  = Arrow3D ( start=ORIGIN, end=[0,0, 1.5*2.2], color=GREEN )
        auu  = Arrow3D ( start=ORIGIN, end=[-4.0,0.0, 0], color=BLACK)

        self.add ( e, azz, auu )
        # self.wait (duration=1.0)

        ## show rotation to rotation
        ## one rotation = 0.2 precession
        ## five rotations is one precession
        r_phi  = _phi.get_value () + ( 32 * TAU )
        r_psi  = _psi.get_value () + (  4 * TAU )

        self.play ( 
            _phi.animate.set_value ( r_phi ), 
            # self.camera.phi_tracker.animate.set_value( 4*PI/6 ),
            _psi.animate.set_value ( r_psi ),
            rate_func=linear,
            run_time=4
        )

class SlowRotationShow(ThreeDScene):
    """

    """
    ZETA  = PI/4
    ALPHA = PI/10
    PHI   = PI
    def construct (self):
        """
        phi is colat?
        theta is azi?
        """
        # self.set_camera_orientation(phi=self.ZETA, theta=PI)
        self.set_camera_orientation(phi=self.ZETA, theta=PI)

        _phi   = ValueTracker ( 0. )
        _theta = ValueTracker ( 0. )
        _psi   = ValueTracker ( 0. )

        lines  = [ 
            dict(alpha=self.ALPHA, phi=self.PHI, height=2.8, color=RED, opacity=1.),
            # dict(alpha=0, phi=0, height=2.8, color=RED, opacity=1.),
        ]

        masks = [
            ## main body
            {
                'uslice':slice(None, None),
                'vslice':slice(None, None),
                'color':BLUE,
            },
            ## 40x50 : 30x60
            {
                'uslice':uslice_from_deg ( 20,70 ),
                'vslice':vslice_from_deg (30,60),
                'color':ORANGE,
            },
            {
                'uslice':uslice_from_deg ( 35,60 ),
                'vslice':vslice_from_deg (60,110),
                'color':GREEN,
            },
            {
                'uslice':uslice_from_deg ( 40,50 ),
                'vslice':vslice_from_deg (110,130),
                'color':PURE_BLUE,
            },
        ]

        e = always_redraw (  lambda : CCStar ( lines,masks, phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value() , radius_p=1.5, radius_e=2.2 ) )

        # azz  = Arrow3D ( start=ORIGIN, end=[0,0, 1.5*2.2], color=GREEN )
        # auu  = Arrow3D ( start=ORIGIN, end=[-4.0,0.0, 0], color=RED)
        def sphcoord ( r, theta, phi ):
            return r*np.array ( [np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)] )
        obs  = Arrow3D ( start=ORIGIN, end=sphcoord (4.0, self.ZETA, self.PHI), color=BLACK )

        self.add ( 
            e, 
            # azz, 
            # auu, 
            obs 
        )
        # self.wait (duration=1.0)

        ## show rotation to rotation
        ## one rotation = 0.2 precession
        ## five rotations is one precession
        r_phi  = _phi.get_value () + ( 1 * TAU )
        # r_psi  = _psi.get_value () + (  4 * TAU )
        ## only one rotation
        ## 

        self.play ( 
            _phi.animate.set_value ( r_phi ), 
            # self.camera.phi_tracker.animate.set_value( 4*PI/6 ),
            # _psi.animate.set_value ( r_psi ),
            rate_func=linear,
            run_time=2
        )

class PrecessionShow(ThreeDScene):
    """

    """
    ZETA  = PI/3
    ALPHA = PI/6
    PHI   = PI
    def construct (self):
        """
        phi is colat?
        theta is azi?
        """
        # self.set_camera_orientation(phi=self.ZETA, theta=PI)
        self.set_camera_orientation(phi=self.ZETA, theta=PI)

        _phi   = ValueTracker ( 0. )
        _theta = ValueTracker ( PI/8 )
        _psi   = ValueTracker ( 0. )

        lines  = [ 
            dict(alpha=self.ALPHA, phi=self.PHI, height=2.8, color=RED, opacity=1.),
            # dict(alpha=0, phi=0, height=2.8, color=RED, opacity=1.),
        ]

        ## from top
        ## 
        masks = [
            ## main body
            {
                'uslice':slice(None, None),
                'vslice':slice(None, None),
                'color':BLUE,
            },
            ## 40x50 : 30x60
            {
                'uslice':uslice_from_deg ( 10,30 ),
                'vslice':vslice_from_deg (40,60),
                'color':ORANGE,
            },
            {
                'uslice':uslice_from_deg ( 30,60 ),
                'vslice':vslice_from_deg (30,80),
                'color':GREEN,
            },
            {
                'uslice':uslice_from_deg ( 60,100 ),
                'vslice':vslice_from_deg (15,110),
                'color':PURE_BLUE,
            },
        ]

        e = always_redraw (  lambda : CCStar ( lines,masks, phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value() , radius_p=1.5, radius_e=2.2 ) )

        # azz  = Arrow3D ( start=ORIGIN, end=[0,0, 1.5*2.2], color=GREEN )
        # auu  = Arrow3D ( start=ORIGIN, end=[-4.0,0.0, 0], color=RED)
        def sphcoord ( r, theta, phi ):
            return r*np.array ( [np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)] )
        obs  = Arrow3D ( start=ORIGIN, end=sphcoord (4.0, self.ZETA, self.PHI), color=BLACK )

        self.add ( 
            e, 
            # azz, 
            # auu, 
            obs 
        )
        # self.wait (duration=1.0)

        r_phi  = _phi.get_value () + ( 10 * TAU )
        r_psi  = _psi.get_value () + (  1 * TAU )
        ## only one precession rotation
        ## 4 spin rotation
        ## 

        self.play ( 
            _phi.animate.set_value ( r_phi ), 
            # self.camera.phi_tracker.animate.set_value( 4*PI/6 ),
            _psi.animate.set_value ( r_psi ),
            rate_func=linear,
            run_time=10
        )

class PrecessionTest(ThreeDScene):
    """

    """
    ZETA  = PI/3
    ALPHA = PI/6
    PHI   = PI
    def construct (self):
        """
        phi is colat?
        theta is azi?
        """
        # self.set_camera_orientation(phi=self.ZETA, theta=PI)
        self.set_camera_orientation(phi=self.ZETA, theta=PI)

        _phi   = ValueTracker ( 0. )
        _theta = ValueTracker ( PI/8 )
        _psi   = ValueTracker ( 0. )

        lines  = [ 
            dict(alpha=self.ALPHA, phi=self.PHI, height=2.8, color=RED, opacity=1.),
            dict(alpha=0, phi=0, height=2.8, color=BLACK, opacity=1.),
        ]

        ## from top
        ## 
        masks = [
            ## main body
            {
                'uslice':slice(None, None),
                'vslice':slice(None, None),
                'color':BLUE,
            },
        ]

        e = always_redraw (  lambda : CCStar ( lines,masks, phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value() , radius_p=1.5, radius_e=2.2, nu=8, nv=16 ) )

        # azz  = Arrow3D ( start=ORIGIN, end=[0,0, 1.5*2.2], color=GREEN )
        # auu  = Arrow3D ( start=ORIGIN, end=[-4.0,0.0, 0], color=RED)
        def sphcoord ( r, theta, phi ):
            return r*np.array ( [np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)] )
        obs  = Arrow3D ( start=ORIGIN, end=sphcoord (4.0, self.ZETA, self.PHI), color=BLACK )

        self.add ( 
            e, 
            # azz, 
            # auu, 
            obs 
        )
        # self.wait (duration=1.0)

        r_phi  = _phi.get_value () + ( 50 * TAU )
        r_psi  = _psi.get_value () + (  1 * TAU )
        ## only one precession rotation
        ## 4 spin rotation
        ## 

        self.play ( 
            _phi.animate.set_value ( r_phi ), 
            # self.camera.phi_tracker.animate.set_value( 4*PI/6 ),
            _psi.animate.set_value ( r_psi ),
            rate_func=linear,
            run_time=10
        )

############################################

class PrecessionSetup(ThreeDScene):
    """
    introducing precession.
    will tell bursts when emission is near observer

    emission RED
    symmetric axis GREEN
    ref axis BLACK
    observer PURE_BLUE

    make observer small for now
    """
    ZETA  = PI/3
    ALPHA = PI/6
    PHI   = PI
    def construct (self):
        """
        phi is colat?
        theta is azi?
        """
        # self.set_camera_orientation(phi=self.ZETA, theta=PI)
        self.set_camera_orientation(phi=self.ZETA, theta=PI)

        _phi   = ValueTracker ( 0. )
        _theta = ValueTracker ( PI/8 )
        _psi   = ValueTracker ( 0. )

        lines  = [ 
            dict(alpha=self.ALPHA, phi=self.PHI, height=2.8, color=RED, opacity=1.),
            dict(alpha=0, phi=0, height=2.8, color=GREEN, opacity=1.),
        ]

        ## from top
        ## 
        masks = [
            ## main body
            {
                'uslice':slice(None, None),
                'vslice':slice(None, None),
                'color':BLUE,
            },
        ]

        e = always_redraw (  lambda : CCStar ( lines,masks, phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value() , radius_p=1.5, radius_e=2.2 ) )

        azz  = Arrow3D ( start=ORIGIN, end=[0,0, 2.8], color=BLACK )
        # auu  = Arrow3D ( start=ORIGIN, end=[-4.0,0.0, 0], color=RED)
        def sphcoord ( r, theta, phi ):
            return r*np.array ( [np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)] )
        ## 1.5 is too large
        ## 0.6 is large
        ## 0.3 is medium
        ## 0.1 is small
        obs  = Arrow3D ( start=ORIGIN, end=sphcoord (4.0, self.ZETA, self.PHI), color=PURE_BLUE, base_radius=0.25 )

        self.add ( 
            e, 
            azz, 
            # auu, 
            obs 
        )
        # self.wait (duration=1.0)

        r_phi  = _phi.get_value () + ( 10 * TAU )
        r_psi  = _psi.get_value () + (  1 * TAU )
        ## only one precession rotation
        ## 4 spin rotation
        ## 

        self.play ( 
            _phi.animate.set_value ( r_phi ), 
            # self.camera.phi_tracker.animate.set_value( 4*PI/6 ),
            _psi.animate.set_value ( r_psi ),
            rate_func=linear,
            run_time=10
        )

class SlowRotationSetup(ThreeDScene):
    """
    introducing slowrotation
    will tell bursts when emission is near observer
    render one rotation and then loop

    emission RED
    symmetric axis GREEN
    ref axis BLACK
    observer PURE_BLUE

    make observer small for now
    """
    ZETA  = PI/3
    ALPHA = PI/3.5
    PHI   = PI
    def construct (self):
        """
        phi is colat?
        theta is azi?
        """
        # self.set_camera_orientation(phi=self.ZETA, theta=PI)
        self.set_camera_orientation(phi=self.ZETA, theta=PI)

        _phi   = ValueTracker ( 0. )
        _theta = ValueTracker ( 0. )
        _psi   = ValueTracker ( 0. )

        lines  = [ 
            dict(alpha=self.ALPHA, phi=self.PHI, height=2.8, color=RED, opacity=1.),
            # dict(alpha=0, phi=0, height=2.8, color=GREEN, opacity=1.),
        ]

        ## from top
        ## 
        masks = [
            ## main body
            {
                'uslice':slice(None, None),
                'vslice':slice(None, None),
                'color':BLUE,
            },
        ]

        e = always_redraw (  lambda : CCStar ( lines,masks, phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value() , radius_p=1.8, radius_e=1.8 ) )

        azz  = Arrow3D ( start=ORIGIN, end=[0,0, 2.8], color=BLACK )
        # auu  = Arrow3D ( start=ORIGIN, end=[-4.0,0.0, 0], color=RED)
        def sphcoord ( r, theta, phi ):
            return r*np.array ( [np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)] )
        ## 1.5 is too large
        ## 0.6 is large
        ## 0.3 is medium
        ## 0.1 is small
        obs  = Arrow3D ( start=ORIGIN, end=sphcoord (4.0, self.ZETA, self.PHI), color=PURE_BLUE, base_radius=0.25 )

        self.add ( 
            e, 
            azz, 
            # auu, 
            obs 
        )
        # self.wait (duration=1.0)

        r_phi  = _phi.get_value () + ( 1 * TAU )
        r_psi  = _psi.get_value () + (  0 * TAU )
        ## only one precession rotation
        ## 4 spin rotation
        ## 

        self.play ( 
            _phi.animate.set_value ( r_phi ), 
            # self.camera.phi_tracker.animate.set_value( 4*PI/6 ),
            # _psi.animate.set_value ( r_psi ),
            rate_func=linear,
            run_time=1
        )

class SlowRotationLowAlpha(ThreeDScene):
    """
    introducing slowrotation
    will tell bursts when emission is near observer
    render one rotation and then loop

    emission RED
    symmetric axis GREEN
    ref axis BLACK
    observer PURE_BLUE

    make observer small for now
    """
    ZETA  = PI/2.5
    ALPHA = PI/6
    PHI   = PI
    def construct (self):
        """
        phi is colat?
        theta is azi?
        """
        # self.set_camera_orientation(phi=self.ZETA, theta=PI)
        self.set_camera_orientation(phi=self.ZETA, theta=PI)

        _phi   = ValueTracker ( 0. )
        _theta = ValueTracker ( 0. )
        _psi   = ValueTracker ( 0. )

        lines  = [ 
            dict(alpha=self.ALPHA, phi=self.PHI, height=2.8, color=RED, opacity=1.),
            # dict(alpha=0, phi=0, height=2.8, color=GREEN, opacity=1.),
        ]

        ## from top
        ## 
        masks = [
            ## main body
            {
                'uslice':slice(None, None),
                'vslice':slice(None, None),
                'color':BLUE,
            },
        ]

        e = always_redraw (  lambda : CCStar ( lines,masks, phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value() , radius_p=1.8, radius_e=1.8 ) )

        azz  = Arrow3D ( start=ORIGIN, end=[0,0, 2.8], color=BLACK )
        # auu  = Arrow3D ( start=ORIGIN, end=[-4.0,0.0, 0], color=RED)
        def sphcoord ( r, theta, phi ):
            return r*np.array ( [np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)] )
        ## 1.5 is too large
        ## 0.6 is large
        ## 0.3 is medium
        ## 0.1 is small
        obs  = Arrow3D ( start=ORIGIN, end=sphcoord (4.0, self.ZETA, self.PHI), color=PURE_BLUE, base_radius=0.25 )

        self.add ( 
            e, 
            azz, 
            # auu, 
            obs 
        )
        # self.wait (duration=1.0)

        r_phi  = _phi.get_value () + ( 1 * TAU )
        r_psi  = _psi.get_value () + (  0 * TAU )
        ## only one precession rotation
        ## 4 spin rotation
        ## 

        self.play ( 
            _phi.animate.set_value ( r_phi ), 
            # self.camera.phi_tracker.animate.set_value( 4*PI/6 ),
            # _psi.animate.set_value ( r_psi ),
            rate_func=linear,
            run_time=1
        )

class SlowRotationHighAlpha(ThreeDScene):
    """
    introducing slowrotation
    will tell bursts when emission is near observer
    render one rotation and then loop

    emission RED
    symmetric axis GREEN
    ref axis BLACK
    observer PURE_BLUE

    make observer small for now
    """
    ZETA  = PI/2.5
    ALPHA = PI/3
    PHI   = PI
    def construct (self):
        """
        phi is colat?
        theta is azi?
        """
        # self.set_camera_orientation(phi=self.ZETA, theta=PI)
        self.set_camera_orientation(phi=self.ZETA, theta=PI)

        _phi   = ValueTracker ( 0. )
        _theta = ValueTracker ( 0. )
        _psi   = ValueTracker ( 0. )

        lines  = [ 
            dict(alpha=self.ALPHA, phi=self.PHI, height=2.8, color=RED, opacity=1.),
            # dict(alpha=0, phi=0, height=2.8, color=GREEN, opacity=1.),
        ]

        ## from top
        ## 
        masks = [
            ## main body
            {
                'uslice':slice(None, None),
                'vslice':slice(None, None),
                'color':BLUE,
            },
        ]

        e = always_redraw (  lambda : CCStar ( lines,masks, phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value() , radius_p=1.8, radius_e=1.8 ) )

        azz  = Arrow3D ( start=ORIGIN, end=[0,0, 2.8], color=BLACK )
        # auu  = Arrow3D ( start=ORIGIN, end=[-4.0,0.0, 0], color=RED)
        def sphcoord ( r, theta, phi ):
            return r*np.array ( [np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)] )
        ## 1.5 is too large
        ## 0.6 is large
        ## 0.3 is medium
        ## 0.1 is small
        obs  = Arrow3D ( start=ORIGIN, end=sphcoord (4.0, self.ZETA, self.PHI), color=PURE_BLUE, base_radius=0.25 )

        self.add ( 
            e, 
            azz, 
            # auu, 
            obs 
        )
        # self.wait (duration=1.0)

        r_phi  = _phi.get_value () + ( 1 * TAU )
        r_psi  = _psi.get_value () + (  0 * TAU )
        ## only one precession rotation
        ## 4 spin rotation
        ## 

        self.play ( 
            _phi.animate.set_value ( r_phi ), 
            # self.camera.phi_tracker.animate.set_value( 4*PI/6 ),
            # _psi.animate.set_value ( r_psi ),
            rate_func=linear,
            run_time=1
        )

############################################
class PrecessionRange(ThreeDScene):
    """
    identify phase range

    emission RED
    symmetric axis GREEN
    ref axis BLACK
    observer PURE_BLUE
    """
    ZETA  = PI/3
    ALPHA = PI/6
    PHI   = PI
    def construct (self):
        """
        phi is colat?
        theta is azi?
        """
        # self.set_camera_orientation(phi=self.ZETA, theta=PI)
        self.set_camera_orientation(phi=self.ZETA, theta=PI)

        _phi   = ValueTracker ( 0. )
        _theta = ValueTracker ( PI/8 )
        _psi   = ValueTracker ( 6. * TAU / 10. )

        lines  = [ 
            dict(alpha=self.ALPHA, phi=self.PHI, height=2.8, color=RED, opacity=1.),
            dict(alpha=0, phi=0, height=2.8, color=GREEN, opacity=1.),
        ]

        ## from top
        ## 
        masks = [
            ## main body
            {
                'uslice':slice(None, None),
                'vslice':slice(None, None),
                'color':BLUE,
            },
        ]

        e = always_redraw (  lambda : CCStar ( lines,masks, phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value() , radius_p=1.5, radius_e=2.2 ) )

        azz  = Arrow3D ( start=ORIGIN, end=[0,0, 2.8], color=BLACK )
        # auu  = Arrow3D ( start=ORIGIN, end=[-4.0,0.0, 0], color=RED)
        def sphcoord ( r, theta, phi ):
            return r*np.array ( [np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)] )
        ## 1.5 is too large
        ## 0.6 is large
        ## 0.3 is medium
        ## 0.1 is small
        obs  = Arrow3D ( start=ORIGIN, end=sphcoord (4.0, self.ZETA, self.PHI), color=PURE_BLUE, base_radius=0.4 )

        self.add ( 
            e, 
            azz, 
            # auu, 
            obs 
        )
        # self.wait (duration=1.0)

        r_phi  = _phi.get_value () + ( 10 * TAU )
        r_psi  = _psi.get_value () + (  3 * TAU / 10 )
        ## only one precession rotation
        ## 4 spin rotation
        ## 

        self.play ( 
            _phi.animate.set_value ( r_phi ), 
            # self.camera.phi_tracker.animate.set_value( 4*PI/6 ),
            _psi.animate.set_value ( r_psi ),
            rate_func=linear,
            run_time=10
        )

class PrecessionAlphaSmall(ThreeDScene):
    """
    make effective alpha small

    emission RED
    symmetric axis GREEN
    ref axis BLACK
    observer PURE_BLUE
    """
    ZETA  = PI/3
    ALPHA = PI/10
    PHI   = PI
    def construct (self):
        """
        phi is colat?
        theta is azi?
        """
        # self.set_camera_orientation(phi=self.ZETA, theta=PI)
        self.set_camera_orientation(phi=self.ZETA, theta=PI)

        _phi   = ValueTracker ( 0. )
        _theta = ValueTracker ( PI/12 )
        _psi   = ValueTracker ( 6 * TAU / 10. )

        lines  = [ 
            dict(alpha=self.ALPHA, phi=self.PHI, height=2.8, color=RED, opacity=1.),
            dict(alpha=0, phi=0, height=2.8, color=GREEN, opacity=1.),
        ]

        ## from top
        ## 
        masks = [
            ## main body
            {
                'uslice':slice(None, None),
                'vslice':slice(None, None),
                'color':BLUE,
            },
        ]

        e = always_redraw (  lambda : CCStar ( lines,masks, phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value() , radius_p=1.5, radius_e=2.2 ) )

        azz  = Arrow3D ( start=ORIGIN, end=[0,0, 2.8], color=BLACK )
        # auu  = Arrow3D ( start=ORIGIN, end=[-4.0,0.0, 0], color=RED)
        def sphcoord ( r, theta, phi ):
            return r*np.array ( [np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)] )
        ## 1.5 is too large
        ## 0.6 is large
        ## 0.3 is medium
        ## 0.1 is small
        obs  = Arrow3D ( start=ORIGIN, end=sphcoord (4.0, self.ZETA, self.PHI), color=PURE_BLUE, base_radius=0.4 )

        self.add ( 
            e, 
            azz, 
            # auu, 
            obs 
        )
        # self.wait (duration=1.0)

        r_phi  = _phi.get_value () + ( 10 * TAU )
        r_psi  = _psi.get_value () + (  3 * TAU / 10 )
        ## only one precession rotation
        ## 4 spin rotation
        ## 

        self.play ( 
            _phi.animate.set_value ( r_phi ), 
            # self.camera.phi_tracker.animate.set_value( 4*PI/6 ),
            _psi.animate.set_value ( r_psi ),
            rate_func=linear,
            run_time=10
        )

class PrecessionAlphaSmallClose(ThreeDScene):
    """
    This is like always ON.

    emission RED
    symmetric axis GREEN
    ref axis BLACK
    observer PURE_BLUE
    """
    ZETA  = PI/8
    ALPHA = PI/10
    PHI   = PI
    def construct (self):
        """
        phi is colat?
        theta is azi?
        """
        # self.set_camera_orientation(phi=self.ZETA, theta=PI)
        self.set_camera_orientation(phi=self.ZETA, theta=PI)

        _phi   = ValueTracker ( 0. )
        _theta = ValueTracker ( PI/12 )
        _psi   = ValueTracker ( 6 * TAU / 10. )

        lines  = [ 
            dict(alpha=self.ALPHA, phi=self.PHI, height=2.8, color=RED, opacity=1.),
            dict(alpha=0, phi=0, height=2.8, color=GREEN, opacity=1.),
        ]

        ## from top
        ## 
        masks = [
            ## main body
            {
                'uslice':slice(None, None),
                'vslice':slice(None, None),
                'color':BLUE,
            },
        ]

        e = always_redraw (  lambda : CCStar ( lines,masks, phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value() , radius_p=1.5, radius_e=2.2 ) )

        azz  = Arrow3D ( start=ORIGIN, end=[0,0, 2.8], color=BLACK )
        # auu  = Arrow3D ( start=ORIGIN, end=[-4.0,0.0, 0], color=RED)
        def sphcoord ( r, theta, phi ):
            return r*np.array ( [np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)] )
        ## 1.5 is too large
        ## 0.6 is large
        ## 0.3 is medium
        ## 0.1 is small
        obs  = Arrow3D ( start=ORIGIN, end=sphcoord (4.0, self.ZETA, self.PHI), color=PURE_BLUE, base_radius=0.9 )

        self.add ( 
            e, 
            azz, 
            # auu, 
            obs 
        )
        # self.wait (duration=1.0)

        r_phi  = _phi.get_value () + ( 10 * TAU )
        r_psi  = _psi.get_value () + (  3 * TAU / 10 )
        ## only one precession rotation
        ## 4 spin rotation
        ## 

        self.play ( 
            _phi.animate.set_value ( r_phi ), 
            # self.camera.phi_tracker.animate.set_value( 4*PI/6 ),
            _psi.animate.set_value ( r_psi ),
            rate_func=linear,
            run_time=10
        )

class PrecessionAlphaSmallAway(ThreeDScene):
    """
    you cannot have arbitrarily large bursting window.

    emission RED
    symmetric axis GREEN
    ref axis BLACK
    observer PURE_BLUE
    """
    ZETA  = PI/1.5
    ALPHA = PI/10
    PHI   = PI
    def construct (self):
        """
        phi is colat?
        theta is azi?
        """
        # self.set_camera_orientation(phi=self.ZETA, theta=PI)
        self.set_camera_orientation(phi=self.ZETA, theta=PI)

        _phi   = ValueTracker ( 0. )
        _theta = ValueTracker ( PI/12 )
        _psi   = ValueTracker ( 6 * TAU / 10. )

        lines  = [ 
            dict(alpha=self.ALPHA, phi=self.PHI, height=2.8, color=RED, opacity=1.),
            dict(alpha=0, phi=0, height=2.8, color=GREEN, opacity=1.),
        ]

        ## from top
        ## 
        masks = [
            ## main body
            {
                'uslice':slice(None, None),
                'vslice':slice(None, None),
                'color':BLUE,
            },
        ]

        e = always_redraw (  lambda : CCStar ( lines,masks, phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value() , radius_p=1.5, radius_e=2.2 ) )

        azz  = Arrow3D ( start=ORIGIN, end=[0,0, 2.8], color=BLACK )
        # auu  = Arrow3D ( start=ORIGIN, end=[-4.0,0.0, 0], color=RED)
        def sphcoord ( r, theta, phi ):
            return r*np.array ( [np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)] )
        ## 1.5 is too large
        ## 0.6 is large
        ## 0.3 is medium
        ## 0.1 is small
        obs  = Arrow3D ( start=ORIGIN, end=sphcoord (4.0, self.ZETA, self.PHI), color=PURE_BLUE, base_radius=0.9 )

        self.add ( 
            e, 
            azz, 
            # auu, 
            obs 
        )
        # self.wait (duration=1.0)

        r_phi  = _phi.get_value () + ( 10 * TAU )
        r_psi  = _psi.get_value () + (  3 * TAU / 10 )
        ## only one precession rotation
        ## 4 spin rotation
        ## 

        self.play ( 
            _phi.animate.set_value ( r_phi ), 
            # self.camera.phi_tracker.animate.set_value( 4*PI/6 ),
            _psi.animate.set_value ( r_psi ),
            rate_func=linear,
            run_time=10
        )

class PrecessionAlphaNoSweetSpot(ThreeDScene):
    """
    you get burst periodicity.

    emission RED
    symmetric axis GREEN
    ref axis BLACK
    observer PURE_BLUE
    """
    ZETA  = PI/4
    ALPHA = PI/10
    PHI   = PI
    def construct (self):
        """
        phi is colat?
        theta is azi?
        """
        # self.set_camera_orientation(phi=self.ZETA, theta=PI)
        self.set_camera_orientation(phi=self.ZETA, theta=PI)

        _phi   = ValueTracker ( 0. )
        _theta = ValueTracker ( PI/12 )
        _psi   = ValueTracker ( 6 * TAU / 10. )

        lines  = [ 
            dict(alpha=self.ALPHA, phi=self.PHI, height=2.8, color=RED, opacity=1.),
            dict(alpha=0, phi=0, height=2.8, color=GREEN, opacity=1.),
        ]

        ## from top
        ## 
        masks = [
            ## main body
            {
                'uslice':slice(None, None),
                'vslice':slice(None, None),
                'color':BLUE,
            },
        ]

        e = always_redraw (  lambda : CCStar ( lines,masks, phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value() , radius_p=1.5, radius_e=2.2 ) )

        azz  = Arrow3D ( start=ORIGIN, end=[0,0, 2.8], color=BLACK )
        # auu  = Arrow3D ( start=ORIGIN, end=[-4.0,0.0, 0], color=RED)
        def sphcoord ( r, theta, phi ):
            return r*np.array ( [np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)] )
        ## 1.5 is too large
        ## 0.6 is large
        ## 0.3 is medium
        ## 0.1 is small
        obs  = Arrow3D ( start=ORIGIN, end=sphcoord (4.0, self.ZETA, self.PHI), color=PURE_BLUE, base_radius=0.45 )

        self.add ( 
            e, 
            azz, 
            # auu, 
            obs 
        )
        # self.wait (duration=1.0)

        r_phi  = _phi.get_value () + ( 10 * TAU )
        r_psi  = _psi.get_value () + (  3 * TAU / 10 )
        ## only one precession rotation
        ## 4 spin rotation
        ## 

        self.play ( 
            _phi.animate.set_value ( r_phi ), 
            # self.camera.phi_tracker.animate.set_value( 4*PI/6 ),
            _psi.animate.set_value ( r_psi ),
            rate_func=linear,
            run_time=10
        )
############################################
