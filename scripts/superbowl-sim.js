// Monte Carlo Super Bowl LX Simulation: Patriots vs Seahawks
// Based on: SEA -4.5, O/U 45.5, SEA ML -238 (~70.4% win prob)
// Key data: SEA defense elite pressure, NE struggles early, Sam Darnold + JSN

const SIMS = 1000;

// Team parameters (based on season stats + betting lines)
const SEA = {
  name: 'Seahawks', abbr: 'SEA',
  winProb: 0.704,
  avgPoints: 25.2, stdPoints: 7.5,
  qb: 'Sam Darnold', qbPassYards: [220, 60], qbTDs: [2.1, 1.0], qbINTs: [0.7, 0.6], qbCompAtt: [22, 34],
  rb1: 'Kenneth Walker III', rb1Yards: [78, 28], rb1TDs: [0.6, 0.5],
  rb2: 'Zach Charbonnet', rb2Yards: [35, 18], rb2TDs: [0.3, 0.4],
  wr1: 'Jaxon Smith-Njigba', wr1Yards: [88, 30], wr1TDs: [0.7, 0.5], wr1Rec: [7, 2.5],
  wr2: 'DK Metcalf', wr2Yards: [65, 28], wr2TDs: [0.5, 0.5], wr2Rec: [4, 2],
  te1: 'Noah Fant', te1Yards: [35, 18], te1TDs: [0.2, 0.3], te1Rec: [3, 1.5],
  defSacks: [3.2, 1.5], defINTs: [1.1, 0.8], defFumbles: [0.5, 0.5]
};

const NE = {
  name: 'Patriots', abbr: 'NE',
  winProb: 0.296,
  avgPoints: 20.3, stdPoints: 8.0,
  qb: 'Drake Maye', qbPassYards: [245, 65], qbTDs: [1.8, 1.0], qbINTs: [1.0, 0.7], qbCompAtt: [21, 33],
  rb1: 'Rhamondre Stevenson', rb1Yards: [72, 25], rb1TDs: [0.5, 0.5],
  rb2: 'Antonio Gibson', rb2Yards: [28, 15], rb2TDs: [0.2, 0.3],
  wr1: 'Ja\'Marr Chase', wr1Yards: [95, 35], wr1TDs: [0.8, 0.6], wr1Rec: [7, 3],
  wr2: 'Kayshon Boutte', wr2Yards: [52, 22], wr2TDs: [0.4, 0.4], wr2Rec: [4, 2],
  te1: 'Hunter Henry', te1Yards: [45, 20], te1TDs: [0.4, 0.4], te1Rec: [4, 2],
  defSacks: [2.5, 1.3], defINTs: [0.8, 0.6], defFumbles: [0.4, 0.4]
};

function gaussRand(mean, std) {
  let u = 0, v = 0;
  while (u === 0) u = Math.random();
  while (v === 0) v = Math.random();
  return Math.max(0, Math.round(mean + std * Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v)));
}

function simGame() {
  const seaWins = Math.random() < SEA.winProb;
  
  // Generate correlated scores
  let seaScore, neScore;
  if (seaWins) {
    seaScore = gaussRand(SEA.avgPoints, SEA.stdPoints);
    neScore = gaussRand(NE.avgPoints - 2, NE.stdPoints);
    if (neScore >= seaScore) neScore = seaScore - Math.ceil(Math.random() * 7);
    if (neScore < 0) neScore = Math.ceil(Math.random() * 10);
  } else {
    neScore = gaussRand(NE.avgPoints + 3, NE.stdPoints);
    seaScore = gaussRand(SEA.avgPoints - 3, SEA.stdPoints);
    if (seaScore >= neScore) seaScore = neScore - Math.ceil(Math.random() * 7);
    if (seaScore < 0) seaScore = Math.ceil(Math.random() * 10);
  }

  const simPlayer = (team, prefix) => ({
    passYards: gaussRand(team[prefix+'PassYards']?.[0]||0, team[prefix+'PassYards']?.[1]||0),
    passTDs: gaussRand(team[prefix+'TDs']?.[0]||0, team[prefix+'TDs']?.[1]||0),
    passINTs: gaussRand(team[prefix+'INTs']?.[0]||0, team[prefix+'INTs']?.[1]||0),
    comp: gaussRand(team[prefix+'CompAtt']?.[0]||0, team[prefix+'CompAtt']?.[1]||0),
    att: gaussRand(team[prefix+'CompAtt']?.[1]||0, 5),
    yards: gaussRand(team[prefix+'Yards']?.[0]||0, team[prefix+'Yards']?.[1]||0),
    tds: gaussRand(team[prefix+'TDs']?.[0]||0, team[prefix+'TDs']?.[1]||0),
    rec: gaussRand(team[prefix+'Rec']?.[0]||0, team[prefix+'Rec']?.[1]||0),
  });

  return {
    seaScore, neScore, winner: seaWins ? 'SEA' : 'NE',
    seaQB: simPlayer(SEA, 'qb'), neQB: simPlayer(NE, 'qb'),
    seaRB1: simPlayer(SEA, 'rb1'), neRB1: simPlayer(NE, 'rb1'),
    seaWR1: simPlayer(SEA, 'wr1'), neWR1: simPlayer(NE, 'wr1'),
    seaWR2: simPlayer(SEA, 'wr2'), neWR2: simPlayer(NE, 'wr2'),
    seaTE: simPlayer(SEA, 'te1'), neTE: simPlayer(NE, 'te1'),
    seaDefSacks: gaussRand(SEA.defSacks[0], SEA.defSacks[1]),
    seaDefINTs: gaussRand(SEA.defINTs[0], SEA.defINTs[1]),
    neDefSacks: gaussRand(NE.defSacks[0], NE.defSacks[1]),
    neDefINTs: gaussRand(NE.defINTs[0], NE.defINTs[1]),
  };
}

// Run simulations
const results = [];
let seaWins = 0, neWins = 0;
let totalSeaScore = 0, totalNeScore = 0;
const scoreCounts = {};

for (let i = 0; i < SIMS; i++) {
  const g = simGame();
  results.push(g);
  if (g.winner === 'SEA') seaWins++; else neWins++;
  totalSeaScore += g.seaScore;
  totalNeScore += g.neScore;
  const key = `${g.seaScore}-${g.neScore}`;
  scoreCounts[key] = (scoreCounts[key] || 0) + 1;
}

// Find most common score
const sortedScores = Object.entries(scoreCounts).sort((a,b) => b[1] - a[1]);
const [mostLikelyScore, mostLikelyCount] = sortedScores[0];

// Get median game for the most likely winner
const winnerGames = results.filter(g => g.winner === (seaWins > neWins ? 'SEA' : 'NE'));
winnerGames.sort((a,b) => Math.abs(a.seaScore - totalSeaScore/SIMS) - Math.abs(b.seaScore - totalSeaScore/SIMS));
const medianGame = winnerGames[Math.floor(winnerGames.length / 2)];

// Calculate averages
const avg = (arr, fn) => Math.round(arr.reduce((s, g) => s + fn(g), 0) / arr.length);

const output = {
  simulations: SIMS,
  seaWinPct: (seaWins / SIMS * 100).toFixed(1),
  neWinPct: (neWins / SIMS * 100).toFixed(1),
  avgScore: `SEA ${(totalSeaScore/SIMS).toFixed(1)} - NE ${(totalNeScore/SIMS).toFixed(1)}`,
  mostLikelyScore: mostLikelyScore,
  mostLikelyScoreFreq: `${(mostLikelyCount/SIMS*100).toFixed(1)}%`,
  top5Scores: sortedScores.slice(0, 5).map(([s, c]) => `${s} (${(c/SIMS*100).toFixed(1)}%)`),
  predictedWinner: seaWins > neWins ? 'Seattle Seahawks' : 'New England Patriots',
  predictedLoser: seaWins > neWins ? 'New England Patriots' : 'Seattle Seahawks',
  predictedScore: `${medianGame.seaScore}-${medianGame.neScore}`,
  medianGame: {
    seaScore: medianGame.seaScore,
    neScore: medianGame.neScore,
    darnold: { passYards: medianGame.seaQB.passYards, tds: medianGame.seaQB.passTDs, ints: medianGame.seaQB.passINTs, comp: medianGame.seaQB.comp, att: Math.max(medianGame.seaQB.comp + 8, medianGame.seaQB.att) },
    maye: { passYards: medianGame.neQB.passYards, tds: medianGame.neQB.passTDs, ints: medianGame.neQB.passINTs, comp: medianGame.neQB.comp, att: Math.max(medianGame.neQB.comp + 10, medianGame.neQB.att) },
    walker: { rushYards: medianGame.seaRB1.yards, tds: medianGame.seaRB1.tds },
    stevenson: { rushYards: medianGame.neRB1.yards, tds: medianGame.neRB1.tds },
    jsn: { rec: medianGame.seaWR1.rec, yards: medianGame.seaWR1.yards, tds: medianGame.seaWR1.tds },
    metcalf: { rec: medianGame.seaWR2.rec, yards: medianGame.seaWR2.yards, tds: medianGame.seaWR2.tds },
    chase: { rec: medianGame.neWR1.rec, yards: medianGame.neWR1.yards, tds: medianGame.neWR1.tds },
    henry: { rec: medianGame.neTE.rec, yards: medianGame.neTE.yards, tds: medianGame.neTE.tds },
    seaSacks: medianGame.seaDefSacks,
    neINTs: medianGame.seaDefINTs,
  },
  mvpPrediction: seaWins > neWins ? 'Jaxon Smith-Njigba' : 'Drake Maye',
};

console.log(JSON.stringify(output, null, 2));
