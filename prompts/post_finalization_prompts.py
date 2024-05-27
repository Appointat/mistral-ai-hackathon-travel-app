from camel.prompts import TextPrompt

USER_PREPOST_RUN_PROMPT = TextPrompt(
    """Instructions:
    Your answer MUST strictly adhere to the structure of ANSWER TEMPLATE.
    Before we finish the conversation, we have to finalize the TASK with a report based on all the conversation we had. So that you now shoud extract a coherent solution strategy from this extensive conversation, accounting for the whole conversation and SUGGESTIONS FOR FINALIZATION.

====== SUGGESTIONS FOR FINALIZATION ======
1. Identify Key Information:
- Focus on identifying key information related to task solutions within the conversation, including specific steps, required resources, potential barriers, and pros and cons of the solutions.
2. Knowledge Framework Construction:
- Build a knowledge framework or flowchart based on extracted information to visualize the components of the solution and their interrelations.
3. Use of Technological Tools:
4. Methods/Results Integration:
- If multiple conflicted methods/results are presented in the conversation, consider integrating these methods/results to form a consolidated solution.
5. Solution Documentation/Report:
- Ensure each step of the solution is clearly listed, along with the resources needed and the expected outcomes for each step.
- Visual tables (MARKDOWN format) or lists (MARKDOWN format) are strongly recommended to enhance the clarity of the solution.

====== ANSWER TEMPLATE ======
After a deep thinking and the execution, I have come up with the following solution strategy:
<YOUR_REPORT>
"""
)

ASSISTANT_PREPOST_RUN_PROMPT = TextPrompt(
    """Thought:
Before we finish the conversation, I have to finalize the TASK with a report based on all the conversation we had.

====== SUGGESTIONS FOR FINALIZATION ======
1. Identify Key Information:
- Focus on identifying key information related to task solutions within the conversation, including specific steps, required resources, potential barriers, and pros and cons of the solutions.
2. Knowledge Framework Construction:
- Build a knowledge framework or flowchart based on extracted information to visualize the components of the solution and their interrelations.
3. Use of Technological Tools:
4. Methods/Results Integration:
- If multiple conflicted methods/results are presented in the conversation, consider integrating these methods/results to form a consolidated solution.
5. Solution Documentation/Report:
- Ensure each step of the solution is clearly listed, along with the resources needed and the expected outcomes for each step.
- Visual tables (MARKDOWN format) or lists (MARKDOWN format) are strongly recommended to enhance the clarity of the solution.

Action:
    So that can you now instruct me to extract the coherent solution strategy from this extensive conversation, accounting for the whole conversation and SUGGESTIONS FOR FINALIZATION?

Feedback:
    I need one instruction to extract the coherent solution strategy from this extensive conversation, accounting for the whole conversation and SUGGESTIONS FOR FINALIZATION, as a report in markdown format.
"""
)

USER_FINALIZATION_PROMPT = TextPrompt(
    """Instructions:
    Your answer MUST strictly adhere to the structure of ANSWER TEMPLATE.
Make your report longer and more detailed, and I need you add more details to your report, with a focus on the SUGGESTIONS FOR FINALIZATION.

====== SUGGESTIONS FOR FINALIZATION ======
1. Identify Key Information:
- Focus on identifying key information related to task solutions within the conversation, including specific steps, required resources, potential barriers, and pros and cons of the solutions.
2. Knowledge Framework Construction:
- Build a knowledge framework or flowchart based on extracted information to visualize the components of the solution and their interrelations.
3. Use of Technological Tools:
4. Methods/Results Integration:
- If multiple conflicted methods/results are presented in the conversation, consider integrating these methods/results to form a consolidated solution.
5. Solution Documentation/Report:
- Ensure each step of the solution is clearly listed, along with the resources needed and the expected outcomes for each step.
- Visual aids such as diagrams, tables, or graphs (presented in markdown format) is strongly recommended to enhance the clarity of the solution.

""")

ASSISTANT_FINALIZATION_PROMPT = TextPrompt(
    """Thought:
    I think the report can still be enhanced. Please instruct me to make the report longer and more detailed.

Action:
    Can you instruct me to make the report longer and more detailed?

Feedback:
    I need one instruction to make the report longer and more detailed.
"""
)