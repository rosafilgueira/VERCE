/*
 * Copyright (c) 2008-2014 The Open Source Geospatial Foundation
 *
 * Published under the BSD license.
 * See https://github.com/geoext/geoext2/blob/master/license.txt for the full
 * text of the license.
 */

/**
 * @requires GeoExt/Version.js
 */

/**
 * Small Base class to make creating stores for remote OWS information sources
 * easier.
 *
 * NOTE: This is a BASE CLASS and is not designed for direct use in an
 * application. Instead, one should extend from this class in any situation in
 * which a you need a {@link Ext.data.proxy.Server} (ex: 'ajax', 'jsonp', etc)
 * and a reader which requires an {@link OpenLayers.Format} to parse the data.
 *
 * @class GeoExt.data.OwsStore
 */
Ext.define('GeoExt.data.OwsStore', {
    extend: 'Ext.data.Store',
    requires: [
        'GeoExt.Version'
    ],
    alternateClassName: ['GeoExt.data.OWSStore'],

    config: {
        /**
         * The URL from which to retrieve the OWS document.
         *
         * @cfg {String}
         */
        url : null,

        /**
         * A parser for transforming the XHR response into an array of objects
         * representing attributes.
         *
         * @cfg {OpenLayers.Format}
         */
        format : null,

        /**
         * Any baseParams to use on this store.
         *
         * @cfg {Object}
         */
        baseParams: null
    },

    /**
     * @private
     */
    constructor: function(config) {
        // At this point, we have to copy the complex objects from the config
        // into the prototype. This is because Ext.data.Store's constructor
        // creates deep copies of these objects.
        if (config.format) {
            this.format = config.format;
            delete config.format;
        }

        this.callParent([config]);

        if(config.url) {
            this.setUrl(config.url);
        }
        if(this.format) {
            this.setFormat(this.format);
        }
        var proxy = this.getProxy();
        if (proxy) {
            proxy.startParam = false;
            proxy.limitParam = false;
            proxy.pageParam = false;
        }
        if (config.baseParams) {
            this.setBaseParams(config.baseParams);
        }
    },

    /**
     * @private
     */
    applyBaseParams: function(newParams) {
        if (newParams && Ext.isObject(newParams)) {
            var proxy = this.getProxy();
            if(proxy) {
                if (proxy.setExtraParams) {
                    // ExtJS 5 needs the setter
                    proxy.setExtraParams(newParams);
                } else {
                    proxy.extraParams = newParams;
                }
            }
        }
    },

    /**
     * @private
     */
    applyUrl: function(newValue) {
        if(newValue && Ext.isString(newValue)) {
            var proxy = this.getProxy();
            if(proxy) {
                if (proxy.setUrl){
                    // ExtJS 5 needs the setter
                    proxy.setUrl(newValue);
                } else {
                    proxy.url = newValue;
                }
            }
        }
    },

    /**
     * @private
     */
    applyFormat: function(newFormat) {
        var proxy = this.getProxy();
        var reader = (proxy) ? proxy.getReader() : null;
        if(reader) {
            if (reader.setFormat) {
                // ExtJS 5 needs the setter
                reader.setFormat(newFormat);
            } else {
                reader.format = newFormat;
            }
        }
    }
});
