#include "parser.hpp"

#include <algorithm>
#include <iostream>
#include <utility>
#include <vector>

namespace {

using Point = std::pair<double, double>;

double getSignedArea(const std::vector<Point>& coords) {
    double area = 0.0;
    int vertexCount = static_cast<int>(coords.size());

    for (int i = 0; i < vertexCount; ++i) {
        int next = (i + 1) % vertexCount;
        area += coords[i].first * coords[next].second - coords[next].first * coords[i].second;
    }

    return area / 2.0;
}

void normalizeOrientation(std::vector<Point>& coords, bool isOuter) {
    double signedArea = getSignedArea(coords);
    if ((isOuter && signedArea < 0.0) || (!isOuter && signedArea > 0.0)) {
        std::reverse(coords.begin(), coords.end());
    }
}

}  // namespace

void parsePolygonEdges(Face* gallery, bool isOuter) {
    int vertexCount;
    std::cin >> vertexCount;

    std::vector<Point> coords;
    coords.reserve(vertexCount);
    for (int i = 0; i < vertexCount; ++i) {
        double x, y;
        std::cin >> x >> y;
        coords.emplace_back(x, y);
    }

    normalizeOrientation(coords, isOuter);

    std::vector<HalfEdge*> polyEdges;
    polyEdges.reserve(vertexCount);
    for (const auto& [x, y] : coords) {
        Vertex* v = new Vertex{x, y, nullptr};
        HalfEdge* e = new HalfEdge{v, gallery, nullptr, nullptr, nullptr};
        v->originatingEdge = e;
        polyEdges.push_back(e);
    }

    for (int i = 0; i < vertexCount; ++i) {
        int next = (i + 1) % vertexCount;
        int prev = (i + vertexCount - 1) % vertexCount;
        polyEdges[i]->nextEdge = polyEdges[next];
        polyEdges[i]->prevEdge = polyEdges[prev];
    }

    if (isOuter) {
        gallery->boundaryEdge = polyEdges.front();
    } else {
        gallery->InnerComponents.push_back(polyEdges.front());
    }
}

Face* parseSingleGallery() {
    Face* gallery = new Face();
    parsePolygonEdges(gallery, true);

    int holeCount;
    std::cin >> holeCount;
    for (int i = 0; i < holeCount; ++i) {
        parsePolygonEdges(gallery, false);
    }

    return gallery;
}
