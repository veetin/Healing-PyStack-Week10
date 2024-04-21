from django.shortcuts import render, redirect
from medicos.models import DadosMedico, Especialidades, DatasAbertas
from django.http import HttpResponse
from datetime import datetime
from .models import consulta
from django.contrib import messages
from django.contrib.messages import constants 


def home(request):
    if request.method == 'GET':
        medicos = DadosMedico.objects.all()
        especialidades = Especialidades.objects.all()

        medico_filtrar = request.GET.get('medico')
        especialidades_filtrar = request.GET.getlist('especialidades')
       
        if medico_filtrar:
            medicos = medicos.filter(nome__icontains=medico_filtrar)
        
        if especialidades_filtrar:
            medicos = medicos.filter(Especialidade_id__in=especialidades_filtrar)
        
        return render(request, 'home.html', {'medicos':medicos, 'especialidades': especialidades})

def escolher_horario(request, id_dados_medicos):
    if request.method == "GET":
        medico = DadosMedico.objects.get(id=id_dados_medicos)
        datas_abertas = DatasAbertas.objects.filter(user=medico.user).filter(data__gte=datetime.now()).filter(agendado=False)
        return render(request, 'escolher_horario.html', {'medico':medico, 'datas_abertas':datas_abertas})
    
def agendar_horario(request, id_data_aberta):
    if request.method == "GET":
        data_aberta = DatasAbertas.objects.get(id=id_data_aberta)
        
        horario_agendado = consulta(
            paciente=request.user,
            data_aberta=data_aberta
        )
        horario_agendado.save()
        
        data_aberta.agendado == True
        data_aberta.save()

        messages.add_message(request, constants.SUCCESS, "Consulta agendada com sucesso")
        return redirect('/pacientes/minhas_consultas')

def minhas_consultas(request):
    minhas_consultas = consulta.objects.filter(paciente=request.user).filter(data_aberta__data__gte=datetime.now())
    return render(request, 'minhas_consultas.html', {'minhas_consultas':minhas_consultas})

    



    