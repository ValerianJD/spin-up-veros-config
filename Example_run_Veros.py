# !/usr/bin/env python3

from global_4deg_no_cycle import GlobalFourDegreeSetup as setup

path_files = "./"
identifier = "spinup_200"
run_len = 50 * 86400 * 360  # in seconds
restart_name = "./Init_state.restart.h5"

model = setup(
    identifier,
    run_len,
    restart_name,
    snap_out_freq=86400 * 30,
    restart_mode=(len(restart_name) > 0),
)
model.setup()
model.run()
