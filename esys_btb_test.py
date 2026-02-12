import os

from oemof.solph import EnergySystem, Model, processing

# DONT REMOVE THIS LINE!
from oemof.tabular import datapackage  # noqa
from oemof.tabular.constraint_facades import CONSTRAINT_TYPE_MAP
from oemof.tabular.facades import TYPEMAP
from oemof.tabular.postprocessing import calculations


THIS_PATH = os.path.dirname(os.path.abspath(__file__))

# Path to directory with datapackage to load
datapackage_dir = os.path.join(THIS_PATH, "raw_data")

# Create  path for results (we use the datapackage_dir to store results)
results_path = os.path.join(
    os.path.expanduser(THIS_PATH), "results", "oemof"
)

if not os.path.exists(results_path):
    os.makedirs(results_path)

# Create energy system object
es = EnergySystem.from_datapackage(
    os.path.join(datapackage_dir, "datapackage.json"),
    attributemap={},
    typemap=TYPEMAP,
)

# Create model from energy system (this is just oemof.solph)
m = Model(es)

# Add constraints from datapackage to the model
m.add_constraints_from_datapackage(
    os.path.join(datapackage_dir, "datapackage.json"),
    constraint_type_map=CONSTRAINT_TYPE_MAP,
)

# If you want dual variables / shadow prices uncomment line below
# m.receive_duals()

# Select solver 'gurobi', 'cplex', 'glpk' etc
m.solve("cbc")

es.params = processing.parameter_as_dict(es)
es.results = m.results()

# Now we use the write results method to write the results in oemof-tabular
# format
postprocessed_results = calculations.run_postprocessing(es)
postprocessed_results.to_csv(os.path.join(results_path, "results.csv"))