# Personal Finance Dashboard Using Python and Dash

Ever have trouble understanding and maintaining a personal budget, your investments, and understanding your net wealth?  Over the past years, I've built up a tool that has helped me manage my personal financial situation, providing me with everything I've needed to stay on top of my finances and expenses.  This tool has allowed me to work on my programming skills, building up my development, testing, and deployment capabilities while being useful in my every day life.  Not often do those two components align perfectly, so I hope you can improve and enhance this to benefit your skillset and your personal finances.

## 1. Introduction

With the use of Quicken, I've been able to connect all of my accounts (savings, checking, credit cards, investments, retirement, etc.) across the US and Singapore.  Quicken has good connectors to automatically download transactions and a simple enough interface to get some basic information; however, it lacked a number of key features that helped me better understand my budget and finances.  I used Quicken to download all of the account transactions and I exported the information in a .QIF file.  I wrote a separate algorithm to parse this output into distinct readable files (CSVs).  With these files, I developed a dashboard to process my budget, spending, account information, and investment progress.  This dashboard utilizes Plotly's Open Source Dash tool, a low-code framework for rapidly building data apps in Python.  This app is interactive, allowing me to slice and dice my information to better understand my situation.  

## 2. Project Set Up

The Quicken component, while immensely helpful for me, isn't necessarily required.  This tool relies on a number of CSVs, which can be updated directly based on your financial statements and transactions.  While that may need to be done manually, it still allows you to use this tool to its full extent.

The required Files are:
** Budget.xlsx - A file containing all of your budgeting decisions.  This file is in a long data format and each month needs to be updated based on your budgeting needs.  This file can be built and adjusted using the app, as the budgeting page in the tool will automatically overwrite and update this file.
** Spending File.csv - A file with all of your transaction details across all of your accounts.
** Account File.csv - A file that contains all of your balances by month across all of your accounts.  While not directly useful in my day to day, a yearly review of my overall net wealth is helpful.
** Hierarchy.csv - A file that describes the categories that I use and the details about them.  For example, I have a category "Health & Fitness" with a subcategory "Doctor", which has a monthly budget and is considered an expense.  This file helps my categorize and group these budget categories.
** Investment File.csv - A file that is used to show all of my investment and trading transactions.  It supports stocks, dividends, bonds, options, and mutual funds.

## 3. Architectural Design

The app is built to be modular and re-usable.  Should you wish to not use investments, account details, or any other component, you can amend the code to remove those and it will still function.  This improves the usability and enables less code to be written.

The overall structure of the app is:

personal-finance-dashboard/
|---apps/
    |---account.py      # Account Details
    |---actual.py       # Actual Income v Actual Expense
    |---budget.py       # Budget Income v Budget Expense
    |---detail.py      # A Detail wrapper page to break down actual vs budget for income vs expenses
    |---expense.py     # Actual Expense v Budgeted Expense
    |---income.py       # Acutal Income v Budgeted Income
    |---investment.py  # Investments
    |---summary.py      # High level summary of income vs expenses for actual and budget
|---assets/
    |---favicon.ico
    |---Loading.gif
    |---style.css
|---datasets/
    |---Budget.csv
    |---Spending.csv
    |---Account.csv
    |---Hiearchy.csv
    |---Investment.csv
|---app.py
|---index.py

## 4. How to Use

The main purpose of this app is to support your monthly budgeting and investment operations and monitoring.  The dashboards provide easily slice and dice capabilities to better understand how you spent your money, while still understanding your broader budget.

For first time use, I'd recommend looking at the "Budget" page to set a reasonable budget.  My overall preference is to have 10% of my income go into savings and 10% go towards retirement/investment.  The rest will be used to offset spending.  When setting up the budget, it's important to include all things which you could spend money on, whether they're monthly or one off purchases.  When you come to a budget that works for you, you can save the budget and then monitor your spending vs that budget over time.

Once my budget is set, every month I'll review my previous month's performance to the budget to see if I've over- or under-budgeted.  When looking category by category and month by month (or quarter, etc.), you can see if the over- and under-budgeted items cancel out or show a trend.  This enables me to review my budget and adjust, thus becoming a cycle of review and adjust.  While it takes some time initially to get into the groove, it's smooth sailing to maintain.

The investment component helps to show individual and aggregate performance as compared to a benchmark (S&P500).  This allows you to get a relative understanding of how we'll your stocks have been doing.  This is an area that I continually try to evolve as my personal investment strategy changes over time.  I don't use this to actively explore new stocks and opportunities, as professional investing platforms have a lot more time and money to throw at that problem.  The beauty of this app, is it allows me to customize the output to see exactly what I want to see.  As some of my investments are multi-year, looking at total growth is very misleading (e.g. 2 stocks can have 50% growth but if I've held one for 3 years and 1 for 1 month, their actual returns are quite different).  I've often been frustrated by investment platforms not showing Cumulative Annual Growth Rates (CAGR) or a similar annualized growth rate because it misleads how your stocks have been performing and how to update your investments.  I continually adjust this app to better account for new strategies and outputs I'd like to see, such as including an Covered Call Options Income approach and looking at how realized vs unrealized gains/losses per year have performed.

## 5. Deployment

While not directly shown here, I've used a Raspberry Pi within my home network to host my app.  This is inaccessible to the outside internet, which allows me to ensure my information is safe and secure.  I've adjusted the DNS on my router to use my Raspberry Pi, which allows me to put an easy custom url to access the app.  My raspberry pi uses RSync to automatically pull updates that I've made throughout the day and redeploy the app every morning.

## 6. Improvements

If you have any improvements or ideas to recommend, let me know!