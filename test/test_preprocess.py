import os
import pytest
from preprocess import parsing
import json

EXAMPLE_PATH = "./example_datas/talent_ex3.json"
COMPANY_EXAMPLE_PATH = "./example_datas/company_ex1_비바리퍼블리카.json"

def test_name_parsing():
    """
    Test if the first and last name combined well
    """

    data = parsing.preprocessing_personal_info(EXAMPLE_PATH)
    assert data['name'] == "양승모"

def test_position_count():
    """
    Test if parsing the position well
    """

    data = parsing.preprocessing_personal_info(EXAMPLE_PATH)
    assert len(data["positions"]) == 9

def test_position_structure():
    """
    Test if parsing the component of the position well
    """

    data = parsing.preprocessing_personal_info(EXAMPLE_PATH)

    for pos in data["positions"]:
        assert "company" in pos
        assert "title" in pos
        assert isinstance(pos["start"], tuple)
        assert "description" in pos
        
        if pos["description"]:
            assert pos["description"].startswith("-")
        else:
            assert pos["description"] == ""

def test_education_parsing():
    """
    Test if parsing the education well
    """

    data = parsing.preprocessing_personal_info(EXAMPLE_PATH)
    edu = data["education"]

    assert edu["school"] == "연세대학교"
    assert edu["year"] == (1997, 2004)
    assert edu["degree"] == "학사"
    assert edu["field"] == "전기 및 전자 공학"

def test_industry_present():
    """
    Test if parsing the industry well
    """

    data = parsing.preprocessing_personal_info(EXAMPLE_PATH)
    assert "industry" in data
    assert data["industry"] == "IT 서비스 및 IT 컨설팅"

def test_get_company_info():
    """
    Test if get company information with certain time period well
    """

    with open(COMPANY_EXAMPLE_PATH, "r") as f:
        company_data = json.load(f)
    
    start_date = (2024, 1)
    end_date = (2025, 8)

    data = parsing.get_company_info(company_data, start_date, end_date)

    assert "mau" in data
    assert all("referenceMonth" in d for d in data["mau"])
    assert all("2024-01" <= d["referenceMonth"] <= "2025-08" for d in data["mau"])
    assert isinstance(data["finance"], list)

def test_extract_company():
    """
    Test if extracting multiple company's name and working period well
    """

    data = parsing.preprocessing_personal_info(EXAMPLE_PATH)
    positions = data['positions']
    companies = parsing.extract_company_period(positions)

    assert len(companies) == 9
