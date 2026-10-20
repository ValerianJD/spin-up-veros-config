# VEROS configuration for the P2F global ocean circulation model spin-up competition

First, install VEROS by following these instructions: https://veros.readthedocs.io/en/latest/introduction/get-started.html

You should now have a Conda environment (that may be named `veros`).
Activate it with `conda activate veros`.
You can now run any Python script importing the VEROS model.

The file "Example_run_veros.py" is given as example to run a 200-year-long spinup of the model by calling `python Example_run_veros.py`.

## Some additional details about the structure of VEROS restart files and computation

The restart is a plain HDF5 file written with h5py. The model state is in the group “core”, while the additional groups (e.g. the "averages" diagnostic) do not affect the model evolution. Arrays are stored in VEROS index order (x, y, z, time level) (which differs from the netCDF snapshot/averages output of dimension (time, z, y, x)).

The restart contains every variable that is read during a time step before being recomputed in that step. They fall into four groups:

Prognostic state: temp, salt, u, v, psi (barotropic streamfunction; the setup uses a rigid lid), tke, eke. These are the only independent degrees of freedom used in the code for the restart. Note that the depth-mean part of u and v is replaced at every step by the barotropic flow derived from psi, so only their baroclinic part is independent of psi.

Diagnostics stored and used at the start of a step: rho, int_drhodT, int_drhodS, Nsqr and Hd (functions of temp and salt through the equation of state), w (diagnosed from u and v by continuity) and K_diss_v (the vertical-friction dissipation of the previous step, used by the TKE closure). They do affect the first step after a restart, but they carry no independent information and are recomputed within one step.

Time-stepping history: dtemp, dsalt, du, dv, dtke, deke, dpsi, dpsin are the tendencies of the previous step, required by the Adams-Bashforth scheme.

Bookkeeping: tau, taum1, taup1 and time. The model time is not inert: it sets the phase of the seasonal cycle of the surface forcing.

The three snapshots come from the time stepping. Tracers, momentum, TKE and EKE use a second-order Adams-Bashforth scheme and the last axis of each field is a rotating three-level buffer. The scalars tau, taum1 and taup1 in the file give the indices of the current, previous and next levels. Because the buffer rotates, the current state is not always in the same slot.

Strictly, the model reads only the tau level of the prognostic fields and the taum1 level of the tendencies but an exactly repeatable restart should keep the file as written. An alternative consistent choice is to write the same field into all three levels of each prognostic variable you change; the stored diagnostics and tendencies are then inconsistent for one time step only, after which the model recomputes them.

Finally, VEROS stores arrays with their overlap regions, so every horizontal field includes 2 halo cells on each side in x and y. For the 4deg setup the global shape is (94, 44, ...) for nx = 90, ny = 40, and the physical domain is [2:-2, 2:-2]. The domain is periodic in x, so the x-halos are copies of the opposite edge and are rebuilt from the interior when the restart is read.

The grid is an Arakawa C-grid, and the placement of each field is:

T-points (xt, yt, zt): temp, salt, rho, int_drhodT, int_drhodS, Hd, dtemp, dsalt -> maskT
U-points (xu, yt, zt): u, du -> maskU
V-points (xt, yu, zt): v, dv -> maskV
W-points (xt, yt, zw): w, Nsqr, tke, eke, dtke, deke, K_diss_v -> maskW
Corner points (xu, yu): psi, dpsi -> maskZ at the surface level. Note that psi is not zero over land: it is constant on each island, and dpsin holds the per-island coefficients.

The vertical index increases upwards (k = 0 is the deepest level, k = nz - 1 the surface). The masks are not stored but computed at setup from the bathymetry through kbot, the index of the deepest wet cell (kbot = 0 for a land column):

maskT[i,j,k] = 1 if kbot[i,j] > 0 and k >= kbot[i,j] - 1, else 0
maskU[i,j,k] = min(maskT[i,j,k], maskT[i+1,j,k])
maskV[i,j,k] = min(maskT[i,j,k], maskT[i,j+1,k])
maskW[i,j,k] = min(maskT[i,j,k], maskT[i,j,k+1]), and maskW = maskT at the surface level
maskZ[i,j,k] = min(maskT[i,j,k], maskT[i,j+1,k], maskT[i+1,j,k])
