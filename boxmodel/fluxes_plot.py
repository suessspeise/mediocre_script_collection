import numpy as np
import sympy as sym

def sec2yr(s):
    return s * 60 * 60 * 24 * 365
def yr2sec(y):
    return y / (60 * 60 * 24 * 365)


class Box:
    attributes = dict()
    links = dict()
    
    def __init__(self, attributes, links=None):
        self.attr = attributes
        self.links = links
        
    def __str__(self):
        attributes = ''
        for e in list(self.attr.keys()): attributes += (e + ', ')
        return f"Box: {attributes[0:-2]}"
    
    def get(self, key):
        return self.attr[key]
    
    def set(self, key, value):
        self.attr[key] = value
        
    def add(self, key, value):
        self.attr[key] += value
    
    def keys(self):
        return self.attr.keys()
    
    def apply_delta(self, delta):
        for key in delta.keys():
            if not key == 'label': self.add(key, delta.get(key) )
        
        
class Delta(Box):
    
    scaling_factor = 1.0
    
    def __init__(self, original_box, time_step_length):
        self.attr = dict()
        for key in original_box.keys():
            self.attr[key] = 0.0
            self.scaling_factor
    
    def scale(self, key, value):
        self.attr[key] = self.attr[key] * value
        
    def get_delta(self, key):
        return self.attr[key] * self.scaling_factor
    
    
# Sympy symbols 
C_l, C_a, C_s, C_d, T_s = sym.symbols('C_l, C_a, C_s, C_d, T_s')
delta, eta_C = sym.symbols('\delta, \eta_C')
tau_l0, chi, C_l0, T_s = sym.symbols('\\tau_l^0 \chi C_l^0 T_s')
beta_P, beta, C_a0, preInd = sym.symbols('\\beta_{\Pi} \\beta \mathcal{C}_a^0 \Pi^0')
gam, k_a, k_o = sym.symbols('\gamma, \mathcal{k}_a \mathcal{k}_o')
A_tot, t_opt, t = sym.symbols('A_{tot}, t_{opt}, t')
eta_H = sym.Symbol('\eta_H')
lam, lam_st = sym.symbols('\lambda, \lambda_*')
delta, c_star = sym.symbols('\delta, c_*')

# values those symbols that are constants or parameters to be set
constants = {
    chi    : 1.8, # scaling factor for soil carbon lifetime decrease. empirically set to 1.8 (S
    tau_l0 : 41, # years 
    # C_l0   : 2500,  # GtCO2 (Sec 7.1)  
    C_l0   : 2460,  # GtCO2 tuned to get rid of initial exchange
    preInd : 60, # GtC/yr
    beta_P : 0.4, # co2 fertilisation factor
    # C_a0   : 37000 / 7, # GtC, estimate as 1/7 of ocean reservoir as given in paragraph 7.2
    C_a0   : 2.12 * 280,
    k_a    : 2.12, # GtC/ppm (page 41)
    # k_o    : 2.12 * (1-1/7)/(1/7) * 0.015,
    # k_o    : 2.12, # proposed by Victor
    k_o    : 2.0421, # also proposed by Victor via Mattermost, apparentyl the equation missed a Revelle factor
    gam    : 0.005, # GtC/year/ppm
    t_opt  : 250,  # years, time scale of emission
    A_tot  : 5000,  # GtC total emission
    # A_tot  : 100000,  # GtC total emission
    delta  : 0.015,  # Surface ocean fraction
    # eta_C  : 60e-12,  # [s^-1] Surface-deep ocean carbon exchange coefficient
    eta_C  : sec2yr(60e-12), # [yr^-1] Surface-deep ocean carbon exchange coefficient
    # eta_H  : 1, # enthalpy exchange coefficient
    eta_H  : 0.73, # enthalpy exchange coefficient, as proposed by Moritz
    beta   : 5.77, # W m-2 ; CO2 radiative forcing strength
    # lam    : 0.0, # W m-1 K-2 ; Radiative response to surface temperature anomaly
    lam    : 1.77, # W m-1 K-2 ; Radiative response to surface temperature anomaly
    # lam_st : 0, # W m-1 K-2 ; Radiative response to surface-deep ocean equilibrium, tunable parameter
    lam_st : 0.75, # W m-1 K-2 ; Radiative response to surface-deep ocean equilibrium, tunable parameter
    delta  : 0.015, # surface ocean fraction (of all ocean)
    # c_star : sec2yr(10.8e9), # J K-1 m-2 ; area specific heat of sea water
    c_star : yr2sec(108e8), # J K-1 m-2 ; area specific heat of sea water
}

def fetch_constants(symbol_set):
    # returns a subset of the global constants
    global constants
    c = dict()
    for s in symbol_set:
        c[s] = constants[s]
    return c

def radiation_term():
    T_s, T_d, C_a = sym.symbols('T_s, T_d, C_a') 
    global lam, lam_st, beta, C_a0, k_a
    constants = fetch_constants([lam, lam_st, beta, C_a0, k_a])
    expr = - (lam * (T_s)) - (lam_st * (T_s - T_d)) + (beta * sym.log( C_a / C_a0 + 1 ))
    return sym.lambdify((T_s, T_d, C_a), expr.subs(constants))

# this performs thermal conduction between two layers (Eq. 6.14), also used as part of Eq. 6.13
def enthalpy_exchange():
    T_s, T_d = sym.symbols('T_s, T_d') 
    global eta_H
    constants = fetch_constants([eta_H])
    expr = eta_H * (T_s - T_d)
    return sym.lambdify((T_s, T_d), expr.subs(constants))

def carbon_flux_surface_deep():
    # carbon flux between the surface and deep ocean (C_d)
    C_s, C_d = sym.symbols('C_s, C_d') 
    global delta, eta_C
    constants = fetch_constants([delta, eta_C])
    expr = eta_C * (C_s / delta - C_d / (1 - delta)) # Eq. 7.11 / 8.5
    return sym.lambdify((C_s, C_d), expr.subs(constants))

def land_carbon_uptake():
    # Heterotrophic (soil) respiration (Eq. 7.5)
    C_l, C_a, T_s = sym.symbols('C_l, C_a, T_s') # as by model design: T_s == T_l
    global tau_l0, chi, C_l0
    Rh_constants = fetch_constants([tau_l0, chi, C_l0])
    Rh_expr = (C_l + C_l0)/(tau_l0 * chi **( -T_s / 10 ))
    # global net primary productivity (Eq. 7.4)
    global beta_P, C_a0, preInd
    P_constants = fetch_constants([beta_P, C_a0, preInd])
    P_expr = preInd * (1 + beta_P * sym.ln(C_a/C_a0 + 1))
    # unified function is land carbon uptake flux (Eq. 7.3) 
    return sym.lambdify((C_l,C_a,T_s), (P_expr - Rh_expr).subs(P_constants | Rh_constants))

def atmosphere_ocean_exchange():
    # model of atmosphere ocean exchange of CO2 J_{a-s} (Eq. 7.9)
    C_a, C_s = sym.symbols('C_a, C_s') 
    global gam, k_a, k_o
    constants = fetch_constants([gam, k_a, k_o])
    expr = gam * ((C_a/k_a) - (C_s/k_o))
    return sym.lambdify((C_a, C_s), expr.subs(constants))

def gammavar_atmosphere_ocean_exchange(gamma):
    # model of atmosphere ocean exchange of CO2 J_{a-s} (Eq. 7.9)
    C_a, C_s = sym.symbols('C_a, C_s') 
    global gam, k_a, k_o
    constants = fetch_constants([gam, k_a, k_o])
    # victor suggested, that the surface ocean - amtmosphere coupling is too sluggish
    # so i play around a little:
    constants[gam] = gamma

    expr = gam * ((C_a/k_a) - (C_s/k_o))
    return sym.lambdify((C_a, C_s), expr.subs(constants))

def anthropogenic_emission():
    # Anthropogenic emissions (A(t)), Eq. (7.17)
    t = sym.Symbol('t')
    global A_tot, t_opt
    constants = fetch_constants([A_tot, t_opt])
    expr = A_tot * ((1 / (1 + 2.5 * sym.exp((t_opt - t)/50))) - (1 / (1 + 2.5 * sym.exp(t_opt / 50))))
    expr_dt = sym.Derivative(expr,t).doit()
    return sym.lambdify((t), expr_dt.subs(constants))

def no_emission():
    def zero(t):
        return 0
    return zero

def instantaneous_emission():
    def insta(t):
        if t == 1:
            return constants[A_tot]
        else:
            return 0
    return insta

    
def run_model(boxes, output, t_end, step_length=1):
    times = list()
# DB begin
    fluxes = dict()
    for key in ['ocean_atmo', 'ocean_ocean', 'atmo_land', 'T_flux', 'T_rad']:
        fluxes[key] = list()
# DB end
    
    for t in range(t_end):
        # write output in the beginning to capture t = 0
        times.append(t * step_length)
        for key in output.keys():
            output[key]['values'].append(boxes[output[key]['box']].get(output[key]['var']) )

        deltas = dict()
        for key in boxes.keys():
            deltas[key] = Delta(boxes[key], step_length)

        # calculate temperature fluxes
        exchange  = enthalpy_exchange_ocean(boxes['surface ocean'].get('T'), 
                                       boxes['deep ocean'].get('T'))
        radiation = surface_radiation(boxes['surface ocean'].get('T'), 
                                  boxes['deep ocean'].get('T'), 
                                  boxes['atmosphere'].get('C') )
# DB begin        
        fluxes['T_flux'].append(exchange)
        fluxes['T_rad'].append(radiation)
# DB end

        # add
        deltas['deep ocean'   ].add('T',   exchange)
        deltas['surface ocean'].add('T', - exchange)
        deltas['surface ocean'].add('T',   radiation)
        deltas['deep ocean'   ].scale('T', 1 / boxes['deep ocean'].get('c'))
        deltas['surface ocean'].scale('T', 1 / boxes['surface ocean'].get('c'))


        # calculate carbon fluxes
        oceanflux = flux_s2d( boxes['surface ocean'].get('C'), boxes['deep ocean'].get('C') )
        land_carb = landcarbon(boxes['land'].get('C'), boxes['surface ocean'].get('C'), boxes['surface ocean'].get('T'))
        ocean_atmosphere = Jas( boxes['atmosphere'].get('C'), boxes['surface ocean'].get('C') )
        deltas['deep ocean'   ].add('C',   oceanflux)
        deltas['surface ocean'].add('C', - oceanflux)
        deltas['surface ocean'].add('C', ocean_atmosphere)
        deltas['land'].add('C', land_carb)
        deltas['atmosphere'].add('C',   emission(t))
        deltas['atmosphere'].add('C', - deltas['land'].get('C'))
        deltas['atmosphere'].add('C', - deltas['surface ocean'].get('C'))
        deltas['atmosphere'].add('C', - deltas['deep ocean'].get('C'))

# DB begin        
        fluxes['atmo_land'].append(land_carb)
        fluxes['ocean_atmo'].append(ocean_atmosphere)
        fluxes['ocean_ocean'].append(oceanflux)
# DB end

        # apply deltas
        for key in boxes.keys():
            boxes[key].apply_delta(deltas[key])

    return output, times, fluxes


def plot_model(title=None):
    import matplotlib.pyplot as plt

    fig, axs  = plt.subplots(1,2, figsize=(10,5))
    if title: fig.suptitle(title)
    # for i, y in enumerate([ys,yd]): ax.plot(x,y, label=str(i))#, color=i/len(yy))
    ax = axs[0]
    ax.plot(times,output['T_s']['values'],label=f"surface ocean \n(max:{np.max(output['T_s']['values']):.2f} K; last: {output['T_s']['values'][-1]:.2f} K)",color='lightblue')
    ax.plot(times,output['T_d']['values'],label=f"deep ocean \n(max:{np.max(output['T_d']['values']):.2f} K; last: {output['T_d']['values'][-1]:.2f} K)",color='darkblue')
    # ax.set_xlabel(f"time step : {step_length} years")
    ax.set_xlabel(f"years")
    ax.legend()
    ax = axs[1]
    ax.plot(times,output['C_s']['values'],label=f"surface ocean (last: {output['C_s']['values'][-1]:.0f} Gt)", color='lightblue')
    ax.plot(times,output['C_d']['values'],label=f"deep ocean (last: {output['C_d']['values'][-1]:.0f} Gt)", color='darkblue')
    ax.plot(times,output['C_l']['values'],label=f"land (last: {output['C_l']['values'][-1]:.0f} Gt)", color='green')
    ax.plot(times,output['C_a']['values'],label=f"atmosphere (last: {output['C_a']['values'][-1]:.0f} Gt)", color='red')
    # ax.set_xlabel(f"time step : {step_length} years")
    ax.set_xlabel(f"years")
    # ax.set_ylim((-100,1000))
    # ax.set_xlim((0,2000))
    # ax.set_ylim((-10,100))
    ax.legend()
    plt.show()
    
def plot_fluxes(title=None):
    import matplotlib.pyplot as plt

    fig, axs  = plt.subplots(1,2, figsize=(10,5))
    if title: fig.suptitle(title)
    # for i, y in enumerate([ys,yd]): ax.plot(x,y, label=str(i))#, color=i/len(yy))
    ax = axs[0]
    ax.axhline(0,lw=0.2, color='black')
    ax.plot(times,fluxes['T_flux'],label=f"enthalpy mixing",color='pink')
    ax.plot(times,fluxes['T_rad'],label=f"radiation",color='red')
    # ax.set_xlabel(f"time step : {step_length} years")
    ax.set_xlabel(f"years")
    ax.legend()
    ax = axs[1]
    ax.axhline(0,lw=0.2, color='black')
    ax.plot(times,fluxes['atmo_land'],label=f"atmosphere-land", color='green')
    ax.plot(times,fluxes['ocean_atmo'],label=f"ocean-atmosphere", color='yellow')
    ax.plot(times,fluxes['ocean_ocean'],label=f"deep-surface ocean", color='blue')
    # ax.set_xlabel(f"time step : {step_length} years")
    ax.set_xlabel(f"years")
    ax.set_ylim((-1,1))
    # ax.set_xlim((0,2000))
    # ax.set_ylim((-10,100))
    ax.legend()
    plt.show()


# define boxes
atmo = Box({'C':0.0, 'T':0.0, 'label':'atmosphere'})
land = Box({'C':0.0, 'T':0.0, 'label':'land'})
deep = Box({'C':0.0, 'T':0.0, 'c':0.0, 'label':'deep ocean'})
surf = Box({'C':0.0, 'T':0.0, 'c':0.0, 'label':'surface ocean'})
# assign capacity terms
surf.set('c', constants[delta]       * constants[c_star])
deep.set('c', (1 - constants[delta]) * constants[c_star])
# join boxes in a dictionary for accessability
boxes = dict()
for e in [atmo, land, deep, surf]:
    boxes[e.get('label')] = e


# define functions
surface_radiation = radiation_term()
enthalpy_exchange_ocean = enthalpy_exchange()
Jas = atmosphere_ocean_exchange()
# Jas = gammavar_atmosphere_ocean_exchange(0.1)

landcarbon = land_carbon_uptake()
emission = anthropogenic_emission()
# emission = no_emission()
# emission = instantaneous_emission()

# boxes['atmosphere'].add('C', 280 * constants[k_a])
# print(f"boxes['atmosphere'].add('C', {280 * constants[k_a]})")

flux_s2d = carbon_flux_surface_deep()


# output variables
output = dict()
output['T_s'] = {'box':'surface ocean', 'var':'T', 'values':list()}
output['T_d'] = {'box':'deep ocean',    'var':'T', 'values':list()}
output['C_s'] = {'box':'surface ocean', 'var':'C', 'values':list()}
output['C_d'] = {'box':'deep ocean',    'var':'C', 'values':list()}
output['C_a'] = {'box':'atmosphere',    'var':'C', 'values':list()}
output['C_l'] = {'box':'land',          'var':'C', 'values':list()}

# time stepping
step_length = 0.1
step_length = 1
t_end = 2000

output, times, fluxes = run_model(boxes=boxes, output=output, t_end=2000)
# plot_model()
plot_fluxes()
# surface ocean too sluggish?
