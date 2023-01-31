#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Copyright (C) November 2022 Francesco Camaglia, LPENS 
'''

import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .beta_func_multivar import Experiment_Compact, Divergence_Compact
from . import default_divergence, default_entropy

class Skeleton_Class :
    ''' Auxiliary class for Experiment and Divergence.'''

    def _update_categories( self, categories ):
        '''Change the number of categories.

        Parameters
        ----------        
        categories : scalar
                The new number of categories of the system (int or float). 
                If the value is lower than the observed number of categories, 
                the observed number is used instead.'''

        obs_n_categ = np.max(self.obs_n_categ)
        if categories is None:
            self.usr_n_categ = obs_n_categ    
        else :
            try : 
                categories = int( categories )
            except :        
                raise TypeError("The parameter `categories` must be an integer.")
            if categories > obs_n_categ :
                self.usr_n_categ = categories
            else :
                self.usr_n_categ = obs_n_categ 
                if categories < obs_n_categ :
                    warnings.warn("The parameter `categories` is set equal to the observed number of categories.")
    
    def show( self ):
        '''Print a short summary.'''
        
        print("Total n. of counts:")
        if type(self.tot_counts) == pd.Series :
            print(self.tot_counts.to_string())
        else :
            print(self.tot_counts)
            
        print("N. of Categories:")
        print(self.obs_n_categ, ' (observed)')
        print(self.usr_n_categ, ' (a priori)')
        
        print("Recurrencies:")
        print(self.counts_hist)
    
######################
#  EXPERIMENT CLASS  #
######################

class Experiment( Skeleton_Class ) :
    '''A class for entropy estimation from data distribution.
    
    Methods
    -------
    entropy( method="naive", unit="ln", **kwargs )
        Estimate Shannon entropy.'''

    __doc__ += Skeleton_Class.__doc__
    
    def __init__( self, data_hist, categories=2, ishist=True ):
        '''
        Parameters
        ----------    
        data_hist : Union[dict, pd.DataFrame, pd.Series, list, np.array] 
            The number of observations for each category or a raw list of observations (deprecated).
        categories : scalar, optional
            The a priori total number of categories.
        ishist : bool
            When `data_hist` is a list of integers, it specifies wheter it is a histogram (True, default) 
            or a raw list of observations (False, deprecated).
        '''
        
        #  Load data_hist #
        if type( data_hist ) == dict :   
            # loading dictionary where values represent keys counts                                    
            data_hist = pd.Series( data_hist )
        elif type( data_hist ) == pd.DataFrame :
            # loading datafame where values represent keys counts 
            if len( data_hist.columns ) > 1 :
                warnings.warn("The parameter `data` contained multiple columns, only the first one is considered.")
            data_hist = data_hist[ data_hist.columns[0] ]
        elif type( data_hist ) == pd.Series :
            # loading series where values represent index counts
            data_hist = data_hist
        elif type( data_hist ) == list or type( data_hist ) == np.ndarray :                              
            if ishist == True :
                # loading list of counts
                data_hist = pd.Series( data_hist ).astype(int)
            else :
                # loading raw list of sequences
                temp = pd.Series( data_hist )
                data_hist = temp.groupby( temp ).size()
        else :
            raise TypeError("The parameter `data` has unsopported type.")

        # check int counts 
        try :
            data_hist = data_hist.astype(int)
        except ValueError :
            # WARNING! : this try/except doesn't looks nice
            raise ValueError("Unrecognized count value in `data`.")    

        self.data_hist = data_hist
        # total n. of counts
        self.tot_counts = np.sum( data_hist.values )  
        # n. of observed categories
        self.obs_n_categ = (data_hist > 0).sum() 
        # frquencies of observed counts
        temp = pd.Series( data_hist.values ).astype(int)

        self.counts_hist = temp.groupby( temp ).size()  
        self.counts_hist.name = "freq"
        # n. of coincidences
        self.obs_coincedences = self.counts_hist[ self.counts_hist.index > 1 ].sum()

        #  Load categories  #
        categories = np.max([categories, len(data_hist)])
        self._update_categories( categories )

        if self.usr_n_categ > self.obs_n_categ :
            self.counts_hist[ 0 ] = self.usr_n_categ - self.obs_n_categ
            self.counts_hist = self.counts_hist.sort_index(ascending=True) 

    def shannon( self, method="naive", unit="ln", **kwargs ):
        # create an alias to use for clarity
        __doc__ = self.entropy.__doc___

        return self.entropy( method=method, unit=unit, **kwargs)

    def entropy( self, method="naive", unit="ln", **kwargs ):
        '''Estimate Shannon entropy.

        Shannon entropy estimation through a chosen `method`.
        The unit (of the logarithm) can be specified with the parameter `unit`.
            
        Parameters
        ----------
        method: str
            the name of the entropy estimation method:
            - "naive": naive estimator (default);
            - "MM": Miller Madow estimator;
            - "CS": Chao Shen estimator;       
            - "shrink": shrinkage estimator;       
            - "Jeffreys": Jeffreys estimator;
            - "Laplace": Laplace estimator;
            - "SG": Schurmann-Grassberger estimator;
            - "minimax": minimax estimator;
            - "NSB": Nemenman Shafee Bialek estimator.
        unit: str, optional
            the entropy logbase unit:
            - "ln": natural logarithm (default);
            - "log2": base 2 logarihtm;
            - "log10":base 10 logarithm.

        return numpy.array
        '''
        
        return default_entropy.switchboard( self.compact(), which="Shannon", method=method, unit=unit, **kwargs )
    
    def simpson( self, method="naive", **kwargs ):
        '''Estimate Simpson index.

        Simpson infrx estimation through a chosen `method`.
        The unit (of the logarithm) can be specified with the parameter `unit`.
            
        Parameters
        ----------
        method: str
            the name of the entropy estimation method:
            - "naive": naive estimator (default);
            - "MM": Miller Madow estimator;
            - "CS": Chao Shen estimator;       
            - "shrink": shrinkage estimator;       
            - "Jeffreys": Jeffreys estimator;
            - "Laplace": Laplace estimator;
            - "SG": Schurmann-Grassberger estimator;
            - "minimax": minimax estimator;
            - "NSB": Nemenman Shafee Bialek estimator.
        unit: str, optional
            the entropy logbase unit:
            - "ln": natural logarithm (default);
            - "log2": base 2 logarihtm;
            - "log10":base 10 logarithm.

        return numpy.array
        '''
        
        return default_entropy.switchboard( self.compact(), which="Simpson", method=method, **kwargs )
    
    def compact( self ) :
        '''It provides aliases for computations.'''
        return Experiment_Compact( source=self )

    def rank_plot( self, figsize=(3,3), color="#ff0054", xlabel="rank", ylabel="frequency", grid=True, logscale=True) :
        '''Rank plot.'''
        return experiment_rank_plot( self, figsize=figsize, color=color, xlabel=xlabel, ylabel=ylabel, logscale=logscale, grid=grid)
     
    def save_compact( self, filename ) :
        '''It saves the compact features of Experiment to `filename`.'''
        self.compact( )._save( filename )


######################
#  DIVERGENCE CLASS  #
######################

class Divergence( Skeleton_Class ) :
    
    '''The basic class for estimating divergence between two dataset distributions.

    Methods
    -------
    jensen_shannon( method="naive", unit="ln", **kwargs ):
        Estimate Jensen-Shannon divergence.
    kullback_leibler( method="naive", unit="ln", **kwargs )
        Estimate Kullback-Leibler divergence.'''

    __doc__ += Skeleton_Class.__doc__

    def __init__( self, my_exp_1, my_exp_2, categories=None, ) :
        '''
        Parameters
        ----------    
        my_exp_1 : class Experiment
            the first dataset.
        my_exp_2 : class Experiment
            the second dataset.
        '''

        if type( my_exp_1 ) != Experiment :
            my_exp_1 = Experiment( my_exp_1, categories=categories )
        if type( my_exp_2 ) != Experiment :
            my_exp_2 = Experiment( my_exp_2, categories=categories )

        self.tot_counts = pd.Series(
            {"Exp-1": my_exp_1.tot_counts,
            "Exp-2": my_exp_2.tot_counts}
            )

        df = pd.concat( [my_exp_1.data_hist, my_exp_2.data_hist], axis=1 )
        df = df.replace(np.nan, 0).astype(int)
        df.columns = ["Exp-1", "Exp-2"]
        self.data_hist = df

        # Observed Categories
        self.obs_n_categ = pd.Series(
            {"Exp-1": my_exp_1.obs_n_categ,
            "Exp-2":my_exp_2.obs_n_categ,
            "Union":len(self.data_hist.loc[(df>0).any(axis=1)])}
            )
        # User Stated Categories
        categories = np.max([my_exp_1.usr_n_categ, my_exp_2.usr_n_categ, self.obs_n_categ["Union"]])
        self._update_categories( categories )

        # Counts Histogram
        self.counts_hist = df.groupby(by=["Exp-1", "Exp-2"]).size()
        self.counts_hist.name = "freq"
        # add (0,0) to counts_hist
        if self.usr_n_categ > self.obs_n_categ["Union"] :
            self.counts_hist[(0,0)] = self.usr_n_categ - self.obs_n_categ["Union"]
            self.counts_hist = self.counts_hist.sort_index(ascending=True)
        
        # WARNING!: is this a deep copy ?
        tmp = self.counts_hist.reset_index(level=[0,1]).copy()
        # experiment 1 copy
        self.exp_1 = Experiment( my_exp_1.data_hist )
        self.exp_1._update_categories( self.usr_n_categ )
        counts_1 = tmp[["freq", "Exp-1"]].set_index("Exp-1", drop=True)
        self.exp_1.counts_hist = counts_1["freq"] # convert to series
        # experiment 2 copy
        self.exp_2 = Experiment( my_exp_2.data_hist )
        self.exp_2._update_categories( self.usr_n_categ )
        counts_2 = tmp[["freq", "Exp-2"]].set_index("Exp-2", drop=True)
        self.exp_2.counts_hist = counts_2["freq"]

    def kullback_leibler( self, method="naive", unit="ln", **kwargs ):
        '''Estimate Kullback-Leibler divergence.

        Kullback-Leibler divergence estimation through a chosen `method`.
        The unit (of the logarithm) can be specified with the parameter `unit`.
            
        Parameters
        ----------
        method: str
            the name of the estimation method:
            - ["naive", "maximum-likelihood"] : naive estimator (default);
            - "CMW" : Camaglia Mora Walczak estimator.
            - ["Jeffreys", "Krichevsky-Trofimov"] : Jeffreys estimator;
            - ["L", "Laplace", "Bayesian-Laplace"] : Laplace estimator;
            - ["SG", "Schurmann-Grassberger"] : Schurmann-Grassberger estimator;
            - ["minimax", "Trybula"] : minimax estimator; 
            - ["D", "Dirichlet"] : Dirichlet   
        unit: str, optional
            the divergence logbase unit:
            - "ln": natural logarithm (default);
            - "log2": base 2 logarihtm;
            - "log10":base 10 logarithm.

        return numpy.array
        '''
        
        return default_divergence.switchboard( self.compact(), which="Kullback-Leibler", method=method, unit=unit, **kwargs )

    def jensen_shannon( self, method="naive", unit="ln", **kwargs ):
        '''Estimate Jensen-Shannon divergence.

        Jensen-Shannon divergence estimation through a chosen `method`.
        The unit (of the logarithm) can be specified with the parameter `unit`.
            
        Parameters
        ----------
        method: str
            the name of the estimation method:
            - ["naive", "maximum-likelihood"] : naive estimator (default);
            - ["Jeffreys", "Krichevsky-Trofimov"] : Jeffreys estimator;
            - ["L", "Laplace", "Bayesian-Laplace"] : Laplace estimator;
            - ["SG", "Schurmann-Grassberger"] : Schurmann-Grassberger estimator;
            - ["minimax", "Trybula"] : minimax estimator; 
            - ["D", "Dirichlet"] : Dirichlet    
        unit: str, optional
            the divergence logbase unit:
            - "ln": natural logarithm (default);
            - "log2": base 2 logarihtm;
            - "log10":base 10 logarithm.

        return numpy.array
        '''
        
        return default_divergence.switchboard( self.compact(), method=method, which="Jensen-Shannon", unit=unit, **kwargs )

    def hellinger( self, method="naive", **kwargs ):
        '''Estimate Hellinger divergence.

        Hellinger divergence estimation through a chosen `method`.
            
        Parameters
        ----------
        method: str
            the name of the estimation method:
            - ["naive", "maximum-likelihood"] : naive estimator (default);
            - ["Jeffreys", "Krichevsky-Trofimov"] : Jeffreys estimator;
            - ["L", "Laplace", "Bayesian-Laplace"] : Laplace estimator;
            - ["SG", "Schurmann-Grassberger"] : Schurmann-Grassberger estimator;
            - ["minimax", "Trybula"] : minimax estimator; 
            - ["D", "Dirichlet"] : Dirichlet    

        return numpy.array
        '''
        
        return default_divergence.switchboard( self.compact(), method=method, which="Hellinger", **kwargs )


    def rank_plot( self, figsize=(3,3), color1="#ff0054", color2="#0088ff", xlabel="rank", ylabel="frequency", logscale=True, grid=True, by_first=True) :
        '''Rank plot.'''
        return divergence_rank_plot( self, figsize=figsize, color1=color1, color2=color2, xlabel=xlabel, ylabel=ylabel, logscale=logscale, grid=grid, by_first=by_first )

    def compact( self ) :
        '''It provides aliases for computations.'''
        return Divergence_Compact( self )
        
    def save_compact( self, filename ) :
        '''It saves the compact version of Experiment to `filename`.'''
        self.compact( )._save( filename )

# >>>>>>>>>>>>
#  GRAPHICS  #
# <<<<<<<<<<<<

def experiment_rank_plot( 
    experiment_object, figsize=(3,3), color="#ff0054", 
    xlabel="rank", ylabel="frequency", logscale=True, grid=True ) :
    ''' '''

    fig, ax = plt.subplots(ncols=1, figsize=figsize )
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if logscale :
        ax.set_xscale("log")
        ax.set_yscale("log")
    if grid :
        ax.set_axisbelow(True)
        ax.yaxis.grid(color='gray', linestyle='dashed')
    ax.set_xlim([1, experiment_object.usr_n_categ])

    sequences = experiment_object.data_hist
    N = experiment_object.tot_counts
    x = np.arange(len(sequences)) + 1
    y = sequences.sort_values(ascending=False).values / N
    ax.plot( x ,y, ls="", marker="o", color=color )
    return ax

def divergence_rank_plot( 
    divergence_object, figsize=(3,3), color1="#ff0054", color2="#0088ff",
    xlabel="rank", ylabel="frequency", logscale=True, grid=True, by_first=True ) :
    ''' '''
    
    fig, ax = plt.subplots(ncols=1, figsize=figsize )
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if logscale :
        ax.set_xscale("log")
        ax.set_yscale("log")
    if grid :
        ax.set_axisbelow(True)
        ax.yaxis.grid(color='gray', linestyle='dashed')
    ax.set_xlim([1, divergence_object.usr_n_categ])

    sort_by = [ 'Exp-1' if by_first else 'Exp-2' ]
    data_hist = divergence_object.data_hist.sort_values( by=sort_by, ascending=False)
    sequences_1 = data_hist['Exp-1']
    N_1 = divergence_object.tot_counts['Exp-1']
    sequences_2 = data_hist['Exp-2']
    N_2 = divergence_object.tot_counts['Exp-2']

    x = np.arange(len(data_hist)) + 1
    y1 = sequences_1.values / N_1
    ax.plot( x, y1, ls="", marker="o", color=color1 )
    y2 = sequences_2.values / N_2
    ax.plot( x, y2, ls="", marker="s", color=color2 )
    return ax