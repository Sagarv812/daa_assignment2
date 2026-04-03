import re

with open('src/hole_merger.cpp', 'r') as f:
    code = f.read()

old_code = r"""double getRayIntersectionX\(Vertex\* M, const HalfEdge\* E\){.*?return activeEdges\.end\(\);\n}"""

new_code = """static double g_current_sweep_y = 0.0;

double getRayIntersectionXExact(const HalfEdge* E) {
    Vertex* A = E->origin;
    Vertex* B = E->nextEdge->origin;
    if (A->y == B->y) return min(A->x, B->x);
    return A->x + (B->x - A->x) * (g_current_sweep_y - A->y) / (B->y - A->y);
}

double getInverseSlope(const HalfEdge* E) {
    Vertex* A = E->origin;
    Vertex* B = E->nextEdge->origin;
    if (A->y == B->y) return 0.0;
    return (B->x - A->x) / (B->y - A->y);
}

struct EdgeComparator {
    bool operator()(const HalfEdge* a, const HalfEdge* b) const {
        if(a == b) return false;
        
        double x_a = getRayIntersectionXExact(a);
        double x_b = getRayIntersectionXExact(b);
        
        if (std::abs(x_a - x_b) > 1e-9) {
            return x_a < x_b;
        }
        
        double m_a = getInverseSlope(a);
        double m_b = getInverseSlope(b);
        if (std::abs(m_a - m_b) > 1e-9) {
            return m_a > m_b;
        }
        
        return a < b;
    }
};

auto findClosestWallToLeft(Vertex* M, std::map<HalfEdge*,Vertex*, EdgeComparator>& activeEdges){
    Vertex vTop = {M->x, M->y, nullptr};
    Vertex vBot = {M->x, M->y - 1.0, nullptr};
    HalfEdge dummyEdge = {&vTop, nullptr, nullptr, nullptr, nullptr};
    HalfEdge dummyBot = {&vBot, nullptr, nullptr, nullptr, nullptr};
    dummyEdge.nextEdge = &dummyBot;

    auto it = activeEdges.lower_bound(&dummyEdge);

    if (it != activeEdges.begin()) {
        --it;
        return it;
    }   
    return activeEdges.end();
}"""

# Using re.DOTALL to match across newlines
new_src = re.sub(old_code, new_code, code, flags=re.DOTALL)
if new_src == code:
    print("REPLACE FAILED!")
else:
    print("REPLACE SUCCESS!")
    with open('src/hole_merger.cpp', 'w') as f:
        f.write(new_src)

