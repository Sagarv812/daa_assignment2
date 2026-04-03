with open('src/hole_merger.cpp', 'r') as f:
    code = f.read()

import re

# Replace bridgeFitsSector and isInsideSector completely
old_sect = r"""bool isInsideSector\(double v1X.*?}

bool bridgeFitsSector\(HalfEdge\* e_out, Vertex\* v\) {.*?return isInsideSector\(outX, outY, inX, inY, bX, bY\);
}"""

new_sect = """bool isInsideSector(double outAngle, double inAngle, double bridgeAngle) {
    if (outAngle < inAngle) {
        return bridgeAngle >= outAngle - 1e-9 && bridgeAngle <= inAngle + 1e-9;
    } else {
        return bridgeAngle >= outAngle - 1e-9 || bridgeAngle <= inAngle + 1e-9;
    }
}

bool bridgeFitsSector(HalfEdge* e_out, Vertex* v) {
    double outAngle = getOutgoingAngle(e_out);
    double inAngle = getIncomingAngle(e_out);
    double bridgeAngle = getBridgeAngle(e_out->origin, v);
    return isInsideSector(outAngle, inAngle, bridgeAngle);
}"""

code = re.sub(old_sect, new_sect, code, flags=re.DOTALL)

old_findValid = r"""    for \(HalfEdge\* edge : options\) {
        if \(!bridgeFitsSector\(edge, v\)\) {
            continue;
        }

        const double currentSweep = sectorSweep\(edge\);
        const double currentProgress = bridgeProgress\(edge, v\);
        if \(best == nullptr \|\| currentSweep < bestSweep \|\|
            \(currentSweep == bestSweep && currentProgress < bestProgress\)\) {
            best = edge;
            bestSweep = currentSweep;
            bestProgress = currentProgress;
        }
    }"""

new_findValid = """    for (HalfEdge* edge : options) {
        if (!bridgeFitsSector(edge, v)) continue;
        const double edgeAngle = getOutgoingAngle(edge);
        double diff = bridgeAngle - edgeAngle;
        if (diff < 0) diff += 6.28318530717958647692;
        if (best == nullptr || diff < bestProgress) {
            best = edge;
            bestProgress = diff;
        }
    }"""

code = re.sub(old_findValid, new_findValid, code, flags=re.DOTALL)

with open('src/hole_merger.cpp', 'w') as f:
    f.write(code)
