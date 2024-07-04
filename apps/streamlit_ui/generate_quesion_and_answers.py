from camel.configs import ChatGPTConfig
from camel.types import ModelType

from agents.answer_agent import AnswerAgent
from agents.question_agent import QuestionAgent


async def async_main(content: str):
    model_type = ModelType.GPT_4O
    model_config = ChatGPTConfig(
        max_tokens=4096,
        temperature=0.7,
    )

    question_agent = QuestionAgent(
        model_type=model_type, model_config=model_config
    )
    answer_agent = AnswerAgent(model_type=model_type, model_config=model_config)

    question = question_agent.run()
    yield question

    answer = answer_agent.run(question=question)
    yield answer
