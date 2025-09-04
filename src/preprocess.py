import json
import os
from datetime import datetime

class parsing:
    def preprocessing_personal_info(talent_data_path: str) -> dict:
        """
        Load and preprocessing the personal information from JSON file of a person

        Parameter
            - path (str): The path of the JSON file
        
        Return
            - talent_profile (dict): Preprocessed data of the talent
        """
        
        # Load talent's professional data
        with open(talent_data_path, "r") as f:
            talent_dict = json.load(f)
        
        # Combine the last and first name of talent
        name = talent_dict['lastName'] + talent_dict['firstName']

        # Preprocess the talent's education and store their higher education
        edu_raw = talent_dict.get("educations", []) if talent_dict.get("educations") else {}
        
        education = []
        
        for edu in edu_raw:
            start_date = edu.get("originStartEndDate", {}).get("startDateOn", {}).get("year")
            end_date = edu.get("originStartEndDate", {}).get("endDateOn", {}).get("year")

            education.append({"school": edu.get("schoolName"),
                              "degree": edu.get("degreeName"),
                              "field": edu.get("fieldOfStudy"),
                              "year": (start_date, end_date)})
        
        if education:
            education = sorted(education,
                               key=lambda x: x["year"][1] if x["year"][1] is not None else 0,
                               reverse=True)[0]
        else:
            education = {}
        
        # Preprocess the talent's position
        position = []
        
        for p in talent_dict['positions']:
            start_date = p.get("startEndDate", {}).get("start", {})
            end_date = p.get("startEndDate", {}).get("end", {})
            
            # Mapping the name of the company
            profile_company = p.get("companyName", "")

            if profile_company == "토스":
                company_name = "비바리퍼블리카"
            elif profile_company.lower() == "kasa":
                company_name = "카사코리아"
            else: company_name = profile_company

            # Preprocess description part
            description = p.get("description", "")
            if description.strip():
                description_clean = "\n".join([f"- {line.strip()}" for line in description.splitlines() if line.strip()])
            else:
                description_clean = ""

            position.append({"company": company_name,
                            "title": p['title'],
                            "start": (start_date.get("year"), start_date.get("month")) if start_date else None,
                            "end": (end_date.get("year"), end_date.get("month")) if end_date else "Present",
                            "description": description_clean
                            })
        
        # Get and preprocess the talent's other field
        skills = talent_dict.get("skills", [])
        summary = talent_dict.get("summary", "")
        headline = talent_dict.get("headline", "")
        linkedin = talent_dict.get("linkedinUrl", "")

        # Make new dictionary with preprocessed talent's data
        talent_profile = {"name": name,
                        "education": education,
                        "positions": position,
                        "headline": headline,
                        "skills": skills,
                        "summary": summary,
                        "linkedInUrl": linkedin,
                        "industry": talent_dict.get("industryName", "")}

        return talent_profile
    
    def get_company_data(conn, company:str) -> dict | None:
        """
        Get data on the company the talent worked for

        Parameters
            - company (str): The name of the company the talent worked for
        
        Return
            - company_data (dict): The data on the company the talent worked for. If there is no company data, return None
        """

        cursor = conn.cursor()
        cursor.execute("SELECT data FROM company WHERE name = %s", (company,))

        row = cursor.fetchone()
        if row:
            company_data = row[0]
        else:
            company_data = None
        
        return company_data
    
    def get_mau(company_data: dict, start_date: str, end_date: str) -> list:
        """
        Get mau information from company_data

        Parameters
            - company_data (dict): The company data
            - start_date (str): Date (year and month) the talent started working for the company
            - end_date (str): Date (year and month) the talent left the company

        Returns
            - mau (list): The mau information from company_data
        """

        try:
            mau_info = company_data["mau"]["list"][0]["data"]
            mau = [data for data in mau_info if start_date <= data["referenceMonth"] <= end_date]

            return mau
        except (KeyError, IndexError):
            return []
    
    def get_org(company_data: dict, start_date: str, end_date: str) -> list:
        """
        Get organization information from company_data

        Parameters
            - company_data (dict): The company data
            - start_date (str): Date (year and month) the talent started working for the company
            - end_date (str): Date (year and month) the talent left the company

        Returns
            - org (list): The organization information from company_data
        """

        try:
            org_info = company_data["organization"]["data"]
            org = [data for data in org_info if start_date <= data["referenceMonth"] <= end_date]

            return org
        except (KeyError, IndexError):
            return []
    
    def get_invest(company_data: dict, start_date: str, end_date: str) -> list:
        """
        Get investment information from company_data

        Parameters
            - company_data (dict): The company data
            - start_date (str): Date (year and month) the talent started working for the company
            - end_date (str): Date (year and month) the talent left the company

        Returns
            - invest (list): The investment information from company_data
        """

        try:
            invest_info = company_data["investment"]["data"]
            invest = [data for data in invest_info if start_date <= data["investAt"][:7] <= end_date]

            return invest
        except (KeyError, IndexError):
            return []
    
    def get_fin(company_data: dict, start_date: str, end_date: str) -> list:
        """
        Get finance information from company_data

        Parameters
            - company_data (dict): The company data
            - start_date (str): Date (year and month) the talent started working for the company
            - end_date (str): Date (year and month) the talent left the company

        Returns
            - fin (list): The finance information from company_data
        """

        try:
            fin_info = company_data["finance"]["data"]
            fin = [data for data in fin_info if int(start_date[:4]) <= data["year"] <= int(end_date[:4])]

            return fin
        except (KeyError, IndexError):
            return []
    
    def get_company_info(company_data: dict, start_date: tuple[int, int], end_date: tuple[int, int]) -> dict:
        """
        Get company information during talent has worked for the company

        Parameters
            - company (dict): The data of the company
            - start_date (tuple[int, int]): Date (year and month) the talent started working for the company
            - end_date (tuple[int, int]): Date (year and month) the talent left the company
        
        Return
            - company_info (dict): The dictionary contains company information of the mau, investment, organization, finance during tatlent worked for
        """
        
        start_year_month = f"{start_date[0]}-{int(start_date[1]):02d}"

        if end_date != "Present":
            end_year_month = f"{end_date[0]}-{end_date[1]:02d}"
        else:
            today = datetime.today()
            end_year_month = f"{today.year}-{today.month:02d}"

        company_info = {"mau": parsing.get_mau(company_data, start_year_month, end_year_month),
                        "investment": parsing.get_invest(company_data, start_year_month, end_year_month),
                        "organization": parsing.get_org(company_data, start_year_month, end_year_month),
                        "finance": parsing.get_fin(company_data, start_year_month, end_year_month)}
        
        return company_info
    
    def extract_company_period(positions: list[dict]) -> list[dict]:
        """
        Extract company and working period information from positions of the talent profile

        Parameter
            - positions (list[dict]): Preprocessed talent profile
        
        Return
            - (list[dict]): Extracted company and working period information
        """
        talent_company = []
        today = datetime.today()
        date = (today.year, today.month)
        
        for pos in positions:
            company = pos.get('company')
            
            start_date = pos.get("start")
            end_date = pos.get("end")
        
            if company and start_date:      # If there are company and start_date information then append it to the talent_company
                talent_company.append({"company": company,
                                    "start_date": start_date,
                                    "end_date": end_date if end_date != "Present" else date})    # If the talent is still working on the current company, then replace 'Present' to today's year and month
        
        return talent_company

    def get_company_news(conn, company: str, start_date: tuple[int, int], end_date: tuple[int, int]) -> list[dict]:
        """
        Get and preprocess company news information from the company_news table during talent's tenure

        Parameters
            - company (str): The name of the company
            - start_date (tuple[int, int]): Date (year and month) the talent started working for the company
            - end_date (tuple[int, int]): Date (year and month) the talent left the company

        Return
            - news_titles (list[dict]): The list of the company news title during talent's tenure
        """

        if isinstance(end_date, tuple):
            end_date = end_date
        else:
            today = datetime.today()
            end_date = (today.year, today.month)

        company_id = {'비바리퍼블리카': 1,
                      '네이버': 2,
                      '리디': 3,
                      '엘박스': 4,
                      '야놀자': 6}

        # Get company news data from company_news table during talent's tenure
        cursor = conn.cursor()
        cursor.execute("""
                    SELECT * 
                    FROM company_news 
                    WHERE company_id = %s
                    AND (EXTRACT(YEAR FROM news_date) > %s
                        OR (EXTRACT(YEAR FROM news_date) = %s AND EXTRACT(MONTH FROM news_date) >= %s))
                    AND (EXTRACT(YEAR FROM news_date) < %s
                        OR (EXTRACT(YEAR FROM news_date) = %s AND EXTRACT(MONTH FROM news_date) <= %s))
                    """,
                    (company_id.get(company),
                     start_date[0], start_date[0], start_date[1],
                     end_date[0], end_date[0], end_date[1]))
        
        news_raw = cursor.fetchall()
        news_titles = []

        # Store news title and its date
        for i in range(0, len(news_raw)):
            title = news_raw[i][2]
            date = news_raw[i][4]
            news_titles.append({'title': title, 'date': date})
        
        return news_titles
