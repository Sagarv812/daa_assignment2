#pragma once

#include <array>
#include <iosfwd>
#include <vector>

#include "dcel.hpp"

enum class VertexCategory {
    START,
    END,
    SPLIT,
    MERGE,
    REGULAR_LEFT,
    REGULAR_RIGHT,
};

using Triangle = std::array<Vertex*, 3>;

std::vector<Triangle> triangulateGallery(Face* gallery);
void printTriangles(const std::vector<Triangle>& triangles, std::ostream& out);
