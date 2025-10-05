import { Calendar } from '../js/core/index.global.min.js';
import esLocale from '../js/core/locales-all.global.min.js';
import bootstrap5Plugin from '../js/core/bootstrap5/index.global.min.js';

FullCalendar.Calendar = Calendar;
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
        },]
    });
    calendar.render();
});