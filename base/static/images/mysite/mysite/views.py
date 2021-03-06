from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from base.forms import ContactForm, LoginForm, AddShiftForm, goalupdateForm, ContactMe
import mysql.connector
from mysite.air_crew import AirCrew
from mysite.contact import Contact
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from mysite.shift import Shift
from mysite.shift_manager import ShiftManager
from datetime import datetime





from django.contrib.admin.views.decorators import staff_member_required



mydb = mysql.connector.connect(host="localhost", user="root", password = 'a1234567', database = 'flight_manager',auth_plugin='mysql_native_password')


@login_required(login_url='/login/')
def about(request):
    return render(request, 'base/about.html')



def Login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = User()
            name = [username]
            if user.is_exist():
                return render(request, 'base/exists.html', {'name': name})
            else:
                return render(request, 'base/form.html')
        else:
            form = LoginForm()
        return render(request, 'base/login.html')
    else:
        form = ContactForm()
        return render(request, 'base/form.html', {'form': form})

def register(request):
    if request.user.is_authenticated:
        return render(request, 'base/profile.html')
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(first_name =form.cleaned_data['first_name'], username = form.cleaned_data['username'],
                                            last_name = form.cleaned_data['last_name'], password =form.cleaned_data['password'], )
            user.save()
            aircrew = AirCrew()
            aircrew.personal_num = form.cleaned_data['username']
            aircrew.movil = form.cleaned_data['movil']
            aircrew.category = form.cleaned_data['category']
            aircrew.status = form.cleaned_data['status']
            aircrew.InsertToDb()
            return redirect('/profile')
    else:
        form = ContactForm()
    args = {'form': form}
    return render(request,'base/register.html',args)




@login_required(login_url='/login/')
def Profile(request):
    if request.user.is_staff:
        shift_manager = ShiftManager()
        usernamequery = (str(request.user),)
        name = shift_manager.getname(usernamequery)
        totalgoal = shift_manager.totalgoal()
        totaldid = shift_manager.totaldid()
        remain = float(totalgoal) - float(totaldid)
        args = {'name': name, 'totalgoal' : totalgoal, 'totaldid': totaldid, 'remain': remain}
        return render(request, 'base/managerpage.html', args)
    else:
        username = str(request.user)
        usernamequery = (str(request.user),)
        mydb = mysql.connector.connect(host="localhost", user="root", password='a1234567', database='flight_manager',
                                       auth_plugin='mysql_native_password')
        mycursor = mydb.cursor()
        query = """
         SELECT goal FROM flight_manager.air_crew WHERE personal_number = %s 
        """
        mycursor.execute(query, usernamequery)
        results = mycursor.fetchall()
        mydb.commit()
        for row in results:
            shift = str(row[0])
        new_shift = Shift()
        all_shifts = new_shift.ShowAllShifts()
        if len(shift) == 0:
            shift = '0'
        air_crew = AirCrew()
        future_shifts = air_crew.ShowFutureShifts(username)
        name = air_crew.getname(usernamequery)
        howmanydid = air_crew.howmanydid(username)
        howmanytot = air_crew.howmanytot(usernamequery)
        name = air_crew.getname(usernamequery)
        try:
            left = int(shift) - int(howmanydid[0])
        except:
            left = str('0')
        finally:
            args = {'user': name, 'shifts': shift, 'all_shifts' : all_shifts, 'howmanydid' : howmanydid[0], 'left': left, 'shift': shift}
            return render(request, 'base/profile.html', args)

def myshifts(request):
    username = str(request.user)
    air_crew = AirCrew()
    my_shifts = air_crew.ShowMyShifts(username)
    future_shifts = air_crew.ShowFutureShifts(username)
    args = {'my_shifts' : my_shifts, 'future_shifts': future_shifts}
    return render(request, 'base/myshifts.html', args)

@login_required
def allshifts(request):
    shift = Shift()
    all_shifts = shift.ShowAllShifts()
    args = {'all_shifts' : all_shifts}
    return render(request, 'base/allshifts.html', args)

@login_required
def unmannedshifts(request):
    air_crew = AirCrew()
    shift = Shift()
    all_shifts = shift.ShowAllShifts()
    username = str(request.user)
    if air_crew.CheckLeader(username) == True:
        if air_crew.CheckPilot(username) == True:
            available = air_crew.ShowAvailableShiftsLeaders('pilot')
        elif air_crew.CheckPilot(username) == False:
            available = air_crew.ShowAvailableShiftsLeaders('navigator')

    elif not air_crew.CheckLeader(username) == True:
        if air_crew.CheckPilot(username):
            available = air_crew.ShowAvailableShifts('pilot')
        elif air_crew.CheckPilot(username) == False:
            available = air_crew.ShowAvailableShifts('navigator')
    args = {'available': available}
    return render(request, 'base/unmannedshifts.html', args)




def newshift(request):
    personal_num = str(request.user)
    air_crew = AirCrew()
    if air_crew.CheckPilot(personal_num):
        crew_role = 'pilot'
    else:
        crew_role = 'navigator'
    flight_date = request.GET.get('flight_date')
    flight_type = request.GET.get('flight_type')
    leader = str(request.GET.get('leader'))
    newshift = Shift()
    newshift.InsertToStaffing(flight_date, flight_type, personal_num, crew_role, leader)
    if leader == '0':
        leader = ' Number 2'
    elif leader == '1':
        leader == 'Movil'
    if leader == '3':
        leader = ' '

    context = {
        'flight_date': flight_date, 'flight_type': flight_type, 'leader': leader
    }
    return render (request, 'base/newshift.html', context)

@staff_member_required
def managerstaffing(request):
    shift_manager = ShiftManager()
    usernamequery = (str(request.user),)
    name = shift_manager.getname(usernamequery)
    shifts = Shift()
    all_shifts = shifts.ShowAllShifts()
    all_staffing = shifts.ShowAllStaffing()
    if request.method == 'POST':
        form = AddShiftForm(request.POST)
        if form.is_valid():
            flight_type = form.cleaned_data['flight_type']
            flight_date = form.cleaned_data['flight_date']
            notes = form.cleaned_data['notes']
            shift_manager.insertshift(flight_type, flight_date, notes)
            template = 'base/staffingshow.html'
            args = { 'form': form, 'flight_type': flight_type, 'flight_date': flight_date}
    else:
        form = AddShiftForm()
        template = 'base/managerstaffing1.html'
        args = {'name': name, 'all_shifts': all_shifts , 'all_staffing': all_staffing, 'form': form }
    return render(request, template, args)

def staffingshow(request):
    if request.method == 'POST':
        form = AddShiftForm(request.POST)
        if form.is_valid():
            flight_type = form.cleaned_data['flight_type']
            flight_date = form.cleaned_data['flight_date']
    else:
        form = AddShiftForm()
    args = { 'form': form, 'flight_type': flight_type , 'flight_date': flight_date}
    return render(request, 'base/staffingshow.html', args)



@staff_member_required
def airgoals(request):
    shift_manager = ShiftManager()
    number_of_people = shift_manager.staffnumber()
    air_goals = shift_manager.goaltracker()
    totalgoal = shift_manager.totalgoal()
    totaldid = shift_manager.totaldid()
    remain = float(totalgoal) - float(totaldid)
    args = {'air_goals' : air_goals, 'number_of_people': number_of_people, 'totalgoal': totalgoal, 'totaldid': totaldid, 'remain': remain}
    return render(request, 'base/airgoals1.html', args)

@staff_member_required
def airgoalsinfo(request):
    air_crew = AirCrew()
    username = request.GET.get('personal_num')
    usernamequery = (str(username),)
    name = air_crew.getname(usernamequery)
    air_info  = air_crew.ShowMyShifts(username)
    args = {'air_info' : air_info, 'name':name}
    return render(request, 'base/airgoalsinfo.html', args)

@staff_member_required
def managerunmanned(request):
    shift_manager = ShiftManager()
    unmanned = shift_manager.unmannedshifts()
    args = {'unmanned' : unmanned}
    return render(request, 'base/managerunmanned1.html', args)

@staff_member_required
def managershifts(request):
    shifts = Shift()
    shift_manager = ShiftManager()
    all_shifts = shifts.ShowAllShifts()
    totalgoal = shift_manager.totalgoal()
    totaldid = shift_manager.totaldid()
    remain = float(totalgoal) - float(totaldid)
    args = {'all_shifts': all_shifts,'totalgoal': totalgoal, 'totaldid': totaldid, 'remain': remain}
    return render(request, 'base/managershifts1.html', args)




@staff_member_required
def managergoalupdateshow(request):
    if request.method == 'POST':
        form = goalupdateForm(request.POST)
        if form.is_valid():
            azach_num = form.cleaned_data['azach_num']
            miluim_num = form.cleaned_data['miluim_num']
    else:
        form = goalupdateForm(request.POST)
    args = { 'form': form, 'azach_num': azach_num , 'miluim_num': miluim_num}
    return render(request, 'base/staffingshow.html', args)



@staff_member_required
def managergoalupdate(request):
    try :
        if request.method == 'POST':
            form = goalupdateForm(request.POST)
            if form.is_valid():
                shift_manager = ShiftManager()
                azach_num = form.cleaned_data['azach_num']
                miluim_num = form.cleaned_data['miluim_num']
                shift_manager.insertgoals(azach_num, miluim_num)
                template = 'base/managerpagegoal.html'
                args = { 'form': form, 'azach_num': azach_num, 'miluim_num': miluim_num}
        else:
            form = goalupdateForm(request.POST)
            template = 'base/managergoalupdate.html'
            args = {'form': form }
        return render(request, template, args)
    except:
        situation = 'bad'
        args = {'form': form , 'situation' : situation }
        template = 'base/managergoalupdate.html'
        return render(request, template, args)

@staff_member_required
def deletegoals(request):
    shift_manager = ShiftManager()
    shift_manager.deletegoals()
    return render (request, 'base/deletedgoals.html')



@staff_member_required
def managershowalljobs(request):
    shifts = Shift()
    all_jobs = shifts.showalljobs()
    if request.method == 'POST':
        form = AddShiftForm(request.POST)
        if form.is_valid():
            shift_manager = ShiftManager()
            flight_type = form.cleaned_data['flight_type']
            flight_date = form.cleaned_data['flight_date']
            notes = form.cleaned_data['notes']
            shift_manager.insertshift(flight_date,flight_type, notes)
            args = {'form': form}
            return redirect('/managershowalljobs')

    else:
        form = AddShiftForm()
    template = 'base/manageralljobs.html'
    args = { 'form': form ,'all_jobs': all_jobs}
    return render(request, template, args)



@staff_member_required
def deletejob(request):
    shift_manager = ShiftManager()
    flight_date = request.GET.get('flight_date')
    flight_type = request.GET.get('flight_type')
    shift_manager.deletejob(flight_date, flight_type)
    return redirect('/managershowalljobs')

def contact(request):
    if request.method == "POST":
        form = ContactMe(request.POST)
        if form.is_valid():
            contact = Contact()
            contact.personal_num = str(request.user)
            contact.content = form.cleaned_data['content']
            contact.insertcontent(contact.personal_num, contact.content)
            return redirect('/profile')
    else:
        form = ContactMe()
    args = {'form': form}
    return render(request,'base/contact.html',args)

def managercontact(request):
    shift_manager = ShiftManager()
    letters = shift_manager.getletters()
    args = { 'letters': letters}
    return render(request,'base/managercontact.html',args)

def deletecontact(request):
    contact = Contact()
    personal_num = request.GET.get('letter_personal_num')
    date = request.GET.get('letter_date')
    content = request.GET.get('letter_content')
    contact.deleteletter(personal_num, date, content)
    return redirect('/managercontact')























