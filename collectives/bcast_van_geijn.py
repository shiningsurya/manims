#!/usr/bin/env python

import numpy as np
from copy import deepcopy
from manimlib.imports import *


CONFIG={
        "name":"van Geijn's", 
        "cat":"Broadcast", 
        "desc":"One node has all the data and shares it with all the other nodes.",
        "ndbs":16,
        "ndbs_x":4, 
        "ndbs_y":4,
        "ncpus":8,
        "ON_opacity":0.8
}
COLOR = [
    BLUE_B, BLUE_C, BLUE_D, BLUE_E,
    GREEN_B, GREEN_C, GREEN_D, GREEN_D,
    RED_B, RED_C, RED_D, RED_E,
    PURPLE_B, PURPLE_C, PURPLE_D, PURPLE_E
]


oSTATE = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8,
    9, 10, 11, 12, 13, 14, 15],
]

INIT_CONF = deepcopy (oSTATE)
# 1
TX = [0,1,2,3,4,5,6,7]
RX = [1,2,3,4,5,6,7,0]

COLOR = [
    BLUE_B, BLUE_C, BLUE_D, BLUE_E,
    GREEN_B, GREEN_C, GREEN_D, GREEN_D,
    RED_B, RED_C, RED_D, RED_E,
    PURPLE_B, PURPLE_C, PURPLE_D, PURPLE_E
]

class Bcast_vanGeijn(Scene):
    """Base class for all coll animations with 8 cpus"""
    global CONFIG
    global COLOR
    global STATE

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
        for irt, iop, ixx in zip (start, stop, idx):
            print ("{0} ---> {1} blks:{2} {3} {4}".format(irt, iop, len(ixx), *ixx))
            ia = self.NODES [irt]
            ib = self.NODES [iop]
            if irt > iop:
                ang = TAU / 3
            else:
                ang = - TAU / 5
            for ix in ixx:
                ic = COLOR [ix]
                rarw.append (
                        CurvedArrow (
                            ia.get_top(), 
                            ib.get_top(), 
                            angle=ang, 
                            color=ic
                        )
                )
                rtrf.append (ApplyMethod( ib[1][ix].set_fill, ic, {'opacity':0.7} ))
                # rtrf.append (ApplyMethod( ib[1][ix].set_fill_opacity, .7))
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
        lat  = Integer (0, edge_to_fix=RIGHT)
        bwlab     = TextMobject ("blks")
        bw   = Integer (0, edge_to_fix=RIGHT)
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
        self.vv  = VGroup (stepv, latv, bwv).arrange (DOWN, buff=SMALL_BUFF)
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
        va = VGroup (*a)
        self.play (*map(ShowCreation, a)) 
        self.wait (2)
        self.play (*t)
        self.play (*map(FadeOut, va))
        self.wait (0.5)
        # self.play (*t)
        # self.play (*map(FadeOut, va))
        print (len(starts), len(stops), len(idxs), len(a), len(t))

    def incr_com (self, ste, lat, bw):
        """Im just lazy"""
        self.STEP += ste
        self.LAT += lat
        self.BW  += bw

    def construct (self):
        self.construct_Intro ()
        self.wait (0.3)
        self.construct_conf ( INIT_CONF )
        self.wait (0.3)
        #
        self.LAT  = 0 
        self.BW   = 0
        self.STEP = 0
        self.construct_Complexity ()
        STATE = [
            [0, 1],
            [2, 3],
            [4, 5],
            [6, 7],
            [8, 9],
            [10, 11],
            [12, 13],
            [14, 15]
        ]
        allSTATE = [
            [0, 1],
            [2, 3],
            [4, 5],
            [6, 7],
            [8, 9],
            [10, 11],
            [12, 13],
            [14, 15]
        ]
        ## Scatter step
        sss = [STATE[ii] for ii in range (1,CONFIG['ncpus'])]
        self.construct_step (
            [0,  0,  0,  0,  0,  0,  0],
            [1,  2,  3,  4,  5,  6,  7],
            sss
        )
        self.incr_com (1, 1, sum([len(i) for i in sss]))
        self.vv.update ()
        ## AllGather
        '''
        THis is almost like Bruck's allgather 
        but all sends to 0 are removed because we don't need them
        --

        And I gave up!
        Took those from bruck
        '''
        # 1
        STEP1_TX = [0,2,3,4,5,6,7]
        STEP1_RX = [7,1,2,3,4,5,6]
        STEP1_DB = [[0, 1], [4, 5], [6, 7], [8, 9], [10, 11], [12, 13], [14, 15]]
        # 2
        STEP2_TX = [0,1,3,4,5,6,7]
        STEP2_RX = [6,7,1,2,3,4,5]
        STEP2_DB = [[0, 1, 2, 3], [2, 3, 4, 5], [6, 7, 8, 9], [8, 9, 10, 11], [10, 11, 12, 13], [12, 13, 14, 15], [14, 15, 0, 1, 2, 3]]
        # 3
        STEP3_TX = [0,1,2,3,5,6,7]
        STEP3_RX = [4,5,6,7,1,2,3]
        STEP3_DB = [[0, 1, 2, 3, 4, 5, 6, 7], [2, 3, 4, 5, 6, 7, 8, 9], [4, 5, 6, 7, 8, 9, 10, 11], [6, 7, 8, 9, 10, 11, 12, 13], [10, 11, 12, 13, 14, 15, 0, 1, 2, 3], [12, 13, 14, 15, 0, 1, 2, 3, 4, 5, 6, 7], [14, 15, 0, 1, 2, 3, 2, 3, 4, 5, 6, 7, 8, 9]]
        ##
        self.construct_step (
            STEP1_TX, STEP1_RX, STEP1_DB
        )
        self.incr_com (1, len(STEP1_TX), sum([len(i) for i in STEP1_DB]))
        self.vv.update ()

        self.construct_step (
            STEP2_TX, STEP2_RX, STEP2_DB
        )
        self.incr_com (1, len(STEP2_TX), sum([len(i) for i in STEP2_DB]))
        self.vv.update ()
        self.construct_step (
            STEP3_TX, STEP3_RX, STEP3_DB
        )
        self.incr_com (1, len(STEP3_TX), sum([len(i) for i in STEP3_DB]))
        self.vv.update ()

