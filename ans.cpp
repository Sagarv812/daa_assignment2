#include<assert.h> 
#include<cfloat>
#include<iostream>
#include<vector>
#include<map>
#include<set>
#include<unordered_set>
#include<algorithm>
#include<utility>

struct HalfEdge;

struct Vertex{
    double x, y;
    HalfEdge* originatingEdge;
}; // Store just one edge counter clockwise one for Outer Polygon and Clockwise Edge for hole 

struct Face{
    HalfEdge* boundaryEdge;
    //Choose a random edge of the outer boundary (which we can traverse to get polygon)
    std::vector<HalfEdge*> InnerComponents;
    // Similarly store all the inner holes as well
};


struct HalfEdge{
    Vertex* origin;// We consider directed edge
    Face* boundaryFace;// Inner Face
    HalfEdge* nextEdge;// Next edge in polygon
    HalfEdge* prevEdge;// Prev edge in polygon
    HalfEdge* twin; // Same Vertices Opposite direction we will be using for Bridges 
};

static double getSignedArea(const std::vector<std::pair<double, double>>& coords){
    double area = 0.0;
    int n = static_cast<int>(coords.size());

    for(int i = 0; i < n; i++){
        int next = (i+1)%n;
        area += coords[i].first * coords[next].second - coords[next].first * coords[i].second;
    }

    return area/2.0;
}

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
        Vertex* rayV = new Vertex{-DBL_MAX, yRay, NULL};
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
        delete rayV;
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

void parsePolygonEdges(Face* gallery, bool isOuter){
    int v0;
    std::cin >> v0;
    
    std::vector<std::pair<double, double>> coords;
    for(int i = 0; i < v0; i++){
        double x, y;
        std::cin >> x >> y;
        coords.push_back({x, y});
    }

    std::vector<HalfEdge*> polyEdges;
    // Adding all the vertices and corresponding originating Half edges
    // Assuming Counter clockwise input for the Outer Polygon
    // And assuming Clockwise input for inner holes
    // (The gallery will be same as the direction of input is being adjusted)
    double signedArea = getSignedArea(coords);
    if(isOuter && signedArea < 0){
        std::reverse(coords.begin(), coords.end());
    }else if(!isOuter && signedArea > 0){
        std::reverse(coords.begin(), coords.end());
    }

    for(int i = 0; i < v0; i++){
        double x = coords[i].first;
        double y = coords[i].second;

        Vertex* v = new Vertex{x, y, nullptr};
        HalfEdge* e = new HalfEdge{v, gallery, nullptr, nullptr, nullptr};
        
        v->originatingEdge = e;

        polyEdges.push_back(e);
    }

    for(int i = 0 ; i < v0; i++){
        int next = (i+1)%v0;
        int prev = (i+v0-1)%v0;
        // Setting next and previous edges accordingly
        polyEdges[i]->nextEdge = polyEdges[next];
        polyEdges[i]->prevEdge = polyEdges[prev];
        // We are not going to be using the twin edge in this scenario 
    }

    // Adding them to the gallery according to if they are outer / hole edges
    if(isOuter)
        gallery->boundaryEdge = polyEdges[0];
    else
        gallery->InnerComponents.push_back(polyEdges[0]);
}

Face* parseSingleGallery(){
    Face* gallery = new Face();

    parsePolygonEdges(gallery, true);

    // Parsing the inner holes 
    int h;
    std::cin >> h;

    // Assuming clockwise vertex input for the inner holes 
    for(int i = 0; i < h; i++){
        parsePolygonEdges(gallery, false);
    }
    return gallery;
}

void addVertices(HalfEdge* startEdge, std::vector<Vertex*> &vertices){
        HalfEdge* currEdge = startEdge;
        // pushing first edge's origin
        vertices.push_back(currEdge->origin);
        currEdge = currEdge->nextEdge;


        // Adding all other edges cyclically
        while(currEdge != startEdge && currEdge != nullptr){
            vertices.push_back(currEdge->origin);
            currEdge = currEdge->nextEdge;
        }
        //Safety check that it's a polygon
        assert(currEdge != nullptr);
}

std::vector<Vertex*> getMergedPolygonVertices(Face* gallery){
    std::vector<Vertex*> mergedPolygonVertices;
    // Safety check to make sure gallery has edges
    if(gallery->boundaryEdge != nullptr){
        // Adding the final merged polygon vertices
        HalfEdge* startEdge = gallery->boundaryEdge;
        addVertices(startEdge, mergedPolygonVertices);
    }

    return mergedPolygonVertices;
}

template <typename CompareFunc>
std::vector<Vertex*> getVerticesSorted(Face* gallery, CompareFunc comp) {
    std::vector<Vertex*> allVertices;
    // Safety check to make sure gallery has edges
    if(gallery->boundaryEdge != nullptr){
        // Adding outer vertices
        HalfEdge* startEdge = gallery->boundaryEdge;
        addVertices(startEdge, allVertices);
    }    

    // Okay now adding the vertices of the inner holes
    for(HalfEdge* holeEdgeStart : gallery->InnerComponents){
        addVertices(holeEdgeStart, allVertices);
    }
    // Sorting vertices with custom lambda 
    std::sort(allVertices.begin(), allVertices.end(), comp);
    return allVertices;
}

std::vector<Vertex*> getTopmostVertices(Face* gallery){
    std::vector<Vertex*> topmostVertices;
    // Iterating through all the Holes
    for(HalfEdge* startingEdge : gallery->InnerComponents){
        // Setting max as initial edge
        double maxY = startingEdge->origin->y;
        Vertex* topMost = startingEdge->origin;
        // Traversing through all the edges (and in turn the vertices)
        HalfEdge* curr = startingEdge->nextEdge;
        while(curr != startingEdge && curr != nullptr){
            if(curr->origin->y > maxY){
                // Updating the max
                maxY = curr->origin->y;
                topMost = curr->origin;
            }
            curr  = curr->nextEdge;
        }
        // Safety Check that polygon was complete
        assert(curr != nullptr);
        topmostVertices.push_back(topMost);
    }
    // Sorting the vertices
    sort(topmostVertices.begin(), topmostVertices.end(), [](Vertex* a, Vertex* b){
        if(a->y != b->y){
            return a->y > b->y;
        }else{
            return a->x < b->x;
        }
    });

    return topmostVertices;
}

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
    std::map<HalfEdge*,Vertex* ,EdgeComparator> activeEdges;

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



int main() {
    int T;
    std::cin >> T;
    
    while(T--){
        Face* gallery = parseSingleGallery();
        mergeHoles(gallery);
        std::vector<Vertex*> mergedPolygonVertices = getMergedPolygonVertices(gallery);

        if(mergedPolygonVertices.size() == 0) continue;
    }
}
