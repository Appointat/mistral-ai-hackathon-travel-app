# from apps.streamlit_ui.multi_agents import main
from apps.streamlit_ui.learning_by_QA import learning_by_QA

with open("examples/task_prompt_dl_learning.txt", "r") as file:
    task_prompt = file.read()
with open("examples/context_content_dl_learning.txt", "r") as file:
    context_text = file.read()
num_roles = 5  # num_roles could be null or a number
search_enabled = False
output_language = "Chinese"  # English is recommended for better performance

learning_by_QA(
    task_prompt=task_prompt,
    context_text=context_text,
    num_roles=num_roles,
    search_enabled=search_enabled,
    output_language=output_language,
)
