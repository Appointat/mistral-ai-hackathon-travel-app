from typing import Any, Dict, Optional, Union

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.prompts import TextPrompt
from camel.types import ModelType, RoleType
from utils.structure_output import extract_json_from_string


class ReportAgent(ChatAgent):
    r"""An agent that aims to generate a report to the task.
    Args:
        model_type (ModelType, optional): The type of model to use for the
            agent. (default: :obj:`ModelType.GPT_3_5_TURBO`)
        model_config (Any, optional): The configuration for the model.
            (default: :obj:`None`)
    """

    def __init__(
        self,
        model_type: ModelType = ModelType.GPT_3_5_TURBO,
        model_config: Optional[Any] = None,
    ) -> None:
        system_message = BaseMessage(
            role_name="Report Agent",
            role_type=RoleType.ASSISTANT,
            meta_dict=None,
            content="You generate a report from a provided text.",
        )
        super().__init__(system_message, model_type, model_config)

    def run(
        self,
        context_text: Union[str, TextPrompt],
        task_prompt: Union[str, TextPrompt]
    ) -> Dict[str, Dict[str, Any]]:
        r"""Generate role names based on the input task prompt.

        Args:
            context_text (Union[str, TextPrompt]): The context text to
                generate insights from.
            task_prompt (Union[str, TextPrompt]): The task to solve.

        Returns:
            Dict[str, Dict[str, Any]]: The generated insights from the context
                text.
        """
        self.reset()

        report_instruction_prompt = TextPrompt(
            "Based on the CONTEXT TEXT "
            + "provided, generate a comprehensive and detailed report that "
            + "can complete the TASK (Visual tables (MARKDOWN format) or lists (MARKDOWN format) are strongly recommended to enhance the clarity of the solution) "
            + "and use the \"ANSWER TEMPLATE\" to "
            + "structure your response.\nYour answer MUST strictly "
            + "adhere to the structure of ANSWER TEMPLATE, ONLY "
            + "fill in  the BLANKs, and DO NOT alter or modify any "
            + "other part of the template.\n"
        )
        context_text_prompt = TextPrompt(
            "===== CONTEXT TEXT =====\n{context_text}\n\n"
        )
        task_prompt = TextPrompt("===== TASK =====\n{task_prompt}\n\n")
        answer_template_prompt = (
            "===== ANSWER TEMPLATE =====\n"
            "<BLANK_IN_MARKDOWN>"
        )
        insights_generation_prompt = (
            report_instruction_prompt + context_text_prompt
        )
        insights_generation = insights_generation_prompt.format(
            context_text=context_text,
            task_prompt=task_prompt,
        )
        insights_generation += answer_template_prompt

        insights_generation_msg = BaseMessage.make_user_message(
            role_name="Report Agent", content=insights_generation
        )

        response = self.step(input_message=insights_generation_msg)

        if response.terminated:
            raise RuntimeError(
                "Insights generation failed. Error:\n" + f"{response.info}"
            )
        msg = response.msg  # type: BaseMessage

        return msg.content
