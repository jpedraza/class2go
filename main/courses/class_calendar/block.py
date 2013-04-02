from datetime import date
from calendar import HTMLCalendar
from django.utils.html import conditional_escape as esc
from itertools import groupby

class ClassCalendar(HTMLCalendar):

    def __init__(self, assignments, course_start, course_end):
        super(ClassCalendar, self).__init__()
        self.assignments = self.group_by_day(assignments)
        self.course_start = course_start
        self.course_end = course_end

    def formatday(self, day, weekday):
        if day != 0:
            cssclass = self.cssclasses[weekday]
            body = ['']
            if day in self.assignments:
                cssclass += ' filled'
                body.append('<span class="day_content"><ul>')
                for assignment in self.assignments[day]:
                    body.append('<li>')
                    body.append('<a href="%s">' % assignment.get_absolute_url())
                    body.append(esc(assignment.title))
                    body.append('</a></li>')
                body.append('</ul>')
            if day == self.course_start:
                body.append('<span class="day_content"><a href="#" class="icon-play-circle"></a></span>')
            if day == self.course_end:
                body.append('<span class="day_content"><a href="#" class="icon-star"></a></span>')
            if date.today() == date(self.year, self.month, day):
                cssclass += ' today'
                body.append('<div class="today_border"></div>')
            return self.day_cell(cssclass, '<div class="day_num">%d</div> %s' % (day, ''.join(body)))
        return self.day_cell('noday', '&nbsp;')

    def formatmonth(self, year, month):
        self.year, self.month = year, month
        return super(ClassCalendar, self).formatmonth(year, month)

    def group_by_day(self, assignments):
        field = lambda assignment: assignment.performed_at.day
        return dict(
            [(day, list(items)) for day, items in groupby(assignments, field)]
        )

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)