# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 18:10:44 2019

@author: donatif
"""

import numpy as np

def sherman_morrison(A, L, coordinates_for_u, coordinates_for_v):
    
    IA = np.identity(A) - A
    
    change_coef=0.1;
    #write u
    u = np.zeros(len(L))
    v = np.zeros(len(L))
    
    u[coordinates_for_u] = change_coef;
    v[coordinates_for_v] = -A[coordinates_for_v]  # this must be a matrix
    
    #the update in A
    delta_A = u * v.T
    new_A = A + delta_A
    
    #the update in IA
    delta_IA = u * -v.T
    
    new_L 
    #apply Sherman–Morrison formula to find the new inverse
    inv_new_L_Sherman_Morrison = L - (( L @ u @ -v.T)* L) / (1 + -v @ L @ u)
    
    #check whether the answer is true by comparing it to the default
    #calculation
    
    inv_new_L_default = np.linalg.inv(np.identity(L) - new_A);
    
    error = max(max(inv_new_L_default - inv_new_L_Sherman_Morrison))


# =============================================================================
# 
# %now calculate the new leontief inverse
# %select production in a single sectors i  in single region k
#  k=1;
# i=1;
# %select consumption in multiple sectors j in  multiple regions m
# j=[1,3];
# m=2;
# %what is the change in tech coef
# change_coef=0.1;
# %write u
# u=zeros(n_s*n_c,1);
# u((k-1)*n_s+i,1)=0.1;
# %write v
# v=zeros(n_s*n_c,1);
# v((m-1)*n_s+j,1)=-A(i,(m-1)*n_s+j);
# %the update in A
# delta_A=u* transpose(v) ;
# new_A=A+delta_A;
# %the update in A
# delta_L=u* transpose(-v) ;
# %Assume you know the initial Leontief inverse
# inv_L=inv(L);
# %apply Sherman–Morrison formula to find the new inverse
# inv_new_L_Sherman_Morrison=inv_L-(inv_L*u*transpose(-v)*inv_L)/(1+transpose(-v)*inv_L*u) ;
# %check whether the answer is true by comparing it to the default
# %calculation
# new_L= (eye(n_s*n_c,n_s*n_c)-new_A);
# inv_new_L_default=inv(new_L); %this is minus delta a
# error=max(max(inv_new_L_default-inv_new_L_Sherman_Morrison))
# =============================================================================
