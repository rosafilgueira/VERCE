#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Input file writer for SPECFEM3D_CARTESIAN with support for the CEM project.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
    Emanuele Casarotti (emanuele.casarotti@ingv.it), 2013
:license:
    GNU General Public License, Version 3
    (http://www.gnu.org/copyleft/gpl.html)
"""
import inspect
import math
import os

# Define the required configuration items. The key is always the name of the
# configuration item and the value is a tuple. The first item in the tuple is
# the function or type that it will be converted to and the second is the
# documentation.
REQUIRED_CONFIGURATION = {
    "RECORD_LENGTH_IN_MINUTES": (float, "record length in minutes"),
    "SIMULATION_TYPE": (
        int, "forward or adjoint simulation, 1 = forward, "
        "2 = adjoint for sources, 3 = kernel simulations"),
    "NCHUNKS": (int, "number of chunks (1, 2, 3, or 6)"),
    # number of elements at the surface along the two sides of the first chunk
    # (must be multiple of 16 and 8 * multiple of NPROC below)
    "NEX_XI": (int, "number of elements at the surface along the xi side "
                    "of the first chunk (must be multiple of 16 and 8 * "
                    "multiple of NPROC_XI)."),
    "NEX_ETA": (int, "number of elements at the surface along the eta side "
                     "of the first chunk (must be multiple of 16 and 8 * "
                     "multiple of NPROC_ETA)."),
    # number of MPI processors along the two sides of the first chunk
    "NPROC_XI": (int, "number of MPI processors along the xi side of the "
                      "first chunk."),
    "NPROC_ETA": (int, "number of MPI processors along the eta side of the "
                       "first chunk."),
    "MODEL": (str, "The used model. See the manual for a number of choices. ")
}

# The default configuration item. Contains everything that can sensibly be set
# to some default value. The syntax is very similar to the
# REQUIRED_CONFIGURATION except that the tuple now has three items, the first
# one being the actual default value.
DEFAULT_CONFIGURATION = {
    "NOISE_TOMOGRAPHY":
        (0, int,  "flag of noise tomography, three steps (1,2,3). If "
                  "earthquake simulation, set it to 0."),
    "SAVE_FORWARD": (False, bool, "save last frame of forward simulation or "
                                  "not"),
    "ANGULAR_WIDTH_XI_IN_DEGREES": (90.0, float, "Width of one side of the "
                                                 "chunk"),
    "ANGULAR_WIDTH_ETA_IN_DEGREES": (90.0, float,
                                     "Width of the other side of the chunk"),
    "CENTER_LATITUDE_IN_DEGREES": (40.0, float, "Laitude center of chunk"),
    "CENTER_LONGITUDE_IN_DEGREES": (10.0, float, "Longitude center of chunk"),
    "GAMMA_ROTATION_AZIMUTH": (
        0.0, float, "Defines the rotation angle of the chunk about its "
                    "center measured counter clockwise from due North "
                    "(degrees)."),

    "OCEANS": (True, bool, "parameter describing the earth model."),
    "ELLIPTICITY": (True, bool, "parameter describing the earth model."),
    "TOPOGRAPHY": (True, bool, "parameter describing the earth model."),
    "GRAVITY": (True, bool, "parameter describing the earth model."),
    "ROTATION": (True, bool, "parameter describing the earth model."),
    "ATTENUATION": (True, bool, "parameter describing the earth model."),
    "ABSORBING_CONDITIONS": (False, bool, "absorbing boundary conditions for "
                                          "a regional simulation"),

    # to undo attenuation for sensitivity kernel calculations or forward
    # runs with SAVE_FORWARD
    # use one (and only one) of the two flags below. UNDO_ATTENUATION is
    # much better (it is exact)
    # but requires a significant amount of disk space for temporary storage.
    "ATTENUATION_1D_WITH_3D_STORAGE": (True, bool, ""),
    "PARTIAL_PHYS_DISPERSION_ONLY": (True, bool, ""),
    "UNDO_ATTENUATION": (False, bool, ""),

    "MEMORY_INSTALLED_PER_CORE_IN_GB": (4.0, float,
                                        "Memory available per core."),
    "PERCENT_OF_MEM_TO_USE_PER_CORE": (85.0, float,
                                       "Percent memory to use per core."),

    "EXACT_MASS_MATRIX_FOR_ROTATION":
        (False, bool,
         "three mass matrices instead of one are needed to handle rotation "
         "very accurately; otherwise rotation is handled slightly less "
         "accurately (but still reasonably well); set to .true. if you are "
         "interested in precise effects related to rotation; set to .false. "
         "if you are solving very large inverse problems at high frequency "
         "and also undoing attenuation exactly using the UNDO_ATTENUATION "
         "flag above, in which case saving as much memory as possible can be "
         "a good idea. You can also safely set it to .false. if you are not "
         "in a period range in which rotation matters, e.g. if you are "
         "targetting very short-period body waves. if in doubt, set to "
         ".true. Set it to .true. if you have ABSORBING_CONDITIONS above, "
         "because in that case the code will use the three mass matrices "
         "anyway and thus there is no additional cost. this flag is of "
         "course unused if ROTATION above is set to .false."),

    "USE_LDDRK": (False, bool, "this for LDDRK high-order time scheme instead "
                               "of Newmark"),
    "INCREASE_CFL_FOR_LDDRK":
        (True, bool,
         "the maximum CFL of LDDRK is significantly higher than that of the "
         "Newmark scheme, in a ratio that is theoretically 1.327 / 0.697 = "
         "1.15 / 0.604 = 1.903 for a solid with Poisson's ratio = 0.25 and "
         "for a fluid (see the manual of the 2D code, SPECFEM2D, Tables 4.1 "
         "and 4.2, and that ratio does not depend on whether we are in 2D or "
         "in 3D). However in practice a ratio of about 1.5 to 1.7 is often "
         "safer (for instance for models with a large range of Poisson's "
         "ratio values). Since the code computes the time step using the "
         "Newmark scheme, for LDDRK we will simply multiply that time step "
         "by this ratio when LDDRK is on and when flag "
         "INCREASE_CFL_FOR_LDDRK is true."),
    "RATIO_BY_WHICH_TO_INCREASE_IT": (1.5, float, ""),

    "MOVIE_SURFACE": (False, bool, ""),
    "MOVIE_VOLUME": (False, bool, ""),
    "MOVIE_COARSE": (False, bool, "Saves movie only at corners of elements."),
    "NTSTEP_BETWEEN_FRAMES": (100, int, ""),
    "HDUR_MOVIE": (0.0, float, 0.0),

    # save movie in volume.  Will save element if center of element is in
    # prescribed volume
    # top/bottom: depth in KM, use MOVIE_TOP = -100 to make sure the surface
    #  is stored.
    # west/east: longitude, degrees East [-180/180] top/bottom: latitute,
    # degrees North [-90/90]
    # start/stop: frames will be stored at MOVIE_START +
    # i*NSTEP_BETWEEN_FRAMES, where i=(0,1,2..) and iNSTEP_BETWEEN_FRAMES <=
    #  MOVIE_STOP
    # movie_volume_type: 1=strain, 2=time integral of strain, 3=\mu*time
    # integral of strain
    # type 4 saves the trace and deviatoric stress in the whole volume,
    # 5=displacement, 6=velocity
    "MOVIE_VOLUME_TYPE": (2, int, ""),
    "MOVIE_TOP_KM": (-100.0, float, ""),
    "MOVIE_BOTTOM_KM": (1000.0, float, ""),
    "MOVIE_WEST_DEG": (-90.0, float, ""),
    "MOVIE_EAST_DEG": (90.0, float, ""),
    "MOVIE_NORTH_DEG": (90.0, float, ""),
    "MOVIE_SOUTH_DEG": (-90.0, float, ""),
    "MOVIE_START": (0, int, ""),
    "MOVIE_STOP": (40000, int, ""),

    # I/O flags.
    "SAVE_MESH_FILES": (False, bool, "save mesh files to check the mesh"),
    "NUMBER_OF_RUNS": (1, int, "restart files (number of runs can be 1 or "
                               "higher, choose 1 for no restart files)"),
    "NUMBER_OF_THIS_RUN": (1, int, ""),
    "LOCAL_PATH": ("./DATABASES_MPI", str,
                   "path to store the local database files on each node"),
    "LOCAL_TMP_PATH": ("./DATABASES_MPI", str,
                       "temporary wavefield/kernel/movie files"),
    "NTSTEP_BETWEEN_OUTPUT_INFO": (1000, int,
                                   "interval at which we output time step "
                                   "info and max of norm of displacement"),
    "NTSTEP_BETWEEN_OUTPUT_SEISMOS": (5000000, int,
                                      "interval in time steps for temporary "
                                      "writing of seismograms"),
    "NTSTEP_BETWEEN_READ_ADJSRC": (1000, int, ""),

    "OUTPUT_SEISMOS_ASCII_TEXT": (True, bool, ""),
    "OUTPUT_SEISMOS_SAC_ALPHANUM": (False, bool, ""),
    "OUTPUT_SEISMOS_SAC_BINARY": (False, bool, ""),
    "OUTPUT_SEISMOS_ASDF": (False, bool, ""),


    "ROTATE_SEISMOGRAMS_RT": (False, bool,
                              "rotate seismograms to Radial-Transverse-Z or "
                              "use default North-East-Z reference frame"),
    "WRITE_SEISMOGRAMS_BY_MASTER": (True, bool,
                                    "decide if master process writes all the "
                                    "seismograms or if all processes do it in "
                                    "parallel"),
    "SAVE_ALL_SEISMOS_IN_ONE_FILE": (False, bool,
                                     "save all seismograms in one large "
                                     "combined file instead of one file per "
                                     "seismogram to avoid overloading shared "
                                     "non-local file systems such as GPFS for "
                                     "instance"),
    "USE_BINARY_FOR_LARGE_FILE": (False, bool, ""),
    "RECEIVERS_CAN_BE_BURIED": (True, bool, "flag to impose receivers at the "
                                            "surface or allow them to be "
                                            "buried"),
    "PRINT_SOURCE_TIME_FUNCTION": (False, bool, "Print source time function."),

    #  adjoint kernel flags
    "READ_ADJSRC_ASDF": (False, bool,
                         "Use ASDF format for reading the adjoint sources"),
    "ANISOTROPIC_KL": (False, bool,
                       "this parameter must be set to .true. to compute "
                       "anisotropic kernels in crust and mantle (related to "
                       "the 21 Cij in geographical coordinates) default is "
                       ".false. to compute isotropic kernels (related to "
                       "alpha and beta)"),
    "SAVE_TRANSVERSE_KL_ONLY": (False, bool,
                                "output only transverse isotropic kernels "
                                "(alpha_v,alpha_h,beta_v,beta_h,eta,rho) "
                                "rather than fully anisotropic kernels when "
                                "ANISOTROPIC_KL above is set to .true. means "
                                "to save radial anisotropic kernels, i.e., "
                                "sensitivity kernels for beta_v, beta_h, "
                                "etc."),
    "APPROXIMATE_HESS_KL": (False, bool,
                            "output approximate Hessian in crust mantle "
                            "region. means to save the preconditioning for "
                            "gradients, they are cross correlations between "
                            "forward and adjoint accelerations."),
    "USE_FULL_TISO_MANTLE": (False, bool,
                             "forces transverse isotropy for all mantle "
                             "elements (default is to use transverse isotropy "
                             "only between MOHO and 220) means we allow "
                             "radial anisotropy between the bottom of the "
                             "crust to the bottom of the transition zone, "
                             "i.e., 660~km depth."),
    "SAVE_SOURCE_MASK": (False, bool, "output kernel mask to zero out source "
                                      "region to remove large values near "
                                      "the sources in the sensitivity "
                                      "kernels"),
    "SAVE_REGULAR_KL": (False, bool, "output kernels on a regular grid "
                                     "instead of on the GLL mesh points "
                                     "(a bit expensive)"),

    "NUMBER_OF_SIMULTANEOUS_RUNS": (1, int, "Number of simultaneous runs"),

    "BROADCAST_SAME_MESH_AND_MODEL":
        (False, bool, "Use same mesh and model for all simultaneous runs."),

    "USE_FAILSAFE_MECHANISM": (False, bool,
                               "Failsafe mechanism for simultaneous runs"),


    "GPU_MODE": (False, bool, "set to true to use GPUs"),
    "GPU_RUNTIME": (1, int, "Only used if GPU_MODE=True"),
    "GPU_PLATFORM": ("NVIDIA", str, "GPU platform to use"),
    "GPU_DEVICE": ("Tesla", str, "GPU device to use."),

    # Adios related settings.
    "ADIOS_ENABLED": (False, bool, "set to true to use the ADIOS library for "
                                   "I/Os"),
    "ADIOS_FOR_FORWARD_ARRAYS": (True, bool, ""),
    "ADIOS_FOR_MPI_ARRAYS": (True, bool, ""),
    "ADIOS_FOR_ARRAYS_SOLVER": (True, bool, ""),
    "ADIOS_FOR_SOLVER_MESHFILES": (True, bool, ""),
    "ADIOS_FOR_AVS_DX": (True, bool, ""),
    "ADIOS_FOR_KERNELS": (True, bool, ""),
    "ADIOS_FOR_MODELS": (True, bool, ""),
    "ADIOS_FOR_UNDO_ATTENUATION": (True, bool, "")
}


def write(config):
    """
    Writes a Par_file for SPECFEM3D_GLOBE.
    """

    def fbool(value):
        """
        Convert a value to a FORTRAN boolean representation.
        """
        if value:
            return ".true."
        else:
            return ".false."

    for key, value in config.iteritems():
        if isinstance(value, bool):
            config[key] = fbool(value)

    template_file = os.path.join(os.path.dirname(os.path.abspath(
        inspect.getfile(inspect.currentframe()))),
        "specfem_globe_par_file.template")
    with open(template_file, "rt") as fh:
        par_file_template = fh.read()

    par_file = par_file_template.format(**config).strip()

    return par_file
