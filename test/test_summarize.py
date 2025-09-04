import pytest
from preprocess import parsing
from summarize import company_summary
import json

COMPANY_EXAMPLE_PATH = "./example_datas/company_ex1_비바리퍼블리카.json"

def test_mau_summary():
    """
    Test if summarize mau information well
    """

    with open(COMPANY_EXAMPLE_PATH, "r") as f:
        company_data = json.load(f)
    
    start_date = (2024, 1)
    end_date = (2025, 8)

    data = parsing.get_company_info(company_data, start_date, end_date)
    mau_data = data['mau']
    statement = company_summary.mau_summary(mau_data)

    assert statement != ""

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
