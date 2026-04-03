#include "hole_merger.hpp"
#include "polygon_utils.hpp"
#include <map>
#include <vector>
#include <algorithm>
#include <cfloat>
#include <cmath>
#include <cstdint>
#include <limits>
#include <unordered_map>

double getRayIntersectionX(const Vertex* M,const HalfEdge* E){
    Vertex* A = E->origin;
    Vertex* B = E->nextEdge->origin;

    // Ray and edge are parallel then return false;
    // even if ray coincides with with edge it 
    // will intersect with another edge so it works and we can safely return false 
    if(A->y == B->y){
        return std::min(A->x, B->x);
    }

    double minY = std::min(A->y, B->y);
    double maxY = std::max(A->y, B->y);
    // Checking bounds of edges and ray
    if(M->y < minY || M->y >= maxY){
        return DBL_MAX;
    }

    // doing the maths
    double x_int = A->x + (B->x - A->x) * (M->y - A->y) / (B->y - A->y);
    
    // X-direction Check
    if(x_int < M->x){
        return DBL_MAX;
    }

    return x_int;
}
struct EdgeComparator {
    bool operator()(const HalfEdge* a, const HalfEdge* b) const {
        if(a == b){
            return false;
        }
        // Lower vertices of both edges a and b
        double minaY = std::min(a->origin->y, a->nextEdge->origin->y);
        double minbY = std::min(b->origin->y, b->nextEdge->origin->y);

        // Now (given that both edges have common y assumption)
        double yRay = std::max(minaY, minbY);
        // fake vertex so we can use our function comfortably
        Vertex rayVObj{-DBL_MAX, yRay, nullptr}; Vertex* rayV = &rayVObj;
        double int_a = getRayIntersectionX(rayV, a);
        double int_b = getRayIntersectionX(rayV, b);
        if(int_a == int_b){
            //might be that it's a vertex from which 2 edges are originating so just take a small distance above
            double maxaY = std::max(a->origin->y, a->nextEdge->origin->y);
            double maxbY = std::max(b->origin->y, b->nextEdge->origin->y);
            double yRay2 = std::min(maxaY, maxbY);
            rayV->y =  (yRay2+yRay)/2;
            
            int_a = getRayIntersectionX(rayV, a);
            int_b = getRayIntersectionX(rayV, b);
        }
        
        if(int_a == int_b) return a<b; // To prevent something called silent deletion by sets
        if(int_a < int_b){
            return true;
        }else{
            return false;
        }
        // Assuming Edges can't be equal cuz of polygon
        // Also assuming we won't compare 2 edges with no common y value 
        
    }
};

auto findClosestWallToLeft(Vertex* M, std::map<HalfEdge*,Vertex*, EdgeComparator>& activeEdges){
    
    // Making the dummyEdge for doing Binary Search
    Vertex vTop = {M->x, M->y - 1.0, nullptr};
    Vertex vBot = {M->x, M->y + 1.0, nullptr};
    HalfEdge eBot = {&vBot, nullptr, nullptr, nullptr, nullptr};
    HalfEdge dummyEdge = {&vTop, nullptr, &eBot, nullptr, nullptr};

    // Binary Search (log n)
    auto it = activeEdges.upper_bound(&dummyEdge);

    // Validate and Return 
    if(it != activeEdges.begin()){
        it--;
        return it;
    }   
    // Could not find right wall :( 
    return activeEdges.end();
}

bool isInsideSector(double v1X, double v1Y, double v2X, double v2Y, double bX, double bY);

namespace {

constexpr double kTwoPi = 6.28318530717958647692;

double getVectorAngle(double dx, double dy) {
    double angle = std::atan2(dy, dx);
    if (angle < 0.0) {
        angle += kTwoPi;
    }
    return angle;
}

double getOutgoingAngle(const HalfEdge* edge) {
    Vertex* origin = edge->origin;
    Vertex* next = edge->nextEdge->origin;
    return getVectorAngle(next->x - origin->x, next->y - origin->y);
}

double getBridgeAngle(const Vertex* from, const Vertex* to) {
    return getVectorAngle(to->x - from->x, to->y - from->y);
}

struct OutgoingKey {
    double angle;
    std::uintptr_t edgeId;
};

struct OutgoingKeyComparator {
    bool operator()(const OutgoingKey& lhs, const OutgoingKey& rhs) const {
        if (lhs.angle != rhs.angle) {
            return lhs.angle < rhs.angle;
        }
        return lhs.edgeId < rhs.edgeId;
    }
};

using OutgoingAngleIndex = std::map<OutgoingKey, HalfEdge*, OutgoingKeyComparator>;
using VertexOutgoingIndex = std::unordered_map<Vertex*, OutgoingAngleIndex>;

OutgoingKey makeOutgoingKey(const HalfEdge* edge) {
    return {getOutgoingAngle(edge), reinterpret_cast<std::uintptr_t>(edge)};
}

void addCycleToOutgoingIndex(HalfEdge* startEdge, VertexOutgoingIndex& outgoingIndex) {
    if (startEdge == nullptr) {
        return;
    }

    HalfEdge* currEdge = startEdge;
    do {
        outgoingIndex[currEdge->origin].emplace(makeOutgoingKey(currEdge), currEdge);
        currEdge = currEdge->nextEdge;
    } while (currEdge != startEdge && currEdge != nullptr);
}

void addOutgoingEdgeToIndex(HalfEdge* edge, VertexOutgoingIndex& outgoingIndex) {
    outgoingIndex[edge->origin].emplace(makeOutgoingKey(edge), edge);
}

bool bridgeFitsSector(HalfEdge* e_out, Vertex* v) {
    HalfEdge* e_in = e_out->prevEdge;

    double bX = v->x - e_out->origin->x;
    double bY = v->y - e_out->origin->y;
    double inX = e_in->origin->x - e_out->origin->x;
    double inY = e_in->origin->y - e_out->origin->y;
    double outX = e_out->nextEdge->origin->x - e_out->origin->x;
    double outY = e_out->nextEdge->origin->y - e_out->origin->y;

    return isInsideSector(outX, outY, inX, inY, bX, bY);
}
}  // namespace

bool isInsideSector(double v1X, double v1Y, double v2X, double v2Y, double bX, double bY) {
    double cross12 = v1X * v2Y - v1Y * v2X;
    double cross1B = v1X * bY - v1Y * bX;
    double crossB2 = bX * v2Y - bY * v2X;

    if (cross12 > 1e-9) {
        return cross1B >= -1e-9 && crossB2 >= -1e-9;
    } else {
        return cross1B >= -1e-9 || crossB2 >= -1e-9; 
    }
}

HalfEdge* findValidSplicePoint(Vertex* target, Vertex* v, VertexOutgoingIndex& outgoingIndex) {
    auto targetIt = outgoingIndex.find(target);
    if (targetIt == outgoingIndex.end() || targetIt->second.empty()) {
        return nullptr;
    }

    OutgoingAngleIndex& candidates = targetIt->second;
    if (candidates.size() == 1) {
        return candidates.begin()->second;
    }

    OutgoingKey probe{getBridgeAngle(target, v), std::numeric_limits<std::uintptr_t>::max()};
    auto upper = candidates.upper_bound(probe);
    auto candidateIt = (upper == candidates.begin()) ? std::prev(candidates.end()) : std::prev(upper);

    if (bridgeFitsSector(candidateIt->second, v)) {
        return candidateIt->second;
    }

    if (upper != candidates.end() && bridgeFitsSector(upper->second, v)) {
        return upper->second;
    }

    if (upper == candidates.end() && bridgeFitsSector(candidates.begin()->second, v)) {
        return candidates.begin()->second;
    }

    return candidateIt->second;
}

void buildBridge(Vertex* M, Vertex* Target, Face* gallery, VertexOutgoingIndex& outgoingIndex){
    // Bridging outgoing and incoming edges of M
    HalfEdge* e_M_out = M->originatingEdge;
    HalfEdge* e_M_in = M->originatingEdge->prevEdge;

    // Bridging outgoing and incoming edges of T
    HalfEdge* e_T_out = findValidSplicePoint(Target, M, outgoingIndex);
    if (!e_T_out) e_T_out = Target->originatingEdge;
    HalfEdge* e_T_in = e_T_out->prevEdge;

    HalfEdge* bridge = new HalfEdge{M, gallery, nullptr, nullptr, nullptr};
    HalfEdge* bridgeTwin = new HalfEdge{Target, gallery,nullptr, nullptr, nullptr};
    bridge->twin = bridgeTwin;
    bridgeTwin->twin = bridge;

    e_M_in->nextEdge = bridge;
    bridge->prevEdge = e_M_in;

    bridge->nextEdge = e_T_out;
    e_T_out->prevEdge = bridge;

    e_T_in->nextEdge = bridgeTwin;
    bridgeTwin->prevEdge = e_T_in;

    bridgeTwin->nextEdge = e_M_out;
    e_M_out->prevEdge = bridgeTwin;

    M->originatingEdge = bridge;
    Target->originatingEdge = bridgeTwin;

    addOutgoingEdgeToIndex(bridge, outgoingIndex);
    addOutgoingEdgeToIndex(bridgeTwin, outgoingIndex);
}
void mergeHoles(Face* gallery){
    // Getting holes by storing the topMostVertices of those holes  
    std::vector<Vertex*> topmostVertices = getTopmostVertices(gallery);
    auto compY = [](Vertex* a, Vertex* b){
        if(a->y != b->y){
            return a->y > b->y;
        }else{
            return a->x < b->x;
        }
    };
    // Vertices stored from top to bottom 
    std::vector<Vertex*> sweepVertices = getVerticesSorted(gallery, compY);
    VertexOutgoingIndex outgoingIndex;
    addCycleToOutgoingIndex(gallery->boundaryEdge, outgoingIndex);
    for (HalfEdge* holeEdgeStart : gallery->InnerComponents) {
        addCycleToOutgoingIndex(holeEdgeStart, outgoingIndex);
    }

    // Making Active Edges
    std::map<HalfEdge*,Vertex* ,EdgeComparator> activeEdges;

    int nextHoleIdx = 0;

    // Going through all the vertices one by one 
    for(Vertex* collidingVertex : sweepVertices){
        if(nextHoleIdx < (int)topmostVertices.size() && collidingVertex == topmostVertices[nextHoleIdx]){
            auto leftWall_it = findClosestWallToLeft(collidingVertex, activeEdges);

            if(leftWall_it != activeEdges.end()){
                Vertex* Target = leftWall_it->second;
                buildBridge(collidingVertex, Target, gallery, outgoingIndex);
            }

            nextHoleIdx++;
        }

        HalfEdge* incomingEdge = collidingVertex->originatingEdge->prevEdge;
        HalfEdge* outgoingEdge = collidingVertex->originatingEdge;

        if(incomingEdge->origin->y > collidingVertex->y) activeEdges.erase(incomingEdge);
        else activeEdges[incomingEdge] = collidingVertex;

        if(outgoingEdge->nextEdge->origin->y > collidingVertex->y) activeEdges.erase(outgoingEdge);
        else activeEdges[outgoingEdge] = collidingVertex;

        auto leftWall_it = findClosestWallToLeft(collidingVertex, activeEdges);
        if(leftWall_it != activeEdges.end()){
            leftWall_it->second = collidingVertex;
        }
        
    }
}
