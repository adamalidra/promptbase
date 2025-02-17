# This is a very naive guidance program for doing zero shot multiple choice questions
# with chain-of-thought prompting
# It is not what generated the reported results

import logging
import sys

from textwrap import dedent
from typing import Any, Dict

import guidance
from guidance import gen, select, system, user, assistant


_logger = logging.getLogger(__file__)
_logger.setLevel(logging.INFO)
_logger.addHandler(logging.StreamHandler(stream=sys.stdout))


@guidance
def zero_shot_cot_multiple_choice(
    lm: guidance.models.Chat, question: str, choices: list[str]
):
    # Some general instruction to the model
    with system():
        lm += dedent(
            """Answer the following multiple choice **Question**.
            First, think step by step and write an **Explanation** for reasoning through the question.
            Then, when prompted by the user for a **Final Answer**, analyze your explanation and write just the number of the correct answer.
            Do not say the final answer until the user asks for it."""
        )

    with user():
        lm += "**Question**\n"
        lm += question + "\n"
        for i, choice in enumerate(choices):
            lm += f"{i} : {choice}" + "\n"
        lm += "**Explanation**"

    with assistant():
        lm += gen(name=f"explanation")

    response_choices = [str(i) for i in range(len(choices))]
    with user():
        lm += f"**Final Answer**"

    with assistant():
        lm += select(response_choices, name="string_choice")

    return lm


def guidance_generation(
    lm: guidance.models.Chat, input: Dict[str, Any]
) -> Dict[str, Any]:
    _logger.info("Starting guidance_generation")
    result = lm + zero_shot_cot_multiple_choice(
        question=input["question"], choices=input["choices"]
    )

    result = dict(zeroshot_choice=int(result["string_choice"]))
    return result
