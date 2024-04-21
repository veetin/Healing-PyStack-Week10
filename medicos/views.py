from django.shortcuts import render, redirect
from .models import Especialidades, DadosMedico, is_medico, DatasAbertas
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime, timedelta
from pacientes.models import consulta, Documento

# Create your views here.



def cadastro_medico(request):
    
    
    if is_medico(request.user):
        messages.add_message(request, constants.WARNING, "Você já é medico")
        return redirect("/medicos/abrir_horario")
    
    if request.method == "GET":
        especialidades = Especialidades.objects.all()
        return render(request, 'cadastro_medico.html', {'especialidades': especialidades, 'is_medico': is_medico(request.user)})
    elif request.method == "POST":
        crm = request.POST.get('crm')
        nome = request.POST.get('nome')
        cep = request.POST.get('cep')
        rua = request.POST.get('rua')
        bairro = request.POST.get('bairro')
        numero = request.POST.get('numero')
        cim = request.FILES.get('cim')
        rg = request.FILES.get('rg')
        foto = request.FILES.get('foto')
        especialidade = request.POST.get('especialidade')
        descricao = request.POST.get('descricao')
        valor_consulta = request.POST.get('valor_consulta')

        dados_medico = DadosMedico(
            crm=crm,
            nome=nome,
            cep=cep,
            rua=rua,
            bairro=bairro,
            numero=numero,
            cedula_identidae_medica = cim,
            rg=rg,
            foto=foto,
            Especialidade_id=especialidade,
            descricao=descricao,
            valor_consulta=valor_consulta,
            user=request.user 

        )

        dados_medico.save()

        messages.add_message(request, constants.SUCCESS, "Cadastro medico realizado com sucesso")
        return redirect('/medicos/abrir_horario')

def abrir_horario(request):

    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente medicos podem abrir horários')
        return redirect('/usuarios/sair')
    
    if request.method == 'GET':
        dados_medicos = DadosMedico.objects.get(user=request.user)
        datas_abertas = DatasAbertas.objects.filter(user=request.user)
        return render(request, 'abrir_horario.html', {'dados_medicos': dados_medicos, 'datas_abertas': datas_abertas, 'is_medico': is_medico(request.user)})
    
    elif request.method == 'POST':
        data = request.POST.get('data')
        data_formatada = datetime.strptime(data, '%Y-%m-%dT%H:%M')
        if data_formatada <= datetime.now():
            messages.add_message(request, constants.WARNING, 'A data não pode ser anterior a data atual')
            return redirect('/medicos/abrir_horario')
        
        horario_abrir = DatasAbertas(
            data=data,
            user=request.user
            )
        horario_abrir.save()
        
        messages.add_message(request, constants.SUCCESS, 'Horário cadastrado com sucesso')

        return redirect('/medicos/abrir_horario')

def consultas_medico(request):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    hoje = datetime.now().date()
    hoje = datetime.now().date()

    consultas_hoje = consulta.objects.filter(data_aberta__user=request.user).filter(data_aberta__data__gte=hoje).filter(data_aberta__data__lt=hoje + timedelta(days=1))
    consultas_restantes = consulta.objects.exclude(id__in=consultas_hoje.values('id')).filter(data_aberta__user=request.user)
    print(consultas_hoje.values('id'))
    return render(request, 'consultas_medico.html', {'consultas_hoje':consultas_hoje, 'consultas_restantes':consultas_restantes, 'is_medico': is_medico(request.user)})

def consulta_area_medico(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    if request.method == 'GET':
        consultas = consulta.objects.get(id=id_consulta)
        documentos = Documento.objects.filter(consultas=consultas)
        return render(request, 'consulta_area_medico.html', {'consulta':consultas, "documentos":documentos})
    
    elif request.method == 'POST':
         consultas = consulta.objects.get(id=id_consulta)
         link = request.POST.get('link')

         if consultas.status == 'C':
             messages.add_message(request, constants.WARNING, 'Essa consulta já foi cancelada')
             return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
         
         elif consultas.status == 'F':
            messages.add_message(request, constants.WARNING, 'Essa consulta já foi finalizada')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
         
         consultas.link = link
         consultas.status = 'I'
         consultas.save()

         messages.add_message(request, constants.SUCCESS, 'Consulta inicializada')
         return redirect(f'/medicos/consulta_area_medico/{id_consulta}')

def finalizar_consulta(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    consultas = consulta.objects.get(id=id_consulta)
    if request.user != consultas.data_aberta.user:
        messages.add_message(request, constants.WARNING, 'Essa consulta não é sua')
        return redirect(f'/medicos/consultas_medico')
    
    consultas.status = 'F'
    consultas.save()
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')

def add_documento(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')

    consultas = consulta.objects.get(id=id_consulta)

    if request.user != consultas.data_aberta.user:
        messages.add_message(request, constants.WARNING, 'Essa consulta não é sua')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
    titulo = request.POST.get('titulo')
    documento = request.FILES.get('documento')

    if not documento:
        messages.add_message(request, constants.ERROR, 'Preencha o campo documento')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
    documento = Documento(
        consultas=consultas,
        titulo=titulo,
        documento=documento
    )
    documento.save()
    messages.add_message(request, constants.SUCCESS, 'Documento enviado com sucesso')
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')