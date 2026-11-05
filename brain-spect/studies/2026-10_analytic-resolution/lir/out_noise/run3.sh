for c in current_conv uniform_parallel uniform_conv; do
micromamba run -n raytracing env -u DISPLAY PYTHONPATH=$HOME/Work/RPIL/QMIRT/pytorch-optix python -u $HOME/Work/RPIL/QMIRT/qmirt-gate-10-sim/dev/reports/2026-10-28_analytic_resolution/lir/lir_build.py --case $c --noise-c1 2.5e6 --f32 --out $HOME/Work/RPIL/QMIRT/qmirt-gate-10-sim/dev/reports/2026-10-28_analytic_resolution/lir/out_noise/$c > $HOME/Work/RPIL/QMIRT/qmirt-gate-10-sim/dev/reports/2026-10-28_analytic_resolution/lir/out_noise/$c.log 2>&1
done
