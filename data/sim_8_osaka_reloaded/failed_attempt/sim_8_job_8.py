from tumorsphere.simulation import SimulationLite

# Parameter list
prob_stem = [0.1, 0.2, 0.3, 0.4, 0.45, 0.5, 0.9, 0.95]
prob_diff = [0]
realizations=4
steps_per_realization=60
rng_seed=1292317634567
parallel_processes = 32

sim = SimulationLite(
    first_cell_is_stem=True,
    prob_stem=prob_stem,
    prob_diff=prob_diff,
    num_of_realizations=realizations,
    num_of_steps_per_realization=steps_per_realization,
    rng_seed=rng_seed,
    cell_radius=1,
    adjacency_threshold=4,
    cell_max_repro_attempts=1000,
    # continuous_graph_generation=False, # for Simulation
)
sim.simulate_parallel(parallel_processes)

# python -m tumorsphere.cli --prob-stem "0.1,0.2,0.3,0.4,0.45,0.5,0.9,0.95" --prob-diff "0" --realizations 4 --steps-per-realization 60 --rng-seed 1292317634567 --parallel-processes 32
