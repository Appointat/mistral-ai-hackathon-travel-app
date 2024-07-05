# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========
from camel.configs import ChatGPTConfig
from camel.societies import RolePlaying
from camel.types import ModelType
from colorama import Fore

from agents.mind_map_agent import MindMapAgent
from prompts.lesson_plan_prompts import LESSON_PLAN_PROMPT as LessonPlan


async def async_main(task_prompt: str, model_type=None):
    model_type = ModelType.GPT_4_TURBO

    task_prompt = (
        LessonPlan + "\n===== CONTENT OF ARTICEL =====\n" + task_prompt
    )

    agent_kwargs = {
        role: dict(
            model_type=model_type,
            model_config=ChatGPTConfig(
                max_tokens=4096,
                temperature=0.7,
            ),
            function_list=[],
        )
        for role in ["assistant", "user"]
    }

    role_play_session = RolePlaying(
        assistant_role_name="AI Assistant",
        assistant_agent_kwargs=agent_kwargs["assistant"],
        user_role_name="AI User",
        user_agent_kwargs=agent_kwargs["user"],
        task_prompt=task_prompt,
        with_task_specify=False,
        output_language="English",
    )

    print(Fore.RED + f"Final task prompt:\n{role_play_session.task_prompt}\n")

    chat_turn_limit, n = 50, 0
    input_msg = role_play_session.init_chat()
    while n < chat_turn_limit:
        n += 1
        assistant_response, user_response = role_play_session.step(input_msg)

        if assistant_response.terminated:
            print(
                Fore.GREEN
                + (
                    "AI Assistant terminated. Reason: "
                    f"{assistant_response.info['termination_reasons']}."
                )
            )
            break
        if user_response.terminated:
            print(
                Fore.GREEN
                + (
                    "AI User terminated. "
                    f"Reason: {user_response.info['termination_reasons']}."
                )
            )
            break

        async for message in yield_message(
            "user", "AI User", user_response.msg.content + "\n"
        ):
            yield message
        async for message in yield_message(
            "assistant", "AI Assistant", assistant_response.msg.content + "\n"
        ):
            yield message

        if (
            "CAMEL_TASK_DONE" in user_response.msg.content
            or "CAMEL_TASK_DONE" in assistant_response.msg.content
        ):
            break

        input_msg = assistant_response.msg

    # Generate a mind map in HTML/CSS based on the chat history
    chat_history = role_play_session.assistant_agent.memory.retrieve()
    mind_map_agent = MindMapAgent(
        model_type=model_type,
        model_config=ChatGPTConfig(max_tokens=4096, temperature=0.7),
    )
    mind_map_agent.run(chat_history)


async def yield_message(role: str, role_name: str, message: str):
    import asyncio
    import re

    if role not in ["user", "assistant", "system"]:
        raise ValueError("The role should be one of 'user' or 'assistant'.")

    printed_message = (
        message.replace("Next request.", "")
        .replace("CAMEL_TASK_DONE", "TASK_DONE")
        .replace("None", "")
    )
    patterns = [
        r"Thought:\s*",
        r"Action:\s*",
        r"Feedback:\s*",
        r"Judgement:\s*",
        r"Instruction:\s*",
        r"Input:\s*",
    ]
    for pattern in patterns:
        printed_message = re.sub(pattern, "", printed_message)

    print(Fore.YELLOW + f"{role_name} says:\n{printed_message}\n\n")
    # yield f"{role_name} says:\n{printed_message}"
    if role == "assistant":
        yield f"{printed_message}\n"
    await asyncio.sleep(0.1)
