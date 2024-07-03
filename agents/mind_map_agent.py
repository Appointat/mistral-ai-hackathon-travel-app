from typing import Any, Optional, Union

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.prompts import TextPrompt
from camel.types import ModelType, RoleType


class MindMapAgent(ChatAgent):
    r"""An agent that aims to generate a mind map for the content in CSS.
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
        content: Union[str, TextPrompt],
    ):
        r"""Generate a mind map based on the input content in CSS.

        Args:
            content (Union[str, TextPrompt]): The content to generate a mind
                map from.
        """
        self.reset()

        mind_map_instruction_prompt = TextPrompt(
            "Read this long content and write completed CSS/HTML code to "
            "visually present the complex internal logic of the "
            "conversation in the form of a mind map. Remember that the "
            "complet code can be opened in a browser."
        )
        content_prompt = TextPrompt("===== CONTENT =====\n{content}\n\n")
        answer_template_prompt = (
            "===== ANSWER TEMPLATE =====\n```html\n<HTML_CODE>\n```"
        )
        mind_map_generation_prompt = (
            mind_map_instruction_prompt + content_prompt
        )
        mind_map_generation = mind_map_generation_prompt.format(content=content)
        mind_map_generation += answer_template_prompt

        mind_map_generation_msg = BaseMessage.make_user_message(
            role_name="Logician", content=mind_map_generation
        )

        response = self.step(input_message=mind_map_generation_msg)

        if response.terminated:
            raise RuntimeError(
                "Insights generation failed. Error:\n" + f"{response.info}"
            )
        msg = response.msg  # type: BaseMessage
        print(msg.content)

        # Extract the CSS code from the response
        css_code = msg.content.split("```html\n")[1].split("\n```")[0]

        # Store the CSS code in apps/streamlit_ui/cache/mind_map.html
        with open("apps/streamlit_ui/cache/mind_map.html", "w") as f:
            f.write(css_code)
