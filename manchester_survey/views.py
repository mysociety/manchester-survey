from manchester_survey.shortcuts import render

def home(request):
    return render(request, 'index.html')

