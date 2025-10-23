import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import time

# Configure the page
st.set_page_config(
    page_title="Baraka FinTech",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2563EB;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .module-card {
        background-color: #F0F9FF;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border-left: 5px solid #2563EB;
    }
    .metric-card {
        background-color: #EFF6FF;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem;
    }
    .success-box {
        background-color: #D1FAE5;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #FEF3C7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .islamic-green {
        color: #059669;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for user data
if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        'name': 'Ahmed Hassan',
        'savings': 150000,
        'investments': 75000,
        'zakat_paid': 3750,
        'compliance_score': 92,
        'last_login': datetime.now().strftime("%Y-%m-%d")
    }

if 'transactions' not in st.session_state:
    st.session_state.transactions = [
        {'date': '2023-10-01', 'type': 'Murabaha', 'amount': 50000, 'status': 'Completed'},
        {'date': '2023-10-05', 'type': 'Ijara', 'amount': 25000, 'status': 'Pending'},
        {'date': '2023-10-10', 'type': 'Musharakah', 'amount': 100000, 'status': 'Completed'},
    ]

if 'investments' not in st.session_state:
    st.session_state.investments = [
        {'name': 'Sukuk Al-Ijarah', 'amount': 30000, 'return': 8.5, 'maturity': '2024-06-15'},
        {'name': 'Halal Equity Fund', 'amount': 25000, 'return': 12.2, 'maturity': '2025-01-20'},
        {'name': 'Islamic Real Estate Fund', 'amount': 20000, 'return': 7.8, 'maturity': '2024-09-30'},
    ]

# App Header
st.markdown('<h1 class="main-header">🌙 Baraka FinTech</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align: center; color: #4B5563;">Islamic Banking Compliance & Empowerment Platform</h3>', unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=100)
st.sidebar.title("Navigation")
app_module = st.sidebar.selectbox(
    "Select Module",
    ["Dashboard", "AI Sharia Compliance", "Smart Contracts", "Halal Investments", "Zakat Management", "Education & Advisory"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### User Profile")
st.sidebar.write(f"**Name:** {st.session_state.user_data['name']}")
st.sidebar.write(f"**Compliance Score:** {st.session_state.user_data['compliance_score']}%")
st.sidebar.progress(st.session_state.user_data['compliance_score'] / 100)

# Dashboard Module
if app_module == "Dashboard":
    st.markdown('<h2 class="sub-header">📊 Dashboard Overview</h2>', unsafe_allow_html=True)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>KES {st.session_state.user_data['savings']:,}</h3>
            <p>Total Savings</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>KES {st.session_state.user_data['investments']:,}</h3>
            <p>Halal Investments</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>KES {st.session_state.user_data['zakat_paid']:,}</h3>
            <p>Zakat Paid (YTD)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{st.session_state.user_data['compliance_score']}%</h3>
            <p>Sharia Compliance</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts and Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Investment Performance")
        
        # Create sample data for investment performance
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct']
        sukuk_returns = [5.2, 5.5, 5.8, 6.1, 6.3, 6.5, 6.8, 7.0, 7.2, 7.5]
        equity_returns = [8.1, 8.5, 9.2, 9.8, 10.5, 11.2, 11.8, 12.0, 12.2, 12.5]
        real_estate_returns = [4.5, 4.8, 5.0, 5.3, 5.5, 5.8, 6.0, 6.3, 6.5, 6.8]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=sukuk_returns, mode='lines+markers', name='Sukuk', line=dict(color='#2563EB')))
        fig.add_trace(go.Scatter(x=months, y=equity_returns, mode='lines+markers', name='Halal Equity', line=dict(color='#059669')))
        fig.add_trace(go.Scatter(x=months, y=real_estate_returns, mode='lines+markers', name='Real Estate', line=dict(color='#7C3AED')))
        
        fig.update_layout(
            title="Investment Returns (%) Over Time",
            xaxis_title="Month",
            yaxis_title="Return (%)",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Recent Transactions")
        
        transactions_df = pd.DataFrame(st.session_state.transactions)
        if not transactions_df.empty:
            st.dataframe(transactions_df, use_container_width=True)
        else:
            st.info("No recent transactions")
        
        st.markdown("#### Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 New Contract"):
                st.session_state.current_module = "Smart Contracts"
                st.experimental_rerun()
        
        with col2:
            if st.button("💰 Calculate Zakat"):
                st.session_state.current_module = "Zakat Management"
                st.experimental_rerun()
        
        with col3:
            if st.button("📚 Learn More"):
                st.session_state.current_module = "Education & Advisory"
                st.experimental_rerun()

# AI Sharia Compliance Engine Module
elif app_module == "AI Sharia Compliance":
    st.markdown('<h2 class="sub-header">🧠 AI Sharia Compliance Engine</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="module-card">
        <p>This module uses machine learning to analyze transactions, loan terms, and contracts in real time for Sharia compliance.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Transaction Analysis")
        
        transaction_text = st.text_area(
            "Enter transaction details to analyze:",
            "Purchase of manufacturing equipment for textile production with 5% interest financing for 2 years"
        )
        
        if st.button("Analyze Transaction"):
            with st.spinner("Analyzing for Sharia compliance..."):
                time.sleep(2)
                
                # Mock analysis results
                st.markdown("### Analysis Results")
                
                # Check for interest (riba)
                if "interest" in transaction_text.lower():
                    st.markdown("""
                    <div class="warning-box">
                        <h4>🚨 Potential Riba (Interest) Detected</h4>
                        <p>The transaction appears to involve interest-based financing, which is prohibited in Islamic finance.</p>
                        <p><strong>Recommendation:</strong> Consider Murabaha (cost-plus financing) or Ijara (leasing) as Sharia-compliant alternatives.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="success-box">
                        <h4>✅ No Riba Detected</h4>
                        <p>The transaction does not appear to involve interest-based elements.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Check for excessive uncertainty (gharar)
                if "uncertain" in transaction_text.lower() or "speculative" in transaction_text.lower():
                    st.markdown("""
                    <div class="warning-box">
                        <h4>⚠️ Potential Gharar (Uncertainty) Detected</h4>
                        <p>The transaction may involve excessive uncertainty or speculation.</p>
                        <p><strong>Recommendation:</strong> Ensure all terms are clearly defined and avoid speculative elements.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Check for prohibited sectors
                prohibited_sectors = ["alcohol", "gambling", "pork", "casino", "tobacco"]
                detected_sectors = [sector for sector in prohibited_sectors if sector in transaction_text.lower()]
                
                if detected_sectors:
                    st.markdown(f"""
                    <div class="warning-box">
                        <h4>🚨 Prohibited Sector Detected</h4>
                        <p>The transaction involves sectors not permissible in Islamic finance: {', '.join(detected_sectors)}.</p>
                        <p><strong>Recommendation:</strong> Consider alternative Sharia-compliant investment opportunities.</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("Compliance Dashboard")
        
        # Compliance metrics
        st.metric("Overall Compliance Score", f"{st.session_state.user_data['compliance_score']}%")
        
        # Compliance by category
        compliance_data = {
            'Category': ['Riba Avoidance', 'Gharar Avoidance', 'Halal Investments', 'Zakat Payment'],
            'Score': [95, 88, 92, 85]
        }
        
        fig = px.bar(compliance_data, x='Category', y='Score', 
                     title="Compliance by Category", 
                     color='Score', color_continuous_scale='Viridis')
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent compliance checks
        st.subheader("Recent Compliance Checks")
        
        compliance_checks = [
            {'Date': '2023-10-15', 'Transaction': 'Murabaha Financing', 'Status': 'Compliant', 'Details': 'No issues found'},
            {'Date': '2023-10-10', 'Transaction': 'Auto Loan Application', 'Status': 'Non-Compliant', 'Details': 'Interest component detected'},
            {'Date': '2023-10-05', 'Transaction': 'Investment Screening', 'Status': 'Compliant', 'Details': 'Halal sector verified'},
        ]
        
        st.dataframe(pd.DataFrame(compliance_checks), use_container_width=True)

# Smart Contract Automation Module
elif app_module == "Smart Contracts":
    st.markdown('<h2 class="sub-header">📜 Smart Contract Automation</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="module-card">
        <p>Automate generation of Islamic contracts (Murabaha, Musharakah, Ijarah, etc.) with blockchain-based traceability.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Create New Contract")
        
        contract_type = st.selectbox(
            "Select Contract Type",
            ["Murabaha (Cost-Plus Financing)", "Musharakah (Partnership)", "Ijara (Leasing)", "Salam (Advance Payment)", "Istisna (Manufacturing Contract)"]
        )
        
        st.subheader("Contract Details")
        
        col1a, col2a = st.columns(2)
        
        with col1a:
            party_a = st.text_input("Party A (Financier)", "Baraka Islamic Bank")
            party_b = st.text_input("Party B (Customer)", st.session_state.user_data['name'])
            asset_description = st.text_input("Asset Description", "Commercial vehicle for transportation business")
        
        with col2a:
            contract_value = st.number_input("Contract Value (KES)", min_value=1000, value=500000, step=1000)
            profit_margin = st.number_input("Profit Margin (%)", min_value=0.0, value=8.5, step=0.1)
            duration = st.selectbox("Contract Duration", ["3 months", "6 months", "1 year", "2 years", "3 years", "5 years"])
        
        payment_terms = st.selectbox("Payment Terms", ["Lump sum at maturity", "Monthly installments", "Quarterly installments"])
        
        if st.button("Generate Contract"):
            with st.spinner("Generating smart contract..."):
                time.sleep(3)
                
                st.success("✅ Smart contract generated successfully!")
                
                # Display contract preview
                st.subheader("Contract Preview")
                
                st.markdown(f"""
                ### {contract_type} Agreement
                
                **Between:** {party_a} (Hereinafter referred to as the "Financier")
                
                **And:** {party_b} (Hereinafter referred to as the "Customer")
                
                **Asset:** {asset_description}
                
                **Contract Value:** KES {contract_value:,}
                
                **Profit Margin:** {profit_margin}%
                
                **Duration:** {duration}
                
                **Payment Terms:** {payment_terms}
                
                **Terms and Conditions:**
                
                1. This contract is governed by Sharia principles and complies with AAOIFI standards.
                2. All transactions under this contract are free from Riba (interest).
                3. The asset remains in the ownership of the Financier until full payment is received.
                4. The Customer bears all maintenance costs during the contract period.
                5. Any dispute shall be resolved through Sharia-compliant arbitration.
                
                **Digital Signature:** 
                - Financier: ____________________ (To be signed digitally)
                - Customer: ____________________ (To be signed digitally)
                
                **Blockchain Hash:** `0x1a2b3c4d5e6f7890abcdef1234567890`
                """)
                
                col1b, col2b, col3b = st.columns(3)
                
                with col1b:
                    st.download_button(
                        "Download Contract PDF",
                        data="Mock contract content",
                        file_name=f"{contract_type.replace(' ', '_')}_Contract.pdf",
                        mime="application/pdf"
                    )
                
                with col2b:
                    if st.button("Send for Sharia Board Review"):
                        st.info("Contract sent to Sharia Board for approval")
                
                with col3b:
                    if st.button("Sign Digitally"):
                        st.success("Contract signed successfully! Hash recorded on blockchain.")
    
    with col2:
        st.subheader("Contract Templates")
        
        templates = [
            {"name": "Murabaha", "usage": "Asset Financing", "complexity": "Medium"},
            {"name": "Musharakah", "usage": "Partnership", "complexity": "High"},
            {"name": "Ijara", "usage": "Leasing", "complexity": "Medium"},
            {"name": "Salam", "usage": "Advance Payment", "complexity": "Medium"},
            {"name": "Istisna", "usage": "Manufacturing", "complexity": "High"},
        ]
        
        for template in templates:
            with st.expander(f"{template['name']} - {template['usage']}"):
                st.write(f"Complexity: {template['complexity']}")
                if st.button(f"Use Template", key=template['name']):
                    st.info(f"{template['name']} template selected")
        
        st.subheader("Contract History")
        
        contract_history = [
            {"Date": "2023-09-15", "Type": "Murabaha", "Value": "KES 750,000", "Status": "Active"},
            {"Date": "2023-08-22", "Type": "Ijara", "Value": "KES 1,200,000", "Status": "Completed"},
            {"Date": "2023-07-10", "Type": "Musharakah", "Value": "KES 2,500,000", "Status": "Active"},
        ]
        
        for contract in contract_history:
            st.write(f"**{contract['Date']}** - {contract['Type']}")
            st.write(f"Value: {contract['Value']} | Status: {contract['Status']}")
            st.progress(80 if contract['Status'] == 'Active' else 100)
            st.write("---")

# Halal Investments Module
elif app_module == "Halal Investments":
    st.markdown('<h2 class="sub-header">💹 Sukuk & Halal Investment Marketplace</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="module-card">
        <p>Discover and invest in Sharia-compliant investment opportunities with profit-sharing models instead of interest.</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Investment Opportunities", "My Portfolio", "Sukuk Marketplace"])
    
    with tab1:
        st.subheader("Available Investment Opportunities")
        
        # Sample investment opportunities
        opportunities = [
            {
                "name": "Sukuk Al-Ijarah - Government",
                "type": "Sukuk",
                "return": 8.5,
                "risk": "Low",
                "min_investment": 50000,
                "duration": "3 years",
                "description": "Government infrastructure project financing through Ijarah structure"
            },
            {
                "name": "Halal Equity Fund",
                "type": "Equity",
                "return": 12.2,
                "risk": "Medium",
                "min_investment": 10000,
                "duration": "5 years",
                "description": "Diversified portfolio of Sharia-compliant stocks"
            },
            {
                "name": "Islamic Real Estate Fund",
                "type": "Real Estate",
                "return": 7.8,
                "risk": "Medium",
                "min_investment": 50000,
                "duration": "7 years",
                "description": "Income-generating commercial real estate properties"
            },
            {
                "name": "Green Energy Sukuk",
                "type": "Sukuk",
                "return": 9.2,
                "risk": "Medium",
                "min_investment": 25000,
                "duration": "5 years",
                "description": "Financing for renewable energy projects"
            }
        ]
        
        for i, opportunity in enumerate(opportunities):
            with st.expander(f"{opportunity['name']} - Expected Return: {opportunity['return']}%", expanded=True if i==0 else False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Type:** {opportunity['type']}")
                    st.write(f"**Risk Level:** {opportunity['risk']}")
                    st.write(f"**Minimum Investment:** KES {opportunity['min_investment']:,}")
                    st.write(f"**Duration:** {opportunity['duration']}")
                    st.write(f"**Description:** {opportunity['description']}")
                
                with col2:
                    investment_amount = st.number_input(
                        f"Investment Amount (KES)",
                        min_value=opportunity['min_investment'],
                        value=opportunity['min_investment'],
                        step=1000,
                        key=f"invest_{i}"
                    )
                    
                    if st.button("Invest Now", key=f"btn_{i}"):
                        if investment_amount > st.session_state.user_data['savings']:
                            st.error("Insufficient funds for this investment")
                        else:
                            # Update user data
                            st.session_state.user_data['savings'] -= investment_amount
                            st.session_state.user_data['investments'] += investment_amount
                            
                            # Add to investments
                            new_investment = {
                                'name': opportunity['name'],
                                'amount': investment_amount,
                                'return': opportunity['return'],
                                'maturity': (datetime.now() + timedelta(days=365*3)).strftime("%Y-%m-%d")
                            }
                            st.session_state.investments.append(new_investment)
                            
                            st.success(f"Successfully invested KES {investment_amount:,} in {opportunity['name']}")
    
    with tab2:
        st.subheader("My Investment Portfolio")
        
        if not st.session_state.investments:
            st.info("You don't have any investments yet. Explore opportunities in the 'Investment Opportunities' tab.")
        else:
            # Portfolio summary
            total_invested = sum(inv['amount'] for inv in st.session_state.investments)
            avg_return = sum(inv['return'] * inv['amount'] for inv in st.session_state.investments) / total_invested
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Invested", f"KES {total_invested:,}")
            col2.metric("Number of Investments", len(st.session_state.investments))
            col3.metric("Average Return", f"{avg_return:.1f}%")
            
            # Investment breakdown
            st.subheader("Investment Breakdown")
            
            investment_names = [inv['name'] for inv in st.session_state.investments]
            investment_amounts = [inv['amount'] for inv in st.session_state.investments]
            
            fig = px.pie(
                values=investment_amounts, 
                names=investment_names,
                title="Portfolio Allocation"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Investment details
            st.subheader("Investment Details")
            investments_df = pd.DataFrame(st.session_state.investments)
            st.dataframe(investments_df, use_container_width=True)
    
    with tab3:
        st.subheader("Sukuk Marketplace")
        
        st.info("""
        Sukuk are Sharia-compliant bonds that represent partial ownership in an asset. 
        Unlike conventional bonds that pay interest, Sukuk provide returns through profit-sharing 
        or rental income from the underlying asset.
        """)
        
        # Sample Sukuk offerings
        sukuk_offerings = [
            {
                "name": "Kenya Government Ijarah Sukuk",
                "issue_date": "2023-11-01",
                "maturity": "2028-11-01",
                "yield": 8.7,
                "minimum": 50000,
                "rating": "AAA"
            },
            {
                "name": East African Community Infrastructure Sukuk",
                "issue_date": "2023-10-15",
                "maturity": "2030-10-15",
                "yield": 9.2,
                "minimum": 100000,
                "rating": "AA"
            },
            {
                "name": "Green Energy Wakala Sukuk",
                "issue_date": "2023-09-20",
                "maturity": "2026-09-20",
                "yield": 7.9,
                "minimum": 25000,
                "rating": "A"
            }
        ]
        
        for sukuk in sukuk_offerings:
            with st.expander(f"{sukuk['name']} - Yield: {sukuk['yield']}%"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Issue Date:** {sukuk['issue_date']}")
                    st.write(f"**Maturity:** {sukuk['maturity']}")
                
                with col2:
                    st.write(f"**Minimum Investment:** KES {sukuk['minimum']:,}")
                    st.write(f"**Credit Rating:** {sukuk['rating']}")
                
                with col3:
                    st.write(f"**Expected Yield:** {sukuk['yield']}%")
                    if st.button("View Details", key=f"sukuk_{sukuk['name']}"):
                        st.info(f"Detailed prospectus for {sukuk['name']} would be displayed here")

# Zakat Management Module
elif app_module == "Zakat Management":
    st.markdown('<h2 class="sub-header">💰 Zakat & Sadaqah Management Hub</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="module-card">
        <p>Calculate, track, and automate your Zakat contributions to eligible recipients and charitable causes.</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Zakat Calculator", "Zakat Payment", "Sadaqah & Donations"])
    
    with tab1:
        st.subheader("Zakat Calculator")
        
        st.info("""
        Zakat is obligatory for Muslims who meet the Nisab threshold (value of 87.48g of gold or 612.36g of silver).
        Typically calculated as 2.5% of wealth held for one lunar year.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Your Assets")
            cash_savings = st.number_input("Cash & Savings (KES)", min_value=0, value=st.session_state.user_data['savings'])
            gold_value = st.number_input("Gold Value (KES)", min_value=0, value=50000)
            silver_value = st.number_input("Silver Value (KES)", min_value=0, value=10000)
            investments_value = st.number_input("Investments (KES)", min_value=0, value=st.session_state.user_data['investments'])
            business_assets = st.number_input("Business Assets (KES)", min_value=0, value=0)
            other_assets = st.number_input("Other Assets (KES)", min_value=0, value=0)
        
        with col2:
            st.subheader("Your Liabilities")
            immediate_debts = st.number_input("Immediate Debts (KES)", min_value=0, value=0)
            bills_payable = st.number_input("Bills Payable (KES)", min_value=0, value=0)
            other_liabilities = st.number_input("Other Liabilities (KES)", min_value=0, value=0)
            
            st.subheader("Zakat Calculation")
            if st.button("Calculate My Zakat"):
                total_assets = cash_savings + gold_value + silver_value + investments_value + business_assets + other_assets
                total_liabilities = immediate_debts + bills_payable + other_liabilities
                net_wealth = total_assets - total_liabilities
                
                # Nisab threshold (using silver standard - approximately KES 15,000)
                nisab = 15000
                
                if net_wealth >= nisab:
                    zakat_payable = net_wealth * 0.025
                    
                    st.success(f"Your Zakat payable is: KES {zakat_payable:,.2f}")
                    
                    # Store for potential payment
                    st.session_state.calculated_zakat = zakat_payable
                else:
                    st.info(f"Your net wealth (KES {net_wealth:,.2f}) is below the Nisab threshold (KES {nisab:,.2f}). Zakat is not obligatory.")
    
    with tab2:
        st.subheader("Zakat Payment")
        
        if 'calculated_zakat' in st.session_state:
            st.metric("Your Calculated Zakat", f"KES {st.session_state.calculated_zakat:,.2f}")
            
            st.subheader("Select Recipient")
            recipient_type = st.selectbox(
                "Zakat Recipient Category",
                ["The Poor (Fuqara)", "The Needy (Masakin)", "Zakat Collectors", "Those whose hearts are to be reconciled", 
                 "Those in bondage", "The debt-ridden", "In the cause of Allah", "The wayfarer"]
            )
            
            st.subheader("Payment Method")
            payment_method = st.radio("Select Payment Method", ["M-Pesa", "Bank Transfer", "Debit Card", "Direct Deduction"])
            
            if st.button("Pay Zakat"):
                with st.spinner("Processing your Zakat payment..."):
                    time.sleep(2)
                    
                    # Update user data
                    st.session_state.user_data['zakat_paid'] += st.session_state.calculated_zakat
                    st.session_state.user_data['savings'] -= st.session_state.calculated_zakat
                    
                    st.success(f"Zakat payment of KES {st.session_state.calculated_zakat:,.2f} completed successfully!")
                    st.balloons()
                    
                    # Reset calculated zakat
                    del st.session_state.calculated_zakat
        else:
            st.info("Please calculate your Zakat first using the Zakat Calculator tab.")
    
    with tab3:
        st.subheader("Sadaqah & Donations")
        
        st.info("""
        Sadaqah is voluntary charity that can be given at any time, in any amount, to any worthy cause.
        Unlike Zakat, there are no specific rules or thresholds for Sadaqah.
        """)
        
        charities = [
            {"name": "Islamic Relief Kenya", "focus": "Poverty Alleviation", "rating": "★★★★★"},
            {"name": "Muslim Hands Africa", "focus": "Education & Healthcare", "rating": "★★★★☆"},
            {"name": "Local Mosque Fund", "focus": "Community Development", "rating": "★★★★☆"},
            {"name": "Orphan Support Program", "focus": "Child Welfare", "rating": "★★★★★"},
        ]
        
        selected_charity = st.selectbox("Select Charity", [charity["name"] for charity in charities])
        
        donation_amount = st.number_input("Donation Amount (KES)", min_value=100, value=1000, step=100)
        
        col1, col2 = st.columns(2)
        
        with col1:
            donation_frequency = st.selectbox("Donation Frequency", ["One-time", "Monthly", "Quarterly", "Annually"])
        
        with col2:
            payment_method = st.selectbox("Payment Method", ["M-Pesa", "Bank Transfer", "Debit Card"])
        
        if st.button("Make Donation"):
            if donation_amount > st.session_state.user_data['savings']:
                st.error("Insufficient funds for this donation")
            else:
                # Update user data
                st.session_state.user_data['savings'] -= donation_amount
                
                st.success(f"Thank you for your donation of KES {donation_amount:,} to {selected_charity}!")
                st.balloons()

# Education & Advisory Module
elif app_module == "Education & Advisory":
    st.markdown('<h2 class="sub-header">📚 Islamic Finance Education & Advisory</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="module-card">
        <p>Learn about Islamic finance principles and get personalized advice through our AI-powered Virtual Sharia Advisor.</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Learning Center", "Virtual Advisor", "Certification"])
    
    with tab1:
        st.subheader("Islamic Finance Learning Center")
        
        topics = [
            {
                "title": "Introduction to Islamic Finance",
                "level": "Beginner",
                "duration": "15 min",
                "description": "Basic principles and concepts of Islamic banking and finance"
            },
            {
                "title": "Understanding Riba (Interest)",
                "level": "Beginner",
                "duration": "20 min",
                "description": "Why interest is prohibited and alternatives in Islamic finance"
            },
            {
                "title": "Murabaha Financing",
                "level": "Intermediate",
                "duration": "25 min",
                "description": "Cost-plus financing structure and applications"
            },
            {
                "title": "Sukuk vs Conventional Bonds",
                "level": "Intermediate",
                "duration": "30 min",
                "description": "Key differences between Islamic and conventional bonds"
            },
            {
                "title": "Advanced Islamic Contracts",
                "level": "Advanced",
                "duration": "45 min",
                "description": "Musharakah, Mudarabah, and other partnership models"
            }
        ]
        
        for topic in topics:
            with st.expander(f"{topic['title']} ({topic['level']} - {topic['duration']})"):
                st.write(topic['description'])
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if st.button(f"Start Learning", key=f"learn_{topic['title']}"):
                        st.info(f"Starting lesson: {topic['title']}")
                
                with col2:
                    if st.button("Take Quiz", key=f"quiz_{topic['title']}"):
                        st.info(f"Quiz for {topic['title']} would open here")
        
        st.subheader("Video Resources")
        st.video("https://www.youtube.com/watch?v=2K7mtA1BBNU")  # Sample Islamic finance video
    
    with tab2:
        st.subheader("Virtual Sharia Advisor")
        
        st.info("""
        Our AI-powered advisor can answer your questions about Islamic finance principles, 
        product suitability, and Sharia compliance based on AAOIFI and IFSB standards.
        """)
        
        user_question = st.text_area(
            "Ask a question about Islamic finance:",
            "What's the difference between Murabaha and conventional loan?"
        )
        
        if st.button("Get Advice"):
            with st.spinner("Consulting Sharia principles..."):
                time.sleep(2)
                
                # Sample responses based on question keywords
                if "murabaha" in user_question.lower() and "conventional" in user_question.lower():
                    st.markdown("""
                    ### Murabaha vs Conventional Loan
                    
                    **Murabaha (Cost-Plus Financing):**
                    - The bank purchases an asset and sells it to you at a marked-up price
                    - The profit margin is fixed and agreed upon upfront
                    - No interest is charged
                    - The asset is owned by the bank until full payment
                    
                    **Conventional Loan:**
                    - The bank lends money which you use to purchase the asset
                    - Interest is charged on the loan amount
                    - You own the asset immediately
                    - The interest rate may be fixed or variable
                    
                    **Key Difference:** Murabaha is asset-based with transparent profit, while conventional loans are money-based with interest.
                    """)
                elif "sukuk" in user_question.lower():
                    st.markdown("""
                    ### Sukuk (Islamic Bonds)
                    
                    Sukuk are Sharia-compliant investment certificates that represent:
                    - Partial ownership in an underlying asset
                    - Rights to cash flows from the asset
                    - Unlike conventional bonds that pay interest, Sukuk provide returns through:
                      - Profit-sharing from business activities
                      - Rental income from real estate
                      - Other Sharia-compliant revenue streams
                    
                    Sukuk must be backed by tangible assets and cannot involve interest, uncertainty, or prohibited activities.
                    """)
                else:
                    st.markdown("""
                    ### General Islamic Finance Principles
                    
                    Islamic finance is guided by Sharia principles that prohibit:
                    - **Riba (Interest)**: Charging or paying interest
                    - **Gharar (Excessive Uncertainty)**: Speculative transactions
                    - **Haram Activities**: Investments in prohibited sectors
                    
                    Instead, Islamic finance uses:
                    - Asset-backed financing
                    - Profit-and-loss sharing
                    - Ethical investment screening
                    
                    Would you like more specific information about any of these principles?
                    """)
    
    with tab3:
        st.subheader("Islamic Banking Certification")
        
        st.info("""
        Enhance your knowledge with our certified courses in Islamic banking and finance.
        These courses are designed for banking professionals, students, and anyone interested
        in understanding Sharia-compliant financial systems.
        """)
        
        courses = [
            {
                "name": "Certified Islamic Finance Executive (CIFE)",
                "level": "Professional",
                "duration": "3 months",
                "fee": "KES 25,000"
            },
            {
                "name": "Sharia Advisory Certification",
                "level": "Advanced",
                "duration": "6 months",
                "fee": "KES 45,000"
            },
            {
                "name": "Islamic Banking Fundamentals",
                "level": "Beginner",
                "duration": "1 month",
                "fee": "KES 10,000"
            }
        ]
        
        for course in courses:
            with st.expander(f"{course['name']} ({course['level']})"):
                st.write(f"**Duration:** {course['duration']}")
                st.write(f"**Fee:** {course['fee']}")
                
                if st.button("Enroll Now", key=f"enroll_{course['name']}"):
                    st.success(f"Successfully enrolled in {course['name']}!")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #6B7280;">
        <p>Baraka FinTech - Islamic Banking Compliance & Empowerment Platform</p>
        <p>© 2023 Baraka FinTech. All rights reserved. | Sharia Advisory Board Certified</p>
    </div>
    """, 
    unsafe_allow_html=True
)