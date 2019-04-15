#!/usr/bin/env python3
#
# Pints Boundaries that limit the transition rates in the Beattie et al model.
#
from __future__ import division, print_function
import numpy as np
import pints


class Boundaries(pints.Boundaries):
    """
    Boundary constraints on the parameters.
    """
    def __init__(self, lower_conductance, transformation=None,
                 conductance=True):
        super(Boundaries, self).__init__()

        # Include conductance parameter
        self._conductance = True if conductance else False

        # Conductance limits
        self.lower_conductance = lower_conductance
        self.upper_conductance = 10 * lower_conductance

        # Limits on p1-p8
        self.lower_alpha = 1e-7              # Kylie: 1e-7
        self.upper_alpha = 1e3               # Kylie: 1e3
        self.lower_beta  = 1e-7              # Kylie: 1e-7
        self.upper_beta  = 0.4               # Kylie: 0.4

        # Lower and upper bounds for all parameters
        self.lower = [
            self.lower_alpha,
            self.lower_beta,
            self.lower_alpha,
            self.lower_beta,
            self.lower_alpha,
            self.lower_beta,
            self.lower_alpha,
            self.lower_beta,
        ]
        self.upper = [
            self.upper_alpha,
            self.upper_beta,
            self.upper_alpha,
            self.upper_beta,
            self.upper_alpha,
            self.upper_beta,
            self.upper_alpha,
            self.upper_beta,
        ]

        if self._conductance:
            self.lower.append(self.lower_conductance)
            self.upper.append(self.upper_conductance)

        self.lower = np.array(self.lower)
        self.upper = np.array(self.upper)

        # Limits on maximum reaction rates
        self.rmin = 1.67e-5
        self.rmax = 1000

        # Voltages used to calculate maximum rates
        self.vmin = -120
        self.vmax =  60

        # Optional transformation
        self.transformation = transformation

    def n_parameters(self):
        return 9 if self._conductance else 8

    def check(self, parameters):

        debug = False

        # Transform parameters back to model space
        if self.transformation is not None:
            parameters = self.transformation.detransform(parameters)

        # Check parameter boundaries
        if np.any(parameters < self.lower):
            if debug: print('Lower')
            return False
        if np.any(parameters > self.upper):
            if debug: print('Upper')
            return False

        # Check maximum rate constants
        p1, p2, p3, p4, p5, p6, p7, p8 = parameters[:8]

        # Check positive signed rates
        r = p1 * np.exp(p2 * self.vmax)
        if r < self.rmin or r > self.rmax:
            if debug: print('r1')
            return False
        r = p5 * np.exp(p6 * self.vmax)
        if r < self.rmin or r > self.rmax:
            if debug: print('r2')
            return False

        # Check negative signed rates
        r = p3 * np.exp(-p4 * self.vmin)
        if r < self.rmin or r > self.rmax:
            if debug: print('r3')
            return False
        r = p7 * np.exp(-p8 * self.vmin)
        if r < self.rmin or r > self.rmax:
            if debug: print('r4')
            return False

        return True

    def _sample_partial(self, v):
        """
        Sample a pair of parameters - uniformly in the transformed space - that
        satisfy the maximum transition rate constraints.
        """
        for i in range(100):
            a = np.exp(np.random.uniform(
                np.log(self.lower_alpha), np.log(self.upper_alpha)))
            b = np.random.uniform(self.lower_beta, self.upper_beta)
            r = a * np.exp(b * v)
            if r >= self.rmin and r <= self.rmax:
                return a, b
        raise ValueError('Too many iterations')

    def sample(self, n=1):

        if n > 1:
            raise NotImplementedError

        p = np.zeros(9 if self._conductance else 8)

        # Sample forward rates
        p[0:2] = self._sample_partial(self.vmax)
        p[4:6] = self._sample_partial(self.vmax)

        # Sample backward rates
        p[2:4] = self._sample_partial(-self.vmin)
        p[6:8] = self._sample_partial(-self.vmin)

        # Sample conductance
        if self._conductance:
            p[8] = np.random.uniform(
                self.lower_conductance, self.upper_conductance)

        # Transform from model to search space, if required
        if self.transformation is not None:
            p = self.transformation.transform(p)

        # The Boundaries interface requires a matrix ``(n, n_parameters)``
        p.reshape(1, 9 if self._conductance else 8)
        return p

