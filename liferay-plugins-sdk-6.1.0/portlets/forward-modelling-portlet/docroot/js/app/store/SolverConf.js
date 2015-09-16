/**
 * The store used for submits
 */
Ext.define('CF.store.SolverConf', {
  extend: 'Ext.data.Store',
  requires: ['CF.model.Conf'],
  model: 'CF.model.Conf',
  storeId: 'solverConfStore',
  groupField: 'group'
});