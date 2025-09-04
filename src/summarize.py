

class company_summary:    
    def growth_summary(datas: list, key: str = 'value', label: str = 'mau') -> str:
        """
        Summarize the mau or organization information of the company

        Parameter
            - datas (list): The mau or organization information of the company
            - key (str): The key of the value value (default = 'value')
            - label (str): The data label to handle (default = 'mau') (for the organization '조직 규모')
        
        Return
            - statement (str): The mau or organization information summary
        """

        statement = ""

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

        invest_statement = f"재직 중 {len(rounds)}건의 투자 유치 (총 {total_invest/1e8: .2f}억원 규모)."

        return invest_statement
    
    