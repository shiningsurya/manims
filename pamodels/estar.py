
from manim import *

from manim.typing import Point3D, Vector3D
from manim.utils.color import BLUE, BLUE_D, BLUE_E, LIGHT_GREY, WHITE, interpolate_color

from typing import Any, Callable, Iterable, Sequence

class Ellipsoid(Surface):
    """A three-dimensional ellipsoid.

    Parameters
    ----------
    center
        Center of the :class:`Sphere`.
    equitorial_radius
        The radius of the :class:`Sphere`.
    polar_radius 
        The radius of the :class:`Sphere`.
    resolution
        The number of samples taken of the :class:`Sphere`. A tuple can be used
        to define different resolutions for ``u`` and ``v`` respectively.
    u_range
        The range of the ``u`` variable: ``(u_min, u_max)``.
    v_range
        The range of the ``v`` variable: ``(v_min, v_max)``.

    Examples
    --------

    .. manim:: ExampleSphere
        :save_last_frame:

        class ExampleSphere(ThreeDScene):
            def construct(self):
                self.set_camera_orientation(phi=PI / 6, theta=PI / 6)
                sphere1 = Sphere(
                    center=(3, 0, 0),
                    radius=1,
                    resolution=(20, 20),
                    u_range=[0.001, PI - 0.001],
                    v_range=[0, TAU]
                )
                sphere1.set_color(RED)
                self.add(sphere1)
                sphere2 = Sphere(center=(-1, -3, 0), radius=2, resolution=(18, 18))
                sphere2.set_color(GREEN)
                self.add(sphere2)
                sphere3 = Sphere(center=(-1, 2, 0), radius=2, resolution=(16, 16))
                sphere3.set_color(BLUE)
                self.add(sphere3)
    """

    def __init__(
        self,
        center: Point3D = ORIGIN,
        equitorial_radius : float = 1.4,
        polar_radius : float = 1.0,
        # euler angles
        phi : float = PI / 3,
        theta : float = PI / 8,
        psi : float = PI / 3,
        resolution: Sequence[int] | None = None,
        u_range: Sequence[float] = (0, TAU),
        v_range: Sequence[float] = (0, PI),
        **kwargs,
    ) -> None:
        if config.renderer == RendererType.OPENGL:
            res_value = (101, 51)
        elif config.renderer == RendererType.CAIRO:
            res_value = (24, 12)
        else:
            raise Exception("Unknown renderer")

        resolution = resolution if resolution is not None else res_value

        self.radius_e = equitorial_radius
        self.radius_p = polar_radius

        cphi, sphi     = np.cos ( phi ), np.sin ( phi )
        ctheta, stheta = np.cos ( theta ), np.sin ( theta )
        cpsi, spsi     = np.cos ( psi ), np.sin ( psi )
        self.rot = np.array ( [
            [cpsi*cphi - spsi*ctheta*sphi, -cpsi*sphi - spsi*ctheta*cphi, spsi*stheta ],
            [spsi*cphi + cpsi*ctheta*sphi, -spsi*sphi + cpsi*ctheta*cphi, -cpsi*stheta],
            [stheta*sphi, stheta*cphi, ctheta]
        ])

        super().__init__(
            self.func,
            resolution=resolution,
            u_range=u_range,
            v_range=v_range,
            **kwargs,
        )

        self.shift(center)

    def func(self, u: float, v: float) -> np.ndarray:
        """The z values defining the :class:`Sphere` being plotted.

        Returns
        -------
        :class:`numpy.array`
            The z values defining the :class:`Sphere`.
        """
        return self.rot @ np.array(
            [self.radius_e * np.cos(u) * np.sin(v), self.radius_e * np.sin(u) * np.sin(v), -self.radius_p * np.cos(v)],
        )

class TestE(ThreeDScene):
    def construct (self):
        self.set_camera_orientation(phi=PI/3, theta=PI/3)

        _phi   = ValueTracker ( 0. )
        _theta = ValueTracker ( PI / 8 )
        _psi   = ValueTracker ( 0. )

        e = always_redraw (  lambda : Ellipsoid ( phi=_phi.get_value(), theta=_theta.get_value(), psi=_psi.get_value() ) )

        self.add ( e )
        self.wait (2)

        self.play ( 
            _phi.animate.set_value ( 8*TAU ), 
            _psi.animate.set_value ( 2*TAU ),
            rate_func=linear,
            run_time=16
        )
