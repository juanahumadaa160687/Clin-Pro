import 'bootstrap';
import { Calendar } from '@fullcalendar/core';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import listPlugin from '@fullcalendar/list';
import interactionPlugin from '@fullcalendar/interaction';
import esLocale from '@fullcalendar/core/locales/es';
import bootstrap5Plugin from '@fullcalendar/bootstrap5';

FullCalendar.Calendar = Calendar;
FullCalendar.dayGridPlugin = dayGridPlugin;
FullCalendar.timeGridPlugin = timeGridPlugin;
FullCalendar.listPlugin = listPlugin;
FullCalendar.interactionPlugin = interactionPlugin;
FullCalendar.esLocale = esLocale;
FullCalendar.bootstrap5Plugin = bootstrap5Plugin;

document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        systemTheme: 'bootstrap5',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },
        buttonText: {
            today: 'Hoy',
            month: 'Mes',
            week: 'Semana',
            day: 'Día',
            list: 'Lista',
        },
        locale: 'es',
        firstDay: 1, // Lunes como primer día de la semana
        timeZone: 'America/Santiago',

        editable: true,
        selectable: true,
        events: [{
            title: 'Paciente 1 - Dr numero 2',
            start: '2025-10-11T10:00:00',
            end: '2025-10-11T10:45:00',
            color: '#9ae8ce',
            backgroundColor: 'white',
            borderColor: 'white',
            textColor: 'black',

        },]
    });
    calendar.render();
});