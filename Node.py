#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 25 18:48:05 2020

@author: Hudson Leone and Deepesh Singh
"""

import QNET
import numpy as np
import scipy.integrate
from pvlib import atmosphere
from skyfield.api import EarthSatellite
from skyfield.api import Topos, load


class Qnode:
    """
    Default Qnode Class
    """

    def __init__(self, Q, name=None, coords=None, isMemory=False, **kwargs):
        """
        Qnode Initialization
        :param Q: The Qnet graph intended for the node.
        :param name: The name of the Qnode.
        :param coords: Cartesian coordinates. Usage: [x,y,z]
        :param isMemory: Boolean to describe if the node has quantum memory or not
        :param kwargs: Costs that are valid for the Qnet graph Q.
        """
        if name is None:
            name = "None"
        if coords is None:
            coords = [0]*3
        else:
            assert (len(coords) == 3), "Usage: [x, y, z]"

        # Initialize cost vector
        cost_vector = QNET.make_cost_vector(Q, **kwargs)
        
        # Initialize memory cost vector
        memory_vector = QNET.make_memory_vector(Q, **kwargs)

        self.name = name
        self.coords = coords
        self.costs = cost_vector
        self.memory = memory_vector
        self.isMemory = isMemory

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def update(self, Q, from_default=True, **kwargs):
        """
        Updates the attributes of a given qnode
        :param qnode: Node to be updated
        :param kwargs: Keyword arguements for updating the qnode
        :return: None

        """
        if from_default is True:
            # Set attributes of node to default
            class_name = self.__class__
            dummy_node = class_name(Q, name=self.name)
            for arg in self.__dict__:
                setattr(self, arg, dummy_node.__dict__[arg])

        # For all keyword arguments, check if it exists in the Qnode attributes. If it does, update it.
        args_to_cull = []
        for arg in kwargs:
            if arg in self.__dict__:
                setattr(self, arg, kwargs[arg])
                args_to_cull.append(arg)

        # Remove the kwargs that were used
        for arg in args_to_cull:
            kwargs.pop(arg)

        # Update node.costs with remaining kwargs
        for item in kwargs:
            print(kwargs)
        cost_vector = QNET.make_cost_vector(Q, **kwargs)
        self.costs = cost_vector
        
        # Update node.memory with remaining kwargs
        memory_vector = QNET.make_memory_vector(Q, **kwargs)
        self.memory = memory_vector


class Ground(Qnode):
    def __init__(self, Q, name=None, coords=None, **kwargs):
        """
        Ground Node initialization
        :param str name: Name of Qnode
        :param list coords: Cartesian coordinates. Usage: [x,y,z]
        :param float e: Efficiancy. Proportion of photons that pass through the Qnode
        :param float p: Proportion of surviving photons that haven't changed state
        :param float px: Probability of x-flip (Bitflip)
        :param float py: Probability of y-flip
        :param float pz: Probability of z-flip (Dephasing)
        :param float kwargs: Other costs or qualifying attributes
        """
        super().__init__(Q, name, coords, **kwargs)


class Satellite(Qnode):
    def __init__(self, Q, name=None, coords=None, t=0, v_cart=None, line1=None,
                 line2=None, cartesian=True, **kwargs):
        """
        Intialises the satellite class. If cartesian == True, satellite coordinates will be cartesian and  it will
        travel in a fixed plane.
        Else the satellite will be initalised with the given TLEs with geodesic coordinates.
        If either TLE is invalid or None, the satellite defaults to ISS Zarya with geodesic coordinates

        Parameters
        ----------
        name : String
            Name of the satellite. The default is None.
        coords : Array of floats
            Coords of satellite, usage [x,y,z]. The default is [0,0,0].
        e : float
            Efficiancy. The default is 1.
        p : float
            Proportion of surviving photons that haven't changed state. The default is 1.
        px : float
            Probability of x-flip (Bitflip). The default is 0.
        py : float
            Probability of y-flip. The default is 0.
        pz : float
            Probability of z-flip (Dephasing). The default is 0.
        t : float
            Time (in seconds) ahead of the current time from which the satellite is started being tracked. The default is 0.
        v_cart: Array of floats
            Cartesian velocity of Satellite.
        line1 : String
            Line 1 of TLE of the satellite to be added in the network. The default is ''.
        line2 : String
            Line 2 of TLE of the satellite to be added in the network. The default is ''.
        **kwargs : TYPE
            Other costs or qualifying attributes.

        Returns
        -------
        None.

        """
        # Initialise coordinate type
        self.cartesian = cartesian
        
        super().__init__(Q, name, coords, **kwargs)


        if cartesian is True:
            if v_cart is None:
                v_cart = [0]*2
            else:
                assert len(v_cart) == 2
            self.velocity = v_cart
            super().__init__(Q, name, coords, **kwargs)

        else:
            ## Define the time at which the satellite is being tracked ##
            ts = load.timescale()
            t_now = ts.now()
            t_startTime = ts.utc(t_now.utc[0], t_now.utc[1], t_now.utc[2], t_now.utc[3], t_now.utc[4], t_now.utc[5] + t)
            t_new = t_startTime

            ## Initialise which satellite to track. Default is ISS Zarya ##
            try:
                satellite = EarthSatellite(line1, line2, self.name, ts)
                geometry = satellite.at(t_new)
                subpoint = geometry.subpoint()
                self.coords = [int(subpoint.latitude.degrees), int(subpoint.longitude.degrees),
                               int(subpoint.elevation.km)]
            except:
                # Add ISS Zarya to the network by default if the given TLE is invalid
                # l1 and l2 are TLE of ISS Zarya
                l1 = '1 25544U 98067A   20154.85125762  .00002004  00000-0  43906-4 0  9990'
                l2 = '2 25544  51.6443  59.4222 0002071  22.0017  92.6243 15.49416742229799'
                satellite = EarthSatellite(l1, l2, self.name, ts)
                geometry = satellite.at(t_new)
                subpoint = geometry.subpoint()
                geo_coords = [int(subpoint.latitude.degrees), int(subpoint.longitude.degrees),
                              int(subpoint.elevation.km)]
                super().__init__(Q, name, geo_coords, **kwargs)

            # TODO: Write descriptions for these variables here
            self.ts = ts
            self.t_now = t_now
            self.t_startTime = t_startTime
            self.t_new = t_new
            self.satellite = satellite

            print(t_now.utc)

    def posUpdate(self, dt):
        if self.cartesian is True:
            vx = self.velocity[0]
            vy = self.velocity[1]
            self.coords = [self.coords[0] + vx * dt, self.coords[1] + vy * dt, self.coords[2]]

        else:
            self.t_new = self.ts.utc(self.t_new.utc[0], self.t_new.utc[1], self.t_new.utc[2], self.t_new.utc[3],
                                     self.t_new.utc[4], self.t_new.utc[5] + dt)
            geometry = self.satellite.at(self.t_new)
            subpoint = geometry.subpoint()
            self.coords = [int(subpoint.latitude.degrees), int(subpoint.longitude.degrees), int(subpoint.elevation.km)]

        return

    def setTime(self):
        '''
        Restart tracking the satellite. 
        
        Reset the time to the start time after function: QNET.update(dt) has been applied in some process

        Returns
        -------
        None.

        '''
        self.t_new = self.t_startTime
        return

    def cart_distance(self, node):
        sx, sy, sz = self.coords
        x, y, z = node.coords
        return np.sqrt((x - sx) ** 2 + (y - sy) ** 2 + (z - sz) ** 2)

    def distance(self, node):
        if self.cartesian is True:
            sx, sy, sz = self.coords
            x, y, z = node.coords
            return np.sqrt((x - sx) ** 2 + (y - sy) ** 2 + (z - sz) ** 2)

        else:
            node_location = Topos(float(node.coords[0]), float(node.coords[1]))
            difference = self.satellite - node_location
            topocentric = difference.at(self.t_new)
            alt, az, distMagnitude = topocentric.altaz()
            return int(distMagnitude.km / 1000)

    def airCost(self, node):
        """
        :param Qnode() node: The target node for the satellite communication
        :return list: [e, p] -- [Transmission probability, phasing probability]
        """

        if self.cartesian is True:
            # Straight line distance between nodes
            dist = self.cart_distance(node)
            # Difference in altitude
            dz = self.coords[2] - node.coords[2]
            assert (dz > 0), f"Satellite altitude [{self.coords[2]}] must be greater than node altitude. [{node.coords[2]}]"
            # Altitude angle
            theta = np.arcsin(dz / dist)

        else:
            node_location = Topos(float(node.coords[0]), float(node.coords[1]))
            difference = self.satellite - node_location
            topocentric = difference.at(self.t_new)
            alt, az, dist1 = topocentric.altaz()
            theta = alt.degrees
            dist = self.distance(node)

        """
        Line integral for effective density
            
          / L'
         |     rho(L * sin(theta)) dL
        /   0
        """

        def rho(L, theta):

            # From altitude, calculate pressure
            # Assume T = 288.15K and 0% humidity
            P = atmosphere.alt2pres(L * np.sin(theta))
            T = 288.15
            R = 287.058  # Specific gas constant of air
            return P / (R * T)

        # Perform numerical integration to get effective density (?)
        # d = scipy.integrate.quad(rho, 0, int(dist.km/1000), args = (theta))[0]
        d = scipy.integrate.quad(rho, 0, dist, args=(theta))[0]

        def get_efficiency(d):
            """
            Calculate efficiency for the transmission given effective density
            :param float d: Effective density
            :return float: "p" Probability of survival
            """

            # Attenuation coefficient
            K = 0.005
            return np.exp(-K*d)
            # return QNET.convert(d * K, 'linear')

        def get_fidelity(d):
            """
            Calculate fidelity for the transmission given effective density
            :param float d: Effective density
            :return float: "e" probability of no phase flip.
            """

            # Attenuation coefficient
            K = 0.005
            return (1 + np.exp(-K*d))/2
            # return QNET.convert(d * K, 'linear')

        ## Check if satellite is above the horizon before making an edge ##
        '''
        if alt.degrees>0:
            results = [transmission_probability(d), phasing_probability(d)]
        else:
            results = [0,0]
        '''

        results = [get_efficiency(d), get_fidelity(d)]

        return results

class Swapper(Qnode):
    # prob is probability of succesful swapping between nodes
    def __init__(self, Q, name=None, coords=None, swap_prob=0.5, **kwargs):
        assert Q is not None
        assert swap_prob >= 0.5
        self.swap_prob = swap_prob
        super().__init__(Q, name, coords, **kwargs)
        
        
class Memory(Qnode):
    def __init__(self, Q, name=None, coords=None, mem_e = 1, mem_f=1, **kwargs):
        #assert Q is not None
        #assert swap_prob >= 0.5
        #self.swap_prob = swap_prob
        super().__init__(Q, name, coords, **kwargs)       
        
        self.t_memory = 0
        
    def timeUpdate(self, dt):
        self.t_memory = self.t_memory + dt
        return
    