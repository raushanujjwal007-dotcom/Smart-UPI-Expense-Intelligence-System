import pandas as pd
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Transaction
from .categorizer import categorize, detect_money_leaks, calculate_health_score
import json
from datetime import datetime

@csrf_exempt
def upload_csv(request):
    if request.method == 'POST':

     
        csv_file = request.FILES['file']

        df = pd.read_csv(csv_file)

        
        session_id = str(uuid.uuid4())[:8]

        transactions = []
        for _, row in df.iterrows():
            try:
                
                category = categorize(str(row['Description']))

                amount = float(str(row['Amount']).replace(',', '').replace('₹', ''))
                trans_type = 'debit' if amount < 0 else 'credit'
                amount = abs(amount)

                Transaction.objects.create(
                    session_id=session_id,
                    date=row['Date'],
                    description=str(row['Description']),
                    amount=amount,
                    type=trans_type,
                    category=category
                )

                transactions.append({
                    'date': str(row['Date']),
                    'description': str(row['Description']),
                    'amount': amount,
                    'type': trans_type,
                    'category': category
                })

            except Exception as e:
                continue

        return JsonResponse({
            'session_id': session_id,
            'total_transactions': len(transactions),
            'message': 'Upload successful'
        })


@csrf_exempt
def get_analysis(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        session_id = data['session_id']

        transactions = Transaction.objects.filter(session_id=session_id)

        if not transactions:
            return JsonResponse({'error': 'No data found'}, status=404)

        df = pd.DataFrame(list(transactions.values()))

        score, tips = calculate_health_score(df)

     
        leaks = detect_money_leaks(df)

       
        category_spending = df[df['type'] == 'debit'].groupby('category')['amount'].sum()
        category_dict = category_spending.to_dict()

      
        total_income = float(df[df['type'] == 'credit']['amount'].sum())
        total_expense = float(df[df['type'] == 'debit']['amount'].sum())
        savings = total_income - total_expense

        return JsonResponse({
            'health_score': score,
            'tips': tips,
            'money_leaks': leaks,
            'category_spending': category_dict,
            'total_income': total_income,
            'total_expense': total_expense,
            'savings': savings
        })