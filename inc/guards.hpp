#pragma once

#include <vector>

#include "dcel.hpp"
#include "triangulation.hpp"

struct GuardSolution {
    int theoreticalBound;
    std::vector<Vertex*> guards;
};

GuardSolution computeGuards(const TriangulationResult& triangulation, int totalVertices, int holeCount);
void printGuards(const GuardSolution& solution);
