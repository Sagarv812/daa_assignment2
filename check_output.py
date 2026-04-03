import sys

def check(in_file, out_file):
    with open(in_file, 'r') as f:
        in_lines = f.read().split()
    
    idx = 0
    test_cases = []
    T = int(in_lines[idx]); idx += 1
    for _ in range(T):
        outer = int(in_lines[idx]); idx += 1
        idx += 2 * outer
        h = int(in_lines[idx]); idx += 1
        inner_sizes = []
        for _ in range(h):
            s = int(in_lines[idx]); idx += 1
            idx += 2 * s
            inner_sizes.append(s)
        test_cases.append({'outer': outer, 'h': h, 'inner': inner_sizes})
        
    with open(out_file, 'r') as f:
        out_lines = f.read().split()
    
    out_idx = 0
    for i, tc in enumerate(test_cases):
        n = tc['outer'] + sum(tc['inner'])
        h = tc['h']
        expected_triangles = n + 2 * h - 2
        actual_triangles = int(out_lines[out_idx]); out_idx += 1
        out_idx += 6 * actual_triangles # 3 vertices * 2 coords
        guard_count = int(out_lines[out_idx]); out_idx += 1
        out_idx += 2 * guard_count
        
        if expected_triangles != actual_triangles:
            print(f"Test case {i+1} FAIL: Expected {expected_triangles} triangles, got {actual_triangles}")
        else:
            print(f"Test case {i+1} PASS: matched {expected_triangles}")

check("tests/hard_suite.in", "output_hard.txt")
