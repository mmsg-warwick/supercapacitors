#
# Parameter set from the Iamrod et al (2024) paper
#

def get_parameter_values():
    """
    Parameters for a supercapacitor, from our current work. Currently it contains
    the Verbrugge & Liu parameters, please update accordingly.
    """

    return {
        "chemistry": "supercapacitor",
        # cell
        "Negative electrode thickness [m]": 5e-05,
        "Separator thickness [m]": 2.5e-05,
        "Positive electrode thickness [m]": 5e-05,
        "Electrode height [m]": 2.747,
        "Electrode width [m]": 1,
        "Nominal cell capacity [A.h]": 5.0,
        "Current function [A]": 300.0,
        # negative electrode
        "Negative electrode conductivity [S.m-1]": 0.0521,
        "Negative electrode porosity": 0.67,
        "Negative electrode active material volume fraction": 0.33,
        "Negative particle radius [m]": 0.99,
        "Negative electrode Bruggeman coefficient (electrolyte)": 1.5,
        "Negative electrode Bruggeman coefficient (electrode)": 0,
        "Negative electrode double-layer capacity [F.m-2]": 42e6,
        # positive electrode
        "Positive electrode conductivity [S.m-1]": 0.0521,
        "Positive electrode porosity": 0.67,
        "Positive electrode active material volume fraction": 0.33,
        "Positive particle radius [m]": 0.99,
        "Positive electrode Bruggeman coefficient (electrolyte)": 1.5,
        "Positive electrode Bruggeman coefficient (electrode)": 0,
        "Positive electrode double-layer capacity [F.m-2]": 42e6,
        # separator
        "Separator porosity": 0.6,
        "Separator Bruggeman coefficient (electrolyte)": 1.5,
        # electrolyte
        "Initial concentration in electrolyte [mol.m-3]": 930,
        "Cation transference number": 0.5,
        "Thermodynamic factor": 1.0,
        "Electrolyte diffusivity [m2.s-1]": 3.5e-11,
        "Electrolyte conductivity [S.m-1]": 0.067,
        # experiment
        "Reference temperature [K]": 298.15,
        "Ambient temperature [K]": 298.15,
        "Initial temperature [K]": 298.15,
        "Number of electrodes connected in parallel to make a cell": 1.0,
        "Number of cells connected in series to make a battery": 1.0,
        "Lower voltage cut-off [V]": 0,
        "Upper voltage cut-off [V]": 10,
        # citations
        "notcite": ["Verbrugge2005"],
    }
