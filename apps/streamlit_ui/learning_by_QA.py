import json
import re

from camel.agents.deductive_reasoner_agent import DeductiveReasonerAgent
from camel.configs import ChatGPTConfig, FunctionCallingConfig
from camel.functions import MATH_FUNCS, SEARCH_FUNCS
from camel.societies import RolePlaying
from camel.types import ModelType, TaskType
from colorama import Fore, init
from imgcat import imgcat

from agents.insight_agent import InsightAgent
from agents.multi_agent import MultiAgent
from agents.report_agent import ReportAgent

# Initialize Colorama
init(autoreset=True)


def print_colored_message(message, color=Fore.WHITE):
    print(color + message)
    print(Fore.WHITE)


def learning_by_QA(
    model_type=ModelType.MISTRAL_7B,
    task_prompt=None,
    context_text=None,
    num_roles=None,
    search_enabled=False,
    output_language="en",
) -> None:
    # task_prompt = """
    # Doing continually the QA role-playing between the student and the tutor to learn the Deep Learning concepts. The user will guide the student through the test, provide explanations, and evaluate the student's performance. The test consists of multiple-choice questions and practical exercises.
    # """
    #     task_prompt = """
    # Suppose there is a criteria of the assessment that evaluates students' learning outcomes. It can assess based on the student's latest responses, building upon existing achievements. For example, if a student answers a question correctly about knowledge A&B, it indicates that their mastery of A and B (possibly represented as a complex vector) has **improved**, which should be noted down. Conversely, if they answer incorrectly, their mastery has declined.
    # Therefore, the TASK is to create a set of detailed evaluation criteria to promote education in Deep Learning, by the similar method in the provided example.
    # """
    task_prompt = """
Compose a very challenging system design problem for deep learning, and then solve this difficult issue step by step.
"""

    # Model and agent initialization
    model_type = ModelType.GPT_4O
    model_type_json = ModelType.GPT_4O
    model_config_json = ChatGPTConfig(max_tokens=4096, temperature=0.7)

    multi_agent = MultiAgent(
        model_type=model_type_json,
        model_config=model_config_json,
    )
    insight_agent = InsightAgent(
        model_type=model_type_json, model_config=model_config_json
    )
    deductive_reasoner_agent = DeductiveReasonerAgent(
        model_type=model_type_json, model_config=model_config_json
    )
    report_agent = ReportAgent(
        model_type=model_type_json, model_config=model_config_json
    )

    # Generate role with descriptions
    role_names = None
    role_descriptions_dict = multi_agent.generate_role_with_description(
        task_prompt=task_prompt,
        num_roles=num_roles,
        role_names=role_names,
        function_list=[],
    )
    print_colored_message(
        f" 🦊 The role descriptions:\n{json.dumps(role_descriptions_dict, indent=4)}",
        Fore.GREEN,
    )

    # Split the original task into subtasks
    num_subtasks = None
    subtasks_with_dependencies_dict = multi_agent.split_tasks(
        task_prompt=task_prompt,
        role_descriptions_dict=role_descriptions_dict,
        num_subtasks=num_subtasks,
        context_text=context_text,
    )

    # Draw the graph of the subtasks
    oriented_graph = {}
    subtasks_image_path = "apps/streamlit_ui/task_dependency_graph.png"
    for subtask_idx, details in subtasks_with_dependencies_dict.items():
        deps = details["dependencies"]
        oriented_graph[subtask_idx] = deps
    multi_agent.draw_subtasks_graph(
        oriented_graph=oriented_graph,
        graph_file_path=subtasks_image_path,
    )

    # subtasks_image = Image.open(subtasks_image_path)
    print_colored_message("Displaying workflow of task image.", Fore.CYAN)
    imgcat(open(subtasks_image_path, "rb").read())

    # Get the list of subtasks
    subtasks = [
        subtasks_with_dependencies_dict[key]["description"]
        for key in sorted(subtasks_with_dependencies_dict.keys())
    ]
    print_colored_message(" 🦊 The subtasks list:", Fore.GREEN)
    for idx, subtask in enumerate(subtasks):
        print_colored_message(f"{idx + 1}. {subtask}", Fore.GREEN)

    # Calculate the execution order of the subtasks, based on their
    # dependencies
    parallel_subtask_pipelines = multi_agent.get_task_execution_order(
        subtasks_with_dependencies_dict
    )

    # Initialize the environment record
    environment_record = {}  # the cache of the system
    if context_text is not None:
        insights = insight_agent.run(context_text=context_text)
        for insight in insights.values():
            if insight["entity_recognition"] is None:
                continue
            tags = tuple(insight["entity_recognition"])
            environment_record[tags] = insight

    # Resolve the subtasks in sequence of the pipelines
    subtask_output_msgs = []
    for subtask_id in (
        subtask
        for pipeline in parallel_subtask_pipelines
        for subtask in pipeline
    ):
        # Get the description of the subtask
        subtask = subtasks_with_dependencies_dict[subtask_id]["description"]
        subtask_labels = subtasks_with_dependencies_dict[subtask_id][
            "input_tags"
        ]
        # Get the insights from the environment for the subtask
        insights_for_subtask = get_insights_from_environment(
            subtask_id,
            subtask,
            subtask_labels,
            environment_record,
            deductive_reasoner_agent,
            multi_agent,
            insight_agent,
            context_text,
        )

        # Get the role with the highest compatibility score
        role_compatibility_scores_dict = (
            multi_agent.evaluate_role_compatibility(
                subtask, role_descriptions_dict
            )
        )

        # Get the top two roles with the highest compatibility scores
        ai_assistant_role = max(
            role_compatibility_scores_dict,
            key=lambda role: role_compatibility_scores_dict[role][
                "score_assistant"
            ],
        )
        ai_user_role = max(
            role_compatibility_scores_dict,
            key=lambda role: role_compatibility_scores_dict[role]["score_user"],
        )

        ai_assistant_description = role_descriptions_dict[ai_assistant_role]
        from agents.roles_profile.tutor import (
            ROLE_PROFILE_FOR_EVALUATION_CRITERIA,
        )

        ai_user_description = (
            role_descriptions_dict[ai_user_role]
            + "Your next instruction and your next question asked by you should based on the result of the criteria evaluation.\n"
            + ROLE_PROFILE_FOR_EVALUATION_CRITERIA.format()
        )

        output_msg = ""
        print_colored_message(f"🌲 {subtask_id}: {subtask}", Fore.GREEN)

        subtask_content = (
            "- Description of TASK:\n"
            + subtasks_with_dependencies_dict[subtask_id]["description"]
            + "\n- Input of TASK:\n"
            + subtasks_with_dependencies_dict[subtask_id]["input_content"]
            + "\n- Output Standard for the completion of TASK:\n"
            + subtasks_with_dependencies_dict[subtask_id]["output_standard"]
        )

        # You can use the following code to play the role-playing game
        if search_enabled:
            sys_msg_meta_dicts = [
                dict(
                    assistant_role=ai_assistant_role,
                    user_role=ai_user_role,
                    assistant_description=ai_assistant_description
                    + "\nAnd I have the ability to call the function "
                    + "search_google_and_summarize.\n"
                    + insights_for_subtask,
                    user_description=ai_user_description + "\n" + "",
                )
                for _ in range(2)
            ]  # System message meta data dicts
        else:
            sys_msg_meta_dicts = [
                dict(
                    assistant_role=ai_assistant_role,
                    user_role=ai_user_role,
                    assistant_description=ai_assistant_description
                    + "\n"
                    + insights_for_subtask,
                    user_description=ai_user_description + "\n" + "",
                )
                for _ in range(2)
            ]  # System message meta data dicts

        if search_enabled:
            function_list = [*MATH_FUNCS, *SEARCH_FUNCS]
        else:
            function_list = [*MATH_FUNCS]

        assistant_config = FunctionCallingConfig.from_openai_function_list(
            function_list=function_list,
            kwargs=dict(
                max_tokens=4096,
                temperature=1,
                n=3,
                presence_penalty=1.0,
                frequency_penalty=1.0,
            ),
        )

        user_config = FunctionCallingConfig.from_openai_function_list(
            function_list=function_list,
            kwargs=dict(
                max_tokens=4096,
                temperature=1,
                n=2,
                presence_penalty=1.0,
                frequency_penalty=1.0,
            ),
        )

        assistant_agent_kwargs = dict(
            model_type=model_type,
            model_config=assistant_config,
            function_list=function_list,
        )

        user_agent_kwargs = dict(
            model_type=model_type,
            model_config=user_config,
            # function_list=function_list,
        )

        # Initialize the role-playing session
        role_play_session = RolePlaying(
            assistant_role_name=ai_assistant_role,
            assistant_agent_kwargs=assistant_agent_kwargs,
            user_role_name=ai_user_role,
            user_agent_kwargs=user_agent_kwargs,
            critic_role_name="Human",
            task_type=TaskType.ROLE_DESCRIPTION,
            task_prompt=subtask_content,
            with_task_specify=False,
            with_critic_in_the_loop=True,
            extend_sys_msg_meta_dicts=sys_msg_meta_dicts,
            output_language=output_language,
        )

        assistant_msg_record = (
            "The TASK of the context text is:\n"
            f"{subtask}\n"
            "The solutions and the actions to "
            "the TASK:\n"
        )

        # Start the role-playing to complete the subtask
        chat_turn_limit, n = 30, 0
        input_msg = role_play_session.init_chat()
        while n < chat_turn_limit:
            n += 1
            try:
                assistant_response, user_response = role_play_session.step(
                    input_msg
                )
            except Exception as e:
                print_colored_message(f"Warning: {e}", Fore.YELLOW)
                continue

            if assistant_response.terminated:
                print_colored_message(
                    f"{ai_assistant_role} terminated. "
                    f"Reason: {assistant_response.info['termination_reasons']}.",
                    Fore.RED,
                )
                break
            if user_response.terminated:
                print_colored_message(
                    f"{ai_user_role} terminated. "
                    f"Reason: {user_response.info['termination_reasons']}.",
                    Fore.RED,
                )
                break

            input_msg = assistant_response.msg

            assistant_msg_record += (
                f"--- [{n}] ---\n"
                + assistant_response.msg.content.replace(
                    "Next request.", ""
                ).strip("\n")
                + "\n"
            )

            print_agent_message(
                role="user",
                role_name=ai_user_role,
                message=user_response.msg.content,
            )
            print_agent_message(
                role="assistant",
                role_name=ai_assistant_role,
                message=assistant_response.msg.content,
            )

            assistant_response.msg.content += (
                "\n\n"
                + "To avoid repetitive conversations, "
                + "please make your next instruction different "
                + "from the previous one."
            )
            if (
                "CAMEL_TASK_DONE" in user_response.msg.content
                or "CAMEL_TASK_DONE" in assistant_response.msg.content
                or n >= chat_turn_limit
            ):
                break

            print_colored_message("===" * 20 + "\n", Fore.RESET)

        print_colored_message("===" * 20 + "\n", Fore.RESET)

        insights_instruction = (
            "The CONTEXT TEXT is the steps to resolve "
            + "the TASK. The INSIGHTs should come solely"
            + "from the assistant's solutions and actions."
        )
        insights = insight_agent.run(
            context_text=assistant_msg_record,
            insights_instruction=insights_instruction,
        )

        for insight in insights.values():
            if insight["entity_recognition"] is None:
                continue
            labels_key = tuple(insight["entity_recognition"])
            environment_record[labels_key] = insight

        print_colored_message(output_msg, Fore.YELLOW)


def get_insights_from_environment(
    subtask_id,
    subtask,
    subtask_labels,
    environment_record,
    deductive_reasoner_agent,
    multi_agent,
    insight_agent,
    context_text,
):
    # React to the environment, and get the insights from it
    conditions_and_quality_json = (
        deductive_reasoner_agent.deduce_conditions_and_quality(
            starting_state="None", target_state=subtask
        )
    )

    target_labels = list(
        set(conditions_and_quality_json["labels"]) | set(subtask_labels)
    )

    labels_sets = [list(labels_set) for labels_set in environment_record.keys()]

    _, _, _, labels_retrieved_sets = (
        multi_agent.get_retrieval_index_from_environment(
            labels_sets=labels_sets, target_labels=target_labels
        )
    )

    # Retrive the necessaray insights from the environment
    retrieved_insights = [
        environment_record[tuple(label_set)]
        for label_set in labels_retrieved_sets
    ]

    insights_none_pre_subtask = insight_agent.run(context_text=context_text)
    insights_for_subtask = (
        "\n====== CURRENT STATE =====\n"
        "The snapshot and the context of the TASK is presented in "
        "the following insights which is closely related to the "
        '"Instruction" and the "Input":\n'
        + f"{json.dumps(insights_none_pre_subtask, indent=4)}\n"
    )

    insights_for_subtask += "\n".join(
        [json.dumps(insight, indent=4) for insight in retrieved_insights]
    )

    return insights_for_subtask


def print_agent_message(role="", role_name="", message=""):
    if role not in ["user", "assistant"]:
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
        r"Instruction:\s*",
        r"Input:\s*",
    ]
    for pattern in patterns:
        printed_message = re.sub(pattern, "", printed_message)

    print_colored_message(
        f"{role_name} says:\n{printed_message}",
        Fore.CYAN if role == "user" else Fore.YELLOW,
    )
