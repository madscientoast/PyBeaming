# PyBEAMING Functions #
# Program for characterizing properties of THIA ion beam #
# By: Robert Snuggs #
# Converted From R. Haar's BEAMNG program #
# Much of the physics is also reviewed in R. Haar's Thesis #

import math

# Constants# 
Z_T = 6 # We normally use carbon targets 
M_T = 12 # mass of the target in amu
a_0 = 0.529e-8 # Bohr radius
e2 = 14.4e-11 # in units of KeV * cm (think fine-structure constant to convince yourself of units)

        
#########################################################
#                 Calculation Functions                 #
#########################################################
def Lindhard(a_0, Z_I, Z_T, M_I, M_T, t, E_i):
    #####################################################
    #    Energy Loss and Stopping Power Calculation     #
    #                                                   #
    #       J.Lindhard, m. Scharff, & H.E.Schiott,      #
    #       Kgl. Danske Videnskab. Selskab.,            #
    #       Mat-Fys. Medd. _33_, #14 (1963)             #
    #                                                   #
    #       F.S.Garnir-Gonjoie & H.P.Garnir,            #
    #       J. Physique _41_, 31-33 (1980)              #
    #####################################################
    
    # Parameters #
    a = 0.8853 * a_0 / math.sqrt((Z_I**(2/3))+(Z_T**(2/3))) # screening parameter (Lindhard)
    N = 1 / (M_T * (1.66e-18)) #number of striking centers
    # These C constants are just equations stored in variables to simplify the execution of the function
    C1 = ((a*M_T)/(Z_I*Z_T*e2*(M_T+M_I)))
    C2 = 4 * math.pi * (a**2) * N * ((M_T*M_I)/((M_T+M_I)**2))
    rho = t * C2 # reduced thickness (unitless)
    
    #Now to begin calculations#
    k = 0.0793 * (Z_I**(1/6)) * ((math.sqrt(Z_I*Z_T))*((M_I+M_T)**(3/2))) / (((Z_I**(2/3))+(Z_T**(2/3)))**(3/4)*(M_I**(3/2))*math.sqrt(M_T))
    epsilon = E_i * C1 # reduced energy (unitless)

    Se = k * math.sqrt(epsilon) # electronic stopping power

    E_loss_e = rho * Se / C1 # electronic energy loss

    # Now for Lindhard nuclear stopping power #
    Sn = 0.6175 - (0.3198 * math.sqrt(epsilon)) + (0.0695 * epsilon) - (0.005556 * (epsilon**(3/2)))
    E_loss_n = rho * Sn / C1 # nuclear energy loss

    # Now to perform Garnir part of calculations #
    SN_F = 0.75 * ((math.log((0.78*math.sqrt(epsilon))+1)) / (((0.78*math.sqrt(epsilon))+1)**(2))) # forward nuclear stopping
    SN_A = 1.6 * ((math.log((1.2*math.sqrt(epsilon))+1)) / (((1.2*math.sqrt(epsilon))+1)**(2)))    # nuclear stopping all angles
    ELNF = rho * SN_F / C1 # energy loss forward
    ELNA = rho * SN_A / C1 # energy loss all angles
    
    # Calculating Post-Foil Energy
    if ELNF < E_loss_n:
        E_f = E_i - E_loss_e - ELNF
    else:
        E_f = E_i - E_loss_e - E_loss_n
    
    
    return E_f, E_loss_e, E_loss_n, ELNF, ELNA
        
def gbar(v_i, v_f, Z_I, M_T, t, E_f):
    
    ###########################################################
    #           Angular Distribution and Mean Charge          #
    #                                                         #
    #           Nikolaev & Dmitriev                           #
    #           Phys. Letters _28a_, 277-278 (1968)           #
    #                                                         #
    #           Hogberg, Norden, & Barry                      #
    #           Nucl.Instr.Meth. _90_ 283-288 (1970)          #
    ###########################################################
    theta_half = M_T * (Z_I**(3/4)) * (t/E_f) #angle of half-beam intensity
    v = (v_i + v_f)/2 # average velocity)
    vp = 3.6 #vp is 3.6 cm/sec
    #alpha and k are parameters#
    alpha = 0.45
    k = 0.6
    qb = Z_I * (1 + (((v/vp)*(Z_I**(-1*alpha)))**(-1/k)))**(-1*k) #mean charge

    return theta_half, qb
        
def foil_life(E_i, Z_I, M_I):
    #########################################################
    #                       Foil Life                       #
    #                                                       #
    #           R.L.Auble & D.M.Galbraith,                  #
    #           Nucl.Instr.Meth. _200_, 13-14 (1982)        #
    #########################################################
    radius = 3.0
    area = math.pi * (radius**2)
    flife = (area * 1.8 * E_i) / ((Z_I**2)*M_I)
    return flife