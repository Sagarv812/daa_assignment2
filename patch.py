with open('src/hole_merger.cpp', 'r') as f:
    code = f.read()

# Replace isInsideSector
old_isInsideSector = """bool isInsideSector(double v1X, double v1Y, double v2X, double v2Y, double bX, double bY) {
    double cross12 = v1X * v2Y - v1Y * v2X;
    double cross1B = v1X * bY - v1Y * bX;
    double crossB2 = bX * v2Y - bY * v2X;

    if (cross12 > 0) {
        return cross1B > 0 && crossB2 > 0;
    } else {
        return cross1B > 0 || crossB2 > 0;
    }
}"""

new_isInsideSector = """bool isInsideSector(double v1X, double v1Y, double v2X, double v2Y, double bX, double bY) {
    double cross12 = v1X * v2Y - v1Y * v2X;
    double dot12   = v1X * v2X + v1Y * v2Y;
    double cross1B = v1X * bY - v1Y * bX;
    double crossB2 = bX * v2Y - bY * v2X;

    if (abs(cross12) < 1e-9) {
        if (dot12 < 0) {
            return cross1B > -1e-9;
        } else {
            return True;
        }
    }

    if (cross12 > 0) {
        return cross1B > -1e-9 && crossB2 > -1e-9;
    } else {
        return cross1B > -1e-9 || crossB2 > -1e-9;
    }
}""".replace("True", "true").replace("abs(", "std::abs(")

code = code.replace(old_isInsideSector, new_isInsideSector)

# Replace findValidSplicePoint candidate logic
import re
old_findValid = r"""    const double bridgeAngle = getBridgeAngle\(target, v\);.*?    HalfEdge\* best = nullptr;"""
new_findValid = """    std::vector<HalfEdge*> options;
    for (auto& pair : candidates) {
        options.push_back(pair.second);
    }
    HalfEdge* best = nullptr;"""

code = re.sub(old_findValid, new_findValid, code, flags=re.DOTALL)

with open('src/hole_merger.cpp', 'w') as f:
    f.write(code)
