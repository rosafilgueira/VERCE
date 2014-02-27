
var wfStore = Ext.create('Ext.data.ArrayStore', {
    fields: [
       {name: 'name'},
       {name: 'desc'},
       {name: 'status'},
       {name: 'date', type: 'date', dateFormat: 'Y-m-d'},
       {name: 'date2'},
       {name: 'workflowId'}
    ],
    sortOnLoad: true, 
    sorters: { property: 'date2', direction : 'DESC' },
    proxy: {
	         type: 'ajax',
	          url: getWorkflowListURL,
	          reader: {
		             root: 'list'
		          }
	},
	autoLoad: true
});

wfStore.load(function() {
		console.log(arguments);
});

Ext.define('CF.view.WfGrid', {
	extend: 'Ext.grid.Panel',
	initComponent: function() {
	    Ext.apply(this, {
	        store: wfStore,
	        id: 'wfGrid',
	        columns: [
	            {
	                text     : 'Name',
	                flex     : 1,
	                sortable : true,
	                dataIndex: 'name'
	            },
	            {
	                text     : 'Desc',
	                flex     : 1,
	                sortable : true,
	                dataIndex: 'desc',
	                renderer: function(value, metaData, record, row, col, store, gridView) {
	                	if (value == null || value === '' || value === 'null') {
	                		return '-';
	                	}

	                	return value;
	                }
	            },
	            {
	                text     : 'Status',
	                width    : 75,
	                sortable : true,
	                renderer : statusRenderer,
	                dataIndex: 'status'
	            },
	            {
	                text     : 'Date',
	                width    : 90,
	                sortable : true,
	                renderer : Ext.util.Format.dateRenderer('d - m - Y'),
	                dataIndex: 'date'
	            },
	            {
	                xtype: 'actioncolumn',
	                width: 55,
	                items: [
		            {
		                icon   : localResourcesPath+'/img/Farm-Fresh_page_white_text.png', 
		                tooltip: 'Download logfiles',
		                handler: function(grid, rowIndex, colIndex) {
		                    var rec = wfStore.getAt(rowIndex);
		
		                    window.open(downloadWorkflowOutputURL + '&workflowId=' + rec.get('workflowId'), '_self');
		                }
		            },
		            {
		                icon   : localResourcesPath+'/img/Farm-Fresh_arrow_rotate_clockwise.png', 
		                tooltip: 'Reuse',
		                handler: function(grid, rowIndex, colIndex) {
		                    var rec = wfStore.getAt(rowIndex);
		
		                    Ext.Ajax.request({
		                    	url: "/j2ep-1.0/prov/workflow/"+encodeURIComponent(rec.get('name')),
      	      	    			params: {
      	      	    			},
      	      	    			method: 'GET',
      	      	    			success: function(response){
      	      	    				var object = JSON.parse(response.responseText);

      	      	    				var input = {};
      	      	    				object.input.forEach(function(item) {
      	      	    					input[item.name] = item;
      	      	    				});

				                    Ext.Ajax.request({
				                    	url: input.solverconf.url,
		      	      	    			success: function(response){
		      	      	    				var object = JSON.parse(response.responseText);

		      	      	    				// reuse solver
		      	      	    				var solverType = Ext.getCmp('solvertype');
		      	      	    				var solver = solverType.store.findRecord('name', object.solver);
		      	      	    				solverType.clearValue();
		      	      	    				solverType.setValue(solver.get('abbr'));

		      	      	    				// reuse velocity when store is loaded
											var velocityCombo = Ext.getCmp('velocity');
		      	      	    				velocityCombo.store.addListener('add', function() {
			  	      	    					velocityCombo.setValue(object.velocity_model);

			      	      	    				solverConfStore.loadData(object.fields);

			      	      	    				// TODO fix selecting events and stations
			      	      	    				// var eventGrid = Ext.getCmp('gridEvents');
			      	      	    				// Ext.util.Observable.capture(ctrl, function(evname) {console.log("ctrl: ", evname, arguments);});
			      	      	    				// Ext.util.Observable.capture(ctrl.eventstore, function(evname) {console.log("store: ", evname, arguments);});
			      	      	    				// Ext.util.Observable.capture(eventGrid, function(evname) {console.log("grid: ", evname, arguments);});
			      	      	    				// eventGrid.on('add', function() {
			      	      	    				// 	console.log('add', arguments);
			      	      	    				// }, this);
			      	      	    				// Ext.util.Observable.capture(eventGrid.getSelectionModel(), function(evname) {console.log("grid: ", evname, arguments);});
			      	      	    				// Ext.util.Observable.capture(ctrl.mapPanel, function(evname) {console.log("mapPanel: ", evname, arguments);});
			      	      	    				// Ext.util.Observable.capture(ctrl.mapPanel.map.events, function(evname) {console.log("map: ", evname, arguments);});

			      	      	    				// ctrl.eventstore.addListener('refresh', function() {
				      	      	    			// 	object.events.forEach(function(eventId) {
				      	      	    			// 		var record = eventGrid.store.findRecord('eventId', eventId);
				      	      	    			// 		eventGrid.getSelectionModel().select(record);
				      	      	    			// 	});
				      	      	    			// }, this, { single: true });
												
												// reuse events
			      	      	    				getEvents(ctrl, input.quakeml.url);

			      	      	    				// reuse stations
			      	      	    				getStations(ctrl, input.stations.url, input.stations['mime-type'] === 'application/xml' ? STXML_TYPE : STPOINTS_TYPE);
		      	      	    					var selectedStations = Ext.getCmp('gridStations').getSelectionModel().selected;
		      	      	    				}, this, { single: true });

		      	      	    				// reuse mesh and trigger velocity store reload
		      	      	    				Ext.getCmp('meshes').setValue(object.mesh);
		      	      	    			},
		      	      	    			failure: function(response) {
		      	      	    				Ext.Msg.alert("Error", "Failed to get workflow settings!");
		      	      	                }
				                    })
      	      	    			},
      	      	    			failure: function(response) {
      	      	    				Ext.Msg.alert("Error", "Failed to get workflow from provenance api!");
      	      	                }
		                    })
		                }
		            },
	                {
	                    icon   : localResourcesPath+'/img/delete-icon.png',
	                    tooltip: 'Delete instance',
	                    handler: function(grid, rowIndex, colIndex) {
	                        var rec = wfStore.getAt(rowIndex);
	                        Ext.Msg.confirm('Warning', 'Are you sure that you want to delete '+rec.get('name')+"?", 
	          	                  function(btn) {
	          	                  	if(btn === 'yes')
	          	                  	{	
	    	      	                  	Ext.Ajax.request({
	    	      	      	    			url: deleteWorkflowURL,
	    	      	      	    			params: {
	    	      	      	    				"workflowId": rec.get('workflowId')
	    	      	      	    			},
	    	      	      	    			success: function(response){
	    	      	      	    				wfStore.load();
	    	      	      	    			},
	    	      	      	    			failure: function(response) {
	    	      	      	    				Ext.Msg.alert("Error", "Delete failed!");
	    	      	      	                }
	    	      	                    });
	          	                  	}
	          	            });
	                    }
	                }
	                ]
	            }
	        ],
	        flex: 1
	    });
	    this.callParent(arguments);
	}
});

var refreshMenuControl = [
	{
       html: '<strong style="color: #416DA3; position: relative; font-size: 12px; top: -1px;">Submited workflows</strong>'
	},                      
	"->",
	{
		tooltip: 'Refresh list',
		handler: function() {
			  wfStore.load();
		},
		style: {
		    background:'none',
		    backgroundImage: 'url('+localResourcesPath+'/img/refresh-icon.png)',
		    backgroundSize: '90% 85%',
		    backgroundRepeat: 'no-repeat',
			height: 32,
			width: 45,
			margin: 1,
			marginRight: '10px'
		},
		height: 35,
		width: 35
	},
	{
		tooltip: 'Go to Document Library<br>(open in a new win)',
		height: 32,
		width: 32,
		handler: function() {
		    openInNewTab('file-manager');
		},
		style: {
		    background:'none',
		    backgroundImage: 'url('+localResourcesPath+'/img/folder-icon.png)',
		    backgroundSize: '90% 90%',
		    backgroundRepeat: 'no-repeat',
			height: 32,
			width: 32,
			top: 0,
			margin: 1,
			marginRight: '10px'
		},
		height: 32,
		width: 32
	}
	];

Ext.define('CF.view.Control', {
	  extend:'Ext.form.Panel',
		layout: 'fit',
		  viewConfig      : {
		    style           : { overflow: 'scroll', overflowX: 'hidden' }
		  },
	  dockedItems: 
		  [{
		    xtype: 'toolbar',
		    dock: 'top',
			height: 35,
		    items: refreshMenuControl
		}],
	  items: [Ext.create('CF.view.WfGrid')]
	});

function statusRenderer(val) {
    if (val === 'INIT' || val === 'RUNNING') {
        return '<span style="color:green;">' + val + '</span>';
    } 
    else if (val === 'ERROR') {
        return '<span style="color:red;">' + val + '</span>';
    }
    return val;
}

function openInNewTab(url)
{
  var win=window.open(url, '_blank');
  win.focus();
}

