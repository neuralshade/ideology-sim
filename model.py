import numpy as np
from scipy.special import softmax

class SocietyModel:
    def __init__(self, N=5000, seed=42):
        rng = np.random.default_rng(seed)

        self.N = N
        self.t = 0

        # === MICRO ===
        self.income = rng.pareto(2.0, N)
        self.income /= self.income.max()
        self.ideology = rng.uniform(-1, 1, N)

        # === MACRO ===
        self.G = 0.45
        self.S = 0.55
        self.U = 0.1
        self.C = 0.02

        # === PARÂMETROS ===
        self.S_crit = 0.7
        self.sigma = 0.08
        self.m0 = 0.35

        self.ideology_bins = np.array([-0.8, -0.3, 0.3, 0.8])
        self.labels = ["Comunismo", "Social-democracia", "Capitalismo", "Libertarianismo"]

    # -------------------------------
    # Mobilidade ideológica contínua
    # -------------------------------
    def mobility(self):
        return self.m0 * (1 - np.tanh((self.S - self.S_crit) / self.sigma))

    # -------------------------------
    # Utilidade percebida
    # -------------------------------
    def utility(self, i, target):
        r = self.income[i]
        current = self.ideology[i]

        # Benefício material
        if target < -0.5:
            material = 2.0 * (1 - r)
        elif target > 0.5:
            material = 1.6 * r
        else:
            material = 0.6

        # Inércia ideológica
        inertia = -abs(target - current)

        # Efeito da satisfação (centro como atrator)
        satisfaction = self.S * (1 - abs(target))

        # Desemprego e crescimento
        macro = (
            -0.5 * self.U * abs(target)
            + 0.4 * self.C * target
        )

        return material + inertia + satisfaction + macro

    # -------------------------------
    # Um passo temporal
    # -------------------------------
    def step(self):
        M = self.mobility()
        rng = np.random.default_rng()

        for i in range(self.N):
            if rng.random() < M:
                utilities = np.array([
                    self.utility(i, ide) for ide in self.ideology_bins
                ])
                probs = softmax(utilities)
                self.ideology[i] = rng.choice(self.ideology_bins, p=probs)

        self.update_macro()
        self.t += 1

    # -------------------------------
    # Feedback macro
    # -------------------------------
    def update_macro(self):
        self.G = np.clip(np.std(self.income) * 1.8, 0, 1)

        avg_ideology = np.mean(self.ideology)
        polarization = np.var(self.ideology)

        self.S = np.clip(
            0.75
            - 0.4 * abs(avg_ideology)
            - 0.3 * polarization
            - 0.2 * self.G,
            0, 1
        )

    # -------------------------------
    # Observáveis
    # -------------------------------
    def snapshot(self):
        return {
            "Comunismo": np.mean(self.ideology < -0.5),
            "Social-democracia": np.mean((self.ideology >= -0.5) & (self.ideology < 0)),
            "Capitalismo": np.mean((self.ideology >= 0) & (self.ideology < 0.5)),
            "Libertarianismo": np.mean(self.ideology >= 0.5),
            "Satisfação": self.S,
            "Mobilidade": self.mobility(),
            "Gini": self.G
        }
