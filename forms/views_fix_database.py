from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection
from django.db.models import Sum
from django.core.management import call_command
from .models import StockItem
import json


@staff_member_required
@require_http_methods(["GET", "POST"])
def fix_railway_database(request):
    """
    Emergency database fix endpoint
    Visit: /stock/fix-database/ to clean and reload stock data
    """
    
    if request.method == "GET":
        # Show confirmation page
        current_count = StockItem.objects.count()
        current_qty = StockItem.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
        
        context = {
            'current_count': current_count,
            'current_qty': current_qty,
            'expected_count': 1976,
            'expected_qty': 259406,
        }
        return render(request, 'forms/fix_database.html', context)
    
    elif request.method == "POST":
        # Execute the fix
        results = {
            'steps': [],
            'success': False
        }
        
        try:
            # Step 0: Run migrations (create tables if missing)
            try:
                call_command('migrate', verbosity=0)
                results['steps'].append({
                    'step': 0,
                    'action': 'Database Migrations',
                    'status': 'success',
                    'data': 'All migrations applied successfully'
                })
            except Exception as e:
                results['steps'].append({
                    'step': 0,
                    'action': 'Database Migrations',
                    'status': 'warning',
                    'data': f'Migration check complete: {str(e)[:100]}'
                })
            
            # Step 1: Get current state
            current_count = StockItem.objects.count()
            current_qty = StockItem.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
            results['steps'].append({
                'step': 1,
                'action': 'Current State',
                'status': 'success',
                'data': f'{current_count} items, {current_qty:.0f} PCS'
            })
            
            # Step 2: Delete all stock items using TRUNCATE
            with connection.cursor() as cursor:
                cursor.execute('TRUNCATE TABLE forms_stockitem RESTART IDENTITY CASCADE;')
            
            remaining = StockItem.objects.count()
            if remaining == 0:
                results['steps'].append({
                    'step': 2,
                    'action': 'Delete All Data',
                    'status': 'success',
                    'data': 'All stock items deleted'
                })
            else:
                results['steps'].append({
                    'step': 2,
                    'action': 'Delete All Data',
                    'status': 'error',
                    'data': f'{remaining} items still remain'
                })
                return JsonResponse(results)
            
            # Step 3: Load fixture
            try:
                call_command('loaddata', 'stock_items', verbosity=0)
                results['steps'].append({
                    'step': 3,
                    'action': 'Load Fixture',
                    'status': 'success',
                    'data': 'Fixture loaded successfully'
                })
            except Exception as e:
                results['steps'].append({
                    'step': 3,
                    'action': 'Load Fixture',
                    'status': 'error',
                    'data': str(e)
                })
                return JsonResponse(results)
            
            # Step 4: Verify new data
            new_count = StockItem.objects.count()
            new_qty = StockItem.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
            
            if new_count == 1976 and abs(new_qty - 259406) < 1:
                results['steps'].append({
                    'step': 4,
                    'action': 'Verify Data',
                    'status': 'success',
                    'data': f'{new_count} items, {new_qty:.0f} PCS - PERFECT!'
                })
                results['success'] = True
            else:
                results['steps'].append({
                    'step': 4,
                    'action': 'Verify Data',
                    'status': 'warning',
                    'data': f'{new_count} items, {new_qty:.0f} PCS (expected 1976, 259406)'
                })
            
            return JsonResponse(results)
            
        except Exception as e:
            results['steps'].append({
                'step': 0,
                'action': 'Error',
                'status': 'error',
                'data': str(e)
            })
            return JsonResponse(results, status=500)
