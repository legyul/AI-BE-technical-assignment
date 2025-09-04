import pytest
from preprocess import parsing
from summarize import company_summary
import json

COMPANY_EXAMPLE_PATH = "./example_datas/company_ex1_비바리퍼블리카.json"

def test_growth_summary():
    """
    Test if summarize growth (mau and orgainization) information well
    """

    with open(COMPANY_EXAMPLE_PATH, "r") as f:
        company_data = json.load(f)
    
    start_date = (2024, 1)
    end_date = (2025, 8)

    data = parsing.get_company_info(company_data, start_date, end_date)
    
    # Get mau data and its summary
    mau_data = data['mau']
    mau_statement = company_summary.growth_summary(mau_data, 'mau')
    
    # Get orgainization data and its summary
    org_data = data['organization']
    org_statement = company_summary.growth_summary(org_data, '조직 규모')

    assert mau_statement != ""
    assert org_statement != ""

def test_invest_summary():
    """
    Test if summarize investment information well
    """

    with open(COMPANY_EXAMPLE_PATH, "r") as f:
        company_data = json.load(f)
    
    start_date = (2024, 1)
    end_date = (2025, 8)

    data = parsing.get_company_info(company_data, start_date, end_date)
    inv_data = data['investment']
    statement = company_summary.invest_summary(inv_data)

    assert statement != ""

def test_fin_summary():
    """
    Test if summarize investment information well
    """

    with open(COMPANY_EXAMPLE_PATH, "r") as f:
        company_data = json.load(f)

    start_date = (2024, 1)
    end_date = (2025, 8)

    data = parsing.get_company_info(company_data, start_date, end_date)
    fin_data = data['finance']
    statement = company_summary.fin_summary(fin_data)

    assert statement != ""

def test_company_info_summary():
    """
    Test if summarize the company information well
    """

    with open(COMPANY_EXAMPLE_PATH, "r") as f:
        company_data = json.load(f)

    start_date = (2021, 1)
    end_date = (2023, 8)

    data = parsing.get_company_info(company_data, start_date, end_date)

    statement = company_summary.company_info_summary(data)

    assert "- 재직 기간 중 mau" in statement
    assert "투자 유치" in statement
    assert "조직 규모" in statement
    assert "- 재직 중 재무 정보:" in statement

def test_company_info_summary_empty_info():
    """
    Test if summarize the company info with no certain information
    """

    with open(COMPANY_EXAMPLE_PATH, "r") as f:
        company_data = json.load(f)

    start_date = (2024, 1)
    end_date = (2025, 8)

    data = parsing.get_company_info(company_data, start_date, end_date)

    statement = company_summary.company_info_summary(data)

    assert "투자 정보 없음" in statement
    assert "재무 정보 없음" in statement