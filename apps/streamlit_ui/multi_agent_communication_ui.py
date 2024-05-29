import json, queue, re

import streamlit as st
from PIL import Image

from camel.agents.deductive_reasoner_agent import DeductiveReasonerAgent
from camel.configs import ChatGPTConfig, FunctionCallingConfig
from camel.functions import MATH_FUNCS, SEARCH_FUNCS
from camel.societies import RolePlaying
from camel.types import ModelType, TaskType

from agents.insight_agent import InsightAgent
from agents.multi_agent import MultiAgent
from agents.report_agent import ReportAgent
from apps.streamlit_ui.read_input_messages import read_input_messages


def main(
    model_type=ModelType.MISTRAL_7B,
    task_prompt=None,
    context_text=None,
    num_roles=None,
    search_enabled=False,
) -> None:
    # Model and agent initialization
    model_type = ModelType.GPT_4O
    model_type_json = ModelType.GPT_4O
    model_config = ChatGPTConfig(max_tokens=4096, temperature=0)

    multi_agent = MultiAgent(
        model_type=model_type_json,
        model_config=model_config,
    )
    insight_agent = InsightAgent(model_type=model_type_json, model_config=model_config)
    deductive_reasoner_agent = DeductiveReasonerAgent(
        model_type=model_type_json, model_config=model_config
    )
    report_agent = ReportAgent(model_type=model_type_json, model_config=model_config)

    # Generate role with descriptions
    role_names = None
    role_descriptions_dict = multi_agent.generate_role_with_description(
        task_prompt=task_prompt,
        num_roles=num_roles,
        role_names=role_names,
        function_list=[],
    )

    # Split the original task into subtasks
    num_subtasks=None
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
    subtasks_image = Image.open(subtasks_image_path)
    st.image(
        subtasks_image, caption='Workflows of Task.',
        use_column_width=True
    )

    # Get the list of subtasks
    subtasks = [
        subtasks_with_dependencies_dict[key]["description"]
        for key in sorted(subtasks_with_dependencies_dict.keys())
    ]
    send_subtasks_to_ui(subtasks=subtasks)

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
        subtask for pipeline in parallel_subtask_pipelines for subtask in pipeline
    ):
        # Get the description of the subtask
        subtask = subtasks_with_dependencies_dict[subtask_id]["description"]
        subtask_labels = subtasks_with_dependencies_dict[subtask_id]["input_tags"]
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
        role_compatibility_scores_dict = multi_agent.evaluate_role_compatibility(
            subtask, role_descriptions_dict
        )

        # Get the top two roles with the highest compatibility scores
        ai_assistant_role = max(
            role_compatibility_scores_dict,
            key=lambda role: role_compatibility_scores_dict[role]["score_assistant"],
        )
        ai_user_role = max(
            role_compatibility_scores_dict,
            key=lambda role: role_compatibility_scores_dict[role]["score_user"],
        )

        ai_assistant_description = role_descriptions_dict[ai_assistant_role]
        ai_user_description = role_descriptions_dict[ai_user_role]

        output_msg = ""
        with st.expander(f"# 🌲 {subtask_id}:\n\n{subtask}"):
            send_two_role_descriptions_to_ui(
                ai_assistant_role=ai_assistant_role,
                ai_user_role=ai_user_role,
                ai_assistant_description=ai_assistant_description,
                ai_user_description=ai_user_description,
            )

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

            # Assistant model config
            assistant_config = FunctionCallingConfig.from_openai_function_list(
                function_list=function_list,
                kwargs=dict(temperature=0.7),
            )

            # User model config
            user_config = FunctionCallingConfig.from_openai_function_list(
                function_list=function_list,
                kwargs=dict(temperature=0.7),
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
                task_type=TaskType.ROLE_DESCRIPTION,
                task_prompt=subtask_content,
                with_task_specify=False,
                extend_sys_msg_meta_dicts=sys_msg_meta_dicts,
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
                    try:
                        # Read the human messages from the file
                        read_input_messages()
                    except FileNotFoundError:
                        pass

                    if 'human_messages' not in st.session_state:
                        st.session_state['human_messages'] = queue.Queue()
                    human_message = ""
                    while len(st.session_state['human_messages']) > 0:
                        human_message += st.session_state['human_messages'].pop(0) + "\n\n"

                    if human_message != "":
                        send_message_to_ui(role="user", role_name="Human", message=human_message)
                        from prompts.human_in_loop_prompts import HUMAN_AS_ASSISTANT_PROMPT
                        input_msg.content += HUMAN_AS_ASSISTANT_PROMPT.format(
                            human_message=human_message
                        )

                    assistant_response, user_response = role_play_session.step(
                        input_msg
                    )
                except Exception as e:
                    # output a warning message and continue
                    st.warning(f"Warning: {e}")
                    continue

                if assistant_response.terminated:
                    st.warning(
                        f"{ai_assistant_role} terminated. Reason: "
                        f"{assistant_response.info['termination_reasons']}."
                    )
                    break
                if user_response.terminated:
                    st.warning(
                        f"{ai_user_role} terminated. Reason: "
                        f"{user_response.info['termination_reasons']}."
                    )
                    break

                input_msg = assistant_response.msg

                assistant_msg_record += (
                    f"--- [{n}] ---\n"
                    + assistant_response.msg.content.replace("Next request.", "").strip(
                        "\n"
                    )
                    + "\n"
                )

                send_message_to_ui(
                    role="user",
                    role_name=ai_user_role,
                    message=user_response.msg.content,
                )
                send_message_to_ui(
                    role="assistant",
                    role_name=ai_assistant_role,
                    message=assistant_response.msg.content,
                )

                # Avoid the repetition
                assistant_response.msg.content += (
                    "\n\n" + "To avoid repetitive conversations, " +
                    "please make your next instruction different " +
                    "from the previous one."
                )

                # reproduced_assistant_msg_with_category = (
                #     multi_agent.transform_dialogue_into_text(
                #         user_name=ai_user_role,
                #         assistant_name=ai_assistant_role,
                #         task_prompt=subtask,
                #         user_conversation=user_response.msg.content,
                #         assistant_conversation=assistant_response.msg.content,
                #     )
                # )
                # reproduced_assistant_msg = reproduced_assistant_msg_with_category[
                #     "text"
                # ]
                # output_msg += reproduced_assistant_msg + "\n"

                if (
                    "CAMEL_TASK_DONE" in user_response.msg.content
                    or "CAMEL_TASK_DONE" in assistant_response.msg.content
                    or n >= chat_turn_limit
                ):
                    from prompts.post_finalization_prompts import (
                        ASSISTANT_PREPOST_RUN_PROMPT,
                        ASSISTANT_FINALIZATION_PROMPT,
                    )
                    assistant_response.msg.content += ASSISTANT_PREPOST_RUN_PROMPT
                    _input_msg = assistant_response.msg
                    assistant_response, user_response = role_play_session.step(_input_msg)
                    for _ in range(2):
                        assistant_response.msg.content += str(ASSISTANT_FINALIZATION_PROMPT)
                        _input_msg = assistant_response.msg
                        assistant_response, user_response = role_play_session.step(_input_msg)

                    output_msg = assistant_response.msg.content.replace('CAMEL_TASK_DONE', '')
                    subtask_output_msgs.append(output_msg)

                    # send_message_to_ui(
                    #     role="user",
                    #     role_name=ai_user_role,
                    #     message=user_response.msg.content.replace('CAMEL_TASK_DONE', ''),
                    # )
                    # send_message_to_ui(
                    #     role="assistant",
                    #     role_name=ai_assistant_role,
                    #     message=assistant_response.msg.content.replace('CAMEL_TASK_DONE', ''),
                    # )

                    break

            insights_instruction = (
                "The CONTEXT TEXT is the steps to resolve "
                + "the TASK. The INSIGHTs should come solely"
                + "from the assistant's solutions and actions."
            )
            insights = insight_agent.run(
                context_text=assistant_msg_record,
                insights_instruction=insights_instruction,
            )

            # Update the environment record
            for insight in insights.values():
                if insight["entity_recognition"] is None:
                    continue
                labels_key = tuple(insight["entity_recognition"])
                environment_record[labels_key] = insight

        with st.expander(f"# 📝 {subtask_id}:\n\nSummary"):
            send_summary_to_ui(output_msg=output_msg)
    
    all_output_msgs = "\n".join(subtask_output_msgs)
    with st.expander("# 📝 Final Summary"):
        report_context_text = report_agent.run(
            context_text=all_output_msgs,
            task_prompt=task_prompt,
        )
        send_summary_to_ui(output_msg=report_context_text)


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

    _, _, _, labels_retrieved_sets = multi_agent.get_retrieval_index_from_environment(
        labels_sets=labels_sets, target_labels=target_labels
    )

    # Retrive the necessaray insights from the environment
    retrieved_insights = [
        environment_record[tuple(label_set)] for label_set in labels_retrieved_sets
    ]

    insights_none_pre_subtask = insight_agent.run(context_text=context_text)
    insights_for_subtask = (
        "\n====== CURRENT STATE =====\n"
        "The snapshot and the context of the TASK is presentd in "
        "the following insights which is close related to The "
        '"Insctruction" and the "Input":\n'
        + f"{json.dumps(insights_none_pre_subtask, indent=4)}\n"
    )

    insights_for_subtask += "\n".join(
        [json.dumps(insight, indent=4) for insight in retrieved_insights]
    )

    return insights_for_subtask


def send_role_descriptions_to_ui(role_descriptions_dict={}):
    num_roles = len(role_descriptions_dict)
    with st.expander(f"Build {num_roles} AI agents:"):
        for role, role_description in role_descriptions_dict.items():
            st.markdown(f"{role}:")
            st.markdown(role_description)

    # Save the role descriptions
    with open("downloads/CAMEL_multi_agent_output.md", "a") as file:
        # Continue to write
        for role, role_description in role_descriptions_dict.items():
            file.write(f"Buid {num_roles} AI agents:\n")
            file.write(f"{role}:\n{role_description}\n")
        file.text("\n")


def send_two_role_descriptions_to_ui(
    ai_assistant_role="",
    ai_user_role="",
    ai_assistant_description="",
    ai_user_description="",
):
    st.markdown(f"{ai_assistant_role}:")
    st.markdown(ai_assistant_description)
    st.markdown(f"{ai_user_role}:")
    st.markdown(ai_user_description)

    # Save the role descriptions
    with open("downloads/CAMEL_multi_agent_output.md", "a") as file:
        file.write(f"{ai_assistant_role}:\n{ai_assistant_description}\n")
        file.write(f"{ai_user_role}:\n{ai_user_description}\n")
        file.write("\n")


def send_subtasks_to_ui(subtasks=[]):
    with st.expander("# 🦊 Subtasks:"):
        for i, subtask in enumerate(subtasks):
            st.markdown(f"Subtask {i + 1}:")
            st.markdown(subtask)

    # Save the subtasks
    with open("downloads/CAMEL_multi_agent_output.md", "a") as file:
        for i, subtask in enumerate(subtasks):
            file.write(f"Subtask {i + 1}:\n")
            file.write(subtask + "\n")
        file.write("\n")


def send_summary_to_ui(output_msg=""):
    st.write(output_msg.replace("\n", "\n\n"))

    # Save the output message
    with open("downloads/CAMEL_multi_agent_summary.md", "a") as file:
        file.write(output_msg + "\n\n")


def send_message_to_ui(role="", role_name="", message=""):
    if role not in ["user", "assistant"]:
        raise ValueError("The role should be one of 'user' or 'assistant'.")

    message = message.replace('Next request.', '').replace('CAMEL_TASK_DONE', 'TASK_DONE').replace('None', '')
    if role == "user":
        matches = re.findall(
            r"(Instruction|Input):[ \n]+(.+?)(?=\n[A-Z]|$)",
            message,
            re.DOTALL
        )
    else:
        matches = re.findall(
            r"(Thought|Action|Feedback):[ \n]+(.+?)(?=\n[A-Z]|$)",
            message,
            re.DOTALL
        )
    matched_messages = {
        match[0].lower(): match[1].strip().replace('\n', '\n\n')
        for match in matches
    }
    printed_message = ""
    for key in matched_messages:
        printed_message += f"{(matched_messages[key])}\n\n"

    with st.chat_message(role):
        st.markdown(
            f"AI {role}: {role_name}\n\n{printed_message}"
        )

    # Save the messages
    with open("downloads/CAMEL_multi_agent_output.md", "a") as file:
        file.write(f"AI {role}: {role_name}\n\n")
        file.write(message.replace("Next request.", "") + "\n")
        file.write("\n")
