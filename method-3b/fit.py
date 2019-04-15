#!/usr/bin/env python3
#
# Method 3b: Simulate the traditional protocols, calculate the summary
# statistic, and then optimise the model to match the experimental summary
# statistics.
#
from __future__ import division, print_function
import os
import sys
import pints
import numpy as np
import myokit

# Load project modules
sys.path.append(os.path.abspath(os.path.join('..', 'python')))
import boundaries
import cells
import errors
import transformation


#
# Check input arguments
#
base = os.path.splitext(os.path.basename(__file__))[0]
args = sys.argv[1:]
if len(args) != 1:
    print('Syntax: ' + base + '.py <cell>')
    sys.exit(1)
cell = int(args[0])
filename = 'cell-' + str(cell) + '-fit-3b'
print('Selected cell ' + str(cell))
print('Storing results to ' + filename + '.txt')


#
# Define error function, boundaries, and parameter transformation
#
trans = transformation.Transformation()
boundaries = boundaries.Boundaries(cells.lower_conductance(cell), trans)
f = errors.E3(cell, trans)


#
# Run
#
b = myokit.Benchmarker()
repeats = 1
params, scores = [], []
times = []
for i in range(repeats):
    print('Repeat ' + str(1 + i))

    # Choose random starting point
    # Allow resampling, in case calculation of summary statistics fails
    print('Choosing starting point')
    #q0 = f0 = float('inf')
    #while not np.isfinite(f0):
    #    q0 = boundaries.sample()    # Search space
    #    f0 = f(q0)                  # Initial score
    import results
    p0 = results.load_parameters(cell, 1)
    q0 = trans.transform(p0)


    # Create optimiser
    opt = pints.OptimisationController(
        f, q0, boundaries=boundaries, method=pints.CMAES)
    opt.set_log_to_file(filename + '-log-' + str(i) + '.csv', True)
    opt.set_max_iterations(None)
    opt.set_parallel(True)

    # Run optimisation
    try:
        with np.errstate(all='ignore'): # Tell numpy not to issue warnings
            b.reset()
            q, s = opt.run()            # Search space
            times.append(b.time())
            p = trans.detransform(q)    # Model space
            params.append(p)
            scores.append(s)
    except ValueError:
        import traceback
        traceback.print_exc()

# Order from best to worst
order = np.argsort(scores)
scores = np.asarray(scores)[order]
params = np.asarray(params)[order]
times = np.asarray(times)[order]

# Show results
print('Best scores:')
for score in scores[:10]:
    print(score)
print('Mean & std of score:')
print(np.mean(scores))
print(np.std(scores))
print('Worst score:')
print(scores[-1])

# Extract best
obtained_score = scores[0]
obtained_parameters = params[0]

# Store results
print('Storing best result...')
with open(filename + '.txt', 'w') as f:
    for x in obtained_parameters:
        f.write(pints.strfloat(x) + '\n')

print('Storing all errors')
with open(filename + '-errors.txt', 'w') as f:
    for score in scores:
        f.write(pints.strfloat(score) + '\n')

print('Storing all parameters')
for i, param in enumerate(params):
    with open(filename + '-parameters-' + str(1 + i) + '.txt', 'w') as f:
        for x in param:
            f.write(pints.strfloat(x) + '\n')

print('Storing all simulation times')
with open(filename + '-times.txt', 'w') as f:
    for time in times:
        f.write(pints.strfloat(time) + '\n')

