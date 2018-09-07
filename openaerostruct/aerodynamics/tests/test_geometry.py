import unittest
import numpy as np

from openmdao.api import Group, IndepVarComp, Problem
from openmdao.utils.assert_utils import assert_check_partials

from openaerostruct.aerodynamics.geometry import VLMGeometry
from openaerostruct.geometry.utils import generate_mesh
from openaerostruct.utils.testing import run_test, get_default_surfaces


class Test(unittest.TestCase):

    def test(self):
        surfaces = get_default_surfaces()

        group = Group()

        comp = VLMGeometry(surface=surfaces[0])

        indep_var_comp = IndepVarComp()

        indep_var_comp.add_output('def_mesh', val=surfaces[0]['mesh'], units='m')

        group.add_subsystem('geom', comp)
        group.add_subsystem('indep_var_comp', indep_var_comp)

        group.connect('indep_var_comp.def_mesh', 'geom.def_mesh')

        run_test(self, group)

    def test_derivs_wetted(self):
        # This is a much richer test with the following attributes:
        # - 5x7 mesh so that each dimension of all variables is unique.
        # - Random values given as inputs.
        # - The mesh has been given a random z height at all points.
        # - S_ref_type option is "wetted"
        # Create a dictionary to store options about the mesh
        mesh_dict = {'num_y' : 7,
                     'num_x' : 5,
                     'wing_type' : 'CRM',
                     'symmetry' : True,
                     'num_twist_cp' : 5}

        # Generate the aerodynamic mesh based on the previous dictionary
        mesh, twist_cp = generate_mesh(mesh_dict)

        mesh[:, :, 2] = np.random.random(mesh[:, :, 2].shape)

        # Create a dictionary with info and options about the aerodynamic
        # lifting surface
        surface = {
                    # Wing definition
                    'name' : 'wing',        # name of the surface
                    'type' : 'aero',
                    'symmetry' : True,     # if true, model one half of wing
                                            # reflected across the plane y = 0
                    'S_ref_type' : 'wetted', # how we compute the wing area,
                                             # can be 'wetted' or 'projected'
                    'fem_model_type' : 'tube',

                    'twist_cp' : twist_cp,
                    'mesh' : mesh,
                    'num_x' : mesh.shape[0],
                    'num_y' : mesh.shape[1],

                    # Aerodynamic performance of the lifting surface at
                    # an angle of attack of 0 (alpha=0).
                    # These CL0 and CD0 values are added to the CL and CD
                    # obtained from aerodynamic analysis of the surface to get
                    # the total CL and CD.
                    # These CL0 and CD0 values do not vary wrt alpha.
                    'CL0' : 0.0,            # CL of the surface at alpha=0
                    'CD0' : 0.015,            # CD of the surface at alpha=0

                    # Airfoil properties for viscous drag calculation
                    'k_lam' : 0.05,         # percentage of chord with laminar
                                            # flow, used for viscous drag
                    't_over_c_cp' : np.array([0.15]),      # thickness over chord ratio (NACA0015)
                    'c_max_t' : .303,       # chordwise location of maximum (NACA0015)
                                            # thickness
                    'with_viscous' : True,  # if true, compute viscous drag
                    'with_wave' : False,     # if true, compute wave drag
                    }

        #surfaces = get_default_surfaces()
        surfaces = [surface]

        prob = Problem()
        group = prob.model

        comp = VLMGeometry(surface=surfaces[0])

        indep_var_comp = IndepVarComp()
        indep_var_comp.add_output('def_mesh', val=surfaces[0]['mesh'], units='m')

        group.add_subsystem('geom', comp)
        group.add_subsystem('indep_var_comp', indep_var_comp)

        group.connect('indep_var_comp.def_mesh', 'geom.def_mesh')

        prob.setup()

        prob['geom.def_mesh'] = np.random.random(prob['geom.def_mesh'].shape)

        prob.run_model()

        check = prob.check_partials(compact_print=True)
        assert_check_partials(check, atol=3e-5, rtol=1e-5)

    def test_derivs_projected(self):
        # This is a much richer test with the following attributes:
        # - 5x7 mesh so that each dimension of all variables is unique.
        # - Random values given as inputs.
        # - The mesh has been given a random z height at all points.
        # - S_ref_type option is "projected"

        # Create a dictionary to store options about the mesh
        mesh_dict = {'num_y' : 7,
                     'num_x' : 5,
                     'wing_type' : 'CRM',
                     'symmetry' : True,
                     'num_twist_cp' : 5}

        # Generate the aerodynamic mesh based on the previous dictionary
        mesh, twist_cp = generate_mesh(mesh_dict)

        mesh[:, :, 2] = np.random.random(mesh[:, :, 2].shape)

        # Create a dictionary with info and options about the aerodynamic
        # lifting surface
        surface = {
                    # Wing definition
                    'name' : 'wing',        # name of the surface
                    'type' : 'aero',
                    'symmetry' : True,     # if true, model one half of wing
                                            # reflected across the plane y = 0
                    'S_ref_type' : 'projected', # how we compute the wing area,
                                             # can be 'wetted' or 'projected'
                    'fem_model_type' : 'tube',

                    'twist_cp' : twist_cp,
                    'mesh' : mesh,
                    'num_x' : mesh.shape[0],
                    'num_y' : mesh.shape[1],

                    # Aerodynamic performance of the lifting surface at
                    # an angle of attack of 0 (alpha=0).
                    # These CL0 and CD0 values are added to the CL and CD
                    # obtained from aerodynamic analysis of the surface to get
                    # the total CL and CD.
                    # These CL0 and CD0 values do not vary wrt alpha.
                    'CL0' : 0.0,            # CL of the surface at alpha=0
                    'CD0' : 0.015,            # CD of the surface at alpha=0

                    # Airfoil properties for viscous drag calculation
                    'k_lam' : 0.05,         # percentage of chord with laminar
                                            # flow, used for viscous drag
                    't_over_c_cp' : np.array([0.15]),      # thickness over chord ratio (NACA0015)
                    'c_max_t' : .303,       # chordwise location of maximum (NACA0015)
                                            # thickness
                    'with_viscous' : True,  # if true, compute viscous drag
                    'with_wave' : False,     # if true, compute wave drag
                    }

        #surfaces = get_default_surfaces()
        surfaces = [surface]

        prob = Problem()
        group = prob.model

        comp = VLMGeometry(surface=surfaces[0])

        indep_var_comp = IndepVarComp()
        indep_var_comp.add_output('def_mesh', val=surfaces[0]['mesh'], units='m')

        group.add_subsystem('geom', comp)
        group.add_subsystem('indep_var_comp', indep_var_comp)

        group.connect('indep_var_comp.def_mesh', 'geom.def_mesh')

        prob.setup()

        prob['geom.def_mesh'] = np.random.random(prob['geom.def_mesh'].shape)

        prob.run_model()

        check = prob.check_partials(compact_print=True)

        assert_check_partials(check, atol=3e-5, rtol=1e-5)


if __name__ == '__main__':
    unittest.main()
