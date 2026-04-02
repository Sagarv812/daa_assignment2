#pragma once

#include <array>
#include <vector>

#include "dcel.hpp"

enum class VertexType {
    START,
    END,
    SPLIT,
    MERGE,
    REGULAR_LEFT,
    REGULAR_RIGHT,
};

using Triangle = std::array<Vertex*, 3>;
using TriangleIndices = std::array<int, 3>;

struct TriangulationResult {
    std::vector<Triangle> triangles;
    std::vector<TriangleIndices> triangleIndices;
    std::vector<Vertex*> occurrenceVertices;
};

TriangulationResult triangulateGallery(Face* gallery);
void printTriangles(const std::vector<Triangle>& triangles);
