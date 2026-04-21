#!/usr/bin/env python
# coding: utf-8

# In[1]:


from abc import ABC, abstractmethod
import numpy as np

# -------------------------------
# 1. Investment Class
# -------------------------------
class Investment(ABC):
    # Initializes an Investment object with a name, amount, and return rate.
    # Validates name (not empty) and amount (non-negative).
    def __init__(self, name, amount, returnRate):
        if not name.strip() or amount < 0:
            print("Warning: Invalid name or amount provided to Investment constructor. Object may be in an invalid state.")
            self._is_valid = False # Indicate invalid state
        else:
            self._is_valid = True
        self._name = name
        self._amount = amount
        self._returnRate = returnRate

    # Abstract method to calculate the return of the investment.
    @abstractmethod
    def calculateReturn(self): pass

    # Abstract method to determine the risk level of the investment.
    @abstractmethod
    def riskLevel(self): pass

    # Returns a dictionary containing information about the investment.
    def getInfo(self):
        return {"type": self.__class__.__name__, "name": self._name, "amount": self._amount, "returnRate": self._returnRate}

    # Overloads the addition operator to combine two Investment amounts and calculate a weighted average return rate.
    def __add__(self, other):
        if not isinstance(other, Investment):
          return NotImplemented
        total = self._amount + other._amount
        if total:
            rate = ((self._amount*self._returnRate)+(other._amount*other._returnRate))/total
        else:
            rate = 0
        return {"combinedAmount": total, "combinedReturnRate": rate}

# -------------------------------
# 2. Stock, 3. MutualFund, 4. Crypto
# -------------------------------
class Stock(Investment):
    # Calculates the monetary return for a stock investment.
    def calculateReturn(self):
      return self._amount*(self._returnRate/100)
    # Returns the risk level for a stock investment.
    def riskLevel(self):
      return "High"

class MutualFund(Investment):
    # Calculates the monetary return for a mutual fund investment.
    def calculateReturn(self):
      return self._amount*(self._returnRate/100)
    # Returns the risk level for a mutual fund investment.
    def riskLevel(self):
      return "Medium"

class Crypto(Investment):
    # Calculates the monetary return for a cryptocurrency investment.
    def calculateReturn(self):
      return self._amount*(self._returnRate/100)
    # Returns the risk level for a cryptocurrency investment.
    def riskLevel(self):
      return "Very High"

# -------------------------------
# 5. User Class
# -------------------------------
class User:
    # Initializes a User object with a username and an optional roll number.
    # Validates that the username is not empty.
    def __init__(self, userName, rollNumber="22F-1234"):
        if not userName.strip():
            print("Warning: userName cannot be empty. Object may be in an invalid state.")
            self._is_valid = False
        else:
            self._is_valid = True
        self._userName = userName
        self._rollNumber = rollNumber
        self._portfolios = []

    # Adds a Portfolio object to the user's list of portfolios.
    def addPortfolio(self, portfolio):
        if type(portfolio).__name__ != "Portfolio":
            print("Warning: Attempted to add a non-Portfolio instance. Operation failed.")
            return False # Indicate failure
        self._portfolios.append(portfolio)
        return True # Indicate success

    # Returns a dictionary containing information about the user.
    def getUserInfo(self):
        return {"userName": self._userName, "rollNumber": self._rollNumber, "portfolioCount": len(self._portfolios)}

# -------------------------------
# 6. Portfolio Class
# -------------------------------
class Portfolio:
    # Initializes a Portfolio object with a name.
    # Validates that the portfolio name is not empty.
    def __init__(self, portfolioName):
        if not portfolioName.strip():
            print("Warning: portfolioName cannot be empty. Object may be in an invalid state.")
            self._is_valid = False
        else:
            self._is_valid = True
        self.portfolioName = portfolioName
        self.investments = []

    # Adds an Investment object to the portfolio's list of investments.
    def addInvestment(self, investment):
        if not isinstance(investment, Investment):
            print("Warning: Attempted to add a non-Investment instance. Operation failed.")
            return False
        self.investments.append(investment)
        return True

    # Removes an investment from the portfolio by its name.
    def removeInvestmentByName(self, name):
        for i, inv in enumerate(self.investments):
            if inv._name == name:
              del self.investments[i]
              return True
        return False

    # Calculates the total monetary return for all investments in the portfolio.
    def totalReturn(self):
        return sum(inv.calculateReturn() for inv in self.investments)

    # Calculates the average return rate, standard deviation of return rates, and total return for the portfolio.
    def calculateStatistics(self):
        if not self.investments:
          return 0,0,0
        rates = np.array([inv._returnRate for inv in self.investments])
        return float(np.mean(rates)), float(np.std(rates)), self.totalReturn()

    # Recursively finds the investment with the highest return rate in the portfolio.
    def findBestInvestment(self, index=0, best=None):
        if index >= len(self.investments):
          return best
        current = self.investments[index]
        if best is None or current._returnRate > best._returnRate: best = current
        return self.findBestInvestment(index+1, best)

    # Returns a list of dictionaries, each containing information about an investment in the portfolio.
    def listInvestments(self):
        return [inv.getInfo() for inv in self.investments]

# -------------------------------
# 7. FileManager Class
# -------------------------------
class FileManager:
    # Saves the given portfolio's data to a text file.
    @staticmethod
    def savePortfolioText(filename, portfolio):
        f = open(filename,"w",encoding="utf-8")
        f.write(f"{portfolio.portfolioName}\n")
        for inv in portfolio.investments:
            f.write(f"{inv.__class__.__name__}|{inv._name.replace('|','/')}|{inv._amount}|{inv._returnRate}\n")
        f.close()

    # Loads portfolio data from a text file and reconstructs a Portfolio object.
    @staticmethod
    def loadPortfolioText(filename):
        f = open(filename,"r",encoding="utf-8")
        lines = [l.rstrip("\n") for l in f]
        f.close()
        if not lines:
            print("Warning: File is empty or could not be read. Returning None.")
            return None # Indicate failure to load
        p = Portfolio(lines[0] or "LoadedPortfolio")
        for line in lines[1:]:
            if line.strip(): # Process only non-empty lines
                parts = line.split("|")
                if len(parts) >= 4: # Process only lines with enough parts
                    invType, name, amount, rate = parts[0], parts[1], float(parts[2]), float(parts[3])
                    invType = invType.lower()
                    if invType=="stock":
                        inv = Stock(name,amount,rate)
                    elif invType=="mutualfund":
                        inv = MutualFund(name,amount,rate)
                    elif invType=="crypto":
                        inv = Crypto(name,amount,rate)
                    else:
                        print(f"Warning: Unknown investment type '{invType}' for line: {line}. Skipping investment.")
                        continue # Skip to the next line if type is unknown
                    p.addInvestment(inv)
        return p

# -------------------------------
# 8. ReportGenerator Class
# -------------------------------
class ReportGenerator:
    # Generates a detailed report for a given portfolio.
    @staticmethod
    def generatePortfolioReport(portfolio):
        avg,risk,total = portfolio.calculateStatistics()
        lines = [f"--- Portfolio Report: {portfolio.portfolioName} ---",
                 f"Number of Investments: {len(portfolio.investments)}",
                 f"Total Annual Return: {total:.2f}", f"Average Return Rate (%): {avg:.2f}",
                 f"Portfolio Risk: {risk:.2f}", "", "Investments:"]
        for inv in portfolio.investments:
            lines.append(f" - {inv._name} | Type: {inv.__class__.__name__} | Amount: {inv._amount:.2f} | ReturnRate: {inv._returnRate:.2f}% | Risk: {inv.riskLevel()}")
        best = portfolio.findBestInvestment()
        if best: lines.append(f"\nBest Investment: {best._name} ({best._returnRate:.2f}%)")
        return "\n".join(lines)

    # Saves the generated report text to a specified file.
    @staticmethod
    def saveReportText(filename, reportText):
        f = open(filename,"w",encoding="utf-8")
        f.write(reportText)
        f.close()

# -------------------------------
# 9. InvestmentAnalyzer Class
# -------------------------------
class InvestmentAnalyzer:
    # Compares the returns of two investments, or returns the return of a single investment.
    def compareReturns(self, inv1, inv2=None):
        r1 = inv1.calculateReturn()
        if inv2: r1 -= inv2.calculateReturn()
        return r1
    # Returns the risk level of a given investment.
    def showRisk(self, investment):
      return investment.riskLevel()
    # Filters a list of investments and returns only those with 'High' or 'Very High' risk levels.
    def findHighRisk(self, investments):
      return [inv for inv in investments if inv.riskLevel() in ("High","Very High")]
    # Demonstrates the overloaded addition operator for combining two investments.
    def analyzerAddExample(self, inv1, inv2):
      return inv1+inv2

# -------------------------------
# Interactive CLI
# -------------------------------
def main():
    # Main function for the interactive command-line interface.
    print("=== SIPMS Final Project ===")
    userName = input("Enter your name: ").strip()
    user = User(userName)
    pName = input("Enter portfolio name: ").strip() or "MyPortfolio"
    portfolio = Portfolio(pName)
    user.addPortfolio(portfolio)

    while True:
        print("\nMenu:")
        print("1) Add Investment  2) List Investments  3) Show Stats & Best")
        print("4) Save Portfolio  5) Edit Investment  6) Rank Investments  7) Exit")
        choice = input("Choose: ").strip()

        # Handles adding a new investment to the portfolio.
        if choice=="1":
            invType = input("Type(stock/mutualfund/crypto): ").strip().lower()
            name = input("Investment name: ").strip()
            amount = float(input("Amount invested: ").strip())
            rate = float(input("Return rate(%): ").strip())
            inv = Stock(name,amount,rate) if invType=="stock" else MutualFund(name,amount,rate) if invType=="mutualfund" else Crypto(name,amount,rate)
            portfolio.addInvestment(inv)
            print("Added.")

        # Handles listing all investments in the portfolio.
        elif choice=="2":
            for inv in portfolio.investments: print(inv.getInfo(), "| Risk:", inv.riskLevel())

        # Handles displaying portfolio statistics and the best investment.
        elif choice=="3":
            avg,risk,total = portfolio.calculateStatistics()
            best = portfolio.findBestInvestment()
            print(f"Total Annual Money: {total:.2f}")
            print(f"Average Return Rate: {avg:.2f}%  | Risk: {risk:.2f}")
            if best: print(f"Best Investment: {best._name} ({best._returnRate:.2f}%)")

        # Handles saving the portfolio to a text file.
        elif choice=="4":
            fname = input("Filename to save: ").strip() or portfolio.portfolioName+".txt"
            FileManager.savePortfolioText(fname, portfolio)
            print(f"Saved to {fname}")

        # Handles editing an existing investment's amount.
        elif choice=="5":
            name = input("Investment name to edit: ").strip()
            found = False
            for inv in portfolio.investments:
                if inv._name == name:
                    addAmount = float(input(f"Enter amount to add/subtract to '{name}': ").strip())
                    inv._amount += addAmount
                    print(f"Updated {name} amount to {inv._amount}")
                    found = True
                    break
            if not found: print("Investment not found")

        # Handles ranking investments by annual monetary return.
        elif choice=="6":
            ranked = sorted(portfolio.investments, key=lambda x: x.calculateReturn(), reverse=True)
            print("Investments ranked by annual monetary return:")
            for i, inv in enumerate(ranked,1):
                print(f"{i}. {inv._name} | Type: {inv.__class__.__name__} | Amount: {inv._amount:.2f} | ReturnRate: {inv._returnRate:.2f}% | Annual Money: {inv.calculateReturn():.2f}")

        # Handles exiting the program.
        elif choice=="7":
            print("Exiting. Good luck with submission.")
            break

        # Handles invalid menu choices.
        else:
            print("Invalid choice")

if __name__ == "__main__":
     main()


# In[ ]:




