#
# Supercapacitor model from the Verbrugge & Liu (2005) paper
#
import pybamm


class VerbruggeLiu(pybamm.lithium_ion.BaseModel):
    """Supercapacitor model from the Verbrugge & Liu (2005) paper.


    Parameters
    ----------
    name : str, optional
        The name of the model.
    """

    def __init__(self, name="Single Particle Model"):
        super().__init__({}, name)
        # pybamm.citations.register("Marquis2019")  # need to register the citation
        # `param` is a class containing all the relevant parameters and functions for
        # this model. These are purely symbolic at this stage, and will be set by the
        # `ParameterValues` class when the model is processed.
        param = self.param

        ######################
        # Variables
        ######################
        # Variables that depend on time only are created without a domain
        Q = pybamm.Variable("Discharge capacity [A.h]")

        # Variables that vary spatially are created with a domain

        # Electrolyte concentration
        c_e_n = pybamm.Variable(
            "Negative electrolyte concentration [mol.m-3]",
            domain="negative electrode",
        )
        c_e_s = pybamm.Variable(
            "Separator electrolyte concentration [mol.m-3]",
            domain="separator",
        )
        c_e_p = pybamm.Variable(
            "Positive electrolyte concentration [mol.m-3]",
            domain="positive electrode",
        )

        # Concatenations combine several variables into a single variable, to simplify
        # implementing equations that hold over several domains
        c_e = pybamm.concatenation(c_e_n, c_e_s, c_e_p)

        # Electrolyte potential
        phi_e_n = pybamm.Variable(
            "Negative electrolyte potential [V]",
            domain="negative electrode",
        )
        phi_e_s = pybamm.Variable(
            "Separator electrolyte potential [V]",
            domain="separator",
        )
        phi_e_p = pybamm.Variable(
            "Positive electrolyte potential [V]",
            domain="positive electrode",
        )
        phi_e = pybamm.concatenation(phi_e_n, phi_e_s, phi_e_p)

        # Electrode potential

        # Due to the double layer capacitance, we can't define the potential in the
        # electrode directly, so we define the potential difference between electrode
        # and electrolyte instead.
        delta_phi_n = pybamm.Variable(
            "Negative electrode potential difference [V]",
            domain="negative electrode",
        )
        delta_phi_p = pybamm.Variable(
            "Positive electrode potential difference [V]",
            domain="positive electrode",
        )

        # Constant temperature
        T = param.T_init

        ######################
        # Other set-up
        ######################

        # Current density
        i_cell = param.current_density_with_time

        # Porosity
        # Primary broadcasts are used to broadcast scalar quantities across a domain
        # into a vector of the right shape, for multiplying with other vectors
        eps_n = pybamm.PrimaryBroadcast(
            pybamm.Parameter("Negative electrode porosity"), "negative electrode"
        )
        eps_s = pybamm.PrimaryBroadcast(
            pybamm.Parameter("Separator porosity"), "separator"
        )
        eps_p = pybamm.PrimaryBroadcast(
            pybamm.Parameter("Positive electrode porosity"), "positive electrode"
        )
        eps = pybamm.concatenation(eps_n, eps_s, eps_p)

        # Active material volume fraction (eps + eps_s + eps_inactive = 1)
        eps_s_n = pybamm.Parameter("Negative electrode active material volume fraction")
        eps_s_p = pybamm.Parameter("Positive electrode active material volume fraction")

        # transport_efficiency
        tor_n = eps_n**param.n.b_e
        tor_s = eps_s**param.s.b_e
        tor_p = eps_p**param.p.b_e
        tor = pybamm.concatenation(tor_n, tor_s, tor_p)
        a_n = 3 * param.n.prim.epsilon_s_av / param.n.prim.R_typ
        a_p = 3 * param.p.prim.epsilon_s_av / param.p.prim.R_typ

        ######################
        # State of Charge
        ######################
        I = param.current_with_time
        # The `rhs` dictionary contains differential equations, with the key being the
        # variable in the d/dt
        self.rhs[Q] = I / 3600
        # Initial conditions must be provided for the ODEs
        self.initial_conditions[Q] = pybamm.Scalar(0)

        ######################
        # Electrode potential difference
        ######################
        sigma_eff_n = param.n.sigma(T) * eps_s_n**param.n.b_s
        sigma_eff_p = param.p.sigma(T) * eps_s_p**param.p.b_s
        self.rhs[delta_phi_n] = (
            pybamm.div(sigma_eff_n * pybamm.grad(delta_phi_n))
            + pybamm.div(sigma_eff_n * pybamm.grad(phi_e_n))
        ) / (a_n * param.n.C_dl(T))
        self.rhs[delta_phi_p] = (
            pybamm.div(sigma_eff_p * pybamm.grad(delta_phi_p))
            + pybamm.div(sigma_eff_p * pybamm.grad(phi_e_p))
        ) / (a_p * param.p.C_dl(T))
        self.boundary_conditions[delta_phi_n] = {
            "left": (i_cell / pybamm.boundary_value(-sigma_eff_n, "left"), "Neumann"),
            # "left": (-pybamm.boundary_value(phi_e, "left"), "Dirichlet"),
            "right": (
                i_cell
                / pybamm.boundary_value(param.kappa_e(c_e_n, T) * tor_n, "right"),
                "Neumann",
            ),
        }
        self.boundary_conditions[delta_phi_p] = {
            "left": (
                i_cell
                / pybamm.boundary_value(param.kappa_e(c_e_p, T) * tor_p, "left"),
                "Neumann",
            ),
            "right": (i_cell / pybamm.boundary_value(-sigma_eff_p, "right"), "Neumann"),
        }
        self.initial_conditions[delta_phi_n] = pybamm.Scalar(-0.1)
        self.initial_conditions[delta_phi_p] = pybamm.Scalar(0.1)

        ######################
        # Current in the electrolyte
        ######################
        a_j_n = -(
                pybamm.div(sigma_eff_n * pybamm.grad(delta_phi_n))
                + pybamm.div(sigma_eff_n * pybamm.grad(phi_e_n))
        )
        a_j_s = pybamm.PrimaryBroadcast(0, "separator")
        a_j_p = -(
                pybamm.div(sigma_eff_p * pybamm.grad(delta_phi_p))
                + pybamm.div(sigma_eff_p * pybamm.grad(phi_e_p))
        )
        a_j = pybamm.concatenation(a_j_n, a_j_s, a_j_p) 
        i_e = - param.kappa_e(c_e, T) * tor * pybamm.grad(phi_e)
        # multiply by Lx**2 to improve conditioning
        self.algebraic[phi_e] = param.L_x**2 * (pybamm.div(i_e) + a_j)
        self.boundary_conditions[phi_e] = {
            "left": (pybamm.Scalar(0), "Dirichlet"),
            # "left": (pybamm.Scalar(0), "Neumann"),
            "right": (pybamm.Scalar(0), "Neumann"),
        }
        self.initial_conditions[phi_e] = pybamm.Scalar(0)

        ######################
        # Electrolyte concentration
        ######################
        N_e = -tor * param.D_e(c_e, T) * pybamm.grad(c_e)
        self.rhs[c_e] = (1 / eps) * (
            -pybamm.div(N_e) - (1 - param.t_plus(c_e, T)) * a_j / param.F
        )
        self.boundary_conditions[c_e] = {
            "left": (pybamm.Scalar(0), "Neumann"),
            "right": (pybamm.Scalar(0), "Neumann"),
        }
        self.initial_conditions[c_e] = param.c_e_init

        ######################
        # (Some) variables
        ######################
        # Interfacial reactions
        phi_s_n = delta_phi_n + phi_e_n
        phi_s_p = delta_phi_p + phi_e_p
        V = pybamm.boundary_value(phi_s_p, "right") - pybamm.boundary_value(phi_s_n, "left")
        num_cells = pybamm.Parameter(
            "Number of cells connected in series to make a battery"
        )

        # The `variables` dictionary contains all variables that might be useful for
        # visualising the solution of the model
        # Primary broadcasts are used to broadcast scalar quantities across a domain
        # into a vector of the right shape, for multiplying with other vectors
        self.variables = {
            "Time [s]": pybamm.t,
            "Discharge capacity [A.h]": Q,
            "Current [A]": I,
            "Current variable [A]": I,  # for compatibility with pybamm.Experiment
            "Electrolyte concentration [mol.m-3]": c_e,
            "Negative electrode potential [V]": phi_s_n,
            "Electrolyte potential [V]": phi_e,
            "Positive electrode potential [V]": phi_s_p,
            "Voltage [V]": V,
            "Battery voltage [V]": V * num_cells,
            "Negative electrolyte concentration [mol.m-3]": c_e_n,
            "Separator electrolyte concentration [mol.m-3]": c_e_s,
            "Positive electrolyte concentration [mol.m-3]": c_e_p,
            "Negative electrode potential difference [V]": delta_phi_n,
            "Positive electrode potential difference [V]": delta_phi_p,
            "Negative electrolyte potential [V]": phi_e_n,
            "Separator electrolyte potential [V]": phi_e_s,
            "Positive electrolyte potential [V]": phi_e_p,
            "Negative electrode interfacial current density [A.m-3]": a_j_n,
            "Positive electrode interfacial current density [A.m-3]": a_j_p,
        }

    @property
    def default_quick_plot_variables(self):
        return [
            "Current [A]",
            "Voltage [V]",
            "Electrolyte concentration [mol.m-3]",
            "Electrolyte potential [V]",
            "Negative electrode potential [V]",
            "Positive electrode potential [V]",
            "Negative electrode interfacial current density [A.m-3]",
            "Positive electrode interfacial current density [A.m-3]",
        ]
