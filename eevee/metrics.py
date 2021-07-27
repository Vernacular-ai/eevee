from typing import Callable, List, Optional

import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

from eevee.types import SlotLabel


def slot_capture_rate(slots_predicted: List[SlotLabel], expected_slot_value: str) -> float:
    """
    """

    if isinstance(slots_predicted, list) and slots_predicted:
        captured_count = slots_predicted.count(expected_slot_value)
        return captured_count / len(slots_predicted)
    else:
        raise ValueError(f"Expected {slots_predicted = } to be a list of size greater than 0")


def slot_retry_rate(slot_turn_counts: List[Optional[int]], agg_fn: Callable = np.mean) -> float:
    """
    Slot retry rate refers to aggregating on the number of turns a slot requires.

    Let `n` be the number of calls,
    `slot_turn_counts` be number of turns required to handle the particular slot in each call.
    `agg_fn` runs aggregation on `slot_turn_counts` and returns a float.
    """

    if isinstance(slot_turn_counts, list) and slot_turn_counts:
        filtered_turn_counts = list(filter(None, slot_turn_counts))
        return agg_fn(filtered_turn_counts)
    else:
        raise ValueError(f"Expected {slot_turn_counts =} to be a list of size greater than 0")


def slot_mismatch_rate(y_true: List[SlotLabel], y_pred: List[SlotLabel]) -> float:
    """
    As per the definition, slot mismatch rate captures
    ratio of match on types-but-not-values with
    match on types-but-not-values + match on types-and-values
    """

    type_and_value_matched = 0
    type_matched_but_value_didnt = 0

    for y_true_i, y_pred_i in zip(y_true, y_pred):

        if type(y_true_i) == type(y_pred_i) and y_true_i is not None:
            if y_true_i == y_pred_i:
                type_and_value_matched += 1
            else:
                type_matched_but_value_didnt += 1

    if type_matched_but_value_didnt + type_and_value_matched == 0:
        return 0.0
    return (type_matched_but_value_didnt) / (type_matched_but_value_didnt + type_and_value_matched)


def top_k_slot_mismatch_rate(y_true: List[SlotLabel], y_pred: List[List[SlotLabel]], k=1) -> float:
    ...


def slot_fnr(y_true: List[SlotLabel], y_pred: List[SlotLabel]) -> float:
    """
    False negative rate for slot prediction.

    Slot type is handled outside this, so you will have to segregate the slot
    labels based on types beforehand.
    """

    _y_true = [0 if y is None else 1 for y in y_true]
    _y_pred = [0 if y is None else 1 for y in y_pred]

    mat = confusion_matrix(_y_true, _y_pred, labels=[0, 1])

    fn = mat[1, 0]
    tp = mat[1, 1]

    if (fn + tp) == 0:
        return 0
    else:
        return fn / (fn + tp)


def slot_fpr(y_true: List[SlotLabel], y_pred: List[SlotLabel]) -> float:
    """
    False positive rate for slot prediction.

    Slot type is handled outside this, so you will have to segregate the slot
    labels based on types beforehand.

    0 -> 1 is false positive, assuming 0 is negative label. 1 as positive label.
    None -> {} is false positive under our situation.
    """

    _y_true = [0 if y is None else 1 for y in y_true]
    _y_pred = [0 if y is None else 1 for y in y_pred]

    mat = confusion_matrix(_y_true, _y_pred, labels=[0, 1])

    tn, fp, *_ = mat.ravel()

    if (fp + tn) == 0:
        return 0
    else:
        return fp / (fp + tn)


def intent_report(true_labels: pd.DataFrame, pred_labels: pd.DataFrame, output_dict=False):
    """
    Make an intent report from given label dataframes. We only support single
    intent dataframes as of now.

    TODO:
    - Check type of labels (we are not supporting rich labels right now)
    - Handle 'null' labels.
    """
    df = pd.merge(true_labels, pred_labels, on="id", how="inner")

    return classification_report(df["intent_x"], df["intent_y"], output_dict=output_dict)
