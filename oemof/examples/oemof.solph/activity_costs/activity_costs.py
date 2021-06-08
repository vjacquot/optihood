# -*- coding: utf-8 -*-

"""
General description
-------------------
This example illustrates the effect of activity_costs.

There are the following components:

    - demand_heat: heat demand (constant, for the sake of simplicity)
    - fireplace: wood firing, burns "for free" if somebody is around
    - boiler: gas firing, consumes (paid) gas

Notice that activity_costs is an attribute to NonConvex.
This is because it relies on the activity status of a component
which is only available for nonconvex flows.


Installation requirements
-------------------------
This example requires version 0.3 of oemof. Install by:

    pip install 'oemof.solph>=0.4,<0.5'

"""

import numpy as np
import pandas as pd
from oemof import solph


try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

##########################################################################
# Calculate parameters and initialize the energy system and
##########################################################################

periods = 24
time = pd.date_range('1/1/2018', periods=periods, freq='H')

demand_heat = np.full(periods, 5)
demand_heat[:4] = 0
demand_heat[4:18] = 4

activity_costs = np.full(periods, 5)
activity_costs[18:] = 0

es = solph.EnergySystem(timeindex=time)

b_heat = solph.Bus(label='b_heat')

es.add(b_heat)

sink_heat = solph.Sink(
    label='demand',
    inputs={b_heat: solph.Flow(fix=demand_heat, nominal_value=1)})

fireplace = solph.Source(
    label='fireplace',
    outputs={b_heat: solph.Flow(nominal_value=3,
                                variable_costs=0,
                                nonconvex=solph.NonConvex(
                                    activity_costs=activity_costs))})

boiler = solph.Source(
    label='boiler',
    outputs={b_heat: solph.Flow(nominal_value=10,
                                variable_costs=1)})

es.add(sink_heat, fireplace, boiler)

##########################################################################
# Optimise the energy system
##########################################################################

# create an optimization problem and solve it
om = solph.Model(es)

# solve model
om.solve(solver='cbc', solve_kwargs={'tee': True})

##########################################################################
# Check and plot the results
##########################################################################

results = solph.processing.results(om)

# plot data
if plt is not None:
    data = solph.views.node(results, 'b_heat')['sequences']
    ax = data.plot(kind='line', drawstyle='steps-post', grid=True, rot=0)
    ax.set_xlabel('Time')
    ax.set_ylabel('Heat (arb. units)')
    plt.show()
