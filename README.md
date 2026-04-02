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

Generate plots:

```bash
python3 visualize.py tests/mixed_suite.in solver_output.txt --output-dir plots --format png
```
