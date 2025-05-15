#!/usr/bin/env python

import numpy as np
from copy import deepcopy
from manimlib.imports import *

CONFIG={
        "name":"Binomial tree", 
        "cat":"Broadcast", 
        "desc":"One node has all the data and shares it with all the other nodes.",
        "ndbs":4,
        "ndbs_x":1, 
        "ndbs_y":4,
        "ncpus":8,
        "ON_opacity":0.8
}
COLOR = [BLUE, RED, ORANGE, PINK, GREEN, YELLOW]

class Coll (Scene):
    """Base class for all coll animations with 8 cpus"""
    global CONFIG
    global COLOR

    def onenode (self, i=0):
        """Creates one CPU+data block with rank i"""
        # text in the box
        tcpu = TextMobject ("CPU")
        tidx = TexMobject ("{0}".format(i))
        tvg  = VGroup (tcpu, tidx).arrange (DOWN)
        # enclosing rectangle
        rcpu = Rectangle (
                height=tvg.get_height()+0.2, 
                width =tvg.get_width() +0.2
        )
        rcpu.add (tvg)
        # data block
        dbwidth = rcpu.get_width() / CONFIG['ndbs_y']
        dbs = [
                Rectangle (
                    height=tcpu.get_height(), 
                    width=rcpu.get_width() / CONFIG['ndbs_y'], 
                    name="db{0}".format(i)
                )
                for i in range (CONFIG['ndbs'])
        ]
        for ix in range (CONFIG['ndbs_x']):
            for iy in range (CONFIG['ndbs_y']):
                if ix == 0 and iy == 0:
                    continue
                ixy = iy + CONFIG['ndbs_y']*ix
                if ix == 0:
                    dbs[ixy].next_to (dbs[ixy-1], RIGHT, buff=0)
                else:
                    dbs[ixy].next_to (dbs[ixy-CONFIG['ndbs_y']], DOWN, buff=0)
        rdb  = VGroup (*dbs)
        return VGroup (rcpu, rdb).arrange (DOWN)

    def ltrx (self, start, stop, idx):
        """start sends stop idx data block linear"""
        rarw = []
        rtrf = []
        for irt, iop, ix in zip (start, stop, idx):
            ia = self.NODES [irt]
            ib = self.NODES [iop]
            ic = COLOR [ix]
            rarw.append (
                    CurvedArrow (
                        ia.get_top(), 
                        ib.get_top(), 
                        angle=-TAU/4, 
                        color=ic
                    )
            )
            cib = ib
            cib[1][ix].set_fill (ic)
            cib[1][ix].set_opacity (0.7)
            rtrf.append (Transform ( 
                    ib, 
                    cib
                )
            )
        return rarw, rtrf

    def construct_Intro (self, rootini=True):
        """Sets up name, category, desc and nodes"""
        name = TextMobject (CONFIG['name'])
        cat  = TextMobject (CONFIG['cat'])
        desc = TextMobject (CONFIG['desc'])
        ncv  = VGroup (name, cat).arrange (DOWN)
        desc.next_to (ncv, DOWN)
        desc.set_width ( FRAME_WIDTH - 2 * MED_LARGE_BUFF)
        desc.set_color (YELLOW)
        # title and stuff
        self.play (Write (cat), Write (desc))
        self.wait (0.2)
        self.play (Write (name))
        self.wait (0.2)
        self.play (
            FadeOut (desc),
            ApplyMethod (name.to_edge, UL),
            ApplyMethod (cat.to_edge,  UP)
        )
        # erect nodes
        self.NODES = VGroup (
            *[self.onenode (i) for i in range(CONFIG['ncpus'])]
        )
        self.NODES.arrange (RIGHT).to_edge (DOWN)
        # adjustments
        if rootini == True:
            self.NODES[0][0].set_color (RED)
        # play
        self.play (
            *map (GrowFromCenter, self.NODES)
        )
        
    def construct_conf(self, di):
        """Loads initial db distro using list of lists"""
        Trf = []
        for icpu,dbs  in enumerate(di):
            ib  = self.NODES[icpu]
            cib = ib
            for idb in dbs:
                cib[1][idb].set_fill (COLOR[idb])
                cib[1][idb].set_opacity (0.7)
            Trf.append (Transform(ib,cib))
        self.play (*Trf)

    def construct_Complexity (self):
        """Sets up complexity"""
        latlab    = TextMobject ("msgs")
        lat  = Integer (0)
        bwlab     = TextMobject ("blks")
        bw   = Integer (0)
        slab      = TextMobject ("steps")
        step   = Integer (0)
        #
        lat.add_updater (lambda d : d.set_value (self.LAT))
        bw.add_updater (lambda d : d.set_value (self.BW))
        step.add_updater (lambda d : d.set_value (self.STEP))
        #
        latv   = VGroup (lat, latlab).arrange(RIGHT)
        bwv    = VGroup (bw,  bwlab).arrange (RIGHT)
        stepv  = VGroup (step,  slab).arrange (RIGHT)
        self.vv  = VGroup (stepv, latv, bwv).arrange (DOWN)
        self.vv.to_edge (UR)
        #
        self.play (FadeIn (self.vv))


    def TransformToCircle (self):
        """Transforms the linear nodes into circle
            
            Get X,Ys of the centers from all the vgroup mobjects,
            convert them into (r cos, r sin) with fixed r for all
            and varying theta.
            Rotate each mobject as well to make orientation perpendicular.

        """
        #TODO Do I really need it?
        pass

    def construct_step (self, starts, stops, idxs, ts=0.1):
        a, t = self.ltrx (starts, stops, idxs)
        va   = VGroup (*a)
        # flatten
        A = map (FadeIn, va)
        B = t
        L = []
        for aa,bb in zip (A,B):
            L.append (aa)
            L.append (bb)
        self.play (LaggedStart (*L))
        # self.wait (10*ts)
        self.wait (ts)
        self.play (*map(FadeOut,va))
        self.wait (ts)

    def incr_com (self, ste, lat, bw):
        """Im just lazy"""
        self.STEP += ste
        self.LAT += lat
        self.BW  += bw

    def construct (self):
        self.construct_Intro ()
        self.wait (0.3)
        self.construct_conf ([  
            [0,1,2,3]
        ])
        self.wait (0.3)
        #
        self.LAT  = 0 
        self.BW   = 0
        self.STEP = 0
        self.construct_Complexity ()
        ##
        s = [0,1,2,3]
        ## START
        self.construct_step (
            [0,0,0,0], [4,4,4,4], s
        )
        self.incr_com (1, 1, 4)
        self.vv.update ()

        self.construct_step (
            [0,0,0,0,4,4,4,4], 
            [2,2,2,2,6,6,6,6], 
            [0,1,2,3,0,1,2,3]
        )
        self.incr_com (1, 2, 8)
        self.vv.update ()
        self.construct_step (
            [0,0,0,0,4,4,4,4,2,2,2,2,6,6,6,6], 
            [1,1,1,1,5,5,5,5,3,3,3,3,7,7,7,7], 
            [0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3]
        )
        self.incr_com (1, 4, 16)
        self.vv.update ()
        
    


