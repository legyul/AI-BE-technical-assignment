
def build_prompt(profile_summary: str) -> str:
    """
    Build the prompt to get tags from GPT model

    Parameter
        - profile_summary (str): Summarized the full profile (include the company information and news)

    Return
        - prompt (str): The prompt to get tags
    """

    instruction = """
Based on the following talent profile, infer up to **10 concise and relevant career-related tags** that represent the individual's educational background, work experience, skills, and other notable traits.

Please follow these instructions:
- Consider tags in categories such as:
  - Education: e.g., 상위권대학교, 해외대학, etc
  - Career: e.g., 대기업, 스타트업, 빅테크, 창업, 리더십, etc
  - Skills: e.g., 백엔드개발, 대용량데이터처리, 전략기획, AI모델개발, etc
  - Other: e.g., 글로벌경험, 커뮤니케이션, 사업개발, etc
- Tags should be:
  - In **Korean**
  - **Concise** (1~3 words)
  - **Relevant** to the provided profile
- Do **not exceed 10 tags**
- Output format must be as follows (in Korean):

태그:
- 태그1
- 태그2
- 태그3
...
    """

    prompt = profile_summary.strip() + "\n" + instruction.strip()

    return prompt
    