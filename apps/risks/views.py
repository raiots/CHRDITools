from django.shortcuts import render
from django.views import View


class RiskRecordView(View):
    def get(self, request):
        return render(request, 'risks/risk_record.html')