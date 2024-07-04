from typing import Any, Optional

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.prompts import TextPrompt
from camel.types import ModelType, RoleType

from prompts.lesson_plan_prompts import (
    MACHINE_LEARNING_ARTICEL_PROMPT as ml_prompt,
)


class QuestionAgent(ChatAgent):
    r"""An agent that aims to generate the question based on the syllabus.
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
            role_name="Question Agent",
            role_type=RoleType.ASSISTANT,
            meta_dict=None,
            content="You generate questions based on a provided syllabus.",
        )
        super().__init__(system_message, model_type, model_config)

    def run(
        self,
    ) -> str:
        r"""Generate the questions based on the syllabus.

        Args:
            context_text (Union[str, TextPrompt]): The context text to
                generate insights from.
            insights_instruction (Optional[Union[str, TextPrompt]], optional):
                The instruction for generating insights. (default: :obj:`None`)

        Returns:
            str: The generated question.
        """
        self.reset()

        question_instruction_prompt = TextPrompt("""===== QUESTION GENRATOR =====
You are an AI assistant specialized in educational content creation. Your task is to generate a set of diverse and thought-provoking questions based on a given syllabus or course outline. These questions should be suitable for assessing student understanding, promoting critical thinking, and encouraging deeper engagement with the course material.
Please follow these guidelines when generating questions:

1. Carefully read and analyze the provided syllabus or course outline.
2. Generate questions that cover all main topics and subtopics mentioned in the syllabus.
3. Create a variety of question types, including but not limited to:
    - Multiple choice questions
    - True/False questions
    - Short answer questions
    - Essay questions
    - Case study or scenario-based questions
4. Ensure that the questions assess different levels of cognitive skills, based on Bloom's Taxonomy:
    - Remember (recall facts and basic concepts)
    - Understand (explain ideas or concepts)
    - Apply (use information in new situations)
    - Analyze (draw connections among ideas)
    - Evaluate (justify a stand or decision)
    - Create (produce new or original work)
5. Include questions that:
    - Test factual knowledge
    - Require critical thinking and analysis
    - Encourage application of concepts to real-world scenarios
    - Promote integration of different topics within the syllabus
6. Tailor the difficulty level of questions to the intended audience (e.g., introductory, intermediate, or advanced students).
7. For each question, provide:
    - The question itself
    - The topic or section of the syllabus it relates to
    - The type of question (e.g., multiple choice, short answer)
    - The cognitive level it assesses (based on Bloom's Taxonomy)
8. If appropriate for the subject matter, include questions that:
9. Compare and contrast different concepts
- Require students to explain processes or procedures
- Ask students to interpret data or graphs
- Prompt discussion of ethical considerations or implications

So please generate only one questions for a given syllabus, ensuring a balanced representation of all major topics.
After generating the questions, review them to ensure they are clear, unambiguous, and directly relevant to the syllabus content.

""")

        syllabus_prompt = TextPrompt("===== SYLLABUS =====\n{ml_prompt}\n\n")

        answer_template_prompt = "===== ANSWER TEMPLATE =====\nQuestion:\n<BLANK>\nTopic:\n<BLANK>\nType:\n<BLANK>\nCognitive Level:\n<BLANK>\n"
        question_generation_prompt = (
            question_instruction_prompt + syllabus_prompt
        )
        question_generation = question_generation_prompt.format(
            ml_prompt=ml_prompt
        )
        question_generation += answer_template_prompt

        mind_map_generation_msg = BaseMessage.make_user_message(
            role_name="Question Agent", content=question_generation
        )

        response = self.step(input_message=mind_map_generation_msg)

        return response.msg.content
