from flask import render_template, request, url_for, flash, redirect
from ajax import *


@app.route('/ajax', methods=('GET', 'POST'))
def ajax():
    ret: str = ''
    if not request.args.get('loadLists') is None:
        ret = loadlists()
    elif not request.args.get('addList') is None:
        if not request.form['name'] is None:
            ret = addlist(request.form['name'])
    elif not request.args.get('setHideList') is None:
        if not request.form['list'] is None and not request.form['hide'] is None:
            ret = sethidelist(int(request.form['list']), int(request.form['hide']))
    elif not request.args.get('renameList') is None:
        if not request.form['list'] is None and not request.form['name'] is None:
            ret = renamelist(int(request.form['list']), request.form['name'])
    elif not request.args.get('changeListOrder') is None:
        if not request.form['order[]'] is None:
            ret = changelistorder(request.form.getlist('order[]'))
    elif not request.args.get('deleteList') is None:
        if not request.form['list'] is None:
            ret = deletelist(int(request.form['list']))
    elif not request.args.get('publishList') is None:
        if not request.form['list'] is None and not request.form['publish'] is None:
            ret = publishlist(int(request.form['list']), int(request.form['publish']))
    elif not request.args.get('setSort') is None:
        if not request.form['list'] is None and not request.form['sort'] is None:
            ret = setsort(int(request.form['list']), int(request.form['sort']))
    elif not request.args.get('loadTasks') is None:
        if not request.args.get('list') is None and not request.args.get('compl') is None and \
                not request.args.get('sort') is None:
            ret = loadtasks(int(request.args.get('list')), int(request.args.get('compl')),
                            int(request.args.get('sort')), request.args.get('s'), request.args.get('t'))
    elif not request.args.get('newTask') is None:
        if not request.form['list'] is None and not request.form['title'] is None:
            if not request.form['tag'] is None:
                ret = newtask(int(request.form['list']), request.form['title'], request.form['tag'])
            else:
                ret = newtask(int(request.form['list']), request.form['title'])
    elif not request.args.get('fullNewTask') is None:
        if not request.form['list'] is None and not request.form['title'] is None and \
                not request.form['tags'] is None and not request.form['note'] is None and \
                not request.form['prio'] is None and not request.form['duedate'] is None:
            if not request.form['tag'] is None:
                ret = fullnewtask(int(request.form['list']), request.form['title'], request.form['note'],
                                  int(request.form['prio']), request.form['tags'], request.form['duedate'],
                                  request.form['tag'])
            else:
                ret = fullnewtask(int(request.form['list']), request.form['title'], request.form['note'],
                                  int(request.form['prio']), request.form['tags'], request.form['duedate'])

    elif not request.args.get('editTask') is None:
        if not request.form['id'] is None and not request.form['title'] is None and \
                not request.form['tags'] is None and not request.form['note'] is None and \
                not request.form['prio'] is None and not request.form['duedate'] is None:
            ret = edittask(int(request.form['id']), request.form['title'], request.form['note'],
                           int(request.form['prio']), request.form['tags'], request.form['duedate'])
    elif not request.args.get('deleteTask') is None:
        if not request.form['id'] is None:
            ret = deletetask(int(request.form['id']))
    elif not request.args.get('editNote') is None:
        if not request.form['id'] is None and not request.form['note'] is None:
            ret = editnote(int(request.form['id']), request.form['note'])
    elif not request.args.get('completeTask') is None:
        if not request.form['id'] is None and not request.form['compl'] is None:
            ret = completetask(int(request.form['id']), int(request.form['compl']))
    elif not request.args.get('setPrio') is None:
        if not request.args.get('prio') is None:
            ret = setprio(int(request.args.get('setPrio')), int(request.args.get('prio')))
    elif not request.args.get('moveTask') is None:
        if not request.form['id'] is None and not request.form['to'] is None:
            ret = movetask(int(request.form['id']), int(request.form['to']))
    elif not request.args.get('suggestTags') is None:
        if not request.args.get('list') is None:
            ret = suggesttags(int(request.args.get('list')), str(request.args.get('q')).strip())
    elif not request.args.get('clearCompletedInList') is None:
        if not request.form['list'] is None:
            ret = clearcompletedinlist(int(request.form['list']))
    elif request.args.get('changeOrder') is not None:
        if request.form['order'] is not None:
            ret = changeorder(request.form['order'])
    elif not request.args.get('tagCloud') is None:
        if not request.args.get('list') is None:
            ret = tagcloud(int(request.args.get('list')))
    elif not request.args.get('parseTaskStr') is None:
        if not request.form['title'] is None:
            ret = parsetaskstr(request.form['title'])
    elif not request.args.get('setShowNotesInList') is None:
        if not request.form['list'] is None and not request.form['shownotes'] is None:
            ret = setshownotesinlist(int(request.form['list']), int(request.form['shownotes']))
    elif not request.args.get('login') is None:
        if not request.form['password'] is None:
            ret = login(request.form['password'])
    elif not request.args.get('logout') is None:
        ret = logout()

    return ret


@app.route('/')
def index():
    if s.values['setup'] > 2:
        sitetype = 1
        if not request.args.get('mobile') is None:
            sitetype = 2
        lang = langs.getlanguage(app.static_folder + '/lang/' + s.values['lang'] + '.json')
        return render_template(s.values['templates'] + '/index.html',
                               s=s.values, l=lang, sitetype=sitetype, session=session)
    else:
        return redirect(url_for('settings'))


@app.route('/settings', methods=('GET', 'POST'))
def settings():
    if not islogged():
        return redirect(url_for('index'))

    if request.method == 'POST':
        if s.values['setup'] > 1:
            title = request.form['title']
            lang = request.form['lang']
            smartsyntax = int(request.form['smartsyntax'])
            autotag = int(request.form['autotag'])
            timezone = request.form['timezone']
            firstdayofweek = int(request.form['firstdayofweek'])
            dateformat = request.form['dateformat']
            dateformat2 = request.form['dateformat2']
            dateformatshort = request.form['dateformatshort']
            clock = int(request.form['clock'])
            showdate = int(request.form['showdate'])

            s.values['lang'] = lang if lang else 'en'
            s.values['title'] = title if title else 'My Todo'
            s.values['smartsyntax'] = smartsyntax
            s.values['autotag'] = autotag
            s.values['timezone'] = timezone
            s.values['firstdayofweek'] = firstdayofweek
            s.values['dateformat'] = dateformat
            s.values['dateformat2'] = dateformat2
            s.values['dateformatshort'] = dateformatshort
            s.values['clock'] = clock
            s.values['showdate'] = showdate

            if int(request.form['allowpassword']) == 1:
                password = request.form['password']
                if not password:
                    flash('password is required!')
            else:
                password = ""
                session['logged'] = 0
            s.values['password'] = password

            if s.values['setup'] == 2:
                db = request.form['db']
                s.values['db'] = db
                if db == 'sqlite':
                    pass
                elif db == 'mysql':
                    s.values['sql_password'] = request.form['sql_password']
                    s.values['sql_db'] = request.form['sql_db']
                    s.values['sql_user'] = request.form['sql_user']
                    s.values['sql_host'] = request.form['sql_host']

                if not table_exists(s.values['prefix'] + 'lists'):
                    from mttdatabase import database, Lists
                    database.create_all()
                    row = Lists(uuid=str(uuid.uuid4()),
                                name='Todo1',
                                d_created=time.time(),
                                d_edited=time.time(),
                                taskview=1)
                    database.session.add(row)
                    database.session.commit()
                s.values['setup'] = 3
            s.save('db/config.json')
            return redirect(url_for('index'))

        elif s.values['setup'] == 1:
            title = request.form['title']
            lang = request.form['lang']
            if not title or not lang:
                flash('values is required!')
            else:
                s.values['title'] = title
                s.values['lang'] = lang
                s.values['setup'] = 2
                s.save('db/config.json')
                return redirect(url_for('index'))
    import pytz
    langlist = langs.getlanglist(app.static_folder + '/lang/')
    langua = langs.getlanguage(app.static_folder + '/lang/' + s.values['lang'] + '.json')
    timezones = pytz.all_timezones
    return render_template(s.values['templates'] + '/settings.html',
                           s=s.values, timezones=timezones, langlist=langlist, l=langua)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
