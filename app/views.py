from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from .models import Room, Staff, Booking
from datetime import datetime, date, timedelta, time
from django.db.models import Q
from django.utils.timezone import localtime, make_aware
from app.forms import BookingForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from . import mixins
from django.views import generic


class RoomView(View, mixins.MonthCalendarMixin):
    def get(self, request, *args, **kwargs):
        year =self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        # if request.user.is_authenticated:
        #     start_date = date.today()
        #     weekday = start_date.weekday()
        #     if weekday != 6:
        #         start_date = start_date - timedelta(days=weekday + 1)
            # return redirect('mypage', start_date.year, start_date.month, start_date.day)
            # return redirect('calendar', pk=1)
        room_data = Room.objects.all()
        calendar = {}
        for hour in range(8,17):
            row = {}
            for roomy in room_data:
                # dct = f'{year, month, day}'
                # dct = dct.replace(', ','/')
                dct = date(year=year, month=month, day=day)
                row[roomy, dct] = ''
                # row[roomy] = dct
                calendar[hour] = row

        booking_data = Booking.objects.all()
        for booking in booking_data:
            local_time = localtime(booking.start)
            booking_date = local_time.date()
            # booking_date = booking_date.strftime("(%Y/%m/%d)")
            booking_hour = local_time.hour
            booking_room = booking.room
            # if (booking_hour in calendar) and (booking_date in calendar[booking_hour]):
            if (booking_hour in calendar) and (booking_room, booking_date in calendar[booking_hour]):
                if booking_date == dct:
                    calendar[booking_hour][booking_room, booking_date] = booking.first_name
            # dct = datetime.datetime.strptime(dct, '%Y/%m%d')

        return render(request, 'app/room.html', {
            'room_data': room_data,
            'calendar': calendar,
            'year': year,
            'month': month,
            'day': day,
            'before': dct - timedelta(days=1),
            'next': dct + timedelta(days=1),
            'dct': dct,
        })

class StaffView(View):
    def get(self, request, *args, **kwargs):
        # store_data = get_object_or_404(Store, id=self.kwargs['pk'])
        staff_data = Staff.objects.filter(id=self.kwargs['pk']).select_related('user')

        return render(request, 'app/staff.html', {
            # 'store_data': store_data,
            'staff_data': staff_data
        })


class MonthCalendar(mixins.MonthCalendarMixin, generic.TemplateView):
    """月間カレンダーを表示するビュー"""
    template_name = 'app/month.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar_context = self.get_month_calendar()
        context.update(calendar_context)
        return context


class MonthWithScheduleCalendar(mixins.MonthWithScheduleMixin, generic.TemplateView):
    """スケジュール付きの月間カレンダーを表示するビュー"""
    template_name = 'app/month_with_schedule.html'
    model = Booking
    date_field = 'start'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar_context = self.get_month_calendar()
        context.update(calendar_context)
        return context
    

class CalendarView(View):
    def get(self, request, *args, **kwargs):
        staff_data = Staff.objects.filter(id=self.kwargs['pk']).select_related('user')
        year =self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        if year and month and day:
            start_date = date(year=year, month=month, day=day)
        else:
            start_date = date.today()
        days = [start_date + timedelta(days=day) for day in range(7)]
        start_day = days[0]
        end_day = days[-1]

        calendar = {}
        for hour in range(8,17):
            row ={}
            for day in days:
                row[day] = True
            calendar[hour] = row
        start_time = make_aware(datetime.combine(start_day, time(hour=8, minute=0, second=0)))
        end_time = make_aware(datetime.combine(end_day, time(hour=17, minute=0, second=0)))
        booking_data = Booking.objects.filter(staff=staff_data).exclude(Q(start__gt=end_time) | Q(end__lt=start_time))
        for booking in booking_data:
            local_time = localtime(booking.start)
            booking_date = local_time.date()
            booking_hour = local_time.hour
            if (booking_hour in calendar) and (booking_date in calendar[booking_hour]):
                calendar[booking_hour][booking_date] = False
        return render(request, 'app/calendar.html', {
            'staff_data': staff_data,
            'calendar': calendar,
            'days': days,
            'start_day': start_day,
            'end_day': end_day,
            'before': days[0] - timedelta(days=7),
            'next': days[-1] + timedelta(days=1),
            'today': date.today()
        })


class BookingView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            staff_data = Staff.objects.filter(id=self.request.user.id).select_related('user')[0]
            # staff_data = Staff.objects.filter(id=self.kwargs['id']).select_related('user')
            # staff_data = self.request.user.id
            room_data = Room.objects.get(id=self.kwargs['pk'])
            booking_data = Booking.objects.all()
            year = self.kwargs.get('year')
            month = self.kwargs.get('month')
            day = self.kwargs.get('day')
            hour = self.kwargs.get('hour')
            form = BookingForm(request.POST or None, initial={
                'first_name': staff_data.user.first_name,
                'last_name': staff_data.user.last_name,
            })

            return render(request, 'app/booking.html', {
                'staff_data': staff_data,
                'room_data': room_data,
                'booking_data' : booking_data,
                'year': year,
                'month': month,
                'day': day,
                'hour': hour,
                'form': form,
            })
        else:
            return redirect('account_login')
    
    def post(self, request, *args, **kwargs):
        staff_data = get_object_or_404(Staff, id=self.request.user.id)
        # staff_data = get_object_or_404(Staff, id=self.kwargs['pk'])
        room_data = Room.objects.get(id=self.kwargs['pk'])
        year =self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        hour = self.kwargs.get('hour')
        start_time = make_aware(datetime(year=year, month=month, day=day, hour=hour))
        end_time = make_aware(datetime(year=year, month=month, day=day, hour=hour + 1))
        booking_data = Booking.objects.filter(room=room_data, start=start_time)
        form = BookingForm(request.POST or None)
        if booking_data.exists():
            form.add_error(None, '既に予約があります。\n別の日時で予約をお願いします。')
        else:
            if form.is_valid():
                booking =Booking()
                booking.staff = staff_data
                booking.room = room_data
                booking.start = start_time
                booking.end = end_time
                booking.first_name = form.cleaned_data['first_name']
                booking.last_name = form.cleaned_data['last_name']
                #booking.tel = form.cleaned_data['tel']
                booking.remarks = form.cleaned_data['remarks']
                booking.save()
                return redirect('app:thanks')
            
        return render(request, 'app/booking.html', {
            'staff_data': staff_data,
            'room_data': room_data,
            'year': year,
            'month': month,
            'day': day,
            'hour': hour,
            'form': form,
        })


class ThanksView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'app/thanks.html')
    

class MyPageView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        staff_data = Staff.objects.filter(id=self.kwargs['pk']).select_related('user')[0]
        # room_data = Room.objects.get(id=self.kwargs['pk'])
        # year = self.kwargs.get('year')
        # month = self.kwargs.get('month')
        # day = self.kwargs.get('day')
        # start_date = date(year=year, month=month, day=day)
        # days = [start_date + timedelta(days=day) for day in range(7)]
        # start_day = days[0]
        # end_day = days[-1]

        # calendar = {}
        # for hour in range(10,21):
        #     row ={}
        #     for day_ in days:
        #         row[day_] = ''
        #     calendar[hour] = row
        # start_time = make_aware(datetime.combine(start_day, time(hour=10, minute=0, second=0)))
        # end_time = make_aware(datetime.combine(end_day, time(hour=20, minute=0, second=0)))
        booking_data = Booking.objects.filter(staff=staff_data, start__gte=date.today())
        # for booking in booking_data:
        #     local_time = localtime(booking.start)
        #     booking_date = local_time.date()
        #     booking_hour = local_time.hour
        #     if (booking_hour in calendar) and (booking_date in calendar[booking_hour]):
        #         calendar[booking_hour][booking_date] = booking.first_name

        return render(request, 'app/mypage.html', {
            'staff_data': staff_data,
            'booking_data': booking_data,
            # 'calendar': calendar,
            # 'days': days,
            # 'start_day': start_day,
            # 'end_day': end_day,
            # 'before': days[0] - timedelta(days=7),
            # 'next': days[-1] + timedelta(days=1),
            # 'year': year,
            # 'month': month,
            # 'day': day,
        })


@require_POST
def Holiday(request, year, month, day, hour):
    staff_data = Staff.objects.get(id=request.user.id)
    start_time = make_aware(datetime(year=year, month=month, day=day, hour=hour))
    end_time = make_aware(datetime(year=year, month=month, day=day, hour=hour))

    Booking.objects.create(
        staff=staff_data,
        start=start_time,
        end=end_time,
    )

    start_date = date(year=year, month=month, day=day)
    weekday = start_date.weekday()
    if weekday != 6:
        start_date = start_date - timedelta(days=weekday + 1)
    return redirect('mypage', year=start_date.year, month=start_date.month, day=start_date.day)


@require_POST
def Delete(request, **kwargs):
    # start_time = make_aware(datetime(year=year, month=month, day=day, hour=hour))
    staff_data = Staff.objects.filter(id=request.user.id).select_related('user')[0]
    booking_data = Booking.objects.get(id=kwargs['pk'])

    booking_data.delete()

    # start_date = date(year=year, month=month, day=day)
    # weekday = start_date.weekday()

    # if weekday != 6:
    #     start_date = start_date - timedelta(days=weekday + 1)
    return redirect('app:mypage', pk=staff_data.id)
    # return redirect('mypage', year=start_date.year, month=start_date.month, day=start_date.day)