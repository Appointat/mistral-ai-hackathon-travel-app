from camel.prompts import TextPrompt


HUMAN_AS_ASSISTANT_PROMPT = TextPrompt(
    """
Thought:
    {human_message}
Action:
    Can you instruct me to hlep with my thought?
Feedback:
    I need one instruction to help with my thought.
"""
)