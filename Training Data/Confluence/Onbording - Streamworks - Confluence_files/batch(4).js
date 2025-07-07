WRMCB=function(e){var c=console;if(c&&c.log&&c.error){c.log('Error running batched script.');c.error(e);}}
;
try {
/* module-key = 'confluence.web.resources:legacy-editor-global-AVOID-IF-POSSIBLE', location = 'includes/js/amd/shim/confluence-editor-amd.js' */
define("confluence/legacy-editor-global-AVOID-IF-POSSIBLE",[],function(){"undefined"===typeof Confluence&&(Confluence={});"undefined"===typeof Confluence.Editor&&(Confluence.Editor={});return Confluence.Editor});
}catch(e){WRMCB(e)};
;
try {
/* module-key = 'com.atlassian.plugins.shortcuts.atlassian-shortcuts-plugin:shortcuts', location = '/js/keycommands.js' */
AJS.bind("initialize.keyboardshortcuts",function(){var D=AJS.$,B=function(F){return(AJS.Data&&AJS.Data.get(F))||AJS.params[F]},A=B("build-number"),E=B("keyboardshortcut-hash");if(!A||!E){throw new Error("build-number and keyboardshortcut-hash must both exist in AJS.Data or AJS.params.")}var C=AJS.contextPath()+"/rest/shortcuts/latest/shortcuts/"+encodeURIComponent(A)+"/"+encodeURIComponent(E);D.getJSON(C,function(H){var F=H.shortcuts;if(!F){throw new Error("Server returned no shortcuts.")}AJS.trigger("shortcuts-loaded.keyboardshortcuts",{shortcuts:F});var I=[];var K={enableContext:function(M){var L=D.grep(F,function(N){return N.context===M});I=I.concat(AJS.whenIType.fromJSON(L,true))}};var G=function(){AJS.trigger("register-contexts.keyboardshortcuts",{shortcutRegistry:K})};G();AJS.bind("add-bindings.keyboardshortcuts",G);var J=function(){D.each(I,function(){this.unbind()});I=[]};AJS.bind("remove-bindings.keyboardshortcuts",J)})});
}catch(e){WRMCB(e)};
;
try {
/* module-key = 'com.atlassian.confluence.keyboardshortcuts:confluence-keyboard-shortcuts-soy', location = 'templates/confluence-keyboard-shortcuts.soy' */
// This file was automatically generated from confluence-keyboard-shortcuts.soy.
// Please don't edit this file by hand.

/**
 * @fileoverview Templates in namespace __KeyboardShortcutsDialog.
 */

if (typeof __KeyboardShortcutsDialog == 'undefined') { var __KeyboardShortcutsDialog = {}; }


__KeyboardShortcutsDialog.keyboardShortcutModule = function(opt_data, opt_ignored) {
  return '<div class="module"><div class="mod-header"><h3>' + soy.$$escapeHtml(opt_data.title) + '</h3></div><div class="mod-content"><ul class="mod-item"></ul></div></div>';
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialog.keyboardShortcutModule.soyTemplateName = '__KeyboardShortcutsDialog.keyboardShortcutModule';
}


__KeyboardShortcutsDialog.keyboardShortcutHelpLink = function(opt_data, opt_ignored) {
  return '' + Confluence.Templates.Dialog.customHelpLink({href: '' + soy.$$escapeHtml("https://confluence.atlassian.com/display/ConfCloud/Keyboard+Shortcuts%2C+Markdown%2C+and+Autocomplete"), text: '' + soy.$$escapeHtml('Alle K\xfcrzel')});
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialog.keyboardShortcutHelpLink.soyTemplateName = '__KeyboardShortcutsDialog.keyboardShortcutHelpLink';
}


__KeyboardShortcutsDialog.keyboardShortcutEnabledCheckbox = function(opt_data, opt_ignored) {
  return '<form name="shortcut-settings" id="shortcut-settings-form"><input type="checkbox" name="enabled" id="keyboard-shortcut-enabled-checkbox"><label for="keyboard-shortcut-enabled-checkbox">' + soy.$$escapeHtml('Allgemeine K\xfcrzel aktivieren') + '</label></form>';
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialog.keyboardShortcutEnabledCheckbox.soyTemplateName = '__KeyboardShortcutsDialog.keyboardShortcutEnabledCheckbox';
}


__KeyboardShortcutsDialog.keyboardShortcutPanel = function(opt_data, opt_ignored) {
  return '<div id=' + soy.$$escapeHtml(opt_data.panelId) + '><div class="keyboard-shortcut-dialog-panel-header"></div><div class="shortcutsmenu"></div><div class="keyboard-shortcut-dialog-panel-footer"></div></div>';
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialog.keyboardShortcutPanel.soyTemplateName = '__KeyboardShortcutsDialog.keyboardShortcutPanel';
}

}catch(e){WRMCB(e)};
;
try {
/* module-key = 'com.atlassian.confluence.keyboardshortcuts:confluence-keyboard-shortcuts-soy', location = 'js/confluence-keyboard-shortcuts-soy.js' */
/* eslint confluence/matching-tests:0 */
/* global __KeyboardShortcutsDialog */
define('confluence-keyboard-shortcuts/confluence-keyboard-shortcuts-soy', function () {
    "use strict";
    return __KeyboardShortcutsDialog;
});
}catch(e){WRMCB(e)};
;
try {
/* module-key = 'com.atlassian.confluence.keyboardshortcuts:confluence-keyboard-shortcuts-autoformat-tab-soy', location = 'templates/shortcut-dialog-tab-autoformat.soy' */
// This file was automatically generated from shortcut-dialog-tab-autoformat.soy.
// Please don't edit this file by hand.

/**
 * @fileoverview Templates in namespace __KeyboardShortcutsDialogAutoformat.
 */

if (typeof __KeyboardShortcutsDialogAutoformat == 'undefined') { var __KeyboardShortcutsDialogAutoformat = {}; }


__KeyboardShortcutsDialogAutoformat.configureAutocomplete = function(opt_data, opt_ignored) {
  return '<div id="keyboard-shortcut-autocomplete-message">' + soy.$$escapeHtml('Zum Konfigurieren von AutoVervollst\xe4ndigen') + ' <a target="_blank" href=' + soy.$$escapeHtml(opt_data.href) + '>' + soy.$$escapeHtml('gehen Sie zu Ihren Editor-Einstellungen') + '</a></div>';
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialogAutoformat.configureAutocomplete.soyTemplateName = '__KeyboardShortcutsDialogAutoformat.configureAutocomplete';
}


__KeyboardShortcutsDialogAutoformat.helpItem = function(opt_data, opt_ignored) {
  return '<li class="item-details"><span class="item-description wiki-content">' + opt_data.output + '</span><span class="' + opt_data.actionClass + ' item-action">' + opt_data.type + '</span></li>';
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialogAutoformat.helpItem.soyTemplateName = '__KeyboardShortcutsDialogAutoformat.helpItem';
}


__KeyboardShortcutsDialogAutoformat.simpleHelpItem = function(opt_data, opt_ignored) {
  return '' + __KeyboardShortcutsDialogAutoformat.helpItem({output: opt_data.output, type: '<code>' + opt_data.type + '</code>', actionClass: ''});
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialogAutoformat.simpleHelpItem.soyTemplateName = '__KeyboardShortcutsDialogAutoformat.simpleHelpItem';
}


__KeyboardShortcutsDialogAutoformat.tableHelpItem = function(opt_data, opt_ignored) {
  return '' + __KeyboardShortcutsDialogAutoformat.helpItem({output: opt_data.output, type: '<code>' + opt_data.type + '</code>', actionClass: 'table-action'});
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialogAutoformat.tableHelpItem.soyTemplateName = '__KeyboardShortcutsDialogAutoformat.tableHelpItem';
}


__KeyboardShortcutsDialogAutoformat.styleHelpItem = function(opt_data, opt_ignored) {
  return '' + __KeyboardShortcutsDialogAutoformat.helpItem({output: opt_data.output, type: '<code>' + opt_data.type + '</code>', actionClass: 'style-action'});
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialogAutoformat.styleHelpItem.soyTemplateName = '__KeyboardShortcutsDialogAutoformat.styleHelpItem';
}


__KeyboardShortcutsDialogAutoformat.keyboardShortcutItem = function(opt_data, opt_ignored) {
  return '' + __KeyboardShortcutsDialogAutoformat.helpItem({output: '' + soy.$$escapeHtml(opt_data.output), type: '<kbd class="regular-key">' + soy.$$escapeHtml(opt_data.type) + '</kbd>', actionClass: ''});
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialogAutoformat.keyboardShortcutItem.soyTemplateName = '__KeyboardShortcutsDialogAutoformat.keyboardShortcutItem';
}


__KeyboardShortcutsDialogAutoformat.emoticonHelpItem = function(opt_data, opt_ignored) {
  return '' + __KeyboardShortcutsDialogAutoformat.simpleHelpItem({output: '<img src=' + soy.$$escapeHtml(opt_data.src) + '></img>', type: opt_data.type});
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialogAutoformat.emoticonHelpItem.soyTemplateName = '__KeyboardShortcutsDialogAutoformat.emoticonHelpItem';
}


__KeyboardShortcutsDialogAutoformat.boldDescription = function(opt_data, opt_ignored) {
  return '<b>' + soy.$$escapeHtml('Fett') + '</b> ' + soy.$$escapeHtml('Text');
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialogAutoformat.boldDescription.soyTemplateName = '__KeyboardShortcutsDialogAutoformat.boldDescription';
}


__KeyboardShortcutsDialogAutoformat.underlineDescription = function(opt_data, opt_ignored) {
  return '<span style="text-decoration: underline;">' + soy.$$escapeHtml('Unterstreichen') + '</span> ' + soy.$$escapeHtml('Text');
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialogAutoformat.underlineDescription.soyTemplateName = '__KeyboardShortcutsDialogAutoformat.underlineDescription';
}


__KeyboardShortcutsDialogAutoformat.strikethroughDescription = function(opt_data, opt_ignored) {
  return '<span style="text-decoration: line-through;">' + soy.$$escapeHtml('Durchgestrichen') + '</span> ' + soy.$$escapeHtml('Text');
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialogAutoformat.strikethroughDescription.soyTemplateName = '__KeyboardShortcutsDialogAutoformat.strikethroughDescription';
}


__KeyboardShortcutsDialogAutoformat.italicDescription = function(opt_data, opt_ignored) {
  return '<em>' + soy.$$escapeHtml('Kursiv') + '</em> ' + soy.$$escapeHtml('Text');
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialogAutoformat.italicDescription.soyTemplateName = '__KeyboardShortcutsDialogAutoformat.italicDescription';
}


__KeyboardShortcutsDialogAutoformat.monospaceDescription = function(opt_data, opt_ignored) {
  return '<code>' + soy.$$escapeHtml('Festbreitenschriftart') + '</code> ' + soy.$$escapeHtml('Text');
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialogAutoformat.monospaceDescription.soyTemplateName = '__KeyboardShortcutsDialogAutoformat.monospaceDescription';
}


__KeyboardShortcutsDialogAutoformat.tableDescription = function(opt_data, opt_ignored) {
  return '<table class="confluenceTable"><tbody><tr><td class="confluenceTd">' + soy.$$escapeHtml('erste Zelle') + '</td><td class="confluenceTd">&nbsp;</td><td class="confluenceTd">&nbsp;</td><td class="confluenceTd">&nbsp;</td></tr></tbody></table>';
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialogAutoformat.tableDescription.soyTemplateName = '__KeyboardShortcutsDialogAutoformat.tableDescription';
}


__KeyboardShortcutsDialogAutoformat.tableWithHeadingsDiscriptions = function(opt_data, opt_ignored) {
  return '<table class="confluenceTable"><tbody><tr><th class="confluenceTh">' + soy.$$escapeHtml('\xdcberschrift') + '</th><th class="confluenceTh">' + soy.$$escapeHtml('\xdcberschrift') + '</th></tr><tr><td class="confluenceTd">&#8203;</td><td class="confluenceTd">&#8203;</td></tr></tbody></table>';
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialogAutoformat.tableWithHeadingsDiscriptions.soyTemplateName = '__KeyboardShortcutsDialogAutoformat.tableWithHeadingsDiscriptions';
}


__KeyboardShortcutsDialogAutoformat.h1Description = function(opt_data, opt_ignored) {
  return '<h1>' + soy.$$escapeHtml('\xdcberschrift') + '</h1>';
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialogAutoformat.h1Description.soyTemplateName = '__KeyboardShortcutsDialogAutoformat.h1Description';
}


__KeyboardShortcutsDialogAutoformat.h3Description = function(opt_data, opt_ignored) {
  return '<h3>' + soy.$$escapeHtml('\xdcberschrift') + '</h3>';
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialogAutoformat.h3Description.soyTemplateName = '__KeyboardShortcutsDialogAutoformat.h3Description';
}


__KeyboardShortcutsDialogAutoformat.bqDescription = function(opt_data, opt_ignored) {
  return '<blockquote>' + soy.$$escapeHtml('Zitat') + '</blockquote>';
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialogAutoformat.bqDescription.soyTemplateName = '__KeyboardShortcutsDialogAutoformat.bqDescription';
}


__KeyboardShortcutsDialogAutoformat.numberedListDescription = function(opt_data, opt_ignored) {
  return '<ol><li>' + soy.$$escapeHtml('Liste') + '</li></ol>';
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialogAutoformat.numberedListDescription.soyTemplateName = '__KeyboardShortcutsDialogAutoformat.numberedListDescription';
}


__KeyboardShortcutsDialogAutoformat.bulletedListDescription = function(opt_data, opt_ignored) {
  return '<ul><li>' + soy.$$escapeHtml('Aufz\xe4hlungszeichen') + '</li></ul>';
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialogAutoformat.bulletedListDescription.soyTemplateName = '__KeyboardShortcutsDialogAutoformat.bulletedListDescription';
}


__KeyboardShortcutsDialogAutoformat.inlineTaskListDescription = function(opt_data, opt_ignored) {
  return '<ul class="inline-task-list"><li>task</li></ul>';
};
if (goog.DEBUG) {
  __KeyboardShortcutsDialogAutoformat.inlineTaskListDescription.soyTemplateName = '__KeyboardShortcutsDialogAutoformat.inlineTaskListDescription';
}

}catch(e){WRMCB(e)};
;
try {
/* module-key = 'com.atlassian.confluence.keyboardshortcuts:confluence-keyboard-shortcuts-autoformat-tab-soy', location = 'js/shortcut-dialog-tab-autoformat-soy.js' */
/* eslint confluence/matching-tests:0 */
/* global __KeyboardShortcutsDialogAutoformat */
define('confluence-keyboard-shortcuts/shortcut-dialog-tab-autoformat-soy', function () {
    "use strict";
    return __KeyboardShortcutsDialogAutoformat;
});
}catch(e){WRMCB(e)};
;
try {
/* module-key = 'com.atlassian.confluence.keyboardshortcuts:confluence-keyboard-shortcuts-autoformat-tab', location = 'js/shortcut-dialog-tab-autoformat.js' */
define('confluence-keyboard-shortcuts/shortcut-dialog-tab-autoformat', [
    'ajs',
    'confluence-keyboard-shortcuts/confluence-keyboard-shortcuts-soy',
    'confluence-keyboard-shortcuts/shortcut-dialog-tab-autoformat-soy',
    'jquery'
], function(
    AJS,
    DialogTemplates,
    templates,
    $
) {
    "use strict";

    // An object containing the new button definitions for the ADG3 styling.
    // TODO: Replace defaults with these definitions when the editor ADG3 styling is made the default setting.
    var adg3Items = {
        strikethrough: {
            context: "autoformat.font_formatting",
            description: templates.strikethroughDescription(),
            action: "~~Durchgestrichen~~"
        },
        bold: {
            context: "autoformat.font_formatting",
            description: templates.boldDescription(),
            action: "**Fett** oder __Fett__"
        },
        italic: {
            context: "autoformat.font_formatting",
            description: templates.italicDescription(),
            action: "*Kursiv* oder _Kursiv_"
        },
        monospace: {
            context: "autoformat.font_formatting",
            description: templates.monospaceDescription(),
            action: "Festbreitenschriftart"
        },
        h1: {
            context: "autoformat.styles",
            description: templates.h1Description(),
            action: "# \u00dcberschrift\u00a01"
        },
        h3: {
            context: "autoformat.styles",
            description: templates.h3Description(),
            action: "### \u00dcberschrift\u00a03"
        },
        bq: {
            context: "autoformat.styles",
            description: templates.bqDescription(),
            action: "\u003e Anf\u00fchrungszeichen"
        },
        ol: {
            context: "autoformat.lists",
            description: templates.numberedListDescription(),
            action: "1.\u00a0Liste"
        }
    };


    /*
     Adds the "Editor Autoformatting" tab to the Keyboard Shortcuts help dialog
     */

    var AutoformatItems = [
        adg3Items.bold,
        adg3Items.strikethrough,
        adg3Items.italic,
        adg3Items.monospace,
        {
            context: "autoformat.tables",
            description: templates.tableDescription(),
            action: "||||| + eingeben"
        },
        {
            context: "autoformat.tables",
            description: templates.tableWithHeadingsDiscriptions(),
            action: "||\u00dcberschrift||\u00dcberschrift||"
        },
        adg3Items.h1,
        adg3Items.h3,
        adg3Items.bq,
        {
            context: "autoformat.emoticons",
            img: "check.png",
            action: "(/)"
        },
        {
            context: "autoformat.emoticons",
            img: "smile.png",
            action: "::)"
        },
        adg3Items.ol,
        {
            context: "autoformat.lists",
            description: templates.bulletedListDescription(),
            action: "* Aufz\u00e4hlungszeichen"
        },
        {
            context: "autoformat.lists",
            description: templates.inlineTaskListDescription(),
            action: "[] Aufgabe"
        },
        {
            context: "autoformat.autocomplete",
            description: "Image/Media",
            action: "!"
        },
        {
            context: "autoformat.autocomplete",
            description: "Verkn\u00fcpfung",
            action: "["
        },
        {
            context: "autoformat.autocomplete",
            description: "Makro",
            action: "{"
        }
    ];

    var buildShortcutModule = function (title, context, itemBuilder) {
        var module = $(DialogTemplates.keyboardShortcutModule({title: title}));
        var list = module.find("ul");
        var items = getMenuItemsForContext(context);

        for (var i = 0, ii = items.length; i < ii; i++) {
            list.append(
                itemBuilder(items[i])
            );
        }

        return module;
    };

    var buildStandardShortcutModule = function (title, context, itemTemplate) {
        return buildShortcutModule(
            title,
            context,
            function (item) {
                return itemTemplate({output: item.description, type: item.action});
            }
        );
    };

    var buildEmoticonModule = function (title, context) {
        var emoticonResourceUrl = AJS.params.staticResourceUrlPrefix + "/images/icons/emoticons/";
        return buildShortcutModule(
            title,
            context,
            function (item) {
                return templates.emoticonHelpItem(
                    {src: emoticonResourceUrl + item.img, type: item.action}
                );
            }
        );
    };

    var getMenuItemsForContext = function (context) {
        return $.grep(AutoformatItems, function (e) {
            return e.context === context;
        });
    };

    var buildHelpPanel = function () {
        var autoformatHelpPanel = $(DialogTemplates.keyboardShortcutPanel({panelId: 'autoformat-shortcuts-panel'}));
        var autoformatHelpPanelMenu = autoformatHelpPanel.children(".shortcutsmenu");

        autoformatHelpPanelMenu.append(
            buildStandardShortcutModule(
                "Schriftartformatierung",
                "autoformat.font_formatting",
                templates.simpleHelpItem
            )
        );
        autoformatHelpPanelMenu.append(
            buildStandardShortcutModule("AutoVervollst\u00e4ndigen",
                "autoformat.autocomplete",
                templates.keyboardShortcutItem
            )
        );
        autoformatHelpPanelMenu.append(
            buildStandardShortcutModule(
                "Tabellen",
                "autoformat.tables",
                templates.tableHelpItem
            )
        );
        autoformatHelpPanelMenu.append(
            buildStandardShortcutModule(
                "Formate",
                "autoformat.styles",
                templates.styleHelpItem
            ).addClass("styles-module")
        );
        autoformatHelpPanelMenu.append(
            buildEmoticonModule(
                "Emoticons",
                "autoformat.emoticons"
            )
        );
        autoformatHelpPanelMenu.append(
            buildStandardShortcutModule(
                "Listen",
                "autoformat.lists",
                templates.simpleHelpItem
            )
        );

        if (AJS.Meta.get("remote-user")) {
            autoformatHelpPanel.find(".keyboard-shortcut-dialog-panel-header").append(
                templates.configureAutocomplete(
                    {href: AJS.contextPath() + "/users/viewmyeditorsettings.action"}
                )
            );
        }

        return autoformatHelpPanel;
    };

    return buildHelpPanel;

});
}catch(e){WRMCB(e)};
;
try {
/* module-key = 'com.atlassian.confluence.keyboardshortcuts:confluence-keyboard-shortcuts', location = 'js/confluence-keyboard-shortcuts.js' */
define('confluence-keyboard-shortcuts/confluence-keyboard-shortcuts', [
    'ajs',
    'jquery',
    'confluence-keyboard-shortcuts/confluence-keyboard-shortcuts-soy',
    'window',
    'confluence/dialog',
    'confluence-keyboard-shortcuts/shortcut-dialog-tab-autoformat'
], function(
    AJS,
    $,
    DialogTemplates,
    window,
    ConfluenceDialog,
    buildAutoformatPanel
) {
    "use strict";

    var popup;

    var shortcutsInitialisation = function() {
        AJS.debug("confluence-keyboard-shortcuts initialising");

        // CGP-151/CONFDEV-811 - Skip this if you are in the Page Gadget
        if (AJS.PageGadget || (window.parent.AJS && window.parent.AJS.PageGadget)) {
            AJS.debug("Inside the Page Gadget. Skipping keyboard shortcuts");
            return;
        }

        KeyboardShortcuts.enabled = AJS.Meta.getBoolean('use-keyboard-shortcuts');

        AJS.bind("shortcuts-loaded.keyboardshortcuts", function (e, data) {
            KeyboardShortcuts.shortcuts = data.shortcuts;
            $("#keyboard-shortcuts-link").click(KeyboardShortcuts.openDialog);
        });

        AJS.bind("register-contexts.keyboardshortcuts", function(e, data){

            // Only bind the shortcuts for contexts if the user has the preference set
            if (!KeyboardShortcuts.enabled) {
                return;
            }
            // Here we bind to register-contexts.keyboardshortcuts so that we can select which
            // keyboard shortcut contexts should be enabled. We use jQuery selectors to determine
            // which keyboard shortcut contexts are applicable to a page.

            var shortcutRegistry = data.shortcutRegistry;

            //See CONFDEV-12510 for why we need to check that Editor.isVisible exists.
            var editorVisible = window.Confluence && window.Confluence.Editor && window.Confluence.Editor.isVisible && window.Confluence.Editor.isVisible();
            $("#action-menu-link").length && !editorVisible && shortcutRegistry.enableContext("viewcontent");
            $("#viewPageLink").length && shortcutRegistry.enableContext("viewinfo");

            if (editorVisible) {
                shortcutRegistry.enableContext("adg3.tinymce.actions");

                var tinymce = require('tinymce');

                // tinymce shortcuts are added through the tinymce apis
                var ed = tinymce.activeEditor;
                var editorForm = $("#rte").closest("form");
                $.each(KeyboardShortcuts.shortcuts, function(i, shortcut) {
                    if (shortcut.context.indexOf("tinymce") !== 0) {
                        return;
                    }
                    var operation = shortcut.op;
                    var param = shortcut.param;
                    $.each(shortcut.keys, function() {
                        var shortcutKey = this;
                        var shortcutFunc;
                        if (operation == "click") {
                            shortcutFunc = function() {
                                $(param).click();
                            };
                        }
                        else if (operation == "execute") {
                            shortcutFunc = param;
                        }
                        if (shortcutFunc) {
                            if ($.isArray(shortcutKey)) {
                                shortcutKey = shortcutKey.join(",");
                            }
                            var sk = shortcutKey.toLowerCase();
                            // CONFDEV-54259: tinymce 4x keyboard mapping is different from tinymce 3x
                            var shortCutCombo = parseInt(tinymce.majorVersion, 10) >= 4 && tinymce.isMac ? sk.replace('ctrl', 'meta') : sk;
                            AJS.debug("Adding shortcut for " + shortCutCombo);
                            ed.addShortcut(shortCutCombo, "", shortcutFunc);
                        } else {
                            AJS.logError("ERROR: unkown editor shortcut key operation " + operation + " for shortcut " + shortcutKey);
                        }
                    });
                });
            }

            KeyboardShortcuts.ready = true;
        });

        // Why is this if statment needed? It seems that when we are ready to do an import, the pluginsystem is up, and we
        // pull down the super batch. This superbatch contains this code and it fires off a request to Confluence to get the
        // i18n resources. This request gets redirected to 'selectsetupstep.action' which due to the fact that the import is
        // running thinks we are done, and redirects to 'finishsetup.action' and things blow up.
        if (typeof AJS.contextPath() !== "undefined" && KeyboardShortcuts.enabled) {
            if ($("#rte").length) { //If there is an editor on the page wait for it to load before initializing shortcuts
                AJS.bind("init.rte", function() {
                    AJS.trigger("initialize.keyboardshortcuts");
                });
            } else {
                AJS.trigger("initialize.keyboardshortcuts");
            }
        }
    };

    // Add functions that are referenced from the execute shortcut operations in atlassian-plugin.xml here
    var KeyboardShortcuts = {
        Autoformat: [],
        Editor: [], // hack for jira issue plugin, remove once the plugin has been updated
        enabled: false,
        ready: false,
        dialog: null,
        closeDialog: function() {
            getDialog().then(function(dialog) {
                dialog.hide();
            });
            return false;
        },
        openDialog: function() {
            // remove "interactive" class from menu item. with "interactive" class, the menu does not close when clicking
            // on a menu item. "interactive" class added by help-analytics.js from atlassian-nav-links-plugin-3.2.12
            $(this).removeClass("interactive");
            getDialog().then(function(dialog) {
                dialog.show();
            });
            return false;
        }
    };

    var getDialog = function () {
        var dfr = $.Deferred();

        if (popup) {
            goToEditorTabWhenEditorIsOpened();
            return dfr.resolve(popup);
        }

        var shortcuts = KeyboardShortcuts.shortcuts;

        var cancel = function () {
            AJS.debug("Hiding Shortcuts help");
            popup.hide();
            return false;
        };

        //Same technique as tinyMCE.
        var isMac = window.navigator.platform.indexOf('Mac') !== -1;

        //Construct the key sequence diagram shown on the keyboard shortcuts help dialog
        //e.g. shortcut.keys = [["g", "d"]]
        var makeKeySequence = function (shortcut) {
            var sequenceSpan = AJS("span").addClass("item-action");
            // TODO - may need "or" in future if keys has length > 1
            var keySequence = shortcut.keys[0];

            for (var i = 0; i < keySequence.length; i++) {
                if (i > 0) {
                    sequenceSpan.append(makeKbdSeparator("dann"));
                }

                makeKeyCombo(keySequence[i], sequenceSpan);
            }

            return sequenceSpan;
        };

        var makeKeyCombo = function (combo, sequence) {
            var keys = combo.split("+");

            for (var i = 0; i < keys.length; i++) {
                if (i > 0) {
                    sequence.append(makeKbdSeparator("+"));
                }

                makeKeyAlternatives(keys[i], sequence);
            }
        };

        var makeKeyAlternatives = function (key, sequence) {
            var keys = key.split("..");

            for (var i = 0; i < keys.length; i++) {
                if (i > 0) {
                    sequence.append(makeKbdSeparator("bis"));
                }

                sequence.append(makeKbd(keys[i]));
            }
        };

        var makeKbd = function (key) {
            var kbd = AJS("kbd");
            var text;

            switch (key) {
                case "Shift":
                case "Sh":
                    kbd.text("Shift");
                    kbd.addClass("modifier-key");
                    break;
                case "Ctrl":
                    text = isMac ? '\u2318' : "Strg";  //Apple command key
                    kbd.text(text);
                    kbd.addClass("modifier-key");
                    break;
                case "Tab":
                    kbd.text("Tab");
                    kbd.addClass("modifier-key");
                    break;
                case "Alt":
                    kbd.text("Alt");
                    kbd.addClass("modifier-key");
                    break;
                case "LeftAlt":
                    //Option key for Mac, LeftAlt key for PC
                    text = isMac ? "Option" : "Alt links";
                    kbd.text(text);
                    kbd.addClass("modifier-key");
                    break;
                case "Control":
                    //Control key of Mac
                    kbd.text("Steuerelement");
                    kbd.addClass("modifier-key");
                    break;
                case "Option":
                    //Option key of Mac
                    kbd.text("Option");
                    kbd.addClass("modifier-key");
                    break;
                case "UpArrow":
                    //Option key of Mac
                    kbd.text("\u2191");
                    kbd.addClass("regular-key");
                    break;
                case "DownArrow":
                    //Option key of Mac
                    kbd.text("\u2193");
                    kbd.addClass("regular-key");
                    break;
                case "LeftArrow":
                    //Option key of Mac
                    kbd.text("\u2190");
                    kbd.addClass("regular-key");
                    break;
                case "RightArrow":
                    //Option key of Mac
                    kbd.text("\u2192");
                    kbd.addClass("regular-key");
                    break;
                default:
                    kbd.text(key);
                    kbd.addClass("regular-key");
            }

            return kbd;
        };

        var makeKbdSeparator = function (text) {
            var separator = AJS("span");
            separator.text(text);
            separator.addClass("key-separator");
            return separator;
        };

        var makeShortcutModule = function (title, contexts, shortcuts) {
            var module = $(DialogTemplates.keyboardShortcutModule({title: title}));
            var list = module.find("ul");

            for (var i = 0; i < shortcuts.length; i++) {
                var shortcut = shortcuts[i];

                if (shortcut.hidden) {
                    continue;
                }

                if ($.inArray(shortcut.context, contexts) !== -1) {
                    var shortcutItem = AJS("li").addClass("item-details");
                    var text = shortcut.description;
                    var desc = AJS("strong").addClass("item-description").append(text);
                    shortcutItem.append(desc);
                    shortcutItem.append(makeKeySequence(shortcut));
                    list.append(shortcutItem);
                }
            }

            return module;
        };

        var makeGeneralShortcutsMenu = function () {
            var generalShortcutsMenuPane = $(DialogTemplates.keyboardShortcutPanel({panelId: "general-shortcuts-panel"}));
            var generalShortcutsMenu = $(generalShortcutsMenuPane).children(".shortcutsmenu");

            if (AJS.Meta.get("atlassian-account-id")) {
                generalShortcutsMenuPane.find(".keyboard-shortcut-dialog-panel-header").append(DialogTemplates.keyboardShortcutEnabledCheckbox());
            }

            var isLivePagesOpenBetaEnabled = AJS.DarkFeatures.isEnabled("confluence_live_pages_open_beta_trait_opted_in");
            var actionsText = isLivePagesOpenBetaEnabled ? "Seite / Live-Dokument / Aktionen f\u00fcr Blogposts" :
                "Seiten-/Blog-Eintrag-Aktionen";

            generalShortcutsMenu.append(makeShortcutModule("Globale K\u00fcrzel", ["global"], shortcuts));
            generalShortcutsMenu.append(makeShortcutModule(actionsText, ["viewcontent", "viewinfo"], shortcuts));

            return generalShortcutsMenuPane;
        };

        var makeEditorShortcutsMenu = function () {
            var editorShortcutsMenuPane = $(DialogTemplates.keyboardShortcutPanel({panelId: "editor-shortcuts-panel"}));
            var editorShortcutsMenu = $(editorShortcutsMenuPane).children(".shortcutsmenu");
            var blockContexts = ["tinymce.block"];
            var richContexts = ["tinymce.rich"];
            var actionContexts = ["tinymce.actions"];

                // CONFDEV-57495
                editorShortcutsMenuPane.addClass("foxy-ux-enhancement");

                blockContexts = ["adg3.tinymce.block"];
                richContexts = ["adg3.tinymce.rich"];
                richContexts.push(isMac ? "adg3.tinymce.rich.mac" : "adg3.tinymce.rich.win");
                actionContexts = ["adg3.tinymce.actions"];
                actionContexts.push(isMac ? "adg3.tinymce.actions.mac" : "adg3.tinymce.actions.win");

            editorShortcutsMenu.append(makeShortcutModule("Block-Formatierung", blockContexts, shortcuts));
            editorShortcutsMenu.append(makeShortcutModule("Umfangreiche Formatierung", richContexts, shortcuts));
            editorShortcutsMenu.append(makeShortcutModule("Bearbeitungsaktionen", actionContexts, shortcuts));

            return editorShortcutsMenuPane;
        };

        var toggleEnabled = function (event) {
            var enable = $(this).prop('checked');
            // TODO - after 3.4-m4 and blitz - error handling architecture
            $.ajax(
                {
                    type: "POST",
                    url: AJS.contextPath() + "/rest/confluenceshortcuts/latest/enabled",
                    data: JSON.stringify({
                        enabled: enable
                    }),
                    dataType: "json",
                    contentType: "application/json"
                }).done(function () {
                KeyboardShortcutsObject.keyboardShortcuts.enabled = enable;
                KeyboardShortcutsObject.keyboardShortcuts.ready = false;
                if (enable) {
                    AJS.trigger("add-bindings.keyboardshortcuts");
                } else {
                    AJS.trigger("remove-bindings.keyboardshortcuts");
                }
            });
        };

        var initialiseEnableShortcutsCheckbox = function () {
            $('#keyboard-shortcut-enabled-checkbox')
                .prop('checked', KeyboardShortcutsObject.keyboardShortcuts.enabled)
                .click(toggleEnabled);
        };

        popup = ConfluenceDialog.component({
            width: 950,
            height: 660,
            id: "keyboard-shortcuts-dialog"
        });


        function goToEditorTabWhenEditorIsOpened() {
            // If you have an editor visible automatically open the Editor tab.
            var editorVisible = window.Confluence && window.Confluence.Editor && window.Confluence.Editor.isVisible && window.Confluence.Editor.isVisible();

            if (editorVisible) {
                popup.overrideLastTab();
                popup.gotoPanel(1);
            } else {
                popup.gotoPanel(0);
            }
        }

        popup.addHeader("Tastenkombinationen");
        popup.addPanel("Allgemein", makeGeneralShortcutsMenu());
        popup.addPanel("Editor", makeEditorShortcutsMenu());
        popup.addPanel("Editor-Autoformatierung", buildAutoformatPanel());
        popup.addCancel("Schlie\u00dfen", cancel);
        // CONFDEV-12853: Add help link via prepend() instead of append() to prevent FF display issue
        popup.popup.element.find(".dialog-title").prepend(DialogTemplates.keyboardShortcutHelpLink());
        AJS.trigger("keyboard-shortcut-dialog-ready", popup);

        goToEditorTabWhenEditorIsOpened();

        dfr.resolve(popup);
        initialiseEnableShortcutsCheckbox();
        return dfr;
    };

    var KeyboardShortcutsObject = {};
    KeyboardShortcutsObject.init = shortcutsInitialisation;
    KeyboardShortcutsObject.keyboardShortcuts = KeyboardShortcuts;

    return KeyboardShortcutsObject;
});

require('confluence/module-exporter').safeRequire('confluence-keyboard-shortcuts/confluence-keyboard-shortcuts', function(KeyboardShortcuts) {
    var AJS = require('ajs');
    Confluence.KeyboardShortcuts = KeyboardShortcuts.keyboardShortcuts;
    AJS.toInit(KeyboardShortcuts.init);
});
}catch(e){WRMCB(e)};