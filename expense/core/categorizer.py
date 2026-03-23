def categorize(description):
    desc = description.lower()
    food_keywords = [
        'swiggy', 'zomato', 'dominos', 'pizza', 'burger',
        'restaurant', 'cafe', 'food', 'kitchen', 'hotel',
        'biryani', 'canteen', 'mess', 'tiffin', 'mcdonalds',
        'kfc', 'subway', 'chai', 'coffee', 'bakery'
    ]
    shopping_keywords = [
        'amazon', 'flipkart', 'myntra', 'meesho', 'ajio',
        'nykaa', 'shopping', 'store', 'mart', 'bazaar',
        'clothes', 'fashion', 'electronics', 'mobile'
    ]
    recharge_keywords = [
        'recharge', 'airtel', 'jio', 'vi ', 'bsnl',
        'electricity', 'bescom', 'mseb', 'dth', 'tata sky',
        'dish tv', 'broadband', 'internet', 'bill payment'
    ]
    entertainment_keywords = [
        'netflix', 'spotify', 'prime', 'hotstar', 'disney',
        'youtube', 'gaana', 'wynk', 'zee5', 'sonyliv',
        'bookmyshow', 'movie', 'pvr', 'inox', 'gaming'
    ]

    transport_keywords = [
        'ola', 'uber', 'rapido', 'fuel', 'petrol', 'diesel',
        'namma metro', 'bmtc', 'irctc', 'train', 'flight',
        'makemytrip', 'redbus', 'parking', 'toll'
    ]

    friends_keywords = [
        'sent to', 'received from', 'transfer', 'pay to',
        'split', 'lend', 'borrow'
    ]

    emi_keywords = [
        'emi', 'loan', 'hdfc', 'icici', 'sbi', 'axis bank',
        'bajaj', 'finance', 'installment', 'credit card'
    ]

    
    health_keywords = [
        'pharmacy', 'medical', 'hospital', 'doctor', 'clinic',
        'medicine', 'apollo', 'netmeds', '1mg', 'pharmeasy'
    ]

   
    if any(word in desc for word in food_keywords):
        return 'Food'
    elif any(word in desc for word in shopping_keywords):
        return 'Shopping'
    elif any(word in desc for word in recharge_keywords):
        return 'Recharge & Bills'
    elif any(word in desc for word in entertainment_keywords):
        return 'Entertainment'
    elif any(word in desc for word in transport_keywords):
        return 'Transport'
    elif any(word in desc for word in emi_keywords):
        return 'EMI & Finance'
    elif any(word in desc for word in health_keywords):
        return 'Health'
    elif any(word in desc for word in friends_keywords):
        return 'Friends & Family'
    else:
        return 'Others'


def detect_money_leaks(df):
    leaks = []
    small_debits = df[
        (df['type'] == 'debit') &
        (df['amount'] <= 500)
    ].copy()

  
    recurring = small_debits.groupby('description').agg(
        count=('amount', 'count'),
        total=('amount', 'sum'),
        avg=('amount', 'mean')
    ).reset_index()

    leaks_df = recurring[recurring['count'] >= 2]

    for _, row in leaks_df.iterrows():
        leaks.append({
            'name': row['description'],
            'times': int(row['count']),
            'total_spent': round(row['total'], 2),
            'avg_amount': round(row['avg'], 2)
        })

    return leaks


def calculate_health_score(df):
    score = 100
    tips = []
    total_income = df[df['type'] == 'credit']['amount'].sum()
    total_expense = df[df['type'] == 'debit']['amount'].sum()

    if total_income == 0:
        return 50, ["No income transactions found in this period"]

    savings_rate = ((total_income - total_expense) / total_income) * 100

 
    if savings_rate < 0:
        score -= 30
        tips.append("You are spending MORE than you earn. Cut non-essential expenses immediately.")
    elif savings_rate < 10:
        score -= 20
        tips.append("Your savings rate is below 10%. Try to save at least 20% of your income.")
    elif savings_rate < 20:
        score -= 10
        tips.append("Good progress! Push savings rate above 20% for better financial health.")

  
    entertainment = df[
        (df['type'] == 'debit') &
        (df['category'] == 'Entertainment')
    ]['amount'].sum()

    entertainment_percent = (entertainment / total_income) * 100
    if entertainment_percent > 15:
        score -= 15
        tips.append(f"Entertainment is {entertainment_percent:.1f}% of income. Keep it under 10%.")


    food = df[
        (df['type'] == 'debit') &
        (df['category'] == 'Food')
    ]['amount'].sum()

    food_percent = (food / total_income) * 100
    if food_percent > 30:
        score -= 10
        tips.append(f"Food spending is {food_percent:.1f}% of income. Try cooking at home more.")


    emi = df[
        (df['type'] == 'debit') &
        (df['category'] == 'EMI & Finance')
    ]['amount'].sum()

    emi_percent = (emi / total_income) * 100
    if emi_percent > 40:
        score -= 15
        tips.append(f"EMI burden is {emi_percent:.1f}% of income. This is dangerously high.")

   
    score = max(0, score)


    if not tips:
        tips.append("Excellent financial habits! Keep maintaining this discipline.")
        tips.append("Consider investing your surplus in SIP or FD for better returns.")
        tips.append("You are in the top 10% of smart spenders your age.")

    return round(score), tips