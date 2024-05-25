import json

def extract_json_from_string(input_str: str) -> dict:
    r"""Extract the the first JSON from a string, and returns it as a Python
    dictionary.

    Args:
        string (str): The string to extract JSON from.

    Returns:
        dict: The first JSON object found in the string as a Python dictionary.
    """
    input_str = input_str.replace('\\', '\\\\')  # escaping backslashes first

    in_quotes = False
    in_code_block = False
    escaped = False
    depth = 0
    start_index = -1
    clean_input = []

    i = 0
    while i < len(input_str):
        char = input_str[i]

        # Check for code block start or end
        if (
            input_str[i : i + 3] == '```' and input_str[i + 3 : i + 7] != 'json'
        ):  # assuming ``` as code block delimiter
            in_code_block = not in_code_block
            i += 3  # Skip the next two characters as well
            continue

        if char == '"' and not escaped and not in_code_block:
            in_quotes = not in_quotes

        if in_quotes or in_code_block:
            if char == '\\' and not escaped:
                escaped = True
            elif escaped:
                escaped = False
            else:
                if char == '\n':
                    clean_input.append('\\n')
                elif char == '"' and in_code_block:
                    # Escape quotes only inside code blocks
                    clean_input.append('\\"')
                else:
                    clean_input.append(char)
        else:
            clean_input.append(char)

        if char == '{' and not in_quotes and not in_code_block:
            depth += 1
            if depth == 1:
                start_index = i  # mark the start of a JSON object
        elif char == '}' and not in_quotes and not in_code_block:
            depth -= 1
            if depth == 0 and start_index != -1:
                cleaned_str = ''.join(clean_input[start_index : i + 1])
                try:
                    return json.loads(cleaned_str)
                except json.JSONDecodeError as e:
                    raise ValueError(
                        "Failed to decode JSON object:\n"
                        + cleaned_str
                        + "\n"
                        + str(e)
                    ) from e

        i += 1

    raise ValueError("No complete JSON object found:\n" + ''.join(clean_input))

json_string = '''
JSON object: \n

{
    "Categories of Assistant Response": ["ASSISTANCE"],
    "Retold Text": "Chapter 1: The Genesis of Q* Zero
    \( x = y \)
    \[ x = y \]

    ``` x = "y" ```
    ` x = "y" + :"a" + 'b' `

    'yes, he said'

As the team gathered in the sleek, modern offices of OpenAI, the air was charged with a mix of excitement and anticipation. They were on the cusp of a breakthrough that could change the world forever."
}
'''

json_string = '''

, I will describe the roles of six domain experts that could be involved in the story of the novel. These roles are not limited to the context of the story but are general roles that might be needed in a large-scale AI project like the one depicted in the novel. \n{\n \"Domain expert 1\": {\n \"Role name\": \"AI Ethicist\",\n \"Associated competencies, characteristics, and duties\": \"Expertise in AI ethics, human-AI interaction, and understanding the societal implications of AI. Their primary duty is to ensure the development and implementation of AI systems align with ethical guidelines and principles.\"\n },\n \"Domain expert 2\": {\n \"Role name\": \"AI Researcher\",\n \"Associated competencies, characteristics, and duties\": \"Extensive knowledge in AI, machine learning, and computational linguistics. Their main task is to oversee the research and development of AI systems, focusing on improving performance, efficiency, and safety.\"\n },\n \"Domain expert 3\": {\n \"Role name\": \"AI Security Specialist\",\n \"Associated competencies, characteristics, and duties\": \"Expertise in cybersecurity, AI system security, and threat modeling. Their responsibility is to develop, implement, and maintain security measures for AI systems to protect them from potential threats and attacks.\"\n },\n \"Domain expert 4\": {\n \"Role name\": \"Legal Advisor\",\n \"Associated competencies, characteristics, and duties\": \"Knowledge in AI law, intellectual property rights, and data privacy laws. Their duty is to advise on the legal implications of AI development, deployment, and use, as well as to ensure compliance with relevant regulations.\"\n },\n \"Domain expert 5\": {\n \"Role name\": \"Public Relations Specialist\",\n \"Associated competencies, characteristics, and duties\": \"Expertise in communication strategy, crisis management, and media relations. Their role is to manage the public image of the organization and communicate its mission, values, and activities effectively to the public.\"\n },\n \"Domain expert 6\": {\n \"Role name\": \"Regulatory Affairs Specialist\",\n \"Associated competencies, characteristics, and duties\": \"Understanding of AI regulations, industry standards, and governmental policies. Their duty is to monitor regulatory developments, advocate for favorable policies, and ensure the organization's compliance with regulatory requirements.\"\n}}\n These domain experts can support the characters in the novel by providing their unique skills and expertise in various critical situations, such as ethical dilemmas, security concerns, legal challenges, and communication crises.'''

parsed_data = extract_json_from_string(json_string)
print("good")