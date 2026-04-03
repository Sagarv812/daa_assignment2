#include "parser.hpp"

#include <algorithm>
#include <cmath>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

using Point = std::pair<double, double>;

[[noreturn]] void throwParseError(const std::string& message) {
    throw std::runtime_error("Input parse error: " + message);
}

int readIntOrThrow(const std::string& what) {
    int value;
    if (!(std::cin >> value)) {
        throwParseError("expected " + what);
    }
    return value;
}

double readDoubleOrThrow(const std::string& what) {
    double value;
    if (!(std::cin >> value)) {
        throwParseError("expected " + what);
    }
    if (!std::isfinite(value)) {
        throwParseError(what + " must be finite");
    }
    return value;
}

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

void validatePolygonCoords(const std::vector<Point>& coords, bool isOuter) {
    const char* polygonType = isOuter ? "outer polygon" : "hole";
    if (coords.size() < 3) {
        throwParseError(std::string(polygonType) + " must have at least 3 vertices");
    }

    for (std::size_t i = 0; i < coords.size(); ++i) {
        std::size_t next = (i + 1) % coords.size();
        if (coords[i] == coords[next]) {
            throwParseError(std::string(polygonType) + " contains duplicate consecutive vertices");
        }
    }

    if (std::abs(getSignedArea(coords)) <= 1e-12) {
        throwParseError(std::string(polygonType) + " has zero area");
    }
}

}  // namespace

void parsePolygonEdges(Face* gallery, bool isOuter) {
    int vertexCount = readIntOrThrow(isOuter ? "outer polygon vertex count" : "hole vertex count");
    if (vertexCount < 0) {
        throwParseError("vertex count cannot be negative");
    }

    std::vector<Point> coords;
    coords.reserve(vertexCount);
    for (int i = 0; i < vertexCount; ++i) {
        double x = readDoubleOrThrow("x coordinate");
        double y = readDoubleOrThrow("y coordinate");
        coords.emplace_back(x, y);
    }

    validatePolygonCoords(coords, isOuter);
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
    std::unique_ptr<Face> gallery = std::make_unique<Face>();
    parsePolygonEdges(gallery.get(), true);

    int holeCount = readIntOrThrow("hole count");
    if (holeCount < 0) {
        throwParseError("hole count cannot be negative");
    }
    for (int i = 0; i < holeCount; ++i) {
        parsePolygonEdges(gallery.get(), false);
    }

    return gallery.release();
}
