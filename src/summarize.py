import MeCab
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import date
import math
from preprocess import parsing
import textwrap

class talent_summary:
    def profile_summary(profile: dict) -> str:
        """
        Summarize the talent's profile

        Parameter
            - profile (dict): The profile of the talent

        Return
            - (str): Summary of the profile
        """

        name = profile.get('name', '')
        headline = profile.get('headline', '')
        profile_summ = profile.get('summary', '')
        skills = profile.get('skills', '')
        education = profile['education']
        edu_year = education.get('year')
        edu = education.get('school') + " " + education.get('field') + " " + education.get('degree') + " " + f'({edu_year[0]} - {edu_year[1]})'
        industry = profile.get('industry')

        profile_summary = (f"이름: {name}\n"
                           f"헤드라인: {headline}\n"
                           f"요약: {profile_summ}\n"
                           f"기술: {skills}\n"
                           f"최종 학력: {edu}\n"
                           f"산업 분야: {industry}")
        
        return profile_summary

class company_summary:    
    def growth_summary(datas: list, label: str = 'mau') -> str:
        """
        Summarize the mau or organization information of the company

        Parameter
            - datas (list): The mau or organization information of the company
            - label (str): The data label to handle (default = 'mau') (for the organization '조직 규모')
        
        Return
            - statement (str): The mau or organization information summary
        """

        statement = ""
        key = 'value'

        values = [data.get(key) for data in datas if data.get(key) is not None]

        if not datas:
            statement = f"{label} 정보 없음."
            return statement
        
        first_value = values[0]
        last_value = values[-1]

        # Calculate the total growth rate
        if not first_value:
            total_growth = 0
        else:
            total_growth = ((last_value - first_value) / first_value) * 100     

        # Calculate the monthly growth rate
        monthly_growth = []
        
        for i in range(1, len(values)):
            prev = values[i - 1]
            current = values[i]

            if prev != 0:
                growth = ((current - prev) / prev) * 100
                monthly_growth.append(growth)
        
        avg_monthly_growth = sum(monthly_growth) / len(monthly_growth) if monthly_growth else 0

        # Whether the decrease is temporary
        drop = any(growth < 0 for growth in monthly_growth)

        if abs(total_growth) != 0:
            statement = f"재직 기간 중 {label} 약 {abs(total_growth):.2f}% {'증가' if total_growth > 0 else '감소'}"
        else:
            statement = f"재직 기간 중 {label} 변화 없음."
        
        statement += f"(평균 월간 {avg_monthly_growth:.2f}% {'증가' if avg_monthly_growth >= 0 else '감소'})"

        if drop:
            statement += ", 중간에 일시적 하락도 관측됨."

        return statement
    
    def invest_summary(invest: list) -> str:
        """
        Summarize the investment information of the company

        Parameter
            - invest (list): The investment information of the company
        
        Return
            - invest_statement (str): The investment information summary
        """

        invest_statement = ""

        if not invest:
            invest_statement = "재직 중 투자 정보 없음."
            return invest_statement
        
        # Calculate the total investment amount
        total_invest = sum([inv['investmentAmount'] for inv in invest if inv.get('investmentAmount')])

        # Caclulate the how many rounds
        rounds = [inv.get('level') for inv in invest if inv.get('level')]

        invest_statement = f"재직 중 {len(rounds)}건의 투자 유치 (총 {total_invest/1e8: .1f}억원 규모)."

        return invest_statement
    
    def fin_summary(fin: list) -> str:
        """
        Summarize the finance information of the company

        Parameter
            - fin (list): The list of the finance information of the company

        Return
            - fin_summary (str): The finance information summary
        """

        fin_statement = []
        
        for f in fin:
            year = f.get('year')
            profit = f.get('netProfit')

            if profit is not None:
                status = '흑자' if profit > 0 else '적자'
                fin_statement.append(f'{year}년 {abs(profit/1e8): .1f}억원 {status}')
        
        if fin_statement:
            fin_summary = "재직 중 재무 정보: " + ", ".join(fin_statement)
        else:
            fin_summary = "재직 중 재무 정보 없음."
        
        return fin_summary
    
    def company_info_summary(info: dict) -> str:
        """
        Summarize the company information

        Parameter
            - info (dict): The dictionary of the company info

        Return
            - company_info_summary (str): The comapny information summary
        """

        company_info_summary = (f"- {company_summary.growth_summary(info.get('mau', []), 'mau')}\n"
                                f"- {company_summary.invest_summary(info.get('investment', []))}\n"
                                f"- {company_summary.growth_summary(info.get('organization', []), '조직 규모')}\n"
                                f"- {company_summary.fin_summary(info.get('finance', []))}\n")
        
        return company_info_summary

class news_summary:
    def get_top_news_title(news: list[str], top_n: int = 10) -> list[str]:
        """
        Get top 10 news titles using TF-IDF

        Parameters
            - news (list[str]): The list of the company news titles
            - top_n (int): The number of how many news titles that will get (default = 10)

        Return
            - top_n_news (list[str]): The list of the top n company news titles
        """
        mecabrc_path = "/opt/homebrew/etc/mecabrc"
        dic_path = "/opt/homebrew/Cellar/mecab-ko-dic/2.1.1-20180720/lib/mecab/dic/mecab-ko-dic"

        mecab = MeCab.Tagger(f"-r {mecabrc_path} -d {dic_path}")

        def tokenizer(text):
            parsed = mecab.parse(text)
            return [line.split('\t')[0] for line in parsed.splitlines() if '\t' in line]
        
        vectorizer = TfidfVectorizer(tokenizer=tokenizer, token_pattern=None)
        tfidf_matrix = vectorizer.fit_transform(news)

        # Select the top N based on the average TF-IDF score for each title
        scores = tfidf_matrix.mean(axis=1).flatten().tolist()[0]
        ranked = sorted(zip(news, scores), key=lambda x: x[1], reverse=True)

        # Get top n index
        top_n_news = [title for title, _ in ranked[:top_n]]

        return top_n_news
    
    def get_3_news(top_news: list[dict], top_n: int = 3) -> list[dict]:
        """
        Get the top 3 news using the latest date and the keyword-based weight scores

        Parameters
            - top_news (list[dict]): The list of the top 10 news that filtered with TF-IDF
            - top_n (int): The number of how many news titles that will get (default = 3)
        
        Return
            - top_scored_news (list[dict]): The list of the top n company news titles and their date
        """

        keywords = ['매출', '흑자', '적자', '실적', '이익', '수익', '영업이익', '재무', '성장', '분기', '연간', '달성',
                    '해외진출', '확장', '진출', '글로벌', '출시', '오픈', '출범', '런칭', '사업', '전략', '개편',
                    'AI', '기술', '신기술', '서비스', '개발', '혁신', '솔루션', 'API', '모델', '플랫폼',
                    '채용', '인재', '조직', '인사', '대표', 'CEO', '팀', '임원', '인력', '리더십',
                    '투자', '시리즈', 'M&A', '인수', '지분', '유치', '펀딩', '상장', 'IPO',
                    '사용자', '고객', 'MAU', '트래픽', '리텐션', '시장', '점유율', '경쟁', '반응',
                    '규제', '이슈', '소송', '법', '정부', '정책', '감사', '과징금', '제재']
        
        today = date.today()
        
        score = []

        for item in top_news:
            title = item['title']
            news_date = item['date']

            # Keyword appearance score
            # Remove duplicate keywords
            matched_keywords = {key for key in keywords if key in title}
            keyword_scores = len(matched_keywords)

            # Date based weights (e.g., The oldest news is lower weights)
            days_count = (today - news_date).days
            date_weights = 1 / (math.log(days_count + 2))       # log scale weights -> A method to decay the score as the date gets older
                                                                #                   -> Boost the score for fresher news
            
            total_scores = keyword_scores * date_weights

            score.append({'title': title,
                          'date': news_date,
                          'score': total_scores})
        
        # Get top n based on the score
        top_scored_news = sorted(score, key=lambda x: x['score'], reverse=True)[:top_n]

        return top_scored_news
    
    def summarize_news(news_list: list[dict]) -> str:
        """
        Summarize the company news

        Parameter
            - top_3_news (dict): The dictionary of the filtered 3 company news

        Return
            - company_news_summary (str): The comapny news summary
        """

        titles = [title['title'] for title in news_list]
        top_n_titles = news_summary.get_top_news_title(titles)
        filtered_news = [item for item in news_list if item['title'] in top_n_titles]
        top_news = news_summary.get_3_news(filtered_news)
        
        summary = []

        for news in top_news:
            date_str = news['date'].strftime("%Y-%m-%d") if hasattr(news['date'], 'strftime') else str(news['date'])
            title = news['title']
            summary.append(f"{date_str}: {title}")
        
        company_news_summary = '\n'.join(summary)
        
        return company_news_summary

def summary(conn, profile: dict, profile_summary: str) -> str:
    """
    Summarize and combine all talent's profile, company information, and company news

    Parameters
        - profile (dict): Preprocessed profile of the talent
        - profile_summary (str): Summarized profile (exclude the company information and news)

    Return
        - full_summary (str): Summarized the full profile (include the company information and news)
    """

    positions_summary = []

    # Get and summarize the company information and news by the position of the talent
    for pos in profile['positions']:
        summary_text = summarize_position(conn, pos)
        positions_summary.append(summary_text)

    filtered_profile = [line for line in profile_summary.splitlines() if '이름' not in line.strip()]
    profile_statement = "[프로필 요약]\n" + "\n".join(filtered_profile)
    full_summary = profile_statement + '\n\n' + '\n\n'.join(positions_summary)

    return full_summary

def summarize_position(conn, position: dict) -> str:
    """
    Summarize the company information and news of each position

    Parameter
        - position (dict): The position information 
    
    Return
        - position_summary (str): The summary of each position
    """

    company_name = position['company']
    start_date = position['start']
    end_date = position['end']

    if isinstance(end_date, tuple):
        end_str = f"{end_date[0]}.{end_date[1]:02d}"
    else:
        today = date.today()
        end_str = f"{today.year}.{today.month:02d}"
    
    company_data = parsing.get_company_data(conn, company_name)
    info_summary = ""
    company_news_summary = ""

    if company_data:
        company_info = parsing.get_company_info(company_data, start_date, end_date)

        if company_info:
            company_info_summary = company_summary.company_info_summary(company_info)

            filtered_summary = [line for line in company_info_summary.splitlines() if '정보 없음' not in line.strip()]

            if filtered_summary:
                info_summary = "\n\n[재직 중 회사 정보 요약]\n" + "\n".join(filtered_summary)
            else:
                info_summary = ""
        
        news_data = parsing.get_company_news(conn, company_name, start_date, end_date)

        if news_data:
            company_news_summary = f"\n\n[재직 중 주요 뉴스 요약]\n{news_summary.summarize_news(news_data)}"

    summarize_info_news = (f"회사명: {company_name}\n"
                           f"직책: {position['title']}\n"
                           f"재직 기간: {start_date[0]}.{start_date[1]:02d} - {end_str}\n"
                           f"담당 업무:\n{position['description']}")
    
    if info_summary:
        summarize_info_news += info_summary
    if company_news_summary:
        summarize_info_news += company_news_summary
    
    return summarize_info_news


def summary_short(conn, profile: dict, profile_summary: str, max_positions: int = 3) -> str:
    """
    (When want to use only 3 positions)
    Summarize and combine all talent's profile, company information, and company news

    Parameters
        - profile (dict): Preprocessed profile of the talent
        - profile_summary (str): Summarized profile (exclude the company information and news)
        - max_positions (int): Limit the number of positions (default = 3)

    Return
        - full_summary (str): Summarized the full profile (include the company information and news)
    """

    positions = profile.get('positions', [])
    positions_summary = []

    for i, pos in enumerate(positions[:max_positions]):
        summary_text = summarize_position(conn, pos)
        positions_summary.append(summary_text)

    # If there is more than maximum number of the positions
    remain = len(positions) - max_positions
    if remain > 0:
        positions_summary.append(f"...외 {remain}건의 추가 포지션이 있습니다.")
    
    filtered_profile = [line for line in profile_summary.splitlines() if '이름' not in line.strip()]
    profile_statement = "[프로필 요약]\n" + "\n".join(filtered_profile)
    full_summary = profile_statement + '\n\n' + '\n\n'.join(positions_summary)

    return full_summary