#!/usr/bin/env python3

import json
from datetime import datetime, timedelta
import os # Import os module for file operations

# Try to import matplotlib for the bonus graphing feature.
# If it's not installed, the graphing feature will be disabled.
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Base file names (these will be dynamically prefixed with the username)
BASE_EXPENSE_FILE = "_expenses.json"
BASE_BUDGET_FILE = "_budgets.json"
USERS_FILE = "users.json" # To store the list of registered users

# Global variables to hold the current user's file paths
CURRENT_EXPENSE_FILE = ""
CURRENT_BUDGET_FILE = ""
CURRENT_USERNAME = None

def load_data(filename):
    """Loads data from a JSON file. Returns empty dict/list if file doesn't exist or is invalid."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return appropriate empty structure based on file type
        if BASE_EXPENSE_FILE in filename: # Check if it's an expense file
            return []
        elif BASE_BUDGET_FILE in filename: # Check if it's a budget file
            return {}
        elif filename == USERS_FILE: # Check if it's the users file
            return [] # List of usernames
        return {} # Default fallback

def save_data(data, filename):
    """Saves data to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def get_valid_amount(prompt):
    """Prompts for a positive numeric amount."""
    while True:
        try:
            amount = float(input(prompt))
            if amount <= 0:
                print("Amount must be a positive number. Please try again.")
                continue
            return amount
        except ValueError:
            print("Invalid input. Please enter a valid number for the amount.")

def get_valid_date(prompt, default_date=None):
    """
    Prompts the user for a date and validates the format.
    Allows 'today' or 'yesterday' as input.
    """
    if default_date:
        prompt_text = f"{prompt} (YYYY-MM-DD, 'today', 'yesterday') [default: {default_date}]: "
    else:
        prompt_text = f"{prompt} (YYYY-MM-DD, 'today', 'yesterday') [default: today]: "

    while True:
        date_input = input(prompt_text).strip().lower()
        if not date_input:
            return default_date if default_date else datetime.now().strftime('%Y-%m-%d')
        elif date_input == 'today':
            return datetime.now().strftime('%Y-%m-%d')
        elif date_input == 'yesterday':
            return (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            try:
                datetime.strptime(date_input, '%Y-%m-%d')
                return date_input
            except ValueError:
                print("Oops! Invalid date format. Please use YYYY-MM-DD, 'today', or 'yesterday'.")

def get_valid_category():
    """Prompts for a category, offering common choices or a custom input."""
    print("\n--- Choose a Category ---")
    common_categories = ["Food", "Transport", "Entertainment", "Utilities", "Rent", "Groceries", "Shopping", "Health", "Education", "Other"]
    for i, cat in enumerate(common_categories):
        print(f"  {i+1}. {cat}")
    print("  'C' for Custom Category")

    while True:
        category_choice = input("Enter category number or 'C' for custom: ").strip().lower()
        if category_choice == 'c':
            category = input("Enter your custom category name: ").strip().title()
            if category:
                return category
            else:
                print("Custom category cannot be empty. Please try again.")
        elif category_choice.isdigit():
            idx = int(category_choice) - 1
            if 0 <= idx < len(common_categories):
                return common_categories[idx]
            else:
                print("Invalid category number. Please try again.")
        else:
            print("Invalid choice. Please enter a number or 'C'.")


def add_expense(expenses):
    """Prompts the user to add a new expense and adds it to the list."""
    print("\n--- ➕ Add a New Expense ---")
    amount = get_valid_amount("Enter the amount: ₹")
    category = get_valid_category()
    date = get_valid_date("Enter the date")

    new_expense = {
        "amount": amount,
        "category": category,
        "date": date
    }
    expenses.append(new_expense)
    print(f"🎉 Success! You've logged ₹{amount:.2f} for '{category}' on {date}.")

def view_summary(expenses):
    """
    Displays a summary of total spending and spending by category.
    Also offers detailed views and a graphical summary if matplotlib is available.
    """
    if not expenses:
        print("\n😔 No expenses recorded yet. Start by adding one!")
        return

    print("\n--- 📊 Expense Summary ---")
    total_spending = sum(item['amount'] for item in expenses)
    print(f"💰 Overall Total Spending: ₹{total_spending:.2f}")

    # Calculate spending by category
    category_spending = {}
    for item in expenses:
        category = item['category']
        amount = item['amount']
        category_spending[category] = category_spending.get(category, 0) + amount
    
    print("\nSpending by Category:")
    # Sort categories by spending amount, descending
    sorted_categories = sorted(category_spending.items(), key=lambda item: item[1], reverse=True)
    for category, total in sorted_categories:
        print(f"  - {category}: ₹{total:.2f}")

    print("\n--- Detailed Summary Options ---")
    print("  1. View Monthly Spending")
    print("  2. View Annual Spending")
    print("  3. View All Expenses (Sorted by Date)")
    if MATPLOTLIB_AVAILABLE:
        print("  4. Show Graphical Summary (Pie Chart)")
    print("  5. Return to Main Menu")

    while True:
        summary_choice = input("Your choice: ").strip()
        if summary_choice == '1':
            view_monthly_summary(expenses)
            break
        elif summary_choice == '2':
            view_annual_summary(expenses)
            break
        elif summary_choice == '3':
            view_all_expenses_detailed(expenses)
            break
        elif summary_choice == '4' and MATPLOTLIB_AVAILABLE:
            plot_expense_summary(category_spending)
            break
        elif summary_choice == '5' or (summary_choice == '4' and not MATPLOTLIB_AVAILABLE):
            break
        else:
            print("Invalid choice. Please select a valid option.")

def view_monthly_summary(expenses):
    """Displays spending aggregated by month."""
    if not expenses:
        print("\nNo expenses to summarize by month.")
        return

    monthly_spending = {}
    for item in expenses:
        month_year = datetime.strptime(item['date'], '%Y-%m-%d').strftime('%Y-%m')
        monthly_spending[month_year] = monthly_spending.get(month_year, 0) + item['amount']

    print("\n--- Monthly Spending Overview ---")
    for month_year in sorted(monthly_spending.keys()):
        print(f"  🗓️ {month_year}: ₹{monthly_spending[month_year]:.2f}")

def view_annual_summary(expenses):
    """Displays spending aggregated by year."""
    if not expenses:
        print("\nNo expenses to summarize by year.")
        return

    annual_spending = {}
    for item in expenses:
        year = datetime.strptime(item['date'], '%Y-%m-%d').strftime('%Y')
        annual_spending[year] = annual_spending.get(year, 0) + item['amount']

    print("\n--- Annual Spending Overview ---")
    for year in sorted(annual_spending.keys()):
        print(f"  📅 {year}: ₹{annual_spending[year]:.2f}")

def view_all_expenses_detailed(expenses):
    """Lists all expenses with their details, sorted by date."""
    if not expenses:
        print("\nNo expenses to list.")
        return
    
    print("\n--- All Recorded Expenses (Sorted by Date) ---")
    # Sort expenses by date for better readability
    sorted_expenses = sorted(expenses, key=lambda x: x['date'])
    for i, expense in enumerate(sorted_expenses):
        print(f"  {i + 1}. Date: {expense['date']} | Category: {expense['category']} | Amount: ₹{expense['amount']:.2f}")


def plot_expense_summary(category_spending):
    """
    Generates and displays a pie chart of expenses by category.
    """
    if not category_spending:
        print("\nNo category data to plot.")
        return

    labels = category_spending.keys()
    sizes = category_spending.values()

    fig, ax = plt.subplots(figsize=(8, 8)) # Make chart a bit bigger
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
            wedgeprops={"edgecolor": "white", 'linewidth': 1.5}, textprops={'fontsize': 10})
    # Removing emoji from title to avoid font warnings
    plt.title(f"Expense Distribution for {CURRENT_USERNAME}'s Categories", fontsize=16, pad=20) 
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    
    plt.show()

def manage_expenses(expenses):
    """
    Provides options to view, edit, or delete existing expenses.
    """
    if not expenses:
        print("\n😔 No expenses to manage yet.")
        return

    while True:
        print("\n--- 📝 Manage Expenses ---")
        print("Here are your current expenses:")
        # Sort expenses by date for easier management
        sorted_expenses = sorted(expenses, key=lambda x: x['date'], reverse=True)
        for i, expense in enumerate(sorted_expenses):
            print(f"  {i + 1}. ₹{expense['amount']:.2f} - {expense['category']} ({expense['date']})")
            
        print("\nSelect an option:")
        print("  'E' to Edit an expense")
        print("  'D' to Delete an expense")
        print("  'Q' to return to the Main Menu")
        
        choice = input("Your choice: ").lower()

        if choice == 'q':
            break
        elif choice in ['e', 'd']:
            try:
                idx_to_manage = int(input("Enter the number of the expense to manage: ")) - 1
                if not 0 <= idx_to_manage < len(sorted_expenses):
                    print("Invalid number. Please enter a valid number from the list.")
                    continue
                
                # Find the original index in the 'expenses' list, as 'sorted_expenses' is a copy
                original_expense = sorted_expenses[idx_to_manage]
                original_idx = expenses.index(original_expense)

                if choice == 'd':
                    confirm = input(f"Are you sure you want to delete the expense: ₹{original_expense['amount']:.2f} - {original_expense['category']} ({original_expense['date']})? (y/n): ").lower()
                    if confirm == 'y':
                        deleted_expense = expenses.pop(original_idx)
                        print(f"🗑️ Expense of ₹{deleted_expense['amount']:.2f} in '{deleted_expense['category']}' deleted successfully.")
                        # After deletion, it's good to re-display or exit to main menu
                        break 
                    else:
                        print("Deletion cancelled.")
                        continue
                        
                elif choice == 'e':
                    print("\n✏️ Enter new details (leave blank to keep current value):")
                    
                    new_amount_str = input(f"Enter new amount (current: ₹{expenses[original_idx]['amount']:.2f}): ")
                    if new_amount_str:
                        try:
                            new_amount = float(new_amount_str)
                            if new_amount <= 0:
                                print("Amount must be positive. Keeping current amount.")
                            else:
                                expenses[original_idx]['amount'] = new_amount
                        except ValueError:
                            print("Invalid amount format. Keeping current amount.")

                    new_category = input(f"Enter new category (current: {expenses[original_idx]['category']}): ").strip().title()
                    if new_category:
                        expenses[original_idx]['category'] = new_category

                    new_date = get_valid_date(f"Enter new date", expenses[original_idx]['date'])
                    if new_date != expenses[original_idx]['date']: # Only update if it's actually new
                         expenses[original_idx]['date'] = new_date

                    print("✅ Expense updated successfully.")
                    break # Exit management loop after edit

            except (ValueError, IndexError):
                print("Invalid input. Please enter a valid number.")
        else:
            print("Invalid choice. Please try again.")

def set_budget(budgets):
    """Allows users to set or update budget limits for categories."""
    print("\n--- 💰 Set Category Budgets ---")
    category = input("Enter the category to set a budget for (e.g., Food, Transport): ").strip().title()
    while True:
        try:
            limit = float(input(f"Enter budget limit for '{category}': ₹"))
            if limit < 0:
                print("Budget limit cannot be negative.")
                continue
            break
        except ValueError:
            print("Invalid amount. Please enter a number.")
    
    budgets[category] = limit
    print(f"💰 Budget of ₹{limit:.2f} set for '{category}'.")

def check_budgets(expenses, budgets):
    """Checks current spending against set budgets."""
    if not budgets:
        print("\nNo budgets set yet. Use option 4 to set one!")
        return
    
    print("\n--- 📈 Budget vs. Spending Overview ---")
    current_spending = {}
    for item in expenses:
        category = item['category']
        current_spending[category] = current_spending.get(category, 0) + item['amount']
    
    for category, limit in budgets.items():
        spent = current_spending.get(category, 0)
        remaining = limit - spent
        status = ""
        if remaining < 0:
            status = f"🚨 OVER budget by ₹{abs(remaining):.2f}!"
        elif remaining == 0:
            status = "🎯 Exactly on budget!"
        else:
            status = f"✅ ₹{remaining:.2f} remaining."
        
        print(f"  {category}: Spent ₹{spent:.2f} / Budget ₹{limit:.2f} - {status}")

def reset_user_data(username):
    """Deletes the expense and budget files for a given user."""
    global CURRENT_EXPENSE_FILE, CURRENT_BUDGET_FILE
    
    expense_file_path = f"{username}{BASE_EXPENSE_FILE}"
    budget_file_path = f"{username}{BASE_BUDGET_FILE}"

    print(f"\n--- ⚠️ Resetting Data for {username} ---")
    confirm = input(f"Are you absolutely sure you want to delete ALL expense and budget data for '{username}'? This cannot be undone! (type 'YES' to confirm): ")
    
    if confirm == 'YES':
        try:
            if os.path.exists(expense_file_path):
                os.remove(expense_file_path)
                print(f"🗑️ Deleted {expense_file_path}")
            else:
                print(f"No expense data found for '{username}' to delete.")

            if os.path.exists(budget_file_path):
                os.remove(budget_file_path)
                print(f"🗑️ Deleted {budget_file_path}")
            else:
                print(f"No budget data found for '{username}' to delete.")

            print(f"✅ All data for '{username}' has been reset.")
            return True # Indicate successful reset
        except Exception as e:
            print(f"❌ Error resetting data: {e}")
            return False
    else:
        print("Reset cancelled. Your data is safe.")
        return False

def delete_user_profile(users_list, username_to_delete):
    """Deletes a user's data files and removes them from the users list."""
    global CURRENT_USERNAME

    print(f"\n--- ⚠️ Deleting User Profile: {username_to_delete} ---")
    confirm = input(f"Are you absolutely sure you want to delete the user '{username_to_delete}' and ALL their data? This cannot be undone! (type 'DELETE USER' to confirm): ")

    if confirm == 'DELETE USER':
        # 1. Delete user's data files
        expense_file_path = f"{username_to_delete}{BASE_EXPENSE_FILE}"
        budget_file_path = f"{username_to_delete}{BASE_BUDGET_FILE}"

        try:
            if os.path.exists(expense_file_path):
                os.remove(expense_file_path)
                print(f"🗑️ Deleted {expense_file_path}")
            if os.path.exists(budget_file_path):
                os.remove(budget_file_path)
                print(f"🗑️ Deleted {budget_file_path}")
            
            # 2. Remove user from the users list
            if username_to_delete in users_list:
                users_list.remove(username_to_delete)
                save_data(users_list, USERS_FILE)
                print(f"🗑️ User '{username_to_delete}' removed from user list.")
                
                # If the deleted user was the active one, log them out
                if CURRENT_USERNAME == username_to_delete:
                    CURRENT_USERNAME = None
                    print("Current user logged out due to profile deletion.")

                print(f"✅ User profile '{username_to_delete}' has been completely deleted.")
                return True
            else:
                print(f"User '{username_to_delete}' not found in the user list.")
                return False

        except Exception as e:
            print(f"❌ Error deleting user profile: {e}")
            return False
    else:
        print("User profile deletion cancelled.")
        return False


def user_management_menu():
    """Handles user selection, creation, and deletion."""
    global CURRENT_EXPENSE_FILE, CURRENT_BUDGET_FILE, CURRENT_USERNAME

    users = load_data(USERS_FILE)

    while True:
        print("\n--- 👤 User Management ---")
        if users:
            print("Existing Users:")
            for i, user in enumerate(users):
                print(f"  {i+1}. {user}")
        else:
            print("No users found. Let's create one!")

        print("\nOptions:")
        print("  1. Select an existing user")
        print("  2. Create a new user")
        print("  3. Delete a user profile (careful!)")
        print("  4. Exit to main menu")

        choice = input("Your choice: ").strip()

        if choice == '1':
            if not users:
                print("No users to select. Please create a user first.")
                continue
            
            while True:
                user_choice = input("Enter the number of the user to select: ").strip()
                if user_choice.isdigit():
                    idx = int(user_choice) - 1
                    if 0 <= idx < len(users):
                        CURRENT_USERNAME = users[idx]
                        CURRENT_EXPENSE_FILE = f"{CURRENT_USERNAME}{BASE_EXPENSE_FILE}"
                        CURRENT_BUDGET_FILE = f"{CURRENT_USERNAME}{BASE_BUDGET_FILE}"
                        print(f"🌟 Welcome back, {CURRENT_USERNAME}! Your financial journey continues.")
                        return True # User selected, exit management menu
                    else:
                        print("Invalid user number. Please try again.")
                else:
                    print("Invalid input. Please enter a number.")

        elif choice == '2':
            while True:
                new_username = input("Enter a new username (alphanumeric, no spaces): ").strip()
                if not new_username.isalnum():
                    print("Username must be alphanumeric (letters and numbers only). No spaces or special characters.")
                elif new_username in users:
                    print("This username already exists. Please choose a different one.")
                else:
                    users.append(new_username)
                    save_data(users, USERS_FILE)
                    CURRENT_USERNAME = new_username
                    CURRENT_EXPENSE_FILE = f"{CURRENT_USERNAME}{BASE_EXPENSE_FILE}"
                    CURRENT_BUDGET_FILE = f"{CURRENT_USERNAME}{BASE_BUDGET_FILE}"
                    print(f"🎉 User '{new_username}' created and selected successfully!")
                    return True # New user created and selected

        elif choice == '3':
            if not users:
                print("No users to delete.")
                continue
            print("\n--- Users Available for Deletion ---")
            for i, user in enumerate(users):
                print(f"  {i+1}. {user}")
            
            while True:
                user_to_delete_idx = input("Enter the number of the user to DELETE (or 'q' to cancel): ").strip().lower()
                if user_to_delete_idx == 'q':
                    print("User deletion cancelled.")
                    break
                elif user_to_delete_idx.isdigit():
                    idx = int(user_to_delete_idx) - 1
                    if 0 <= idx < len(users):
                        username_to_delete = users[idx]
                        delete_user_profile(users, username_to_delete)
                        users = load_data(USERS_FILE) # Reload users list after deletion
                        if not users: # If no users left, return to main loop to force user creation/selection
                            return False 
                        break # Exit inner loop, continue user management menu
                    else:
                        print("Invalid user number. Please try again.")
                else:
                    print("Invalid input.")

        elif choice == '4':
            return False # Exit user management menu to main loop

        else:
            print("Invalid choice. Please try again.")

def main():
    """
    Main function to run the Personal Expense Tracker application.
    """
    global CURRENT_USERNAME, CURRENT_EXPENSE_FILE, CURRENT_BUDGET_FILE

    print("--- 👋 Welcome to your Personal Expense Tracker! ---")

    # Initial user selection/creation
    if not user_management_menu():
        print("Exiting application. Please select or create a user to proceed next time.")
        return # Exit if user doesn't select/create a user

    # Main application loop for the selected user
    while CURRENT_USERNAME: # Loop continues as long as a user is logged in
        expenses = load_data(CURRENT_EXPENSE_FILE)
        budgets = load_data(CURRENT_BUDGET_FILE)

        print(f"\n🌟 --- {CURRENT_USERNAME}'s Dashboard --- 🌟")
        print("What would you like to do today?")
        print("  1. ➕ Add a New Expense")
        print("  2. 📊 View Expense Summary")
        print("  3. 📝 Manage (Edit/Delete) Expenses")
        print("  4. 💰 Set Category Budget")
        print("  5. 📈 Check Budgets")
        print("  6. 🧹 Reset My Data (Delete all my expenses/budgets)") # New option
        print("  7. 🔄 Switch User / User Management") # New option
        print("  8. 👋 Exit Application")
        
        choice = input("Please choose an option: ")
        
        if choice == '1':
            add_expense(expenses)
            save_data(expenses, CURRENT_EXPENSE_FILE)
        elif choice == '2':
            view_summary(expenses)
        elif choice == '3':
            manage_expenses(expenses)
            save_data(expenses, CURRENT_EXPENSE_FILE)
        elif choice == '4':
            set_budget(budgets)
            save_data(budgets, CURRENT_BUDGET_FILE)
        elif choice == '5':
            check_budgets(expenses, budgets)
        elif choice == '6':
            if reset_user_data(CURRENT_USERNAME):
                # If data reset successful, force reload of expenses/budgets for current user
                expenses = [] # Clear in memory
                budgets = {} # Clear in memory
                print(f"You can now add new expenses for {CURRENT_USERNAME}.")
            else:
                print("Data reset failed or cancelled.")
        elif choice == '7':
            # This will return to the user management menu. If a user is selected, it will loop back here.
            # If user chooses to exit user management, CURRENT_USERNAME might become None, breaking this loop.
            if not user_management_menu():
                print("Exiting application. Goodbye! 😊")
                break # Exit the main application loop
        elif choice == '8':
            print(f"Goodbye, {CURRENT_USERNAME}! Thanks for tracking your finances with us. See you next time! 😊")
            break
        else:
            print("🚫 Invalid choice. Please enter a number from 1 to 8.")

if __name__ == "__main__":
    main()