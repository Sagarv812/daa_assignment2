#include "hole_merger.hpp"

#include <algorithm>
#include <cfloat>
#include <map>

#include "polygon_utils.hpp"
namespace {

double getRayIntersectionX(const Vertex* M,const HalfEdge* E){
    Vertex* A = E->origin;
    Vertex* B = E->nextEdge->origin;

    // Ray and edge are parallel then return false;
    // even if ray coincides with with edge it
    // will intersect with another edge so it works and we can safely return false
    if(A->y == B->y){
        return DBL_MAX;
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
        Vertex rayV{-DBL_MAX, yRay, NULL};
        double int_a = getRayIntersectionX(&rayV, a);
        double int_b = getRayIntersectionX(&rayV, b);
        if(int_a == int_b){
            //might be that it's a vertex from which 2 edges are originating so just take a small distance above
            double maxaY = std::max(a->origin->y, a->nextEdge->origin->y);
            double maxbY = std::max(b->origin->y, b->nextEdge->origin->y);
            double yRay2 = std::min(maxaY, maxbY);
            rayV.y =  (yRay2+yRay)/2;

            int_a = getRayIntersectionX(&rayV, a);
            int_b = getRayIntersectionX(&rayV, b);
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

using ActiveEdges = std::map<HalfEdge*, Vertex*, EdgeComparator>;
using ActiveEdgeIterator = ActiveEdges::iterator;

ActiveEdgeIterator findClosestWallToLeft(Vertex* M, ActiveEdges& activeEdges){
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

void buildBridge(Vertex* M, Vertex* Target, Face* gallery){
    // We want to bridge M and Target

    // Bridging outgoing and incoming edges of M
    HalfEdge* e_M_out = M->originatingEdge;
    HalfEdge* e_M_in = M->originatingEdge->prevEdge;

    // Bridging outgoing and incoming edges of T
    HalfEdge* e_T_out = Target->originatingEdge;
    HalfEdge* e_T_in = Target->originatingEdge->prevEdge;

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
}

}  // namespace

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

    // Making Active Edges
    ActiveEdges activeEdges;

    int nextHoleIdx = 0;

    // Going through all the vertices one by one
    for(Vertex* collidingVertex : sweepVertices){

        if(nextHoleIdx < (int)topmostVertices.size() && collidingVertex == topmostVertices[nextHoleIdx]){
            auto leftWall_it = findClosestWallToLeft(collidingVertex, activeEdges);

            if(leftWall_it != activeEdges.end()){
                Vertex* Target = leftWall_it->second;
                buildBridge(collidingVertex, Target, gallery);
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
