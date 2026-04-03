# DAA Assignment 2 - Art Gallery Problem

Current workspace layout:

- `ans.cpp`: original monolithic draft kept as reference.
- `inc/`: all header files kept directly in one folder.
- `src/`: all `.cpp` files kept directly in one folder.
- `tests/`: sample assignment-format input files.
- `Makefile`: simple build setup using `g++`.
- `test.sh`: assignment-friendly script that builds and runs the program.
- `visualize.py`: generates `matplotlib` plots of the input polygon and its triangulation.

Build and run:

```bash
./test.sh tests/mixed_suite.in
```

If `matplotlib` is installed in a specific Python environment, you can run:

```bash
PYTHON=<path_to_env> ./test.sh tests/mixed_suite.in
```

`test.sh` now:
- builds the art gallery solver
- runs it on the given input file
- saves the solver output in `solver_output.txt`
- generates plot files in `plots/`

Check triangle counts without plotting:

```bash
./check_triangle_counts.py tests/hard_suite.in
```

`check_triangle_counts.py`:
- builds the solver by default
- runs it on the given assignment-format input file(s)
- compares each case against the theoretical count `n + 2h - 2`
- exits with status `0` on full success and `1` if any case mismatches

Generate plots:

```bash
python3 visualize.py tests/mixed_suite.in solver_output.txt --output-dir plots --format png
```
