#include "hole_merger.hpp"
#include "polygon_utils.hpp"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cfloat>
#include <limits>
#include <map>
#include <unordered_map>
#include <vector>

double getRayIntersectionX(const Vertex* M, const HalfEdge* E) {
    const Vertex* A = E->origin;
    const Vertex* B = E->nextEdge->origin;

    // Horizontal edges do not contribute to the left-ray intersection.
    if (A->y == B->y) {
        return DBL_MAX;
    }

    double minY = std::min(A->y, B->y);
    double maxY = std::max(A->y, B->y);
    if (M->y < minY || M->y >= maxY) {
        return DBL_MAX;
    }

    double x_int = A->x + (B->x - A->x) * (M->y - A->y) / (B->y - A->y);
    if (x_int < M->x) {
        return DBL_MAX;
    }

    return x_int;
}

struct EdgeComparator {
    bool operator()(const HalfEdge* a, const HalfEdge* b) const {
        if (a == b) {
            return false;
        }

        double minaY = std::min(a->origin->y, a->nextEdge->origin->y);
        double minbY = std::min(b->origin->y, b->nextEdge->origin->y);
        double yRay = std::max(minaY, minbY);

        Vertex rayVObj{-DBL_MAX, yRay, nullptr};
        Vertex* rayV = &rayVObj;
        double int_a = getRayIntersectionX(rayV, a);
        double int_b = getRayIntersectionX(rayV, b);

        if (int_a == int_b) {
            double maxaY = std::max(a->origin->y, a->nextEdge->origin->y);
            double maxbY = std::max(b->origin->y, b->nextEdge->origin->y);
            double yRay2 = std::min(maxaY, maxbY);
            rayV->y = (yRay2 + yRay) / 2;

            int_a = getRayIntersectionX(rayV, a);
            int_b = getRayIntersectionX(rayV, b);
        }

        if (int_a == int_b) {
            return a < b;
        }
        return int_a < int_b;
    }
};

struct HelperState {
    Vertex* helper;
    double lockedAtY;
    int lockedComponentId;
    bool lockSameLevel;
    Vertex* minLockedHelper;
    Vertex* maxLockedHelper;
};

using ActiveEdges = std::map<HalfEdge*, HelperState, EdgeComparator>;

auto findClosestWallToLeft(Vertex* M, ActiveEdges& activeEdges) {
    Vertex vTop = {M->x, M->y - 1.0, nullptr};
    Vertex vBot = {M->x, M->y + 1.0, nullptr};
    HalfEdge eBot = {&vBot, nullptr, nullptr, nullptr, nullptr};
    HalfEdge dummyEdge = {&vTop, nullptr, &eBot, nullptr, nullptr};

    auto it = activeEdges.upper_bound(&dummyEdge);
    if (it == activeEdges.begin()) {
        return activeEdges.end();
    }

    --it;
    return it;
}

bool isInsideSector(double v1X, double v1Y, double v2X, double v2Y, double bX, double bY);

namespace {

constexpr double kTwoPi = 6.28318530717958647692;
constexpr double kHelperLockEps = 1e-9;

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

void addCycleVerticesToComponentMap(HalfEdge* startEdge, int componentId,
                                    std::unordered_map<Vertex*, int>& vertexComponentIds) {
    if (startEdge == nullptr) {
        return;
    }

    HalfEdge* currEdge = startEdge;
    do {
        vertexComponentIds[currEdge->origin] = componentId;
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

HelperState makeUnlockedHelper(Vertex* helper) {
    return {helper, helper != nullptr ? helper->y : 0.0, -1, false, helper, helper};
}

void setUnlockedHelper(HelperState& state, Vertex* helper) {
    state = makeUnlockedHelper(helper);
}

void setHoleTopHelper(HelperState& state, Vertex* helper, int componentId) {
    state = {helper, helper != nullptr ? helper->y : 0.0, componentId, true, helper, helper};
}

bool canOverwriteWithOrdinary(const HelperState& state, Vertex* candidate, int candidateComponentId) {
    if (!state.lockSameLevel) {
        return true;
    }
    if (candidate->y < state.lockedAtY - kHelperLockEps) {
        return true;
    }
    return std::abs(candidate->y - state.lockedAtY) <= kHelperLockEps &&
           candidateComponentId == state.lockedComponentId;
}

void applyOrdinaryHelperUpdate(HelperState& state, Vertex* candidate, int candidateComponentId) {
    if (!state.lockSameLevel || candidate->y < state.lockedAtY - kHelperLockEps) {
        setUnlockedHelper(state, candidate);
        return;
    }

    state.helper = candidate;
    state.lockedComponentId = candidateComponentId;
    if (state.minLockedHelper == nullptr || candidate->x < state.minLockedHelper->x) {
        state.minLockedHelper = candidate;
    }
    if (state.maxLockedHelper == nullptr || candidate->x > state.maxLockedHelper->x) {
        state.maxLockedHelper = candidate;
    }
}

Vertex* getBridgeTarget(const HelperState& state, Vertex* queryVertex) {
    if (!state.lockSameLevel || state.minLockedHelper == nullptr || state.maxLockedHelper == nullptr) {
        return state.helper;
    }

    double distToMin = std::abs(queryVertex->x - state.minLockedHelper->x);
    double distToMax = std::abs(queryVertex->x - state.maxLockedHelper->x);
    if (distToMin <= distToMax) {
        return state.minLockedHelper;
    }
    return state.maxLockedHelper;
}

void updateActiveEdge(HalfEdge* edge,
                      double otherEndpointY,
                      Vertex* helperVertex,
                      ActiveEdges& activeEdges) {
    if (otherEndpointY > helperVertex->y) {
        activeEdges.erase(edge);
    } else if (otherEndpointY < helperVertex->y) {
        activeEdges[edge] = makeUnlockedHelper(helperVertex);
    }
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

void buildBridge(Vertex* M, Vertex* target, Face* gallery, VertexOutgoingIndex& outgoingIndex) {
    HalfEdge* e_M_out = M->originatingEdge;
    HalfEdge* e_M_in = M->originatingEdge->prevEdge;

    HalfEdge* e_T_out = findValidSplicePoint(target, M, outgoingIndex);
    if (!e_T_out) {
        e_T_out = target->originatingEdge;
    }
    HalfEdge* e_T_in = e_T_out->prevEdge;

    HalfEdge* bridge = new HalfEdge{M, gallery, nullptr, nullptr, nullptr};
    HalfEdge* bridgeTwin = new HalfEdge{target, gallery, nullptr, nullptr, nullptr};
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
    target->originatingEdge = bridgeTwin;

    addOutgoingEdgeToIndex(bridge, outgoingIndex);
    addOutgoingEdgeToIndex(bridgeTwin, outgoingIndex);
}

void mergeHoles(Face* gallery) {
    std::vector<Vertex*> topmostVertices = getTopmostVertices(gallery);
    auto compY = [](Vertex* a, Vertex* b) {
        if (a->y != b->y) {
            return a->y > b->y;
        }
        return a->x < b->x;
    };

    std::vector<Vertex*> sweepVertices = getVerticesSorted(gallery, compY);
    VertexOutgoingIndex outgoingIndex;
    addCycleToOutgoingIndex(gallery->boundaryEdge, outgoingIndex);
    for (HalfEdge* holeEdgeStart : gallery->InnerComponents) {
        addCycleToOutgoingIndex(holeEdgeStart, outgoingIndex);
    }
    std::unordered_map<Vertex*, int> vertexComponentIds;
    addCycleVerticesToComponentMap(gallery->boundaryEdge, 0, vertexComponentIds);
    for (int i = 0; i < static_cast<int>(gallery->InnerComponents.size()); ++i) {
        addCycleVerticesToComponentMap(gallery->InnerComponents[i], i + 1, vertexComponentIds);
    }

    ActiveEdges activeEdges;
    int nextHoleIdx = 0;

    for (Vertex* collidingVertex : sweepVertices) {
        auto preLeftWall_it = findClosestWallToLeft(collidingVertex, activeEdges);
        HalfEdge* preLeftWall = (preLeftWall_it != activeEdges.end()) ? preLeftWall_it->first : nullptr;
        bool didProcessHoleTop = false;

        if (nextHoleIdx < static_cast<int>(topmostVertices.size()) &&
            collidingVertex == topmostVertices[nextHoleIdx]) {
            if (preLeftWall_it != activeEdges.end()) {
                Vertex* target = getBridgeTarget(preLeftWall_it->second, collidingVertex);
                buildBridge(collidingVertex, target, gallery, outgoingIndex);
            }

            didProcessHoleTop = true;
            ++nextHoleIdx;
        }

        HalfEdge* incomingEdge = collidingVertex->originatingEdge->prevEdge;
        HalfEdge* outgoingEdge = collidingVertex->originatingEdge;

        updateActiveEdge(incomingEdge, incomingEdge->origin->y, collidingVertex, activeEdges);
        updateActiveEdge(outgoingEdge, outgoingEdge->nextEdge->origin->y, collidingVertex, activeEdges);

        auto leftWall_it = findClosestWallToLeft(collidingVertex, activeEdges);
        if (leftWall_it != activeEdges.end()) {
            if (didProcessHoleTop) {
                setHoleTopHelper(leftWall_it->second, collidingVertex, vertexComponentIds[collidingVertex]);
            } else if (canOverwriteWithOrdinary(leftWall_it->second,
                                                collidingVertex,
                                                vertexComponentIds[collidingVertex])) {
                applyOrdinaryHelperUpdate(leftWall_it->second, collidingVertex,
                                          vertexComponentIds[collidingVertex]);
            }
        }

        if (didProcessHoleTop && preLeftWall != nullptr) {
            auto preservedLeftWall_it = activeEdges.find(preLeftWall);
            if (preservedLeftWall_it != activeEdges.end()) {
                setHoleTopHelper(preservedLeftWall_it->second, collidingVertex,
                                 vertexComponentIds[collidingVertex]);
            }
        }
    }
}
