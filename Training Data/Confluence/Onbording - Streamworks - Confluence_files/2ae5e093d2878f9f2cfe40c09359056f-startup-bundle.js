/*! For license information please see startup-bundle.js.LICENSE.txt */
(()=>{var t={1557:(t,e)=>{"use strict";Object.defineProperty(e,"__esModule",{value:!0})},2497:(t,e)=>{"use strict";function r(t){
return r="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},r(t)}function n(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,o(n.key),n)}}function o(t){var e=function(t,e){
if("object"!=r(t)||!t)return t;var n=t[Symbol.toPrimitive];if(void 0!==n){var o=n.call(t,e||"default");if("object"!=r(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==r(e)?e:e+""}
Object.defineProperty(e,"__esModule",{value:!0}),e.Page=void 0;var i=function(){return t=function t(e){!function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.client=e},(e=[{key:"createPage",value:function(t,e){var r={
url:"/api/v2/pages",type:"POST",queryParams:{embedded:null==e?void 0:e.embedded,private:null==e?void 0:e.private},requestBody:{spaceId:t.spaceId,status:t.status,
title:t.title,parentId:t.parentId,body:t.body}};return this.client.sendRequest(r)}},{key:"getPageById",value:function(t,e){var r={url:"/api/v2/pages/".concat(t),
type:"GET",queryParams:{"body-format":null==e?void 0:e["body-format"],"get-draft":null==e?void 0:e["get-draft"],version:null==e?void 0:e.version}}
;return this.client.sendRequest(r)}},{key:"deletePage",value:function(t){var e={url:"/api/v2/pages/".concat(t),type:"DELETE"};return this.client.sendRequest(e)}},{
key:"updatePage",value:function(t,e){var r={url:"/api/v2/pages/".concat(t),type:"PUT",requestBody:{id:e.id,status:e.status,title:e.title,spaceId:e.spaceId,
parentId:e.parentId,body:e.body,version:e.version}};return this.client.sendRequest(r)}}])&&n(t.prototype,e),r&&n(t,r),Object.defineProperty(t,"prototype",{
writable:!1}),t;var t,e,r}();e.Page=i},4205:(t,e)=>{"use strict";function r(t){return r="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){
return typeof t}:function(t){return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},r(t)}function n(t,e){
for(var r=0;r<e.length;r++){var n=e[r];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,o(n.key),n)}}
function o(t){var e=function(t,e){if("object"!=r(t)||!t)return t;var n=t[Symbol.toPrimitive];if(void 0!==n){var o=n.call(t,e||"default");if("object"!=r(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==r(e)?e:e+""}
Object.defineProperty(e,"__esModule",{value:!0}),e.Content=void 0;var i=function(){return t=function t(e){!function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.client=e},(e=[{key:"getContentType",value:function(t){var e={
url:"/api/v2/content/convert-ids-to-types",type:"POST",requestBody:{contentIds:t.contentIds}};return this.client.sendRequest(e)}}])&&n(t.prototype,e),r&&n(t,r),
Object.defineProperty(t,"prototype",{writable:!1}),t;var t,e,r}();e.Content=i},6032:(t,e,r)=>{"use strict";function n(t){
return n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},n(t)}function o(){o=function(){return e}
;var t,e={},r=Object.prototype,i=r.hasOwnProperty,a=Object.defineProperty||function(t,e,r){t[e]=r.value
},s="function"==typeof Symbol?Symbol:{},u=s.iterator||"@@iterator",c=s.asyncIterator||"@@asyncIterator",l=s.toStringTag||"@@toStringTag";function f(t,e,r){
return Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}),t[e]}try{f({},"")}catch(t){f=function(t,e,r){return t[e]=r}}
function h(t,e,r,n){var o=e&&e.prototype instanceof b?e:b,i=Object.create(o.prototype),s=new I(n||[]);return a(i,"_invoke",{value:j(t,r,s)}),i}function p(t,e,r){try{
return{type:"normal",arg:t.call(e,r)}}catch(t){return{type:"throw",arg:t}}}e.wrap=h;var d="suspendedStart",y="suspendedYield",v="executing",g="completed",m={}
;function b(){}function w(){}function _(){}var x={};f(x,u,(function(){return this}));var P=Object.getPrototypeOf,S=P&&P(P(L([])));S&&S!==r&&i.call(S,u)&&(x=S)
;var E=_.prototype=b.prototype=Object.create(x);function O(t){["next","throw","return"].forEach((function(e){f(t,e,(function(t){return this._invoke(e,t)}))}))}
function k(t,e){function r(o,a,s,u){var c=p(t[o],t,a);if("throw"!==c.type){var l=c.arg,f=l.value
;return f&&"object"==n(f)&&i.call(f,"__await")?e.resolve(f.__await).then((function(t){r("next",t,s,u)}),(function(t){r("throw",t,s,u)
})):e.resolve(f).then((function(t){l.value=t,s(l)}),(function(t){return r("throw",t,s,u)}))}u(c.arg)}var o;a(this,"_invoke",{value:function(t,n){function i(){
return new e((function(e,o){r(t,n,e,o)}))}return o=o?o.then(i,i):i()}})}function j(e,r,n){var o=d;return function(i,a){
if(o===v)throw Error("Generator is already running");if(o===g){if("throw"===i)throw a;return{value:t,done:!0}}for(n.method=i,n.arg=a;;){var s=n.delegate;if(s){
var u=C(s,n);if(u){if(u===m)continue;return u}}if("next"===n.method)n.sent=n._sent=n.arg;else if("throw"===n.method){if(o===d)throw o=g,n.arg
;n.dispatchException(n.arg)}else"return"===n.method&&n.abrupt("return",n.arg);o=v;var c=p(e,r,n);if("normal"===c.type){if(o=n.done?g:y,c.arg===m)continue;return{
value:c.arg,done:n.done}}"throw"===c.type&&(o=g,n.method="throw",n.arg=c.arg)}}}function C(e,r){var n=r.method,o=e.iterator[n];if(o===t)return r.delegate=null,
"throw"===n&&e.iterator.return&&(r.method="return",r.arg=t,C(e,r),"throw"===r.method)||"return"!==n&&(r.method="throw",
r.arg=new TypeError("The iterator does not provide a '"+n+"' method")),m;var i=p(o,e.iterator,r.arg);if("throw"===i.type)return r.method="throw",r.arg=i.arg,
r.delegate=null,m;var a=i.arg;return a?a.done?(r[e.resultName]=a.value,r.next=e.nextLoc,"return"!==r.method&&(r.method="next",r.arg=t),r.delegate=null,
m):a:(r.method="throw",r.arg=new TypeError("iterator result is not an object"),r.delegate=null,m)}function T(t){var e={tryLoc:t[0]};1 in t&&(e.catchLoc=t[1]),
2 in t&&(e.finallyLoc=t[2],e.afterLoc=t[3]),this.tryEntries.push(e)}function A(t){var e=t.completion||{};e.type="normal",delete e.arg,t.completion=e}function I(t){
this.tryEntries=[{tryLoc:"root"}],t.forEach(T,this),this.reset(!0)}function L(e){if(e||""===e){var r=e[u];if(r)return r.call(e);if("function"==typeof e.next)return e
;if(!isNaN(e.length)){var o=-1,a=function r(){for(;++o<e.length;)if(i.call(e,o))return r.value=e[o],r.done=!1,r;return r.value=t,r.done=!0,r};return a.next=a}}
throw new TypeError(n(e)+" is not iterable")}return w.prototype=_,a(E,"constructor",{value:_,configurable:!0}),a(_,"constructor",{value:w,configurable:!0}),
w.displayName=f(_,l,"GeneratorFunction"),e.isGeneratorFunction=function(t){var e="function"==typeof t&&t.constructor
;return!!e&&(e===w||"GeneratorFunction"===(e.displayName||e.name))},e.mark=function(t){return Object.setPrototypeOf?Object.setPrototypeOf(t,_):(t.__proto__=_,
f(t,l,"GeneratorFunction")),t.prototype=Object.create(E),t},e.awrap=function(t){return{__await:t}},O(k.prototype),f(k.prototype,c,(function(){return this})),
e.AsyncIterator=k,e.async=function(t,r,n,o,i){void 0===i&&(i=Promise);var a=new k(h(t,r,n,o),i);return e.isGeneratorFunction(r)?a:a.next().then((function(t){
return t.done?t.value:a.next()}))},O(E),f(E,l,"Generator"),f(E,u,(function(){return this})),f(E,"toString",(function(){return"[object Generator]"})),
e.keys=function(t){var e=Object(t),r=[];for(var n in e)r.push(n);return r.reverse(),function t(){for(;r.length;){var n=r.pop();if(n in e)return t.value=n,t.done=!1,t
}return t.done=!0,t}},e.values=L,I.prototype={constructor:I,reset:function(e){if(this.prev=0,this.next=0,this.sent=this._sent=t,this.done=!1,this.delegate=null,
this.method="next",this.arg=t,this.tryEntries.forEach(A),!e)for(var r in this)"t"===r.charAt(0)&&i.call(this,r)&&!isNaN(+r.slice(1))&&(this[r]=t)},stop:function(){
this.done=!0;var t=this.tryEntries[0].completion;if("throw"===t.type)throw t.arg;return this.rval},dispatchException:function(e){if(this.done)throw e;var r=this
;function n(n,o){return s.type="throw",s.arg=e,r.next=n,o&&(r.method="next",r.arg=t),!!o}for(var o=this.tryEntries.length-1;o>=0;--o){
var a=this.tryEntries[o],s=a.completion;if("root"===a.tryLoc)return n("end");if(a.tryLoc<=this.prev){var u=i.call(a,"catchLoc"),c=i.call(a,"finallyLoc");if(u&&c){
if(this.prev<a.catchLoc)return n(a.catchLoc,!0);if(this.prev<a.finallyLoc)return n(a.finallyLoc)}else if(u){if(this.prev<a.catchLoc)return n(a.catchLoc,!0)}else{
if(!c)throw Error("try statement without catch or finally");if(this.prev<a.finallyLoc)return n(a.finallyLoc)}}}},abrupt:function(t,e){
for(var r=this.tryEntries.length-1;r>=0;--r){var n=this.tryEntries[r];if(n.tryLoc<=this.prev&&i.call(n,"finallyLoc")&&this.prev<n.finallyLoc){var o=n;break}}
o&&("break"===t||"continue"===t)&&o.tryLoc<=e&&e<=o.finallyLoc&&(o=null);var a=o?o.completion:{};return a.type=t,a.arg=e,o?(this.method="next",
this.next=o.finallyLoc,m):this.complete(a)},complete:function(t,e){if("throw"===t.type)throw t.arg
;return"break"===t.type||"continue"===t.type?this.next=t.arg:"return"===t.type?(this.rval=this.arg=t.arg,this.method="return",
this.next="end"):"normal"===t.type&&e&&(this.next=e),m},finish:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.finallyLoc===t)return this.complete(r.completion,r.afterLoc),A(r),m}},catch:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.tryLoc===t){var n=r.completion;if("throw"===n.type){var o=n.arg;A(r)}return o}}throw Error("illegal catch attempt")},delegateYield:function(e,r,n){
return this.delegate={iterator:L(e),resultName:r,nextLoc:n},"next"===this.method&&(this.arg=t),m}},e}function i(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,a(n.key),n)}}function a(t){var e=function(t,e){
if("object"!=n(t)||!t)return t;var r=t[Symbol.toPrimitive];if(void 0!==r){var o=r.call(t,e||"default");if("object"!=n(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==n(e)?e:e+""}
Object.defineProperty(e,"__esModule",{value:!0}),e.ContentProperties=void 0;var s=r(95006),u=r(28271),c=r(18759),l=r(62941),f=function(){return t=function t(e){
!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.extendedConfluence=e,
this.contentPropertiesGetOperations=new Map([[u.ContentType.Page,this.getPagePropertyByKey.bind(this)],[u.ContentType.BlogPost,this.getBlogPostPropertyByKey.bind(this)]]),
this.contentPropertiesSetOperations=new Map([[u.ContentType.Page,this.setPageProperty.bind(this)],[u.ContentType.BlogPost,this.setBlogPostProperty.bind(this)]]),
this.contentPropertiesDeleteOperations=new Map([[u.ContentType.Page,this.deletePagePropertyByKey.bind(this)],[u.ContentType.BlogPost,this.deleteBlogPostPropertyByKey.bind(this)]]),
this.confluenceApi=e.confluenceApi},(e=[{key:"getContentPropertyByKey",value:function(t,e,r){return s.__awaiter(this,void 0,void 0,o().mark((function n(){var i,a
;return o().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:return n.next=2,this.extendedConfluence.content.resolveContentType(t,r);case 2:if(i=n.sent,
a=this.contentPropertiesGetOperations.get(i)){n.next=6;break}
throw new c.ExtendedConfluenceError("Unsupported opperation for content type [".concat(r,"]")).withClassName("ContentProperties").withMethodName("getContentPropertyByKey").withContext({
contentId:t,propertyKey:e}).withStatus(500,l.ErrorCode.UNSUPPORTED_OPERATION);case 6:return n.abrupt("return",a(t,e));case 7:case"end":return n.stop()}}),n,this)})))
}},{key:"getContentPropertyByKeyWithContentType",value:function(t,e,r){return s.__awaiter(this,void 0,void 0,o().mark((function n(){var i,a,s
;return o().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:return n.next=2,this.extendedConfluence.content.resolveContentType(t,r);case 2:if(i=n.sent,
a=this.contentPropertiesGetOperations.get(i)){n.next=6;break}
throw new c.ExtendedConfluenceError("Unsupported opperation for content type [".concat(r,"]")).withClassName("ContentProperties").withMethodName("getContentPropertyByKeyWithContentType").withContext({
contentId:t,propertyKey:e}).withStatus(500,l.ErrorCode.UNSUPPORTED_OPERATION);case 6:return n.prev=6,n.next=9,a(t,e);case 9:return s=n.sent,n.abrupt("return",{
contentProperty:s,contentType:i});case 13:if(n.prev=13,n.t0=n.catch(6),404!==n.t0.status){n.next=17;break}return n.abrupt("return",{contentProperty:void 0,
contentType:i});case 17:throw n.t0;case 18:case"end":return n.stop()}}),n,this,[[6,13]])})))}},{key:"setContentPropertyByKey",value:function(t,e,r,n){
return s.__awaiter(this,void 0,void 0,o().mark((function i(){var a,s;return o().wrap((function(o){for(;;)switch(o.prev=o.next){case 0:return o.next=2,
this.extendedConfluence.content.resolveContentType(t,n);case 2:if(a=o.sent,s=this.contentPropertiesSetOperations.get(a)){o.next=6;break}
throw new c.ExtendedConfluenceError("Unsupported opperation for content type [".concat(n,"]")).withClassName("ContentProperties").withMethodName("setContentPropertyByKey").withContext({
contentId:t,contentProperty:e}).withStatus(500,l.ErrorCode.UNSUPPORTED_OPERATION);case 6:return o.abrupt("return",s(t,e,r));case 7:case"end":return o.stop()}
}),i,this)})))}},{key:"deleteContentPropertyByKey",value:function(t,e,r){return s.__awaiter(this,void 0,void 0,o().mark((function n(){var i,a
;return o().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:return n.next=2,this.extendedConfluence.content.resolveContentType(t,r);case 2:if(i=n.sent,
a=this.contentPropertiesDeleteOperations.get(i)){n.next=6;break}
throw new c.ExtendedConfluenceError("Unsupported opperation for content type [".concat(r,"]")).withClassName("ContentProperties").withMethodName("getContentPropertyByKey").withContext({
contentId:t,propertyKey:e}).withStatus(500,l.ErrorCode.UNSUPPORTED_OPERATION);case 6:return n.next=8,a(t,e);case 8:case"end":return n.stop()}}),n,this)})))}},{
key:"getPagePropertyByKey",value:function(t,e){return s.__awaiter(this,void 0,void 0,o().mark((function r(){var n;return o().wrap((function(r){
for(;;)switch(r.prev=r.next){case 0:return r.next=2,this.confluenceApi.contentProperties.getContentPropertiesForPage(t,{key:e});case 2:if(n=r.sent,
!this.isMultiEntryResultEmpty(n)){r.next=5;break}
throw new c.ExtendedConfluenceError("Could not find property with key [".concat(e,"] on page with id [").concat(t,"]")).withClassName("ContentProperties").withMethodName("getPagePropertyByKey").withStatus(404)
;case 5:return r.abrupt("return",this.getLatestProperty(n.results));case 6:case"end":return r.stop()}}),r,this)})))}},{key:"setPageProperty",value:function(t,e,r){
return s.__awaiter(this,void 0,void 0,o().mark((function n(){var i;return o().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:return n.prev=0,n.next=3,
this.getPagePropertyByKey(t,e.key);case 3:return i=n.sent,e.value=r&&r.merge?Object.assign({},i.value,e.value):e.value,
n.abrupt("return",this.updatePageProperty(t,e,i));case 8:if(n.prev=8,n.t0=n.catch(0),404!==(null===n.t0||void 0===n.t0?void 0:n.t0.status)){n.next=12;break}
return n.abrupt("return",this.confluenceApi.contentProperties.createContentPropertyForPage(t,e));case 12:throw n.t0;case 13:case"end":return n.stop()}
}),n,this,[[0,8]])})))}},{key:"deletePagePropertyByKey",value:function(t,e){return s.__awaiter(this,void 0,void 0,o().mark((function r(){var n
;return o().wrap((function(r){for(;;)switch(r.prev=r.next){case 0:return r.next=2,this.getPagePropertyByKey(t,e);case 2:return n=r.sent,r.next=5,
this.confluenceApi.contentProperties.deleteContentPropertyForPageById(t,n.id);case 5:case"end":return r.stop()}}),r,this)})))}},{key:"getBlogPostPropertyByKey",
value:function(t,e){return s.__awaiter(this,void 0,void 0,o().mark((function r(){var n;return o().wrap((function(r){for(;;)switch(r.prev=r.next){case 0:
return r.next=2,this.confluenceApi.contentProperties.getContentPropertiesForBlogPost(t,{key:e});case 2:if(n=r.sent,!this.isMultiEntryResultEmpty(n)){r.next=5;break}
throw new c.ExtendedConfluenceError("Could not find property with key [".concat(e,"] on blogpost with id [").concat(t,"]")).withClassName("ContentProperties").withMethodName("getBlogPostPropertyByKey").withStatus(404)
;case 5:return r.abrupt("return",this.getLatestProperty(n.results));case 6:case"end":return r.stop()}}),r,this)})))}},{key:"setBlogPostProperty",
value:function(t,e,r){return s.__awaiter(this,void 0,void 0,o().mark((function n(){var i;return o().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:
return n.prev=0,n.next=3,this.getBlogPostPropertyByKey(t,e.key);case 3:return i=n.sent,e.value=r&&r.merge?Object.assign({},i.value,e.value):e.value,
n.abrupt("return",this.updateBlogPostProperty(t,e,i));case 8:if(n.prev=8,n.t0=n.catch(0),404!==(null===n.t0||void 0===n.t0?void 0:n.t0.status)){n.next=12;break}
return n.abrupt("return",this.confluenceApi.contentProperties.createContentPropertyForBlogPost(t,e));case 12:throw n.t0;case 13:case"end":return n.stop()}
}),n,this,[[0,8]])})))}},{key:"deleteBlogPostPropertyByKey",value:function(t,e){return s.__awaiter(this,void 0,void 0,o().mark((function r(){var n
;return o().wrap((function(r){for(;;)switch(r.prev=r.next){case 0:return r.next=2,this.getBlogPostPropertyByKey(t,e);case 2:return n=r.sent,r.next=5,
this.confluenceApi.contentProperties.deleteContentPropertyForBlogPostById(t,n.id);case 5:case"end":return r.stop()}}),r,this)})))}},{key:"updatePageProperty",
value:function(t,e,r){return s.__awaiter(this,void 0,void 0,o().mark((function n(){var i;return o().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:
return i=Object.assign(Object.assign({},e),{version:{number:r.version.number+1,message:""}}),
n.abrupt("return",this.confluenceApi.contentProperties.updateContentPropertyForPageById(t,r.id,i));case 2:case"end":return n.stop()}}),n,this)})))}},{
key:"updateBlogPostProperty",value:function(t,e,r){return s.__awaiter(this,void 0,void 0,o().mark((function n(){var i;return o().wrap((function(n){
for(;;)switch(n.prev=n.next){case 0:return i=Object.assign(Object.assign({},e),{version:{number:r.version.number+1,message:""}}),
n.abrupt("return",this.confluenceApi.contentProperties.updateContentPropertyForBlogPostById(t,r.id,i));case 2:case"end":return n.stop()}}),n,this)})))}},{
key:"getLatestProperty",value:function(t){return t.reduce((function(t,e){return t.version.createdAt>e.version.createdAt?t:e}))}},{key:"isMultiEntryResultEmpty",
value:function(t){return!(null==t?void 0:t.results)||t.results.length<=0}}])&&i(t.prototype,e),r&&i(t,r),Object.defineProperty(t,"prototype",{writable:!1}),t
;var t,e,r}();e.ContentProperties=f},8474:t=>{function e(t){return e="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t
}:function(t){return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},e(t)}
var r=1e3,n=60*r,o=60*n,i=24*o,a=7*i,s=365.25*i;function u(t,e,r,n){var o=e>=1.5*r;return Math.round(t/r)+" "+n+(o?"s":"")}t.exports=function(t,c){c=c||{};var l=e(t)
;if("string"===l&&t.length>0)return function(t){if((t=String(t)).length>100)return
;var e=/^(-?(?:\d+)?\.?\d+) *(milliseconds?|msecs?|ms|seconds?|secs?|s|minutes?|mins?|m|hours?|hrs?|h|days?|d|weeks?|w|years?|yrs?|y)?$/i.exec(t);if(!e)return
;var u=parseFloat(e[1]);switch((e[2]||"ms").toLowerCase()){case"years":case"year":case"yrs":case"yr":case"y":return u*s;case"weeks":case"week":case"w":return u*a
;case"days":case"day":case"d":return u*i;case"hours":case"hour":case"hrs":case"hr":case"h":return u*o;case"minutes":case"minute":case"mins":case"min":case"m":
return u*n;case"seconds":case"second":case"secs":case"sec":case"s":return u*r;case"milliseconds":case"millisecond":case"msecs":case"msec":case"ms":return u;default:
return}}(t);if("number"===l&&isFinite(t))return c.long?function(t){var e=Math.abs(t);if(e>=i)return u(t,e,i,"day");if(e>=o)return u(t,e,o,"hour")
;if(e>=n)return u(t,e,n,"minute");if(e>=r)return u(t,e,r,"second");return t+" ms"}(t):function(t){var e=Math.abs(t);if(e>=i)return Math.round(t/i)+"d"
;if(e>=o)return Math.round(t/o)+"h";if(e>=n)return Math.round(t/n)+"m";if(e>=r)return Math.round(t/r)+"s";return t+"ms"}(t)
;throw new Error("val is not a non-empty string or a valid number. val="+JSON.stringify(t))}},14773:(t,e)=>{"use strict";function r(t){
return r="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},r(t)}function n(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,o(n.key),n)}}function o(t){var e=function(t,e){
if("object"!=r(t)||!t)return t;var n=t[Symbol.toPrimitive];if(void 0!==n){var o=n.call(t,e||"default");if("object"!=r(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==r(e)?e:e+""}
Object.defineProperty(e,"__esModule",{value:!0}),e.Children=void 0;var i=function(){return t=function t(e){!function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.client=e},(e=[{key:"getChildPages",value:function(t,e){var r={
url:"/api/v2/pages/".concat(t,"/children"),type:"GET",queryParams:{cursor:null==e?void 0:e.cursor,limit:null==e?void 0:e.limit,sort:null==e?void 0:e.sort}}
;return this.client.sendRequest(r)}}])&&n(t.prototype,e),r&&n(t,r),Object.defineProperty(t,"prototype",{writable:!1}),t;var t,e,r}();e.Children=i},16140:(t,e,r)=>{
"use strict";Object.defineProperty(e,"__esModule",{value:!0});var n,o=function(){function t(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,n.key,n)}}return function(e,r,n){return r&&t(e.prototype,r),
n&&t(e,n),e}}(),i=r(76232),a=(n=i)&&n.__esModule?n:{default:n};var s=function(){function t(e){!function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.migrator=e||{}}return o(t,[{key:"_getMigrator",value:function(t,e){
return this.migrator[t]&&this.migrator[t][e]?this.migrator[t][e]:null}},{key:"_getLatestVersion",value:function(t){return t?Math.max(Object.keys(t).map((function(t){
return parseInt(t,10)}))):0}},{key:"_checkMigrator",value:function(t,e,r){for(var n=Object.keys(t),o=e+1;o<=r;o++){if(!n.includes(o+""))return!1;if(!t[o+""])return!1
}return!0}},{key:"migrate",value:function(t,e){var r=e.key,n=e.value.version,o=void 0===n?0:n,i=this._getMigrator(t,r);if(!i)return e;var s=this._getLatestVersion(i)
;if(s===o)return e;if(!this._checkMigrator(i,o,s))return console.error("Migrator inconsistency for property "+r+" from version "+o+" to version "+s),e
;for(var u=o+1;u<=s;u++)a.default.set(e,"value",i[u](e.value));return e}}]),t}();e.default=s,t.exports=e.default},16293:t=>{"use strict";t.exports=vendor},
18759:(t,e,r)=>{"use strict";function n(t){return n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},n(t)}function o(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,i(n.key),n)}}function i(t){var e=function(t,e){
if("object"!=n(t)||!t)return t;var r=t[Symbol.toPrimitive];if(void 0!==r){var o=r.call(t,e||"default");if("object"!=n(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==n(e)?e:e+""}
function a(t,e,r){return e=u(e),function(t,e){if(e&&("object"==n(e)||"function"==typeof e))return e
;if(void 0!==e)throw new TypeError("Derived constructors may only return object or undefined");return function(t){
if(void 0===t)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return t}(t)
}(t,s()?Reflect.construct(e,r||[],u(t).constructor):e.apply(t,r))}function s(){try{
var t=!Boolean.prototype.valueOf.call(Reflect.construct(Boolean,[],(function(){})))}catch(t){}return(s=function(){return!!t})()}function u(t){
return u=Object.setPrototypeOf?Object.getPrototypeOf.bind():function(t){return t.__proto__||Object.getPrototypeOf(t)},u(t)}function c(t,e){
return c=Object.setPrototypeOf?Object.setPrototypeOf.bind():function(t,e){return t.__proto__=e,t},c(t,e)}Object.defineProperty(e,"__esModule",{value:!0}),
e.ExtendedConfluenceError=void 0;var l=function(t){function e(t,r){var n;return function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,e),(n=a(this,e,[t,r])).name="ExtendedConfluenceError",n}return function(t,e){
if("function"!=typeof e&&null!==e)throw new TypeError("Super expression must either be null or a function");t.prototype=Object.create(e&&e.prototype,{constructor:{
value:t,writable:!0,configurable:!0}}),Object.defineProperty(t,"prototype",{writable:!1}),e&&c(t,e)}(e,t),r=e,(n=[{key:"withClassName",value:function(t){
return this.className=t,this}},{key:"withMethodName",value:function(t){return this.methodName=t,this}},{key:"withContext",value:function(t){return this.context=t,
this}}])&&o(r.prototype,n),i&&o(r,i),Object.defineProperty(r,"prototype",{writable:!1}),r;var r,n,i}(r(62941).ConfluenceClientError);e.ExtendedConfluenceError=l},
20160:(t,e)=>{"use strict";function r(t){return r="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},r(t)}function n(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,o(n.key),n)}}function o(t){var e=function(t,e){
if("object"!=r(t)||!t)return t;var n=t[Symbol.toPrimitive];if(void 0!==n){var o=n.call(t,e||"default");if("object"!=r(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==r(e)?e:e+""}
Object.defineProperty(e,"__esModule",{value:!0}),e.SpacePermissions=void 0;var i=function(){return t=function t(e){!function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.client=e},(e=[{key:"getSpacePermissions",value:function(t,e){var r={
url:"/api/v2/spaces/".concat(t,"/permissions"),type:"GET",queryParams:{cursor:null==e?void 0:e.cursor,limit:null==e?void 0:e.limit}}
;return this.client.sendRequest(r)}}])&&n(t.prototype,e),r&&n(t,r),Object.defineProperty(t,"prototype",{writable:!1}),t;var t,e,r}();e.SpacePermissions=i},
20481:(t,e)=>{"use strict";Object.defineProperty(e,"__esModule",{value:!0});var r=Object.assign||function(t){for(var e=1;e<arguments.length;e++){var r=arguments[e]
;for(var n in r)Object.prototype.hasOwnProperty.call(r,n)&&(t[n]=r[n])}return t},n=function(){function t(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,n.key,n)}}return function(e,r,n){return r&&t(e.prototype,r),
n&&t(e,n),e}}();var o=function(){function t(e){if(function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),
"function"==typeof e)this.httpClient=e;else{if("function"!=typeof e.atlasRequest)throw new Error("Not valid http client provided");this.httpClient=e.atlasRequest}}
return n(t,[{key:"createContent",value:function(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{};return this.httpClient(Object.assign({type:"POST",
url:"/rest/api/content",headers:{"Content-Type":"application/json"},data:JSON.stringify(t)},e))}},{key:"getContent",value:function(){
var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{},e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=this._serializeGETParams(t)
;return this.httpClient(Object.assign({url:"/rest/api/content?"+r},e))}},{key:"updateContent",value:function(t,e){
var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{};return this.httpClient(Object.assign({type:"PUT",url:"/rest/api/content/"+t,headers:{
"Content-Type":"application/json"},data:JSON.stringify(e)},r))}},{key:"moveContent",value:function(t,e,r){
var n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{};return this.httpClient(Object.assign({type:"PUT",url:"/rest/api/content/"+t+"/move/"+e+"/"+r,
headers:{"Content-Type":"application/json"}},n))}},{key:"getContentById",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=this._serializeGETParams(e)
;return this.httpClient(Object.assign({url:"/rest/api/content/"+t+"?"+n},r))}},{key:"deleteContent",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{};return this.httpClient(Object.assign({type:"DELETE",url:"/rest/api/content/"+t,headers:{
"Content-Type":"application/json"}},e))}},{key:"checkContentRestrictions",value:function(t,e,r,n){var o=arguments.length>4&&void 0!==arguments[4]?arguments[4]:{},i={
subject:{type:e,identifier:r},operation:n};return this.httpClient(Object.assign({type:"POST",url:"/rest/api/content/"+t+"/permission/check",headers:{
"Content-Type":"application/json"},data:JSON.stringify(i)},o))}},{key:"getContentRestrictions",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=this._serializeGETParams(e)
;return this.httpClient(Object.assign({url:"/rest/api/content/"+t+"/restriction?"+n},r))}},{key:"addContentRestrictions",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{},o=this._serializeGETParams(r)
;return this.httpClient(Object.assign({type:"POST",headers:{Accept:"application/json","Content-Type":"application/json"},
url:"/rest/api/content/"+t+"/restriction?"+o,data:JSON.stringify(e)},n))}},{key:"updateContentRestrictions",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{},o=this._serializeGETParams(r)
;return this.httpClient(Object.assign({type:"PUT",headers:{Accept:"application/json","Content-Type":"application/json"},url:"/rest/api/content/"+t+"/restriction?"+o,
data:JSON.stringify(e)},n))}},{key:"removeContentRestrictions",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=this._serializeGETParams(e)
;return this.httpClient(Object.assign({type:"DELETE",headers:{Accept:"application/json","Content-Type":"application/json"},
url:"/rest/api/content/"+t+"/restriction?"+n},r))}},{key:"addUserToContentRestriction",value:function(t,e){
var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{},o=this._serializeGETParams(r)
;return this.httpClient(Object.assign({type:"PUT",headers:{Accept:"application/json"},url:"/rest/api/content/"+t+"/restriction/byOperation/"+e+"/user?"+o},n))}},{
key:"removeUserToContentRestriction",value:function(t,e){
var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{},o=this._serializeGETParams(r)
;return this.httpClient(Object.assign({type:"DELETE",headers:{Accept:"application/json"},url:"/rest/api/content/"+t+"/restriction/byOperation/"+e+"/user?"+o},n))}},{
key:"addGroupToContentRestriction",value:function(t,e,r){
var n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{},o=arguments.length>4&&void 0!==arguments[4]?arguments[4]:{},i=this._serializeGETParams(n)
;return this.httpClient(Object.assign({type:"PUT",headers:{Accept:"application/json"},
url:"/rest/api/content/"+t+"/restriction/byOperation/"+e+"/group/"+encodeURIComponent(r)+"?"+i},o))}},{key:"removeGroupToContentRestriction",value:function(t,e,r){
var n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{},o=arguments.length>4&&void 0!==arguments[4]?arguments[4]:{},i=this._serializeGETParams(n)
;return this.httpClient(Object.assign({type:"DELETE",headers:{Accept:"application/json"},
url:"/rest/api/content/"+t+"/restriction/byOperation/"+e+"/group/"+encodeURIComponent(r)+"?"+i},o))}},{key:"getHistory",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=this._serializeGETParams(e)
;return this.httpClient(Object.assign({url:"/rest/api/content/"+t+"/history?"+n},r))}},{key:"getContentLabels",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=this._serializeGETParams(e)
;return this.httpClient(Object.assign({url:"/rest/api/content/"+t+"/label?"+n},r))}},{key:"addContentLabels",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{},o=this._serializeGETParams(r)
;return this.httpClient(Object.assign({type:"POST",headers:{Accept:"application/json","Content-Type":"application/json"},url:"/rest/api/content/"+t+"/label?"+o,
data:JSON.stringify(e)},n))}},{key:"removeContentLabel",value:function(t,e){var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{}
;return this.httpClient(Object.assign({type:"DELETE",headers:{Accept:"application/json","Content-Type":"application/json"},url:"/rest/api/content/"+t+"/label/"+e
},r))}},{key:"cqlSearch",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=this._serializeGETParams(e)
;return this.httpClient(Object.assign({url:"/rest/api/search?"+n,headers:{Accept:"application/json"},data:{cql:t}},r))}},{key:"search",value:function(){
var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{},e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=this._serializeGETParams(t)
;return this.httpClient(Object.assign({url:"/rest/api/search?"+r},e))}},{key:"searchContent",value:function(){
var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{},e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=this._serializeGETParams(t)
;return this.httpClient(Object.assign({url:"/rest/api/content/search?"+r},e))}},{key:"searchUsers",value:function(){
var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{},e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=this._serializeGETParams(t)
;return this.httpClient(Object.assign({url:"/rest/api/search/user?"+r},e))}},{key:"getChildren",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=this._serializeGETParams(e)
;return this.httpClient(Object.assign({url:"/rest/api/content/"+t+"/child?"+n},r))}},{key:"getChildrenOfType",value:function(t,e){
var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{},o=this._serializeGETParams(r)
;return this.httpClient(Object.assign({url:"/rest/api/content/"+t+"/child/"+e+"?"+o},n))}},{key:"getNotificationsForChildContentCreated",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=this._serializeGETParams(e)
;return this.httpClient(Object.assign({url:"/rest/api/content/"+t+"/notification/child-created?"+n},r))}},{key:"getNotificationsForContentCreated",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=this._serializeGETParams(e)
;return this.httpClient(Object.assign({url:"/rest/api/content/"+t+"/notification/created?"+n},r))}},{key:"getContentHistory",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=this._serializeGETParams(e)
;return this.httpClient(Object.assign({url:"/rest/api/content/"+t+"/version?"+n},r))}},{key:"getContentVersion",value:function(t,e){
var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{},o=this._serializeGETParams(r)
;return this.httpClient(Object.assign({url:"/rest/api/content/"+t+"/version/"+e+"?"+o},n))}},{key:"getGroups",value:function(){
var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{},e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=this._serializeGETParams(t)
;return this.httpClient(Object.assign({url:"/rest/api/group?"+r},e))}},{key:"getGroup",value:function(t){
var e=this,r=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},n=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{}
;return this.getGroupById(t,r,n).catch((function(o){return 404===o.status?e.getGroupByName(t,r,n):o}))}},{key:"getGroupById",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=this._serializeGETParams(e)
;return this.httpClient(Object.assign({url:"/rest/api/group/by-id?id="+encodeURIComponent(t)+"&"+n},r))}},{key:"getGroupByName",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=this._serializeGETParams(e)
;return this.httpClient(Object.assign({url:"/rest/api/group/by-name?name="+encodeURIComponent(t)+"&"+n},r))}},{key:"getMembers",value:function(t){
var e=this,r=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},n=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{}
;return this.getMembersByGroupId(t,r,n).then((function(o){return Array.isArray(o.results)&&o.results.length>0?o:e.getMembersByGroupName(t,r,n)}))}},{
key:"getMembersByGroupName",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=this._serializeGETParams(e)
;return this.httpClient(Object.assign({url:"/rest/api/group/member?name="+encodeURIComponent(t)+"&"+n},r))}},{key:"getMembersByGroupId",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{}
;if(!this._isGroupIdValid(t))return Promise.resolve({results:[]});var n=this._serializeGETParams(e);return this.httpClient(Object.assign({
url:"/rest/api/group/"+t+"/membersByGroupId?"+n},r))}},{key:"_isGroupIdValid",value:function(t){return/^[a-z0-9-]*$/.test(t)}},{key:"getTasks",value:function(){
var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{},e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=this._serializeGETParams(t)
;return this.httpClient(Object.assign({url:"/rest/api/longtask?"+r},e))}},{key:"getTask",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=this._serializeGETParams(e)
;return this.httpClient(Object.assign({url:"/rest/api/longtask/"+t+"?"+n},r))}},{key:"getSpaces",value:function(){
var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{},e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=this._serializeGETParams(t)
;return this.httpClient(Object.assign({url:"/rest/api/space?"+r},e))}},{key:"createSpace",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{};return this.httpClient(Object.assign({type:"POST",url:"/rest/api/space",headers:{
"Content-Type":"application/json"},data:JSON.stringify(t)},e))}},{key:"updateSpace",value:function(t,e){
var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{};return this.httpClient(Object.assign({type:"PUT",url:"/rest/api/space/"+t,headers:{
"Content-Type":"application/json"},data:JSON.stringify(e)},r))}},{key:"deleteSpace",value:function(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{}
;return this.httpClient(Object.assign({type:"DELETE",url:"/rest/api/space/"+t,headers:{"Content-Type":"application/json"}},e))}},{key:"getSpace",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=this._serializeGETParams(e)
;return this.httpClient(Object.assign({url:"/rest/api/space/"+t+"?"+n},r))}},{key:"getSpaceContent",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=this._serializeGETParams(e)
;return this.httpClient(Object.assign({url:"/rest/api/space/"+t+"/content?"+n},r))}},{key:"getSpaceContentByType",value:function(t,e){
var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{},o=this._serializeGETParams(r)
;return this.httpClient(Object.assign({url:"/rest/api/space/"+t+"/content/"+e+"?"+o},n))}},{key:"getAllContentProperties",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{}
;return this._getAllProperties.bind(this,"content")(t,e,r)}},{key:"getContentProperty",value:function(t,e){
var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{}
;return this._getProperty.bind(this,"content")(t,e,r,n)}},{key:"createContentProperty",value:function(t,e){
var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{};return this._createProperty.bind(this,"content")(t,e,r)}},{key:"updateContentProperty",
value:function(t,e,r){var n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{};return this._updateProperty.bind(this,"content")(t,e,r,n)}},{
key:"deleteContentProperty",value:function(t,e){var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{}
;return this._deleteProperty.bind(this,"content")(t,e,r)}},{key:"getAllSpaceProperties",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{}
;return this._getAllProperties.bind(this,"space")(t,e,r)}},{key:"getSpaceProperty",value:function(t,e){
var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{}
;return this._getProperty.bind(this,"space")(t,e,r,n)}},{key:"createSpaceProperty",value:function(t,e){
var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{};return this._createProperty.bind(this,"space")(t,e,r)}},{key:"updateSpaceProperty",
value:function(t,e,r){var n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{};return this._updateProperty.bind(this,"space")(t,e,r,n)}},{
key:"deleteSpaceProperty",value:function(t,e){var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{};return this._deleteProperty.bind(this,"space")(t,e,r)}
},{key:"_getAllProperties",value:function(t,e){
var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{},o=this._serializeGETParams(r)
;return this.httpClient(Object.assign({url:"/rest/api/"+t+"/"+e+"/property?"+o},n))}},{key:"_getProperty",value:function(t,e,r){
var n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{},o=arguments.length>4&&void 0!==arguments[4]?arguments[4]:{},i=this._serializeGETParams(n)
;return this.httpClient(Object.assign({url:"/rest/api/"+t+"/"+e+"/property/"+r+"?"+i},o))}},{key:"_createProperty",value:function(t,e,r){
var n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{};return this.httpClient(Object.assign({type:"POST",url:"/rest/api/"+t+"/"+e+"/property",headers:{
"Content-Type":"application/json"},data:JSON.stringify(r)},n))}},{key:"_updateProperty",value:function(t,e,r,n){
var o=arguments.length>4&&void 0!==arguments[4]?arguments[4]:{};return this.httpClient(Object.assign({type:"PUT",url:"/rest/api/"+t+"/"+e+"/property/"+r,headers:{
"Content-Type":"application/json"},data:JSON.stringify(n)},o))}},{key:"_deleteProperty",value:function(t,e,r){
var n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{};return this.httpClient(Object.assign({type:"DELETE",url:"/rest/api/"+t+"/"+e+"/property/"+r},n))}},{
key:"getAddonProperties",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=this._serializeGETParams(e)
;return this.httpClient(Object.assign({url:"/rest/atlassian-connect/1/addons/"+t+"/properties?"+n},r))}},{key:"getAddonProperty",value:function(t,e){
var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{},o=this._serializeGETParams(r)
;return this.httpClient(Object.assign({url:"/rest/atlassian-connect/1/addons/"+t+"/properties/"+e+"?"+o},n)).catch((function(t){if(!t||404!==t["status-code"])throw t
}))}},{key:"setAddonProperty",value:function(t,e,r){var n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{};return this.httpClient(Object.assign({type:"PUT",
url:"/rest/atlassian-connect/1/addons/"+t+"/properties/"+e,headers:{"Content-Type":"application/json"},data:JSON.stringify(r)},n))}},{key:"deleteAddonProperty",
value:function(t,e){var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{};return this.httpClient(Object.assign({type:"DELETE",
url:"/rest/atlassian-connect/1/addons/"+t+"/properties/"+e,headers:{"Content-Type":"application/json"}},r))}},{key:"getAddonInfo",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=this._serializeGETParams(e)
;return this.httpClient(Object.assign({url:"/rest/atlassian-connect/1/addons/"+t+"?"+n},r))}},{key:"getUser",value:function(){
var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{},e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=this._serializeGETParams(t)
;return this.httpClient(Object.assign({url:"/rest/api/user?"+r},e))}},{key:"getUserAnonymous",value:function(){
var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{},e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=this._serializeGETParams(t)
;return this.httpClient(Object.assign({url:"/rest/api/user/anonymous?"+r},e))}},{key:"getUserCurrent",value:function(){
var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{},e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=this._serializeGETParams(t)
;return this.httpClient(Object.assign({url:"/rest/api/user/current?"+r},e))}},{key:"getUserGroups",value:function(){
var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{},e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=this._serializeGETParams(t)
;return this.httpClient(Object.assign({url:"/rest/api/user/memberof?"+r},e))}},{key:"userSearch",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=this._serializeGETParams(e)
;return this.httpClient(Object.assign({url:"/rest/prototype/1/search/user?"+n,headers:{Accept:"application/json"},data:{query:t,"max-results":10}},r))}},{
key:"groupSearch",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=this._serializeGETParams(e)
;return this.httpClient(Object.assign({url:"/rest/prototype/1/search/group?"+n,headers:{Accept:"application/json"},data:{query:t,"max-results":10}},r))}},{
key:"getEmail",value:function(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{};return this.httpClient(Object.assign({
url:"/rest/api/user/email?accountId="+t},e))}},{key:"getBulkEmails",value:function(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{}
;return this.httpClient(Object.assign({url:"/rest/api/user/email/bulk?"+t.map((function(t){return"accountId="+t})).join("&")},e))}},{key:"_serializeGETParams",
value:function(t){return t.expand&&Array.isArray(t.expand)&&(t.expand=t.expand.join(",")),Object.keys(t).filter((function(e){return t[e]&&0!==t[e].length
})).map((function(e){return e+"="+encodeURIComponent(t[e])})).join("&")}},{key:"createOrUpdateAttachment",value:function(t,e){
var r=this,n=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},o=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{},i=this._serializeGETParams(o)
;this.getReadableStreamFromAttachment(e).then((function(o){var a={file:{value:o,options:{filename:e.title},minorEdit:"true"}};return r.httpClient(Object.assign({
type:"PUT",headers:{"X-Atlassian-Token":"nocheck"},url:"/rest/api/content/"+t+"/child/attachment?"+i,formData:a},n))}))}},{key:"setSpacePermission",
value:function(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{};return this.httpClient(Object.assign({type:"POST",
url:"/rest/api/space/"+t+"/permission",headers:{Accept:"application/json","Content-Type":"application/json"},data:JSON.stringify(e)}))}},{
key:"deleteSpacePermission",value:function(t,e){return this.httpClient(Object.assign({type:"DELETE",url:"/rest/api/space/"+t+"/permission/"+e}))}},{
key:"getReadableStreamFromAttachment",value:function(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{};return this.httpClient(Object.assign({
type:"GET",url:t._links.download},r({},e,{encoding:null})))}},{key:"createOrUpdateAttachmentFromStream",value:function(t,e,r){
var n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{},o=arguments.length>4&&void 0!==arguments[4]?arguments[4]:{},i=this._serializeGETParams(o),a={file:{
value:e,options:{filename:r.title},minorEdit:"true"}};return this.httpClient(Object.assign({type:"PUT",headers:{"X-Atlassian-Token":"nocheck"},
url:"/rest/api/content/"+t+"/child/attachment?"+i,formData:a},n))}},{key:"copySinglePage",value:function(t,e){
var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{},o=this._serializeGETParams(r)
;return this.httpClient(Object.assign({type:"POST",headers:{Accept:"application/json","Content-Type":"application/json"},url:"/rest/api/content/"+t+"/copy?"+o,
data:JSON.stringify(e)},n))}}]),t}();e.default=o,t.exports=e.default},21367:(t,e,r)=>{"use strict";function n(t){
return n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},n(t)}function o(){o=function(){return e}
;var t,e={},r=Object.prototype,i=r.hasOwnProperty,a=Object.defineProperty||function(t,e,r){t[e]=r.value
},s="function"==typeof Symbol?Symbol:{},u=s.iterator||"@@iterator",c=s.asyncIterator||"@@asyncIterator",l=s.toStringTag||"@@toStringTag";function f(t,e,r){
return Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}),t[e]}try{f({},"")}catch(t){f=function(t,e,r){return t[e]=r}}
function h(t,e,r,n){var o=e&&e.prototype instanceof b?e:b,i=Object.create(o.prototype),s=new I(n||[]);return a(i,"_invoke",{value:j(t,r,s)}),i}function p(t,e,r){try{
return{type:"normal",arg:t.call(e,r)}}catch(t){return{type:"throw",arg:t}}}e.wrap=h;var d="suspendedStart",y="suspendedYield",v="executing",g="completed",m={}
;function b(){}function w(){}function _(){}var x={};f(x,u,(function(){return this}));var P=Object.getPrototypeOf,S=P&&P(P(L([])));S&&S!==r&&i.call(S,u)&&(x=S)
;var E=_.prototype=b.prototype=Object.create(x);function O(t){["next","throw","return"].forEach((function(e){f(t,e,(function(t){return this._invoke(e,t)}))}))}
function k(t,e){function r(o,a,s,u){var c=p(t[o],t,a);if("throw"!==c.type){var l=c.arg,f=l.value
;return f&&"object"==n(f)&&i.call(f,"__await")?e.resolve(f.__await).then((function(t){r("next",t,s,u)}),(function(t){r("throw",t,s,u)
})):e.resolve(f).then((function(t){l.value=t,s(l)}),(function(t){return r("throw",t,s,u)}))}u(c.arg)}var o;a(this,"_invoke",{value:function(t,n){function i(){
return new e((function(e,o){r(t,n,e,o)}))}return o=o?o.then(i,i):i()}})}function j(e,r,n){var o=d;return function(i,a){
if(o===v)throw Error("Generator is already running");if(o===g){if("throw"===i)throw a;return{value:t,done:!0}}for(n.method=i,n.arg=a;;){var s=n.delegate;if(s){
var u=C(s,n);if(u){if(u===m)continue;return u}}if("next"===n.method)n.sent=n._sent=n.arg;else if("throw"===n.method){if(o===d)throw o=g,n.arg
;n.dispatchException(n.arg)}else"return"===n.method&&n.abrupt("return",n.arg);o=v;var c=p(e,r,n);if("normal"===c.type){if(o=n.done?g:y,c.arg===m)continue;return{
value:c.arg,done:n.done}}"throw"===c.type&&(o=g,n.method="throw",n.arg=c.arg)}}}function C(e,r){var n=r.method,o=e.iterator[n];if(o===t)return r.delegate=null,
"throw"===n&&e.iterator.return&&(r.method="return",r.arg=t,C(e,r),"throw"===r.method)||"return"!==n&&(r.method="throw",
r.arg=new TypeError("The iterator does not provide a '"+n+"' method")),m;var i=p(o,e.iterator,r.arg);if("throw"===i.type)return r.method="throw",r.arg=i.arg,
r.delegate=null,m;var a=i.arg;return a?a.done?(r[e.resultName]=a.value,r.next=e.nextLoc,"return"!==r.method&&(r.method="next",r.arg=t),r.delegate=null,
m):a:(r.method="throw",r.arg=new TypeError("iterator result is not an object"),r.delegate=null,m)}function T(t){var e={tryLoc:t[0]};1 in t&&(e.catchLoc=t[1]),
2 in t&&(e.finallyLoc=t[2],e.afterLoc=t[3]),this.tryEntries.push(e)}function A(t){var e=t.completion||{};e.type="normal",delete e.arg,t.completion=e}function I(t){
this.tryEntries=[{tryLoc:"root"}],t.forEach(T,this),this.reset(!0)}function L(e){if(e||""===e){var r=e[u];if(r)return r.call(e);if("function"==typeof e.next)return e
;if(!isNaN(e.length)){var o=-1,a=function r(){for(;++o<e.length;)if(i.call(e,o))return r.value=e[o],r.done=!1,r;return r.value=t,r.done=!0,r};return a.next=a}}
throw new TypeError(n(e)+" is not iterable")}return w.prototype=_,a(E,"constructor",{value:_,configurable:!0}),a(_,"constructor",{value:w,configurable:!0}),
w.displayName=f(_,l,"GeneratorFunction"),e.isGeneratorFunction=function(t){var e="function"==typeof t&&t.constructor
;return!!e&&(e===w||"GeneratorFunction"===(e.displayName||e.name))},e.mark=function(t){return Object.setPrototypeOf?Object.setPrototypeOf(t,_):(t.__proto__=_,
f(t,l,"GeneratorFunction")),t.prototype=Object.create(E),t},e.awrap=function(t){return{__await:t}},O(k.prototype),f(k.prototype,c,(function(){return this})),
e.AsyncIterator=k,e.async=function(t,r,n,o,i){void 0===i&&(i=Promise);var a=new k(h(t,r,n,o),i);return e.isGeneratorFunction(r)?a:a.next().then((function(t){
return t.done?t.value:a.next()}))},O(E),f(E,l,"Generator"),f(E,u,(function(){return this})),f(E,"toString",(function(){return"[object Generator]"})),
e.keys=function(t){var e=Object(t),r=[];for(var n in e)r.push(n);return r.reverse(),function t(){for(;r.length;){var n=r.pop();if(n in e)return t.value=n,t.done=!1,t
}return t.done=!0,t}},e.values=L,I.prototype={constructor:I,reset:function(e){if(this.prev=0,this.next=0,this.sent=this._sent=t,this.done=!1,this.delegate=null,
this.method="next",this.arg=t,this.tryEntries.forEach(A),!e)for(var r in this)"t"===r.charAt(0)&&i.call(this,r)&&!isNaN(+r.slice(1))&&(this[r]=t)},stop:function(){
this.done=!0;var t=this.tryEntries[0].completion;if("throw"===t.type)throw t.arg;return this.rval},dispatchException:function(e){if(this.done)throw e;var r=this
;function n(n,o){return s.type="throw",s.arg=e,r.next=n,o&&(r.method="next",r.arg=t),!!o}for(var o=this.tryEntries.length-1;o>=0;--o){
var a=this.tryEntries[o],s=a.completion;if("root"===a.tryLoc)return n("end");if(a.tryLoc<=this.prev){var u=i.call(a,"catchLoc"),c=i.call(a,"finallyLoc");if(u&&c){
if(this.prev<a.catchLoc)return n(a.catchLoc,!0);if(this.prev<a.finallyLoc)return n(a.finallyLoc)}else if(u){if(this.prev<a.catchLoc)return n(a.catchLoc,!0)}else{
if(!c)throw Error("try statement without catch or finally");if(this.prev<a.finallyLoc)return n(a.finallyLoc)}}}},abrupt:function(t,e){
for(var r=this.tryEntries.length-1;r>=0;--r){var n=this.tryEntries[r];if(n.tryLoc<=this.prev&&i.call(n,"finallyLoc")&&this.prev<n.finallyLoc){var o=n;break}}
o&&("break"===t||"continue"===t)&&o.tryLoc<=e&&e<=o.finallyLoc&&(o=null);var a=o?o.completion:{};return a.type=t,a.arg=e,o?(this.method="next",
this.next=o.finallyLoc,m):this.complete(a)},complete:function(t,e){if("throw"===t.type)throw t.arg
;return"break"===t.type||"continue"===t.type?this.next=t.arg:"return"===t.type?(this.rval=this.arg=t.arg,this.method="return",
this.next="end"):"normal"===t.type&&e&&(this.next=e),m},finish:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.finallyLoc===t)return this.complete(r.completion,r.afterLoc),A(r),m}},catch:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.tryLoc===t){var n=r.completion;if("throw"===n.type){var o=n.arg;A(r)}return o}}throw Error("illegal catch attempt")},delegateYield:function(e,r,n){
return this.delegate={iterator:L(e),resultName:r,nextLoc:n},"next"===this.method&&(this.arg=t),m}},e}function i(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,a(n.key),n)}}function a(t){var e=function(t,e){
if("object"!=n(t)||!t)return t;var r=t[Symbol.toPrimitive];if(void 0!==r){var o=r.call(t,e||"default");if("object"!=n(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==n(e)?e:e+""}
Object.defineProperty(e,"__esModule",{value:!0}),e.SpaceProperties=void 0;var s=r(95006),u=r(18759),c=function(){return t=function t(e){!function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.extendedConfluence=e,this.confluenceApi=e.confluenceApi},e=[{
key:"getSpacePropertyByKey",value:function(t,e){var r,n;return s.__awaiter(this,void 0,void 0,o().mark((function i(){var a,s;return o().wrap((function(o){
for(;;)switch(o.prev=o.next){case 0:return o.prev=0,o.next=3,this.resolveSpaceId(t);case 3:return a=o.sent,o.next=6,
this.confluenceApi.spaceProperties.getSpacePropertiesInSpace(a,{key:e});case 6:return s=o.sent,
o.abrupt("return",null===(r=null==s?void 0:s.results)||void 0===r?void 0:r[0]);case 10:if(o.prev=10,o.t0=o.catch(0),!(o.t0 instanceof u.ExtendedConfluenceError)){
o.next=14;break}throw o.t0;case 14:
throw new u.ExtendedConfluenceError("Unexpected error on getting the space property with key [".concat(e,"]"),o.t0).withClassName("SpaceProperties").withMethodName("getSpacePropertyByKey").withContext({
space:t,resolvedSpaceId:a}).withStatus(null!==(n=o.t0.status)&&void 0!==n?n:500);case 15:case"end":return o.stop()}}),i,this,[[0,10]])})))}},{
key:"getSpacePropertiesBySpaceKey",value:function(t,e){return s.__awaiter(this,void 0,void 0,o().mark((function r(){var n;return o().wrap((function(r){
for(;;)switch(r.prev=r.next){case 0:return r.next=2,this.extendedConfluence.space.getSpaceByKey(t);case 2:if(n=r.sent){r.next=5;break}return r.abrupt("return",[])
;case 5:return r.abrupt("return",this.getAllSpaceProperties(n.id,e));case 6:case"end":return r.stop()}}),r,this)})))}},{key:"setSpaceProperty",value:function(t,e){
var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{};return s.__awaiter(this,void 0,void 0,o().mark((function n(){var i,a;return o().wrap((function(n){
for(;;)switch(n.prev=n.next){case 0:return n.next=2,this.resolveSpaceId(t);case 2:return i=n.sent,n.next=5,this.getSpacePropertyByKey({id:i},e.key);case 5:
if(a=n.sent){n.next=8;break}return n.abrupt("return",this.confluenceApi.spaceProperties.createSpacePropertyInSpace(i,e));case 8:
return e.value=r.merge?Object.assign({},a.value,e.value):e.value,n.abrupt("return",this.updateSpaceProperty(i,e,a));case 10:case"end":return n.stop()}}),n,this)})))}
},{key:"deleteSpacePropertyByKey",value:function(t,e){return s.__awaiter(this,void 0,void 0,o().mark((function r(){var n,i;return o().wrap((function(r){
for(;;)switch(r.prev=r.next){case 0:return r.next=2,this.resolveSpaceId(t);case 2:return n=r.sent,r.next=5,this.getSpacePropertyByKey(t,e);case 5:if(i=r.sent){
r.next=10;break}return r.abrupt("return");case 10:return r.abrupt("return",this.confluenceApi.spaceProperties.deleteSpacePropertyById(n,i.id));case 11:case"end":
return r.stop()}}),r,this)})))}},{key:"updateSpaceProperty",value:function(t,e,r){return s.__awaiter(this,void 0,void 0,o().mark((function n(){var i
;return o().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:return i=Object.assign(Object.assign({},e),{version:{number:r.version.number+1,message:""}}),
n.abrupt("return",this.confluenceApi.spaceProperties.updateSpacePropertyById(t,r.id,i));case 2:case"end":return n.stop()}}),n,this)})))}},{
key:"getAllSpaceProperties",value:function(t,e,r){return s.__awaiter(this,void 0,void 0,o().mark((function n(){var i,a,s,u;return o().wrap((function(n){
for(;;)switch(n.prev=n.next){case 0:return n.next=2,this.getSpaceProperties(t,e,r);case 2:if(i=n.sent,a=i.results,!(s=i._links).next){n.next=12;break}
return n.next=8,this.getAllSpaceProperties(t,e,s.next);case 8:return u=n.sent,n.abrupt("return",a.concat(u));case 12:return n.abrupt("return",a);case 13:case"end":
return n.stop()}}),n,this)})))}},{key:"getSpaceProperties",value:function(t,e,r){return s.__awaiter(this,void 0,void 0,o().mark((function n(){var i=this
;return o().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:return n.abrupt("return",this.extendedConfluence.sendPaginationRequest((function(){
return i.confluenceApi.spaceProperties.getSpacePropertiesInSpace(t,e)}),r));case 1:case"end":return n.stop()}}),n,this)})))}},{key:"getSpaceId",value:function(t){
return s.__awaiter(this,void 0,void 0,o().mark((function e(){var r;return o().wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,
this.extendedConfluence.space.getOneSpaceByKey(t);case 2:return r=e.sent,e.abrupt("return",r.id);case 4:case"end":return e.stop()}}),e,this)})))}},{
key:"resolveSpaceId",value:function(t){return s.__awaiter(this,void 0,void 0,o().mark((function e(){return o().wrap((function(e){for(;;)switch(e.prev=e.next){case 0:
if(!(null==t?void 0:t.id)){e.next=2;break}return e.abrupt("return",t.id);case 2:if(!(null==t?void 0:t.key)){e.next=4;break}
return e.abrupt("return",this.getSpaceId(t.key));case 4:
throw new u.ExtendedConfluenceError("Missing space properties: [id], [key]").withClassName("SpaceProperties").withMethodName("resolveSpaceId").withContext({space:t
}).withStatus(400);case 5:case"end":return e.stop()}}),e,this)})))}}],e&&i(t.prototype,e),r&&i(t,r),Object.defineProperty(t,"prototype",{writable:!1}),t;var t,e,r}()
;e.SpaceProperties=c},24289:(t,e)=>{"use strict";function r(t){return r="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t
}:function(t){return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},r(t)}function n(t,e){for(var r=0;r<e.length;r++){
var n=e[r];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,o(n.key),n)}}function o(t){var e=function(t,e){
if("object"!=r(t)||!t)return t;var n=t[Symbol.toPrimitive];if(void 0!==n){var o=n.call(t,e||"default");if("object"!=r(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==r(e)?e:e+""}
Object.defineProperty(e,"__esModule",{value:!0}),e.Operation=void 0;var i=function(){return t=function t(e){!function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.client=e},(e=[{key:"getPermittedOperationsForPage",value:function(t){
var e={url:"/api/v2/pages/".concat(t,"/operations"),type:"GET"};return this.client.sendRequest(e)}},{key:"getPermittedOperationsForBlogPost",value:function(t){
var e={url:"/api/v2/blogposts/".concat(t,"/operations"),type:"GET"};return this.client.sendRequest(e)}},{key:"getPermittedOperationsForSpace",value:function(t){
var e={url:"/api/v2/spaces/".concat(t,"/operations"),type:"GET"};return this.client.sendRequest(e)}}])&&n(t.prototype,e),r&&n(t,r),
Object.defineProperty(t,"prototype",{writable:!1}),t;var t,e,r}();e.Operation=i},24297:(t,e,r)=>{function n(t){
return n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},n(t)}var o=r(73769),i=t.exports;!function(){"use strict"
;var t,e,r,a=/[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,s={"\b":"\\b","\t":"\\t",
"\n":"\\n","\f":"\\f","\r":"\\r",'"':'\\"',"\\":"\\\\"};function u(t){return a.lastIndex=0,a.test(t)?'"'+t.replace(a,(function(t){var e=s[t]
;return"string"==typeof e?e:"\\u"+("0000"+t.charCodeAt(0).toString(16)).slice(-4)}))+'"':'"'+t+'"'}function c(i,a){
var s,l,f,h,p,d=t,y=a[i],v=null!=y&&(y instanceof o||o.isBigNumber(y));switch(y&&"object"===n(y)&&"function"==typeof y.toJSON&&(y=y.toJSON(i)),
"function"==typeof r&&(y=r.call(a,i,y)),n(y)){case"string":return v?y:u(y);case"number":return isFinite(y)?String(y):"null";case"boolean":case"null":case"bigint":
return String(y);case"object":if(!y)return"null";if(t+=e,p=[],"[object Array]"===Object.prototype.toString.apply(y)){for(h=y.length,s=0;s<h;s+=1)p[s]=c(s,y)||"null"
;return f=0===p.length?"[]":t?"[\n"+t+p.join(",\n"+t)+"\n"+d+"]":"["+p.join(",")+"]",t=d,f}if(r&&"object"===n(r))for(h=r.length,
s=0;s<h;s+=1)"string"==typeof r[s]&&(f=c(l=r[s],y))&&p.push(u(l)+(t?": ":":")+f);else Object.keys(y).forEach((function(e){var r=c(e,y);r&&p.push(u(e)+(t?": ":":")+r)
}));return f=0===p.length?"{}":t?"{\n"+t+p.join(",\n"+t)+"\n"+d+"}":"{"+p.join(",")+"}",t=d,f}}"function"!=typeof i.stringify&&(i.stringify=function(o,i,a){var s
;if(t="",e="","number"==typeof a)for(s=0;s<a;s+=1)e+=" ";else"string"==typeof a&&(e=a);if(r=i,
i&&"function"!=typeof i&&("object"!==n(i)||"number"!=typeof i.length))throw new Error("JSON.stringify");return c("",{"":o})})}()},24929:(t,e)=>{"use strict"
;Object.defineProperty(e,"__esModule",{value:!0}),e.ConfluencePrimaryBodyRepresentation=void 0,function(t){t.Storage="storage",t.AtlasDocFormat="atlas_doc_format",
t.View="view",t.Wiki="wiki",t.Raw="raw"}(e.ConfluencePrimaryBodyRepresentation||(e.ConfluencePrimaryBodyRepresentation={}))},25363:(t,e,r)=>{"use strict"
;function n(t){return n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},n(t)}function o(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,i(n.key),n)}}function i(t){var e=function(t,e){
if("object"!=n(t)||!t)return t;var r=t[Symbol.toPrimitive];if(void 0!==r){var o=r.call(t,e||"default");if("object"!=n(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==n(e)?e:e+""}
Object.defineProperty(e,"__esModule",{value:!0}),e.Confluence=void 0;var a=r(60667),s=r(52400),u=function(){return t=function t(e,r){if(function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.httpClient=e,this.requestOptions=r,this.confluenceApi={
attachment:new s.Attachment(this),blogPost:new s.BlogPost(this),children:new s.Children(this),content:new s.Content(this),
contentProperties:new s.ContentProperties(this),customContent:new s.CustomContent(this),operation:new s.Operation(this),page:new s.Page(this),
space:new s.Space(this),spacePermissions:new s.SpacePermissions(this),spaceProperties:new s.SpaceProperties(this),version:new s.Version(this),label:new s.Label(this)
},"function"==typeof e)this.httpClient=e;else{if("function"!=typeof e.atlasRequest)throw new Error("Not valid http client provided");this.httpClient=e.atlasRequest}
},(e=[{key:"sendRequest",value:function(t){
var e,r,n,o=null!==(r=null===(e=this.requestOptions)||void 0===e?void 0:e.userAgent)&&void 0!==r?r:"Comala Cloud Client",i=Object.assign(Object.assign({},t),{
url:this.getUrl(t),data:JSON.stringify(t.requestBody),headers:{"User-Agent":o}});return i.data&&(i.headers=null!==(n=i.headers)&&void 0!==n?n:{},
i.headers["Content-Type"]="application/json"),this.httpClient(Object.assign(i,this.requestOptions))}},{key:"sendPaginationRequest",value:function(t,e){if(e){
var r=this.sanitizeUrl(e);return this.httpClient(Object.assign({url:r},this.requestOptions))}return t()}},{key:"getUrl",value:function(t){var e=(0,
a.parameterSerializer)(t.queryParams);return e?"".concat(t.url,"?").concat(e):t.url}},{key:"sanitizeUrl",value:function(t){var e=/\/wiki\/(.*)/g.exec(t)
;return e?e[1]:t}}])&&o(t.prototype,e),r&&o(t,r),Object.defineProperty(t,"prototype",{writable:!1}),t;var t,e,r}();e.Confluence=u},25916:(t,e,r)=>{"use strict"
;function n(){n=function(){return e};var t,e={},r=Object.prototype,o=r.hasOwnProperty,a=Object.defineProperty||function(t,e,r){t[e]=r.value
},s="function"==typeof Symbol?Symbol:{},u=s.iterator||"@@iterator",c=s.asyncIterator||"@@asyncIterator",l=s.toStringTag||"@@toStringTag";function f(t,e,r){
return Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}),t[e]}try{f({},"")}catch(t){f=function(t,e,r){return t[e]=r}}
function h(t,e,r,n){var o=e&&e.prototype instanceof b?e:b,i=Object.create(o.prototype),s=new I(n||[]);return a(i,"_invoke",{value:j(t,r,s)}),i}function p(t,e,r){try{
return{type:"normal",arg:t.call(e,r)}}catch(t){return{type:"throw",arg:t}}}e.wrap=h;var d="suspendedStart",y="suspendedYield",v="executing",g="completed",m={}
;function b(){}function w(){}function _(){}var x={};f(x,u,(function(){return this}));var P=Object.getPrototypeOf,S=P&&P(P(L([])));S&&S!==r&&o.call(S,u)&&(x=S)
;var E=_.prototype=b.prototype=Object.create(x);function O(t){["next","throw","return"].forEach((function(e){f(t,e,(function(t){return this._invoke(e,t)}))}))}
function k(t,e){function r(n,a,s,u){var c=p(t[n],t,a);if("throw"!==c.type){var l=c.arg,f=l.value
;return f&&"object"==i(f)&&o.call(f,"__await")?e.resolve(f.__await).then((function(t){r("next",t,s,u)}),(function(t){r("throw",t,s,u)
})):e.resolve(f).then((function(t){l.value=t,s(l)}),(function(t){return r("throw",t,s,u)}))}u(c.arg)}var n;a(this,"_invoke",{value:function(t,o){function i(){
return new e((function(e,n){r(t,o,e,n)}))}return n=n?n.then(i,i):i()}})}function j(e,r,n){var o=d;return function(i,a){
if(o===v)throw Error("Generator is already running");if(o===g){if("throw"===i)throw a;return{value:t,done:!0}}for(n.method=i,n.arg=a;;){var s=n.delegate;if(s){
var u=C(s,n);if(u){if(u===m)continue;return u}}if("next"===n.method)n.sent=n._sent=n.arg;else if("throw"===n.method){if(o===d)throw o=g,n.arg
;n.dispatchException(n.arg)}else"return"===n.method&&n.abrupt("return",n.arg);o=v;var c=p(e,r,n);if("normal"===c.type){if(o=n.done?g:y,c.arg===m)continue;return{
value:c.arg,done:n.done}}"throw"===c.type&&(o=g,n.method="throw",n.arg=c.arg)}}}function C(e,r){var n=r.method,o=e.iterator[n];if(o===t)return r.delegate=null,
"throw"===n&&e.iterator.return&&(r.method="return",r.arg=t,C(e,r),"throw"===r.method)||"return"!==n&&(r.method="throw",
r.arg=new TypeError("The iterator does not provide a '"+n+"' method")),m;var i=p(o,e.iterator,r.arg);if("throw"===i.type)return r.method="throw",r.arg=i.arg,
r.delegate=null,m;var a=i.arg;return a?a.done?(r[e.resultName]=a.value,r.next=e.nextLoc,"return"!==r.method&&(r.method="next",r.arg=t),r.delegate=null,
m):a:(r.method="throw",r.arg=new TypeError("iterator result is not an object"),r.delegate=null,m)}function T(t){var e={tryLoc:t[0]};1 in t&&(e.catchLoc=t[1]),
2 in t&&(e.finallyLoc=t[2],e.afterLoc=t[3]),this.tryEntries.push(e)}function A(t){var e=t.completion||{};e.type="normal",delete e.arg,t.completion=e}function I(t){
this.tryEntries=[{tryLoc:"root"}],t.forEach(T,this),this.reset(!0)}function L(e){if(e||""===e){var r=e[u];if(r)return r.call(e);if("function"==typeof e.next)return e
;if(!isNaN(e.length)){var n=-1,a=function r(){for(;++n<e.length;)if(o.call(e,n))return r.value=e[n],r.done=!1,r;return r.value=t,r.done=!0,r};return a.next=a}}
throw new TypeError(i(e)+" is not iterable")}return w.prototype=_,a(E,"constructor",{value:_,configurable:!0}),a(_,"constructor",{value:w,configurable:!0}),
w.displayName=f(_,l,"GeneratorFunction"),e.isGeneratorFunction=function(t){var e="function"==typeof t&&t.constructor
;return!!e&&(e===w||"GeneratorFunction"===(e.displayName||e.name))},e.mark=function(t){return Object.setPrototypeOf?Object.setPrototypeOf(t,_):(t.__proto__=_,
f(t,l,"GeneratorFunction")),t.prototype=Object.create(E),t},e.awrap=function(t){return{__await:t}},O(k.prototype),f(k.prototype,c,(function(){return this})),
e.AsyncIterator=k,e.async=function(t,r,n,o,i){void 0===i&&(i=Promise);var a=new k(h(t,r,n,o),i);return e.isGeneratorFunction(r)?a:a.next().then((function(t){
return t.done?t.value:a.next()}))},O(E),f(E,l,"Generator"),f(E,u,(function(){return this})),f(E,"toString",(function(){return"[object Generator]"})),
e.keys=function(t){var e=Object(t),r=[];for(var n in e)r.push(n);return r.reverse(),function t(){for(;r.length;){var n=r.pop();if(n in e)return t.value=n,t.done=!1,t
}return t.done=!0,t}},e.values=L,I.prototype={constructor:I,reset:function(e){if(this.prev=0,this.next=0,this.sent=this._sent=t,this.done=!1,this.delegate=null,
this.method="next",this.arg=t,this.tryEntries.forEach(A),!e)for(var r in this)"t"===r.charAt(0)&&o.call(this,r)&&!isNaN(+r.slice(1))&&(this[r]=t)},stop:function(){
this.done=!0;var t=this.tryEntries[0].completion;if("throw"===t.type)throw t.arg;return this.rval},dispatchException:function(e){if(this.done)throw e;var r=this
;function n(n,o){return s.type="throw",s.arg=e,r.next=n,o&&(r.method="next",r.arg=t),!!o}for(var i=this.tryEntries.length-1;i>=0;--i){
var a=this.tryEntries[i],s=a.completion;if("root"===a.tryLoc)return n("end");if(a.tryLoc<=this.prev){var u=o.call(a,"catchLoc"),c=o.call(a,"finallyLoc");if(u&&c){
if(this.prev<a.catchLoc)return n(a.catchLoc,!0);if(this.prev<a.finallyLoc)return n(a.finallyLoc)}else if(u){if(this.prev<a.catchLoc)return n(a.catchLoc,!0)}else{
if(!c)throw Error("try statement without catch or finally");if(this.prev<a.finallyLoc)return n(a.finallyLoc)}}}},abrupt:function(t,e){
for(var r=this.tryEntries.length-1;r>=0;--r){var n=this.tryEntries[r];if(n.tryLoc<=this.prev&&o.call(n,"finallyLoc")&&this.prev<n.finallyLoc){var i=n;break}}
i&&("break"===t||"continue"===t)&&i.tryLoc<=e&&e<=i.finallyLoc&&(i=null);var a=i?i.completion:{};return a.type=t,a.arg=e,i?(this.method="next",
this.next=i.finallyLoc,m):this.complete(a)},complete:function(t,e){if("throw"===t.type)throw t.arg
;return"break"===t.type||"continue"===t.type?this.next=t.arg:"return"===t.type?(this.rval=this.arg=t.arg,this.method="return",
this.next="end"):"normal"===t.type&&e&&(this.next=e),m},finish:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.finallyLoc===t)return this.complete(r.completion,r.afterLoc),A(r),m}},catch:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.tryLoc===t){var n=r.completion;if("throw"===n.type){var o=n.arg;A(r)}return o}}throw Error("illegal catch attempt")},delegateYield:function(e,r,n){
return this.delegate={iterator:L(e),resultName:r,nextLoc:n},"next"===this.method&&(this.arg=t),m}},e}function o(t,e,r,n,o,i,a){try{var s=t[i](a),u=s.value}catch(t){
return void r(t)}s.done?e(u):Promise.resolve(u).then(n,o)}function i(t){return i="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){
return typeof t}:function(t){return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},i(t)}
Object.defineProperty(e,"__esModule",{value:!0});var a=function(){function t(t,e){for(var r=0;r<e.length;r++){var n=e[r];n.enumerable=n.enumerable||!1,
n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,n.key,n)}}return function(e,r,n){return r&&t(e.prototype,r),n&&t(e,n),e}
}(),s=function t(e,r,n){null===e&&(e=Function.prototype);var o=Object.getOwnPropertyDescriptor(e,r);if(void 0===o){var i=Object.getPrototypeOf(e)
;return null===i?void 0:t(i,r,n)}if("value"in o)return o.value;var a=o.get;return void 0!==a?a.call(n):void 0},u=l(r(93501)),c=l(r(20481));function l(t){
return t&&t.__esModule?t:{default:t}}var f=function(t){function e(t){return function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,e),function(t,e){
if(!t)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return!e||"object"!==i(e)&&"function"!=typeof e?t:e
}(this,(e.__proto__||Object.getPrototypeOf(e)).call(this,t))}var r,c;return function(t,e){
if("function"!=typeof e&&null!==e)throw new TypeError("Super expression must either be null or a function, not "+i(e));t.prototype=Object.create(e&&e.prototype,{
constructor:{value:t,enumerable:!1,writable:!0,configurable:!0}}),e&&(Object.setPrototypeOf?Object.setPrototypeOf(t,e):t.__proto__=e)}(e,t),a(e,[{key:"setContent",
value:function(t,e){var r=this,n=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},o=(0,u.default)(n,"retrials",1);return this.getContentById(t,{
expand:["version"]},n).then((function(i){if(i){var a=Object.assign({type:i.type,title:i.title,version:{number:i.version.number+1}},e)
;return r.updateContent(t,a,n).catch((function(i){if(409===i.status&&o>0)return console.warn("Retrying setContent (409 received), "+o+" tries left"),
r.setContent(t,e,Object.assign({},n,{retrials:o-1}));throw i}))}return r.createContent(e,n)}))}},{key:"setFirstChildOfType",value:function(t,e,r){
var n=this,o=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{},i=(0,u.default)(o,"retrials",1)
;if(Object.prototype.hasOwnProperty.call(r,"version"))return this.updateContent(t,r,o).catch((function(a){if(409===a.status){
console.warn("Retrying setFirstChildOfType [has version] (409 received), "+i+" tries left");var s=Object.assign({},r);return delete s.version,
n.setFirstChildOfType(t,e,s,Object.assign({},o,{retrials:i-1}))}throw a}));var a=r.container.id;return this.getChildrenOfType(a,e,{expand:["version"]
}).then((function(a){var s=a&&a.results&&a.results[0];if(s){var u=Object.assign({type:s.type,title:s.title,version:{number:s.version.number+1},container:{
type:"page",id:t}},r);return n.updateContent(s.id,u,o).catch((function(a){
if(409===a.status&&i>0)return console.warn("Retrying setFirstChildOfType [has no version] (409 received), "+i+" tries left"),
n.setFirstChildOfType(t,e,r,Object.assign({},o,{retrials:i-1}));throw a}))}return n.createContent(r,o)}))}},{key:"setContentProperty",value:function(t,e,r){
var n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{};return this._setProperty.bind(this,"content")(t,e,r,n)}},{key:"mergeContentProperty",
value:function(t,e,r){var n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{};return n.merge=!0,this._setProperty.bind(this,"content")(t,e,r,n)}},{
key:"setSpaceProperty",value:function(t,e,r){var n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{};return this._setProperty.bind(this,"space")(t,e,r,n)}},{
key:"mergeSpaceProperty",value:function(t,e,r){var n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{};return n.merge=!0,
this._setProperty.bind(this,"space")(t,e,r,n)}},{key:"_getProperty",value:function(t,r,n){
var o=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{},i=arguments.length>4&&void 0!==arguments[4]?arguments[4]:{}
;return s(e.prototype.__proto__||Object.getPrototypeOf(e.prototype),"_getProperty",this).call(this,t,r,n,o,i).catch((function(t){if(!t||404!==t.status)throw t}))}},{
key:"_setProperty",value:function(t,e,r,n){var o=this,i=arguments.length>4&&void 0!==arguments[4]?arguments[4]:{},a=(0,u.default)(i,"retrials",1)
;return this._getProperty(t,e,r,{},i).then((function(s){var u=i.merge?Object.assign({},s.value,n):n,c={key:r,version:{
number:s&&s.version&&s.version.number?s.version.number+1:1},value:u};return o.httpClient(Object.assign({type:s?"PUT":"POST",url:"/rest/api/"+t+"/"+e+"/property/"+r,
headers:{"Content-Type":"application/json"},data:JSON.stringify(c)},i)).catch((function(s){
if(409===s.status&&a>0)return console.warn("Retrying _setProperty (409 received), "+a+" tries left"),o._setProperty(t,e,r,n,Object.assign({},i,{retrials:a-1}))
;throw s}))}))}},{key:"deleteSpaceAndWait",value:function(t){var e=this,r=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{}
;return this.deleteSpace(t,r).then((function(t){var n=t.id;return new Promise((function(t,o){!function i(){e.getTask(n,{},r).then((function(e){
e.successful?t():e.percentageComplete<100&&setTimeout(i,200)})).catch((function(t){return o(t)}))}()}))}))}},{key:"getAllSpaces",value:(r=n().mark((function t(){
var e,r,o,i,a,s,u,c,l=arguments;return n().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:r=[],o=!0,i=(e=l.length>0&&void 0!==l[0]?l[0]:{}).limit||100,a=0
;case 5:if(!o){t.next=16;break}return t.next=8,this.getSpaces({limit:i,start:a},e);case 8:s=t.sent,u=s.results,c=s._links,r=r.concat(u),o=c&&c.next,a+=i,t.next=5
;break;case 16:return t.abrupt("return",r);case 17:case"end":return t.stop()}}),t,this)})),c=function(){var t=this,e=arguments;return new Promise((function(n,i){
var a=r.apply(t,e);function s(t){o(a,n,i,s,u,"next",t)}function u(t){o(a,n,i,s,u,"throw",t)}s(void 0)}))},function(){return c.apply(this,arguments)})}]),e
}(c.default);e.default=f,t.exports=e.default},27171:(t,e)=>{"use strict";Object.defineProperty(e,"__esModule",{value:!0})},28271:(t,e,r)=>{"use strict"
;Object.defineProperty(e,"__esModule",{value:!0});var n=r(95006);n.__exportStar(r(74954),e),n.__exportStar(r(47869),e),n.__exportStar(r(65994),e),
n.__exportStar(r(64185),e),n.__exportStar(r(24929),e),n.__exportStar(r(71762),e),n.__exportStar(r(74341),e),n.__exportStar(r(27171),e),n.__exportStar(r(37720),e),
n.__exportStar(r(43322),e),n.__exportStar(r(57615),e),n.__exportStar(r(1557),e),n.__exportStar(r(78777),e),n.__exportStar(r(39948),e),n.__exportStar(r(89889),e),
n.__exportStar(r(53886),e),n.__exportStar(r(60877),e),n.__exportStar(r(85572),e),n.__exportStar(r(67838),e),n.__exportStar(r(51839),e)},28663:(t,e)=>{"use strict"
;function r(t){return r="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},r(t)}function n(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,o(n.key),n)}}function o(t){var e=function(t,e){
if("object"!=r(t)||!t)return t;var n=t[Symbol.toPrimitive];if(void 0!==n){var o=n.call(t,e||"default");if("object"!=r(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==r(e)?e:e+""}
Object.defineProperty(e,"__esModule",{value:!0}),e.Attachment=void 0;var i=function(){return t=function t(e){!function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.client=e},(e=[{key:"getAttachmentById",value:function(t,e){var r={
url:"/api/v2/attachments/".concat(t),type:"GET",queryParams:{version:null==e?void 0:e.version}};return this.client.sendRequest(r)}},{key:"deleteAttachment",
value:function(t){var e={url:"/api/v2/attachments/".concat(t),type:"DELETE"};return this.client.sendRequest(e)}},{key:"getAttachmentsForPage",value:function(t,e){
var r={url:"/api/v2/pages/".concat(t,"/attachments"),type:"GET",queryParams:{sort:null==e?void 0:e.sort,cursor:null==e?void 0:e.cursor,
status:null==e?void 0:e.status,mediaType:null==e?void 0:e.mediaType,filename:null==e?void 0:e.filename,limit:null==e?void 0:e.limit}}
;return this.client.sendRequest(r)}}])&&n(t.prototype,e),r&&n(t,r),Object.defineProperty(t,"prototype",{writable:!1}),t;var t,e,r}();e.Attachment=i},34173:(t,e,r)=>{
"use strict";Object.defineProperty(e,"__esModule",{value:!0});var n=r(95006);n.__exportStar(r(25363),e),n.__exportStar(r(42674),e)},36508:(t,e,r)=>{"use strict"
;function n(t){return n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},n(t)}
var o="function"==typeof Symbol&&"symbol"===n(Symbol.iterator)?function(t){return n(t)}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":n(t)},i=r(79112),a=r(38474);t.exports={renameProps:function(t,e){
Object.keys(e).forEach((function(r){t[e[r]]=t[r],delete t[r]}))},methodMapping:{get:"get",post:"post",put:"put",delete:"del",head:"head",patch:"patch"},
defaultOptions:{type:"GET",contentType:"application/json",headers:{}},parseJson:function(t){var e=i.parse(t);return a(e)},getType:function(t){
return null===t?"null":t instanceof Array?"array":void 0===t?"undefined":o(t)}}},37720:(t,e)=>{"use strict";Object.defineProperty(e,"__esModule",{value:!0}),
e.OnlyArchivedAndCurrentContentStatus=e.ContentStatus=void 0,function(t){t.Current="current",t.Trashed="trashed",t.Historical="historical",t.Deleted="deleted",
t.Any="any",t.Draft="draft",t.Archived="archived"}(e.ContentStatus||(e.ContentStatus={})),function(t){t.Archived="archived",t.Current="current"
}(e.OnlyArchivedAndCurrentContentStatus||(e.OnlyArchivedAndCurrentContentStatus={}))},38474:(t,e,r)=>{function n(t){
return n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},n(t)}t=r.nmd(t)
;var o="__lodash_hash_undefined__",i=9007199254740991,a="[object Arguments]",s="[object Boolean]",u="[object Date]",c="[object Function]",l="[object GeneratorFunction]",f="[object Map]",h="[object Number]",p="[object Object]",d="[object Promise]",y="[object RegExp]",v="[object Set]",g="[object String]",m="[object Symbol]",b="[object WeakMap]",w="[object ArrayBuffer]",_="[object DataView]",x="[object Float32Array]",P="[object Float64Array]",S="[object Int8Array]",E="[object Int16Array]",O="[object Int32Array]",k="[object Uint8Array]",j="[object Uint8ClampedArray]",C="[object Uint16Array]",T="[object Uint32Array]",A=/\w*$/,I=/^\[object .+?Constructor\]$/,L=/^(?:0|[1-9]\d*)$/,N={}
;N[a]=N["[object Array]"]=N[w]=N[_]=N[s]=N[u]=N[x]=N[P]=N[S]=N[E]=N[O]=N[f]=N[h]=N[p]=N[y]=N[v]=N[g]=N[m]=N[k]=N[j]=N[C]=N[T]=!0,N["[object Error]"]=N[c]=N[b]=!1
;var R="object"==(void 0===r.g?"undefined":n(r.g))&&r.g&&r.g.Object===Object&&r.g,D="object"==("undefined"==typeof self?"undefined":n(self))&&self&&self.Object===Object&&self,B=R||D||Function("return this")(),F="object"==n(e)&&e&&!e.nodeType&&e,M=F&&"object"==n(t)&&t&&!t.nodeType&&t,G=M&&M.exports===F
;function V(t,e){return t.set(e[0],e[1]),t}function U(t,e){return t.add(e),t}function q(t,e,r,n){var o=-1,i=t?t.length:0;for(n&&i&&(r=t[++o]);++o<i;)r=e(r,t[o],o,t)
;return r}function Z(t){var e=!1;if(null!=t&&"function"!=typeof t.toString)try{e=!!(t+"")}catch(t){}return e}function K(t){var e=-1,r=Array(t.size)
;return t.forEach((function(t,n){r[++e]=[n,t]})),r}function z(t,e){return function(r){return t(e(r))}}function $(t){var e=-1,r=Array(t.size)
;return t.forEach((function(t){r[++e]=t})),r}
var H,Y=Array.prototype,J=Function.prototype,W=Object.prototype,Q=B["__core-js_shared__"],X=(H=/[^.]+$/.exec(Q&&Q.keys&&Q.keys.IE_PROTO||""))?"Symbol(src)_1."+H:"",tt=J.toString,et=W.hasOwnProperty,rt=W.toString,nt=RegExp("^"+tt.call(et).replace(/[\\^$.*+?()[\]{}|]/g,"\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g,"$1.*?")+"$"),ot=G?B.Buffer:void 0,it=B.Symbol,at=B.Uint8Array,st=z(Object.getPrototypeOf,Object),ut=Object.create,ct=W.propertyIsEnumerable,lt=Y.splice,ft=Object.getOwnPropertySymbols,ht=ot?ot.isBuffer:void 0,pt=z(Object.keys,Object),dt=Mt(B,"DataView"),yt=Mt(B,"Map"),vt=Mt(B,"Promise"),gt=Mt(B,"Set"),mt=Mt(B,"WeakMap"),bt=Mt(Object,"create"),wt=Zt(dt),_t=Zt(yt),xt=Zt(vt),Pt=Zt(gt),St=Zt(mt),Et=it?it.prototype:void 0,Ot=Et?Et.valueOf:void 0
;function kt(t){var e=-1,r=t?t.length:0;for(this.clear();++e<r;){var n=t[e];this.set(n[0],n[1])}}function jt(t){var e=-1,r=t?t.length:0;for(this.clear();++e<r;){
var n=t[e];this.set(n[0],n[1])}}function Ct(t){var e=-1,r=t?t.length:0;for(this.clear();++e<r;){var n=t[e];this.set(n[0],n[1])}}function Tt(t){
this.__data__=new jt(t)}function At(t,e){var r=zt(t)||function(t){return function(t){return function(t){return!!t&&"object"==n(t)}(t)&&$t(t)
}(t)&&et.call(t,"callee")&&(!ct.call(t,"callee")||rt.call(t)==a)}(t)?function(t,e){for(var r=-1,n=Array(t);++r<t;)n[r]=e(r);return n
}(t.length,String):[],o=r.length,i=!!o;for(var s in t)!e&&!et.call(t,s)||i&&("length"==s||Ut(s,o))||r.push(s);return r}function It(t,e,r){var n=t[e]
;et.call(t,e)&&Kt(n,r)&&(void 0!==r||e in t)||(t[e]=r)}function Lt(t,e){for(var r=t.length;r--;)if(Kt(t[r][0],e))return r;return-1}function Nt(t,e,r,n,o,i,d){var b
;if(n&&(b=i?n(t,o,i,d):n(t)),void 0!==b)return b;if(!Jt(t))return t;var I=zt(t);if(I){if(b=function(t){var e=t.length,r=t.constructor(e)
;e&&"string"==typeof t[0]&&et.call(t,"index")&&(r.index=t.index,r.input=t.input);return r}(t),!e)return function(t,e){var r=-1,n=t.length;e||(e=Array(n))
;for(;++r<n;)e[r]=t[r];return e}(t,b)}else{var L=Vt(t),R=L==c||L==l;if(Ht(t))return function(t,e){if(e)return t.slice();var r=new t.constructor(t.length)
;return t.copy(r),r}(t,e);if(L==p||L==a||R&&!i){if(Z(t))return i?t:{};if(b=function(t){return"function"!=typeof t.constructor||qt(t)?{}:(e=st(t),Jt(e)?ut(e):{})
;var e}(R?{}:t),!e)return function(t,e){return Bt(t,Gt(t),e)}(t,function(t,e){return t&&Bt(e,Wt(e),t)}(b,t))}else{if(!N[L])return i?t:{};b=function(t,e,r,n){
var o=t.constructor;switch(e){case w:return Dt(t);case s:case u:return new o(+t);case _:return function(t,e){var r=e?Dt(t.buffer):t.buffer
;return new t.constructor(r,t.byteOffset,t.byteLength)}(t,n);case x:case P:case S:case E:case O:case k:case j:case C:case T:return function(t,e){
var r=e?Dt(t.buffer):t.buffer;return new t.constructor(r,t.byteOffset,t.length)}(t,n);case f:return function(t,e,r){var n=e?r(K(t),!0):K(t)
;return q(n,V,new t.constructor)}(t,n,r);case h:case g:return new o(t);case y:return function(t){var e=new t.constructor(t.source,A.exec(t))
;return e.lastIndex=t.lastIndex,e}(t);case v:return function(t,e,r){var n=e?r($(t),!0):$(t);return q(n,U,new t.constructor)}(t,n,r);case m:return i=t,
Ot?Object(Ot.call(i)):{}}var i}(t,L,Nt,e)}}d||(d=new Tt);var D=d.get(t);if(D)return D;if(d.set(t,b),!I)var B=r?function(t){return function(t,e,r){var n=e(t)
;return zt(t)?n:function(t,e){for(var r=-1,n=e.length,o=t.length;++r<n;)t[o+r]=e[r];return t}(n,r(t))}(t,Wt,Gt)}(t):Wt(t);return function(t,e){
for(var r=-1,n=t?t.length:0;++r<n&&!1!==e(t[r],r,t););}(B||t,(function(o,i){B&&(o=t[i=o]),It(b,i,Nt(o,e,r,n,i,t,d))})),b}function Rt(t){return!(!Jt(t)||(e=t,
X&&X in e))&&(Yt(t)||Z(t)?nt:I).test(Zt(t));var e}function Dt(t){var e=new t.constructor(t.byteLength);return new at(e).set(new at(t)),e}function Bt(t,e,r,n){
r||(r={});for(var o=-1,i=e.length;++o<i;){var a=e[o],s=n?n(r[a],t[a],a,r,t):void 0;It(r,a,void 0===s?t[a]:s)}return r}function Ft(t,e){var r,o,i=t.__data__
;return("string"==(o=n(r=e))||"number"==o||"symbol"==o||"boolean"==o?"__proto__"!==r:null===r)?i["string"==typeof e?"string":"hash"]:i.map}function Mt(t,e){
var r=function(t,e){return null==t?void 0:t[e]}(t,e);return Rt(r)?r:void 0}kt.prototype.clear=function(){this.__data__=bt?bt(null):{}},
kt.prototype.delete=function(t){return this.has(t)&&delete this.__data__[t]},kt.prototype.get=function(t){var e=this.__data__;if(bt){var r=e[t];return r===o?void 0:r
}return et.call(e,t)?e[t]:void 0},kt.prototype.has=function(t){var e=this.__data__;return bt?void 0!==e[t]:et.call(e,t)},kt.prototype.set=function(t,e){
return this.__data__[t]=bt&&void 0===e?o:e,this},jt.prototype.clear=function(){this.__data__=[]},jt.prototype.delete=function(t){var e=this.__data__,r=Lt(e,t)
;return!(r<0)&&(r==e.length-1?e.pop():lt.call(e,r,1),!0)},jt.prototype.get=function(t){var e=this.__data__,r=Lt(e,t);return r<0?void 0:e[r][1]},
jt.prototype.has=function(t){return Lt(this.__data__,t)>-1},jt.prototype.set=function(t,e){var r=this.__data__,n=Lt(r,t);return n<0?r.push([t,e]):r[n][1]=e,this},
Ct.prototype.clear=function(){this.__data__={hash:new kt,map:new(yt||jt),string:new kt}},Ct.prototype.delete=function(t){return Ft(this,t).delete(t)},
Ct.prototype.get=function(t){return Ft(this,t).get(t)},Ct.prototype.has=function(t){return Ft(this,t).has(t)},Ct.prototype.set=function(t,e){
return Ft(this,t).set(t,e),this},Tt.prototype.clear=function(){this.__data__=new jt},Tt.prototype.delete=function(t){return this.__data__.delete(t)},
Tt.prototype.get=function(t){return this.__data__.get(t)},Tt.prototype.has=function(t){return this.__data__.has(t)},Tt.prototype.set=function(t,e){
var r=this.__data__;if(r instanceof jt){var n=r.__data__;if(!yt||n.length<199)return n.push([t,e]),this;r=this.__data__=new Ct(n)}return r.set(t,e),this}
;var Gt=ft?z(ft,Object):function(){return[]},Vt=function(t){return rt.call(t)};function Ut(t,e){
return!!(e=null==e?i:e)&&("number"==typeof t||L.test(t))&&t>-1&&t%1==0&&t<e}function qt(t){var e=t&&t.constructor;return t===("function"==typeof e&&e.prototype||W)}
function Zt(t){if(null!=t){try{return tt.call(t)}catch(t){}try{return t+""}catch(t){}}return""}function Kt(t,e){return t===e||t!=t&&e!=e}
(dt&&Vt(new dt(new ArrayBuffer(1)))!=_||yt&&Vt(new yt)!=f||vt&&Vt(vt.resolve())!=d||gt&&Vt(new gt)!=v||mt&&Vt(new mt)!=b)&&(Vt=function(t){
var e=rt.call(t),r=e==p?t.constructor:void 0,n=r?Zt(r):void 0;if(n)switch(n){case wt:return _;case _t:return f;case xt:return d;case Pt:return v;case St:return b}
return e});var zt=Array.isArray;function $t(t){return null!=t&&function(t){return"number"==typeof t&&t>-1&&t%1==0&&t<=i}(t.length)&&!Yt(t)}var Ht=ht||function(){
return!1};function Yt(t){var e=Jt(t)?rt.call(t):"";return e==c||e==l}function Jt(t){var e=n(t);return!!t&&("object"==e||"function"==e)}function Wt(t){
return $t(t)?At(t):function(t){if(!qt(t))return pt(t);var e=[];for(var r in Object(t))et.call(t,r)&&"constructor"!=r&&e.push(r);return e}(t)}t.exports=function(t){
return Nt(t,!0,!0)}},38611:(t,e)=>{"use strict";Object.defineProperty(e,"__esModule",{value:!0});var r=Object.assign||function(t){
for(var e=1;e<arguments.length;e++){var r=arguments[e];for(var n in r)Object.prototype.hasOwnProperty.call(r,n)&&(t[n]=r[n])}return t},n=function(){function t(t,e){
for(var r=0;r<e.length;r++){var n=e[r];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,n.key,n)}}
return function(e,r,n){return r&&t(e.prototype,r),n&&t(e,n),e}}();var o=function(){function t(e){if(function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),"function"==typeof e)this.httpClient=e;else{
if("function"!=typeof e.atlasRequest)throw new Error("Not valid http client provided");this.httpClient=e.atlasRequest}}return n(t,[{key:"getWebhooks",
value:function(){var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{};return this.httpClient(r({url:"/rest/atlassian-connect/1/migration/webhook"},t))}},{
key:"putWebhooks",value:function(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{};return this.httpClient(r({type:"PUT",
url:"/rest/atlassian-connect/1/migration/webhook",headers:{"Content-Type":"application/json"},data:JSON.stringify(t)},e))}},{key:"deleteWebhooks",value:function(){
var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{};return this.putWebhooks({endpoints:[]},t)}},{key:"getMappings",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},n=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},o=this._serializeGETParams(e)
;return this.httpClient(r({url:"/rest/atlassian-connect/1/migration/mapping/"+t+"/page?"+o,headers:{"Content-Type":"application/json"}},n))}},{
key:"getMigrationData",value:function(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{};return this.httpClient(r({
url:"/rest/atlassian-connect/1/migration/data/"+t,headers:{Accept:"*/*"}},e))}},{key:"getAllUploadedDataKeys",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{};return this.httpClient(r({url:"/rest/atlassian-connect/1/migration/data/"+t+"/all",headers:{
Accept:"*/*"}},e))}},{key:"getAvailableMigrations",value:function(){var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{};return this.httpClient(r({
url:"/rest/atlassian-connect/1/migration",headers:{Accept:"*/*"}},t))}},{key:"getActiveTransfers",value:function(){
var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{};return this.httpClient(r({url:"/rest/atlassian-connect/1/migration/transfer/recent",headers:{
Accept:"*/*"}},t))}},{key:"getContainersInPages",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},n=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},o=this._serializeGETParams(e)
;return this.httpClient(r({url:"/rest/atlassian-connect/1/migration/api/connect/v1/container/"+t+"/page?"+o,headers:{"Content-Type":"application/json"}},n))}},{
key:"updateMigrationStatus",value:function(t,e){var n=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{};return this.httpClient(r({type:"POST",
url:"/rest/atlassian-connect/1/migration/progress/"+t,headers:{"Content-Type":"application/json"},data:JSON.stringify(e)},n))}},{key:"_serializeGETParams",
value:function(t){return t.expand&&Array.isArray(t.expand)&&(t.expand=t.expand.join(",")),Object.keys(t).filter((function(e){return t[e]&&0!==t[e].length
})).map((function(e){return e+"="+encodeURIComponent(t[e])})).join("&")}}]),t}();e.default=o,t.exports=e.default},39948:(t,e)=>{"use strict"
;Object.defineProperty(e,"__esModule",{value:!0})},42674:(t,e,r)=>{"use strict";function n(t){
return n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},n(t)}function o(){o=function(){return e}
;var t,e={},r=Object.prototype,i=r.hasOwnProperty,a=Object.defineProperty||function(t,e,r){t[e]=r.value
},s="function"==typeof Symbol?Symbol:{},u=s.iterator||"@@iterator",c=s.asyncIterator||"@@asyncIterator",l=s.toStringTag||"@@toStringTag";function f(t,e,r){
return Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}),t[e]}try{f({},"")}catch(t){f=function(t,e,r){return t[e]=r}}
function h(t,e,r,n){var o=e&&e.prototype instanceof b?e:b,i=Object.create(o.prototype),s=new I(n||[]);return a(i,"_invoke",{value:j(t,r,s)}),i}function p(t,e,r){try{
return{type:"normal",arg:t.call(e,r)}}catch(t){return{type:"throw",arg:t}}}e.wrap=h;var d="suspendedStart",y="suspendedYield",v="executing",g="completed",m={}
;function b(){}function w(){}function _(){}var x={};f(x,u,(function(){return this}));var P=Object.getPrototypeOf,S=P&&P(P(L([])));S&&S!==r&&i.call(S,u)&&(x=S)
;var E=_.prototype=b.prototype=Object.create(x);function O(t){["next","throw","return"].forEach((function(e){f(t,e,(function(t){return this._invoke(e,t)}))}))}
function k(t,e){function r(o,a,s,u){var c=p(t[o],t,a);if("throw"!==c.type){var l=c.arg,f=l.value
;return f&&"object"==n(f)&&i.call(f,"__await")?e.resolve(f.__await).then((function(t){r("next",t,s,u)}),(function(t){r("throw",t,s,u)
})):e.resolve(f).then((function(t){l.value=t,s(l)}),(function(t){return r("throw",t,s,u)}))}u(c.arg)}var o;a(this,"_invoke",{value:function(t,n){function i(){
return new e((function(e,o){r(t,n,e,o)}))}return o=o?o.then(i,i):i()}})}function j(e,r,n){var o=d;return function(i,a){
if(o===v)throw Error("Generator is already running");if(o===g){if("throw"===i)throw a;return{value:t,done:!0}}for(n.method=i,n.arg=a;;){var s=n.delegate;if(s){
var u=C(s,n);if(u){if(u===m)continue;return u}}if("next"===n.method)n.sent=n._sent=n.arg;else if("throw"===n.method){if(o===d)throw o=g,n.arg
;n.dispatchException(n.arg)}else"return"===n.method&&n.abrupt("return",n.arg);o=v;var c=p(e,r,n);if("normal"===c.type){if(o=n.done?g:y,c.arg===m)continue;return{
value:c.arg,done:n.done}}"throw"===c.type&&(o=g,n.method="throw",n.arg=c.arg)}}}function C(e,r){var n=r.method,o=e.iterator[n];if(o===t)return r.delegate=null,
"throw"===n&&e.iterator.return&&(r.method="return",r.arg=t,C(e,r),"throw"===r.method)||"return"!==n&&(r.method="throw",
r.arg=new TypeError("The iterator does not provide a '"+n+"' method")),m;var i=p(o,e.iterator,r.arg);if("throw"===i.type)return r.method="throw",r.arg=i.arg,
r.delegate=null,m;var a=i.arg;return a?a.done?(r[e.resultName]=a.value,r.next=e.nextLoc,"return"!==r.method&&(r.method="next",r.arg=t),r.delegate=null,
m):a:(r.method="throw",r.arg=new TypeError("iterator result is not an object"),r.delegate=null,m)}function T(t){var e={tryLoc:t[0]};1 in t&&(e.catchLoc=t[1]),
2 in t&&(e.finallyLoc=t[2],e.afterLoc=t[3]),this.tryEntries.push(e)}function A(t){var e=t.completion||{};e.type="normal",delete e.arg,t.completion=e}function I(t){
this.tryEntries=[{tryLoc:"root"}],t.forEach(T,this),this.reset(!0)}function L(e){if(e||""===e){var r=e[u];if(r)return r.call(e);if("function"==typeof e.next)return e
;if(!isNaN(e.length)){var o=-1,a=function r(){for(;++o<e.length;)if(i.call(e,o))return r.value=e[o],r.done=!1,r;return r.value=t,r.done=!0,r};return a.next=a}}
throw new TypeError(n(e)+" is not iterable")}return w.prototype=_,a(E,"constructor",{value:_,configurable:!0}),a(_,"constructor",{value:w,configurable:!0}),
w.displayName=f(_,l,"GeneratorFunction"),e.isGeneratorFunction=function(t){var e="function"==typeof t&&t.constructor
;return!!e&&(e===w||"GeneratorFunction"===(e.displayName||e.name))},e.mark=function(t){return Object.setPrototypeOf?Object.setPrototypeOf(t,_):(t.__proto__=_,
f(t,l,"GeneratorFunction")),t.prototype=Object.create(E),t},e.awrap=function(t){return{__await:t}},O(k.prototype),f(k.prototype,c,(function(){return this})),
e.AsyncIterator=k,e.async=function(t,r,n,o,i){void 0===i&&(i=Promise);var a=new k(h(t,r,n,o),i);return e.isGeneratorFunction(r)?a:a.next().then((function(t){
return t.done?t.value:a.next()}))},O(E),f(E,l,"Generator"),f(E,u,(function(){return this})),f(E,"toString",(function(){return"[object Generator]"})),
e.keys=function(t){var e=Object(t),r=[];for(var n in e)r.push(n);return r.reverse(),function t(){for(;r.length;){var n=r.pop();if(n in e)return t.value=n,t.done=!1,t
}return t.done=!0,t}},e.values=L,I.prototype={constructor:I,reset:function(e){if(this.prev=0,this.next=0,this.sent=this._sent=t,this.done=!1,this.delegate=null,
this.method="next",this.arg=t,this.tryEntries.forEach(A),!e)for(var r in this)"t"===r.charAt(0)&&i.call(this,r)&&!isNaN(+r.slice(1))&&(this[r]=t)},stop:function(){
this.done=!0;var t=this.tryEntries[0].completion;if("throw"===t.type)throw t.arg;return this.rval},dispatchException:function(e){if(this.done)throw e;var r=this
;function n(n,o){return s.type="throw",s.arg=e,r.next=n,o&&(r.method="next",r.arg=t),!!o}for(var o=this.tryEntries.length-1;o>=0;--o){
var a=this.tryEntries[o],s=a.completion;if("root"===a.tryLoc)return n("end");if(a.tryLoc<=this.prev){var u=i.call(a,"catchLoc"),c=i.call(a,"finallyLoc");if(u&&c){
if(this.prev<a.catchLoc)return n(a.catchLoc,!0);if(this.prev<a.finallyLoc)return n(a.finallyLoc)}else if(u){if(this.prev<a.catchLoc)return n(a.catchLoc,!0)}else{
if(!c)throw Error("try statement without catch or finally");if(this.prev<a.finallyLoc)return n(a.finallyLoc)}}}},abrupt:function(t,e){
for(var r=this.tryEntries.length-1;r>=0;--r){var n=this.tryEntries[r];if(n.tryLoc<=this.prev&&i.call(n,"finallyLoc")&&this.prev<n.finallyLoc){var o=n;break}}
o&&("break"===t||"continue"===t)&&o.tryLoc<=e&&e<=o.finallyLoc&&(o=null);var a=o?o.completion:{};return a.type=t,a.arg=e,o?(this.method="next",
this.next=o.finallyLoc,m):this.complete(a)},complete:function(t,e){if("throw"===t.type)throw t.arg
;return"break"===t.type||"continue"===t.type?this.next=t.arg:"return"===t.type?(this.rval=this.arg=t.arg,this.method="return",
this.next="end"):"normal"===t.type&&e&&(this.next=e),m},finish:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.finallyLoc===t)return this.complete(r.completion,r.afterLoc),A(r),m}},catch:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.tryLoc===t){var n=r.completion;if("throw"===n.type){var o=n.arg;A(r)}return o}}throw Error("illegal catch attempt")},delegateYield:function(e,r,n){
return this.delegate={iterator:L(e),resultName:r,nextLoc:n},"next"===this.method&&(this.arg=t),m}},e}function i(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,a(n.key),n)}}function a(t){var e=function(t,e){
if("object"!=n(t)||!t)return t;var r=t[Symbol.toPrimitive];if(void 0!==r){var o=r.call(t,e||"default");if("object"!=n(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==n(e)?e:e+""}
function s(t,e,r){return e=c(e),function(t,e){if(e&&("object"==n(e)||"function"==typeof e))return e
;if(void 0!==e)throw new TypeError("Derived constructors may only return object or undefined");return function(t){
if(void 0===t)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return t}(t)
}(t,u()?Reflect.construct(e,r||[],c(t).constructor):e.apply(t,r))}function u(){try{
var t=!Boolean.prototype.valueOf.call(Reflect.construct(Boolean,[],(function(){})))}catch(t){}return(u=function(){return!!t})()}function c(t){
return c=Object.setPrototypeOf?Object.getPrototypeOf.bind():function(t){return t.__proto__||Object.getPrototypeOf(t)},c(t)}function l(t,e){
return l=Object.setPrototypeOf?Object.setPrototypeOf.bind():function(t,e){return t.__proto__=e,t},l(t,e)}Object.defineProperty(e,"__esModule",{value:!0}),
e.ExtendedConfluence=void 0;var f=r(95006),h=r(25363),p=r(60667),d=r(54884),y=function(t){function e(t,r){var n;return function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,e),(n=s(this,e,[t,r])).content=new d.Content(n),
n.contentProperties=new d.ContentProperties(n),n.customContent=new d.CustomContent(n),n.space=new d.Space(n),n.spacePermissions=new d.SpacePermissions(n),
n.spaceProperties=new d.SpaceProperties(n),n.version=new d.Version(n),n}return function(t,e){
if("function"!=typeof e&&null!==e)throw new TypeError("Super expression must either be null or a function");t.prototype=Object.create(e&&e.prototype,{constructor:{
value:t,writable:!0,configurable:!0}}),Object.defineProperty(t,"prototype",{writable:!1}),e&&l(t,e)}(e,t),r=e,n=[{key:"getSpaceByKey",value:function(t,e){
return this.space.getSpaceByKey(t,e)}},{key:"getSpaceById",value:function(t,e){return this.confluenceApi.space.getSpaceById(t,e)}},{key:"getSpacePropertyByKey",
value:function(t,e){return f.__awaiter(this,void 0,void 0,o().mark((function r(){var n;return o().wrap((function(r){for(;;)switch(r.prev=r.next){case 0:return n={
key:t},r.abrupt("return",this.spaceProperties.getSpacePropertyByKey(n,e));case 2:case"end":return r.stop()}}),r,this)})))}},{key:"setSpaceProperty",
value:function(t,e,r,n){return f.__awaiter(this,void 0,void 0,o().mark((function i(){var a;return o().wrap((function(o){for(;;)switch(o.prev=o.next){case 0:
return a={key:e,id:r},o.abrupt("return",this.spaceProperties.setSpaceProperty(a,t,n));case 2:case"end":return o.stop()}}),i,this)})))}},{key:"createSpaceProperty",
value:function(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:"",r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:""
;return f.__awaiter(this,void 0,void 0,o().mark((function n(){var i;return o().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:return i={key:r,id:e},
n.abrupt("return",this.spaceProperties.setSpaceProperty(i,t));case 2:case"end":return n.stop()}}),n,this)})))}},{key:"updateSpaceProperty",value:function(t,e){
var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:"";return f.__awaiter(this,void 0,void 0,o().mark((function n(){var i;return o().wrap((function(n){
for(;;)switch(n.prev=n.next){case 0:return i={key:e,id:r},n.abrupt("return",this.spaceProperties.setSpaceProperty(i,t));case 2:case"end":return n.stop()}}),n,this)
})))}},{key:"deleteSpaceProperty",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:"",r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:""
;return f.__awaiter(this,void 0,void 0,o().mark((function n(){var i;return o().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:return i={key:r,id:e},
n.abrupt("return",this.spaceProperties.deleteSpacePropertyByKey(i,t));case 2:case"end":return n.stop()}}),n,this)})))}},{key:"getContentById",value:function(t,e){
return f.__awaiter(this,void 0,void 0,o().mark((function r(){var n,i;return o().wrap((function(r){for(;;)switch(r.prev=r.next){case 0:return r.next=2,
this.content.resolveContentType(t,e);case 2:return n=r.sent,i=(0,p.parameterSerializer)({}),r.abrupt("return",this.httpClient(Object.assign({
url:"/api/v2/".concat(n,"s/").concat(t,"?").concat(i)})));case 5:case"end":return r.stop()}}),r,this)})))}},{key:"getContentVersions",value:function(t){
return this.version.getContentVersions(t)}},{key:"_getContentProperty",value:function(t,e,r){return f.__awaiter(this,void 0,void 0,o().mark((function n(){var i,a
;return o().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:return i={key:e},a=(0,p.parameterSerializer)(i),n.abrupt("return",this.httpClient(Object.assign({
url:"/api/v2/".concat(r,"s/").concat(t,"/properties?").concat(a)},this.requestOptions)));case 3:case"end":return n.stop()}}),n,this)})))}},{key:"_getLatestProperty",
value:function(t){if(!(t.length<=0))return t.reduce((function(t,e){return t.version.createdAt>e.version.createdAt?t:e}))}},{key:"getContentPropertyWithContentType",
value:function(t,e,r){return f.__awaiter(this,void 0,void 0,o().mark((function n(){var i,a,s,u;return o().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:
return n.prev=0,n.next=3,this.content.resolveContentType(t,r);case 3:return i=n.sent,n.next=6,this._getContentProperty(t,e,i);case 6:if(a=n.sent){n.next=9;break}
return n.abrupt("return",{contentType:i});case 9:return s=a.results,u=void 0===s?[]:s,n.abrupt("return",{contentProperty:this._getLatestProperty(u),contentType:i})
;case 13:throw n.prev=13,n.t0=n.catch(0),new Error("Confluence client error",{cause:n.t0});case 16:case"end":return n.stop()}}),n,this,[[0,13]])})))}},{
key:"getContentProperty",value:function(t,e,r){return f.__awaiter(this,void 0,void 0,o().mark((function n(){var i,a,s,u;return o().wrap((function(n){
for(;;)switch(n.prev=n.next){case 0:return n.prev=0,n.next=3,this.content.resolveContentType(t,r);case 3:return i=n.sent,n.next=6,this._getContentProperty(t,e,i)
;case 6:if(a=n.sent){n.next=9;break}return n.abrupt("return",void 0);case 9:return s=a.results,u=void 0===s?[]:s,n.abrupt("return",this._getLatestProperty(u))
;case 13:throw n.prev=13,n.t0=n.catch(0),new Error("Confluence client error",{cause:n.t0});case 16:case"end":return n.stop()}}),n,this,[[0,13]])})))}},{
key:"setContentProperty",value:function(t,e){var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=arguments.length>3?arguments[3]:void 0
;return f.__awaiter(this,void 0,void 0,o().mark((function i(){var a,s,u,c,l;return o().wrap((function(o){for(;;)switch(o.prev=o.next){case 0:return o.prev=0,
o.next=3,this.getContentPropertyWithContentType(t,e.key,n);case 3:if(a=o.sent,s=a.contentProperty,u=a.contentType,s){o.next=10;break}return o.next=8,
this.createContentProperty(t,u,e);case 8:return c=o.sent,o.abrupt("return",c);case 10:return e.value=r.merge?Object.assign({},s.value,e.value):e.value,o.next=13,
this.updateContentProperty(t,u,e);case 13:return l=o.sent,o.abrupt("return",l);case 17:throw o.prev=17,o.t0=o.catch(0),new Error("Confluence client error",{
cause:o.t0});case 20:case"end":return o.stop()}}),i,this,[[0,17]])})))}},{key:"createContentProperty",value:function(t,e,r){
return f.__awaiter(this,void 0,void 0,o().mark((function n(){return o().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:
return n.abrupt("return",this.httpClient(Object.assign({type:"POST",url:"/api/v2/".concat(e,"s/").concat(t,"/properties"),headers:{"Content-Type":"application/json"
},data:JSON.stringify(r)},this.requestOptions)));case 1:case"end":return n.stop()}}),n,this)})))}},{key:"updateContentProperty",value:function(t,e,r){
return f.__awaiter(this,void 0,void 0,o().mark((function n(){var i,a,s;return o().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:return n.next=2,
this._getContentPropertyDetails(t,r.key,e);case 2:return i=n.sent,a=i.id,s=i.version,r.version={number:s},n.abrupt("return",this.httpClient(Object.assign({
type:"PUT",url:"/api/v2/".concat(e,"s/").concat(t,"/properties/").concat(a),headers:{"Content-Type":"application/json"},data:JSON.stringify(r)
},this.requestOptions)));case 7:case"end":return n.stop()}}),n,this)})))}},{key:"deleteContentProperty",value:function(t,e,r){
return f.__awaiter(this,void 0,void 0,o().mark((function n(){var i,a,s;return o().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:return n.prev=0,n.next=3,
this.content.resolveContentType(t,r);case 3:return i=n.sent,n.next=6,this._getContentPropertyDetails(t,e,i);case 6:if(a=n.sent,s=a.id){n.next=10;break}
return n.abrupt("return");case 10:return n.abrupt("return",this.httpClient(Object.assign({type:"DELETE",
url:"/api/v2/".concat(i,"s/").concat(t,"/properties/").concat(s)})));case 13:throw n.prev=13,n.t0=n.catch(0),new Error("Confluence client error",{cause:n.t0})
;case 16:case"end":return n.stop()}}),n,this,[[0,13]])})))}},{key:"_getContentPropertyDetails",value:function(t,e,r){
return f.__awaiter(this,void 0,void 0,o().mark((function n(){var i,a,s;return o().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:return n.next=2,
this.getContentProperty(t,e,r);case 2:if(i=n.sent){n.next=5;break}return n.abrupt("return",{id:"",version:1});case 5:return a=i.id,s=i.version,n.abrupt("return",{
id:a,version:s.number+1});case 7:case"end":return n.stop()}}),n,this)})))}},{key:"getPageById",value:function(t,e){return this.confluenceApi.page.getPageById(t,e)}
},{key:"getBlogpostById",value:function(t,e){return this.confluenceApi.blogPost.getBlogPostById(t,e)}},{key:"createPageProperty",value:function(t,e){
return this.confluenceApi.contentProperties.createContentPropertyForPage(t,e)}},{key:"updatePageProperty",value:function(t,e){
return this.contentProperties.setPageProperty(t,e)}},{key:"deletePageProperty",value:function(t,e){return this.contentProperties.deletePagePropertyByKey(t,e)}},{
key:"createBlogpostProperty",value:function(t,e){return this.confluenceApi.contentProperties.createContentPropertyForBlogPost(t,e)}},{key:"updateBlogpostProperty",
value:function(t,e){return this.contentProperties.setBlogPostProperty(t,e)}},{key:"deleteBlogpostProperty",value:function(t,e){
return this.contentProperties.deleteBlogPostPropertyByKey(t,e)}}],n&&i(r.prototype,n),a&&i(r,a),Object.defineProperty(r,"prototype",{writable:!1}),r;var r,n,a
}(h.Confluence);e.ExtendedConfluence=y},43322:(t,e)=>{"use strict";Object.defineProperty(e,"__esModule",{value:!0}),
e.ContentTypeForCustomContents=e.ContentType=void 0,function(t){t.Attachment="attachment",t.BlogPost="blogpost",t.Custom="custom-content",t.Page="page",
t.FooterComment="footer-comment",t.InlineComment="inline-comment"}(e.ContentType||(e.ContentType={})),function(t){t.BlogPost="blogpost",t.Page="page",t.Space="space"
}(e.ContentTypeForCustomContents||(e.ContentTypeForCustomContents={}))},44053:(t,e,r)=>{"use strict";function n(t){
return n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},n(t)}function o(){o=function(){return e}
;var t,e={},r=Object.prototype,i=r.hasOwnProperty,a=Object.defineProperty||function(t,e,r){t[e]=r.value
},s="function"==typeof Symbol?Symbol:{},u=s.iterator||"@@iterator",c=s.asyncIterator||"@@asyncIterator",l=s.toStringTag||"@@toStringTag";function f(t,e,r){
return Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}),t[e]}try{f({},"")}catch(t){f=function(t,e,r){return t[e]=r}}
function h(t,e,r,n){var o=e&&e.prototype instanceof b?e:b,i=Object.create(o.prototype),s=new I(n||[]);return a(i,"_invoke",{value:j(t,r,s)}),i}function p(t,e,r){try{
return{type:"normal",arg:t.call(e,r)}}catch(t){return{type:"throw",arg:t}}}e.wrap=h;var d="suspendedStart",y="suspendedYield",v="executing",g="completed",m={}
;function b(){}function w(){}function _(){}var x={};f(x,u,(function(){return this}));var P=Object.getPrototypeOf,S=P&&P(P(L([])));S&&S!==r&&i.call(S,u)&&(x=S)
;var E=_.prototype=b.prototype=Object.create(x);function O(t){["next","throw","return"].forEach((function(e){f(t,e,(function(t){return this._invoke(e,t)}))}))}
function k(t,e){function r(o,a,s,u){var c=p(t[o],t,a);if("throw"!==c.type){var l=c.arg,f=l.value
;return f&&"object"==n(f)&&i.call(f,"__await")?e.resolve(f.__await).then((function(t){r("next",t,s,u)}),(function(t){r("throw",t,s,u)
})):e.resolve(f).then((function(t){l.value=t,s(l)}),(function(t){return r("throw",t,s,u)}))}u(c.arg)}var o;a(this,"_invoke",{value:function(t,n){function i(){
return new e((function(e,o){r(t,n,e,o)}))}return o=o?o.then(i,i):i()}})}function j(e,r,n){var o=d;return function(i,a){
if(o===v)throw Error("Generator is already running");if(o===g){if("throw"===i)throw a;return{value:t,done:!0}}for(n.method=i,n.arg=a;;){var s=n.delegate;if(s){
var u=C(s,n);if(u){if(u===m)continue;return u}}if("next"===n.method)n.sent=n._sent=n.arg;else if("throw"===n.method){if(o===d)throw o=g,n.arg
;n.dispatchException(n.arg)}else"return"===n.method&&n.abrupt("return",n.arg);o=v;var c=p(e,r,n);if("normal"===c.type){if(o=n.done?g:y,c.arg===m)continue;return{
value:c.arg,done:n.done}}"throw"===c.type&&(o=g,n.method="throw",n.arg=c.arg)}}}function C(e,r){var n=r.method,o=e.iterator[n];if(o===t)return r.delegate=null,
"throw"===n&&e.iterator.return&&(r.method="return",r.arg=t,C(e,r),"throw"===r.method)||"return"!==n&&(r.method="throw",
r.arg=new TypeError("The iterator does not provide a '"+n+"' method")),m;var i=p(o,e.iterator,r.arg);if("throw"===i.type)return r.method="throw",r.arg=i.arg,
r.delegate=null,m;var a=i.arg;return a?a.done?(r[e.resultName]=a.value,r.next=e.nextLoc,"return"!==r.method&&(r.method="next",r.arg=t),r.delegate=null,
m):a:(r.method="throw",r.arg=new TypeError("iterator result is not an object"),r.delegate=null,m)}function T(t){var e={tryLoc:t[0]};1 in t&&(e.catchLoc=t[1]),
2 in t&&(e.finallyLoc=t[2],e.afterLoc=t[3]),this.tryEntries.push(e)}function A(t){var e=t.completion||{};e.type="normal",delete e.arg,t.completion=e}function I(t){
this.tryEntries=[{tryLoc:"root"}],t.forEach(T,this),this.reset(!0)}function L(e){if(e||""===e){var r=e[u];if(r)return r.call(e);if("function"==typeof e.next)return e
;if(!isNaN(e.length)){var o=-1,a=function r(){for(;++o<e.length;)if(i.call(e,o))return r.value=e[o],r.done=!1,r;return r.value=t,r.done=!0,r};return a.next=a}}
throw new TypeError(n(e)+" is not iterable")}return w.prototype=_,a(E,"constructor",{value:_,configurable:!0}),a(_,"constructor",{value:w,configurable:!0}),
w.displayName=f(_,l,"GeneratorFunction"),e.isGeneratorFunction=function(t){var e="function"==typeof t&&t.constructor
;return!!e&&(e===w||"GeneratorFunction"===(e.displayName||e.name))},e.mark=function(t){return Object.setPrototypeOf?Object.setPrototypeOf(t,_):(t.__proto__=_,
f(t,l,"GeneratorFunction")),t.prototype=Object.create(E),t},e.awrap=function(t){return{__await:t}},O(k.prototype),f(k.prototype,c,(function(){return this})),
e.AsyncIterator=k,e.async=function(t,r,n,o,i){void 0===i&&(i=Promise);var a=new k(h(t,r,n,o),i);return e.isGeneratorFunction(r)?a:a.next().then((function(t){
return t.done?t.value:a.next()}))},O(E),f(E,l,"Generator"),f(E,u,(function(){return this})),f(E,"toString",(function(){return"[object Generator]"})),
e.keys=function(t){var e=Object(t),r=[];for(var n in e)r.push(n);return r.reverse(),function t(){for(;r.length;){var n=r.pop();if(n in e)return t.value=n,t.done=!1,t
}return t.done=!0,t}},e.values=L,I.prototype={constructor:I,reset:function(e){if(this.prev=0,this.next=0,this.sent=this._sent=t,this.done=!1,this.delegate=null,
this.method="next",this.arg=t,this.tryEntries.forEach(A),!e)for(var r in this)"t"===r.charAt(0)&&i.call(this,r)&&!isNaN(+r.slice(1))&&(this[r]=t)},stop:function(){
this.done=!0;var t=this.tryEntries[0].completion;if("throw"===t.type)throw t.arg;return this.rval},dispatchException:function(e){if(this.done)throw e;var r=this
;function n(n,o){return s.type="throw",s.arg=e,r.next=n,o&&(r.method="next",r.arg=t),!!o}for(var o=this.tryEntries.length-1;o>=0;--o){
var a=this.tryEntries[o],s=a.completion;if("root"===a.tryLoc)return n("end");if(a.tryLoc<=this.prev){var u=i.call(a,"catchLoc"),c=i.call(a,"finallyLoc");if(u&&c){
if(this.prev<a.catchLoc)return n(a.catchLoc,!0);if(this.prev<a.finallyLoc)return n(a.finallyLoc)}else if(u){if(this.prev<a.catchLoc)return n(a.catchLoc,!0)}else{
if(!c)throw Error("try statement without catch or finally");if(this.prev<a.finallyLoc)return n(a.finallyLoc)}}}},abrupt:function(t,e){
for(var r=this.tryEntries.length-1;r>=0;--r){var n=this.tryEntries[r];if(n.tryLoc<=this.prev&&i.call(n,"finallyLoc")&&this.prev<n.finallyLoc){var o=n;break}}
o&&("break"===t||"continue"===t)&&o.tryLoc<=e&&e<=o.finallyLoc&&(o=null);var a=o?o.completion:{};return a.type=t,a.arg=e,o?(this.method="next",
this.next=o.finallyLoc,m):this.complete(a)},complete:function(t,e){if("throw"===t.type)throw t.arg
;return"break"===t.type||"continue"===t.type?this.next=t.arg:"return"===t.type?(this.rval=this.arg=t.arg,this.method="return",
this.next="end"):"normal"===t.type&&e&&(this.next=e),m},finish:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.finallyLoc===t)return this.complete(r.completion,r.afterLoc),A(r),m}},catch:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.tryLoc===t){var n=r.completion;if("throw"===n.type){var o=n.arg;A(r)}return o}}throw Error("illegal catch attempt")},delegateYield:function(e,r,n){
return this.delegate={iterator:L(e),resultName:r,nextLoc:n},"next"===this.method&&(this.arg=t),m}},e}function i(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,a(n.key),n)}}function a(t){var e=function(t,e){
if("object"!=n(t)||!t)return t;var r=t[Symbol.toPrimitive];if(void 0!==r){var o=r.call(t,e||"default");if("object"!=n(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==n(e)?e:e+""}
Object.defineProperty(e,"__esModule",{value:!0}),e.Label=void 0;var s=r(95006),u=function(){return t=function t(e){!function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.client=e,this.urlPrefix="/api/v2"},(e=[{
key:"getLabelsByContentIdAndContentType",value:function(t,e,r){return s.__awaiter(this,void 0,void 0,o().mark((function n(){var i,a,s,u,c
;return o().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:return i={url:"".concat(this.urlPrefix,"/").concat(e,"/").concat(t,"/labels"),type:"GET",
queryParams:Object.assign({},r)},n.next=3,this.client.sendRequest(i);case 3:return a=n.sent,s=a.results,u=a._links,c=s.filter((function(t){var e=t.name
;return"string"==typeof e&&e})),n.abrupt("return",{results:c,_links:u});case 8:case"end":return n.stop()}}),n,this)})))}}])&&i(t.prototype,e),r&&i(t,r),
Object.defineProperty(t,"prototype",{writable:!1}),t;var t,e,r}();e.Label=u},45328:(t,e,r)=>{"use strict";function n(t){
return n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},n(t)}function o(){o=function(){return e}
;var t,e={},r=Object.prototype,i=r.hasOwnProperty,a=Object.defineProperty||function(t,e,r){t[e]=r.value
},s="function"==typeof Symbol?Symbol:{},u=s.iterator||"@@iterator",c=s.asyncIterator||"@@asyncIterator",l=s.toStringTag||"@@toStringTag";function f(t,e,r){
return Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}),t[e]}try{f({},"")}catch(t){f=function(t,e,r){return t[e]=r}}
function h(t,e,r,n){var o=e&&e.prototype instanceof b?e:b,i=Object.create(o.prototype),s=new I(n||[]);return a(i,"_invoke",{value:j(t,r,s)}),i}function p(t,e,r){try{
return{type:"normal",arg:t.call(e,r)}}catch(t){return{type:"throw",arg:t}}}e.wrap=h;var d="suspendedStart",y="suspendedYield",v="executing",g="completed",m={}
;function b(){}function w(){}function _(){}var x={};f(x,u,(function(){return this}));var P=Object.getPrototypeOf,S=P&&P(P(L([])));S&&S!==r&&i.call(S,u)&&(x=S)
;var E=_.prototype=b.prototype=Object.create(x);function O(t){["next","throw","return"].forEach((function(e){f(t,e,(function(t){return this._invoke(e,t)}))}))}
function k(t,e){function r(o,a,s,u){var c=p(t[o],t,a);if("throw"!==c.type){var l=c.arg,f=l.value
;return f&&"object"==n(f)&&i.call(f,"__await")?e.resolve(f.__await).then((function(t){r("next",t,s,u)}),(function(t){r("throw",t,s,u)
})):e.resolve(f).then((function(t){l.value=t,s(l)}),(function(t){return r("throw",t,s,u)}))}u(c.arg)}var o;a(this,"_invoke",{value:function(t,n){function i(){
return new e((function(e,o){r(t,n,e,o)}))}return o=o?o.then(i,i):i()}})}function j(e,r,n){var o=d;return function(i,a){
if(o===v)throw Error("Generator is already running");if(o===g){if("throw"===i)throw a;return{value:t,done:!0}}for(n.method=i,n.arg=a;;){var s=n.delegate;if(s){
var u=C(s,n);if(u){if(u===m)continue;return u}}if("next"===n.method)n.sent=n._sent=n.arg;else if("throw"===n.method){if(o===d)throw o=g,n.arg
;n.dispatchException(n.arg)}else"return"===n.method&&n.abrupt("return",n.arg);o=v;var c=p(e,r,n);if("normal"===c.type){if(o=n.done?g:y,c.arg===m)continue;return{
value:c.arg,done:n.done}}"throw"===c.type&&(o=g,n.method="throw",n.arg=c.arg)}}}function C(e,r){var n=r.method,o=e.iterator[n];if(o===t)return r.delegate=null,
"throw"===n&&e.iterator.return&&(r.method="return",r.arg=t,C(e,r),"throw"===r.method)||"return"!==n&&(r.method="throw",
r.arg=new TypeError("The iterator does not provide a '"+n+"' method")),m;var i=p(o,e.iterator,r.arg);if("throw"===i.type)return r.method="throw",r.arg=i.arg,
r.delegate=null,m;var a=i.arg;return a?a.done?(r[e.resultName]=a.value,r.next=e.nextLoc,"return"!==r.method&&(r.method="next",r.arg=t),r.delegate=null,
m):a:(r.method="throw",r.arg=new TypeError("iterator result is not an object"),r.delegate=null,m)}function T(t){var e={tryLoc:t[0]};1 in t&&(e.catchLoc=t[1]),
2 in t&&(e.finallyLoc=t[2],e.afterLoc=t[3]),this.tryEntries.push(e)}function A(t){var e=t.completion||{};e.type="normal",delete e.arg,t.completion=e}function I(t){
this.tryEntries=[{tryLoc:"root"}],t.forEach(T,this),this.reset(!0)}function L(e){if(e||""===e){var r=e[u];if(r)return r.call(e);if("function"==typeof e.next)return e
;if(!isNaN(e.length)){var o=-1,a=function r(){for(;++o<e.length;)if(i.call(e,o))return r.value=e[o],r.done=!1,r;return r.value=t,r.done=!0,r};return a.next=a}}
throw new TypeError(n(e)+" is not iterable")}return w.prototype=_,a(E,"constructor",{value:_,configurable:!0}),a(_,"constructor",{value:w,configurable:!0}),
w.displayName=f(_,l,"GeneratorFunction"),e.isGeneratorFunction=function(t){var e="function"==typeof t&&t.constructor
;return!!e&&(e===w||"GeneratorFunction"===(e.displayName||e.name))},e.mark=function(t){return Object.setPrototypeOf?Object.setPrototypeOf(t,_):(t.__proto__=_,
f(t,l,"GeneratorFunction")),t.prototype=Object.create(E),t},e.awrap=function(t){return{__await:t}},O(k.prototype),f(k.prototype,c,(function(){return this})),
e.AsyncIterator=k,e.async=function(t,r,n,o,i){void 0===i&&(i=Promise);var a=new k(h(t,r,n,o),i);return e.isGeneratorFunction(r)?a:a.next().then((function(t){
return t.done?t.value:a.next()}))},O(E),f(E,l,"Generator"),f(E,u,(function(){return this})),f(E,"toString",(function(){return"[object Generator]"})),
e.keys=function(t){var e=Object(t),r=[];for(var n in e)r.push(n);return r.reverse(),function t(){for(;r.length;){var n=r.pop();if(n in e)return t.value=n,t.done=!1,t
}return t.done=!0,t}},e.values=L,I.prototype={constructor:I,reset:function(e){if(this.prev=0,this.next=0,this.sent=this._sent=t,this.done=!1,this.delegate=null,
this.method="next",this.arg=t,this.tryEntries.forEach(A),!e)for(var r in this)"t"===r.charAt(0)&&i.call(this,r)&&!isNaN(+r.slice(1))&&(this[r]=t)},stop:function(){
this.done=!0;var t=this.tryEntries[0].completion;if("throw"===t.type)throw t.arg;return this.rval},dispatchException:function(e){if(this.done)throw e;var r=this
;function n(n,o){return s.type="throw",s.arg=e,r.next=n,o&&(r.method="next",r.arg=t),!!o}for(var o=this.tryEntries.length-1;o>=0;--o){
var a=this.tryEntries[o],s=a.completion;if("root"===a.tryLoc)return n("end");if(a.tryLoc<=this.prev){var u=i.call(a,"catchLoc"),c=i.call(a,"finallyLoc");if(u&&c){
if(this.prev<a.catchLoc)return n(a.catchLoc,!0);if(this.prev<a.finallyLoc)return n(a.finallyLoc)}else if(u){if(this.prev<a.catchLoc)return n(a.catchLoc,!0)}else{
if(!c)throw Error("try statement without catch or finally");if(this.prev<a.finallyLoc)return n(a.finallyLoc)}}}},abrupt:function(t,e){
for(var r=this.tryEntries.length-1;r>=0;--r){var n=this.tryEntries[r];if(n.tryLoc<=this.prev&&i.call(n,"finallyLoc")&&this.prev<n.finallyLoc){var o=n;break}}
o&&("break"===t||"continue"===t)&&o.tryLoc<=e&&e<=o.finallyLoc&&(o=null);var a=o?o.completion:{};return a.type=t,a.arg=e,o?(this.method="next",
this.next=o.finallyLoc,m):this.complete(a)},complete:function(t,e){if("throw"===t.type)throw t.arg
;return"break"===t.type||"continue"===t.type?this.next=t.arg:"return"===t.type?(this.rval=this.arg=t.arg,this.method="return",
this.next="end"):"normal"===t.type&&e&&(this.next=e),m},finish:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.finallyLoc===t)return this.complete(r.completion,r.afterLoc),A(r),m}},catch:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.tryLoc===t){var n=r.completion;if("throw"===n.type){var o=n.arg;A(r)}return o}}throw Error("illegal catch attempt")},delegateYield:function(e,r,n){
return this.delegate={iterator:L(e),resultName:r,nextLoc:n},"next"===this.method&&(this.arg=t),m}},e}function i(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,a(n.key),n)}}function a(t){var e=function(t,e){
if("object"!=n(t)||!t)return t;var r=t[Symbol.toPrimitive];if(void 0!==r){var o=r.call(t,e||"default");if("object"!=n(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==n(e)?e:e+""}
Object.defineProperty(e,"__esModule",{value:!0}),e.CustomContent=void 0;var s=r(95006),u=r(28271),c=function(){return t=function t(e){!function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.extendedConfluence=e,this.confluenceApi=e.confluenceApi},(e=[{
key:"_resolveCursor",value:function(t){var e=t.next;return e?new URL("https://"+e).searchParams.get("cursor"):""}},{key:"getCustomContentHistory",
value:function(t,e){return s.__awaiter(this,void 0,void 0,o().mark((function r(){var n,i,a,s,c;return o().wrap((function(r){for(;;)switch(r.prev=r.next){case 0:
return r.next=2,this.confluenceApi.version.getCustomContentVersions(t,{limit:(null==e?void 0:e.limit)||100,cursor:(null==e?void 0:e.cursor)||"",
sort:"-modified-date","body-format":u.ConfluencePrimaryBodyRepresentation.Storage});case 2:if(n=r.sent){r.next=5;break}return r.abrupt("return",{results:[],_links:{}
});case 5:return i=n.results,a=n._links,s=void 0===a?{}:a,c=this._resolveCursor(s)||"",r.abrupt("return",{results:i,_links:{},cursor:c});case 8:case"end":
return r.stop()}}),r,this)})))}},{key:"deleteCustomContent",value:function(t,e){return s.__awaiter(this,void 0,void 0,o().mark((function r(){var n
;return o().wrap((function(r){for(;;)switch(r.prev=r.next){case 0:return r.next=2,this.getCustomContent(t,e);case 2:if(n=r.sent){r.next=5;break}
return r.abrupt("return");case 5:return r.abrupt("return",this.confluenceApi.customContent.deleteCustomContent(n.id));case 6:case"end":return r.stop()}}),r,this)})))
}},{key:"getCustomContent",value:function(t,e,r){return s.__awaiter(this,void 0,void 0,o().mark((function n(){var i,a,s,c;return o().wrap((function(n){
for(;;)switch(n.prev=n.next){case 0:return n.next=2,this.extendedConfluence.content.getContentType(t);case 2:if(i=n.sent){n.next=5;break}
return n.abrupt("return",void 0);case 5:return n.next=7,this.confluenceApi.customContent.getCustomContent(t,i,{type:e,
sort:u.ConfluenceCustomContentSortOrder.ValueCreatedDate,"body-format":u.ConfluencePrimaryBodyRepresentation.Storage});case 7:if(a=n.sent){n.next=10;break}
return n.abrupt("return",void 0);case 10:return s=a.results,c=void 0===s?[]:s,r&&r.forEach((function(t,e,r){var n=a[e]
;"atl-traceid"===e&&"string"==typeof n&&r.set(e,n)})),n.abrupt("return",c[0]);case 13:case"end":return n.stop()}}),n,this)})))}},{key:"createCustomContent",
value:function(t,e){return s.__awaiter(this,void 0,void 0,o().mark((function r(){var n;return o().wrap((function(r){for(;;)switch(r.prev=r.next){case 0:
return r.next=2,this.extendedConfluence.content.getContentType(t);case 2:return n=r.sent,
r.abrupt("return",this.confluenceApi.customContent.createCustomContent(Object.assign(Object.assign(Object.assign(Object.assign({},e),{status:u.ContentStatus.Current
}),n===u.ContentType.Page&&{pageId:t}),n===u.ContentType.BlogPost&&{blogPostId:t})));case 4:case"end":return r.stop()}}),r,this)})))}},{key:"updateCustomContent",
value:function(t,e){return s.__awaiter(this,void 0,void 0,o().mark((function r(){return o().wrap((function(r){for(;;)switch(r.prev=r.next){case 0:
return r.abrupt("return",this.confluenceApi.customContent.updateCustomContent(t.id,{id:t.id,type:e.type,status:u.ContentStatus.Current,spaceId:t.spaceId,
title:e.title,body:e.body,version:{number:t.version.number+1}}));case 1:case"end":return r.stop()}}),r,this)})))}},{key:"setCustomContent",value:function(t,e){
return s.__awaiter(this,void 0,void 0,o().mark((function r(){var n;return o().wrap((function(r){for(;;)switch(r.prev=r.next){case 0:return r.next=2,
this.getCustomContent(t,e.type);case 2:if(n=r.sent){r.next=5;break}return r.abrupt("return",this.createCustomContent(t,e));case 5:
return r.abrupt("return",this.updateCustomContent(n,e));case 6:case"end":return r.stop()}}),r,this)})))}}])&&i(t.prototype,e),r&&i(t,r),
Object.defineProperty(t,"prototype",{writable:!1}),t;var t,e,r}();e.CustomContent=c},47869:(t,e)=>{"use strict";Object.defineProperty(e,"__esModule",{value:!0})},
51839:(t,e)=>{"use strict";Object.defineProperty(e,"__esModule",{value:!0})},52400:(t,e,r)=>{"use strict";Object.defineProperty(e,"__esModule",{value:!0})
;var n=r(95006);n.__exportStar(r(28663),e),n.__exportStar(r(84928),e),n.__exportStar(r(14773),e),n.__exportStar(r(4205),e),n.__exportStar(r(98852),e),
n.__exportStar(r(76804),e),n.__exportStar(r(24289),e),n.__exportStar(r(2497),e),n.__exportStar(r(74358),e),n.__exportStar(r(20160),e),n.__exportStar(r(58515),e),
n.__exportStar(r(79804),e),n.__exportStar(r(44053),e)},53886:(t,e)=>{"use strict";Object.defineProperty(e,"__esModule",{value:!0})},54884:(t,e,r)=>{"use strict"
;Object.defineProperty(e,"__esModule",{value:!0});var n=r(95006);n.__exportStar(r(87753),e),n.__exportStar(r(6032),e),n.__exportStar(r(45328),e),
n.__exportStar(r(73978),e),n.__exportStar(r(89676),e),n.__exportStar(r(21367),e),n.__exportStar(r(93720),e)},57615:(t,e)=>{"use strict"
;Object.defineProperty(e,"__esModule",{value:!0})},58515:(t,e)=>{"use strict";function r(t){
return r="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},r(t)}function n(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,o(n.key),n)}}function o(t){var e=function(t,e){
if("object"!=r(t)||!t)return t;var n=t[Symbol.toPrimitive];if(void 0!==n){var o=n.call(t,e||"default");if("object"!=r(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==r(e)?e:e+""}
Object.defineProperty(e,"__esModule",{value:!0}),e.SpaceProperties=void 0;var i=function(){return t=function t(e){!function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.client=e},(e=[{key:"getSpacePropertiesInSpace",value:function(t,e){
var r={url:"/api/v2/spaces/".concat(t,"/properties"),type:"GET",queryParams:{key:null==e?void 0:e.key,cursor:null==e?void 0:e.cursor,limit:null==e?void 0:e.limit}}
;return this.client.sendRequest(r)}},{key:"createSpacePropertyInSpace",value:function(t,e){var r={url:"/api/v2/spaces/".concat(t,"/properties"),type:"POST",
requestBody:{key:e.key,value:e.value}};return this.client.sendRequest(r)}},{key:"getSpacePropertyById",value:function(t,e){var r={
url:"/api/v2/spaces/".concat(t,"/properties/").concat(e),type:"GET"};return this.client.sendRequest(r)}},{key:"updateSpacePropertyById",value:function(t,e,r){var n={
url:"/api/v2/spaces/".concat(t,"/properties/").concat(e),type:"PUT",requestBody:{key:r.key,value:r.value,version:r.version}};return this.client.sendRequest(n)}},{
key:"deleteSpacePropertyById",value:function(t,e){var r={url:"/api/v2/spaces/".concat(t,"/properties/").concat(e),type:"DELETE"};return this.client.sendRequest(r)}
}])&&n(t.prototype,e),r&&n(t,r),Object.defineProperty(t,"prototype",{writable:!1}),t;var t,e,r}();e.SpaceProperties=i},60052:function(t,e){var r,n,o,i;function a(t){
return a="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},a(t)}i=function(t){"use strict";function e(t){
return"0123456789abcdefghijklmnopqrstuvwxyz".charAt(t)}function r(t,e){return t&e}function n(t,e){return t|e}function o(t,e){return t^e}function i(t,e){return t&~e}
function a(t){if(0==t)return-1;var e=0;return 65535&t||(t>>=16,e+=16),255&t||(t>>=8,e+=8),15&t||(t>>=4,e+=4),3&t||(t>>=2,e+=2),1&t||++e,e}function s(t){
for(var e=0;0!=t;)t&=t-1,++e;return e}var u="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";function c(t){var e,r,n=""
;for(e=0;e+3<=t.length;e+=3)r=parseInt(t.substring(e,e+3),16),n+=u.charAt(r>>6)+u.charAt(63&r);for(e+1==t.length?(r=parseInt(t.substring(e,e+1),16),
n+=u.charAt(r<<2)):e+2==t.length&&(r=parseInt(t.substring(e,e+2),16),n+=u.charAt(r>>2)+u.charAt((3&r)<<4));(3&n.length)>0;)n+="=";return n}function l(t){
var r,n="",o=0,i=0;for(r=0;r<t.length&&"="!=t.charAt(r);++r){var a=u.indexOf(t.charAt(r));a<0||(0==o?(n+=e(a>>2),i=3&a,o=1):1==o?(n+=e(i<<2|a>>4),i=15&a,
o=2):2==o?(n+=e(i),n+=e(a>>2),i=3&a,o=3):(n+=e(i<<2|a>>4),n+=e(15&a),o=0))}return 1==o&&(n+=e(i<<2)),n}var f,h,p=function(t,e){return p=Object.setPrototypeOf||{
__proto__:[]}instanceof Array&&function(t,e){t.__proto__=e}||function(t,e){for(var r in e)e.hasOwnProperty(r)&&(t[r]=e[r])},p(t,e)},d=function(t){var e
;if(void 0===f){var r="0123456789ABCDEF",n=" \f\n\r\t \u2028\u2029";for(f={},e=0;e<16;++e)f[r.charAt(e)]=e;for(r=r.toLowerCase(),e=10;e<16;++e)f[r.charAt(e)]=e
;for(e=0;e<8;++e)f[n.charAt(e)]=-1}var o=[],i=0,a=0;for(e=0;e<t.length;++e){var s=t.charAt(e);if("="==s)break;if(-1!=(s=f[s])){
if(void 0===s)throw new Error("Illegal character at offset "+e);i|=s,++a>=2?(o[o.length]=i,i=0,a=0):i<<=4}}
if(a)throw new Error("Hex encoding incomplete: 4 bits missing");return o},y={decode:function(t){var e;if(void 0===h){var r="= \f\n\r\t \u2028\u2029"
;for(h=Object.create(null),e=0;e<64;++e)h["ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charAt(e)]=e;for(e=0;e<9;++e)h[r.charAt(e)]=-1}
var n=[],o=0,i=0;for(e=0;e<t.length;++e){var a=t.charAt(e);if("="==a)break;if(-1!=(a=h[a])){if(void 0===a)throw new Error("Illegal character at offset "+e);o|=a,
++i>=4?(n[n.length]=o>>16,n[n.length]=o>>8&255,n[n.length]=255&o,o=0,i=0):o<<=6}}switch(i){case 1:
throw new Error("Base64 encoding incomplete: at least 2 bits missing");case 2:n[n.length]=o>>10;break;case 3:n[n.length]=o>>16,n[n.length]=o>>8&255}return n},
re:/-----BEGIN [^-]+-----([A-Za-z0-9+\/=\s]+)-----END [^-]+-----|begin-base64[^\n]+\n([A-Za-z0-9+\/=\s]+)====/,unarmor:function(t){var e=y.re.exec(t)
;if(e)if(e[1])t=e[1];else{if(!e[2])throw new Error("RegExp out of sync");t=e[2]}return y.decode(t)}},v=1e13,g=function(){function t(t){this.buf=[+t||0]}
return t.prototype.mulAdd=function(t,e){var r,n,o=this.buf,i=o.length;for(r=0;r<i;++r)(n=o[r]*t+e)<v?e=0:n-=(e=0|n/v)*v,o[r]=n;e>0&&(o[r]=e)},
t.prototype.sub=function(t){var e,r,n=this.buf,o=n.length;for(e=0;e<o;++e)(r=n[e]-t)<0?(r+=v,t=1):t=0,n[e]=r;for(;0===n[n.length-1];)n.pop()},
t.prototype.toString=function(t){if(10!=(t||10))throw new Error("only base 10 is supported")
;for(var e=this.buf,r=e[e.length-1].toString(),n=e.length-2;n>=0;--n)r+=(v+e[n]).toString().substring(1);return r},t.prototype.valueOf=function(){
for(var t=this.buf,e=0,r=t.length-1;r>=0;--r)e=e*v+t[r];return e},t.prototype.simplify=function(){var t=this.buf;return 1==t.length?t[0]:this},t
}(),m=/^(\d\d)(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])([01]\d|2[0-3])(?:([0-5]\d)(?:([0-5]\d)(?:[.,](\d{1,3}))?)?)?(Z|[-+](?:[0]\d|1[0-2])([0-5]\d)?)?$/,b=/^(\d\d\d\d)(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])([01]\d|2[0-3])(?:([0-5]\d)(?:([0-5]\d)(?:[.,](\d{1,3}))?)?)?(Z|[-+](?:[0]\d|1[0-2])([0-5]\d)?)?$/
;function w(t,e){return t.length>e&&(t=t.substring(0,e)+"…"),t}var _,x=function(){function t(e,r){this.hexDigits="0123456789ABCDEF",e instanceof t?(this.enc=e.enc,
this.pos=e.pos):(this.enc=e,this.pos=r)}return t.prototype.get=function(t){if(void 0===t&&(t=this.pos++),
t>=this.enc.length)throw new Error("Requesting byte offset "+t+" on a stream of length "+this.enc.length)
;return"string"==typeof this.enc?this.enc.charCodeAt(t):this.enc[t]},t.prototype.hexByte=function(t){
return this.hexDigits.charAt(t>>4&15)+this.hexDigits.charAt(15&t)},t.prototype.hexDump=function(t,e,r){for(var n="",o=t;o<e;++o)if(n+=this.hexByte(this.get(o)),
!0!==r)switch(15&o){case 7:n+="  ";break;case 15:n+="\n";break;default:n+=" "}return n},t.prototype.isASCII=function(t,e){for(var r=t;r<e;++r){var n=this.get(r)
;if(n<32||n>176)return!1}return!0},t.prototype.parseStringISO=function(t,e){for(var r="",n=t;n<e;++n)r+=String.fromCharCode(this.get(n));return r},
t.prototype.parseStringUTF=function(t,e){for(var r="",n=t;n<e;){var o=this.get(n++)
;r+=o<128?String.fromCharCode(o):o>191&&o<224?String.fromCharCode((31&o)<<6|63&this.get(n++)):String.fromCharCode((15&o)<<12|(63&this.get(n++))<<6|63&this.get(n++))}
return r},t.prototype.parseStringBMP=function(t,e){for(var r,n,o="",i=t;i<e;)r=this.get(i++),n=this.get(i++),o+=String.fromCharCode(r<<8|n);return o},
t.prototype.parseTime=function(t,e,r){var n=this.parseStringISO(t,e),o=(r?m:b).exec(n);return o?(r&&(o[1]=+o[1],o[1]+=+o[1]<70?2e3:1900),
n=o[1]+"-"+o[2]+"-"+o[3]+" "+o[4],o[5]&&(n+=":"+o[5],o[6]&&(n+=":"+o[6],o[7]&&(n+="."+o[7]))),o[8]&&(n+=" UTC","Z"!=o[8]&&(n+=o[8],o[9]&&(n+=":"+o[9]))),
n):"Unrecognized time: "+n},t.prototype.parseInteger=function(t,e){for(var r,n=this.get(t),o=n>127,i=o?255:0,a="";n==i&&++t<e;)n=this.get(t)
;if(0==(r=e-t))return o?-1:0;if(r>4){for(a=n,r<<=3;!(128&(+a^i));)a=+a<<1,--r;a="("+r+" bit)\n"}o&&(n-=256)
;for(var s=new g(n),u=t+1;u<e;++u)s.mulAdd(256,this.get(u));return a+s.toString()},t.prototype.parseBitString=function(t,e,r){
for(var n=this.get(t),o="("+((e-t-1<<3)-n)+" bit)\n",i="",a=t+1;a<e;++a){for(var s=this.get(a),u=a==e-1?n:0,c=7;c>=u;--c)i+=s>>c&1?"1":"0"
;if(i.length>r)return o+w(i,r)}return o+i},t.prototype.parseOctetString=function(t,e,r){if(this.isASCII(t,e))return w(this.parseStringISO(t,e),r)
;var n=e-t,o="("+n+" byte)\n";n>(r/=2)&&(e=t+r);for(var i=t;i<e;++i)o+=this.hexByte(this.get(i));return n>r&&(o+="…"),o},t.prototype.parseOID=function(t,e,r){
for(var n="",o=new g,i=0,a=t;a<e;++a){var s=this.get(a);if(o.mulAdd(128,127&s),i+=7,!(128&s)){if(""===n)if((o=o.simplify())instanceof g)o.sub(80),
n="2."+o.toString();else{var u=o<80?o<40?0:1:2;n=u+"."+(o-40*u)}else n+="."+o.toString();if(n.length>r)return w(n,r);o=new g,i=0}}return i>0&&(n+=".incomplete"),n},t
}(),P=function(){function t(t,e,r,n,o){if(!(n instanceof S))throw new Error("Invalid tag value.");this.stream=t,this.header=e,this.length=r,this.tag=n,this.sub=o}
return t.prototype.typeName=function(){switch(this.tag.tagClass){case 0:switch(this.tag.tagNumber){case 0:return"EOC";case 1:return"BOOLEAN";case 2:return"INTEGER"
;case 3:return"BIT_STRING";case 4:return"OCTET_STRING";case 5:return"NULL";case 6:return"OBJECT_IDENTIFIER";case 7:return"ObjectDescriptor";case 8:return"EXTERNAL"
;case 9:return"REAL";case 10:return"ENUMERATED";case 11:return"EMBEDDED_PDV";case 12:return"UTF8String";case 16:return"SEQUENCE";case 17:return"SET";case 18:
return"NumericString";case 19:return"PrintableString";case 20:return"TeletexString";case 21:return"VideotexString";case 22:return"IA5String";case 23:return"UTCTime"
;case 24:return"GeneralizedTime";case 25:return"GraphicString";case 26:return"VisibleString";case 27:return"GeneralString";case 28:return"UniversalString";case 30:
return"BMPString"}return"Universal_"+this.tag.tagNumber.toString();case 1:return"Application_"+this.tag.tagNumber.toString();case 2:
return"["+this.tag.tagNumber.toString()+"]";case 3:return"Private_"+this.tag.tagNumber.toString()}},t.prototype.content=function(t){if(void 0===this.tag)return null
;void 0===t&&(t=1/0);var e=this.posContent(),r=Math.abs(this.length)
;if(!this.tag.isUniversal())return null!==this.sub?"("+this.sub.length+" elem)":this.stream.parseOctetString(e,e+r,t);switch(this.tag.tagNumber){case 1:
return 0===this.stream.get(e)?"false":"true";case 2:return this.stream.parseInteger(e,e+r);case 3:
return this.sub?"("+this.sub.length+" elem)":this.stream.parseBitString(e,e+r,t);case 4:
return this.sub?"("+this.sub.length+" elem)":this.stream.parseOctetString(e,e+r,t);case 6:return this.stream.parseOID(e,e+r,t);case 16:case 17:
return null!==this.sub?"("+this.sub.length+" elem)":"(no elem)";case 12:return w(this.stream.parseStringUTF(e,e+r),t);case 18:case 19:case 20:case 21:case 22:
case 26:return w(this.stream.parseStringISO(e,e+r),t);case 30:return w(this.stream.parseStringBMP(e,e+r),t);case 23:case 24:
return this.stream.parseTime(e,e+r,23==this.tag.tagNumber)}return null},t.prototype.toString=function(){
return this.typeName()+"@"+this.stream.pos+"[header:"+this.header+",length:"+this.length+",sub:"+(null===this.sub?"null":this.sub.length)+"]"},
t.prototype.toPrettyString=function(t){void 0===t&&(t="");var e=t+this.typeName()+" @"+this.stream.pos;if(this.length>=0&&(e+="+"),e+=this.length,
this.tag.tagConstructed?e+=" (constructed)":!this.tag.isUniversal()||3!=this.tag.tagNumber&&4!=this.tag.tagNumber||null===this.sub||(e+=" (encapsulates)"),e+="\n",
null!==this.sub){t+="  ";for(var r=0,n=this.sub.length;r<n;++r)e+=this.sub[r].toPrettyString(t)}return e},t.prototype.posStart=function(){return this.stream.pos},
t.prototype.posContent=function(){return this.stream.pos+this.header},t.prototype.posEnd=function(){return this.stream.pos+this.header+Math.abs(this.length)},
t.prototype.toHexString=function(){return this.stream.hexDump(this.posStart(),this.posEnd(),!0)},t.decodeLength=function(t){var e=t.get(),r=127&e;if(r==e)return r
;if(r>6)throw new Error("Length over 48 bits not supported at position "+(t.pos-1));if(0===r)return null;e=0;for(var n=0;n<r;++n)e=256*e+t.get();return e},
t.prototype.getHexStringValue=function(){var t=this.toHexString(),e=2*this.header,r=2*this.length;return t.substr(e,r)},t.decode=function(e){var r
;r=e instanceof x?e:new x(e,0);var n=new x(r),o=new S(r),i=t.decodeLength(r),a=r.pos,s=a-n.pos,u=null,c=function(){var e=[];if(null!==i){
for(var n=a+i;r.pos<n;)e[e.length]=t.decode(r);if(r.pos!=n)throw new Error("Content size is not correct for container starting at offset "+a)}else try{for(;;){
var o=t.decode(r);if(o.tag.isEOC())break;e[e.length]=o}i=a-r.pos}catch(t){throw new Error("Exception while decoding undefined length content: "+t)}return e}
;if(o.tagConstructed)u=c();else if(o.isUniversal()&&(3==o.tagNumber||4==o.tagNumber))try{
if(3==o.tagNumber&&0!=r.get())throw new Error("BIT STRINGs with unused bits cannot encapsulate.");u=c()
;for(var l=0;l<u.length;++l)if(u[l].tag.isEOC())throw new Error("EOC is not supposed to be actual content.")}catch(t){u=null}if(null===u){
if(null===i)throw new Error("We can't skip over an invalid tag with undefined length at offset "+a);r.pos=a+Math.abs(i)}return new t(n,s,i,o,u)},t}(),S=function(){
function t(t){var e=t.get();if(this.tagClass=e>>6,this.tagConstructed=!!(32&e),this.tagNumber=31&e,31==this.tagNumber){var r=new g;do{e=t.get(),r.mulAdd(128,127&e)
}while(128&e);this.tagNumber=r.simplify()}}return t.prototype.isUniversal=function(){return 0===this.tagClass},t.prototype.isEOC=function(){
return 0===this.tagClass&&0===this.tagNumber},t
}(),E=[2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,179,181,191,193,197,199,211,223,227,229,233,239,241,251,257,263,269,271,277,281,283,293,307,311,313,317,331,337,347,349,353,359,367,373,379,383,389,397,401,409,419,421,431,433,439,443,449,457,461,463,467,479,487,491,499,503,509,521,523,541,547,557,563,569,571,577,587,593,599,601,607,613,617,619,631,641,643,647,653,659,661,673,677,683,691,701,709,719,727,733,739,743,751,757,761,769,773,787,797,809,811,821,823,827,829,839,853,857,859,863,877,881,883,887,907,911,919,929,937,941,947,953,967,971,977,983,991,997],O=(1<<26)/E[E.length-1],k=function(){
function t(t,e,r){null!=t&&("number"==typeof t?this.fromNumber(t,e,r):null==e&&"string"!=typeof t?this.fromString(t,256):this.fromString(t,e))}
return t.prototype.toString=function(t){if(this.s<0)return"-"+this.negate().toString(t);var r;if(16==t)r=4;else if(8==t)r=3;else if(2==t)r=1;else if(32==t)r=5;else{
if(4!=t)return this.toRadix(t);r=2}var n,o=(1<<r)-1,i=!1,a="",s=this.t,u=this.DB-s*this.DB%r;if(s-- >0)for(u<this.DB&&(n=this[s]>>u)>0&&(i=!0,
a=e(n));s>=0;)u<r?(n=(this[s]&(1<<u)-1)<<r-u,n|=this[--s]>>(u+=this.DB-r)):(n=this[s]>>(u-=r)&o,u<=0&&(u+=this.DB,--s)),n>0&&(i=!0),i&&(a+=e(n));return i?a:"0"},
t.prototype.negate=function(){var e=I();return t.ZERO.subTo(this,e),e},t.prototype.abs=function(){return this.s<0?this.negate():this},
t.prototype.compareTo=function(t){var e=this.s-t.s;if(0!=e)return e;var r=this.t;if(0!=(e=r-t.t))return this.s<0?-e:e;for(;--r>=0;)if(0!=(e=this[r]-t[r]))return e
;return 0},t.prototype.bitLength=function(){return this.t<=0?0:this.DB*(this.t-1)+M(this[this.t-1]^this.s&this.DM)},t.prototype.mod=function(e){var r=I()
;return this.abs().divRemTo(e,null,r),this.s<0&&r.compareTo(t.ZERO)>0&&e.subTo(r,r),r},t.prototype.modPowInt=function(t,e){var r
;return r=t<256||e.isEven()?new C(e):new T(e),this.exp(t,r)},t.prototype.clone=function(){var t=I();return this.copyTo(t),t},t.prototype.intValue=function(){
if(this.s<0){if(1==this.t)return this[0]-this.DV;if(0==this.t)return-1}else{if(1==this.t)return this[0];if(0==this.t)return 0}
return(this[1]&(1<<32-this.DB)-1)<<this.DB|this[0]},t.prototype.byteValue=function(){return 0==this.t?this.s:this[0]<<24>>24},t.prototype.shortValue=function(){
return 0==this.t?this.s:this[0]<<16>>16},t.prototype.signum=function(){return this.s<0?-1:this.t<=0||1==this.t&&this[0]<=0?0:1},t.prototype.toByteArray=function(){
var t=this.t,e=[];e[0]=this.s;var r,n=this.DB-t*this.DB%8,o=0
;if(t-- >0)for(n<this.DB&&(r=this[t]>>n)!=(this.s&this.DM)>>n&&(e[o++]=r|this.s<<this.DB-n);t>=0;)n<8?(r=(this[t]&(1<<n)-1)<<8-n,
r|=this[--t]>>(n+=this.DB-8)):(r=this[t]>>(n-=8)&255,n<=0&&(n+=this.DB,--t)),128&r&&(r|=-256),0==o&&(128&this.s)!=(128&r)&&++o,(o>0||r!=this.s)&&(e[o++]=r);return e
},t.prototype.equals=function(t){return 0==this.compareTo(t)},t.prototype.min=function(t){return this.compareTo(t)<0?this:t},t.prototype.max=function(t){
return this.compareTo(t)>0?this:t},t.prototype.and=function(t){var e=I();return this.bitwiseTo(t,r,e),e},t.prototype.or=function(t){var e=I()
;return this.bitwiseTo(t,n,e),e},t.prototype.xor=function(t){var e=I();return this.bitwiseTo(t,o,e),e},t.prototype.andNot=function(t){var e=I()
;return this.bitwiseTo(t,i,e),e},t.prototype.not=function(){for(var t=I(),e=0;e<this.t;++e)t[e]=this.DM&~this[e];return t.t=this.t,t.s=~this.s,t},
t.prototype.shiftLeft=function(t){var e=I();return t<0?this.rShiftTo(-t,e):this.lShiftTo(t,e),e},t.prototype.shiftRight=function(t){var e=I()
;return t<0?this.lShiftTo(-t,e):this.rShiftTo(t,e),e},t.prototype.getLowestSetBit=function(){for(var t=0;t<this.t;++t)if(0!=this[t])return t*this.DB+a(this[t])
;return this.s<0?this.t*this.DB:-1},t.prototype.bitCount=function(){for(var t=0,e=this.s&this.DM,r=0;r<this.t;++r)t+=s(this[r]^e);return t},
t.prototype.testBit=function(t){var e=Math.floor(t/this.DB);return e>=this.t?0!=this.s:!!(this[e]&1<<t%this.DB)},t.prototype.setBit=function(t){
return this.changeBit(t,n)},t.prototype.clearBit=function(t){return this.changeBit(t,i)},t.prototype.flipBit=function(t){return this.changeBit(t,o)},
t.prototype.add=function(t){var e=I();return this.addTo(t,e),e},t.prototype.subtract=function(t){var e=I();return this.subTo(t,e),e},
t.prototype.multiply=function(t){var e=I();return this.multiplyTo(t,e),e},t.prototype.divide=function(t){var e=I();return this.divRemTo(t,e,null),e},
t.prototype.remainder=function(t){var e=I();return this.divRemTo(t,null,e),e},t.prototype.divideAndRemainder=function(t){var e=I(),r=I();return this.divRemTo(t,e,r),
[e,r]},t.prototype.modPow=function(t,e){var r,n,o=t.bitLength(),i=F(1);if(o<=0)return i;r=o<18?1:o<48?3:o<144?4:o<768?5:6,n=o<8?new C(e):e.isEven()?new A(e):new T(e)
;var a=[],s=3,u=r-1,c=(1<<r)-1;if(a[1]=n.convert(this),r>1){var l=I();for(n.sqrTo(a[1],l);s<=c;)a[s]=I(),n.mulTo(l,a[s-2],a[s]),s+=2}var f,h,p=t.t-1,d=!0,y=I()
;for(o=M(t[p])-1;p>=0;){for(o>=u?f=t[p]>>o-u&c:(f=(t[p]&(1<<o+1)-1)<<u-o,p>0&&(f|=t[p-1]>>this.DB+o-u)),s=r;!(1&f);)f>>=1,--s;if((o-=s)<0&&(o+=this.DB,--p),
d)a[f].copyTo(i),d=!1;else{for(;s>1;)n.sqrTo(i,y),n.sqrTo(y,i),s-=2;s>0?n.sqrTo(i,y):(h=i,i=y,y=h),n.mulTo(y,a[f],i)}for(;p>=0&&!(t[p]&1<<o);)n.sqrTo(i,y),h=i,i=y,
y=h,--o<0&&(o=this.DB-1,--p)}return n.revert(i)},t.prototype.modInverse=function(e){var r=e.isEven();if(this.isEven()&&r||0==e.signum())return t.ZERO
;for(var n=e.clone(),o=this.clone(),i=F(1),a=F(0),s=F(0),u=F(1);0!=n.signum();){for(;n.isEven();)n.rShiftTo(1,n),r?(i.isEven()&&a.isEven()||(i.addTo(this,i),
a.subTo(e,a)),i.rShiftTo(1,i)):a.isEven()||a.subTo(e,a),a.rShiftTo(1,a);for(;o.isEven();)o.rShiftTo(1,o),r?(s.isEven()&&u.isEven()||(s.addTo(this,s),u.subTo(e,u)),
s.rShiftTo(1,s)):u.isEven()||u.subTo(e,u),u.rShiftTo(1,u);n.compareTo(o)>=0?(n.subTo(o,n),r&&i.subTo(s,i),a.subTo(u,a)):(o.subTo(n,o),r&&s.subTo(i,s),u.subTo(a,u))}
return 0!=o.compareTo(t.ONE)?t.ZERO:u.compareTo(e)>=0?u.subtract(e):u.signum()<0?(u.addTo(e,u),u.signum()<0?u.add(e):u):u},t.prototype.pow=function(t){
return this.exp(t,new j)},t.prototype.gcd=function(t){var e=this.s<0?this.negate():this.clone(),r=t.s<0?t.negate():t.clone();if(e.compareTo(r)<0){var n=e;e=r,r=n}
var o=e.getLowestSetBit(),i=r.getLowestSetBit();if(i<0)return e;for(o<i&&(i=o),i>0&&(e.rShiftTo(i,e),
r.rShiftTo(i,r));e.signum()>0;)(o=e.getLowestSetBit())>0&&e.rShiftTo(o,e),(o=r.getLowestSetBit())>0&&r.rShiftTo(o,r),e.compareTo(r)>=0?(e.subTo(r,e),
e.rShiftTo(1,e)):(r.subTo(e,r),r.rShiftTo(1,r));return i>0&&r.lShiftTo(i,r),r},t.prototype.isProbablePrime=function(t){var e,r=this.abs()
;if(1==r.t&&r[0]<=E[E.length-1]){for(e=0;e<E.length;++e)if(r[0]==E[e])return!0;return!1}if(r.isEven())return!1;for(e=1;e<E.length;){
for(var n=E[e],o=e+1;o<E.length&&n<O;)n*=E[o++];for(n=r.modInt(n);e<o;)if(n%E[e++]==0)return!1}return r.millerRabin(t)},t.prototype.copyTo=function(t){
for(var e=this.t-1;e>=0;--e)t[e]=this[e];t.t=this.t,t.s=this.s},t.prototype.fromInt=function(t){this.t=1,this.s=t<0?-1:0,
t>0?this[0]=t:t<-1?this[0]=t+this.DV:this.t=0},t.prototype.fromString=function(e,r){var n
;if(16==r)n=4;else if(8==r)n=3;else if(256==r)n=8;else if(2==r)n=1;else if(32==r)n=5;else{if(4!=r)return void this.fromRadix(e,r);n=2}this.t=0,this.s=0
;for(var o=e.length,i=!1,a=0;--o>=0;){var s=8==n?255&+e[o]:B(e,o);s<0?"-"==e.charAt(o)&&(i=!0):(i=!1,
0==a?this[this.t++]=s:a+n>this.DB?(this[this.t-1]|=(s&(1<<this.DB-a)-1)<<a,this[this.t++]=s>>this.DB-a):this[this.t-1]|=s<<a,(a+=n)>=this.DB&&(a-=this.DB))}
8==n&&128&+e[0]&&(this.s=-1,a>0&&(this[this.t-1]|=(1<<this.DB-a)-1<<a)),this.clamp(),i&&t.ZERO.subTo(this,this)},t.prototype.clamp=function(){
for(var t=this.s&this.DM;this.t>0&&this[this.t-1]==t;)--this.t},t.prototype.dlShiftTo=function(t,e){var r;for(r=this.t-1;r>=0;--r)e[r+t]=this[r]
;for(r=t-1;r>=0;--r)e[r]=0;e.t=this.t+t,e.s=this.s},t.prototype.drShiftTo=function(t,e){for(var r=t;r<this.t;++r)e[r-t]=this[r];e.t=Math.max(this.t-t,0),e.s=this.s},
t.prototype.lShiftTo=function(t,e){for(var r=t%this.DB,n=this.DB-r,o=(1<<n)-1,i=Math.floor(t/this.DB),a=this.s<<r&this.DM,s=this.t-1;s>=0;--s)e[s+i+1]=this[s]>>n|a,
a=(this[s]&o)<<r;for(s=i-1;s>=0;--s)e[s]=0;e[i]=a,e.t=this.t+i+1,e.s=this.s,e.clamp()},t.prototype.rShiftTo=function(t,e){e.s=this.s;var r=Math.floor(t/this.DB)
;if(r>=this.t)e.t=0;else{var n=t%this.DB,o=this.DB-n,i=(1<<n)-1;e[0]=this[r]>>n;for(var a=r+1;a<this.t;++a)e[a-r-1]|=(this[a]&i)<<o,e[a-r]=this[a]>>n
;n>0&&(e[this.t-r-1]|=(this.s&i)<<o),e.t=this.t-r,e.clamp()}},t.prototype.subTo=function(t,e){for(var r=0,n=0,o=Math.min(t.t,this.t);r<o;)n+=this[r]-t[r],
e[r++]=n&this.DM,n>>=this.DB;if(t.t<this.t){for(n-=t.s;r<this.t;)n+=this[r],e[r++]=n&this.DM,n>>=this.DB;n+=this.s}else{for(n+=this.s;r<t.t;)n-=t[r],
e[r++]=n&this.DM,n>>=this.DB;n-=t.s}e.s=n<0?-1:0,n<-1?e[r++]=this.DV+n:n>0&&(e[r++]=n),e.t=r,e.clamp()},t.prototype.multiplyTo=function(e,r){
var n=this.abs(),o=e.abs(),i=n.t;for(r.t=i+o.t;--i>=0;)r[i]=0;for(i=0;i<o.t;++i)r[i+n.t]=n.am(0,o[i],r,i,0,n.t);r.s=0,r.clamp(),this.s!=e.s&&t.ZERO.subTo(r,r)},
t.prototype.squareTo=function(t){for(var e=this.abs(),r=t.t=2*e.t;--r>=0;)t[r]=0;for(r=0;r<e.t-1;++r){var n=e.am(r,e[r],t,2*r,0,1)
;(t[r+e.t]+=e.am(r+1,2*e[r],t,2*r+1,n,e.t-r-1))>=e.DV&&(t[r+e.t]-=e.DV,t[r+e.t+1]=1)}t.t>0&&(t[t.t-1]+=e.am(r,e[r],t,2*r,0,1)),t.s=0,t.clamp()},
t.prototype.divRemTo=function(e,r,n){var o=e.abs();if(!(o.t<=0)){var i=this.abs();if(i.t<o.t)return null!=r&&r.fromInt(0),void(null!=n&&this.copyTo(n))
;null==n&&(n=I());var a=I(),s=this.s,u=e.s,c=this.DB-M(o[o.t-1]);c>0?(o.lShiftTo(c,a),i.lShiftTo(c,n)):(o.copyTo(a),i.copyTo(n));var l=a.t,f=a[l-1];if(0!=f){
var h=f*(1<<this.F1)+(l>1?a[l-2]>>this.F2:0),p=this.FV/h,d=(1<<this.F1)/h,y=1<<this.F2,v=n.t,g=v-l,m=null==r?I():r;for(a.dlShiftTo(g,m),
n.compareTo(m)>=0&&(n[n.t++]=1,n.subTo(m,n)),t.ONE.dlShiftTo(l,m),m.subTo(a,a);a.t<l;)a[a.t++]=0;for(;--g>=0;){
var b=n[--v]==f?this.DM:Math.floor(n[v]*p+(n[v-1]+y)*d);if((n[v]+=a.am(0,b,n,g,0,l))<b)for(a.dlShiftTo(g,m),n.subTo(m,n);n[v]<--b;)n.subTo(m,n)}
null!=r&&(n.drShiftTo(l,r),s!=u&&t.ZERO.subTo(r,r)),n.t=l,n.clamp(),c>0&&n.rShiftTo(c,n),s<0&&t.ZERO.subTo(n,n)}}},t.prototype.invDigit=function(){
if(this.t<1)return 0;var t=this[0];if(!(1&t))return 0;var e=3&t
;return(e=(e=(e=(e=e*(2-(15&t)*e)&15)*(2-(255&t)*e)&255)*(2-((65535&t)*e&65535))&65535)*(2-t*e%this.DV)%this.DV)>0?this.DV-e:-e},t.prototype.isEven=function(){
return 0==(this.t>0?1&this[0]:this.s)},t.prototype.exp=function(e,r){if(e>4294967295||e<1)return t.ONE;var n=I(),o=I(),i=r.convert(this),a=M(e)-1
;for(i.copyTo(n);--a>=0;)if(r.sqrTo(n,o),(e&1<<a)>0)r.mulTo(o,i,n);else{var s=n;n=o,o=s}return r.revert(n)},t.prototype.chunkSize=function(t){
return Math.floor(Math.LN2*this.DB/Math.log(t))},t.prototype.toRadix=function(t){if(null==t&&(t=10),0==this.signum()||t<2||t>36)return"0"
;var e=this.chunkSize(t),r=Math.pow(t,e),n=F(r),o=I(),i=I(),a="";for(this.divRemTo(n,o,i);o.signum()>0;)a=(r+i.intValue()).toString(t).substr(1)+a,o.divRemTo(n,o,i)
;return i.intValue().toString(t)+a},t.prototype.fromRadix=function(e,r){this.fromInt(0),null==r&&(r=10)
;for(var n=this.chunkSize(r),o=Math.pow(r,n),i=!1,a=0,s=0,u=0;u<e.length;++u){var c=B(e,u);c<0?"-"==e.charAt(u)&&0==this.signum()&&(i=!0):(s=r*s+c,
++a>=n&&(this.dMultiply(o),this.dAddOffset(s,0),a=0,s=0))}a>0&&(this.dMultiply(Math.pow(r,a)),this.dAddOffset(s,0)),i&&t.ZERO.subTo(this,this)},
t.prototype.fromNumber=function(e,r,o){if("number"==typeof r)if(e<2)this.fromInt(1);else for(this.fromNumber(e,o),
this.testBit(e-1)||this.bitwiseTo(t.ONE.shiftLeft(e-1),n,this),this.isEven()&&this.dAddOffset(1,0);!this.isProbablePrime(r);)this.dAddOffset(2,0),
this.bitLength()>e&&this.subTo(t.ONE.shiftLeft(e-1),this);else{var i=[],a=7&e;i.length=1+(e>>3),r.nextBytes(i),a>0?i[0]&=(1<<a)-1:i[0]=0,this.fromString(i,256)}},
t.prototype.bitwiseTo=function(t,e,r){var n,o,i=Math.min(t.t,this.t);for(n=0;n<i;++n)r[n]=e(this[n],t[n]);if(t.t<this.t){for(o=t.s&this.DM,
n=i;n<this.t;++n)r[n]=e(this[n],o);r.t=this.t}else{for(o=this.s&this.DM,n=i;n<t.t;++n)r[n]=e(o,t[n]);r.t=t.t}r.s=e(this.s,t.s),r.clamp()},
t.prototype.changeBit=function(e,r){var n=t.ONE.shiftLeft(e);return this.bitwiseTo(n,r,n),n},t.prototype.addTo=function(t,e){
for(var r=0,n=0,o=Math.min(t.t,this.t);r<o;)n+=this[r]+t[r],e[r++]=n&this.DM,n>>=this.DB;if(t.t<this.t){for(n+=t.s;r<this.t;)n+=this[r],e[r++]=n&this.DM,n>>=this.DB
;n+=this.s}else{for(n+=this.s;r<t.t;)n+=t[r],e[r++]=n&this.DM,n>>=this.DB;n+=t.s}e.s=n<0?-1:0,n>0?e[r++]=n:n<-1&&(e[r++]=this.DV+n),e.t=r,e.clamp()},
t.prototype.dMultiply=function(t){this[this.t]=this.am(0,t-1,this,0,0,this.t),++this.t,this.clamp()},t.prototype.dAddOffset=function(t,e){if(0!=t){
for(;this.t<=e;)this[this.t++]=0;for(this[e]+=t;this[e]>=this.DV;)this[e]-=this.DV,++e>=this.t&&(this[this.t++]=0),++this[e]}},
t.prototype.multiplyLowerTo=function(t,e,r){var n=Math.min(this.t+t.t,e);for(r.s=0,r.t=n;n>0;)r[--n]=0
;for(var o=r.t-this.t;n<o;++n)r[n+this.t]=this.am(0,t[n],r,n,0,this.t);for(o=Math.min(t.t,e);n<o;++n)this.am(0,t[n],r,n,0,e-n);r.clamp()},
t.prototype.multiplyUpperTo=function(t,e,r){--e;var n=r.t=this.t+t.t-e;for(r.s=0;--n>=0;)r[n]=0
;for(n=Math.max(e-this.t,0);n<t.t;++n)r[this.t+n-e]=this.am(e-n,t[n],r,0,0,this.t+n-e);r.clamp(),r.drShiftTo(1,r)},t.prototype.modInt=function(t){if(t<=0)return 0
;var e=this.DV%t,r=this.s<0?t-1:0;if(this.t>0)if(0==e)r=this[0]%t;else for(var n=this.t-1;n>=0;--n)r=(e*r+this[n])%t;return r},t.prototype.millerRabin=function(e){
var r=this.subtract(t.ONE),n=r.getLowestSetBit();if(n<=0)return!1;var o=r.shiftRight(n);(e=e+1>>1)>E.length&&(e=E.length);for(var i=I(),a=0;a<e;++a){
i.fromInt(E[Math.floor(Math.random()*E.length)]);var s=i.modPow(o,this);if(0!=s.compareTo(t.ONE)&&0!=s.compareTo(r)){
for(var u=1;u++<n&&0!=s.compareTo(r);)if(0==(s=s.modPowInt(2,this)).compareTo(t.ONE))return!1;if(0!=s.compareTo(r))return!1}}return!0},t.prototype.square=function(){
var t=I();return this.squareTo(t),t},t.prototype.gcda=function(t,e){var r=this.s<0?this.negate():this.clone(),n=t.s<0?t.negate():t.clone();if(r.compareTo(n)<0){
var o=r;r=n,n=o}var i=r.getLowestSetBit(),a=n.getLowestSetBit();if(a<0)e(r);else{i<a&&(a=i),a>0&&(r.rShiftTo(a,r),n.rShiftTo(a,n));var s=function(){
(i=r.getLowestSetBit())>0&&r.rShiftTo(i,r),(i=n.getLowestSetBit())>0&&n.rShiftTo(i,n),r.compareTo(n)>=0?(r.subTo(n,r),r.rShiftTo(1,r)):(n.subTo(r,n),
n.rShiftTo(1,n)),r.signum()>0?setTimeout(s,0):(a>0&&n.lShiftTo(a,n),setTimeout((function(){e(n)}),0))};setTimeout(s,10)}},
t.prototype.fromNumberAsync=function(e,r,o,i){if("number"==typeof r)if(e<2)this.fromInt(1);else{this.fromNumber(e,o),
this.testBit(e-1)||this.bitwiseTo(t.ONE.shiftLeft(e-1),n,this),this.isEven()&&this.dAddOffset(1,0);var a=this,s=function(){a.dAddOffset(2,0),
a.bitLength()>e&&a.subTo(t.ONE.shiftLeft(e-1),a),a.isProbablePrime(r)?setTimeout((function(){i()}),0):setTimeout(s,0)};setTimeout(s,0)}else{var u=[],c=7&e
;u.length=1+(e>>3),r.nextBytes(u),c>0?u[0]&=(1<<c)-1:u[0]=0,this.fromString(u,256)}},t}(),j=function(){function t(){}return t.prototype.convert=function(t){return t
},t.prototype.revert=function(t){return t},t.prototype.mulTo=function(t,e,r){t.multiplyTo(e,r)},t.prototype.sqrTo=function(t,e){t.squareTo(e)},t}(),C=function(){
function t(t){this.m=t}return t.prototype.convert=function(t){return t.s<0||t.compareTo(this.m)>=0?t.mod(this.m):t},t.prototype.revert=function(t){return t},
t.prototype.reduce=function(t){t.divRemTo(this.m,null,t)},t.prototype.mulTo=function(t,e,r){t.multiplyTo(e,r),this.reduce(r)},t.prototype.sqrTo=function(t,e){
t.squareTo(e),this.reduce(e)},t}(),T=function(){function t(t){this.m=t,this.mp=t.invDigit(),this.mpl=32767&this.mp,this.mph=this.mp>>15,this.um=(1<<t.DB-15)-1,
this.mt2=2*t.t}return t.prototype.convert=function(t){var e=I();return t.abs().dlShiftTo(this.m.t,e),e.divRemTo(this.m,null,e),
t.s<0&&e.compareTo(k.ZERO)>0&&this.m.subTo(e,e),e},t.prototype.revert=function(t){var e=I();return t.copyTo(e),this.reduce(e),e},t.prototype.reduce=function(t){
for(;t.t<=this.mt2;)t[t.t++]=0;for(var e=0;e<this.m.t;++e){var r=32767&t[e],n=r*this.mpl+((r*this.mph+(t[e]>>15)*this.mpl&this.um)<<15)&t.DM
;for(t[r=e+this.m.t]+=this.m.am(0,n,t,e,0,this.m.t);t[r]>=t.DV;)t[r]-=t.DV,t[++r]++}t.clamp(),t.drShiftTo(this.m.t,t),t.compareTo(this.m)>=0&&t.subTo(this.m,t)},
t.prototype.mulTo=function(t,e,r){t.multiplyTo(e,r),this.reduce(r)},t.prototype.sqrTo=function(t,e){t.squareTo(e),this.reduce(e)},t}(),A=function(){function t(t){
this.m=t,this.r2=I(),this.q3=I(),k.ONE.dlShiftTo(2*t.t,this.r2),this.mu=this.r2.divide(t)}return t.prototype.convert=function(t){
if(t.s<0||t.t>2*this.m.t)return t.mod(this.m);if(t.compareTo(this.m)<0)return t;var e=I();return t.copyTo(e),this.reduce(e),e},t.prototype.revert=function(t){
return t},t.prototype.reduce=function(t){for(t.drShiftTo(this.m.t-1,this.r2),t.t>this.m.t+1&&(t.t=this.m.t+1,t.clamp()),
this.mu.multiplyUpperTo(this.r2,this.m.t+1,this.q3),this.m.multiplyLowerTo(this.q3,this.m.t+1,this.r2);t.compareTo(this.r2)<0;)t.dAddOffset(1,this.m.t+1)
;for(t.subTo(this.r2,t);t.compareTo(this.m)>=0;)t.subTo(this.m,t)},t.prototype.mulTo=function(t,e,r){t.multiplyTo(e,r),this.reduce(r)},
t.prototype.sqrTo=function(t,e){t.squareTo(e),this.reduce(e)},t}();function I(){return new k(null)}function L(t,e){return new k(t,e)}
"Microsoft Internet Explorer"==navigator.appName?(k.prototype.am=function(t,e,r,n,o,i){for(var a=32767&e,s=e>>15;--i>=0;){
var u=32767&this[t],c=this[t++]>>15,l=s*u+c*a;o=((u=a*u+((32767&l)<<15)+r[n]+(1073741823&o))>>>30)+(l>>>15)+s*c+(o>>>30),r[n++]=1073741823&u}return o},
_=30):"Netscape"!=navigator.appName?(k.prototype.am=function(t,e,r,n,o,i){for(;--i>=0;){var a=e*this[t++]+r[n]+o;o=Math.floor(a/67108864),r[n++]=67108863&a}return o
},_=26):(k.prototype.am=function(t,e,r,n,o,i){for(var a=16383&e,s=e>>14;--i>=0;){var u=16383&this[t],c=this[t++]>>14,l=s*u+c*a
;o=((u=a*u+((16383&l)<<14)+r[n]+o)>>28)+(l>>14)+s*c,r[n++]=268435455&u}return o},_=28),k.prototype.DB=_,k.prototype.DM=(1<<_)-1,k.prototype.DV=1<<_,
k.prototype.FV=Math.pow(2,52),k.prototype.F1=52-_,k.prototype.F2=2*_-52;var N,R,D=[];for(N="0".charCodeAt(0),R=0;R<=9;++R)D[N++]=R;for(N="a".charCodeAt(0),
R=10;R<36;++R)D[N++]=R;for(N="A".charCodeAt(0),R=10;R<36;++R)D[N++]=R;function B(t,e){var r=D[t.charCodeAt(e)];return null==r?-1:r}function F(t){var e=I()
;return e.fromInt(t),e}function M(t){var e,r=1;return 0!=(e=t>>>16)&&(t=e,r+=16),0!=(e=t>>8)&&(t=e,r+=8),0!=(e=t>>4)&&(t=e,r+=4),0!=(e=t>>2)&&(t=e,r+=2),
0!=(e=t>>1)&&(t=e,r+=1),r}k.ZERO=F(0),k.ONE=F(1);var G,V,U=function(){function t(){this.i=0,this.j=0,this.S=[]}return t.prototype.init=function(t){var e,r,n
;for(e=0;e<256;++e)this.S[e]=e;for(r=0,e=0;e<256;++e)r=r+this.S[e]+t[e%t.length]&255,n=this.S[e],this.S[e]=this.S[r],this.S[r]=n;this.i=0,this.j=0},
t.prototype.next=function(){var t;return this.i=this.i+1&255,this.j=this.j+this.S[this.i]&255,t=this.S[this.i],this.S[this.i]=this.S[this.j],this.S[this.j]=t,
this.S[t+this.S[this.i]&255]},t}(),q=null;if(null==q){q=[],V=0;var Z=void 0;if(window.crypto&&window.crypto.getRandomValues){var K=new Uint32Array(256)
;for(window.crypto.getRandomValues(K),Z=0;Z<K.length;++Z)q[V++]=255&K[Z]}var z=function(t){if(this.count=this.count||0,
this.count>=256||V>=256)window.removeEventListener?window.removeEventListener("mousemove",z,!1):window.detachEvent&&window.detachEvent("onmousemove",z);else try{
var e=t.x+t.y;q[V++]=255&e,this.count+=1}catch(t){}}
;window.addEventListener?window.addEventListener("mousemove",z,!1):window.attachEvent&&window.attachEvent("onmousemove",z)}function $(){if(null==G){
for(G=new U;V<256;){var t=Math.floor(65536*Math.random());q[V++]=255&t}for(G.init(q),V=0;V<q.length;++V)q[V]=0;V=0}return G.next()}var H=function(){function t(){}
return t.prototype.nextBytes=function(t){for(var e=0;e<t.length;++e)t[e]=$()},t}(),Y=function(){function t(){this.n=null,this.e=0,this.d=null,this.p=null,
this.q=null,this.dmp1=null,this.dmq1=null,this.coeff=null}return t.prototype.doPublic=function(t){return t.modPowInt(this.e,this.n)},
t.prototype.doPrivate=function(t){if(null==this.p||null==this.q)return t.modPow(this.d,this.n)
;for(var e=t.mod(this.p).modPow(this.dmp1,this.p),r=t.mod(this.q).modPow(this.dmq1,this.q);e.compareTo(r)<0;)e=e.add(this.p)
;return e.subtract(r).multiply(this.coeff).mod(this.p).multiply(this.q).add(r)},t.prototype.setPublic=function(t,e){
null!=t&&null!=e&&t.length>0&&e.length>0?(this.n=L(t,16),this.e=parseInt(e,16)):console.error("Invalid RSA public key")},t.prototype.encrypt=function(t){
var e=function(t,e){if(e<t.length+11)return console.error("Message too long for RSA"),null;for(var r=[],n=t.length-1;n>=0&&e>0;){var o=t.charCodeAt(n--)
;o<128?r[--e]=o:o>127&&o<2048?(r[--e]=63&o|128,r[--e]=o>>6|192):(r[--e]=63&o|128,r[--e]=o>>6&63|128,r[--e]=o>>12|224)}r[--e]=0;for(var i=new H,a=[];e>2;){
for(a[0]=0;0==a[0];)i.nextBytes(a);r[--e]=a[0]}return r[--e]=2,r[--e]=0,new k(r)}(t,this.n.bitLength()+7>>3);if(null==e)return null;var r=this.doPublic(e)
;if(null==r)return null;var n=r.toString(16);return 1&n.length?"0"+n:n},t.prototype.setPrivate=function(t,e,r){
null!=t&&null!=e&&t.length>0&&e.length>0?(this.n=L(t,16),this.e=parseInt(e,16),this.d=L(r,16)):console.error("Invalid RSA private key")},
t.prototype.setPrivateEx=function(t,e,r,n,o,i,a,s){null!=t&&null!=e&&t.length>0&&e.length>0?(this.n=L(t,16),this.e=parseInt(e,16),this.d=L(r,16),this.p=L(n,16),
this.q=L(o,16),this.dmp1=L(i,16),this.dmq1=L(a,16),this.coeff=L(s,16)):console.error("Invalid RSA private key")},t.prototype.generate=function(t,e){
var r=new H,n=t>>1;this.e=parseInt(e,16);for(var o=new k(e,16);;){for(;this.p=new k(t-n,1,r),
0!=this.p.subtract(k.ONE).gcd(o).compareTo(k.ONE)||!this.p.isProbablePrime(10););for(;this.q=new k(n,1,r),
0!=this.q.subtract(k.ONE).gcd(o).compareTo(k.ONE)||!this.q.isProbablePrime(10););if(this.p.compareTo(this.q)<=0){var i=this.p;this.p=this.q,this.q=i}
var a=this.p.subtract(k.ONE),s=this.q.subtract(k.ONE),u=a.multiply(s);if(0==u.gcd(o).compareTo(k.ONE)){this.n=this.p.multiply(this.q),this.d=o.modInverse(u),
this.dmp1=this.d.mod(a),this.dmq1=this.d.mod(s),this.coeff=this.q.modInverse(this.p);break}}},t.prototype.decrypt=function(t){var e=L(t,16),r=this.doPrivate(e)
;return null==r?null:function(t,e){for(var r=t.toByteArray(),n=0;n<r.length&&0==r[n];)++n;if(r.length-n!=e-1||2!=r[n])return null
;for(++n;0!=r[n];)if(++n>=r.length)return null;for(var o="";++n<r.length;){var i=255&r[n]
;i<128?o+=String.fromCharCode(i):i>191&&i<224?(o+=String.fromCharCode((31&i)<<6|63&r[n+1]),++n):(o+=String.fromCharCode((15&i)<<12|(63&r[n+1])<<6|63&r[n+2]),n+=2)}
return o}(r,this.n.bitLength()+7>>3)},t.prototype.generateAsync=function(t,e,r){var n=new H,o=t>>1;this.e=parseInt(e,16);var i=new k(e,16),a=this,s=function(){
var e=function(){if(a.p.compareTo(a.q)<=0){var t=a.p;a.p=a.q,a.q=t}var e=a.p.subtract(k.ONE),n=a.q.subtract(k.ONE),o=e.multiply(n)
;0==o.gcd(i).compareTo(k.ONE)?(a.n=a.p.multiply(a.q),a.d=i.modInverse(o),a.dmp1=a.d.mod(e),a.dmq1=a.d.mod(n),a.coeff=a.q.modInverse(a.p),setTimeout((function(){r()
}),0)):setTimeout(s,0)},u=function(){a.q=I(),a.q.fromNumberAsync(o,1,n,(function(){a.q.subtract(k.ONE).gcda(i,(function(t){
0==t.compareTo(k.ONE)&&a.q.isProbablePrime(10)?setTimeout(e,0):setTimeout(u,0)}))}))},c=function(){a.p=I(),a.p.fromNumberAsync(t-o,1,n,(function(){
a.p.subtract(k.ONE).gcda(i,(function(t){0==t.compareTo(k.ONE)&&a.p.isProbablePrime(10)?setTimeout(u,0):setTimeout(c,0)}))}))};setTimeout(c,0)};setTimeout(s,0)},
t.prototype.sign=function(t,e,r){var n=function(t,e){if(e<t.length+22)return console.error("Message too long for RSA"),null
;for(var r=e-t.length-6,n="",o=0;o<r;o+=2)n+="ff";return L("0001"+n+"00"+t,16)}((J[r]||"")+e(t).toString(),this.n.bitLength()/4);if(null==n)return null
;var o=this.doPrivate(n);if(null==o)return null;var i=o.toString(16);return 1&i.length?"0"+i:i},t.prototype.verify=function(t,e,r){var n=L(e,16),o=this.doPublic(n)
;return null==o?null:function(t){for(var e in J)if(J.hasOwnProperty(e)){var r=J[e],n=r.length;if(t.substr(0,n)==r)return t.substr(n)}return t
}(o.toString(16).replace(/^1f+00/,""))==r(t).toString()},t}(),J={md2:"3020300c06082a864886f70d020205000410",md5:"3020300c06082a864886f70d020505000410",
sha1:"3021300906052b0e03021a05000414",sha224:"302d300d06096086480165030402040500041c",sha256:"3031300d060960864801650304020105000420",
sha384:"3041300d060960864801650304020205000430",sha512:"3051300d060960864801650304020305000440",ripemd160:"3021300906052b2403020105000414"},W={};W.lang={
extend:function(t,e,r){if(!e||!t)throw new Error("YAHOO.lang.extend failed, please check that all dependencies are included.");var n=function(){}
;if(n.prototype=e.prototype,t.prototype=new n,t.prototype.constructor=t,t.superclass=e.prototype,
e.prototype.constructor==Object.prototype.constructor&&(e.prototype.constructor=e),r){var o;for(o in r)t.prototype[o]=r[o]
;var i=function(){},a=["toString","valueOf"];try{/MSIE/.test(navigator.userAgent)&&(i=function(t,e){for(o=0;o<a.length;o+=1){var r=a[o],n=e[r]
;"function"==typeof n&&n!=Object.prototype[r]&&(t[r]=n)}})}catch(t){}i(t.prototype,r)}}};var Q={};void 0!==Q.asn1&&Q.asn1||(Q.asn1={}),
Q.asn1.ASN1Util=new function(){this.integerToByteHex=function(t){var e=t.toString(16);return e.length%2==1&&(e="0"+e),e},
this.bigIntToMinTwosComplementsHex=function(t){var e=t.toString(16);if("-"!=e.substr(0,1))e.length%2==1?e="0"+e:e.match(/^[0-7]/)||(e="00"+e);else{
var r=e.substr(1).length;r%2==1?r+=1:e.match(/^[0-7]/)||(r+=2);for(var n="",o=0;o<r;o++)n+="f";e=new k(n,16).xor(t).add(k.ONE).toString(16).replace(/^-/,"")}return e
},this.getPEMStringFromHex=function(t,e){return hextopem(t,e)},this.newObject=function(t){
var e=Q.asn1,r=e.DERBoolean,n=e.DERInteger,o=e.DERBitString,i=e.DEROctetString,a=e.DERNull,s=e.DERObjectIdentifier,u=e.DEREnumerated,c=e.DERUTF8String,l=e.DERNumericString,f=e.DERPrintableString,h=e.DERTeletexString,p=e.DERIA5String,d=e.DERUTCTime,y=e.DERGeneralizedTime,v=e.DERSequence,g=e.DERSet,m=e.DERTaggedObject,b=e.ASN1Util.newObject,w=Object.keys(t)
;if(1!=w.length)throw"key of param shall be only one.";var _=w[0]
;if(-1==":bool:int:bitstr:octstr:null:oid:enum:utf8str:numstr:prnstr:telstr:ia5str:utctime:gentime:seq:set:tag:".indexOf(":"+_+":"))throw"undefined key: "+_
;if("bool"==_)return new r(t[_]);if("int"==_)return new n(t[_]);if("bitstr"==_)return new o(t[_]);if("octstr"==_)return new i(t[_]);if("null"==_)return new a(t[_])
;if("oid"==_)return new s(t[_]);if("enum"==_)return new u(t[_]);if("utf8str"==_)return new c(t[_]);if("numstr"==_)return new l(t[_])
;if("prnstr"==_)return new f(t[_]);if("telstr"==_)return new h(t[_]);if("ia5str"==_)return new p(t[_]);if("utctime"==_)return new d(t[_])
;if("gentime"==_)return new y(t[_]);if("seq"==_){for(var x=t[_],P=[],S=0;S<x.length;S++){var E=b(x[S]);P.push(E)}return new v({array:P})}if("set"==_){for(x=t[_],
P=[],S=0;S<x.length;S++)E=b(x[S]),P.push(E);return new g({array:P})}if("tag"==_){var O=t[_];if("[object Array]"===Object.prototype.toString.call(O)&&3==O.length){
var k=b(O[2]);return new m({tag:O[0],explicit:O[1],obj:k})}var j={};if(void 0!==O.explicit&&(j.explicit=O.explicit),void 0!==O.tag&&(j.tag=O.tag),
void 0===O.obj)throw"obj shall be specified for 'tag'.";return j.obj=b(O.obj),new m(j)}},this.jsonToASN1HEX=function(t){return this.newObject(t).getEncodedHex()}},
Q.asn1.ASN1Util.oidHexToInt=function(t){for(var e="",r=parseInt(t.substr(0,2),16),n=(e=Math.floor(r/40)+"."+r%40,""),o=2;o<t.length;o+=2){
var i=("00000000"+parseInt(t.substr(o,2),16).toString(2)).slice(-8);n+=i.substr(1,7),"0"==i.substr(0,1)&&(e=e+"."+new k(n,2).toString(10),n="")}return e},
Q.asn1.ASN1Util.oidIntToHex=function(t){var e=function(t){var e=t.toString(16);return 1==e.length&&(e="0"+e),e},r=function(t){
var r="",n=new k(t,10).toString(2),o=7-n.length%7;7==o&&(o=0);for(var i="",a=0;a<o;a++)i+="0";for(n=i+n,a=0;a<n.length-1;a+=7){var s=n.substr(a,7)
;a!=n.length-7&&(s="1"+s),r+=e(parseInt(s,2))}return r};if(!t.match(/^[0-9.]+$/))throw"malformed oid string: "+t
;var n="",o=t.split("."),i=40*parseInt(o[0])+parseInt(o[1]);n+=e(i),o.splice(0,2);for(var a=0;a<o.length;a++)n+=r(o[a]);return n},Q.asn1.ASN1Object=function(){
this.getLengthHexFromValue=function(){if(void 0===this.hV||null==this.hV)throw"this.hV is null or undefined."
;if(this.hV.length%2==1)throw"value hex must be even length: n=0,v="+this.hV;var t=this.hV.length/2,e=t.toString(16);if(e.length%2==1&&(e="0"+e),t<128)return e
;var r=e.length/2;if(r>15)throw"ASN.1 length too long to represent by 8x: n = "+t.toString(16);return(128+r).toString(16)+e},this.getEncodedHex=function(){
return(null==this.hTLV||this.isModified)&&(this.hV=this.getFreshValueHex(),this.hL=this.getLengthHexFromValue(),this.hTLV=this.hT+this.hL+this.hV,
this.isModified=!1),this.hTLV},this.getValueHex=function(){return this.getEncodedHex(),this.hV},this.getFreshValueHex=function(){return""}},
Q.asn1.DERAbstractString=function(t){Q.asn1.DERAbstractString.superclass.constructor.call(this),this.getString=function(){return this.s},this.setString=function(t){
this.hTLV=null,this.isModified=!0,this.s=t,this.hV=stohex(this.s)},this.setStringHex=function(t){this.hTLV=null,this.isModified=!0,this.s=null,this.hV=t},
this.getFreshValueHex=function(){return this.hV
},void 0!==t&&("string"==typeof t?this.setString(t):void 0!==t.str?this.setString(t.str):void 0!==t.hex&&this.setStringHex(t.hex))},
W.lang.extend(Q.asn1.DERAbstractString,Q.asn1.ASN1Object),Q.asn1.DERAbstractTime=function(t){Q.asn1.DERAbstractTime.superclass.constructor.call(this),
this.localDateToUTC=function(t){return utc=t.getTime()+6e4*t.getTimezoneOffset(),new Date(utc)},this.formatDate=function(t,e,r){
var n=this.zeroPadding,o=this.localDateToUTC(t),i=String(o.getFullYear());"utc"==e&&(i=i.substr(2,2))
;var a=i+n(String(o.getMonth()+1),2)+n(String(o.getDate()),2)+n(String(o.getHours()),2)+n(String(o.getMinutes()),2)+n(String(o.getSeconds()),2);if(!0===r){
var s=o.getMilliseconds();if(0!=s){var u=n(String(s),3);a=a+"."+(u=u.replace(/[0]+$/,""))}}return a+"Z"},this.zeroPadding=function(t,e){
return t.length>=e?t:new Array(e-t.length+1).join("0")+t},this.getString=function(){return this.s},this.setString=function(t){this.hTLV=null,this.isModified=!0,
this.s=t,this.hV=stohex(t)},this.setByDateValue=function(t,e,r,n,o,i){var a=new Date(Date.UTC(t,e-1,r,n,o,i,0));this.setByDate(a)},this.getFreshValueHex=function(){
return this.hV}},W.lang.extend(Q.asn1.DERAbstractTime,Q.asn1.ASN1Object),Q.asn1.DERAbstractStructured=function(t){
Q.asn1.DERAbstractString.superclass.constructor.call(this),this.setByASN1ObjectArray=function(t){this.hTLV=null,this.isModified=!0,this.asn1Array=t},
this.appendASN1Object=function(t){this.hTLV=null,this.isModified=!0,this.asn1Array.push(t)},this.asn1Array=new Array,
void 0!==t&&void 0!==t.array&&(this.asn1Array=t.array)},W.lang.extend(Q.asn1.DERAbstractStructured,Q.asn1.ASN1Object),Q.asn1.DERBoolean=function(){
Q.asn1.DERBoolean.superclass.constructor.call(this),this.hT="01",this.hTLV="0101ff"},W.lang.extend(Q.asn1.DERBoolean,Q.asn1.ASN1Object),
Q.asn1.DERInteger=function(t){Q.asn1.DERInteger.superclass.constructor.call(this),this.hT="02",this.setByBigInteger=function(t){this.hTLV=null,this.isModified=!0,
this.hV=Q.asn1.ASN1Util.bigIntToMinTwosComplementsHex(t)},this.setByInteger=function(t){var e=new k(String(t),10);this.setByBigInteger(e)},
this.setValueHex=function(t){this.hV=t},this.getFreshValueHex=function(){return this.hV},
void 0!==t&&(void 0!==t.bigint?this.setByBigInteger(t.bigint):void 0!==t.int?this.setByInteger(t.int):"number"==typeof t?this.setByInteger(t):void 0!==t.hex&&this.setValueHex(t.hex))
},W.lang.extend(Q.asn1.DERInteger,Q.asn1.ASN1Object),Q.asn1.DERBitString=function(t){if(void 0!==t&&void 0!==t.obj){var e=Q.asn1.ASN1Util.newObject(t.obj)
;t.hex="00"+e.getEncodedHex()}Q.asn1.DERBitString.superclass.constructor.call(this),this.hT="03",this.setHexValueIncludingUnusedBits=function(t){this.hTLV=null,
this.isModified=!0,this.hV=t},this.setUnusedBitsAndHexValue=function(t,e){if(t<0||7<t)throw"unused bits shall be from 0 to 7: u = "+t;var r="0"+t;this.hTLV=null,
this.isModified=!0,this.hV=r+e},this.setByBinaryString=function(t){var e=8-(t=t.replace(/0+$/,"")).length%8;8==e&&(e=0);for(var r=0;r<=e;r++)t+="0";var n=""
;for(r=0;r<t.length-1;r+=8){var o=t.substr(r,8),i=parseInt(o,2).toString(16);1==i.length&&(i="0"+i),n+=i}this.hTLV=null,this.isModified=!0,this.hV="0"+e+n},
this.setByBooleanArray=function(t){for(var e="",r=0;r<t.length;r++)1==t[r]?e+="1":e+="0";this.setByBinaryString(e)},this.newFalseArray=function(t){
for(var e=new Array(t),r=0;r<t;r++)e[r]=!1;return e},this.getFreshValueHex=function(){return this.hV},
void 0!==t&&("string"==typeof t&&t.toLowerCase().match(/^[0-9a-f]+$/)?this.setHexValueIncludingUnusedBits(t):void 0!==t.hex?this.setHexValueIncludingUnusedBits(t.hex):void 0!==t.bin?this.setByBinaryString(t.bin):void 0!==t.array&&this.setByBooleanArray(t.array))
},W.lang.extend(Q.asn1.DERBitString,Q.asn1.ASN1Object),Q.asn1.DEROctetString=function(t){if(void 0!==t&&void 0!==t.obj){var e=Q.asn1.ASN1Util.newObject(t.obj)
;t.hex=e.getEncodedHex()}Q.asn1.DEROctetString.superclass.constructor.call(this,t),this.hT="04"},W.lang.extend(Q.asn1.DEROctetString,Q.asn1.DERAbstractString),
Q.asn1.DERNull=function(){Q.asn1.DERNull.superclass.constructor.call(this),this.hT="05",this.hTLV="0500"},W.lang.extend(Q.asn1.DERNull,Q.asn1.ASN1Object),
Q.asn1.DERObjectIdentifier=function(t){var e=function(t){var e=t.toString(16);return 1==e.length&&(e="0"+e),e},r=function(t){
var r="",n=new k(t,10).toString(2),o=7-n.length%7;7==o&&(o=0);for(var i="",a=0;a<o;a++)i+="0";for(n=i+n,a=0;a<n.length-1;a+=7){var s=n.substr(a,7)
;a!=n.length-7&&(s="1"+s),r+=e(parseInt(s,2))}return r};Q.asn1.DERObjectIdentifier.superclass.constructor.call(this),this.hT="06",this.setValueHex=function(t){
this.hTLV=null,this.isModified=!0,this.s=null,this.hV=t},this.setValueOidString=function(t){if(!t.match(/^[0-9.]+$/))throw"malformed oid string: "+t
;var n="",o=t.split("."),i=40*parseInt(o[0])+parseInt(o[1]);n+=e(i),o.splice(0,2);for(var a=0;a<o.length;a++)n+=r(o[a]);this.hTLV=null,this.isModified=!0,
this.s=null,this.hV=n},this.setValueName=function(t){var e=Q.asn1.x509.OID.name2oid(t);if(""===e)throw"DERObjectIdentifier oidName undefined: "+t
;this.setValueOidString(e)},this.getFreshValueHex=function(){return this.hV
},void 0!==t&&("string"==typeof t?t.match(/^[0-2].[0-9.]+$/)?this.setValueOidString(t):this.setValueName(t):void 0!==t.oid?this.setValueOidString(t.oid):void 0!==t.hex?this.setValueHex(t.hex):void 0!==t.name&&this.setValueName(t.name))
},W.lang.extend(Q.asn1.DERObjectIdentifier,Q.asn1.ASN1Object),Q.asn1.DEREnumerated=function(t){Q.asn1.DEREnumerated.superclass.constructor.call(this),this.hT="0a",
this.setByBigInteger=function(t){this.hTLV=null,this.isModified=!0,this.hV=Q.asn1.ASN1Util.bigIntToMinTwosComplementsHex(t)},this.setByInteger=function(t){
var e=new k(String(t),10);this.setByBigInteger(e)},this.setValueHex=function(t){this.hV=t},this.getFreshValueHex=function(){return this.hV},
void 0!==t&&(void 0!==t.int?this.setByInteger(t.int):"number"==typeof t?this.setByInteger(t):void 0!==t.hex&&this.setValueHex(t.hex))},
W.lang.extend(Q.asn1.DEREnumerated,Q.asn1.ASN1Object),Q.asn1.DERUTF8String=function(t){Q.asn1.DERUTF8String.superclass.constructor.call(this,t),this.hT="0c"},
W.lang.extend(Q.asn1.DERUTF8String,Q.asn1.DERAbstractString),Q.asn1.DERNumericString=function(t){Q.asn1.DERNumericString.superclass.constructor.call(this,t),
this.hT="12"},W.lang.extend(Q.asn1.DERNumericString,Q.asn1.DERAbstractString),Q.asn1.DERPrintableString=function(t){
Q.asn1.DERPrintableString.superclass.constructor.call(this,t),this.hT="13"},W.lang.extend(Q.asn1.DERPrintableString,Q.asn1.DERAbstractString),
Q.asn1.DERTeletexString=function(t){Q.asn1.DERTeletexString.superclass.constructor.call(this,t),this.hT="14"},
W.lang.extend(Q.asn1.DERTeletexString,Q.asn1.DERAbstractString),Q.asn1.DERIA5String=function(t){Q.asn1.DERIA5String.superclass.constructor.call(this,t),this.hT="16"
},W.lang.extend(Q.asn1.DERIA5String,Q.asn1.DERAbstractString),Q.asn1.DERUTCTime=function(t){Q.asn1.DERUTCTime.superclass.constructor.call(this,t),this.hT="17",
this.setByDate=function(t){this.hTLV=null,this.isModified=!0,this.date=t,this.s=this.formatDate(this.date,"utc"),this.hV=stohex(this.s)},
this.getFreshValueHex=function(){return void 0===this.date&&void 0===this.s&&(this.date=new Date,this.s=this.formatDate(this.date,"utc"),this.hV=stohex(this.s)),
this.hV
},void 0!==t&&(void 0!==t.str?this.setString(t.str):"string"==typeof t&&t.match(/^[0-9]{12}Z$/)?this.setString(t):void 0!==t.hex?this.setStringHex(t.hex):void 0!==t.date&&this.setByDate(t.date))
},W.lang.extend(Q.asn1.DERUTCTime,Q.asn1.DERAbstractTime),Q.asn1.DERGeneralizedTime=function(t){Q.asn1.DERGeneralizedTime.superclass.constructor.call(this,t),
this.hT="18",this.withMillis=!1,this.setByDate=function(t){this.hTLV=null,this.isModified=!0,this.date=t,this.s=this.formatDate(this.date,"gen",this.withMillis),
this.hV=stohex(this.s)},this.getFreshValueHex=function(){return void 0===this.date&&void 0===this.s&&(this.date=new Date,
this.s=this.formatDate(this.date,"gen",this.withMillis),this.hV=stohex(this.s)),this.hV},
void 0!==t&&(void 0!==t.str?this.setString(t.str):"string"==typeof t&&t.match(/^[0-9]{14}Z$/)?this.setString(t):void 0!==t.hex?this.setStringHex(t.hex):void 0!==t.date&&this.setByDate(t.date),
!0===t.millis&&(this.withMillis=!0))},W.lang.extend(Q.asn1.DERGeneralizedTime,Q.asn1.DERAbstractTime),Q.asn1.DERSequence=function(t){
Q.asn1.DERSequence.superclass.constructor.call(this,t),this.hT="30",this.getFreshValueHex=function(){
for(var t="",e=0;e<this.asn1Array.length;e++)t+=this.asn1Array[e].getEncodedHex();return this.hV=t,this.hV}},
W.lang.extend(Q.asn1.DERSequence,Q.asn1.DERAbstractStructured),Q.asn1.DERSet=function(t){Q.asn1.DERSet.superclass.constructor.call(this,t),this.hT="31",
this.sortFlag=!0,this.getFreshValueHex=function(){for(var t=new Array,e=0;e<this.asn1Array.length;e++){var r=this.asn1Array[e];t.push(r.getEncodedHex())}
return 1==this.sortFlag&&t.sort(),this.hV=t.join(""),this.hV},void 0!==t&&void 0!==t.sortflag&&0==t.sortflag&&(this.sortFlag=!1)},
W.lang.extend(Q.asn1.DERSet,Q.asn1.DERAbstractStructured),Q.asn1.DERTaggedObject=function(t){Q.asn1.DERTaggedObject.superclass.constructor.call(this),this.hT="a0",
this.hV="",this.isExplicit=!0,this.asn1Object=null,this.setASN1Object=function(t,e,r){this.hT=e,this.isExplicit=t,this.asn1Object=r,
this.isExplicit?(this.hV=this.asn1Object.getEncodedHex(),this.hTLV=null,this.isModified=!0):(this.hV=null,this.hTLV=r.getEncodedHex(),
this.hTLV=this.hTLV.replace(/^../,e),this.isModified=!1)},this.getFreshValueHex=function(){return this.hV},void 0!==t&&(void 0!==t.tag&&(this.hT=t.tag),
void 0!==t.explicit&&(this.isExplicit=t.explicit),void 0!==t.obj&&(this.asn1Object=t.obj,this.setASN1Object(this.isExplicit,this.hT,this.asn1Object)))},
W.lang.extend(Q.asn1.DERTaggedObject,Q.asn1.ASN1Object);var X=function(t){function e(r){var n=t.call(this)||this
;return r&&("string"==typeof r?n.parseKey(r):(e.hasPrivateKeyProperty(r)||e.hasPublicKeyProperty(r))&&n.parsePropertiesFrom(r)),n}return function(t,e){function r(){
this.constructor=t}p(t,e),t.prototype=null===e?Object.create(e):(r.prototype=e.prototype,new r)}(e,t),e.prototype.parseKey=function(t){try{
var e=0,r=0,n=/^\s*(?:[0-9A-Fa-f][0-9A-Fa-f]\s*)+$/.test(t)?d(t):y.unarmor(t),o=P.decode(n);if(3===o.sub.length&&(o=o.sub[2].sub[0]),9===o.sub.length){
e=o.sub[1].getHexStringValue(),this.n=L(e,16),r=o.sub[2].getHexStringValue(),this.e=parseInt(r,16);var i=o.sub[3].getHexStringValue();this.d=L(i,16)
;var a=o.sub[4].getHexStringValue();this.p=L(a,16);var s=o.sub[5].getHexStringValue();this.q=L(s,16);var u=o.sub[6].getHexStringValue();this.dmp1=L(u,16)
;var c=o.sub[7].getHexStringValue();this.dmq1=L(c,16);var l=o.sub[8].getHexStringValue();this.coeff=L(l,16)}else{if(2!==o.sub.length)return!1;var f=o.sub[1].sub[0]
;e=f.sub[0].getHexStringValue(),this.n=L(e,16),r=f.sub[1].getHexStringValue(),this.e=parseInt(r,16)}return!0}catch(t){return!1}},
e.prototype.getPrivateBaseKey=function(){var t={array:[new Q.asn1.DERInteger({int:0}),new Q.asn1.DERInteger({bigint:this.n}),new Q.asn1.DERInteger({int:this.e
}),new Q.asn1.DERInteger({bigint:this.d}),new Q.asn1.DERInteger({bigint:this.p}),new Q.asn1.DERInteger({bigint:this.q}),new Q.asn1.DERInteger({bigint:this.dmp1
}),new Q.asn1.DERInteger({bigint:this.dmq1}),new Q.asn1.DERInteger({bigint:this.coeff})]};return new Q.asn1.DERSequence(t).getEncodedHex()},
e.prototype.getPrivateBaseKeyB64=function(){return c(this.getPrivateBaseKey())},e.prototype.getPublicBaseKey=function(){var t=new Q.asn1.DERSequence({
array:[new Q.asn1.DERObjectIdentifier({oid:"1.2.840.113549.1.1.1"}),new Q.asn1.DERNull]}),e=new Q.asn1.DERSequence({array:[new Q.asn1.DERInteger({bigint:this.n
}),new Q.asn1.DERInteger({int:this.e})]}),r=new Q.asn1.DERBitString({hex:"00"+e.getEncodedHex()});return new Q.asn1.DERSequence({array:[t,r]}).getEncodedHex()},
e.prototype.getPublicBaseKeyB64=function(){return c(this.getPublicBaseKey())},e.wordwrap=function(t,e){if(!t)return t
;var r="(.{1,"+(e=e||64)+"})( +|$\n?)|(.{1,"+e+"})";return t.match(RegExp(r,"g")).join("\n")},e.prototype.getPrivateKey=function(){
var t="-----BEGIN RSA PRIVATE KEY-----\n";return t+=e.wordwrap(this.getPrivateBaseKeyB64())+"\n",t+="-----END RSA PRIVATE KEY-----"},
e.prototype.getPublicKey=function(){var t="-----BEGIN PUBLIC KEY-----\n";return t+=e.wordwrap(this.getPublicBaseKeyB64())+"\n",t+="-----END PUBLIC KEY-----"},
e.hasPublicKeyProperty=function(t){return(t=t||{}).hasOwnProperty("n")&&t.hasOwnProperty("e")},e.hasPrivateKeyProperty=function(t){
return(t=t||{}).hasOwnProperty("n")&&t.hasOwnProperty("e")&&t.hasOwnProperty("d")&&t.hasOwnProperty("p")&&t.hasOwnProperty("q")&&t.hasOwnProperty("dmp1")&&t.hasOwnProperty("dmq1")&&t.hasOwnProperty("coeff")
},e.prototype.parsePropertiesFrom=function(t){this.n=t.n,this.e=t.e,t.hasOwnProperty("d")&&(this.d=t.d,this.p=t.p,this.q=t.q,this.dmp1=t.dmp1,this.dmq1=t.dmq1,
this.coeff=t.coeff)},e}(Y),tt=function(){function t(t){t=t||{},this.default_key_size=parseInt(t.default_key_size,10)||1024,
this.default_public_exponent=t.default_public_exponent||"010001",this.log=t.log||!1,this.key=null}return t.prototype.setKey=function(t){
this.log&&this.key&&console.warn("A key was already set, overriding existing."),this.key=new X(t)},t.prototype.setPrivateKey=function(t){this.setKey(t)},
t.prototype.setPublicKey=function(t){this.setKey(t)},t.prototype.decrypt=function(t){try{return this.getKey().decrypt(l(t))}catch(t){return!1}},
t.prototype.encrypt=function(t){try{return c(this.getKey().encrypt(t))}catch(t){return!1}},t.prototype.sign=function(t,e,r){try{return c(this.getKey().sign(t,e,r))
}catch(t){return!1}},t.prototype.verify=function(t,e,r){try{return this.getKey().verify(t,l(e),r)}catch(t){return!1}},t.prototype.getKey=function(t){if(!this.key){
if(this.key=new X,t&&"[object Function]"==={}.toString.call(t))return void this.key.generateAsync(this.default_key_size,this.default_public_exponent,t)
;this.key.generate(this.default_key_size,this.default_public_exponent)}return this.key},t.prototype.getPrivateKey=function(){return this.getKey().getPrivateKey()},
t.prototype.getPrivateKeyB64=function(){return this.getKey().getPrivateBaseKeyB64()},t.prototype.getPublicKey=function(){return this.getKey().getPublicKey()},
t.prototype.getPublicKeyB64=function(){return this.getKey().getPublicBaseKeyB64()},t.version="3.0.0-rc.1",t}();window.JSEncrypt=tt,t.JSEncrypt=tt,t.default=tt,
Object.defineProperty(t,"__esModule",{value:!0})},"object"===a(e)?i(e):(n=[e],void 0===(o="function"==typeof(r=i)?r.apply(e,n):r)||(t.exports=o))},60667:(t,e)=>{
"use strict";Object.defineProperty(e,"__esModule",{value:!0}),e.parameterSerializer=void 0,e.parameterSerializer=function(){
var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{};return t["serialize-ids-as-strings"]=!0,Object.keys(t).filter((function(e){
return t[e]&&0!==t[e].length})).map((function(e){return"".concat(e,"=").concat(encodeURIComponent(t[e]))})).join("&")}},60877:(t,e)=>{"use strict"
;Object.defineProperty(e,"__esModule",{value:!0})},62599:(t,e,r)=>{function n(t){return n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){
return typeof t}:function(t){return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},n(t)}
var o=null,i=/(?:_|\\u005[Ff])(?:_|\\u005[Ff])(?:p|\\u0070)(?:r|\\u0072)(?:o|\\u006[Ff])(?:t|\\u0074)(?:o|\\u006[Ff])(?:_|\\u005[Ff])(?:_|\\u005[Ff])/,a=/(?:c|\\u0063)(?:o|\\u006[Ff])(?:n|\\u006[Ee])(?:s|\\u0073)(?:t|\\u0074)(?:r|\\u0072)(?:u|\\u0075)(?:c|\\u0063)(?:t|\\u0074)(?:o|\\u006[Ff])(?:r|\\u0072)/
;t.exports=function(t){"use strict";var e={strict:!1,storeAsString:!1,alwaysParseAsBig:!1,useNativeBigInt:!1,protoAction:"error",constructorAction:"error"}
;if(null!=t){if(!0===t.strict&&(e.strict=!0),!0===t.storeAsString&&(e.storeAsString=!0),e.alwaysParseAsBig=!0===t.alwaysParseAsBig&&t.alwaysParseAsBig,
e.useNativeBigInt=!0===t.useNativeBigInt&&t.useNativeBigInt,void 0!==t.constructorAction){
if("error"!==t.constructorAction&&"ignore"!==t.constructorAction&&"preserve"!==t.constructorAction)throw new Error('Incorrect value for constructorAction option, must be "error", "ignore" or undefined but passed '.concat(t.constructorAction))
;e.constructorAction=t.constructorAction}if(void 0!==t.protoAction){
if("error"!==t.protoAction&&"ignore"!==t.protoAction&&"preserve"!==t.protoAction)throw new Error('Incorrect value for protoAction option, must be "error", "ignore" or undefined but passed '.concat(t.protoAction))
;e.protoAction=t.protoAction}}var s,u,c,l,f={'"':'"',"\\":"\\","/":"/",b:"\b",f:"\f",n:"\n",r:"\r",t:"\t"},h=function(t){throw{name:"SyntaxError",message:t,at:s,
text:c}},p=function(t){return t&&t!==u&&h("Expected '"+t+"' instead of '"+u+"'"),u=c.charAt(s),s+=1,u},d=function(){var t,n="";for("-"===u&&(n="-",
p("-"));u>="0"&&u<="9";)n+=u,p();if("."===u)for(n+=".";p()&&u>="0"&&u<="9";)n+=u;if("e"===u||"E"===u)for(n+=u,p(),"-"!==u&&"+"!==u||(n+=u,p());u>="0"&&u<="9";)n+=u,
p()
;if(t=+n,isFinite(t))return null==o&&(o=r(73769)),n.length>15?e.storeAsString?n:e.useNativeBigInt?BigInt(n):new o(n):e.alwaysParseAsBig?e.useNativeBigInt?BigInt(t):new o(t):t
;h("Bad number")},y=function(){var t,e,r,n="";if('"'===u)for(var o=s;p();){if('"'===u)return s-1>o&&(n+=c.substring(o,s-1)),p(),n;if("\\"===u){
if(s-1>o&&(n+=c.substring(o,s-1)),p(),"u"===u){for(r=0,e=0;e<4&&(t=parseInt(p(),16),isFinite(t));e+=1)r=16*r+t;n+=String.fromCharCode(r)}else{
if("string"!=typeof f[u])break;n+=f[u]}o=s}}h("Bad string")},v=function(){for(;u&&u<=" ";)p()},g=function(){var t=[];if("["===u){if(p("["),v(),"]"===u)return p("]"),
t;for(;u;){if(t.push(l()),v(),"]"===u)return p("]"),t;p(","),v()}}h("Bad array")},m=function(){var t,r=Object.create(null);if("{"===u){if(p("{"),v(),
"}"===u)return p("}"),r;for(;u;){if(t=y(),v(),p(":"),!0===e.strict&&Object.hasOwnProperty.call(r,t)&&h('Duplicate key "'+t+'"'),
!0===i.test(t)?"error"===e.protoAction?h("Object contains forbidden prototype property"):"ignore"===e.protoAction?l():r[t]=l():!0===a.test(t)?"error"===e.constructorAction?h("Object contains forbidden constructor property"):"ignore"===e.constructorAction?l():r[t]=l():r[t]=l(),
v(),"}"===u)return p("}"),r;p(","),v()}}h("Bad object")};return l=function(){switch(v(),u){case"{":return m();case"[":return g();case'"':return y();case"-":
return d();default:return u>="0"&&u<="9"?d():function(){switch(u){case"t":return p("t"),p("r"),p("u"),p("e"),!0;case"f":return p("f"),p("a"),p("l"),p("s"),p("e"),!1
;case"n":return p("n"),p("u"),p("l"),p("l"),null}h("Unexpected '"+u+"'")}()}},function(t,e){var r;return c=t+"",s=0,u=" ",r=l(),v(),u&&h("Syntax error"),
"function"==typeof e?function t(r,o){var i,a=r[o];return a&&"object"===n(a)&&Object.keys(a).forEach((function(e){void 0!==(i=t(a,e))?a[e]=i:delete a[e]})),
e.call(r,o,a)}({"":r},""):r}}},62941:(t,e)=>{"use strict";function r(t){return r="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){
return typeof t}:function(t){return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},r(t)}function n(t,e){
for(var r=0;r<e.length;r++){var n=e[r];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,o(n.key),n)}}
function o(t){var e=function(t,e){if("object"!=r(t)||!t)return t;var n=t[Symbol.toPrimitive];if(void 0!==n){var o=n.call(t,e||"default");if("object"!=r(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==r(e)?e:e+""}
function i(t,e,n){return e=c(e),function(t,e){if(e&&("object"==r(e)||"function"==typeof e))return e
;if(void 0!==e)throw new TypeError("Derived constructors may only return object or undefined");return function(t){
if(void 0===t)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return t}(t)
}(t,s()?Reflect.construct(e,n||[],c(t).constructor):e.apply(t,n))}function a(t){var e="function"==typeof Map?new Map:void 0;return a=function(t){
if(null===t||!function(t){try{return-1!==Function.toString.call(t).indexOf("[native code]")}catch(e){return"function"==typeof t}}(t))return t
;if("function"!=typeof t)throw new TypeError("Super expression must either be null or a function");if(void 0!==e){if(e.has(t))return e.get(t);e.set(t,r)}
function r(){return function(t,e,r){if(s())return Reflect.construct.apply(null,arguments);var n=[null];n.push.apply(n,e);var o=new(t.bind.apply(t,n))
;return r&&u(o,r.prototype),o}(t,arguments,c(this).constructor)}return r.prototype=Object.create(t.prototype,{constructor:{value:r,enumerable:!1,writable:!0,
configurable:!0}}),u(r,t)},a(t)}function s(){try{var t=!Boolean.prototype.valueOf.call(Reflect.construct(Boolean,[],(function(){})))}catch(t){}return(s=function(){
return!!t})()}function u(t,e){return u=Object.setPrototypeOf?Object.setPrototypeOf.bind():function(t,e){return t.__proto__=e,t},u(t,e)}function c(t){
return c=Object.setPrototypeOf?Object.getPrototypeOf.bind():function(t){return t.__proto__||Object.getPrototypeOf(t)},c(t)}var l
;Object.defineProperty(e,"__esModule",{value:!0}),e.ConfluenceClientError=e.ErrorCode=void 0,function(t){t.BAD_REQUEST="BAD_REQUEST",t.NOT_FOUND="NOT_FOUND",
t.INTERNAL="INTERNAL",t.UNKNOWN="UNKNOWN",t.UNSUPPORTED_OPERATION="UNSUPPORTED_OPERATION",t.EMPTY_RESPONSE="EMPTY_RESPONSE"}(l=e.ErrorCode||(e.ErrorCode={}))
;var f=function(t){function e(t,r){var n;return function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,e),
(n=i(this,e,[t])).statusCodeMap=new Map([[400,l.BAD_REQUEST],[404,l.NOT_FOUND],[500,l.INTERNAL]]),n.name="ConfluenceClientError",n.title=t,n.cause=r,n}
return function(t,e){if("function"!=typeof e&&null!==e)throw new TypeError("Super expression must either be null or a function")
;t.prototype=Object.create(e&&e.prototype,{constructor:{value:t,writable:!0,configurable:!0}}),Object.defineProperty(t,"prototype",{writable:!1}),e&&u(t,e)}(e,t),
r=e,(o=[{key:"withStatus",value:function(t,e){return this.status=t,e?(this.code=e,this):(this.setErrorCode(t),this)}},{key:"setErrorCode",value:function(t){
this.code=this.statusCodeMap.get(t)||l.UNKNOWN}}])&&n(r.prototype,o),a&&n(r,a),Object.defineProperty(r,"prototype",{writable:!1}),r;var r,o,a}(a(Error))
;e.ConfluenceClientError=f},64185:(t,e)=>{"use strict";Object.defineProperty(e,"__esModule",{value:!0}),e.ConfluenceCustomContentSortOrder=void 0,function(t){
t.Id="id",t.ValueId="-id",t.CreatedDate="created-date",t.ValueCreatedDate="-created-date",t.ModifiedDate="modified-date",t.ValueModifiedDate="-modified-date",
t.Title="title",t.ValueTitle="-title"}(e.ConfluenceCustomContentSortOrder||(e.ConfluenceCustomContentSortOrder={}))},65994:(t,e)=>{"use strict"
;Object.defineProperty(e,"__esModule",{value:!0})},67838:(t,e)=>{"use strict";Object.defineProperty(e,"__esModule",{value:!0})},71762:(t,e)=>{"use strict"
;Object.defineProperty(e,"__esModule",{value:!0})},73769:function(t,e,r){var n;function o(t){
return o="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},o(t)}!function(){"use strict"
;var i,a=/^-?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i,s=Math.ceil,u=Math.floor,c="[BigNumber Error] ",l=c+"Number primitive has more than 15 significant digits: ",f=1e14,h=14,p=9007199254740991,d=[1,10,100,1e3,1e4,1e5,1e6,1e7,1e8,1e9,1e10,1e11,1e12,1e13],y=1e7,v=1e9
;function g(t){var e=0|t;return t>0||t===e?e:e-1}function m(t){for(var e,r,n=1,o=t.length,i=t[0]+"";n<o;){for(e=t[n++]+"",r=h-e.length;r--;e="0"+e);i+=e}
for(o=i.length;48===i.charCodeAt(--o););return i.slice(0,o+1||1)}function b(t,e){var r,n,o=t.c,i=e.c,a=t.s,s=e.s,u=t.e,c=e.e;if(!a||!s)return null;if(r=o&&!o[0],
n=i&&!i[0],r||n)return r?n?0:-s:a;if(a!=s)return a;if(r=a<0,n=u==c,!o||!i)return n?0:!o^r?1:-1;if(!n)return u>c^r?1:-1;for(s=(u=o.length)<(c=i.length)?u:c,
a=0;a<s;a++)if(o[a]!=i[a])return o[a]>i[a]^r?1:-1;return u==c?0:u>c^r?1:-1}function w(t,e,r,n){
if(t<e||t>r||t!==u(t))throw Error(c+(n||"Argument")+("number"==typeof t?t<e||t>r?" out of range: ":" not an integer: ":" not a primitive number: ")+String(t))}
function _(t){var e=t.c.length-1;return g(t.e/h)==e&&t.c[e]%2!=0}function x(t,e){return(t.length>1?t.charAt(0)+"."+t.slice(1):t)+(e<0?"e":"e+")+e}function P(t,e,r){
var n,o;if(e<0){for(o=r+".";++e;o+=r);t=o+t}else if(++e>(n=t.length)){for(o=r,e-=n;--e;o+=r);t+=o}else e<n&&(t=t.slice(0,e)+"."+t.slice(e));return t}i=function t(e){
var r,n,i,S,E,O,k,j,C,T,A=K.prototype={constructor:K,toString:null,valueOf:null},I=new K(1),L=20,N=4,R=-7,D=21,B=-1e7,F=1e7,M=!1,G=1,V=0,U={prefix:"",groupSize:3,
secondaryGroupSize:0,groupSeparator:",",decimalSeparator:".",fractionGroupSize:0,fractionGroupSeparator:" ",suffix:""},q="0123456789abcdefghijklmnopqrstuvwxyz",Z=!0
;function K(t,e){var r,o,s,c,f,d,y,v,g=this;if(!(g instanceof K))return new K(t,e);if(null==e){if(t&&!0===t._isBigNumber)return g.s=t.s,
void(!t.c||t.e>F?g.c=g.e=null:t.e<B?g.c=[g.e=0]:(g.e=t.e,g.c=t.c.slice()));if((d="number"==typeof t)&&0*t==0){if(g.s=1/t<0?(t=-t,-1):1,t===~~t){for(c=0,
f=t;f>=10;f/=10,c++);return void(c>F?g.c=g.e=null:(g.e=c,g.c=[t]))}v=String(t)}else{if(!a.test(v=String(t)))return i(g,v,d);g.s=45==v.charCodeAt(0)?(v=v.slice(1),
-1):1}(c=v.indexOf("."))>-1&&(v=v.replace(".","")),(f=v.search(/e/i))>0?(c<0&&(c=f),c+=+v.slice(f+1),v=v.substring(0,f)):c<0&&(c=v.length)}else{
if(w(e,2,q.length,"Base"),10==e&&Z)return Y(g=new K(t),L+g.e+1,N);if(v=String(t),d="number"==typeof t){if(0*t!=0)return i(g,v,d,e);if(g.s=1/t<0?(v=v.slice(1),-1):1,
K.DEBUG&&v.replace(/^0\.0*|\./,"").length>15)throw Error(l+t)}else g.s=45===v.charCodeAt(0)?(v=v.slice(1),-1):1;for(r=q.slice(0,e),c=f=0,
y=v.length;f<y;f++)if(r.indexOf(o=v.charAt(f))<0){if("."==o){if(f>c){c=y;continue}
}else if(!s&&(v==v.toUpperCase()&&(v=v.toLowerCase())||v==v.toLowerCase()&&(v=v.toUpperCase()))){s=!0,f=-1,c=0;continue}return i(g,String(t),d,e)}d=!1,
(c=(v=n(v,e,10,g.s)).indexOf("."))>-1?v=v.replace(".",""):c=v.length}for(f=0;48===v.charCodeAt(f);f++);for(y=v.length;48===v.charCodeAt(--y););if(v=v.slice(f,++y)){
if(y-=f,d&&K.DEBUG&&y>15&&(t>p||t!==u(t)))throw Error(l+g.s*t);if((c=c-f-1)>F)g.c=g.e=null;else if(c<B)g.c=[g.e=0];else{if(g.e=c,g.c=[],f=(c+1)%h,c<0&&(f+=h),f<y){
for(f&&g.c.push(+v.slice(0,f)),y-=h;f<y;)g.c.push(+v.slice(f,f+=h));f=h-(v=v.slice(f)).length}else f-=y;for(;f--;v+="0");g.c.push(+v)}}else g.c=[g.e=0]}
function z(t,e,r,n){var o,i,a,s,u;if(null==r?r=N:w(r,0,8),!t.c)return t.toString();if(o=t.c[0],a=t.e,null==e)u=m(t.c),
u=1==n||2==n&&(a<=R||a>=D)?x(u,a):P(u,a,"0");else if(i=(t=Y(new K(t),e,r)).e,s=(u=m(t.c)).length,1==n||2==n&&(e<=i||i<=R)){for(;s<e;u+="0",s++);u=x(u,i)
}else if(e-=a,u=P(u,i,"0"),i+1>s){if(--e>0)for(u+=".";e--;u+="0");}else if((e+=i-s)>0)for(i+1==s&&(u+=".");e--;u+="0");return t.s<0&&o?"-"+u:u}function $(t,e){
for(var r,n,o=1,i=new K(t[0]);o<t.length;o++)(!(n=new K(t[o])).s||(r=b(i,n))===e||0===r&&i.s===e)&&(i=n);return i}function H(t,e,r){
for(var n=1,o=e.length;!e[--o];e.pop());for(o=e[0];o>=10;o/=10,n++);return(r=n+r*h-1)>F?t.c=t.e=null:r<B?t.c=[t.e=0]:(t.e=r,t.c=e),t}function Y(t,e,r,n){
var o,i,a,c,l,p,y,v=t.c,g=d;if(v){t:{for(o=1,c=v[0];c>=10;c/=10,o++);if((i=e-o)<0)i+=h,a=e,l=v[p=0],y=u(l/g[o-a-1]%10);else if((p=s((i+1)/h))>=v.length){
if(!n)break t;for(;v.length<=p;v.push(0));l=y=0,o=1,a=(i%=h)-h+1}else{for(l=c=v[p],o=1;c>=10;c/=10,o++);y=(a=(i%=h)-h+o)<0?0:u(l/g[o-a-1]%10)}
if(n=n||e<0||null!=v[p+1]||(a<0?l:l%g[o-a-1]),n=r<4?(y||n)&&(0==r||r==(t.s<0?3:2)):y>5||5==y&&(4==r||n||6==r&&(i>0?a>0?l/g[o-a]:0:v[p-1])%10&1||r==(t.s<0?8:7)),
e<1||!v[0])return v.length=0,n?(e-=t.e+1,v[0]=g[(h-e%h)%h],t.e=-e||0):v[0]=t.e=0,t;if(0==i?(v.length=p,c=1,p--):(v.length=p+1,c=g[h-i],
v[p]=a>0?u(l/g[o-a]%g[a])*c:0),n)for(;;){if(0==p){for(i=1,a=v[0];a>=10;a/=10,i++);for(a=v[0]+=c,c=1;a>=10;a/=10,c++);i!=c&&(t.e++,v[0]==f&&(v[0]=1));break}
if(v[p]+=c,v[p]!=f)break;v[p--]=0,c=1}for(i=v.length;0===v[--i];v.pop());}t.e>F?t.c=t.e=null:t.e<B&&(t.c=[t.e=0])}return t}function J(t){var e,r=t.e
;return null===r?t.toString():(e=m(t.c),e=r<=R||r>=D?x(e,r):P(e,r,"0"),t.s<0?"-"+e:e)}return K.clone=t,K.ROUND_UP=0,K.ROUND_DOWN=1,K.ROUND_CEIL=2,K.ROUND_FLOOR=3,
K.ROUND_HALF_UP=4,K.ROUND_HALF_DOWN=5,K.ROUND_HALF_EVEN=6,K.ROUND_HALF_CEIL=7,K.ROUND_HALF_FLOOR=8,K.EUCLID=9,K.config=K.set=function(t){var e,r;if(null!=t){
if("object"!=o(t))throw Error(c+"Object expected: "+t);if(t.hasOwnProperty(e="DECIMAL_PLACES")&&(w(r=t[e],0,v,e),L=r),
t.hasOwnProperty(e="ROUNDING_MODE")&&(w(r=t[e],0,8,e),N=r),t.hasOwnProperty(e="EXPONENTIAL_AT")&&((r=t[e])&&r.pop?(w(r[0],-v,0,e),w(r[1],0,v,e),R=r[0],
D=r[1]):(w(r,-v,v,e),R=-(D=r<0?-r:r))),t.hasOwnProperty(e="RANGE"))if((r=t[e])&&r.pop)w(r[0],-v,-1,e),w(r[1],1,v,e),B=r[0],F=r[1];else{if(w(r,-v,v,e),
!r)throw Error(c+e+" cannot be zero: "+r);B=-(F=r<0?-r:r)}if(t.hasOwnProperty(e="CRYPTO")){if((r=t[e])!==!!r)throw Error(c+e+" not true or false: "+r);if(r){
if("undefined"==typeof crypto||!crypto||!crypto.getRandomValues&&!crypto.randomBytes)throw M=!r,Error(c+"crypto unavailable");M=r}else M=r}
if(t.hasOwnProperty(e="MODULO_MODE")&&(w(r=t[e],0,9,e),G=r),t.hasOwnProperty(e="POW_PRECISION")&&(w(r=t[e],0,v,e),V=r),t.hasOwnProperty(e="FORMAT")){
if("object"!=o(r=t[e]))throw Error(c+e+" not an object: "+r);U=r}if(t.hasOwnProperty(e="ALPHABET")){
if("string"!=typeof(r=t[e])||/^.?$|[+\-.\s]|(.).*\1/.test(r))throw Error(c+e+" invalid: "+r);Z="0123456789"==r.slice(0,10),q=r}}return{DECIMAL_PLACES:L,
ROUNDING_MODE:N,EXPONENTIAL_AT:[R,D],RANGE:[B,F],CRYPTO:M,MODULO_MODE:G,POW_PRECISION:V,FORMAT:U,ALPHABET:q}},K.isBigNumber=function(t){
if(!t||!0!==t._isBigNumber)return!1;if(!K.DEBUG)return!0;var e,r,n=t.c,o=t.e,i=t.s;t:if("[object Array]"=={}.toString.call(n)){
if((1===i||-1===i)&&o>=-v&&o<=v&&o===u(o)){if(0===n[0]){if(0===o&&1===n.length)return!0;break t}if((e=(o+1)%h)<1&&(e+=h),String(n[0]).length==e){
for(e=0;e<n.length;e++)if((r=n[e])<0||r>=f||r!==u(r))break t;if(0!==r)return!0}}}else if(null===n&&null===o&&(null===i||1===i||-1===i))return!0
;throw Error(c+"Invalid BigNumber: "+t)},K.maximum=K.max=function(){return $(arguments,-1)},K.minimum=K.min=function(){return $(arguments,1)},
K.random=(S=9007199254740992,E=Math.random()*S&2097151?function(){return u(Math.random()*S)}:function(){
return 8388608*(1073741824*Math.random()|0)+(8388608*Math.random()|0)},function(t){var e,r,n,o,i,a=0,l=[],f=new K(I);if(null==t?t=L:w(t,0,v),o=s(t/h),
M)if(crypto.getRandomValues){
for(e=crypto.getRandomValues(new Uint32Array(o*=2));a<o;)(i=131072*e[a]+(e[a+1]>>>11))>=9e15?(r=crypto.getRandomValues(new Uint32Array(2)),e[a]=r[0],
e[a+1]=r[1]):(l.push(i%1e14),a+=2);a=o/2}else{if(!crypto.randomBytes)throw M=!1,Error(c+"crypto unavailable")
;for(e=crypto.randomBytes(o*=7);a<o;)(i=281474976710656*(31&e[a])+1099511627776*e[a+1]+4294967296*e[a+2]+16777216*e[a+3]+(e[a+4]<<16)+(e[a+5]<<8)+e[a+6])>=9e15?crypto.randomBytes(7).copy(e,a):(l.push(i%1e14),
a+=7);a=o/7}if(!M)for(;a<o;)(i=E())<9e15&&(l[a++]=i%1e14);for(o=l[--a],t%=h,o&&t&&(i=d[h-t],l[a]=u(o/i)*i);0===l[a];l.pop(),a--);if(a<0)l=[n=0];else{
for(n=-1;0===l[0];l.splice(0,1),n-=h);for(a=1,i=l[0];i>=10;i/=10,a++);a<h&&(n-=h-a)}return f.e=n,f.c=l,f}),K.sum=function(){
for(var t=1,e=arguments,r=new K(e[0]);t<e.length;)r=r.plus(e[t++]);return r},n=function(){var t="0123456789";function e(t,e,r,n){
for(var o,i,a=[0],s=0,u=t.length;s<u;){for(i=a.length;i--;a[i]*=e);for(a[0]+=n.indexOf(t.charAt(s++)),o=0;o<a.length;o++)a[o]>r-1&&(null==a[o+1]&&(a[o+1]=0),
a[o+1]+=a[o]/r|0,a[o]%=r)}return a.reverse()}return function(n,o,i,a,s){var u,c,l,f,h,p,d,y,v=n.indexOf("."),g=L,b=N;for(v>=0&&(f=V,V=0,n=n.replace(".",""),
p=(y=new K(o)).pow(n.length-v),V=f,y.c=e(P(m(p.c),p.e,"0"),10,i,t),y.e=y.c.length),l=f=(d=e(n,o,i,s?(u=q,t):(u=t,q))).length;0==d[--f];d.pop());
if(!d[0])return u.charAt(0);if(v<0?--l:(p.c=d,p.e=l,p.s=a,d=(p=r(p,y,g,b,i)).c,h=p.r,l=p.e),v=d[c=l+g+1],f=i/2,h=h||c<0||null!=d[c+1],
h=b<4?(null!=v||h)&&(0==b||b==(p.s<0?3:2)):v>f||v==f&&(4==b||h||6==b&&1&d[c-1]||b==(p.s<0?8:7)),c<1||!d[0])n=h?P(u.charAt(1),-g,u.charAt(0)):u.charAt(0);else{
if(d.length=c,h)for(--i;++d[--c]>i;)d[c]=0,c||(++l,d=[1].concat(d));for(f=d.length;!d[--f];);for(v=0,n="";v<=f;n+=u.charAt(d[v++]));n=P(n,l,u.charAt(0))}return n}
}(),r=function(){function t(t,e,r){var n,o,i,a,s=0,u=t.length,c=e%y,l=e/y|0;for(t=t.slice();u--;)s=((o=c*(i=t[u]%y)+(n=l*i+(a=t[u]/y|0)*c)%y*y+s)/r|0)+(n/y|0)+l*a,
t[u]=o%r;return s&&(t=[s].concat(t)),t}function e(t,e,r,n){var o,i;if(r!=n)i=r>n?1:-1;else for(o=i=0;o<r;o++)if(t[o]!=e[o]){i=t[o]>e[o]?1:-1;break}return i}
function r(t,e,r,n){for(var o=0;r--;)t[r]-=o,o=t[r]<e[r]?1:0,t[r]=o*n+t[r]-e[r];for(;!t[0]&&t.length>1;t.splice(0,1));}return function(n,o,i,a,s){
var c,l,p,d,y,v,m,b,w,_,x,P,S,E,O,k,j,C=n.s==o.s?1:-1,T=n.c,A=o.c;if(!(T&&T[0]&&A&&A[0]))return new K(n.s&&o.s&&(T?!A||T[0]!=A[0]:A)?T&&0==T[0]||!A?0*C:C/0:NaN)
;for(w=(b=new K(C)).c=[],C=i+(l=n.e-o.e)+1,s||(s=f,l=g(n.e/h)-g(o.e/h),C=C/h|0),p=0;A[p]==(T[p]||0);p++);if(A[p]>(T[p]||0)&&l--,C<0)w.push(1),d=!0;else{
for(E=T.length,k=A.length,p=0,C+=2,(y=u(s/(A[0]+1)))>1&&(A=t(A,y,s),T=t(T,y,s),k=A.length,E=T.length),S=k,x=(_=T.slice(0,k)).length;x<k;_[x++]=0);j=A.slice(),
j=[0].concat(j),O=A[0],A[1]>=s/2&&O++;do{if(y=0,(c=e(A,_,k,x))<0){if(P=_[0],k!=x&&(P=P*s+(_[1]||0)),(y=u(P/O))>1)for(y>=s&&(y=s-1),m=(v=t(A,y,s)).length,
x=_.length;1==e(v,_,m,x);)y--,r(v,k<m?j:A,m,s),m=v.length,c=1;else 0==y&&(c=y=1),m=(v=A.slice()).length;if(m<x&&(v=[0].concat(v)),r(_,v,x,s),x=_.length,
-1==c)for(;e(A,_,k,x)<1;)y++,r(_,k<x?j:A,x,s),x=_.length}else 0===c&&(y++,_=[0]);w[p++]=y,_[0]?_[x++]=T[S]||0:(_=[T[S]],x=1)}while((S++<E||null!=_[0])&&C--)
;d=null!=_[0],w[0]||w.splice(0,1)}if(s==f){for(p=1,C=w[0];C>=10;C/=10,p++);Y(b,i+(b.e=p+l*h-1)+1,a,d)}else b.e=l,b.r=+d;return b}}(),O=/^(-?)0([xbo])(?=\w[\w.]*$)/i,
k=/^([^.]+)\.$/,j=/^\.([^.]+)$/,C=/^-?(Infinity|NaN)$/,T=/^\s*\+(?=[\w.])|^\s+|\s+$/g,i=function(t,e,r,n){var o,i=r?e:e.replace(T,"")
;if(C.test(i))t.s=isNaN(i)?null:i<0?-1:1;else{if(!r&&(i=i.replace(O,(function(t,e,r){return o="x"==(r=r.toLowerCase())?16:"b"==r?2:8,n&&n!=o?t:e})),n&&(o=n,
i=i.replace(k,"$1").replace(j,"0.$1")),e!=i))return new K(i,o);if(K.DEBUG)throw Error(c+"Not a"+(n?" base "+n:"")+" number: "+e);t.s=null}t.c=t.e=null},
A.absoluteValue=A.abs=function(){var t=new K(this);return t.s<0&&(t.s=1),t},A.comparedTo=function(t,e){return b(this,new K(t,e))},A.decimalPlaces=A.dp=function(t,e){
var r,n,o,i=this;if(null!=t)return w(t,0,v),null==e?e=N:w(e,0,8),Y(new K(i),t+i.e+1,e);if(!(r=i.c))return null;if(n=((o=r.length-1)-g(this.e/h))*h,
o=r[o])for(;o%10==0;o/=10,n--);return n<0&&(n=0),n},A.dividedBy=A.div=function(t,e){return r(this,new K(t,e),L,N)},A.dividedToIntegerBy=A.idiv=function(t,e){
return r(this,new K(t,e),0,1)},A.exponentiatedBy=A.pow=function(t,e){var r,n,o,i,a,l,f,p,d=this
;if((t=new K(t)).c&&!t.isInteger())throw Error(c+"Exponent not an integer: "+J(t));if(null!=e&&(e=new K(e)),a=t.e>14,
!d.c||!d.c[0]||1==d.c[0]&&!d.e&&1==d.c.length||!t.c||!t.c[0])return p=new K(Math.pow(+J(d),a?t.s*(2-_(t)):+J(t))),e?p.mod(e):p;if(l=t.s<0,e){
if(e.c?!e.c[0]:!e.s)return new K(NaN);(n=!l&&d.isInteger()&&e.isInteger())&&(d=d.mod(e))}else{
if(t.e>9&&(d.e>0||d.e<-1||(0==d.e?d.c[0]>1||a&&d.c[1]>=24e7:d.c[0]<8e13||a&&d.c[0]<=9999975e7)))return i=d.s<0&&_(t)?-0:0,d.e>-1&&(i=1/i),new K(l?1/i:i)
;V&&(i=s(V/h+2))}for(a?(r=new K(.5),l&&(t.s=1),f=_(t)):f=(o=Math.abs(+J(t)))%2,p=new K(I);;){if(f){if(!(p=p.times(d)).c)break
;i?p.c.length>i&&(p.c.length=i):n&&(p=p.mod(e))}if(o){if(0===(o=u(o/2)))break;f=o%2}else if(Y(t=t.times(r),t.e+1,1),t.e>14)f=_(t);else{if(0===(o=+J(t)))break;f=o%2}
d=d.times(d),i?d.c&&d.c.length>i&&(d.c.length=i):n&&(d=d.mod(e))}return n?p:(l&&(p=I.div(p)),e?p.mod(e):i?Y(p,V,N,undefined):p)},A.integerValue=function(t){
var e=new K(this);return null==t?t=N:w(t,0,8),Y(e,e.e+1,t)},A.isEqualTo=A.eq=function(t,e){return 0===b(this,new K(t,e))},A.isFinite=function(){return!!this.c},
A.isGreaterThan=A.gt=function(t,e){return b(this,new K(t,e))>0},A.isGreaterThanOrEqualTo=A.gte=function(t,e){return 1===(e=b(this,new K(t,e)))||0===e},
A.isInteger=function(){return!!this.c&&g(this.e/h)>this.c.length-2},A.isLessThan=A.lt=function(t,e){return b(this,new K(t,e))<0},
A.isLessThanOrEqualTo=A.lte=function(t,e){return-1===(e=b(this,new K(t,e)))||0===e},A.isNaN=function(){return!this.s},A.isNegative=function(){return this.s<0},
A.isPositive=function(){return this.s>0},A.isZero=function(){return!!this.c&&0==this.c[0]},A.minus=function(t,e){var r,n,o,i,a=this,s=a.s;if(e=(t=new K(t,e)).s,
!s||!e)return new K(NaN);if(s!=e)return t.s=-e,a.plus(t);var u=a.e/h,c=t.e/h,l=a.c,p=t.c;if(!u||!c){if(!l||!p)return l?(t.s=-e,t):new K(p?a:NaN)
;if(!l[0]||!p[0])return p[0]?(t.s=-e,t):new K(l[0]?a:3==N?-0:0)}if(u=g(u),c=g(c),l=l.slice(),s=u-c){for((i=s<0)?(s=-s,o=l):(c=u,o=p),o.reverse(),e=s;e--;o.push(0));
o.reverse()}else for(n=(i=(s=l.length)<(e=p.length))?s:e,s=e=0;e<n;e++)if(l[e]!=p[e]){i=l[e]<p[e];break}if(i&&(o=l,l=p,p=o,t.s=-t.s),
(e=(n=p.length)-(r=l.length))>0)for(;e--;l[r++]=0);for(e=f-1;n>s;){if(l[--n]<p[n]){for(r=n;r&&!l[--r];l[r]=e);--l[r],l[n]+=f}l[n]-=p[n]}for(;0==l[0];l.splice(0,1),
--c);return l[0]?H(t,l,c):(t.s=3==N?-1:1,t.c=[t.e=0],t)},A.modulo=A.mod=function(t,e){var n,o,i=this;return t=new K(t,e),
!i.c||!t.s||t.c&&!t.c[0]?new K(NaN):!t.c||i.c&&!i.c[0]?new K(i):(9==G?(o=t.s,t.s=1,n=r(i,t,0,3),t.s=o,n.s*=o):n=r(i,t,0,G),
(t=i.minus(n.times(t))).c[0]||1!=G||(t.s=i.s),t)},A.multipliedBy=A.times=function(t,e){var r,n,o,i,a,s,u,c,l,p,d,v,m,b,w,_=this,x=_.c,P=(t=new K(t,e)).c
;if(!(x&&P&&x[0]&&P[0]))return!_.s||!t.s||x&&!x[0]&&!P||P&&!P[0]&&!x?t.c=t.e=t.s=null:(t.s*=_.s,x&&P?(t.c=[0],t.e=0):t.c=t.e=null),t;for(n=g(_.e/h)+g(t.e/h),
t.s*=_.s,(u=x.length)<(p=P.length)&&(m=x,x=P,P=m,o=u,u=p,p=o),o=u+p,m=[];o--;m.push(0));for(b=f,w=y,o=p;--o>=0;){for(r=0,d=P[o]%w,v=P[o]/w|0,
i=o+(a=u);i>o;)r=((c=d*(c=x[--a]%w)+(s=v*c+(l=x[a]/w|0)*d)%w*w+m[i]+r)/b|0)+(s/w|0)+v*l,m[i--]=c%b;m[i]=r}return r?++n:m.splice(0,1),H(t,m,n)},A.negated=function(){
var t=new K(this);return t.s=-t.s||null,t},A.plus=function(t,e){var r,n=this,o=n.s;if(e=(t=new K(t,e)).s,!o||!e)return new K(NaN);if(o!=e)return t.s=-e,n.minus(t)
;var i=n.e/h,a=t.e/h,s=n.c,u=t.c;if(!i||!a){if(!s||!u)return new K(o/0);if(!s[0]||!u[0])return u[0]?t:new K(s[0]?n:0*o)}if(i=g(i),a=g(a),s=s.slice(),o=i-a){
for(o>0?(a=i,r=u):(o=-o,r=s),r.reverse();o--;r.push(0));r.reverse()}for((o=s.length)-(e=u.length)<0&&(r=u,u=s,s=r,e=o),o=0;e;)o=(s[--e]=s[e]+u[e]+o)/f|0,
s[e]=f===s[e]?0:s[e]%f;return o&&(s=[o].concat(s),++a),H(t,s,a)},A.precision=A.sd=function(t,e){var r,n,o,i=this;if(null!=t&&t!==!!t)return w(t,1,v),
null==e?e=N:w(e,0,8),Y(new K(i),t,e);if(!(r=i.c))return null;if(n=(o=r.length-1)*h+1,o=r[o]){for(;o%10==0;o/=10,n--);for(o=r[0];o>=10;o/=10,n++);}
return t&&i.e+1>n&&(n=i.e+1),n},A.shiftedBy=function(t){return w(t,-9007199254740991,p),this.times("1e"+t)},A.squareRoot=A.sqrt=function(){
var t,e,n,o,i,a=this,s=a.c,u=a.s,c=a.e,l=L+4,f=new K("0.5");if(1!==u||!s||!s[0])return new K(!u||u<0&&(!s||s[0])?NaN:s?a:1/0)
;if(0==(u=Math.sqrt(+J(a)))||u==1/0?(((e=m(s)).length+c)%2==0&&(e+="0"),u=Math.sqrt(+e),c=g((c+1)/2)-(c<0||c%2),
n=new K(e=u==1/0?"5e"+c:(e=u.toExponential()).slice(0,e.indexOf("e")+1)+c)):n=new K(u+""),n.c[0])for((u=(c=n.e)+l)<3&&(u=0);;)if(i=n,n=f.times(i.plus(r(a,i,l,1))),
m(i.c).slice(0,u)===(e=m(n.c)).slice(0,u)){if(n.e<c&&--u,"9999"!=(e=e.slice(u-3,u+1))&&(o||"4999"!=e)){+e&&(+e.slice(1)||"5"!=e.charAt(0))||(Y(n,n.e+L+2,1),
t=!n.times(n).eq(a));break}if(!o&&(Y(i,i.e+L+2,0),i.times(i).eq(a))){n=i;break}l+=4,u+=4,o=1}return Y(n,n.e+L+1,N,t)},A.toExponential=function(t,e){
return null!=t&&(w(t,0,v),t++),z(this,t,e,1)},A.toFixed=function(t,e){return null!=t&&(w(t,0,v),t=t+this.e+1),z(this,t,e)},A.toFormat=function(t,e,r){var n,i=this
;if(null==r)null!=t&&e&&"object"==o(e)?(r=e,e=null):t&&"object"==o(t)?(r=t,t=e=null):r=U;else if("object"!=o(r))throw Error(c+"Argument not an object: "+r)
;if(n=i.toFixed(t,e),i.c){var a,s=n.split("."),u=+r.groupSize,l=+r.secondaryGroupSize,f=r.groupSeparator||"",h=s[0],p=s[1],d=i.s<0,y=d?h.slice(1):h,v=y.length
;if(l&&(a=u,u=l,l=a,v-=a),u>0&&v>0){for(a=v%u||u,h=y.substr(0,a);a<v;a+=u)h+=f+y.substr(a,u);l>0&&(h+=f+y.slice(a)),d&&(h="-"+h)}
n=p?h+(r.decimalSeparator||"")+((l=+r.fractionGroupSize)?p.replace(new RegExp("\\d{"+l+"}\\B","g"),"$&"+(r.fractionGroupSeparator||"")):p):h}
return(r.prefix||"")+n+(r.suffix||"")},A.toFraction=function(t){var e,n,o,i,a,s,u,l,f,p,y,v,g=this,b=g.c
;if(null!=t&&(!(u=new K(t)).isInteger()&&(u.c||1!==u.s)||u.lt(I)))throw Error(c+"Argument "+(u.isInteger()?"out of range: ":"not an integer: ")+J(u))
;if(!b)return new K(g);for(e=new K(I),f=n=new K(I),o=l=new K(I),v=m(b),a=e.e=v.length-g.e-1,e.c[0]=d[(s=a%h)<0?h+s:s],t=!t||u.comparedTo(e)>0?a>0?e:f:u,s=F,F=1/0,
u=new K(v),l.c[0]=0;p=r(u,e,0,1),1!=(i=n.plus(p.times(o))).comparedTo(t);)n=o,o=i,f=l.plus(p.times(i=f)),l=i,e=u.minus(p.times(i=e)),u=i
;return i=r(t.minus(n),o,0,1),l=l.plus(i.times(f)),n=n.plus(i.times(o)),l.s=f.s=g.s,
y=r(f,o,a*=2,N).minus(g).abs().comparedTo(r(l,n,a,N).minus(g).abs())<1?[f,o]:[l,n],F=s,y},A.toNumber=function(){return+J(this)},A.toPrecision=function(t,e){
return null!=t&&w(t,1,v),z(this,t,e,2)},A.toString=function(t){var e,r=this,o=r.s,i=r.e;return null===i?o?(e="Infinity",
o<0&&(e="-"+e)):e="NaN":(null==t?e=i<=R||i>=D?x(m(r.c),i):P(m(r.c),i,"0"):10===t&&Z?e=P(m((r=Y(new K(r),L+i+1,N)).c),r.e,"0"):(w(t,2,q.length,"Base"),
e=n(P(m(r.c),i,"0"),10,t,o,!0)),o<0&&r.c[0]&&(e="-"+e)),e},A.valueOf=A.toJSON=function(){return J(this)},A._isBigNumber=!0,null!=e&&K.set(e),K}(),
i.default=i.BigNumber=i,void 0===(n=function(){return i}.call(e,r,e,t))||(t.exports=n)}()},73978:(t,e,r)=>{"use strict";function n(t){
return n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},n(t)}function o(){o=function(){return e}
;var t,e={},r=Object.prototype,i=r.hasOwnProperty,a=Object.defineProperty||function(t,e,r){t[e]=r.value
},s="function"==typeof Symbol?Symbol:{},u=s.iterator||"@@iterator",c=s.asyncIterator||"@@asyncIterator",l=s.toStringTag||"@@toStringTag";function f(t,e,r){
return Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}),t[e]}try{f({},"")}catch(t){f=function(t,e,r){return t[e]=r}}
function h(t,e,r,n){var o=e&&e.prototype instanceof b?e:b,i=Object.create(o.prototype),s=new I(n||[]);return a(i,"_invoke",{value:j(t,r,s)}),i}function p(t,e,r){try{
return{type:"normal",arg:t.call(e,r)}}catch(t){return{type:"throw",arg:t}}}e.wrap=h;var d="suspendedStart",y="suspendedYield",v="executing",g="completed",m={}
;function b(){}function w(){}function _(){}var x={};f(x,u,(function(){return this}));var P=Object.getPrototypeOf,S=P&&P(P(L([])));S&&S!==r&&i.call(S,u)&&(x=S)
;var E=_.prototype=b.prototype=Object.create(x);function O(t){["next","throw","return"].forEach((function(e){f(t,e,(function(t){return this._invoke(e,t)}))}))}
function k(t,e){function r(o,a,s,u){var c=p(t[o],t,a);if("throw"!==c.type){var l=c.arg,f=l.value
;return f&&"object"==n(f)&&i.call(f,"__await")?e.resolve(f.__await).then((function(t){r("next",t,s,u)}),(function(t){r("throw",t,s,u)
})):e.resolve(f).then((function(t){l.value=t,s(l)}),(function(t){return r("throw",t,s,u)}))}u(c.arg)}var o;a(this,"_invoke",{value:function(t,n){function i(){
return new e((function(e,o){r(t,n,e,o)}))}return o=o?o.then(i,i):i()}})}function j(e,r,n){var o=d;return function(i,a){
if(o===v)throw Error("Generator is already running");if(o===g){if("throw"===i)throw a;return{value:t,done:!0}}for(n.method=i,n.arg=a;;){var s=n.delegate;if(s){
var u=C(s,n);if(u){if(u===m)continue;return u}}if("next"===n.method)n.sent=n._sent=n.arg;else if("throw"===n.method){if(o===d)throw o=g,n.arg
;n.dispatchException(n.arg)}else"return"===n.method&&n.abrupt("return",n.arg);o=v;var c=p(e,r,n);if("normal"===c.type){if(o=n.done?g:y,c.arg===m)continue;return{
value:c.arg,done:n.done}}"throw"===c.type&&(o=g,n.method="throw",n.arg=c.arg)}}}function C(e,r){var n=r.method,o=e.iterator[n];if(o===t)return r.delegate=null,
"throw"===n&&e.iterator.return&&(r.method="return",r.arg=t,C(e,r),"throw"===r.method)||"return"!==n&&(r.method="throw",
r.arg=new TypeError("The iterator does not provide a '"+n+"' method")),m;var i=p(o,e.iterator,r.arg);if("throw"===i.type)return r.method="throw",r.arg=i.arg,
r.delegate=null,m;var a=i.arg;return a?a.done?(r[e.resultName]=a.value,r.next=e.nextLoc,"return"!==r.method&&(r.method="next",r.arg=t),r.delegate=null,
m):a:(r.method="throw",r.arg=new TypeError("iterator result is not an object"),r.delegate=null,m)}function T(t){var e={tryLoc:t[0]};1 in t&&(e.catchLoc=t[1]),
2 in t&&(e.finallyLoc=t[2],e.afterLoc=t[3]),this.tryEntries.push(e)}function A(t){var e=t.completion||{};e.type="normal",delete e.arg,t.completion=e}function I(t){
this.tryEntries=[{tryLoc:"root"}],t.forEach(T,this),this.reset(!0)}function L(e){if(e||""===e){var r=e[u];if(r)return r.call(e);if("function"==typeof e.next)return e
;if(!isNaN(e.length)){var o=-1,a=function r(){for(;++o<e.length;)if(i.call(e,o))return r.value=e[o],r.done=!1,r;return r.value=t,r.done=!0,r};return a.next=a}}
throw new TypeError(n(e)+" is not iterable")}return w.prototype=_,a(E,"constructor",{value:_,configurable:!0}),a(_,"constructor",{value:w,configurable:!0}),
w.displayName=f(_,l,"GeneratorFunction"),e.isGeneratorFunction=function(t){var e="function"==typeof t&&t.constructor
;return!!e&&(e===w||"GeneratorFunction"===(e.displayName||e.name))},e.mark=function(t){return Object.setPrototypeOf?Object.setPrototypeOf(t,_):(t.__proto__=_,
f(t,l,"GeneratorFunction")),t.prototype=Object.create(E),t},e.awrap=function(t){return{__await:t}},O(k.prototype),f(k.prototype,c,(function(){return this})),
e.AsyncIterator=k,e.async=function(t,r,n,o,i){void 0===i&&(i=Promise);var a=new k(h(t,r,n,o),i);return e.isGeneratorFunction(r)?a:a.next().then((function(t){
return t.done?t.value:a.next()}))},O(E),f(E,l,"Generator"),f(E,u,(function(){return this})),f(E,"toString",(function(){return"[object Generator]"})),
e.keys=function(t){var e=Object(t),r=[];for(var n in e)r.push(n);return r.reverse(),function t(){for(;r.length;){var n=r.pop();if(n in e)return t.value=n,t.done=!1,t
}return t.done=!0,t}},e.values=L,I.prototype={constructor:I,reset:function(e){if(this.prev=0,this.next=0,this.sent=this._sent=t,this.done=!1,this.delegate=null,
this.method="next",this.arg=t,this.tryEntries.forEach(A),!e)for(var r in this)"t"===r.charAt(0)&&i.call(this,r)&&!isNaN(+r.slice(1))&&(this[r]=t)},stop:function(){
this.done=!0;var t=this.tryEntries[0].completion;if("throw"===t.type)throw t.arg;return this.rval},dispatchException:function(e){if(this.done)throw e;var r=this
;function n(n,o){return s.type="throw",s.arg=e,r.next=n,o&&(r.method="next",r.arg=t),!!o}for(var o=this.tryEntries.length-1;o>=0;--o){
var a=this.tryEntries[o],s=a.completion;if("root"===a.tryLoc)return n("end");if(a.tryLoc<=this.prev){var u=i.call(a,"catchLoc"),c=i.call(a,"finallyLoc");if(u&&c){
if(this.prev<a.catchLoc)return n(a.catchLoc,!0);if(this.prev<a.finallyLoc)return n(a.finallyLoc)}else if(u){if(this.prev<a.catchLoc)return n(a.catchLoc,!0)}else{
if(!c)throw Error("try statement without catch or finally");if(this.prev<a.finallyLoc)return n(a.finallyLoc)}}}},abrupt:function(t,e){
for(var r=this.tryEntries.length-1;r>=0;--r){var n=this.tryEntries[r];if(n.tryLoc<=this.prev&&i.call(n,"finallyLoc")&&this.prev<n.finallyLoc){var o=n;break}}
o&&("break"===t||"continue"===t)&&o.tryLoc<=e&&e<=o.finallyLoc&&(o=null);var a=o?o.completion:{};return a.type=t,a.arg=e,o?(this.method="next",
this.next=o.finallyLoc,m):this.complete(a)},complete:function(t,e){if("throw"===t.type)throw t.arg
;return"break"===t.type||"continue"===t.type?this.next=t.arg:"return"===t.type?(this.rval=this.arg=t.arg,this.method="return",
this.next="end"):"normal"===t.type&&e&&(this.next=e),m},finish:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.finallyLoc===t)return this.complete(r.completion,r.afterLoc),A(r),m}},catch:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.tryLoc===t){var n=r.completion;if("throw"===n.type){var o=n.arg;A(r)}return o}}throw Error("illegal catch attempt")},delegateYield:function(e,r,n){
return this.delegate={iterator:L(e),resultName:r,nextLoc:n},"next"===this.method&&(this.arg=t),m}},e}function i(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,a(n.key),n)}}function a(t){var e=function(t,e){
if("object"!=n(t)||!t)return t;var r=t[Symbol.toPrimitive];if(void 0!==r){var o=r.call(t,e||"default");if("object"!=n(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==n(e)?e:e+""}
Object.defineProperty(e,"__esModule",{value:!0}),e.Space=void 0;var s=r(95006),u=r(18759),c=function(){return t=function t(e){!function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.confluenceApi=e.confluenceApi},(e=[{key:"getSpaceByKey",
value:function(t,e){return s.__awaiter(this,void 0,void 0,o().mark((function r(){var n,i;return o().wrap((function(r){for(;;)switch(r.prev=r.next){case 0:
return r.next=2,this.confluenceApi.space.getSpaces(Object.assign(Object.assign({},e),{keys:[t]}));case 2:return n=r.sent,i=n.results,r.abrupt("return",i[0]);case 5:
case"end":return r.stop()}}),r,this)})))}},{key:"getOneSpaceByKey",value:function(t,e){var r;return s.__awaiter(this,void 0,void 0,o().mark((function n(){var i
;return o().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:return n.prev=0,n.next=3,this.confluenceApi.space.getSpaces(Object.assign(Object.assign({},e),{
keys:[t]}));case 3:if(i=n.sent,!this.isMultiEntryResultEmpty(i)){n.next=6;break}
throw new u.ExtendedConfluenceError("Cannot find a space with key [".concat(t,"]")).withClassName("Space").withMethodName("getOneSpaceByKey").withStatus(404);case 6:
return n.abrupt("return",i.results[0]);case 9:
throw n.prev=9,n.t0=n.catch(0),new u.ExtendedConfluenceError("Unexpected error on getting the space with key [".concat(t,"]"),n.t0).withClassName("Space").withMethodName("getOneSpaceByKey").withContext({
params:e}).withStatus(null!==(r=n.t0.status)&&void 0!==r?r:500);case 12:case"end":return n.stop()}}),n,this,[[0,9]])})))}},{key:"isMultiEntryResultEmpty",
value:function(t){return!(null==t?void 0:t.results)||t.results.length<=0}}])&&i(t.prototype,e),r&&i(t,r),Object.defineProperty(t,"prototype",{writable:!1}),t
;var t,e,r}();e.Space=c},74189:(t,e,r)=>{function n(t){return n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},n(t)}t=r.nmd(t)
;var o="__lodash_hash_undefined__",i=9007199254740991,a="[object Arguments]",s="[object Array]",u="[object Boolean]",c="[object Date]",l="[object Error]",f="[object Function]",h="[object Map]",p="[object Number]",d="[object Object]",y="[object Promise]",v="[object RegExp]",g="[object Set]",m="[object String]",b="[object Symbol]",w="[object WeakMap]",_="[object ArrayBuffer]",x="[object DataView]",P=/^\[object .+?Constructor\]$/,S=/^(?:0|[1-9]\d*)$/,E={}
;E["[object Float32Array]"]=E["[object Float64Array]"]=E["[object Int8Array]"]=E["[object Int16Array]"]=E["[object Int32Array]"]=E["[object Uint8Array]"]=E["[object Uint8ClampedArray]"]=E["[object Uint16Array]"]=E["[object Uint32Array]"]=!0,
E[a]=E[s]=E[_]=E[u]=E[x]=E[c]=E[l]=E[f]=E[h]=E[p]=E[d]=E[v]=E[g]=E[m]=E[w]=!1
;var O="object"==(void 0===r.g?"undefined":n(r.g))&&r.g&&r.g.Object===Object&&r.g,k="object"==("undefined"==typeof self?"undefined":n(self))&&self&&self.Object===Object&&self,j=O||k||Function("return this")(),C="object"==n(e)&&e&&!e.nodeType&&e,T=C&&"object"==n(t)&&t&&!t.nodeType&&t,A=T&&T.exports===C,I=A&&O.process,L=function(){
try{return I&&I.binding&&I.binding("util")}catch(t){}}(),N=L&&L.isTypedArray;function R(t,e){for(var r=-1,n=null==t?0:t.length;++r<n;)if(e(t[r],r,t))return!0
;return!1}function D(t){var e=-1,r=Array(t.size);return t.forEach((function(t,n){r[++e]=[n,t]})),r}function B(t){var e=-1,r=Array(t.size)
;return t.forEach((function(t){r[++e]=t})),r}
var F,M,G,V=Array.prototype,U=Function.prototype,q=Object.prototype,Z=j["__core-js_shared__"],K=U.toString,z=q.hasOwnProperty,$=(F=/[^.]+$/.exec(Z&&Z.keys&&Z.keys.IE_PROTO||""))?"Symbol(src)_1."+F:"",H=q.toString,Y=RegExp("^"+K.call(z).replace(/[\\^$.*+?()[\]{}|]/g,"\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g,"$1.*?")+"$"),J=A?j.Buffer:void 0,W=j.Symbol,Q=j.Uint8Array,X=q.propertyIsEnumerable,tt=V.splice,et=W?W.toStringTag:void 0,rt=Object.getOwnPropertySymbols,nt=J?J.isBuffer:void 0,ot=(M=Object.keys,
G=Object,function(t){return M(G(t))
}),it=Lt(j,"DataView"),at=Lt(j,"Map"),st=Lt(j,"Promise"),ut=Lt(j,"Set"),ct=Lt(j,"WeakMap"),lt=Lt(Object,"create"),ft=Bt(it),ht=Bt(at),pt=Bt(st),dt=Bt(ut),yt=Bt(ct),vt=W?W.prototype:void 0,gt=vt?vt.valueOf:void 0
;function mt(t){var e=-1,r=null==t?0:t.length;for(this.clear();++e<r;){var n=t[e];this.set(n[0],n[1])}}function bt(t){var e=-1,r=null==t?0:t.length
;for(this.clear();++e<r;){var n=t[e];this.set(n[0],n[1])}}function wt(t){var e=-1,r=null==t?0:t.length;for(this.clear();++e<r;){var n=t[e];this.set(n[0],n[1])}}
function _t(t){var e=-1,r=null==t?0:t.length;for(this.__data__=new wt;++e<r;)this.add(t[e])}function xt(t){var e=this.__data__=new bt(t);this.size=e.size}
function Pt(t,e){var r=Gt(t),n=!r&&Mt(t),o=!r&&!n&&Vt(t),i=!r&&!n&&!o&&zt(t),a=r||n||o||i,s=a?function(t,e){for(var r=-1,n=Array(t);++r<t;)n[r]=e(r);return n
}(t.length,String):[],u=s.length
;for(var c in t)!e&&!z.call(t,c)||a&&("length"==c||o&&("offset"==c||"parent"==c)||i&&("buffer"==c||"byteLength"==c||"byteOffset"==c)||Dt(c,u))||s.push(c);return s}
function St(t,e){for(var r=t.length;r--;)if(Ft(t[r][0],e))return r;return-1}function Et(t){
return null==t?void 0===t?"[object Undefined]":"[object Null]":et&&et in Object(t)?function(t){var e=z.call(t,et),r=t[et];try{t[et]=void 0;var n=!0}catch(t){}
var o=H.call(t);n&&(e?t[et]=r:delete t[et]);return o}(t):function(t){return H.call(t)}(t)}function Ot(t){return Kt(t)&&Et(t)==a}function kt(t,e,r,n,o){
return t===e||(null==t||null==e||!Kt(t)&&!Kt(e)?t!=t&&e!=e:function(t,e,r,n,o,i){
var f=Gt(t),y=Gt(e),w=f?s:Rt(t),P=y?s:Rt(e),S=(w=w==a?d:w)==d,E=(P=P==a?d:P)==d,O=w==P;if(O&&Vt(t)){if(!Vt(e))return!1;f=!0,S=!1}if(O&&!S)return i||(i=new xt),
f||zt(t)?Tt(t,e,r,n,o,i):function(t,e,r,n,o,i,a){switch(r){case x:if(t.byteLength!=e.byteLength||t.byteOffset!=e.byteOffset)return!1;t=t.buffer,e=e.buffer;case _:
return!(t.byteLength!=e.byteLength||!i(new Q(t),new Q(e)));case u:case c:case p:return Ft(+t,+e);case l:return t.name==e.name&&t.message==e.message;case v:case m:
return t==e+"";case h:var s=D;case g:var f=1&n;if(s||(s=B),t.size!=e.size&&!f)return!1;var d=a.get(t);if(d)return d==e;n|=2,a.set(t,e);var y=Tt(s(t),s(e),n,o,i,a)
;return a.delete(t),y;case b:if(gt)return gt.call(t)==gt.call(e)}return!1}(t,e,w,r,n,o,i);if(!(1&r)){var k=S&&z.call(t,"__wrapped__"),j=E&&z.call(e,"__wrapped__")
;if(k||j){var C=k?t.value():t,T=j?e.value():e;return i||(i=new xt),o(C,T,r,n,i)}}if(!O)return!1;return i||(i=new xt),function(t,e,r,n,o,i){
var a=1&r,s=At(t),u=s.length,c=At(e),l=c.length;if(u!=l&&!a)return!1;var f=u;for(;f--;){var h=s[f];if(!(a?h in e:z.call(e,h)))return!1}var p=i.get(t)
;if(p&&i.get(e))return p==e;var d=!0;i.set(t,e),i.set(e,t);var y=a;for(;++f<u;){var v=t[h=s[f]],g=e[h];if(n)var m=a?n(g,v,h,e,t,i):n(v,g,h,t,e,i)
;if(!(void 0===m?v===g||o(v,g,r,n,i):m)){d=!1;break}y||(y="constructor"==h)}if(d&&!y){var b=t.constructor,w=e.constructor
;b==w||!("constructor"in t)||!("constructor"in e)||"function"==typeof b&&b instanceof b&&"function"==typeof w&&w instanceof w||(d=!1)}return i.delete(t),i.delete(e),
d}(t,e,r,n,o,i)}(t,e,r,n,kt,o))}function jt(t){return!(!Zt(t)||function(t){return!!$&&$ in t}(t))&&(Ut(t)?Y:P).test(Bt(t))}function Ct(t){if(r=(e=t)&&e.constructor,
n="function"==typeof r&&r.prototype||q,e!==n)return ot(t);var e,r,n,o=[];for(var i in Object(t))z.call(t,i)&&"constructor"!=i&&o.push(i);return o}
function Tt(t,e,r,n,o,i){var a=1&r,s=t.length,u=e.length;if(s!=u&&!(a&&u>s))return!1;var c=i.get(t);if(c&&i.get(e))return c==e;var l=-1,f=!0,h=2&r?new _t:void 0
;for(i.set(t,e),i.set(e,t);++l<s;){var p=t[l],d=e[l];if(n)var y=a?n(d,p,l,e,t,i):n(p,d,l,t,e,i);if(void 0!==y){if(y)continue;f=!1;break}if(h){if(!R(e,(function(t,e){
if(a=e,!h.has(a)&&(p===t||o(p,t,r,n,i)))return h.push(e);var a}))){f=!1;break}}else if(p!==d&&!o(p,d,r,n,i)){f=!1;break}}return i.delete(t),i.delete(e),f}
function At(t){return function(t,e,r){var n=e(t);return Gt(t)?n:function(t,e){for(var r=-1,n=e.length,o=t.length;++r<n;)t[o+r]=e[r];return t}(n,r(t))}(t,$t,Nt)}
function It(t,e){var r,o,i=t.__data__
;return("string"==(o=n(r=e))||"number"==o||"symbol"==o||"boolean"==o?"__proto__"!==r:null===r)?i["string"==typeof e?"string":"hash"]:i.map}function Lt(t,e){
var r=function(t,e){return null==t?void 0:t[e]}(t,e);return jt(r)?r:void 0}mt.prototype.clear=function(){this.__data__=lt?lt(null):{},this.size=0},
mt.prototype.delete=function(t){var e=this.has(t)&&delete this.__data__[t];return this.size-=e?1:0,e},mt.prototype.get=function(t){var e=this.__data__;if(lt){
var r=e[t];return r===o?void 0:r}return z.call(e,t)?e[t]:void 0},mt.prototype.has=function(t){var e=this.__data__;return lt?void 0!==e[t]:z.call(e,t)},
mt.prototype.set=function(t,e){var r=this.__data__;return this.size+=this.has(t)?0:1,r[t]=lt&&void 0===e?o:e,this},bt.prototype.clear=function(){this.__data__=[],
this.size=0},bt.prototype.delete=function(t){var e=this.__data__,r=St(e,t);return!(r<0)&&(r==e.length-1?e.pop():tt.call(e,r,1),--this.size,!0)},
bt.prototype.get=function(t){var e=this.__data__,r=St(e,t);return r<0?void 0:e[r][1]},bt.prototype.has=function(t){return St(this.__data__,t)>-1},
bt.prototype.set=function(t,e){var r=this.__data__,n=St(r,t);return n<0?(++this.size,r.push([t,e])):r[n][1]=e,this},wt.prototype.clear=function(){this.size=0,
this.__data__={hash:new mt,map:new(at||bt),string:new mt}},wt.prototype.delete=function(t){var e=It(this,t).delete(t);return this.size-=e?1:0,e},
wt.prototype.get=function(t){return It(this,t).get(t)},wt.prototype.has=function(t){return It(this,t).has(t)},wt.prototype.set=function(t,e){
var r=It(this,t),n=r.size;return r.set(t,e),this.size+=r.size==n?0:1,this},_t.prototype.add=_t.prototype.push=function(t){return this.__data__.set(t,o),this},
_t.prototype.has=function(t){return this.__data__.has(t)},xt.prototype.clear=function(){this.__data__=new bt,this.size=0},xt.prototype.delete=function(t){
var e=this.__data__,r=e.delete(t);return this.size=e.size,r},xt.prototype.get=function(t){return this.__data__.get(t)},xt.prototype.has=function(t){
return this.__data__.has(t)},xt.prototype.set=function(t,e){var r=this.__data__;if(r instanceof bt){var n=r.__data__;if(!at||n.length<199)return n.push([t,e]),
this.size=++r.size,this;r=this.__data__=new wt(n)}return r.set(t,e),this.size=r.size,this};var Nt=rt?function(t){return null==t?[]:(t=Object(t),function(t,e){
for(var r=-1,n=null==t?0:t.length,o=0,i=[];++r<n;){var a=t[r];e(a,r,t)&&(i[o++]=a)}return i}(rt(t),(function(e){return X.call(t,e)})))}:function(){return[]},Rt=Et
;function Dt(t,e){return!!(e=null==e?i:e)&&("number"==typeof t||S.test(t))&&t>-1&&t%1==0&&t<e}function Bt(t){if(null!=t){try{return K.call(t)}catch(t){}try{
return t+""}catch(t){}}return""}function Ft(t,e){return t===e||t!=t&&e!=e}
(it&&Rt(new it(new ArrayBuffer(1)))!=x||at&&Rt(new at)!=h||st&&Rt(st.resolve())!=y||ut&&Rt(new ut)!=g||ct&&Rt(new ct)!=w)&&(Rt=function(t){
var e=Et(t),r=e==d?t.constructor:void 0,n=r?Bt(r):"";if(n)switch(n){case ft:return x;case ht:return h;case pt:return y;case dt:return g;case yt:return w}return e})
;var Mt=Ot(function(){return arguments}())?Ot:function(t){return Kt(t)&&z.call(t,"callee")&&!X.call(t,"callee")},Gt=Array.isArray;var Vt=nt||function(){return!1}
;function Ut(t){if(!Zt(t))return!1;var e=Et(t);return e==f||"[object GeneratorFunction]"==e||"[object AsyncFunction]"==e||"[object Proxy]"==e}function qt(t){
return"number"==typeof t&&t>-1&&t%1==0&&t<=i}function Zt(t){var e=n(t);return null!=t&&("object"==e||"function"==e)}function Kt(t){return null!=t&&"object"==n(t)}
var zt=N?function(t){return function(e){return t(e)}}(N):function(t){return Kt(t)&&qt(t.length)&&!!E[Et(t)]};function $t(t){
return null!=(e=t)&&qt(e.length)&&!Ut(e)?Pt(t):Ct(t);var e}t.exports=function(t,e){return kt(t,e)}},74341:(t,e)=>{"use strict";Object.defineProperty(e,"__esModule",{
value:!0})},74358:(t,e)=>{"use strict";function r(t){return r="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},r(t)}function n(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,o(n.key),n)}}function o(t){var e=function(t,e){
if("object"!=r(t)||!t)return t;var n=t[Symbol.toPrimitive];if(void 0!==n){var o=n.call(t,e||"default");if("object"!=r(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==r(e)?e:e+""}
Object.defineProperty(e,"__esModule",{value:!0}),e.Space=void 0;var i=function(){return t=function t(e){!function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.client=e},(e=[{key:"getSpaces",value:function(t){var e={
url:"/api/v2/spaces",type:"GET",queryParams:{ids:null==t?void 0:t.ids,keys:null==t?void 0:t.keys,type:null==t?void 0:t.type,status:null==t?void 0:t.status,
labels:null==t?void 0:t.labels,sort:null==t?void 0:t.sort,"description-format":null==t?void 0:t["description-format"],
"include-icon":null==t?void 0:t["include-icon"],cursor:null==t?void 0:t.cursor,limit:null==t?void 0:t.limit}};return this.client.sendRequest(e)}},{
key:"getSpaceById",value:function(t,e){var r={url:"/api/v2/spaces/".concat(t),type:"GET",queryParams:{"description-format":null==e?void 0:e["description-format"],
"include-icon":null==e?void 0:e["include-icon"]}};return this.client.sendRequest(r)}},{key:"getPagesInSpace",value:function(t,e){var r={
url:"/api/v2/spaces/".concat(t,"/pages"),type:"GET",queryParams:{depth:null==e?void 0:e.depth,sort:null==e?void 0:e.sort,status:null==e?void 0:e.status,
title:null==e?void 0:e.title,"body-format":null==e?void 0:e["body-format"],cursor:null==e?void 0:e.cursor,limit:null==e?void 0:e.limit}}
;return this.client.sendRequest(r)}},{key:"getBlogPostsInSpace",value:function(t,e){var r={url:"/api/v2/spaces/".concat(t,"/blogposts"),type:"GET",queryParams:{
sort:null==e?void 0:e.sort,status:null==e?void 0:e.status,title:null==e?void 0:e.title,"body-format":null==e?void 0:e["body-format"],cursor:null==e?void 0:e.cursor,
limit:null==e?void 0:e.limit}};return this.client.sendRequest(r)}}])&&n(t.prototype,e),r&&n(t,r),Object.defineProperty(t,"prototype",{writable:!1}),t;var t,e,r}()
;e.Space=i},74954:(t,e)=>{"use strict";Object.defineProperty(e,"__esModule",{value:!0})},76175:(t,e,r)=>{"use strict";function n(t){
return n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},n(t)}
var o="function"==typeof Symbol&&"symbol"===n(Symbol.iterator)?function(t){return n(t)}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":n(t)},i=r(20481);var a=r(25916);Object.defineProperty(e,"sK",{
enumerable:!0,get:function(){return l(a).default}});var s=r(88970);var u=r(16140);var c=r(38611);function l(t){return t&&t.__esModule?t:{default:t}}
var f=r(96200)("http"),h=r(60052).default,p=r(36508).parseJson,d=function(t,e){return{type:"GET",contentType:"application/json",success:function(e){
if("object"==(void 0===e?"undefined":o(e)))t(e);else try{t(p(e))}catch(r){t(e)}},error:function(t){try{var r=p(t.responseText);r&&r.statusCode&&(n=r,o="statusCode",
i="status",Object.defineProperty(n,i,Object.getOwnPropertyDescriptor(n,o)),delete n[o]),e(r)}catch(r){e({status:500,
message:t&&t.responseText?t.responseText:"Server response error"})}var n,o,i}}},y=function(){var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{},e=null
;if(t.client?e=t.client:window.AP?e=window.AP.request:window.AJS?e=window.AJS.$.ajax:(window.$||window.jQuery)&&(e=window.$.ajax||window.jQuery.ajax),
null===e)throw new Error("No compatible client found");var r=t.baseUrl;return new Promise((function(n,o){var i=Object.assign({},d(n,o),t)
;if(r&&i.url&&(i.url=r+i.url),i.url.includes("?")?i.url+="&privacyMode=true":i.url+="?privacyMode=true",f.enabled){var a=i.type,s=i.url,u=function(t,e){var r={}
;for(var n in t)e.indexOf(n)>=0||Object.prototype.hasOwnProperty.call(t,n)&&(r[n]=t[n]);return r}(i,["type","url"])
;f("### "+a.toUpperCase()+" "+s+", "+JSON.stringify(u))}e(i)}))};y.encrypt=h},76232:t=>{"use strict";function e(t){
return e="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},e(t)}function r(t,e,r){
e="number"==typeof e?i(e.toString()):"string"==typeof e?i(e):e;var n=function(t,e,r,i){var a,s=e[i];return e.length>i?(Array.isArray(t)?(s=o(s,t),
a=t.slice()):a=Object.assign({},t),a[s]=n(void 0!==t[s]?t[s]:{},e,r,i+1),a):"function"==typeof r?r(t):r};return n(t,e,r,0)}function n(t,r,n){
r="number"==typeof r?i(r.toString()):"string"==typeof r?i(r):r;for(var o=0;o<r.length;o++){if(null===t||"object"!==e(t))return n;var a=r[o]
;Array.isArray(t)&&"$end"===a&&(a=t.length-1),t=t[a]}return void 0===t?n:t}function o(t,e){if("$end"===t&&(t=Math.max(e.length-1,0)),
!/^\+?\d+$/.test(t))throw new Error("Array index '"+t+"' has to be an integer");return parseInt(t)}function i(t){return t.split(".").reduce((function(t,e,r,n){
var o=r>0&&n[r-1];return o&&/(?:^|[^\\])\\$/.test(o)?(t.pop(),t.push(o.slice(0,-1)+"."+e)):t.push(e),t}),[])}t.exports={set:r,get:n,delete:function(t,r){
r="number"==typeof r?i(r.toString()):"string"==typeof r?i(r):r;var n=function(t,r,i){var a,s=r[i]
;return null===t||"object"!==e(t)||!Array.isArray(t)&&void 0===t[s]?t:r.length-1>i?(Array.isArray(t)?(s=o(s,t),a=t.slice()):a=Object.assign({},t),a[s]=n(t[s],r,i+1),
a):(Array.isArray(t)?(s=o(s,t),a=[].concat(t.slice(0,s),t.slice(s+1))):delete(a=Object.assign({},t))[s],a)};return n(t,r,0)},toggle:function(t,e){var o=n(t,e)
;return r(t,e,!Boolean(o))},merge:function(t,o,i){var a=n(t,o)
;return"object"===e(a)?Array.isArray(a)?r(t,o,a.concat(i)):r(t,o,null===a?i:Object.assign({},a,i)):void 0===a?r(t,o,i):t}}},76804:(t,e)=>{"use strict";function r(t){
return r="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},r(t)}function n(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,o(n.key),n)}}function o(t){var e=function(t,e){
if("object"!=r(t)||!t)return t;var n=t[Symbol.toPrimitive];if(void 0!==n){var o=n.call(t,e||"default");if("object"!=r(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==r(e)?e:e+""}
Object.defineProperty(e,"__esModule",{value:!0}),e.CustomContent=void 0;var i=function(){return t=function t(e){!function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.client=e},(e=[{key:"getCustomContentHistory",value:function(t,e){var r={
url:"/api/v2/custom-content/".concat(t,"/versions"),type:"GET",queryParams:{sort:null==e?void 0:e.sort,cursor:null==e?void 0:e.cursor,limit:null==e?void 0:e.limit,
"body-format":null==e?void 0:e["body-format"]}};return this.client.sendRequest(r)}},{key:"createCustomContent",value:function(t){var e={url:"/api/v2/custom-content",
type:"POST",requestBody:t};return this.client.sendRequest(e)}},{key:"updateCustomContent",value:function(t,e){var r={url:"/api/v2/custom-content/".concat(t),
type:"PUT",requestBody:e};return this.client.sendRequest(r)}},{key:"deleteCustomContent",value:function(t){var e={url:"/api/v2/custom-content/".concat(t),
type:"DELETE"};return this.client.sendRequest(e)}},{key:"getCustomContent",value:function(t,e,r){var n={url:"/api/v2/".concat(e,"s/").concat(t,"/custom-content"),
type:"GET",queryParams:{type:r.type,sort:r.sort,cursor:r.cursor,limit:r.limit,"body-format":r["body-format"]}};return this.client.sendRequest(n)}},{
key:"getCustomContentById",value:function(t,e){var r={url:"/api/v2/custom-content/".concat(t),type:"GET",queryParams:{"body-format":null==e?void 0:e["body-format"],
version:null==e?void 0:e.version}};return this.client.sendRequest(r)}}])&&n(t.prototype,e),r&&n(t,r),Object.defineProperty(t,"prototype",{writable:!1}),t;var t,e,r
}();e.CustomContent=i},78777:(t,e)=>{"use strict";Object.defineProperty(e,"__esModule",{value:!0})},79112:(t,e,r)=>{var n=r(24297).stringify,o=r(62599)
;t.exports=function(t){return{parse:o(t),stringify:n}},t.exports.parse=o(),t.exports.stringify=n},79804:(t,e)=>{"use strict";function r(t){
return r="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},r(t)}function n(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,o(n.key),n)}}function o(t){var e=function(t,e){
if("object"!=r(t)||!t)return t;var n=t[Symbol.toPrimitive];if(void 0!==n){var o=n.call(t,e||"default");if("object"!=r(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==r(e)?e:e+""}
Object.defineProperty(e,"__esModule",{value:!0}),e.Version=void 0;var i=function(){return t=function t(e){!function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.client=e},(e=[{key:"getAttachmentVersions",value:function(t,e){var r={
url:"/api/v2/attachments/".concat(t,"/versions"),type:"GET",queryParams:{sort:null==e?void 0:e.sort,cursor:null==e?void 0:e.cursor,limit:null==e?void 0:e.limit}}
;return this.client.sendRequest(r)}},{key:"getBlogPostVersions",value:function(t,e){var r={url:"/api/v2/blogposts/".concat(t,"/versions"),type:"GET",queryParams:{
sort:null==e?void 0:e.sort,cursor:null==e?void 0:e.cursor,limit:null==e?void 0:e.limit,"body-format":null==e?void 0:e["body-format"]}}
;return this.client.sendRequest(r)}},{key:"getPageVersions",value:function(t,e){var r={url:"/api/v2/pages/".concat(t,"/versions"),type:"GET",queryParams:{
sort:null==e?void 0:e.sort,cursor:null==e?void 0:e.cursor,limit:null==e?void 0:e.limit,"body-format":null==e?void 0:e["body-format"]}}
;return this.client.sendRequest(r)}},{key:"getCustomContentVersions",value:function(t,e){var r={url:"/api/v2/custom-content/".concat(t,"/versions"),type:"GET",
queryParams:{sort:null==e?void 0:e.sort,cursor:null==e?void 0:e.cursor,limit:null==e?void 0:e.limit,"body-format":null==e?void 0:e["body-format"]}}
;return this.client.sendRequest(r)}},{key:"getFooterCommentVersions",value:function(t,e){var r={url:"/api/v2/footer-comments/".concat(t,"/versions"),type:"GET",
queryParams:{sort:null==e?void 0:e.sort,cursor:null==e?void 0:e.cursor,limit:null==e?void 0:e.limit,"body-format":null==e?void 0:e["body-format"]}}
;return this.client.sendRequest(r)}},{key:"getInlineCommentVersions",value:function(t,e){var r={url:"/api/v2/inline-comments/".concat(t,"/versions"),type:"GET",
queryParams:{sort:null==e?void 0:e.sort,cursor:null==e?void 0:e.cursor,limit:null==e?void 0:e.limit,"body-format":null==e?void 0:e["body-format"]}}
;return this.client.sendRequest(r)}}])&&n(t.prototype,e),r&&n(t,r),Object.defineProperty(t,"prototype",{writable:!1}),t;var t,e,r}();e.Version=i},82402:(t,e,r)=>{
"use strict";Object.defineProperty(e,"__esModule",{value:!0}),r(95006).__exportStar(r(34173),e)},84928:(t,e)=>{"use strict";function r(t){
return r="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},r(t)}function n(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,o(n.key),n)}}function o(t){var e=function(t,e){
if("object"!=r(t)||!t)return t;var n=t[Symbol.toPrimitive];if(void 0!==n){var o=n.call(t,e||"default");if("object"!=r(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==r(e)?e:e+""}
Object.defineProperty(e,"__esModule",{value:!0}),e.BlogPost=void 0;var i=function(){return t=function t(e){!function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.client=e},(e=[{key:"createBlogPost",value:function(t,e){var r={
url:"/api/v2/blogposts",type:"POST",queryParams:{embedded:null==e?void 0:e.embedded,private:null==e?void 0:e.private},requestBody:{spaceId:t.spaceId,status:t.status,
title:t.title,parentId:t.parentId,body:t.body}};return this.client.sendRequest(r)}},{key:"getBlogPostById",value:function(t,e){var r={
url:"/api/v2/blogposts/".concat(t),type:"GET",queryParams:{"body-format":null==e?void 0:e["body-format"],"get-draft":null==e?void 0:e["get-draft"],
version:null==e?void 0:e.version}};return this.client.sendRequest(r)}},{key:"deleteBlogPost",value:function(t){var e={url:"/api/v2/blogposts/".concat(t),
type:"DELETE"};return this.client.sendRequest(e)}},{key:"updateBlogPost",value:function(t,e){var r={url:"/api/v2/blogposts/".concat(t),type:"PUT",requestBody:{
id:e.id,status:e.status,title:e.title,spaceId:e.spaceId,parentId:e.parentId,body:e.body,version:e.version}};return this.client.sendRequest(r)}}])&&n(t.prototype,e),
r&&n(t,r),Object.defineProperty(t,"prototype",{writable:!1}),t;var t,e,r}();e.BlogPost=i},85572:(t,e)=>{"use strict";Object.defineProperty(e,"__esModule",{value:!0})
},87753:(t,e,r)=>{"use strict";function n(t){return n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},n(t)}function o(){o=function(){return e}
;var t,e={},r=Object.prototype,i=r.hasOwnProperty,a=Object.defineProperty||function(t,e,r){t[e]=r.value
},s="function"==typeof Symbol?Symbol:{},u=s.iterator||"@@iterator",c=s.asyncIterator||"@@asyncIterator",l=s.toStringTag||"@@toStringTag";function f(t,e,r){
return Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}),t[e]}try{f({},"")}catch(t){f=function(t,e,r){return t[e]=r}}
function h(t,e,r,n){var o=e&&e.prototype instanceof b?e:b,i=Object.create(o.prototype),s=new I(n||[]);return a(i,"_invoke",{value:j(t,r,s)}),i}function p(t,e,r){try{
return{type:"normal",arg:t.call(e,r)}}catch(t){return{type:"throw",arg:t}}}e.wrap=h;var d="suspendedStart",y="suspendedYield",v="executing",g="completed",m={}
;function b(){}function w(){}function _(){}var x={};f(x,u,(function(){return this}));var P=Object.getPrototypeOf,S=P&&P(P(L([])));S&&S!==r&&i.call(S,u)&&(x=S)
;var E=_.prototype=b.prototype=Object.create(x);function O(t){["next","throw","return"].forEach((function(e){f(t,e,(function(t){return this._invoke(e,t)}))}))}
function k(t,e){function r(o,a,s,u){var c=p(t[o],t,a);if("throw"!==c.type){var l=c.arg,f=l.value
;return f&&"object"==n(f)&&i.call(f,"__await")?e.resolve(f.__await).then((function(t){r("next",t,s,u)}),(function(t){r("throw",t,s,u)
})):e.resolve(f).then((function(t){l.value=t,s(l)}),(function(t){return r("throw",t,s,u)}))}u(c.arg)}var o;a(this,"_invoke",{value:function(t,n){function i(){
return new e((function(e,o){r(t,n,e,o)}))}return o=o?o.then(i,i):i()}})}function j(e,r,n){var o=d;return function(i,a){
if(o===v)throw Error("Generator is already running");if(o===g){if("throw"===i)throw a;return{value:t,done:!0}}for(n.method=i,n.arg=a;;){var s=n.delegate;if(s){
var u=C(s,n);if(u){if(u===m)continue;return u}}if("next"===n.method)n.sent=n._sent=n.arg;else if("throw"===n.method){if(o===d)throw o=g,n.arg
;n.dispatchException(n.arg)}else"return"===n.method&&n.abrupt("return",n.arg);o=v;var c=p(e,r,n);if("normal"===c.type){if(o=n.done?g:y,c.arg===m)continue;return{
value:c.arg,done:n.done}}"throw"===c.type&&(o=g,n.method="throw",n.arg=c.arg)}}}function C(e,r){var n=r.method,o=e.iterator[n];if(o===t)return r.delegate=null,
"throw"===n&&e.iterator.return&&(r.method="return",r.arg=t,C(e,r),"throw"===r.method)||"return"!==n&&(r.method="throw",
r.arg=new TypeError("The iterator does not provide a '"+n+"' method")),m;var i=p(o,e.iterator,r.arg);if("throw"===i.type)return r.method="throw",r.arg=i.arg,
r.delegate=null,m;var a=i.arg;return a?a.done?(r[e.resultName]=a.value,r.next=e.nextLoc,"return"!==r.method&&(r.method="next",r.arg=t),r.delegate=null,
m):a:(r.method="throw",r.arg=new TypeError("iterator result is not an object"),r.delegate=null,m)}function T(t){var e={tryLoc:t[0]};1 in t&&(e.catchLoc=t[1]),
2 in t&&(e.finallyLoc=t[2],e.afterLoc=t[3]),this.tryEntries.push(e)}function A(t){var e=t.completion||{};e.type="normal",delete e.arg,t.completion=e}function I(t){
this.tryEntries=[{tryLoc:"root"}],t.forEach(T,this),this.reset(!0)}function L(e){if(e||""===e){var r=e[u];if(r)return r.call(e);if("function"==typeof e.next)return e
;if(!isNaN(e.length)){var o=-1,a=function r(){for(;++o<e.length;)if(i.call(e,o))return r.value=e[o],r.done=!1,r;return r.value=t,r.done=!0,r};return a.next=a}}
throw new TypeError(n(e)+" is not iterable")}return w.prototype=_,a(E,"constructor",{value:_,configurable:!0}),a(_,"constructor",{value:w,configurable:!0}),
w.displayName=f(_,l,"GeneratorFunction"),e.isGeneratorFunction=function(t){var e="function"==typeof t&&t.constructor
;return!!e&&(e===w||"GeneratorFunction"===(e.displayName||e.name))},e.mark=function(t){return Object.setPrototypeOf?Object.setPrototypeOf(t,_):(t.__proto__=_,
f(t,l,"GeneratorFunction")),t.prototype=Object.create(E),t},e.awrap=function(t){return{__await:t}},O(k.prototype),f(k.prototype,c,(function(){return this})),
e.AsyncIterator=k,e.async=function(t,r,n,o,i){void 0===i&&(i=Promise);var a=new k(h(t,r,n,o),i);return e.isGeneratorFunction(r)?a:a.next().then((function(t){
return t.done?t.value:a.next()}))},O(E),f(E,l,"Generator"),f(E,u,(function(){return this})),f(E,"toString",(function(){return"[object Generator]"})),
e.keys=function(t){var e=Object(t),r=[];for(var n in e)r.push(n);return r.reverse(),function t(){for(;r.length;){var n=r.pop();if(n in e)return t.value=n,t.done=!1,t
}return t.done=!0,t}},e.values=L,I.prototype={constructor:I,reset:function(e){if(this.prev=0,this.next=0,this.sent=this._sent=t,this.done=!1,this.delegate=null,
this.method="next",this.arg=t,this.tryEntries.forEach(A),!e)for(var r in this)"t"===r.charAt(0)&&i.call(this,r)&&!isNaN(+r.slice(1))&&(this[r]=t)},stop:function(){
this.done=!0;var t=this.tryEntries[0].completion;if("throw"===t.type)throw t.arg;return this.rval},dispatchException:function(e){if(this.done)throw e;var r=this
;function n(n,o){return s.type="throw",s.arg=e,r.next=n,o&&(r.method="next",r.arg=t),!!o}for(var o=this.tryEntries.length-1;o>=0;--o){
var a=this.tryEntries[o],s=a.completion;if("root"===a.tryLoc)return n("end");if(a.tryLoc<=this.prev){var u=i.call(a,"catchLoc"),c=i.call(a,"finallyLoc");if(u&&c){
if(this.prev<a.catchLoc)return n(a.catchLoc,!0);if(this.prev<a.finallyLoc)return n(a.finallyLoc)}else if(u){if(this.prev<a.catchLoc)return n(a.catchLoc,!0)}else{
if(!c)throw Error("try statement without catch or finally");if(this.prev<a.finallyLoc)return n(a.finallyLoc)}}}},abrupt:function(t,e){
for(var r=this.tryEntries.length-1;r>=0;--r){var n=this.tryEntries[r];if(n.tryLoc<=this.prev&&i.call(n,"finallyLoc")&&this.prev<n.finallyLoc){var o=n;break}}
o&&("break"===t||"continue"===t)&&o.tryLoc<=e&&e<=o.finallyLoc&&(o=null);var a=o?o.completion:{};return a.type=t,a.arg=e,o?(this.method="next",
this.next=o.finallyLoc,m):this.complete(a)},complete:function(t,e){if("throw"===t.type)throw t.arg
;return"break"===t.type||"continue"===t.type?this.next=t.arg:"return"===t.type?(this.rval=this.arg=t.arg,this.method="return",
this.next="end"):"normal"===t.type&&e&&(this.next=e),m},finish:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.finallyLoc===t)return this.complete(r.completion,r.afterLoc),A(r),m}},catch:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.tryLoc===t){var n=r.completion;if("throw"===n.type){var o=n.arg;A(r)}return o}}throw Error("illegal catch attempt")},delegateYield:function(e,r,n){
return this.delegate={iterator:L(e),resultName:r,nextLoc:n},"next"===this.method&&(this.arg=t),m}},e}function i(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,a(n.key),n)}}function a(t){var e=function(t,e){
if("object"!=n(t)||!t)return t;var r=t[Symbol.toPrimitive];if(void 0!==r){var o=r.call(t,e||"default");if("object"!=n(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==n(e)?e:e+""}
Object.defineProperty(e,"__esModule",{value:!0}),e.Content=void 0;var s=r(95006),u=r(18759),c=r(62941),l=function(){return t=function t(e){!function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.confluenceApi=e.confluenceApi},(e=[{key:"getContentType",
value:function(t){return s.__awaiter(this,void 0,void 0,o().mark((function e(){var r,n,i;return o().wrap((function(e){for(;;)switch(e.prev=e.next){case 0:
return e.next=2,this.confluenceApi.content.getContentType({contentIds:[t]});case 2:if(r=e.sent,!this.isContentIdToContentTypeResponseEmpty(r)){e.next=5;break}
throw new u.ExtendedConfluenceError("Unable to process an empty response for content id [".concat(t,"]")).withClassName("Content").withMethodName("getContentType").withStatus(500,c.ErrorCode.EMPTY_RESPONSE)
;case 5:return n=r.results,i=n[t],e.abrupt("return",i);case 8:case"end":return e.stop()}}),e,this)})))}},{key:"resolveContentType",value:function(t,e){
return s.__awaiter(this,void 0,void 0,o().mark((function r(){return o().wrap((function(r){for(;;)switch(r.prev=r.next){case 0:if(!e){r.next=2;break}
return r.abrupt("return",e);case 2:return r.next=4,this.getContentType(t);case 4:return r.abrupt("return",r.sent);case 5:case"end":return r.stop()}}),r,this)})))}},{
key:"isContentIdToContentTypeResponseEmpty",value:function(t){return!(null==t?void 0:t.results)||Object.entries(t.results).length<=0}}])&&i(t.prototype,e),r&&i(t,r),
Object.defineProperty(t,"prototype",{writable:!1}),t;var t,e,r}();e.Content=l},88970:(t,e,r)=>{"use strict";function n(t){
return n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},n(t)}Object.defineProperty(e,"__esModule",{value:!0})
;var o=function(){function t(t,e){for(var r=0;r<e.length;r++){var n=e[r];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),
Object.defineProperty(t,n.key,n)}}return function(e,r,n){return r&&t(e.prototype,r),n&&t(e,n),e}}(),i=s(r(25916)),a=s(r(76232));function s(t){
return t&&t.__esModule?t:{default:t}}var u=function(t){function e(t){var r=arguments.length>1&&void 0!==arguments[1]?arguments[1]:null;!function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,e);var o=function(t,e){
if(!t)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return!e||"object"!==n(e)&&"function"!=typeof e?t:e
}(this,(e.__proto__||Object.getPrototypeOf(e)).call(this,t));return o.migrator=r,o}return function(t,e){
if("function"!=typeof e&&null!==e)throw new TypeError("Super expression must either be null or a function, not "+n(e));t.prototype=Object.create(e&&e.prototype,{
constructor:{value:t,enumerable:!1,writable:!0,configurable:!0}}),e&&(Object.setPrototypeOf?Object.setPrototypeOf(t,e):t.__proto__=e)}(e,t),o(e,[{
key:"getAllContentProperties",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{}
;return this.getAllMigratedProperties("content",t,e,r)}},{key:"getContentProperty",value:function(t,e){
var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{}
;return this.getMigratedProperty("content",t,e,r,n)}},{key:"getAllSpaceProperties",value:function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{}
;return this.getAllMigratedProperties("space",t,e,r)}},{key:"getSpaceProperty",value:function(t,e){
var r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{},n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{}
;return this.getMigratedProperty("space",t,e,r,n)}},{key:"getAllMigratedProperties",value:function(t,e,r,n){var o=this
;return this._getAllProperties.bind(this,t)(e,r,n).then((function(e){if(!o.migrator)return e;var r=[];return e.results.map((function(e){
r.push(o.migrator.migrate(t,e))})),a.default.set(e,"results",r),e}))}},{key:"getMigratedProperty",value:function(t,e,r,n,o){var i=this
;return this._getProperty.bind(this,t)(e,r,n,o).then((function(e){return e&&i.migrator?i.migrator.migrate(t,e):e}))}}]),e}(i.default);e.default=u,t.exports=e.default
},89676:(t,e,r)=>{"use strict";function n(t){return n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},n(t)}function o(){o=function(){return e}
;var t,e={},r=Object.prototype,i=r.hasOwnProperty,a=Object.defineProperty||function(t,e,r){t[e]=r.value
},s="function"==typeof Symbol?Symbol:{},u=s.iterator||"@@iterator",c=s.asyncIterator||"@@asyncIterator",l=s.toStringTag||"@@toStringTag";function f(t,e,r){
return Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}),t[e]}try{f({},"")}catch(t){f=function(t,e,r){return t[e]=r}}
function h(t,e,r,n){var o=e&&e.prototype instanceof b?e:b,i=Object.create(o.prototype),s=new I(n||[]);return a(i,"_invoke",{value:j(t,r,s)}),i}function p(t,e,r){try{
return{type:"normal",arg:t.call(e,r)}}catch(t){return{type:"throw",arg:t}}}e.wrap=h;var d="suspendedStart",y="suspendedYield",v="executing",g="completed",m={}
;function b(){}function w(){}function _(){}var x={};f(x,u,(function(){return this}));var P=Object.getPrototypeOf,S=P&&P(P(L([])));S&&S!==r&&i.call(S,u)&&(x=S)
;var E=_.prototype=b.prototype=Object.create(x);function O(t){["next","throw","return"].forEach((function(e){f(t,e,(function(t){return this._invoke(e,t)}))}))}
function k(t,e){function r(o,a,s,u){var c=p(t[o],t,a);if("throw"!==c.type){var l=c.arg,f=l.value
;return f&&"object"==n(f)&&i.call(f,"__await")?e.resolve(f.__await).then((function(t){r("next",t,s,u)}),(function(t){r("throw",t,s,u)
})):e.resolve(f).then((function(t){l.value=t,s(l)}),(function(t){return r("throw",t,s,u)}))}u(c.arg)}var o;a(this,"_invoke",{value:function(t,n){function i(){
return new e((function(e,o){r(t,n,e,o)}))}return o=o?o.then(i,i):i()}})}function j(e,r,n){var o=d;return function(i,a){
if(o===v)throw Error("Generator is already running");if(o===g){if("throw"===i)throw a;return{value:t,done:!0}}for(n.method=i,n.arg=a;;){var s=n.delegate;if(s){
var u=C(s,n);if(u){if(u===m)continue;return u}}if("next"===n.method)n.sent=n._sent=n.arg;else if("throw"===n.method){if(o===d)throw o=g,n.arg
;n.dispatchException(n.arg)}else"return"===n.method&&n.abrupt("return",n.arg);o=v;var c=p(e,r,n);if("normal"===c.type){if(o=n.done?g:y,c.arg===m)continue;return{
value:c.arg,done:n.done}}"throw"===c.type&&(o=g,n.method="throw",n.arg=c.arg)}}}function C(e,r){var n=r.method,o=e.iterator[n];if(o===t)return r.delegate=null,
"throw"===n&&e.iterator.return&&(r.method="return",r.arg=t,C(e,r),"throw"===r.method)||"return"!==n&&(r.method="throw",
r.arg=new TypeError("The iterator does not provide a '"+n+"' method")),m;var i=p(o,e.iterator,r.arg);if("throw"===i.type)return r.method="throw",r.arg=i.arg,
r.delegate=null,m;var a=i.arg;return a?a.done?(r[e.resultName]=a.value,r.next=e.nextLoc,"return"!==r.method&&(r.method="next",r.arg=t),r.delegate=null,
m):a:(r.method="throw",r.arg=new TypeError("iterator result is not an object"),r.delegate=null,m)}function T(t){var e={tryLoc:t[0]};1 in t&&(e.catchLoc=t[1]),
2 in t&&(e.finallyLoc=t[2],e.afterLoc=t[3]),this.tryEntries.push(e)}function A(t){var e=t.completion||{};e.type="normal",delete e.arg,t.completion=e}function I(t){
this.tryEntries=[{tryLoc:"root"}],t.forEach(T,this),this.reset(!0)}function L(e){if(e||""===e){var r=e[u];if(r)return r.call(e);if("function"==typeof e.next)return e
;if(!isNaN(e.length)){var o=-1,a=function r(){for(;++o<e.length;)if(i.call(e,o))return r.value=e[o],r.done=!1,r;return r.value=t,r.done=!0,r};return a.next=a}}
throw new TypeError(n(e)+" is not iterable")}return w.prototype=_,a(E,"constructor",{value:_,configurable:!0}),a(_,"constructor",{value:w,configurable:!0}),
w.displayName=f(_,l,"GeneratorFunction"),e.isGeneratorFunction=function(t){var e="function"==typeof t&&t.constructor
;return!!e&&(e===w||"GeneratorFunction"===(e.displayName||e.name))},e.mark=function(t){return Object.setPrototypeOf?Object.setPrototypeOf(t,_):(t.__proto__=_,
f(t,l,"GeneratorFunction")),t.prototype=Object.create(E),t},e.awrap=function(t){return{__await:t}},O(k.prototype),f(k.prototype,c,(function(){return this})),
e.AsyncIterator=k,e.async=function(t,r,n,o,i){void 0===i&&(i=Promise);var a=new k(h(t,r,n,o),i);return e.isGeneratorFunction(r)?a:a.next().then((function(t){
return t.done?t.value:a.next()}))},O(E),f(E,l,"Generator"),f(E,u,(function(){return this})),f(E,"toString",(function(){return"[object Generator]"})),
e.keys=function(t){var e=Object(t),r=[];for(var n in e)r.push(n);return r.reverse(),function t(){for(;r.length;){var n=r.pop();if(n in e)return t.value=n,t.done=!1,t
}return t.done=!0,t}},e.values=L,I.prototype={constructor:I,reset:function(e){if(this.prev=0,this.next=0,this.sent=this._sent=t,this.done=!1,this.delegate=null,
this.method="next",this.arg=t,this.tryEntries.forEach(A),!e)for(var r in this)"t"===r.charAt(0)&&i.call(this,r)&&!isNaN(+r.slice(1))&&(this[r]=t)},stop:function(){
this.done=!0;var t=this.tryEntries[0].completion;if("throw"===t.type)throw t.arg;return this.rval},dispatchException:function(e){if(this.done)throw e;var r=this
;function n(n,o){return s.type="throw",s.arg=e,r.next=n,o&&(r.method="next",r.arg=t),!!o}for(var o=this.tryEntries.length-1;o>=0;--o){
var a=this.tryEntries[o],s=a.completion;if("root"===a.tryLoc)return n("end");if(a.tryLoc<=this.prev){var u=i.call(a,"catchLoc"),c=i.call(a,"finallyLoc");if(u&&c){
if(this.prev<a.catchLoc)return n(a.catchLoc,!0);if(this.prev<a.finallyLoc)return n(a.finallyLoc)}else if(u){if(this.prev<a.catchLoc)return n(a.catchLoc,!0)}else{
if(!c)throw Error("try statement without catch or finally");if(this.prev<a.finallyLoc)return n(a.finallyLoc)}}}},abrupt:function(t,e){
for(var r=this.tryEntries.length-1;r>=0;--r){var n=this.tryEntries[r];if(n.tryLoc<=this.prev&&i.call(n,"finallyLoc")&&this.prev<n.finallyLoc){var o=n;break}}
o&&("break"===t||"continue"===t)&&o.tryLoc<=e&&e<=o.finallyLoc&&(o=null);var a=o?o.completion:{};return a.type=t,a.arg=e,o?(this.method="next",
this.next=o.finallyLoc,m):this.complete(a)},complete:function(t,e){if("throw"===t.type)throw t.arg
;return"break"===t.type||"continue"===t.type?this.next=t.arg:"return"===t.type?(this.rval=this.arg=t.arg,this.method="return",
this.next="end"):"normal"===t.type&&e&&(this.next=e),m},finish:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.finallyLoc===t)return this.complete(r.completion,r.afterLoc),A(r),m}},catch:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.tryLoc===t){var n=r.completion;if("throw"===n.type){var o=n.arg;A(r)}return o}}throw Error("illegal catch attempt")},delegateYield:function(e,r,n){
return this.delegate={iterator:L(e),resultName:r,nextLoc:n},"next"===this.method&&(this.arg=t),m}},e}function i(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,a(n.key),n)}}function a(t){var e=function(t,e){
if("object"!=n(t)||!t)return t;var r=t[Symbol.toPrimitive];if(void 0!==r){var o=r.call(t,e||"default");if("object"!=n(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==n(e)?e:e+""}
Object.defineProperty(e,"__esModule",{value:!0}),e.SpacePermissions=void 0;var s=r(95006),u=function(){return t=function t(e){!function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.extendedConfluence=e,this.confluenceApi=e.confluenceApi},(e=[{
key:"getSpacePermissionsByKey",value:function(t,e){return s.__awaiter(this,void 0,void 0,o().mark((function r(){var n;return o().wrap((function(r){
for(;;)switch(r.prev=r.next){case 0:return r.next=2,this.extendedConfluence.space.getSpaceByKey(t);case 2:if(n=r.sent){r.next=5;break}return r.abrupt("return",[])
;case 5:return r.abrupt("return",this.getAllSpacePermissions(n.id,e));case 6:case"end":return r.stop()}}),r,this)})))}},{key:"getAllSpacePermissions",
value:function(t,e,r){return s.__awaiter(this,void 0,void 0,o().mark((function n(){var i,a,s,u;return o().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:
return n.next=2,this.getSpacePermissions(t,e,r);case 2:if(i=n.sent,a=i.results,!(s=i._links).next){n.next=12;break}return n.next=8,
this.getAllSpacePermissions(t,e,s.next);case 8:return u=n.sent,n.abrupt("return",a.concat(u));case 12:return n.abrupt("return",a);case 13:case"end":return n.stop()}
}),n,this)})))}},{key:"getSpacePermissions",value:function(t,e,r){return s.__awaiter(this,void 0,void 0,o().mark((function n(){var i=this
;return o().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:return n.abrupt("return",this.extendedConfluence.sendPaginationRequest((function(){
return i.confluenceApi.spacePermissions.getSpacePermissions(t,e)}),r));case 1:case"end":return n.stop()}}),n,this)})))}}])&&i(t.prototype,e),r&&i(t,r),
Object.defineProperty(t,"prototype",{writable:!1}),t;var t,e,r}();e.SpacePermissions=u},89889:(t,e)=>{"use strict";Object.defineProperty(e,"__esModule",{value:!0})},
93501:(t,e,r)=>{function n(t){return n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},n(t)}
var o="__lodash_hash_undefined__",i="[object Function]",a="[object GeneratorFunction]",s=/\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/,u=/^\w*$/,c=/^\./,l=/[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g,f=/\\(\\)?/g,h=/^\[object .+?Constructor\]$/,p="object"==(void 0===r.g?"undefined":n(r.g))&&r.g&&r.g.Object===Object&&r.g,d="object"==("undefined"==typeof self?"undefined":n(self))&&self&&self.Object===Object&&self,y=p||d||Function("return this")()
;var v,g=Array.prototype,m=Function.prototype,b=Object.prototype,w=y["__core-js_shared__"],_=(v=/[^.]+$/.exec(w&&w.keys&&w.keys.IE_PROTO||""))?"Symbol(src)_1."+v:"",x=m.toString,P=b.hasOwnProperty,S=b.toString,E=RegExp("^"+x.call(P).replace(/[\\^$.*+?()[\]{}|]/g,"\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g,"$1.*?")+"$"),O=y.Symbol,k=g.splice,j=M(y,"Map"),C=M(Object,"create"),T=O?O.prototype:void 0,A=T?T.toString:void 0
;function I(t){var e=-1,r=t?t.length:0;for(this.clear();++e<r;){var n=t[e];this.set(n[0],n[1])}}function L(t){var e=-1,r=t?t.length:0;for(this.clear();++e<r;){
var n=t[e];this.set(n[0],n[1])}}function N(t){var e=-1,r=t?t.length:0;for(this.clear();++e<r;){var n=t[e];this.set(n[0],n[1])}}function R(t,e){
for(var r,n,o=t.length;o--;)if((r=t[o][0])===(n=e)||r!=r&&n!=n)return o;return-1}function D(t,e){var r;e=function(t,e){if(q(t))return!1;var r=n(t)
;if("number"==r||"symbol"==r||"boolean"==r||null==t||K(t))return!0;return u.test(t)||!s.test(t)||null!=e&&t in Object(e)}(e,t)?[e]:q(r=e)?r:G(r)
;for(var o=0,i=e.length;null!=t&&o<i;)t=t[V(e[o++])];return o&&o==i?t:void 0}function B(t){if(!Z(t)||(e=t,_&&_ in e))return!1;var e,r=function(t){
var e=Z(t)?S.call(t):"";return e==i||e==a}(t)||function(t){var e=!1;if(null!=t&&"function"!=typeof t.toString)try{e=!!(t+"")}catch(t){}return e}(t)?E:h
;return r.test(function(t){if(null!=t){try{return x.call(t)}catch(t){}try{return t+""}catch(t){}}return""}(t))}function F(t,e){var r,o,i=t.__data__
;return("string"==(o=n(r=e))||"number"==o||"symbol"==o||"boolean"==o?"__proto__"!==r:null===r)?i["string"==typeof e?"string":"hash"]:i.map}function M(t,e){
var r=function(t,e){return null==t?void 0:t[e]}(t,e);return B(r)?r:void 0}I.prototype.clear=function(){this.__data__=C?C(null):{}},I.prototype.delete=function(t){
return this.has(t)&&delete this.__data__[t]},I.prototype.get=function(t){var e=this.__data__;if(C){var r=e[t];return r===o?void 0:r}return P.call(e,t)?e[t]:void 0},
I.prototype.has=function(t){var e=this.__data__;return C?void 0!==e[t]:P.call(e,t)},I.prototype.set=function(t,e){return this.__data__[t]=C&&void 0===e?o:e,this},
L.prototype.clear=function(){this.__data__=[]},L.prototype.delete=function(t){var e=this.__data__,r=R(e,t);return!(r<0)&&(r==e.length-1?e.pop():k.call(e,r,1),!0)},
L.prototype.get=function(t){var e=this.__data__,r=R(e,t);return r<0?void 0:e[r][1]},L.prototype.has=function(t){return R(this.__data__,t)>-1},
L.prototype.set=function(t,e){var r=this.__data__,n=R(r,t);return n<0?r.push([t,e]):r[n][1]=e,this},N.prototype.clear=function(){this.__data__={hash:new I,
map:new(j||L),string:new I}},N.prototype.delete=function(t){return F(this,t).delete(t)},N.prototype.get=function(t){return F(this,t).get(t)},
N.prototype.has=function(t){return F(this,t).has(t)},N.prototype.set=function(t,e){return F(this,t).set(t,e),this};var G=U((function(t){var e
;t=null==(e=t)?"":function(t){if("string"==typeof t)return t;if(K(t))return A?A.call(t):"";var e=t+"";return"0"==e&&1/t==-1/0?"-0":e}(e);var r=[]
;return c.test(t)&&r.push(""),t.replace(l,(function(t,e,n,o){r.push(n?o.replace(f,"$1"):e||t)})),r}));function V(t){if("string"==typeof t||K(t))return t;var e=t+""
;return"0"==e&&1/t==-1/0?"-0":e}function U(t,e){if("function"!=typeof t||e&&"function"!=typeof e)throw new TypeError("Expected a function");var r=function(){
var n=arguments,o=e?e.apply(this,n):n[0],i=r.cache;if(i.has(o))return i.get(o);var a=t.apply(this,n);return r.cache=i.set(o,a),a};return r.cache=new(U.Cache||N),r}
U.Cache=N;var q=Array.isArray;function Z(t){var e=n(t);return!!t&&("object"==e||"function"==e)}function K(t){return"symbol"==n(t)||function(t){
return!!t&&"object"==n(t)}(t)&&"[object Symbol]"==S.call(t)}t.exports=function(t,e,r){var n=null==t?void 0:D(t,e);return void 0===n?r:n}},93720:(t,e,r)=>{
"use strict";function n(t){return n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},n(t)}function o(){o=function(){return e}
;var t,e={},r=Object.prototype,i=r.hasOwnProperty,a=Object.defineProperty||function(t,e,r){t[e]=r.value
},s="function"==typeof Symbol?Symbol:{},u=s.iterator||"@@iterator",c=s.asyncIterator||"@@asyncIterator",l=s.toStringTag||"@@toStringTag";function f(t,e,r){
return Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}),t[e]}try{f({},"")}catch(t){f=function(t,e,r){return t[e]=r}}
function h(t,e,r,n){var o=e&&e.prototype instanceof b?e:b,i=Object.create(o.prototype),s=new I(n||[]);return a(i,"_invoke",{value:j(t,r,s)}),i}function p(t,e,r){try{
return{type:"normal",arg:t.call(e,r)}}catch(t){return{type:"throw",arg:t}}}e.wrap=h;var d="suspendedStart",y="suspendedYield",v="executing",g="completed",m={}
;function b(){}function w(){}function _(){}var x={};f(x,u,(function(){return this}));var P=Object.getPrototypeOf,S=P&&P(P(L([])));S&&S!==r&&i.call(S,u)&&(x=S)
;var E=_.prototype=b.prototype=Object.create(x);function O(t){["next","throw","return"].forEach((function(e){f(t,e,(function(t){return this._invoke(e,t)}))}))}
function k(t,e){function r(o,a,s,u){var c=p(t[o],t,a);if("throw"!==c.type){var l=c.arg,f=l.value
;return f&&"object"==n(f)&&i.call(f,"__await")?e.resolve(f.__await).then((function(t){r("next",t,s,u)}),(function(t){r("throw",t,s,u)
})):e.resolve(f).then((function(t){l.value=t,s(l)}),(function(t){return r("throw",t,s,u)}))}u(c.arg)}var o;a(this,"_invoke",{value:function(t,n){function i(){
return new e((function(e,o){r(t,n,e,o)}))}return o=o?o.then(i,i):i()}})}function j(e,r,n){var o=d;return function(i,a){
if(o===v)throw Error("Generator is already running");if(o===g){if("throw"===i)throw a;return{value:t,done:!0}}for(n.method=i,n.arg=a;;){var s=n.delegate;if(s){
var u=C(s,n);if(u){if(u===m)continue;return u}}if("next"===n.method)n.sent=n._sent=n.arg;else if("throw"===n.method){if(o===d)throw o=g,n.arg
;n.dispatchException(n.arg)}else"return"===n.method&&n.abrupt("return",n.arg);o=v;var c=p(e,r,n);if("normal"===c.type){if(o=n.done?g:y,c.arg===m)continue;return{
value:c.arg,done:n.done}}"throw"===c.type&&(o=g,n.method="throw",n.arg=c.arg)}}}function C(e,r){var n=r.method,o=e.iterator[n];if(o===t)return r.delegate=null,
"throw"===n&&e.iterator.return&&(r.method="return",r.arg=t,C(e,r),"throw"===r.method)||"return"!==n&&(r.method="throw",
r.arg=new TypeError("The iterator does not provide a '"+n+"' method")),m;var i=p(o,e.iterator,r.arg);if("throw"===i.type)return r.method="throw",r.arg=i.arg,
r.delegate=null,m;var a=i.arg;return a?a.done?(r[e.resultName]=a.value,r.next=e.nextLoc,"return"!==r.method&&(r.method="next",r.arg=t),r.delegate=null,
m):a:(r.method="throw",r.arg=new TypeError("iterator result is not an object"),r.delegate=null,m)}function T(t){var e={tryLoc:t[0]};1 in t&&(e.catchLoc=t[1]),
2 in t&&(e.finallyLoc=t[2],e.afterLoc=t[3]),this.tryEntries.push(e)}function A(t){var e=t.completion||{};e.type="normal",delete e.arg,t.completion=e}function I(t){
this.tryEntries=[{tryLoc:"root"}],t.forEach(T,this),this.reset(!0)}function L(e){if(e||""===e){var r=e[u];if(r)return r.call(e);if("function"==typeof e.next)return e
;if(!isNaN(e.length)){var o=-1,a=function r(){for(;++o<e.length;)if(i.call(e,o))return r.value=e[o],r.done=!1,r;return r.value=t,r.done=!0,r};return a.next=a}}
throw new TypeError(n(e)+" is not iterable")}return w.prototype=_,a(E,"constructor",{value:_,configurable:!0}),a(_,"constructor",{value:w,configurable:!0}),
w.displayName=f(_,l,"GeneratorFunction"),e.isGeneratorFunction=function(t){var e="function"==typeof t&&t.constructor
;return!!e&&(e===w||"GeneratorFunction"===(e.displayName||e.name))},e.mark=function(t){return Object.setPrototypeOf?Object.setPrototypeOf(t,_):(t.__proto__=_,
f(t,l,"GeneratorFunction")),t.prototype=Object.create(E),t},e.awrap=function(t){return{__await:t}},O(k.prototype),f(k.prototype,c,(function(){return this})),
e.AsyncIterator=k,e.async=function(t,r,n,o,i){void 0===i&&(i=Promise);var a=new k(h(t,r,n,o),i);return e.isGeneratorFunction(r)?a:a.next().then((function(t){
return t.done?t.value:a.next()}))},O(E),f(E,l,"Generator"),f(E,u,(function(){return this})),f(E,"toString",(function(){return"[object Generator]"})),
e.keys=function(t){var e=Object(t),r=[];for(var n in e)r.push(n);return r.reverse(),function t(){for(;r.length;){var n=r.pop();if(n in e)return t.value=n,t.done=!1,t
}return t.done=!0,t}},e.values=L,I.prototype={constructor:I,reset:function(e){if(this.prev=0,this.next=0,this.sent=this._sent=t,this.done=!1,this.delegate=null,
this.method="next",this.arg=t,this.tryEntries.forEach(A),!e)for(var r in this)"t"===r.charAt(0)&&i.call(this,r)&&!isNaN(+r.slice(1))&&(this[r]=t)},stop:function(){
this.done=!0;var t=this.tryEntries[0].completion;if("throw"===t.type)throw t.arg;return this.rval},dispatchException:function(e){if(this.done)throw e;var r=this
;function n(n,o){return s.type="throw",s.arg=e,r.next=n,o&&(r.method="next",r.arg=t),!!o}for(var o=this.tryEntries.length-1;o>=0;--o){
var a=this.tryEntries[o],s=a.completion;if("root"===a.tryLoc)return n("end");if(a.tryLoc<=this.prev){var u=i.call(a,"catchLoc"),c=i.call(a,"finallyLoc");if(u&&c){
if(this.prev<a.catchLoc)return n(a.catchLoc,!0);if(this.prev<a.finallyLoc)return n(a.finallyLoc)}else if(u){if(this.prev<a.catchLoc)return n(a.catchLoc,!0)}else{
if(!c)throw Error("try statement without catch or finally");if(this.prev<a.finallyLoc)return n(a.finallyLoc)}}}},abrupt:function(t,e){
for(var r=this.tryEntries.length-1;r>=0;--r){var n=this.tryEntries[r];if(n.tryLoc<=this.prev&&i.call(n,"finallyLoc")&&this.prev<n.finallyLoc){var o=n;break}}
o&&("break"===t||"continue"===t)&&o.tryLoc<=e&&e<=o.finallyLoc&&(o=null);var a=o?o.completion:{};return a.type=t,a.arg=e,o?(this.method="next",
this.next=o.finallyLoc,m):this.complete(a)},complete:function(t,e){if("throw"===t.type)throw t.arg
;return"break"===t.type||"continue"===t.type?this.next=t.arg:"return"===t.type?(this.rval=this.arg=t.arg,this.method="return",
this.next="end"):"normal"===t.type&&e&&(this.next=e),m},finish:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.finallyLoc===t)return this.complete(r.completion,r.afterLoc),A(r),m}},catch:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.tryLoc===t){var n=r.completion;if("throw"===n.type){var o=n.arg;A(r)}return o}}throw Error("illegal catch attempt")},delegateYield:function(e,r,n){
return this.delegate={iterator:L(e),resultName:r,nextLoc:n},"next"===this.method&&(this.arg=t),m}},e}function i(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,a(n.key),n)}}function a(t){var e=function(t,e){
if("object"!=n(t)||!t)return t;var r=t[Symbol.toPrimitive];if(void 0!==r){var o=r.call(t,e||"default");if("object"!=n(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==n(e)?e:e+""}
Object.defineProperty(e,"__esModule",{value:!0}),e.Version=void 0;var s=r(95006),u=r(28271),c=function(){return t=function t(e){!function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.extendedConfluence=e,this.confluenceApi=e.confluenceApi},(e=[{
key:"getContentVersions",value:function(t,e){return s.__awaiter(this,void 0,void 0,o().mark((function r(){var n;return o().wrap((function(r){
for(;;)switch(r.prev=r.next){case 0:return r.next=2,this.extendedConfluence.content.getContentType(t);case 2:if(n=r.sent){r.next=5;break}
return r.abrupt("return",void 0);case 5:
r.t0=n,r.next=r.t0===u.ContentType.Attachment?8:r.t0===u.ContentType.BlogPost?9:r.t0===u.ContentType.Page?10:r.t0===u.ContentType.Custom?11:r.t0===u.ContentType.FooterComment?12:r.t0===u.ContentType.InlineComment?13:14
;break;case 8:return r.abrupt("return",this.confluenceApi.version.getAttachmentVersions(t,e));case 9:
return r.abrupt("return",this.confluenceApi.version.getBlogPostVersions(t,e));case 10:return r.abrupt("return",this.confluenceApi.version.getPageVersions(t,e))
;case 11:return r.abrupt("return",this.confluenceApi.version.getCustomContentVersions(t,e));case 12:
return r.abrupt("return",this.confluenceApi.version.getFooterCommentVersions(t,e));case 13:
return r.abrupt("return",this.confluenceApi.version.getInlineCommentVersions(t,e));case 14:return r.abrupt("return",void 0);case 15:case"end":return r.stop()}
}),r,this)})))}}])&&i(t.prototype,e),r&&i(t,r),Object.defineProperty(t,"prototype",{writable:!1}),t;var t,e,r}();e.Version=c},93891:(t,e,r)=>{t.exports=r(16293)(696)
},95006:(t,e,r)=>{"use strict";function n(t){return n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},n(t)}r.r(e),r.d(e,{__assign:()=>a,__asyncDelegator:()=>_,
__asyncGenerator:()=>w,__asyncValues:()=>x,__await:()=>b,__awaiter:()=>f,__classPrivateFieldGet:()=>O,__classPrivateFieldSet:()=>k,__createBinding:()=>p,
__decorate:()=>u,__exportStar:()=>d,__extends:()=>i,__generator:()=>h,__importDefault:()=>E,__importStar:()=>S,__makeTemplateObject:()=>P,__metadata:()=>l,
__param:()=>c,__read:()=>v,__rest:()=>s,__spread:()=>g,__spreadArrays:()=>m,__values:()=>y});var o=function(t,e){return o=Object.setPrototypeOf||{__proto__:[]
}instanceof Array&&function(t,e){t.__proto__=e}||function(t,e){for(var r in e)e.hasOwnProperty(r)&&(t[r]=e[r])},o(t,e)};function i(t,e){function r(){
this.constructor=t}o(t,e),t.prototype=null===e?Object.create(e):(r.prototype=e.prototype,new r)}var a=function(){return a=Object.assign||function(t){
for(var e,r=1,n=arguments.length;r<n;r++)for(var o in e=arguments[r])Object.prototype.hasOwnProperty.call(e,o)&&(t[o]=e[o]);return t},a.apply(this,arguments)}
;function s(t,e){var r={};for(var n in t)Object.prototype.hasOwnProperty.call(t,n)&&e.indexOf(n)<0&&(r[n]=t[n])
;if(null!=t&&"function"==typeof Object.getOwnPropertySymbols){var o=0
;for(n=Object.getOwnPropertySymbols(t);o<n.length;o++)e.indexOf(n[o])<0&&Object.prototype.propertyIsEnumerable.call(t,n[o])&&(r[n[o]]=t[n[o]])}return r}
function u(t,e,r,o){var i,a=arguments.length,s=a<3?e:null===o?o=Object.getOwnPropertyDescriptor(e,r):o
;if("object"===("undefined"==typeof Reflect?"undefined":n(Reflect))&&"function"==typeof Reflect.decorate)s=Reflect.decorate(t,e,r,o);else for(var u=t.length-1;u>=0;u--)(i=t[u])&&(s=(a<3?i(s):a>3?i(e,r,s):i(e,r))||s)
;return a>3&&s&&Object.defineProperty(e,r,s),s}function c(t,e){return function(r,n){e(r,n,t)}}function l(t,e){
if("object"===("undefined"==typeof Reflect?"undefined":n(Reflect))&&"function"==typeof Reflect.metadata)return Reflect.metadata(t,e)}function f(t,e,r,n){
return new(r||(r=Promise))((function(o,i){function a(t){try{u(n.next(t))}catch(t){i(t)}}function s(t){try{u(n.throw(t))}catch(t){i(t)}}function u(t){var e
;t.done?o(t.value):(e=t.value,e instanceof r?e:new r((function(t){t(e)}))).then(a,s)}u((n=n.apply(t,e||[])).next())}))}function h(t,e){var r,n,o,i,a={label:0,
sent:function(){if(1&o[0])throw o[1];return o[1]},trys:[],ops:[]};return i={next:s(0),throw:s(1),return:s(2)},
"function"==typeof Symbol&&(i[Symbol.iterator]=function(){return this}),i;function s(i){return function(s){return function(i){
if(r)throw new TypeError("Generator is already executing.");for(;a;)try{if(r=1,n&&(o=2&i[0]?n.return:i[0]?n.throw||((o=n.return)&&o.call(n),
0):n.next)&&!(o=o.call(n,i[1])).done)return o;switch(n=0,o&&(i=[2&i[0],o.value]),i[0]){case 0:case 1:o=i;break;case 4:return a.label++,{value:i[1],done:!1};case 5:
a.label++,n=i[1],i=[0];continue;case 7:i=a.ops.pop(),a.trys.pop();continue;default:if(!(o=a.trys,(o=o.length>0&&o[o.length-1])||6!==i[0]&&2!==i[0])){a=0;continue}
if(3===i[0]&&(!o||i[1]>o[0]&&i[1]<o[3])){a.label=i[1];break}if(6===i[0]&&a.label<o[1]){a.label=o[1],o=i;break}if(o&&a.label<o[2]){a.label=o[2],a.ops.push(i);break}
o[2]&&a.ops.pop(),a.trys.pop();continue}i=e.call(t,a)}catch(t){i=[6,t],n=0}finally{r=o=0}if(5&i[0])throw i[1];return{value:i[0]?i[1]:void 0,done:!0}}([i,s])}}}
function p(t,e,r,n){void 0===n&&(n=r),t[n]=e[r]}function d(t,e){for(var r in t)"default"===r||e.hasOwnProperty(r)||(e[r]=t[r])}function y(t){
var e="function"==typeof Symbol&&Symbol.iterator,r=e&&t[e],n=0;if(r)return r.call(t);if(t&&"number"==typeof t.length)return{next:function(){
return t&&n>=t.length&&(t=void 0),{value:t&&t[n++],done:!t}}};throw new TypeError(e?"Object is not iterable.":"Symbol.iterator is not defined.")}function v(t,e){
var r="function"==typeof Symbol&&t[Symbol.iterator];if(!r)return t;var n,o,i=r.call(t),a=[];try{for(;(void 0===e||e-- >0)&&!(n=i.next()).done;)a.push(n.value)
}catch(t){o={error:t}}finally{try{n&&!n.done&&(r=i.return)&&r.call(i)}finally{if(o)throw o.error}}return a}function g(){
for(var t=[],e=0;e<arguments.length;e++)t=t.concat(v(arguments[e]));return t}function m(){for(var t=0,e=0,r=arguments.length;e<r;e++)t+=arguments[e].length
;var n=Array(t),o=0;for(e=0;e<r;e++)for(var i=arguments[e],a=0,s=i.length;a<s;a++,o++)n[o]=i[a];return n}function b(t){return this instanceof b?(this.v=t,
this):new b(t)}function w(t,e,r){if(!Symbol.asyncIterator)throw new TypeError("Symbol.asyncIterator is not defined.");var n,o=r.apply(t,e||[]),i=[];return n={},
a("next"),a("throw"),a("return"),n[Symbol.asyncIterator]=function(){return this},n;function a(t){o[t]&&(n[t]=function(e){return new Promise((function(r,n){
i.push([t,e,r,n])>1||s(t,e)}))})}function s(t,e){try{(r=o[t](e)).value instanceof b?Promise.resolve(r.value.v).then(u,c):l(i[0][2],r)}catch(t){l(i[0][3],t)}var r}
function u(t){s("next",t)}function c(t){s("throw",t)}function l(t,e){t(e),i.shift(),i.length&&s(i[0][0],i[0][1])}}function _(t){var e,r;return e={},n("next"),
n("throw",(function(t){throw t})),n("return"),e[Symbol.iterator]=function(){return this},e;function n(n,o){e[n]=t[n]?function(e){return(r=!r)?{value:b(t[n](e)),
done:"return"===n}:o?o(e):e}:o}}function x(t){if(!Symbol.asyncIterator)throw new TypeError("Symbol.asyncIterator is not defined.");var e,r=t[Symbol.asyncIterator]
;return r?r.call(t):(t=y(t),e={},n("next"),n("throw"),n("return"),e[Symbol.asyncIterator]=function(){return this},e);function n(r){e[r]=t[r]&&function(e){
return new Promise((function(n,o){(function(t,e,r,n){Promise.resolve(n).then((function(e){t({value:e,done:r})}),e)})(n,o,(e=t[r](e)).done,e.value)}))}}}
function P(t,e){return Object.defineProperty?Object.defineProperty(t,"raw",{value:e}):t.raw=e,t}function S(t){if(t&&t.__esModule)return t;var e={}
;if(null!=t)for(var r in t)Object.hasOwnProperty.call(t,r)&&(e[r]=t[r]);return e.default=t,e}function E(t){return t&&t.__esModule?t:{default:t}}function O(t,e){
if(!e.has(t))throw new TypeError("attempted to get private field on non-instance");return e.get(t)}function k(t,e,r){
if(!e.has(t))throw new TypeError("attempted to set private field on non-instance");return e.set(t,r),r}},96200:(t,e,r)=>{"use strict";function n(t){
return n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},n(t)}function o(t){
return o="function"==typeof Symbol&&"symbol"===n(Symbol.iterator)?function(t){return n(t)}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":n(t)},o(t)}e.log=function(){var t
;return"object"===("undefined"==typeof console?"undefined":o(console))&&console.log&&(t=console).log.apply(t,arguments)},e.formatArgs=function(e){
if(e[0]=(this.useColors?"%c":"")+this.namespace+(this.useColors?" %c":" ")+e[0]+(this.useColors?"%c ":" ")+"+"+t.exports.humanize(this.diff),!this.useColors)return
;var r="color: "+this.color;e.splice(1,0,r,"color: inherit");var n=0,o=0;e[0].replace(/%[a-zA-Z%]/g,(function(t){"%%"!==t&&(n++,"%c"===t&&(o=n))})),e.splice(o,0,r)},
e.save=function(t){try{t?e.storage.setItem("debug",t):e.storage.removeItem("debug")}catch(t){}},e.load=function(){var t;try{t=e.storage.getItem("debug")}catch(t){}
!t&&"undefined"!=typeof process&&"env"in process&&(t=process.env.DEBUG);return t},e.useColors=function(){
if("undefined"!=typeof window&&window.process&&("renderer"===window.process.type||window.process.__nwjs))return!0
;if("undefined"!=typeof navigator&&navigator.userAgent&&navigator.userAgent.toLowerCase().match(/(edge|trident)\/(\d+)/))return!1
;return"undefined"!=typeof document&&document.documentElement&&document.documentElement.style&&document.documentElement.style.WebkitAppearance||"undefined"!=typeof window&&window.console&&(window.console.firebug||window.console.exception&&window.console.table)||"undefined"!=typeof navigator&&navigator.userAgent&&navigator.userAgent.toLowerCase().match(/firefox\/(\d+)/)&&parseInt(RegExp.$1,10)>=31||"undefined"!=typeof navigator&&navigator.userAgent&&navigator.userAgent.toLowerCase().match(/applewebkit\/(\d+)/)
},e.storage=function(){try{return localStorage}catch(t){}
}(),e.colors=["#0000CC","#0000FF","#0033CC","#0033FF","#0066CC","#0066FF","#0099CC","#0099FF","#00CC00","#00CC33","#00CC66","#00CC99","#00CCCC","#00CCFF","#3300CC","#3300FF","#3333CC","#3333FF","#3366CC","#3366FF","#3399CC","#3399FF","#33CC00","#33CC33","#33CC66","#33CC99","#33CCCC","#33CCFF","#6600CC","#6600FF","#6633CC","#6633FF","#66CC00","#66CC33","#9900CC","#9900FF","#9933CC","#9933FF","#99CC00","#99CC33","#CC0000","#CC0033","#CC0066","#CC0099","#CC00CC","#CC00FF","#CC3300","#CC3333","#CC3366","#CC3399","#CC33CC","#CC33FF","#CC6600","#CC6633","#CC9900","#CC9933","#CCCC00","#CCCC33","#FF0000","#FF0033","#FF0066","#FF0099","#FF00CC","#FF00FF","#FF3300","#FF3333","#FF3366","#FF3399","#FF33CC","#FF33FF","#FF6600","#FF6633","#FF9900","#FF9933","#FFCC00","#FFCC33"],
t.exports=r(97399)(e),t.exports.formatters.j=function(t){try{return JSON.stringify(t)}catch(t){return"[UnexpectedJSONParseError]: "+t.message}}},97399:(t,e,r)=>{
"use strict";t.exports=function(t){function e(t){for(var e=0,r=0;r<t.length;r++)e=(e<<5)-e+t.charCodeAt(r),e|=0;return n.colors[Math.abs(e)%n.colors.length]}
function n(t){var r;function a(){if(a.enabled){for(var t=arguments.length,e=new Array(t),o=0;o<t;o++)e[o]=arguments[o];var i=a,s=Number(new Date),u=s-(r||s)
;i.diff=u,i.prev=r,i.curr=s,r=s,e[0]=n.coerce(e[0]),"string"!=typeof e[0]&&e.unshift("%O");var c=0;e[0]=e[0].replace(/%([a-zA-Z%])/g,(function(t,r){
if("%%"===t)return t;c++;var o=n.formatters[r];if("function"==typeof o){var a=e[c];t=o.call(i,a),e.splice(c,1),c--}return t})),n.formatArgs.call(i,e),
(i.log||n.log).apply(i,e)}}return a.namespace=t,a.enabled=n.enabled(t),a.useColors=n.useColors(),a.color=e(t),a.destroy=o,a.extend=i,
"function"==typeof n.init&&n.init(a),n.instances.push(a),a}function o(){var t=n.instances.indexOf(this);return-1!==t&&(n.instances.splice(t,1),!0)}function i(t,e){
return n(this.namespace+(void 0===e?":":e)+t)}return n.debug=n,n.default=n,n.coerce=function(t){if(t instanceof Error)return t.stack||t.message;return t},
n.disable=function(){n.enable("")},n.enable=function(t){var e;n.save(t),n.names=[],n.skips=[];var r=("string"==typeof t?t:"").split(/[\s,]+/),o=r.length
;for(e=0;e<o;e++)r[e]&&("-"===(t=r[e].replace(/\*/g,".*?"))[0]?n.skips.push(new RegExp("^"+t.substr(1)+"$")):n.names.push(new RegExp("^"+t+"$")))
;for(e=0;e<n.instances.length;e++){var i=n.instances[e];i.enabled=n.enabled(i.namespace)}},n.enabled=function(t){if("*"===t[t.length-1])return!0;var e,r;for(e=0,
r=n.skips.length;e<r;e++)if(n.skips[e].test(t))return!1;for(e=0,r=n.names.length;e<r;e++)if(n.names[e].test(t))return!0;return!1},n.humanize=r(8474),
Object.keys(t).forEach((function(e){n[e]=t[e]})),n.instances=[],n.names=[],n.skips=[],n.formatters={},n.selectColor=e,n.enable(n.load()),n}},98852:(t,e)=>{
"use strict";function r(t){return r="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},r(t)}function n(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,o(n.key),n)}}function o(t){var e=function(t,e){
if("object"!=r(t)||!t)return t;var n=t[Symbol.toPrimitive];if(void 0!==n){var o=n.call(t,e||"default");if("object"!=r(o))return o
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==r(e)?e:e+""}
Object.defineProperty(e,"__esModule",{value:!0}),e.ContentProperties=void 0;var i=function(){return t=function t(e){!function(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.client=e},(e=[{key:"getContentPropertiesForPage",value:function(t,e){
var r={url:"/api/v2/pages/".concat(t,"/properties"),type:"GET",queryParams:{key:null==e?void 0:e.key,sort:null==e?void 0:e.sort,cursor:null==e?void 0:e.cursor,
limit:null==e?void 0:e.limit}};return this.client.sendRequest(r)}},{key:"createContentPropertyForPage",value:function(t,e){var r={
url:"/api/v2/pages/".concat(t,"/properties"),type:"POST",requestBody:{key:e.key,value:e.value}};return this.client.sendRequest(r)}},{
key:"getContentPropertyForPageById",value:function(t,e){var r={url:"/api/v2/pages/".concat(t,"/properties/").concat(e),type:"GET"};return this.client.sendRequest(r)}
},{key:"updateContentPropertyForPageById",value:function(t,e,r){var n={url:"/api/v2/pages/".concat(t,"/properties/").concat(e),type:"PUT",requestBody:{key:r.key,
value:r.value,version:r.version}};return this.client.sendRequest(n)}},{key:"deleteContentPropertyForPageById",value:function(t,e){var r={
url:"/api/v2/pages/".concat(t,"/properties/").concat(e),type:"DELETE"};return this.client.sendRequest(r)}},{key:"getContentPropertiesForBlogPost",
value:function(t,e){var r={url:"/api/v2/blogposts/".concat(t,"/properties"),type:"GET",queryParams:{key:null==e?void 0:e.key,sort:null==e?void 0:e.sort,
cursor:null==e?void 0:e.cursor,limit:null==e?void 0:e.limit}};return this.client.sendRequest(r)}},{key:"createContentPropertyForBlogPost",value:function(t,e){var r={
url:"/api/v2/blogposts/".concat(t,"/properties"),type:"POST",requestBody:{key:e.key,value:e.value}};return this.client.sendRequest(r)}},{
key:"getContentPropertyForBlogPostById",value:function(t,e){var r={url:"/api/v2/blogposts/".concat(t,"/properties/").concat(e),type:"GET"}
;return this.client.sendRequest(r)}},{key:"updateContentPropertyForBlogPostById",value:function(t,e,r){var n={
url:"/api/v2/blogposts/".concat(t,"/properties/").concat(e),type:"PUT",requestBody:{key:r.key,value:r.value,version:r.version}};return this.client.sendRequest(n)}},{
key:"deleteContentPropertyForBlogPostById",value:function(t,e){var r={url:"/api/v2/blogposts/".concat(t,"/properties/").concat(e),type:"DELETE"}
;return this.client.sendRequest(r)}}])&&n(t.prototype,e),r&&n(t,r),Object.defineProperty(t,"prototype",{writable:!1}),t;var t,e,r}();e.ContentProperties=i}},e={}
;function r(n){var o=e[n];if(void 0!==o)return o.exports;var i=e[n]={id:n,loaded:!1,exports:{}};return t[n].call(i.exports,i,i.exports,r),i.loaded=!0,i.exports}
r.d=(t,e)=>{for(var n in e)r.o(e,n)&&!r.o(t,n)&&Object.defineProperty(t,n,{enumerable:!0,get:e[n]})},r.g=function(){if("object"==typeof globalThis)return globalThis
;try{return this||new Function("return this")()}catch(t){if("object"==typeof window)return window}}(),r.o=(t,e)=>Object.prototype.hasOwnProperty.call(t,e),r.r=t=>{
"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},
r.nmd=t=>(t.paths=[],t.children||(t.children=[]),t),(()=>{"use strict";var t="checkJobStatus",e="updateJobProgress",n="CPC",o=function(t,e,r){
return r?AP.events.onPublic("".concat(n,".").concat(t),e):AP.events.on(t,e)};const i=function(t,e,r){
return r?AP.events.emitPublic("".concat(n,".").concat(t),e):AP.events.emit(t,e)}
;var a=r(28271),s="https://raw.githubusercontent.com/fuegokit/appfire-design-systems-brand-svg/main/",u=("".concat(s,"full-color-brand-icons/comala-publishing-72.svg"),
"".concat(s,"single-color-brand-icons/af-logo-comala-publishing-24.svg"),
"/rest/publishing/1"),c="cpc-config",l="cpc-status",f="cpc-job-page-publication",h="cw-status",p={NEW:"new",SYNCED:"synced",OUT_OF_SYNC:"outofsync",REMOVED:"removed"
},d={MANIFEST:{url:"/content/:contentId",params:[":contentId"]},PUBLISH_CONTENT:{url:"/publish_content/:spaceKey/:contentId",params:[":spaceKey",":contentId"]},
PUBLISH_PAGE:{url:"/publish/:spaceKey/:contentId",params:[":spaceKey",":contentId"]},PUBLISH_SPACE:{url:"/publish/:spaceKey",params:[":spaceKey"]},CHECK_JOB_STATUS:{
url:"/job/:jobId/status",params:[":jobId"]},SPACE_REINDEX:{url:"/config/:spaceKey/reindex",params:[":spaceKey"]},DIAGNOSIS:{url:"/diagnosis/:spaceKey/:contentId",
params:[":spaceKey",":contentId"]},CHECK_CDX:{url:"/check/cdx",params:[]}};var y=function(t){return t.Idle="IDLE",t.Init="INIT",t.Queued="ENQUEUED",
t.Started="STARTED",t.Finished="FINISHED",t.Failed="FAILED",t}(y||{}),v={IDLE:y.Idle,INIT:y.Init,QUEUED:y.Queued,STARTED:y.Started,FINISHED:y.Finished,
FAILED:y.Failed};var g=function(t){var e=t||document.location.search;e=e.split("+").join(" ")
;for(var r,n={},o=/[?&]?([^=]+)=([^&]*)/g;r=o.exec(e);)n[decodeURIComponent(r[1])]=decodeURIComponent(r[2]);return n};function m(t){
return m="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},m(t)}function b(t,e){var r=Object.keys(t)
;if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(t);e&&(n=n.filter((function(e){return Object.getOwnPropertyDescriptor(t,e).enumerable}))),
r.push.apply(r,n)}return r}function w(t){for(var e=1;e<arguments.length;e++){var r=null!=arguments[e]?arguments[e]:{};e%2?b(Object(r),!0).forEach((function(e){
_(t,e,r[e])})):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(r)):b(Object(r)).forEach((function(e){
Object.defineProperty(t,e,Object.getOwnPropertyDescriptor(r,e))}))}return t}function _(t,e,r){return(e=function(t){var e=function(t,e){if("object"!=m(t)||!t)return t
;var r=t[Symbol.toPrimitive];if(void 0!==r){var n=r.call(t,e||"default");if("object"!=m(n))return n
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==m(e)?e:e+""
}(e))in t?Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}):t[e]=r,t}function x(){x=function(){return e}
;var t,e={},r=Object.prototype,n=r.hasOwnProperty,o=Object.defineProperty||function(t,e,r){t[e]=r.value
},i="function"==typeof Symbol?Symbol:{},a=i.iterator||"@@iterator",s=i.asyncIterator||"@@asyncIterator",u=i.toStringTag||"@@toStringTag";function c(t,e,r){
return Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}),t[e]}try{c({},"")}catch(t){c=function(t,e,r){return t[e]=r}}
function l(t,e,r,n){var i=e&&e.prototype instanceof g?e:g,a=Object.create(i.prototype),s=new I(n||[]);return o(a,"_invoke",{value:j(t,r,s)}),a}function f(t,e,r){try{
return{type:"normal",arg:t.call(e,r)}}catch(t){return{type:"throw",arg:t}}}e.wrap=l;var h="suspendedStart",p="suspendedYield",d="executing",y="completed",v={}
;function g(){}function b(){}function w(){}var _={};c(_,a,(function(){return this}));var P=Object.getPrototypeOf,S=P&&P(P(L([])));S&&S!==r&&n.call(S,a)&&(_=S)
;var E=w.prototype=g.prototype=Object.create(_);function O(t){["next","throw","return"].forEach((function(e){c(t,e,(function(t){return this._invoke(e,t)}))}))}
function k(t,e){function r(o,i,a,s){var u=f(t[o],t,i);if("throw"!==u.type){var c=u.arg,l=c.value
;return l&&"object"==m(l)&&n.call(l,"__await")?e.resolve(l.__await).then((function(t){r("next",t,a,s)}),(function(t){r("throw",t,a,s)
})):e.resolve(l).then((function(t){c.value=t,a(c)}),(function(t){return r("throw",t,a,s)}))}s(u.arg)}var i;o(this,"_invoke",{value:function(t,n){function o(){
return new e((function(e,o){r(t,n,e,o)}))}return i=i?i.then(o,o):o()}})}function j(e,r,n){var o=h;return function(i,a){
if(o===d)throw Error("Generator is already running");if(o===y){if("throw"===i)throw a;return{value:t,done:!0}}for(n.method=i,n.arg=a;;){var s=n.delegate;if(s){
var u=C(s,n);if(u){if(u===v)continue;return u}}if("next"===n.method)n.sent=n._sent=n.arg;else if("throw"===n.method){if(o===h)throw o=y,n.arg
;n.dispatchException(n.arg)}else"return"===n.method&&n.abrupt("return",n.arg);o=d;var c=f(e,r,n);if("normal"===c.type){if(o=n.done?y:p,c.arg===v)continue;return{
value:c.arg,done:n.done}}"throw"===c.type&&(o=y,n.method="throw",n.arg=c.arg)}}}function C(e,r){var n=r.method,o=e.iterator[n];if(o===t)return r.delegate=null,
"throw"===n&&e.iterator.return&&(r.method="return",r.arg=t,C(e,r),"throw"===r.method)||"return"!==n&&(r.method="throw",
r.arg=new TypeError("The iterator does not provide a '"+n+"' method")),v;var i=f(o,e.iterator,r.arg);if("throw"===i.type)return r.method="throw",r.arg=i.arg,
r.delegate=null,v;var a=i.arg;return a?a.done?(r[e.resultName]=a.value,r.next=e.nextLoc,"return"!==r.method&&(r.method="next",r.arg=t),r.delegate=null,
v):a:(r.method="throw",r.arg=new TypeError("iterator result is not an object"),r.delegate=null,v)}function T(t){var e={tryLoc:t[0]};1 in t&&(e.catchLoc=t[1]),
2 in t&&(e.finallyLoc=t[2],e.afterLoc=t[3]),this.tryEntries.push(e)}function A(t){var e=t.completion||{};e.type="normal",delete e.arg,t.completion=e}function I(t){
this.tryEntries=[{tryLoc:"root"}],t.forEach(T,this),this.reset(!0)}function L(e){if(e||""===e){var r=e[a];if(r)return r.call(e);if("function"==typeof e.next)return e
;if(!isNaN(e.length)){var o=-1,i=function r(){for(;++o<e.length;)if(n.call(e,o))return r.value=e[o],r.done=!1,r;return r.value=t,r.done=!0,r};return i.next=i}}
throw new TypeError(m(e)+" is not iterable")}return b.prototype=w,o(E,"constructor",{value:w,configurable:!0}),o(w,"constructor",{value:b,configurable:!0}),
b.displayName=c(w,u,"GeneratorFunction"),e.isGeneratorFunction=function(t){var e="function"==typeof t&&t.constructor
;return!!e&&(e===b||"GeneratorFunction"===(e.displayName||e.name))},e.mark=function(t){return Object.setPrototypeOf?Object.setPrototypeOf(t,w):(t.__proto__=w,
c(t,u,"GeneratorFunction")),t.prototype=Object.create(E),t},e.awrap=function(t){return{__await:t}},O(k.prototype),c(k.prototype,s,(function(){return this})),
e.AsyncIterator=k,e.async=function(t,r,n,o,i){void 0===i&&(i=Promise);var a=new k(l(t,r,n,o),i);return e.isGeneratorFunction(r)?a:a.next().then((function(t){
return t.done?t.value:a.next()}))},O(E),c(E,u,"Generator"),c(E,a,(function(){return this})),c(E,"toString",(function(){return"[object Generator]"})),
e.keys=function(t){var e=Object(t),r=[];for(var n in e)r.push(n);return r.reverse(),function t(){for(;r.length;){var n=r.pop();if(n in e)return t.value=n,t.done=!1,t
}return t.done=!0,t}},e.values=L,I.prototype={constructor:I,reset:function(e){if(this.prev=0,this.next=0,this.sent=this._sent=t,this.done=!1,this.delegate=null,
this.method="next",this.arg=t,this.tryEntries.forEach(A),!e)for(var r in this)"t"===r.charAt(0)&&n.call(this,r)&&!isNaN(+r.slice(1))&&(this[r]=t)},stop:function(){
this.done=!0;var t=this.tryEntries[0].completion;if("throw"===t.type)throw t.arg;return this.rval},dispatchException:function(e){if(this.done)throw e;var r=this
;function o(n,o){return s.type="throw",s.arg=e,r.next=n,o&&(r.method="next",r.arg=t),!!o}for(var i=this.tryEntries.length-1;i>=0;--i){
var a=this.tryEntries[i],s=a.completion;if("root"===a.tryLoc)return o("end");if(a.tryLoc<=this.prev){var u=n.call(a,"catchLoc"),c=n.call(a,"finallyLoc");if(u&&c){
if(this.prev<a.catchLoc)return o(a.catchLoc,!0);if(this.prev<a.finallyLoc)return o(a.finallyLoc)}else if(u){if(this.prev<a.catchLoc)return o(a.catchLoc,!0)}else{
if(!c)throw Error("try statement without catch or finally");if(this.prev<a.finallyLoc)return o(a.finallyLoc)}}}},abrupt:function(t,e){
for(var r=this.tryEntries.length-1;r>=0;--r){var o=this.tryEntries[r];if(o.tryLoc<=this.prev&&n.call(o,"finallyLoc")&&this.prev<o.finallyLoc){var i=o;break}}
i&&("break"===t||"continue"===t)&&i.tryLoc<=e&&e<=i.finallyLoc&&(i=null);var a=i?i.completion:{};return a.type=t,a.arg=e,i?(this.method="next",
this.next=i.finallyLoc,v):this.complete(a)},complete:function(t,e){if("throw"===t.type)throw t.arg
;return"break"===t.type||"continue"===t.type?this.next=t.arg:"return"===t.type?(this.rval=this.arg=t.arg,this.method="return",
this.next="end"):"normal"===t.type&&e&&(this.next=e),v},finish:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.finallyLoc===t)return this.complete(r.completion,r.afterLoc),A(r),v}},catch:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.tryLoc===t){var n=r.completion;if("throw"===n.type){var o=n.arg;A(r)}return o}}throw Error("illegal catch attempt")},delegateYield:function(e,r,n){
return this.delegate={iterator:L(e),resultName:r,nextLoc:n},"next"===this.method&&(this.arg=t),v}},e}function P(t,e){return function(t){if(Array.isArray(t))return t
}(t)||function(t,e){var r=null==t?null:"undefined"!=typeof Symbol&&t[Symbol.iterator]||t["@@iterator"];if(null!=r){var n,o,i,a,s=[],u=!0,c=!1;try{
if(i=(r=r.call(t)).next,0===e){if(Object(r)!==r)return;u=!1}else for(;!(u=(n=i.call(r)).done)&&(s.push(n.value),s.length!==e);u=!0);}catch(t){c=!0,o=t}finally{try{
if(!u&&null!=r.return&&(a=r.return(),Object(a)!==a))return}finally{if(c)throw o}}return s}}(t,e)||function(t,e){if(t){if("string"==typeof t)return S(t,e)
;var r={}.toString.call(t).slice(8,-1);return"Object"===r&&t.constructor&&(r=t.constructor.name),
"Map"===r||"Set"===r?Array.from(t):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?S(t,e):void 0}}(t,e)||function(){
throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()}
function S(t,e){(null==e||e>t.length)&&(e=t.length);for(var r=0,n=Array(e);r<e;r++)n[r]=t[r];return n}function E(t,e,r,n,o,i,a){try{var s=t[i](a),u=s.value}catch(t){
return void r(t)}s.done?e(u):Promise.resolve(u).then(n,o)}function O(t){return function(){var e=this,r=arguments;return new Promise((function(n,o){var i=t.apply(e,r)
;function a(t){E(i,n,o,a,s,"next",t)}function s(t){E(i,n,o,a,s,"throw",t)}a(void 0)}))}}var k=function(){var t=O(x().mark((function t(){var e,r,n,o
;return x().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,Promise.all([new Promise((function(t){AP.getLocation(t)
})),new Promise((function(t){AP.navigator.getLocation(t)}))]);case 2:return e=t.sent,r=P(e,2),n=r[0],o=r[1],t.abrupt("return",w({url:n},o));case 7:case"end":
return t.stop()}}),t)})));return function(){return t.apply(this,arguments)}}();r(74189);var j,C,T=r(76175),A=r(82402);function I(t){return function(t){
if(Array.isArray(t))return L(t)}(t)||function(t){if("undefined"!=typeof Symbol&&null!=t[Symbol.iterator]||null!=t["@@iterator"])return Array.from(t)
}(t)||function(t,e){if(t){if("string"==typeof t)return L(t,e);var r={}.toString.call(t).slice(8,-1);return"Object"===r&&t.constructor&&(r=t.constructor.name),
"Map"===r||"Set"===r?Array.from(t):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?L(t,e):void 0}}(t)||function(){
throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()}
function L(t,e){(null==e||e>t.length)&&(e=t.length);for(var r=0,n=Array(e);r<e;r++)n[r]=t[r];return n}function N(t,e,r,n){var o=function(t,e){
return(Array.isArray(t)?t:[t]).reduce((function(t,r){
return Array.isArray(e)&&-1!==e.indexOf(r)||"string"==typeof e&&e===r||-1!==t.indexOf(r)||!r?t:[].concat(I(t),[r])}),[])}(e,n),i=r?"".concat(r," "):""
;if(0===o.length)return"";var a=o.join('", "');return"".concat(i).concat(t," ").concat(-1!==a.indexOf('", "')?'IN ("'.concat(a,'")'):'= "'.concat(a,'"'))}
!function(t){t.assertEqual=t=>t,t.assertIs=function(t){},t.assertNever=function(t){throw new Error},t.arrayToEnum=t=>{const e={};for(const r of t)e[r]=r;return e},
t.getValidEnumValues=e=>{const r=t.objectKeys(e).filter((t=>"number"!=typeof e[e[t]])),n={};for(const t of r)n[t]=e[t];return t.objectValues(n)},
t.objectValues=e=>t.objectKeys(e).map((function(t){return e[t]})),t.objectKeys="function"==typeof Object.keys?t=>Object.keys(t):t=>{const e=[]
;for(const r in t)Object.prototype.hasOwnProperty.call(t,r)&&e.push(r);return e},t.find=(t,e)=>{for(const r of t)if(e(r))return r},
t.isInteger="function"==typeof Number.isInteger?t=>Number.isInteger(t):t=>"number"==typeof t&&isFinite(t)&&Math.floor(t)===t,t.joinValues=function(t,e=" | "){
return t.map((t=>"string"==typeof t?`'${t}'`:t)).join(e)},t.jsonStringifyReplacer=(t,e)=>"bigint"==typeof e?e.toString():e}(j||(j={})),function(t){
t.mergeShapes=(t,e)=>({...t,...e})}(C||(C={}))
;const R=j.arrayToEnum(["string","nan","number","integer","float","boolean","date","bigint","symbol","function","undefined","null","array","object","unknown","promise","void","never","map","set"]),D=t=>{
switch(typeof t){case"undefined":return R.undefined;case"string":return R.string;case"number":return isNaN(t)?R.nan:R.number;case"boolean":return R.boolean
;case"function":return R.function;case"bigint":return R.bigint;case"symbol":return R.symbol;case"object":
return Array.isArray(t)?R.array:null===t?R.null:t.then&&"function"==typeof t.then&&t.catch&&"function"==typeof t.catch?R.promise:"undefined"!=typeof Map&&t instanceof Map?R.map:"undefined"!=typeof Set&&t instanceof Set?R.set:"undefined"!=typeof Date&&t instanceof Date?R.date:R.object
;default:return R.unknown}
},B=j.arrayToEnum(["invalid_type","invalid_literal","custom","invalid_union","invalid_union_discriminator","invalid_enum_value","unrecognized_keys","invalid_arguments","invalid_return_type","invalid_date","invalid_string","too_small","too_big","invalid_intersection_types","not_multiple_of","not_finite"])
;class F extends Error{get errors(){return this.issues}constructor(t){super(),this.issues=[],this.addIssue=t=>{this.issues=[...this.issues,t]},
this.addIssues=(t=[])=>{this.issues=[...this.issues,...t]};const e=new.target.prototype;Object.setPrototypeOf?Object.setPrototypeOf(this,e):this.__proto__=e,
this.name="ZodError",this.issues=t}format(t){const e=t||function(t){return t.message},r={_errors:[]},n=t=>{
for(const o of t.issues)if("invalid_union"===o.code)o.unionErrors.map(n);else if("invalid_return_type"===o.code)n(o.returnTypeError);else if("invalid_arguments"===o.code)n(o.argumentsError);else if(0===o.path.length)r._errors.push(e(o));else{
let t=r,n=0;for(;n<o.path.length;){const r=o.path[n];n===o.path.length-1?(t[r]=t[r]||{_errors:[]},t[r]._errors.push(e(o))):t[r]=t[r]||{_errors:[]},t=t[r],n++}}}
;return n(this),r}static assert(t){if(!(t instanceof F))throw new Error(`Not a ZodError: ${t}`)}toString(){return this.message}get message(){
return JSON.stringify(this.issues,j.jsonStringifyReplacer,2)}get isEmpty(){return 0===this.issues.length}flatten(t=t=>t.message){const e={},r=[]
;for(const n of this.issues)n.path.length>0?(e[n.path[0]]=e[n.path[0]]||[],e[n.path[0]].push(t(n))):r.push(t(n));return{formErrors:r,fieldErrors:e}}get formErrors(){
return this.flatten()}}F.create=t=>new F(t);const M=(t,e)=>{let r;switch(t.code){case B.invalid_type:
r=t.received===R.undefined?"Required":`Expected ${t.expected}, received ${t.received}`;break;case B.invalid_literal:
r=`Invalid literal value, expected ${JSON.stringify(t.expected,j.jsonStringifyReplacer)}`;break;case B.unrecognized_keys:
r=`Unrecognized key(s) in object: ${j.joinValues(t.keys,", ")}`;break;case B.invalid_union:r="Invalid input";break;case B.invalid_union_discriminator:
r=`Invalid discriminator value. Expected ${j.joinValues(t.options)}`;break;case B.invalid_enum_value:
r=`Invalid enum value. Expected ${j.joinValues(t.options)}, received '${t.received}'`;break;case B.invalid_arguments:r="Invalid function arguments";break
;case B.invalid_return_type:r="Invalid function return type";break;case B.invalid_date:r="Invalid date";break;case B.invalid_string:
"object"==typeof t.validation?"includes"in t.validation?(r=`Invalid input: must include "${t.validation.includes}"`,
"number"==typeof t.validation.position&&(r=`${r} at one or more positions greater than or equal to ${t.validation.position}`)):"startsWith"in t.validation?r=`Invalid input: must start with "${t.validation.startsWith}"`:"endsWith"in t.validation?r=`Invalid input: must end with "${t.validation.endsWith}"`:j.assertNever(t.validation):r="regex"!==t.validation?`Invalid ${t.validation}`:"Invalid"
;break;case B.too_small:
r="array"===t.type?`Array must contain ${t.exact?"exactly":t.inclusive?"at least":"more than"} ${t.minimum} element(s)`:"string"===t.type?`String must contain ${t.exact?"exactly":t.inclusive?"at least":"over"} ${t.minimum} character(s)`:"number"===t.type?`Number must be ${t.exact?"exactly equal to ":t.inclusive?"greater than or equal to ":"greater than "}${t.minimum}`:"date"===t.type?`Date must be ${t.exact?"exactly equal to ":t.inclusive?"greater than or equal to ":"greater than "}${new Date(Number(t.minimum))}`:"Invalid input"
;break;case B.too_big:
r="array"===t.type?`Array must contain ${t.exact?"exactly":t.inclusive?"at most":"less than"} ${t.maximum} element(s)`:"string"===t.type?`String must contain ${t.exact?"exactly":t.inclusive?"at most":"under"} ${t.maximum} character(s)`:"number"===t.type?`Number must be ${t.exact?"exactly":t.inclusive?"less than or equal to":"less than"} ${t.maximum}`:"bigint"===t.type?`BigInt must be ${t.exact?"exactly":t.inclusive?"less than or equal to":"less than"} ${t.maximum}`:"date"===t.type?`Date must be ${t.exact?"exactly":t.inclusive?"smaller than or equal to":"smaller than"} ${new Date(Number(t.maximum))}`:"Invalid input"
;break;case B.custom:r="Invalid input";break;case B.invalid_intersection_types:r="Intersection results could not be merged";break;case B.not_multiple_of:
r=`Number must be a multiple of ${t.multipleOf}`;break;case B.not_finite:r="Number must be finite";break;default:r=e.defaultError,j.assertNever(t)}return{message:r}}
;let G=M;function V(){return G}const U=t=>{const{data:e,path:r,errorMaps:n,issueData:o}=t,i=[...r,...o.path||[]],a={...o,path:i};if(void 0!==o.message)return{...o,
path:i,message:o.message};let s="";const u=n.filter((t=>!!t)).slice().reverse();for(const t of u)s=t(a,{data:e,defaultError:s}).message;return{...o,path:i,message:s}
};function q(t,e){const r=V(),n=U({issueData:e,data:t.data,path:t.path,errorMaps:[t.common.contextualErrorMap,t.schemaErrorMap,r,r===M?void 0:M].filter((t=>!!t))})
;t.common.issues.push(n)}class Z{constructor(){this.value="valid"}dirty(){"valid"===this.value&&(this.value="dirty")}abort(){
"aborted"!==this.value&&(this.value="aborted")}static mergeArray(t,e){const r=[];for(const n of e){if("aborted"===n.status)return K;"dirty"===n.status&&t.dirty(),
r.push(n.value)}return{status:t.value,value:r}}static async mergeObjectAsync(t,e){const r=[];for(const t of e){const e=await t.key,n=await t.value;r.push({key:e,
value:n})}return Z.mergeObjectSync(t,r)}static mergeObjectSync(t,e){const r={};for(const n of e){const{key:e,value:o}=n;if("aborted"===e.status)return K
;if("aborted"===o.status)return K;"dirty"===e.status&&t.dirty(),"dirty"===o.status&&t.dirty(),
"__proto__"===e.value||void 0===o.value&&!n.alwaysSet||(r[e.value]=o.value)}return{status:t.value,value:r}}}const K=Object.freeze({status:"aborted"}),z=t=>({
status:"dirty",value:t}),$=t=>({status:"valid",value:t
}),H=t=>"aborted"===t.status,Y=t=>"dirty"===t.status,J=t=>"valid"===t.status,W=t=>"undefined"!=typeof Promise&&t instanceof Promise;function Q(t,e,r,n){
if("a"===r&&!n)throw new TypeError("Private accessor was defined without a getter")
;if("function"==typeof e?t!==e||!n:!e.has(t))throw new TypeError("Cannot read private member from an object whose class did not declare it")
;return"m"===r?n:"a"===r?n.call(t):n?n.value:e.get(t)}function X(t,e,r,n,o){if("m"===n)throw new TypeError("Private method is not writable")
;if("a"===n&&!o)throw new TypeError("Private accessor was defined without a setter")
;if("function"==typeof e?t!==e||!o:!e.has(t))throw new TypeError("Cannot write private member to an object whose class did not declare it")
;return"a"===n?o.call(t,r):o?o.value=r:e.set(t,r),r}var tt,et,rt;"function"==typeof SuppressedError&&SuppressedError,function(t){t.errToObj=t=>"string"==typeof t?{
message:t}:t||{},t.toString=t=>"string"==typeof t?t:null==t?void 0:t.message}(tt||(tt={}));class nt{constructor(t,e,r,n){this._cachedPath=[],this.parent=t,
this.data=e,this._path=r,this._key=n}get path(){
return this._cachedPath.length||(this._key instanceof Array?this._cachedPath.push(...this._path,...this._key):this._cachedPath.push(...this._path,this._key)),
this._cachedPath}}const ot=(t,e)=>{if(J(e))return{success:!0,data:e.value};if(!t.common.issues.length)throw new Error("Validation failed but no issues detected.")
;return{success:!1,get error(){if(this._error)return this._error;const e=new F(t.common.issues);return this._error=e,this._error}}};function it(t){if(!t)return{}
;const{errorMap:e,invalid_type_error:r,required_error:n,description:o}=t
;if(e&&(r||n))throw new Error('Can\'t use "invalid_type_error" or "required_error" in conjunction with custom error map.');if(e)return{errorMap:e,description:o}
;return{errorMap:(e,o)=>{var i,a;const{message:s}=t;return"invalid_enum_value"===e.code?{message:null!=s?s:o.defaultError}:void 0===o.data?{
message:null!==(i=null!=s?s:n)&&void 0!==i?i:o.defaultError}:"invalid_type"!==e.code?{message:o.defaultError}:{
message:null!==(a=null!=s?s:r)&&void 0!==a?a:o.defaultError}},description:o}}class at{get description(){return this._def.description}_getType(t){return D(t.data)}
_getOrReturnCtx(t,e){return e||{common:t.parent.common,data:t.data,parsedType:D(t.data),schemaErrorMap:this._def.errorMap,path:t.path,parent:t.parent}}
_processInputParams(t){return{status:new Z,ctx:{common:t.parent.common,data:t.data,parsedType:D(t.data),schemaErrorMap:this._def.errorMap,path:t.path,parent:t.parent
}}}_parseSync(t){const e=this._parse(t);if(W(e))throw new Error("Synchronous parse encountered promise.");return e}_parseAsync(t){const e=this._parse(t)
;return Promise.resolve(e)}parse(t,e){const r=this.safeParse(t,e);if(r.success)return r.data;throw r.error}safeParse(t,e){var r;const n={common:{issues:[],
async:null!==(r=null==e?void 0:e.async)&&void 0!==r&&r,contextualErrorMap:null==e?void 0:e.errorMap},path:(null==e?void 0:e.path)||[],
schemaErrorMap:this._def.errorMap,parent:null,data:t,parsedType:D(t)},o=this._parseSync({data:t,path:n.path,parent:n});return ot(n,o)}"~validate"(t){var e,r
;const n={common:{issues:[],async:!!this["~standard"].async},path:[],schemaErrorMap:this._def.errorMap,parent:null,data:t,parsedType:D(t)}
;if(!this["~standard"].async)try{const e=this._parseSync({data:t,path:[],parent:n});return J(e)?{value:e.value}:{issues:n.common.issues}}catch(t){
(null===(r=null===(e=null==t?void 0:t.message)||void 0===e?void 0:e.toLowerCase())||void 0===r?void 0:r.includes("encountered"))&&(this["~standard"].async=!0),
n.common={issues:[],async:!0}}return this._parseAsync({data:t,path:[],parent:n}).then((t=>J(t)?{value:t.value}:{issues:n.common.issues}))}async parseAsync(t,e){
const r=await this.safeParseAsync(t,e);if(r.success)return r.data;throw r.error}async safeParseAsync(t,e){const r={common:{issues:[],
contextualErrorMap:null==e?void 0:e.errorMap,async:!0},path:(null==e?void 0:e.path)||[],schemaErrorMap:this._def.errorMap,parent:null,data:t,parsedType:D(t)
},n=this._parse({data:t,path:r.path,parent:r}),o=await(W(n)?n:Promise.resolve(n));return ot(r,o)}refine(t,e){const r=t=>"string"==typeof e||void 0===e?{message:e
}:"function"==typeof e?e(t):e;return this._refinement(((e,n)=>{const o=t(e),i=()=>n.addIssue({code:B.custom,...r(e)})
;return"undefined"!=typeof Promise&&o instanceof Promise?o.then((t=>!!t||(i(),!1))):!!o||(i(),!1)}))}refinement(t,e){
return this._refinement(((r,n)=>!!t(r)||(n.addIssue("function"==typeof e?e(r,n):e),!1)))}_refinement(t){return new ae({schema:this,typeName:be.ZodEffects,effect:{
type:"refinement",refinement:t}})}superRefine(t){return this._refinement(t)}constructor(t){this.spa=this.safeParseAsync,this._def=t,this.parse=this.parse.bind(this),
this.safeParse=this.safeParse.bind(this),this.parseAsync=this.parseAsync.bind(this),this.safeParseAsync=this.safeParseAsync.bind(this),this.spa=this.spa.bind(this),
this.refine=this.refine.bind(this),this.refinement=this.refinement.bind(this),this.superRefine=this.superRefine.bind(this),this.optional=this.optional.bind(this),
this.nullable=this.nullable.bind(this),this.nullish=this.nullish.bind(this),this.array=this.array.bind(this),this.promise=this.promise.bind(this),
this.or=this.or.bind(this),this.and=this.and.bind(this),this.transform=this.transform.bind(this),this.brand=this.brand.bind(this),
this.default=this.default.bind(this),this.catch=this.catch.bind(this),this.describe=this.describe.bind(this),this.pipe=this.pipe.bind(this),
this.readonly=this.readonly.bind(this),this.isNullable=this.isNullable.bind(this),this.isOptional=this.isOptional.bind(this),this["~standard"]={version:1,
vendor:"zod",validate:t=>this["~validate"](t)}}optional(){return se.create(this,this._def)}nullable(){return ue.create(this,this._def)}nullish(){
return this.nullable().optional()}array(){return Vt.create(this)}promise(){return ie.create(this,this._def)}or(t){return Zt.create([this,t],this._def)}and(t){
return Ht.create(this,t,this._def)}transform(t){return new ae({...it(this._def),schema:this,typeName:be.ZodEffects,effect:{type:"transform",transform:t}})}
default(t){const e="function"==typeof t?t:()=>t;return new ce({...it(this._def),innerType:this,defaultValue:e,typeName:be.ZodDefault})}brand(){return new pe({
typeName:be.ZodBranded,type:this,...it(this._def)})}catch(t){const e="function"==typeof t?t:()=>t;return new le({...it(this._def),innerType:this,catchValue:e,
typeName:be.ZodCatch})}describe(t){return new(0,this.constructor)({...this._def,description:t})}pipe(t){return de.create(this,t)}readonly(){return ye.create(this)}
isOptional(){return this.safeParse(void 0).success}isNullable(){return this.safeParse(null).success}}
const st=/^c[^\s-]{8,}$/i,ut=/^[0-9a-z]+$/,ct=/^[0-9A-HJKMNP-TV-Z]{26}$/i,lt=/^[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}$/i,ft=/^[a-z0-9_-]{21}$/i,ht=/^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]*$/,pt=/^[-+]?P(?!$)(?:(?:[-+]?\d+Y)|(?:[-+]?\d+[.,]\d+Y$))?(?:(?:[-+]?\d+M)|(?:[-+]?\d+[.,]\d+M$))?(?:(?:[-+]?\d+W)|(?:[-+]?\d+[.,]\d+W$))?(?:(?:[-+]?\d+D)|(?:[-+]?\d+[.,]\d+D$))?(?:T(?=[\d+-])(?:(?:[-+]?\d+H)|(?:[-+]?\d+[.,]\d+H$))?(?:(?:[-+]?\d+M)|(?:[-+]?\d+[.,]\d+M$))?(?:[-+]?\d+(?:[.,]\d+)?S)?)??$/,dt=/^(?!\.)(?!.*\.\.)([A-Z0-9_'+\-\.]*)[A-Z0-9_+-]@([A-Z0-9][A-Z0-9\-]*\.)+[A-Z]{2,}$/i
;let yt
;const vt=/^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])$/,gt=/^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\/(3[0-2]|[12]?[0-9])$/,mt=/^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$/,bt=/^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))\/(12[0-8]|1[01][0-9]|[1-9]?[0-9])$/,wt=/^([0-9a-zA-Z+/]{4})*(([0-9a-zA-Z+/]{2}==)|([0-9a-zA-Z+/]{3}=))?$/,_t=/^([0-9a-zA-Z-_]{4})*(([0-9a-zA-Z-_]{2}(==)?)|([0-9a-zA-Z-_]{3}(=)?))?$/,xt="((\\d\\d[2468][048]|\\d\\d[13579][26]|\\d\\d0[48]|[02468][048]00|[13579][26]00)-02-29|\\d{4}-((0[13578]|1[02])-(0[1-9]|[12]\\d|3[01])|(0[469]|11)-(0[1-9]|[12]\\d|30)|(02)-(0[1-9]|1\\d|2[0-8])))",Pt=new RegExp(`^${xt}$`)
;function St(t){let e="([01]\\d|2[0-3]):[0-5]\\d:[0-5]\\d";return t.precision?e=`${e}\\.\\d{${t.precision}}`:null==t.precision&&(e=`${e}(\\.\\d+)?`),e}
function Et(t){let e=`${xt}T${St(t)}`;const r=[];return r.push(t.local?"Z?":"Z"),t.offset&&r.push("([+-]\\d{2}:?\\d{2})"),e=`${e}(${r.join("|")})`,
new RegExp(`^${e}$`)}function Ot(t,e){if(!ht.test(t))return!1;try{
const[r]=t.split("."),n=r.replace(/-/g,"+").replace(/_/g,"/").padEnd(r.length+(4-r.length%4)%4,"="),o=JSON.parse(atob(n))
;return"object"==typeof o&&null!==o&&(!(!o.typ||!o.alg)&&(!e||o.alg===e))}catch(t){return!1}}function kt(t,e){
return!("v4"!==e&&e||!gt.test(t))||!("v6"!==e&&e||!bt.test(t))}class jt extends at{_parse(t){this._def.coerce&&(t.data=String(t.data))
;if(this._getType(t)!==R.string){const e=this._getOrReturnCtx(t);return q(e,{code:B.invalid_type,expected:R.string,received:e.parsedType}),K}const e=new Z;let r
;for(const i of this._def.checks)if("min"===i.kind)t.data.length<i.value&&(r=this._getOrReturnCtx(t,r),q(r,{code:B.too_small,minimum:i.value,type:"string",
inclusive:!0,exact:!1,message:i.message}),e.dirty());else if("max"===i.kind)t.data.length>i.value&&(r=this._getOrReturnCtx(t,r),q(r,{code:B.too_big,maximum:i.value,
type:"string",inclusive:!0,exact:!1,message:i.message}),e.dirty());else if("length"===i.kind){const n=t.data.length>i.value,o=t.data.length<i.value
;(n||o)&&(r=this._getOrReturnCtx(t,r),n?q(r,{code:B.too_big,maximum:i.value,type:"string",inclusive:!0,exact:!0,message:i.message}):o&&q(r,{code:B.too_small,
minimum:i.value,type:"string",inclusive:!0,exact:!0,message:i.message}),e.dirty())}else if("email"===i.kind)dt.test(t.data)||(r=this._getOrReturnCtx(t,r),q(r,{
validation:"email",code:B.invalid_string,message:i.message
}),e.dirty());else if("emoji"===i.kind)yt||(yt=new RegExp("^(\\p{Extended_Pictographic}|\\p{Emoji_Component})+$","u")),yt.test(t.data)||(r=this._getOrReturnCtx(t,r),
q(r,{validation:"emoji",code:B.invalid_string,message:i.message}),e.dirty());else if("uuid"===i.kind)lt.test(t.data)||(r=this._getOrReturnCtx(t,r),q(r,{
validation:"uuid",code:B.invalid_string,message:i.message}),e.dirty());else if("nanoid"===i.kind)ft.test(t.data)||(r=this._getOrReturnCtx(t,r),q(r,{
validation:"nanoid",code:B.invalid_string,message:i.message}),e.dirty());else if("cuid"===i.kind)st.test(t.data)||(r=this._getOrReturnCtx(t,r),q(r,{
validation:"cuid",code:B.invalid_string,message:i.message}),e.dirty());else if("cuid2"===i.kind)ut.test(t.data)||(r=this._getOrReturnCtx(t,r),q(r,{
validation:"cuid2",code:B.invalid_string,message:i.message}),e.dirty());else if("ulid"===i.kind)ct.test(t.data)||(r=this._getOrReturnCtx(t,r),q(r,{validation:"ulid",
code:B.invalid_string,message:i.message}),e.dirty());else if("url"===i.kind)try{new URL(t.data)}catch(n){r=this._getOrReturnCtx(t,r),q(r,{validation:"url",
code:B.invalid_string,message:i.message}),e.dirty()}else if("regex"===i.kind){i.regex.lastIndex=0;i.regex.test(t.data)||(r=this._getOrReturnCtx(t,r),q(r,{
validation:"regex",code:B.invalid_string,message:i.message}),e.dirty())
}else if("trim"===i.kind)t.data=t.data.trim();else if("includes"===i.kind)t.data.includes(i.value,i.position)||(r=this._getOrReturnCtx(t,r),q(r,{
code:B.invalid_string,validation:{includes:i.value,position:i.position},message:i.message}),
e.dirty());else if("toLowerCase"===i.kind)t.data=t.data.toLowerCase();else if("toUpperCase"===i.kind)t.data=t.data.toUpperCase();else if("startsWith"===i.kind)t.data.startsWith(i.value)||(r=this._getOrReturnCtx(t,r),
q(r,{code:B.invalid_string,validation:{startsWith:i.value},message:i.message
}),e.dirty());else if("endsWith"===i.kind)t.data.endsWith(i.value)||(r=this._getOrReturnCtx(t,r),q(r,{code:B.invalid_string,validation:{endsWith:i.value},
message:i.message}),e.dirty());else if("datetime"===i.kind){Et(i).test(t.data)||(r=this._getOrReturnCtx(t,r),q(r,{code:B.invalid_string,validation:"datetime",
message:i.message}),e.dirty())}else if("date"===i.kind){Pt.test(t.data)||(r=this._getOrReturnCtx(t,r),q(r,{code:B.invalid_string,validation:"date",message:i.message
}),e.dirty())}else if("time"===i.kind){new RegExp(`^${St(i)}$`).test(t.data)||(r=this._getOrReturnCtx(t,r),q(r,{code:B.invalid_string,validation:"time",
message:i.message}),e.dirty())}else"duration"===i.kind?pt.test(t.data)||(r=this._getOrReturnCtx(t,r),q(r,{validation:"duration",code:B.invalid_string,
message:i.message}),e.dirty()):"ip"===i.kind?(n=t.data,("v4"!==(o=i.version)&&o||!vt.test(n))&&("v6"!==o&&o||!mt.test(n))&&(r=this._getOrReturnCtx(t,r),q(r,{
validation:"ip",code:B.invalid_string,message:i.message}),e.dirty())):"jwt"===i.kind?Ot(t.data,i.alg)||(r=this._getOrReturnCtx(t,r),q(r,{validation:"jwt",
code:B.invalid_string,message:i.message}),e.dirty()):"cidr"===i.kind?kt(t.data,i.version)||(r=this._getOrReturnCtx(t,r),q(r,{validation:"cidr",code:B.invalid_string,
message:i.message}),e.dirty()):"base64"===i.kind?wt.test(t.data)||(r=this._getOrReturnCtx(t,r),q(r,{validation:"base64",code:B.invalid_string,message:i.message}),
e.dirty()):"base64url"===i.kind?_t.test(t.data)||(r=this._getOrReturnCtx(t,r),q(r,{validation:"base64url",code:B.invalid_string,message:i.message}),
e.dirty()):j.assertNever(i);var n,o;return{status:e.value,value:t.data}}_regex(t,e,r){return this.refinement((e=>t.test(e)),{validation:e,code:B.invalid_string,
...tt.errToObj(r)})}_addCheck(t){return new jt({...this._def,checks:[...this._def.checks,t]})}email(t){return this._addCheck({kind:"email",...tt.errToObj(t)})}
url(t){return this._addCheck({kind:"url",...tt.errToObj(t)})}emoji(t){return this._addCheck({kind:"emoji",...tt.errToObj(t)})}uuid(t){return this._addCheck({
kind:"uuid",...tt.errToObj(t)})}nanoid(t){return this._addCheck({kind:"nanoid",...tt.errToObj(t)})}cuid(t){return this._addCheck({kind:"cuid",...tt.errToObj(t)})}
cuid2(t){return this._addCheck({kind:"cuid2",...tt.errToObj(t)})}ulid(t){return this._addCheck({kind:"ulid",...tt.errToObj(t)})}base64(t){return this._addCheck({
kind:"base64",...tt.errToObj(t)})}base64url(t){return this._addCheck({kind:"base64url",...tt.errToObj(t)})}jwt(t){return this._addCheck({kind:"jwt",...tt.errToObj(t)
})}ip(t){return this._addCheck({kind:"ip",...tt.errToObj(t)})}cidr(t){return this._addCheck({kind:"cidr",...tt.errToObj(t)})}datetime(t){var e,r
;return"string"==typeof t?this._addCheck({kind:"datetime",precision:null,offset:!1,local:!1,message:t}):this._addCheck({kind:"datetime",
precision:void 0===(null==t?void 0:t.precision)?null:null==t?void 0:t.precision,offset:null!==(e=null==t?void 0:t.offset)&&void 0!==e&&e,
local:null!==(r=null==t?void 0:t.local)&&void 0!==r&&r,...tt.errToObj(null==t?void 0:t.message)})}date(t){return this._addCheck({kind:"date",message:t})}time(t){
return"string"==typeof t?this._addCheck({kind:"time",precision:null,message:t}):this._addCheck({kind:"time",
precision:void 0===(null==t?void 0:t.precision)?null:null==t?void 0:t.precision,...tt.errToObj(null==t?void 0:t.message)})}duration(t){return this._addCheck({
kind:"duration",...tt.errToObj(t)})}regex(t,e){return this._addCheck({kind:"regex",regex:t,...tt.errToObj(e)})}includes(t,e){return this._addCheck({kind:"includes",
value:t,position:null==e?void 0:e.position,...tt.errToObj(null==e?void 0:e.message)})}startsWith(t,e){return this._addCheck({kind:"startsWith",value:t,
...tt.errToObj(e)})}endsWith(t,e){return this._addCheck({kind:"endsWith",value:t,...tt.errToObj(e)})}min(t,e){return this._addCheck({kind:"min",value:t,
...tt.errToObj(e)})}max(t,e){return this._addCheck({kind:"max",value:t,...tt.errToObj(e)})}length(t,e){return this._addCheck({kind:"length",value:t,...tt.errToObj(e)
})}nonempty(t){return this.min(1,tt.errToObj(t))}trim(){return new jt({...this._def,checks:[...this._def.checks,{kind:"trim"}]})}toLowerCase(){return new jt({
...this._def,checks:[...this._def.checks,{kind:"toLowerCase"}]})}toUpperCase(){return new jt({...this._def,checks:[...this._def.checks,{kind:"toUpperCase"}]})}
get isDatetime(){return!!this._def.checks.find((t=>"datetime"===t.kind))}get isDate(){return!!this._def.checks.find((t=>"date"===t.kind))}get isTime(){
return!!this._def.checks.find((t=>"time"===t.kind))}get isDuration(){return!!this._def.checks.find((t=>"duration"===t.kind))}get isEmail(){
return!!this._def.checks.find((t=>"email"===t.kind))}get isURL(){return!!this._def.checks.find((t=>"url"===t.kind))}get isEmoji(){
return!!this._def.checks.find((t=>"emoji"===t.kind))}get isUUID(){return!!this._def.checks.find((t=>"uuid"===t.kind))}get isNANOID(){
return!!this._def.checks.find((t=>"nanoid"===t.kind))}get isCUID(){return!!this._def.checks.find((t=>"cuid"===t.kind))}get isCUID2(){
return!!this._def.checks.find((t=>"cuid2"===t.kind))}get isULID(){return!!this._def.checks.find((t=>"ulid"===t.kind))}get isIP(){
return!!this._def.checks.find((t=>"ip"===t.kind))}get isCIDR(){return!!this._def.checks.find((t=>"cidr"===t.kind))}get isBase64(){
return!!this._def.checks.find((t=>"base64"===t.kind))}get isBase64url(){return!!this._def.checks.find((t=>"base64url"===t.kind))}get minLength(){let t=null
;for(const e of this._def.checks)"min"===e.kind&&(null===t||e.value>t)&&(t=e.value);return t}get maxLength(){let t=null
;for(const e of this._def.checks)"max"===e.kind&&(null===t||e.value<t)&&(t=e.value);return t}}function Ct(t,e){
const r=(t.toString().split(".")[1]||"").length,n=(e.toString().split(".")[1]||"").length,o=r>n?r:n
;return parseInt(t.toFixed(o).replace(".",""))%parseInt(e.toFixed(o).replace(".",""))/Math.pow(10,o)}jt.create=t=>{var e;return new jt({checks:[],
typeName:be.ZodString,coerce:null!==(e=null==t?void 0:t.coerce)&&void 0!==e&&e,...it(t)})};class Tt extends at{constructor(){super(...arguments),this.min=this.gte,
this.max=this.lte,this.step=this.multipleOf}_parse(t){this._def.coerce&&(t.data=Number(t.data));if(this._getType(t)!==R.number){const e=this._getOrReturnCtx(t)
;return q(e,{code:B.invalid_type,expected:R.number,received:e.parsedType}),K}let e;const r=new Z
;for(const n of this._def.checks)if("int"===n.kind)j.isInteger(t.data)||(e=this._getOrReturnCtx(t,e),q(e,{code:B.invalid_type,expected:"integer",received:"float",
message:n.message}),r.dirty());else if("min"===n.kind){(n.inclusive?t.data<n.value:t.data<=n.value)&&(e=this._getOrReturnCtx(t,e),q(e,{code:B.too_small,
minimum:n.value,type:"number",inclusive:n.inclusive,exact:!1,message:n.message}),r.dirty())}else if("max"===n.kind){
(n.inclusive?t.data>n.value:t.data>=n.value)&&(e=this._getOrReturnCtx(t,e),q(e,{code:B.too_big,maximum:n.value,type:"number",inclusive:n.inclusive,exact:!1,
message:n.message}),r.dirty())}else"multipleOf"===n.kind?0!==Ct(t.data,n.value)&&(e=this._getOrReturnCtx(t,e),q(e,{code:B.not_multiple_of,multipleOf:n.value,
message:n.message}),r.dirty()):"finite"===n.kind?Number.isFinite(t.data)||(e=this._getOrReturnCtx(t,e),q(e,{code:B.not_finite,message:n.message}),
r.dirty()):j.assertNever(n);return{status:r.value,value:t.data}}gte(t,e){return this.setLimit("min",t,!0,tt.toString(e))}gt(t,e){
return this.setLimit("min",t,!1,tt.toString(e))}lte(t,e){return this.setLimit("max",t,!0,tt.toString(e))}lt(t,e){return this.setLimit("max",t,!1,tt.toString(e))}
setLimit(t,e,r,n){return new Tt({...this._def,checks:[...this._def.checks,{kind:t,value:e,inclusive:r,message:tt.toString(n)}]})}_addCheck(t){return new Tt({
...this._def,checks:[...this._def.checks,t]})}int(t){return this._addCheck({kind:"int",message:tt.toString(t)})}positive(t){return this._addCheck({kind:"min",
value:0,inclusive:!1,message:tt.toString(t)})}negative(t){return this._addCheck({kind:"max",value:0,inclusive:!1,message:tt.toString(t)})}nonpositive(t){
return this._addCheck({kind:"max",value:0,inclusive:!0,message:tt.toString(t)})}nonnegative(t){return this._addCheck({kind:"min",value:0,inclusive:!0,
message:tt.toString(t)})}multipleOf(t,e){return this._addCheck({kind:"multipleOf",value:t,message:tt.toString(e)})}finite(t){return this._addCheck({kind:"finite",
message:tt.toString(t)})}safe(t){return this._addCheck({kind:"min",inclusive:!0,value:Number.MIN_SAFE_INTEGER,message:tt.toString(t)})._addCheck({kind:"max",
inclusive:!0,value:Number.MAX_SAFE_INTEGER,message:tt.toString(t)})}get minValue(){let t=null
;for(const e of this._def.checks)"min"===e.kind&&(null===t||e.value>t)&&(t=e.value);return t}get maxValue(){let t=null
;for(const e of this._def.checks)"max"===e.kind&&(null===t||e.value<t)&&(t=e.value);return t}get isInt(){
return!!this._def.checks.find((t=>"int"===t.kind||"multipleOf"===t.kind&&j.isInteger(t.value)))}get isFinite(){let t=null,e=null;for(const r of this._def.checks){
if("finite"===r.kind||"int"===r.kind||"multipleOf"===r.kind)return!0
;"min"===r.kind?(null===e||r.value>e)&&(e=r.value):"max"===r.kind&&(null===t||r.value<t)&&(t=r.value)}return Number.isFinite(e)&&Number.isFinite(t)}}
Tt.create=t=>new Tt({checks:[],typeName:be.ZodNumber,coerce:(null==t?void 0:t.coerce)||!1,...it(t)});class At extends at{constructor(){super(...arguments),
this.min=this.gte,this.max=this.lte}_parse(t){if(this._def.coerce)try{t.data=BigInt(t.data)}catch(e){return this._getInvalidInput(t)}
if(this._getType(t)!==R.bigint)return this._getInvalidInput(t);let e;const r=new Z;for(const n of this._def.checks)if("min"===n.kind){
(n.inclusive?t.data<n.value:t.data<=n.value)&&(e=this._getOrReturnCtx(t,e),q(e,{code:B.too_small,type:"bigint",minimum:n.value,inclusive:n.inclusive,
message:n.message}),r.dirty())}else if("max"===n.kind){(n.inclusive?t.data>n.value:t.data>=n.value)&&(e=this._getOrReturnCtx(t,e),q(e,{code:B.too_big,type:"bigint",
maximum:n.value,inclusive:n.inclusive,message:n.message}),r.dirty())}else"multipleOf"===n.kind?t.data%n.value!==BigInt(0)&&(e=this._getOrReturnCtx(t,e),q(e,{
code:B.not_multiple_of,multipleOf:n.value,message:n.message}),r.dirty()):j.assertNever(n);return{status:r.value,value:t.data}}_getInvalidInput(t){
const e=this._getOrReturnCtx(t);return q(e,{code:B.invalid_type,expected:R.bigint,received:e.parsedType}),K}gte(t,e){return this.setLimit("min",t,!0,tt.toString(e))}
gt(t,e){return this.setLimit("min",t,!1,tt.toString(e))}lte(t,e){return this.setLimit("max",t,!0,tt.toString(e))}lt(t,e){
return this.setLimit("max",t,!1,tt.toString(e))}setLimit(t,e,r,n){return new At({...this._def,checks:[...this._def.checks,{kind:t,value:e,inclusive:r,
message:tt.toString(n)}]})}_addCheck(t){return new At({...this._def,checks:[...this._def.checks,t]})}positive(t){return this._addCheck({kind:"min",value:BigInt(0),
inclusive:!1,message:tt.toString(t)})}negative(t){return this._addCheck({kind:"max",value:BigInt(0),inclusive:!1,message:tt.toString(t)})}nonpositive(t){
return this._addCheck({kind:"max",value:BigInt(0),inclusive:!0,message:tt.toString(t)})}nonnegative(t){return this._addCheck({kind:"min",value:BigInt(0),
inclusive:!0,message:tt.toString(t)})}multipleOf(t,e){return this._addCheck({kind:"multipleOf",value:t,message:tt.toString(e)})}get minValue(){let t=null
;for(const e of this._def.checks)"min"===e.kind&&(null===t||e.value>t)&&(t=e.value);return t}get maxValue(){let t=null
;for(const e of this._def.checks)"max"===e.kind&&(null===t||e.value<t)&&(t=e.value);return t}}At.create=t=>{var e;return new At({checks:[],typeName:be.ZodBigInt,
coerce:null!==(e=null==t?void 0:t.coerce)&&void 0!==e&&e,...it(t)})};class It extends at{_parse(t){this._def.coerce&&(t.data=Boolean(t.data))
;if(this._getType(t)!==R.boolean){const e=this._getOrReturnCtx(t);return q(e,{code:B.invalid_type,expected:R.boolean,received:e.parsedType}),K}return $(t.data)}}
It.create=t=>new It({typeName:be.ZodBoolean,coerce:(null==t?void 0:t.coerce)||!1,...it(t)});class Lt extends at{_parse(t){this._def.coerce&&(t.data=new Date(t.data))
;if(this._getType(t)!==R.date){const e=this._getOrReturnCtx(t);return q(e,{code:B.invalid_type,expected:R.date,received:e.parsedType}),K}if(isNaN(t.data.getTime())){
return q(this._getOrReturnCtx(t),{code:B.invalid_date}),K}const e=new Z;let r
;for(const n of this._def.checks)"min"===n.kind?t.data.getTime()<n.value&&(r=this._getOrReturnCtx(t,r),q(r,{code:B.too_small,message:n.message,inclusive:!0,exact:!1,
minimum:n.value,type:"date"}),e.dirty()):"max"===n.kind?t.data.getTime()>n.value&&(r=this._getOrReturnCtx(t,r),q(r,{code:B.too_big,message:n.message,inclusive:!0,
exact:!1,maximum:n.value,type:"date"}),e.dirty()):j.assertNever(n);return{status:e.value,value:new Date(t.data.getTime())}}_addCheck(t){return new Lt({...this._def,
checks:[...this._def.checks,t]})}min(t,e){return this._addCheck({kind:"min",value:t.getTime(),message:tt.toString(e)})}max(t,e){return this._addCheck({kind:"max",
value:t.getTime(),message:tt.toString(e)})}get minDate(){let t=null;for(const e of this._def.checks)"min"===e.kind&&(null===t||e.value>t)&&(t=e.value)
;return null!=t?new Date(t):null}get maxDate(){let t=null;for(const e of this._def.checks)"max"===e.kind&&(null===t||e.value<t)&&(t=e.value)
;return null!=t?new Date(t):null}}Lt.create=t=>new Lt({checks:[],coerce:(null==t?void 0:t.coerce)||!1,typeName:be.ZodDate,...it(t)});class Nt extends at{_parse(t){
if(this._getType(t)!==R.symbol){const e=this._getOrReturnCtx(t);return q(e,{code:B.invalid_type,expected:R.symbol,received:e.parsedType}),K}return $(t.data)}}
Nt.create=t=>new Nt({typeName:be.ZodSymbol,...it(t)});class Rt extends at{_parse(t){if(this._getType(t)!==R.undefined){const e=this._getOrReturnCtx(t);return q(e,{
code:B.invalid_type,expected:R.undefined,received:e.parsedType}),K}return $(t.data)}}Rt.create=t=>new Rt({typeName:be.ZodUndefined,...it(t)});class Dt extends at{
_parse(t){if(this._getType(t)!==R.null){const e=this._getOrReturnCtx(t);return q(e,{code:B.invalid_type,expected:R.null,received:e.parsedType}),K}return $(t.data)}}
Dt.create=t=>new Dt({typeName:be.ZodNull,...it(t)});class Bt extends at{constructor(){super(...arguments),this._any=!0}_parse(t){return $(t.data)}}
Bt.create=t=>new Bt({typeName:be.ZodAny,...it(t)});class Ft extends at{constructor(){super(...arguments),this._unknown=!0}_parse(t){return $(t.data)}}
Ft.create=t=>new Ft({typeName:be.ZodUnknown,...it(t)});class Mt extends at{_parse(t){const e=this._getOrReturnCtx(t);return q(e,{code:B.invalid_type,
expected:R.never,received:e.parsedType}),K}}Mt.create=t=>new Mt({typeName:be.ZodNever,...it(t)});class Gt extends at{_parse(t){if(this._getType(t)!==R.undefined){
const e=this._getOrReturnCtx(t);return q(e,{code:B.invalid_type,expected:R.void,received:e.parsedType}),K}return $(t.data)}}Gt.create=t=>new Gt({typeName:be.ZodVoid,
...it(t)});class Vt extends at{_parse(t){const{ctx:e,status:r}=this._processInputParams(t),n=this._def;if(e.parsedType!==R.array)return q(e,{code:B.invalid_type,
expected:R.array,received:e.parsedType}),K;if(null!==n.exactLength){const t=e.data.length>n.exactLength.value,o=e.data.length<n.exactLength.value;(t||o)&&(q(e,{
code:t?B.too_big:B.too_small,minimum:o?n.exactLength.value:void 0,maximum:t?n.exactLength.value:void 0,type:"array",inclusive:!0,exact:!0,
message:n.exactLength.message}),r.dirty())}if(null!==n.minLength&&e.data.length<n.minLength.value&&(q(e,{code:B.too_small,minimum:n.minLength.value,type:"array",
inclusive:!0,exact:!1,message:n.minLength.message}),r.dirty()),null!==n.maxLength&&e.data.length>n.maxLength.value&&(q(e,{code:B.too_big,maximum:n.maxLength.value,
type:"array",inclusive:!0,exact:!1,message:n.maxLength.message
}),r.dirty()),e.common.async)return Promise.all([...e.data].map(((t,r)=>n.type._parseAsync(new nt(e,t,e.path,r))))).then((t=>Z.mergeArray(r,t)))
;const o=[...e.data].map(((t,r)=>n.type._parseSync(new nt(e,t,e.path,r))));return Z.mergeArray(r,o)}get element(){return this._def.type}min(t,e){return new Vt({
...this._def,minLength:{value:t,message:tt.toString(e)}})}max(t,e){return new Vt({...this._def,maxLength:{value:t,message:tt.toString(e)}})}length(t,e){
return new Vt({...this._def,exactLength:{value:t,message:tt.toString(e)}})}nonempty(t){return this.min(1,t)}}function Ut(t){if(t instanceof qt){const e={}
;for(const r in t.shape){const n=t.shape[r];e[r]=se.create(Ut(n))}return new qt({...t._def,shape:()=>e})}return t instanceof Vt?new Vt({...t._def,type:Ut(t.element)
}):t instanceof se?se.create(Ut(t.unwrap())):t instanceof ue?ue.create(Ut(t.unwrap())):t instanceof Yt?Yt.create(t.items.map((t=>Ut(t)))):t}Vt.create=(t,e)=>new Vt({
type:t,minLength:null,maxLength:null,exactLength:null,typeName:be.ZodArray,...it(e)});class qt extends at{constructor(){super(...arguments),this._cached=null,
this.nonstrict=this.passthrough,this.augment=this.extend}_getCached(){if(null!==this._cached)return this._cached;const t=this._def.shape(),e=j.objectKeys(t)
;return this._cached={shape:t,keys:e}}_parse(t){if(this._getType(t)!==R.object){const e=this._getOrReturnCtx(t);return q(e,{code:B.invalid_type,expected:R.object,
received:e.parsedType}),K}const{status:e,ctx:r}=this._processInputParams(t),{shape:n,keys:o}=this._getCached(),i=[]
;if(!(this._def.catchall instanceof Mt&&"strip"===this._def.unknownKeys))for(const t in r.data)o.includes(t)||i.push(t);const a=[];for(const t of o){
const e=n[t],o=r.data[t];a.push({key:{status:"valid",value:t},value:e._parse(new nt(r,o,r.path,t)),alwaysSet:t in r.data})}if(this._def.catchall instanceof Mt){
const t=this._def.unknownKeys;if("passthrough"===t)for(const t of i)a.push({key:{status:"valid",value:t},value:{status:"valid",value:r.data[t]}
});else if("strict"===t)i.length>0&&(q(r,{code:B.unrecognized_keys,keys:i
}),e.dirty());else if("strip"!==t)throw new Error("Internal ZodObject error: invalid unknownKeys value.")}else{const t=this._def.catchall;for(const e of i){
const n=r.data[e];a.push({key:{status:"valid",value:e},value:t._parse(new nt(r,n,r.path,e)),alwaysSet:e in r.data})}}
return r.common.async?Promise.resolve().then((async()=>{const t=[];for(const e of a){const r=await e.key,n=await e.value;t.push({key:r,value:n,alwaysSet:e.alwaysSet
})}return t})).then((t=>Z.mergeObjectSync(e,t))):Z.mergeObjectSync(e,a)}get shape(){return this._def.shape()}strict(t){return tt.errToObj,new qt({...this._def,
unknownKeys:"strict",...void 0!==t?{errorMap:(e,r)=>{var n,o,i,a
;const s=null!==(i=null===(o=(n=this._def).errorMap)||void 0===o?void 0:o.call(n,e,r).message)&&void 0!==i?i:r.defaultError;return"unrecognized_keys"===e.code?{
message:null!==(a=tt.errToObj(t).message)&&void 0!==a?a:s}:{message:s}}}:{}})}strip(){return new qt({...this._def,unknownKeys:"strip"})}passthrough(){return new qt({
...this._def,unknownKeys:"passthrough"})}extend(t){return new qt({...this._def,shape:()=>({...this._def.shape(),...t})})}merge(t){return new qt({
unknownKeys:t._def.unknownKeys,catchall:t._def.catchall,shape:()=>({...this._def.shape(),...t._def.shape()}),typeName:be.ZodObject})}setKey(t,e){
return this.augment({[t]:e})}catchall(t){return new qt({...this._def,catchall:t})}pick(t){const e={};return j.objectKeys(t).forEach((r=>{
t[r]&&this.shape[r]&&(e[r]=this.shape[r])})),new qt({...this._def,shape:()=>e})}omit(t){const e={};return j.objectKeys(this.shape).forEach((r=>{
t[r]||(e[r]=this.shape[r])})),new qt({...this._def,shape:()=>e})}deepPartial(){return Ut(this)}partial(t){const e={};return j.objectKeys(this.shape).forEach((r=>{
const n=this.shape[r];t&&!t[r]?e[r]=n:e[r]=n.optional()})),new qt({...this._def,shape:()=>e})}required(t){const e={};return j.objectKeys(this.shape).forEach((r=>{
if(t&&!t[r])e[r]=this.shape[r];else{let t=this.shape[r];for(;t instanceof se;)t=t._def.innerType;e[r]=t}})),new qt({...this._def,shape:()=>e})}keyof(){
return re(j.objectKeys(this.shape))}}qt.create=(t,e)=>new qt({shape:()=>t,unknownKeys:"strip",catchall:Mt.create(),typeName:be.ZodObject,...it(e)}),
qt.strictCreate=(t,e)=>new qt({shape:()=>t,unknownKeys:"strict",catchall:Mt.create(),typeName:be.ZodObject,...it(e)}),qt.lazycreate=(t,e)=>new qt({shape:t,
unknownKeys:"strip",catchall:Mt.create(),typeName:be.ZodObject,...it(e)});class Zt extends at{_parse(t){const{ctx:e}=this._processInputParams(t),r=this._def.options
;if(e.common.async)return Promise.all(r.map((async t=>{const r={...e,common:{...e.common,issues:[]},parent:null};return{result:await t._parseAsync({data:e.data,
path:e.path,parent:r}),ctx:r}}))).then((function(t){for(const e of t)if("valid"===e.result.status)return e.result
;for(const r of t)if("dirty"===r.result.status)return e.common.issues.push(...r.ctx.common.issues),r.result;const r=t.map((t=>new F(t.ctx.common.issues)))
;return q(e,{code:B.invalid_union,unionErrors:r}),K}));{let t;const n=[];for(const o of r){const r={...e,common:{...e.common,issues:[]},parent:null},i=o._parseSync({
data:e.data,path:e.path,parent:r});if("valid"===i.status)return i;"dirty"!==i.status||t||(t={result:i,ctx:r}),r.common.issues.length&&n.push(r.common.issues)}
if(t)return e.common.issues.push(...t.ctx.common.issues),t.result;const o=n.map((t=>new F(t)));return q(e,{code:B.invalid_union,unionErrors:o}),K}}get options(){
return this._def.options}}Zt.create=(t,e)=>new Zt({options:t,typeName:be.ZodUnion,...it(e)})
;const Kt=t=>t instanceof te?Kt(t.schema):t instanceof ae?Kt(t.innerType()):t instanceof ee?[t.value]:t instanceof ne?t.options:t instanceof oe?j.objectValues(t.enum):t instanceof ce?Kt(t._def.innerType):t instanceof Rt?[void 0]:t instanceof Dt?[null]:t instanceof se?[void 0,...Kt(t.unwrap())]:t instanceof ue?[null,...Kt(t.unwrap())]:t instanceof pe||t instanceof ye?Kt(t.unwrap()):t instanceof le?Kt(t._def.innerType):[]
;class zt extends at{_parse(t){const{ctx:e}=this._processInputParams(t);if(e.parsedType!==R.object)return q(e,{code:B.invalid_type,expected:R.object,
received:e.parsedType}),K;const r=this.discriminator,n=e.data[r],o=this.optionsMap.get(n);return o?e.common.async?o._parseAsync({data:e.data,path:e.path,parent:e
}):o._parseSync({data:e.data,path:e.path,parent:e}):(q(e,{code:B.invalid_union_discriminator,options:Array.from(this.optionsMap.keys()),path:[r]}),K)}
get discriminator(){return this._def.discriminator}get options(){return this._def.options}get optionsMap(){return this._def.optionsMap}static create(t,e,r){
const n=new Map;for(const r of e){const e=Kt(r.shape[t])
;if(!e.length)throw new Error(`A discriminator value for key \`${t}\` could not be extracted from all schema options`);for(const o of e){
if(n.has(o))throw new Error(`Discriminator property ${String(t)} has duplicate value ${String(o)}`);n.set(o,r)}}return new zt({typeName:be.ZodDiscriminatedUnion,
discriminator:t,options:e,optionsMap:n,...it(r)})}}function $t(t,e){const r=D(t),n=D(e);if(t===e)return{valid:!0,data:t};if(r===R.object&&n===R.object){
const r=j.objectKeys(e),n=j.objectKeys(t).filter((t=>-1!==r.indexOf(t))),o={...t,...e};for(const r of n){const n=$t(t[r],e[r]);if(!n.valid)return{valid:!1}
;o[r]=n.data}return{valid:!0,data:o}}if(r===R.array&&n===R.array){if(t.length!==e.length)return{valid:!1};const r=[];for(let n=0;n<t.length;n++){
const o=$t(t[n],e[n]);if(!o.valid)return{valid:!1};r.push(o.data)}return{valid:!0,data:r}}return r===R.date&&n===R.date&&+t==+e?{valid:!0,data:t}:{valid:!1}}
class Ht extends at{_parse(t){const{status:e,ctx:r}=this._processInputParams(t),n=(t,n)=>{if(H(t)||H(n))return K;const o=$t(t.value,n.value)
;return o.valid?((Y(t)||Y(n))&&e.dirty(),{status:e.value,value:o.data}):(q(r,{code:B.invalid_intersection_types}),K)}
;return r.common.async?Promise.all([this._def.left._parseAsync({data:r.data,path:r.path,parent:r}),this._def.right._parseAsync({data:r.data,path:r.path,parent:r
})]).then((([t,e])=>n(t,e))):n(this._def.left._parseSync({data:r.data,path:r.path,parent:r}),this._def.right._parseSync({data:r.data,path:r.path,parent:r}))}}
Ht.create=(t,e,r)=>new Ht({left:t,right:e,typeName:be.ZodIntersection,...it(r)});class Yt extends at{_parse(t){const{status:e,ctx:r}=this._processInputParams(t)
;if(r.parsedType!==R.array)return q(r,{code:B.invalid_type,expected:R.array,received:r.parsedType}),K;if(r.data.length<this._def.items.length)return q(r,{
code:B.too_small,minimum:this._def.items.length,inclusive:!0,exact:!1,type:"array"}),K;!this._def.rest&&r.data.length>this._def.items.length&&(q(r,{code:B.too_big,
maximum:this._def.items.length,inclusive:!0,exact:!1,type:"array"}),e.dirty());const n=[...r.data].map(((t,e)=>{const n=this._def.items[e]||this._def.rest
;return n?n._parse(new nt(r,t,r.path,e)):null})).filter((t=>!!t));return r.common.async?Promise.all(n).then((t=>Z.mergeArray(e,t))):Z.mergeArray(e,n)}get items(){
return this._def.items}rest(t){return new Yt({...this._def,rest:t})}}Yt.create=(t,e)=>{
if(!Array.isArray(t))throw new Error("You must pass an array of schemas to z.tuple([ ... ])");return new Yt({items:t,typeName:be.ZodTuple,rest:null,...it(e)})}
;class Jt extends at{get keySchema(){return this._def.keyType}get valueSchema(){return this._def.valueType}_parse(t){
const{status:e,ctx:r}=this._processInputParams(t);if(r.parsedType!==R.object)return q(r,{code:B.invalid_type,expected:R.object,received:r.parsedType}),K
;const n=[],o=this._def.keyType,i=this._def.valueType;for(const t in r.data)n.push({key:o._parse(new nt(r,t,r.path,t)),value:i._parse(new nt(r,r.data[t],r.path,t)),
alwaysSet:t in r.data});return r.common.async?Z.mergeObjectAsync(e,n):Z.mergeObjectSync(e,n)}get element(){return this._def.valueType}static create(t,e,r){
return new Jt(e instanceof at?{keyType:t,valueType:e,typeName:be.ZodRecord,...it(r)}:{keyType:jt.create(),valueType:t,typeName:be.ZodRecord,...it(e)})}}
class Wt extends at{get keySchema(){return this._def.keyType}get valueSchema(){return this._def.valueType}_parse(t){const{status:e,ctx:r}=this._processInputParams(t)
;if(r.parsedType!==R.map)return q(r,{code:B.invalid_type,expected:R.map,received:r.parsedType}),K
;const n=this._def.keyType,o=this._def.valueType,i=[...r.data.entries()].map((([t,e],i)=>({key:n._parse(new nt(r,t,r.path,[i,"key"])),
value:o._parse(new nt(r,e,r.path,[i,"value"]))})));if(r.common.async){const t=new Map;return Promise.resolve().then((async()=>{for(const r of i){
const n=await r.key,o=await r.value;if("aborted"===n.status||"aborted"===o.status)return K;"dirty"!==n.status&&"dirty"!==o.status||e.dirty(),t.set(n.value,o.value)}
return{status:e.value,value:t}}))}{const t=new Map;for(const r of i){const n=r.key,o=r.value;if("aborted"===n.status||"aborted"===o.status)return K
;"dirty"!==n.status&&"dirty"!==o.status||e.dirty(),t.set(n.value,o.value)}return{status:e.value,value:t}}}}Wt.create=(t,e,r)=>new Wt({valueType:e,keyType:t,
typeName:be.ZodMap,...it(r)});class Qt extends at{_parse(t){const{status:e,ctx:r}=this._processInputParams(t);if(r.parsedType!==R.set)return q(r,{
code:B.invalid_type,expected:R.set,received:r.parsedType}),K;const n=this._def;null!==n.minSize&&r.data.size<n.minSize.value&&(q(r,{code:B.too_small,
minimum:n.minSize.value,type:"set",inclusive:!0,exact:!1,message:n.minSize.message}),e.dirty()),null!==n.maxSize&&r.data.size>n.maxSize.value&&(q(r,{code:B.too_big,
maximum:n.maxSize.value,type:"set",inclusive:!0,exact:!1,message:n.maxSize.message}),e.dirty());const o=this._def.valueType;function i(t){const r=new Set
;for(const n of t){if("aborted"===n.status)return K;"dirty"===n.status&&e.dirty(),r.add(n.value)}return{status:e.value,value:r}}
const a=[...r.data.values()].map(((t,e)=>o._parse(new nt(r,t,r.path,e))));return r.common.async?Promise.all(a).then((t=>i(t))):i(a)}min(t,e){return new Qt({
...this._def,minSize:{value:t,message:tt.toString(e)}})}max(t,e){return new Qt({...this._def,maxSize:{value:t,message:tt.toString(e)}})}size(t,e){
return this.min(t,e).max(t,e)}nonempty(t){return this.min(1,t)}}Qt.create=(t,e)=>new Qt({valueType:t,minSize:null,maxSize:null,typeName:be.ZodSet,...it(e)})
;class Xt extends at{constructor(){super(...arguments),this.validate=this.implement}_parse(t){const{ctx:e}=this._processInputParams(t)
;if(e.parsedType!==R.function)return q(e,{code:B.invalid_type,expected:R.function,received:e.parsedType}),K;function r(t,r){return U({data:t,path:e.path,
errorMaps:[e.common.contextualErrorMap,e.schemaErrorMap,V(),M].filter((t=>!!t)),issueData:{code:B.invalid_arguments,argumentsError:r}})}function n(t,r){return U({
data:t,path:e.path,errorMaps:[e.common.contextualErrorMap,e.schemaErrorMap,V(),M].filter((t=>!!t)),issueData:{code:B.invalid_return_type,returnTypeError:r}})}
const o={errorMap:e.common.contextualErrorMap},i=e.data;if(this._def.returns instanceof ie){const t=this;return $((async function(...e){
const a=new F([]),s=await t._def.args.parseAsync(e,o).catch((t=>{throw a.addIssue(r(e,t)),a})),u=await Reflect.apply(i,this,s)
;return await t._def.returns._def.type.parseAsync(u,o).catch((t=>{throw a.addIssue(n(u,t)),a}))}))}{const t=this;return $((function(...e){
const a=t._def.args.safeParse(e,o);if(!a.success)throw new F([r(e,a.error)]);const s=Reflect.apply(i,this,a.data),u=t._def.returns.safeParse(s,o)
;if(!u.success)throw new F([n(s,u.error)]);return u.data}))}}parameters(){return this._def.args}returnType(){return this._def.returns}args(...t){return new Xt({
...this._def,args:Yt.create(t).rest(Ft.create())})}returns(t){return new Xt({...this._def,returns:t})}implement(t){return this.parse(t)}strictImplement(t){
return this.parse(t)}static create(t,e,r){return new Xt({args:t||Yt.create([]).rest(Ft.create()),returns:e||Ft.create(),typeName:be.ZodFunction,...it(r)})}}
class te extends at{get schema(){return this._def.getter()}_parse(t){const{ctx:e}=this._processInputParams(t);return this._def.getter()._parse({data:e.data,
path:e.path,parent:e})}}te.create=(t,e)=>new te({getter:t,typeName:be.ZodLazy,...it(e)});class ee extends at{_parse(t){if(t.data!==this._def.value){
const e=this._getOrReturnCtx(t);return q(e,{received:e.data,code:B.invalid_literal,expected:this._def.value}),K}return{status:"valid",value:t.data}}get value(){
return this._def.value}}function re(t,e){return new ne({values:t,typeName:be.ZodEnum,...it(e)})}ee.create=(t,e)=>new ee({value:t,typeName:be.ZodLiteral,...it(e)})
;class ne extends at{constructor(){super(...arguments),et.set(this,void 0)}_parse(t){if("string"!=typeof t.data){const e=this._getOrReturnCtx(t),r=this._def.values
;return q(e,{expected:j.joinValues(r),received:e.parsedType,code:B.invalid_type}),K}if(Q(this,et,"f")||X(this,et,new Set(this._def.values),"f"),
!Q(this,et,"f").has(t.data)){const e=this._getOrReturnCtx(t),r=this._def.values;return q(e,{received:e.data,code:B.invalid_enum_value,options:r}),K}return $(t.data)}
get options(){return this._def.values}get enum(){const t={};for(const e of this._def.values)t[e]=e;return t}get Values(){const t={}
;for(const e of this._def.values)t[e]=e;return t}get Enum(){const t={};for(const e of this._def.values)t[e]=e;return t}extract(t,e=this._def){return ne.create(t,{
...this._def,...e})}exclude(t,e=this._def){return ne.create(this.options.filter((e=>!t.includes(e))),{...this._def,...e})}}et=new WeakMap,ne.create=re
;class oe extends at{constructor(){super(...arguments),rt.set(this,void 0)}_parse(t){const e=j.getValidEnumValues(this._def.values),r=this._getOrReturnCtx(t)
;if(r.parsedType!==R.string&&r.parsedType!==R.number){const t=j.objectValues(e);return q(r,{expected:j.joinValues(t),received:r.parsedType,code:B.invalid_type}),K}
if(Q(this,rt,"f")||X(this,rt,new Set(j.getValidEnumValues(this._def.values)),"f"),!Q(this,rt,"f").has(t.data)){const t=j.objectValues(e);return q(r,{received:r.data,
code:B.invalid_enum_value,options:t}),K}return $(t.data)}get enum(){return this._def.values}}rt=new WeakMap,oe.create=(t,e)=>new oe({values:t,
typeName:be.ZodNativeEnum,...it(e)});class ie extends at{unwrap(){return this._def.type}_parse(t){const{ctx:e}=this._processInputParams(t)
;if(e.parsedType!==R.promise&&!1===e.common.async)return q(e,{code:B.invalid_type,expected:R.promise,received:e.parsedType}),K
;const r=e.parsedType===R.promise?e.data:Promise.resolve(e.data);return $(r.then((t=>this._def.type.parseAsync(t,{path:e.path,errorMap:e.common.contextualErrorMap
}))))}}ie.create=(t,e)=>new ie({type:t,typeName:be.ZodPromise,...it(e)});class ae extends at{innerType(){return this._def.schema}sourceType(){
return this._def.schema._def.typeName===be.ZodEffects?this._def.schema.sourceType():this._def.schema}_parse(t){
const{status:e,ctx:r}=this._processInputParams(t),n=this._def.effect||null,o={addIssue:t=>{q(r,t),t.fatal?e.abort():e.dirty()},get path(){return r.path}}
;if(o.addIssue=o.addIssue.bind(o),"preprocess"===n.type){const t=n.transform(r.data,o);if(r.common.async)return Promise.resolve(t).then((async t=>{
if("aborted"===e.value)return K;const n=await this._def.schema._parseAsync({data:t,path:r.path,parent:r})
;return"aborted"===n.status?K:"dirty"===n.status||"dirty"===e.value?z(n.value):n}));{if("aborted"===e.value)return K;const n=this._def.schema._parseSync({data:t,
path:r.path,parent:r});return"aborted"===n.status?K:"dirty"===n.status||"dirty"===e.value?z(n.value):n}}if("refinement"===n.type){const t=t=>{
const e=n.refinement(t,o);if(r.common.async)return Promise.resolve(e)
;if(e instanceof Promise)throw new Error("Async refinement encountered during synchronous parse operation. Use .parseAsync instead.");return t}
;if(!1===r.common.async){const n=this._def.schema._parseSync({data:r.data,path:r.path,parent:r});return"aborted"===n.status?K:("dirty"===n.status&&e.dirty(),
t(n.value),{status:e.value,value:n.value})}return this._def.schema._parseAsync({data:r.data,path:r.path,parent:r
}).then((r=>"aborted"===r.status?K:("dirty"===r.status&&e.dirty(),t(r.value).then((()=>({status:e.value,value:r.value}))))))}if("transform"===n.type){
if(!1===r.common.async){const t=this._def.schema._parseSync({data:r.data,path:r.path,parent:r});if(!J(t))return t;const i=n.transform(t.value,o)
;if(i instanceof Promise)throw new Error("Asynchronous transform encountered during synchronous parse operation. Use .parseAsync instead.");return{status:e.value,
value:i}}return this._def.schema._parseAsync({data:r.data,path:r.path,parent:r}).then((t=>J(t)?Promise.resolve(n.transform(t.value,o)).then((t=>({status:e.value,
value:t}))):t))}j.assertNever(n)}}ae.create=(t,e,r)=>new ae({schema:t,typeName:be.ZodEffects,effect:e,...it(r)}),ae.createWithPreprocess=(t,e,r)=>new ae({schema:e,
effect:{type:"preprocess",transform:t},typeName:be.ZodEffects,...it(r)});class se extends at{_parse(t){
return this._getType(t)===R.undefined?$(void 0):this._def.innerType._parse(t)}unwrap(){return this._def.innerType}}se.create=(t,e)=>new se({innerType:t,
typeName:be.ZodOptional,...it(e)});class ue extends at{_parse(t){return this._getType(t)===R.null?$(null):this._def.innerType._parse(t)}unwrap(){
return this._def.innerType}}ue.create=(t,e)=>new ue({innerType:t,typeName:be.ZodNullable,...it(e)});class ce extends at{_parse(t){
const{ctx:e}=this._processInputParams(t);let r=e.data;return e.parsedType===R.undefined&&(r=this._def.defaultValue()),this._def.innerType._parse({data:r,path:e.path,
parent:e})}removeDefault(){return this._def.innerType}}ce.create=(t,e)=>new ce({innerType:t,typeName:be.ZodDefault,
defaultValue:"function"==typeof e.default?e.default:()=>e.default,...it(e)});class le extends at{_parse(t){const{ctx:e}=this._processInputParams(t),r={...e,common:{
...e.common,issues:[]}},n=this._def.innerType._parse({data:r.data,path:r.path,parent:{...r}});return W(n)?n.then((t=>({status:"valid",
value:"valid"===t.status?t.value:this._def.catchValue({get error(){return new F(r.common.issues)},input:r.data})}))):{status:"valid",
value:"valid"===n.status?n.value:this._def.catchValue({get error(){return new F(r.common.issues)},input:r.data})}}removeCatch(){return this._def.innerType}}
le.create=(t,e)=>new le({innerType:t,typeName:be.ZodCatch,catchValue:"function"==typeof e.catch?e.catch:()=>e.catch,...it(e)});class fe extends at{_parse(t){
if(this._getType(t)!==R.nan){const e=this._getOrReturnCtx(t);return q(e,{code:B.invalid_type,expected:R.nan,received:e.parsedType}),K}return{status:"valid",
value:t.data}}}fe.create=t=>new fe({typeName:be.ZodNaN,...it(t)});const he=Symbol("zod_brand");class pe extends at{_parse(t){
const{ctx:e}=this._processInputParams(t),r=e.data;return this._def.type._parse({data:r,path:e.path,parent:e})}unwrap(){return this._def.type}}class de extends at{
_parse(t){const{status:e,ctx:r}=this._processInputParams(t);if(r.common.async){return(async()=>{const t=await this._def.in._parseAsync({data:r.data,path:r.path,
parent:r});return"aborted"===t.status?K:"dirty"===t.status?(e.dirty(),z(t.value)):this._def.out._parseAsync({data:t.value,path:r.path,parent:r})})()}{
const t=this._def.in._parseSync({data:r.data,path:r.path,parent:r});return"aborted"===t.status?K:"dirty"===t.status?(e.dirty(),{status:"dirty",value:t.value
}):this._def.out._parseSync({data:t.value,path:r.path,parent:r})}}static create(t,e){return new de({in:t,out:e,typeName:be.ZodPipeline})}}class ye extends at{
_parse(t){const e=this._def.innerType._parse(t),r=t=>(J(t)&&(t.value=Object.freeze(t.value)),t);return W(e)?e.then((t=>r(t))):r(e)}unwrap(){
return this._def.innerType}}function ve(t,e){const r="function"==typeof t?t(e):"string"==typeof t?{message:t}:t;return"string"==typeof r?{message:r}:r}
function ge(t,e={},r){return t?Bt.create().superRefine(((n,o)=>{var i,a;const s=t(n);if(s instanceof Promise)return s.then((t=>{var i,a;if(!t){
const t=ve(e,n),s=null===(a=null!==(i=t.fatal)&&void 0!==i?i:r)||void 0===a||a;o.addIssue({code:"custom",...t,fatal:s})}}));if(!s){
const t=ve(e,n),s=null===(a=null!==(i=t.fatal)&&void 0!==i?i:r)||void 0===a||a;o.addIssue({code:"custom",...t,fatal:s})}})):Bt.create()}ye.create=(t,e)=>new ye({
innerType:t,typeName:be.ZodReadonly,...it(e)});const me={object:qt.lazycreate};var be;!function(t){t.ZodString="ZodString",t.ZodNumber="ZodNumber",t.ZodNaN="ZodNaN",
t.ZodBigInt="ZodBigInt",t.ZodBoolean="ZodBoolean",t.ZodDate="ZodDate",t.ZodSymbol="ZodSymbol",t.ZodUndefined="ZodUndefined",t.ZodNull="ZodNull",t.ZodAny="ZodAny",
t.ZodUnknown="ZodUnknown",t.ZodNever="ZodNever",t.ZodVoid="ZodVoid",t.ZodArray="ZodArray",t.ZodObject="ZodObject",t.ZodUnion="ZodUnion",
t.ZodDiscriminatedUnion="ZodDiscriminatedUnion",t.ZodIntersection="ZodIntersection",t.ZodTuple="ZodTuple",t.ZodRecord="ZodRecord",t.ZodMap="ZodMap",
t.ZodSet="ZodSet",t.ZodFunction="ZodFunction",t.ZodLazy="ZodLazy",t.ZodLiteral="ZodLiteral",t.ZodEnum="ZodEnum",t.ZodEffects="ZodEffects",
t.ZodNativeEnum="ZodNativeEnum",t.ZodOptional="ZodOptional",t.ZodNullable="ZodNullable",t.ZodDefault="ZodDefault",t.ZodCatch="ZodCatch",t.ZodPromise="ZodPromise",
t.ZodBranded="ZodBranded",t.ZodPipeline="ZodPipeline",t.ZodReadonly="ZodReadonly"}(be||(be={}))
;const we=jt.create,_e=Tt.create,xe=fe.create,Pe=At.create,Se=It.create,Ee=Lt.create,Oe=Nt.create,ke=Rt.create,je=Dt.create,Ce=Bt.create,Te=Ft.create,Ae=Mt.create,Ie=Gt.create,Le=Vt.create,Ne=qt.create,Re=qt.strictCreate,De=Zt.create,Be=zt.create,Fe=Ht.create,Me=Yt.create,Ge=Jt.create,Ve=Wt.create,Ue=Qt.create,qe=Xt.create,Ze=te.create,Ke=ee.create,ze=ne.create,$e=oe.create,He=ie.create,Ye=ae.create,Je=se.create,We=ue.create,Qe=ae.createWithPreprocess,Xe=de.create,tr={
string:t=>jt.create({...t,coerce:!0}),number:t=>Tt.create({...t,coerce:!0}),boolean:t=>It.create({...t,coerce:!0}),bigint:t=>At.create({...t,coerce:!0}),
date:t=>Lt.create({...t,coerce:!0})},er=K;var rr=Object.freeze({__proto__:null,defaultErrorMap:M,setErrorMap:function(t){G=t},getErrorMap:V,makeIssue:U,
EMPTY_PATH:[],addIssueToContext:q,ParseStatus:Z,INVALID:K,DIRTY:z,OK:$,isAborted:H,isDirty:Y,isValid:J,isAsync:W,get util(){return j},get objectUtil(){return C},
ZodParsedType:R,getParsedType:D,ZodType:at,datetimeRegex:Et,ZodString:jt,ZodNumber:Tt,ZodBigInt:At,ZodBoolean:It,ZodDate:Lt,ZodSymbol:Nt,ZodUndefined:Rt,ZodNull:Dt,
ZodAny:Bt,ZodUnknown:Ft,ZodNever:Mt,ZodVoid:Gt,ZodArray:Vt,ZodObject:qt,ZodUnion:Zt,ZodDiscriminatedUnion:zt,ZodIntersection:Ht,ZodTuple:Yt,ZodRecord:Jt,ZodMap:Wt,
ZodSet:Qt,ZodFunction:Xt,ZodLazy:te,ZodLiteral:ee,ZodEnum:ne,ZodNativeEnum:oe,ZodPromise:ie,ZodEffects:ae,ZodTransformer:ae,ZodOptional:se,ZodNullable:ue,
ZodDefault:ce,ZodCatch:le,ZodNaN:fe,BRAND:he,ZodBranded:pe,ZodPipeline:de,ZodReadonly:ye,custom:ge,Schema:at,ZodSchema:at,late:me,get ZodFirstPartyTypeKind(){
return be},coerce:tr,any:Ce,array:Le,bigint:Pe,boolean:Se,date:Ee,discriminatedUnion:Be,effect:Ye,enum:ze,function:qe,instanceof:(t,e={
message:`Input not instance of ${t.name}`})=>ge((e=>e instanceof t),e),intersection:Fe,lazy:Ze,literal:Ke,map:Ve,nan:xe,nativeEnum:$e,never:Ae,null:je,nullable:We,
number:_e,object:Ne,oboolean:()=>Se().optional(),onumber:()=>_e().optional(),optional:Je,ostring:()=>we().optional(),pipeline:Xe,preprocess:Qe,promise:He,record:Ge,
set:Ue,strictObject:Re,string:we,symbol:Oe,transformer:Ye,tuple:Me,undefined:ke,union:De,unknown:Te,void:Ie,NEVER:er,ZodIssueCode:B,
quotelessJson:t=>JSON.stringify(t,null,2).replace(/"([^"]+)":/g,"$1:"),ZodError:F});function nr(t){
return nr="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},nr(t)}function or(t,e){var r=Object.keys(t)
;if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(t);e&&(n=n.filter((function(e){return Object.getOwnPropertyDescriptor(t,e).enumerable}))),
r.push.apply(r,n)}return r}function ir(){ir=function(){return e};var t,e={},r=Object.prototype,n=r.hasOwnProperty,o=Object.defineProperty||function(t,e,r){
t[e]=r.value},i="function"==typeof Symbol?Symbol:{},a=i.iterator||"@@iterator",s=i.asyncIterator||"@@asyncIterator",u=i.toStringTag||"@@toStringTag"
;function c(t,e,r){return Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}),t[e]}try{c({},"")}catch(t){c=function(t,e,r){return t[e]=r}}
function l(t,e,r,n){var i=e&&e.prototype instanceof g?e:g,a=Object.create(i.prototype),s=new T(n||[]);return o(a,"_invoke",{value:O(t,r,s)}),a}function f(t,e,r){try{
return{type:"normal",arg:t.call(e,r)}}catch(t){return{type:"throw",arg:t}}}e.wrap=l;var h="suspendedStart",p="suspendedYield",d="executing",y="completed",v={}
;function g(){}function m(){}function b(){}var w={};c(w,a,(function(){return this}));var _=Object.getPrototypeOf,x=_&&_(_(A([])));x&&x!==r&&n.call(x,a)&&(w=x)
;var P=b.prototype=g.prototype=Object.create(w);function S(t){["next","throw","return"].forEach((function(e){c(t,e,(function(t){return this._invoke(e,t)}))}))}
function E(t,e){function r(o,i,a,s){var u=f(t[o],t,i);if("throw"!==u.type){var c=u.arg,l=c.value
;return l&&"object"==nr(l)&&n.call(l,"__await")?e.resolve(l.__await).then((function(t){r("next",t,a,s)}),(function(t){r("throw",t,a,s)
})):e.resolve(l).then((function(t){c.value=t,a(c)}),(function(t){return r("throw",t,a,s)}))}s(u.arg)}var i;o(this,"_invoke",{value:function(t,n){function o(){
return new e((function(e,o){r(t,n,e,o)}))}return i=i?i.then(o,o):o()}})}function O(e,r,n){var o=h;return function(i,a){
if(o===d)throw Error("Generator is already running");if(o===y){if("throw"===i)throw a;return{value:t,done:!0}}for(n.method=i,n.arg=a;;){var s=n.delegate;if(s){
var u=k(s,n);if(u){if(u===v)continue;return u}}if("next"===n.method)n.sent=n._sent=n.arg;else if("throw"===n.method){if(o===h)throw o=y,n.arg
;n.dispatchException(n.arg)}else"return"===n.method&&n.abrupt("return",n.arg);o=d;var c=f(e,r,n);if("normal"===c.type){if(o=n.done?y:p,c.arg===v)continue;return{
value:c.arg,done:n.done}}"throw"===c.type&&(o=y,n.method="throw",n.arg=c.arg)}}}function k(e,r){var n=r.method,o=e.iterator[n];if(o===t)return r.delegate=null,
"throw"===n&&e.iterator.return&&(r.method="return",r.arg=t,k(e,r),"throw"===r.method)||"return"!==n&&(r.method="throw",
r.arg=new TypeError("The iterator does not provide a '"+n+"' method")),v;var i=f(o,e.iterator,r.arg);if("throw"===i.type)return r.method="throw",r.arg=i.arg,
r.delegate=null,v;var a=i.arg;return a?a.done?(r[e.resultName]=a.value,r.next=e.nextLoc,"return"!==r.method&&(r.method="next",r.arg=t),r.delegate=null,
v):a:(r.method="throw",r.arg=new TypeError("iterator result is not an object"),r.delegate=null,v)}function j(t){var e={tryLoc:t[0]};1 in t&&(e.catchLoc=t[1]),
2 in t&&(e.finallyLoc=t[2],e.afterLoc=t[3]),this.tryEntries.push(e)}function C(t){var e=t.completion||{};e.type="normal",delete e.arg,t.completion=e}function T(t){
this.tryEntries=[{tryLoc:"root"}],t.forEach(j,this),this.reset(!0)}function A(e){if(e||""===e){var r=e[a];if(r)return r.call(e);if("function"==typeof e.next)return e
;if(!isNaN(e.length)){var o=-1,i=function r(){for(;++o<e.length;)if(n.call(e,o))return r.value=e[o],r.done=!1,r;return r.value=t,r.done=!0,r};return i.next=i}}
throw new TypeError(nr(e)+" is not iterable")}return m.prototype=b,o(P,"constructor",{value:b,configurable:!0}),o(b,"constructor",{value:m,configurable:!0}),
m.displayName=c(b,u,"GeneratorFunction"),e.isGeneratorFunction=function(t){var e="function"==typeof t&&t.constructor
;return!!e&&(e===m||"GeneratorFunction"===(e.displayName||e.name))},e.mark=function(t){return Object.setPrototypeOf?Object.setPrototypeOf(t,b):(t.__proto__=b,
c(t,u,"GeneratorFunction")),t.prototype=Object.create(P),t},e.awrap=function(t){return{__await:t}},S(E.prototype),c(E.prototype,s,(function(){return this})),
e.AsyncIterator=E,e.async=function(t,r,n,o,i){void 0===i&&(i=Promise);var a=new E(l(t,r,n,o),i);return e.isGeneratorFunction(r)?a:a.next().then((function(t){
return t.done?t.value:a.next()}))},S(P),c(P,u,"Generator"),c(P,a,(function(){return this})),c(P,"toString",(function(){return"[object Generator]"})),
e.keys=function(t){var e=Object(t),r=[];for(var n in e)r.push(n);return r.reverse(),function t(){for(;r.length;){var n=r.pop();if(n in e)return t.value=n,t.done=!1,t
}return t.done=!0,t}},e.values=A,T.prototype={constructor:T,reset:function(e){if(this.prev=0,this.next=0,this.sent=this._sent=t,this.done=!1,this.delegate=null,
this.method="next",this.arg=t,this.tryEntries.forEach(C),!e)for(var r in this)"t"===r.charAt(0)&&n.call(this,r)&&!isNaN(+r.slice(1))&&(this[r]=t)},stop:function(){
this.done=!0;var t=this.tryEntries[0].completion;if("throw"===t.type)throw t.arg;return this.rval},dispatchException:function(e){if(this.done)throw e;var r=this
;function o(n,o){return s.type="throw",s.arg=e,r.next=n,o&&(r.method="next",r.arg=t),!!o}for(var i=this.tryEntries.length-1;i>=0;--i){
var a=this.tryEntries[i],s=a.completion;if("root"===a.tryLoc)return o("end");if(a.tryLoc<=this.prev){var u=n.call(a,"catchLoc"),c=n.call(a,"finallyLoc");if(u&&c){
if(this.prev<a.catchLoc)return o(a.catchLoc,!0);if(this.prev<a.finallyLoc)return o(a.finallyLoc)}else if(u){if(this.prev<a.catchLoc)return o(a.catchLoc,!0)}else{
if(!c)throw Error("try statement without catch or finally");if(this.prev<a.finallyLoc)return o(a.finallyLoc)}}}},abrupt:function(t,e){
for(var r=this.tryEntries.length-1;r>=0;--r){var o=this.tryEntries[r];if(o.tryLoc<=this.prev&&n.call(o,"finallyLoc")&&this.prev<o.finallyLoc){var i=o;break}}
i&&("break"===t||"continue"===t)&&i.tryLoc<=e&&e<=i.finallyLoc&&(i=null);var a=i?i.completion:{};return a.type=t,a.arg=e,i?(this.method="next",
this.next=i.finallyLoc,v):this.complete(a)},complete:function(t,e){if("throw"===t.type)throw t.arg
;return"break"===t.type||"continue"===t.type?this.next=t.arg:"return"===t.type?(this.rval=this.arg=t.arg,this.method="return",
this.next="end"):"normal"===t.type&&e&&(this.next=e),v},finish:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.finallyLoc===t)return this.complete(r.completion,r.afterLoc),C(r),v}},catch:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.tryLoc===t){var n=r.completion;if("throw"===n.type){var o=n.arg;C(r)}return o}}throw Error("illegal catch attempt")},delegateYield:function(e,r,n){
return this.delegate={iterator:A(e),resultName:r,nextLoc:n},"next"===this.method&&(this.arg=t),v}},e}function ar(t,e,r,n,o,i,a){try{var s=t[i](a),u=s.value}catch(t){
return void r(t)}s.done?e(u):Promise.resolve(u).then(n,o)}function sr(t){return function(){var e=this,r=arguments;return new Promise((function(n,o){
var i=t.apply(e,r);function a(t){ar(i,n,o,a,s,"next",t)}function s(t){ar(i,n,o,a,s,"throw",t)}a(void 0)}))}}function ur(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,vr(n.key),n)}}function cr(t,e,r){return e=dr(e),function(t,e){
if(e&&("object"==nr(e)||"function"==typeof e))return e;if(void 0!==e)throw new TypeError("Derived constructors may only return object or undefined")
;return function(t){if(void 0===t)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return t}(t)
}(t,hr()?Reflect.construct(e,r||[],dr(t).constructor):e.apply(t,r))}function lr(){
return lr="undefined"!=typeof Reflect&&Reflect.get?Reflect.get.bind():function(t,e,r){var n=function(t,e){for(;!{}.hasOwnProperty.call(t,e)&&null!==(t=dr(t)););
return t}(t,e);if(n){var o=Object.getOwnPropertyDescriptor(n,e);return o.get?o.get.call(arguments.length<3?t:r):o.value}},lr.apply(null,arguments)}function fr(t){
var e="function"==typeof Map?new Map:void 0;return fr=function(t){if(null===t||!function(t){try{return-1!==Function.toString.call(t).indexOf("[native code]")
}catch(e){return"function"==typeof t}}(t))return t;if("function"!=typeof t)throw new TypeError("Super expression must either be null or a function");if(void 0!==e){
if(e.has(t))return e.get(t);e.set(t,r)}function r(){return function(t,e,r){if(hr())return Reflect.construct.apply(null,arguments);var n=[null];n.push.apply(n,e)
;var o=new(t.bind.apply(t,n));return r&&pr(o,r.prototype),o}(t,arguments,dr(this).constructor)}return r.prototype=Object.create(t.prototype,{constructor:{value:r,
enumerable:!1,writable:!0,configurable:!0}}),pr(r,t)},fr(t)}function hr(){try{var t=!Boolean.prototype.valueOf.call(Reflect.construct(Boolean,[],(function(){})))
}catch(t){}return(hr=function(){return!!t})()}function pr(t,e){return pr=Object.setPrototypeOf?Object.setPrototypeOf.bind():function(t,e){return t.__proto__=e,t},
pr(t,e)}function dr(t){return dr=Object.setPrototypeOf?Object.getPrototypeOf.bind():function(t){return t.__proto__||Object.getPrototypeOf(t)},dr(t)}
function yr(t,e,r){return(e=vr(e))in t?Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}):t[e]=r,t}function vr(t){var e=function(t,e){
if("object"!=nr(t)||!t)return t;var r=t[Symbol.toPrimitive];if(void 0!==r){var n=r.call(t,e||"default");if("object"!=nr(n))return n
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==nr(e)?e:e+""}
var gr=function(t){function e(t,r){var n,o;if(function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,e),
yr(o=cr(this,e,[t]),"functionName",void 0),yr(o,"page",void 0),yr(o,"error",void 0),yr(o,"childPage",void 0),yr(o,"pageId",void 0),yr(o,"spaceId",void 0),
yr(o,"spaceKey",void 0),yr(o,"title",void 0),yr(o,"empty",!1),yr(o,"invalid",!1),yr(o,"null",!1),yr(o,"shouldReturn",!1),yr(o,"targetContentId",void 0),
yr(o,"contentId",void 0),yr(o,"attachmentId",void 0),yr(o,"contentProperty",void 0),yr(o,"confluenceApiVersion",void 0),yr(o,"context",void 0),
yr(o,"propertyKey",void 0),yr(o,"customContent",void 0),yr(o,"statusCode",void 0),yr(o,"retryableStatusCodes",void 0),yr(o,"insufficientPermissions",!1),o.error=r,
o.name="ConfluenceAccessorError",r instanceof F){o.name="ConfluenceAccessorValidateError";var i=r.flatten((function(t){
return r.formErrors.formErrors.length>0&&"null"===t.received?"".concat(t.message,"_NULL"):t.message}));i.formErrors.includes("EMPTY_VALUE")&&(o.empty=!0),
i.formErrors.includes("INVALID_TYPE")&&(o.invalid=!0),i.formErrors.includes("INVALID_TYPE_NULL")&&(o.null=!0)}
return o.statusCode=null===(n=o.error)||void 0===n?void 0:n.status,o.retryableStatusCodes=[500,504],r&&404===r.status&&(o.empty=!0),
r&&403===r.status&&(o.insufficientPermissions=!0),o}return function(t,e){
if("function"!=typeof e&&null!==e)throw new TypeError("Super expression must either be null or a function");t.prototype=Object.create(e&&e.prototype,{constructor:{
value:t,writable:!0,configurable:!0}}),Object.defineProperty(t,"prototype",{writable:!1}),e&&pr(t,e)}(e,t),r=e,n=[{key:"sleep",value:(a=sr(ir().mark((function t(e){
return ir().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.abrupt("return",new Promise((function(t){return setTimeout(t,e)})));case 1:case"end":
return t.stop()}}),t)}))),function(t){return a.apply(this,arguments)})},{key:"withHandleError",value:(i=sr(ir().mark((function t(e,r,n){
return ir().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:if(!(this.shouldRetry()&&r>0)){t.next=7;break}
return n.warn("Retriable error found. Retrying... Attempts remaining: ".concat(r)),t.next=4,this.sleep(2e3);case 4:return t.abrupt("return",e());case 7:throw this
;case 8:case"end":return t.stop()}}),t,this)}))),function(t,e,r){return i.apply(this,arguments)})},{key:"shouldRetry",value:function(){var t
;return this.retryableStatusCodes.includes(null!==(t=this.statusCode)&&void 0!==t?t:0)}},{key:"setIsAPIv1",value:function(){return this.confluenceApiVersion=1,this}
},{key:"setIsAPIv2",value:function(){return this.confluenceApiVersion=2,this}},{key:"setIsInvalid",value:function(){return this.invalid=!0,this}},{key:"setIsEmpty",
value:function(){return this.empty=!0,this}},{key:"setIsNull",value:function(){return this.null=!0,this}},{key:"setShouldReturn",value:function(){
return this.shouldReturn=!0,this}},{key:"isEmpty",value:function(){return this.empty}},{key:"isInvalid",value:function(){return this.invalid}},{key:"isNull",
value:function(){return this.null}},{key:"isShouldReturn",value:function(){return this.shouldReturn}},{key:"message",get:function(){var t,r,n,o,i,a=(t=e,r="message",
n=this,i=lr(dr(1&(o=1)?t.prototype:t),r,n),2&o&&"function"==typeof i?function(t){return i.apply(n,t)}:i)
;return this.functionName&&(a+="\nFunction Name: ".concat(this.functionName)),this.page&&(a+="\nPage: ".concat(JSON.stringify(this.page))),
this.childPage&&(a+="\nChild Page: ".concat(JSON.stringify(this.childPage))),this.pageId&&(a+="\nPage ID: ".concat(this.pageId)),
this.spaceId&&(a+="\nSpace ID: ".concat(this.spaceId)),this.spaceKey&&(a+="\nSpace Key: ".concat(this.spaceKey)),this.title&&(a+="\nTitle: ".concat(this.title)),
this.error&&(a+="\nOriginal Error: ".concat(this.error.message)),this.contentId&&(a+="\nContent ID: ".concat(this.contentId)),
this.targetContentId&&(a+="\nTarget Content ID: ".concat(this.targetContentId)),this.attachmentId&&(a+="\nAttachment ID: ".concat(this.attachmentId)),
this.contentProperty&&(a+="\nContent Property: ".concat(JSON.stringify(this.contentProperty))),
this.confluenceApiVersion&&(a+="\nConfluence API Version: ".concat(this.confluenceApiVersion)),this.context&&(a+="\nContext: ".concat(JSON.stringify(this.context))),
this.propertyKey&&(a+="\nProperty Key: ".concat(this.propertyKey)),this.customContent&&(a+="\nCustom Content: ".concat(JSON.stringify(this.customContent))),a}},{
key:"withContext",value:function(t){return this.context=function(t){for(var e=1;e<arguments.length;e++){var r=null!=arguments[e]?arguments[e]:{}
;e%2?or(Object(r),!0).forEach((function(e){yr(t,e,r[e])
})):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(r)):or(Object(r)).forEach((function(e){
Object.defineProperty(t,e,Object.getOwnPropertyDescriptor(r,e))}))}return t}({},t),this}},{key:"withSpaceId",value:function(t){return this.spaceId=t,this}},{
key:"withSpaceKey",value:function(t){return this.spaceKey=t,this}},{key:"withTitle",value:function(t){return this.title=t,this}},{key:"withError",value:function(t){
return this.error=t,this}},{key:"withPropertyKey",value:function(t){return this.propertyKey=t,this}},{key:"withFunctionName",value:function(t){
return this.functionName=t,this}},{key:"withPage",value:function(t){return this.page=t,this}},{key:"withChildPage",value:function(t){return this.childPage=t,this}},{
key:"withPageId",value:function(t){return this.pageId=t,this}},{key:"withContentId",value:function(t){return this.contentId=t,this}},{key:"withTargetContentId",
value:function(t){return this.targetContentId=t,this}},{key:"withAttachmentId",value:function(t){return this.attachmentId=t,this}},{key:"withContentProperty",
value:function(t){return this.contentProperty=t,this}},{key:"withCustomContent",value:function(t){return this.customContent=t,this}},{key:"withRetryableStatusCodes",
value:function(t){return this.retryableStatusCodes=t,this}}],n&&ur(r.prototype,n),o&&ur(r,o),Object.defineProperty(r,"prototype",{writable:!1}),r;var r,n,o,i,a
}(fr(Error));function mr(t){return mr="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},mr(t)}function br(t,e){
if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}function wr(t,e){for(var r=0;r<e.length;r++){var n=e[r];n.enumerable=n.enumerable||!1,
n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,Pr(n.key),n)}}function _r(t,e,r){return e&&wr(t.prototype,e),r&&wr(t,r),
Object.defineProperty(t,"prototype",{writable:!1}),t}function xr(t,e,r){return(e=Pr(e))in t?Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,
writable:!0}):t[e]=r,t}function Pr(t){var e=function(t,e){if("object"!=mr(t)||!t)return t;var r=t[Symbol.toPrimitive];if(void 0!==r){var n=r.call(t,e||"default")
;if("object"!=mr(n))return n;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string")
;return"symbol"==mr(e)?e:e+""}var Sr=function(){function t(){br(this,t)}return _r(t,null,[{key:"validate",value:function(e){var r=t.schema.safeParse(e)
;if(r.success)return r.data;throw r.error}}])}();xr(Sr,"schema",rr.object({createdAt:rr.string(),message:rr.string(),number:rr.number(),
minorEdit:rr.boolean().optional(),authorId:rr.string().optional()}));var Er=function(){function t(){br(this,t)}return _r(t,null,[{key:"validate",value:function(e){
var r=t.schema.safeParse(e);if(r.success)return r.data;throw r.error}}])}();xr(Er,"schema",rr.object({id:rr.string(),type:rr.string(),status:rr.string(),
title:rr.string(),version:rr.lazy((function(){return rr.object({number:rr.number()})})),space:rr.lazy((function(){return rr.object({id:rr.number(),key:rr.string(),
name:rr.string(),type:rr.string(),status:rr.string()})}))},{invalid_type_error:"INVALID_TYPE",required_error:"EMPTY_VALUE"}));var Or=function(){function t(){
br(this,t)}return _r(t,null,[{key:"validate",value:function(e){var r=t.schema.safeParse(e);if(r.success)return r.data;throw r.error}}])}()
;xr(Or,"schema",rr.lazy((function(){return rr.object({id:rr.string(),status:rr.string(),title:rr.string(),spaceId:rr.string(),
parentId:rr.string().nullable().optional(),parentType:rr.string().nullable().optional(),position:rr.number().nullable().optional(),authorId:rr.string(),
createdAt:rr.string(),version:Sr.schema,body:rr.object({storage:rr.object({representation:rr.string(),value:rr.string().optional()}).optional()}).optional(),
_links:rr.object({webui:rr.string(),editui:rr.string(),tinyui:rr.string()})},{invalid_type_error:"INVALID_TYPE",required_error:"EMPTY_VALUE"})})));var kr=function(){
function t(){br(this,t)}return _r(t,null,[{key:"validate",value:function(e){var r=t.schema.safeParse(e);if(r.success)return r.data;throw r.error}}])}()
;xr(kr,"schema",rr.lazy((function(){return rr.object({id:rr.string(),status:rr.string(),title:rr.string(),spaceId:rr.string(),childPosition:rr.number()})})))
;var jr=function(){function t(){br(this,t)}return _r(t,null,[{key:"validate",value:function(e){var r=t.schema.safeParse(e);if(r.success)return r.data;throw r.error}
}])}();xr(jr,"schema",rr.lazy((function(){return rr.object({id:rr.string(),type:rr.string(),status:rr.string(),title:rr.string().optional(),spaceId:rr.string(),
pageId:rr.string().optional(),blogPostId:rr.string().optional(),customContentId:rr.string().nullable().optional(),authorId:rr.string(),createdAt:rr.string(),
body:rr.object({raw:rr.object({representation:rr.string(),value:rr.string().optional()}).optional(),storage:rr.object({representation:rr.string(),
value:rr.string().optional()}).optional()}),version:Sr.schema})})));var Cr=function(){function t(){br(this,t)}return _r(t,null,[{key:"validate",value:function(e){
var r=t.schema.safeParse(e);if(r.success)return r.data;throw r.error}}])}();xr(Cr,"schema",rr.object({id:rr.string(),status:rr.string(),title:rr.string()}))
;var Tr=function(){function t(){br(this,t)}return _r(t,null,[{key:"validate",value:function(e){var r=t.permittedOperationsSchema.safeParse(e)
;if(r.success)return r.data;throw r.error}}])}();xr(Tr,"permittedOperationsSchema",rr.object({operations:rr.array(rr.object({operation:rr.string(),
targetType:rr.string()}))}));var Ar=function(){function t(){br(this,t)}return _r(t,null,[{key:"validate",value:function(e){var r=t.schema.safeParse(e)
;if(r.success)return r.data;throw r.error}}])}();xr(Ar,"schema",rr.object({id:rr.string(),key:rr.string(),name:rr.string(),type:rr.string(),status:rr.string(),
authorId:rr.string(),createdAt:rr.string(),homepageId:rr.string().nullable(),description:rr.object({plain:rr.string().optional(),view:rr.string().optional()
}).nullish(),icon:rr.object({path:rr.string(),apiDownloadLink:rr.string().optional()}).nullish(),_links:rr.object({webui:rr.string()}).nullable()},{
invalid_type_error:"INVALID_TYPE",required_error:"EMPTY_VALUE"}));var Ir=function(){function t(){br(this,t)}return _r(t,null,[{key:"validate",value:function(e){
var r=t.schema.safeParse(e);if(r.success)return r.data;throw r.error}}])}();xr(Ir,"schema",rr.lazy((function(){return rr.object({id:rr.string(),key:rr.string(),
value:rr.union([rr.string(),rr.number(),rr.boolean(),rr.record(rr.string(),rr.any()),rr.array(rr.string()),rr.array(rr.number()),rr.array(rr.record(rr.string(),rr.any()))]),
version:Sr.schema},{invalid_type_error:"INVALID_TYPE",required_error:"EMPTY_VALUE"})})));var Lr=function(){function t(){br(this,t)}return _r(t,null,[{key:"validate",
value:function(e){var r=t.schema.safeParse(e);if(r.success)return r.data;throw r.error}}])}();xr(Lr,"schema",rr.lazy((function(){return rr.object({
results:rr.array(rr.any()),start:rr.number(),limit:rr.number(),size:rr.number(),_links:rr.object({base:rr.string(),context:rr.string(),prev:rr.string().optional(),
next:rr.string().optional(),self:rr.string()})},{invalid_type_error:"INVALID_TYPE",required_error:"EMPTY_VALUE"})})));var Nr=function(){function t(){br(this,t)}
return _r(t,null,[{key:"validate",value:function(e){var r=t.schema.safeParse(e);if(r.success)return r.data;throw r.error}}])}();xr(Nr,"schema",rr.lazy((function(){
return rr.object({results:rr.array(rr.any()),start:rr.number(),limit:rr.number(),size:rr.number(),cqlQuery:rr.string(),totalSize:rr.number(),
searchDuration:rr.number(),_expandable:rr.record(rr.string(),rr.string()).nullable().optional(),_links:rr.object({base:rr.string(),context:rr.string(),
prev:rr.string().optional(),next:rr.string().optional(),self:rr.string()})},{invalid_type_error:"INVALID_TYPE",required_error:"EMPTY_VALUE"})})));var Rr=function(){
function t(){br(this,t)}return _r(t,null,[{key:"validate",value:function(e){var r=t.schema.safeParse(e);if(r.success)return r.data;throw r.error}}])}()
;xr(Rr,"schema",rr.lazy((function(){return rr.object({type:rr.string(),accountId:rr.string(),displayName:rr.string(),publicName:rr.string(),
email:rr.string().optional(),profilePicture:rr.object({path:rr.string(),width:rr.number(),height:rr.number(),isDefault:rr.boolean()}),
isExternalCollaborator:rr.boolean(),operations:rr.array(rr.object({operation:rr.string(),targetType:rr.string()})).optional(),personalSpace:Ar.schema.optional(),
_expandable:rr.record(rr.string(),rr.string()),_links:rr.object({self:rr.string()})},{invalid_type_error:"INVALID_TYPE",required_error:"EMPTY_VALUE"})})))
;var Dr=function(){return _r((function t(){br(this,t)}),null,[{key:"createSchema",value:function(t){return rr.lazy((function(){return rr.object({results:rr.array(t)
},{invalid_type_error:"INVALID_TYPE",required_error:"EMPTY_VALUE"})}))}},{key:"validate",value:function(t,e){var r=this.createSchema(e).safeParse(t)
;if(r.success)return r.data;throw r.error}}])}(),Br=function(){function t(){br(this,t)}return _r(t,null,[{key:"validate",value:function(e){
var r=t.schema.safeParse(e);if(r.success)return r.data;throw r.error}}])}();xr(Br,"schema",rr.lazy((function(){return rr.object({id:rr.string(),principal:rr.object({
id:rr.string(),type:rr.string()}),operation:rr.object({key:rr.string(),targetType:rr.string()})},{invalid_type_error:"INVALID_TYPE",required_error:"EMPTY_VALUE"})
})));var Fr=function(){function t(){br(this,t)}return _r(t,null,[{key:"validate",value:function(e){var r=t.schema.safeParse(e);if(r.success)return r.data
;throw r.error}}])}();xr(Fr,"schema",rr.object({createdAt:rr.string(),createdBy:rr.string().nullable().optional(),message:rr.string(),number:rr.number()},{
invalid_type_error:"INVALID_TYPE",required_error:"EMPTY_VALUE"}).nullable().optional());var Mr=function(){function t(){br(this,t)}return _r(t,null,[{key:"validate",
value:function(e){var r=t.schema.safeParse(e);if(r.success)return r.data;throw r.error}}])}();xr(Mr,"schema",rr.lazy((function(){return rr.object({id:rr.string(),
key:rr.string(),
value:rr.union([rr.string(),rr.number(),rr.boolean(),rr.record(rr.string(),rr.any()),rr.array(rr.string()),rr.array(rr.number()),rr.array(rr.record(rr.string(),rr.any()))]),
createdAt:rr.string(),createdBy:rr.string().nullable().optional(),version:Fr.schema},{invalid_type_error:"INVALID_TYPE",required_error:"EMPTY_VALUE"})})))
;var Gr=function(){function t(){br(this,t)}return _r(t,null,[{key:"validate",value:function(e){var r=t.schema.safeParse(e);if(r.success)return r.data;throw r.error}
}])}();xr(Gr,"schema",rr.lazy((function(){return rr.object({
value:rr.union([rr.string(),rr.number(),rr.boolean(),rr.record(rr.string(),rr.any()),rr.array(rr.string()),rr.array(rr.number()),rr.array(rr.record(rr.string(),rr.any()))])
})})));var Vr=function(){function t(){br(this,t)}return _r(t,null,[{key:"validate",value:function(e){var r=t.schema.safeParse(e);if(r.success)return r.data
;throw r.error}}])}();function Ur(t){return Ur="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},Ur(t)}function qr(t,e){var r=Object.keys(t)
;if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(t);e&&(n=n.filter((function(e){return Object.getOwnPropertyDescriptor(t,e).enumerable}))),
r.push.apply(r,n)}return r}function Zr(t){for(var e=1;e<arguments.length;e++){var r=null!=arguments[e]?arguments[e]:{};e%2?qr(Object(r),!0).forEach((function(e){
Kr(t,e,r[e])})):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(r)):qr(Object(r)).forEach((function(e){
Object.defineProperty(t,e,Object.getOwnPropertyDescriptor(r,e))}))}return t}function Kr(t,e,r){return(e=Qr(e))in t?Object.defineProperty(t,e,{value:r,enumerable:!0,
configurable:!0,writable:!0}):t[e]=r,t}function zr(t){return function(t){if(Array.isArray(t))return $r(t)}(t)||function(t){
if("undefined"!=typeof Symbol&&null!=t[Symbol.iterator]||null!=t["@@iterator"])return Array.from(t)}(t)||function(t,e){if(t){if("string"==typeof t)return $r(t,e)
;var r={}.toString.call(t).slice(8,-1);return"Object"===r&&t.constructor&&(r=t.constructor.name),
"Map"===r||"Set"===r?Array.from(t):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?$r(t,e):void 0}}(t)||function(){
throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()}
function $r(t,e){(null==e||e>t.length)&&(e=t.length);for(var r=0,n=Array(e);r<e;r++)n[r]=t[r];return n}function Hr(){Hr=function(){return e}
;var t,e={},r=Object.prototype,n=r.hasOwnProperty,o=Object.defineProperty||function(t,e,r){t[e]=r.value
},i="function"==typeof Symbol?Symbol:{},a=i.iterator||"@@iterator",s=i.asyncIterator||"@@asyncIterator",u=i.toStringTag||"@@toStringTag";function c(t,e,r){
return Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}),t[e]}try{c({},"")}catch(t){c=function(t,e,r){return t[e]=r}}
function l(t,e,r,n){var i=e&&e.prototype instanceof g?e:g,a=Object.create(i.prototype),s=new T(n||[]);return o(a,"_invoke",{value:O(t,r,s)}),a}function f(t,e,r){try{
return{type:"normal",arg:t.call(e,r)}}catch(t){return{type:"throw",arg:t}}}e.wrap=l;var h="suspendedStart",p="suspendedYield",d="executing",y="completed",v={}
;function g(){}function m(){}function b(){}var w={};c(w,a,(function(){return this}));var _=Object.getPrototypeOf,x=_&&_(_(A([])));x&&x!==r&&n.call(x,a)&&(w=x)
;var P=b.prototype=g.prototype=Object.create(w);function S(t){["next","throw","return"].forEach((function(e){c(t,e,(function(t){return this._invoke(e,t)}))}))}
function E(t,e){function r(o,i,a,s){var u=f(t[o],t,i);if("throw"!==u.type){var c=u.arg,l=c.value
;return l&&"object"==Ur(l)&&n.call(l,"__await")?e.resolve(l.__await).then((function(t){r("next",t,a,s)}),(function(t){r("throw",t,a,s)
})):e.resolve(l).then((function(t){c.value=t,a(c)}),(function(t){return r("throw",t,a,s)}))}s(u.arg)}var i;o(this,"_invoke",{value:function(t,n){function o(){
return new e((function(e,o){r(t,n,e,o)}))}return i=i?i.then(o,o):o()}})}function O(e,r,n){var o=h;return function(i,a){
if(o===d)throw Error("Generator is already running");if(o===y){if("throw"===i)throw a;return{value:t,done:!0}}for(n.method=i,n.arg=a;;){var s=n.delegate;if(s){
var u=k(s,n);if(u){if(u===v)continue;return u}}if("next"===n.method)n.sent=n._sent=n.arg;else if("throw"===n.method){if(o===h)throw o=y,n.arg
;n.dispatchException(n.arg)}else"return"===n.method&&n.abrupt("return",n.arg);o=d;var c=f(e,r,n);if("normal"===c.type){if(o=n.done?y:p,c.arg===v)continue;return{
value:c.arg,done:n.done}}"throw"===c.type&&(o=y,n.method="throw",n.arg=c.arg)}}}function k(e,r){var n=r.method,o=e.iterator[n];if(o===t)return r.delegate=null,
"throw"===n&&e.iterator.return&&(r.method="return",r.arg=t,k(e,r),"throw"===r.method)||"return"!==n&&(r.method="throw",
r.arg=new TypeError("The iterator does not provide a '"+n+"' method")),v;var i=f(o,e.iterator,r.arg);if("throw"===i.type)return r.method="throw",r.arg=i.arg,
r.delegate=null,v;var a=i.arg;return a?a.done?(r[e.resultName]=a.value,r.next=e.nextLoc,"return"!==r.method&&(r.method="next",r.arg=t),r.delegate=null,
v):a:(r.method="throw",r.arg=new TypeError("iterator result is not an object"),r.delegate=null,v)}function j(t){var e={tryLoc:t[0]};1 in t&&(e.catchLoc=t[1]),
2 in t&&(e.finallyLoc=t[2],e.afterLoc=t[3]),this.tryEntries.push(e)}function C(t){var e=t.completion||{};e.type="normal",delete e.arg,t.completion=e}function T(t){
this.tryEntries=[{tryLoc:"root"}],t.forEach(j,this),this.reset(!0)}function A(e){if(e||""===e){var r=e[a];if(r)return r.call(e);if("function"==typeof e.next)return e
;if(!isNaN(e.length)){var o=-1,i=function r(){for(;++o<e.length;)if(n.call(e,o))return r.value=e[o],r.done=!1,r;return r.value=t,r.done=!0,r};return i.next=i}}
throw new TypeError(Ur(e)+" is not iterable")}return m.prototype=b,o(P,"constructor",{value:b,configurable:!0}),o(b,"constructor",{value:m,configurable:!0}),
m.displayName=c(b,u,"GeneratorFunction"),e.isGeneratorFunction=function(t){var e="function"==typeof t&&t.constructor
;return!!e&&(e===m||"GeneratorFunction"===(e.displayName||e.name))},e.mark=function(t){return Object.setPrototypeOf?Object.setPrototypeOf(t,b):(t.__proto__=b,
c(t,u,"GeneratorFunction")),t.prototype=Object.create(P),t},e.awrap=function(t){return{__await:t}},S(E.prototype),c(E.prototype,s,(function(){return this})),
e.AsyncIterator=E,e.async=function(t,r,n,o,i){void 0===i&&(i=Promise);var a=new E(l(t,r,n,o),i);return e.isGeneratorFunction(r)?a:a.next().then((function(t){
return t.done?t.value:a.next()}))},S(P),c(P,u,"Generator"),c(P,a,(function(){return this})),c(P,"toString",(function(){return"[object Generator]"})),
e.keys=function(t){var e=Object(t),r=[];for(var n in e)r.push(n);return r.reverse(),function t(){for(;r.length;){var n=r.pop();if(n in e)return t.value=n,t.done=!1,t
}return t.done=!0,t}},e.values=A,T.prototype={constructor:T,reset:function(e){if(this.prev=0,this.next=0,this.sent=this._sent=t,this.done=!1,this.delegate=null,
this.method="next",this.arg=t,this.tryEntries.forEach(C),!e)for(var r in this)"t"===r.charAt(0)&&n.call(this,r)&&!isNaN(+r.slice(1))&&(this[r]=t)},stop:function(){
this.done=!0;var t=this.tryEntries[0].completion;if("throw"===t.type)throw t.arg;return this.rval},dispatchException:function(e){if(this.done)throw e;var r=this
;function o(n,o){return s.type="throw",s.arg=e,r.next=n,o&&(r.method="next",r.arg=t),!!o}for(var i=this.tryEntries.length-1;i>=0;--i){
var a=this.tryEntries[i],s=a.completion;if("root"===a.tryLoc)return o("end");if(a.tryLoc<=this.prev){var u=n.call(a,"catchLoc"),c=n.call(a,"finallyLoc");if(u&&c){
if(this.prev<a.catchLoc)return o(a.catchLoc,!0);if(this.prev<a.finallyLoc)return o(a.finallyLoc)}else if(u){if(this.prev<a.catchLoc)return o(a.catchLoc,!0)}else{
if(!c)throw Error("try statement without catch or finally");if(this.prev<a.finallyLoc)return o(a.finallyLoc)}}}},abrupt:function(t,e){
for(var r=this.tryEntries.length-1;r>=0;--r){var o=this.tryEntries[r];if(o.tryLoc<=this.prev&&n.call(o,"finallyLoc")&&this.prev<o.finallyLoc){var i=o;break}}
i&&("break"===t||"continue"===t)&&i.tryLoc<=e&&e<=i.finallyLoc&&(i=null);var a=i?i.completion:{};return a.type=t,a.arg=e,i?(this.method="next",
this.next=i.finallyLoc,v):this.complete(a)},complete:function(t,e){if("throw"===t.type)throw t.arg
;return"break"===t.type||"continue"===t.type?this.next=t.arg:"return"===t.type?(this.rval=this.arg=t.arg,this.method="return",
this.next="end"):"normal"===t.type&&e&&(this.next=e),v},finish:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.finallyLoc===t)return this.complete(r.completion,r.afterLoc),C(r),v}},catch:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.tryLoc===t){var n=r.completion;if("throw"===n.type){var o=n.arg;C(r)}return o}}throw Error("illegal catch attempt")},delegateYield:function(e,r,n){
return this.delegate={iterator:A(e),resultName:r,nextLoc:n},"next"===this.method&&(this.arg=t),v}},e}function Yr(t,e,r,n,o,i,a){try{var s=t[i](a),u=s.value}catch(t){
return void r(t)}s.done?e(u):Promise.resolve(u).then(n,o)}function Jr(t){return function(){var e=this,r=arguments;return new Promise((function(n,o){
var i=t.apply(e,r);function a(t){Yr(i,n,o,a,s,"next",t)}function s(t){Yr(i,n,o,a,s,"throw",t)}a(void 0)}))}}function Wr(t,e){for(var r=0;r<e.length;r++){var n=e[r]
;n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,Qr(n.key),n)}}function Qr(t){var e=function(t,e){
if("object"!=Ur(t)||!t)return t;var r=t[Symbol.toPrimitive];if(void 0!==r){var n=r.call(t,e||"default");if("object"!=Ur(n))return n
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==Ur(e)?e:e+""}
xr(Vr,"schema",rr.lazy((function(){return rr.array(rr.object({id:rr.string(),name:rr.string(),prefix:rr.string()}))})));var Xr=function(){return t=function t(e){
var r=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},n=arguments.length>2&&void 0!==arguments[2]?arguments[2]:{info:console.info,error:console.error,
warn:console.warn,debug:console.debug};!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.client=e,
this.context=r,this.logger=n},e=[{key:"getUserAccountId",value:function(){return this.context.userAccountId}},{key:"getChildPages",
value:(Y=Jr(Hr().mark((function t(e,r){var n,o,i;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,
this.logger.debug("Get child pages with APIV2",{pageId:e,params:r}),t.next=4,new A.ExtendedConfluence(this.client).confluenceApi.children.getChildPages(e,r);case 4:
return n=t.sent,o=Dr.validate(n,kr.schema),i=o.results,t.abrupt("return",i);case 9:if(t.prev=9,t.t0=t.catch(0),!(t.t0 instanceof gr)){t.next=13;break}throw t.t0
;case 13:throw new gr("Unexpected error while getting child pages",t.t0).withFunctionName("getChildPages").withPageId(e).withContext({params:r}).setIsAPIv2()
;case 14:case"end":return t.stop()}}),t,this,[[0,9]])}))),function(t,e){return Y.apply(this,arguments)})},{key:"getPageById",value:(H=Jr(Hr().mark((function t(e,r){
var n;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,this.logger.debug("Get page by id with APIV2",{pageId:e,params:r}),t.next=4,
new A.ExtendedConfluence(this.client).confluenceApi.page.getPageById(e,r);case 4:return n=t.sent,t.abrupt("return",Or.validate(n));case 8:throw t.prev=8,
t.t0=t.catch(0),new gr("Unexpected error while getting the page",t.t0).withFunctionName("getPageById").withPageId(e).withContext({params:r}).setIsAPIv2();case 11:
case"end":return t.stop()}}),t,this,[[0,8]])}))),function(t,e){return H.apply(this,arguments)})},{key:"searchContent",value:($=Jr(Hr().mark((function t(e,r){var n
;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,this.logger.debug("Search content with APIV1",{params:e,options:r}),t.next=4,
new T.sK(this.client).searchContent(e,r);case 4:return n=t.sent,t.abrupt("return",Lr.validate(n));case 8:throw t.prev=8,t.t0=t.catch(0),
new gr("Unexpected error on search content",t.t0).withFunctionName("searchContent").withContext({params:e,options:r}).setIsAPIv1();case 11:case"end":return t.stop()}
}),t,this,[[0,8]])}))),function(t,e){return $.apply(this,arguments)})},{key:"getSpacePages",value:(z=Jr(Hr().mark((function t(e){var r,n,o,i,a,s,u=arguments
;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:if(r=u.length>1&&void 0!==u[1]?u[1]:[],n=u.length>2?u[2]:void 0,o=u.length>3?u[3]:void 0,
""!==(i=N("space",e,"AND"))){t.next=6;break}throw new gr("No valid spaceKeys provided").withFunctionName("getSpacePages").withContext({spaceKeys:e,excludePageIds:r,
limit:n,expand:o});case 6:return a=N("id",r,"AND NOT"),s='type="page" '.concat(i," ").concat(a," order by title asc"),t.abrupt("return",this.search({cql:s,limit:n,
expand:o}));case 9:case"end":return t.stop()}}),t,this)}))),function(t){return z.apply(this,arguments)})},{key:"getSpacePagesWithFinalWorkflow",
value:(K=Jr(Hr().mark((function t(e){var r,n,o,i,a,s=arguments;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:
return r=s.length>1&&void 0!==s[1]?s[1]:[],n=s.length>2?s[2]:void 0,o=[].concat(zr(s.length>3&&void 0!==s[3]?s[3]:[]),["content.metadata.properties.".concat(h)]),
t.next=6,this.getNotSyncedPages(e,r,n,o);case 6:return i=t.sent,a=i.results.filter((function(t){var e,r
;return(null===(e=t.content)||void 0===e||null===(e=e.metadata)||void 0===e||null===(e=e.properties)||void 0===e||null===(e=e[h])||void 0===e||null===(e=e.value)||void 0===e?void 0:e.enabled)&&(null===(r=t.content)||void 0===r||null===(r=r.metadata)||void 0===r||null===(r=r.properties)||void 0===r||null===(r=r[h])||void 0===r||null===(r=r.value)||void 0===r||null===(r=r.state)||void 0===r?void 0:r.final)
})),t.abrupt("return",Zr(Zr({},i),{},{results:a,totalSize:a.length}));case 9:case"end":return t.stop()}}),t,this)}))),function(t){return K.apply(this,arguments)})},{
key:"getNotSyncedPages",value:(Z=Jr(Hr().mark((function t(e){var r,n,o,i,a,s,u=arguments;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:
if(r=u.length>1&&void 0!==u[1]?u[1]:[],n=u.length>2?u[2]:void 0,o=u.length>3?u[3]:void 0,""!==(i=N("space",e,"AND"))){t.next=6;break}
throw new gr("No valid spaceKeys provided").withFunctionName("getNotSyncedPages").withContext({spaceKeys:e,excludePageIds:r,limit:n,expand:o});case 6:
return a=N("id",r,"AND NOT"),s=' type="page" '.concat(i," ").concat(a,' AND NOT cpcState = "').concat(p.SYNCED,'" ORDER BY title ASC'),
t.abrupt("return",this.search({cql:s,limit:n,expand:o}));case 9:case"end":return t.stop()}}),t,this)}))),function(t){return Z.apply(this,arguments)})},{
key:"getNotSyncedPagesWithFinalWorkflow",value:(q=Jr(Hr().mark((function t(e){var r,n,o,i,a,s,u,c,l=arguments;return Hr().wrap((function(t){
for(;;)switch(t.prev=t.next){case 0:return r=l.length>1&&void 0!==l[1]?l[1]:[],n=l.length>2?l[2]:void 0,
o=[].concat(zr(l.length>3&&void 0!==l[3]?l[3]:[]),["content.metadata.properties.".concat(h)]),t.next=6,this.getNotSyncedPages(e,r,n,o);case 6:i=t.sent,a=i.results,
s=i._links.next;case 9:if(!s){t.next=17;break}return t.next=12,this.client({url:s});case 12:u=t.sent,a=a.concat(u.results),s=u._links.next,t.next=9;break;case 17:
return c=a.filter((function(t){var e,r
;return(null===(e=t.content)||void 0===e||null===(e=e.metadata)||void 0===e||null===(e=e.properties)||void 0===e||null===(e=e[h])||void 0===e||null===(e=e.value)||void 0===e?void 0:e.enabled)&&(null===(r=t.content)||void 0===r||null===(r=r.metadata)||void 0===r||null===(r=r.properties)||void 0===r||null===(r=r[h])||void 0===r||null===(r=r.value)||void 0===r||null===(r=r.state)||void 0===r?void 0:r.final)
})),t.abrupt("return",Zr(Zr({},i),{},{_links:Zr(Zr({},i._links),{},{next:""}),results:c,totalSize:c.length}));case 19:case"end":return t.stop()}}),t,this)}))),
function(t){return q.apply(this,arguments)})},{key:"getPagesFromIds",value:(U=Jr(Hr().mark((function t(e){var r,n,o,i,a,s,u,c=arguments
;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:if(r=c.length>1&&void 0!==c[1]?c[1]:[],o=c.length>3?c[3]:void 0,i=c.length>4?c[4]:void 0,
""!==(a=N("id",e,"AND",n=c.length>2&&void 0!==c[2]?c[2]:[]))){t.next=7;break}
throw new gr("No valid pageIds provided").withFunctionName("getPagesFromIds").withContext({pageIds:e,spaceKeys:r,excludePageIds:n,limit:o,expand:i});case 7:
return s=N("space",r,"AND"),u='type="page" '.concat(a," ").concat(s),t.abrupt("return",this.searchContent({cql:u,limit:o,expand:i}));case 10:case"end":
return t.stop()}}),t,this)}))),function(t){return U.apply(this,arguments)})},{key:"search",value:(V=Jr(Hr().mark((function t(e,r){var n
;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,new T.sK(this.client).search(e,r);case 3:return n=t.sent,
t.abrupt("return",Nr.validate(n));case 7:throw t.prev=7,t.t0=t.catch(0),new gr("Unexpected error on search",t.t0).withFunctionName("search").withContext({params:e,
options:r}).setIsAPIv1();case 10:case"end":return t.stop()}}),t,this,[[0,7]])}))),function(t,e){return V.apply(this,arguments)})},{key:"findPagesWithTitle",
value:(G=Jr(Hr().mark((function t(e,r){var n,o,i;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,
this.logger.debug("Find pages with title with APIV2",{spaceId:e,title:r}),t.next=4,new A.ExtendedConfluence(this.client).confluenceApi.space.getPagesInSpace(e,{
title:r,depth:"all"});case 4:return n=t.sent,o=Dr.validate(n,Or.schema),i=o.results,t.abrupt("return",i);case 9:throw t.prev=9,t.t0=t.catch(0),
new gr("Unexpected error while finding pages with title",t.t0).withFunctionName("findPagesWithTitle").withSpaceId(e).withTitle(r).setIsAPIv2();case 12:case"end":
return t.stop()}}),t,this,[[0,9]])}))),function(t,e){return G.apply(this,arguments)})},{key:"createCustomContent",value:(M=Jr(Hr().mark((function t(e){var r
;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,this.logger.debug("Create custom content with APIV2",{content:e}),t.next=4,
new A.ExtendedConfluence(this.client).confluenceApi.customContent.createCustomContent(e);case 4:return r=t.sent,t.abrupt("return",jr.validate(r));case 8:
throw t.prev=8,
t.t0=t.catch(0),new gr("Unexpected error while creating custom content",t.t0).withFunctionName("createCustomContent").withCustomContent(e).setIsAPIv2();case 11:
case"end":return t.stop()}}),t,this,[[0,8]])}))),function(t){return M.apply(this,arguments)})},{key:"moveContent",value:(F=Jr(Hr().mark((function t(e,r,n){
return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,new T.sK(this.client).moveContent(e,r,n);case 3:t.next=8;break;case 5:
throw t.prev=5,
t.t0=t.catch(0),new gr("Unexpected error while moving content",t.t0).withFunctionName("moveContent").withContentId(e).withTargetContentId(n).setIsAPIv1();case 8:
case"end":return t.stop()}}),t,this,[[0,5]])}))),function(t,e,r){return F.apply(this,arguments)})},{key:"getContentProperty",
value:(B=Jr(Hr().mark((function t(e,r,n){var o;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,
this.logger.debug("Get content property with APIV2",{contentId:e,propertyKey:r}),t.next=4,
new A.ExtendedConfluence(this.client).contentProperties.getPagePropertyByKey(e,r);case 4:return o=t.sent,t.abrupt("return",Ir.validate(o));case 8:throw t.prev=8,
t.t0=t.catch(0),new gr("Unexpected error while getting the content property",t.t0).withFunctionName("getContentProperty").withContext({contentId:e,propertyKey:r,
asUser:n}).setIsAPIv2();case 11:case"end":return t.stop()}}),t,this,[[0,8]])}))),function(t,e,r){return B.apply(this,arguments)})},{key:"setContentProperty",
value:(D=Jr(Hr().mark((function t(e,r,n,o){var i,a,s;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:
return this.logger.debug("Set content property with APIV2",{contentId:e,propertyKey:r,value:n,options:o}),a=null!==(i=null==o?void 0:o.retrials)&&void 0!==i?i:1,
t.prev=2,t.next=5,new A.ExtendedConfluence(this.client).contentProperties.setPageProperty(e,{key:r,value:n},o);case 5:if(s=t.sent){t.next=8;break}
throw new Error("Invalid response received.");case 8:return t.abrupt("return",s);case 11:if(t.prev=11,t.t0=t.catch(2),!(409===t.t0.status&&a>0)){t.next=16;break}
return console.warn("Retrying setContentProperty (409 received), ".concat(a," tries left")),t.abrupt("return",this.setContentProperty(e,r,n,Object.assign({},o,{
retrials:a-1})));case 16:throw new gr("Unexpected error while setting content property",t.t0).withFunctionName("setContentProperty").withContext({contentId:e,
propertyKey:r,value:n}).setIsAPIv2();case 17:case"end":return t.stop()}}),t,this,[[2,11]])}))),function(t,e,r,n){return D.apply(this,arguments)})},{
key:"deleteContentProperty",value:(R=Jr(Hr().mark((function t(e,r){return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,
this.logger.debug("Delete content property with APIV2",{contentId:e,propertyKey:r}),t.next=4,
new A.ExtendedConfluence(this.client).contentProperties.deletePagePropertyByKey(e,r);case 4:t.next=9;break;case 6:throw t.prev=6,t.t0=t.catch(0),
new gr("Unexpected error while deleting content property",t.t0).withFunctionName("deleteContentProperty").withContentId(e).withPropertyKey(r).setIsAPIv2();case 9:
case"end":return t.stop()}}),t,this,[[0,6]])}))),function(t,e){return R.apply(this,arguments)})},{key:"getAttachmentsForPage",value:(L=Jr(Hr().mark((function t(e,r){
var n,o,i;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,this.logger.debug("Get attachments for page with APIV2",{pageId:e,
params:r}),t.next=4,new A.ExtendedConfluence(this.client).confluenceApi.attachment.getAttachmentsForPage(e,r);case 4:return n=t.sent,o=Dr.validate(n,Cr.schema),
i=o.results,t.abrupt("return",i);case 9:
throw t.prev=9,t.t0=t.catch(0),new gr("Unexpected error while getting attachments for page",t.t0).withFunctionName("getAttachmentsForPage").withContext({params:r
}).withPageId(e).setIsAPIv2();case 12:case"end":return t.stop()}}),t,this,[[0,9]])}))),function(t,e){return L.apply(this,arguments)})},{key:"getCustomContentInPage",
value:(I=Jr(Hr().mark((function t(e,r){var n,o,i;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,
this.logger.debug("Get custom content in page with APIV2",{pageId:e,params:r}),t.next=4,
new A.ExtendedConfluence(this.client).confluenceApi.customContent.getCustomContent(e,a.ContentType.Page,r);case 4:return n=t.sent,o=Dr.validate(n,jr.schema),
i=o.results,t.abrupt("return",i);case 9:
throw t.prev=9,t.t0=t.catch(0),new gr("Unexpected error while getting the custom contents in Page",t.t0).withFunctionName("getCustomContentInPage").withContext({
params:r}).withPageId(e).setIsAPIv2();case 12:case"end":return t.stop()}}),t,this,[[0,9]])}))),function(t,e){return I.apply(this,arguments)})},{
key:"deleteAttachment",value:(C=Jr(Hr().mark((function t(e){var r,n=this,o=arguments;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:
return r=o.length>1&&void 0!==o[1]?o[1]:1,t.prev=1,this.logger.debug("Delete attachment with APIV2",{attachmentId:e}),t.next=5,
new A.ExtendedConfluence(this.client).confluenceApi.attachment.deleteAttachment(e);case 5:t.next=11;break;case 7:return t.prev=7,t.t0=t.catch(1),t.next=11,
new gr("Unexpected error while deleting attachment",t.t0).withFunctionName("deleteAttachment").withAttachmentId(e).setIsAPIv2().withRetryableStatusCodes([500]).withHandleError((function(){
return n.deleteAttachment(e,r-1)}),r,this.logger);case 11:case"end":return t.stop()}}),t,this,[[1,7]])}))),function(t){return C.apply(this,arguments)})},{
key:"deletePage",value:(j=Jr(Hr().mark((function t(e){return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,
this.logger.debug("Delete page with APIV2",{pageId:e}),t.next=4,new A.ExtendedConfluence(this.client).confluenceApi.page.deletePage(e);case 4:t.next=9;break;case 6:
throw t.prev=6,t.t0=t.catch(0),new gr("Unexpected error while deleting page",t.t0).withFunctionName("deletePage").withPageId(e).setIsAPIv2();case 9:case"end":
return t.stop()}}),t,this,[[0,6]])}))),function(t){return j.apply(this,arguments)})},{key:"getOperationsForPage",value:(k=Jr(Hr().mark((function t(e){var r
;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,this.logger.debug("Get permitted operations for page with APIV2",{pageId:e}),
t.next=4,new A.ExtendedConfluence(this.client).confluenceApi.operation.getPermittedOperationsForPage(e);case 4:return r=t.sent,t.abrupt("return",Tr.validate(r))
;case 8:
throw t.prev=8,t.t0=t.catch(0),new gr("Unexpected error while getting the operations for Page",t.t0).withFunctionName("getOperationsForPage").withPageId(e).setIsAPIv2()
;case 11:case"end":return t.stop()}}),t,this,[[0,8]])}))),function(t){return k.apply(this,arguments)})},{key:"getOperationsForSpace",
value:(O=Jr(Hr().mark((function t(e){var r;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,
this.logger.debug("Get permitted operations for space with APIV2",{spaceId:e}),t.next=4,
new A.ExtendedConfluence(this.client).confluenceApi.operation.getPermittedOperationsForSpace(e);case 4:return r=t.sent,t.abrupt("return",Tr.validate(r));case 8:
throw t.prev=8,
t.t0=t.catch(0),new gr("Unexpected error while getting the operations for Page",t.t0).withFunctionName("getOperationsForSpace").withPageId(e).setIsAPIv2();case 11:
case"end":return t.stop()}}),t,this,[[0,8]])}))),function(t){return O.apply(this,arguments)})},{key:"getSpaceById",value:(E=Jr(Hr().mark((function t(e,r){var n
;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,this.logger.debug("Get space by id with APIV2",{spaceId:e,params:r}),t.next=4,
new A.ExtendedConfluence(this.client).confluenceApi.space.getSpaceById(e,r);case 4:return n=t.sent,t.abrupt("return",Ar.validate(n));case 8:throw t.prev=8,
t.t0=t.catch(0),new gr("Unexpected error while getting the space",t.t0).withFunctionName("getSpaceById").withSpaceId(e).withContext({params:r}).setIsAPIv2();case 11:
case"end":return t.stop()}}),t,this,[[0,8]])}))),function(t,e){return E.apply(this,arguments)})},{key:"getSpaceByKey",value:(S=Jr(Hr().mark((function t(e,r){var n
;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,this.logger.debug("Get space by key with APIV2",{spaceKey:e,params:r}),t.next=4,
new A.ExtendedConfluence(this.client).space.getOneSpaceByKey(e,r);case 4:return n=t.sent,t.abrupt("return",Ar.validate(n));case 8:throw t.prev=8,t.t0=t.catch(0),
new gr("Unexpected error while getting the space by key",t.t0).withFunctionName("getSpaceByKey").withSpaceKey(e).withContext({params:r}).setIsAPIv2();case 11:
case"end":return t.stop()}}),t,this,[[0,8]])}))),function(t,e){return S.apply(this,arguments)})},{key:"getSpacePermissions",value:(P=Jr(Hr().mark((function t(e,r){
var n;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,this.logger.debug("Get space permissions with APIV2",{spaceKey:e,params:r}),
t.next=4,new A.ExtendedConfluence(this.client).spacePermissions.getSpacePermissionsByKey(e,r);case 4:return n=t.sent,t.abrupt("return",n.map((function(t){
return Br.validate(t)})));case 8:
throw t.prev=8,t.t0=t.catch(0),new gr("Unexpected error while getting space permissions",t.t0).withFunctionName("getSpacePermissions").withSpaceKey(e).withContext({
params:r}).setIsAPIv2();case 11:case"end":return t.stop()}}),t,this,[[0,8]])}))),function(t,e){return P.apply(this,arguments)})},{key:"getSpaces",
value:(x=Jr(Hr().mark((function t(e){var r,n,o;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,
this.logger.debug("Get spaces with APIV2",{params:e}),t.next=4,new A.ExtendedConfluence(this.client).confluenceApi.space.getSpaces(e);case 4:return r=t.sent,
n=Dr.validate(r,Ar.schema),o=n.results,t.abrupt("return",o);case 9:throw t.prev=9,t.t0=t.catch(0),
new gr("Unexpected error while getting spaces",t.t0).withFunctionName("getSpaces").withContext({params:e}).setIsAPIv2();case 12:case"end":return t.stop()}
}),t,this,[[0,9]])}))),function(t){return x.apply(this,arguments)})},{key:"getSpaceProperty",value:(_=Jr(Hr().mark((function t(e,r){var n
;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,this.logger.debug("Get space property with APIV2",{spaceKey:e,spacePropertyKey:r
}),t.next=4,new A.ExtendedConfluence(this.client).spaceProperties.getSpacePropertyByKey({key:e},r);case 4:return n=t.sent,t.abrupt("return",Mr.validate(n));case 8:
throw t.prev=8,
t.t0=t.catch(0),new gr("Unexpected error while getting space property",t.t0).withFunctionName("getSpaceProperty").withSpaceKey(e).withPropertyKey(r).setIsAPIv2()
;case 11:case"end":return t.stop()}}),t,this,[[0,8]])}))),function(t,e){return _.apply(this,arguments)})},{key:"setSpaceProperty",
value:(w=Jr(Hr().mark((function t(e,r,n,o){var i;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,
this.logger.debug("Set space property with APIV2",{spaceKey:e,spacePropertyKey:r,value:n,options:o}),t.next=4,
new A.ExtendedConfluence(this.client).spaceProperties.setSpaceProperty({key:e},{key:r,value:n},o);case 4:return i=t.sent,t.abrupt("return",Mr.validate(i));case 8:
throw t.prev=8,t.t0=t.catch(0),new gr("Unexpected error while setting space property",t.t0).withFunctionName("setSpaceProperty").withContext({spaceKey:e,
spacePropertyKey:r,value:n,options:o}).setIsAPIv2();case 11:case"end":return t.stop()}}),t,this,[[0,8]])}))),function(t,e,r,n){return w.apply(this,arguments)})},{
key:"deleteSpaceProperty",value:(b=Jr(Hr().mark((function t(e,r){return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,
this.logger.debug("Delete space property with APIV2",{spaceKey:e,spacePropertyKey:r}),t.next=4,
new A.ExtendedConfluence(this.client).spaceProperties.deleteSpacePropertyByKey({key:e},r);case 4:t.next=9;break;case 6:throw t.prev=6,t.t0=t.catch(0),
new gr("Unexpected error while deleting space property",t.t0).withFunctionName("deleteSpaceProperty").withSpaceKey(e).withPropertyKey(r).setIsAPIv2();case 9:
case"end":return t.stop()}}),t,this,[[0,6]])}))),function(t,e){return b.apply(this,arguments)})},{key:"copySinglePage",value:(m=Jr(Hr().mark((function t(e,r){var n
;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,new T.sK(this.client).copySinglePage(e,r);case 3:return n=t.sent,
t.abrupt("return",Er.validate(n));case 7:
throw t.prev=7,t.t0=t.catch(0),new gr("Unexpected error on copy single page",t.t0).withFunctionName("copySinglePage").withContext({contentId:e,params:r
}).setIsAPIv1();case 10:case"end":return t.stop()}}),t,this,[[0,7]])}))),function(t,e){return m.apply(this,arguments)})},{key:"getCurrentUser",
value:(g=Jr(Hr().mark((function t(){var e,r,n=arguments;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return e=n.length>0&&void 0!==n[0]?n[0]:[],
t.prev=1,t.next=4,new T.sK(this.client).getUserCurrent({expand:e});case 4:return r=t.sent,t.abrupt("return",Rr.validate(r));case 8:throw t.prev=8,t.t0=t.catch(1),
new gr("Unexpected error on get current user",t.t0).withFunctionName("getCurrentUser").withContext({expand:e}).setIsAPIv1();case 11:case"end":return t.stop()}
}),t,this,[[1,8]])}))),function(){return g.apply(this,arguments)})},{key:"getUser",value:(v=Jr(Hr().mark((function t(){var e,r,n,o=arguments
;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:if(r=o.length>1&&void 0!==o[1]?o[1]:[],!(e=o.length>0&&void 0!==o[0]?o[0]:"")){t.next=15;break}
return t.prev=3,t.next=6,new T.sK(this.client).getUser({accountId:e},{expand:r});case 6:return n=t.sent,t.abrupt("return",Rr.validate(n));case 10:throw t.prev=10,
t.t0=t.catch(3),new gr("Unexpected error on get user",t.t0).withFunctionName("getUser").withContext({accountId:e,expand:r}).setIsAPIv1();case 13:t.next=16;break
;case 15:return t.abrupt("return",this.getCurrentUser(r));case 16:case"end":return t.stop()}}),t,this,[[3,10]])}))),function(){return v.apply(this,arguments)})},{
key:"getVersion",value:function(t,e,r){return new T.sK(this.client).getContentHistory(t,{expand:e},{asUser:r})}},{key:"getAddonProperty",
value:(y=Jr(Hr().mark((function t(e,r,n){var o,i,a,s=arguments;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:
return o=s.length>3&&void 0!==s[3]?s[3]:{},t.prev=1,t.next=4,new T.sK(this.client).getAddonProperty(e,r,o);case 4:return i=t.sent,t.abrupt("return",Gr.validate(i))
;case 8:return t.prev=8,t.t0=t.catch(1),a={value:n},t.abrupt("return",a);case 12:case"end":return t.stop()}}),t,this,[[1,8]])}))),function(t,e,r){
return y.apply(this,arguments)})},{key:"setAddonProperty",value:(d=Jr(Hr().mark((function t(e,r,n){var o,i,a=arguments;return Hr().wrap((function(t){
for(;;)switch(t.prev=t.next){case 0:return o=a.length>3&&void 0!==a[3]?a[3]:{},t.prev=1,t.next=4,new T.sK(this.client).setAddonProperty(e,r,n,o);case 4:
return i=t.sent,t.abrupt("return",i);case 8:
throw t.prev=8,t.t0=t.catch(1),new gr("Unexpected error on set addon property",t.t0).withFunctionName("setAddonProperty").withContext({addonKey:e,key:r,data:n,
options:o}).setIsAPIv1();case 11:case"end":return t.stop()}}),t,this,[[1,8]])}))),function(t,e,r){return d.apply(this,arguments)})},{key:"createStatus",
value:function(t,e,r){return this.setContentProperty(t,l,{state:e},{asUser:r})}},{key:"setSourceStatus",value:function(t,e,r){
var n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:void 0;return this._setStatus(t,{state:e,targetContentId:"".concat(r)},n)}},{key:"setTargetStatus",
value:function(t,e,r){var n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:void 0;return this._setStatus(t,{state:e,sourceContentId:"".concat(r)},n)}},{
key:"setTargetParentContentId",value:function(t,e,r,n){var o={asUser:n,merge:!0};return this.setContentProperty(t,l,{state:e,targetParentContentId:r},o)}},{
key:"setManifest",value:function(t,e,r,n){var o=n||this.context.accountId;return this.logger.debug("Set MANIFEST [".concat(t,", ").concat(e,"]"),{sourceContentId:t,
targetContentId:e,asUser:n,body:r}),Promise.all([this._setStatus(t,Zr({targetContentId:"".concat(e)},r),o),this._setStatus(e,Zr({sourceContentId:"".concat(t)
},r),o)])}},{key:"_setStatus",value:(f=Jr(Hr().mark((function t(e,r,n){var o,i,a;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,
this.getContentProperty(e,l,n);case 2:if(!t.sent){t.next=6;break}t.t0={merge:!0,asUser:n},t.next=7;break;case 6:t.t0={asUser:n};case 7:return o=t.t0,t.next=10,
this.setContentProperty(e,l,r,o);case 10:return i=t.sent,a=i.value,t.abrupt("return",a);case 13:case"end":return t.stop()}}),t,this)}))),function(t,e,r){
return f.apply(this,arguments)})},{key:"getStatus",value:(u=Jr(Hr().mark((function t(e,r){var n,o,i;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){
case 0:return t.prev=0,t.next=3,this.getContentProperty(e,l,r);case 3:if(t.t0=t.sent,t.t0){t.next=6;break}t.t0={};case 6:return n=t.t0,o=n.value,i=void 0===o?{
state:p.NEW}:o,t.abrupt("return",i);case 12:if(t.prev=12,t.t1=t.catch(0),!t.t1.isEmpty()){t.next=16;break}return t.abrupt("return",{state:p.NEW});case 16:throw t.t1
;case 17:case"end":return t.stop()}}),t,this,[[0,12]])}))),function(t,e){return u.apply(this,arguments)})},{key:"getSpaceConfig",
value:(s=Jr(Hr().mark((function t(e){var r;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,this.getSpaceProperty(e,c);case 2:
return r=t.sent,t.abrupt("return",r.value);case 4:case"end":return t.stop()}}),t,this)}))),function(t){return s.apply(this,arguments)})},{key:"setSpaceConfig",
value:(i=Jr(Hr().mark((function t(e,r){var n,o,i=arguments;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:
return n=i.length>2&&void 0!==i[2]&&i[2],t.next=3,this.setSpaceProperty(e,c,r,{merge:n});case 3:return o=t.sent,t.abrupt("return",o.value);case 5:case"end":
return t.stop()}}),t,this)}))),function(t,e){return i.apply(this,arguments)})},{key:"deleteSpaceConfig",value:function(t){return this.deleteSpaceProperty(t,c)}},{
key:"getIsAppInstalled",value:(o=Jr(Hr().mark((function t(e){var r,n;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return r=!1,t.prev=1,t.next=4,
new A.ExtendedConfluence(this.client).sendRequest({url:"/rest/atlassian-connect/1/addons/".concat(e),type:"GET",contentType:"application/json"});case 4:n=t.sent,
r=!!n,t.next=10;break;case 8:t.prev=8,t.t0=t.catch(1);case 10:return t.abrupt("return",r);case 11:case"end":return t.stop()}}),t,this,[[1,8]])}))),function(t){
return o.apply(this,arguments)})},{key:"getLabelsForPage",value:(n=Jr(Hr().mark((function t(e,r){var n,o;return Hr().wrap((function(t){for(;;)switch(t.prev=t.next){
case 0:return t.prev=0,this.logger.debug("Get labels by content id and content type with APIV2",{contentId:e,params:r}),t.next=4,
new A.ExtendedConfluence(this.client).confluenceApi.label.getLabelsByContentIdAndContentType(e,"pages",r);case 4:return n=t.sent,o=n.results,
t.abrupt("return",Vr.validate(o));case 9:
throw t.prev=9,t.t0=t.catch(0),new gr("Unexpected error while getting labels",t.t0).withFunctionName("getLabelsForPage").withContext({contentId:e,params:r
}).setIsAPIv2();case 12:case"end":return t.stop()}}),t,this,[[0,9]])}))),function(t,e){return n.apply(this,arguments)})}],e&&Wr(t.prototype,e),r&&Wr(t,r),
Object.defineProperty(t,"prototype",{writable:!1}),t;var t,e,r,n,o,i,s,u,f,d,y,v,g,m,b,w,_,x,P,S,E,O,k,j,C,I,L,R,D,B,F,M,G,V,U,q,Z,K,z,$,H,Y}();var tn=function(t){
for(var e=u+en(t),r=arguments.length,n=new Array(r>1?r-1:0),o=1;o<r;o++)n[o-1]=arguments[o];var i=n.filter((function(t){return t}))
;if(Object.prototype.hasOwnProperty.call(d,t)){var a=d[t];if(a.params.length===i.length)for(var s=0;s<i.length;s++)e=e.replace(a.params[s],i[s])}return e
},en=function(t){return Object.prototype.hasOwnProperty.call(d,t)?d[t].url:""};function rn(t){
return rn="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},rn(t)}function nn(t,e){var r=Object.keys(t)
;if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(t);e&&(n=n.filter((function(e){return Object.getOwnPropertyDescriptor(t,e).enumerable}))),
r.push.apply(r,n)}return r}function on(t){for(var e=1;e<arguments.length;e++){var r=null!=arguments[e]?arguments[e]:{};e%2?nn(Object(r),!0).forEach((function(e){
an(t,e,r[e])})):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(r)):nn(Object(r)).forEach((function(e){
Object.defineProperty(t,e,Object.getOwnPropertyDescriptor(r,e))}))}return t}function an(t,e,r){return(e=function(t){var e=function(t,e){
if("object"!=rn(t)||!t)return t;var r=t[Symbol.toPrimitive];if(void 0!==r){var n=r.call(t,e||"default");if("object"!=rn(n))return n
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==rn(e)?e:e+""
}(e))in t?Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}):t[e]=r,t}const sn=function(t){return new Promise((function(e,r){var n={
type:"GET",contentType:"application/json",error:function(t){try{var e=JSON.parse((null==t?void 0:t.responseText)||"{}");null!=e&&e.statusCode&&Object.assign(e,{
status:e.statusCode}),r(e)}catch(e){r({status:500,message:(null==t?void 0:t.responseText)||"Server response error"})}}}
;t.binaryAttachment?AP.request(on(on(on({},n),t),{},{success:function(t){e(t)}})):AP.request(on(on(on({},n),t),{},{success:function(t){try{e(JSON.parse(t))}catch(r){
e(t)}}}))}))};function un(t){return un="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},un(t)}function cn(){cn=function(){return e}
;var t,e={},r=Object.prototype,n=r.hasOwnProperty,o=Object.defineProperty||function(t,e,r){t[e]=r.value
},i="function"==typeof Symbol?Symbol:{},a=i.iterator||"@@iterator",s=i.asyncIterator||"@@asyncIterator",u=i.toStringTag||"@@toStringTag";function c(t,e,r){
return Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}),t[e]}try{c({},"")}catch(t){c=function(t,e,r){return t[e]=r}}
function l(t,e,r,n){var i=e&&e.prototype instanceof g?e:g,a=Object.create(i.prototype),s=new T(n||[]);return o(a,"_invoke",{value:O(t,r,s)}),a}function f(t,e,r){try{
return{type:"normal",arg:t.call(e,r)}}catch(t){return{type:"throw",arg:t}}}e.wrap=l;var h="suspendedStart",p="suspendedYield",d="executing",y="completed",v={}
;function g(){}function m(){}function b(){}var w={};c(w,a,(function(){return this}));var _=Object.getPrototypeOf,x=_&&_(_(A([])));x&&x!==r&&n.call(x,a)&&(w=x)
;var P=b.prototype=g.prototype=Object.create(w);function S(t){["next","throw","return"].forEach((function(e){c(t,e,(function(t){return this._invoke(e,t)}))}))}
function E(t,e){function r(o,i,a,s){var u=f(t[o],t,i);if("throw"!==u.type){var c=u.arg,l=c.value
;return l&&"object"==un(l)&&n.call(l,"__await")?e.resolve(l.__await).then((function(t){r("next",t,a,s)}),(function(t){r("throw",t,a,s)
})):e.resolve(l).then((function(t){c.value=t,a(c)}),(function(t){return r("throw",t,a,s)}))}s(u.arg)}var i;o(this,"_invoke",{value:function(t,n){function o(){
return new e((function(e,o){r(t,n,e,o)}))}return i=i?i.then(o,o):o()}})}function O(e,r,n){var o=h;return function(i,a){
if(o===d)throw Error("Generator is already running");if(o===y){if("throw"===i)throw a;return{value:t,done:!0}}for(n.method=i,n.arg=a;;){var s=n.delegate;if(s){
var u=k(s,n);if(u){if(u===v)continue;return u}}if("next"===n.method)n.sent=n._sent=n.arg;else if("throw"===n.method){if(o===h)throw o=y,n.arg
;n.dispatchException(n.arg)}else"return"===n.method&&n.abrupt("return",n.arg);o=d;var c=f(e,r,n);if("normal"===c.type){if(o=n.done?y:p,c.arg===v)continue;return{
value:c.arg,done:n.done}}"throw"===c.type&&(o=y,n.method="throw",n.arg=c.arg)}}}function k(e,r){var n=r.method,o=e.iterator[n];if(o===t)return r.delegate=null,
"throw"===n&&e.iterator.return&&(r.method="return",r.arg=t,k(e,r),"throw"===r.method)||"return"!==n&&(r.method="throw",
r.arg=new TypeError("The iterator does not provide a '"+n+"' method")),v;var i=f(o,e.iterator,r.arg);if("throw"===i.type)return r.method="throw",r.arg=i.arg,
r.delegate=null,v;var a=i.arg;return a?a.done?(r[e.resultName]=a.value,r.next=e.nextLoc,"return"!==r.method&&(r.method="next",r.arg=t),r.delegate=null,
v):a:(r.method="throw",r.arg=new TypeError("iterator result is not an object"),r.delegate=null,v)}function j(t){var e={tryLoc:t[0]};1 in t&&(e.catchLoc=t[1]),
2 in t&&(e.finallyLoc=t[2],e.afterLoc=t[3]),this.tryEntries.push(e)}function C(t){var e=t.completion||{};e.type="normal",delete e.arg,t.completion=e}function T(t){
this.tryEntries=[{tryLoc:"root"}],t.forEach(j,this),this.reset(!0)}function A(e){if(e||""===e){var r=e[a];if(r)return r.call(e);if("function"==typeof e.next)return e
;if(!isNaN(e.length)){var o=-1,i=function r(){for(;++o<e.length;)if(n.call(e,o))return r.value=e[o],r.done=!1,r;return r.value=t,r.done=!0,r};return i.next=i}}
throw new TypeError(un(e)+" is not iterable")}return m.prototype=b,o(P,"constructor",{value:b,configurable:!0}),o(b,"constructor",{value:m,configurable:!0}),
m.displayName=c(b,u,"GeneratorFunction"),e.isGeneratorFunction=function(t){var e="function"==typeof t&&t.constructor
;return!!e&&(e===m||"GeneratorFunction"===(e.displayName||e.name))},e.mark=function(t){return Object.setPrototypeOf?Object.setPrototypeOf(t,b):(t.__proto__=b,
c(t,u,"GeneratorFunction")),t.prototype=Object.create(P),t},e.awrap=function(t){return{__await:t}},S(E.prototype),c(E.prototype,s,(function(){return this})),
e.AsyncIterator=E,e.async=function(t,r,n,o,i){void 0===i&&(i=Promise);var a=new E(l(t,r,n,o),i);return e.isGeneratorFunction(r)?a:a.next().then((function(t){
return t.done?t.value:a.next()}))},S(P),c(P,u,"Generator"),c(P,a,(function(){return this})),c(P,"toString",(function(){return"[object Generator]"})),
e.keys=function(t){var e=Object(t),r=[];for(var n in e)r.push(n);return r.reverse(),function t(){for(;r.length;){var n=r.pop();if(n in e)return t.value=n,t.done=!1,t
}return t.done=!0,t}},e.values=A,T.prototype={constructor:T,reset:function(e){if(this.prev=0,this.next=0,this.sent=this._sent=t,this.done=!1,this.delegate=null,
this.method="next",this.arg=t,this.tryEntries.forEach(C),!e)for(var r in this)"t"===r.charAt(0)&&n.call(this,r)&&!isNaN(+r.slice(1))&&(this[r]=t)},stop:function(){
this.done=!0;var t=this.tryEntries[0].completion;if("throw"===t.type)throw t.arg;return this.rval},dispatchException:function(e){if(this.done)throw e;var r=this
;function o(n,o){return s.type="throw",s.arg=e,r.next=n,o&&(r.method="next",r.arg=t),!!o}for(var i=this.tryEntries.length-1;i>=0;--i){
var a=this.tryEntries[i],s=a.completion;if("root"===a.tryLoc)return o("end");if(a.tryLoc<=this.prev){var u=n.call(a,"catchLoc"),c=n.call(a,"finallyLoc");if(u&&c){
if(this.prev<a.catchLoc)return o(a.catchLoc,!0);if(this.prev<a.finallyLoc)return o(a.finallyLoc)}else if(u){if(this.prev<a.catchLoc)return o(a.catchLoc,!0)}else{
if(!c)throw Error("try statement without catch or finally");if(this.prev<a.finallyLoc)return o(a.finallyLoc)}}}},abrupt:function(t,e){
for(var r=this.tryEntries.length-1;r>=0;--r){var o=this.tryEntries[r];if(o.tryLoc<=this.prev&&n.call(o,"finallyLoc")&&this.prev<o.finallyLoc){var i=o;break}}
i&&("break"===t||"continue"===t)&&i.tryLoc<=e&&e<=i.finallyLoc&&(i=null);var a=i?i.completion:{};return a.type=t,a.arg=e,i?(this.method="next",
this.next=i.finallyLoc,v):this.complete(a)},complete:function(t,e){if("throw"===t.type)throw t.arg
;return"break"===t.type||"continue"===t.type?this.next=t.arg:"return"===t.type?(this.rval=this.arg=t.arg,this.method="return",
this.next="end"):"normal"===t.type&&e&&(this.next=e),v},finish:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.finallyLoc===t)return this.complete(r.completion,r.afterLoc),C(r),v}},catch:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.tryLoc===t){var n=r.completion;if("throw"===n.type){var o=n.arg;C(r)}return o}}throw Error("illegal catch attempt")},delegateYield:function(e,r,n){
return this.delegate={iterator:A(e),resultName:r,nextLoc:n},"next"===this.method&&(this.arg=t),v}},e}function ln(t,e){var r=Object.keys(t)
;if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(t);e&&(n=n.filter((function(e){return Object.getOwnPropertyDescriptor(t,e).enumerable}))),
r.push.apply(r,n)}return r}function fn(t){for(var e=1;e<arguments.length;e++){var r=null!=arguments[e]?arguments[e]:{};e%2?ln(Object(r),!0).forEach((function(e){
hn(t,e,r[e])})):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(r)):ln(Object(r)).forEach((function(e){
Object.defineProperty(t,e,Object.getOwnPropertyDescriptor(r,e))}))}return t}function hn(t,e,r){return(e=function(t){var e=function(t,e){
if("object"!=un(t)||!t)return t;var r=t[Symbol.toPrimitive];if(void 0!==r){var n=r.call(t,e||"default");if("object"!=un(n))return n
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==un(e)?e:e+""
}(e))in t?Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}):t[e]=r,t}function pn(t,e,r,n,o,i,a){try{var s=t[i](a),u=s.value}catch(t){
return void r(t)}s.done?e(u):Promise.resolve(u).then(n,o)}function dn(t){return function(){var e=this,r=arguments;return new Promise((function(n,o){
var i=t.apply(e,r);function a(t){pn(i,n,o,a,s,"next",t)}function s(t){pn(i,n,o,a,s,"throw",t)}a(void 0)}))}}var yn=g(),vn=function(t){
var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:["darkDebug","contentType"],r=t.indexOf("?"),n=e.filter((function(t){return yn[t]})).map((function(t){
return"".concat(t,"=").concat(yn[t])})).join("&");return-1!==r?"".concat(t,"&").concat(n):"".concat(t,"?").concat(n)},gn=function(){
var t=dn(cn().mark((function t(e){var r,n,o,i,a,s,c,l,f,h,p,d,y;return cn().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return r=e.url,n=void 0===r?"":r,
o=e.type,i=void 0===o?"GET":o,a=e.contentType,s=void 0===a?"application/json":a,c=e.data,l=void 0===c?{}:c,f=e.silent,h=void 0!==f&&f,p=e.gzip,d=void 0!==p&&p,
t.next=3,new Promise((function(t){AP.context.getToken(t)}));case 3:return y=t.sent,t.abrupt("return",new Promise((function(t,e){var r=function(){
var t=dn(cn().mark((function t(r){var n,o,i,a,s,u,c;return cn().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:if(n={title:"Error",body:"",type:"error"},
"string"==typeof r)n=fn(fn({},n),{},{body:r}),o=r;else if(Object.prototype.hasOwnProperty.call(r,"body"))o="string"==typeof(a=r).body?a.body:a.body.message,
n=fn(fn({},n),{},{title:"Error ".concat(null!==(i=a.status)&&void 0!==i?i:""),body:o});else if(o=r.statusText,n=fn(fn({},n),{},{
title:"Error ".concat(null!==(s=r.status)&&void 0!==s?s:""),body:r.statusText}),Object.prototype.hasOwnProperty.call(r,"responseText")){u=r;try{
o=JSON.parse(u.responseText),Object.prototype.hasOwnProperty.call(o,"message")&&(n=fn(fn({},n),{},{body:o.message}))}catch(t){}}if(h){t.next=5;break}
throw null===(c=AP)||void 0===c||null===(c=c.flag)||void 0===c||c.create(n),new Error(n.body);case 5:e(r);case 6:case"end":return t.stop()}}),t)})))
;return function(e){return t.apply(this,arguments)}}(),o={contentType:s,headers:{Accept:"*/*","If-Match":"*","If-None-Match":"*","Cache-Control":"no-cache",
Authorization:"JWT ".concat(y),"Content-Type":s}};/^https?:\/\//.test(n)||0===n.indexOf(u)?(o=fn(fn({},o),{},{gzip:d}),"GET"!==i&&(o=fn(fn({},o),{},{method:i,
body:JSON.stringify(l)})),fetch(vn(n),o).then(function(){var e=dn(cn().mark((function e(n){var o;return cn().wrap((function(e){for(;;)switch(e.prev=e.next){case 0:
return e.prev=0,e.next=3,n.json();case 3:o=e.sent,n.ok?t(o):r(fn(fn({},n),{},{body:o})),e.next=10;break;case 7:e.prev=7,e.t0=e.catch(0),r(e.t0);case 10:case"end":
return e.stop()}}),e,null,[[0,7]])})));return function(t){return e.apply(this,arguments)}}())):AP.request(fn(fn({type:i},o),{},{url:n,
data:"GET"!==i?JSON.stringify(l):l,success:function(e){if(e)try{t(JSON.parse(e))}catch(t){r(e)}else t(e)},error:r}))})));case 5:case"end":return t.stop()}}),t)})))
;return function(e){return t.apply(this,arguments)}}();const mn=gn;function bn(t){return bn="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){
return typeof t}:function(t){return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},bn(t)}function wn(){wn=function(){
return e};var t,e={},r=Object.prototype,n=r.hasOwnProperty,o=Object.defineProperty||function(t,e,r){t[e]=r.value
},i="function"==typeof Symbol?Symbol:{},a=i.iterator||"@@iterator",s=i.asyncIterator||"@@asyncIterator",u=i.toStringTag||"@@toStringTag";function c(t,e,r){
return Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}),t[e]}try{c({},"")}catch(t){c=function(t,e,r){return t[e]=r}}
function l(t,e,r,n){var i=e&&e.prototype instanceof g?e:g,a=Object.create(i.prototype),s=new T(n||[]);return o(a,"_invoke",{value:O(t,r,s)}),a}function f(t,e,r){try{
return{type:"normal",arg:t.call(e,r)}}catch(t){return{type:"throw",arg:t}}}e.wrap=l;var h="suspendedStart",p="suspendedYield",d="executing",y="completed",v={}
;function g(){}function m(){}function b(){}var w={};c(w,a,(function(){return this}));var _=Object.getPrototypeOf,x=_&&_(_(A([])));x&&x!==r&&n.call(x,a)&&(w=x)
;var P=b.prototype=g.prototype=Object.create(w);function S(t){["next","throw","return"].forEach((function(e){c(t,e,(function(t){return this._invoke(e,t)}))}))}
function E(t,e){function r(o,i,a,s){var u=f(t[o],t,i);if("throw"!==u.type){var c=u.arg,l=c.value
;return l&&"object"==bn(l)&&n.call(l,"__await")?e.resolve(l.__await).then((function(t){r("next",t,a,s)}),(function(t){r("throw",t,a,s)
})):e.resolve(l).then((function(t){c.value=t,a(c)}),(function(t){return r("throw",t,a,s)}))}s(u.arg)}var i;o(this,"_invoke",{value:function(t,n){function o(){
return new e((function(e,o){r(t,n,e,o)}))}return i=i?i.then(o,o):o()}})}function O(e,r,n){var o=h;return function(i,a){
if(o===d)throw Error("Generator is already running");if(o===y){if("throw"===i)throw a;return{value:t,done:!0}}for(n.method=i,n.arg=a;;){var s=n.delegate;if(s){
var u=k(s,n);if(u){if(u===v)continue;return u}}if("next"===n.method)n.sent=n._sent=n.arg;else if("throw"===n.method){if(o===h)throw o=y,n.arg
;n.dispatchException(n.arg)}else"return"===n.method&&n.abrupt("return",n.arg);o=d;var c=f(e,r,n);if("normal"===c.type){if(o=n.done?y:p,c.arg===v)continue;return{
value:c.arg,done:n.done}}"throw"===c.type&&(o=y,n.method="throw",n.arg=c.arg)}}}function k(e,r){var n=r.method,o=e.iterator[n];if(o===t)return r.delegate=null,
"throw"===n&&e.iterator.return&&(r.method="return",r.arg=t,k(e,r),"throw"===r.method)||"return"!==n&&(r.method="throw",
r.arg=new TypeError("The iterator does not provide a '"+n+"' method")),v;var i=f(o,e.iterator,r.arg);if("throw"===i.type)return r.method="throw",r.arg=i.arg,
r.delegate=null,v;var a=i.arg;return a?a.done?(r[e.resultName]=a.value,r.next=e.nextLoc,"return"!==r.method&&(r.method="next",r.arg=t),r.delegate=null,
v):a:(r.method="throw",r.arg=new TypeError("iterator result is not an object"),r.delegate=null,v)}function j(t){var e={tryLoc:t[0]};1 in t&&(e.catchLoc=t[1]),
2 in t&&(e.finallyLoc=t[2],e.afterLoc=t[3]),this.tryEntries.push(e)}function C(t){var e=t.completion||{};e.type="normal",delete e.arg,t.completion=e}function T(t){
this.tryEntries=[{tryLoc:"root"}],t.forEach(j,this),this.reset(!0)}function A(e){if(e||""===e){var r=e[a];if(r)return r.call(e);if("function"==typeof e.next)return e
;if(!isNaN(e.length)){var o=-1,i=function r(){for(;++o<e.length;)if(n.call(e,o))return r.value=e[o],r.done=!1,r;return r.value=t,r.done=!0,r};return i.next=i}}
throw new TypeError(bn(e)+" is not iterable")}return m.prototype=b,o(P,"constructor",{value:b,configurable:!0}),o(b,"constructor",{value:m,configurable:!0}),
m.displayName=c(b,u,"GeneratorFunction"),e.isGeneratorFunction=function(t){var e="function"==typeof t&&t.constructor
;return!!e&&(e===m||"GeneratorFunction"===(e.displayName||e.name))},e.mark=function(t){return Object.setPrototypeOf?Object.setPrototypeOf(t,b):(t.__proto__=b,
c(t,u,"GeneratorFunction")),t.prototype=Object.create(P),t},e.awrap=function(t){return{__await:t}},S(E.prototype),c(E.prototype,s,(function(){return this})),
e.AsyncIterator=E,e.async=function(t,r,n,o,i){void 0===i&&(i=Promise);var a=new E(l(t,r,n,o),i);return e.isGeneratorFunction(r)?a:a.next().then((function(t){
return t.done?t.value:a.next()}))},S(P),c(P,u,"Generator"),c(P,a,(function(){return this})),c(P,"toString",(function(){return"[object Generator]"})),
e.keys=function(t){var e=Object(t),r=[];for(var n in e)r.push(n);return r.reverse(),function t(){for(;r.length;){var n=r.pop();if(n in e)return t.value=n,t.done=!1,t
}return t.done=!0,t}},e.values=A,T.prototype={constructor:T,reset:function(e){if(this.prev=0,this.next=0,this.sent=this._sent=t,this.done=!1,this.delegate=null,
this.method="next",this.arg=t,this.tryEntries.forEach(C),!e)for(var r in this)"t"===r.charAt(0)&&n.call(this,r)&&!isNaN(+r.slice(1))&&(this[r]=t)},stop:function(){
this.done=!0;var t=this.tryEntries[0].completion;if("throw"===t.type)throw t.arg;return this.rval},dispatchException:function(e){if(this.done)throw e;var r=this
;function o(n,o){return s.type="throw",s.arg=e,r.next=n,o&&(r.method="next",r.arg=t),!!o}for(var i=this.tryEntries.length-1;i>=0;--i){
var a=this.tryEntries[i],s=a.completion;if("root"===a.tryLoc)return o("end");if(a.tryLoc<=this.prev){var u=n.call(a,"catchLoc"),c=n.call(a,"finallyLoc");if(u&&c){
if(this.prev<a.catchLoc)return o(a.catchLoc,!0);if(this.prev<a.finallyLoc)return o(a.finallyLoc)}else if(u){if(this.prev<a.catchLoc)return o(a.catchLoc,!0)}else{
if(!c)throw Error("try statement without catch or finally");if(this.prev<a.finallyLoc)return o(a.finallyLoc)}}}},abrupt:function(t,e){
for(var r=this.tryEntries.length-1;r>=0;--r){var o=this.tryEntries[r];if(o.tryLoc<=this.prev&&n.call(o,"finallyLoc")&&this.prev<o.finallyLoc){var i=o;break}}
i&&("break"===t||"continue"===t)&&i.tryLoc<=e&&e<=i.finallyLoc&&(i=null);var a=i?i.completion:{};return a.type=t,a.arg=e,i?(this.method="next",
this.next=i.finallyLoc,v):this.complete(a)},complete:function(t,e){if("throw"===t.type)throw t.arg
;return"break"===t.type||"continue"===t.type?this.next=t.arg:"return"===t.type?(this.rval=this.arg=t.arg,this.method="return",
this.next="end"):"normal"===t.type&&e&&(this.next=e),v},finish:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.finallyLoc===t)return this.complete(r.completion,r.afterLoc),C(r),v}},catch:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.tryLoc===t){var n=r.completion;if("throw"===n.type){var o=n.arg;C(r)}return o}}throw Error("illegal catch attempt")},delegateYield:function(e,r,n){
return this.delegate={iterator:A(e),resultName:r,nextLoc:n},"next"===this.method&&(this.arg=t),v}},e}function _n(t,e,r,n,o,i,a){try{var s=t[i](a),u=s.value}catch(t){
return void r(t)}s.done?e(u):Promise.resolve(u).then(n,o)}function xn(t){return function(){var e=this,r=arguments;return new Promise((function(n,o){
var i=t.apply(e,r);function a(t){_n(i,n,o,a,s,"next",t)}function s(t){_n(i,n,o,a,s,"throw",t)}a(void 0)}))}}var Pn=new Xr(sn),Sn=function(){
var t=xn(wn().mark((function t(e){return wn().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,Pn.getSpaceConfig(e);case 3:
return t.abrupt("return",t.sent);case 6:
return t.prev=6,t.t0=t.catch(0),t.t0 instanceof gr&&t.t0.isEmpty()||console.error('Error getting Publishing Configuration from Space with key "'.concat(e,'"'),t.t0),
t.abrupt("return",Promise.resolve(null));case 10:case"end":return t.stop()}}),t,null,[[0,6]])})));return function(e){return t.apply(this,arguments)}}()
;function En(t){return En="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},En(t)}var On=["jobId"],kn=["jobId"];function jn(t,e){
var r=Object.keys(t);if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(t);e&&(n=n.filter((function(e){
return Object.getOwnPropertyDescriptor(t,e).enumerable}))),r.push.apply(r,n)}return r}function Cn(t){for(var e=1;e<arguments.length;e++){
var r=null!=arguments[e]?arguments[e]:{};e%2?jn(Object(r),!0).forEach((function(e){Tn(t,e,r[e])
})):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(r)):jn(Object(r)).forEach((function(e){
Object.defineProperty(t,e,Object.getOwnPropertyDescriptor(r,e))}))}return t}function Tn(t,e,r){return(e=function(t){var e=function(t,e){
if("object"!=En(t)||!t)return t;var r=t[Symbol.toPrimitive];if(void 0!==r){var n=r.call(t,e||"default");if("object"!=En(n))return n
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==En(e)?e:e+""
}(e))in t?Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}):t[e]=r,t}function An(t,e){if(null==t)return{};var r,n,o=function(t,e){
if(null==t)return{};var r={};for(var n in t)if({}.hasOwnProperty.call(t,n)){if(-1!==e.indexOf(n))continue;r[n]=t[n]}return r}(t,e);if(Object.getOwnPropertySymbols){
var i=Object.getOwnPropertySymbols(t);for(n=0;n<i.length;n++)r=i[n],-1===e.indexOf(r)&&{}.propertyIsEnumerable.call(t,r)&&(o[r]=t[r])}return o}function In(){
In=function(){return e};var t,e={},r=Object.prototype,n=r.hasOwnProperty,o=Object.defineProperty||function(t,e,r){t[e]=r.value
},i="function"==typeof Symbol?Symbol:{},a=i.iterator||"@@iterator",s=i.asyncIterator||"@@asyncIterator",u=i.toStringTag||"@@toStringTag";function c(t,e,r){
return Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}),t[e]}try{c({},"")}catch(t){c=function(t,e,r){return t[e]=r}}
function l(t,e,r,n){var i=e&&e.prototype instanceof g?e:g,a=Object.create(i.prototype),s=new T(n||[]);return o(a,"_invoke",{value:O(t,r,s)}),a}function f(t,e,r){try{
return{type:"normal",arg:t.call(e,r)}}catch(t){return{type:"throw",arg:t}}}e.wrap=l;var h="suspendedStart",p="suspendedYield",d="executing",y="completed",v={}
;function g(){}function m(){}function b(){}var w={};c(w,a,(function(){return this}));var _=Object.getPrototypeOf,x=_&&_(_(A([])));x&&x!==r&&n.call(x,a)&&(w=x)
;var P=b.prototype=g.prototype=Object.create(w);function S(t){["next","throw","return"].forEach((function(e){c(t,e,(function(t){return this._invoke(e,t)}))}))}
function E(t,e){function r(o,i,a,s){var u=f(t[o],t,i);if("throw"!==u.type){var c=u.arg,l=c.value
;return l&&"object"==En(l)&&n.call(l,"__await")?e.resolve(l.__await).then((function(t){r("next",t,a,s)}),(function(t){r("throw",t,a,s)
})):e.resolve(l).then((function(t){c.value=t,a(c)}),(function(t){return r("throw",t,a,s)}))}s(u.arg)}var i;o(this,"_invoke",{value:function(t,n){function o(){
return new e((function(e,o){r(t,n,e,o)}))}return i=i?i.then(o,o):o()}})}function O(e,r,n){var o=h;return function(i,a){
if(o===d)throw Error("Generator is already running");if(o===y){if("throw"===i)throw a;return{value:t,done:!0}}for(n.method=i,n.arg=a;;){var s=n.delegate;if(s){
var u=k(s,n);if(u){if(u===v)continue;return u}}if("next"===n.method)n.sent=n._sent=n.arg;else if("throw"===n.method){if(o===h)throw o=y,n.arg
;n.dispatchException(n.arg)}else"return"===n.method&&n.abrupt("return",n.arg);o=d;var c=f(e,r,n);if("normal"===c.type){if(o=n.done?y:p,c.arg===v)continue;return{
value:c.arg,done:n.done}}"throw"===c.type&&(o=y,n.method="throw",n.arg=c.arg)}}}function k(e,r){var n=r.method,o=e.iterator[n];if(o===t)return r.delegate=null,
"throw"===n&&e.iterator.return&&(r.method="return",r.arg=t,k(e,r),"throw"===r.method)||"return"!==n&&(r.method="throw",
r.arg=new TypeError("The iterator does not provide a '"+n+"' method")),v;var i=f(o,e.iterator,r.arg);if("throw"===i.type)return r.method="throw",r.arg=i.arg,
r.delegate=null,v;var a=i.arg;return a?a.done?(r[e.resultName]=a.value,r.next=e.nextLoc,"return"!==r.method&&(r.method="next",r.arg=t),r.delegate=null,
v):a:(r.method="throw",r.arg=new TypeError("iterator result is not an object"),r.delegate=null,v)}function j(t){var e={tryLoc:t[0]};1 in t&&(e.catchLoc=t[1]),
2 in t&&(e.finallyLoc=t[2],e.afterLoc=t[3]),this.tryEntries.push(e)}function C(t){var e=t.completion||{};e.type="normal",delete e.arg,t.completion=e}function T(t){
this.tryEntries=[{tryLoc:"root"}],t.forEach(j,this),this.reset(!0)}function A(e){if(e||""===e){var r=e[a];if(r)return r.call(e);if("function"==typeof e.next)return e
;if(!isNaN(e.length)){var o=-1,i=function r(){for(;++o<e.length;)if(n.call(e,o))return r.value=e[o],r.done=!1,r;return r.value=t,r.done=!0,r};return i.next=i}}
throw new TypeError(En(e)+" is not iterable")}return m.prototype=b,o(P,"constructor",{value:b,configurable:!0}),o(b,"constructor",{value:m,configurable:!0}),
m.displayName=c(b,u,"GeneratorFunction"),e.isGeneratorFunction=function(t){var e="function"==typeof t&&t.constructor
;return!!e&&(e===m||"GeneratorFunction"===(e.displayName||e.name))},e.mark=function(t){return Object.setPrototypeOf?Object.setPrototypeOf(t,b):(t.__proto__=b,
c(t,u,"GeneratorFunction")),t.prototype=Object.create(P),t},e.awrap=function(t){return{__await:t}},S(E.prototype),c(E.prototype,s,(function(){return this})),
e.AsyncIterator=E,e.async=function(t,r,n,o,i){void 0===i&&(i=Promise);var a=new E(l(t,r,n,o),i);return e.isGeneratorFunction(r)?a:a.next().then((function(t){
return t.done?t.value:a.next()}))},S(P),c(P,u,"Generator"),c(P,a,(function(){return this})),c(P,"toString",(function(){return"[object Generator]"})),
e.keys=function(t){var e=Object(t),r=[];for(var n in e)r.push(n);return r.reverse(),function t(){for(;r.length;){var n=r.pop();if(n in e)return t.value=n,t.done=!1,t
}return t.done=!0,t}},e.values=A,T.prototype={constructor:T,reset:function(e){if(this.prev=0,this.next=0,this.sent=this._sent=t,this.done=!1,this.delegate=null,
this.method="next",this.arg=t,this.tryEntries.forEach(C),!e)for(var r in this)"t"===r.charAt(0)&&n.call(this,r)&&!isNaN(+r.slice(1))&&(this[r]=t)},stop:function(){
this.done=!0;var t=this.tryEntries[0].completion;if("throw"===t.type)throw t.arg;return this.rval},dispatchException:function(e){if(this.done)throw e;var r=this
;function o(n,o){return s.type="throw",s.arg=e,r.next=n,o&&(r.method="next",r.arg=t),!!o}for(var i=this.tryEntries.length-1;i>=0;--i){
var a=this.tryEntries[i],s=a.completion;if("root"===a.tryLoc)return o("end");if(a.tryLoc<=this.prev){var u=n.call(a,"catchLoc"),c=n.call(a,"finallyLoc");if(u&&c){
if(this.prev<a.catchLoc)return o(a.catchLoc,!0);if(this.prev<a.finallyLoc)return o(a.finallyLoc)}else if(u){if(this.prev<a.catchLoc)return o(a.catchLoc,!0)}else{
if(!c)throw Error("try statement without catch or finally");if(this.prev<a.finallyLoc)return o(a.finallyLoc)}}}},abrupt:function(t,e){
for(var r=this.tryEntries.length-1;r>=0;--r){var o=this.tryEntries[r];if(o.tryLoc<=this.prev&&n.call(o,"finallyLoc")&&this.prev<o.finallyLoc){var i=o;break}}
i&&("break"===t||"continue"===t)&&i.tryLoc<=e&&e<=i.finallyLoc&&(i=null);var a=i?i.completion:{};return a.type=t,a.arg=e,i?(this.method="next",
this.next=i.finallyLoc,v):this.complete(a)},complete:function(t,e){if("throw"===t.type)throw t.arg
;return"break"===t.type||"continue"===t.type?this.next=t.arg:"return"===t.type?(this.rval=this.arg=t.arg,this.method="return",
this.next="end"):"normal"===t.type&&e&&(this.next=e),v},finish:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.finallyLoc===t)return this.complete(r.completion,r.afterLoc),C(r),v}},catch:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.tryLoc===t){var n=r.completion;if("throw"===n.type){var o=n.arg;C(r)}return o}}throw Error("illegal catch attempt")},delegateYield:function(e,r,n){
return this.delegate={iterator:A(e),resultName:r,nextLoc:n},"next"===this.method&&(this.arg=t),v}},e}function Ln(t,e,r,n,o,i,a){try{var s=t[i](a),u=s.value}catch(t){
return void r(t)}s.done?e(u):Promise.resolve(u).then(n,o)}function Nn(t){return function(){var e=this,r=arguments;return new Promise((function(n,o){
var i=t.apply(e,r);function a(t){Ln(i,n,o,a,s,"next",t)}function s(t){Ln(i,n,o,a,s,"throw",t)}a(void 0)}))}}var Rn=new Xr(sn),Dn=function(){
var t=Nn(In().mark((function t(e){var r;return In().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,Rn.getSpaceById(e,{
"include-icon":!0});case 3:return r=t.sent,t.abrupt("return",r);case 7:if(t.prev=7,t.t0=t.catch(0),!(t.t0 instanceof gr&&t.t0.isEmpty())){t.next=13;break}
throw new Error('Could not find space with ID "'.concat(e,'"'),t.t0);case 13:throw t.t0;case 14:case"end":return t.stop()}}),t,null,[[0,7]])})));return function(e){
return t.apply(this,arguments)}}(),Bn=function(){var t=Nn(In().mark((function t(e){return In().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,
t.next=3,Rn.getPageById(e);case 3:return t.abrupt("return",t.sent);case 6:if(t.prev=6,t.t0=t.catch(0),!(t.t0 instanceof gr&&t.t0.isEmpty())){t.next=13;break}
return console.error('Could not find page with id "'.concat(e,'"'),t.t0),t.abrupt("return",Promise.resolve(void 0));case 13:throw t.t0;case 14:case"end":
return t.stop()}}),t,null,[[0,6]])})));return function(e){return t.apply(this,arguments)}}(),Fn=function(){var t=Nn(In().mark((function t(e){var r
;return In().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,Rn.getStatus(e);case 3:return t.abrupt("return",t.sent);case 6:t.prev=6,
t.t0=t.catch(0),t.t0 instanceof gr&&t.t0.isEmpty()||console.error('Error getting Publishing Status for page with ID "'.concat(e,'"'),t.t0);case 9:return r={
state:p.NEW},t.abrupt("return",r);case 11:case"end":return t.stop()}}),t,null,[[0,6]])})));return function(e){return t.apply(this,arguments)}}(),Mn=function(t,e,r){
return Rn.setContentProperty(t,l,e,{merge:r})},Gn=function(){var t=Nn(In().mark((function t(e){var r,n;return In().wrap((function(t){for(;;)switch(t.prev=t.next){
case 0:return t.prev=0,t.next=3,Rn.getContentProperty(e,f);case 3:return r=t.sent,n=r.value,t.abrupt("return",n);case 8:return t.prev=8,t.t0=t.catch(0),
t.t0 instanceof gr&&t.t0.isEmpty()||console.error('Error getting Publishing Status for page with ID "'.concat(e,'"'),t.t0),t.abrupt("return",void 0);case 12:
case"end":return t.stop()}}),t,null,[[0,8]])})));return function(e){return t.apply(this,arguments)}}(),Vn=function(){var t=Nn(In().mark((function t(e,r){
var n,o,i,a,s;return In().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,Fn(e);case 2:return n=t.sent,t.next=5,Gn(e);case 5:if(o=t.sent,
!Object.prototype.hasOwnProperty.call(n,"jobId")||(null==n?void 0:n.jobId)!==r){t.next=10;break}return(i=n).jobId,a=An(i,On),t.next=10,Mn(e,a);case 10:
if((null==o?void 0:o.jobId)!==r){t.next=14;break}return o.jobId,s=An(o,kn),t.next=14,Rn.setContentProperty(e,f,Cn(Cn({},s),{},{notified:!0}));case 14:case"end":
return t.stop()}}),t)})));return function(e,r){return t.apply(this,arguments)}}(),Un=function(t){return mn({url:"".concat(tn("CHECK_JOB_STATUS",t)),type:"GET",
silent:!0})},qn={};o("flag.close",(function(t){if(qn[t.flagIdentifier]){var e=qn[t.flagIdentifier].onClose;e&&e(t),delete qn[t.flagIdentifier]}})),
o("flag.action",(function(t){if("refresh"===t.actionIdentifier&&AP.navigator.reload(),qn[t.flagIdentifier]){var e=qn[t.flagIdentifier].onAction
;e&&e(Object.assign(t,{close:function(){qn[t.flagIdentifier].flagRef.close(),delete qn[t.flagIdentifier]}}))}}));const Zn=function(t,e,r){
var n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{},o=AP.flag.create({type:t,title:e,body:r,actions:n.actions,close:n.close},(function(t){qn[t]={
onClose:n.onClose,onAction:n.onAction,flagRef:o}}))};r(93891);var Kn={status:v.IDLE,processedTasks:0,totalTasks:0,errors:[],accountId:"",jobType:"",targetSpaceId:""}
;function zn(t){return zn="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},zn(t)}function $n(t,e){var r=Object.keys(t)
;if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(t);e&&(n=n.filter((function(e){return Object.getOwnPropertyDescriptor(t,e).enumerable}))),
r.push.apply(r,n)}return r}function Hn(t){for(var e=1;e<arguments.length;e++){var r=null!=arguments[e]?arguments[e]:{};e%2?$n(Object(r),!0).forEach((function(e){
Yn(t,e,r[e])})):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(r)):$n(Object(r)).forEach((function(e){
Object.defineProperty(t,e,Object.getOwnPropertyDescriptor(r,e))}))}return t}function Yn(t,e,r){return(e=function(t){var e=function(t,e){
if("object"!=zn(t)||!t)return t;var r=t[Symbol.toPrimitive];if(void 0!==r){var n=r.call(t,e||"default");if("object"!=zn(n))return n
;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===e?String:Number)(t)}(t,"string");return"symbol"==zn(e)?e:e+""
}(e))in t?Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}):t[e]=r,t}function Jn(t,e){return function(t){if(Array.isArray(t))return t
}(t)||function(t,e){var r=null==t?null:"undefined"!=typeof Symbol&&t[Symbol.iterator]||t["@@iterator"];if(null!=r){var n,o,i,a,s=[],u=!0,c=!1;try{
if(i=(r=r.call(t)).next,0===e){if(Object(r)!==r)return;u=!1}else for(;!(u=(n=i.call(r)).done)&&(s.push(n.value),s.length!==e);u=!0);}catch(t){c=!0,o=t}finally{try{
if(!u&&null!=r.return&&(a=r.return(),Object(a)!==a))return}finally{if(c)throw o}}return s}}(t,e)||function(t,e){if(t){if("string"==typeof t)return Wn(t,e)
;var r={}.toString.call(t).slice(8,-1);return"Object"===r&&t.constructor&&(r=t.constructor.name),
"Map"===r||"Set"===r?Array.from(t):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?Wn(t,e):void 0}}(t,e)||function(){
throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()}
function Wn(t,e){(null==e||e>t.length)&&(e=t.length);for(var r=0,n=Array(e);r<e;r++)n[r]=t[r];return n}function Qn(){Qn=function(){return e}
;var t,e={},r=Object.prototype,n=r.hasOwnProperty,o=Object.defineProperty||function(t,e,r){t[e]=r.value
},i="function"==typeof Symbol?Symbol:{},a=i.iterator||"@@iterator",s=i.asyncIterator||"@@asyncIterator",u=i.toStringTag||"@@toStringTag";function c(t,e,r){
return Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}),t[e]}try{c({},"")}catch(t){c=function(t,e,r){return t[e]=r}}
function l(t,e,r,n){var i=e&&e.prototype instanceof g?e:g,a=Object.create(i.prototype),s=new T(n||[]);return o(a,"_invoke",{value:O(t,r,s)}),a}function f(t,e,r){try{
return{type:"normal",arg:t.call(e,r)}}catch(t){return{type:"throw",arg:t}}}e.wrap=l;var h="suspendedStart",p="suspendedYield",d="executing",y="completed",v={}
;function g(){}function m(){}function b(){}var w={};c(w,a,(function(){return this}));var _=Object.getPrototypeOf,x=_&&_(_(A([])));x&&x!==r&&n.call(x,a)&&(w=x)
;var P=b.prototype=g.prototype=Object.create(w);function S(t){["next","throw","return"].forEach((function(e){c(t,e,(function(t){return this._invoke(e,t)}))}))}
function E(t,e){function r(o,i,a,s){var u=f(t[o],t,i);if("throw"!==u.type){var c=u.arg,l=c.value
;return l&&"object"==zn(l)&&n.call(l,"__await")?e.resolve(l.__await).then((function(t){r("next",t,a,s)}),(function(t){r("throw",t,a,s)
})):e.resolve(l).then((function(t){c.value=t,a(c)}),(function(t){return r("throw",t,a,s)}))}s(u.arg)}var i;o(this,"_invoke",{value:function(t,n){function o(){
return new e((function(e,o){r(t,n,e,o)}))}return i=i?i.then(o,o):o()}})}function O(e,r,n){var o=h;return function(i,a){
if(o===d)throw Error("Generator is already running");if(o===y){if("throw"===i)throw a;return{value:t,done:!0}}for(n.method=i,n.arg=a;;){var s=n.delegate;if(s){
var u=k(s,n);if(u){if(u===v)continue;return u}}if("next"===n.method)n.sent=n._sent=n.arg;else if("throw"===n.method){if(o===h)throw o=y,n.arg
;n.dispatchException(n.arg)}else"return"===n.method&&n.abrupt("return",n.arg);o=d;var c=f(e,r,n);if("normal"===c.type){if(o=n.done?y:p,c.arg===v)continue;return{
value:c.arg,done:n.done}}"throw"===c.type&&(o=y,n.method="throw",n.arg=c.arg)}}}function k(e,r){var n=r.method,o=e.iterator[n];if(o===t)return r.delegate=null,
"throw"===n&&e.iterator.return&&(r.method="return",r.arg=t,k(e,r),"throw"===r.method)||"return"!==n&&(r.method="throw",
r.arg=new TypeError("The iterator does not provide a '"+n+"' method")),v;var i=f(o,e.iterator,r.arg);if("throw"===i.type)return r.method="throw",r.arg=i.arg,
r.delegate=null,v;var a=i.arg;return a?a.done?(r[e.resultName]=a.value,r.next=e.nextLoc,"return"!==r.method&&(r.method="next",r.arg=t),r.delegate=null,
v):a:(r.method="throw",r.arg=new TypeError("iterator result is not an object"),r.delegate=null,v)}function j(t){var e={tryLoc:t[0]};1 in t&&(e.catchLoc=t[1]),
2 in t&&(e.finallyLoc=t[2],e.afterLoc=t[3]),this.tryEntries.push(e)}function C(t){var e=t.completion||{};e.type="normal",delete e.arg,t.completion=e}function T(t){
this.tryEntries=[{tryLoc:"root"}],t.forEach(j,this),this.reset(!0)}function A(e){if(e||""===e){var r=e[a];if(r)return r.call(e);if("function"==typeof e.next)return e
;if(!isNaN(e.length)){var o=-1,i=function r(){for(;++o<e.length;)if(n.call(e,o))return r.value=e[o],r.done=!1,r;return r.value=t,r.done=!0,r};return i.next=i}}
throw new TypeError(zn(e)+" is not iterable")}return m.prototype=b,o(P,"constructor",{value:b,configurable:!0}),o(b,"constructor",{value:m,configurable:!0}),
m.displayName=c(b,u,"GeneratorFunction"),e.isGeneratorFunction=function(t){var e="function"==typeof t&&t.constructor
;return!!e&&(e===m||"GeneratorFunction"===(e.displayName||e.name))},e.mark=function(t){return Object.setPrototypeOf?Object.setPrototypeOf(t,b):(t.__proto__=b,
c(t,u,"GeneratorFunction")),t.prototype=Object.create(P),t},e.awrap=function(t){return{__await:t}},S(E.prototype),c(E.prototype,s,(function(){return this})),
e.AsyncIterator=E,e.async=function(t,r,n,o,i){void 0===i&&(i=Promise);var a=new E(l(t,r,n,o),i);return e.isGeneratorFunction(r)?a:a.next().then((function(t){
return t.done?t.value:a.next()}))},S(P),c(P,u,"Generator"),c(P,a,(function(){return this})),c(P,"toString",(function(){return"[object Generator]"})),
e.keys=function(t){var e=Object(t),r=[];for(var n in e)r.push(n);return r.reverse(),function t(){for(;r.length;){var n=r.pop();if(n in e)return t.value=n,t.done=!1,t
}return t.done=!0,t}},e.values=A,T.prototype={constructor:T,reset:function(e){if(this.prev=0,this.next=0,this.sent=this._sent=t,this.done=!1,this.delegate=null,
this.method="next",this.arg=t,this.tryEntries.forEach(C),!e)for(var r in this)"t"===r.charAt(0)&&n.call(this,r)&&!isNaN(+r.slice(1))&&(this[r]=t)},stop:function(){
this.done=!0;var t=this.tryEntries[0].completion;if("throw"===t.type)throw t.arg;return this.rval},dispatchException:function(e){if(this.done)throw e;var r=this
;function o(n,o){return s.type="throw",s.arg=e,r.next=n,o&&(r.method="next",r.arg=t),!!o}for(var i=this.tryEntries.length-1;i>=0;--i){
var a=this.tryEntries[i],s=a.completion;if("root"===a.tryLoc)return o("end");if(a.tryLoc<=this.prev){var u=n.call(a,"catchLoc"),c=n.call(a,"finallyLoc");if(u&&c){
if(this.prev<a.catchLoc)return o(a.catchLoc,!0);if(this.prev<a.finallyLoc)return o(a.finallyLoc)}else if(u){if(this.prev<a.catchLoc)return o(a.catchLoc,!0)}else{
if(!c)throw Error("try statement without catch or finally");if(this.prev<a.finallyLoc)return o(a.finallyLoc)}}}},abrupt:function(t,e){
for(var r=this.tryEntries.length-1;r>=0;--r){var o=this.tryEntries[r];if(o.tryLoc<=this.prev&&n.call(o,"finallyLoc")&&this.prev<o.finallyLoc){var i=o;break}}
i&&("break"===t||"continue"===t)&&i.tryLoc<=e&&e<=i.finallyLoc&&(i=null);var a=i?i.completion:{};return a.type=t,a.arg=e,i?(this.method="next",
this.next=i.finallyLoc,v):this.complete(a)},complete:function(t,e){if("throw"===t.type)throw t.arg
;return"break"===t.type||"continue"===t.type?this.next=t.arg:"return"===t.type?(this.rval=this.arg=t.arg,this.method="return",
this.next="end"):"normal"===t.type&&e&&(this.next=e),v},finish:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.finallyLoc===t)return this.complete(r.completion,r.afterLoc),C(r),v}},catch:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.tryLoc===t){var n=r.completion;if("throw"===n.type){var o=n.arg;C(r)}return o}}throw Error("illegal catch attempt")},delegateYield:function(e,r,n){
return this.delegate={iterator:A(e),resultName:r,nextLoc:n},"next"===this.method&&(this.arg=t),v}},e}function Xn(t,e,r,n,o,i,a){try{var s=t[i](a),u=s.value}catch(t){
return void r(t)}s.done?e(u):Promise.resolve(u).then(n,o)}function to(t){return function(){var e=this,r=arguments;return new Promise((function(n,o){
var i=t.apply(e,r);function a(t){Xn(i,n,o,a,s,"next",t)}function s(t){Xn(i,n,o,a,s,"throw",t)}a(void 0)}))}}var eo=0,ro=function(){var t=to(Qn().mark((function t(r){
var n;return Qn().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.next=2,Un(r);case 2:return n=t.sent,i(e,n,!0),t.abrupt("return",n);case 5:case"end":
return t.stop()}}),t)})));return function(e){return t.apply(this,arguments)}}(),no=function(t){return new Promise((function(e,r){setTimeout((function(){
ro(t).then(e).catch(r)}),2500)}))},oo=function(){var t=to(Qn().mark((function t(e){var r;return Qn().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:
return t.prev=0,t.next=3,ro(e);case 3:r=t.sent,eo=0,t.next=16;break;case 7:if(t.prev=7,t.t0=t.catch(0),!(++eo<5)){t.next=14;break}
return t.abrupt("return",new Promise((function(t,r){setTimeout((function(){
console.info('Status check for Job with ID "'.concat(e,'" failed ').concat(eo," time(s), retrying...")),oo(e).then(t).catch(r)}),2500*eo)})));case 14:
throw console.error('Status check for Job with ID "'.concat(e,'" failed for ').concat(eo," time(s)")),t.t0;case 16:if(r.status===v.FINISHED){t.next=22;break}
return t.next=19,no(e);case 19:r=t.sent,t.next=16;break;case 22:return t.abrupt("return",r);case 23:case"end":return t.stop()}}),t,null,[[0,7]])})))
;return function(e){return t.apply(this,arguments)}}();const io=function(t,r,n){var o={refreshPage:"Refresh page",viewPublished:"View published version"}
;(function(t,e,r){return new Promise((function(n,o){oo(e).then(function(){var e=to(Qn().mark((function e(i){var a,s,u,c,l,f,h,p,d,y,v;return Qn().wrap((function(e){
for(;;)switch(e.prev=e.next){case 0:return a=i.errors.find((function(t){return t.contentId===r})),e.prev=1,e.next=4,Fn(r);case 4:if(!(s=e.sent)){e.next=29;break}
if(u=s.targetContentId,c=void 0===u?"":u,a){e.next=25;break}if(!c){e.next=24;break}return l=t.targetSpaceId,f=void 0===l?"":l,e.next=12,Promise.all([Bn(r),Dn(f)])
;case 12:return h=e.sent,p=Jn(h,2),d=p[0],y=p[1],e.next=18,Dn(null==d?void 0:d.spaceId);case 18:return v=e.sent,n({job:i,source:{content:d,space:v,manifest:s},
target:{content:{id:c},space:y}}),e.abrupt("return");case 24:a={contentId:r,errorType:"error",errorMessage:"Could not find target content id in manifest."};case 25:
o({error:a,source:{manifest:s},target:{content:{id:c}}}),e.next=30;break;case 29:o({error:{contentId:r,errorType:"error",
errorMessage:"Could not retrieve content details."}});case 30:e.next=35;break;case 32:e.prev=32,e.t0=e.catch(1),o({error:{contentId:r,errorType:"error",
errorMessage:"Could not retrieve content manifest. ".concat(e.t0.message)}});case 35:case"end":return e.stop()}}),e,null,[[1,32]])})));return function(t){
return e.apply(this,arguments)}}()).catch(function(){var t=to(Qn().mark((function t(n){var o,i;return Qn().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:
o=n.body,i="string"==typeof o?o:o.message,Zn("error",'Could not check status of job with ID  "'.concat(e,'"'),i),Vn(r,e),eo=0;case 5:case"end":return t.stop()}}),t)
})));return function(e){return t.apply(this,arguments)}}())}))})(t,n,r).then((function(t){var e,i,a,s=t.source,u=t.target;Vn(r,n),
Zn("success","Page published",'Page "'.concat(null==s||null===(e=s.content)||void 0===e?void 0:e.title,'" has been successfully published to "').concat(null==u||null===(i=u.space)||void 0===i?void 0:i.name,'"'),{
actions:o,onAction:(a=to(Qn().mark((function t(e){var r;return Qn().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:e.close(),
"refreshPage"===e.actionIdentifier?AP.navigator.reload():AP.navigator.go("contentview",{contentId:null==u||null===(r=u.content)||void 0===r?void 0:r.id});case 2:
case"end":return t.stop()}}),t)}))),function(t){return a.apply(this,arguments)})})})).catch((function(t){var e=t.target,i=t.error;Vn(r,n)
;var a,s=i.errorType,u=void 0===s?"error":s,c="error"===u?"Could not publish page":"Page was published but...",l={};"error"!==u&&(l=Hn(Hn({},l),{},{actions:o,
onAction:(a=to(Qn().mark((function t(r){var n;return Qn().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:r.close(),
"refreshPage"===r.actionIdentifier?AP.navigator.reload():AP.navigator.go("contentview",{contentId:null==e||null===(n=e.content)||void 0===n?void 0:n.id});case 2:
case"end":return t.stop()}}),t)}))),function(t){return a.apply(this,arguments)})})),Zn(u,c,null==i?void 0:i.errorMessage,l)})).finally((function(){
setTimeout((function(){return i(e,Kn,!0)}),3500)}))};const ao=function(){
Zn("info","This Space is setup as a Target Space","Updates you make here may be overwritten next time this space or page is published.")};function so(t){
return so="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(t){return typeof t}:function(t){
return t&&"function"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?"symbol":typeof t},so(t)}function uo(){uo=function(){return e}
;var t,e={},r=Object.prototype,n=r.hasOwnProperty,o=Object.defineProperty||function(t,e,r){t[e]=r.value
},i="function"==typeof Symbol?Symbol:{},a=i.iterator||"@@iterator",s=i.asyncIterator||"@@asyncIterator",u=i.toStringTag||"@@toStringTag";function c(t,e,r){
return Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}),t[e]}try{c({},"")}catch(t){c=function(t,e,r){return t[e]=r}}
function l(t,e,r,n){var i=e&&e.prototype instanceof g?e:g,a=Object.create(i.prototype),s=new T(n||[]);return o(a,"_invoke",{value:O(t,r,s)}),a}function f(t,e,r){try{
return{type:"normal",arg:t.call(e,r)}}catch(t){return{type:"throw",arg:t}}}e.wrap=l;var h="suspendedStart",p="suspendedYield",d="executing",y="completed",v={}
;function g(){}function m(){}function b(){}var w={};c(w,a,(function(){return this}));var _=Object.getPrototypeOf,x=_&&_(_(A([])));x&&x!==r&&n.call(x,a)&&(w=x)
;var P=b.prototype=g.prototype=Object.create(w);function S(t){["next","throw","return"].forEach((function(e){c(t,e,(function(t){return this._invoke(e,t)}))}))}
function E(t,e){function r(o,i,a,s){var u=f(t[o],t,i);if("throw"!==u.type){var c=u.arg,l=c.value
;return l&&"object"==so(l)&&n.call(l,"__await")?e.resolve(l.__await).then((function(t){r("next",t,a,s)}),(function(t){r("throw",t,a,s)
})):e.resolve(l).then((function(t){c.value=t,a(c)}),(function(t){return r("throw",t,a,s)}))}s(u.arg)}var i;o(this,"_invoke",{value:function(t,n){function o(){
return new e((function(e,o){r(t,n,e,o)}))}return i=i?i.then(o,o):o()}})}function O(e,r,n){var o=h;return function(i,a){
if(o===d)throw Error("Generator is already running");if(o===y){if("throw"===i)throw a;return{value:t,done:!0}}for(n.method=i,n.arg=a;;){var s=n.delegate;if(s){
var u=k(s,n);if(u){if(u===v)continue;return u}}if("next"===n.method)n.sent=n._sent=n.arg;else if("throw"===n.method){if(o===h)throw o=y,n.arg
;n.dispatchException(n.arg)}else"return"===n.method&&n.abrupt("return",n.arg);o=d;var c=f(e,r,n);if("normal"===c.type){if(o=n.done?y:p,c.arg===v)continue;return{
value:c.arg,done:n.done}}"throw"===c.type&&(o=y,n.method="throw",n.arg=c.arg)}}}function k(e,r){var n=r.method,o=e.iterator[n];if(o===t)return r.delegate=null,
"throw"===n&&e.iterator.return&&(r.method="return",r.arg=t,k(e,r),"throw"===r.method)||"return"!==n&&(r.method="throw",
r.arg=new TypeError("The iterator does not provide a '"+n+"' method")),v;var i=f(o,e.iterator,r.arg);if("throw"===i.type)return r.method="throw",r.arg=i.arg,
r.delegate=null,v;var a=i.arg;return a?a.done?(r[e.resultName]=a.value,r.next=e.nextLoc,"return"!==r.method&&(r.method="next",r.arg=t),r.delegate=null,
v):a:(r.method="throw",r.arg=new TypeError("iterator result is not an object"),r.delegate=null,v)}function j(t){var e={tryLoc:t[0]};1 in t&&(e.catchLoc=t[1]),
2 in t&&(e.finallyLoc=t[2],e.afterLoc=t[3]),this.tryEntries.push(e)}function C(t){var e=t.completion||{};e.type="normal",delete e.arg,t.completion=e}function T(t){
this.tryEntries=[{tryLoc:"root"}],t.forEach(j,this),this.reset(!0)}function A(e){if(e||""===e){var r=e[a];if(r)return r.call(e);if("function"==typeof e.next)return e
;if(!isNaN(e.length)){var o=-1,i=function r(){for(;++o<e.length;)if(n.call(e,o))return r.value=e[o],r.done=!1,r;return r.value=t,r.done=!0,r};return i.next=i}}
throw new TypeError(so(e)+" is not iterable")}return m.prototype=b,o(P,"constructor",{value:b,configurable:!0}),o(b,"constructor",{value:m,configurable:!0}),
m.displayName=c(b,u,"GeneratorFunction"),e.isGeneratorFunction=function(t){var e="function"==typeof t&&t.constructor
;return!!e&&(e===m||"GeneratorFunction"===(e.displayName||e.name))},e.mark=function(t){return Object.setPrototypeOf?Object.setPrototypeOf(t,b):(t.__proto__=b,
c(t,u,"GeneratorFunction")),t.prototype=Object.create(P),t},e.awrap=function(t){return{__await:t}},S(E.prototype),c(E.prototype,s,(function(){return this})),
e.AsyncIterator=E,e.async=function(t,r,n,o,i){void 0===i&&(i=Promise);var a=new E(l(t,r,n,o),i);return e.isGeneratorFunction(r)?a:a.next().then((function(t){
return t.done?t.value:a.next()}))},S(P),c(P,u,"Generator"),c(P,a,(function(){return this})),c(P,"toString",(function(){return"[object Generator]"})),
e.keys=function(t){var e=Object(t),r=[];for(var n in e)r.push(n);return r.reverse(),function t(){for(;r.length;){var n=r.pop();if(n in e)return t.value=n,t.done=!1,t
}return t.done=!0,t}},e.values=A,T.prototype={constructor:T,reset:function(e){if(this.prev=0,this.next=0,this.sent=this._sent=t,this.done=!1,this.delegate=null,
this.method="next",this.arg=t,this.tryEntries.forEach(C),!e)for(var r in this)"t"===r.charAt(0)&&n.call(this,r)&&!isNaN(+r.slice(1))&&(this[r]=t)},stop:function(){
this.done=!0;var t=this.tryEntries[0].completion;if("throw"===t.type)throw t.arg;return this.rval},dispatchException:function(e){if(this.done)throw e;var r=this
;function o(n,o){return s.type="throw",s.arg=e,r.next=n,o&&(r.method="next",r.arg=t),!!o}for(var i=this.tryEntries.length-1;i>=0;--i){
var a=this.tryEntries[i],s=a.completion;if("root"===a.tryLoc)return o("end");if(a.tryLoc<=this.prev){var u=n.call(a,"catchLoc"),c=n.call(a,"finallyLoc");if(u&&c){
if(this.prev<a.catchLoc)return o(a.catchLoc,!0);if(this.prev<a.finallyLoc)return o(a.finallyLoc)}else if(u){if(this.prev<a.catchLoc)return o(a.catchLoc,!0)}else{
if(!c)throw Error("try statement without catch or finally");if(this.prev<a.finallyLoc)return o(a.finallyLoc)}}}},abrupt:function(t,e){
for(var r=this.tryEntries.length-1;r>=0;--r){var o=this.tryEntries[r];if(o.tryLoc<=this.prev&&n.call(o,"finallyLoc")&&this.prev<o.finallyLoc){var i=o;break}}
i&&("break"===t||"continue"===t)&&i.tryLoc<=e&&e<=i.finallyLoc&&(i=null);var a=i?i.completion:{};return a.type=t,a.arg=e,i?(this.method="next",
this.next=i.finallyLoc,v):this.complete(a)},complete:function(t,e){if("throw"===t.type)throw t.arg
;return"break"===t.type||"continue"===t.type?this.next=t.arg:"return"===t.type?(this.rval=this.arg=t.arg,this.method="return",
this.next="end"):"normal"===t.type&&e&&(this.next=e),v},finish:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.finallyLoc===t)return this.complete(r.completion,r.afterLoc),C(r),v}},catch:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e]
;if(r.tryLoc===t){var n=r.completion;if("throw"===n.type){var o=n.arg;C(r)}return o}}throw Error("illegal catch attempt")},delegateYield:function(e,r,n){
return this.delegate={iterator:A(e),resultName:r,nextLoc:n},"next"===this.method&&(this.arg=t),v}},e}function co(t,e,r,n,o,i,a){try{var s=t[i](a),u=s.value}catch(t){
return void r(t)}s.done?e(u):Promise.resolve(u).then(n,o)}k().then(function(){var e,r=(e=uo().mark((function e(r){var n,i,a,s,u,c,l,f,h
;return uo().wrap((function(e){for(;;)switch(e.prev=e.next){case 0:if(n=r.target,i=r.context,a=i.contentId,s=i.spaceKey){e.next=4;break}return e.abrupt("return")
;case 4:return e.prev=4,e.next=7,Sn(s);case 7:if(!(u=e.sent)||!u.enabled){e.next=19;break}c=u.sourceSpaceId,l=u.targetSpaceId,f=c&&""!==c,h=l&&""!==l,e.t0=n,
e.next="contentcreate"===e.t0||"contentedit"===e.t0?15:"contentview"===e.t0?17:19;break;case 15:return f&&ao(),e.abrupt("break",19);case 17:
return h&&(Fn(a).then((function(t){if(Object.prototype.hasOwnProperty.call(t,"jobId")){var e=t.jobId;io(u,a,void 0===e?"":e)}else Gn(a).then((function(t){
t&&t.jobId&&!t.notified&&io(u,a,t.jobId)}))})),o(t,(function(t){t&&t.jobId&&io(u,a,t.jobId)}),!0)),e.abrupt("break",19);case 19:e.next=24;break;case 21:e.prev=21,
e.t1=e.catch(4),console.error('[startup] Couldn´t get cpc-config for space with key "'.concat(s,'"'),e.t1);case 24:case"end":return e.stop()}}),e,null,[[4,21]])})),
function(){var t=this,r=arguments;return new Promise((function(n,o){var i=e.apply(t,r);function a(t){co(i,n,o,a,s,"next",t)}function s(t){co(i,n,o,a,s,"throw",t)}
a(void 0)}))});return function(t){return r.apply(this,arguments)}}())})()})();