# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 18:10:44 2019

@author: donatif
"""

#Hey again, I wrote a matlab code to calculate the new L inverse when you change the technical coef matrix in a single row (i.e. single product product in a single country and it can be consumed by many sectors in many regions.
#Please see the following if you want to play around.
#The vice verse is quite straight forward, in other words, updating the technical matrix in a column. (i.e. multiple products produced by multiple region consumed in a single sector single region).
#Let me know.
#Br

# generate a random A matrix with n_s sectors n_countries
n_s=3;
n_c=2;
#random matrix generation
c = 0;
b = 0.2; #max of the tech coef
A = (b-c).*rand(n_s*n_c,n_s*n_c) + c;

L= (eye(n_s*n_c,n_s*n_c)-A);

#now calculate the new leontief inverse
#select production in a single sectors i  in single region k
k=1;
i=1;
#select consumption in multiple sectors j in  multiple regions m
j=[1,3];
m=2;
#what is the change in tech coef
change_coef=0.1;
#write u
u=zeros(n_s*n_c,1);
u((k-1)*n_s+i,1)=0.1;
#write v
v=zeros(n_s*n_c,1);
v((m-1)*n_s+j,1)=-A(i,(m-1)*n_s+j);
#the update in A
delta_A=u* transpose(v) ;
new_A=A+delta_A;
#the update in A
delta_L=u* transpose(-v) ;
#Assume you know the initial Leontief inverse
inv_L=inv(L);
#apply Sherman–Morrison formula to find the new inverse
inv_new_L_Sherman_Morrison=inv_L-(inv_L*u*transpose(-v)*inv_L)/(1+transpose(-v)*inv_L*u) ;
#check whether the answer is true by comparing it to the default
#calculation
new_L= (eye(n_s*n_c,n_s*n_c)-new_A);
inv_new_L_default=inv(new_L); #this is minus delta a
error=max(max(inv_new_L_default-inv_new_L_Sherman_Morrison))
