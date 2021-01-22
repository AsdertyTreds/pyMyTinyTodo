import uuid
import time
import datetime
import json
from locale import setlocale, LC_TIME
from flask import session
from mttdatabase import os, database, Lists, Todolist, Tags2Task, Tags, func, s, app
from sqlalchemy.exc import OperationalError as Error
from math import ceil
import langs

language = langs.getlanguage(app.static_folder + '/lang/' + s.values['lang'] + '.json')

def need_auth():
    return 0 if s.values['password'] == '' else 1


def islogged():
    if 'logged' in session:
        return True if (s.values['password'] == '') | (session['logged'] == 1) else False
    elif s.values['password'] == '':
        return True
    elif s.values['password'] != '':
        return False


def check_write_access(list_id: int = None):
    ret = True
    if not islogged():
        ret = False
    if list_id:
        if Lists.query.filter_by(id=list_id).count() == 0:
            ret = False
    return ret


def tstodatetime(timest):
    format_dt = s.values['dateformat'] + (' %I:%M %p' if s.values['clock'] == 12 else ' %H:%M')
    return formattime(format_dt, timest)


def formattime(format_dt, timestamp: int = 0):
    if timestamp == 0:
        timestamp = time.time()
    setlocale(LC_TIME, s.values['lang'])
    format_dt = format_dt.replace('%-', '%#') if os.name == 'nt' else format_dt
    ret = time.strftime(format_dt, time.localtime(timestamp))
    return ret


def clear_name(name):
    for x in ['"', "'", '>', '<', '&']:
        name = name.replace(x, '')
    return name


def loadlists(list_id: int = None):
    query = database.session.query(Lists)
    if 'logged' in session:
        if session['logged'] == 1:
            query = query.filter_by(published=1)
    if list_id is not None:
        query = query.filter_by(id=list_id)

    query = query.order_by(Lists.ow.asc()).order_by(Lists.id.asc())
    rows = query.all()
    return {"total": 0} if not rows else \
        {"total": len(rows) if rows else 1,
         "list": [
             {"id": row.id,
              "name": row.name,
              "sort": row.sorting,
              "published": row.published,
              "showCompl": 1 if row.taskview & 1 else 0,
              "showNotes": 1 if row.taskview & 2 else 0,
              "hidden": 1 if row.taskview & 4 else 0} for row
             in rows]}


def addlist(name):
    if not check_write_access():
        return {"total": 0, "list": [], "denied": 1}

    publish = 0
    if 'logged' in session:
        if session['logged'] == 1:
            publish = 1
    try:
        ow = Lists.max_ow() + 1
        name = clear_name(name)
        row = Lists(uuid=str(uuid.uuid4()),
                    name=name,
                    ow=ow,
                    d_created=time.time(),
                    d_edited=time.time(),
                    taskview=1,
                    published=publish)
        database.session.add(row)
        database.session.commit()
        return loadlists(row.id)
    except Error as e:
        database.session.rollback()
        return str(e)


def renamelist(list_id: int, name: str):
    if not check_write_access():
        return {"total": 0, "list": [], "denied": 1}

    try:
        name = clear_name(name)
        row = Lists.query.filter_by(id=list_id).first()
        row.name = name
        row.d_edited = time.time()
        database.session.commit()
        return loadlists(row.id)
    except Error as e:
        database.session.rollback()
        return str(e)


def changelistorder(order: list):
    if not check_write_access():
        return {"total": 0, "list": [], "denied": 1}

    if order:
        try:
            for i, k in enumerate(order):
                row = Lists.query.filter_by(id=k).first()
                row.d_edited = time.time()
                row.ow = i
            database.session.commit()
            return {"total": 1}
        except Error as e:
            database.session.rollback()
            return str(e)
    return {"total": 0}


def publishlist(list_id: int, publish: int):
    if not check_write_access():
        return {"total": 0, "list": [], "denied": 1}

    try:
        row = Lists.query.filter_by(id=list_id).first()
        row.published = publish
        row.d_created = time.time()
        database.session.commit()
        return {"total": 1, "id": list_id}
    except Error:
        database.session.rollback()
        return {"total": 0}


def setshownotesinlist(list_id: int, flag: int):
    if not check_write_access():
        return {"total": 0, "list": [], "denied": 1}
    try:
        row = Lists.query.filter_by(id=list_id).first()
        row.taskview = row.taskview & ~2 if flag == 0 else row.taskview | 2
        database.session.commit()
        return {"total": 1}
    except Error as e:
        database.session.rollback()
        return str(e)


def setsort(list_id: int, sort: int):
    if not check_write_access():
        return {"total": 0, "list": [], "denied": 1}

    try:
        row = Lists.query.filter_by(id=list_id).first()
        row.sorting = 0 if (sort < 0 | sort > 104) | (sort < 101 & sort > 4) else sort
        row.d_edited = time.time()
        database.session.commit()
        return {"total": 1}
    except Error as e:
        database.session.rollback()
        return str(e)


def deletelist(list_id: int):
    if not check_write_access():
        return {"total": 0, "list": [], "denied": 1}

    try:
        row = Lists.query.count()
        if row > 1:
            Lists.query.filter_by(id=list_id).delete()
            Todolist.query.filter_by(list_id=list_id).delete()
            Tags2Task.query.filter_by(list_id=list_id).delete()
            database.session.commit()
            return {"total": 1}
        else:
            return {"total": 0}
    except Error as e:
        database.session.rollback()
        return str(e)


def sethidelist(list_id: int, hide: int):
    if not check_write_access(list_id):
        return {"total": 0, "list": [], "denied": 1}

    try:
        row = Lists.query.filter_by(id=list_id).first()
        row.taskview = row.taskview & ~4 if hide == 0 else row.taskview | 4
        database.session.commit()
        return {"total": 1}
    except Error as e:
        database.session.rollback()
        return str(e)


def html_special_chars(text, i: int = 1):
    if i:
        return text \
            .replace(u"&", u"&amp;") \
            .replace(u"<", u"&lt;") \
            .replace(u">", u"&gt;")
        # .replace(u'"', u"&quot;") \
        # .replace(u"'", u"&apos;") \
    else:
        return text \
            .replace(u"&amp;", u"&") \
            .replace(u"&lt;", u"<") \
            .replace(u"&gt;", u">")
        # .replace( u"&quot;", u'"') \
        # .replace(u"&apos;", u"'") \


def escapetags(ss):
    c1 = chr(1)
    c2 = chr(2)
    r1 = ['<b>', '<i>', '<u>', '<s>', '</b>', '</i>', '</u>', '</s>']
    for r in r1:
        rs = r.replace('<', c1).replace('>', c2)
        ss = ss.replace(r, rs)
    ss = html_special_chars(ss)
    ss = ss.replace(c1, '<')
    ss = ss.replace(c2, '>')
    return ss


def preparetaskrow1(rows):
    from main import language
    dueclass = duestr = ''
    return {'total': len(rows),
            'list': [{'id': row.id, 'title': escapetags(row.title), 'listId': row.list_id,
                      'date': tstodatetime(row.d_created),
                      'dateInt': int(row.d_created),
                      "dateInline": formattime(s.values['dateformat2'], row.d_created)
                      if time.strftime('%Y', time.localtime(time.time())) == time.strftime('%Y', time.localtime(
                          row.d_created))
                      else formattime(s.values['dateformatshort'], row.d_created),
                      "dateInlineTitle": language['taskdate_inline_created'] + tstodatetime(row.d_created),
                      "dateEditedInt": int(row.d_edited),
                      "dateCompleted": tstodatetime(row.d_completed) if not row.d_completed == '' else row.d_completed,
                      "dateCompletedInline": formattime(s.values['dateformat2'], row.d_completed)
                      if (not time.strftime('%Y', time.localtime(time.time())) == time.strftime('%Y', time.localtime(
                          row.d_completed))) & (not row.d_completed == '')
                      else formattime(s.values['dateformatshort'], row.d_completed),
                      "dateCompletedInlineTitle": language['taskdate_inline_completed'] +
                      (tstodatetime(row.d_completed) if not row.d_completed == '' else row.d_completed),
                      "compl": row.compl,
                      "prio": row.prio,
                      "note": '' if row.note is None else escapetags(row.note),
                      "noteText": '' if row.note is None else row.note,
                      "ow": row.ow,
                      "tags": row.tags,
                      "tags_ids": row.tags_ids,
                      "duedate": '' if row.duedate == 0 else formattime(s.values['dateformat2'], row.duedate),
                      "dueClass": dueclass,
                      "dueStr": duestr,
                      "dueInt": row.duedate,
                      "dueTitle": '' if row.duedate == 0 else language['taskdate_inline_duedate'] +
                      formattime(s.values['dateformat2'], row.duedate)}
                     for row in rows]}


def preparetaskrow(rows):
    ret = []
    for row in rows:
        a = (time.localtime(time.time())[0], time.localtime(time.time())[1], time.localtime(time.time())[2],
             0, 0, 0, 0, 0, 0)
        # for i in range(0, 3):
        #     a.append(time.localtime(time.time())[i])
        # for i in range(3, 9):
        #     a.append(0)
        now = time.struct_time(a)
        diff = row.duedate - time.mktime(now)
        at = int(time.strftime("%Y", now))
        ad = int(time.strftime("%Y", time.localtime(row.duedate)))

        if diff < -604800 & ad == at:
            dueclass = 'past'
            duestr = formattime(s.values['dateformatshort'], row.duedate)
        elif diff < -604800:
            dueclass = 'past'
            duestr = formattime(s.values['dateformat2'], row.duedate)
        elif diff < -86400:
            dueclass = 'past'
            duestr = language['daysago'].replace('%d', str(ceil(abs(diff)/86400)))
        elif diff < 0:
            dueclass = 'past'
            duestr = language['yesterday']
        elif diff < 86400:
            dueclass = 'today'
            duestr = language['today']
        elif diff < 172800:
            dueclass = 'today'
            duestr = language['tomorrow']
        elif diff < 691200:
            dueclass = 'soon'
            duestr = language['indays'].replace('%d', str(ceil(diff/86400)))
        elif ad == at:
            dueclass = 'future'
            duestr = formattime(s.values['dateformatshort'], row.duedate)
        else:
            dueclass = 'future'
            duestr = formattime(s.values['dateformat2'], row.duedate)

        ret.append({'id': row.id,
                    'title': escapetags(row.title),
                    'listId': row.list_id,
                    'date': tstodatetime(row.d_created),
                    'dateInt': int(row.d_created),
                    "dateInline": formattime(s.values['dateformat2'], row.d_created)
                    if time.strftime('%Y', time.localtime(time.time())) == time.strftime('%Y', time.localtime(
                      row.d_created))
                    else formattime(s.values['dateformatshort'], row.d_created),
                    "dateInlineTitle": language['taskdate_inline_created'] + tstodatetime(row.d_created),
                    "dateEditedInt": int(row.d_edited),
                    "dateCompleted": tstodatetime(row.d_completed) if not row.d_completed == '' else row.d_completed,
                    "dateCompletedInline": formattime(s.values['dateformat2'], row.d_completed)
                    if (not time.strftime('%Y', time.localtime(time.time())) == time.strftime('%Y', time.localtime(
                      row.d_completed))) & (not row.d_completed == '')
                    else formattime(s.values['dateformatshort'], row.d_completed),
                    "dateCompletedInlineTitle": language['taskdate_inline_completed'] +
                    (tstodatetime(row.d_completed) if not row.d_completed == '' else row.d_completed),
                    "compl": row.compl,
                    "prio": row.prio,
                    "note": '' if row.note is None else escapetags(row.note).replace('\n', '<br />'),
                    "noteText": '' if row.note is None else row.note,
                    "ow": row.ow,
                    "tags": row.tags,
                    "tags_ids": row.tags_ids,
                    "duedate": '' if row.duedate == 0 else formattime(s.values['dateformat2'], row.duedate),
                    "dueClass": dueclass,
                    "dueStr": duestr,
                    "dueInt": row.duedate,
                    "dueTitle": '' if row.duedate == 0 else language['taskdate_inline_duedate'] +
                    formattime(s.values['dateformat2'], row.duedate)})

    return {'total': len(rows), 'list': ret}


def preparetags(tags: str, task_id: int, list_id: int):
    for x in ['"', "'", '<', '>', '&', '/', '\\', '^', '#', '%', '_']:
        tags = tags.replace(x, '')
    tags = tags.split(',')
    atags = []
    aids = []
    try:
        for tag in tags:
            tag = tag.strip()
            if not tag == '':
                row = Tags.query.filter_by(name=tag).first()
                if not row:
                    row = Tags(name=tag)
                    database.session.add(row)
                    database.session.commit()
                tag_id = row.id
                atags.append(tag)
                aids.append(tag_id)
                row = Tags2Task(task_id=task_id,
                                tag_id=tag_id,
                                list_id=list_id)
                database.session.add(row)
                database.session.commit()
        return [atags, aids]
    except Error as e:
        database.session.rollback()
        return str(e)


def parse_smartsyntax(title):
    import re
    match = re.findall("^(/([+-]{0,1}\d+)?/)?(.*?)(\s+/([^/]*)/$)?$", title.strip())
    if match[0]:
        prio = re.search("(/([+-]{0,1}\d+)?/)", match[0][0])
        title = match[0][2]
        tags = re.search("(\s+/([^/]*)/$)", match[0][3])
        return {'prio': (int(prio[2]) if prio[2] else 0) if prio else 0,
                'title': title.strip() if title else '',
                'tags': (tags[2] if tags[2] else '') if tags else ''}
    return False


def loadtasks(list_id: int, compl: int, sort: int, search, t):
    query = database.session.query(Todolist)
    userlists = ''
    if list_id == -1:
        rows_lists = Lists.query.all()
        userlists = ','.join(str(row.id) for row in rows_lists)
        query = query.filter(Todolist.list_id.in_(userlists))
    else:
        query = query.filter_by(list_id=list_id)

    if search is not None:
        search.strip()
        search = "%{}%".format(search)
        query = query.filter(Todolist.title.like(search) | Todolist.note.like(search))

    if compl == 0:
        query = query.filter_by(compl=0)

    if t is not None:
        tagei = []
        tagi = []
        at = str(t).split(',')

        for atv in at:
            atv = atv.strip()
            if atv == '' or atv == '^':
                continue
            tagid = Tags.query.filter_by(name=atv.replace('^', '', 1)).first().id
            if atv.find('^') > -1:
                tagei.append(tagid)
            else:
                tagi.append(tagid)

        if len(tagi) > 1:
            strtagi = ','.join(map(str, tagi))
            t2t = database.session.query().with_entities(Tags2Task.task_id, func.count(Tags2Task.tag_id).label('c')) \
                .filter(Tags2Task.tag_id.in_(strtagi))
            if list_id == -1:
                t2t = t2t.filter(Tags2Task.list_id.in_(userlists))
            else:
                t2t = t2t.filter_by(list_id=list_id)
            t2t = t2t.group_by(Tags2Task.task_id).subquery()
            query = query.join(t2t, t2t.c.task_id == Todolist.id)
            query = query.filter(t2t.c.c == len(tagi))
        elif len(tagi) == 1:
            query = query.join(Tags2Task, Tags2Task.task_id == Todolist.id).filter(Tags2Task.tag_id == tagi[0])
            query = query.filter(Tags2Task.tag_id == tagi[0])

        if len(tagei) > 0:
            strtagei = ','.join(map(str, tagei))
            t2t = database.session.query().with_entities(Tags2Task.task_id).filter(Tags2Task.tag_id.in_(strtagei))
            if list_id == -1:
                t2t = t2t.filter(Tags2Task.list_id.in_(userlists))
            else:
                t2t = t2t.filter_by(list_id=list_id)
            t2t = t2t.distinct().subquery()
            query = query.filter(Todolist.id.notin_(t2t))
    query = query.order_by(Todolist.compl.asc())

    if sort == 1:
        query = query.order_by(Todolist.prio.desc()).order_by(Todolist.duedate.is_(None).asc()).order_by(
            Todolist.ow.asc())
    elif sort == 101:
        query = query.order_by(Todolist.prio.asc()).order_by(Todolist.duedate.is_(None).desc()).order_by(
            Todolist.ow.desc())
    elif sort == 2:
        query = query.order_by(Todolist.duedate.is_(None).asc()).order_by(Todolist.prio.desc()).order_by(
            Todolist.ow.asc())
    elif sort == 102:
        query = query.order_by(Todolist.duedate.is_(None).desc()).order_by(Todolist.prio.asc()).order_by(
            Todolist.ow.desc())
    elif sort == 3:
        query = query.order_by(Todolist.d_created.asc()).order_by(Todolist.prio.desc()).order_by(Todolist.ow.asc())
    elif sort == 103:
        query = query.order_by(Todolist.d_created.desc()).order_by(Todolist.prio.asc()).order_by(Todolist.ow.desc())
    elif sort == 4:
        query = query.order_by(Todolist.d_edited.asc()).order_by(Todolist.prio.desc()).order_by(Todolist.ow.asc())
    elif sort == 104:
        query = query.order_by(Todolist.d_edited.desc()).order_by(Todolist.prio.asc()).order_by(Todolist.ow.desc())
    else:
        query = query.order_by(Todolist.ow.asc())

    try:
        rows = query.all()
        return preparetaskrow(rows) if rows else {"total": 0}
    except Error as e:
        database.session.rollback()
        return str(e)


def newtask(list_id: int, title: str, tag: str = None):
    if not check_write_access(list_id):
        return {"total": 0, "list": [], "denied": 1}
    prio = 0
    ow = Todolist.max_ow() + 1
    if s.values['smartsyntax']:
        a = parse_smartsyntax(title)
        if a:
            prio = -1 if a.get('prio') < -1 else 2 if a.get('prio') > 2 else a.get('prio')
            title = a.get('title')
            tag = a.get('tags')
    try:
        row = Todolist(uuid=str(uuid.uuid4()),
                       list_id=list_id,
                       title=title,
                       d_created=time.time(),
                       d_edited=time.time(),
                       ow=ow,
                       prio=prio)
        database.session.add(row)
        database.session.commit()
        atags = preparetags(tag, row.id, list_id)
        if atags:
            row.tags = ",".join(atags[0])
            row.tags_ids = ",".join(map(str, atags[1]))
            database.session.commit()
        return preparetaskrow([row])
    except Error as e:
        database.session.rollback()
        return str(e)


def fullnewtask(list_id: int, title: str, note: str, prio: int, tags: str, duedate: str, tag: str = None):
    if not check_write_access(list_id):
        return {"total": 0, "list": [], "denied": 1}

    prio = -1 if prio < -1 else 2 if prio > 2 else prio
    duedate = time.mktime(
        datetime.datetime.strptime(duedate, s.values['dateformat2']).timetuple()) if not duedate == '' else 0

    ow = Todolist.max_ow() + 1

    try:
        row = Todolist(uuid=str(uuid.uuid4()),
                       list_id=list_id,
                       title=title,
                       d_created=time.time(),
                       d_edited=time.time(),
                       ow=ow,
                       prio=prio,
                       note=note,
                       duedate=duedate)
        database.session.add(row)
        database.session.commit()
        task_id = row.id

        atags = preparetags((tags + ',' + tag) if tag else tags, task_id, list_id)
        if atags:
            row.tags = ",".join(atags[0])
            row.tags_ids = ",".join(map(str, atags[1]))
            database.session.commit()

        return preparetaskrow([row])
    except Error as e:
        database.session.rollback()
        return str(e)


def edittask(task_id: int, title: str, note: str, prio: int, tags: str, duedate: str):
    if not check_write_access():
        return {"total": 0, "list": [], "denied": 1}
    prio = -1 if prio < -1 else 2 if prio > 2 else prio
    duedate = time.mktime(
        datetime.datetime.strptime(duedate, s.values['dateformat2']).timetuple()) if not duedate == '' else 0
    try:
        row = Todolist.query.filter_by(id=task_id).first()
        list_id = row.list_id
        row.title = title
        row.d_edited = time.time()
        row.prio = prio
        row.note = note
        row.duedate = duedate
        if not tags == '':
            Tags2Task.query.filter(Tags2Task.task_id == task_id).delete()
            database.session.commit()
            atags = preparetags(tags, task_id, list_id)
            if atags:
                row.tags = ",".join(atags[0])
                row.tags_ids = ",".join(map(str, atags[1]))

        database.session.commit()

        return preparetaskrow([row])
    except Error as e:
        database.session.rollback()
        return str(e)


def deletetask(task_id: int):
    if not check_write_access():
        return {"total": 0, "list": [], "denied": 1}

    try:
        Todolist.query.filter_by(id=task_id).delete()
        Tags2Task.query.filter_by(task_id=task_id).delete()
        database.session.commit()
        return {"total": 1, "list": [{"id": task_id}]}
    except Error as e:
        database.session.rollback()
        return str(e)


def editnote(task_id: int, note: str):
    if not check_write_access():
        return {"total": 0, "list": [], "denied": 1}

    try:
        row = Todolist.query.filter_by(id=task_id).first()
        row.note = note
        row.d_edited = time.time()
        database.session.commit()
        return {"total": 1, "list": [{"id": task_id, "note": escapetags(note), "noteText": note}]}
    except Error as e:
        database.session.rollback()
        return str(e)


def completetask(task_id: int, compl: int):
    if not check_write_access():
        return {"total": 0, "list": [], "denied": 1}

    try:
        row = Todolist.query.filter_by(id=task_id).first()
        ow = Todolist.max_ow(compl, row.list_id) + 1
        row.compl = compl
        row.ow = ow
        row.d_completed = 0 if compl == 0 else time.time()
        row.d_edited = time.time()
        database.session.commit()
        rows = Todolist.query.all()
        return preparetaskrow(rows)
    except Error as e:
        database.session.rollback()
        return str(e)


def setprio(task_id: int, prio: int):
    if not check_write_access():
        return {"total": 0, "list": [], "denied": 1}

    prio = -1 if prio < -1 else 2 if prio > 2 else prio
    try:
        row = Todolist.query.filter_by(id=task_id).first()
        row.prio = prio
        row.d_edited = time.time()
        database.session.commit()
        return {"total": 1, "list": [{"id": task_id, "prio": prio}]}
    except Error as e:
        database.session.rollback()
        return str(e)


def movetask(task_id: int, to_id: int):
    if not check_write_access():
        return {"total": 0, "list": [], "denied": 1}

    try:
        row = Todolist.query.filter_by(id=task_id).first()
        if (not row) | (Lists.query.filter_by(id=to_id).count() == 0):
            return {"total": 0}
        elif row.list_id == to_id:
            return {"total": 0}
        ow = Todolist.max_ow(row.compl, to_id) + 1

        row_t2t = Tags2Task.query.filter_by(task_id=task_id).first()
        if row_t2t:
            row_t2t.list_id = to_id

        row.list_id = to_id
        row.ow = ow
        row.d_edited = time.time()
        database.session.commit()

        return {"total": 1}
    except Error as e:
        database.session.rollback()
        return str(e)


def suggesttags(list_id: int, q):
    try:
        limit = 8
        q = "%{}%".format(q)
        query = database.session.query(Tags)
        query = query.join(Tags2Task, Tags.id == Tags2Task.tag_id).filter(Tags2Task.list_id == list_id)
        query = query.filter(Tags.name.like(q))
        query = query.group_by(Tags2Task.tag_id).order_by(Tags.name)
        rows = query.limit(limit).all()

        return json.dumps([tag.name for tag in rows])
    except Error as e:
        database.session.rollback()
        return str(e)


def clearcompletedinlist(list_id: int):
    if not check_write_access():
        return {"total": 0, "list": [], "denied": 1}

    try:
        rows = Todolist.query.filter_by(list_id=list_id).filter_by(compl=1).all()
        for row in rows:
            Tags2Task.query.filter_by(task_id=row.id).delete()
        Todolist.query.filter_by(list_id=list_id).filter_by(compl=1).delete()
        database.session.commit()
        return {"total": 1}
    except Error as e:
        database.session.rollback()
        return str(e)


def changeorder(order: str):
    if not check_write_access():
        return {"total": 0, "list": [], "denied": 1}

    q = order.split('&')
    query = database.session.query(Todolist)
    if q:
        try:
            for w in q:
                if w:
                    task_id, diff = w.split('=')
                    diff = int(diff)
                    row = query.filter_by(id=int(task_id)).first()
                    row.d_edited = time.time()
                    row.ow = row.ow + diff if diff > -1 else row.ow - abs(diff)
            database.session.commit()
            return {"total": 1}
        except Error as e:
            database.session.rollback()
            return str(e)
    else:
        return {"total": 0}


def tagsize(qmin, q, step):
    from math import ceil
    if step == 0:
        return 1
    v = ceil((q - qmin) / step)
    return 0 if v == 0 else v - 1


def tagcloud(list_id: int):
    try:
        query = database.session.query(Tags2Task, Tags, func.count(Tags2Task.tag_id).label('tags_count'))
        query = query.filter_by(list_id=list_id)
        query = query.join(Tags, Tags2Task.tag_id == Tags.id)
        query = query.group_by(Tags2Task.tag_id).order_by('tags_count')
        rows = query.all()
        if not rows:
            return {"total": 0}
        count_at = len(rows)
        ac = [row.tags_count for row in rows]
        qmax = max(ac)
        qmin = min(ac)
        step = (qmax - qmin) / (10 if count_at >= 10 else count_at)
        return {"total": count_at, "cloud":
                [{"tag": row.Tags.name, "id": row.Tags.id, "w": tagsize(qmin, row.tags_count, step)} for row in rows]}

    except Error as e:
        database.session.rollback()
        return str(e)


def parsetaskstr(title):
    if not check_write_access():
        return {"total": 0, "list": [], "denied": 1}

    ret = {'prio': 0,
           'title': title,
           'tags': ''}
    if s.values['smartsyntax']:
        a = parse_smartsyntax(title)
        if a:
            ret = {'prio': -1 if a.get('prio') < -1 else 2 if a.get('prio') > 2 else 0,
                   'title': a.get('title'),
                   'tags': a.get('tags')}
    return ret


def login(password):
    if s.values['password'] == '':
        return {"logged": 0, "disabled": 1}
    if password == s.values['password']:
        session['logged'] = 1
        return {"logged": 1}


def logout():
    session['logged'] = 0
    return {"logged": 0}
