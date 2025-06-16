using CP;

// -------- Parameters --------
int P = ...; // Number of planes
int R = ...; // Number of runways

range PLANES = 1..P;

int Ai[PLANES] = ...;    // Appearance time (can be omitted if unused)
int Ei[PLANES] = ...;    // Earliest landing time
int Li[PLANES] = ...;    // Latest landing time
int Ti[PLANES] = ...;    // Target landing time
int gi[PLANES] = ...;    // Earliness penalty
int hi[PLANES] = ...;    // Lateness penalty
int S[PLANES][PLANES] = ...; // Separation time if on same runway

// -------- Decision Variables --------
dvar int+ x[PLANES];   // Actual landing time
dvar int r[PLANES];                       // Runway assignment
dvar int+ alpha[PLANES];                  // Earliness
dvar int+ beta[PLANES];                   // Lateness

// -------- Objective --------
minimize sum(i in PLANES) (gi[i] * alpha[i] + hi[i] * beta[i]);

// -------- Constraints --------
subject to {
  // Assign each plane a runway in 1..R
  forall(i in PLANES)
    r[i] >= 1 && r[i] <= R;

  // Landing window
  forall(i in PLANES)
    Ei[i] <= x[i] <= Li[i];

  // Earliness and lateness calculation
  forall(i in PLANES) {
    alpha[i] >= Ti[i] - x[i];
    beta[i]  >= x[i] - Ti[i];
  }

  // Runway separation constraints (CP-native version)
  forall(i in PLANES, j in PLANES : i < j) {
    if (S[i][j] > 0) {
      (r[i] != r[j]) || (x[i] + S[i][j] <= x[j]) || (x[j] + S[j][i] <= x[i]);
    }
  }
}
