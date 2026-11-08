"""Считаем метрики классификатора на учебных данных."""
import numpy as np


def score(y_true, probabilities, threshold):
    pred = probabilities >= threshold
    tp = int(np.sum((y_true == 1) & pred))
    fp = int(np.sum((y_true == 0) & pred))
    tn = int(np.sum((y_true == 0) & ~pred))
    fn = int(np.sum((y_true == 1) & ~pred))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    specificity = tn / (tn + fp) if tn + fp else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / len(y_true)
    balanced_accuracy = (recall + specificity) / 2
    return tp, fp, tn, fn, precision, recall, f1, accuracy, balanced_accuracy


def main():
    rng = np.random.default_rng(123)
    n = 5000
    y = rng.binomial(1, .05, n)  # 5% positive class
    probs = np.where(y == 1, rng.beta(5, 2, n), rng.beta(1.2, 10, n))
    print("threshold TP FP TN FN precision recall F1 accuracy balanced_acc")
    for threshold in (.20, .35, .50, .65, .80):
        result = score(y, probs, threshold)
        tp, fp, tn, fn, precision, recall, f1, accuracy, balanced = result
        print(f"{threshold:9.2f} {tp:4d} {fp:4d} {tn:4d} {fn:4d} "
              f"{precision:9.3f} {recall:6.3f} {f1:5.3f} {accuracy:8.3f} {balanced:12.3f}")


if __name__ == "__main__":
    main()
