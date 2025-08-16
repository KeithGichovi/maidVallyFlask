from app.extensions import celery, mail
from flask_mail import Message
from flask import current_app
from datetime import datetime, timedelta
from app.models import *
from sqlalchemy import and_

@celery.task
def send_test_email():
    """
    Send a test email
    """
    if not current_app.config['BUSINESS_NOTIFICATIONS_ENABLED']:
        return "Business notifications are disabled."

    with current_app.app_context():
        msg = Message(
            subject = "Test Email",
            recipients = [current_app.config['BUSINESS_NOTIFICATIONS_EMAIL']],
            body = "This is a test email. The date and time is {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        mail.send(msg)
        return "Test email sent successfully."

@celery.task
def send_weekly_reminder_for_unpaid_jobs():
    """
    Send a weekly reminder email for unpaid jobs.
    """
    if not current_app.config['BUSINESS_NOTIFICATIONS_ENABLED']:
        return "Business notifications are disabled."
    
    with current_app.app_context():
        # Get all unpaid payments
        unpaid_payments = Payment.query.filter(
            Payment.payment_status == PaymentStatus.UNPAID
        ).all()
        
        if not unpaid_payments:
            return "No unpaid jobs found"
        
        today = datetime.utcnow()
        
        # Categorize payments
        overdue = []
        due_soon = []  # Due within 7 days
        future = []
        
        week_from_now = today + timedelta(days=7)
        
        for payment in unpaid_payments:
            if payment.due_date < today:
                days_overdue = (today - payment.due_date).days
                overdue.append({
                    'payment': payment,
                    'days_overdue': days_overdue,
                    'client': payment.job.client.name,
                    'amount': payment.amount,
                    'job_description': payment.job.description or 'No description'
                })
            elif payment.due_date <= week_from_now:
                days_until_due = (payment.due_date - today).days
                due_soon.append({
                    'payment': payment,
                    'days_until_due': days_until_due,
                    'client': payment.job.client.name,
                    'amount': payment.amount,
                    'job_description': payment.job.description or 'No description'
                })
            else:
                future.append(payment)
        
        total_unpaid = sum(p.amount for p in unpaid_payments)
        total_overdue = sum(item['amount'] for item in overdue)
        
        email_body = f"""
📋 WEEKLY PAYMENT REMINDER - {today.strftime('%d/%m/%Y')}

💰 PAYMENT SUMMARY:
• Total Outstanding: £{total_unpaid:.2f}
• Overdue Amount: £{total_overdue:.2f}

🔴 OVERDUE PAYMENTS ({len(overdue)} invoices):
"""
        
        for item in overdue:
            email_body += f"   • {item['client']}: £{item['amount']:.2f} ({item['days_overdue']} days overdue)\n"
            email_body += f"     Service: {item['job_description']}\n"
        
        if not overdue:
            email_body += "   🎉 No overdue payments!\n"
        
        email_body += f"""

🟡 DUE SOON ({len(due_soon)} invoices):
"""
        
        for item in due_soon:
            email_body += f"   • {item['client']}: £{item['amount']:.2f} (due in {item['days_until_due']} days)\n"
        
        if not due_soon:
            email_body += "   ✅ No payments due this week\n"
        
        email_body += f"""

🟢 FUTURE PAYMENTS: {len(future)} invoices (£{sum(p.amount for p in future):.2f})

📞 ACTION NEEDED:
"""
        
        if overdue:
            email_body += "• Contact overdue clients immediately\n"
            email_body += "• Consider late payment fees\n"
        
        if due_soon:
            email_body += "• Send gentle reminders to clients with upcoming due dates\n"
        
        email_body += """
• Update payment tracking system
• Follow up on any payment commitments

Your Payment Tracker 💳
        """
        
        msg = Message(
            subject=f"📋 Weekly Payment Reminder - £{total_overdue:.2f} Overdue",
            recipients=[current_app.config['BUSINESS_NOTIFICATIONS_EMAIL']],
            body=email_body
        )
        
        mail.send(msg)
        return f"Weekly reminder sent: {len(overdue)} overdue, {len(due_soon)} due soon"

@celery.task
def send_monthly_reminder_for_unpaid_jobs():
    """
    Send a monthly reminder email for unpaid jobs.
    More detailed analysis than weekly reminder.
    """
    if not current_app.config['BUSINESS_NOTIFICATIONS_ENABLED']:
        return "Business notifications are disabled."
    
    with current_app.app_context():
        # Get all unpaid payments
        unpaid_payments = Payment.query.filter(
            Payment.payment_status == PaymentStatus.UNPAID
        ).all()
        
        if not unpaid_payments:
            # Still send a report showing good payment status
            email_body = f"""
📊 MONTHLY PAYMENT STATUS - {datetime.utcnow().strftime('%B %Y')}

🎉 EXCELLENT NEWS!
No outstanding payments - all clients are up to date!

Keep up the great work with your payment collection!

Your Business Manager 💯
            """
            
            msg = Message(
                subject=f"📊 Monthly Payment Status - All Clear! 🎉",
                recipients=[current_app.config['BUSINESS_NOTIFICATIONS_EMAIL']],
                body=email_body
            )
            
            mail.send(msg)
            return "Monthly reminder sent: No unpaid jobs"
        
        today = datetime.utcnow()
        
        # Analyze payment patterns by client
        client_analysis = {}
        total_unpaid = 0
        
        for payment in unpaid_payments:
            client_name = payment.job.client.name
            total_unpaid += payment.amount
            
            if client_name not in client_analysis:
                client_analysis[client_name] = {
                    'total_owed': 0,
                    'payments': [],
                    'oldest_payment': payment.due_date,
                    'payment_count': 0
                }
            
            client_analysis[client_name]['total_owed'] += payment.amount
            client_analysis[client_name]['payment_count'] += 1
            client_analysis[client_name]['payments'].append({
                'amount': payment.amount,
                'due_date': payment.due_date,
                'days_overdue': max(0, (today - payment.due_date).days),
                'job_description': payment.job.description or 'No description'
            })
            
            # Track oldest payment
            if payment.due_date < client_analysis[client_name]['oldest_payment']:
                client_analysis[client_name]['oldest_payment'] = payment.due_date
        
        # Sort clients by total amount owed
        sorted_clients = sorted(client_analysis.items(), key=lambda x: x[1]['total_owed'], reverse=True)
        
        email_body = f"""
📊 MONTHLY PAYMENT ANALYSIS - {today.strftime('%B %Y')}

💰 OVERVIEW:
• Total Outstanding: £{total_unpaid:.2f}
• Number of Clients with Unpaid Jobs: {len(client_analysis)}
• Total Unpaid Invoices: {len(unpaid_payments)}

👥 CLIENT BREAKDOWN (by amount owed):
"""
        
        for client_name, data in sorted_clients:
            oldest_days = (today - data['oldest_payment']).days
            email_body += f"""
   🏢 {client_name}:
      • Total Owed: £{data['total_owed']:.2f}
      • Number of Unpaid Invoices: {data['payment_count']}
      • Oldest Payment: {oldest_days} days overdue
"""
            
            # Show individual payments for this client
            for payment in data['payments']:
                if payment['days_overdue'] > 0:
                    status = f"({payment['days_overdue']} days overdue)"
                else:
                    days_until_due = (payment['due_date'] - today).days
                    status = f"(due in {days_until_due} days)" if days_until_due >= 0 else "(due today)"
                
                email_body += f"        - £{payment['amount']:.2f} {status}\n"
        
        # Recommendations
        email_body += f"""

💡 RECOMMENDATIONS:

HIGH PRIORITY ACTIONS:
"""
        
        # Identify worst clients
        urgent_clients = [name for name, data in sorted_clients if 
                         any(p['days_overdue'] > 30 for p in data['payments']) or 
                         data['total_owed'] > 500]
        
        if urgent_clients:
            email_body += f"• Contact these clients immediately: {', '.join(urgent_clients[:3])}\n"
            email_body += "• Consider payment plans for large amounts\n"
            email_body += "• Review credit terms for repeat late payers\n"
        
        email_body += f"""
GENERAL ACTIONS:
• Send payment reminders to all overdue clients
• Update payment tracking system
• Consider requiring deposits for new jobs from slow payers
• Review and tighten payment terms if needed

📈 BUSINESS HEALTH:
• Track your payment collection rate monthly
• Set up automatic reminders for due dates
• Consider offering early payment discounts

Generated: {today.strftime('%d/%m/%Y at %H:%M')}

Your Business Analyst 📊
        """
        
        msg = Message(
            subject=f"📊 Monthly Payment Analysis - £{total_unpaid:.2f} Outstanding",
            recipients=[current_app.config['BUSINESS_NOTIFICATIONS_EMAIL']],
            body=email_body
        )
        
        mail.send(msg)
        return f"Monthly analysis sent: {len(client_analysis)} clients, £{total_unpaid:.2f} outstanding"
    
@celery.task
def get_monthly_report():
    """
    Generate the monthly report, to be sent via email. 
    It should show the key metrics for the month.
    Show the total revenue paid, show any outstanding payments,
    show the total number of jobs completed.
    """
    if not current_app.config['BUSINESS_NOTIFICATIONS_ENABLED']:
        return "Business notifications are disabled."
    
    with current_app.app_context():
        # Calculate date ranges
        today = datetime.utcnow()
        first_day_this_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # This month's jobs
        this_month_jobs = Job.query.filter(
            Job.time_started >= first_day_this_month
        ).all()
        
        # Calculate revenue metrics
        total_revenue_generated = sum(job.total_amount for job in this_month_jobs)
        total_expenses = sum(job.total_expenses for job in this_month_jobs)
        profit_this_month = total_revenue_generated - total_expenses
        
        # Payment metrics
        payments_received_this_month = Payment.query.filter(
            and_(
                Payment.payment_date >= first_day_this_month,
                Payment.payment_status == PaymentStatus.PAID
            )
        ).all()
        
        cash_received = sum(payment.amount for payment in payments_received_this_month)
        
        # Outstanding payments (all time)
        outstanding_payments = Payment.query.filter(
            Payment.payment_status == PaymentStatus.UNPAID
        ).all()
        
        total_outstanding = sum(payment.amount for payment in outstanding_payments)
        overdue_payments = [p for p in outstanding_payments if p.due_date < today]
        total_overdue = sum(payment.amount for payment in overdue_payments)
        
        # Top clients this month
        client_revenue = {}
        for job in this_month_jobs:
            client_name = job.client.name
            client_revenue[client_name] = client_revenue.get(client_name, 0) + job.total_amount
        
        top_clients = sorted(client_revenue.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Calculate collection rate (fix the syntax error)
        if total_revenue_generated > 0:
            collection_rate = (cash_received / total_revenue_generated * 100)
        else:
            collection_rate = 0
        
        avg_job_value = (total_revenue_generated / len(this_month_jobs)) if this_month_jobs else 0
        
        # Create email report
        email_body = f"""
📊 MONTHLY BUSINESS REPORT - {today.strftime('%B %Y')}

💰 REVENUE & PROFIT:
- Jobs Completed: {len(this_month_jobs)}
- Total Revenue Generated: £{total_revenue_generated:.2f}
- Total Expenses: £{total_expenses:.2f}
- Profit This Month: £{profit_this_month:.2f}

💳 CASH FLOW:
- Cash Received: £{cash_received:.2f}
- Outstanding Payments: £{total_outstanding:.2f}
- ⚠️ Overdue Payments: £{total_overdue:.2f} ({len(overdue_payments)} invoices)

🏆 TOP CLIENTS THIS MONTH:
"""
        
        for i, (client, revenue) in enumerate(top_clients, 1):
            email_body += f"   {i}. {client}: £{revenue:.2f}\n"
        
        if not top_clients:
            email_body += "   No jobs completed this month\n"
        
        email_body += f"""

📈 SUMMARY:
- Revenue vs Last Month: Track your growth!
- Average Job Value: £{avg_job_value:.2f}
- Payment Collection Rate: {collection_rate:.1f}%

Generated on: {today.strftime('%d/%m/%Y at %H:%M')}

Your Business Assistant 📈
        """
        
        msg = Message(
            subject=f"📊 Monthly Report - {today.strftime('%B %Y')} - £{profit_this_month:.2f} Profit",
            recipients=[current_app.config['BUSINESS_NOTIFICATIONS_EMAIL']],
            body=email_body
        )
        
        mail.send(msg)
        return f"Monthly report sent: {len(this_month_jobs)} jobs, £{profit_this_month:.2f} profit"