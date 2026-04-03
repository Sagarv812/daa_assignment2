import sys

def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) - (B[1]-A[1]) * (C[0]-A[0])

def intersect(A, B, C, D):
    if ccw(A, B, C) == 0 and ccw(A, B, D) == 0:
        return False
    return (ccw(A, B, C) * ccw(A, B, D) < 0) and (ccw(C, D, A) * ccw(C, D, B) < 0)

with open('error_hard.txt', 'r') as f:
    lines = f.readlines()

current_case = -1
vertices = {}
edges = []

for line in lines:
    parts = line.split()
    if not parts: continue
    
    if parts[0] == "MERGE_DUMP_BEGIN":
        current_case = int(parts[1])
        vertices = {}
        edges = []
    elif parts[0] == "VERTEX":
        vid = int(parts[1])
        vertices[vid] = (float(parts[2]), float(parts[3]))
    elif parts[0] == "EDGE":
        orig = int(parts[2])
        dest = int(parts[3])
        edges.append((orig, dest))
    elif parts[0] == "MERGE_DUMP_END":
        if current_case == 3:
            for i in range(len(edges)):
                for j in range(i+1, len(edges)):
                    e1 = edges[i]
                    e2 = edges[j]
                    if e1[0] == e2[0] or e1[0] == e2[1] or e1[1] == e2[0] or e1[1] == e2[1]:
                        continue
                    A, B = vertices[e1[0]], vertices[e1[1]]
                    C, D = vertices[e2[0]], vertices[e2[1]]
                    if intersect(A, B, C, D):
                        print(f"Case 3 Intersection: E1({e1[0]}->{e1[1]}) {A}->{B}  AND  E2({e2[0]}->{e2[1]}) {C}->{D}")

