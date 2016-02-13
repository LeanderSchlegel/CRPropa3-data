from numpy import *
import interactionRate as iR
import photonField


eV = 1.60217657e-19
ElectronMass = 0.510998918e6 # [eV/c^2]
K_boltz = 8.617342294984e-5  # [eV/K ] Boltzman constant
C_speed = 299792458          # [m/s] speed of light
SigmaThompson = 6.6524e-29   # m**2
alpha = 1. / 137.035999074

# cross sections [1/m^2] for choosen s range [J^2]

def Sigma_PP(s):
    """
    comp. Lee 96
    """
    if (s < 4.*ElectronMass**2 *eV**2):
        return 0.
    else:
        beta = sqrt(1.-4.*ElectronMass**2 *eV**2 /s)
        return SigmaThompson * 3./16.*(1-beta**2)*((3-beta**4)*log((1+beta)/(1-beta))-2*beta*(2-beta**2))

def Sigma_ICS(s):
    """
    comp. Lee 96
    """
    if (s < 1.0 * ElectronMass**2 *eV**2):
        return 0.
    else:
      beta = (s - ElectronMass**2 *eV**2)/(s + ElectronMass**2 *eV**2)
      return SigmaThompson * 3./8. * ElectronMass**2 * eV**2 / s / beta * (2./beta/(1+beta)*(2.+2.*beta-beta**2-2.*beta**3)-1./beta**2 * (2.-3.*beta**2- beta**3)*log((1.+beta)/(1.-beta)))

def Sigma_TPP(s):
    """
    comp. Lee 96
    """
    if (28/9*log(s/ElectronMass**2 /eV**2)- 218./27. < 0.):
        return 0.
    else:
        return SigmaThompson *3.*alpha/8./pi*(28/9*log(s/ElectronMass**2 /eV**2)- 218./27.)
 
# truncate to largest length 2^i + 1 for Romberg integration
skin_PP_DPP = logspace(-28,log10(10**23 * eV**2),500)
skin_ICS_TPP = logspace(-28,log10(10**23 * eV**2- ElectronMass**2 *eV**2),500)
skin_PP_DPP_URB = logspace(-28,log10(10**17 * eV**2),500)
skin_ICS_TPP_URB = logspace(-28,log10(10**17 * eV**2- ElectronMass**2 *eV**2),500)

# choose energy range of interacting particle for which the interaction rate should be tabulated
lEnergy = linspace(15, 23, 81)
Energy  = 10**lEnergy * eV

# photo pair production PP
xs1 = zeros(len(skin_PP_DPP))
xs1_urb = zeros(len(skin_PP_DPP_URB))
for i in range(0,len(skin_PP_DPP)):
    xs1[i] = Sigma_PP(skin_PP_DPP[i])
for i in range(0,len(skin_PP_DPP_URB)):
    xs1_urb[i] = Sigma_PP(skin_PP_DPP_URB[i])

# inverse compton scattering ICS
xs2 = zeros(len(skin_ICS_TPP))
xs2_urb = zeros(len(skin_ICS_TPP_URB))
for i in range(0,len(skin_ICS_TPP)):
  xs2[i] = Sigma_ICS(skin_ICS_TPP[i]+ ElectronMass**2 * eV**2)  
for i in range(0,len(skin_ICS_TPP_URB)):
  xs2_urb[i] = Sigma_ICS(skin_ICS_TPP_URB[i]+ ElectronMass**2 * eV**2)  

# triplet pair production TPP
xs3 = zeros(len(skin_ICS_TPP))
xs3_urb = zeros(len(skin_ICS_TPP_URB))
for i in range(0,len(skin_ICS_TPP)):
  xs3[i] = Sigma_TPP(skin_ICS_TPP[i] + ElectronMass**2 * eV**2)
for i in range(0,len(skin_ICS_TPP_URB)):
  xs3_urb[i] = Sigma_TPP(skin_ICS_TPP_URB[i] + ElectronMass**2 * eV**2)

fields = [
#    photonField.URB_Protheroe96(),
    photonField.CMB(),
    photonField.EBL_Stecker05(),
    photonField.EBL_Kneiske04(),
    photonField.EBL_Franceschini08(),
    photonField.EBL_Finke10(),
    photonField.EBL_Dominguez11(),
    photonField.EBL_Gilmore12()
    ]

en = zeros(len(Energy)*len(skin_PP_DPP))
eps_PP = zeros(len(Energy)*len(skin_PP_DPP))
eps_ICS_TPP = zeros(len(Energy)*len(skin_ICS_TPP))
s_pp = zeros(len(Energy)*len(skin_PP_DPP))
s_ics_tpp = zeros(len(Energy)*len(skin_ICS_TPP))
s_pp_urb = zeros(len(Energy)*len(skin_PP_DPP_URB))
s_ics_tpp_urb = zeros(len(Energy)*len(skin_ICS_TPP_URB))
for i in range(0,len(Energy)):
  for j in range(0,len(skin_PP_DPP)):
    en[i*len(skin_PP_DPP)+j] = Energy[i]
    eps_PP[i*len(skin_PP_DPP)+j] = skin_PP_DPP[j] / 4. / Energy[i]
    eps_ICS_TPP[i*len(skin_PP_DPP)+j] = skin_ICS_TPP[j] / 4. / Energy[i]
    s_pp[i*len(skin_PP_DPP)+j] = skin_PP_DPP[j]
    s_ics_tpp[i*len(skin_ICS_TPP)+j] = skin_ICS_TPP[j]
    s_pp_urb[i*len(skin_PP_DPP_URB)+j] = skin_PP_DPP_URB[j]
    s_ics_tpp_urb[i*len(skin_ICS_TPP_URB)+j] = skin_ICS_TPP_URB[j]


for field in fields:

# Take care that all things are changed if one wants to create the tables for different processes
# in data choose right s array and rate array r
# in fname set right process name
# in header set right process in lambda

    r1 = iR.integrant_simple(skin_PP_DPP, xs1, Energy, field)
    r2 = iR.integrant_simple(skin_ICS_TPP, xs2, Energy, field)
    r3 = iR.integrant_simple(skin_ICS_TPP, xs3, Energy, field)

    fname = 'CRPropa_Tables_1e15_1e23_eV/CDFs/EMTripletPairProduction_CDF_%s.txt' % field.name
    data  = c_[log10(en/eV),log10(s_ics_tpp/eV/eV),r3]
    fmt   = '%.5e\t%.5e\t%.5e'
    header = 'CDF of the %s\nlog10(E/eV)\tlog10(s_kin/eV/eV)\t(1/lambda_TPP)_cumulative [1/Mpc]'%field.info
    savetxt(fname, data, fmt=fmt, header=header)

field = photonField.URB_Protheroe96() # handle URB extra cause needs different s range
r1 = iR.integrant_simple(skin_PP_DPP_URB, xs1_urb, Energy, field)
r2 = iR.integrant_simple(skin_ICS_TPP_URB, xs2_urb, Energy, field)
r3 = iR.integrant_simple(skin_ICS_TPP_URB, xs3_urb, Energy, field)

fname = 'CRPropa_Tables_1e15_1e23_eV/CDFs/EMTripletPairProduction_CDF_%s.txt' % field.name
data  = c_[log10(en/eV),log10(s_ics_tpp_urb/eV/eV),r3]
fmt   = '%.5e\t%.5e\t%.5e'
header = 'CDF of the %s\nlog10(E/eV)\tlog10(s_kin/eV/eV)\t(1/lambda_TPP)_cumulative [1/Mpc]'%field.info
savetxt(fname, data, fmt=fmt, header=header)
