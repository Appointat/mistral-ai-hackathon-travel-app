from camel.prompts import TextPrompt


HUMAN_AS_ASSISTANT_PROMPT = TextPrompt(
    """
Thought:
    {human_message}
Action:
    I am not satisfied with your instruction. Can you instruct me to hlep with my thought?
Feedback:
    I need one instruction to help with my thought. Please give priority to this thought.
"""
)