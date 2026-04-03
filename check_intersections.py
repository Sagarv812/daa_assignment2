import sys

def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) - (B[1]-A[1]) * (C[0]-A[0])

def intersect(A, B, C, D):
    if ccw(A, B, C) == 0 and ccw(A, B, D) == 0:
        # Collinear
        return False
    return (ccw(A, B, C) * ccw(A, B, D) < 0) and (ccw(C, D, A) * ccw(C, D, B) < 0)

with open('error_hard.txt', 'r') as f:
    lines = f.readlines()

current_case = -1
vertices = {}
edges = []
errors = 0

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
        # EDGE id orig dest ...
        orig = int(parts[2])
        dest = int(parts[3])
        edges.append((orig, dest))
    elif parts[0] == "MERGE_DUMP_END":
        # Check intersections
        intersect_count = 0
        for i in range(len(edges)):
            for j in range(i+1, len(edges)):
                e1 = edges[i]
                e2 = edges[j]
                # If they share a vertex, ignore
                if e1[0] == e2[0] or e1[0] == e2[1] or e1[1] == e2[0] or e1[1] == e2[1]:
                    continue
                A, B = vertices[e1[0]], vertices[e1[1]]
                C, D = vertices[e2[0]], vertices[e2[1]]
                if intersect(A, B, C, D):
                    intersect_count += 1
        print(f"Case {current_case}: {intersect_count} crossing edges")
        errors += intersect_count

print(f"Total crossing edges: {errors}")
