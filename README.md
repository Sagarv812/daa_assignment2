# daa_assignment2

Current workspace layout:

- `ans.cpp`: original monolithic draft kept as reference.
- `inc/`: all header files kept directly in one folder.
- `src/`: all `.cpp` files kept directly in one folder.
- `Makefile`: simple build setup using `g++`.
- `test.sh`: assignment-friendly script that builds and runs the program.

Build and run:

```bash
./test.sh < input.txt
```

If you want, the next cleanup step can be moving triangulation and guard-placement into their own modules too.
