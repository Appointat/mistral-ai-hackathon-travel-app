from typing import Any, Optional

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.prompts import TextPrompt
from camel.types import ModelType, RoleType


class AnswerAgent(ChatAgent):
    r"""An agent that aims to generate the two answers (correct and incorrect).
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
            role_name="Answer Agent",
            role_type=RoleType.ASSISTANT,
            meta_dict=None,
            content="You generate the answers (correct and incorrect).",
        )
        super().__init__(system_message, model_type, model_config)

    def run(
        self,
        question: str,
    ) -> str:
        r"""Generate the answers (correct and incorrect) based on the syllabus.

        Args:
            context_text (Union[str, TextPrompt]): The context text to
                generate insights from.
            insights_instruction (Optional[Union[str, TextPrompt]], optional):
                The instruction for generating insights. (default: :obj:`None`)

        Returns:
            str: The generated question.
        """
        self.reset()

        answer_instruction_prompt = TextPrompt("""===== ANSWERS GENRATOR =====
You are an AI assistant specialized in educational content creation. Your task is to generate two different answers for a given question: one correct answer and one incorrect (or partially incorrect) answer. This will help in creating educational materials that can test students' understanding and ability to identify misconceptions.

For the given question, please provide the following:
1. Correct Answer:
   - Provide a clear, concise, and accurate answer to the question.
   - Ensure that all information in this answer is factually correct and directly addresses the question.
2. Incorrect or Partially Incorrect Answer:
   - Create an answer that contains one or more errors or misconceptions.
   - This answer should be plausible enough that it might trick a student who doesn't fully understand the topic.
   - The error(s) can be factual mistakes, logical fallacies, or misapplications of concepts.
3. Explanation of the Error:
   - Briefly explain why the incorrect answer is wrong or partially wrong.
   - Identify the specific mistake(s) or misconception(s) present in the incorrect answer.
   - If applicable, explain how this error relates to common misunderstandings of the topic.
Guidelines:
- Both answers should be of similar length and detail to avoid giving away which is correct based on format alone.
- The incorrect answer should not be obviously wrong; it should require careful consideration to identify the error.
- Ensure that the incorrect answer doesn't inadvertently reinforce false information. The error should be clear once explained.
- Tailor the complexity of both answers to the expected knowledge level of the students.
- If the question allows for multiple correct approaches or perspectives, acknowledge this in your correct answer.
""")

        question_prompt = TextPrompt("===== QUESTION =====\n{question}\n\n")

        answer_template_prompt = "===== ANSWER TEMPLATE =====\nCorrect Answer:<BLANK>\nWrong Answer:<BLANK>\nExplanation of the Error:<BLANK>\n"
        answer_generation_prompt = answer_instruction_prompt + question_prompt
        answer_generation = answer_generation_prompt.format(question=question)
        answer_generation += answer_template_prompt

        mind_map_generation_msg = BaseMessage.make_user_message(
            role_name="Answer Agent", content=answer_generation
        )

        response = self.step(input_message=mind_map_generation_msg)

        return response.msg.content
