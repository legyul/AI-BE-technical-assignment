from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv(dotenv_path="./.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
- For **each tag**, include a **short justification** based on the profile content (1 sentence).
- Do **not exceed 10 tags**
- Output format must be as follows (in Korean):

태그 (example):
- 상위권대학교 (연세대학교 출신)
- 성장기스타트업 경험 (토스 재직 시기 중 투자 및 조직 규모 급성장)
- 리더십 (Tech Lead, Chapter Lead 등 리더 타이틀 보유)
- 대용량데이터처리 (네이버 AI팀에서 LLM, 하이퍼클로바 등 대규모 모델 및 데이터 다룸)
...
※ The format must be followed.
    """

    prompt = profile_summary.strip() + "\n" + instruction.strip()

    return prompt

def gen_tags(prompt: str, model: str = "gpt-5-mini", temperature: float = 0.2) -> str:
    """
    Call the GPT model to generate tags

    Parameters
        - prompt (str): The prompt to put into the GPT model
        - model (str): The name of the GPT model that will be used (default = "gpt-5-mini")
        - temperature (float): The value that controls GPT's creativity/randomness (default = 0.2)
    
    Returns
        - str: The model response
    """
    try:
        response = client.chat.completions.create(model=model,
                                                  messages=[
                                                      {"role": "system", "content": "You are a specialist in precisely inferring talent tags."},
                                                      {"role": "user", "content": prompt}
                                                  ],)
                                                  #temperature=temperature,)
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"GPT 호출 실패: {e}")
        return ""