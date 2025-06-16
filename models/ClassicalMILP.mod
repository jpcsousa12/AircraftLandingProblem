/*********************************************
 * OPL Aircraft Landing Problem (Multi-Runway)
 * Based on Beasley et al. (2000)
 * Adapted to the provided mathematical formulation
 *********************************************/

// ---------------------------
// Parameters
// ---------------------------
int P = ...; // Number of planes (n in math formulation)
int R = ...;   // Number of runways (m in math formulation)

range PLANES = 1..P;  // I in math formulation
range RUNWAYS = 1..R; // R in math formulation

// Time and cost parameters
float Ai[PLANES] = ...;        // Appearance time (not used in this mathematical model)
float Ei[PLANES] = ...;        // Earliest landing time (Ei in math formulation)
float Li[PLANES] = ...;        // Latest landing time (Li in math formulation)
float Ti[PLANES] = ...;        // Target landing time (Ti in math formulation)
float gi[PLANES] = ...;        // Earliness penalty (ci+ in math formulation)
float hi[PLANES] = ...;        // Lateness penalty (ci- in math formulation)
float S[PLANES][PLANES] = ...; // Separation time if on same runway (s_ij in math formulation for same runway)
float M = 99999;               // Large number for big-M constraints

// ---------------------------
// Decision Variables
// ---------------------------
dvar float+ x[PLANES];                 // Actual landing time (xi in math formulation)
dvar float+ alpha[PLANES];             // Earliness (alpha_i in math formulation)
dvar float+ beta[PLANES];              // Lateness (beta_i in math formulation)
dvar boolean y[PLANES][PLANES];        // 1 if i lands before j (y_ij in math formulation, based on its usage in (4) and (5))
dvar boolean gamma[PLANES][RUNWAYS];   // 1 if plane i lands on runway r (gamma_ir in math formulation)
dvar boolean delta[PLANES][PLANES];    // 1 if i and j land on the same runway (z_ij in math formulation)

execute {
    cplex.tilim = 60; // set time limit in seconds
}

// ---------------------------
// Objective
// ---------------------------
// Corresponds to Mathematical Objective (1)
minimize sum(i in PLANES) (gi[i] * alpha[i] + hi[i] * beta[i]);

// ---------------------------
// Constraints
// ---------------------------
subject to {

  // (1) Time window for each plane - Corresponds to Mathematical Constraint (2)
  forall(i in PLANES)
    Ei[i] <= x[i] <= Li[i];

  // (2) Define alpha, beta - Corresponds to Mathematical Constraint (3)
  forall(i in PLANES)
	x[i] - Ti[i] == alpha[i] - beta[i];
	
  // (3) 
  forall(i, j in PLANES: i != j)
    x[j] - x[i] >= S[i][j] * delta[i][j] - M * y[j][i];

  // (4) 
  forall(i, j in PLANES: i != j)
    forall(r in RUNWAYS)
      delta[i][j] >= gamma[i][r] + gamma[j][r] - 1;
      
  // (5) Mutual ordering - Corresponds to Mathematical Constraint (5)
  forall(i, j in PLANES: i != j)
    y[i][j] + y[j][i] == 1;
    
  // (7) Each plane must land on exactly one runway - Corresponds to Mathematical Constraint (7)
  forall(i in PLANES)
    sum(r in RUNWAYS) gamma[i][r] == 1;
}