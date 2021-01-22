/*
	This file is a part of myTinyTodo.
	(C) Copyright 2010 Max Pozdeev <maxpozdeev@gmail.com>
	Licensed under the GNU GPL v2 license. See file COPYRIGHT for details.
*/

// AJAX myTinyTodo Storage

(function(){

"use strict";

var mtt;

function mytinytodoStorageAjax(amtt)
{
	this.mtt = mtt = amtt;
}

window.mytinytodoStorageAjax = mytinytodoStorageAjax;

mytinytodoStorageAjax.prototype =
{
	/* required method */
	request:function(action, params, callback)
	{
		if(!this[action]) throw "Unknown storage action: "+action;

		this[action](params, function(json){
			if(json.denied) mtt.errorDenied();
			if(callback) callback.call(mtt, json)
		});
	},


	loadLists: function(params, callback)
	{
		$.getJSON('/ajax?loadLists'+'&rnd='+Math.random(), callback);
	},


	loadTasks: function(params, callback)
	{
		var q = '';
		if(params.search && params.search != '') q += '&s='+encodeURIComponent(params.search);
		if(params.tag && params.tag != '') q += '&t='+encodeURIComponent(params.tag);
		if(params.setCompl && params.setCompl != 0) q += '&setCompl=1';
		q += '&rnd='+Math.random();

/*		$.getJSON(mtt.mttUrl+'ajax?loadTasks&list='+params.list+'&compl='+params.compl+'&sort='+params.sort+'&tz='+params.tz+q, function(json){
			callback.call(mtt, json);
		})
*/

		$.getJSON('/ajax?loadTasks&list='+params.list+'&compl='+params.compl+'&sort='+params.sort+q, callback);
	},


	newTask: function(params, callback)
	{
		$.post('/ajax?newTask',
			{ list:params.list, title: params.title, tag:params.tag }, callback, 'json');
	},


	fullNewTask: function(params, callback)
	{
		$.post('/ajax?fullNewTask',
			{ list:params.list, title:params.title, note:params.note, prio:params.prio, tags:params.tags, duedate:params.duedate, tag:params.tag },
			callback, 'json');
	},


	editTask: function(params, callback)
	{
		$.post('/ajax?editTask='+params.id,
			{ id:params.id, title:params.title, note:params.note, prio:params.prio, tags:params.tags, duedate:params.duedate },
			callback, 'json');
	},


	editNote: function(params, callback)
	{
		$.post('/ajax?editNote='+params.id, {id:params.id, note: params.note}, callback, 'json');
	},


	completeTask: function(params, callback)
	{
		$.post('/ajax?completeTask='+params.id, { id:params.id, compl:params.compl }, callback, 'json');
	},


	deleteTask: function(params, callback)
	{
		$.post('/ajax?deleteTask='+params.id, { id:params.id }, callback, 'json');
	},


	setPrio: function(params, callback)
	{
		$.getJSON('/ajax?setPrio='+params.id+'&prio='+params.prio+'&rnd='+Math.random(), callback);
	},


	setSort: function(params, callback)
	{
		$.post('/ajax?setSort', { list:params.list, sort:params.sort }, callback, 'json');
	},

	changeOrder: function(params, callback)
	{
		var order = '';
		for(var i in params.order) {
			order += params.order[i].id +'='+ params.order[i].diff + '&';
		}
		$.post('/ajax?changeOrder', { order:order }, callback, 'json');
	},

	suggestTags: function(params, callback)
	{
		$.getJSON('/ajax?suggestTags', {list:params.list, q:params.q, rnd:Math.random()}, callback);
	},

	tagCloud: function(params, callback)
	{
		$.getJSON('/ajax?tagCloud&list='+params.list+'&rnd='+Math.random(), callback);
	},

	moveTask: function(params, callback)
	{
		$.post('/ajax?moveTask', { id:params.id, from:params.from, to:params.to }, callback, 'json');
	},

	parseTaskStr: function(params, callback)
	{
		$.post('/ajax?parseTaskStr', { list:params.list, title:params.title, tag:params.tag }, callback, 'json');
	},


	// Lists
	addList: function(params, callback)
	{
		$.post('/ajax?addList', { name:params.name }, callback, 'json');

	},

	renameList:  function(params, callback)
	{
		$.post('/ajax?renameList', { list:params.list, name:params.name }, callback, 'json');
	},

	deleteList: function(params, callback)
	{
		$.post('/ajax?deleteList', { list:params.list }, callback, 'json');
	},

	publishList: function(params, callback)
	{
		$.post('/ajax?publishList', { list:params.list, publish:params.publish },  callback, 'json');
	},

	setShowNotesInList: function(params, callback)
	{
	    $.post('/ajax?setShowNotesInList', { list:params.list, shownotes:params.shownotes },  callback, 'json');
	},

	setHideList: function(params, callback)
	{
		$.post('/ajax?setHideList', { list:params.list, hide:params.hide }, callback, 'json');
	},

	changeListOrder: function(params, callback)
	{
		$.post('/ajax?changeListOrder', { order:params.order }, callback, 'json');
	},

	clearCompletedInList: function(params, callback)
	{
		$.post('/ajax?clearCompletedInList', { list:params.list }, callback, 'json');
	}

};

})();
