import numpy as np
from copy import deepcopy
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator, Aer
from scipy.optimize import minimize
import random
import math

N = 3

# ═══════════════════════════════════════════════════════════
# UTILITAIRES DE BASE
# ═══════════════════════════════════════════════════════════

def case_to_qubit(i, j):
    return i * N + j

def qubit_to_case(q):
    return (q // N, q % N)

def liste_possibilite(plateau):
    return [(i, j) for i in range(N) for j in range(N) if plateau[i][j] == 0]

def cases_disponibles_quantum(plateau, marques_q):
    return [(i, j) for i in range(N) for j in range(N) if plateau[i][j] == 0]

def verifier_victoire(plateau, joueur):
    for i in range(N):
        if all(plateau[i][j] == joueur for j in range(N)): return True
    for j in range(N):
        if all(plateau[i][j] == joueur for i in range(N)): return True
    if all(plateau[i][i] == joueur for i in range(N)): return True
    if all(plateau[i][N-1-i] == joueur for i in range(N)): return True
    return False

def cases_gagnantes(plateau, joueur):
    """Retourne la liste des 3 cases formant l alignement gagnant, ou []."""
    for i in range(N):
        cells = [(i, j) for j in range(N)]
        if all(plateau[i][j] == joueur for j in range(N)): return cells
    for j in range(N):
        cells = [(i, j) for i in range(N)]
        if all(plateau[i][j] == joueur for i in range(N)): return cells
    cells = [(i, i) for i in range(N)]
    if all(plateau[i][i] == joueur for i in range(N)): return cells
    cells = [(i, N-1-i) for i in range(N)]
    if all(plateau[i][N-1-i] == joueur for i in range(N)): return cells
    return []

def determine_gagnant(plateau):
    if verifier_victoire(plateau, 1):   return "Le joueur 1 a gagné"
    if verifier_victoire(plateau, -1):  return "Le joueur 2 a gagné"
    if not liste_possibilite(plateau):  return "Match nul"
    return None

# ═══════════════════════════════════════════════════════════
# HEURISTIQUES
# ═══════════════════════════════════════════════════════════

def _get_lignes(plateau):
    lignes = []
    for i in range(N): lignes.append([plateau[i][j] for j in range(N)])
    for j in range(N): lignes.append([plateau[i][j] for i in range(N)])
    lignes.append([plateau[i][i] for i in range(N)])
    lignes.append([plateau[i][N-1-i] for i in range(N)])
    return lignes

def heuristique(plateau):
    g = determine_gagnant(plateau)
    if g == "Le joueur 1 a gagné": return 1000
    if g == "Le joueur 2 a gagné": return -1000
    if g == "Match nul": return 0
    score = 0
    for ligne in _get_lignes(plateau):
        x, o = ligne.count(1), ligne.count(-1)
        if o == 0:
            if x == 2: score += 50
            elif x == 1: score += 10
        if x == 0:
            if o == 2: score -= 50
            elif o == 1: score -= 10
    if plateau[1][1] == 1: score += 30
    elif plateau[1][1] == -1: score -= 30
    for i, j in [(0,0),(0,2),(2,0),(2,2)]:
        if plateau[i][j] == 1: score += 20
        elif plateau[i][j] == -1: score -= 20
    return score

def heuristique_optimal(plateau):
    g = determine_gagnant(plateau)
    if g == "Le joueur 1 a gagné": return 10000
    if g == "Le joueur 2 a gagné": return -10000
    if g == "Match nul": return 0
    score = 0
    mx = mo = 0
    for ligne in _get_lignes(plateau):
        x, o, v = ligne.count(1), ligne.count(-1), ligne.count(0)
        if x == 2 and o == 0: score += 100; mx += 1
        elif x == 1 and o == 0 and v == 2: score += 10
        if o == 2 and x == 0: score -= 100; mo += 1
        elif o == 1 and x == 0 and v == 2: score -= 10
    if mx >= 2: score += 500
    if mo >= 2: score -= 500
    if plateau[1][1] == 1: score += 40
    elif plateau[1][1] == -1: score -= 40
    coins = [(0,0),(0,2),(2,0),(2,2)]
    cx = sum(1 for i,j in coins if plateau[i][j] == 1)
    co = sum(1 for i,j in coins if plateau[i][j] == -1)
    if cx >= 2: score += 50
    elif cx == 1: score += 30
    if co >= 2: score -= 50
    elif co == 1: score -= 30
    for diag in [[plateau[i][i] for i in range(N)], [plateau[i][N-1-i] for i in range(N)]]:
        if diag.count(1) >= 1 and diag.count(-1) == 0: score += 20
        if diag.count(-1) >= 1 and diag.count(1) == 0: score -= 20
    return score

# ═══════════════════════════════════════════════════════════
# INITIALISATION
# ═══════════════════════════════════════════════════════════

def init_quantum():
    return [[0]*N for _ in range(N)], []

def init_quantum_9q():
    plateau = [[0]*N for _ in range(N)]
    marques_q = []
    circuit_global = QuantumCircuit(9, 9)
    return plateau, marques_q, circuit_global

# ═══════════════════════════════════════════════════════════
# CIRCUIT GATE SEQUENCE (ASCII comme dans le notebook)
# ═══════════════════════════════════════════════════════════

def get_circuit_ascii(circuit_global):
    """
    Retourne la représentation ASCII du circuit Qiskit,
    exactement comme dans le notebook de l'ami (draw output='text').
    """
    try:
        return str(circuit_global.draw(output='text'))
    except Exception as e:
        return f"Circuit non disponible : {e}"

# ═══════════════════════════════════════════════════════════
# DÉTECTION DE CYCLE
# ═══════════════════════════════════════════════════════════

def detecter_cycle_entanglement(marques_q):
    """
    Détecte un cycle d'intrication dans le graphe d'entanglement.
    Chaque case est un nœud, chaque marque quantique est une hyper-arête.
    Retourne (bool, indices_cycle, None).
    """
    if not marques_q:
        return False, [], None

    # adj[case] = liste des indices de marques qui touchent cette case
    adj = {}
    for idx, (joueur, cases, num) in enumerate(marques_q):
        for case in cases:
            adj.setdefault(case, []).append(idx)

    def trouver_cycle(case_actuelle, marque_precedente, chemin_marques, cases_visitees):
        cases_visitees.add(case_actuelle)
        for idx_marque in adj.get(case_actuelle, []):
            if idx_marque == marque_precedente:
                continue
            if idx_marque in chemin_marques:
                start_idx = chemin_marques.index(idx_marque)
                return True, chemin_marques[start_idx:]
            _, cases_de_la_marque, _ = marques_q[idx_marque]
            for prochaine_case in cases_de_la_marque:
                if prochaine_case == case_actuelle:
                    continue
                res, cycle = trouver_cycle(
                    prochaine_case, idx_marque,
                    chemin_marques + [idx_marque], cases_visitees.copy()
                )
                if res:
                    return True, cycle
        return False, []

    for case_depart in list(adj.keys()):
        trouve, indices_cycle = trouver_cycle(case_depart, -1, [], set())
        if trouve:
            return True, indices_cycle, None

    return False, [], None

# ═══════════════════════════════════════════════════════════
# COUP QUANTIQUE (circuit 9 qubits — Gate sequence du notebook)
# ═══════════════════════════════════════════════════════════

def jouer_coup_quantum_9q(plateau, marques_q, circuit_global, joueur, case1, case2):
    """
    Applique H(q1) → CX(q1,q2) → X(q2) exactement comme dans le notebook :
    ┌───┐     ┌───┐
    ┤ H ├──■──┤ H ├  ...
    └───┘┌─┴─┐├───┤
    ─────┤ X ├┤ X ├
         └───┘└───┘
    """
    numero = len(marques_q) + 1
    q1 = case_to_qubit(*case1)
    q2 = case_to_qubit(*case2)

    # Gate sequence identique au notebook de l'ami
    circuit_global.h(q1)
    circuit_global.cx(q1, q2)
    circuit_global.x(q2)

    marques_q.append((joueur, [case1, case2], numero))
    return plateau, marques_q

def jouer_coup_quantum_multi(plateau, marques_q, qc, joueur, selection):
    """
    Version multi-cases : H sur le premier qubit + CX en chaîne.
    Quand selection a exactement 2 cases, produit la même gate sequence
    que jouer_coup_quantum_9q.
    """
    numero = len(marques_q) + 1
    marques_q.append((joueur, list(selection), numero))

    qubits_bruts = [case_to_qubit(*c) for c in selection]
    # Déduplique en conservant l'ordre
    seen = set()
    qubits_uniques = []
    for q in qubits_bruts:
        if q not in seen:
            seen.add(q)
            qubits_uniques.append(q)

    if len(qubits_uniques) >= 1:
        qc.h(qubits_uniques[0])
        for i in range(len(qubits_uniques) - 1):
            qc.cx(qubits_uniques[i], qubits_uniques[i+1])
        # Différenciation joueur O (comme dans le notebook)
        if joueur == -1:
            qc.x(qubits_uniques[-1])

    return plateau, marques_q

def reinitialiser_circuit_9q(plateau, marques_q_restantes):
    """Reconstruit le circuit depuis l'état courant (après collapse)."""
    qc = QuantumCircuit(9, 9)
    for i in range(N):
        for j in range(N):
            if plateau[i][j] != 0:
                qc.x(case_to_qubit(i, j))
    for joueur, cases, num in marques_q_restantes:
        qubits = list(dict.fromkeys(case_to_qubit(*c) for c in cases))
        if qubits:
            qc.h(qubits[0])
            for k in range(len(qubits) - 1):
                qc.cx(qubits[k], qubits[k+1])
            if joueur == -1:
                qc.x(qubits[-1])
    return qc

# ═══════════════════════════════════════════════════════════
# MESURE / EFFONDREMENT
# ═══════════════════════════════════════════════════════════

def mesurer_cycle_9q(plateau, marques_q, circuit_global, indices_a_effondrer, case_critique=None):
    """
    Simule le circuit Qiskit sur 1 shot et efface les marques concernées
    en plaçant les pions selon le bitstring mesuré.
    """
    if not indices_a_effondrer:
        return plateau, marques_q, circuit_global

    sim = Aer.get_backend('qasm_simulator')
    qc_m = circuit_global.copy()
    qc_m.measure_all()
    res = sim.run(transpile(qc_m, sim), shots=1).result()
    bitstring = list(res.get_counts().keys())[0][::-1]

    marques_a_traiter   = [marques_q[i] for i in indices_a_effondrer]
    indices_persistants = [i for i in range(len(marques_q)) if i not in indices_a_effondrer]
    marques_persistantes = [marques_q[i] for i in indices_persistants]

    # Gestion case critique (saturation)
    if case_critique and plateau[case_critique[0]][case_critique[1]] == 0:
        joueurs_eligibles = [m[0] for m in marques_a_traiter if case_critique in m[1]]
        if joueurs_eligibles:
            gagnant = np.random.choice(joueurs_eligibles)
            plateau[case_critique[0]][case_critique[1]] = gagnant
            for i, m in enumerate(marques_a_traiter):
                if m[0] == gagnant and case_critique in m[1]:
                    marques_a_traiter.pop(i)
                    break

    # Placement selon le bitstring
    for joueur, cases, num in marques_a_traiter:
        candidates = [c for c in cases if plateau[c[0]][c[1]] == 0]
        if candidates:
            q_cand = [c for c in candidates if bitstring[c[0]*3 + c[1]] == '1']
            pool   = q_cand if q_cand else candidates
            choix  = pool[np.random.randint(len(pool))]
            plateau[choix[0]][choix[1]] = joueur
        else:
            vides = [(r, c) for r in range(3) for c in range(3) if plateau[r][c] == 0]
            if vides:
                plateau[vides[0][0]][vides[0][1]] = joueur

    # Reconstruction du circuit pour les survivants
    _, _, qc_new = init_quantum_9q()
    mq_finale = []
    for j, cs, n in marques_persistantes:
        cs_libres = [c for c in cs if plateau[c[0]][c[1]] == 0]
        if cs_libres:
            _, mq_finale = jouer_coup_quantum_multi(plateau, mq_finale, qc_new, j, cs_libres)

    return plateau, mq_finale, qc_new

def obtenir_toute_la_chaine(indices_depart, marques_q):
    """Parcourt le graphe pour trouver toutes les marques connectées."""
    chaine = set(indices_depart)
    nouveau_ajoute = True
    while nouveau_ajoute:
        nouveau_ajoute = False
        cases_touchees = set()
        for i in chaine:
            cases_touchees.update(marques_q[i][1])
        for i, (joueur, cases, num) in enumerate(marques_q):
            if i not in chaine and any(c in cases_touchees for c in cases):
                chaine.add(i)
                nouveau_ajoute = True
    return list(chaine)

def resoudre_par_saturation(plateau, marques_q, circuit_global, limite_N, trigger_sat, trigger_cyc):
    """
    Boucle principale de résolution :
      1. Saturation par même signe (TOUJOURS — règle fondamentale)
      2. Saturation générale (si trigger_sat)
      3. Cycle (si trigger_cyc)
      4. Effondrement total si toutes les cases atteignent N/N
      3. S'arrête quand rien à résoudre
    """
    continuer = True
    while continuer:
        continuer = False
        indices_initiaux = []
        case_critique = None

        # Règle 1 : saturation par même signe (indépendante de trigger_sat)
        # Si une case a N marques du même joueur → effondrement obligatoire
        if not continuer:
            for c_test in [(i, j) for i in range(N) for j in range(N)]:
                if plateau[c_test[0]][c_test[1]] != 0:
                    continue
                for joueur_test in [1, -1]:
                    count_same = sum(
                        m[1].count(c_test)
                        for m in marques_q if m[0] == joueur_test
                    )
                    if count_same >= limite_N:
                        case_critique = c_test
                        indices_initiaux = [i for i, m in enumerate(marques_q) if c_test in m[1]]
                        continuer = True
                        break
                if continuer:
                    break

        # Règle 2 : saturation générale (si trigger_sat activé)
        if not continuer and trigger_sat:
            compteur = {}
            for idx, (joueur, cases, num) in enumerate(marques_q):
                for c in cases:
                    compteur[c] = compteur.get(c, 0) + 1
                    if compteur[c] >= limite_N:
                        case_critique = c
                        indices_initiaux = [i for i, m in enumerate(marques_q) if c in m[1]]
                        continuer = True
                        break
                if continuer: break

        # Règle 3 : cycles
        if not continuer and trigger_cyc:
            existe, indices_cycle, _ = detecter_cycle_entanglement(marques_q)
            if existe:
                indices_initiaux = indices_cycle
                continuer = True

        if continuer:
            indices_globaux = obtenir_toute_la_chaine(indices_initiaux, marques_q)
            plateau, marques_q, circuit_global = mesurer_cycle_9q(
                plateau, marques_q, circuit_global, indices_globaux, case_critique
            )

    # Règle 4 : si toutes les cases libres ont atteint N/N → effondrement total
    cases_libres = [(i, j) for i in range(N) for j in range(N) if plateau[i][j] == 0]
    if cases_libres and marques_q:
        toutes_saturees = all(
            sum(m[1].count(c) for m in marques_q) >= limite_N
            for c in cases_libres
        )
        if toutes_saturees:
            indices_tous = list(range(len(marques_q)))
            plateau, marques_q, circuit_global = mesurer_cycle_9q(
                plateau, marques_q, circuit_global, indices_tous, None
            )

    return plateau, marques_q, circuit_global

# ═══════════════════════════════════════════════════════════
# IA MINIMAX CLASSIQUE (du notebook)
# ═══════════════════════════════════════════════════════════

def minmax_elagage_alphabeta(plateau, profondeur_max, joueur):
    """Minimax alpha-bêta classique (coup unique, non-quantique)."""
    def score(plateau, profondeur, joueur_actuel, alpha, beta):
        g = determine_gagnant(plateau)
        if profondeur == profondeur_max or g is not None:
            return heuristique_optimal(plateau)
        coups = liste_possibilite(plateau)
        if joueur_actuel == 1:
            s_max, c_max = float('-inf'), None
            for i, j in coups:
                nv = deepcopy(plateau); nv[i][j] = joueur_actuel
                s = score(nv, profondeur+1, -joueur_actuel, alpha, beta)
                if s > s_max: s_max, c_max = s, (i, j)
                alpha = max(alpha, s_max)
                if beta <= alpha: break
            return (s_max, c_max) if profondeur == 0 else s_max
        else:
            s_min, c_min = float('inf'), None
            for i, j in coups:
                nv = deepcopy(plateau); nv[i][j] = joueur_actuel
                s = score(nv, profondeur+1, -joueur_actuel, alpha, beta)
                if s < s_min: s_min, c_min = s, (i, j)
                beta = min(beta, s_min)
                if beta <= alpha: break
            return (s_min, c_min) if profondeur == 0 else s_min
    return score(plateau, 0, joueur, float('-inf'), float('inf'))

# ═══════════════════════════════════════════════════════════
# IA GROVER / QAOA (quantique — du notebook)
# ═══════════════════════════════════════════════════════════

def alignements_case(i, j):
    aligns = {f"row_{i}", f"col_{j}"}
    if i == j: aligns.add("diag_main")
    if i + j == N - 1: aligns.add("diag_anti")
    return aligns

def construire_qubo_plateau(plateau):
    cases = [(i, j) for i in range(N) for j in range(N) if plateau[i][j] == 0]
    n = len(cases)
    all_lignes = (
        [[(i, j) for j in range(N)] for i in range(N)] +
        [[(i, j) for i in range(N)] for j in range(N)] +
        [[(i, i) for i in range(N)]] +
        [[(i, N-1-i) for i in range(N)]]
    )
    h = {}
    for idx, (ci, cj) in enumerate(cases):
        val = 3 if (ci,cj)==(1,1) else (2 if (ci,cj) in [(0,0),(0,2),(2,0),(2,2)] else 1)
        for ligne in all_lignes:
            if (ci, cj) in ligne:
                if not any(plateau[li][lj] != 0 and plateau[li][lj] == 1 for li, lj in ligne):
                    val += 1
        h[idx] = val
    J = {}
    for i in range(n):
        for j in range(i+1, n):
            syn = len(alignements_case(*cases[i]) | alignements_case(*cases[j])) - \
                  len(alignements_case(*cases[i]) & alignements_case(*cases[j]))
            for ligne in all_lignes:
                if cases[i] in ligne and cases[j] in ligne:
                    if not any(plateau[li][lj] == 1 for li, lj in ligne):
                        syn += 3
            J[(i, j)] = syn
    return cases, h, J

def evaluer_cases_qaoa(plateau, p_layers=1):
    cases, h, J = construire_qubo_plateau(plateau)
    n = len(cases)
    if n < 2: return {c: 0 for c in cases}
    if n > 7:
        top = sorted(h.keys(), key=lambda k: h[k], reverse=True)[:7]
        cases = [cases[i] for i in top]
        h = {ni: h[oi] for ni, oi in enumerate(top)}
        J = {(ni, nj): J[(oi, oj)] for ni, oi in enumerate(top)
             for nj, oj in enumerate(top) if ni < nj and (oi, oj) in J}
        n = len(cases)

    def circuit_qaoa(gamma, beta):
        qc = QuantumCircuit(n, n)
        qc.h(range(n))
        for layer in range(p_layers):
            for i in range(n):
                if i in h: qc.rz(gamma[layer] * h[i], i)
            for (i, j), val in J.items():
                if i < n and j < n:
                    qc.cx(i, j); qc.rz(gamma[layer] * val, j); qc.cx(i, j)
            for i in range(n): qc.rx(beta[layer], i)
        qc.measure(range(n), range(n))
        return qc

    def objectif(params):
        gamma, beta = params[:p_layers], params[p_layers:]
        qc = circuit_qaoa(gamma, beta)
        sim = AerSimulator()
        counts = sim.run(transpile(qc, sim), shots=200).result().get_counts()
        total = cost_total = 0
        for bitstring, count in counts.items():
            bits = bitstring[::-1]
            cost = sum(h[i] for i in range(n) if i < len(bits) and bits[i] == '1')
            for (i, j), val in J.items():
                if i < len(bits) and j < len(bits) and bits[i] == '1' and bits[j] == '1':
                    cost += val
            cost_total += cost * count; total += count
        return -cost_total / total if total else 0

    p0 = np.random.uniform(0, np.pi, 2 * p_layers)
    res = minimize(objectif, p0, method='COBYLA', options={'maxiter': 30})
    gamma_opt, beta_opt = res.x[:p_layers], res.x[p_layers:]
    qc = circuit_qaoa(gamma_opt, beta_opt)
    sim = AerSimulator()
    counts = sim.run(transpile(qc, sim), shots=500).result().get_counts()
    scores = {c: 0.0 for c in cases}
    total_shots = sum(counts.values())
    for bitstring, count in counts.items():
        bits = bitstring[::-1]
        for i in range(min(n, len(bits))):
            if bits[i] == '1': scores[cases[i]] += count / total_shots
    return scores

def evaluer_paire_grover(plateau, case1, case2, marques_q, joueur_ia=-1, scores_qaoa=None):
    p1 = deepcopy(plateau); p1[case1[0]][case1[1]] = joueur_ia
    p2 = deepcopy(plateau); p2[case2[0]][case2[1]] = joueur_ia
    score = (heuristique(p1) + heuristique(p2)) / 2.0

    a1, a2 = alignements_case(*case1), alignements_case(*case2)
    score += len(a1 | a2) * 15 * joueur_ia
    score -= len(a1 & a2) * 10 * joueur_ia
    for case in [case1, case2]:
        if case == (1,1): score += 20 * joueur_ia
        elif case in [(0,0),(0,2),(2,0),(2,2)]: score += 10 * joueur_ia

    # Conscience des cycles
    marques_test = marques_q + [(joueur_ia, [case1, case2], len(marques_q)+1)]
    cycle_detecte, marques_cycle, _ = detecter_cycle_entanglement(marques_test)
    if cycle_detecte:
        scores_res = []
        for direction in ['10', '01']:
            p_sim = deepcopy(plateau)
            cases_occ = {(i,j) for i in range(N) for j in range(N) if p_sim[i][j] != 0}
            for idx in marques_cycle:
                j_sim, cases_sim, _ = marques_test[idx]
                if len(cases_sim) >= 2:
                    pref, alt = (cases_sim[0], cases_sim[1]) if direction == '10' else (cases_sim[1], cases_sim[0])
                    cf = next((c for c in [pref, alt] if c not in cases_occ and p_sim[c[0]][c[1]] == 0), None)
                    if cf: p_sim[cf[0]][cf[1]] = j_sim; cases_occ.add(cf)
            scores_res.append(heuristique(p_sim))
        score_cycle = max(scores_res) if joueur_ia == -1 else min(scores_res)
        score = 0.4 * score + 0.6 * score_cycle

    if scores_qaoa:
        score += (scores_qaoa.get(case1, 0) + scores_qaoa.get(case2, 0)) * 50 * joueur_ia
    return score

def construire_oracle_grover(qc, indices_marques, n_qubits):
    for idx in indices_marques:
        binary = format(idx, f'0{n_qubits}b')
        for bp, bit in enumerate(binary):
            if bit == '0': qc.x(bp)
        if n_qubits == 1:
            qc.z(0)
        else:
            qc.h(n_qubits-1); qc.mcx(list(range(n_qubits-1)), n_qubits-1); qc.h(n_qubits-1)
        for bp, bit in enumerate(binary):
            if bit == '0': qc.x(bp)

def construire_diffuseur_grover(qc, n_qubits):
    qc.h(range(n_qubits)); qc.x(range(n_qubits))
    qc.h(n_qubits-1); qc.mcx(list(range(n_qubits-1)), n_qubits-1); qc.h(n_qubits-1)
    qc.x(range(n_qubits)); qc.h(range(n_qubits))

def recherche_grover(scores_paires):
    K = len(scores_paires)
    if K == 0: return 0
    seuil = sorted(scores_paires)[max(1, K//4) - 1]
    bons  = [i for i, s in enumerate(scores_paires) if s <= seuil]
    M     = len(bons)
    if M == 0 or M == K:
        return scores_paires.index(min(scores_paires))
    n_q = max(2, math.ceil(math.log2(K)))
    n_it = max(1, int(math.pi/4 * math.sqrt(K/M)))
    qc = QuantumCircuit(n_q, n_q)
    qc.h(range(n_q))
    for _ in range(n_it):
        construire_oracle_grover(qc, bons, n_q)
        construire_diffuseur_grover(qc, n_q)
    qc.measure(range(n_q), range(n_q))
    sim = AerSimulator()
    mesure = list(sim.run(transpile(qc, sim), shots=1).result().get_counts().keys())[0][::-1]
    idx = int(mesure, 2)
    return idx if idx < K else scores_paires.index(min(scores_paires))

def choisir_coup_ia_grover(plateau, marques_q, joueur_ia=-1, mode='heuristique_optimal'):
    cases = cases_disponibles_quantum(plateau, marques_q)
    if len(cases) < 2: return None, None
    paires = [(cases[i], cases[j]) for i in range(len(cases)) for j in range(i+1, len(cases))]
    if not paires: return None, None
    if mode == 'qaoa':
        scores_qaoa = evaluer_cases_qaoa(plateau, p_layers=1)
        scores = [evaluer_paire_grover(plateau, c1, c2, marques_q, joueur_ia, scores_qaoa) for c1,c2 in paires]
    else:
        scores = [evaluer_paire_grover(plateau, c1, c2, marques_q, joueur_ia) for c1,c2 in paires]
    return paires[recherche_grover(scores)]

# ═══════════════════════════════════════════════════════════
# IA MINIMAX QUANTIQUE (du notebook)
# ═══════════════════════════════════════════════════════════

def heuristique_quantum(plateau, marques_q, joueur):
    if verifier_victoire(plateau, joueur):  return 1000
    if verifier_victoire(plateau, -joueur): return -1000
    score = heuristique_optimal(plateau)
    for j, cases, num in marques_q:
        for case in set(cases):
            if plateau[case[0]][case[1]] == 0:
                base = 5 if case==(1,1) else (3 if case in [(0,0),(0,2),(2,0),(2,2)] else 1)
                score += base * j
    return score

def minmax_quantum(plateau, marques_q, profondeur_max, joueur):
    """Minimax alpha-bêta adapté au jeu quantique (paires de cases)."""
    def score(plateau, marques_q, profondeur, joueur_actuel, alpha, beta):
        if verifier_victoire(plateau, 1):  return 1000
        if verifier_victoire(plateau, -1): return -1000
        cases = cases_disponibles_quantum(plateau, marques_q)
        if len(cases) < 2 or profondeur == profondeur_max:
            return heuristique_quantum(plateau, marques_q, joueur_actuel)
        paires = [(cases[i], cases[j]) for i in range(len(cases)) for j in range(i+1, len(cases))]
        if joueur_actuel == 1:
            s_max, p_max = float('-inf'), None
            for c1, c2 in paires:
                p_sim = deepcopy(plateau)
                mq_sim = deepcopy(marques_q)
                _, _, qc_sim = init_quantum_9q()
                _, mq_sim = jouer_coup_quantum_multi(p_sim, mq_sim, qc_sim, joueur_actuel, [c1, c2])
                s = score(p_sim, mq_sim, profondeur+1, -joueur_actuel, alpha, beta)
                if s > s_max: s_max, p_max = s, (c1, c2)
                alpha = max(alpha, s_max)
                if beta <= alpha: break
            return (s_max, p_max) if profondeur == 0 else s_max
        else:
            s_min, p_min = float('inf'), None
            for c1, c2 in paires:
                p_sim = deepcopy(plateau)
                mq_sim = deepcopy(marques_q)
                _, _, qc_sim = init_quantum_9q()
                _, mq_sim = jouer_coup_quantum_multi(p_sim, mq_sim, qc_sim, joueur_actuel, [c1, c2])
                s = score(p_sim, mq_sim, profondeur+1, -joueur_actuel, alpha, beta)
                if s < s_min: s_min, p_min = s, (c1, c2)
                beta = min(beta, s_min)
                if beta <= alpha: break
            return (s_min, p_min) if profondeur == 0 else s_min

    resultat = score(plateau, marques_q, 0, joueur, float('-inf'), float('inf'))
    _, paire = resultat
    if paire is None: return None, None
    return paire[0], paire[1]

def choisir_coup_minimax_quantum(plateau, marques_q, joueur=-1, profondeur=2):
    cases = cases_disponibles_quantum(plateau, marques_q)
    if len(cases) < 2: return None, None
    return minmax_quantum(plateau, marques_q, profondeur, joueur)

# ═══════════════════════════════════════════════════════════
# IA RANDOM (baseline)
# ═══════════════════════════════════════════════════════════

def choisir_coup_random(plateau, marques_q):
    cases = cases_disponibles_quantum(plateau, marques_q)
    if len(cases) < 2: return None, None
    return random.sample(cases, 2)


# ═══════════════════════════════════════════════════════════
# TOURNOI ELO (du notebook de l'ami — cell 103)
# ═══════════════════════════════════════════════════════════

def calculer_elo(ratings, ia1, ia2, resultat, k=64):
    r1, r2 = ratings[ia1], ratings[ia2]
    E1 = 1 / (1 + 10 ** ((r2 - r1) / 400))
    E2 = 1 - E1
    S1 = 1.0 if resultat == 1 else (0.5 if resultat == 0 else 0.0)
    S2 = 1.0 - S1
    ratings[ia1] += k * (S1 - E1)
    ratings[ia2] += k * (S2 - E2)
    return ratings


def jouer_partie_ia_vs_ia_tournoi(nom_ia1, nom_ia2):
    """
    Fait jouer deux IAs l'une contre l'autre (du notebook cell 103).
    Retourne +1 (ia1 gagne), -1 (ia2 gagne), 0 (nul).
    """
    plateau, marques_q, circuit_global = init_quantum_9q()
    joueur = 1
    config = {1: nom_ia1, -1: nom_ia2}

    for _ in range(10):
        nom_ia = config[joueur]
        cases  = cases_disponibles_quantum(plateau, marques_q)
        if len(cases) < 2:
            break

        if nom_ia == 'random':
            c1, c2 = random.sample(cases, 2)
        elif nom_ia == 'grover':
            c1, c2 = choisir_coup_ia_grover(plateau, marques_q, mode='heuristique_optimal')
        elif nom_ia == 'qaoa':
            c1, c2 = choisir_coup_ia_grover(plateau, marques_q, mode='qaoa')
        elif nom_ia == 'minimax_q':
            c1, c2 = choisir_coup_minimax_quantum(plateau, marques_q, joueur=joueur, profondeur=2)
        else:
            c1, c2 = random.sample(cases, 2)

        if c1 is None:
            break

        plateau, marques_q = jouer_coup_quantum_multi(plateau, marques_q, circuit_global, joueur, [c1, c2])
        plateau, marques_q, circuit_global = resoudre_par_saturation(
            plateau, marques_q, circuit_global, 2, False, True
        )

        if verifier_victoire(plateau,  1): return  1
        if verifier_victoire(plateau, -1): return -1
        joueur = -joueur

    if verifier_victoire(plateau,  1): return  1
    if verifier_victoire(plateau, -1): return -1
    return 0


def tournoi_round_robin_elo(n_parties, callback_progression=None):
    """
    Tournoi round-robin ELO entre les 4 IAs (du notebook cell 103).
    callback_progression(match_num, total, ia1, ia2, elo, stats) appelé après chaque match.
    Retourne (elo, stats, classement, historique_elo).
    """
    ias = ['random', 'grover', 'qaoa', 'minimax_q']
    elo            = {ia: 1000.0 for ia in ias}
    stats          = {ia: {'V': 0, 'N': 0, 'D': 0} for ia in ias}
    historique_elo = {ia: [1000.0] for ia in ias}

    n = len(ias)
    total = n * (n - 1) // 2
    match_num = 0

    for i in range(n):
        for j in range(i + 1, n):
            ia1, ia2   = ias[i], ias[j]
            match_num += 1
            for k in range(n_parties):
                if k % 2 == 0:
                    res = jouer_partie_ia_vs_ia_tournoi(ia1, ia2)
                else:
                    res = -jouer_partie_ia_vs_ia_tournoi(ia2, ia1)

                elo = calculer_elo(elo, ia1, ia2, res)
                historique_elo[ia1].append(elo[ia1])
                historique_elo[ia2].append(elo[ia2])

                if   res ==  1: stats[ia1]['V'] += 1; stats[ia2]['D'] += 1
                elif res == -1: stats[ia2]['V'] += 1; stats[ia1]['D'] += 1
                else:           stats[ia1]['N'] += 1; stats[ia2]['N'] += 1

            if callback_progression:
                callback_progression(match_num, total, ia1, ia2, dict(elo), dict(stats))

    classement = sorted(ias, key=lambda ia: elo[ia], reverse=True)
    return elo, stats, classement, historique_elo
