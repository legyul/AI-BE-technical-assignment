from logger_utils import logger
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import date
import math
from .preprocess import parsing
import textwrap
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")
import MeCab

# os.environ["MECABRC"] = os.getenv("MECABRC")
# mecab = MeCab.Tagger(f"-r {os.getenv('MECABRC')} -d {os.getenv('DIC_PATH')}")

class talent_summary:
    def profile_summary(profile: dict) -> str:
        """
        Summarize the talent's profile

        Parameter
            - profile (dict): The profile of the talent

        Return
            - (str): Summary of the profile
        """

        try:
            name = profile.get('name', '')
            headline = profile.get('headline', '')
            profile_summ = profile.get('summary', '')
            skills = profile.get('skills', '')
            education = profile['education']
            edu_year = education.get('year')
            edu = education.get('school', '') + " " + education.get('field') + " " + education.get('degree') + " " + f'({edu_year[0]} - {edu_year[1]})'
            industry = profile.get('industry', '')

            profile_summary = (f"이름: {name}\n"
                            f"헤드라인: {headline}\n"
                            f"요약: {profile_summ}\n"
                            f"기술: {skills}\n"
                            f"최종 학력: {edu}\n"
                            f"산업 분야: {industry}")
            
            logger.info("[INFO] Completed the talent profile summarize.")
        
            return profile_summary
        
        except KeyError as  e:
            logger.error(f"[ERROR] Missing field error in profile: {e}")
            return " Error occurs while load the profile information."
        except Exception as e:
            logger.exception(f"Unexpected error occurs: {e}")
            return "Error occurs while summarize the profile."

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

        try:
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
                logger.warning(f"[WARNING] {label}: First value is 0 or None (value={first_value})")
                total_growth = 0
            else:
                total_growth = ((last_value - first_value) / first_value) * 100     

            # Calculate the monthly growth rate
            monthly_growth = []
            
            for i in range(1, len(values)):
                prev = values[i - 1]
                current = values[i]

                try:
                    if prev != 0:
                        growth = ((current - prev) / prev) * 100
                        monthly_growth.append(growth)
                except Exception as e:
                    logger.error(f"[ERROR] {label}: Monthly growth calculation error (prev={prev}, current={current}) - {e}")
            
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

        except Exception as e:
            logger.exception(f"[ERROR] {label} Fatal error during growth rate analysis: {e}")
            return f"{label} 정보 분석 실패"
    
    def invest_summary(invest: list) -> str:
        """
        Summarize the investment information of the company

        Parameter
            - invest (list): The investment information of the company
        
        Return
            - invest_statement (str): The investment information summary
        """

        invest_statement = ""

        try:
            if not invest:
                invest_statement = "재직 중 투자 정보 없음."
                logger.info("[INFO] No investment data provided.")
                return invest_statement
            
            # Calculate the total investment amount
            total_invest = sum([inv['investmentAmount'] for inv in invest if inv.get('investmentAmount')])
            logger.debug(f"[DEBUG] Total investment calculated: {total_invest}")

            # Caclulate the how many rounds
            rounds = [inv.get('level') for inv in invest if inv.get('level')]
            logger.debug(f"[DEBUG] Investment rounds parsed: {rounds}")

            invest_statement = f"재직 중 {len(rounds)}건의 투자 유치 (총 {total_invest/1e8: .1f}억원 규모)."
            logger.info(f"[INFO] Parsed investment statement: {invest_statement}")

            return invest_statement
        
        except Exception as e:
            logger.warning(f"[WARNING] Error while parsing investment data: {e}", exc_info=True)
            return "투자 정보 파싱 중 오류 발생."
    
    def fin_summary(fin: list) -> str:
        """
        Summarize the finance information of the company

        Parameter
            - fin (list): The list of the finance information of the company

        Return
            - fin_summary (str): The finance information summary
        """

        fin_statement = []

        try:
            for f in fin:
                year = f.get('year')
                profit = f.get('netProfit')

                if profit is not None:
                    try:
                        profit_float = float(profit)
                        status = '흑자' if profit_float > 0 else '적자'
                        fin_statement.append(f'{year}년 {abs(profit_float/1e8): .1f}억원 {status}')
                    except Exception as e:
                        logger.warning(f"[WARNING] Faile parsing the finance information (year: {year}, profit: {profit_float}: {e}")
            
            if fin_statement:
                fin_summary = "재직 중 재무 정보: " + ", ".join(fin_statement)
            else:
                fin_summary = "재직 중 재무 정보 없음."
            
            return fin_summary
        
        except Exception as e:
            logger.error(f"[ERROR] Error occurs while summarize the finance information: {e}")
            return "재직 중 재무 정보 요약 생성 중 오류 발생"
    
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
        try:
            logger.info(f"[INFO] Start summarize the news data. Number of input news: {len(news)}")

            mecab = MeCab.Tagger(f"-r {os.getenv('MECABRC')} -d {os.getenv('DIC_PATH')}")
            logger.info("[INFO] Completed reset MeCab tagger")

            def tokenizer(text):
                parsed = mecab.parse(text)
                if parsed is None:
                    logger.warning("[WARNING] The result of MeCab parsing is None")
                    return []
                return [line.split('\t')[0] for line in parsed.splitlines() if '\t' in line]
            
            vectorizer = TfidfVectorizer(tokenizer=tokenizer, token_pattern=None)
            tfidf_matrix = vectorizer.fit_transform(news)
            logger.info(f"[INFO] Completed TF-IDF vectorization. shape: {tfidf_matrix.shape}")

            # Select the top N based on the average TF-IDF score for each title
            scores = tfidf_matrix.mean(axis=1).flatten().tolist()[0]
            ranked = sorted(zip(news, scores), key=lambda x: x[1], reverse=True)
            logger.info("[INFO] Completed news scoring and sorting")

            # Get top n index
            top_n_news = [title for title, _ in ranked[:top_n]]
            logger.info(f"[INFO] Completed parsing the top {top_n} news.")

            return top_n_news
        
        except Exception as e:
            logger.exception(f"[ERROR] Error occurs while parsing the top {top_n} news")
    
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

        for idx, item in enumerate(top_news):
            try:
                title = item['title']
                news_date = item['date']

                if not title:
                    logger.warning(f"[WARNING] {idx} Invalid data: title='{title}', date='{news_date}'")
                    continue

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
            
            except Exception as e:
                logger.exception(f"[ERROR] Error occurs while scoring {idx} news: {e}")
                continue
        
        # Get top n based on the score
        top_scored_news = sorted(score, key=lambda x: x['score'], reverse=True)[:top_n]
        logger.info(f"[INFO] Completed scoring the news: total {len(score)}")

        return top_scored_news
    
    def summarize_news(news_list: list[dict]) -> str:
        """
        Summarize the company news

        Parameter
            - top_3_news (dict): The dictionary of the filtered 3 company news

        Return
            - company_news_summary (str): The comapny news summary
        """

        try:
            titles = [title['title'] for title in news_list]
            logger.info(f"[INFO] Completed parsing the news title, total: {len(titles)}")
            top_n_titles = news_summary.get_top_news_title(titles)
            filtered_news = [item for item in news_list if item['title'] in top_n_titles]
            top_news = news_summary.get_3_news(filtered_news)
            logger.info("[INFO] Completed top 3 news selection")
            
            summary = []

            for news in top_news:
                date_str = news['date'].strftime("%Y-%m-%d") if hasattr(news['date'], 'strftime') else str(news['date'])
                title = news['title']
                summary.append(f"{date_str}: {title}")
            
            company_news_summary = '\n'.join(summary)
            logger.info("[INFO] Completed the company news summarization")
            
            return company_news_summary
        
        except Exception as e:
            logger.exception(f"[ERROR] Error occurs while the company news summarization: {e}")
            return "뉴스 요약 중 에러 발생"

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
        try:
            summary_text = summarize_position(conn, pos)
            positions_summary.append(summary_text)
        except Exception as e:
            logger.warning(f"[ERROR] Failed to summarize position '{pos}': {e}")
            continue

    try:
        filtered_profile = [line for line in profile_summary.splitlines() if '이름' not in line.strip()]
        profile_statement = "[프로필 요약]\n" + "\n".join(filtered_profile)
    except Exception as e:
        logger.error(f"[ERROR] Filtering profile summary: {e}")
        profile_statement = "[프로필 요약]\n(요약 실패)"

    try:
        full_summary = profile_statement + '\n\n' + '\n\n'.join(positions_summary)
    except Exception as e:
        logger.error(f"[ERROR] Generating full summary: {e}")
        full_summary = profile_statement

    return full_summary

def summarize_position(conn, position: dict) -> str:
    """
    Summarize the company information and news of each position

    Parameter
        - position (dict): The position information 
    
    Return
        - position_summary (str): The summary of each position
    """

    try:
        company_name = position['company']
        start_date = position['start']
        end_date = position['end']

        logger.debug(f"[DEBUG] Processing position at company: {company_name} ({start_date} - {end_date})")

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
                    logger.debug(f"[DEBUG] Company info summary found for {company_name}")
                else:
                    logger.info(f"[INFO] No useful company info found for {company_name}")
                    info_summary = ""
            
            news_data = parsing.get_company_news(conn, company_name, start_date, end_date)

            if news_data:
                company_news_summary = f"\n\n[재직 중 주요 뉴스 요약]\n{news_summary.summarize_news(news_data)}"
                logger.info(f"[INFO] News summary added for {company_name}")
            else:
                logger.warning(f"[WARNING] No news data found for {company_name}")
        
        else:
            logger.warning(f"[WARNING] No company data found for {company_name}")

        summarize_info_news = (f"회사명: {company_name}\n"
                            f"직책: {position['title']}\n"
                            f"재직 기간: {start_date[0]}.{start_date[1]:02d} - {end_str}\n"
                            f"담당 업무:\n{position['description']}")
        
        if info_summary:
            summarize_info_news += info_summary
        if company_news_summary:
            summarize_info_news += company_news_summary
        
        return summarize_info_news
    
    except Exception as e:
        logger.error(f"[ERROR] Failed to summarize position info for {company_name}: {e}", exc_info=True)
        return f"회사명: {company_name} - 정보를 처리하는 중 오류 발생"


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