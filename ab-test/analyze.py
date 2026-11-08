"""Сравниваем конверсию двух вариантов на учебных данных."""
import numpy as np
from scipy.stats import norm, chisquare

SEED = 2026
N_PER_GROUP = 10_000


def main():
    rng = np.random.default_rng(SEED)
    # Synthetic scenario: baseline conversion 10%, variant 11%.
    control = rng.binomial(1, 0.10, N_PER_GROUP)
    variant = rng.binomial(1, 0.11, N_PER_GROUP)
    x0, x1 = int(control.sum()), int(variant.sum())
    p0, p1 = x0 / len(control), x1 / len(variant)
    diff = p1 - p0
    pooled = (x0 + x1) / (len(control) + len(variant))
    se_test = np.sqrt(pooled * (1 - pooled) * (1 / len(control) + 1 / len(variant)))
    z = diff / se_test
    p_value = 2 * norm.sf(abs(z))
    se_ci = np.sqrt(p0 * (1 - p0) / len(control) + p1 * (1 - p1) / len(variant))
    ci = (diff - 1.96 * se_ci, diff + 1.96 * se_ci)
    # Проверяем, не разъехалось ли распределение по группам.
    observed = np.array([len(control), len(variant)])
    srm_p = chisquare(observed, f_exp=[observed.sum() / 2] * 2).pvalue

    print(f"Control: {x0}/{len(control)} = {p0:.3%}")
    print(f"Variant: {x1}/{len(variant)} = {p1:.3%}")
    print(f"Absolute difference: {diff:.3%}; relative lift: {diff / p0:.2%}")
    print(f"95% CI for absolute difference: [{ci[0]:.3%}, {ci[1]:.3%}]")
    print(f"Two-sided z-test p-value: {p_value:.5f}")
    print(f"SRM chi-square p-value: {srm_p:.5f}")
    print("Statistically significant at 5%" if p_value < .05 else "Not statistically significant at 5%")
    print("Interpret the effect with its interval, practical value, experiment design, and guardrail metrics.")


if __name__ == "__main__":
    main()
