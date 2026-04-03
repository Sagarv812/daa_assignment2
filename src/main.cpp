#include <iostream>

#include "guards.hpp"
#include "hole_merger.hpp"
#include "parser.hpp"
#include "polygon_utils.hpp"
#include "triangulation.hpp"

int main() {
    int T;
    std::cin >> T;

    while (T--) {
        Face* gallery = parseSingleGallery();
        const int totalVertices = static_cast<int>(getTotalVertexCount(gallery));
        const int holeCount = static_cast<int>(gallery->InnerComponents.size());
        mergeHoles(gallery);

        const TriangulationResult triangulation = triangulateGallery(gallery);
        const GuardSolution guards = computeGuards(triangulation, totalVertices, holeCount);
        printTriangles(triangulation.triangles);
        printGuards(guards);
    }

    return 0;
}
