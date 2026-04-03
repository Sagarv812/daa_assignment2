#include <iostream>
#include <exception>

#include "guards.hpp"
#include "hole_merger.hpp"
#include "parser.hpp"
#include "polygon_utils.hpp"
#include "triangulation.hpp"

int main() {
    int testCaseCount;
    if (!(std::cin >> testCaseCount)) {
        std::cerr << "Input parse error: expected testcase count\n";
        return 1;
    }
    if (testCaseCount < 0) {
        std::cerr << "Input parse error: testcase count cannot be negative\n";
        return 1;
    }

    try {
        for (int caseIndex = 0; caseIndex < testCaseCount; ++caseIndex) {
            Face* gallery = parseSingleGallery();
            int totalVertices = static_cast<int>(getTotalVertexCount(gallery));
            int holeCount = static_cast<int>(gallery->InnerComponents.size());
            mergeHoles(gallery);

            TriangulationResult triangulation = triangulateGallery(gallery);
            GuardSolution guards = computeGuards(triangulation, totalVertices, holeCount);
            printTriangles(triangulation.triangles);
            printGuards(guards);
        }
    } catch (const std::exception& ex) {
        std::cerr << ex.what() << '\n';
        return 1;
    }

    return 0;
}
