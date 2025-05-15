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
    def __init__ (self, alpha, phi, theta, psi, radius_p, radius_e, ures=12, vres=12, **kwargs):
        """
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
        self.rot = np.array ( [
            [cpsi*cphi - spsi*ctheta*sphi, -cpsi*sphi - spsi*ctheta*cphi, spsi*stheta ],
            [spsi*cphi + cpsi*ctheta*sphi, -spsi*sphi + cpsi*ctheta*cphi, -cpsi*stheta],
            [stheta*sphi, stheta*cphi, ctheta]
        ])

        ##
        ## 
        ## call before
        super().__init__(**kwargs)

        ##
        star  = self.get_star (radius_p=radius_p, radius_e=radius_e)
        star.set_fill ( color=BLUE, opacity=1.0 )
        star.set_stroke ( color=BLUE, opacity=0.5, width=0.5 )
        self.add(*star)

        line0  = self.get_arrow_line ()
        line0.set_fill ( color=RED, opacity=1.0 )
        line0.set_stroke ( color=RED, opacity=0.5, width=0.5 )
        self.add(*line0)

        line1  = self.get_arrow_line (alpha=alpha, phi=0.5*PI)
        line1.set_fill ( color=BLUE, opacity=1.0 )
        line1.set_stroke ( color=BLUE, opacity=0.5, width=0.5 )
        self.add(*line1)

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

    def get_line (self, alpha=0., phi=0., hres=10, pres=10, radius=0.02, height=2.0):
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

    def get_arrow_line (self, alpha=0., phi=0., hres=10, pres=10, cres=8, radius=0.02, height=2.0, cheight=0.25, ctheta=PI/8):
        """
        returns a VGroup

        arrow means there is a cone at the end
        cone is radius and phi
        """
        afaces = VGroup ()
        ##
        cphi, sphi     = np.cos(phi), np.sin(phi)
        calpha, salpha = np.cos(alpha), np.sin(alpha)
        irot    = np.array ( [
            [ cphi, -sphi*calpha, sphi*salpha ],
            [ sphi, cphi*calpha, -cphi*salpha ],
            [0, salpha, calpha],
        ] )
        rot    = self.rot @ irot
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
