#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    *** Default Divergence ***
    Copyright (C) November 2021 Francesco Camaglia, LPENS 
    Following the architecture of J. Hausser and K. Strimmer : https://strimmerlab.github.io/software/entropy/
'''

import numpy as np 

from . import cmw_divergence

# loagirthm unit
_unit_Dict_ = { "ln": 1., "log2": 1./np.log(2), "log10": 1./np.log(10) }


#################
#  SWITCHBOARD  #
#################

def switchboard( compACT, method="naive", unit=None, measure="Kullback-Leibler", **kwargs ):

    # loading units
    if unit in _unit_Dict_.keys( ) :
        unit_conv = _unit_Dict_[ unit ]
    else:
        raise IOError("Unknown unit, please choose amongst ", _unit_Dict_.keys( ) )

    # check measure 
    if measure not in ["Kullback-Leibler", "Jensen-Shannon"] :
        raise IOError("Choose `measure` between `Kullback-Leibler` and `Jensen-Shannon`.")

    # choosing entropy estimation method
    if method == "naive":                       # Naive
        dkl_estimate = Naive( compACT, measure=measure, **kwargs )
    
    elif method == "CMW":                       # Camaglia Mora Walczak
        if measure != "Kullback-Leibler" :
            raise IOError("Unknown method `CMW` for the chosen measure.")
        dkl_estimate = cmw_divergence.CamagliaMoraWalczak( compACT, **kwargs )
    
    elif method == "Jeffreys":                  # Jeffreys
        a = 0.5
        b = 0.5
        dkl_estimate = Dirichlet( compACT, a, b, measure=measure, **kwargs )
    
    elif method == "Laplace":                   # Laplace
        a = 1.
        b = 1.
        dkl_estimate = Dirichlet( compACT, a, b, measure=measure, **kwargs )
    
    elif method == "SG":                        # Schurmann-Grassberger
        a = 1. / compACT.compact_A.Kobs
        b = 1. / compACT.compact_B.Kobs
        dkl_estimate = Dirichlet( compACT, a, b, measure=measure, **kwargs )
        
    elif method == "minimax":                   # minimax
        a = np.sqrt( compACT.N_A ) / compACT.compact_A.Kobs
        b = np.sqrt( compACT.N_B ) / compACT.compact_B.Kobs
        dkl_estimate = Dirichlet( compACT, a, b, measure=measure, **kwargs )
        
    else:
        raise IOError("The chosen method is unknown.")

    return unit_conv * dkl_estimate
###



###########
#  NAIVE  #
###########

def Naive( compACT, measure="Kullback-Leibler", ) :
    '''
    Replacing probabilities with frequencies without considering categories not seen in one of the two.
    '''
    
    # loading parameters from compACT 
    N_A, N_B = compACT.N_A, compACT.N_B
    # delete 0 counts
    gtr0mask = np.logical_and( compACT.nn_A > 0, compACT.nn_B > 0 )
    nn_A, nn_B, ff = compACT.nn_A[gtr0mask], compACT.nn_B[gtr0mask], compACT.ff[gtr0mask]
    
    hh_A = nn_A / N_A                  # frequencies
    hh_B = nn_B / N_B                  # frequencies
    
    if measure == "Kullback-Leibler" :                       
        output = np.dot ( ff, hh_A * np.log( hh_A / hh_B ) )
    elif measure == "Jensen-Shannon" :
        mm_AB = 0.5 * ( hh_A + hh_B )
        output = 0.5 * np.dot ( ff, hh_A * np.log( hh_A / mm_AB ) + hh_B * np.log( hh_B / mm_AB ) )
    else :
        raise IOError("Choose `measure` between `Kullback-Leibler` and `Jensen-Shannon`.")

    return np.array( output )

##########################
#  DIRICHELET ESTIMATOR  #
##########################

def Dirichlet( compACT, a, b, measure="Kullback-Leibler",  ):
    '''
    Estimate Kullback-Leibler with Dirichlet-multinomial pseudocount model.
    
    Parameters
    ----------  
    a: float
    b: float
        Pseudocount per bin (Dirichlet parameter)
        (e.g.)
        a=1 , b=1                            :   Laplace
        a=1/2 , b=1/2                        :   Jeffreys
        a=1/Kobs , b=1/Kobs                  :   Schurmann-Grassberger  (Kobs: number of bins)
        a=sqrt(N_A)/Kobs , b=sqrt(N_B)/Kobs  :   minimax
    '''

    # loading parameters from compACT 
    N_A, N_B = compACT.N_A, compACT.N_B
    # delete 0 counts
    nn_A, nn_B, ff = compACT.nn_A, compACT.nn_B, compACT.ff

    nn_A_a = nn_A + a                   # counts plus pseudocounts
    nn_B_b = nn_B + b                   # counts plus pseudocounts                                   
    N_A_a = N_A + a * np.sum( ff )      # total number of counts plus pseudocounts               
    N_B_b = N_B + b * np.sum( ff )      # total number of counts plus pseudocounts
    
    hh_A_a = nn_A_a / N_A_a             # frequencies
    hh_B_b = nn_B_b / N_B_b             # frequencies
     
    if measure == "Kullback-Leibler" :                               
        output = np.dot( ff, hh_A_a * np.log( hh_A_a / hh_B_b ) )
    elif measure == "Jensen-Shannon" :
        mm_AB_ab = 0.5 * ( hh_A_a + hh_B_b )
        output = 0.5 * np.dot ( ff, hh_A_a * np.log( hh_A_a / mm_AB_ab ) + hh_B_b * np.log( hh_B_b / mm_AB_ab ) )
    else :
        raise IOError("Choose `measure` between `Kullback-Leibler` and `Jensen-Shannon`.")

    return np.array( output )
###
