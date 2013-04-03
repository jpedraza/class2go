from datetime import date
from calendar import HTMLCalendar
from django.utils.html import conditional_escape as esc

class ClassCalendar(HTMLCalendar):

    def __init__(self, assignments, course_prefix, course_suffix, course_start, course_end):
        super(ClassCalendar, self).__init__()
        print assignments
        self.assignments = self.group_by_day(assignments)
        self.course_prefix = course_prefix
        self.course_suffix = course_suffix
        self.course_start = course_start
        self.course_end = course_end

    def formatday(self, day, weekday):
        if day != 0:
            cssclass = self.cssclasses[weekday]
            body = ['']
            print self.assignments
            if day in self.assignments:
                cssclass += ' filled'
                body.append('<span class="day_content"><em class="icon-file"><ul class="day_content_list">')
                for assignment in self.assignments[day]:
                    body.append('<li>')
                    body.append('<a href="%s">' % self.get_assignment_url(assignment))
                    body.append(esc(assignment.title))
                    body.append('</a></li>')
                body.append('</ul></em></span>')
            if day == self.course_start:
                body.append('<span class="day_content"><em class="icon-play-circle"></em></span>')
            if day == self.course_end:
                body.append('<span class="day_content"><em class="icon-star"></em></span>')
            if date.today() == date(self.year, self.month, day):
                cssclass += ' today'
                body.append('<div class="today_border"></div>')
            return self.day_cell(cssclass, '<div class="day_num">%d</div> %s' % (day, ''.join(body)))
        return self.day_cell('noday', '&nbsp;')

    def formatmonth(self, year, month):
        self.year, self.month = year, month
        return super(ClassCalendar, self).formatmonth(year, month)

    def group_by_day(self, assignments):
        assignment_dictionary = {}
        
        for assignment in assignments:
            day = assignment.due_date.day
            if assignment_dictionary.has_key(day):
                assignment_dictionary[day].append(assignment)
            else:
                assignment_dictionary[day] = [assignment]
        return assignment_dictionary

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)
    
    def get_assignment_url(self, assignment):
        #if assignment.has_child():
        #    return '/%s/%s/%ss#%s' % (self.course_prefix, self.course_suffix, assignment.exam_type,  assignment.slug)
        #else:
        return '/%s/%s/%ss/%s' % (self.course_prefix, self.course_suffix, assignment.exam_type,  assignment.slug)