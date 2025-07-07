function e(e,t,r,a){Object.defineProperty(e,t,{get:r,set:a,enumerable:!0,configurable:!0})}function t(e){return e&&e.__esModule?e.default:e}var r=globalThis,a={},o={},n=r.parcelRequired477;null==n&&(n=function(e){if(e in a)return a[e].exports;if(e in o){var t=o[e];delete o[e];var r={id:e,exports:{}};return a[e]=r,t.call(r.exports,r,r.exports),r.exports}var n=Error("Cannot find module '"+e+"'");throw n.code="MODULE_NOT_FOUND",n},n.register=function(e,t){o[e]=t},r.parcelRequired477=n);var i=n.register;i("jvYFk",function(t,r){e(t.exports,"PanelName",()=>o);var a,o=((a={}).CommentsPanel="commentsPanel",a.DetailsPanel="detailsPanel",a.WorkflowsPanel="workflowsPanel",a.LoomScriptPanel="loomScriptPanel",a)}),i("ip8TF",function(t,r){e(t.exports,"useDataRetentionDetailsGetDetailsQuery",()=>o),e(t.exports,"useDataRetentionDetails",()=>i);var a=n("j1Ss3");let o=(0,n("d2LG0").default)`query useDataRetentionDetailsGetDetailsQuery($cloudId:ID!){confluence_dataLifecycleManagementPolicy(cloudId:$cloudId){dataRetentionPolicyDetailsForWorkspace{policyEnabledStatus disabledOnDate{value}}}}`,i=()=>{let{cloudId:e}=(0,n("bQm3c").useSessionData)(),{data:t,error:r,loading:i}=(0,a.useQuery)(o,{skip:!e||!(0,n("9wGTI").fg)("dlp-dlm-data-retention-policy"),variables:{cloudId:e}});r&&(0,n("7Sm4c").markErrorAsHandled)(r);let{dataRetentionPolicyDetailsForWorkspace:s}=t?.confluence_dataLifecycleManagementPolicy??{},{policyEnabledStatus:d,disabledOnDate:l}=s??{},{value:c}=l??{},p=d===n("3eH3b").ConfluencePolicyEnabledStatus.ENABLED,u=!p&&c?parseInt(c,10):null;return{isDataRetentionPolicyEnabled:p,disabledOnEpoch:u,error:r,loading:i}}}),i("3eH3b",function(t,r){e(t.exports,"ConfluencePolicyEnabledStatus",()=>o);var a,o=((a={}).DISABLED="DISABLED",a.ENABLED="ENABLED",a.UNDETERMINED_DUE_TO_INTERNAL_ERROR="UNDETERMINED_DUE_TO_INTERNAL_ERROR",a)}),i("14FKK",function(t,r){e(t.exports,"parseContent",()=>i);let a=e=>{let t=["annotation","link"];return!e.marks||!e.marks.some(e=>t.includes(e.type))},o=e=>!["codeBlock"].includes(e.type),n=(e,t)=>{if(o(e)&&e.content&&e.content.length>0)for(let r of e.content)n(r,t);"text"===e.type&&a(e)&&t.push(e)},i=e=>{let t=[];return n(e,t),t.map(e=>e.text).join(",")}}),i("jWDKZ",function(t,r){e(t.exports,"useTextHighlighterClickNative",()=>o),e(t.exports,"useTextHighlighterClick",()=>i);var a=n("gwFzn");let o=({singleClickCallback:e,doubleClickCallback:t,delay:r=250})=>{let[o,n]=(0,a.useState)({e:null});return(0,a.useEffect)(()=>{if(!o.e)return;let a=setTimeout(()=>{o.e?.detail===1?e(o.e):o.e?.detail&&o.e.detail>1&&t(o.e),n({e:null})},r);return()=>clearTimeout(a)},[o,e,t,r]),e=>{n({e:e})}},i=({singleClickCallback:e,doubleClickCallback:t,delay:r=250})=>{let[o,n]=(0,a.useState)({click:0,e:null});return(0,a.useEffect)(()=>{if(!o.e)return;let a=setTimeout(()=>{1===o.click&&e(o.e),n({e:null,click:0})},r);return 2===o.click&&t(o.e),()=>clearTimeout(a)},[o,e,t,r]),e=>{n({click:o.click+1,e:e})}}}),i("5Mdl1",function(r,a){e(r.exports,"CrossIconCloseButton",()=>i);var o=n("gwFzn");let i=({onClose:e,source:r})=>{let{createAnalyticsEvent:a}=(0,n("inPa6").useAnalyticsEvents)(),i=(0,o.useCallback)(()=>{a({type:"sendUIEvent",data:{action:"clicked",actionSubject:"button",actionSubjectId:"dismiss",source:r}}).fire(),e()},[e,a,r]);return t(o).createElement(n("1qfLF").default,{icon:e=>t(o).createElement(t(n("hmuev")),{...e,color:"var(--ds-icon-inverse, #FFFFFF)"}),appearance:"subtle",label:t(o).createElement(n("4jR19").default,s.dismiss),onClick:i})},s=(0,n("2nPZH").defineMessages)({dismiss:{id:"modernize-changeboarding.cross-icon-close-button.dismiss",defaultMessage:"Dismiss"}})}),i("7wVkn",function(t,r){e(t.exports,"DefinitionPopup",()=>d);var a=n("7UHDa"),o=n("gwFzn");let i=(0,o.forwardRef)(({children:e,...t},r)=>(0,a.jsx)("span",{...t,ref:r,className:(0,n("35pXk").default)(["_1pbyowjs"]),children:e})),s=(0,o.lazy)(()=>n("goMcG").then(e=>({default:e.DefinitionPopupContent})));function d({onClose:e,triggerPosition:t,onLoad:r,...d}){let l={height:`${t.height}px`,left:`${t.left}px`,top:`${t.top}px`,width:`${t.width}px`};return(0,a.jsx)(n("lGgRw").default,{content:({update:t})=>(0,a.jsx)(o.Suspense,{fallback:null,children:(0,a.jsx)(s,{...d,onClose:e,onLoad:()=>{r?.(),t()}})}),onClose:e,placement:"bottom-start",popupComponent:i,trigger:e=>(0,a.jsx)("span",{...e,style:l,"data-testid":"definition-popup-trigger",className:(0,n("35pXk").default)(["_tzy4idpf _kqswstnw _lcxvglyw _bfhk18uv _1ltvidpf _94n5idpf"])}),isOpen:!0})}}),i("goMcG",function(e,t){let r=n("lhnSv")(5);e.exports=Promise.all([r("gLxW3"),r("d1vfP"),r("eUXnF"),r("kenYr"),r("lvdR8"),r("ej4rO"),r("iDB1L"),r("6Nh0d"),r("hl547"),r("eEyVs"),r("8ZOct"),r("iHjI2"),r("3RGYS"),r("b6fLX"),r("GUXOU"),r("lADvr"),r("dhs92"),r("7a4au"),r("b35rK"),r("baPD8"),r("jCu7l"),r("1ZAFx"),r("ftJgg"),r("19uFC"),r("5uN9h"),r("1d7Ag"),r("7lGj4"),r("cUIjD"),r("61fF8"),r("eb06U"),r("dUEf9"),r("7jH9e"),r("khwsQ"),r("1slQX"),r("cNo2P"),r("eQxPG"),r("dTsOE"),r("6wr18"),r("kjZZD"),r("6wUwl"),r("Wowvf"),r("g9CVe"),r("c6MKV"),r("6qah4"),r("aZinD"),r("dAH4n"),r("iPi66"),r("aikvX"),r("jrKPL"),r("ffEVr"),r("hhss7"),r("6Z8WE"),r("6Yu8N"),r("hsF0G"),r("7EorR"),r("77ceh")]).then(()=>n("bA47i"))}),i("lhnSv",function(e,t){e.exports=e=>t=>import(n("9WHwv").shardUrl(n("fzRTW").resolve(t),e))}),i("9WHwv",function(t,r){var a,o;e(t.exports,"shardUrl",()=>a,e=>a=e),e(t.exports,"domainShardingKey",()=>o,e=>o=e);let n="__ATLASPACK_ENABLE_DOMAIN_SHARDS",i=/-\d+$/;function s(e){if(!i.test(e))return e;let t=e.lastIndexOf("-");return e.slice(0,t)}a=function(e,t){var r;let a,o,i,d;return globalThis[n]?(r=function(e){let t=e.lastIndexOf("/");if(-1===t||t===e.length-1)throw Error("Expected an absolute URL with a file name, unable to apply sharding.");return e.slice(t+1)}((a=new URL(e)).pathname),o=t+1,(i=r.split("").reduce((e,t)=>{let r=(e<<o)-e+t.charCodeAt(0);return r&r},0)%o)<0&&(i+=o),d=i,a.hostname=function(e,t){let r=e.indexOf("."),a=0===t?"":`-${t-1}`;if(-1===r)return`${s(e)}${a}`;let o=s(e.slice(0,r));return`${o}${a}${e.slice(r)}`}(a.hostname,d),a.toString()):e},o=n}),i("fzRTW",function(t,r){e(t.exports,"register",()=>a,e=>a=e),e(t.exports,"resolve",()=>o,e=>o=e);var a,o,n=new Map;a=function(e,t){for(var r=0;r<t.length-1;r+=2)n.set(t[r],{baseUrl:e,path:t[r+1]})},o=function(e){var t=n.get(e);if(null==t)throw Error("Could not resolve bundle with id "+e);return new URL(t.path,t.baseUrl).toString()}}),i("dLvRS",function(r,a){e(r.exports,"EditorCardProvider",()=>N),e(r.exports,"editorCardProvider",()=>L);var o=n("7P7n4");let i=e=>e.match(/^https:\/\/.*?\/jira\/software\/(c\/)?projects\/[^\/]+?\/boards\/.*?\/(timeline|roadmap)\/?/),s=e=>e.match(/^https:\/\/.*?\/jira\/polaris\/projects\/[^\/]+?\/ideas\/view\/\d+$|^https:\/\/.*?\/secure\/JiraProductDiscoveryAnonymous\.jspa\?hash=\w+|^https:\/\/.*?\/jira\/polaris\/share\/\w+|^https:\/\/.*?\/jira\/discovery\/share\/views\/[\w-]+(\?selectedIssue=[\w-]+&issueViewLayout=sidebar&issueViewSection=[\w-]+)?$/),d=e=>e.match(/^https:\/\/.*?\/jira\/core\/projects\/[^\/]+?\/(timeline|calendar|list|board|summary|(form\/[^\/]+?))\/?/),l=e=>e.match(/^https:\/\/.*?\/jira\/software\/(c\/)?projects\/[^\/]+?\/list\/?/),c=e=>e.match(/^https:\/\/(.*?\.)?giphy\.com\/(gifs|media|clips)\//),p=e=>e.match(/^https:\/\/[^/]+\/jira\/(core|software(\/c)?|servicedesk)\/projects\/\w+\/forms\/form\/direct\/\d+\/\d+.*$/),u=e=>e.match(RegExp("\\/wiki\\/spaces\\/?.*\\/whiteboard\\/(?<resourceId>\\d+)(\\?\\/)?"))||e.match(RegExp("\\/wiki\\/spaces\\/?.*\\/whiteboard\\/(?<resourceId>[0-9a-fA-F]{8}\\b-[0-9a-fA-F]{4}\\b-[0-9a-fA-F]{4}\\b-[0-9a-fA-F]{4}\\b-[0-9a-fA-F]{12})(\\?\\/)?")),m=e=>e.match(/\/wiki\/spaces\/~?[\d\w]+\/database\/\d+(\?.*)?$/),h=e=>e.match(/^https:\/\/(.*?\.)?(youtube\..*?\/(watch\?|v\/|shorts\/)|youtu\.be)/),g=e=>e.match(RegExp("^https:\\/\\/(.*?\\.)?(loom\\..*?\\/(share|embed))\\/([a-zA-Z0-9-]*-)?(?<videoId>[a-f0-9]{32})")),b=e=>e.match(/^https:\/\/.*?\/jira\/dashboards\/[0-9]+.*/),f=e=>e.match(/https:\/\/.*?\/jira\/software\/(c\/)?projects\/[^\/]+?\/boards\/\d\/backlog\??.*/),x=e=>e.match(/https:\/\/.*?\/jira\/software\/(c\/)?projects\/[^\/]+?\/boards\/\d\??.*/),v=e=>e.match(RegExp("https:\\/\\/.*?\\/jira\\/plans\\/(?<resourceId>\\d+)"))&&(0,n("dh538").fg)("plan_smart_link_base_url")||e.match(RegExp("https:\\/\\/.*?\\/jira\\/plans\\/(?<resourceId>\\d+)\\/scenarios\\/(?<resourceContext>\\d+)\\/(timeline|summary|calendar|program\\/\\d+|dependencies)\\/?")),y=e=>e.match(/https:\/\/.*?\/projects\/[^\/]+?\/versions\/\d+\/tab\/release-report-all-issues/),E=e=>e.match(/https:\/\/.*?\/jira\/software\/(c\/)?projects\/[^\/]+?\/form\/\d\??.*/),S=e=>e.match(/^https:\/\/.*?\/jira\/software\/(c\/)?projects\/[^\/]+?\/summary/),C=e=>e.match(/^https:\/\/.*?\/people\/agent\/.+$/),k=e=>e.match(/^https:\/\/customer\.atlassian\.com\/.*$/),T=e=>e.match(RegExp("\\/wiki\\/spaces\\/(?<resourceContext>[^\\/]+)\\/calendars\\/(?<resourceId>[a-zA-Z0-9-]+)")),w=e=>e.match(/^https:\/\/.*?\/jira\/software|core\/(c\/)?projects\/[^\/]+?\/issues\/?/),_=e=>/\/browse\/((?:\w+)-(?:\d+))/i.test(e);class N{async batchProviders(e){let t=await this.fetchProvidersData();return e.map(()=>t)}async checkLinkResolved(e){try{let t=await this.cardClient.fetchData(e);if("not_found"!==(0,n("btw9C").getStatus)(t))return!0}catch(e){return!1}}async fetchDataForResource(e){try{let t=await this.cardClient.fetchData(e);if("not_found"!==(0,n("btw9C").getStatus)(t))return t}catch(e){return}}extractAriFromData(e){if(e.data&&"atlassian:ari"in e.data)return e.data["atlassian:ari"]}async fetchProvidersData(){let e=`${this.resolverUrl}/providers`,t=await n("6pra5").request("post",e,void 0,this.requestHeaders);return{patterns:t.providers.reduce((e,t)=>e.concat(t.patterns),[]),userPreferences:t.userPreferences}}async loadProviderData(){try{this.providersData=await this.providersLoader.load("providersData")}catch(e){console.error("failed to fetch /providers",e),this.providersLoader.clear("providerData");return}}async findPattern(e){return!!await this.findPatternData(e)||!!await this.checkLinkResolved(e)}doesUrlMatchPath(e,t){let r=new RegExp(/^[a-zA-Z0-9]/).test(e)?"(^|[^a-zA-Z0-9])":"",a=new RegExp(/[a-zA-Z0-9]$/).test(e)?"($|[^a-zA-Z0-9])":"",o=e.replace(/[-\/\\^$*+?.()|[\]{}]/g,"\\$&");return RegExp(`${r}${o}${a}`).test(t)}async findUserPreference(e){this.providersData||await this.loadProviderData();let t=this.providersData?.userPreferences;if(t){let{defaultAppearance:r,appearances:a}=t,o=a.filter(({urlSegment:t})=>this.doesUrlMatchPath(t,e));if(o.length>0)return o.reduce((e,t)=>e.urlSegment.length>t.urlSegment.length?e:t).appearance;if("inline"!==r)return r}}async findPatternData(e){return this.providersData||await this.loadProviderData(),this.providersData?.patterns.find(t=>e.match(t.source))}getHardCodedAppearance(e){let t,r,a,o;let _=v(e);if((0,n("dh538").fg)("smartlink_jira_software_form")&&(t=E(e)),this.getExperimentValue("jsw-summary-page-embed-smart-link-experiment","isEnabled",!1)&&(r=S(e)),(0,n("dh538").fg)("tc_smart_link_embed_view")&&(a=T(e)),this.getExperimentValue("jsc_nin_smart_link","isEnabled",!1)&&(o=w(e)),i(e)||s(e)||d(e)||l(e)||c(e)||p(e)||u(e)||m(e)||h(e)||g(e)||b(e)||f(e)||x(e)||C(e)||y(e)||_||t||r||k(e)||a||o)return"embed"}async canBeResolvedAsEmbed(e){try{let t=await this.cardClient.fetchData(e);if(!t||"resolved"!==(0,n("btw9C").getStatus)(t))return!1;return!!(0,n("79vw2").extractSmartLinkEmbed)(t)}catch(e){return!1}}async getDatasourceFromResolveResponse(e){try{let t=await this.cardClient.fetchData(e),r=t&&t.datasources||[];if(r.length>0)return r[0]}catch(e){return}}isLocalUrl(e){return new URL(e).origin===this.baseUrl}async resolve(e,t,r,a){try{if(!0===r)return this.transformer.toSmartlinkAdf(e,t);let o=this.getHardCodedAppearance(e),[i,s]=await Promise.all([this.findPatternData(e),this.findUserPreference(e)]);if((0,n("dh538").fg)("issue-link-suggestions-in-comments")&&_(e)&&this.isLocalUrl(e)){let t=await this.fetchDataForResource(e);if(t){let r=this.extractAriFromData(t);r&&this.onResolve?.(e,r)}}if(!1===r&&"url"===s)return Promise.reject(void 0);if(i||await this.checkLinkResolved(e)){let n=i?.defaultView,d=void 0===r?o||t:s||(a||void 0===a)&&o||n||t;d!==s||"embed"!==s||await this.canBeResolvedAsEmbed(e)||(d="inline");let l=await this.getDatasourceFromResolveResponse(e);if(l){let{id:t,parameters:r}=l;return this.transformer.toDatasourceAdf({id:t,parameters:r,views:[{type:"table"}]},e)}return this.transformer.toSmartlinkAdf(e,d)}}catch(t){console.warn(`Error when trying to check Smart Card url "${e}"${t instanceof Error?` - ${t.name} ${t.message}`:""}`,t)}return Promise.reject(void 0)}constructor(e,r,a,i){this.baseUrl=void 0,this.resolverUrl=void 0,this.providersData=void 0,this.requestHeaders=void 0,this.transformer=void 0,this.providersLoader=void 0,this.cardClient=void 0,this.onResolve=void 0,this.getExperimentValue=(e,t,r)=>{try{return(0,n("c6GJD").default).getExperimentValue(e,t,r)}catch{return r}},this.baseUrl=r||(0,n("dDhJe").getBaseUrl)(e),this.resolverUrl=(0,n("dDhJe").getResolverUrl)(e,r),this.transformer=new(n("1SiSh")).Transformer,this.onResolve=i,this.requestHeaders={Origin:this.baseUrl},this.providersLoader=new(t(o))(e=>this.batchProviders(e),{batchScheduleFn:e=>setTimeout(e,50)}),this.cardClient=new(n("k00oi")).default(e,r),a&&this.cardClient.setProduct(a)}}let L=new N}),i("79vw2",function(t,r){e(t.exports,"extractSmartLinkTitle",()=>a),e(t.exports,"extractSmartLinkUrl",()=>o),e(t.exports,"extractSmartLinkAri",()=>i),e(t.exports,"extractSmartLinkEmbed",()=>s),e(t.exports,"extractSmartLinkProvider",()=>d),e(t.exports,"extractSmartLinkCreatedOn",()=>l),e(t.exports,"extractSmartLinkModifiedOn",()=>c),e(t.exports,"extractSmartLinkCreatedBy",()=>p),e(t.exports,"extractSmartLinkAuthorGroup",()=>u),e(t.exports,"extractSmartLinkModifiedBy",()=>m),e(t.exports,"extractSmartLinkDownloadUrl",()=>h);let a=(e,t)=>(0,n("dh538").fg)("smart_links_noun_support")&&(0,n("lyclm").isEntityPresent)(e)?n("lyclm").extractEntity(e)?.displayName:(0,n("hUifo").extractTitle)(e?.data,t),o=e=>(0,n("dh538").fg)("smart_links_noun_support")&&(0,n("lyclm").isEntityPresent)(e)?n("lyclm").extractEntity(e)?.url:(0,n("l6lJr").extractLink)(e?.data),i=e=>{if((0,n("dh538").fg)("smart_links_noun_support")&&(0,n("lyclm").isEntityPresent)(e))return n("lyclm").extractEntity(e)?.ari||n("lyclm").extractEntity(e)?.thirdPartyAri;let t=e?.data;return(0,n("99WQy").extractAri)(t)},s=(e,t)=>{if((0,n("dh538").fg)("smart_links_noun_support")&&(0,n("lyclm").isEntityPresent)(e)){let t=(0,n("lyclm").extractEntityEmbedUrl)(e);return t?{src:t}:void 0}return(0,n("9JHBV").extractPreview)(e?.data,"web",t)},d=e=>(0,n("dh538").fg)("smart_links_noun_support")&&(0,n("lyclm").isEntityPresent)(e)?(0,n("lyclm").extractEntityProvider)(e):e?.data&&(0,n("ccQw1").extractProvider)(e?.data),l=e=>(0,n("dh538").fg)("smart_links_noun_support")&&(0,n("lyclm").isEntityPresent)(e)?n("lyclm").extractEntity(e)?.createdAt:e?.data&&(0,n("7MMjM").extractDateCreated)(e.data),c=e=>(0,n("dh538").fg)("smart_links_noun_support")&&(0,n("lyclm").isEntityPresent)(e)?n("lyclm").extractEntity(e)?.lastUpdatedAt:e?.data&&(0,n("dsdUb").extractDateUpdated)(e.data),p=e=>{if(!e||!e.data)return;if((0,n("dh538").fg)("smart_links_noun_support")&&(0,n("lyclm").isEntityPresent)(e))return n("lyclm").extractEntity(e)?.createdBy?.displayName;let t=(0,n("9WUug").extractPersonCreatedBy)(e.data);return t?.length?t[0].name:void 0},u=e=>{if(e&&e.data){if((0,n("dh538").fg)("smart_links_noun_support")&&(0,n("lyclm").isEntityPresent)(e)){let t=(0,n("lyclm").extractEntity)(e),r=t?.owners;if(r)return r.map(e=>({name:e.displayName,src:e.picture})).filter(e=>!!e)}return(0,n("9WUug").extractPersonCreatedBy)(e.data)}},m=e=>{if(!e||!e.data)return;if((0,n("dh538").fg)("smart_links_noun_support")&&(0,n("lyclm").isEntityPresent)(e))return n("lyclm").extractEntity(e)?.lastUpdatedBy?.displayName;let t=(0,n("4sK6R").extractPersonUpdatedBy)(e.data);return t?t.name:void 0},h=e=>{if((0,n("dh538").fg)("smart_links_noun_support")&&(0,n("lyclm").isEntityPresent)(e)){let t=(0,n("lyclm").extractEntity)(e);return t&&"exportLinks"in t&&Array.isArray(t.exportLinks)&&t.exportLinks.length>0?t?.exportLinks?.[0].url:void 0}return e?.data?.["atlassian:downloadUrl"]}}),i("99WQy",function(t,r){e(t.exports,"extractAri",()=>a);let a=e=>{if(e["atlassian:ari"])return e["atlassian:ari"]}}),i("7MMjM",function(t,r){e(t.exports,"extractDateCreated",()=>a);let a=e=>{if(e["schema:dateCreated"])return e["schema:dateCreated"]}}),i("dsdUb",function(t,r){e(t.exports,"extractDateUpdated",()=>a);let a=e=>{if(e.updated)return e.updated}}),i("l6lJr",function(t,r){e(t.exports,"extractLink",()=>a);let a=e=>{let t=e?.url;if(t)return"string"==typeof t?t:(0,n("kzBLz").extractUrlFromLinkJsonLd)(t)}}),i("kzBLz",function(t,r){e(t.exports,"extractUrlFromLinkJsonLd",()=>a);let a=e=>"string"==typeof e?e:Array.isArray(e)?e.length>0?a(e[0]):void 0:e.href}),i("9WUug",function(t,r){e(t.exports,"extractPersonCreatedBy",()=>a);let a=e=>{let t=e.attributedTo;if(t){if(Array.isArray(t))return t.map(n("kzSaQ").extractPersonFromJsonLd).filter(e=>!!e);{let e=(0,n("kzSaQ").extractPersonFromJsonLd)(t);if(e)return[e]}}}}),i("kzSaQ",function(t,r){e(t.exports,"extractPersonFromJsonLd",()=>a);let a=e=>{if("string"==typeof e)throw Error("Link.person needs to be an object.");if("Link"===e["@type"]){if(e.name)return{name:e.name}}else if(e.name)return{name:e.name,src:e.icon&&(0,n("8hlRK").extractUrlFromIconJsonLd)(e.icon)}}}),i("8hlRK",function(t,r){e(t.exports,"extractUrlFromIconJsonLd",()=>a);let a=e=>"string"==typeof e?e:"Link"===e["@type"]?(0,n("kzBLz").extractUrlFromLinkJsonLd)(e):e.url?(0,n("kzBLz").extractUrlFromLinkJsonLd)(e.url):void 0}),i("4sK6R",function(t,r){e(t.exports,"extractPersonUpdatedBy",()=>a);let a=e=>{let t=e["atlassian:updatedBy"];if(t)return(0,n("kzSaQ").extractPersonFromJsonLd)(t)}}),i("ccQw1",function(t,r){e(t.exports,"extractProvider",()=>o),e(t.exports,"extractProviderIcon",()=>i),e(t.exports,"isConfluenceGenerator",()=>d);var a=n("7UHDa");n("gwFzn");let o=e=>{let t=e.generator;if(t){if("string"==typeof t)throw Error("Link.generator requires a name and icon.");if("Link"===t["@type"]){if(t.name)return{text:t.name}}else if(t.name){let e=t["@id"];return{text:t.name,icon:i(t.icon,e),id:e,image:s(t.image)}}}},i=(e,t)=>{if(t){if(t===n("3fvfu").CONFLUENCE_GENERATOR_ID)return(0,a.jsx)(n("lAFHW").ConfluenceIcon,{appearance:"brand",size:"xxsmall"});if(t===n("3fvfu").JIRA_GENERATOR_ID)return(0,a.jsx)(n("lAFHW").JiraIcon,{appearance:"brand",size:"xxsmall"})}if(e)return(0,n("8hlRK").extractUrlFromIconJsonLd)(e)},s=e=>{if(e){if("string"==typeof e)return e;if("Link"===e["@type"])return(0,n("kzBLz").extractUrlFromLinkJsonLd)(e);if("Image"===e["@type"]&&e.url)return(0,n("kzBLz").extractUrlFromLinkJsonLd)(e.url)}},d=e=>e===n("3fvfu").CONFLUENCE_GENERATOR_ID}),i("3fvfu",function(t,r){e(t.exports,"CONFLUENCE_GENERATOR_ID",()=>a),e(t.exports,"JIRA_GENERATOR_ID",()=>o);let a="https://www.atlassian.com/#Confluence",o="https://www.atlassian.com/#Jira"}),i("hUifo",function(t,r){e(t.exports,"extractTitle",()=>a);let a=(e,t)=>{if(!e)return;let r=e.name?.replace(/[\r\n]+/g,""),a=e["@id"]||"",o=(0,n("2LN0V").extractContext)(e),i=(0,n("aliCf").extractType)(e);if(o&&o.type&&o.type.includes("atlassian:SourceCodeRepository")&&i){let t=o.name&&`${o.name}: `||"";if(i.includes("atlassian:SourceCodeCommit")){let[,e]=a.split(":");return t+(e&&`${e.substring(0,8)} `||"")+r}if(i.includes("atlassian:SourceCodePullRequest")){let a=e["atlassian:internalId"];return t+(a&&`#${a} `||"")+r}if(i.includes("atlassian:SourceCodeReference")||i.includes("schema:DigitalDocument"))return t+r}if(t){let e=RegExp(" \\| :~:text=.*","g");return r?.replace(e,"")}return r}}),i("2LN0V",function(t,r){e(t.exports,"extractContext",()=>a);let a=e=>{let t=e.context;if(t){if("string"==typeof t)return{name:t};if("Link"===t["@type"]){if(t.name)return{name:t.name}}else if(t.name)return{name:t.name,icon:t.icon&&(0,n("8hlRK").extractUrlFromIconJsonLd)(t.icon),type:(0,n("aliCf").extractType)(t)}}}}),i("aliCf",function(t,r){e(t.exports,"extractType",()=>a);let a=e=>{let t=e["@type"];if(t)return Array.isArray(e["@type"])?t:[t]}}),i("9JHBV",function(t,r){e(t.exports,"extractPreview",()=>a);let a=(e,t,r)=>{let a=e?.preview,o=(0,n("lmIyd").extractPlatformIsSupported)(a,t);if(a&&o){if("string"==typeof a)return{src:a};if("Link"===a["@type"]&&"interactiveHref"===r&&a.interactiveHref)return{src:a.interactiveHref,aspectRatio:a["atlassian:aspectRatio"]};if("Link"===a["@type"])return{src:(0,n("kzBLz").extractUrlFromLinkJsonLd)(a),aspectRatio:a["atlassian:aspectRatio"]};if(a.url||a.href)return"interactiveHref"===r&&a.interactiveHref?{src:a.interactiveHref,aspectRatio:a["atlassian:aspectRatio"]}:{src:(0,n("kzBLz").extractUrlFromLinkJsonLd)(a.url||a.href),aspectRatio:a["atlassian:aspectRatio"]};if(a.content)return{content:a.content}}}}),i("lmIyd",function(t,r){e(t.exports,"extractPlatformIsSupported",()=>a);let a=(e,t)=>{if(e){if("string"==typeof e)return!0;{let r=e["atlassian:supportedPlatforms"];if(r){let e="web"===t;return e&&r.includes("web")||!e&&r.includes("mobile")}return!0}}return!1}}),i("lyclm",function(t,r){e(t.exports,"extractEntity",()=>o),e(t.exports,"isEntityPresent",()=>i),e(t.exports,"extractEntityEmbedUrl",()=>s),e(t.exports,"extractEntityProvider",()=>d),e(t.exports,"extractEntityIcon",()=>l);var a=n("7UHDa");n("gwFzn");let o=e=>(0,n("dh538").fg)("smart_links_noun_support")?e?.entityData:void 0,i=e=>!!o(e),s=e=>{let t=o(e);return t&&"liveEmbedUrl"in t&&"string"==typeof t?.liveEmbedUrl?t?.liveEmbedUrl:void 0},d=e=>{let t;if(!e?.meta?.generator)return;let{icon:r,id:o,image:i,name:s}=e.meta.generator;if(!s||!r)throw Error("Link.generator requires a name and icon.");switch(o){case n("3fvfu").CONFLUENCE_GENERATOR_ID:t=(0,a.jsx)(n("lAFHW").ConfluenceIcon,{appearance:"brand",size:"xxsmall"});break;case n("3fvfu").JIRA_GENERATOR_ID:t=(0,a.jsx)(n("lAFHW").JiraIcon,{appearance:"brand",size:"xxsmall"});break;default:t=r.url}return{text:s,icon:t,id:o,image:i||r.url}},l=e=>{let t;let r=o(e);return r&&(t="iconUrl"in r&&"string"==typeof r?.iconUrl?r.iconUrl:(0,n("dh538").fg)("smart_links_noun_support")?e?.meta.generator?.icon?.url:void 0),{url:t,label:r?.displayName}}}),i("dDhJe",function(t,r){e(t.exports,"getBaseUrl",()=>s),e(t.exports,"getResolverUrl",()=>d);let a="https://api-private.dev.atlassian.com",o="https://pug.jira-dev.com/gateway/api",n="https://api-private.atlassian.com",i={dev:a,development:a,stg:o,staging:o,prd:n,prod:n,production:n},s=e=>e?e in i?i[e]:n:void 0!==window.location?window.location.origin:"",d=(e,t)=>{if(!e&&!t)return"/gateway/api/object-resolver";{let r=t||s(e);return`${r}/object-resolver`}}}),i("btw9C",function(t,r){e(t.exports,"getStatus",()=>o);let a=e=>{let t=e.requestAccess?.accessType;return t&&"ACCESS_EXISTS"!==t?"forbidden":"not_found"},o=({meta:e})=>{let{access:t,visibility:r}=e;switch(t){case"forbidden":if("not_found"===r)return a(e);return"forbidden";case"unauthorized":return"unauthorized";default:return"resolved"}}}),i("1SiSh",function(t,r){e(t.exports,"Transformer",()=>a);class a{buildInlineAdf(e){return{type:"inlineCard",attrs:{url:e}}}buildBlockAdf(e){return{type:"blockCard",attrs:{url:e}}}buildEmbedAdf(e){return{type:"embedCard",attrs:{url:e,layout:"wide"}}}buildDatasourceAdf(e,t){return{type:"blockCard",attrs:{url:t,datasource:e}}}toSmartlinkAdf(e,t){switch(t){case"inline":return this.buildInlineAdf(e);case"block":return this.buildBlockAdf(e);case"embed":return this.buildEmbedAdf(e)}}toDatasourceAdf(e,t){return this.buildDatasourceAdf(e,t)}}}),i("k00oi",function(r,a){e(r.exports,"default",()=>l);var o=n("7P7n4"),i=n("frzlB"),s=n("hSrtD");let d=new(n("aoOGA")).LRUMap(100);class l{setProduct(e){this.product=e}createLoader(){let e=t(s)({limit:1,interval:250})(this.batchResolve);return new(t(o))(t=>e(t),{maxBatchSize:50,cache:!1})}getLoader(e){return this.loadersByDomain[e]||(this.loadersByDomain[e]=this.createLoader()),this.loadersByDomain[e]}async resolveUrl(e,t=!1){let r,a;let o=new URL(e).hostname,i=this.getLoader(o);(r=d.get(e))&&!t||(r=i.load(e),d.set(e,r));try{a=await r}catch(t){throw d.delete(e),t}return(0,n("97i3I").isSuccessfulResponse)(a)&&"resolved"===(0,n("btw9C").getStatus)(a.body)||d.delete(e),a}async prefetchData(e){let r=await this.resolveUrl(e,!1);if((0,n("97i3I").isSuccessfulResponse)(r))return r.body;try{return(await t(i)(async()=>{if(this.resolvedCache[e])throw Error("Retry unneeded - link has been resolved.");{let t=await this.resolveUrl(e,!1);if((0,n("97i3I").isSuccessfulResponse)(t))return t;throw Error("Retry for URL failed")}},this.retryConfig)).body}catch(e){return}}isRateLimitError(e){return(0,n("97i3I").isErrorResponse)(e)&&429===e.error.status}async fetchData(e,r){let a=await this.resolveUrl(e,r);if(this.isRateLimitError(a)&&(a=await t(i)(async()=>{let t=await this.resolveUrl(e,!1);if(this.isRateLimitError(t))throw this.mapErrorResponse(t,new URL(e).hostname);return t},this.retryConfig)),!(0,n("97i3I").isSuccessfulResponse)(a))throw this.mapErrorResponse(a,new URL(e).hostname);return this.resolvedCache[e]=!0,a.body}async fetchDataAris(e){return await this.batchResolveAris(e)}async postData(e){let t={key:e.key,action:e.action,context:e.context};return await (0,n("gmi3X").request)("post",`${this.resolverUrl}/invoke`,t)}async search(e){let{key:t,action:r}=e,{query:a,context:o}=r,i=await (0,n("gmi3X").request)("post",`${this.resolverUrl}/invoke/search`,{key:t,search:{query:a,context:o}});if((0,n("97i3I").isErrorResponse)(i))throw this.mapErrorResponse(i);return i}async fetchAvailableSearchProviders(){return(await (0,n("gmi3X").request)("post",`${this.resolverUrl}/providers`,{type:"search"})).providers}mapErrorResponse(e,t=""){if(e?.error){let r=e.error.type,a=e.error.message,o=e.error.extensionKey;if(e.error instanceof n("gmi3X").NetworkError)return new(n("jHnts")).APIError("fallback",t,a,r);switch(r){case"ResolveBadRequestError":case"SearchBadRequestError":case"BadRequestError":return new(n("jHnts")).APIError("fallback",t,a,r,o);case"ResolveAuthError":case"SearchAuthError":case"AuthError":return new(n("jHnts")).APIError("auth",t,a,r,o);case"ResolveUnsupportedError":case"SearchUnsupportedError":case"UnsupportedError":return new(n("jHnts")).APIError("fatal",t,a,r,o);case"ResolveFailedError":case"SearchFailedError":case"ResolveTimeoutError":case"SearchTimeoutError":case"SearchRateLimitError":case"ResolveRateLimitError":case"InternalServerError":case"TimeoutError":case"RateLimitError":return new(n("jHnts")).APIError("error",t,a,r,o)}}let{error:r,...a}=e||{};return new(n("jHnts")).APIError("fatal",t,e?`${this.stringifyError(r)} ${JSON.stringify(a)}`:"Response undefined","UnexpectedError")}stringifyError(e){return JSON.stringify(e,"object"==typeof e?Object.getOwnPropertyNames(e):void 0)}constructor(e,t){this.resolverUrl=void 0,this.envKey=void 0,this.baseUrlOverride=void 0,this.loadersByDomain=void 0,this.retryConfig=void 0,this.resolvedCache=void 0,this.product=void 0,this.postBatchResolve=async(e,t="URL")=>{let r=[...new Set(e)],a=[],o={"origin-timezone":Intl?.DateTimeFormat().resolvedOptions().timeZone,...this.product?{"X-Product":this.product}:{}};try{"URL"===t&&(a=await (0,n("gmi3X").request)("post",`${this.resolverUrl}/resolve/batch`,r.map(e=>({resourceUrl:e})),o)),"ARI"===t&&(a=await (0,n("gmi3X").request)("post",`${this.resolverUrl}/resolve/ari/batch`,r.map(e=>({ari:e})),o))}catch(t){a=e.map(()=>({status:(0,n("97i3I").isErrorResponse)(t)?t.status:500,error:t}))}let i={};for(let e=0;e<r.length;++e){let t=r[e],o=a[e];i[t]=o}return e.map(e=>i[e])},this.batchResolve=async e=>this.postBatchResolve(e,"URL"),this.batchResolveAris=async e=>this.postBatchResolve(e,"ARI"),this.resolverUrl=(0,n("dDhJe").getResolverUrl)(e,t),this.loadersByDomain={},this.retryConfig={retries:2},this.resolvedCache={},this.envKey=e,this.baseUrlOverride=t}}}),i("jHnts",function(t,r){e(t.exports,"APIError",()=>a);class a extends Error{constructor(e,t,r,a,o){super(`${e}: ${r}`),this.kind=e,this.hostname=t,this.message=r,this.type=a,this.extensionKey=o,this.name="APIError",this.type=a,this.kind=e,this.message=r,this.hostname=t,this.extensionKey=o}}}),i("gmi3X",function(t,r){e(t.exports,"NetworkError",()=>o),e(t.exports,"request",()=>n);let a=[200,401,404];class o extends Error{constructor(e){super(e)}}async function n(e,t,r,i,s=a){let d={method:e,credentials:"include",headers:{Accept:"application/json","Cache-Control":"no-cache","Content-Type":"application/json",...i},...r?{body:JSON.stringify(r)}:{}};try{let e=await fetch(t,d);if(e.ok||s?.includes(e.status)){if(!s.includes(204))return await e.json();{let t=await e.text();return t?JSON.parse(t):void 0}}throw e}catch(e){if("string"==typeof e||e instanceof TypeError)throw new o(e);throw e}}}),i("97i3I",function(t,r){e(t.exports,"isSuccessfulResponse",()=>a),e(t.exports,"isErrorResponse",()=>o);let a=e=>{if(!e)return!1;let t=200===e.status,r="body"in e;return t&&r},o=e=>{if(!e)return!1;let t="status"in e&&e.status>=200,r="error"in e;return t&&r}}),i("6pra5",function(t,r){e(t.exports,"request",()=>n);let a=[200,401,404];class o extends Error{constructor(e){super(e)}}async function n(e,t,r,n){let i={method:e,credentials:"include",headers:{Accept:"application/json","Cache-Control":"no-cache","Content-Type":"application/json",...n},...r?{body:JSON.stringify(r)}:{}};try{let e=await fetch(t,i);if(e.ok||a.includes(e.status))return await e.json();throw e}catch(e){if("string"==typeof e||e instanceof TypeError)throw new o(e);throw e}}}),i("gjBRE",function(t,r){e(t.exports,"ExtensionNode",()=>i),e(t.exports,"default",()=>s);var a=n("7UHDa");n("gwFzn");var o=n("fPlBD");class i extends n("2gkmX").default{ignoreMutation(e){return this.node.type.isAtom||"selection"!==e.type&&"data-layout"!==e.attributeName}createDomRef(){if(!(0,n("dh538").fg)("confluence_connect_macro_preset_height"))return super.createDomRef();if(!this.node.isInline){let e=document.createElement("div"),t=this.reactComponentProps?.extensionNodeViewOptions?.getExtensionHeight?.(this.node);return t&&e.style.setProperty("min-height",`${t}px`),e}return document.createElement("span")}stopEvent(e){return e.target instanceof HTMLInputElement&&(0,n("dh538").fg)("interactable_in_editor_inputs")}getContentDOM(){if(this.node.isInline)return;let e=document.createElement("div");return e.className=`${this.node.type.name}-content-dom-wrapper`,{dom:e}}render(e,t){return(0,a.jsx)(n("3oRlx").ExtensionNodeWrapper,{nodeType:this.node.type.name,macroInteractionDesignFeatureFlags:e.macroInteractionDesignFeatureFlags,children:(0,a.jsx)(o.Extension,{editorView:this.view,node:this.node,eventDispatcher:this.eventDispatcher,getPos:this.getPos,providerFactory:e.providerFactory,handleContentDOMRef:t,extensionHandlers:e.extensionHandlers,editorAppearance:e.extensionNodeViewOptions?.appearance,pluginInjectionApi:e.pluginInjectionApi,macroInteractionDesignFeatureFlags:e.macroInteractionDesignFeatureFlags,showLivePagesBodiedMacrosRendererView:e.showLivePagesBodiedMacrosRendererView,showUpdatedLivePages1PBodiedExtensionUI:e.showUpdatedLivePages1PBodiedExtensionUI,rendererExtensionHandlers:e.rendererExtensionHandlers})})}}function s(e,t,r,a,o,n,s,d,l,c){return(p,u,m)=>new i(p,u,m,e,t,{providerFactory:r,extensionHandlers:a,extensionNodeViewOptions:o,pluginInjectionApi:n,macroInteractionDesignFeatureFlags:s,showLivePagesBodiedMacrosRendererView:d,showUpdatedLivePages1PBodiedExtensionUI:l,rendererExtensionHandlers:c}).init()}}),i("2gkmX",function(t,r){e(t.exports,"default",()=>o);var a=n("7UHDa");n("gwFzn");class o{init(){this.domRef=this.createDomRef(),this.setDomAttrs(this.node,this.domRef);let{dom:e,contentDOM:t}=this.getContentDOM()||{dom:void 0,contentDOM:void 0};this.domRef&&e&&(this.domRef.appendChild(e),this.contentDOM=t||e,this.contentDOMWrapper=e||t),this.domRef.classList.add(`${this.node.type.name}View-content-wrap`);let{samplingRate:r,slowThreshold:a,trackingEnabled:o}=(0,n("led7c").getPerformanceOptions)(this.view);return o&&(0,n("led7c").startMeasureReactNodeViewRendered)({nodeTypeName:this.node.type.name}),this.renderReactComponent(()=>this.render(this.reactComponentProps,this.handleRef)),o&&(0,n("led7c").stopMeasureReactNodeViewRendered)({nodeTypeName:this.node.type.name,dispatchAnalyticsEvent:this.dispatchAnalyticsEvent,samplingRate:r,slowThreshold:a}),this}renderReactComponent(e){this.domRef&&e&&this.portalProviderAPI.render(()=>(0,a.jsx)(n("7fmpI").ErrorBoundary,{component:n("d925B").ACTION_SUBJECT.REACT_NODE_VIEW,componentId:this?.node?.type?.name??n("d925B").ACTION_SUBJECT_ID.UNKNOWN_NODE,dispatchAnalyticsEvent:this.dispatchAnalyticsEvent,children:e()}),this.domRef,this.key)}createDomRef(){return this.node.isInline?document.createElement("span"):document.createElement("div")}getContentDOM(){}_handleRef(e){let t,r;let a=this.contentDOMWrapper||this.contentDOM,o=0,i=!1;e&&a&&!e.contains(a)&&(t=this.ignoreMutation,this.ignoreMutation=e=>{let t="selection"===e.type;return t||(i=!0),!t},this.view.state.selection.visible&&(r=this.view.state.selection.getBookmark()),!(0,n("dh538").fg)("platform_editor_r18_fix_selection_resync")&&this.view.state.selection?.ranges.length>0&&(o=this.view.state.selection?.ranges[0].$from?.parentOffset??0),e.appendChild(a),requestAnimationFrame(()=>{if(this.ignoreMutation=t,r&&i){if((0,n("dh538").fg)("platform_editor_r18_fix_selection_resync")){let e=r.resolve(this.view.state.tr.doc);if(!e.eq(this.view.state.selection)){let t=this.view.state.tr.setSelection(e);t.setMeta("source","ReactNodeView:_handleRef:selection-resync"),this.view.dispatch(t)}}else o>0&&this.view.dispatch(this.view.state.tr.setSelection(r.resolve(this.view.state.tr.doc)))}}))}render(e,t){return this.reactComponent?(0,a.jsx)(this.reactComponent,{view:this.view,getPos:this.getPos,node:this.node,forwardRef:t,...e}):null}update(e,t,r,a=()=>!0){let o=this.node.type===e.type&&a(this.node,e);return this.decorations=t,!!o&&((this.domRef&&!this.node.sameMarkup(e)&&this.setDomAttrs(e,this.domRef),this.viewShouldUpdate(e,t))?(this.node=e,this.renderReactComponent(()=>this.render(this.reactComponentProps,this.handleRef))):this.node=e,!0)}viewShouldUpdate(e,t){return!this._viewShouldUpdate||this._viewShouldUpdate(e)}setDomAttrs(e,t){Object.keys(e.attrs||{}).forEach(r=>{t.setAttribute(r,e.attrs[r])})}get dom(){return this.domRef}destroy(){this.domRef&&(this.portalProviderAPI.remove(this.key),this.domRef=void 0,this.contentDOM=void 0)}static fromComponent(e,t,r,a,n){return(i,s,d)=>new o(i,s,d,t,r,a,e,n).init()}constructor(e,t,r,a,o,i,s,d){this.domRef=void 0,this.contentDOMWrapper=void 0,this.reactComponent=void 0,this.portalProviderAPI=void 0,this._viewShouldUpdate=void 0,this.eventDispatcher=void 0,this.decorations=[],this.reactComponentProps=void 0,this.view=void 0,this.getPos=void 0,this.contentDOM=void 0,this.node=void 0,this.key=void 0,this.handleRef=e=>this._handleRef(e),this.dispatchAnalyticsEvent=e=>{this.eventDispatcher&&(0,n("5vVM5").createDispatch)(this.eventDispatcher)(n("lWghV").analyticsEventKey,{payload:e})},this.node=e,this.view=t,this.getPos=r,this.portalProviderAPI=a,this.reactComponentProps=i||{},this.reactComponent=s,this._viewShouldUpdate=d,this.eventDispatcher=o,this.key=(0,n("gSnMl").generateUniqueNodeKey)()}}}),i("5vVM5",function(t,r){e(t.exports,"EventDispatcher",()=>a),e(t.exports,"createDispatch",()=>o);class a{on(e,t){this.listeners[e]||(this.listeners[e]=new Set),this.listeners[e].add(t)}has(e,t){return!!this.listeners[e]&&this.listeners[e].has(t)}off(e,t){this.listeners[e]&&this.listeners[e].has(t)&&this.listeners[e].delete(t)}emit(e,t){this.listeners[e]&&this.listeners[e].forEach(e=>e(t))}destroy(){this.listeners={}}constructor(){this.listeners={}}}function o(e){return(t,r)=>{if(!t)throw Error("event name is required!");e.emit("string"==typeof t?t:t.key,r)}}}),i("7fmpI",function(r,a){e(r.exports,"ErrorBoundary",()=>i);var o=n("gwFzn");class i extends t(o).Component{hasFallback(){return void 0!==this.props.fallbackComponent}shouldRecover(){return this.hasFallback()&&this.state.errorCaptured}componentDidCatch(e,t){this.props.dispatchAnalyticsEvent&&this.props.dispatchAnalyticsEvent({action:n("d925B").ACTION.EDITOR_CRASHED,actionSubject:this.props.component,actionSubjectId:this.props.componentId,eventType:n("d925B").EVENT_TYPE.OPERATIONAL,attributes:{error:e,errorInfo:t,errorRethrown:!this.hasFallback()}}),(0,n("hWRJP").logException)(e,{location:"editor-common"}),this.hasFallback()&&this.setState({errorCaptured:!0})}render(){return this.shouldRecover()?this.props.fallbackComponent:this.props.children}constructor(...e){super(...e),this.state={errorCaptured:!1}}}}),i("led7c",function(t,r){e(t.exports,"getPerformanceOptions",()=>o),e(t.exports,"startMeasureReactNodeViewRendered",()=>i),e(t.exports,"stopMeasureReactNodeViewRendered",()=>s);let a=0;function o(e){let t=({key:"analyticsPlugin$",getState:e=>e.analyticsPlugin$}).getState(e.state),r=t&&t.performanceTracking&&t.performanceTracking.nodeViewTracking||{},a=r.samplingRate??100,o=r.slowThreshold??7;return{trackingEnabled:!!r.enabled,samplingRate:a,slowThreshold:o}}function i({nodeTypeName:e}){(0,n("2T4ch").startMeasure)(`\u{1F989}${e}::ReactNodeView`)}function s({nodeTypeName:e,dispatchAnalyticsEvent:t,samplingRate:r,slowThreshold:o}){(0,n("2T4ch").stopMeasure)(`\u{1F989}${e}::ReactNodeView`,i=>{++a%r==0&&i>o&&t({action:n("d925B").ACTION.REACT_NODEVIEW_RENDERED,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,eventType:n("d925B").EVENT_TYPE.OPERATIONAL,attributes:{node:e,duration:i}})})}}),i("gSnMl",function(r,a){e(r.exports,"generateUniqueNodeKey",()=>i);var o=n("kyKWe");let i=()=>t(o)()}),i("bT1qC",function(t,r){e(t.exports,"inlineNodeViewClassname",()=>a),e(t.exports,"getInlineNodeViewProducer",()=>u),n("gwFzn");let a="inlineNodeView",o=e=>e.type.isInline&&e.type.isAtom&&e.type.isLeaf,i=["inlineCard"];function s({nodeViewParams:e,pmPluginFactoryParams:t,Component:r,extraComponentProps:o,extraNodeViewProps:i}){let s=e.node,d=(0,n("gSnMl").generateUniqueNodeKey)(),p=document.createElement("span");p.contentEditable="false",l(e.node,p);let u={current:null};function m(e){t.eventDispatcher.emit(n("lWghV").analyticsEventKey,{payload:e})}function h(){t.portalProviderAPI.render(c({dispatchAnalyticsEvent:m,currentNode:s,nodeViewParams:e,Component:r,extraComponentProps:o}),p,d)}p.classList.add(`${e.node.type.name}View-content-wrap`,`${a}`);let{samplingRate:g,slowThreshold:b,trackingEnabled:f}=(0,n("led7c").getPerformanceOptions)(e.view);return f&&(0,n("led7c").startMeasureReactNodeViewRendered)({nodeTypeName:s.type.name}),h(),f&&(0,n("led7c").stopMeasureReactNodeViewRendered)({nodeTypeName:s.type.name,dispatchAnalyticsEvent:m,samplingRate:g,slowThreshold:b}),{get dom(){return p},update:(e,t)=>s.type===e.type&&(s.sameMarkup(e)||l(e,p),s=e,h(),!0),destroy(){t.portalProviderAPI.remove(d),p=void 0,u.current=null},...{...i}}}function d({nodeViewParams:e,pmPluginFactoryParams:t,Component:r,extraComponentProps:i,extraNodeViewProps:s}){let d=e.node,p=(0,n("gSnMl").generateUniqueNodeKey)(),u=document.createElement("span");u.contentEditable="false",l(e.node,u);let m={current:null};function h(){m.current&&(u.removeChild(m.current),m.current=null)}function g(e){t.eventDispatcher.emit(n("lWghV").analyticsEventKey,{payload:e})}function b(){t.portalProviderAPI.render(c({dispatchAnalyticsEvent:g,currentNode:d,nodeViewParams:e,Component:r,extraComponentProps:i}),u,p,h)}u.classList.add(`${e.node.type.name}View-content-wrap`,`${a}`);let f=!1,x=!1,v=()=>{};return function(){if(!o(d)||"function"!=typeof d.type?.spec?.toDOM)return;let e=(0,n("kviC1").DOMSerializer).renderSpec(document,d.type.spec.toDOM(d)).dom;m.current=e,u.replaceChildren(e)}(),setTimeout(()=>{!function(){let t=(0,n("iEqmY").getOrCreateOnVisibleObserver)(e.view);u&&(v=t.observe(u,()=>{f||x||(b(),f=!0)}))}()},0),{get dom(){return u},update:(e,t)=>d.type===e.type&&(d.sameMarkup(e)||l(e,u),d=e,f&&b(),!0),destroy(){v(),x=!0,t.portalProviderAPI.remove(p),u=void 0,m.current=null},...{...s,stopEvent:e=>{let t=s?.stopEvent;return"function"==typeof t&&t(e)}}}}function l(e,t){Object.keys(e.attrs||{}).forEach(r=>{t.setAttribute(r,e.attrs[r])})}function c({dispatchAnalyticsEvent:e,currentNode:t,nodeViewParams:r,Component:o,extraComponentProps:i}){return function(){return(0,n("3jLHL").jsx)(n("7fmpI").ErrorBoundary,{component:n("d925B").ACTION_SUBJECT.REACT_NODE_VIEW,componentId:t?.type?.name??n("d925B").ACTION_SUBJECT_ID.UNKNOWN_NODE,dispatchAnalyticsEvent:e},(0,n("3jLHL").jsx)("span",{className:"zeroWidthSpaceContainer"},(0,n("3jLHL").jsx)("span",{className:`${a}AddZeroWidthSpace`}),n("TfRUG").ZERO_WIDTH_SPACE),(0,n("3jLHL").jsx)(o,{view:r.view,getPos:r.getPos,node:t,...i}),n("d7ZU3").browser.android?(0,n("3jLHL").jsx)("span",{className:"zeroWidthSpaceContainer",contentEditable:"false"},(0,n("3jLHL").jsx)("span",{className:`${a}AddZeroWidthSpace`}),n("TfRUG").ZERO_WIDTH_SPACE):(0,n("3jLHL").jsx)("span",{className:`${a}AddZeroWidthSpace`}))}}let p=new WeakMap;function u({pmPluginFactoryParams:e,Component:t,extraComponentProps:r,extraNodeViewProps:a}){return function(...o){let l=o[1],c=o[0],u={nodeViewParams:{node:c,view:l,getPos:o[2],decorations:o[3]},pmPluginFactoryParams:e,Component:t,extraComponentProps:r,extraNodeViewProps:a};if(!i.includes(c?.type?.name||""))return s(u);if((0,n("dh538").fg)("platform_editor_inline_node_virt_threshold_override"))return d(u);let m=p.get(l)||0;return(m+=1,p.set(l,m),m<=100)?s(u):d(u)}}}),i("TfRUG",function(t,r){e(t.exports,"ZERO_WIDTH_SPACE",()=>a),e(t.exports,"ZERO_WIDTH_JOINER",()=>o);let a="​",o="‍"}),i("iEqmY",function(r,a){e(r.exports,"getOrCreateOnVisibleObserver",()=>s);var o=n("dsBQ6");let i={rootMargin:"0px 0px 100px 0px",threshold:0},s=t(o)(e=>{let t={root:e.dom.closest('[data-editor-scroll-container="true"]'),...i},r=new WeakMap,a=new IntersectionObserver(e=>{e.filter(e=>e.isIntersecting).map(e=>r.get(e.target)).forEach(e=>e?.())},t);return{observe:(e,t)=>(r.set(e,t),a.observe(e),()=>a.unobserve(e))}})}),i("fPlBD",function(t,r){e(t.exports,"Extension",()=>s);var a=n("7UHDa"),o=n("gwFzn"),i=n("dhO1r");class s extends o.Component{componentWillUnmount(){this.props.providerFactory||this.providerFactory.destroy()}render(){return(0,a.jsx)(n("dYBVS").WithProviders,{providers:["extensionProvider"],providerFactory:this.providerFactory,renderNode:this.renderWithProvider})}constructor(e){super(e),this.providerFactory=void 0,this.renderWithProvider=({extensionProvider:e})=>{let{node:t,getPos:r,editorView:o,handleContentDOMRef:n,extensionHandlers:s,references:d,editorAppearance:l,pluginInjectionApi:c,eventDispatcher:p,macroInteractionDesignFeatureFlags:u,showLivePagesBodiedMacrosRendererView:m,showUpdatedLivePages1PBodiedExtensionUI:h,rendererExtensionHandlers:g}=this.props,{contentMode:b,mode:f}=c?.editorViewMode?.sharedState?.currentState()||{};return(0,a.jsx)(i.ExtensionComponent,{editorView:o,node:t,getPos:r,references:d,extensionProvider:e,handleContentDOMRef:n,extensionHandlers:s,editorAppearance:l,pluginInjectionApi:c,eventDispatcher:p,macroInteractionDesignFeatureFlags:u,showLivePagesBodiedMacrosRendererView:m,showUpdatedLivePages1PBodiedExtensionUI:h,rendererExtensionHandlers:g,isLivePageViewMode:"live-view"===b||"view"===f})},this.providerFactory=e.providerFactory||new(n("4FxUL")).default}}s.displayName="Extension"}),i("dhO1r",function(r,a){e(r.exports,"ExtensionComponent",()=>l);var o=n("7UHDa"),i=n("gwFzn"),s=n("heH5c");let d=e=>{let t=[];return e.content.forEach(e=>{t.push((0,n("7iE7T").nodeToJSON)(e))}),t.length?t:e.attrs.text},l=e=>{let{extensionProvider:t,showLivePagesBodiedMacrosRendererView:r,node:a,...s}=e,[d,l]=(0,i.useState)(void 0),[p,u]=(0,i.useState)(!!r?.(n("7iE7T").nodeToJSON(a))&&!(0,n("5wrbt").isEmptyBodiedMacro)(a)),m=(0,i.useRef)(!0);return(0,i.useLayoutEffect)(()=>(m.current=!0,()=>{m.current=!1}),[]),(0,i.useEffect)(()=>{t?.then(e=>{m.current&&l(e)})},[t]),(0,o.jsx)(c,{...s,extensionProvider:d,node:a,showLivePagesBodiedMacrosRendererView:r,showBodiedExtensionRendererView:p,setShowBodiedExtensionRendererView:u})};class c extends i.Component{componentDidUpdate(){this.parsePrivateNodePropsIfNeeded()}render(){let{node:e,handleContentDOMRef:t,editorView:r,references:a,editorAppearance:i,pluginInjectionApi:s,getPos:d,eventDispatcher:l,macroInteractionDesignFeatureFlags:c,extensionProvider:p,showLivePagesBodiedMacrosRendererView:u,showUpdatedLivePages1PBodiedExtensionUI:m,showBodiedExtensionRendererView:h,setShowBodiedExtensionRendererView:g,isLivePageViewMode:b}=this.props,{selection:f}=r.state,x=f instanceof n("7T7aA").NodeSelection&&f.node,v="function"==typeof d&&d(),y=v&&r.state.doc.resolve(v),E=!!(y&&y.depth>0);if("multiBodiedExtension"===e.type.name){let a=this.state._privateProps?.__allowBodiedOverride&&(0,n("dh538").fg)("platform_editor_multi_body_extension_extensibility");return(0,o.jsx)(n("akFmj").default,{node:e,editorView:r,getPos:d,handleContentDOMRef:t,tryExtensionHandler:this.tryExtensionHandler.bind(this),eventDispatcher:l,pluginInjectionApi:s,editorAppearance:i,macroInteractionDesignFeatureFlags:c,isNodeSelected:x===e,isNodeNested:E,isNodeHovered:this.state.isNodeHovered,setIsNodeHovered:this.setIsNodeHovered,isLivePageViewMode:b,allowBodiedOverride:a})}let S=this.tryExtensionHandler(void 0);switch(e.type.name){case"extension":case"bodiedExtension":return(0,o.jsx)(n("8Ze8r").default,{node:e,getPos:this.props.getPos,references:a,extensionProvider:p,handleContentDOMRef:t,view:r,editorAppearance:i,hideFrame:this.state._privateProps?.__hideFrame,pluginInjectionApi:s,macroInteractionDesignFeatureFlags:c,isNodeSelected:x===e,isNodeHovered:this.state.isNodeHovered,isNodeNested:E,setIsNodeHovered:this.setIsNodeHovered,showLivePagesBodiedMacrosRendererView:!!u?.(n("7iE7T").nodeToJSON(e)),showUpdatedLivePages1PBodiedExtensionUI:!!m?.(n("7iE7T").nodeToJSON(e)),showBodiedExtensionRendererView:h,setShowBodiedExtensionRendererView:g,isLivePageViewMode:b,children:S});case"inlineExtension":return(0,o.jsx)(n("aAiMR").default,{node:e,macroInteractionDesignFeatureFlags:c,isNodeSelected:x===e,pluginInjectionApi:s,isNodeHovered:this.state.isNodeHovered,setIsNodeHovered:this.setIsNodeHovered,isLivePageViewMode:b,children:S});default:return null}}tryExtensionHandler(e){let{node:r}=this.props;try{let a=this.handleExtension(r,e);if(a&&t(i).isValidElement(a))return a}catch(e){console.error("Provided extension handler has thrown an error\n",e)}return null}constructor(...e){super(...e),this.privatePropsParsed=!1,this.state={},this.getNodeRenderer=(0,n("csnse").default)(s.getNodeRenderer),this.getExtensionModuleNodePrivateProps=(0,n("csnse").default)(s.getExtensionModuleNodePrivateProps),this.setIsNodeHovered=e=>{this.props.isLivePageViewMode||this.setState({isNodeHovered:e})},this.parsePrivateNodePropsIfNeeded=async()=>{if(this.privatePropsParsed||!this.props.extensionProvider)return;this.privatePropsParsed=!0;let{extensionType:e,extensionKey:t}=this.props.node.attrs;try{let r=await this.getExtensionModuleNodePrivateProps(this.props.extensionProvider,e,t);this.setState({_privateProps:r})}catch(e){console.error("Provided extension handler has thrown an error\n",e)}},this.handleExtension=(e,t)=>{let r;let{extensionHandlers:a,editorView:i,showBodiedExtensionRendererView:s,rendererExtensionHandlers:l}=this.props,{extensionType:c,extensionKey:p,parameters:u,text:m}=e.attrs,h="bodiedExtension"===e.type.name;if(h&&!s)return;let g=e?.marks?.find(e=>"fragment"===e.type.name)?.attrs?.localId,b=h?d(e):m,f={type:e.type.name,extensionType:c,extensionKey:p,parameters:u,content:b,localId:e.attrs.localId,fragmentLocalId:g};if(h){let e=l?.[c];if(e)return(0,n("2diEG").getExtensionRenderer)(e)(f,(0,n("7iE7T").toJSON)(i.state.doc))}if(a&&a[c]&&(r=(0,n("2diEG").getExtensionRenderer)(a[c])(f,i.state.doc,t)),!r){let e=this.props.extensionProvider&&this.getNodeRenderer(this.props.extensionProvider,c,p);if(e)return"multiBodiedExtension"===f.type?(0,o.jsx)(e,{node:f,references:this.props.references,actions:t}):(0,o.jsx)(e,{node:f,references:this.props.references})}return r}}}}),i("7iE7T",function(t,r){e(t.exports,"isParagraph",()=>s),e(t.exports,"isText",()=>d),e(t.exports,"isLinkMark",()=>l),e(t.exports,"SelectedState",()=>c),e(t.exports,"isNodeSelectedOrInRange",()=>p),e(t.exports,"isSupportedInParent",()=>u),e(t.exports,"isMediaNode",()=>m),e(t.exports,"isNodeBeforeMediaNode",()=>h),e(t.exports,"toJSON",()=>b),e(t.exports,"nodeToJSON",()=>f);var a,o=n("gWR1e");let i=(e,t)=>t&&e&&e.type===t,s=(e,t)=>i(e,t.nodes.paragraph),d=(e,t)=>i(e,t.nodes.text),l=(e,t)=>i(e,t.marks.link);var c=((a={})[a.selectedInRange=0]="selectedInRange",a[a.selectedInside=1]="selectedInside",a);let p=(e,t,r,a)=>{if("number"!=typeof r)return null;let o=Math.min(e,t),n=Math.max(e,t),i=r+a;return e===t?null:o<=r&&i<n||o<r&&i<=n?0:r<=e&&t<=i?1:null},u=(e,t,r)=>{let a=e.selection.$from.node("embed"===r||"block"===r?void 0:-1);return a&&a.type.validContent(t)},m=e=>["media","mediaInline","mediaGroup","mediaSingle"].includes(e.type.name),h=(e,t)=>{let r=e.nodeBefore;if(!r){let a=e.depth-1||1,n=(0,o.findParentNodeOfType)([t.schema.nodes[`${e.node(a).type.name}`]])(t.selection),i=n?t.tr.doc.resolve(n.pos):void 0,s=i&&i.pos<t.doc.nodeSize?i.nodeBefore:void 0;s&&(r=s)}return!!r&&["media","mediaInline","mediaGroup","mediaSingle"].includes(r.type.name)},g=new(n("h9yJL")).JSONTransformer;function b(e){return g.encode(e)}function f(e){return g.encodeNode(e)}}),i("8Ze8r",function(r,a){e(r.exports,"default",()=>l);var o=n("gwFzn"),i=n("6qIXK");function s(e){let{node:r,handleContentDOMRef:a,children:s,widthState:d,handleRef:l,shadowClassNames:c,hideFrame:p,editorAppearance:u,macroInteractionDesignFeatureFlags:m,isNodeSelected:h,isNodeHovered:g,isNodeNested:b,setIsNodeHovered:f,showLivePagesBodiedMacrosRendererView:x,showUpdatedLivePages1PBodiedExtensionUI:v,showBodiedExtensionRendererView:y,setShowBodiedExtensionRendererView:E,pluginInjectionApi:S,isLivePageViewMode:C}=e,{showMacroInteractionDesignUpdates:k}=m||{},T=e=>"extension"===e.type.name&&e.attrs?.extensionType==="com.atlassian.confluence.migration"&&e.attrs?.extensionKey==="legacy-content",w=["bodiedExtension","multiBodiedExtension"].includes(r.type.name),_=k||!!(p&&!w),N=r?.attrs?.parameters?.macroParams?.hidden?.value,{getPos:L,view:$}=e,R=t(o).useMemo(()=>{let e="function"==typeof L?L():void 0;return void 0!==e&&!isNaN(e)&&0===$.state.doc.resolve(e).depth},[$,L]),A=["full-width","wide"].includes(r.attrs.layout)&&R&&"full-width"!==u,I=!v||(0,n("5wrbt").isEmptyBodiedMacro)(r),F=t(i)("extension-container","block",c,{"with-overlay":!w&&!k,"with-bodied-border":k&&(w||T(r))&&!y&&I,"with-margin-styles":k&&!b&&!y,"with-hover-border":k&&g,"with-danger-overlay":k,"without-frame":_,[n("jY6Lt").widerLayoutClassName]:A}),P=t(i)("extension-overflow-wrapper",{"with-body":w,"with-margin-styles":k&&!b&&!y,"with-padding-styles":k&&y}),O=t(i)({"with-children":!!s,"without-frame":_}),D=t(i)({"with-padding-styles":k,"with-bodied-padding-styles":w&&k}),B=t(i)("extension-content","block",{"remove-border":k,"hide-content":y}),M={width:"100%"},H={};if(A){let{type:e,...t}=(0,n("fJNzZ").calculateBreakoutStyles)({mode:r.attrs.layout,widthStateWidth:d.width,widthStateLineLength:d.lineLength});H={...t},M=t}H={...H,...n("jY6Lt").contentWrapper};let j=e=>{f&&f(e)};return(0,n("3jLHL").jsx)(o.Fragment,null,k&&!C&&(0,n("3jLHL").jsx)(n("klDBQ").default,{isNodeSelected:h,isNodeHovered:g,isNodeNested:b,node:r,showMacroInteractionDesignUpdates:k,customContainerStyles:M,setIsNodeHovered:f,isBodiedMacro:w||T(r),showLivePagesBodiedMacrosRendererView:x,showUpdatedLivePages1PBodiedExtensionUI:v,showBodiedExtensionRendererView:y,setShowBodiedExtensionRendererView:E,pluginInjectionApi:S}),(0,n("3jLHL").jsx)("div",{"data-testid":"extension-container",ref:l,"data-layout":r.attrs.layout,className:F,css:n("jY6Lt").wrapperStyleInheritedCursor,style:M,onMouseEnter:()=>j(!0),onMouseLeave:()=>j(!1)},(0,n("3jLHL").jsx)("div",{"data-testid":"extension-overflow-wrapper",className:P,css:n("jY6Lt").overflowWrapperStyles},(0,n("3jLHL").jsx)("div",{className:"extension-overlay",css:n("mBi3D").overlay}),(0,n("3jLHL").jsx)("div",{css:n("jY6Lt").header,contentEditable:!1,className:O},!_&&(0,n("3jLHL").jsx)(n("klDBQ").default,{isNodeSelected:h,node:r,showMacroInteractionDesignUpdates:k,pluginInjectionApi:S}),s),w&&(0,n("3jLHL").jsx)("div",{css:H,className:D,"data-testid":"extension-new-content"},!(C&&"true"===N)&&(0,n("3jLHL").jsx)("div",{"data-testid":"extension-content",css:n("jY6Lt").content,className:B},(0,n("3jLHL").jsx)("div",{ref:a}))))))}let d=(0,n("574ry").sharedPluginStateHookMigratorFactory)(e=>{let{widthState:t}=(0,n("1Oo9w").useSharedPluginState)(e,["width"]);return{widthState:{width:t?.width??0,lineLength:t?.lineLength}}},e=>({widthState:{width:(0,n("b3YrF").useSharedPluginStateSelector)(e,"width.width")??0,lineLength:(0,n("b3YrF").useSharedPluginStateSelector)(e,"width.lineLength")}}));var l=(0,n("frt7o").default)(e=>{let{pluginInjectionApi:t}=e,{widthState:r}=d(t);return(0,n("3jLHL").jsx)(s,{widthState:r,...e})},{overflowSelector:".extension-overflow-wrapper"})}),i("574ry",function(t,r){e(t.exports,"sharedPluginStateHookMigratorFactory",()=>o);var a=n("1oCLl");function o(e,t){return(0,n("dTb09").conditionalHooksFactory)(()=>(0,a.expValEquals)("platform_editor_usesharedpluginstateselector","isEnabled",!0),e,t)}}),i("dTb09",function(t,r){e(t.exports,"conditionalHooksFactory",()=>a);function a(e,t,r){let a=null;return(...o)=>{let n=e();return(null===a&&(a=n),a)?t(...o):r(...o)}}}),i("1Oo9w",function(r,a){e(r.exports,"useSharedPluginState",()=>d);var o=n("gwFzn"),i=n("2jjxD");function s(e,t){return Object.entries(e).reduce((e,[r,a])=>({...e,[r]:t(a)}),{})}function d(e,r,a){let n=(0,o.useMemo)(()=>r,[]);return function(e,r={}){let[a,n]=(0,o.useState)(s(e,e=>r.disabled?void 0:e?.sharedState.currentState())),d=(0,o.useRef)({}),l=(0,o.useRef)(!1);return(0,o.useLayoutEffect)(()=>{if(r.disabled)return;let a=t(i)(()=>{n(e=>({...e,...d.current}))});l.current&&(d.current=s(e,e=>e?.sharedState.currentState()),a());let o=Object.entries(e).map(([e,t])=>t?.sharedState.onChange(({nextSharedState:t,prevSharedState:r})=>{r!==t&&(d.current[e]=t,a())}));return l.current=!0,()=>{d.current={},o.forEach(e=>e?.())}},[e,r.disabled]),a}((0,o.useMemo)(()=>n.reduce((t,r)=>({...t,[`${String(r)}State`]:e?.[r]}),{}),[e,n]),a)}}),i("b3YrF",function(r,a){e(r.exports,"useSharedPluginStateSelector",()=>d);var o=n("gwFzn"),i=n("g9LeK"),s=n("atveb");function d(e,r,a={}){let l=(0,o.useCallback)(e=>{let[a,...o]=r.split(".");if(e&&o?.length!==0)return t(i)(e?.[`${a}State`],o)},[r]),c=(0,o.useMemo)(()=>{let[e]=r.split(".");return[e]},[r]),p=(0,o.useMemo)(()=>{if(a.disabled)return;let[t]=r.split(".");return l({[`${t}State`]:e?.[t]?.sharedState.currentState()})},[r,e,a.disabled,l]);return function(e,r,a,i,d={}){let[l,c]=(0,o.useState)(()=>i);return(0,n("6qdjm").usePluginStateEffect)(e,r,e=>{let r=a(e);t(s)(r,l)||c(()=>r)},d),l}(e,c,l,p,a)}}),i("6qdjm",function(r,a){e(r.exports,"usePluginStateEffect",()=>d);var o=n("gwFzn"),i=n("2jjxD"),s=n("1oCLl");function d(e,r,a,n={}){let l=(0,o.useMemo)(()=>r,[]);(function(e,r,a={}){let n=(0,o.useRef)(),d=(0,o.useRef)(),l=(0,o.useRef)(r);(0,o.useLayoutEffect)(()=>{if(!a.disabled&&(0,s.expValEquals)("platform_editor_usesharedpluginstateselector","isEnabled",!0))return l.current=t(i)(r),()=>{l.current=void 0}},[r,a.disabled]),(0,o.useEffect)(()=>{if(!(a.disabled||(0,s.expValEquals)("platform_editor_usesharedpluginstateselector","isEnabled",!0)))return l.current=t(i)(r),()=>{l.current=void 0}},[r,a.disabled]),(0,o.useLayoutEffect)(()=>{var t;if(a.disabled)return;n.current=(t=e=>e?.sharedState.currentState(),Object.entries(e).reduce((e,[r,a])=>({...e,[r]:t(a)}),{})),d.current=l.current?.(n.current);let r=Object.entries(e).map(([e,t])=>t?.sharedState.onChange(({nextSharedState:t,prevSharedState:r})=>{r!==t&&n.current&&(n.current[e]=t,d.current=l.current?.(n.current))}));return()=>{n.current=void 0,r.forEach(e=>e?.()),d.current?.()}},[e,a.disabled])})((0,o.useMemo)(()=>l.reduce((t,r)=>({...t,[`${String(r)}State`]:e?.[r]}),{}),[e,l]),a,n)}}),i("klDBQ",function(t,r){e(t.exports,"default",()=>o);var a=n("gwFzn");class o extends a.Component{render(){let{node:e,showMacroInteractionDesignUpdates:t}=this.props,r=(0,n("21PP6").getExtensionLozengeData)({node:e,type:"image"});if(!t&&r&&"extension"!==e.type.name)return this.renderImage(r);let a=(0,n("21PP6").getExtensionLozengeData)({node:e,type:"icon"});return this.renderFallback(a)}constructor(...e){super(...e),this.renderImage=e=>{let{extensionKey:t}=this.props.node.attrs,{url:r,...a}=e;return(0,n("3jLHL").jsx)("img",{css:n("mBi3D").styledImage,src:r,...a,alt:t})},this.renderFallback=e=>{let{showMacroInteractionDesignUpdates:t,isNodeSelected:r,isNodeHovered:a,isNodeNested:o,customContainerStyles:i,setIsNodeHovered:s,isBodiedMacro:d,showLivePagesBodiedMacrosRendererView:l,showUpdatedLivePages1PBodiedExtensionUI:c,showBodiedExtensionRendererView:p,setShowBodiedExtensionRendererView:u,pluginInjectionApi:m}=this.props,{parameters:h,extensionKey:g}=this.props.node.attrs,{name:b}=this.props.node.type,f=h&&h.macroParams,x=h&&h.extensionTitle||h&&h.macroMetadata&&h.macroMetadata.title||g;return(0,n("3jLHL").jsx)(n("gSgoy").LozengeComponent,{isNodeHovered:a,isNodeSelected:r,isNodeNested:o,showMacroInteractionDesignUpdates:t,extensionName:b,lozengeData:e,params:f,title:x,renderImage:this.renderImage,customContainerStyles:i,setIsNodeHovered:s,isBodiedMacro:d,showLivePagesBodiedMacrosRendererView:l,showUpdatedLivePages1PBodiedExtensionUI:c,showBodiedExtensionRendererView:p,setShowBodiedExtensionRendererView:u,pluginInjectionApi:m})}}}}),i("21PP6",function(t,r){e(t.exports,"getExtensionLozengeData",()=>a);let a=({node:e,type:t})=>{if(!e.attrs.parameters)return;let{macroMetadata:r}=e.attrs.parameters;if(r&&r.placeholder){let e;return r.placeholder.forEach(r=>{r.type===t&&r.data&&r.data.url&&(e=r.data)}),e}}}),i("mBi3D",function(t,r){e(t.exports,"wrapperDefault",()=>a),e(t.exports,"overlay",()=>o),e(t.exports,"placeholderFallback",()=>i),e(t.exports,"placeholderFallbackParams",()=>s),e(t.exports,"styledImage",()=>d);let a=(0,n("3jLHL").css)({background:"var(--ds-background-neutral, #091E420F)",borderRadius:"var(--ds-border-radius, 3px)",position:"relative",verticalAlign:"middle","&.with-overlay":{".extension-overlay":{background:"var(--ds-background-neutral-hovered, #091E4224)",color:"transparent"},"&:hover .extension-overlay":{opacity:1}}}),o=(0,n("3jLHL").css)({borderRadius:"var(--ds-border-radius, 3px)",position:"absolute",width:"100%",height:"100%",opacity:0,pointerEvents:"none",transition:"opacity 0.3s",top:0,left:0}),i=(0,n("3jLHL").css)({display:"inline-flex",alignItems:"center","& > img":{margin:"0 var(--ds-space-050, 4px)"},label:"placeholder-fallback"}),s=(0,n("3jLHL").css)({display:"inline-block",maxWidth:"200px",marginLeft:"var(--ds-space-050, 4px)",color:"var(--ds-text-subtlest, #626F86)",textOverflow:"ellipsis",whiteSpace:"nowrap",overflow:"hidden"}),d=(0,n("3jLHL").css)({maxHeight:"16px",maxWidth:"16px",label:"lozenge-image"})}),i("gSgoy",function(r,a){e(r.exports,"LozengeComponent",()=>s);var o=n("gwFzn");let i=e=>e.charAt(0).toUpperCase()+e.slice(1),s=({lozengeData:e,extensionName:r,title:a,params:s,renderImage:d,showMacroInteractionDesignUpdates:l,customContainerStyles:c,isNodeHovered:p,isNodeNested:u,setIsNodeHovered:m,isBodiedMacro:h,showLivePagesBodiedMacrosRendererView:g,showUpdatedLivePages1PBodiedExtensionUI:b,showBodiedExtensionRendererView:f,setShowBodiedExtensionRendererView:x,pluginInjectionApi:v})=>{let y=i(a);if(l)return(0,n("3jLHL").jsx)(o.Fragment,null,(0,n("3jLHL").jsx)(n("3owB7").ExtensionLabel,{text:y,extensionName:r,isNodeHovered:p,isNodeNested:u,customContainerStyles:c,setIsNodeHovered:m,isBodiedMacro:h,showLivePagesBodiedMacrosRendererView:g,showUpdatedLivePages1PBodiedExtensionUI:b,showBodiedExtensionRendererView:f,pluginInjectionApi:v}),g&&h&&(0,n("3jLHL").jsx)(n("lFpYn").EditToggle,{isNodeHovered:p,setIsNodeHovered:m,customContainerStyles:c,showBodiedExtensionRendererView:f,setShowBodiedExtensionRendererView:x}));let E="extension"===r;return(0,n("3jLHL").jsx)("div",{"data-testid":"lozenge-fallback",css:n("mBi3D").placeholderFallback},e&&!E?d({height:24,width:24,...e}):(0,n("3jLHL").jsx)(t(n("bha8O")),{label:a}),(0,n("3jLHL").jsx)("span",{className:"extension-title"},y),s&&!E&&(0,n("3jLHL").jsx)("span",{css:n("mBi3D").placeholderFallbackParams},Object.keys(s).map(e=>e&&` | ${e} = ${s[e].value}`)))}}),i("lFpYn",function(r,a){e(r.exports,"EditToggle",()=>p);var o=n("gwFzn");let i=(0,n("3jLHL").css)({opacity:0,lineHeight:1,position:"absolute",width:"max-content",top:"-28px",display:"inline-flex",justifyContent:"flex-end",color:"var(--ds-text-subtle, #44546F)"}),s=(0,n("3jLHL").css)({display:"flex",alignItems:"center",cursor:"pointer",boxShadow:"0 0 0 1px var(--ds-border, #091E4224)",minHeight:"var(--ds-space-300, 24px)",borderRadius:"var(--ds-border-radius, 4px)",paddingLeft:"var(--ds-space-150, 12px)",paddingRight:"var(--ds-space-150, 12px)",font:'var(--ds-font-body, normal 400 14px/20px ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif)',"&:hover":{backgroundColor:"var(--ds-background-input-hovered, #F7F8F9)"},outlineColor:"var(--ds-border-focused, #388BFF)",border:"none",backgroundColor:"var(--ds-background-input, #FFFFFF)",color:"var(--ds-text-subtle, #44546F)"}),d=(0,n("3jLHL").css)({opacity:1}),l=(0,n("ecnYn").xcss)({marginRight:"space.075"}),c=(0,n("2nPZH").defineMessages)({doneEditing:{id:"editor-common-extensibility-extension-lozenge-editToggle.done.editing",defaultMessage:"Done editing"},makeEdits:{id:"editor-common-extensibility-extension-lozenge-editToggle.make.edits",defaultMessage:"Make edits"}}),p=({isNodeHovered:e,customContainerStyles:r,setIsNodeHovered:a,showBodiedExtensionRendererView:p,setShowBodiedExtensionRendererView:u})=>{let m=(0,n("dBxQj").default)(),h=p?m.formatMessage(c.makeEdits):m.formatMessage(c.doneEditing),g=p?(0,n("3jLHL").jsx)(t(n("1Zr9M")),{testId:"edit-icon",label:""}):(0,n("3jLHL").jsx)(t(n("cvXh8")),{testId:"check-mark-icon",label:""}),b=(0,o.useCallback)(()=>{u?.(!p)},[p,u]),f=(0,o.useCallback)(e=>{"Enter"===e.key&&b()},[b]);return(0,n("3jLHL").jsx)("div",{"data-testid":"extension-edit-toggle-container",css:e?[i,d]:i,style:r,className:"extension-edit-toggle-container",onMouseOver:()=>a?.(!0),onMouseLeave:()=>a?.(!1),tabIndex:-1},(0,n("3jLHL").jsx)("button",{type:"button","data-testid":"edit-toggle",css:s,className:"extension-edit-toggle",onClick:b,onKeyDown:f,onFocus:()=>a?.(!0),onBlur:()=>a?.(!1)},(0,n("3jLHL").jsx)(n("bUlM5").default,{as:"span",xcss:l},g),h))}}),i("3owB7",function(r,a){e(r.exports,"ExtensionLabel",()=>u);var o=n("6qIXK");let i=(0,n("3jLHL").css)({textAlign:"left",zIndex:1,position:"relative","&.bodied":{marginTop:"var(--ds-space-300, 24px)"}}),s=(0,n("3jLHL").css)({opacity:0,lineHeight:1,display:"inline-flex",justifyContent:"left",position:"absolute",width:"max-content",top:"-28px","&.show-label":{cursor:"pointer",opacity:1},"&.nested":{marginLeft:"var(--ds-space-150, 12px)"},"&.inline":{top:"-27px"},"&.bodied-background":{background:"var(--ds-surface, #FFFFFF)"},"&.bodied-border":{boxShadow:"0 0 0 1px var(--ds-border, #091E4224)"},minHeight:"var(--ds-space-300, 24px)",alignItems:"center",borderRadius:"var(--ds-border-radius, 3px)",paddingLeft:"var(--ds-space-100, 8px)",paddingRight:"var(--ds-space-100, 8px)",color:"var(--ds-text-subtle, #44546F)",backgroundColor:"var(--ds-background-accent-gray-subtlest, #F1F2F4)","&.remove-left-margin":{marginLeft:"var(--ds-space-negative-150, -12px)"},"&.remove-nested-left-margin":{marginLeft:0},font:'var(--ds-font-body, normal 400 14px/20px ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif)',"&.with-bodied-macro-live-page-styles":{backgroundColor:"var(--ds-background-input, #FFFFFF)",boxShadow:"0 0 0 1px var(--ds-border, #091E4224)"}}),d=(0,n("ecnYn").xcss)({height:"space.200",position:"absolute",width:"100%"}),l=(0,n("3jLHL").css)({marginLeft:"var(--ds-space-075, 6px)","&.hide-icon":{display:"none"}}),c=(0,n("2nPZH").defineMessages)({configure:{id:"editor-common-extensibility.macro.button.configure",defaultMessage:"Configure {macroName}"}}),p=(e,t,r,a,o)=>!e||o?t:!r||!!(t&&!a),u=({text:e,extensionName:r,isNodeHovered:a,customContainerStyles:u,isNodeNested:m,setIsNodeHovered:h,isBodiedMacro:g,showUpdatedLivePages1PBodiedExtensionUI:b,showLivePagesBodiedMacrosRendererView:f,showBodiedExtensionRendererView:x,pluginInjectionApi:v})=>{let y="inlineExtension"===r,E=g&&!a,S=p(g,a,f,x,b),C=t(o)({bodied:g}),k=t(o)("extension-label",{nested:m,inline:y,bodied:g,"bodied-border":E,"bodied-background":E,"show-label":S,"with-bodied-macro-live-page-styles":g&&f,"always-hide-label":g&&x,"remove-left-margin":!g&&!y&&!m,"remove-nested-left-margin":m&&!g&&!y}),T=t(o)({"hide-icon":g&&!a});return(0,n("3jLHL").jsx)("div",{css:i,className:C,style:u,onMouseOver:()=>{h?.(!0)},onMouseLeave:()=>{h?.(!1)},"data-testid":"new-lozenge-container",contentEditable:!1},(0,n("3jLHL").jsx)(n("3gadb").default,{content:(0,n("3jLHL").jsx)(n("4jR19").default,{...c.configure,values:{macroName:e}}),position:"top"},r=>(0,n("3jLHL").jsx)("span",{"data-testid":"new-lozenge-button",...r,css:s,className:k},e,(0,n("3jLHL").jsx)("span",{css:l,className:T,"data-testid":"config-icon"},(0,n("3jLHL").jsx)(t(n("isYda")),{label:""})))),(0,n("3jLHL").jsx)(n("6f0Oj").default,{xcss:d}))}}),i("5wrbt",function(t,r){e(t.exports,"isEmptyBodiedMacro",()=>a);let a=e=>{if("bodiedExtension"!==e.type.name)return!1;let t=e?.content?.firstChild,r=t?.firstChild,a=r?.type?.name==="placeholder"&&t?.childCount===1,o=!r&&1===e.childCount;return a||o}}),i("jY6Lt",function(t,r){e(t.exports,"widerLayoutClassName",()=>a),e(t.exports,"wrapperStyleInheritedCursor",()=>i),e(t.exports,"header",()=>s),e(t.exports,"content",()=>d),e(t.exports,"contentWrapper",()=>l),e(t.exports,"overflowWrapperStyles",()=>c);let a="wider-layout",o=(0,n("3jLHL").css)(n("mBi3D").wrapperDefault,{"&.without-frame":{background:"transparent"},width:"100%",".extension-overflow-wrapper:not(.with-body)":{overflowX:"auto"},"&.with-bodied-border":{boxShadow:"0 0 0 1px var(--ds-border, #091E4224)"},"&.with-hover-border":{boxShadow:"0 0 0 1px var(--ds-border-input, #8590A2)"},"&.with-margin-styles":{margin:"0 var(--ds-space-negative-250, -20px)",padding:"0 var(--ds-space-250, 20px)"}}),i=(0,n("3jLHL").css)(o,{".extension-overflow-wrapper:has(.extension-editable-area)":{cursor:"inherit"},".extension-overflow-wrapper:not(:has(.extension-editable-area))":{cursor:"pointer"}}),s=(0,n("3jLHL").css)({padding:"var(--ds-space-050, 4px) var(--ds-space-050, 4px) 0px",verticalAlign:"middle","&.with-children:not(.without-frame)":{padding:"var(--ds-space-050, 4px) var(--ds-space-100, 8px) var(--ds-space-100, 8px)"},"&.without-frame":{padding:0}}),d=(0,n("3jLHL").css)({padding:"var(--ds-space-100, 8px)",background:"var(--ds-surface, white)",border:"1px solid var(--ds-border, #091E4224)",borderRadius:"var(--ds-border-radius, 3px)",cursor:"initial",width:"100%","&.remove-border":{border:"none"},"&.hide-content":{display:"none"}}),l=(0,n("3jLHL").css)({padding:"0 var(--ds-space-100, 8px) var(--ds-space-100, 8px)",display:"flex",justifyContent:"center","&.with-padding-styles":{padding:"var(--ds-space-100, 8px)"},"&.with-bodied-padding-styles":{padding:"var(--ds-space-100, 8px) var(--ds-space-250, 20px)"}}),c=(0,n("3jLHL").css)({"&.with-margin-styles":{margin:"0 var(--ds-space-negative-250, -20px)"},"&.with-padding-styles":{padding:"var(--ds-space-100, 8px)"}})}),i("aAiMR",function(r,a){e(r.exports,"default",()=>d);var o=n("gwFzn"),i=n("6qIXK");let s=(0,n("574ry").sharedPluginStateHookMigratorFactory)(e=>{let{widthState:t}=(0,n("1Oo9w").useSharedPluginState)(e,["width"]);return{widthState:{width:t?.width}}},e=>({widthState:{width:(0,n("b3YrF").useSharedPluginStateSelector)(e,"width.width")}}));var d=e=>{let{node:r,pluginInjectionApi:a,macroInteractionDesignFeatureFlags:d,isNodeSelected:l,children:c,isNodeHovered:p,setIsNodeHovered:u,isLivePageViewMode:m}=e,{showMacroInteractionDesignUpdates:h}=d||{},{widthState:g}=s(a),b=t(i)("extension-container","inline",{"with-overlay":!h,"with-children":!!c,"with-danger-overlay":h,"with-hover-border":h&&p}),f=g.width?g.width-2*(0,n("aFUXX").akEditorGutterPaddingDynamic)():0,x=e=>{u&&u(e)},v=(0,n("3jLHL").jsx)(o.Fragment,null,h&&!m&&(0,n("3jLHL").jsx)(n("klDBQ").default,{node:r,isNodeSelected:l,isNodeHovered:p,showMacroInteractionDesignUpdates:h,setIsNodeHovered:u,pluginInjectionApi:a}),(0,n("3jLHL").jsx)("div",{"data-testid":"inline-extension-wrapper",css:[n("jZde6").wrapperStyle,n("jZde6").inlineWrapperStyles],className:b,onMouseEnter:()=>x(!0),onMouseLeave:()=>x(!1)},(0,n("3jLHL").jsx)("div",{css:n("mBi3D").overlay,className:"extension-overlay"}),c||(0,n("3jLHL").jsx)(n("klDBQ").default,{node:r,isNodeSelected:l,showMacroInteractionDesignUpdates:h,pluginInjectionApi:a})));return(0,n("3jLHL").jsx)(n("bWRlG").WidthContext.Provider,{value:(0,n("bWRlG").createWidthContext)(f)},v)}}),i("jZde6",function(t,r){e(t.exports,"wrapperStyle",()=>a),e(t.exports,"inlineWrapperStyles",()=>o);let a=(0,n("3jLHL").css)(n("mBi3D").wrapperDefault,{cursor:"pointer",display:"inline-flex",margin:"1px 1px var(--ds-space-050, 4px)","> img":{borderRadius:"var(--ds-border-radius, 3px)"},"&::after, &::before":{verticalAlign:"text-top",display:"inline-block",content:"''"},"&.with-children":{padding:0,background:"var(--ds-background-neutral-subtle, white)"},"&.with-hover-border":{boxShadow:"0 0 0 1px var(--ds-border-input, #8590A2)"}}),o=(0,n("3jLHL").css)({maxWidth:"100%","tr &":{maxWidth:"inherit"},".rich-media-item":{maxWidth:"100%"}})}),i("akFmj",function(r,a){e(r.exports,"default",()=>m);var o=n("gwFzn"),i=n("6qIXK");let s=(e,t)=>(0,n("3jLHL").css)(n("dsfZn").sharedMultiBodiedExtensionStyles.mbeExtensionContainer,{[`.multiBodiedExtension-content-dom-wrapper > [data-extension-frame='true']:nth-of-type(${e+1})`]:(0,n("3jLHL").css)(n("dsfZn").sharedMultiBodiedExtensionStyles.extensionFrameContent,t&&n("dsfZn").removeMarginsAndBorder)}),d=(0,n("3jLHL").css)({maxHeight:"24px",maxWidth:"24px"}),l=({articleRef:e})=>(0,n("3jLHL").jsx)("article",{className:"multiBodiedExtension--frames","data-testid":"multiBodiedExtension--frames",ref:e}),c=(e,r,a)=>{if(a)return null;if(e){let{url:t,...a}=e;return(0,n("3jLHL").jsx)("div",{className:"extension-title"},(0,n("3jLHL").jsx)("img",{css:d,src:t,...a,alt:r}),r)}return(0,n("3jLHL").jsx)("div",{className:"extension-title","data-testid":"multiBodiedExtension-default-lozenge"},(0,n("3jLHL").jsx)(t(n("bha8O")),{label:r}),r)},p=({node:e,handleContentDOMRef:r,getPos:a,tryExtensionHandler:d,editorView:p,eventDispatcher:u,widthState:m,editorAppearance:h,macroInteractionDesignFeatureFlags:g,isNodeSelected:b,isNodeHovered:f,isNodeNested:x,setIsNodeHovered:v,pluginInjectionApi:y,isLivePageViewMode:E,allowBodiedOverride:S=!1})=>{let{showMacroInteractionDesignUpdates:C}=g||{},{parameters:k,extensionKey:T}=e.attrs,w=k&&k.extensionTitle||k&&k.macroMetadata&&k.macroMetadata.title||T||e.type.name,_=(0,n("21PP6").getExtensionLozengeData)({node:e,type:"image"}),[N,L]=(0,o.useState)(0),$=t(o).useCallback(e=>{if("number"!=typeof e)throw L(0),Error("Index is not valid");return L(e),!0},[L]),R=t(o).useCallback(e=>r(e),[r]),A=t(o).useMemo(()=>(0,n("3jLHL").jsx)(l,{articleRef:R}),[R]),I=(0,n("gC39r").useMultiBodiedExtensionActions)({updateActiveChild:$,editorView:p,getPos:a,node:e,eventDispatcher:u,allowBodiedOverride:S,childrenContainer:A}),F=t(o).useMemo(()=>d(I),[d,I]),P=["full-width","wide"].includes(e.attrs.layout)&&"full-width"!==h,O={};if(P){let{...t}=(0,n("fJNzZ").calculateBreakoutStyles)({mode:e.attrs.layout,widthStateLineLength:m?.lineLength,widthStateWidth:m?.width});O=t}let D=t(i)("multiBodiedExtension--wrapper","extension-container","block",{"with-border":C,"with-danger-overlay":C,"with-padding-background-styles":C,"with-margin-styles":C&&!x,"with-hover-border":C&&f}),B=t(i)("multiBodiedExtension--container",{"remove-padding":C}),M=t(i)("multiBodiedExtension--body-container"),H=t(i)("multiBodiedExtension--navigation",{"remove-margins":C,"remove-border":C}),j=t(i)("multiBodiedExtension--overlay",{"with-margin":C}),U=e=>{v&&v(e)};return(0,n("3jLHL").jsx)(o.Fragment,null,C&&!E&&(0,n("3jLHL").jsx)(n("klDBQ").default,{isNodeSelected:b,node:e,showMacroInteractionDesignUpdates:!0,customContainerStyles:O,isNodeHovered:f,isNodeNested:x,setIsNodeHovered:v,isBodiedMacro:!0,pluginInjectionApi:y}),(0,n("3jLHL").jsx)("div",{className:D,css:n("7OgWk").mbeExtensionWrapperCSSStyles,"data-testid":"multiBodiedExtension--wrapper","data-layout":e.attrs.layout,style:O,onMouseEnter:()=>U(!0),onMouseLeave:()=>U(!1)},(0,n("3jLHL").jsx)("div",{css:n("7OgWk").overlayStyles,className:j,"data-testid":"multiBodiedExtension--overlay"}),c(_,w,C),(0,n("3jLHL").jsx)("div",{className:B,css:s(N,C),"data-testid":"multiBodiedExtension--container","data-active-child-index":N},S?(0,n("3jLHL").jsx)("div",{className:M,"data-testid":"multiBodiedExtension--body-container"},F):(0,n("3jLHL").jsx)(o.Fragment,null,(0,n("3jLHL").jsx)("nav",{className:H,css:n("dsfZn").sharedMultiBodiedExtensionStyles.mbeNavigation,"data-testid":"multiBodiedExtension-navigation"},F),A))))},u=(0,n("574ry").sharedPluginStateHookMigratorFactory)(e=>{let{widthState:t}=(0,n("1Oo9w").useSharedPluginState)(e,["width"]);return{widthState:t}},e=>{let t=(0,n("b3YrF").useSharedPluginStateSelector)(e,"width.width"),r=(0,n("b3YrF").useSharedPluginStateSelector)(e,"width.lineLength");return{widthState:void 0===t?void 0:{width:t,lineLength:r}}});var m=e=>{let{pluginInjectionApi:t}=e,{widthState:r}=u(t);return(0,n("3jLHL").jsx)(p,{widthState:r,...e})}}),i("gC39r",function(r,a){e(r.exports,"useMultiBodiedExtensionActions",()=>i);var o=n("gwFzn");let i=({updateActiveChild:e,editorView:r,getPos:a,node:i,eventDispatcher:s,allowBodiedOverride:d,childrenContainer:l})=>t(o).useMemo(()=>({changeActive(t){let{state:o,dispatch:d}=r,l=e(t);s&&(0,n("lWHWf").sendMBEAnalyticsEvent)(n("d925B").ACTION.CHANGE_ACTIVE,i,s);let c=a();if("number"!=typeof c)return l;let p=o.doc.nodeAt(c),u=c;if(p&&p?.type?.name==="multiBodiedExtension"&&p?.content){if(t<0||t>=p?.content?.childCount)throw Error(`Index out of bounds: valid range is 0-${p?.content?.childCount-1} inclusive`);for(let e=0;e<=t&&e<p?.content?.childCount;e++)u+=p?.content?.child(e)?.nodeSize||0;d(o.tr.setSelection(new(n("7T7aA")).TextSelection(o.doc.resolve(u-1))))}return l},addChild(){let{state:e,dispatch:t}=r,o=e.schema.nodes.paragraph.createAndFill({});if(!o)throw Error("Could not create paragraph");let d=e.schema.nodes.extensionFrame.createAndFill({},[o]),l=a();if("number"!=typeof l||!d)throw Error("Could not create frame or position not valid");let c=Math.min((l||1)+i.content.size,e.doc.content.size),p=e.tr.insert(c,d);return p.setSelection(new(n("7T7aA")).TextSelection(p.doc.resolve(c+1))),t(p),s&&(0,n("lWHWf").sendMBEAnalyticsEvent)(n("d925B").ACTION.ADD_CHILD,i,s),!0},getChildrenCount:()=>i.content.childCount,removeChild(e){let t=a();if("number"!=typeof t||"number"!=typeof e)throw Error("Position or index not valid");let{state:o,dispatch:d}=r;if(1===i.content.childCount){let e=o.tr;return e.deleteRange(t,t+i.content.size),d(e),!0}let l=o.doc.resolve(t),c=o.doc.resolve(l.start(l.depth+1)).posAtIndex(e),p=o.doc.nodeAt(c);if(!p)throw Error("Could not find frame node");let u=p.content.size+c,m=o.tr;return m.deleteRange(c,u),d(m),s&&(0,n("lWHWf").sendMBEAnalyticsEvent)(n("d925B").ACTION.REMOVE_CHILD,i,s),!0},updateParameters(e){let{state:t,dispatch:o}=r,d=a();if("number"!=typeof d)throw Error("Position not valid");let l={...i.attrs,parameters:{...i.attrs.parameters,macroParams:e}};return o(t.tr.setNodeMarkup(d,null,l)),s&&(0,n("lWHWf").sendMBEAnalyticsEvent)(n("d925B").ACTION.UPDATE_PARAMETERS,i,s),!0},getChildren(){let{state:e}=r,t=a();if("number"!=typeof t)return[];let o=e.doc.nodeAt(t)?.content;return s&&(0,n("lWHWf").sendMBEAnalyticsEvent)(n("d925B").ACTION.GET_CHILDREN,i,s),o?o.toJSON():[]},getChildrenContainer(){if(!d)throw Error("Could not provide children container");return s&&(0,n("lWHWf").sendMBEAnalyticsEvent)(n("d925B").ACTION.GET_CHILDREN_CONTAINER,i,s),l}}),[i,r,a,e,s,d,l])}),i("lWHWf",function(t,r){e(t.exports,"sendMBEAnalyticsEvent",()=>a);let a=(e,t,r)=>{(0,n("5vVM5").createDispatch)(r)(n("lWghV").analyticsEventKey,{payload:{action:e,actionSubject:n("d925B").ACTION_SUBJECT.MULTI_BODIED_EXTENSION,eventType:n("d925B").EVENT_TYPE.TRACK,attributes:{extensionType:t.attrs.extensionType,extensionKey:t.attrs.extensionKey,localId:t.attrs.localId,currentFramesCount:t.content.childCount}}})}}),i("7OgWk",function(t,r){e(t.exports,"mbeExtensionWrapperCSSStyles",()=>a),e(t.exports,"overlayStyles",()=>o);let a=(0,n("3jLHL").css)(n("mBi3D").wrapperDefault,{"&.with-margin-styles":{marginTop:0,marginLeft:"var(--ds-space-negative-150, -12px)",marginRight:"var(--ds-space-negative-150, -12px)"},cursor:"pointer",marginTop:"var(--ds-space-250, 24px)",marginBottom:"var(--ds-space-200, 16px)",".extension-title":{display:"flex",alignItems:"center",lineHeight:"16px !important",marginBottom:"var(--ds-space-100, 8px)",marginLeft:"var(--ds-space-050, 4px) !important",marginRight:"var(--ds-space-100, 8px)",paddingTop:"var(--ds-space-100, 8px) !important"},"&.with-border":{boxShadow:"0 0 0 1px var(--ds-border, #091E4224)"},"&.with-hover-border":{boxShadow:"0 0 0 1px var(--ds-border-input, #8590A2)"},"&.with-padding-background-styles":{padding:"var(--ds-space-100, 8px) var(--ds-space-250, 20px)",background:"transparent"}}),o=(0,n("3jLHL").css)({borderRadius:"var(--ds-border-radius, 3px)",position:"absolute",width:"100%",height:"100%",opacity:0,pointerEvents:"none",transition:"opacity 0.3s",zIndex:1,"&.with-margin":{margin:"var(--ds-space-negative-100, -8px)"}})}),i("3oRlx",function(r,a){e(r.exports,"ExtensionNodeWrapper",()=>s),n("gwFzn");var o=n("6qIXK");let i=(0,n("3jLHL").css)({"&.inline-extension":{display:"inline-block"},"&.relative":{position:"relative"}}),s=({children:e,nodeType:r,macroInteractionDesignFeatureFlags:a})=>{let{showMacroInteractionDesignUpdates:s}=a||{},d=t(o)({"inline-extension":"inlineExtension"===r&&s,relative:s});return(0,n("3jLHL").jsx)("span",{className:d,css:i},e,"inlineExtension"===r&&n("TfRUG").ZERO_WIDTH_SPACE)}}),i("b5IZN",function(r,a){e(r.exports,"CoreEditor",()=>u);var o=n("gwFzn"),i=n("atveb"),s=n("kyKWe"),d=n("ffCOo"),l=n("1T1oM");function c(e){let t=(0,o.useRef)(e),r=(0,n("19Ub2").default)(e);(0,o.useMemo)(()=>{t.current=r},[r]);let a=(0,n("auTg8").useEditorContext)(),i=(0,o.useMemo)(()=>new(n("fswVK")).default,[]),s=a.editorActions||i,{createAnalyticsEvent:d}=(0,n("inPa6").useAnalyticsEvents)(),c=(0,o.useCallback)(e=>{(0,n("ajtqX").fireAnalyticsEvent)(d)(e)},[d]),p=(0,o.useCallback)(()=>({...(0,n("6DQRK").createFeatureFlagsFromProps)(t.current.featureFlags),useNativeCollabPlugin:!!("boolean"==typeof t.current.collabEdit?.useNativePlugin&&t.current.collabEdit?.useNativePlugin)}),[]),u=(0,o.useCallback)(e=>{let{contextIdentifierProvider:r,onEditorReady:a,featureFlags:o}=t.current;s._privateRegisterEditor(e.view,e.eventDispatcher,e.transformer,p),a&&((0,n("2T4ch").startMeasure)(n("7lreV").default.ON_EDITOR_READY_CALLBACK),a(s),(0,n("2T4ch").stopMeasure)(n("7lreV").default.ON_EDITOR_READY_CALLBACK,(0,n("amGDM").default)(n("d925B").ACTION.ON_EDITOR_READY_CALLBACK,{contextIdentifierProvider:r,featureFlags:o},d)))},[s,d,p,t]),m=(0,o.useCallback)(e=>{let{onDestroy:r}=t.current;s._privateUnregisterEditor(),r&&r()},[s,t]);(0,n("eilyC").default)(r,d);let h=(0,l.default)(r,s,d),{onSave:g}=r,b=(0,o.useCallback)(e=>{g&&g(e)},[g]),f=!!(r.appearance&&["full-page","full-width"].includes(r.appearance));return(0,n("3jLHL").jsx)(o.Fragment,null,f?(0,n("3jLHL").jsx)(n("eqcbK").EditorINPMetrics,null):null,(0,n("3jLHL").jsx)(n("blhF9").EditorInternal,{props:r,handleAnalyticsEvent:c,createAnalyticsEvent:d,preset:r.preset,handleSave:b,editorActions:s,onEditorCreated:u,onEditorDestroyed:m,providerFactory:h,AppearanceComponent:r.AppearanceComponent}))}let p=e=>{let r=(0,o.useRef)(e);return t(i)(r.current,e)||(r.current=e),r.current};function u(e){let r=(0,o.useRef)(t(s)()),a=(0,o.useMemo)(()=>({packageName:n("75KVc").name,packageVersion:n("75KVc").version,componentName:"editorCore",appearance:(0,n("lWghV").getAnalyticsAppearance)(e.appearance),editorSessionId:r.current}),[e.appearance]),i=p(e.featureFlags);return(0,n("3jLHL").jsx)(d.FabricEditorAnalyticsContext,{data:a},(0,n("3jLHL").jsx)(c,{...e,featureFlags:i}))}u.propTypes={minHeight:({appearance:e,minHeight:t})=>t&&e&&!["comment","chromeless"].includes(e)?Error("minHeight only supports editor appearance chromeless and comment for Editor"):null}}),i("ajtqX",function(t,r){e(t.exports,"editorAnalyticsChannel",()=>a),e(t.exports,"fireAnalyticsEvent",()=>o);let a=n("k7eoe").FabricChannel.editor,o=(e,t)=>({payload:r,channel:o=a})=>{if(e){if(t?.immediate){e(r)?.fire(o);return}(0,n("5sRXB").AnalyticsQueue).get().schedule(()=>e(r)?.fire(o))}}}),i("5sRXB",function(t,r){e(t.exports,"AnalyticsQueue",()=>a);class a{request(e){if(window.requestIdleCallback)window.requestIdleCallback(e);else{let t=performance.now();setTimeout(()=>{e({didTimeout:!1,timeRemaining:()=>Math.max(0,50-(performance.now()-t))})},0)}}pending(){return"function"==typeof window.navigator?.scheduling?.isInputPending&&window.navigator?.scheduling?.isInputPending()===!0}process(){this.running||(this.running=!0,this.request(e=>{for(;e.timeRemaining()>0&&this.tasks.length>0&&!this.pending();){let e=this.tasks.shift();e&&e()}this.running=!1,this.tasks.length>0&&this.process()}))}schedule(e){this.tasks.push(e),this.process()}constructor(){this.tasks=[],this.running=!1}}a.get=(0,n("csnse").default)(()=>new a)}),i("fswVK",function(t,r){e(t.exports,"default",()=>i);var a=n("gWR1e");let o=e=>e.nativeCollabProviderPlugin$;class i{static from(e,t,r){let a=new i;return a._privateRegisterEditor(e,t,r),a}_privateGetEditorView(){return this.editorView}_privateGetEventDispatcher(){return this.eventDispatcher}getFeatureFlags(){return{}}_privateRegisterEditor(e,t,r,a=()=>({})){if(this.contentTransformer=r,this.eventDispatcher=t,this.getFeatureFlags=a,!this.editorView&&e)this.editorView=e,this.listeners.forEach(r=>r(e,t));else if(this.editorView!==e)throw Error("Editor has already been registered! It's not allowed to re-register editor with the new Editor instance.");this.contentTransformer&&(this.contentEncode=this.contentTransformer.encode.bind(this.contentTransformer))}_privateUnregisterEditor(){this.editorView=void 0,this.contentTransformer=void 0,this.contentEncode=void 0,this.eventDispatcher=void 0,this.getFeatureFlags=()=>({})}_privateSubscribe(e){this.editorView&&this.eventDispatcher&&e(this.editorView,this.eventDispatcher),this.listeners.push(e)}_privateUnsubscribe(e){this.listeners=this.listeners.filter(t=>t!==e)}focus({scrollIntoView:e}={scrollIntoView:!0}){return!(!this.editorView||this.editorView.hasFocus())&&(this.editorView.focus(),(0,n("dh538").fg)("platform_editor_reduce_scroll_jump_on_editor_start")?(e??!0)&&this.editorView.dispatch(this.editorView.state.tr.scrollIntoView()):this.editorView.dispatch(this.editorView.state.tr.scrollIntoView()),!0)}blur(){return!!(this.editorView&&this.editorView.hasFocus())&&(this.editorView.dom.blur(),!0)}clear(){if(!this.editorView)return!1;let e=this.editorView,{state:t}=e,r=e.state.tr.setSelection((0,n("7T7aA").TextSelection).create(t.doc,0,t.doc.nodeSize-2)).deleteSelection();return e.dispatch(r),!0}async getValue(){let{editorView:e}=this;if(!e)return;let t=await (0,n("g1Zdk").getEditorValueWithMedia)(e),r=(0,n("XtzgJ").toJSON)(t);if(!this.contentEncode)return r;let a=(0,n("kviC1").Node).fromJSON(this.editorView.state.schema,r);try{return this.contentEncode(a)}catch(e){throw this.dispatchAnalyticsEvent({action:n("d925B").ACTION.DOCUMENT_PROCESSING_ERROR,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,eventType:n("d925B").EVENT_TYPE.OPERATIONAL,attributes:{errorMessage:`${e instanceof Error&&"NodeNestingTransformError"===e.name?"NodeNestingTransformError - Failed to encode one or more nested tables":void 0}`}}),e}}getNodeByLocalId(e){if(this.editorView?.state){let t=(0,n("erkez").findNodePosByLocalIds)(this.editorView?.state,[e]),r=t.length>=1?t[0]:void 0;return r?.node}}getNodeByFragmentLocalId(e){if(this.editorView?.state){let t=(0,n("6Pdx8").findNodePosByFragmentLocalIds)(this.editorView?.state,[e]);return t.length>0?t[0].node:void 0}}getSelectedNode(){if(this.editorView?.state?.selection){let{selection:e}=this.editorView.state;return e instanceof n("7T7aA").NodeSelection?e.node:a.findParentNode(e=>!!e.type.spec.selectable)(e)?.node}}isDocumentEmpty(){return!this.editorView||(0,n("4oXlU").isEmptyDocument)(this.editorView.state.doc)}replaceDocument(e,t=!0,r=!0){return(0,n("bwgmA").default)("EditorActions.replaceDocument",{shouldAddToHistory:r},[{property:"shouldAddToHistory",description:"[ED-14158] EditorActions.replaceDocument does not use the shouldAddToHistory arg",type:"removed"}]),!!this.editorView&&null!=e&&(this.eventDispatcher&&this.eventDispatcher.emit("resetEditorState",{doc:e,shouldScrollToBottom:t}),!0)}replaceSelection(e,t,r){if(!this.editorView)return!1;let{state:o}=this.editorView;if(!e){let e=o.tr.deleteSelection().scrollIntoView();return this.editorView.dispatch(e),!0}let{schema:i}=o,s=Array.isArray(e)?(0,n("6tl2G").processRawFragmentValue)(i,e,void 0,void 0,void 0,this.dispatchAnalyticsEvent):(0,n("6tl2G").processRawValue)(i,e,void 0,void 0,void 0,this.dispatchAnalyticsEvent);return!!s&&(this.editorView.dispatch((0,a.safeInsert)(s,r,t)(o.tr).scrollIntoView()),!0)}appendText(e){if(!this.editorView||!e)return!1;let{state:t}=this.editorView,r=t.doc.lastChild;if(r&&r.type!==t.schema.nodes.paragraph)return!1;let a=t.tr.insertText(e).scrollIntoView();return this.editorView.dispatch(a),!0}constructor(){this.editorView=void 0,this.contentTransformer=void 0,this.contentEncode=void 0,this.eventDispatcher=void 0,this.listeners=[],this.dispatchAnalyticsEvent=e=>{this.eventDispatcher&&(0,n("5vVM5").createDispatch)(this.eventDispatcher)(n("lWghV").analyticsEventKey,{payload:e})},this.getResolvedEditorState=async e=>{let{useNativeCollabPlugin:t}=this.getFeatureFlags();if(!this.editorView)throw Error("Called getResolvedEditorState before editorView is ready");if(!t){let e=await this.getValue();if(!e)throw Error("editorValue is undefined");return{content:e,title:null,stepVersion:-1}}let r=this.editorView;await (0,n("g1Zdk").getEditorValueWithMedia)(r);let a=o(r.state);return a?.getFinalAcknowledgedState(e)}}}}),i("6tl2G",function(t,r){e(t.exports,"processRawValueWithoutValidation",()=>o),e(t.exports,"processRawValue",()=>i),e(t.exports,"processRawFragmentValue",()=>s);let a=(e,t)=>{try{let{transformedAdf:r,isTransformed:a}=(0,n("dDZcC").transformNestedTablesIncomingDocument)(e);if(a&&t)return t({action:n("d925B").ACTION.NESTED_TABLE_TRANSFORMED,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,eventType:n("d925B").EVENT_TYPE.OPERATIONAL}),{transformedAdf:r,isTransformed:a}}catch(e){console.error("Failed to transform one or more nested tables in the document"),t&&t({action:n("d925B").ACTION.DOCUMENT_PROCESSING_ERROR,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,eventType:n("d925B").EVENT_TYPE.OPERATIONAL,attributes:{errorMessage:`${e instanceof Error&&"NodeNestingTransformError"===e.name?"NodeNestingTransformError - Failed to transform one or more nested tables":void 0}`}})}return{transformedAdf:e,isTransformed:!1}};function o(e,t,r){let o;if(!t)return;if("string"==typeof t)try{o=JSON.parse(t)}catch(e){console.error(`Error processing value: ${t} isn't a valid JSON`);return}else o=t;let{transformedAdf:i}=a(o,r);return(0,n("kviC1").Node).fromJSON(e,i)}function i(e,t,r,o,i,s){let l;if(t){if("string"==typeof t)try{l=i?i.parse(t).toJSON():JSON.parse(t)}catch(e){console.error(`Error processing value: ${t} isn't a valid JSON`);return}else l=t;if(Array.isArray(l)){console.error(`Error processing value: ${l} is an array, but it must be an object.`);return}try{if("doc"!==l.type||(Array.isArray(l.content)&&0===l.content.length&&l.content.push({type:"paragraph",content:[]}),l.version||(l.version=1)),i)return(0,n("kviC1").Node).fromJSON(e,l);let{transformedAdf:t,isTransformed:c}=(0,n("1LHXq").transformMediaLinkMarks)(l);c&&s&&s({action:n("d925B").ACTION.MEDIA_LINK_TRANSFORMED,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,eventType:n("d925B").EVENT_TYPE.OPERATIONAL}),({transformedAdf:t,isTransformed:c}=(0,n("krPum").transformTextLinkCodeMarks)(t)),c&&s&&s({action:n("d925B").ACTION.TEXT_LINK_MARK_TRANSFORMED,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,eventType:n("d925B").EVENT_TYPE.OPERATIONAL});let p=[];({transformedAdf:t,isTransformed:c,discardedMarks:p}=(0,n("bQZGL").transformDedupeMarks)(t)),c&&s&&s({action:n("d925B").ACTION.DEDUPE_MARKS_TRANSFORMED_V2,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,eventType:n("d925B").EVENT_TYPE.OPERATIONAL,attributes:{discardedMarkTypes:p.map(e=>e.type)}}),({transformedAdf:t,isTransformed:c}=(0,n("fjWka").transformNodesMissingContent)(t)),c&&s&&s({action:n("d925B").ACTION.NODES_MISSING_CONTENT_TRANSFORMED,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,eventType:n("d925B").EVENT_TYPE.OPERATIONAL}),({transformedAdf:t,isTransformed:c}=(0,n("jl4n8").transformIndentationMarks)(t)),c&&s&&s({action:n("d925B").ACTION.INDENTATION_MARKS_TRANSFORMED,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,eventType:n("d925B").EVENT_TYPE.OPERATIONAL}),({transformedAdf:t,isTransformed:c}=(0,n("eJNM0").transformInvalidMediaContent)(t)),c&&s&&s({action:n("d925B").ACTION.INVALID_MEDIA_CONTENT_TRANSFORMED,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,eventType:n("d925B").EVENT_TYPE.OPERATIONAL}),({transformedAdf:t}=a(t,s)),s&&t.content?.some(e=>e&&"layoutSection"===e.type&&e.content?.length===1)&&s({action:n("d925B").ACTION.SINGLE_COL_LAYOUT_DETECTED,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,eventType:n("d925B").EVENT_TYPE.OPERATIONAL});let u=(0,n("6aq5c").validateADFEntity)(e,t||l,s),m=d(u,r,o),h=(0,n("kviC1").Node).fromJSON(e,m);try{h.check()}catch(e){throw s&&s({action:n("d925B").ACTION.INVALID_PROSEMIRROR_DOCUMENT,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,eventType:n("d925B").EVENT_TYPE.OPERATIONAL}),e}return s&&(0,n("juTiU").findAndTrackUnsupportedContentNodes)(h,e,s),h}catch(e){if(s&&s({action:n("d925B").ACTION.DOCUMENT_PROCESSING_ERROR,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,eventType:n("d925B").EVENT_TYPE.OPERATIONAL}),console.error(`Error processing document:
${e instanceof Error?e.message:String(e)}

`,JSON.stringify(l)),e instanceof RangeError&&(e.message.match(/^Invalid collection of marks for node/)||e.message.match(/^Invalid content for node/)))throw e;return}}}function s(e,t,r,a,o,s){if(!t)return;let d=t.map(t=>i(e,t,r,a,o,s)).filter(e=>!!e);if(0!==d.length)return(0,n("kviC1").Fragment).from(d)}let d=(e,t,r)=>r&&t?(0,n("hpdQE").sanitizeNodeForPrivacy)(e,t):e}),i("bQZGL",function(t,r){e(t.exports,"transformDedupeMarks",()=>s);let a=new Set(["strong","underline","textColor","link","em","subsup","strike","backgroundColor"]),o=e=>{let t=e.marks?.map(e=>e.type)?.filter(e=>a.has(e)||"annotation"===e);return!!t?.length&&new Set(t).size!==t.length},i=e=>{let t=new Map,r=new Map,o=[];if(a.forEach(e=>{t.set(e,!1)}),!e.marks)return{discardedMarks:o};let n=e.marks.filter(e=>{let a=e.type;if("annotation"===a){let t=e.attrs?.id;return r.has(t)?(o.push(e),!1):(r.set(t,!0),!0)}if(t.has(a)){if(t.get(a))return o.push(e),!1;t.set(a,!0)}return!0});return{node:{...e,marks:n},discardedMarks:o}},s=e=>{let t=!1,r=[];return{transformedAdf:(0,n("6jPem").traverse)(e,{text:e=>{if(o(e)){let a=i(e),o=a.discardedMarks;if(o.length)return r.push(...o),t=!0,a.node}}}),isTransformed:t,discardedMarks:r}}}),i("jl4n8",function(t,r){e(t.exports,"transformIndentationMarks",()=>i);let a=e=>e.content?.some(e=>e?.type==="heading"&&e?.marks?.some(e=>"indentation"===e.type))??!1,o=e=>({...e,content:e.content?.map(e=>e?.type==="heading"?{...e,marks:e.marks?.filter(e=>"indentation"!==e.type)}:e)}),i=e=>{let t=!1;return{transformedAdf:(0,n("6jPem").traverse)(e,{tableCell:e=>{if(a(e))return t=!0,o(e)},tableHeader:e=>{if(a(e))return t=!0,o(e)}}),isTransformed:t}}}),i("eJNM0",function(t,r){e(t.exports,"transformInvalidMediaContent",()=>s);let a=(e,t)=>{let r={};return e.forEach((e,a)=>{if(e?.type&&t.includes(e.type)){if(!r[e.type]){r[e.type]=1;return}r[e.type]++}}),r},o=(e,t,r)=>{let o=10,n=a(t,[e])[e],i=t.findIndex(r);for(;n>1&&i>-1&&o-- >0;)t.splice(i,1),i=t.findIndex(r),n=a(t,[e])[e]},i=(e,t)=>{if(!e.content)return;let r=[...e.content];return Object.keys(t).forEach(e=>{o(e,r,t=>t?.type===e&&(0,n("hbEec").isEmpty)(t)),o(e,r,t=>t?.type===e)}),{...e,content:r}},s=e=>{let t=!1;return{transformedAdf:(0,n("6jPem").traverse)(e,{mediaSingle:e=>{if(!e?.content?.length)return;let r=a(e.content,["media","caption"]);if(Object.values(r).some(e=>e>1))return t=!0,i(e,r)}}),isTransformed:t}}}),i("fjWka",function(t,r){e(t.exports,"transformNodesMissingContent",()=>b);let a=e=>{let t=1;return e.content?.forEach(e=>{e?.type==="tableRow"&&"number"==typeof e.content?.length&&e.content.length>t&&(t=e.content.length)}),t},o=e=>"tableCell"===e.type?[(0,n("2FFuS").paragraph)()]:[],i=e=>t=>{if((0,n("hbEec").isEmpty)(t))return e(),{...t,content:o(t)}},s=e=>e.content?.some(e=>e?.type!=="listItem"),d=e=>e.content?.some(e=>e?.type==="listItem"&&!e.content?.length),l=e=>e.content?.map(e=>{if(e)switch(e.type){case"listItem":if(n("hbEec").isEmpty(e))return n("eyfm5").listItem([n("2FFuS").paragraph()]);break;case"text":return n("eyfm5").listItem([n("2FFuS").paragraph(e)]);default:return n("eyfm5").listItem([e])}return e}),c=e=>t=>{if(s(t)||d(t))return e(),{...t,content:l(t)}},p=e=>e.content?.some(e=>e?.type!=="tableRow"),u=e=>{let t=a(e);return e.content?.map(e=>{if(e)switch(e.type){case"text":return n("8WrQo").tableRow([n("inmjk").tableCell({})(n("2FFuS").paragraph(e)),...Array(t-1).fill(n("inmjk").tableCell({})(n("2FFuS").paragraph()))]);case"tableCell":return n("8WrQo").tableRow([e]);case"tableRow":if(n("hbEec").isEmpty(e))return n("8WrQo").tableRow([...Array(t).fill(n("inmjk").tableCell({})(n("2FFuS").paragraph()))])}return e})},m=e=>e?.content?.some(e=>e?.type==="tableRow"&&e?.content?.length===0),h=e=>t=>{if(m(t)||p(t))return e(),{...t,content:u(t)}},g=e=>t=>{if((0,n("hbEec").isEmpty)(t))return e(),!1},b=e=>{let t=!1,r=()=>{t=!0},a=(0,n("6jPem").traverse)(e,{tableCell:i(r)});return a=(0,n("6jPem").traverse)(a||e,{mediaSingle:g(r)}),{transformedAdf:a=(0,n("6jPem").traverse)(a||e,{bulletList:c(r),orderedList:c(r),table:h(r)}),isTransformed:t}}}),i("eyfm5",function(t,r){e(t.exports,"listItem",()=>a);let a=e=>({type:"listItem",content:e})}),i("inmjk",function(t,r){e(t.exports,"tableCell",()=>a);let a=e=>(...t)=>({type:"tableCell",attrs:e,content:t})}),i("8WrQo",function(t,r){e(t.exports,"tableRow",()=>a);let a=e=>({type:"tableRow",content:e})}),i("krPum",function(t,r){e(t.exports,"transformTextLinkCodeMarks",()=>i);let a=e=>{let t=e.marks?.map(e=>e.type);return t?.includes("link")&&t?.includes("code")},o=e=>e.marks?{...e,marks:e.marks.filter(e=>"code"!==e.type)}:e,i=e=>{let t=!1;return{transformedAdf:(0,n("6jPem").traverse)(e,{text:e=>{if(a(e))return t=!0,o(e)}}),isTransformed:t}}}),i("hpdQE",function(t,r){e(t.exports,"sanitizeNodeForPrivacy",()=>a);function a(e,t){let r=new Map,a=!1,o=(0,n("6jPem").traverse)(e,{mention:e=>{if(e.attrs&&e.attrs.text){a=!0;let t=e.attrs.text,o=t.startsWith("@")?t.slice(1):t;r.set(e.attrs.id,o)}return{...e,attrs:{...e.attrs,text:""}}}});if(a&&t){let e=(a,o)=>{o&&o.then(a=>{(0,n("bqMS3").isResolvingMentionProvider)(a)&&(r.forEach((e,t)=>{a.cacheMentionName(t,e)}),r.clear(),t.unsubscribe("mentionProvider",e))})};t.subscribe("mentionProvider",e)}return o}}),i("g1Zdk",function(t,r){e(t.exports,"getEditorValueWithMedia",()=>o);let a={getState:e=>e.mediaPlugin$};async function o(e){let t=e.state&&a.getState(e.state);return t&&t.waitForMediaUpload&&await t.waitForPendingTasks(),e.state.doc}}),i("bwgmA",function(t,r){e(t.exports,"default",()=>a);var a=function(e,t,r){}}),i("6Pdx8",function(t,r){e(t.exports,"findNodePosByFragmentLocalIds",()=>a);let a=(e,t)=>{if(0===t.length)return[];let r=[],a=new Set(t);return e.doc.descendants((e,t)=>((e.marks?.filter(e=>"fragment"===e.type.name).map(e=>e.attrs?.localId).filter(e=>e&&a.has(e))).length>0&&r.push({node:e,pos:t}),a.size!==r.length)),r}}),i("4oXlU",function(t,r){e(t.exports,"isEmptyDocument",()=>a);function a(e){let t=e.content.firstChild;return 1===e.childCount&&!!t&&!!t&&"paragraph"===t.type.name&&!t.childCount}}),i("erkez",function(t,r){e(t.exports,"findNodePosByLocalIds",()=>a);let a=(e,t,r={})=>{if(0===t.length)return[];let a=[],o=new Set(t);return r.includeDocNode&&o.has(e.doc.attrs?.localId)&&a.push({node:e.doc,pos:0}),e.doc.descendants((e,t)=>(o.has(e.attrs?.localId)&&a.push({node:e,pos:t}),o.size!==a.length)),a}}),i("XtzgJ",function(t,r){e(t.exports,"toJSON",()=>o);let a=new(n("h9yJL")).JSONTransformer;function o(e){return a.encode(e)}}),i("auTg8",function(r,a){e(r.exports,"useEditorContext",()=>s),e(r.exports,"default",()=>d);var o=n("7UHDa"),i=n("gwFzn");let s=()=>t(i).useContext(n("jZrBc").EditorContext);class d extends t(i).Component{getChildContext(){return{editorActions:this.editorActions}}render(){return(0,o.jsx)(n("jZrBc").EditorContext.Provider,{value:this.getChildContext(),children:this.props.children})}constructor(e){super(e),this.editorActions=void 0,this.editorActions=e.editorActions||new(n("fswVK")).default}}d.childContextTypes={editorActions:t(n("fppBw")).object}}),i("jZrBc",function(r,a){e(r.exports,"EditorContext",()=>o);let o=t(n("gwFzn")).createContext({})}),i("6DQRK",function(t,r){function a(e){try{return JSON.parse(e)}catch(e){return}}function o(e){return{...(0,n("9ciHB").normalizeFeatureFlags)(e),catchAllTracking:!1,showAvatarGroupAsPlugin:!!("boolean"==typeof e?.showAvatarGroupAsPlugin&&e?.showAvatarGroupAsPlugin),errorBoundaryDocStructure:!!("boolean"==typeof e?.useErrorBoundaryDocStructure&&e?.useErrorBoundaryDocStructure),synchronyErrorDocStructure:!!("boolean"==typeof e?.synchronyErrorDocStructure&&e?.synchronyErrorDocStructure),enableViewUpdateSubscription:!!("boolean"==typeof e?.enableViewUpdateSubscription&&e?.enableViewUpdateSubscription),collabAvatarScroll:!!("boolean"==typeof e?.collabAvatarScroll&&e?.collabAvatarScroll),twoLineEditorToolbar:!!("boolean"==typeof e?.twoLineEditorToolbar&&e?.twoLineEditorToolbar),disableSpellcheckByBrowser:e?.disableSpellcheckByBrowser?"object"==typeof e?.disableSpellcheckByBrowser?e?.disableSpellcheckByBrowser:"string"==typeof e?.disableSpellcheckByBrowser?a(e?.disableSpellcheckByBrowser):void 0:e?.["disable-spellcheck-by-browser"]?"object"==typeof e?.["disable-spellcheck-by-browser"]?e?.["disable-spellcheck-by-browser"]:"string"==typeof e?.["disable-spellcheck-by-browser"]?a(e?.["disable-spellcheck-by-browser"]):void 0:void 0}}e(t.exports,"createFeatureFlagsFromProps",()=>o)}),i("7lreV",function(t,r){e(t.exports,"default",()=>a);var a={EDITOR_MOUNTED:"Editor Component Mount Time",PROSEMIRROR_RENDERED:"ProseMirror Render Time",PROSEMIRROR_CONTENT_RENDERED:"ProseMirror Content Render Time",ON_EDITOR_READY_CALLBACK:"onEditorReady Callback Duration"}}),i("75KVc",function(t,r){e(t.exports,"name",()=>a),e(t.exports,"version",()=>o);let a="platform-pkg",o="0.0.0-use.local"}),i("eqcbK",function(r,a){e(r.exports,"EditorINPMetrics",()=>s);var o=n("gwFzn"),i=n("2jjxD");let s=()=>{let e=(0,n("inPa6").useAnalyticsEvents)();return(0,o.useEffect)(()=>{let t;let r=l(()=>{t=(0,n("aCbFD").setupINPTracking)(({value:t})=>{let r=(0,n("4u5NT").getActiveInteraction)(),a=r?.ufoName;d(e.createAnalyticsEvent,t,a)})});return()=>{r(),t?.()}},[]),null},d=t(i)((e,t,r)=>{(0,n("ajtqX").fireAnalyticsEvent)(e)({payload:{action:"inp",actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,eventType:n("d925B").EVENT_TYPE.TRACK,attributes:{inp:t,ufoName:r}}})},1e3,{trailing:!0}),l=e=>{if("function"==typeof window.requestIdleCallback){let t=window.requestIdleCallback(e);return()=>window.cancelIdleCallback(t)}let t=window.setTimeout(e,0);return()=>window.clearTimeout(t)}}),i("aCbFD",function(t,r){e(t.exports,"setupINPTracking",()=>o);var a=n("3mTvL");let o=e=>{if(i())return(0,n("2CrBA").onINP)(t=>{e({value:t.value})})},i=()=>!!(!(!window||void 0!==a&&a?.env?.REACT_SSR)&&"PerformanceEventTiming"in window&&"interactionId"in PerformanceEventTiming.prototype&&(PerformanceObserver.supportedEntryTypes.includes("event")||PerformanceObserver.supportedEntryTypes.includes("first-input")))}),i("2CrBA",function(t,r){e(t.exports,"onINP",()=>a);let a=e=>{let t={value:0,delta:0,entries:[]},r=(0,n("bH22n").bindReporter)(e),a=new(n("8z7gv")).InteractionManager,i=e=>{(0,n("c3PW0").whenIdle)(()=>{e.forEach(e=>a.processInteractionEntry(e));let o=a.estimateP98LongestInteraction();o&&o.latency!==t.value&&(t.value=o.latency,t.entries=e,r(t))})},s=o(i),d=(0,n("1UCry").onHidden)(()=>{i(s.takeRecords()),r(t)});return()=>{s.disconnect(),a.cleanup(),d()}},o=e=>{let t=new PerformanceObserver(t=>{Promise.resolve().then(()=>{e(t.getEntries())})});return PerformanceObserver.supportedEntryTypes.includes("event")&&t.observe({type:"event",buffered:!0,durationThreshold:40}),PerformanceObserver.supportedEntryTypes.includes("first-input")&&t.observe({type:"first-input",buffered:!0}),t}}),i("bH22n",function(t,r){e(t.exports,"bindReporter",()=>a);let a=e=>{let t,r;return a=>{a.value>=0&&((r=a.value-(t||0))||void 0===t)&&(t=a.value,a.delta=r,e(a))}}}),i("8z7gv",function(t,r){e(t.exports,"InteractionManager",()=>a);class a{cleanup(){this.interactionCountPolyfill.cleanup()}estimateP98LongestInteraction(){let e=Math.min(this.longestInteractionList.length-1,Math.floor(this.interactionCountPolyfill.getInteractionCount()/50));return this.longestInteractionList[e]}processInteractionEntry(e){if(!(e.interactionId||"first-input"===e.entryType))return;let t=this.longestInteractionList[this.longestInteractionList.length-1],r=this.longestInteractionMap.get(e.interactionId);if(r||this.longestInteractionList.length<a.MAX_INTERACTIONS_TO_CONSIDER||e.duration>t.latency){if(r)e.duration>r.latency?(r.entries=[e],r.latency=e.duration):e.duration===r.latency&&e.startTime===r.entries[0].startTime&&r.entries.push(e);else{let t={id:e.interactionId,latency:e.duration,entries:[e]};this.longestInteractionMap.set(t.id,t),this.longestInteractionList.push(t)}this.longestInteractionList.sort((e,t)=>t.latency-e.latency),this.longestInteractionList.length>a.MAX_INTERACTIONS_TO_CONSIDER&&this.longestInteractionList.splice(a.MAX_INTERACTIONS_TO_CONSIDER).forEach(e=>this.longestInteractionMap.delete(e.id))}}constructor(){this.longestInteractionList=void 0,this.longestInteractionMap=void 0,this.interactionCountPolyfill=void 0,this.longestInteractionList=[],this.longestInteractionMap=new Map,this.interactionCountPolyfill=new(n("dXj5z")).InteractionCountPolyfill}}a.MAX_INTERACTIONS_TO_CONSIDER=10}),i("dXj5z",function(t,r){e(t.exports,"InteractionCountPolyfill",()=>a);class a{cleanup(){this.po?.disconnect()}updateEstimate(e){e.forEach(e=>{e.interactionId&&(this.minKnownInteractionId=Math.min(this.minKnownInteractionId,e.interactionId),this.maxKnownInteractionId=Math.max(this.maxKnownInteractionId,e.interactionId),this.interactionCountEstimate=this.maxKnownInteractionId?(this.maxKnownInteractionId-this.minKnownInteractionId)/7+1:0)})}getInteractionCount(){return this.po?this.interactionCountEstimate:performance.interactionCount||0}constructor(){if(this.interactionCountEstimate=0,this.minKnownInteractionId=1/0,this.maxKnownInteractionId=0,this.po=void 0,"interactionCount"in performance||this.po||!PerformanceObserver.supportedEntryTypes.includes("event"))return;this.po=new PerformanceObserver(e=>{Promise.resolve().then(()=>{this.updateEstimate(e.getEntries())})}),this.po.observe({type:"event",buffered:!0,durationThreshold:0})}}}),i("1UCry",function(t,r){e(t.exports,"onHidden",()=>a);let a=e=>{let t=()=>{"hidden"===document.visibilityState&&e()};return document.addEventListener("visibilitychange",t),()=>{document.removeEventListener("visibilitychange",t)}}}),i("c3PW0",function(t,r){e(t.exports,"whenIdle",()=>a);let a=e=>{let t=window.requestIdleCallback||window.setTimeout,r=-1;if(e=o(e),"hidden"===document.visibilityState)e();else{let a=(0,n("1UCry").onHidden)(()=>{e(),a()});r=t(()=>{e(),a()})}return r},o=e=>{let t=!1;return()=>{t||(e(),t=!0)}}}),i("blhF9",function(t,r){e(t.exports,"EditorInternal",()=>i);var a=n("gwFzn");let o=(0,n("3jLHL").css)({position:"relative",width:"100%",height:"100%"}),i=(0,a.memo)(({props:e,handleAnalyticsEvent:t,createAnalyticsEvent:r,handleSave:i,editorActions:s,providerFactory:d,onEditorCreated:l,onEditorDestroyed:c,preset:p,AppearanceComponent:u})=>{let m={...e,onSave:e.onSave?i:void 0,analyticsHandler:void 0},h=(0,n("6DQRK").createFeatureFlagsFromProps)(e.featureFlags),g=!(0,n("dh538").fg)("platform_editor_disable_rerender_tracking_jira")&&!h.lcmPreventRenderTracking,[b,f]=(0,n("7nd6h").usePortalProvider)(),[x,v]=(0,n("7nd6h").usePortalProvider)();return(0,n("3jLHL").jsx)(a.Fragment,null,g&&(0,n("3jLHL").jsx)(n("2oRGU").RenderTracking,{componentProps:e,action:n("d925B").ACTION.RE_RENDERED,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,handleAnalyticsEvent:t,propsToIgnore:["defaultValue"],useShallow:!1}),(0,n("3jLHL").jsx)(n("hkDEL").default,{errorTracking:!0,createAnalyticsEvent:r,contextIdentifierProvider:e.contextIdentifierProvider,featureFlags:h},(0,n("3jLHL").jsx)("div",{css:o},(0,n("3jLHL").jsx)(n("auTg8").default,{editorActions:s},(0,n("3jLHL").jsx)(n("f8zg2").IntlProviderIfMissingWrapper,null,(0,n("3jLHL").jsx)(a.Fragment,null,(0,n("3jLHL").jsx)(n("bn5lP").default,{editorProps:m,createAnalyticsEvent:r,portalProviderAPI:b,nodeViewPortalProviderAPI:x,providerFactory:d,onEditorCreated:l,onEditorDestroyed:c,disabled:e.disabled,preset:p,render:({editor:t,view:r,eventDispatcher:a,config:o,dispatchAnalyticsEvent:l,editorRef:c,editorAPI:m})=>(0,n("3jLHL").jsx)(n("lJ3BR").BaseThemeWrapper,{baseFontSize:(0,n("jTtEd").getBaseFontSize)(e.appearance)},(0,n("3jLHL").jsx)(u,{innerRef:c,editorAPI:m,appearance:e.appearance,disabled:e.disabled,editorActions:s,editorDOMElement:t,editorView:r,providerFactory:d,eventDispatcher:a,dispatchAnalyticsEvent:l,maxHeight:e.maxHeight,minHeight:e.minHeight,onSave:e.onSave?i:void 0,onCancel:e.onCancel,popupsMountPoint:e.popupsMountPoint,popupsBoundariesElement:e.popupsBoundariesElement,popupsScrollableElement:e.popupsScrollableElement,contentComponents:o.contentComponents,primaryToolbarComponents:o.primaryToolbarComponents,primaryToolbarIconBefore:e.primaryToolbarIconBefore,secondaryToolbarComponents:o.secondaryToolbarComponents,customContentComponents:e.contentComponents,customPrimaryToolbarComponents:e.primaryToolbarComponents,customSecondaryToolbarComponents:e.secondaryToolbarComponents,contextPanel:e.contextPanel,collabEdit:e.collabEdit,persistScrollGutter:e.persistScrollGutter,enableToolbarMinWidth:e.featureFlags?.toolbarMinWidthOverflow!=null?!!e.featureFlags?.toolbarMinWidthOverflow:e.allowUndoRedoButtons,useStickyToolbar:e.useStickyToolbar,featureFlags:h,pluginHooks:o.pluginHooks,__livePage:e.__livePage,preset:p}))}),(0,n("3jLHL").jsx)(f,null),(0,n("3jLHL").jsx)(v,null)))))))})}),i("7nd6h",function(t,r){e(t.exports,"usePortalProvider",()=>o);var a=n("gwFzn");function o(){let e=(0,a.useMemo)(()=>new(n("fqraH")).PortalManager,[]),t=(0,a.useMemo)(()=>(0,n("Qzrjc").createPortalRendererComponent)(e),[e]),r=(0,a.useMemo)(()=>(0,n("Qzrjc").getPortalProviderAPI)(e),[e]);return(0,a.useEffect)(()=>()=>{r.destroy()},[e,r]),[r,t]}}),i("Qzrjc",function(t,r){e(t.exports,"createPortalRendererComponent",()=>s),e(t.exports,"getPortalProviderAPI",()=>l);var a=n("7UHDa"),o=n("gwFzn"),i=n("4FhhO");function s(e){return function(){let[t,r]=(0,o.useState)(e.getBuckets());(0,o.useLayoutEffect)(()=>(e.registerPortalRenderer(r),()=>{e.unregisterPortalRenderer()}),[]);let i=(0,o.useMemo)(()=>t.map((t,r)=>(0,a.jsx)(n("GD6Gl").PortalBucket,{id:r,portalManager:e},r)),[t]);return(0,a.jsx)(a.Fragment,{children:i})}}let d=(0,o.memo)(({getChildren:e,onBeforeRender:t})=>((0,o.useLayoutEffect)(()=>{t&&t()},[t]),(0,a.jsx)(a.Fragment,{children:e()})));d.displayName="PortalRenderWrapper";let l=e=>{let t=new Map;return{render:(r,o,n,s)=>{if("function"==typeof s){let l=(0,i.createPortal)((0,a.jsx)(d,{getChildren:r,onBeforeRender:s}),o,n);t.set(n,e.registerPortal(n,l))}else{let a=(0,i.createPortal)(r(),o,n);t.set(n,e.registerPortal(n,a))}},remove:e=>{t.get(e)?.(),t.delete(e)},destroy:()=>{t.clear(),e.destroy()}}}}),i("GD6Gl",function(t,r){e(t.exports,"PortalBucket",()=>i);var a=n("7UHDa"),o=n("gwFzn");function i({id:e,portalManager:t}){let[r,n]=(0,o.useState)({});(0,o.useLayoutEffect)(()=>(t.registerBucket(e,n),()=>{t.unregisterBucket(e)}),[e,t]);let i=(0,o.useMemo)(()=>Object.values(r),[r]);return(0,a.jsx)(a.Fragment,{children:i})}}),i("fqraH",function(t,r){function a(e){return{portals:{},capacity:e,updater:null}}e(t.exports,"PortalManager",()=>o);class o{getCurrentBucket(){return this.availableBuckets.values().next().value}createBucket(){let e=this.getCurrentBucket();if(this.buckets[e].capacity>0||(this.availableBuckets.delete(e),this.availableBuckets.size>0))return;let t=Math.floor(this.buckets.length*this.scaleRatio);this.buckets=[...this.buckets];for(let e=0;e<t;e++)this.buckets.push(a(this.maxBucketCapacity)),this.availableBuckets.add(this.buckets.length-1);this.portalRendererUpdater?.(this.buckets)}getBuckets(){return this.buckets}registerBucket(e,t){this.buckets[e].updater=t,this.buckets[e].updater?.(()=>({...this.buckets[e].portals}))}unregisterBucket(e){this.buckets[e].updater=null}updateBuckets(e){this.buckets[e].updater?.(()=>({...this.buckets[e].portals}))}registerPortal(e,t){this.createBucket(),this.buckets[this.getCurrentBucket()].capacity-=1;let r=this.portalToBucketMap.get(e)??this.getCurrentBucket();return this.portalToBucketMap.set(e,r),this.buckets[r].portals[e]!==t&&(this.buckets[r].portals[e]=t,this.updateBuckets(r)),()=>{delete this.buckets[r].portals[e],this.portalToBucketMap.delete(e),this.buckets[r].capacity+=1,this.buckets[r].capacity>this.scaleCapacityThreshold&&this.availableBuckets.add(r),this.updateBuckets(r)}}registerPortalRenderer(e){this.portalRendererUpdater||e(()=>this.buckets),this.portalRendererUpdater=e}unregisterPortalRenderer(){this.portalRendererUpdater=null}destroy(){this.buckets.forEach((e,t)=>{e.portals={},e.updater=null,this.availableBuckets.add(t)}),this.portalToBucketMap.clear(),this.portalRendererUpdater=null,this.availableBuckets=new Set(this.buckets.map((e,t)=>t))}constructor(e=50,t=50,r=.5){this.maxBucketCapacity=void 0,this.scaleRatio=void 0,this.buckets=void 0,this.availableBuckets=void 0,this.portalToBucketMap=void 0,this.portalRendererUpdater=void 0,this.scaleCapacityThreshold=void 0,this.maxBucketCapacity=t,this.scaleRatio=r,this.buckets=Array.from({length:e},()=>a(t)),this.portalToBucketMap=new Map,this.availableBuckets=new Set(Array.from({length:e},(e,t)=>t)),this.portalRendererUpdater=null,this.scaleCapacityThreshold=t/2}}}),i("hkDEL",function(r,a){e(r.exports,"default",()=>l);var o=n("7UHDa"),i=n("gwFzn"),s=n("9HkI0");class d extends t(i).Component{componentDidCatch(e,t){this.state.error||(this.props.errorTracking&&this.sendErrorData({error:e,errorInfo:t,errorStack:e.stack}),this.setState({error:e},()=>{if(this.props.rethrow)throw e}))}render(){return(0,o.jsx)(n("kckFS").IntlErrorBoundary,{children:this.props.children})}constructor(e){super(e),this.featureFlags=void 0,this.browserExtensions=void 0,this.state={error:void 0},this.sendErrorData=async e=>{let r=await this.getProductName(),{error:a,errorInfo:o}=e,i=t(s)(),d=window?.navigator?.userAgent||"unknown",l={product:r,browserInfo:d,error:a.toString(),errorInfo:o,errorId:i,browserExtensions:this.browserExtensions,docStructure:this.featureFlags.errorBoundaryDocStructure&&this.props.editorView?(0,n("56Wjx").getDocStructure)(this.props.editorView.state.doc,{compact:!0}):void 0,outdatedBrowser:(0,n("iStJM").isOutdatedBrowser)(d)};this.fireAnalyticsEvent({action:n("d925B").ACTION.EDITOR_CRASHED,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,eventType:n("d925B").EVENT_TYPE.OPERATIONAL,attributes:l}),this.fireAnalyticsEvent({action:n("d925B").ACTION.EDITOR_CRASHED_ADDITIONAL_INFORMATION,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,eventType:n("d925B").EVENT_TYPE.OPERATIONAL,attributes:{errorId:i}}),(0,n("hWRJP").logException)(a,{location:"editor-core/create-editor",product:r})},this.getProductName=async()=>{let{contextIdentifierProvider:e}=this.props;if(e){let t=await e;if(t.product)return t.product}return"atlaskit"},this.fireAnalyticsEvent=e=>{this.props.createAnalyticsEvent?.(e).fire(n("ajtqX").editorAnalyticsChannel)},this.featureFlags=e.featureFlags}}d.defaultProps={rethrow:!0,errorTracking:!0};var l=(0,n("8DdhL").WithEditorView)(d)}),i("56Wjx",function(t,r){e(t.exports,"getDocStructure",()=>n);let a={nodes:{doc:"doc",paragraph:"p",text:"t",bulletList:"ul",orderedList:"ol",listItem:"li",heading:"h",blockquote:"blockq",codeBlock:"codebl",panel:"pnl",rule:"rl",hardBreak:"br",mention:"ment",emoji:"emj",image:"img",caption:"cap",media:"media",mediaGroup:"mediag",mediaSingle:"medias",plain:"pln",table:"table",tableCell:"td",tableHeader:"th",tableRow:"tr",decisionList:"dl",decisionItem:"di",taskList:"tl",taskItem:"ti",extension:"ext",inlineExtension:"exti",bodiedExtension:"extb",multiBodiedExtension:"extmbe",extensionFrame:"extfrm",status:"sts",placeholder:"plh",inlineCard:"cardi",blockCard:"cardb",embedCard:"carde",expand:"exp",nestedExpand:"expn",unsupportedBlock:"unsupb",unsupportedInline:"unsupi",unknownBlock:"unkb",date:"date"},marks:{em:"em",strong:"strong",code:"code",strike:"strike",underline:"undline",link:"lnk",subsup:"subsup",textColor:"txtclr",unsupportedMark:"unsupmrk",unsupportedNodeAttribute:"unsupnattr",annotation:"anno"}};function o(e,t){return a[t?"marks":"nodes"][e]||e}let n=(e,t)=>{try{let r=i(e,0);if(t?.compact)return function e(t){var r;let a;let n=!t.content,i=t?.type==="text",s=t.marks?.length,d=Array.isArray(t.content);return i?a=String(t.nodeSize):n?a="":d&&(a=t.content.map(t=>e(t)).join(",")),r=`${o(t.type,!1)}(${a})`,s?t.marks.reduce((e,t)=>`${o(t,!0)}(${e})`,r):r}(r);return r}catch(e){return`Error logging document structure: ${e}`}},i=(e,t)=>{let r={type:e.type.name,pos:t,nodeSize:e.nodeSize},a=s(e.content,t);a.length>0&&(r.content=a);let o=l(e);return o.length>0&&(r.marks=o),r},s=(e,t)=>{if(!e||!e.content||!e.content.length)return[];let r=[],{content:a}=e;if(a[0].isBlock){let e;r=a.map(r=>(t+=e?e.nodeSize:1,e=r,i(r,t)))}else{let e=d(a,t);r=e.inlineNodes,t=e.pos}return r},d=(e,t)=>({inlineNodes:e.map(e=>{let{nodeSize:r}=e,a={type:e.type.name,pos:t,nodeSize:r},o=l(e);return o.length>0&&(a.marks=o),t+=r,a}),pos:t}),l=e=>e.marks.map(e=>e.type.name)}),i("iStJM",function(t,r){e(t.exports,"isOutdatedBrowser",()=>a);let a=e=>{let t=/Chrome\//.test(e)&&!/OPR\//.test(e);if((t?parseInt((e.match(/Chrome\/(\d+)/)||[])[1],10):0)>=84)return!1;let r=/gecko\/\d/i.test(e);if((r?parseInt((e.match(/Firefox\/(\d+)/)||[])[1],10):0)>=84)return!1;let a=/Edge\/(\d+)/.exec(e);return!((a?+a[1]:0)>=84||(!t&&!r&&/Version\/([0-9\._]+).*Safari/.test(e)?parseInt((e.match(/Version\/([0-9\._]+).*Safari/)||[])[1],10):0)>=12)}}),i("8DdhL",function(t,r){e(t.exports,"WithEditorView",()=>o);var a=n("7UHDa");n("gwFzn");let o=e=>t=>{let{editorActions:r}=(0,n("auTg8").useEditorContext)();return(0,a.jsx)(e,{...t,editorView:r?._privateGetEditorView()})}}),i("bn5lP",function(r,a){e(r.exports,"default",()=>c);var o=n("7UHDa"),i=n("gwFzn"),s=n("kyKWe"),d=n("1oCLl"),l=n("iu6m9"),c=(0,n("js7oX").default)(function(e){let{preset:r,editorProps:{appearance:a,disabled:c,featureFlags:p,errorReporterHandler:u,defaultValue:m,shouldFocus:h,__livePage:g},onEditorCreated:b,onEditorDestroyed:f}=e,[x,v]=(0,i.useState)(void 0),y=(0,i.useRef)(null),E=(0,i.useRef)(),S=(0,i.useRef)(),C=(0,i.useRef)(!0),k=(0,i.useRef)(t(s)()),T=(0,i.useMemo)(()=>new(n("5vVM5")).EventDispatcher,[]),w=(0,i.useRef)({nodes:[],marks:[],pmPlugins:[],contentComponents:[],pluginHooks:[],primaryToolbarComponents:[],secondaryToolbarComponents:[],onEditorViewStateUpdatedCallbacks:[]}),_=(0,i.useRef)(void 0),N=(0,i.useMemo)(()=>(0,n("6DQRK").createFeatureFlagsFromProps)(p),[p]),L=(0,i.useCallback)(()=>E.current?.state,[]),$=(0,i.useCallback)(()=>E.current,[]),R=(0,i.useMemo)(()=>(0,n("5vVM5").createDispatch)(T),[T]),A=(0,i.useMemo)(()=>(0,n("4T0J6").createErrorReporter)(u),[u]),I=(0,i.useCallback)(t=>{(0,n("ajtqX").fireAnalyticsEvent)(e.createAnalyticsEvent)(t)},[e.createAnalyticsEvent]),F=(0,i.useCallback)(e=>{(0,n("5vVM5").createDispatch)(T)(n("lWghV").analyticsEventKey,{payload:e})},[T]),P=(0,i.useRef)(new(n("jsk1R")).EditorPluginInjectionAPI({getEditorState:L,getEditorView:$,fireAnalyticsEvent:I}));(0,i.useLayoutEffect)(()=>{(0,n("dh538").fg)("platform_editor_setup_editorapi_sync")||v(P.current.api())},[]);let O=(0,i.useCallback)(t=>{let r,a,o;if(E.current){if(!t.resetting)return console.warn("The editor does not support changing the schema dynamically."),E.current.state;r=E.current.state.schema}else w.current=(0,n("4T0J6").processPluginsList)((0,n("1B55v").default)(t.props.preset,e.editorProps,P.current)),r=(0,n("a0rZe").createSchema)(w.current),(0,n("dh538").fg)("platform_editor_setup_editorapi_sync")&&v(P.current.api());let{contentTransformerProvider:i}=t.props.editorProps,s=(0,n("4T0J6").createPMPlugins)({schema:r,dispatch:R,errorReporter:A,editorConfig:w.current,eventDispatcher:T,providerFactory:t.props.providerFactory,portalProviderAPI:e.portalProviderAPI,nodeViewPortalProviderAPI:e.nodeViewPortalProviderAPI,dispatchAnalyticsEvent:F,featureFlags:N,getIntl:()=>e.intl,onEditorStateUpdated:(0,n("dh538").fg)("platform_editor_catch_missing_injection_states")?P.current.onEditorViewUpdated:void 0});_.current=i?i(r):void 0;let d=P.current.api();t.doc&&(a=d?.collabEdit!==void 0&&(0,n("dh538").fg)("editor_load_conf_collab_docs_without_checks")||t.props.editorProps.skipValidation?(0,n("6tl2G").processRawValueWithoutValidation)(r,t.doc,F):(0,n("6tl2G").processRawValue)(r,t.doc,t.props.providerFactory,t.props.editorProps.sanitizePrivateContent,_.current,F));let l=d?.editorViewMode?.sharedState.currentState().mode==="view";if(a){if(l){let e=new(n("7T7aA")).TextSelection(a.resolve(0));return(0,n("7T7aA").EditorState).create({schema:r,plugins:s,doc:a,selection:e})}o=t.selectionAtStart?(0,n("7T7aA").Selection).atStart(a):(0,n("7T7aA").Selection).atEnd(a)}let c=o&&(0,n("7T7aA").Selection).findFrom(o.$head,-1,!0)||void 0;return(0,n("7T7aA").EditorState).create({schema:r,plugins:s,doc:a,selection:c})},[A,N,e.intl,e.portalProviderAPI,e.nodeViewPortalProviderAPI,e.editorProps,F,T,R]),D=(0,i.useMemo)(()=>O({props:e,doc:m,selectionAtStart:(0,n("geLSP").isFullPage)(a)}),[]),B=(0,i.useCallback)(()=>E.current?.state??D,[D]),M=(0,i.useCallback)(()=>{if(!E.current)return;E.current.dom instanceof HTMLElement&&E.current.hasFocus()&&E.current.dom.blur();let e=E.current.root.getSelection();e&&e.removeAllRanges()},[]),H=(0,i.useCallback)(({doc:t,shouldScrollToBottom:r})=>{if(!E.current)return;M();let a=O({props:e,doc:t,resetting:!0,selectionAtStart:!r});E.current.updateState(a),e.editorProps.onChange?.(E.current,{source:"local",isDirtyChange:!1})},[M,O,e]);(0,n("9HtP4").default)(()=>{T.on(n("lWghV").analyticsEventKey,I),T.on("resetEditorState",H),F({action:n("d925B").ACTION.STARTED,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,attributes:{platform:n("e2wMq").PLATFORMS.WEB,featureFlags:N?(0,n("9ciHB").getEnabledFeatureFlagKeys)(N):[],accountLocale:e.intl?.locale,browserLocale:window.navigator.language},eventType:n("d925B").EVENT_TYPE.UI})}),(0,i.useLayoutEffect)(()=>(C.current=!0,()=>{C.current=!1}),[]),(0,i.useLayoutEffect)(()=>()=>{let e=S.current;if(e&&clearTimeout(e),E.current){let e=E.current.state;e.plugins.forEach(t=>{let r=t.getState(e);r&&r.destroy&&r.destroy()})}T.destroy()},[T]);let j=(0,i.useCallback)(e=>{if(!E.current)return;M();let t=(0,n("1B55v").default)(e.preset,e.editorProps,P.current);w.current=(0,n("4T0J6").processPluginsList)(t);let r=E.current.state,a=(0,n("4T0J6").createPMPlugins)({schema:r.schema,dispatch:R,errorReporter:A,editorConfig:w.current,eventDispatcher:T,providerFactory:e.providerFactory,portalProviderAPI:e.portalProviderAPI,nodeViewPortalProviderAPI:e.nodeViewPortalProviderAPI,dispatchAnalyticsEvent:F,featureFlags:N,getIntl:()=>e.intl,onEditorStateUpdated:(0,n("dh538").fg)("platform_editor_catch_missing_injection_states")?P.current.onEditorViewUpdated:void 0}),o=r.reconfigure({plugins:a});return E.current.updateState(o),E.current.update({...E.current.props,state:o})},[M,F,T,R,A,N]),U=(0,i.useCallback)(({originalTransaction:e,transactions:t,oldEditorState:r,newEditorState:a})=>{(0,n("dh538").fg)("platform_editor_catch_missing_injection_states")||P.current.onEditorViewUpdated({newEditorState:a,oldEditorState:r}),(0,n("dh538").fg)("platform_editor_migrate_state_updates")||w.current?.onEditorViewStateUpdatedCallbacks.forEach(o=>{o.callback({originalTransaction:e,transactions:t,oldEditorState:r,newEditorState:a})})},[]),z=(0,n("cUiRv").useDispatchTransaction)({onChange:e.editorProps.onChange,dispatchAnalyticsEvent:F,onEditorViewUpdated:U,isRemoteReplaceDocumentTransaction:P.current.api()?.collabEdit?.actions?.isRemoteReplaceDocumentTransaction}),X=e.editorProps.UNSAFE_cards,W=e.editorProps.smartLinks;(0,n("1FT2u").useProviders)({editorApi:x,contextIdentifierProvider:e.editorProps.contextIdentifierProvider,mediaProvider:e.editorProps.media?.provider,mentionProvider:e.editorProps.mentionProvider,cardProvider:e.editorProps.linking?.smartLinks?.provider||W&&W.provider||X&&X.provider,emojiProvider:e.editorProps.emojiProvider,autoformattingProvider:e.editorProps.autoformattingProvider,taskDecisionProvider:e.editorProps.taskDecisionProvider});let V=(0,i.useCallback)(e=>({state:e??B(),dispatchTransaction:e=>{C.current&&z(E.current,e)},editable:e=>!c,attributes:{"data-gramm":"false"}}),[z,c,B]),G=(0,i.useCallback)(e=>{(0,n("jz9wK").measureRender)(n("7lreV").default.PROSEMIRROR_RENDERED,({duration:e,startTime:t,distortedDuration:r})=>{let a=(0,n("lWghV").getAnalyticsEventSeverity)(e,n("67R1n").PROSEMIRROR_RENDERED_NORMAL_SEVERITY_THRESHOLD,n("67R1n").PROSEMIRROR_RENDERED_DEGRADED_SEVERITY_THRESHOLD);if(E.current){let o=(0,n("hEPfr").getNodesCount)(E.current.state.doc),i=(0,n("8pwxt").getResponseEndTime)(),s=P.current.api().base?.sharedState.currentState();F({action:n("d925B").ACTION.PROSEMIRROR_RENDERED,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,attributes:{duration:e,startTime:t,nodes:o,ttfb:i,severity:a,objectId:s?.objectId,distortedDuration:r},eventType:n("d925B").EVENT_TYPE.OPERATIONAL})}});let t=new(n("jvHoz")).EditorView({mount:e},V());return E.current=t,P.current.onEditorViewUpdated({newEditorState:E.current.state,oldEditorState:void 0}),t},[V,F]),[J,K]=(0,i.useState)(void 0),q=t(i).useRef((0,n("geLSP").isFullPage)(e.editorProps.appearance)&&(0,n("dh538").fg)("platform_editor_reduce_scroll_jump_on_editor_start")?document.querySelector("[data-editor-scroll-container]")?.scrollTop:void 0),Z=(0,n("geLSP").isFullPage)(e.editorProps.appearance)&&(0,n("dh538").fg)("platform_editor_reduce_scroll_jump_on_editor_start")&&q.current&&0!==q.current;(0,i.useLayoutEffect)(()=>{h&&J?.props.editable?.(J.state)&&(0,n("dh538").fg)("platform_editor_react_18_autofocus_fix")&&((0,n("dh538").fg)("platform_editor_reduce_scroll_jump_on_editor_start")?!Z&&((g||(0,d.expValEquals)("platform_editor_no_cursor_on_edit_page_init","isEnabled",!0))&&!(0,n("2pjJ5").isEmptyDocument)(J.state.doc)||(S.current=(0,n("dHwSr").handleEditorFocus)(J)),(0,d.expValEquals)("platform_editor_no_cursor_on_edit_page_init","isEnabled",!0)&&(0,n("dh538").fg)("cc_editor_focus_before_editor_on_load")&&!c&&h&&!(0,n("2pjJ5").isEmptyDocument)(J.state.doc)&&(0,n("imt7Y").focusEditorElement)(k.current)):(g||(0,d.expValEquals)("platform_editor_no_cursor_on_edit_page_init","isEnabled",!0))&&!(0,n("2pjJ5").isEmptyDocument)(J.state.doc)||(S.current=(0,n("dHwSr").handleEditorFocus)(J)))},[J,h,g,Z,c]);let Y=t(i).useRef(),Q=t(i).useRef([]);t(i).useEffect(()=>()=>{if((0,n("dh538").fg)("cc_editor_abort_ufo_load_on_editor_scroll")){if(Y.current)for(let e of Q.current)Y.current?.removeEventListener(...e);Y.current=null}},[]);let ee=(0,i.useCallback)(e=>{if((0,n("dh538").fg)("cc_editor_abort_ufo_load_on_editor_scroll")&&e){Y.current=document.querySelector("[data-editor-scroll-container]");let e=()=>{for(let e of Q.current)Y.current?.removeEventListener(...e)};if(Y.current){let t=()=>{let t=(0,n("4u5NT").getActiveInteraction)();t&&["edit-page","live-edit"].includes(t.ufoName)&&(0,n("4u5NT").abortAll)("new_interaction","wheel-on-editor-element"),e()};Y.current.addEventListener("wheel",t),Q.current.push(["wheel",t]);let r=()=>{let t=(0,n("4u5NT").getActiveInteraction)();t&&["edit-page","live-edit"].includes(t.ufoName)&&(0,n("4u5NT").abortAll)("new_interaction","scroll-on-editor-element"),e()};Y.current.addEventListener("scroll",r),Q.current.push(["scroll",r])}}if(!E.current&&e){(0,l.editorExperiment)("platform_editor_nodevisibility",!0,{exposure:!1})&&(0,n("92LVN").nodeVisibilityManager)(e).initialiseNodeObserver();let r=G(e);if((0,n("dh538").fg)("platform_editor_reduce_scroll_jump_on_editor_start")&&Z){let e=document.querySelector("[data-editor-scroll-container]");e?.scrollTo({top:q.current,behavior:"instant"})}b({view:r,config:w.current,eventDispatcher:T,transformer:_.current}),(0,n("dh538").fg)("platform_editor_react_18_autofocus_fix")?(t(i)?.startTransition??(e=>e()))(()=>{K(r)}):(h&&r.props.editable&&r.props.editable(r.state)&&((0,n("dh538").fg)("platform_editor_reduce_scroll_jump_on_editor_start")?!Z&&(!((g||(0,d.expValEquals)("platform_editor_no_cursor_on_edit_page_init","isEnabled",!0))&&!(0,n("2pjJ5").isEmptyDocument)(r.state.doc))&&h&&r.props.editable&&r.props.editable(r.state)&&(S.current=(0,n("dHwSr").handleEditorFocus)(r)),(0,d.expValEquals)("platform_editor_no_cursor_on_edit_page_init","isEnabled",!0)&&(0,n("dh538").fg)("cc_editor_focus_before_editor_on_load")&&h&&r.props.editable&&r.props.editable(r.state)&&!(0,n("2pjJ5").isEmptyDocument)(r.state.doc)&&(0,n("imt7Y").focusEditorElement)(k.current)):!((g||(0,d.expValEquals)("platform_editor_no_cursor_on_edit_page_init","isEnabled",!0))&&!(0,n("2pjJ5").isEmptyDocument)(r.state.doc))&&h&&r.props.editable&&r.props.editable(r.state)&&(S.current=(0,n("dHwSr").handleEditorFocus)(r))),K(r))}else E.current&&!e&&(f({view:E.current,config:w.current,eventDispatcher:T,transformer:_.current}),T.has(n("lWghV").analyticsEventKey,I)?E.current.destroy():(T.on(n("lWghV").analyticsEventKey,I),E.current.destroy(),T.off(n("lWghV").analyticsEventKey,I)),(0,l.editorExperiment)("platform_editor_nodevisibility",!0)&&(0,n("92LVN").nodeVisibilityManager)(E.current.dom).disconnect(),E.current=void 0)},[G,b,T,h,g,f,I,Z]),et=(0,i.useCallback)((t,r)=>(0,o.jsxs)(o.Fragment,{children:[(0,n("dh538").fg)("cc_editor_focus_before_editor_on_load")&&(0,o.jsx)("div",{tabIndex:-1,"data-focus-id":k.current,"data-testid":"react-editor-view-inital-focus-element"}),(0,o.jsx)("div",{className:`ProseMirror ${(0,n("kbBd7").getUAPrefix)()}`,ref:ee,"aria-label":t||e.intl.formatMessage(n("2q16N").editorMessages.editorAssistiveLabel),"aria-multiline":!0,role:"textbox",id:"ak-editor-textarea","aria-describedby":r,"data-editor-id":k.current,"data-vc-ignore-if-no-layout-shift":!!(0,n("dh538").fg)("platform_vc_ignore_no_ls_mutation_marker")||void 0},"ProseMirror")]}),[ee,e.intl]),er=(0,n("7541v").default)(r);(0,i.useLayoutEffect)(()=>{er&&er!==r&&j(e)},[j,er,r,e]);let ea=(0,n("7541v").default)(c);(0,i.useLayoutEffect)(()=>{if(E.current&&ea!==c){E.current.setProps({editable:e=>!c});let e=(g||(0,d.expValEquals)("platform_editor_no_cursor_on_edit_page_init","isEnabled",!0))&&!(0,n("2pjJ5").isEmptyDocument)(E.current.state.doc);c||!h||e||(S.current=(0,n("dHwSr").handleEditorFocus)(E.current)),(0,d.expValEquals)("platform_editor_no_cursor_on_edit_page_init","isEnabled",!0)&&(0,n("dh538").fg)("cc_editor_focus_before_editor_on_load")&&!c&&h&&!(0,n("2pjJ5").isEmptyDocument)(E.current.state.doc)&&(0,n("imt7Y").focusEditorElement)(k.current)}},[c,h,ea,g]),(0,n("hQcZ1").useFireFullWidthEvent)(a,F);let eo=(0,i.useMemo)(()=>et(e.editorProps.assistiveLabel,e.editorProps.assistiveDescribedBy),[e.editorProps.assistiveLabel,e.editorProps.assistiveDescribedBy]),en=!(0,n("dh538").fg)("platform_editor_disable_rerender_tracking_jira")&&!N.lcmPreventRenderTracking;return(0,o.jsxs)(n("40aJG").default.Provider,{value:{editorRef:y,editorView:E.current,popupsMountPoint:e.editorProps.popupsMountPoint},children:[en&&(0,o.jsx)(n("2oRGU").RenderTracking,{componentProps:e,action:n("d925B").ACTION.RE_RENDERED,actionSubject:n("d925B").ACTION_SUBJECT.REACT_EDITOR_VIEW,handleAnalyticsEvent:I,useShallow:!0}),e.render?e.render?.({editor:eo,view:E.current,config:w.current,eventDispatcher:T,transformer:_.current,dispatchAnalyticsEvent:F,editorRef:y,editorAPI:x})??eo:eo]})})}),i("e2wMq",function(t,r){e(t.exports,"PLATFORMS",()=>s),e(t.exports,"MODE",()=>d),e(t.exports,"FULL_WIDTH_MODE",()=>l),e(t.exports,"BROWSER_FREEZE_INTERACTION_TYPE",()=>c);var a,o,n,i,s=((a={}).NATIVE="mobileNative",a.HYBRID="mobileHybrid",a.WEB="web",a),d=((o={}).RENDERER="renderer",o.EDITOR="editor",o),l=((n={}).FIXED_WIDTH="fixedWidth",n.FULL_WIDTH="fullWidth",n),c=((i={}).LOADING="loading",i.TYPING="typing",i.CLICKING="clicking",i.PASTING="pasting",i)}),i("9HtP4",function(t,r){e(t.exports,"default",()=>o);var a=n("gwFzn");function o(e){let t=(0,a.useRef)(!1);t.current||(e(),t.current=!0)}}),i("7541v",function(t,r){e(t.exports,"default",()=>o);var a=n("gwFzn");function o(e,t){let r=(0,a.useRef)(t);return(0,a.useEffect)(()=>{r.current=e},[e]),r.current}}),i("jsk1R",function(r,a){e(r.exports,"EditorPluginInjectionAPI",()=>g);var o=n("atveb"),i=n("eEhUN");function s(e){return"function"==typeof e.getSharedState}let d=({listeners:e,plugins:t})=>Array.from(e.keys()).map(e=>t.get(e)).filter(e=>void 0!==e&&s(e)),l=({oldEditorState:e,newEditorState:r,plugins:a})=>{let n=!e&&r,i=new Map;for(let d of a){if(!d||!s(d))continue;let a=d.getSharedState(r),l=!n&&e?d.getSharedState(e):void 0,c=t(o)(l,a);(n||!c)&&i.set(d.name,{nextSharedState:a,prevSharedState:l})}return i},c=t(i)(({listeners:e,updatesToNotifyQueue:t})=>{let r=[];for(let[a,o]of t.entries())(e.get(a)||[]).forEach(e=>{o.forEach(t=>{r.push(e.bind(e,t))})});t.clear(),0!==r.length&&r.reverse().forEach(e=>{e()})},0);class p{createAPI(e){return e&&"object"==typeof e.actions?new Proxy(e.actions||{},{get:function(e,t,r){return Reflect.get(e,t)}}):{}}}class u{createAPI(e){return e&&"object"==typeof e.commands?new Proxy(e.commands||{},{get:function(e,t,r){return Reflect.get(e,t)}}):{}}}class m{createAPI(e){if(!e)return{currentState:()=>void 0,onChange:e=>()=>{}};let t=e.name;return{currentState:()=>{if(!s(e))return;let t=this.getEditorState();return e.getSharedState(t)},onChange:e=>{let r=this.listeners.get(t)||new Set;return r.add(e),this.listeners.set(t,r),()=>this.cleanupSubscription(t,e)}}}cleanupSubscription(e,t){(this.listeners.get(e)||new Set).delete(t)}notifyListeners({newEditorState:e,oldEditorState:t,plugins:r}){let{listeners:a,updatesToNotifyQueue:o}=this,n=l({oldEditorState:t,newEditorState:e,plugins:d({plugins:r,listeners:a})});if(0!==n.size){for(let[e,t]of n){let r=o.get(e)||[];o.set(e,[...r,t])}c({updatesToNotifyQueue:o,listeners:a})}}destroy(){this.listeners.clear(),this.updatesToNotifyQueue.clear()}constructor({getEditorState:e}){this.getEditorState=void 0,this.listeners=void 0,this.updatesToNotifyQueue=new Map,this.getEditorState=e,this.listeners=new Map}}let h=new WeakMap;class g{createAPI(){let{sharedStateAPI:e,actionsAPI:t,commandsAPI:r,getPluginByName:a}=this;return new Proxy({},{get:function(o,n,i){if("toJSON"===n)return Reflect.get(o,n);let s=a(n);if(!s)return;let d=e.createAPI(s);return{sharedState:d,actions:t.createAPI(s),commands:r.createAPI(s)}}})}api(){return h.get(this)||h.set(this,this.createAPI()),h.get(this)}constructor({getEditorState:e,getEditorView:t,fireAnalyticsEvent:r}){this.sharedStateAPI=void 0,this.actionsAPI=void 0,this.commandsAPI=void 0,this.plugins=void 0,this.onEditorViewUpdated=({newEditorState:e,oldEditorState:t})=>{this.sharedStateAPI.notifyListeners({newEditorState:e,oldEditorState:t,plugins:this.plugins})},this.onEditorPluginInitialized=e=>{this.addPlugin(e)},this.addPlugin=e=>{if("core"===e.name&&this.plugins.has(e.name))throw Error(`Plugin ${e.name} has already been initialised in the Editor API!
        There cannot be duplicate plugins or you will have unexpected behaviour`);this.plugins.set(e.name,e)},this.getPluginByName=e=>this.plugins.get(e),this.sharedStateAPI=new m({getEditorState:e}),this.plugins=new Map,this.actionsAPI=new p,this.commandsAPI=new u,this.addPlugin((0,n("apxVI").corePlugin)({config:{getEditorView:t,fireAnalyticsEvent:r}}))}}}),i("apxVI",function(t,r){e(t.exports,"corePlugin",()=>a);let a=({config:e})=>{let t=(0,n("eqCon").createThrottleSchedule)(n("eqCon").returnDocumentRequest);return{name:"core",actions:{execute:t=>{let r=e?.getEditorView();if(!r||!t)return!1;let{state:a,dispatch:o}=r;return(0,n("gmyMu").editorCommandToPMCommand)(t)(a,o)},focus:t=>{let r=e?.getEditorView();return!(!r||r.hasFocus())&&(r.focus(),(t?.scrollIntoView??!0)&&r.dispatch(r.state.tr.scrollIntoView()),!0)},blur:()=>{let t=e?.getEditorView();return!!(t&&t.hasFocus())&&(t.dom.blur(),!0)},scrollToPos(t,r){let a=e?.getEditorView();if(!a)return!1;let o=a.state.tr;if(!("number"==typeof t&&t>=0&&t<=o.doc.content.size))return!1;let n=a.domAtPos(t).node;return n instanceof Element?(n.scrollIntoView(r),!0):n.parentNode instanceof Element&&(n.parentNode.scrollIntoView(r),!0)},replaceDocument:(t,r)=>{let a=e?.getEditorView();if(!a||null==t)return!1;let{state:o}=a,{schema:i}=o,s=r?.skipValidation?(0,n("6tl2G").processRawValueWithoutValidation)(i,t):Array.isArray(t)?(0,n("6tl2G").processRawFragmentValue)(i,t):(0,n("6tl2G").processRawValue)(i,t);if((0,n("dh538").fg)("platform_editor_replace_document_shortcircuit")&&s instanceof n("kviC1").Node&&o.doc.eq(s))return!1;if(s){let e=o.tr.replaceWith(0,o.doc.nodeSize-2,s);return r?.scrollIntoView??!0?a.dispatch(e.scrollIntoView()):a.dispatch(e),!0}return!1},requestDocument(r,a){t(e?.getEditorView()??null,r,a?.transformer,e?.fireAnalyticsEvent)},createTransformer(t){let r=e?.getEditorView()??null;if(r?.state.schema)return t(r?.state.schema)}}}}}),i("gmyMu",function(t,r){function a(e){return({tr:t},r)=>{let a=e?.({tr:t});return!!a&&(a instanceof o||(r?.(a),!0))}}e(t.exports,"editorCommandToPMCommand",()=>a),e(t.exports,"PassiveTransaction",()=>o);class o extends n("7T7aA").Transaction{constructor(){super({})}}}),i("eqCon",function(t,r){e(t.exports,"createThrottleSchedule",()=>o),e(t.exports,"returnDocumentRequest",()=>i);let a=new(n("h9yJL")).JSONTransformer;function o(e){let t,r;return(...a)=>{r=a,t||(t=(globalThis.requestIdleCallback??globalThis.requestAnimationFrame)(()=>{t=void 0,r&&e(...r)},{timeout:100}))}}function i(e,t,r,o){let{doc:i,schema:s}=e?.state??{};if(i&&s)try{let e=a.encode(i);if(void 0===r)t(e);else{let a=(0,n("kviC1").Node).fromJSON(s,e);t(r.encode(a))}}catch(e){throw o?.({payload:{action:n("d925B").ACTION.DOCUMENT_PROCESSING_ERROR,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,eventType:n("d925B").EVENT_TYPE.OPERATIONAL,attributes:{errorMessage:`${e instanceof Error&&"NodeNestingTransformError"===e.name?"NodeNestingTransformError - Failed to transform one or more nested tables":void 0}`}}}),e}}}),i("40aJG",function(r,a){e(r.exports,"default",()=>o);var o=t(n("gwFzn")).createContext({})}),i("2pjJ5",function(t,r){e(t.exports,"getStepRange",()=>a),e(t.exports,"hasDocAsParent",()=>o),e(t.exports,"isEmptyDocument",()=>i),e(t.exports,"bracketTyped",()=>s),e(t.exports,"nodesBetweenChanged",()=>d),e(t.exports,"hasVisibleContent",()=>function e(t){if(t.isInline)return t.isText?!!t.textContent.trim():"hardBreak"!==t.type.name;if(t.isBlock&&(t.isLeaf||t.isAtom))return!0;if(!t.childCount)return!1;for(let r=0;r<t.childCount;r++){let a=t.child(r);if(!["paragraph","text","hardBreak"].includes(a.type.name)||e(a))return!0}return!1}),e(t.exports,"isSelectionEndOfParagraph",()=>l),e(t.exports,"getChangedNodes",()=>c),e(t.exports,"isReplaceDocOperation",()=>p);let a=e=>{let t=-1,r=-1;return(e.mapping.maps.forEach((a,o)=>{a.forEach((a,n)=>{let i=e.mapping.slice(o).map(a,-1),s=e.mapping.slice(o).map(n);t=i<t||-1===t?i:t,r=s>r||-1===r?s:r})}),-1!==t)?{from:t,to:r}:null};function o(e){return 1===e.depth}function i(e){let t=e.content.firstChild;return 1===e.childCount&&!!t&&(0,n("kTbzR").isEmptyParagraph)(t)}function s(e){let{selection:t}=e,{$cursor:r,$anchor:a}=t;if(!r)return!1;let n=r.nodeBefore;return!!n&&"text"===n.type.name&&"{"===n.text&&0===a.node().marks.length&&o(a)}function d(e,t,r){let o=a(e);o&&e.doc.nodesBetween(o.from,o.to,t,r)}let l=e=>e.selection.$to.parent.type===e.schema.nodes.paragraph&&e.selection.$to.pos===e.doc.resolve(e.selection.$to.pos).end();function c(e){return function({tr:e,doc:t}){let r=[],o=a(e);if(!o)return r;let n=Math.min(t.nodeSize-2,o.from),i=Math.min(t.nodeSize-2,o.to);return t.nodesBetween(n,i,(e,t)=>{r.push({node:e,pos:t})}),r}({tr:e,doc:e.doc})}let p=(e,t)=>e.some(e=>!!e.getMeta("replaceDocument")||e.steps.some(e=>{if(!(e instanceof n("4FvAQ").ReplaceStep))return!1;let r=0===e.from,a=e.to===t.doc.content.size;return!!r&&!!a}))}),i("kTbzR",function(t,r){e(t.exports,"isEmptyParagraph",()=>o),e(t.exports,"stepHasSlice",()=>i),e(t.exports,"stepAddsOneOf",()=>s),e(t.exports,"extractSliceFromStep",()=>d),e(t.exports,"isTextSelection",()=>l),e(t.exports,"isElementInTableCell",()=>c),e(t.exports,"isLastItemMediaGroup",()=>p),e(t.exports,"setNodeSelection",()=>u),e(t.exports,"setTextSelection",()=>m),e(t.exports,"nonNullable",()=>h),e(t.exports,"isValidPosition",()=>g),e(t.exports,"isInLayoutColumn",()=>b),e(t.exports,"filterChildrenBetween",()=>f),e(t.exports,"removeBlockMarks",()=>x);var a=n("gWR1e");function o(e){return!!e&&"paragraph"===e.type.name&&!e.childCount}let i=e=>e&&e.hasOwnProperty("slice");function s(e,t){let r=!1;return i(e)&&e.slice.content.descendants(e=>(t.has(e.type)&&(r=!0),!r)),r}let d=e=>e instanceof n("4FvAQ").ReplaceStep||e instanceof n("4FvAQ").ReplaceAroundStep?e.slice:null,l=e=>e instanceof n("7T7aA").TextSelection,c=e=>(0,n("dh538").fg)("platform_editor_nested_tables_column_drag_fix")?(0,n("4vlwG").closest)(e,"td, th"):(0,n("4vlwG").closest)(e,"td")||(0,n("4vlwG").closest)(e,"th"),p=e=>{let{content:t}=e;return!!t.lastChild&&"mediaGroup"===t.lastChild.type.name},u=(e,t)=>{let{state:r,dispatch:a}=e;isFinite(t)&&a(r.tr.setSelection((0,n("7T7aA").NodeSelection).create(r.doc,t)))};function m(e,t,r){let{state:a,dispatch:o}=e;o(a.tr.setSelection((0,n("7T7aA").TextSelection).create(a.doc,t,r)))}function h(e){return null!=e}let g=(e,t)=>"number"==typeof e&&!!(e>=0&&e<=t.doc.resolve(0).end()),b=e=>(0,a.hasParentNodeOfType)(e.schema.nodes.layoutSection)(e.selection);function f(e,t,r,a){let o=[];return e.nodesBetween(t,r,(e,t,r)=>{a(e,t,r)&&o.push({node:e,pos:t})}),o}let x=(e,t)=>{let{selection:r,schema:a}=e,{tr:o}=e,n=t.filter(Boolean);if(0===n.length)return;let i=!1,s=e=>n.indexOf(e.type)>-1;return e.doc.nodesBetween(r.from,r.to,(t,r)=>{if(t.type===a.nodes.paragraph&&t.marks.some(s)){i=!0;let a=e.doc.resolve(r),n=t.marks.filter(v(s));o=o.setNodeMarkup(a.pos,void 0,t.attrs,n)}}),i?o:void 0},v=e=>t=>!e(t)}),i("1FT2u",function(t,r){e(t.exports,"useProviders",()=>o);var a=n("gwFzn");let o=({editorApi:e,contextIdentifierProvider:t,mediaProvider:r,mentionProvider:o,cardProvider:n,emojiProvider:i,autoformattingProvider:s,taskDecisionProvider:d})=>{(0,a.useEffect)(()=>{(async function(){if(!t)return;let r=await t;e?.core?.actions.execute(e?.contextIdentifier?.commands.setProvider({contextIdentifierProvider:r}))})()},[t,e]),(0,a.useEffect)(()=>{r&&e?.media?.actions.setProvider(r)},[r,e]),(0,a.useEffect)(()=>{o&&e?.mention?.actions.setProvider(o)},[o,e]),(0,a.useEffect)(()=>{n&&e?.card?.actions.setProvider(n)},[n,e]),(0,a.useEffect)(()=>{i&&e?.emoji?.actions.setProvider(i)},[i,e]),(0,a.useEffect)(()=>{s&&e?.customAutoformat?.actions.setProvider(s)},[s,e]),(0,a.useEffect)(()=>{d&&e?.taskDecision?.actions.setProvider(d)},[d,e])}}),i("hEPfr",function(t,r){e(t.exports,"getNodesCount",()=>a);function a(e){let t={};return e.nodesBetween(0,e.nodeSize-2,e=>{t[e.type.name]=(t[e.type.name]||0)+1}),t}}),i("geLSP",function(t,r){e(t.exports,"isFullPage",()=>a);function a(e){return"full-page"===e||"full-width"===e}}),i("2oRGU",function(r,a){e(r.exports,"RenderTracking",()=>s);var o=n("gwFzn"),i=n("2jjxD");function s(e){let r=(0,o.useMemo)(()=>t(i)(e.handleAnalyticsEvent,500),[e.handleAnalyticsEvent]);return(0,n("h9Yad").useComponentRenderTracking)({onRender:({renderCount:t,propsDifference:a})=>{t&&r({payload:{action:e.action,actionSubject:e.actionSubject,attributes:{count:t,propsDifference:a},eventType:n("d925B").EVENT_TYPE.OPERATIONAL}})},propsDiffingOptions:{enabled:!0,props:e.componentProps,propsToIgnore:e.propsToIgnore,useShallow:e.useShallow},zeroBasedCount:!0}),null}}),i("h9Yad",function(r,a){e(r.exports,"useComponentRenderTracking",()=>s);var o=n("gwFzn"),i=n("kyKWe");function s({onRender:e,propsDiffingOptions:r,zeroBasedCount:a=!0}){let s=(0,o.useRef)(),d=(0,o.useRef)(a?0:1),{current:l}=(0,o.useRef)(t(i)());(0,o.useEffect)(()=>{let t;let a=s.current,o=d.current;r?.enabled&&a&&(t=r?.useShallow?(0,n("ZkPRR").getShallowPropsDifference)(a,r.props):(0,n("ZkPRR").getPropsDifference)(a,r.props,0,2,r?.propsToIgnore)),e({renderCount:o,propsDifference:t,componentId:l}),r?.enabled&&(s.current=r.props),d.current=d.current+1})}}),i("ZkPRR",function(r,a){e(r.exports,"getPropsDifference",()=>l),e(r.exports,"getShallowPropsDifference",()=>c);var o=n("gwFzn");let i=Object.keys,s=(e,t)=>{let r=null!==e?i(e):[],a=null!==t?i(t):[],o=r.filter(e=>!a.includes(e));return{added:a.filter(e=>!r.includes(e)),common:r.filter(e=>a.includes(e)),removed:o}},d=e=>{let t=typeof e;return null===e?"null":void 0===e?"undefined":"string"===t||"number"===t?e:"symbol"===t?e.toString():"function"===t?`function:${e.name}`:"object"===t?{type:"object",keys:Object.keys(e)}:void 0},l=(e,r,a=0,n=2,i=[])=>{let{added:c,common:p,removed:u}=s(e,r),m=[];return p.forEach(s=>{let c=e[s],p=r[s],u=typeof c,h=typeof p;if(c!==p&&-1===i.indexOf(s)){if(t(o).isValidElement(c)||t(o).isValidElement(p))m.push({key:s,reactElementChanged:!0});else if("object"===u&&"object"===h){if(a<=n){let e=l(c,p,a+1,n);m.push({key:s,difference:e})}else m.push({key:s,maxDepthReached:!0})}else m.push({key:s,oldValue:d(c),newValue:d(p)})}}),{added:c,changed:m,removed:u}},c=(e,t)=>{let{added:r,common:a,removed:o}=s(e,t);return{added:r,changed:a.filter(r=>e[r]!==t[r]),removed:o}}}),i("67R1n",function(t,r){e(t.exports,"PROSEMIRROR_RENDERED_NORMAL_SEVERITY_THRESHOLD",()=>a),e(t.exports,"PROSEMIRROR_RENDERED_DEGRADED_SEVERITY_THRESHOLD",()=>o);let a=2e3,o=3e3}),i("4T0J6",function(t,r){function a(e){let t=Object.keys(e),r=new Set(t.map(t=>e[t].group));return t.forEach(t=>{let a=e[t];a.excludes&&(a.excludes=a.excludes.split(" ").filter(e=>r.has(e)).join(" "))}),e}function o(e){let t=e.reduce((e,t)=>(t.pluginsOptions&&Object.keys(t.pluginsOptions).forEach(r=>{e[r]||(e[r]=[]),e[r].push(t.pluginsOptions[r])}),e),{});return e.reduce((e,r)=>(r.pmPlugins&&e.pmPlugins.push(...r.pmPlugins(r.name?t[r.name]:void 0)),r.nodes&&e.nodes.push(...r.nodes()),r.marks&&e.marks.push(...r.marks()),r.contentComponent&&e.contentComponents.push(r.contentComponent),r.usePluginHook&&e.pluginHooks.push(r.usePluginHook),r.primaryToolbarComponent&&e.primaryToolbarComponents.push(r.primaryToolbarComponent),r.secondaryToolbarComponent&&e.secondaryToolbarComponents.push(r.secondaryToolbarComponent),r.onEditorViewStateUpdated&&e.onEditorViewStateUpdatedCallbacks.push({pluginName:r.name,callback:r.onEditorViewStateUpdated}),e),{nodes:[],marks:[],pmPlugins:[],contentComponents:[],pluginHooks:[],primaryToolbarComponents:[],secondaryToolbarComponents:[],onEditorViewStateUpdatedCallbacks:[]})}function i(e){let{editorConfig:t}=e,r=t.pmPlugins.sort((0,n("2oGxU").sortByOrder)("plugins")).map(({plugin:t})=>t({schema:e.schema,dispatch:e.dispatch,eventDispatcher:e.eventDispatcher,providerFactory:e.providerFactory,errorReporter:e.errorReporter,portalProviderAPI:e.portalProviderAPI,nodeViewPortalProviderAPI:e.nodeViewPortalProviderAPI,dispatchAnalyticsEvent:e.dispatchAnalyticsEvent,featureFlags:e.featureFlags||{},getIntl:e.getIntl})).filter(e=>void 0!==e);return void 0!==e.onEditorStateUpdated?[(0,n("9CUJY").createEditorStateNotificationPlugin)(e.onEditorStateUpdated,e.editorConfig.onEditorViewStateUpdatedCallbacks),...r]:r}function s(e){let t=new(n("dSVmA")).ErrorReporter;return e&&(t.handler=e),t}e(t.exports,"fixExcludes",()=>a),e(t.exports,"processPluginsList",()=>o),e(t.exports,"createPMPlugins",()=>i),e(t.exports,"createErrorReporter",()=>s)}),i("dSVmA",function(t,r){e(t.exports,"ErrorReporter",()=>a);class a{captureMessage(e,t){this.handlerStorage&&this.handlerStorage.captureMessage(e,t)}captureException(e,t){this.handlerStorage&&this.handlerStorage.captureException(e,t)}set handler(e){this.handlerStorage=e}constructor(){this.handlerStorage=null}}}),i("2oGxU",function(t,r){e(t.exports,"sortByOrder",()=>o),e(t.exports,"sortByOrderWithTypeName",()=>n);let a={plugins:["featureFlagsContextPlugin","compositionPlugin","inlineCursorTargetPlugin","typeAhead","typeAheadInsertItem","focusHandlerPlugin","frozenEditor","submitEditor","saveOnEnter","customAutoformatting","newlinePreserveMarksPlugin","imageUpload","imageUploadInputRule","clipboard","paste","pasteKeymap","mention","mentionInputRule","mentionKeymap","emoji","placeholderText","emojiInputRule","emojiKeymap","emojiAsciiInputRule","blockType","quickInsert","tasksAndDecisions","blockTypeInputRule","tasksAndDecisionsInputRule","list","typeAheadKeymap","typeAheadInputRule","date","dateKeymap","indentationKeymap","textColor","highlight","highlightKeymap","alignmentPlugin","listInputRule","listKeymap","codeBlock","codeBlockIDEKeyBindings","codeBlockKeyMap","textFormatting","textFormattingCursor","textFormattingInputRule","textFormattingSmartRule","textFormattingClear","textFormattingKeymap","tasksAndDecisionsKeyMap","expandKeymap","tableSelectionKeymap","tableKeymap","captionKeymap","mediaKeymap","selectionKeymap","gapCursorKeymap","gapCursor","syncUrlText","fakeCursorToolbarPlugin","hyperLink","table","tableDecorations","hyperlinkInputRule","tablePMColResizing","hyperlinkKeymap","tableColResizing","undoRedoKeyMap","blockTypeKeyMap","tableEditing","filterStepsPlugin","pmCollab","collab","ruleInputRule","ruleKeymap","panel","media","mediaSingleKeymap","mediaEditor","unsupportedContent","jiraIssue","helpDialog","helpDialogKeymap","macro","expand","extension","layout","contextPanel","selectionToolbar","floatingToolbar","clearMarksOnChange","reactNodeView","history","undoRedoPlugin","codeBlockIndent","placeholder","width","maxContentSize","multilineContent","grid","mobileDimensions","scrollGutterPlugin","analytics","findReplace","selection","avatarGroup","viewUpdateSubscription","beforePrimaryToolbar","inlineCode"],nodes:["doc","paragraph","text","bulletList","orderedList","listItem","heading","blockquote","codeBlock","rule","panel","mention","confluenceUnsupportedBlock","confluenceUnsupportedInline","unsupportedBlock","unsupportedInline","confluenceJiraIssue","hardBreak","emoji","placeholder","mediaSingle","mediaGroup","table","expand","nestedExpand","media","tableHeader","decisionList","tableRow","decisionItem","tableCell","taskList","taskItem","extension","bodiedExtension","multiBodiedExtension","inlineExtension","layoutSection","layoutColumn","inlineCard","blockCard","embedCard"],marks:["fragment","link","em","strong","textColor","backgroundColor","strike","subsup","underline","code","typeAheadQuery","alignment","breakout","indentation","annotation","dataConsumer","border","unsupportedMark","unsupportedNodeAttribute"]};function o(e){return function(t,r){return a[e].indexOf(t.name)-a[e].indexOf(r.name)}}function n(e){return function(t,r){return a[e].indexOf(t.type.name)-a[e].indexOf(r.type.name)}}}),i("9CUJY",function(t,r){e(t.exports,"createEditorStateNotificationPlugin",()=>o);let a=new(n("7T7aA")).PluginKey("editorStateNotificationPlugin"),o=(e,t)=>{let r=[];return new(n("1S4f7")).SafePlugin({key:a,state:{init:()=>({latestTransaction:void 0}),apply:e=>(r.push(e),{latestTransaction:e})},view:()=>({update:(o,i)=>{let s=a.getState(o.state)?.latestTransaction;s&&(0,n("dh538").fg)("platform_editor_migrate_state_updates")&&(t.forEach(e=>{e.callback({originalTransaction:s,transactions:r,oldEditorState:i,newEditorState:o.state})}),r=[]),e({oldEditorState:i,newEditorState:o.state})}})})}}),i("1S4f7",function(t,r){e(t.exports,"SafePlugin",()=>i);let a=({nodeOrMark:e,dom:t})=>{Object.entries((0,n("6VsTy").createProseMirrorMetadata)(e)).forEach(([e,r])=>{t.setAttribute(e,r)})},o=e=>{if(!e?.props?.nodeViews)return e;let t=new Proxy(e.props.nodeViews,{get:(e,t,r)=>new Proxy(Reflect.get(e,t,r),{apply(e,t,r){let[o,n,i,...s]=r,d=(()=>{try{return i()}catch(e){}}).bind(t),l=Reflect.apply(e,t,[o,n,d,...s]);return l?.dom instanceof HTMLElement&&a({nodeOrMark:o,dom:l.dom}),l}})});return e.props.nodeViews=t,e};class i extends n("7T7aA").Plugin{constructor(e){super(o(e)),this._isATypeSafePlugin=void 0}}}),i("6VsTy",function(t,r){e(t.exports,"createProseMirrorMetadata",()=>o);let a=e=>e instanceof n("kviC1").Node||Array.isArray(e.marks),o=e=>{let t=e.type.name,r=a(e),o={"data-prosemirror-content-type":r?"node":"mark"};return r?(o["data-prosemirror-node-name"]=t,e.type.isBlock&&(o["data-prosemirror-node-block"]="true"),e.type.isInline&&(o["data-prosemirror-node-inline"]="true"),o):{...o,"data-prosemirror-mark-name":t}}}),i("1B55v",function(t,r){e(t.exports,"getDefaultPresetOptionsFromEditorProps",()=>o),e(t.exports,"default",()=>i);let a=e=>-1===(e&&e.allowBlockType&&e.allowBlockType.exclude?e.allowBlockType.exclude:[]).indexOf("codeBlock");function o(e,t){let r=e.appearance,a=e.linking?.smartLinks||e.smartLinks||e.UNSAFE_cards;return{...e,createAnalyticsEvent:t,typeAhead:{isMobile:!1},featureFlags:(0,n("6DQRK").createFeatureFlagsFromProps)(e.featureFlags),paste:{cardOptions:a,sanitizePrivateContent:e.sanitizePrivateContent},base:{allowInlineCursorTarget:!0,allowScrollGutter:function(e){let{appearance:t}=e;if((0,n("geLSP").isFullPage)(t))return{getScrollElement:()=>document.querySelector(".fabric-editor-popup-scroll-parent")}}(e)},blockType:{lastNodeMustBeParagraph:"comment"===r||"chromeless"===r,allowBlockType:e.allowBlockType,isUndoRedoButtonsEnabled:e.allowUndoRedoButtons},placeholder:{placeholder:e.placeholder,placeholderBracketHint:e.placeholderBracketHint},textFormatting:{...e.textFormatting||{},responsiveToolbarMenu:e.textFormatting?.responsiveToolbarMenu!=null?e.textFormatting.responsiveToolbarMenu:e.allowUndoRedoButtons},submitEditor:e.onSave,quickInsert:{enableElementBrowser:e.elementBrowser&&e.elementBrowser.showModal,elementBrowserHelpUrl:e.elementBrowser&&e.elementBrowser.helpUrl,disableDefaultItems:!1,headless:!1,emptyStateHandler:e.elementBrowser&&e.elementBrowser.emptyStateHandler,prioritySortingFn:e.quickInsert&&"boolean"!=typeof e.quickInsert&&e.quickInsert.prioritySortingFn||void 0,onInsert:e.quickInsert&&"boolean"!=typeof e.quickInsert&&e.quickInsert.onInsert||void 0},selection:{useLongPressSelection:!1},hyperlinkOptions:{editorAppearance:e.appearance,linkPicker:e.linking?.linkPicker,onClickCallback:a?.onClickCallback,platform:"web"},codeBlock:{...e.codeBlock,useLongPressSelection:!1,allowCompositionInputOverride:!1}}}function i(e,t,r){let o=new Set;return a({allowBlockType:t.allowBlockType})||o.add("codeBlock"),e.build({pluginInjectionAPI:r,excludePlugins:o})}}),i("a0rZe",function(t,r){e(t.exports,"createSchema",()=>s);let a=({nodeOrMark:e,domSpec:t})=>{if(!Array.isArray(t))return t;let r=t[1],a=(0,n("6VsTy").createProseMirrorMetadata)(e);return"object"!=typeof r||Array.isArray(r)?t.splice(1,0,a):t[1]=Object.assign(r,a),t},o=e=>new Proxy(e,{apply(e,t,r){let o=Reflect.apply(e,t,r);return Array.isArray(o)?a({nodeOrMark:r[0],domSpec:o}):o}}),i=e=>new Proxy(e,{get(e,t,r){let a=Reflect.get(e,t,r);return"toDOM"===t&&"function"==typeof a?o(a):a}});function s(e){let t=(0,n("4T0J6").fixExcludes)(e.marks.sort((0,n("2oGxU").sortByOrder)("marks")).reduce((e,t)=>(e[t.name]=i(t.mark),e),{})),r=(0,n("8Nly5").sanitizeNodes)(e.nodes.sort((0,n("2oGxU").sortByOrder)("nodes")).reduce((e,t)=>(e[t.name]=i(t.node),e),{}),t);return new(n("kviC1")).Schema({nodes:r,marks:t})}}),i("2q16N",function(t,r){e(t.exports,"editorMessages",()=>a);let a=(0,n("2nPZH").defineMessages)({editorAssistiveLabel:{id:"fabric.editor.editorAssistiveLabel",defaultMessage:"Main content area, start typing to enter text."}})}),i("imt7Y",function(t,r){e(t.exports,"focusEditorElement",()=>a);function a(e){let t=document.querySelector(`[data-focus-id="${e}"]`);t instanceof HTMLElement&&t.focus({preventScroll:!0})}}),i("kbBd7",function(t,r){e(t.exports,"getUAPrefix",()=>a);function a(){return n("d7ZU3").browser.chrome?"ua-chrome":n("d7ZU3").browser.ie?"ua-ie":n("d7ZU3").browser.gecko?"ua-firefox":n("d7ZU3").browser.safari?"ua-safari":""}}),i("dHwSr",function(r,a){e(r.exports,"handleEditorFocus",()=>i);var o=n("gwFzn");function i(e){if(!e?.hasFocus())return(t(o)?.startTransition&&(0,n("dh538").fg)("platform_editor_react_18_autofocus_fix")?e=>e():e=>window.setTimeout(e,0))(()=>{if((0,n("dh538").fg)("platform_editor_posfromdom_null_fix")&&e?.isDestroyed||e?.hasFocus())return;if(!window.getSelection){e?.focus();return}let t=window.getSelection();if(!t||0===t.rangeCount){e?.focus();return}let r=t.getRangeAt(0);if(e&&r.startContainer.contains(e.dom)){e.focus();return}let a=e?.posAtDOM(r.startContainer,r.startOffset),o=e?.posAtDOM(r.endContainer,r.endOffset);if(a&&a<0||o&&o<0){e?.focus();return}if(e&&a){let t=(0,n("7T7aA").TextSelection).create(e.state.doc,a,o),r=e.state.tr.setSelection(t);e.dispatch(r),e.focus()}})}}),i("cUiRv",function(t,r){e(t.exports,"useDispatchTransaction",()=>o);var a=n("gwFzn");let o=({onChange:e,dispatchAnalyticsEvent:t,onEditorViewUpdated:r,isRemoteReplaceDocumentTransaction:o})=>{let i=(0,a.useRef)(e);return(0,a.useEffect)(()=>{i.current=e},[e]),(0,a.useCallback)((e,a)=>{if(!e)return;let s=(0,n("TRQ5b").findChangedNodesFromTransaction)(a),d=(0,n("bE9x1").validateNodes)(s),l=new Proxy(a,(0,n("jNGLw").freezeUnsafeTransactionProperties)({dispatchAnalyticsEvent:t,pluginKey:"unknown-reacteditorview"})),c=!!o&&o(l);if(d||c){let t=e.state,{state:a,transactions:o}=e.state.applyTransaction(l);if(a===t)return;if(e.updateState(a),r({originalTransaction:l,transactions:o,oldEditorState:t,newEditorState:a}),i.current&&l.docChanged){let t=l.getMeta("isRemote")?"remote":"local",r=(0,n("h3X17").isDirtyTransaction)(l);(0,n("2T4ch").startMeasure)(n("8IgYx").EVENT_NAME_ON_CHANGE),i.current(e,{source:t,isDirtyChange:r}),(0,n("2T4ch").stopMeasure)(n("8IgYx").EVENT_NAME_ON_CHANGE)}}if(!d){let e=s.filter(e=>!(0,n("bE9x1").validNode)(e)).map(e=>(0,n("56Wjx").getDocStructure)(e,{compact:!0}));t({action:n("d925B").ACTION.DISPATCHED_INVALID_TRANSACTION,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,eventType:n("d925B").EVENT_TYPE.OPERATIONAL,attributes:{analyticsEventPayloads:(0,n("4VpM8").getAnalyticsEventsFromTransaction)(l),invalidNodes:e,isRemoteReplaceDocumentTransaction:c}})}},[t,r,o])}}),i("4VpM8",function(t,r){e(t.exports,"getAnalyticsEventsFromTransaction",()=>a);function a(e){return e.steps.filter(e=>e instanceof n("lTYwY").AnalyticsStep).reduce((e,t)=>[...e,...t.analyticsEvents],[])}}),i("TRQ5b",function(t,r){e(t.exports,"findChangedNodesFromTransaction",()=>o);var a=n("gWR1e");let o=e=>{let t=[];return(e.steps||[]).forEach(r=>{r.getMap().forEach((r,o,i,s)=>{e.doc.nodesBetween(i,Math.min(s,e.doc.content.size),r=>{let o=r;if((0,n("dh538").fg)("cc_complexit_fe_improve_node_validation")){let{schema:t}=e.selection.$from.doc.type,n=(0,a.findParentNode)(e=>e.type!==t.nodes.paragraph)(e.selection);o=n?n.node:r}return t.find(e=>e===o)||t.push(o),!1})})}),t}}),i("jNGLw",function(t,r){e(t.exports,"freezeUnsafeTransactionProperties",()=>i);let a=e=>["setSelection"].includes(e.toString()),o=e=>["doc","docs","steps","selection"].includes(e.toString()),i=({dispatchAnalyticsEvent:e,pluginKey:t})=>{let r=()=>{throw e&&e({action:n("d925B").ACTION.TRANSACTION_MUTATED_AFTER_DISPATCH,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,eventType:n("d925B").EVENT_TYPE.OPERATIONAL,attributes:{pluginKey:t||"unknown"}}),Error("Setting an unsafe property on transaction after dispatch!")};return{get:function(e,t,o){return a(t)&&r(),Reflect.get(e,t,o)},set:function(e,t,a){return o(t)&&r(),Reflect.set(e,t,a)}}}}),i("8IgYx",function(t,r){e(t.exports,"EVENT_NAME_ON_CHANGE",()=>a);let a=`\u{1F989} ReactEditorView::onChange`}),i("gpGrj",function(t,r){e(t.exports,"getTimeSince",()=>a);let a=e=>performance.now()-e}),i("bE9x1",function(t,r){e(t.exports,"validNode",()=>i),e(t.exports,"validateNodes",()=>s);var a=n("iu6m9");let o=new WeakSet,i=e=>{try{(0,a.editorExperiment)("platform_editor_memoized_node_check",!0,{exposure:!0})?function e(t){if(o.has(t))return;t.type.checkContent(t.content),t.type.checkAttrs(t.attrs);let r=n("kviC1").Mark.none;for(let e=0;e<t.marks.length;e++){let a=t.marks[e];a.type.checkAttrs(a.attrs),r=a.addToSet(r)}if(!(0,n("kviC1").Mark).sameSet(r,t.marks))throw RangeError(`Invalid collection of marks for node ${t.type.name}: ${t.marks.map(e=>e.type.name)}`);t.content.forEach(t=>e(t)),o.add(t)}(e):e.check()}catch(e){return!1}return!0},s=e=>e.every(i)}),i("hQcZ1",function(t,r){e(t.exports,"useFireFullWidthEvent",()=>o);var a=n("gwFzn");let o=(e,t)=>{let r=(0,n("7541v").default)(e);(0,a.useEffect)(()=>{e!==r&&("full-width"===e||"full-width"===r)&&t({action:n("d925B").ACTION.CHANGED_FULL_WIDTH_MODE,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,eventType:n("d925B").EVENT_TYPE.TRACK,attributes:{previousMode:(0,n("9tU17").formatFullWidthAppearance)(r),newMode:(0,n("9tU17").formatFullWidthAppearance)(e)}})},[e,r,t])}}),i("9tU17",function(t,r){e(t.exports,"formatFullWidthAppearance",()=>a);let a=e=>"full-width"===e?n("e2wMq").FULL_WIDTH_MODE.FULL_WIDTH:n("e2wMq").FULL_WIDTH_MODE.FIXED_WIDTH}),i("f8zg2",function(t,r){e(t.exports,"IntlProviderIfMissingWrapper",()=>s);var a=n("7UHDa"),o=n("gwFzn");let i=()=>null===(0,o.useContext)(n("js7oX").Context);function s({children:e}){return i()?(0,a.jsx)(n("hlhtG").default,{locale:"en",children:e}):e}}),i("lJ3BR",function(t,r){e(t.exports,"BaseThemeWrapper",()=>i);var a=n("7UHDa"),o=n("gwFzn");function i({baseFontSize:e,children:t}){let r=(0,o.useMemo)(()=>({baseFontSize:e||14,layoutMaxWidth:n("aFUXX").akEditorDefaultLayoutWidth}),[e]);return(0,a.jsx)(n("ja596").a,{theme:r,children:t})}}),i("jTtEd",function(t,r){e(t.exports,"getBaseFontSize",()=>a);function a(e){return void 0===e?n("aFUXX").akEditorFullPageDefaultFontSize:["comment","chromeless"].includes(e)?void 0:n("aFUXX").akEditorFullPageDefaultFontSize}}),i("eilyC",function(t,r){e(t.exports,"default",()=>o);var a=n("gwFzn");function o(e,t){(0,n("el1xD").default)(),(0,a.useEffect)(()=>((0,n("2T4ch").stopMeasure)(n("7lreV").default.EDITOR_MOUNTED,(0,n("amGDM").default)(n("d925B").ACTION.EDITOR_MOUNTED,e,t)),()=>{(0,n("2T4ch").clearMeasure)(n("7lreV").default.EDITOR_MOUNTED),(0,n("2T4ch").clearMeasure)(n("7lreV").default.ON_EDITOR_READY_CALLBACK)}),[])}}),i("amGDM",function(t,r){e(t.exports,"default",()=>a);function a(e,t,r){return async(a,o)=>{let i=await t.contextIdentifierProvider,s=i?.objectId;r&&(0,n("ajtqX").fireAnalyticsEvent)(r)({payload:{action:e,actionSubject:n("d925B").ACTION_SUBJECT.EDITOR,attributes:{duration:a,startTime:o,objectId:s},eventType:n("d925B").EVENT_TYPE.OPERATIONAL}})}}}),i("el1xD",function(t,r){e(t.exports,"default",()=>a);function a(){(0,n("9HtP4").default)(()=>{(0,n("2T4ch").startMeasure)(n("7lreV").default.EDITOR_MOUNTED)})}}),i("19Ub2",function(t,r){e(t.exports,"default",()=>o);var a=n("gwFzn"),o=e=>(0,a.useMemo)(()=>({appearance:"comment",disabled:!1,quickInsert:!0,preset:e.preset,appearance:e.appearance,contentComponents:e.contentComponents,primaryToolbarIconBefore:e.primaryToolbarIconBefore,secondaryToolbarComponents:e.secondaryToolbarComponents,persistScrollGutter:e.persistScrollGutter,quickInsert:e.quickInsert,shouldFocus:e.shouldFocus,disabled:e.disabled,contextPanel:e.contextPanel,errorReporterHandler:e.errorReporterHandler,contentTransformerProvider:e.contentTransformerProvider,maxHeight:e.maxHeight,minHeight:e.minHeight,placeholder:e.placeholder,placeholderBracketHint:e.placeholderBracketHint,defaultValue:e.defaultValue,assistiveLabel:e.assistiveLabel,assistiveDescribedBy:e.assistiveDescribedBy,popupsMountPoint:e.popupsMountPoint,popupsBoundariesElement:e.popupsBoundariesElement,popupsScrollableElement:e.popupsScrollableElement,editorActions:e.editorActions,onEditorReady:e.onEditorReady,onDestroy:e.onDestroy,onChange:e.onChange,onCancel:e.onCancel,extensionProviders:e.extensionProviders,UNSAFE_useAnalyticsContext:e.UNSAFE_useAnalyticsContext,useStickyToolbar:e.useStickyToolbar,featureFlags:e.featureFlags,onSave:e.onSave,sanitizePrivateContent:e.sanitizePrivateContent,media:e.media,collabEdit:e.collabEdit,primaryToolbarComponents:e.primaryToolbarComponents,performanceTracking:e.performanceTracking,inputSamplingLimit:e.inputSamplingLimit,allowUndoRedoButtons:e.allowUndoRedoButtons,linking:e.linking,activityProvider:e.activityProvider,searchProvider:e.searchProvider,annotationProviders:e.annotationProviders,collabEditProvider:e.collabEditProvider,presenceProvider:e.presenceProvider,emojiProvider:e.emojiProvider,taskDecisionProvider:e.taskDecisionProvider,legacyImageUploadProvider:e.legacyImageUploadProvider,mentionProvider:e.mentionProvider,autoformattingProvider:e.autoformattingProvider,macroProvider:e.macroProvider,contextIdentifierProvider:e.contextIdentifierProvider,allowExpand:e.allowExpand,allowNestedTasks:e.allowNestedTasks,allowBlockType:e.allowBlockType,allowTasksAndDecisions:e.allowTasksAndDecisions,allowBreakout:e.allowBreakout,allowRule:e.allowRule,allowHelpDialog:e.allowHelpDialog,allowPanel:e.allowPanel,allowExtension:e.allowExtension,allowConfluenceInlineComment:e.allowConfluenceInlineComment,allowTemplatePlaceholders:e.allowTemplatePlaceholders,allowDate:e.allowDate,allowLayouts:e.allowLayouts,allowStatus:e.allowStatus,allowTextAlignment:e.allowTextAlignment,allowIndentation:e.allowIndentation,showIndentationButtons:e.showIndentationButtons,allowFindReplace:e.allowFindReplace,allowBorderMark:e.allowBorderMark,allowFragmentMark:e.allowFragmentMark,autoScrollIntoView:e.autoScrollIntoView,elementBrowser:e.elementBrowser,maxContentSize:e.maxContentSize,saveOnEnter:e.saveOnEnter,feedbackInfo:e.feedbackInfo,mention:e.mention,mentionInsertDisplayName:e.mentionInsertDisplayName,uploadErrorHandler:e.uploadErrorHandler,waitForMediaUpload:e.waitForMediaUpload,extensionHandlers:e.extensionHandlers,allowTextColor:e.allowTextColor,allowTables:e.allowTables,insertMenuItems:e.insertMenuItems,UNSAFE_cards:e.UNSAFE_cards,smartLinks:e.smartLinks,allowAnalyticsGASV3:e.allowAnalyticsGASV3,codeBlock:e.codeBlock,textFormatting:e.textFormatting,__livePage:e.__livePage,AppearanceComponent:e.AppearanceComponent,skipValidation:e.skipValidation}),[e.preset,e.appearance,e.contentComponents,e.primaryToolbarIconBefore,e.secondaryToolbarComponents,e.persistScrollGutter,e.quickInsert,e.shouldFocus,e.disabled,e.contextPanel,e.errorReporterHandler,e.contentTransformerProvider,e.maxHeight,e.minHeight,e.placeholder,e.placeholderBracketHint,e.performanceTracking,e.inputSamplingLimit,e.defaultValue,e.assistiveLabel,e.assistiveDescribedBy,e.popupsMountPoint,e.popupsBoundariesElement,e.popupsScrollableElement,e.editorActions,e.onEditorReady,e.onDestroy,e.onChange,e.onCancel,e.extensionProviders,e.UNSAFE_useAnalyticsContext,e.useStickyToolbar,e.featureFlags,e.onSave,e.sanitizePrivateContent,e.media,e.collabEdit,e.primaryToolbarComponents,e.allowUndoRedoButtons,e.linking,e.activityProvider,e.searchProvider,e.annotationProviders,e.collabEditProvider,e.presenceProvider,e.emojiProvider,e.taskDecisionProvider,e.legacyImageUploadProvider,e.mentionProvider,e.autoformattingProvider,e.macroProvider,e.contextIdentifierProvider,e.allowExpand,e.allowNestedTasks,e.allowBlockType,e.allowTasksAndDecisions,e.allowBreakout,e.allowRule,e.allowHelpDialog,e.allowPanel,e.allowExtension,e.allowConfluenceInlineComment,e.allowTemplatePlaceholders,e.allowDate,e.allowLayouts,e.allowStatus,e.allowTextAlignment,e.allowIndentation,e.showIndentationButtons,e.allowFindReplace,e.allowBorderMark,e.allowFragmentMark,e.autoScrollIntoView,e.elementBrowser,e.maxContentSize,e.saveOnEnter,e.feedbackInfo,e.mention,e.mentionInsertDisplayName,e.uploadErrorHandler,e.waitForMediaUpload,e.extensionHandlers,e.allowTextColor,e.allowTables,e.insertMenuItems,e.UNSAFE_cards,e.smartLinks,e.allowAnalyticsGASV3,e.codeBlock,e.textFormatting,e.__livePage,e.AppearanceComponent,e.skipValidation])}),i("1T1oM",function(t,r){e(t.exports,"default",()=>s);var a=n("gwFzn"),o=n("ewD0v"),i=n("g9y33");function s(e,t,r){let{autoformattingProvider:s,emojiProvider:d,mentionProvider:l,legacyImageUploadProvider:c,taskDecisionProvider:p,contextIdentifierProvider:u,searchProvider:m,macroProvider:h,activityProvider:g,collabEdit:b,collabEditProvider:f,presenceProvider:x,quickInsert:v,extensionProviders:y}=e,E=(0,a.useMemo)(()=>(0,n("b5VLW").default)({autoformattingProvider:s,emojiProvider:d,mentionProvider:l,legacyImageUploadProvider:c,taskDecisionProvider:p,contextIdentifierProvider:u,searchProvider:m,macroProvider:h,activityProvider:g,collabEdit:b,collabEditProvider:f,presenceProvider:x}),[s,d,l,c,p,u,m,h,g,b,f,x]),S=(0,a.useRef)(new(n("4FxUL")).default),C=function(e){let t=(0,a.useRef)();return(0,a.useEffect)(()=>e?.apiResolver.on(e=>{t.current=e}),[e?.apiResolver]),t}(e.preset),k=(0,a.useMemo)(()=>(function(e,t,r,a,n){let s=(0,o.default)(()=>e)(a),d=(0,i.default)(e,t,s,r,n);return{extensionProvider:s,quickInsertProvider:d}})(t,C,v,y,r),[y,v,t,r,C]);return(0,a.useEffect)(()=>{(0,n("4G7Gx").default)(S.current,E,k.extensionProvider,k.quickInsertProvider)},[E,k]),(0,a.useEffect)(()=>()=>{S.current.destroy()},[]),S.current}}),i("ewD0v",function(t,r){e(t.exports,"default",()=>a);var a=e=>(0,n("csnse").default)(t=>(function(e,t){if(t)return"function"==typeof t?(0,n("eEmxu").default)(t(e)):(0,n("eEmxu").default)(t)})(e(),t))}),i("eEmxu",function(t,r){e(t.exports,"default",()=>a);var a=e=>{let t=[],{invokeSingle:r,invokeList:a}=(0,n("iScNA").default)(e);return{getExtensions:()=>a("getExtensions"),async preload(){0===t.length&&(t=await Promise.all(e.map(e=>Promise.resolve(e)))),await Promise.all(t.map(e=>e?.preload?.()))},getPreloadedExtension(e,r){if(0!==t.length)for(let a of t)try{let t=a?.getPreloadedExtension?.(e,r);if(t)return t}catch{}},getExtension:(e,t)=>r("getExtension",[e,t]),search:e=>a("search",[e]),getAutoConverter:()=>a("getAutoConverter")}}}),i("iScNA",function(t,r){e(t.exports,"default",()=>o);let a=e=>[].concat(...e);var o=e=>{if(0===e.length)throw Error("At least one provider must be provided");let t=async()=>{let t=await (0,n("80xRs").waitForAllPromises)(e.map(e=>Promise.resolve(e)));return(0,n("80xRs").getOnlyFulfilled)(t)},r=async e=>(await t()).map(t=>e(t)),o=(e,t)=>r=>{let a=r[e];if("function"==typeof a)return a.apply(r,t);throw Error(`"${String(e)}" isn't a function of the provider`)};return{invokeSingle:async(e,t)=>{let a=o(e,t);return(0,n("80xRs").waitForFirstFulfilledPromise)(await r(a))},invokeList:async(e,t)=>{let i=o(e,t),s=await (0,n("80xRs").waitForAllPromises)(await r(i));return a((0,n("80xRs").getOnlyFulfilled)(s)).filter(e=>e)}}}}),i("80xRs",function(t,r){var a;e(t.exports,"waitForAllPromises",()=>s),e(t.exports,"waitForFirstFulfilledPromise",()=>d),e(t.exports,"getOnlyFulfilled",()=>l),(a={}).FULFILLED="fulfilled",a.FAILED="failed";let o=e=>"fulfilled"===e.status,n=e=>({status:"fulfilled",value:e}),i=e=>({status:"failed",reason:e}),s=e=>Promise.all(e.map(e=>e.then(n).catch(i))),d=e=>{let t=[];return new Promise((r,a)=>{e.forEach(o=>o.then(e=>{if(null==e)throw Error("Result was not found but the method didn't reject/throw. Please ensure that it doesn't return null or undefined.");r(e)}).catch(r=>{t.push(r),t.length===e.length&&a(r)}))})},l=e=>e.filter(o).map(e=>e.value)}),i("g9y33",function(t,r){e(t.exports,"default",()=>o);var a=n("b2s9f");function o(e,t,r,o,n){let i=o&&"boolean"!=typeof o&&o.provider,s=r&&(0,a.extensionProviderToQuickInsertProvider)(r,e,t,n);return i&&s?(0,a.combineQuickInsertProviders)([i,s]):i||s}}),i("b2s9f",function(r,a){e(r.exports,"extensionProviderToQuickInsertProvider",()=>c),e(r.exports,"combineQuickInsertProviders",()=>p);var o=n("7UHDa");n("gwFzn");var i=n("4wH3g");function s(e,t,r,a){if(r){let o=(0,n("dh538").fg)("platform_nested_nbm_analytics_location")?(0,n("lWghV").findInsertLocation)(t):void 0;(0,n("ajtqX").fireAnalyticsEvent)(r)({payload:{action:n("d925B").ACTION.INSERTED,actionSubject:n("d925B").ACTION_SUBJECT.DOCUMENT,actionSubjectId:n("d925B").ACTION_SUBJECT_ID.EXTENSION,attributes:{extensionType:e.extensionType,extensionKey:e.extensionKey,key:e.key,inputMethod:a||n("d925B").INPUT_METHOD.QUICK_INSERT,...o?{insertLocation:o}:{}},eventType:n("d925B").EVENT_TYPE.TRACK}})}}let d=e=>{},l={editInContextPanel:()=>d("editInContextPanel"),_editInLegacyMacroBrowser:()=>d("_editInLegacyMacroBrowser"),getNodeWithPosByLocalId:()=>({node:null,pos:null}),doc:{insertAfter:()=>d("doc:insertAfter"),scrollTo:()=>d("doc:scrollTo"),update:()=>d("doc:update")}};async function c(e,r,a,d){let c=await e.getExtensions();return{getItems:()=>Promise.all((0,n("2cmfr").getQuickInsertItemsFromModule)(c,e=>{let c=t(i)({__loadable_id__:"N8xjw",name:"Icon",loader:e.icon,loading:()=>null});return{title:e.title,description:e.description,icon:()=>(0,o.jsx)(c,{label:""}),keywords:e.keywords,featured:e.featured,categories:e.categories,isDisabledOffline:!0,action:(t,o,i)=>{if("function"!=typeof e.node)return s(e,o.selection,d,i),t(e.node);{let c=a?.current?.extension?.actions?.api();return c?(0,n("3jQ9y").resolveImport)(e.node(c)).then(t=>{s(e,o.selection,d,i),t&&r.replaceSelection(t)}):(0,n("3jQ9y").resolveImport)(e.node(l)).then(t=>{s(e,o.selection,d,i),t&&r.replaceSelection(t)}),t("")}}}}))}}async function p(e){let{invokeList:t}=(0,n("iScNA").default)(e);return{getItems:()=>t("getItems")}}}),i("2cmfr",function(t,r){e(t.exports,"getQuickInsertItemsFromModule",()=>a),e(t.exports,"getAutoConvertPatternsFromModule",()=>o),e(t.exports,"getExtensionAutoConvertersFromProvider",()=>s),e(t.exports,"getContextualToolbarItemsFromModule",()=>u);let a=(e,t)=>[].concat(...e.map(e=>(e.modules.quickInsert||[]).map(t=>(function(e,t){let r=t.title||e.title,a=`${e.key}:${t.key}`,o=(0,n("3jQ9y").buildAction)(t.action,e);if(!o)throw Error(`Couldn't find any action for ${r} (${a})`);return{key:a,title:r,extensionType:e.type,extensionKey:e.key,keywords:t.keywords||e.keywords||[],featured:t.featured||!1,categories:t.categories||e.categories||[],description:t.description||e.description,summary:e.summary,documentationUrl:e.documentationUrl,icon:t.icon||e.icons["48"],node:o}})(e,t)))).map(t);async function o(e){return[].concat(...await Promise.all(e.map(async e=>e.modules.autoConvert&&e.modules.autoConvert.url?e.modules.autoConvert.url:[])))}let i=e=>t=>{for(let r of e){let e=r(t);if(e)return e}};async function s(e){let t=await e;return i(await t.getAutoConverter())}let d=(e,...t)=>{console.error(e,...t)},l=(e,t)=>{let{tooltip:r,tooltipStyle:a,key:o,label:n,ariaLabel:i,icon:s,action:l,disabled:c}=e,p=[t,o].join(":");"function"!=typeof l&&d(`Provided action is not a function for extension toolbar button: ${n} (${p})`);let u={};switch(e.display){case"icon":s||d(`icon should be provided for extension toolbar button (${p}), when display is set to 'icon'`),u={icon:s};break;case"label":n||d(`label should be provided for extension toolbar button (${p}), when display is set to 'label'`),u={label:n};break;default:n&&s||d(`label and icon should be provided for extension toolbar button (${p}), when display is not set or set to 'icon-and-label'`),u={icon:s,label:n}}return{key:p,ariaLabel:i,tooltip:r,tooltipStyle:a,action:l,disabled:c,...u}},c=(e,t)=>{if(e.type===t.type&&e.nodeType===t.nodeType){if("node"===e.type)return!0;if("extension"===e.type&&"extension"===t.type)return e.extensionKey===t.extensionKey&&e.extensionType===t.extensionType}return!1},p=e=>{if(e.length>1){let t=e.map(e=>e.context);return t.find((e,r)=>r!==t.findIndex(t=>c(e,t)))}},u=(e,t,r)=>e.map(e=>{if(e.modules.contextualToolbars){let a=p(e.modules.contextualToolbars);return a?(d(`[contextualToolbars] Duplicate context detected - ${JSON.stringify(a)}.`),[]):e.modules.contextualToolbars.map(e=>{if(function(e,t){if("node"===e.context.type&&e.context.nodeType===t.type)return!0;if("extension"!==e.context.type||t.type!==e.context.nodeType||e.context.shouldExclude&&e.context.shouldExclude(t))return!1;let{extensionType:r,extensionKey:a}=e.context;return(!r||r===t.attrs?.extensionType)&&("string"==typeof a?a===t.attrs?.extensionKey:!!Array.isArray(a)&&!!a.length&&a.includes(t.attrs?.extensionKey))}(e,t)){let{toolbarItems:a}=e;return"function"==typeof a?a(t,r):a}return[]}).flatMap(t=>t.map(t=>m(t)?l(t,e.key):t))}return[]}).flatMap(e=>e),m=e=>!("type"in e)}),i("b5VLW",function(t,r){e(t.exports,"default",()=>a);function a({autoformattingProvider:e,emojiProvider:t,mentionProvider:r,legacyImageUploadProvider:a,taskDecisionProvider:o,contextIdentifierProvider:n,searchProvider:i,macroProvider:s,activityProvider:d,collabEdit:l,collabEditProvider:c,presenceProvider:p}){return{emojiProvider:t,mentionProvider:r,autoformattingProvider:e,activityProvider:d,imageUploadProvider:a,taskDecisionProvider:o,contextIdentifierProvider:n,searchProvider:i,presenceProvider:p,macroProvider:s,collabEditProvider:l?.provider?l.provider:c}}}),i("4G7Gx",function(t,r){e(t.exports,"default",()=>a);function a(e,{mentionProvider:t,contextIdentifierProvider:r,collabEditProvider:a,activityProvider:o,presenceProvider:n,macroProvider:i,imageUploadProvider:s,searchProvider:d},l,c){e.setProvider("mentionProvider",t),e.setProvider("contextIdentifierProvider",r),e.setProvider("imageUploadProvider",s),e.setProvider("collabEditProvider",a),e.setProvider("activityProvider",o),e.setProvider("searchProvider",d),e.setProvider("presenceProvider",n),e.setProvider("macroProvider",i),l&&e.setProvider("extensionProvider",Promise.resolve(l)),c&&e.setProvider("quickInsertProvider",c)}}),i("1PKpt",function(r,a){e(r.exports,"default",()=>b);var o=n("gwFzn"),i=n("1oCLl"),s=n("iu6m9"),d=n("761rI"),l=n("axOCf");let c=(0,n("3jLHL").css)({"-ms-overflow-style":"-ms-autohiding-scrollbar","&::-webkit-scrollbar-corner":{display:"none"},"&::-webkit-scrollbar-thumb":{backgroundColor:"var(--ds-background-neutral-subtle, #00000000)"},"&:hover::-webkit-scrollbar-thumb":{backgroundColor:"var(--ds-background-neutral-bold, #44546F)",borderRadius:8},"&::-webkit-scrollbar-thumb:hover":{backgroundColor:"var(--ds-background-neutral-bold-hovered, #2C3E5D)"}}),p=(0,n("3jLHL").css)({lineHeight:"20px",height:"auto",overflowX:"hidden",overflowY:"auto"},n("26eEE").scrollbarStyles,{maxWidth:"inherit",boxSizing:"border-box",wordWrap:"break-word","div > .ProseMirror":{outline:"none",whiteSpace:"pre-wrap",padding:0,margin:0,"& > :last-child":{paddingBottom:"var(--ds-space-100, 0.5em)"}}}),u=(0,n("3jLHL").css)({lineHeight:"20px",height:"auto",overflowX:"hidden",overflowY:"auto",maxWidth:"inherit",boxSizing:"border-box",wordWrap:"break-word","div > .ProseMirror":{outline:"none",whiteSpace:"pre-wrap",padding:0,margin:0,"& > :last-child":{paddingBottom:"var(--ds-space-100, 0.5em)"}}}),m=(0,d.createEditorContentStyle)();m.displayName="ContentArea";let h=(0,n("9JpPs").componentWithCondition)(()=>(0,s.editorExperiment)("platform_editor_core_static_emotion",!0,{exposure:!0}),l.default,m),g=(0,n("574ry").sharedPluginStateHookMigratorFactory)(e=>{let{editorViewModeState:t}=(0,n("1Oo9w").useSharedPluginState)(e,["editorViewMode"]);return t?.mode},e=>(0,n("b3YrF").useSharedPluginStateSelector)(e,"editorViewMode.mode"));class b extends t(o).Component{render(){return(0,n("3jLHL").jsx)(x,{editorAPI:this.props.editorAPI,renderChrome:this.renderChrome})}constructor(...e){super(...e),this.appearance="chromeless",this.containerElement=null,this.renderChrome=({maxContentSize:e})=>{let{editorDOMElement:t,editorView:r,editorActions:a,eventDispatcher:o,providerFactory:i,contentComponents:s,customContentComponents:d,maxHeight:l,minHeight:c=30,popupsMountPoint:p,popupsBoundariesElement:u,popupsScrollableElement:m,disabled:b,dispatchAnalyticsEvent:f,pluginHooks:x,featureFlags:y}=this.props,E=!!e?.maxContentSizeReached,S=g(this.props.editorAPI);return(0,n("3jLHL").jsx)(n("uq7dM").default,{animate:E},(0,n("3jLHL").jsx)(v,{maxHeight:l,minHeight:c,containerRef:e=>this.containerElement=e},(0,n("3jLHL").jsx)(h,{className:"ak-editor-content-area",featureFlags:y,viewMode:S,appearance:this.appearance},d&&"before"in d?d.before:d,(0,n("3jLHL").jsx)(n("3ae8F").default,{editorView:r,editorActions:a,eventDispatcher:o,providerFactory:i,appearance:this.appearance,items:s,popupsMountPoint:p,popupsBoundariesElement:u,popupsScrollableElement:m,containerElement:this.containerElement,disabled:!!b,dispatchAnalyticsEvent:f,wrapperElement:this.containerElement,pluginHooks:x}),t,d&&"after"in d?d.after:null)))}}}b.displayName="ChromelessEditorAppearance";let f=(0,n("574ry").sharedPluginStateHookMigratorFactory)(e=>{let{maxContentSizeState:t}=(0,n("1Oo9w").useSharedPluginState)(e,["maxContentSize"]);return{maxContentSizeState:t}},e=>{let t=(0,n("b3YrF").useSharedPluginStateSelector)(e,"maxContentSize.maxContentSizeReached");return{maxContentSizeState:void 0===t?void 0:{maxContentSizeReached:t}}});function x({renderChrome:e,editorAPI:t}){let{maxContentSizeState:r}=f(t);return(0,n("3jLHL").jsx)(o.Fragment,null,e({maxContentSize:r}))}let v=(0,n("9JpPs").componentWithCondition)(()=>(0,i.expValEquals)("platform_editor_core_static_emotion","isEnabled",!0),function({maxHeight:e,minHeight:t,children:r,containerRef:a}){return(0,n("3jLHL").jsx)("div",{css:[u,c],style:{maxHeight:e?`${e}px`:void 0,minHeight:`${t}px`},"data-testid":"chromeless-editor",id:"chromeless-editor",ref:a},r)},function({maxHeight:e,minHeight:t,children:r,containerRef:a}){return(0,n("3jLHL").jsx)("div",{css:[p,e&&(0,n("3jLHL").css)({maxHeight:`${e}px`}),(0,n("3jLHL").css)({minHeight:`${t}px`})],"data-testid":"chromeless-editor",id:"chromeless-editor",ref:a},r)})}),i("26eEE",function(t,r){e(t.exports,"scrollbarStyles",()=>a);let a=`
  -ms-overflow-style: -ms-autohiding-scrollbar;

  &::-webkit-scrollbar {
    overflow: hidden,
  }

  &::-webkit-scrollbar-corner {
    display: none;
  }

  &::-webkit-scrollbar-thumb {
    background-color: var(--ds-background-neutral-subtle, #00000000);
  }

  &:hover::-webkit-scrollbar-thumb {
    background-color: var(--ds-background-neutral-bold, #44546F);
    border-radius: 8px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background-color: var(--ds-background-neutral-bold-hovered, #2C3E5D);
  }
`}),i("761rI",function(r,a){e(r.exports,"createEditorContentStyle",()=>C);var o=n("gwFzn");n("o46Yq"),n("9PfP2"),n("agKS6"),n("axrL7");var i=n("dZ8uq"),s=n("iu6m9"),d=n("6Ra3A");let l=(0,n("3jLHL").css)`
	.ProseMirror {
		${(0,n("idF2b").linkSharedStyle)()}
	}
`,c=()=>(0,n("3jLHL").css)`
	.ProseMirror {
		${(0,n("eRvLS").ruleSharedStyles)()};

		hr {
			cursor: pointer;
			padding: ${"var(--ds-space-050, 4px)"} 0;
			margin: ${"var(--ds-space-300, 24px)"} 0;
			background-clip: content-box;

			&.${n("aFUXX").akEditorSelectedNodeClassName} {
				outline: none;
				background-color: ${`var(--ds-border-selected, ${n("aFUXX").akEditorSelectedBorderColor})`};
			}
		}
	}
`,p=(0,n("3jLHL").css)({".editor-mention-primitive":{display:"inline",borderRadius:"20px",cursor:"pointer",padding:"0 0.3em 2px 0.23em",lineHeight:"1.714",fontWeight:"var(--ds-font-weight-regular, 400)",wordBreak:"break-word",background:"var(--ds-background-neutral, #091E420F)",border:"1px solid transparent",color:"var(--ds-text-subtle, #44546F)","&:hover":{background:"var(--ds-background-neutral-hovered, #091E4224)"},"&:active":{background:"var(--ds-background-neutral-pressed, #091E424F)"}},".editor-mention-primitive.mention-restricted":{background:"transparent",border:"1px solid var(--ds-border-bold, #758195)",color:"var(--ds-text, #172B4D)","&:hover":{background:"transparent"},"&:active":{background:"transparent"}},".editor-mention-primitive.mention-self":{background:"var(--ds-background-brand-bold, #0C66E4)",border:"1px solid transparent",color:"var(--ds-text-inverse, #FFFFFF)","&:hover":{background:"var(--ds-background-brand-bold-hovered, #0055CC)"},"&:active":{background:"var(--ds-background-brand-bold-pressed, #09326C)"}}}),u=(0,n("3jLHL").css)({".editor-mention-primitive":{padding:"1px 0.3em 1px 0.23em"}}),m=(0,n("3jLHL").css)`
	.danger {
		.editor-mention-primitive {
			box-shadow: 0 0 0 ${n("aFUXX").akEditorSelectedBorderSize}px ${n("aFUXX").akEditorDeleteBorder};
			background-color: ${`var(--ds-background-danger, ${n("aFUXX").akEditorDeleteBackgroundWithOpacity})`};
		}
	}

	.${n("aFUXX").akEditorSelectedNodeClassName} > .editor-mention-primitive,
	.${n("aFUXX").akEditorSelectedNodeClassName} > .editor-mention-primitive.mention-self,
	.${n("aFUXX").akEditorSelectedNodeClassName} > .editor-mention-primitive.mention-restricted {
		${(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.BoxShadow,n("b38UX").SelectionStyle.Background])}
		/* need to specify dark text colour because personal mentions
	       (in dark blue) have white text by default */
		color: ${"var(--ds-text-subtle, #44546F)"}
	}
`,h=(0,n("3jLHL").css)`
	.${n("9WN1A").MentionSharedCssClassName.MENTION_CONTAINER} {
		&.${n("aFUXX").akEditorSelectedNodeClassName} [data-mention-id] > span {
			${(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.BoxShadow,n("b38UX").SelectionStyle.Background])}

			/* need to specify dark text colour because personal mentions
         (in dark blue) have white text by default */
      color: ${"var(--ds-text-subtle, #44546F)"};
		}
	}

	.danger {
		.${n("9WN1A").MentionSharedCssClassName.MENTION_CONTAINER}.${n("aFUXX").akEditorSelectedNodeClassName}
			> span
			> span
			> span {
			box-shadow: 0 0 0 ${n("aFUXX").akEditorSelectedBorderSize}px ${n("aFUXX").akEditorDeleteBorder};
			background-color: ${`var(--ds-background-danger, ${n("aFUXX").akEditorDeleteBackgroundWithOpacity})`};
		}
		.${n("9WN1A").MentionSharedCssClassName.MENTION_CONTAINER} > span > span > span {
			background-color: ${"var(--ds-background-neutral, #091E420F)"};
			color: ${"var(--ds-text-subtle, #44546F)"};
		}
	}
`,g=(0,n("3jLHL").css)`
	.ProseMirror {
		li {
			position: relative;

			> p:not(:first-child) {
				margin: ${"var(--ds-space-050, 4px)"} 0 0 0;
			}

			/* In SSR the above rule will apply to all p tags because first-child would be a style tag.
			The following rule resets the first p tag back to its original margin
			defined in packages/editor/editor-common/src/styles/shared/paragraph.ts */
			> style:first-child + p {
				margin-top: ${n("aFUXX").blockNodesVerticalMargin};
			}
		}

		&:not([data-node-type='decisionList']) > li,
    /* This prevents https://product-fabric.atlassian.net/browse/ED-20924 */
    &:not(.${n("cV5SN").SmartCardSharedCssClassName.BLOCK_CARD_CONTAINER}) > li {
			${n("d7ZU3").browser.safari?n("5MaNT").codeBlockInListSafariFix:""}
		}
	}
`,b=(0,n("3jLHL").css)`
	.${n("98HrB").EmojiSharedCssClassName.EMOJI_CONTAINER} {
		display: inline-block;
	}

	.${n("98HrB").EmojiSharedCssClassName.EMOJI_SPRITE}, .${n("98HrB").EmojiSharedCssClassName.EMOJI_IMAGE} {
		background: no-repeat transparent;
		display: inline-block;
		height: ${n("fhsiz").defaultEmojiHeight}px;
		max-height: ${n("fhsiz").defaultEmojiHeight}px;
		cursor: pointer;
		vertical-align: middle;
		user-select: all;
	}

	.${n("aFUXX").akEditorSelectedNodeClassName} {
		.${n("98HrB").EmojiSharedCssClassName.EMOJI_SPRITE}, .${n("98HrB").EmojiSharedCssClassName.EMOJI_IMAGE} {
			border-radius: 2px;
			${(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.Blanket,n("b38UX").SelectionStyle.BoxShadow])}
		}
	}
`,f=(0,n("3jLHL").css)({".ProseMirror .placeholder-decoration":{color:"var(--ds-text-subtlest, #626F86)",width:"100%",pointerEvents:"none",userSelect:"none",".placeholder-android":{pointerEvents:"none",outline:"none",userSelect:"none",position:"absolute"}}}),x=(0,n("3jLHL").css)({".ProseMirror p:has(.placeholder-decoration-hide-overflow)":{overflow:"hidden",whiteSpace:"nowrap",textOverflow:"ellipsis"}}),v=(0,n("3jLHL").css)({'.ProseMirror mark[data-type-ahead-query="true"]:has(.placeholder-decoration-wrap)':{whiteSpace:"nowrap"}}),y=(0,n("3jLHL").css)`
	.ProseMirror {
		> .${n("DoNsZ").PanelSharedCssClassName.prefix},
			> .${n("5MaNT").CodeBlockSharedCssClassName.CODEBLOCK_CONTAINER},
			> .${n("cV5SN").SmartCardSharedCssClassName.BLOCK_CARD_CONTAINER},
			> div[data-task-list-local-id],
		> div[data-layout-section],
		> .${n("iMS6j").expandClassNames.prefix} {
			&:first-child {
				margin-top: 0;
			}
		}

		> hr:first-child,
		> .ProseMirror-widget:first-child + hr {
			margin-top: 0;
		}
	}
`,E=(0,n("3jLHL").css)({"button.first-floating-toolbar-button:focus":{outline:"2px solid var(--ds-border-focused, #2684FF)"}}),S=e=>(0,n("3jLHL").css)`
	--ak-editor--default-gutter-padding: ${n("aFUXX").akEditorGutterPadding}px;
	/* 52 is from akEditorGutterPaddingDynamic via editor-shared-styles */
	--ak-editor--large-gutter-padding: ${(0,n("aFUXX").akEditorGutterPaddingDynamic)()}px;
	--ak-editor--default-layout-width: ${n("aFUXX").akEditorDefaultLayoutWidth}px;
	--ak-editor--full-width-layout-width: ${n("aFUXX").akEditorFullWidthLayoutWidth}px;
	/* calculate editor line length, 100cqw is the editor container width */
	--ak-editor--line-length: min(
		calc(100cqw - var(--ak-editor--large-gutter-padding) * 2),
		var(--ak-editor--default-layout-width)
	);
	--ak-editor--breakout-wide-layout-width: ${n("aFUXX").akEditorCalculatedWideLayoutWidthSmallViewport}px;
	--ak-editor--breakout-full-page-guttering-padding: calc(
		var(--ak-editor--large-gutter-padding) * 2 + var(--ak-editor--default-gutter-padding)
	);

	--ak-editor--breakout-fallback-width: calc(
		100cqw - var(--ak-editor--breakout-full-page-guttering-padding)
	);

	.fabric-editor--full-width-mode {
		--ak-editor--line-length: min(
			calc(100cqw - var(--ak-editor--large-gutter-padding) * 2),
			var(--ak-editor--full-width-layout-width)
		);

		/* in full width appearances it's not possible to rely on cqw because it doesn't account for the page scrollbar, which depends on users system settings */
		--ak-editor--breakout-fallback-width: 100%;
	}

	.ProseMirror {
		--ak-editor-max-container-width: calc(100cqw - var(--ak-editor--large-gutter-padding));
	}

	/* We can't allow nodes that are inside other nodes to bleed from the parent container */
	.ProseMirror > div[data-prosemirror-node-block] [data-prosemirror-node-block] {
		--ak-editor-max-container-width: 100%;
	}

	/* container editor-area is defined in platform/packages/editor/editor-core/src/ui/Appearance/FullPage/StyledComponents.ts */
	@container editor-area (width >= ${"1266px"}) {
		.ProseMirror {
			--ak-editor--breakout-wide-layout-width: ${n("aFUXX").akEditorCalculatedWideLayoutWidth}px;
		}
	}

	.ProseMirror {
		outline: none;
		font-size: ${(0,n("aFUXX").editorFontSize)({theme:e.theme})}px;
		${n("3iemu").whitespaceSharedStyles};
		${(0,n("3Khgq").paragraphSharedStyles)(e.typographyTheme)};
		${n("4mSjx").listsSharedStyles};
		${n("diPla").indentationSharedStyles};
		${n("cRffC").shadowSharedStyle};
		${n("gYSj7").InlineNodeViewSharedStyles};
	}

	.ProseMirror-hideselection *::selection {
		background: transparent;
	}

	.ProseMirror-hideselection *::-moz-selection {
		background: transparent;
	}

	/**
	 * This prosemirror css style: https://github.com/ProseMirror/prosemirror-view/blob/f37ebb29befdbde3cd194fe13fe17b78e743d2f2/style/prosemirror.css#L24
	 *
	 * 1. Merge and Release platform_editor_hide_cursor_when_pm_hideselection
	 * 2. Cleanup duplicated style from platform_editor_advanced_code_blocks
	 *    https://product-fabric.atlassian.net/browse/ED-26331
	 */
	${(0,n("dh538").fg)("platform_editor_hide_cursor_when_pm_hideselection")?(0,n("3jLHL").css)`
				.ProseMirror-hideselection {
					caret-color: transparent;
				}
			`:null}

	/* This prosemirror css style: https://github.com/ProseMirror/prosemirror-view/blob/f37ebb29befdbde3cd194fe13fe17b78e743d2f2/style/prosemirror.css#L24 */
	${(0,s.editorExperiment)("platform_editor_advanced_code_blocks",!0)?(0,n("3jLHL").css)`
				.ProseMirror-hideselection {
					caret-color: transparent;
				}
			`:null}

	.ProseMirror-selectednode {
		outline: none;
	}

	.ProseMirror-selectednode:empty {
		outline: 2px solid ${"var(--ds-border-focused, #8cf)"};
	}

	.ProseMirror.ProseMirror-focused:has(.ProseMirror-mark-boundary-cursor) {
		caret-color: transparent;
	}
	.ProseMirror:not(.ProseMirror-focused) .ProseMirror-mark-boundary-cursor {
		display: none;
	}

	${E}
	${n("319kp").placeholderTextStyles}
	${(0,n("dh538").fg)("platform_editor_system_fake_text_highlight_colour")&&n("319kp").placeholderTextStyles_fg_platform_editor_system_fake_text_highlight_colour}
	${f}
	${(0,s.editorExperiment)("platform_editor_controls","variant1")?x:null}
	${(0,s.editorExperiment)("platform_editor_controls","variant1")&&(0,n("dh538").fg)("platform_editor_quick_insert_placeholder")?v:null}

  ${(0,n("1zjTz").codeBlockStyles)()}

  ${(0,n("4jPB7").blocktypeStyles)(e.typographyTheme)}
  ${(0,n("7zsay").codeMarkSharedStyles)()}
  ${n("4h2HM").textColorStyles}
  ${(0,n("52bSY").backgroundColorStyles)()}
  ${g}
  ${c()}
  ${(0,d.mediaStyles)()}
  ${(0,n("3oH64").layoutStyles)(e.viewMode)}
  ${(0,n("dh538").fg)("confluence_team_presence_scroll_to_pointer")?n("h3X17").telepointerStyle:n("h3X17").telepointerStyleWithInitialOnly}
  ${n("4AaC5").gapCursorStyles};
	${(0,n("bD4Xf").panelStyles)()}
	${h}
	${p}
	${(0,n("dh538").fg)("platform_editor_centre_mention_padding")&&u}
	${m}
  ${b}
  ${n("7iisy").tasksAndDecisionsStyles}
  ${n("87iYj").gridStyles}
  ${l}
  ${n("kZBrC").blockMarksSharedStyles}
  ${n("7bDsi").dateSharedStyle}
  ${n("6dFlY").extensionStyles}
  ${(0,n("gSnRq").expandStyles)()}
  ${(0,i.expValEqualsNoExposure)("platform_editor_find_and_replace_improvements","isEnabled",!0)?(0,n("dh538").fg)("platform_editor_find_and_replace_magenta_match")?n("hAOTs").findReplaceStylesNewMagenta:n("hAOTs").findReplaceStylesNewYellow:n("hAOTs").findReplaceStyles}
  ${n("gg4RV").textHighlightStyle}
  ${n("dR5Bd").taskDecisionStyles}
	${n("dR5Bd").taskItemStyles}
  /* Switch between the two icons based on the visual refresh feature gate */
	${(0,n("dh538").fg)("platform-visual-refresh-icons")&&n("dR5Bd").taskDecisionIconWithVisualRefresh}
	${!(0,n("dh538").fg)("platform-visual-refresh-icons")&&n("dR5Bd").taskDecisionIconWithoutVisualRefresh}
  ${n("ftMAt").statusStyles}
  ${(0,n("ftMAt").statusNodeStyles)()}
  ${(0,n("6ESsx").annotationSharedStyles)()}
  ${(0,n("0vvte").smartCardStyles)()}
  ${(0,n("dh538").fg)("platform-linking-visual-refresh-v1")?(0,n("cV5SN").getSmartCardSharedStyles)():n("cV5SN").smartCardSharedStyles}
	${n("jFND0").dateStyles}
  ${n("jFND0").dateNodeStyles}
  ${(0,n("xdUPw").embedCardStyles)()}
  ${n("2wkZs").unsupportedStyles}
  ${n("7QdQz").resizerStyles}
  ${(0,n("7QdQz").pragmaticResizerStyles)()}
  ${(0,n("7QdQz").pragmaticStylesLayoutFirstNodeResizeHandleFix)()}
  ${(0,n("7QdQz").pragmaticResizerStylesForTooltip)()}
  ${(0,n("bl6tp").aiPanelStyles)(e.colorMode)}
  ${y}

  .panelView-content-wrap {
		box-sizing: border-box;
	}

	.mediaGroupView-content-wrap ul {
		padding: 0;
	}

	/** Needed to override any cleared floats, e.g. image wrapping */

	div.fabric-editor-block-mark[class^='fabric-editor-align'] {
		clear: none !important;
	}

	.fabric-editor-align-end {
		text-align: right;
	}

	.fabric-editor-align-start {
		text-align: left;
	}

	.fabric-editor-align-center {
		text-align: center;
	}

	/* For FullPage only when inside a table
	Related code all lives inside: packages/editor/editor-core/src/ui/Appearance/FullPage/StyledComponents.ts
	In the "editorContentAreaContainerStyle" function */
	.fabric-editor--full-width-mode {
		.pm-table-container {
			.code-block,
			.extension-container,
			.multiBodiedExtension--container {
				max-width: 100%;
			}
		}
	}

	.pm-table-header-content-wrap :not(.fabric-editor-alignment),
	.pm-table-header-content-wrap :not(p, .fabric-editor-block-mark) + div.fabric-editor-block-mark,
	.pm-table-cell-content-wrap :not(p, .fabric-editor-block-mark) + div.fabric-editor-block-mark {
		p:first-of-type {
			margin-top: 0;
		}
	}
	.pm-table-cell-content-wrap .mediaGroupView-content-wrap {
		clear: both;
	}

	.hyperlink-floating-toolbar,
	.${n("ag6aQ").ClassNames.FLOATING_TOOLBAR_COMPONENT} {
		padding: 0;
	}

	/* Legacy Link icon in the Atlaskit package
     is bigger than the others, new ADS icon does not have this issue
  */
	${(0,n("dh538").fg)("platform-visual-refresh-icons")?null:(0,n("3jLHL").css)`
				.hyperlink-open-link {
					min-width: 24px;
					svg {
						max-width: 18px;
					}
				}
			`}
`,C=e=>t(o).forwardRef((t,r)=>{let{className:a,children:i,featureFlags:s}=t,d=(0,n("ja596").u)(),{colorMode:l,typography:c}=(0,n("cOrQJ").default)(),p=(0,o.useMemo)(()=>S({theme:d,colorMode:l,featureFlags:s,viewMode:t.viewMode,typographyTheme:c}),[d,l,s,t.viewMode,c]);return t.isScrollable?(0,n("3jLHL").jsx)("div",{className:a,ref:r,css:[p,e],"data-editor-scroll-container":"true","data-testid":"editor-content-container"},i):(0,n("3jLHL").jsx)("div",{className:a,ref:r,css:[p,e],"data-testid":"editor-content-container"},i)});C()}),i("98HrB",function(t,r){e(t.exports,"EmojiSharedCssClassName",()=>a);let a={EMOJI_CONTAINER:"emojiView-content-wrap",EMOJI_NODE:n("8hpYf").emojiNodeStyles,EMOJI_SPRITE:n("8hpYf").emojiSprite,EMOJI_IMAGE:n("8hpYf").emojiImage,EMOJI_PLACEHOLDER:n("8hpYf").placeholder}}),i("9WN1A",function(t,r){e(t.exports,"MentionSharedCssClassName",()=>a);let a={MENTION_CONTAINER:"mentionView-content-wrap"}}),i("DoNsZ",function(t,r){e(t.exports,"darkPanelColors",()=>o),e(t.exports,"PanelSharedCssClassName",()=>c),e(t.exports,"getPanelTypeBackgroundNoTokens",()=>u),e(t.exports,"panelSharedStyles",()=>b);let a={info:"#DEEBFF",note:"#EAE6FF",tip:"#E3FCEF",success:"#E3FCEF",warning:"#FFFAE6",error:"#FFEBE6"},o={info:"#0C294F",error:"#441C13",warning:"#413001",tip:"#052E21",success:"#052E21",note:"#282249",R900:"#601D16",R100S:"#FFEFEB",R300S:"#FFB5A3",R500S:"#FF6B47",R800S:"#C4320E",R1200S:"#441C13",Y900:"#533F04",Y100S:"#FFF3D1",Y300S:"#FFDC7A",Y500S:"#FFC933",Y800S:"#D8A003",Y1200S:"#413001",G900:"#164B35",G100S:"#E3FCF0",G300S:"#95EEC5",G400S:"#60DCA8",G900S:"#086848",G1200S:"#052E21",B900:"#09326C",B100S:"#E5F0FF",B300S:"#A3C9FF",B500S:"#4794FF",B800S:"#0055CC",B1200S:"#0C294F",P900:"#352C63",P100S:"#EEEBFF",P300S:"#CCC3FE",P500S:"#A292F7",P800S:"#5E49CA",P1200S:"#282249",T900:"#1D474C",T100S:"#DBFAFF",T300S:"#78EBFC",T400S:"#3AD6EE",T900S:"#056270",T1200S:"#0B3037",DarkGray:"#161A1D",Gray:"#2C333A",LightGray:"#5A6977",TextColor:"#D9DDE3"},i={info:"var(--ds-icon-information, #1D7AFC)",note:"var(--ds-icon-discovery, #8270DB)",tip:"var(--ds-icon-success, #22A06B)",success:"var(--ds-icon-success, #22A06B)",warning:"var(--ds-icon-warning, #E56910)",error:"var(--ds-icon-danger, #C9372C)"},s=-(24-n("aFUXX").akEditorCustomIconSize)/2,d=s-1,l="ak-editor-panel",c={prefix:l,content:`${l}__content`,icon:`${l}__icon`,noIcon:`${l}__no-icon`};n("kyLrk").PanelType.INFO,n("kyLrk").PanelType.NOTE,n("kyLrk").PanelType.WARNING,n("kyLrk").PanelType.ERROR,n("kyLrk").PanelType.SUCCESS;let p=e=>`
		.${c.icon}[data-panel-type='${e}'] {
			color: ${i[e]};
		}
	`,u=e=>a[e]||"none",m=e=>(0,n("6icEc").hexToEditorBackgroundPaletteColor)(a[e])||"none",h=e=>`
    background-color: ${m(e)};
    color: inherit;
  `,g=()=>(0,n("3jLHL").css)`
	border-radius: ${"var(--ds-border-radius, 3px)"};
	margin: ${n("aFUXX").blockNodesVerticalMargin} 0 0;
	padding-top: ${"var(--ds-space-100, 8px)"};
	padding-right: ${"var(--ds-space-200, 16px)"};
	padding-bottom: ${"var(--ds-space-100, 8px)"};
	padding-left: ${"var(--ds-space-100, 8px)"};
	min-width: ${n("aFUXX").akEditorTableCellMinWidth}px;
	display: flex;
	position: relative;
	align-items: normal;
	word-break: break-word;

	${h(n("kyLrk").PanelType.INFO)}

	.${c.icon} {
		flex-shrink: 0;
		height: ${"var(--ds-space-300, 24px)"};
		width: ${"var(--ds-space-300, 24px)"};
		box-sizing: content-box;
		padding-right: ${"var(--ds-space-100, 8px)"};
		text-align: center;
		user-select: none;
		-moz-user-select: none;
		-webkit-user-select: none;
		-ms-user-select: none;
		margin-top: 0.1em;

		> span {
			vertical-align: middle;
			display: inline-flex;
		}

		.${n("8hpYf").emojiSprite} {
			vertical-align: ${s}px;
		}

		.${n("8hpYf").emojiImage} {
			vertical-align: ${d}px;

			/* Vertical align only works for inline-block elements in Firefox */
			@-moz-document url-prefix() {
				img {
					display: inline-block;
				}
			}
		}
	}

	.ak-editor-panel__content {
		margin: ${"var(--ds-space-025, 2px)"} 0 ${"var(--ds-space-025, 2px)"};
		flex: 1 0 0;
		/*
      https://ishadeed.com/article/min-max-css/#setting-min-width-to-zero-with-flexbox
      The default value for min-width is auto, which is computed to zero. When an element is a flex item, the value of min-width doesn’t compute to zero. The minimum size of a flex item is equal to the size of its contents.
    */
		min-width: 0;
	}

	/* support nested panel */
	${(0,n("dh538").fg)("platform_editor_add_border_for_nested_panel")?`.${c.content} .${l} {
			border: 1px solid var(--ds-border, #091E42);
		}`:""}

	&[data-panel-type='${n("kyLrk").PanelType.INFO}'] {
		${p(n("kyLrk").PanelType.INFO)}
	}

	&[data-panel-type='${n("kyLrk").PanelType.NOTE}'] {
		${h(n("kyLrk").PanelType.NOTE)}
		${p(n("kyLrk").PanelType.NOTE)}
	}

	&[data-panel-type='${n("kyLrk").PanelType.TIP}'] {
		${h(n("kyLrk").PanelType.TIP)}
		${p(n("kyLrk").PanelType.TIP)}
	}

	&[data-panel-type='${n("kyLrk").PanelType.WARNING}'] {
		${h(n("kyLrk").PanelType.WARNING)}
		${p(n("kyLrk").PanelType.WARNING)}
	}

	&[data-panel-type='${n("kyLrk").PanelType.ERROR}'] {
		${h(n("kyLrk").PanelType.ERROR)}
		${p(n("kyLrk").PanelType.ERROR)}
	}

	&[data-panel-type='${n("kyLrk").PanelType.SUCCESS}'] {
		${h(n("kyLrk").PanelType.SUCCESS)}
		${p(n("kyLrk").PanelType.SUCCESS)}
	}

	${(0,n("dh538").fg)("platform_editor_nested_dnd_styles_changes")?`&.${c.noIcon} {
			padding-right: var(--ds-space-150, 12px);
			padding-left: var(--ds-space-150, 12px);
		}`:""}
`,b=()=>(0,n("3jLHL").css)({[`.${c.prefix}`]:g()})}),i("4AaC5",function(t,r){e(t.exports,"hideCaretModifier",()=>o),e(t.exports,"gapCursorStyles",()=>c);let a=(0,n("3jLHL").keyframes)({"from, to":{opacity:0},"50%":{opacity:1}}),o="ProseMirror-hide-gapcursor",i=".ProseMirror-gapcursor",s='.ProseMirror-widget:not([data-blocks-decoration-container="true"]):not([data-blocks-drag-handle-container="true"]):not([data-blocks-quick-insert-container="true"])',d='[layout="wrap-left"]',l='[layout="wrap-right"]',c=(0,n("3jLHL").css)`
	/* =============== GAP CURSOR ================== */
	.ProseMirror {
		&.${o} {
			caret-color: transparent;
		}

		${i} {
			display: none;
			pointer-events: none;
			position: relative;

			& span {
				caret-color: transparent;
				position: absolute;
				height: 100%;
				width: 100%;
				display: block;
			}

			& span::after {
				animation: 1s ${a} step-start infinite;
				border-left: 1px solid;
				content: '';
				display: block;
				position: absolute;
				top: 0;
				height: 100%;
			}
			&.-left span::after {
				left: ${"var(--ds-space-negative-050, -4px)"};
			}
			&.-right span::after {
				right: ${"var(--ds-space-negative-050, -4px)"};
			}
			& span[layout='full-width'],
			& span[layout='wide'],
			& span[layout='fixed-width'] {
				margin-left: 50%;
				transform: translateX(-50%);
			}
			&${l} {
				float: right;
			}

			/* fix vertical alignment of gap cursor */
			&:first-of-type + ul,
			&:first-of-type + span + ul,
			&:first-of-type + ol,
			&:first-of-type + span + ol,
			&:first-of-type + pre,
			&:first-of-type + span + pre,
			&:first-of-type + blockquote,
			&:first-of-type + span + blockquote {
				margin-top: 0;
			}
		}
		&.ProseMirror-focused ${i} {
			display: block;
			border-color: transparent;
		}
	}

	/* This hack below is for two images aligned side by side */
	${i}${d} + span + ${d},
  ${i}${l} + span + ${l},
  ${i} + ${d} + ${l},
  ${i} + ${d} + span + ${l},
  ${i} + ${l} + ${d},
  ${i} + ${l} + span + ${d},
  ${d} + ${i} + ${l},
  ${d} + ${i} + span ${l},
  ${l} + ${i} + ${d},
  ${l} + ${i} + span + ${d},
  ${d} + ${i} {
		clear: none;
	}

	${d} + ${i} + ${l} > div,
  ${d} + ${i} + span + ${l} > div,
  ${l} + ${i} + ${d} > div,
  ${l} + ${i} + span + ${d} > div,
  ${i} + ${l} + ${d} > div,
  ${i} + ${l} + span + ${d} > div,
  ${i} + ${d} + ${l} > div,
  ${i} + ${d} + span + ${l} > div {
		margin-right: 0;
		margin-left: 0;
		margin-bottom: 0;
	}

	${d} + ${i},
  ${l} + ${i} {
		float: left;
	}

	${i} + ${d} + span + ${l}::after,
  ${i} + ${l} + span + ${d}::after,
  ${d} + ${i} + ${l}::after,
  ${d} + ${i} + span + ${l}::after,
  ${l} + ${i} + ${d}::after,
  ${l} + ${i} + span + ${d}::after {
		visibility: hidden;
		display: block;
		font-size: 0;
		content: ' ';
		clear: both;
		height: 0;
	}

	${d} + ${i} + ${l} + *,
  ${d} + ${i} + ${l} + span + *,
  ${l} + ${i} + ${d} + *,
  ${l} + ${i} + ${d} + span + *,
  ${d} + ${i} + span + ${l} + *,
  ${l} + ${i} + span + ${d} + *,
  ${i} + ${d} + span + ${l} + *,
  ${i} + ${l} + span + ${d} + *,
  ${d} + ${i} + ${l} + * > *,
  ${d} + ${i} + ${l} + span + * > *,
  ${l} + ${i} + ${d} + * > *,
  ${l} + ${i} + ${d} + span + * > *,
  ${d} + ${i} + span + ${l} + * > *,
  ${l} + ${i} + span + ${d} + * > *,
  ${i} + ${d} + span + ${l} + * > *,
  ${i} + ${l} + span + ${d} + * > *,
  ${s} + ${i} + *,
  ${s} + ${i} + span + * {
		margin-top: 0;
	}
`}),i("6ESsx",function(t,r){e(t.exports,"AnnotationSharedClassNames",()=>o),e(t.exports,"BlockAnnotationSharedClassNames",()=>s),e(t.exports,"annotationSharedStyles",()=>l);let a="ak-editor-annotation",o={focus:`${a}-focus`,blur:`${a}-blur`,draft:`${a}-draft`,hover:`${a}-hover`},i="ak-editor-block-annotation",s={focus:`${i}-focus`,blur:`${i}-blur`,draft:`${i}-draft`},d=()=>(0,n("dh538").fg)("editor_inline_comments_on_inline_nodes")?{common:{borderBottom:"2px solid transparent",cursor:"pointer",padding:"1px 0 2px","&:has(.card), &:has([data-inline-card])":(0,n("dh538").fg)("annotations_align_editor_and_renderer_styles")?{padding:"5px 0 3px 0"}:{paddingTop:"4px",border:"none",boxShadow:"0 2px 0 0 var(--ds-border-accent-yellow, #B38600)"},"&:has(.date-lozenger-container)":{paddingTop:"2px"}},focus:(0,n("3jLHL").css)({background:"var(--ds-background-accent-yellow-subtlest-pressed, #F5CD47)",borderBottomColor:"var(--ds-border-accent-yellow, #B38600)",boxShadow:"var(--ds-shadow-raised, 0px 1px 1px #091E4240, 0px 0px 1px #091E424f)"}),blur:(0,n("3jLHL").css)({background:"var(--ds-background-accent-yellow-subtlest, #FFF7D6)",borderBottomColor:"var(--ds-border-accent-yellow, #B38600)"}),hover:(0,n("3jLHL").css)({background:"var(--ds-background-accent-yellow-subtlest-hovered, #F8E6A0)",borderBottomColor:"var(--ds-border-accent-yellow, #B38600)",boxShadow:"var(--ds-shadow-raised, 0px 1px 1px #091E4240, 0px 0px 1px #091E424f)"})}:{focus:(0,n("3jLHL").css)({background:"var(--ds-background-accent-yellow-subtler, #F8E6A0)",borderBottom:"2px solid var(--ds-border-accent-yellow, #B38600)",boxShadow:"var(--ds-shadow-overlay, 0px 8px 12px #091E4226, 0px 0px 1px #091E424f)",cursor:"pointer"}),blur:(0,n("3jLHL").css)({background:"var(--ds-background-accent-yellow-subtlest, #FFF7D6)",borderBottom:"2px solid var(--ds-border-accent-yellow, #B38600)",cursor:"pointer"})},l=()=>(0,n("dh538").fg)("editor_inline_comments_on_inline_nodes")?(0,n("3jLHL").css)`
				.ProseMirror {
					.${o.blur},
						.${o.focus},
						.${o.draft} {
						${d().common};
					}

					.${o.focus} {
						${d().focus};
					}

					.${o.draft} {
						${d().focus};
						cursor: initial;
					}

					.${o.blur} {
						${d().blur};
					}
					.${o.hover} {
						${d().common};
						${d().hover};
					}
				}
			`:(0,n("3jLHL").css)`
				.ProseMirror {
					.${o.focus} {
						${d().focus};
					}

					.${o.draft} {
						${d().focus};
						cursor: initial;
					}

					.${o.blur} {
						${d().blur};
					}
				}
			`}),i("52bSY",function(t,r){e(t.exports,"backgroundColorStyles",()=>a);let a=()=>(0,n("3jLHL").css)({".fabric-background-color-mark":{backgroundColor:"var(--custom-palette-color, inherit)",borderRadius:"2px",paddingTop:"1px",paddingBottom:"2px",boxDecorationBreak:"clone"},"a .fabric-background-color-mark":{backgroundColor:"unset"},".fabric-background-color-mark .ak-editor-annotation":{backgroundColor:"unset"}})}),i("kZBrC",function(t,r){e(t.exports,"blockMarksSharedStyles",()=>a);let a=(0,n("3jLHL").css)`
	/**
   * We need to remove margin-top from first item
   * inside doc, tableCell, tableHeader, blockquote, etc.
   */
	*:not(.fabric-editor-block-mark) >,
  /* For nested block marks apart from those with indentation mark */
  *:not(.fabric-editor-block-mark) >
    div.fabric-editor-block-mark:first-of-type
    /* Do not remove the margin top for nodes inside indentation marks */
      :not(.fabric-editor-indentation-mark)
    /* Do not remove the margin top for nodes inside alignment marks */
      :not(.fabric-editor-alignment),
  /* If first element inside a block node has alignment mark, then remove the margin-top */
  .fabric-editor-alignment:first-of-type:first-child,
  /* If first document element has indentation mark remove margin-top */
  .ProseMirror .fabric-editor-indentation-mark:first-of-type:first-child {
		p,
		h1,
		h2,
		h3,
		h4,
		h5,
		h6,
		.heading-wrapper {
			:first-child:not(style),
			style:first-child + * {
				margin-top: 0;
			}
		}
	}
`}),i("7zsay",function(t,r){e(t.exports,"codeMarkSharedStyles",()=>a);let a=()=>(0,n("3jLHL").css)({".code":{"--ds--code--bg-color":"var(--ds-background-neutral, #091E420F)",display:"inline",padding:"2px 0.5ch",backgroundColor:"var(--ds--code--bg-color,var(--ds-background-neutral, #091E420F))",borderRadius:"var(--ds-border-radius, 3px)",borderStyle:"none",boxDecorationBreak:"clone",color:"var(--ds-text, #172B4D)",fontFamily:'var(--ds-font-family-code, ui-monospace, Menlo, "Segoe UI Mono", "Ubuntu Mono", monospace)',fontSize:"0.875em",fontWeight:"var(--ds-font-weight-regular, 400)",overflow:"auto",overflowWrap:"break-word",whiteSpace:"pre-wrap"}})}),i("xdUPw",function(t,r){e(t.exports,"embedCardStyles",()=>a);let a=()=>(0,n("3jLHL").css)({".ProseMirror":{".embedCardView-content-wrap[layout^='wrap-']":{maxWidth:"100%",position:"relative",zIndex:n("aFUXX").akEditorWrappedNodeZIndex},".embedCardView-content-wrap[layout='wrap-left']":{float:"left"},".embedCardView-content-wrap[layout='wrap-right']":{float:"right"},".embedCardView-content-wrap[layout='wrap-right'] + .embedCardView-content-wrap[layout='wrap-left']":{clear:"both"}}});(0,n("3jLHL").css)({margin:"0 var(--ds-space-150, 12px)"})}),i("iMS6j",function(t,r){e(t.exports,"expandIconWrapperStyle",()=>a),e(t.exports,"expandIconContainerStyle",()=>o),e(t.exports,"expandClassNames",()=>s);let a=(0,n("3jLHL").css)({marginLeft:"var(--ds-space-negative-100, -8px)"}),o=(0,n("3jLHL").css)({display:"flex",alignItems:"center"}),i="ak-editor-expand",s={prefix:i,expanded:`${i}__expanded`,titleContainer:`${i}__title-container`,inputContainer:`${i}__input-container`,iconContainer:`${i}__icon-container`,icon:`${i}__icon`,titleInput:`${i}__title-input`,content:`${i}__content`,type:e=>`${i}__type-${e}`}}),i("87iYj",function(t,r){e(t.exports,"GRID_GUTTER",()=>a),e(t.exports,"gridStyles",()=>o);let a=12,o=(0,n("3jLHL").css)({".gridParent":{width:`calc(100% + ${2*a}px)`,marginLeft:"var(--ds-space-negative-150, -12px)",marginRight:"var(--ds-space-negative-150, -12px)",transform:"scale(1)",zIndex:n("aFUXX").akEditorGridLineZIndex},".gridContainer":{position:"fixed",height:"100vh",width:"100%",pointerEvents:"none"},".gridLine":{borderLeft:"1px solid var(--ds-border, #091E4224)",display:"inline-block",boxSizing:"border-box",height:"100%",marginLeft:"-1px",transition:"border-color 0.15s linear",zIndex:0},".highlight":{borderLeft:"1px solid var(--ds-border-focused, #388BFF)"}})}),i("diPla",function(t,r){e(t.exports,"indentationSharedStyles",()=>a);let a=(0,n("3jLHL").css)({".fabric-editor-indentation-mark":{"&[data-level='1']":{marginLeft:"30px"},"&[data-level='2']":{marginLeft:"60px"},"&[data-level='3']":{marginLeft:"90px"},"&[data-level='4']":{marginLeft:"120px"},"&[data-level='5']":{marginLeft:"150px"},"&[data-level='6']":{marginLeft:"180px"}}})}),i("idF2b",function(t,r){e(t.exports,"linkSharedStyle",()=>a);let a=()=>(0,n("dh538").fg)("platform_editor_hyperlink_underline")?(0,n("3jLHL").css)({"a.blockLink":{display:"block"},'a[data-prosemirror-mark-name="link"]':{textDecoration:"underline"},'a[data-prosemirror-mark-name="link"]:hover':{textDecoration:"none"}}):(0,n("3jLHL").css)({"a.blockLink":{display:"block"}})}),i("3Khgq",function(t,r){e(t.exports,"paragraphSharedStyles",()=>a);let a=e=>(0,n("dh538").fg)("platform_editor_typography_ugc")?(0,n("3jLHL").css)({"& p":{font:(0,n("ilPbq").default)("editor.font.body"),marginTop:n("aFUXX").blockNodesVerticalMargin,marginBottom:0}}):(0,n("3jLHL").css)({"& p":{fontSize:"1em",lineHeight:n("aFUXX").akEditorLineHeight,fontWeight:"var(--ds-font-weight-regular, 400)",marginTop:n("aFUXX").blockNodesVerticalMargin,marginBottom:0,letterSpacing:"-0.005em"}})}),i("7QdQz",function(t,r){e(t.exports,"resizerItemClassName",()=>i),e(t.exports,"resizerHoverZoneClassName",()=>s),e(t.exports,"resizerExtendedZone",()=>d),e(t.exports,"resizerHandleClassName",()=>l),e(t.exports,"resizerHandleTrackClassName",()=>c),e(t.exports,"resizerHandleThumbClassName",()=>p),e(t.exports,"resizerDangerClassName",()=>u),e(t.exports,"handleWrapperClass",()=>m),e(t.exports,"resizerHandleThumbWidth",()=>h),e(t.exports,"resizerHandleZIndex",()=>g),e(t.exports,"resizerStyles",()=>b),e(t.exports,"pragmaticResizerStylesForTooltip",()=>f),e(t.exports,"pragmaticStylesLayoutFirstNodeResizeHandleFix",()=>x),e(t.exports,"pragmaticResizerStyles",()=>v);var a=n("dZ8uq"),o=n("iu6m9");let i="resizer-item",s="resizer-hover-zone",d="resizer-is-extended",l="resizer-handle",c=`${l}-track`,p=`${l}-thumb`,u=`${l}-danger`,m="resizer-handle-wrapper",h=3,g=1,b=(0,n("3jLHL").css)`
	.${i} {
		will-change: width;

		&:hover,
		&.display-handle {
			& > .${m} > .${l} {
				visibility: visible;
				opacity: 1;
			}
		}

		&.is-resizing {
			& .${p} {
				background: ${"var(--ds-border-focused, #388BFF)"};
			}
		}

		&.${u} {
			& .${p} {
				transition: none;
				background: ${`var(--ds-icon-danger, ${n("aFUXX").akEditorDeleteIconColor})`};
			}
		}
	}

	.${l} {
		display: flex;
		visibility: hidden;
		opacity: 0;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		width: 7px;
		transition:
			visibility 0.2s,
			opacity 0.2s;

		/*
      NOTE: The below style is targeted at the div element added by the tooltip. We don't have any means of injecting styles
      into the tooltip
    */
		& div[role='presentation'] {
			width: 100%;
			height: 100%;
			display: flex;
			flex-direction: column;
			justify-content: center;
			align-items: center;
			margin-top: ${"var(--ds-space-negative-200, -16px)"};
			white-space: normal;
		}

		/*
      Handle Positions
    */
		&.left {
			align-items: flex-start;
		}
		&.right {
			align-items: flex-end;
		}

		/*
      Handle Sizing
    */
		&.small {
			& .${p} {
				height: 43px;
			}
		}
		&.medium {
			& .${p} {
				height: 64px;
			}
		}
		&.large {
			& .${p} {
				height: 96px;
			}
		}
		&.clamped {
			& .${p} {
				height: clamp(43px, calc(100% - 32px), 96px);
			}
		}

		/*
      Handle Alignment
    */
		&.sticky {
			& .${p} {
				position: sticky;
				top: ${"var(--ds-space-150, 12px)"};
				bottom: ${"var(--ds-space-150, 12px)"};
			}
		}

		&:hover {
			& .${p} {
				background: ${"var(--ds-border-focused, #388BFF)"};
			}

			& .${c} {
				visibility: visible;
				opacity: 0.5;
			}
		}
	}

	.${p} {
		content: ' ';
		display: flex;
		width: 3px;
		margin: 0 ${"var(--ds-space-025, 2px)"};
		height: 64px;
		transition: background-color 0.2s;
		border-radius: 6px;
		border: 0;
		padding: 0;
		z-index: 2;
		outline: none;
		min-height: 24px;
		background: ${"var(--ds-border, #091E4224)"};

		&:hover {
			cursor: col-resize;
		}

		&:focus {
			background: ${"var(--ds-border-selected, #0C66E4)"};

			&::after {
				content: '';
				position: absolute;
				top: ${"var(--ds-space-negative-050, -4px)"};
				right: ${"var(--ds-space-negative-050, -4px)"};
				bottom: ${"var(--ds-space-negative-050, -4px)"};
				left: ${"var(--ds-space-negative-050, -4px)"};
				border: 2px solid ${"var(--ds-border-focused, #388BFF)"};
				border-radius: inherit;
				z-index: -1;
			}
		}
	}

	.${c} {
		visibility: hidden;
		position: absolute;
		width: 7px;
		height: calc(100% - 40px);
		border-radius: 4px;
		opacity: 0;
		transition:
			background-color 0.2s,
			visibility 0.2s,
			opacity 0.2s;

		&.none {
			background: none;
		}

		&.shadow {
			background: ${"var(--ds-background-selected, #E9F2FF)"};
		}

		&.full-height {
			background: ${"var(--ds-background-selected, #E9F2FF)"};
			height: 100%;
			min-height: 36px;
		}
	}

	.${"ak-editor-selected-node"} {
		& .${p} {
			background: ${"var(--ds-border-focused, #388BFF)"};
		}
	}

	.${s} {
		position: relative;
		display: inline-block;
		width: 100%;

		&.${d} {
			padding: 0 ${"var(--ds-space-150, 12px)"};
			left: ${"var(--ds-space-negative-150, -12px)"};
		}
	}

	/* This below style is here to make sure the image width is correct when nested in a table */
	table .${s}, table .${s}.${d} {
		padding: unset;
		left: unset;
	}
`,f=()=>{if((0,a.expValEqualsNoExposure)("platform_editor_breakout_resizing","isEnabled",!0)&&(0,n("dh538").fg)("platform_editor_breakout_resizing_hello_release"))return(0,n("3jLHL").css)({".pm-breakout-resize-handle-rail-wrapper":{display:"flex",alignItems:"center",justifyContent:"center",height:"100%",cursor:"col-resize",borderRadius:4,zIndex:2,'[role="presentation"]':{height:"100%",width:"100%"},".pm-breakout-resize-handle-rail-inside-tooltip":{height:"100%"}}})},x=()=>{if((0,o.editorExperiment)("advanced_layouts",!0)&&(0,a.expValEqualsNoExposure)("platform_editor_breakout_resizing","isEnabled",!0)&&(0,n("dh538").fg)("platform_editor_breakout_resizing_hello_release"))return(0,n("3jLHL").css)({".fabric-editor-breakout-mark":{'&:has([data-prosemirror-node-name="layoutSection"].first-node-in-document)':{"> .pm-breakout-resize-handle-container":{height:"calc(100% - 8px)"}}}})},v=()=>{if((0,a.expValEqualsNoExposure)("platform_editor_breakout_resizing","isEnabled",!0))return(0,n("dh538").fg)("platform_editor_breakout_resizing_hello_release")?(0,n("3jLHL").css)({".fabric-editor-breakout-mark":{'&:has([data-prosemirror-node-name="codeBlock"])':{"> .pm-breakout-resize-handle-container--left":{left:"-5px"},"> .pm-breakout-resize-handle-container--right":{right:"-5px"},"> .pm-breakout-resize-handle-container":{height:"calc(100% - 12px)"}},'&:has([data-prosemirror-node-name="expand"]), &:has([data-prosemirror-node-name="layoutSection"])':{"> .pm-breakout-resize-handle-container--left":{left:"-25px"},"> .pm-breakout-resize-handle-container--right":{right:"-25px"}},'&:has([data-prosemirror-node-name="expand"])':{"> .pm-breakout-resize-handle-container":{height:"calc(100% - 4px)"}},'&:has([data-prosemirror-node-name="layoutSection"])':{"> .pm-breakout-resize-handle-container":{height:"calc(100% - 8px)"}},"&:has(.first-node-in-document)":{"> .pm-breakout-resize-handle-container":{height:"100%"}}},".pm-breakout-resize-handle-container":{position:"relative",alignSelf:"end",gridRow:1,gridColumn:1,height:"100%",width:7},".pm-breakout-resize-handle-container--left":{justifySelf:"start"},".pm-breakout-resize-handle-container--right":{justifySelf:"end"},".pm-breakout-resize-handle-rail":{position:"relative",display:"flex",alignItems:"center",justifyContent:"center",height:"100%",cursor:"col-resize",borderRadius:4,transition:"background-color 0.2s, visibility 0.2s, opacity 0.2s",zIndex:2,opacity:0,"&:hover":{background:"var(--ds-background-selected, #E9F2FF)",".pm-breakout-resize-handle-thumb":{background:"var(--ds-border-focused, #388BFF)"}}},".pm-breakout-resize-handle-container--active":{background:"var(--ds-background-selected, #E9F2FF)",".pm-breakout-resize-handle-thumb":{background:"var(--ds-border-focused, #388BFF)"}},".pm-breakout-resize-handle-hit-box":{position:"absolute",top:0,bottom:0,left:-20,right:-20,zIndex:0},".pm-breakout-resize-handle-thumb":{minWidth:h,height:"clamp(27px, calc(100% - 32px), 96px)",background:"var(--ds-border, #091E4224)",borderRadius:6,position:"sticky",top:"var(--ds-space-150, 12px)",bottom:"var(--ds-space-150, 12px)"}}):(0,n("3jLHL").css)({".fabric-editor-breakout-mark":{'&:has([data-prosemirror-node-name="codeBlock"])':{"> .pm-breakout-resize-handle-container--left":{left:"-12px"},"> .pm-breakout-resize-handle-container--right":{right:"-12px"},"> .pm-breakout-resize-handle-container":{height:"calc(100% - 12px)"}},'&:has([data-prosemirror-node-name="expand"]), &:has([data-prosemirror-node-name="layoutSection"])':{"> .pm-breakout-resize-handle-container--left":{left:"-32px"},"> .pm-breakout-resize-handle-container--right":{right:"-32px"}},'&:has([data-prosemirror-node-name="expand"])':{"> .pm-breakout-resize-handle-container":{height:"calc(100% - 4px)"}},'&:has([data-prosemirror-node-name="layoutSection"])':{"> .pm-breakout-resize-handle-container":{height:"calc(100% - 8px)"}},"&:has(.first-node-in-document)":{"> .pm-breakout-resize-handle-container":{height:"100%"}}},".pm-breakout-resize-handle-container":{position:"relative",alignSelf:"end",gridRow:1,gridColumn:1,height:"100%",width:7},".pm-breakout-resize-handle-container--left":{justifySelf:"start"},".pm-breakout-resize-handle-container--right":{justifySelf:"end"},".pm-breakout-resize-handle-rail":{position:"relative",display:"flex",alignItems:"center",justifyContent:"center",height:"100%",cursor:"col-resize",borderRadius:4,transition:"background-color 0.2s, visibility 0.2s, opacity 0.2s",zIndex:2,opacity:0,"&:hover":{background:"var(--ds-background-selected, #E9F2FF)",".pm-breakout-resize-handle-thumb":{background:"var(--ds-border-focused, #388BFF)"}}},".pm-breakout-resize-handle-container--active":{background:"var(--ds-background-selected, #E9F2FF)",".pm-breakout-resize-handle-thumb":{background:"var(--ds-border-focused, #388BFF)"}},".pm-breakout-resize-handle-hit-box":{position:"absolute",top:0,bottom:0,left:-20,right:-20,zIndex:0},".pm-breakout-resize-handle-thumb":{minWidth:h,height:"clamp(27px, calc(100% - 32px), 96px)",background:"var(--ds-border, #091E4224)",borderRadius:6,position:"sticky",top:"var(--ds-space-150, 12px)",bottom:"var(--ds-space-150, 12px)"}})}}),i("dZ8uq",function(t,r){e(t.exports,"expValEqualsNoExposure",()=>o);var a=n("8Qxmq");function o(e,t,r,n=null){return(0,a.expValEqualsInternal)(e,t,r,n,!1)}}),i("eRvLS",function(t,r){e(t.exports,"ruleSharedStyles",()=>a);let a=()=>(0,n("3jLHL").css)({"& hr":{border:"none",backgroundColor:"var(--ds-border, #091E4224)",margin:`${n("aFUXX").akEditorLineHeight}em 0`,height:"2px",borderRadius:"1px"}})}),i("cRffC",function(t,r){e(t.exports,"shadowSharedStyle",()=>a);let a=(0,n("3jLHL").css)({[`& .${n("frt7o").shadowClassNames.RIGHT_SHADOW}::before, .${n("frt7o").shadowClassNames.RIGHT_SHADOW}::after, .${n("frt7o").shadowClassNames.LEFT_SHADOW}::before, .${n("frt7o").shadowClassNames.LEFT_SHADOW}::after`]:{display:"none",position:"absolute",pointerEvents:"none",zIndex:n("aFUXX").akEditorShadowZIndex,width:"8px",content:"''",height:"calc(100%)"},[`& .${n("frt7o").shadowClassNames.RIGHT_SHADOW}, .${n("frt7o").shadowClassNames.LEFT_SHADOW}`]:{position:"relative"},[`& .${n("frt7o").shadowClassNames.LEFT_SHADOW}::before`]:{background:"linear-gradient( to left, transparent 0, var(--ds-shadow-overflow-spread, #091e4229) 140% ), linear-gradient( to right, var(--ds-shadow-overflow-perimeter, transparent) 0px, transparent 1px )",top:"0px",left:0,display:"block"},[`& .${n("frt7o").shadowClassNames.RIGHT_SHADOW}::after`]:{background:"linear-gradient( to right, transparent 0, var(--ds-shadow-overflow-spread, #091e4229) 140% ), linear-gradient( to left, var(--ds-shadow-overflow-perimeter, transparent) 0px, transparent 1px )",right:"0px",top:"0px",display:"block"},[`& .${n("fp8V7").shadowObserverClassNames.SENTINEL_LEFT}`]:{height:"100%",width:"0px",minWidth:"0px"},[`& .${n("fp8V7").shadowObserverClassNames.SENTINEL_RIGHT}`]:{height:"100%",width:"0px",minWidth:"0px"}})}),i("0vvte",function(t,r){e(t.exports,"DATASOURCE_INNER_CONTAINER_CLASSNAME",()=>o),e(t.exports,"FLOATING_TOOLBAR_LINKPICKER_CLASSNAME",()=>i),e(t.exports,"smartCardStyles",()=>s);var a=n("iu6m9");let o="datasourceView-content-inner-wrap",i="card-floating-toolbar--link-picker",s=()=>(0,n("3jLHL").css)`
	.${n("cV5SN").SmartCardSharedCssClassName.INLINE_CARD_CONTAINER} {
		max-width: calc(100% - 20px);
		vertical-align: top;
		word-break: break-all;
		${(0,n("dh538").fg)("editor_inline_comments_on_inline_nodes")?`.card-with-comment {
          background: var(--ds-background-accent-yellow-subtler, #F8E6A0);
          border-bottom: 2px solid var(--ds-border-accent-yellow, #B38600);
          box-shadow: var(--ds-shadow-overlay, 0px 8px 12px #091E4226, 0px 0px 1px #091E424f);
        }`:""}
		.card {
			padding-left: ${"var(--ds-space-025, 2px)"};
			padding-right: ${"var(--ds-space-025, 2px)"};
			padding-top: 0.5em;
			padding-bottom: 0.5em;
			margin-bottom: -0.5em;

			.${n("cV5SN").SmartCardSharedCssClassName.LOADER_WRAPPER} > a:focus {
				${(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.BoxShadow])}
			}
		}

		${(0,a.editorExperiment)("platform_editor_controls","variant1")?`[data-inlinecard-button-overlay='icon-wrapper-line-height'] span {
				line-height: 0;
			}`:""}

		&.${n("aFUXX").akEditorSelectedNodeClassName} .${n("cV5SN").SmartCardSharedCssClassName.LOADER_WRAPPER} > a {
			${(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.BoxShadow])}
		}
		.${n("cV5SN").SmartCardSharedCssClassName.LOADER_WRAPPER} > a {
			/* EDM-1717: box-shadow Safari fix start */
			z-index: 1;
			position: relative;
			/* EDM-1717: box-shadow Safari fix end */
		}

		&.danger {
			.${n("cV5SN").SmartCardSharedCssClassName.LOADER_WRAPPER} > a {
				box-shadow: 0 0 0 1px ${`var(--ds-border-danger, ${n("aFUXX").akEditorDeleteBorder})`};
				/* EDM-1717: box-shadow Safari fix start */
				z-index: 2;
				/* EDM-1717: box-shadow Safari fix end */
			}
		}
	}

	.${n("cV5SN").SmartCardSharedCssClassName.BLOCK_CARD_CONTAINER} {
		.${n("cV5SN").SmartCardSharedCssClassName.LOADER_WRAPPER} > div {
			cursor: ${(0,n("dh538").fg)("linking_platform_smart_links_in_live_pages")?"text":"pointer"};

			a {
				cursor: ${(0,n("dh538").fg)("linking_platform_smart_links_in_live_pages")?"pointer":"auto"};
			}
		}

		&.${n("aFUXX").akEditorSelectedNodeClassName} .${n("cV5SN").SmartCardSharedCssClassName.LOADER_WRAPPER} > div {
			${(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.BoxShadow])}
			border-radius: ${"var(--ds-border-radius-200, 8px)"};
		}

		&.danger {
			.${n("cV5SN").SmartCardSharedCssClassName.LOADER_WRAPPER} > div {
				box-shadow: 0 0 0 1px ${`var(--ds-border-danger, ${n("aFUXX").akEditorDeleteBorder})`} !important;
			}
		}
	}

	.${n("cV5SN").SmartCardSharedCssClassName.DATASOURCE_CONTAINER}.${n("cV5SN").SmartCardSharedCssClassName.BLOCK_CARD_CONTAINER} {
		max-width: 100%;
		display: flex;
		justify-content: center;

		.${o} {
			cursor: pointer;
			background-color: ${"var(--ds-background-neutral-subtle, #00000000)"};
			border-radius: ${"var(--ds-border-radius-200, 8px)"};
			border: 1px solid ${"var(--ds-border, #091E4224)"};
			overflow: hidden;
		}

		&.${n("aFUXX").akEditorSelectedNodeClassName} {
			.${o} {
				${(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.BoxShadow])}

				input::selection {
					background-color: ${"var(--ds-background-selected-hovered, #CCE0FF)"};
				}
				input::-moz-selection {
					background-color: ${"var(--ds-background-selected-hovered, #CCE0FF)"};
				}
			}
		}

		&.danger {
			.${o} {
				box-shadow: 0 0 0 1px ${`var(--ds-border-danger, ${n("aFUXX").akEditorDeleteBorder})`};
			}
		}
	}

	.${n("cV5SN").SmartCardSharedCssClassName.EMBED_CARD_CONTAINER} {
		.${n("cV5SN").SmartCardSharedCssClassName.LOADER_WRAPPER} > div {
			cursor: pointer;
			a {
				cursor: ${(0,n("dh538").fg)("linking_platform_smart_links_in_live_pages")?"pointer":"auto"};
			}
			&::after {
				transition: box-shadow 0s;
			}
		}

		&.${n("aFUXX").akEditorSelectedNodeClassName} .${n("cV5SN").SmartCardSharedCssClassName.LOADER_WRAPPER} > div::after {
			${(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.BoxShadow])}
		}

		&.danger {
			.media-card-frame::after {
				box-shadow: 0 0 0 1px ${`var(--ds-border-danger, ${n("aFUXX").akEditorDeleteBorder})`} !important;
				background: ${`var(--ds-background-danger, ${n("aFUXX").akEditorDeleteBackground})`} !important;
			}
			.richMedia-resize-handle-right::after,
			.richMedia-resize-handle-left::after {
				background: ${`var(--ds-border-danger, ${n("aFUXX").akEditorDeleteBorder})`};
			}
		}
	}

	.${i} {
		padding: 0;
	}
`}),i("ieXGd",function(t,r){e(t.exports,"getSelectionStyles",()=>a),e(t.exports,"hideNativeBrowserTextSelectionStyles",()=>o);let a=e=>e.map(e=>i(e)).concat(o).join("\n"),o=`
  ::selection,*::selection {
    background-color: transparent;
  }
  ::-moz-selection,*::-moz-selection {
    background-color: transparent;
  }
`,i=e=>{switch(e){case n("b38UX").SelectionStyle.Border:return`
        border: ${n("aFUXX").akEditorSelectedBorder};

        // Fixes ED-15246: Trello card is visible through a border of a table border
        &::after {
          height: 100%;
          content: '\\00a0';
          background: ${n("aFUXX").akEditorSelectedBorderColor};
          position: absolute;
          right: -1px;
          top: 0;
          bottom: 0;
          width: 1px;
          border: none;
          display: inline-block;
        }
      `;case n("b38UX").SelectionStyle.BoxShadow:return`
        box-shadow: ${n("aFUXX").akEditorSelectedBoxShadow};
        border-color: transparent;
        `;case n("b38UX").SelectionStyle.Background:return"background-color: var(--ds-background-selected, #E9F2FF);";case n("b38UX").SelectionStyle.Blanket:return`
        position: relative;

        // Fixes ED-9263, where emoji or inline card in panel makes selection go outside the panel
        // in Safari. Looks like it's caused by user-select: all in the emoji element
        -webkit-user-select: text;

        ::before {
          position: absolute;
          content: '';
          left: 0;
          right: 0;
          top: 0;
          bottom: 0;
          width: 100%;
          pointer-events: none;
          z-index: ${n("aFUXX").akEditorSmallZIndex};
          background-color: var(--ds-blanket-selected, #388BFF14)
        }`;default:return""}}}),i("b38UX",function(t,r){e(t.exports,"SelectionStyle",()=>o);var a,o=((a={})[a.Border=0]="Border",a[a.BoxShadow=1]="BoxShadow",a[a.Background=2]="Background",a[a.Blanket=3]="Blanket",a)}),i("4h2HM",function(t,r){e(t.exports,"textColorStyles",()=>a);let a=(0,n("3jLHL").css)({".fabric-text-color-mark":{color:"var(--custom-palette-color, inherit)"},"a .fabric-text-color-mark":{color:"unset"}})}),i("2wkZs",function(t,r){e(t.exports,"UnsupportedSharedCssClassName",()=>a),e(t.exports,"unsupportedStyles",()=>s);let a={BLOCK_CONTAINER:"unsupportedBlockView-content-wrap",INLINE_CONTAINER:"unsupportedInlineView-content-wrap"},o=`.${a.INLINE_CONTAINER} > span:nth-of-type(2)`,i=`.${a.BLOCK_CONTAINER} > div`,s=(0,n("3jLHL").css)`
	${i}, ${o} {
		cursor: pointer;
	}

	.${n("aFUXX").akEditorSelectedNodeClassName}${i},
		.${n("aFUXX").akEditorSelectedNodeClassName}${o} {
		${(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.Background,n("b38UX").SelectionStyle.Border])}
	}

	.danger {
		.${n("aFUXX").akEditorSelectedNodeClassName}${i},
			.${n("aFUXX").akEditorSelectedNodeClassName}${o} {
			border: ${n("aFUXX").akEditorSelectedBorderSize}px solid
				${`var(--ds-border-danger, ${n("aFUXX").akEditorDeleteBorder})`};
			background-color: ${`var(--ds-blanket-danger, ${n("aFUXX").akEditorDeleteBackgroundWithOpacity})`};
		}
	}
`}),i("3iemu",function(t,r){e(t.exports,"whitespaceSharedStyles",()=>a);let a=(0,n("3jLHL").css)({wordWrap:"break-word",whiteSpace:"pre-wrap"})}),i("o46Yq",function(t,r){e(t.exports,"blocktypeStyles",()=>n("4jPB7").blocktypeStyles)}),i("4jPB7",function(t,r){e(t.exports,"blocktypeStyles",()=>a);let a=e=>(0,n("3jLHL").css)`
	.ProseMirror {
		${n("bEu8b").blockquoteSharedStyles};
		${(0,n("8tkd3").headingsSharedStyles)(e)};
	}

	${(0,n("dh538").fg)("platform_editor_nested_dnd_styles_changes")&&`.ak-editor-content-area.appearance-full-page .ProseMirror blockquote {
		padding-left: var(--ds-space-250, 20px);
	}

	/* Don't want extra padding for inline editor (nested) */
	.ak-editor-content-area .ak-editor-content-area .ProseMirror blockquote {
		padding-left: var(--ds-space-200, 16px);
	}`}
`}),i("bEu8b",function(t,r){e(t.exports,"blockquoteSharedStyles",()=>a);let a=(0,n("3jLHL").css)({"& blockquote":{boxSizing:"border-box",color:"inherit",width:"100%",display:"inline-block",paddingLeft:"var(--ds-space-200, 16px)",borderLeft:`2px solid var(--ds-border, ${n("aFUXX").akEditorBlockquoteBorderColor})`,margin:`${n("aFUXX").blockNodesVerticalMargin} 0 0 0`,marginRight:0,"[dir='rtl'] &":{paddingLeft:0,paddingRight:"var(--ds-space-200, 16px)"},"&:first-child":{marginTop:0},"&::before":{content:"''"},"&::after":{content:"none"},"& p":{display:"block"},"& table, & table:last-child":{display:"inline-table"},"> .code-block:last-child, >.mediaSingleView-content-wrap:last-child, >.mediaGroupView-content-wrap:last-child":{display:"block"},"> .extensionView-content-wrap:last-child":{display:"block"}}})}),i("8tkd3",function(t,r){e(t.exports,"headingsSharedStyles",()=>o);let a=()=>({".fabric-editor-block-mark.fabric-editor-alignment:not(:first-child)":{"> h1:first-child":{marginTop:"1.667em"}," > h2:first-child":{marginTop:"1.8em"},"> h3:first-child":{marginTop:"2em"},"> h4:first-child":{marginTop:"1.357em"},"> h5:first-child":{marginTop:"1.667em"},"> h6:first-child":{marginTop:"1.455em"}},".ProseMirror-gapcursor:first-child + .fabric-editor-block-mark.fabric-editor-alignment, .ProseMirror-widget:first-child + .fabric-editor-block-mark.fabric-editor-alignment, .ProseMirror-widget:first-child + .ProseMirror-widget:nth-child(2) + .fabric-editor-block-mark.fabric-editor-alignment":{"> :is(h1, h2, h3, h4, h5, h6):first-child":{marginTop:"0"}}}),o=e=>(0,n("dh538").fg)("platform_editor_typography_ugc")?(0,n("3jLHL").css)({"& h1":{font:(0,n("ilPbq").default)("editor.font.heading.h1"),marginBottom:0,marginTop:"1.45833em","& strong":{fontWeight:(0,n("ilPbq").default)("editor.font.weight.heading.h1.bold")},"&::before":{}},"& h2":{font:(0,n("ilPbq").default)("editor.font.heading.h2"),marginTop:"1.4em",marginBottom:0,"& strong":{fontWeight:(0,n("ilPbq").default)("editor.font.weight.heading.h1.bold")}},"& h3":{font:(0,n("ilPbq").default)("editor.font.heading.h3"),marginTop:"1.31249em",marginBottom:0,"& strong":{fontWeight:(0,n("ilPbq").default)("editor.font.weight.heading.h1.bold")}},"& h4":{font:(0,n("ilPbq").default)("editor.font.heading.h4"),marginTop:"1.25em","& strong":{fontWeight:(0,n("ilPbq").default)("editor.font.weight.heading.h1.bold")}},"& h5":{font:(0,n("ilPbq").default)("editor.font.heading.h5"),marginTop:"1.45833em",textTransform:"none","& strong":{fontWeight:(0,n("ilPbq").default)("editor.font.weight.heading.h1.bold")}},"& h6":{font:(0,n("ilPbq").default)("editor.font.heading.h6"),marginTop:"1.59091em",textTransform:"none","& strong":{fontWeight:(0,n("ilPbq").default)("editor.font.weight.heading.h1.bold")}},...a()}):(0,n("3jLHL").css)({"& h1":{fontSize:`${24/14}em`,fontStyle:"inherit",lineHeight:28/24,color:"var(--ds-text, #172B4D)",fontWeight:"var(--ds-font-weight-medium, 500)",letterSpacing:"-0.01em",marginBottom:0,marginTop:"1.667em"},"& h2":{fontSize:`${20/14}em`,fontStyle:"inherit",lineHeight:1.2,color:"var(--ds-text, #172B4D)",fontWeight:"var(--ds-font-weight-medium, 500)",letterSpacing:"-0.008em",marginTop:"1.8em",marginBottom:0},"& h3":{fontSize:`${16/14}em`,fontStyle:"inherit",lineHeight:1.25,color:"var(--ds-text, #172B4D)",fontWeight:"var(--ds-font-weight-semibold, 600)",letterSpacing:"-0.006em",marginTop:"2em",marginBottom:0},"& h4":{fontSize:"1em",fontStyle:"inherit",lineHeight:16/14,color:"var(--ds-text, #172B4D)",fontWeight:"var(--ds-font-weight-semibold, 600)",letterSpacing:"-0.003em",marginTop:"1.357em"},"& h5":{fontSize:`${12/14}em`,fontStyle:"inherit",lineHeight:16/12,color:"var(--ds-text, #172B4D)",fontWeight:"var(--ds-font-weight-semibold, 600)",marginTop:"1.667em",textTransform:"none"},"& h6":{fontSize:`${11/14}em`,fontStyle:"inherit",lineHeight:16/11,color:"var(--ds-text-subtlest, #626F86)",fontWeight:"var(--ds-font-weight-bold, 700)",marginTop:"1.455em",textTransform:"none"},...a()})}),i("9PfP2",function(t,r){e(t.exports,"findReplaceStyles",()=>n("hAOTs").findReplaceStyles),e(t.exports,"findReplaceStylesNewYellow",()=>n("hAOTs").findReplaceStylesNewYellow),e(t.exports,"findReplaceStylesNewMagenta",()=>n("hAOTs").findReplaceStylesNewMagenta)}),i("hAOTs",function(t,r){e(t.exports,"searchMatchClass",()=>a),e(t.exports,"searchMatchTextClass",()=>o),e(t.exports,"selectedSearchMatchClass",()=>i),e(t.exports,"blockSearchMatchClass",()=>s),e(t.exports,"selectedBlockSearchMatchClass",()=>d),e(t.exports,"darkModeSearchMatchClass",()=>l),e(t.exports,"searchMatchExpandTitleClass",()=>c),e(t.exports,"findReplaceStyles",()=>g),e(t.exports,"findReplaceStylesNewYellow",()=>b),e(t.exports,"findReplaceStylesNewMagenta",()=>f);let a="search-match",o="search-match-text",i="selected-search-match",s="search-match-block",d="search-match-block-selected",l="search-match-dark",c="search-match-expand-title",p=".loader-wrapper>a",u=".lozenge-wrapper",m=".editor-mention-primitive",h=".date-lozenger-container>span",g=(0,n("3jLHL").css)({[`.${a}`]:{borderRadius:"3px",backgroundColor:"var(--ds-background-accent-teal-subtlest, #E7F9FF)",boxShadow:`var(--ds-shadow-raised, 0 1px 1px 0 ${n("6fnsQ").N50A}, 0 0 1px 0 ${n("6fnsQ").N60A}), inset 0 0 0 1px var(--ds-border-input, ${n("6fnsQ").N40A})`},[`.${i}`]:{backgroundColor:"var(--ds-background-accent-teal-subtle, #6CC3E0)"}}),b=(0,n("3jLHL").css)({[`.${o}`]:{borderRadius:"var(--ds-space-050, 4px)",boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-yellow-subtler-pressed, #E2B203),
		inset 0 0 0 5px var(--ds-background-accent-yellow-subtler, #F8E6A0)
		`,backgroundColor:"var(--ds-background-accent-yellow-subtler, #F8E6A0) !important",color:"var(--ds-text, #172B4D)"},[`.${o}.${i}`]:{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-yellow-subtler-pressed, #E2B203),
		inset 0 0 0 5px var(--ds-background-accent-yellow-subtlest-pressed, #F5CD47)
		`,backgroundColor:"var(--ds-background-accent-yellow-subtlest-pressed, #F5CD47) !important"},[`.${o}.${l}`]:{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-yellow-bolder, #946F00),
		inset 0 0 0 5px var(--ds-background-accent-yellow-bolder-pressed, #533F04)
		`,backgroundColor:"var(--ds-background-accent-yellow-bolder-pressed, #533F04) !important",color:"var(--ds-text-inverse, #FFFFFF)"},[`.${o}.${i}.${l}`]:{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-yellow-bolder, #946F00),
		inset 0 0 0 5px var(--ds-background-accent-yellow-bolder-hovered, #7F5F01)
		`,backgroundColor:"var(--ds-background-accent-yellow-bolder-hovered, #7F5F01) !important"},[`.${s}`]:{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-yellow-subtler-pressed, #E2B203),
			inset 0 0 0 5px var(--ds-background-accent-yellow-subtler, #F8E6A0)
			`},[`${p}, ${u}, ${m}, ${h}`]:{boxShadow:"0px 0px 0px 4px var(--ds-background-accent-yellow-subtler, #F8E6A0), 0px 0px 0px 5px var(--ds-background-accent-yellow-subtler-pressed, #E2B203)"}},[`.${s}.${d}`]:{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-yellow-subtler-pressed, #E2B203),
			inset 0 0 0 4px var(--ds-background-accent-yellow-subtlest-pressed, #F5CD47)
			`},[`${p}, ${u}, ${m}, ${h}`]:{boxShadow:"0px 0px 0px 4px var(--ds-background-accent-yellow-subtlest-pressed, #F5CD47), 0px 0px 0px 5px var(--ds-background-accent-yellow-subtler-pressed, #E2B203)"}},[`.${s}.ak-editor-selected-node`]:{".loader-wrapper>div::after":{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-yellow-subtler-pressed, #E2B203),
			inset 0 0 0 5px var(--ds-background-accent-yellow-subtler, #F8E6A0),
			0 0 0 1px var(--ds-border-selected, #0C66E4)
			`},[`${p}, ${u}, ${m}, ${h}`]:{boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4), 0px 0px 0px 4px var(--ds-background-accent-yellow-subtler, #F8E6A0), 0px 0px 0px 5px var(--ds-background-accent-yellow-subtler-pressed, #E2B203) !important"}},[`.${s}.${d}.ak-editor-selected-node`]:{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-yellow-subtler-pressed, #E2B203),
			inset 0 0 0 4px var(--ds-background-accent-yellow-subtlest-pressed, #F5CD47),
			0 0 0 1px var(--ds-border-selected, #0C66E4)
			`},[`${p}, ${u}, ${m}, ${h}`]:{boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4), 0px 0px 0px 4px var(--ds-background-accent-yellow-subtlest-pressed, #F5CD47), 0px 0px 0px 5px var(--ds-background-accent-yellow-subtler-pressed, #E2B203) !important"}},[`.${s}.${l}`]:{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-yellow-bolder, #946F00),
			inset 0 0 0 5px var(--ds-background-accent-yellow-bolder-pressed, #533F04)
			`},[`${p}, ${u}, ${m}, ${h}`]:{boxShadow:"0px 0px 0px 4px var(--ds-background-accent-yellow-bolder-pressed, #533F04), 0px 0px 0px 5px var(--ds-background-accent-yellow-bolder, #946F00)"}},[`.${s}.${d}.${l}`]:{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-yellow-bolder, #946F00),
			inset 0 0 0 4px var(--ds-background-accent-yellow-bolder-hovered, #7F5F01)
			`},[`${p}, ${u}, ${m}, ${h}`]:{boxShadow:"0px 0px 0px 4px var(--ds-background-accent-yellow-bolder-hovered, #7F5F01), 0px 0px 0px 5px var(--ds-background-accent-yellow-bolder, #946F00)"}},[`.${s}.${l}.ak-editor-selected-node`]:{".loader-wrapper>div::after":{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-yellow-bolder, #946F00),
			inset 0 0 0 5px var(--ds-background-accent-yellow-bolder-pressed, #533F04),
			0 0 0 1px var(--ds-border-selected, #0C66E4)
			`},[`${p}, ${u}, ${m}, ${h}`]:{boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4), 0px 0px 0px 4px var(--ds-background-accent-yellow-bolder-pressed, #533F04), 0px 0px 0px 5px var(--ds-background-accent-yellow-bolder, #946F00) !important"}},[`.${s}.${d}.${l}.ak-editor-selected-node`]:{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-yellow-bolder, #946F00),
			inset 0 0 0 4px var(--ds-background-accent-yellow-bolder-hovered, #7F5F01),
			0 0 0 1px var(--ds-border-selected, #0C66E4)
			`},[`${p}, ${u}, ${m}, ${h}`]:{boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4), 0px 0px 0px 4px var(--ds-background-accent-yellow-bolder-hovered, #7F5F01), 0px 0px 0px 5px var(--ds-background-accent-yellow-bolder, #946F00) !important"}},[`.${c} > .${n("iMS6j").expandClassNames.titleContainer} > .${n("iMS6j").expandClassNames.inputContainer}`]:{borderRadius:"var(--ds-space-050, 4px)",boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-yellow-subtler-pressed, #E2B203),
		inset 0 0 0 5px var(--ds-background-accent-yellow-subtler, #F8E6A0)
		`,backgroundColor:"var(--ds-background-accent-yellow-subtler, #F8E6A0)",[`.${n("iMS6j").expandClassNames.titleInput}`]:{color:"var(--ds-text, #172B4D)"}},[`.${c}.${i} > .${n("iMS6j").expandClassNames.titleContainer} > .${n("iMS6j").expandClassNames.inputContainer}`]:{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-yellow-subtler-pressed, #E2B203),
		inset 0 0 0 5px var(--ds-background-accent-yellow-subtlest-pressed, #F5CD47)
		`,backgroundColor:"var(--ds-background-accent-yellow-subtlest-pressed, #F5CD47)"},[`.${c}.${l} > .${n("iMS6j").expandClassNames.titleContainer} > .${n("iMS6j").expandClassNames.inputContainer}`]:{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-yellow-bolder, #946F00),
		inset 0 0 0 5px var(--ds-background-accent-yellow-bolder-pressed, #533F04)
		`,backgroundColor:"var(--ds-background-accent-yellow-bolder-pressed, #533F04)",[`.${n("iMS6j").expandClassNames.titleInput}`]:{color:"var(--ds-text-inverse, #FFFFFF)"}},[`.${c}.${i}.${l} > .${n("iMS6j").expandClassNames.titleContainer} > .${n("iMS6j").expandClassNames.inputContainer}`]:{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-yellow-bolder, #946F00),
		inset 0 0 0 5px var(--ds-background-accent-yellow-bolder-hovered, #7F5F01)
		`,backgroundColor:"var(--ds-background-accent-yellow-bolder-hovered, #7F5F01)"}}),f=(0,n("3jLHL").css)({[`.${o}`]:{borderRadius:"var(--ds-space-050, 4px)",boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-magenta-subtler-pressed, #E774BB),
		inset 0 0 0 5px var(--ds-background-accent-magenta-subtler, #FDD0EC)
		`,backgroundColor:"var(--ds-background-accent-magenta-subtler, #FDD0EC) !important",color:"var(--ds-text, #172B4D)"},[`.${o}.${i}`]:{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-magenta-subtler-pressed, #E774BB),
		inset 0 0 0 5px var(--ds-background-accent-magenta-subtlest-pressed, #F797D2)
		`,backgroundColor:"var(--ds-background-accent-magenta-subtlest-pressed, #F797D2) !important"},[`.${o}.${l}`]:{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-magenta-bolder, #AE4787),
		inset 0 0 0 5px var(--ds-background-accent-magenta-bolder-pressed, #50253F)
		`,backgroundColor:"var(--ds-background-accent-magenta-bolder-pressed, #50253F) !important",color:"var(--ds-text-inverse, #FFFFFF)"},[`.${o}.${i}.${l}`]:{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-magenta-bolder, #AE4787),
		inset 0 0 0 5px var(--ds-background-accent-magenta-bolder-hovered, #943D73)
		`,backgroundColor:"var(--ds-background-accent-magenta-bolder-hovered, #943D73) !important"},[`.${s}`]:{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-magenta-subtler-pressed, #E774BB),
			inset 0 0 0 5px var(--ds-background-accent-magenta-subtler, #FDD0EC)
			`},[`${p}, ${u}, ${m}, ${h}`]:{boxShadow:"0px 0px 0px 4px var(--ds-background-accent-magenta-subtler, #FDD0EC), 0px 0px 0px 5px var(--ds-background-accent-magenta-subtler-pressed, #E774BB)"}},[`.${s}.${d}`]:{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-magenta-subtler-pressed, #E774BB),
			inset 0 0 0 4px var(--ds-background-accent-magenta-subtlest-pressed, #F797D2)
			`},[`${p}, ${u}, ${m}, ${h}`]:{boxShadow:"0px 0px 0px 4px var(--ds-background-accent-magenta-subtlest-pressed, #F797D2), 0px 0px 0px 5px var(--ds-background-accent-magenta-subtler-pressed, #E774BB)"}},[`.${s}.ak-editor-selected-node`]:{".loader-wrapper>div::after":{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-magenta-subtler-pressed, #E774BB),
			inset 0 0 0 5px var(--ds-background-accent-magenta-subtler, #FDD0EC),
			0 0 0 1px var(--ds-border-selected, #0C66E4)
			`},[`${p}, ${u}, ${m}, ${h}`]:{boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4), 0px 0px 0px 4px var(--ds-background-accent-magenta-subtler, #FDD0EC), 0px 0px 0px 5px var(--ds-background-accent-magenta-subtler-pressed, #E774BB) !important"}},[`.${s}.${d}.ak-editor-selected-node`]:{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-magenta-subtler-pressed, #E774BB),
			inset 0 0 0 4px var(--ds-background-accent-magenta-subtlest-pressed, #F797D2),
			0 0 0 1px var(--ds-border-selected, #0C66E4)
			`},[`${p}, ${u}, ${m}, ${h}`]:{boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4), 0px 0px 0px 4px var(--ds-background-accent-magenta-subtlest-pressed, #F797D2), 0px 0px 0px 5px var(--ds-background-accent-magenta-subtler-pressed, #E774BB) !important"}},[`.${s}.${l}`]:{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-magenta-bolder, #AE4787),
			inset 0 0 0 5px var(--ds-background-accent-magenta-bolder-pressed, #50253F)
			`},[`${p}, ${u}, ${m}, ${h}`]:{boxShadow:"0px 0px 0px 4px var(--ds-background-accent-magenta-bolder-pressed, #50253F), 0px 0px 0px 5px var(--ds-background-accent-magenta-bolder, #AE4787)"}},[`.${s}.${d}.${l}`]:{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-magenta-bolder, #AE4787),
			inset 0 0 0 4px var(--ds-background-accent-magenta-bolder-hovered, #943D73)
			`},[`${p}, ${u}, ${m}, ${h}`]:{boxShadow:"0px 0px 0px 4px var(--ds-background-accent-magenta-bolder-hovered, #943D73), 0px 0px 0px 5px var(--ds-background-accent-magenta-bolder, #AE4787)"}},[`.${s}.${l}.ak-editor-selected-node`]:{".loader-wrapper>div::after":{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-magenta-bolder, #AE4787),
			inset 0 0 0 5px var(--ds-background-accent-magenta-bolder-pressed, #50253F),
			0 0 0 1px var(--ds-border-selected, #0C66E4)
			`},[`${p}, ${u}, ${m}, ${h}`]:{boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4), 0px 0px 0px 4px var(--ds-background-accent-magenta-bolder-pressed, #50253F), 0px 0px 0px 5px var(--ds-background-accent-magenta-bolder, #AE4787) !important"}},[`.${s}.${d}.${l}.ak-editor-selected-node`]:{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-magenta-bolder, #AE4787),
			inset 0 0 0 4px var(--ds-background-accent-magenta-bolder-hovered, #943D73),
			0 0 0 1px var(--ds-border-selected, #0C66E4)
			`},[`${p}, ${u}, ${m}, ${h}`]:{boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4), 0px 0px 0px 4px var(--ds-background-accent-magenta-bolder-hovered, #943D73), 0px 0px 0px 5px var(--ds-background-accent-magenta-bolder, #AE4787) !important"}},[`.${c} > .${n("iMS6j").expandClassNames.titleContainer} > .${n("iMS6j").expandClassNames.inputContainer}`]:{borderRadius:"var(--ds-space-050, 4px)",boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-magenta-subtler-pressed, #E774BB),
		inset 0 0 0 5px var(--ds-background-accent-magenta-subtler, #FDD0EC)
		`,backgroundColor:"var(--ds-background-accent-magenta-subtler, #FDD0EC)",[`.${n("iMS6j").expandClassNames.titleInput}`]:{color:"var(--ds-text, #172B4D)"}},[`.${c}.${i} > .${n("iMS6j").expandClassNames.titleContainer} > .${n("iMS6j").expandClassNames.inputContainer}`]:{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-magenta-subtler-pressed, #E774BB),
		inset 0 0 0 5px var(--ds-background-accent-magenta-subtlest-pressed, #F797D2)
		`,backgroundColor:"var(--ds-background-accent-magenta-subtlest-pressed, #F797D2)"},[`.${c}.${l} > .${n("iMS6j").expandClassNames.titleContainer} > .${n("iMS6j").expandClassNames.inputContainer}`]:{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-magenta-bolder, #AE4787),
		inset 0 0 0 5px var(--ds-background-accent-magenta-bolder-pressed, #50253F)
		`,backgroundColor:"var(--ds-background-accent-magenta-bolder-pressed, #50253F)",[`.${n("iMS6j").expandClassNames.titleInput}`]:{color:"var(--ds-text-inverse, #FFFFFF)"}},[`.${c}.${i}.${l} > .${n("iMS6j").expandClassNames.titleContainer} > .${n("iMS6j").expandClassNames.inputContainer}`]:{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-magenta-bolder, #AE4787),
		inset 0 0 0 5px var(--ds-background-accent-magenta-bolder-hovered, #943D73)
		`,backgroundColor:"var(--ds-background-accent-magenta-bolder-hovered, #943D73)"}})}),i("agKS6",function(t,r){e(t.exports,"textHighlightStyle",()=>n("gg4RV").textHighlightStyle)}),i("gg4RV",function(t,r){e(t.exports,"textHighlightStyle",()=>a);let a=(0,n("3jLHL").css)`
	.${n("jHrqf").TEXT_HIGHLIGHT_CLASS} {
		background-color: ${"var(--ds-background-accent-blue-subtlest, #E9F2FF)"};

		border-bottom: 2px solid ${"var(--ds-background-accent-blue-subtler, #cce0ff)"};
	}
`}),i("jHrqf",function(t,r){e(t.exports,"PASTE_TOOLBAR_CLASS",()=>a),e(t.exports,"TEXT_HIGHLIGHT_CLASS",()=>o),e(t.exports,"PASTE_HIGHLIGHT_DECORATION_KEY",()=>n),e(t.exports,"PASTE_TOOLBAR_ITEM_CLASS",()=>i),e(t.exports,"PASTE_OPTIONS_TEST_ID",()=>s),e(t.exports,"PASTE_OPTIONS_META_ID",()=>d);let a="ak-editor-paste-toolbar",o="text-highlight",n="paste-highlight-decoration-key",i="ak-editor-paste-toolbar-item",s="paste-options-testid",d="paste-options$"}),i("axrL7",function(t,r){e(t.exports,"placeholderTextStyles",()=>n("319kp").placeholderTextStyles),e(t.exports,"placeholderTextStyles_fg_platform_editor_system_fake_text_highlight_colour",()=>n("319kp").placeholderTextStyles_fg_platform_editor_system_fake_text_highlight_colour)}),i("319kp",function(t,r){e(t.exports,"placeholderTextStyles",()=>a),e(t.exports,"placeholderTextStyles_fg_platform_editor_system_fake_text_highlight_colour",()=>o);let a=(0,n("3jLHL").css)`
	.ProseMirror span[data-placeholder] {
		color: ${`var(--ds-text-subtlest, ${n("6fnsQ").N200})`};
		display: inline;
	}

	.ProseMirror span.pm-placeholder {
		display: inline;
		color: ${`var(--ds-text-subtlest, ${n("6fnsQ").N200})`};
	}
	.ProseMirror span.pm-placeholder__text {
		display: inline;
		color: ${`var(--ds-text-subtlest, ${n("6fnsQ").N200})`};
	}

	.ProseMirror span.pm-placeholder.${n("aFUXX").akEditorSelectedNodeClassName} {
		${(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.Background])}
	}

	.ProseMirror span.pm-placeholder__text[data-placeholder]::after {
		color: ${`var(--ds-text-subtlest, ${n("6fnsQ").N200})`};
		cursor: text;
		content: attr(data-placeholder);
		display: inline;
	}

	.ProseMirror {
		.ProseMirror-fake-text-cursor {
			display: inline;
			pointer-events: none;
			position: relative;
		}

		.ProseMirror-fake-text-cursor::after {
			content: '';
			display: inline;
			top: 0;
			position: absolute;
			border-right: 1px solid ${"var(--ds-border, rgba(0, 0, 0, 0.4))"};
		}

		.ProseMirror-fake-text-selection {
			display: inline;
			pointer-events: none;
			position: relative;
			background-color: ${`var(--ds-background-selected, ${n("6fnsQ").B75})`};
		}
	}
`,o=(0,n("3jLHL").css)`
	.ProseMirror {
		.ProseMirror-fake-text-selection {
			/* Follow the system highlight colour to match native text selection */
			background-color: Highlight;
			/* We should also match the text colour to the system highlight text colour.
			   That way if the system highlight background is dark, the text will still be readable. */
			color: HighlightText;
		}
	}
`}),i("gYSj7",function(t,r){e(t.exports,"InlineNodeViewSharedStyles",()=>a);let a=(0,n("3jLHL").css)({[`.${n("bT1qC").inlineNodeViewClassname}`]:{display:"inline",userSelect:"all",whiteSpace:"nowrap","& > *:not(.zeroWidthSpaceContainer)":{whiteSpace:"pre-wrap"},"& > .assistive":{userSelect:"none"}},"&.ua-safari":{[`.${n("bT1qC").inlineNodeViewClassname}`]:{"::selection, *::selection":{background:"transparent"}}},[`&.ua-chrome .${n("bT1qC").inlineNodeViewClassname} > span`]:{userSelect:"none"},[`.${n("bT1qC").inlineNodeViewClassname}AddZeroWidthSpace`]:{"::after":{content:`'${n("TfRUG").ZERO_WIDTH_SPACE}'`}}})}),i("bl6tp",function(t,r){e(t.exports,"aiPanelStyles",()=>l);let a="undefined"!=typeof navigator&&navigator.userAgent.toLowerCase().indexOf("firefox")>-1,o=(0,n("3jLHL").keyframes)({"0%":{"--panel-gradient-angle":"0deg",...a?{backgroundPosition:"100%"}:{}},"100%":{"--panel-gradient-angle":"360deg",...a?{backgroundPosition:"-100%"}:{}}}),i={"prism.border.step.1":{light:"#0065FF",dark:"#0065FF80"},"prism.border.step.2":{light:"#0469FF",dark:"#0469FF80"},"prism.border.step.3":{light:"#BF63F3",dark:"#BF63F380"},"prism.border.step.4":{light:"#FFA900",dark:"#FFA90080"}},s=(0,n("3jLHL").css)({"&::before, &::after":{animationName:o,animationDuration:"2s",animationTimingFunction:"linear",animationIterationCount:"infinite",...a?{animationDirection:"normal",animationDuration:"1s"}:{},"@media (prefers-reduced-motion)":{animation:"none"}}}),d=(e,t)=>(0,n("3jLHL").css)({content:"''",position:"absolute",zIndex:-1,width:"calc(100% + 2px)",height:"calc(100% + 2px)",top:"-1px",left:"-1px",borderRadius:"calc(var(--ds-border-radius-100, 3px) + 1px)",transform:"translate3d(0, 0, 0)",...t?{background:"var(--ds-border-input, #8590A2)"}:a?{background:`linear-gradient(90deg,
								${i["prism.border.step.1"][e??"light"]} 0%,
								${i["prism.border.step.2"][e??"light"]} 12%,
								${i["prism.border.step.3"][e??"light"]} 24%,
								${i["prism.border.step.4"][e??"light"]} 48%,
								${i["prism.border.step.3"][e??"light"]} 64%,
								${i["prism.border.step.2"][e??"light"]} 80%,
								${i["prism.border.step.1"][e??"light"]} 100%
							)`,backgroundSize:"200%"}:{background:`conic-gradient(
								from var(--panel-gradient-angle, 270deg),
								${i["prism.border.step.1"][e??"light"]} 0%,
								${i["prism.border.step.2"][e??"light"]} 20%,
								${i["prism.border.step.3"][e??"light"]} 50%,
								${i["prism.border.step.4"][e??"light"]} 56%,
								${i["prism.border.step.1"][e??"light"]} 100%
							)`}}),l=e=>(0,n("3jLHL").css)`
	@property --panel-gradient-angle {
		syntax: '<angle>';
		initial-value: 270deg;
		inherits: false;
	}

	div[extensionType='com.atlassian.ai-blocks'] {
		/* This hides the label for the extension */
		.extension-label {
			display: none;
		}

		/* This styles the ai panel correctly when its just sitting on the page and there
		is no user interaction */
		.extension-container {
			position: relative;
			box-shadow: none;
			overflow: unset;
			background-color: ${"var(--ds-surface, #FFFFFF)"} !important;
			&::before,
			&::after {
				${d(e)}
			}
			&.with-hover-border {
				&::before,
				&::after {
					${d(e,!0)}
				}
			}
			& .with-margin-styles {
				background-color: ${"var(--ds-surface, #FFFFFF)"} !important;
				border-radius: ${"var(--ds-border-radius-100, 3px)"};
			}
		}
	}

	/* This styles the ai panel correctly when its streaming */
	div[extensionType='com.atlassian.ai-blocks']:has(.streaming) {
		.extension-container {
			box-shadow: none;
			overflow: unset;
			${s}
			&::before,
			&::after {
				${d(e)}
			}
		}
	}

	/* This styles the ai panel correctly when a user is hovering over the delete button in the floating panel */
	div[extensionType='com.atlassian.ai-blocks'].danger {
		.extension-container {
			box-shadow: 0 0 0 1px ${"var(--ds-border-danger, #E2483D)"};
		}
	}

	/* This removes the margin from the action list when inside an ai panel */
	div[extensiontype='com.atlassian.ai-blocks'][extensionkey='ai-action-items-block:aiActionItemsBodiedExtension'] {
		div[data-node-type='actionList'] {
			margin: 0 !important;
		}
	}
`}),i("1zjTz",function(t,r){e(t.exports,"codeBlockStyles",()=>i);let a=()=>(0,n("3jLHL").css)`
	&::after {
		height: 100%;
		content: '';
		position: absolute;
		left: 0;
		top: 0;
		width: 24px;
		background-color: ${"var(--ds-blanket-danger, none)"};
	}
`,o=(0,n("49YLc").functionWithFG)("platform_editor_nested_dnd_styles_changes",()=>(0,n("3jLHL").css)`
		.ak-editor-panel__content {
			> .code-block:first-child,
			> .ProseMirror-widget:first-child + .code-block,
			> .ProseMirror-widget:first-child + .ProseMirror-widget + .code-block {
				margin: 0 0 0 0 !important;
			}
		}
	`,()=>(0,n("3jLHL").css)`
		.ak-editor-panel__content {
			> .code-block:first-child {
				margin: 0 0 0 0 !important;
			}
		}
	`),i=()=>(0,n("3jLHL").css)`
	.ProseMirror {
		${(0,n("5MaNT").codeBlockSharedStyles)()}
	}

	.ProseMirror li {
		/* if same list item has multiple code blocks we need top margin for all but first */
		> .code-block {
			margin: ${n("aFUXX").blockNodesVerticalMargin} 0 0 0;
		}
		> .code-block:first-child,
		> .ProseMirror-gapcursor:first-child + .code-block {
			margin-top: 0;
		}

		> div:last-of-type.code-block,
		> pre:last-of-type.code-block {
			margin-bottom: ${n("aFUXX").blockNodesVerticalMargin};
		}
	}

	.ProseMirror .code-block.${n("aFUXX").akEditorSelectedNodeClassName}:not(.danger) {
		${(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.BoxShadow,n("b38UX").SelectionStyle.Blanket])}
	}

	/* Danger when top level node */
	.ProseMirror .danger.code-block {
		box-shadow: 0 0 0 ${n("aFUXX").akEditorSelectedBorderSize}px
			${`var(--ds-border-danger, ${n("aFUXX").akEditorDeleteBorder})`};

		.${n("5MaNT").CodeBlockSharedCssClassName.CODEBLOCK_LINE_NUMBER_GUTTER} {
			background-color: ${"var(--ds-background-danger, #FFECEB)"};
			color: ${`var(--ds-text-danger, ${n("aFUXX").akEditorDeleteIconColor})`};
			${a()};
		}

		.${n("5MaNT").CodeBlockSharedCssClassName.CODEBLOCK_CONTENT} {
			background-color: ${`var(--ds-blanket-danger, ${n("aFUXX").akEditorDeleteBackground})`};
		}
	}

	/* Danger when nested node */
	.ProseMirror .danger .code-block {
		.${n("5MaNT").CodeBlockSharedCssClassName.CODEBLOCK_LINE_NUMBER_GUTTER} {
			background-color: ${"var(--ds-background-danger, rgba(255, 143, 115, 0.5))"};
			color: ${`var(--ds-text-danger, ${n("aFUXX").akEditorDeleteIconColor})`};
			${a()};
		}

		.${n("5MaNT").CodeBlockSharedCssClassName.CODEBLOCK_CONTENT} {
			background-color: ${"var(--ds-blanket-danger, rgba(255, 189, 173, 0.5))"};
		}
	}

	${o()}
`}),i("49YLc",function(t,r){e(t.exports,"functionWithFG",()=>a);let a=(e,t,r)=>(0,n("1I43V").functionWithCondition)(()=>(0,n("dh538").fg)(e),t,r)}),i("1I43V",function(t,r){e(t.exports,"functionWithCondition",()=>a);function a(e,t,r){return(...a)=>e()?t(...a):r(...a)}}),i("jFND0",function(t,r){e(t.exports,"dateNodeStyles",()=>a),e(t.exports,"dateStyles",()=>o);let a=(0,n("3jLHL").css)({"[data-prosemirror-node-name='date'] .date-lozenger-container span":{backgroundColor:"var(--ds-background-neutral, #091E420F)",color:"var(--ds-text, #172B4D)",borderRadius:"var(--ds-border-radius-100, 4px)",padding:"var(--ds-space-025, 2px) var(--ds-space-050, 4px)",margin:"0 1px",position:"relative",transition:"background 0.3s",whiteSpace:"nowrap",cursor:"unset"},"[data-prosemirror-node-name='date'] .date-lozenger-container span:hover":{backgroundColor:"var(--ds-background-neutral-hovered, #091E4224)"},"[data-prosemirror-node-name='date'] .date-lozenger-container span.date-node-color-red":{backgroundColor:"var(--ds-background-accent-red-subtlest, #FFECEB)",color:"var(--ds-text-accent-red, #AE2E24)"},"[data-prosemirror-node-name='date'] .date-lozenger-container span.date-node-color-red:hover":{backgroundColor:"var(--ds-background-accent-red-subtler, #FFD5D2)"}}),o=(0,n("3jLHL").css)`
	.${n("7bDsi").DateSharedCssClassName.DATE_CONTAINER} {
		.${n("7bDsi").DateSharedCssClassName.DATE_WRAPPER} {
			line-height: initial;
			cursor: pointer;
		}

		&.${n("aFUXX").akEditorSelectedNodeClassName} {
			.${n("7bDsi").DateSharedCssClassName.DATE_WRAPPER} > span {
				${(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.BoxShadow])}
			}
		}
	}

	.danger {
		.${n("7bDsi").DateSharedCssClassName.DATE_CONTAINER}.${n("aFUXX").akEditorSelectedNodeClassName}
			.${n("7bDsi").DateSharedCssClassName.DATE_WRAPPER}
			> span {
			box-shadow: 0 0 0 ${n("aFUXX").akEditorSelectedBorderSize}px
				${`var(--ds-border-danger, ${n("aFUXX").akEditorDeleteBorder})`};
		}
	}
`}),i("gSnRq",function(t,r){e(t.exports,"expandStyles",()=>s);let a="var(--ds-background-neutral-subtle, rgba(255, 255, 255, 0.6))",o=()=>(0,n("3jLHL").css)({color:"var(--ds-icon-subtle, #626F86)"}),i=()=>(0,n("dh538").fg)("platform_editor_nested_dnd_styles_changes")?(0,n("3jLHL").css)`
				> :nth-child(1 of :not(style, .ProseMirror-gapcursor, .ProseMirror-widget, span)) {
					margin-top: 0;
				}

				> div.ak-editor-expand[data-node-type='nestedExpand'] {
					margin-top: ${"var(--ds-space-050, 0.25rem)"};
				}
			`:"",s=()=>(0,n("3jLHL").css)`
	.${n("iMS6j").expandClassNames.icon} > div {
		display: flex;
	}

	.${n("iMS6j").expandClassNames.prefix} {
		${(0,n("4zRjW").sharedExpandStyles).containerStyles({expanded:!1,focused:!1})()}

		cursor: pointer;
		box-sizing: border-box;

		td > & {
			margin-top: 0;
		}

		.${n("iMS6j").expandClassNames.iconContainer} svg {
			${o()};
			transform: rotate(90deg);
		}

		&.${n("aFUXX").akEditorSelectedNodeClassName}:not(.danger) {
			${(0,n("dh538").fg)("platform_editor_nested_dnd_styles_changes")?(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.Blanket])+`border: ${n("aFUXX").akEditorSelectedBorder};`:(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.Blanket,n("b38UX").SelectionStyle.Border])}
		}

		&.danger {
			background: ${"var(--ds-background-danger, #FFECEB)"};
			border-color: ${"var(--ds-border-danger, #E2483D)"};
		}
	}

	.ProseMirror
		> .${(0,n("iMS6j").expandClassNames).type("expand")},
		.${n("ly3wu").BreakoutCssClassName.BREAKOUT_MARK_DOM}
		> .${(0,n("iMS6j").expandClassNames).type("expand")} {
		margin-left: -${n("aFUXX").akLayoutGutterOffset}px;
		margin-right: -${n("aFUXX").akLayoutGutterOffset}px;
	}

	${(0,n("dh538").fg)("platform_editor_nested_dnd_styles_changes")&&`.ak-editor-content-area.appearance-full-page .ProseMirror
		> .${(0,n("iMS6j").expandClassNames).type("expand")},
		.${n("ly3wu").BreakoutCssClassName.BREAKOUT_MARK_DOM}
		> .${(0,n("iMS6j").expandClassNames).type("expand")} {
		margin-left: -${n("aFUXX").akLayoutGutterOffset+8}px;
		margin-right: -${n("aFUXX").akLayoutGutterOffset+8}px;
	}`}

	.${n("iMS6j").expandClassNames.content} {
		${(0,n("4zRjW").sharedExpandStyles).contentStyles({expanded:!1,focused:!1})()}
		cursor: text;
		padding-top: 0px;
	}

	.${n("iMS6j").expandClassNames.titleInput} {
		${(0,n("4zRjW").sharedExpandStyles).titleInputStyles()}
	}

	.${n("iMS6j").expandClassNames.titleContainer} {
		${(0,n("4zRjW").sharedExpandStyles).titleContainerStyles()};
		align-items: center;
		overflow: visible;
	}

	.${n("iMS6j").expandClassNames.expanded} {
		background: ${a};
		border-color: ${"var(--ds-border, #091E4224)"};

		.${n("iMS6j").expandClassNames.content} {
			padding-top: ${"var(--ds-space-100, 8px)"};

			${i()}
		}
	}

	.${n("iMS6j").expandClassNames.inputContainer} {
		width: 100%;
	}

	/* stylelint-disable property-no-unknown, value-keyword-case */
	.${n("iMS6j").expandClassNames.prefix}:(.${n("iMS6j").expandClassNames.expanded}) {
		.expand-content-wrapper {
			height: auto;
		}
	}
	/* stylelint-enable property-no-unknown, value-keyword-case */

	.${n("iMS6j").expandClassNames.prefix}:not(.${n("iMS6j").expandClassNames.expanded}) {
		.ak-editor-expand__content {
			position: absolute;
			height: 1px;
			width: 1px;
			overflow: hidden;
			clip: rect(1px, 1px, 1px, 1px);
			white-space: nowrap;
		}

		.${n("iMS6j").expandClassNames.iconContainer} svg {
			${o()};
			transform: rotate(0deg);
		}

		&:not(.${n("aFUXX").akEditorSelectedNodeClassName}):not(.danger) {
			background: transparent;
			border-color: transparent;

			&:hover {
				border-color: ${"var(--ds-border, #091E4224)"};
				background: ${a};
			}
		}
	}
`}),i("ly3wu",function(t,r){e(t.exports,"BreakoutCssClassName",()=>a);let a={BREAKOUT_MARK:"fabric-editor-breakout-mark",BREAKOUT_MARK_DOM:"fabric-editor-breakout-mark-dom"}}),i("4zRjW",function(t,r){e(t.exports,"EXPAND_CONTAINER_PADDING",()=>a),e(t.exports,"sharedExpandStyles",()=>o);let a=8,o={titleInputStyles:()=>(0,n("3jLHL").css)({outline:"none",border:"none",fontSize:(0,n("aFUXX").relativeFontSizeToBase16)(14),lineHeight:(0,n("dh538").fg)("platform-visual-refresh-icons")?1:n("aFUXX").akEditorLineHeight,fontWeight:"var(--ds-font-weight-regular, 400)",color:"var(--ds-text-subtlest, #626F86)",background:"transparent",display:"flex",flex:1,padding:"0 0 0 var(--ds-space-050, 4px)",width:"100%","&::placeholder":{opacity:1,color:"var(--ds-text-subtlest, #626F86)"}}),titleContainerStyles:()=>(0,n("3jLHL").css)({padding:0,display:"flex",alignItems:"flex-start",background:"none",border:"none",fontSize:(0,n("aFUXX").relativeFontSizeToBase16)(14),width:"100%",color:"var(--ds-text-subtle, #44546F)",overflow:"hidden",cursor:"pointer","&:focus":{outline:0}}),containerStyles:e=>{let{expanded:t,focused:r}=e,o="expand"===e["data-node-type"]?`-${n("aFUXX").akLayoutGutterOffset}px`:0,i=`var(--ds-space-050, 0.25rem) ${o} 0`;return()=>(0,n("3jLHL").css)({borderWidth:"1px",borderStyle:"solid",borderColor:r?"var(--ds-border-focused, #388BFF)":t?"var(--ds-border, #091E4224)":"transparent",borderRadius:"var(--ds-border-radius-100, 4px)",minHeight:"25px",background:t?"var(--ds-surface, rgba(255, 255, 255, 0.6))":"var(--ds-background-neutral-subtle, transparent)",margin:i,transition:`background 0.3s ${n("aFUXX").akEditorSwoopCubicBezier}, border-color 0.3s ${n("aFUXX").akEditorSwoopCubicBezier}`,padding:`var(--ds-space-100, ${a}px)`,"td > :not(style):first-child, td > style:first-child + *":{marginTop:0}})},contentStyles:e=>()=>(0,n("3jLHL").css)`
		padding-top: ${e.expanded?"var(--ds-space-100, 8px)":"var(--ds-space-0, 0px)"};
		padding-right: ${"var(--ds-space-100, 8px)"};
		padding-left: ${"var(--ds-space-300, 24px)"};
		margin-left: ${"var(--ds-space-050, 4px)"};
		display: flow-root;

		/* The follow rules inside @supports block are added as a part of ED-8893
		The fix is targeting mobile bridge on iOS 12 or below,
		We should consider remove this fix when we no longer support iOS 12 */
		@supports not (display: flow-root) {
			width: 100%;
			box-sizing: border-box;
		}

		${e.expanded?"":`
        .expand-content-wrapper, .nestedExpand-content-wrapper {
          /* We visually hide the content here to preserve the content during copy+paste */
          /* Do not add text nowrap here because inline comment navigation depends on the location of the text */
          width: 100%;
          display: block;
          height: 0;
          overflow: hidden;
          clip: rect(1px, 1px, 1px, 1px);
          user-select: none;
        }
      `}
	`}}),i("6dFlY",function(t,r){e(t.exports,"extensionStyles",()=>i);let a=(0,n("3jLHL").css)`
	&.danger > span > div > .extension-label {
		background-color: ${"var(--ds-background-accent-red-subtler, #FFD5D2)"};
		color: ${"var(--ds-text-danger, #AE2E24)"};
		opacity: 1;
		box-shadow: none;
	}

	&:not(.danger).${n("aFUXX").akEditorSelectedNodeClassName} > span > div > .extension-label {
		background-color: ${"var(--ds-background-selected, #E9F2FF)"};
		color: ${"var(--ds-text-selected, #0C66E4)"};
		opacity: 1;
		box-shadow: none;
	}

	/* Targets the icon for bodied macro styling in button label */
	&.danger > span > div > .extension-label > span {
		display: inline;
	}

	&:not(.danger).${n("aFUXX").akEditorSelectedNodeClassName} > span > div .extension-label > span {
		display: inline;
	}

	/* Start of bodied extension edit toggle styles */
	&.danger.${n("aFUXX").akEditorSelectedNodeClassName} > span > .extension-edit-toggle-container {
		opacity: 1;
	}

	&:not(.danger).${n("aFUXX").akEditorSelectedNodeClassName} > span > .extension-edit-toggle-container {
		opacity: 1;
	}

	/* In view mode of the bodied macro, we never want to show the extension label */
	&.danger.${n("aFUXX").akEditorSelectedNodeClassName} > span > div > .extension-label.always-hide-label {
		opacity: 0;
	}

	&:not(.danger).${n("aFUXX").akEditorSelectedNodeClassName}
		> span
		> div
		> .extension-label.always-hide-label {
		opacity: 0;
	}

	/* .with-bodied-macro-live-page-styles class will only be added to bodied macros with the renderer mode gate enabled */
	&:not(.danger).${n("aFUXX").akEditorSelectedNodeClassName}
		> span
		> div
		> .extension-label.with-bodied-macro-live-page-styles {
		box-shadow: 0 0 0 ${n("aFUXX").akEditorSelectedBorderSize}px ${"var(--ds-border-selected, #0C66E4)"};
	}

	&.danger.${n("aFUXX").akEditorSelectedNodeClassName}
		> span
		> div
		> .extension-label.with-bodied-macro-live-page-styles {
		box-shadow: 0 0 0 ${n("aFUXX").akEditorSelectedBorderSize}px ${"var(--ds-border-danger, #E2483D)"};
	}

	&.danger.${n("aFUXX").akEditorSelectedNodeClassName}
		> span
		> .extension-edit-toggle-container
		> .extension-edit-toggle {
		background-color: ${"var(--ds-background-accent-red-subtler, #FFD5D2)"};
		color: ${"var(--ds-text-danger, #AE2E24)"};
		box-shadow: none;
	}
`,o=(0,n("3jLHL").css)({opacity:.3,backgroundColor:`var(--ds-background-danger-hovered, ${n("aFUXX").akEditorDeleteBackground})`}),i=(0,n("3jLHL").css)`
	.multiBodiedExtensionView-content-wrap {
		&.danger > span > .multiBodiedExtension--container {
			box-shadow: 0 0 0 ${n("aFUXX").akEditorSelectedBorderSize}px
				${`var(--ds-border-danger, ${n("aFUXX").akEditorDeleteBorder})`};
			background-color: ${`var(--ds-background-danger, ${n("aFUXX").akEditorDeleteBackground})`};
		}

		${a}

		&.danger > span > .with-danger-overlay {
			background-color: transparent;
			.multiBodiedExtension--overlay {
				${o}
			}
		}

		&:not(.danger).${n("aFUXX").akEditorSelectedNodeClassName} {
			& > span > .multiBodiedExtension--container {
				${(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.BoxShadow,n("b38UX").SelectionStyle.Blanket])}
			}
		}
		.multiBodiedExtension--container {
			width: 100%;
			max-width: 100%; /* ensure width can't go over 100% */
		}
	}

	.inlineExtensionView-content-wrap {
		&.danger > span > .extension-container {
			box-shadow: 0 0 0 ${n("aFUXX").akEditorSelectedBorderSize}px
				${`var(--ds-border-danger, ${n("aFUXX").akEditorDeleteBorder})`};
			background-color: ${`var(--ds-background-danger, ${n("aFUXX").akEditorDeleteBackground})`};
		}

		&.danger > span > .with-danger-overlay {
			/* If the macro turned used to turn red before, not setting the background to be transparent will cause the
			danger state to have two layers of red which we don't want. */
			background-color: transparent;
			.extension-overlay {
				${o}
			}
		}

		&:not(.danger).${n("aFUXX").akEditorSelectedNodeClassName} {
			& > span > .extension-container {
				${(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.BoxShadow])}
			}
		}

		${a}
	}

	/* This is referenced in the toDOM of a bodied extension and is used to put
	label content into the bodied extension.
	We do this so that we don't serialise the label (which causes the label to be
	be copied to the clipboard causing copy-paste issues). */
	.bodied-extension-to-dom-label::after {
		content: attr(data-bodied-extension-label);
	}

	.extensionView-content-wrap,
	.multiBodiedExtensionView-content-wrap,
	.bodiedExtensionView-content-wrap {
		margin: ${n("aFUXX").blockNodesVerticalMargin} 0;

		&:first-of-type {
			margin-top: 0;
		}

		&:last-of-type {
			margin-bottom: 0;
		}

		&:not(.danger).${n("aFUXX").akEditorSelectedNodeClassName} {
			& > span > .extension-container {
				${(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.BoxShadow])}
			}
		}

		&.danger > span > .extension-container {
			box-shadow: 0 0 0 ${n("aFUXX").akEditorSelectedBorderSize}px
				${`var(--ds-border-danger, ${n("aFUXX").akEditorDeleteBorder})`};
			background-color: ${`var(--ds-background-danger, ${n("aFUXX").akEditorDeleteBackground})`};
		}

		${a}

		&.danger > span > .with-danger-overlay {
			background-color: transparent;
			.extension-overlay {
				${o}
			}
		}

		&.inline {
			word-wrap: break-all;
		}
	}

	.extensionView-content-wrap .extension-container {
		overflow: hidden;

		/* Don't hide overflow for editors inside extensions */
		&:has(.extension-editable-area) {
			overflow: visible;
		}
	}

	.bodiedExtensionView-content-wrap .extensionView-content-wrap .extension-container {
		width: 100%;
		max-width: 100%; /* ensure width can't go over 100% */
	}

	[data-mark-type='fragment'] {
		& > .extensionView-content-wrap,
		& > .bodiedExtensionView-content-wrap {
			margin: ${n("aFUXX").blockNodesVerticalMargin} 0;
		}

		& > [data-mark-type='dataConsumer'] {
			& > .extensionView-content-wrap,
			& > .bodiedExtensionView-content-wrap {
				margin: ${n("aFUXX").blockNodesVerticalMargin} 0;
			}
		}

		&:first-child {
			& > .extensionView-content-wrap,
			& > .bodiedExtensionView-content-wrap {
				margin-top: 0;
			}

			& > [data-mark-type='dataConsumer'] {
				& > .extensionView-content-wrap,
				& > .bodiedExtensionView-content-wrap {
					margin-top: 0;
				}
			}
		}

		&:nth-last-of-type(-n + 2):not(:first-of-type) {
			& > .extensionView-content-wrap,
			& > .bodiedExtensionView-content-wrap {
				margin-bottom: 0;
			}

			& > [data-mark-type='dataConsumer'] {
				& > .extensionView-content-wrap,
				& > .bodiedExtensionView-content-wrap {
					margin-bottom: 0;
				}
			}
		}
	}
`}),i("3oH64",function(t,r){e(t.exports,"layoutStyles",()=>h),n("jK0dl"),n("eJQfi");var a=n("iu6m9");let o=()=>(0,n("dh538").fg)("platform_editor_nested_dnd_styles_changes")?(0,n("3jLHL").css)`
				> :nth-child(1 of :not(style, .ProseMirror-gapcursor, .ProseMirror-widget, span)) {
					margin-top: 0;
				}
			`:(0,n("3jLHL").css)`
				> :not(style):first-child,
				> style:first-child + * {
					margin-top: 0;
				}

				> .ProseMirror-gapcursor:first-child + *,
				> style:first-child + .ProseMirror-gapcursor + * {
					margin-top: 0;
				}

				> .ProseMirror-gapcursor:first-child + span + * {
					margin-top: 0;
				}
			`,i=()=>(0,a.editorExperiment)("advanced_layouts",!0)?(0,n("3jLHL").css)`
				> [data-layout-column] {
					margin: 0 ${n("boKri").LAYOUT_SECTION_MARGIN/2}px;
				}

				> [data-layout-column]:first-of-type {
					margin-left: 0;
				}

				> [data-layout-column]:last-of-type {
					margin-right: 0;
				}

				@media screen and (max-width: ${n("aFUXX").gridMediumMaxWidth}px) {
					[data-layout-column] + [data-layout-column] {
						margin: 0;
					}
				}

				> [data-layout-column].${n("aFUXX").akEditorSelectedNodeClassName}:not(.danger) {
					${(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.Blanket])};
					/* layout column selection shorter after layout border has been removed */
					::before {
						width: calc(100% - 8px);
						left: 4px;
						border-radius: ${"var(--ds-border-radius, 3px)"};
					}
				}
			`:(0,n("3jLHL").css)`
				[data-layout-column] + [data-layout-column] {
					margin-left: ${n("boKri").LAYOUT_SECTION_MARGIN}px;
				}

				@media screen and (max-width: ${n("aFUXX").gridMediumMaxWidth}px) {
					[data-layout-column] + [data-layout-column] {
						margin-left: 0;
					}
				}
			`,s=()=>(0,a.editorExperiment)("advanced_layouts",!0)?(0,n("3jLHL").css)`
				${n("lfBm5").columnLayoutResponsiveSharedStyle};
				.layout-section-container [data-layout-section] {
					> .ProseMirror-widget {
						flex: none;
						display: contents !important;

						&[data-blocks-drag-handle-container] div {
							display: contents !important;
						}

						&[data-blocks-drop-target-container] {
							display: block !important;
							margin: ${"var(--ds-space-negative-050, -4px)"};

							[data-drop-target-for-element] {
								position: absolute;
							}
						}

						& + [data-layout-column] {
							margin: 0;
						}
					}

					> [data-layout-column] {
						margin: 0;
					}
				}
			`:(0,n("3jLHL").css)`
				${n("lfBm5").columnLayoutSharedStyle}
			`,d=e=>(0,n("3jLHL").css)`
	/* TODO: Remove the border styles below once design tokens have been enabled and fallbacks are no longer triggered.
	This is because the default state already uses the same token and, as such, the hover style won't change anything.
	https://product-fabric.atlassian.net/browse/DSP-4441 */
	/* Shows the border when cursor is inside a layout */
	&.selected [data-layout-column],
	&:hover [data-layout-column] {
		border: ${"view"===e?0:n("aFUXX").akEditorSelectedBorderSize}px solid ${"var(--ds-border, #091E4224)"};
	}

	&.selected.danger [data-layout-column] {
		background-color: ${`var(--ds-background-danger, ${n("aFUXX").akEditorDeleteBackground})`};
		border-color: ${`var(--ds-border-danger, ${n("aFUXX").akEditorDeleteBorder})`};
	}

	&.${n("aFUXX").akEditorSelectedNodeClassName}:not(.danger) {
		[data-layout-column] {
			${(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.Border,n("b38UX").SelectionStyle.Blanket])}
			::after {
				background-color: transparent;
			}
		}
	}
`,l=e=>(0,n("3jLHL").css)`
	[data-layout-content]::before {
		content: '';
		border-left: ${"view"===e?0:n("aFUXX").akEditorSelectedBorderSize}px solid
			${"var(--ds-border, #091E4224)"};
		position: absolute;
		height: calc(100% - 24px);
		margin-left: -25px;
	}
`,c=e=>(0,n("3jLHL").css)`
	[data-layout-content]::before {
		content: '';
		border-top: ${"view"===e?0:n("aFUXX").akEditorSelectedBorderSize}px solid
			${"var(--ds-border, #091E4224)"};
		position: absolute;
		width: calc(100% - 32px);
		margin-top: -13px;

		/* clear styles for column separator */
		border-left: unset;
		margin-left: unset;
		height: unset;
	}
`,p=(e,t)=>(0,n("3jLHL").css)`
	&.selected,
	&:hover,
	&.selected.danger,
	&.${n("aFUXX").akEditorSelectedNodeClassName}:not(.danger) {
		[data-layout-column]:not(:first-of-type) {
			@container editor-area (max-width:${e}px) {
				${c(t)}
			}
		}
	}
`,u=e=>(0,n("3jLHL").css)`
		&.selected [data-layout-column]:not(:first-of-type),
		[data-empty-layout='true'] [data-layout-column]:not(:first-of-type),
		&:hover [data-layout-column]:not(:first-of-type) {
			${l(e)}
		}

		&.selected.danger [data-layout-section] {
			background-color: ${`var(--ds-background-danger, ${n("aFUXX").akEditorDeleteBackground})`};

			box-shadow: 0 0 0 ${"view"===e?0:n("aFUXX").akEditorSelectedBorderSize}px
				${n("aFUXX").akEditorDeleteBorder};
			border-radius: 4px;
			[data-layout-column]:not(:first-of-type) {
				${l(e)}
			}
		}

		&.${n("aFUXX").akEditorSelectedNodeClassName}:not(.danger) [data-layout-section] {
			box-shadow: 0 0 0 ${"view"===e?0:n("aFUXX").akEditorSelectedBorderSize}px
				${"var(--ds-border-selected, #0C66E4)"};
			border-radius: 4px;
			background-color: ${"var(--ds-background-selected, #E9F2FF)"};
			[data-layout-column] {
				${(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.Blanket])}
				border: 0px;
				::before {
					background-color: transparent;
				}
			}
			[data-layout-column]:not(:first-of-type) {
				${l(e)}
			}
		}
	`,m=e=>(0,n("3jLHL").css)`
		/* chosen breakpoints in container queries are to make sure layout responsiveness in editor aligns with renderer */
		/* not resized layout in full-width editor */
		.fabric-editor--full-width-mode .ProseMirror {
			> .layoutSectionView-content-wrap {
				[data-layout-section] {
					@container editor-area (max-width:724px) {
						flex-direction: column;
					}
				}

				${p(724,e)}
			}
		}

		/* not resized layout in fixed-width editor */
		.ak-editor-content-area:not(.fabric-editor--full-width-mode) .ProseMirror {
			> .layoutSectionView-content-wrap {
				[data-layout-section] {
					@container editor-area (max-width:788px) {
						flex-direction: column;
					}
				}

				${p(788,e)}
			}
		}

		/* resized layout in full/fixed-width editor */
		.ProseMirror .fabric-editor-breakout-mark {
			.layoutSectionView-content-wrap {
				[data-layout-section] {
					@container editor-area (max-width:820px) {
						flex-direction: column;
					}
				}

				${p(820,e)}
			}
		}
	`,h=e=>(0,n("3jLHL").css)`
	.ProseMirror {
		${s()}
		[data-layout-section] {
			/* Ignored via go/ees007
			TODO: Migrate away from gridSize
			Recommendation: Replace directly with 7px */
			margin: ${"var(--ds-space-100, 8px)"} -${n("aFUXX").akLayoutGutterOffset+((0,n("dh538").fg)("platform_editor_nested_dnd_styles_changes")?8:0)}px 0;
			transition: border-color 0.3s ${n("aFUXX").akEditorSwoopCubicBezier};
			cursor: ${"view"===e?"default":"pointer"};

			/* Inner cursor located 26px from left */
			[data-layout-column] {
				flex: 1;
				position: relative;

				min-width: 0;
				/* disable 4 borders when in view mode and advanced layouts is on */
				border: ${"view"===e||(0,a.editorExperiment)("advanced_layouts",!0)?0:n("aFUXX").akEditorSelectedBorderSize}px
					solid ${"var(--ds-border, #091E4224)"};
				border-radius: 4px;
				padding: ${n("boKri").LAYOUT_COLUMN_PADDING}px
					${n("boKri").LAYOUT_COLUMN_PADDING+((0,n("dh538").fg)("platform_editor_nested_dnd_styles_changes")?8:0)}px;
				box-sizing: border-box;

				> div {
					${o()}

					> .embedCardView-content-wrap:first-of-type .rich-media-item {
						margin-top: 0;
					}

					> .mediaSingleView-content-wrap:first-of-type .rich-media-item {
						margin-top: 0;
					}

					> .ProseMirror-gapcursor.-right:first-child
						+ .mediaSingleView-content-wrap
						.rich-media-item,
					> style:first-child
						+ .ProseMirror-gapcursor.-right
						+ .mediaSingleView-content-wrap
						.rich-media-item,
					> .ProseMirror-gapcursor.-right:first-of-type
						+ .embedCardView-content-wrap
						.rich-media-item {
						margin-top: 0;
					}

					> .ProseMirror-gapcursor:first-child
						+ span
						+ .mediaSingleView-content-wrap
						.rich-media-item,
					> style:first-child
						+ .ProseMirror-gapcursor
						+ span
						+ .mediaSingleView-content-wrap
						.rich-media-item {
						margin-top: 0;
					}

					/* Prevent first DecisionWrapper's margin-top: 8px from shifting decisions down
             and shrinking layout's node selectable area (leniency margin) */
					> [data-node-type='decisionList'] {
						li:first-of-type [data-decision-wrapper] {
							margin-top: 0;
						}
					}
				}

				/* Make the 'content' fill the entire height of the layout column to allow click
           handler of layout section nodeview to target only data-layout-column */
				[data-layout-content] {
					height: 100%;
					cursor: text;
					.mediaGroupView-content-wrap {
						clear: both;
					}
				}
			}

			${i()}
		}

		/* styles to support borders for layout */
		[data-layout-section],
		.layoutSectionView-content-wrap {
			${(0,a.editorExperiment)("advanced_layouts",!0)?u(e):d(e)}
		}
	}

	${(0,a.editorExperiment)("advanced_layouts",!0)&&m(e)}

	/* hide separator when element is dragging on top of a layout column */
	[data-blocks-drop-target-container] ~ [data-layout-column] > [data-layout-content]::before {
		display: none;
	}

	.fabric-editor--full-width-mode .ProseMirror {
		[data-layout-section] {
			.${n("d5aTJ").TableCssClassName.TABLE_CONTAINER} {
				margin: 0 ${n("eoFXy").tableMarginFullWidthMode}px;
			}
		}
	}

	${(0,a.editorExperiment)("advanced_layouts",!1)&&(0,n("dh538").fg)("platform_editor_nested_dnd_styles_changes")&&`.ak-editor-content-area.appearance-full-page .ProseMirror [data-layout-section] {
				margin: var(--ds-space-100, 8px) -${n("aFUXX").akLayoutGutterOffset+8}px 0;
				}`}
`}),i("lfBm5",function(t,r){e(t.exports,"columnLayoutSharedStyle",()=>a),e(t.exports,"columnLayoutResponsiveSharedStyle",()=>o);let a=(0,n("3jLHL").css)({"[data-layout-section]":{position:"relative",display:"flex",flexDirection:"row","& > *":{flex:1,minWidth:0},"& > .unsupportedBlockView-content-wrap":{minWidth:"initial"},[`@media screen and (max-width: ${n("aFUXX").gridMediumMaxWidth}px)`]:{flexDirection:"column"}}}),o=(0,n("3jLHL").css)({"[data-layout-section]":{display:"flex",flexDirection:"row",gap:"var(--ds-space-100, 8px)","& > *":{flex:1,minWidth:0},"& > .unsupportedBlockView-content-wrap":{minWidth:"initial"}},".layout-section-container":{containerType:"inline-size",containerName:"layout-area"}});(0,n("3jLHL").css)({".layout-section-container":{"[data-layout-section]":{gap:"var(--ds-space-600, 48px)","@container layout-area (max-width:629px)":{flexDirection:"column",gap:"var(--ds-space-400, 32px)"}}}})}),i("jK0dl",function(t,r){e(t.exports,"TableCssClassName",()=>n("d5aTJ").TableCssClassName)}),i("d5aTJ",function(t,r){e(t.exports,"RESIZE_HANDLE_AREA_DECORATION_GAP",()=>a),e(t.exports,"TableDecorations",()=>s),e(t.exports,"TableCssClassName",()=>d),e(t.exports,"ShadowEvent",()=>l);let a=30;var o,i,s=((o={}).ALL_CONTROLS_HOVER="CONTROLS_HOVER",o.ROW_CONTROLS_HOVER="ROW_CONTROLS_HOVER",o.COLUMN_CONTROLS_HOVER="COLUMN_CONTROLS_HOVER",o.TABLE_CONTROLS_HOVER="TABLE_CONTROLS_HOVER",o.CELL_CONTROLS_HOVER="CELL_CONTROLS_HOVER",o.COLUMN_CONTROLS_DECORATIONS="COLUMN_CONTROLS_DECORATIONS",o.COLUMN_DROP_TARGET_DECORATIONS="COLUMN_DROP_TARGET_DECORATIONS",o.COLUMN_SELECTED="COLUMN_SELECTED",o.COLUMN_RESIZING_HANDLE="COLUMN_RESIZING_HANDLE",o.COLUMN_RESIZING_HANDLE_WIDGET="COLUMN_RESIZING_HANDLE_WIDGET",o.COLUMN_RESIZING_HANDLE_LINE="COLUMN_RESIZING_HANDLE_LINE",o.COLUMN_INSERT_LINE="COLUMN_INSERT_LINE",o.ROW_INSERT_LINE="ROW_INSERT_LINE",o.LAST_CELL_ELEMENT="LAST_CELL_ELEMENT",o);let d={...n("1zav4").TableSharedCssClassName,COLUMN_CONTROLS:`${n("65GP4").tablePrefixSelector}-column-controls`,COLUMN_CONTROLS_DECORATIONS:`${n("65GP4").tablePrefixSelector}-column-controls-decoration`,COLUMN_SELECTED:`${n("65GP4").tablePrefixSelector}-column__selected`,ROW_CONTROLS_WRAPPER:`${n("65GP4").tablePrefixSelector}-row-controls-wrapper`,ROW_CONTROLS:`${n("65GP4").tablePrefixSelector}-row-controls`,ROW_CONTROLS_INNER:`${n("65GP4").tablePrefixSelector}-row-controls__inner`,ROW_CONTROLS_BUTTON_WRAP:`${n("65GP4").tablePrefixSelector}-row-controls__button-wrap`,ROW_CONTROLS_BUTTON:`${n("65GP4").tablePrefixSelector}-row-controls__button`,CONTROLS_BUTTON:`${n("65GP4").tablePrefixSelector}-controls__button`,CONTROLS_BUTTON_ICON:`${n("65GP4").tablePrefixSelector}-controls__button-icon`,CONTROLS_INSERT_BUTTON:`${n("65GP4").tablePrefixSelector}-controls__insert-button`,CONTROLS_INSERT_BUTTON_INNER:`${n("65GP4").tablePrefixSelector}-controls__insert-button-inner`,CONTROLS_INSERT_BUTTON_WRAP:`${n("65GP4").tablePrefixSelector}-controls__insert-button-wrap`,CONTROLS_INSERT_LINE:`${n("65GP4").tablePrefixSelector}-controls__insert-line`,CONTROLS_BUTTON_OVERLAY:`${n("65GP4").tablePrefixSelector}-controls__button-overlay`,DRAG_CONTROLS_INSERT_BUTTON:`${n("65GP4").tablePrefixSelector}-controls__drag-insert-button`,DRAG_CONTROLS_INSERT_BUTTON_INNER:`${n("65GP4").tablePrefixSelector}-controls__drag-insert-button-inner`,DRAG_CONTROLS_INSERT_BUTTON_INNER_COLUMN:`${n("65GP4").tablePrefixSelector}-controls__drag-insert-button-inner-column`,DRAG_CONTROLS_INSERT_BUTTON_INNER_ROW:`${n("65GP4").tablePrefixSelector}-controls__drag-insert-button-inner-row`,DRAG_CONTROLS_INSERT_BUTTON_INNER_ROW_CHROMELESS:`${n("65GP4").tablePrefixSelector}-controls__drag-insert-button-inner-row-chromeless`,DRAG_CONTROLS_INSERT_BUTTON_WRAP:`${n("65GP4").tablePrefixSelector}-controls__drag-insert-button-wrap`,CONTROLS_INSERT_MARKER:`${n("65GP4").tablePrefixSelector}-controls__insert-marker`,CONTROLS_INSERT_COLUMN:`${n("65GP4").tablePrefixSelector}-controls__insert-column`,CONTROLS_INSERT_ROW:`${n("65GP4").tablePrefixSelector}-controls__insert-row`,CONTROLS_DELETE_BUTTON_WRAP:`${n("65GP4").tablePrefixSelector}-controls__delete-button-wrap`,CONTROLS_DELETE_BUTTON:`${n("65GP4").tablePrefixSelector}-controls__delete-button`,CONTROLS_FLOATING_BUTTON_COLUMN:`${n("65GP4").tablePrefixSelector}-controls-floating__button-column`,CONTROLS_FLOATING_BUTTON_ROW:`${n("65GP4").tablePrefixSelector}-controls-floating__button-row`,CORNER_CONTROLS:`${n("65GP4").tablePrefixSelector}-corner-controls`,CORNER_CONTROLS_INSERT_ROW_MARKER:`${n("65GP4").tablePrefixSelector}-corner-controls__insert-row-marker`,CORNER_CONTROLS_INSERT_COLUMN_MARKER:`${n("65GP4").tablePrefixSelector}-corner-controls__insert-column-marker`,CONTROLS_CORNER_BUTTON:`${n("65GP4").tablePrefixSelector}-corner-button`,DRAG_ROW_CONTROLS_WRAPPER:`${n("65GP4").tablePrefixSelector}-drag-row-controls-wrapper`,DRAG_ROW_CONTROLS:`${n("65GP4").tablePrefixSelector}-drag-row-controls`,DRAG_ROW_FLOATING_INSERT_DOT_WRAPPER:`${n("65GP4").tablePrefixSelector}-drag-row-floating-insert-dot-wrapper`,DRAG_ROW_FLOATING_INSERT_DOT:`${n("65GP4").tablePrefixSelector}-drag-row-floating-insert-dot`,DRAG_COLUMN_CONTROLS:`${n("65GP4").tablePrefixSelector}-drag-column-controls`,DRAG_COLUMN_FLOATING_INSERT_DOT_WRAPPER:`${n("65GP4").tablePrefixSelector}-drag-columns-floating-insert-dot-wrapper`,DRAG_COLUMN_FLOATING_INSERT_DOT:`${n("65GP4").tablePrefixSelector}-drag-columns-floating-insert-dot`,DRAG_COLUMN_CONTROLS_WRAPPER:`${n("65GP4").tablePrefixSelector}-col-controls-wrapper`,DRAG_COLUMN_DROP_TARGET_CONTROLS:`${n("65GP4").tablePrefixSelector}-col-drop-target-controls`,DRAG_COLUMN_CONTROLS_INNER:`${n("65GP4").tablePrefixSelector}-col-controls__inner`,DRAG_HANDLE_BUTTON_CONTAINER:`${n("65GP4").tablePrefixSelector}-drag-handle-button-container`,DRAG_HANDLE_BUTTON_CLICKABLE_ZONE:`${n("65GP4").tablePrefixSelector}-drag-handle-button-clickable-zone`,DRAG_CORNER_BUTTON:`${n("65GP4").tablePrefixSelector}-drag-corner-button`,DRAG_CORNER_BUTTON_INNER:`${n("65GP4").tablePrefixSelector}-drag-corner-button-inner`,NESTED_TABLE_WITH_CONTROLS:`${n("65GP4").tablePrefixSelector}-nested-table-with-controls`,DRAG_HANDLE_DISABLED:`${n("65GP4").tablePrefixSelector}-drag-handle-disabled`,DRAG_HANDLE_MINIMISED:`${n("65GP4").tablePrefixSelector}-drag-handle-minimised`,DRAG_SUBMENU:`${n("65GP4").tablePrefixSelector}-drag-submenu`,DRAG_SUBMENU_ICON:`${n("65GP4").tablePrefixSelector}-drag-submenu-icon`,NUMBERED_COLUMN:`${n("65GP4").tablePrefixSelector}-numbered-column`,NUMBERED_COLUMN_BUTTON:`${n("65GP4").tablePrefixSelector}-numbered-column__button`,NUMBERED_COLUMN_BUTTON_DISABLED:`${n("65GP4").tablePrefixSelector}-numbered-column__button-disabled`,HOVERED_COLUMN:`${n("65GP4").tablePrefixSelector}-hovered-column`,HOVERED_ROW:`${n("65GP4").tablePrefixSelector}-hovered-row`,HOVERED_TABLE:`${n("65GP4").tablePrefixSelector}-hovered-table`,HOVERED_NO_HIGHLIGHT:`${n("65GP4").tablePrefixSelector}-hovered-no-highlight`,HOVERED_CELL:`${n("65GP4").tablePrefixSelector}-hovered-cell`,HOVERED_CELL_IN_DANGER:"danger",HOVERED_CELL_ACTIVE:"active",HOVERED_CELL_WARNING:`${n("65GP4").tablePrefixSelector}-hovered-cell__warning`,HOVERED_DELETE_BUTTON:`${n("65GP4").tablePrefixSelector}-hovered-delete-button`,WITH_CONTROLS:`${n("65GP4").tablePrefixSelector}-with-controls`,RESIZING_PLUGIN:`${n("65GP4").tablePrefixSelector}-resizing-plugin`,RESIZE_CURSOR:`${n("65GP4").tablePrefixSelector}-resize-cursor`,IS_RESIZING:`${n("65GP4").tablePrefixSelector}-is-resizing`,RESIZE_HANDLE_DECORATION:`${n("65GP4").tablePrefixSelector}-resize-decoration`,CONTEXTUAL_SUBMENU:`${n("65GP4").tablePrefixSelector}-contextual-submenu`,CONTEXTUAL_MENU_BUTTON_WRAP:`${n("65GP4").tablePrefixSelector}-contextual-menu-button-wrap`,CONTEXTUAL_MENU_BUTTON:`${n("65GP4").tablePrefixSelector}-contextual-menu-button`,CONTEXTUAL_MENU_BUTTON_FIXED:`${n("65GP4").tablePrefixSelector}-contextual-menu-button-fixed`,CONTEXTUAL_MENU_ICON:`${n("65GP4").tablePrefixSelector}-contextual-submenu-icon`,CONTEXTUAL_MENU_ICON_SMALL:`${n("65GP4").tablePrefixSelector}-contextual-submenu-icon-small`,SELECTED_CELL:"selectedCell",NODEVIEW_WRAPPER:"tableView-content-wrap",TABLE_SELECTED:`${n("65GP4").tablePrefixSelector}-table__selected`,TABLE_CELL:n("65GP4").tableCellSelector,TABLE_HEADER_CELL:n("65GP4").tableHeaderSelector,TABLE_STICKY:`${n("65GP4").tablePrefixSelector}-sticky`,TABLE_CHROMELESS:`${n("65GP4").tablePrefixSelector}-chromeless`,TOP_LEFT_CELL:"table > tbody > tr:nth-child(2) > td:nth-child(1)",LAST_ITEM_IN_CELL:`${n("65GP4").tablePrefixSelector}-last-item-in-cell`,WITH_COLUMN_INSERT_LINE:`${n("65GP4").tablePrefixSelector}-column-insert-line`,WITH_COLUMN_INSERT_LINE_INACTIVE:`${n("65GP4").tablePrefixSelector}-column-insert-line__inactive`,WITH_FIRST_COLUMN_INSERT_LINE:`${n("65GP4").tablePrefixSelector}-first-column-insert-line`,WITH_FIRST_COLUMN_INSERT_LINE_INACTIVE:`${n("65GP4").tablePrefixSelector}-first-column-insert-line__inactive`,WITH_LAST_COLUMN_INSERT_LINE:`${n("65GP4").tablePrefixSelector}-last-column-insert-line`,WITH_LAST_COLUMN_INSERT_LINE_INACTIVE:`${n("65GP4").tablePrefixSelector}-last-column-insert-line__inactive`,WITH_RESIZE_LINE:`${n("65GP4").tablePrefixSelector}-column-resize-line`,WITH_RESIZE_LINE_LAST_COLUMN:`${n("65GP4").tablePrefixSelector}-column-resize-line-last-column`,WITH_DRAG_RESIZE_LINE:`${n("65GP4").tablePrefixSelector}-drag-column-resize-line`,WITH_DRAG_RESIZE_LINE_LAST_COLUMN:`${n("65GP4").tablePrefixSelector}-drag-column-resize-line-last-column`,WITH_ROW_INSERT_LINE:`${n("65GP4").tablePrefixSelector}-row-insert-line`,WITH_ROW_INSERT_LINE_INACTIVE:`${n("65GP4").tablePrefixSelector}-row-insert-line__inactive`,WITH_LAST_ROW_INSERT_LINE:`${n("65GP4").tablePrefixSelector}-last-row-insert-line`,WITH_LAST_ROW_INSERT_LINE_INACTIVE:`${n("65GP4").tablePrefixSelector}-last-row-insert-line__inactive`};var l=((i={}).SHOW_BEFORE_SHADOW="showBeforeShadow",i.SHOW_AFTER_SHADOW="showAfterShadow",i)}),i("eJQfi",function(t,r){e(t.exports,"tableMarginFullWidthMode",()=>n("eoFXy").tableMarginFullWidthMode)}),i("eoFXy",function(t,r){e(t.exports,"tableCellBackgroundColor",()=>a),e(t.exports,"tableHeaderCellBackgroundColor",()=>o),e(t.exports,"tableTextColor",()=>i),e(t.exports,"tableBorderColor",()=>s),e(t.exports,"tableCellSelectedColor",()=>d),e(t.exports,"tableToolbarSelectedColor",()=>l),e(t.exports,"tableBorderSelectedColor",()=>c),e(t.exports,"tableCellSelectedDeleteIconColor",()=>p),e(t.exports,"tableCellSelectedDeleteIconBackground",()=>u),e(t.exports,"tableCellDeleteColor",()=>m),e(t.exports,"tableBorderDeleteColor",()=>h),e(t.exports,"tableToolbarDeleteColor",()=>g),e(t.exports,"tableCellHoverDeleteIconColor",()=>b),e(t.exports,"tableCellHoverDeleteIconBackground",()=>f),e(t.exports,"tableBorderRadiusSize",()=>x),e(t.exports,"tablePadding",()=>v),e(t.exports,"tableScrollbarOffset",()=>y),e(t.exports,"tableMarginFullWidthMode",()=>E),e(t.exports,"tableInsertColumnButtonSize",()=>S),e(t.exports,"tableDeleteButtonSize",()=>C),e(t.exports,"tableDeleteButtonOffset",()=>k),e(t.exports,"tableToolbarSize",()=>T),e(t.exports,"tableControlsSpacing",()=>w),e(t.exports,"tableInsertColumnButtonOffset",()=>_),e(t.exports,"lineMarkerSize",()=>N),e(t.exports,"columnControlsDecorationHeight",()=>L),e(t.exports,"columnControlsZIndex",()=>$),e(t.exports,"columnControlsSelectedZIndex",()=>R),e(t.exports,"rowControlsZIndex",()=>A),e(t.exports,"insertLineWidth",()=>I),e(t.exports,"resizeHandlerAreaWidth",()=>F),e(t.exports,"resizeLineWidth",()=>P),e(t.exports,"resizeHandlerZIndex",()=>O),e(t.exports,"contextualMenuTriggerSize",()=>D),e(t.exports,"contextualMenuDropdownWidth",()=>B),e(t.exports,"contextualMenuDropdownWidthDnD",()=>M),e(t.exports,"stickyRowZIndex",()=>H),e(t.exports,"stickyRowOffsetTop",()=>j),e(t.exports,"stickyHeaderBorderBottomWidth",()=>U),e(t.exports,"tableOverflowShadowWidth",()=>z),e(t.exports,"tableOverflowShadowWidthWide",()=>X),e(t.exports,"tablePopupMenuFitHeight",()=>W),e(t.exports,"dropTargetsZIndex",()=>V),e(t.exports,"TABLE_SNAP_GAP",()=>G),e(t.exports,"TABLE_HIGHLIGHT_GAP",()=>J),e(t.exports,"TABLE_HIGHLIGHT_TOLERANCE",()=>K),e(t.exports,"TABLE_GUIDELINE_VISIBLE_ADJUSTMENT",()=>q),e(t.exports,"TABLE_DRAG_MENU_SORT_GROUP_HEIGHT",()=>Z),e(t.exports,"TABLE_DRAG_MENU_PADDING_TOP",()=>Y),e(t.exports,"TABLE_DRAG_MENU_MENU_GROUP_BEFORE_HEIGHT",()=>Q),e(t.exports,"dragMenuDropdownWidth",()=>ee),e(t.exports,"dragTableInsertColumnButtonSize",()=>et),e(t.exports,"dropTargetExtendedWidth",()=>er),e(t.exports,"colorPalletteColumns",()=>ea);let a=`var(--ds-surface, ${n("6fnsQ").N0})`,o=`var(--ds-background-accent-gray-subtlest, ${n("aFUXX").akEditorTableHeaderCellBackground})`;n("aFUXX").akEditorTableToolbar;let i=`var(--ds-text-subtlest, ${n("6fnsQ").N200})`,s=`var(--ds-background-accent-gray-subtler, ${n("aFUXX").akEditorTableBorder})`;n("6fnsQ").N20;let d=`var(--ds-blanket-selected, ${n("aFUXX").akEditorTableCellBlanketSelected})`,l=`var(--ds-background-selected-pressed, ${n("6fnsQ").B200})`,c=`var(--ds-border-focused, ${n("aFUXX").akEditorTableBorderSelected})`,p=`var(--ds-icon-subtle, ${n("6fnsQ").N300})`,u=`var(--ds-background-accent-gray-subtlest, ${n("6fnsQ").N20A})`,m=`var(--ds-blanket-danger, ${n("aFUXX").akEditorTableCellBlanketDeleted})`,h=`var(--ds-border-danger, ${n("6fnsQ").R400})`,g=`var(--ds-background-danger-pressed, ${n("6fnsQ").R75})`,b="var(--ds-icon-inverse, white)",f=`var(--ds-background-danger-bold, ${n("6fnsQ").R300})`,x=3,v=8,y=15,E=2,S=20,C=16,k=6,T=n("aFUXX").akEditorTableToolbarSize,w=n("1zav4").tableMarginTop+v-n("1zav4").tableCellBorderWidth,_=3,N=4,L=25,$=10*n("aFUXX").akEditorUnitZIndex,R=$+1,A=10*n("aFUXX").akEditorUnitZIndex,I=3,F=n("d5aTJ").RESIZE_HANDLE_AREA_DECORATION_GAP/3,P=2,O=$+n("aFUXX").akRichMediaResizeZIndex,D=16,B=180,M=250,H=O+2,j=8,U=1,z=8,X=32,W=188,V=14,G=9,J=10,K=2,q=-68,Z=92,Y=4,Q=6,ee=250,et=16,er=150,ea=7}),i("6Ra3A",function(t,r){e(t.exports,"mediaStyles",()=>a);let a=()=>(0,n("3jLHL").css)`
	.ProseMirror {
		${n("gnMzP").mediaSingleSharedStyleNew} & [layout='full-width'] .${n("gnMzP").richMediaClassName},
    & [layout='wide'] .${n("gnMzP").richMediaClassName} {
			margin-left: 50%;
			transform: translateX(-50%);
		}

		.media-extended-resize-experience[layout^='wrap-'] {
			/* override 'overflow: auto' when viewport <= 410 set by mediaSingleSharedStyle
			to prevent scroll bar */
			overflow: visible !important;
		}

		& [layout^='wrap-'] + [layout^='wrap-'] {
			clear: none;
			& + p,
			& + div[class^='fabric-editor-align'],
			& + ul,
			& + ol,
			& + h1,
			& + h2,
			& + h3,
			& + h4,
			& + h5,
			& + h6 {
				clear: both !important;
			}
			& .${n("gnMzP").richMediaClassName} {
				margin-left: 0;
				margin-right: 0;
			}
		}

		${n("fhm10").mediaInlineImageStyles}

		.mediaSingleView-content-wrap[layout^='wrap-'] {
			max-width: 100%;
			/* overwrite default Prosemirror setting making it clear: both */
			clear: inherit;
		}

		.mediaSingleView-content-wrap[layout='wrap-left'] {
			float: left;
		}

		.mediaSingleView-content-wrap[layout='wrap-right'] {
			float: right;
		}

		.mediaSingleView-content-wrap[layout='wrap-right']
			+ .mediaSingleView-content-wrap[layout='wrap-left'] {
			clear: both;
		}

		/* Larger margins for resize handlers when at depth 0 of the document */
		& > .mediaSingleView-content-wrap {
			.richMedia-resize-handle-right {
				margin-right: -${n("aFUXX").akEditorMediaResizeHandlerPaddingWide}px;
			}
			.richMedia-resize-handle-left {
				margin-left: -${n("aFUXX").akEditorMediaResizeHandlerPaddingWide}px;
			}
		}
	}

	.richMedia-resize-handle-right,
	.richMedia-resize-handle-left {
		display: flex;
		flex-direction: column;

		/* vertical align */
		justify-content: center;
	}

	.richMedia-resize-handle-right {
		align-items: flex-end;
		padding-right: ${"var(--ds-space-150, 12px)"};
		margin-right: -${n("aFUXX").akEditorMediaResizeHandlerPadding}px;
	}

	.richMedia-resize-handle-left {
		align-items: flex-start;
		padding-left: ${"var(--ds-space-150, 12px)"};
		margin-left: -${n("aFUXX").akEditorMediaResizeHandlerPadding}px;
	}

	.richMedia-resize-handle-right::after,
	.richMedia-resize-handle-left::after {
		content: ' ';
		display: flex;
		width: 3px;
		height: 64px;

		border-radius: 6px;
	}

	.${n("gnMzP").richMediaClassName}:hover .richMedia-resize-handle-left::after,
	.${n("gnMzP").richMediaClassName}:hover .richMedia-resize-handle-right::after {
		background: ${"var(--ds-border, #091E4224)"};
	}

	.${n("aFUXX").akEditorSelectedNodeClassName} .richMedia-resize-handle-right::after,
	.${n("aFUXX").akEditorSelectedNodeClassName} .richMedia-resize-handle-left::after,
	.${n("gnMzP").richMediaClassName} .richMedia-resize-handle-right:hover::after,
	.${n("gnMzP").richMediaClassName} .richMedia-resize-handle-left:hover::after,
	.${n("gnMzP").richMediaClassName}.is-resizing .richMedia-resize-handle-right::after,
	.${n("gnMzP").richMediaClassName}.is-resizing .richMedia-resize-handle-left::after {
		background: ${"var(--ds-border-focused, #388BFF)"};
	}

	.__resizable_base__ {
		left: unset !important;
		width: auto !important;
		height: auto !important;
	}

	/* Danger when top level node for smart cards / inline links */
	.danger > div > div > .media-card-frame,
	.danger > span > a {
		background-color: ${`var(--ds-background-danger, ${n("aFUXX").akEditorDeleteBackground})`};
		box-shadow: 0px 0px 0px ${n("aFUXX").akEditorSelectedBorderBoldSize}px
			${`var(--ds-border-danger, ${n("aFUXX").akEditorDeleteBorder})`};
		transition:
			background-color 0s,
			box-shadow 0s;
	}
	/* Danger when nested node or common */
	.danger {
		/* Media single */
		.${n("gnMzP").richMediaClassName} .${n("jTudT").fileCardImageViewSelector}::after {
			border: 1px solid ${`var(--ds-border-danger, ${n("aFUXX").akEditorDeleteIconColor})`};
		}
		/* Media single video player */
		.${n("gnMzP").richMediaClassName} .${n("cDSVG").inlinePlayerClassName}::after {
			border: 1px solid ${`var(--ds-border-danger, ${n("aFUXX").akEditorDeleteIconColor})`};
		}
		/* New file experience */
		.${n("gnMzP").richMediaClassName} .${n("8jrlU").newFileExperienceClassName} {
			box-shadow: 0 0 0 1px ${`var(--ds-border-danger, ${n("aFUXX").akEditorDeleteIconColor})`} !important;
		}
		/* Media resize legacy handlers */
		.richMedia-resize-handle-right::after,
		.richMedia-resize-handle-left::after {
			background: ${`var(--ds-icon-danger, ${n("aFUXX").akEditorDeleteIconColor})`} !important;
		}
		/* Media resize new handlers */
		.resizer-handle-thumb {
			background: ${`var(--ds-icon-danger, ${n("aFUXX").akEditorDeleteIconColor})`} !important;
		}

		/* Smart cards */
		div div .media-card-frame,
		.inlineCardView-content-wrap > span > a {
			background-color: ${"var(--ds-blanket-danger, rgb(255, 189, 173, 0.5))"}; /* R75 with 50% opactiy */
			transition: background-color 0s;
		}

		div div .media-card-frame::after {
			box-shadow: none;
		}
	}

	.warning {
		/* Media single */
		.${n("gnMzP").richMediaClassName} .${n("jTudT").fileCardImageViewSelector}::after {
			border: 1px solid ${"var(--ds-border-warning, #E56910)"};
		}

		.${n("gnMzP").richMediaClassName} .${n("cDSVG").inlinePlayerClassName}::after {
			border: 1px solid ${"var(--ds-border-warning, #E56910)"};
		}

		.${n("gnMzP").richMediaClassName} .${n("8jrlU").newFileExperienceClassName} {
			box-shadow: 0 0 0 1px ${"var(--ds-border-warning, #E56910)"} !important;
		}

		.resizer-handle-thumb {
			background: ${"var(--ds-icon-warning, #E56910)"} !important;
		}
	}

	.media-filmstrip-list-item {
		cursor: pointer;
	}

	/* When clicking drag handle, mediaGroup node will be selected. Hence we need to apply selected style to each media node */
	.mediaGroupView-content-wrap.${n("aFUXX").akEditorSelectedNodeClassName} #newFileExperienceWrapper {
		box-shadow: ${n("aFUXX").akEditorSelectedBoxShadow};
	}
`}),i("cDSVG",function(t,r){e(t.exports,"inlinePlayerClassName",()=>o),e(t.exports,"inlinePlayerWrapperStyles",()=>i);let a=({selected:e})=>`
    ${e?n("ieXGd").hideNativeBrowserTextSelectionStyles:""}

    &::after {
      content: '';
      width: 100%;
      height: 100%;
      position: absolute;
      top: 0;
      box-sizing: border-box;
      pointer-events: none;
      ${n("dTk3A").borderRadius}
      ${e?(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.Border]):""}
    }
  `,o="media-card-inline-player",i=({dimensions:e,selected:t})=>(0,n("3jLHL").css)`
	width: ${(0,n("fDGbV").getDimensionsWithDefault)(e).width||"100%"};
	height: ${(0,n("fDGbV").getDimensionsWithDefault)(e).height||"auto"};
	overflow: hidden;
	border-radius: ${(0,n("dTk3A").borderRadius)()}px;
	position: relative;
	max-width: 100%;
	max-height: 100%;

	${a(t)}

	video {
		width: 100%;
		height: 100%;
	}
`;i.displayName="InlinePlayerWrapper"}),i("fDGbV",function(t,r){e(t.exports,"getDimensionsWithDefault",()=>a);let a=(e={width:"100%",height:"100%"})=>({height:"number"==typeof e.height?`${e.height}px`:e.height,width:"number"==typeof e.width?`${e.width}px`:e.width})}),i("8jrlU",function(t,r){e(t.exports,"newFileExperienceClassName",()=>a);let a="new-file-experience-wrapper"}),i("bD4Xf",function(t,r){e(t.exports,"panelStyles",()=>a);let a=()=>(0,n("3jLHL").css)`
	.ProseMirror {
		.${n("DoNsZ").PanelSharedCssClassName.prefix} {
			cursor: pointer;

			/* Danger when top level node */
			&.danger {
				box-shadow: 0 0 0 ${n("aFUXX").akEditorSelectedBorderSize}px ${n("aFUXX").akEditorDeleteBorder};
				background-color: ${`var(--ds-background-danger, ${n("aFUXX").akEditorDeleteBackground})`} !important;

				.${n("DoNsZ").PanelSharedCssClassName.icon} {
					color: ${`var(--ds-icon-danger, ${n("aFUXX").akEditorDeleteIconColor})`} !important;
				}
			}
		}

		.${n("DoNsZ").PanelSharedCssClassName.content} {
			cursor: text;
		}

		/* Danger when nested node */
		.danger .${n("DoNsZ").PanelSharedCssClassName.prefix} {
			&[data-panel-type] {
				background-color: ${`var(--ds-blanket-danger, ${n("aFUXX").akEditorDeleteBackgroundWithOpacity})`};

				.${n("DoNsZ").PanelSharedCssClassName.icon} {
					color: ${`var(--ds-icon-danger, ${n("aFUXX").akEditorDeleteIconColor})`};
				}
			}
		}

		${(0,n("DoNsZ").panelSharedStyles)()};
	}

	.${n("DoNsZ").PanelSharedCssClassName.prefix}.${n("aFUXX").akEditorSelectedNodeClassName}:not(.danger) {
		${(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.BoxShadow,n("b38UX").SelectionStyle.Blanket])}
	}

	${(0,n("dh538").fg)("platform_editor_nested_dnd_styles_changes")&&`.ak-editor-content-area.appearance-full-page .ProseMirror {
		.ak-editor-panel .${n("DoNsZ").PanelSharedCssClassName.icon} {
			padding-right: var(--ds-space-150, 12px);
		}

		.ak-editor-panel.${n("DoNsZ").PanelSharedCssClassName.noIcon} {
			padding-left: var(--ds-space-250, 20px);
			padding-right: var(--ds-space-250, 20px);
		}
	}`};

	/* Don't want extra padding for inline editor (nested) */
	${(0,n("dh538").fg)("platform_editor_nested_dnd_styles_changes")&&`.ak-editor-content-area .ak-editor-content-area .ProseMirror {
		.ak-editor-panel .${n("DoNsZ").PanelSharedCssClassName.icon} {
			padding-right: var(--ds-space-100, 8px);
		}
		.ak-editor-panel.${n("DoNsZ").PanelSharedCssClassName.noIcon} {
			padding-right: var(--ds-space-150, 12px);
			padding-left: var(--ds-space-150, 12px);
		}
	}`};
`}),i("ftMAt",function(t,r){e(t.exports,"statusNodeStyles",()=>i),e(t.exports,"statusStyles",()=>s);let a=()=>(0,n("dh538").fg)("platform-component-visual-refresh")?(0,n("3jLHL").css)({'[data-prosemirror-node-name="status"] .lozenge-text':{color:"#292A2E"},'[data-prosemirror-node-name="status"] > [data-color=neutral] > .lozenge-wrapper':{backgroundColor:"#DDDEE1"},'[data-prosemirror-node-name="status"] > [data-color=purple] > .lozenge-wrapper':{backgroundColor:"#D8A0F7"},'[data-prosemirror-node-name="status"] > [data-color=blue] > .lozenge-wrapper':{backgroundColor:"#8FB8F6"},'[data-prosemirror-node-name="status"] > [data-color=yellow] > .lozenge-wrapper':{backgroundColor:"#F9C84E"},'[data-prosemirror-node-name="status"] > [data-color=red] > .lozenge-wrapper':{backgroundColor:"#FD9891"},'[data-prosemirror-node-name="status"] > [data-color=green] > .lozenge-wrapper':{backgroundColor:"#B3DF72"}}):(0,n("3jLHL").css)({'[data-prosemirror-node-name="status"] > [data-color=neutral] .lozenge-wrapper':{backgroundColor:"var(--ds-background-neutral, #091E420F)"},'[data-prosemirror-node-name="status"] > [data-color=neutral] .lozenge-text':{color:"var(--ds-text-subtle, #44546F)"},'[data-prosemirror-node-name="status"] > [data-color=purple] .lozenge-wrapper':{backgroundColor:"var(--ds-background-discovery, #F3F0FF)"},'[data-prosemirror-node-name="status"] > [data-color=purple] .lozenge-text':{color:"var(--ds-text-discovery, #5E4DB2)"},'[data-prosemirror-node-name="status"] > [data-color=blue] .lozenge-wrapper':{backgroundColor:"var(--ds-background-information, #E9F2FF)"},'[data-prosemirror-node-name="status"] > [data-color=blue] .lozenge-text':{color:"var(--ds-text-information, #0055CC)"},'[data-prosemirror-node-name="status"] > [data-color=yellow] .lozenge-wrapper':{backgroundColor:"var(--ds-background-warning, #FFF7D6)"},'[data-prosemirror-node-name="status"] > [data-color=yellow] .lozenge-text':{color:"var(--ds-text-warning, #A54800)"},'[data-prosemirror-node-name="status"] > [data-color=red] .lozenge-wrapper':{backgroundColor:"var(--ds-background-danger, #FFECEB)"},'[data-prosemirror-node-name="status"] > [data-color=red] .lozenge-text':{color:"var(--ds-text-danger, #AE2E24)"},'[data-prosemirror-node-name="status"] > [data-color=green] .lozenge-wrapper':{backgroundColor:"var(--ds-background-success, #DCFFF1)"},'[data-prosemirror-node-name="status"] > [data-color=green] .lozenge-text':{color:"var(--ds-text-success, #216E4E)"}}),o=(0,n("3jLHL").css)({'[data-prosemirror-node-name="status"] .lozenge-wrapper':{backgroundColor:"var(--ds-background-neutral, #091E420F)",maxWidth:"100%",paddingInline:"var(--ds-space-050, 4px)",display:"inline-flex",borderRadius:"3px",blockSize:"min-content",position:"static",overflow:"hidden",boxSizing:"border-box",appearance:"none",border:"none"},'[data-prosemirror-node-name="status"] .lozenge-text':{fontSize:"11px",fontStyle:"normal",fontFamily:'var(--ds-font-family-body, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif)',fontWeight:"var(--ds-font-weight-bold, 700)",lineHeight:"16px",overflow:"hidden",textOverflow:"ellipsis",textTransform:"uppercase",whiteSpace:"nowrap",maxWidth:"calc(200px - var(--ds-space-100, 8px))"}}),i=()=>(0,n("3jLHL").css)`
	${o}
	${a()}
`,s=(0,n("3jLHL").css)`
	.${n("1zav4").TableSharedCssClassName.TABLE_CELL_WRAPPER},
		.${n("1zav4").TableSharedCssClassName.TABLE_HEADER_CELL_WRAPPER},
		[data-layout-section] {
		.${n("5UKg9").StatusSharedCssClassName.STATUS_CONTAINER} {
			max-width: 100%;
			line-height: 0;

			> span {
				width: 100%;
			}
		}
	}
	.${n("5UKg9").StatusSharedCssClassName.STATUS_CONTAINER} {
		> span {
			cursor: pointer;
			line-height: 0; /* Prevent responsive layouts increasing height of container. */
		}

		${(0,n("dh538").fg)("platform-component-visual-refresh")?(0,n("3jLHL").css)`
				&.${n("aFUXX").akEditorSelectedNodeClassName} .${n("5UKg9").StatusSharedCssClassName.STATUS_LOZENGE} > span {
					box-shadow: ${n("aFUXX").akEditorSelectedBoldBoxShadow};
				}
			`:(0,n("3jLHL").css)`
				&.${n("aFUXX").akEditorSelectedNodeClassName} .${n("5UKg9").StatusSharedCssClassName.STATUS_LOZENGE} > span {
					${(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.BoxShadow])}
				}
			`}
	}

	.danger {
		.${n("5UKg9").StatusSharedCssClassName.STATUS_LOZENGE} > span {
			background-color: ${n("aFUXX").akEditorDeleteBackgroundWithOpacity};
		}

		.${n("5UKg9").StatusSharedCssClassName.STATUS_CONTAINER}.${n("aFUXX").akEditorSelectedNodeClassName}
			.${n("5UKg9").StatusSharedCssClassName.STATUS_LOZENGE}
			> span {
			box-shadow: 0 0 0 ${n("aFUXX").akEditorSelectedBorderSize}px ${n("aFUXX").akEditorDeleteBorder};
		}
	}
`}),i("5UKg9",function(t,r){e(t.exports,"StatusSharedCssClassName",()=>a);let a={STATUS_CONTAINER:"statusView-content-wrap",STATUS_LOZENGE:"status-lozenge-span"}}),i("dR5Bd",function(t,r){e(t.exports,"taskDecisionStyles",()=>a),e(t.exports,"taskDecisionIconWithVisualRefresh",()=>o),e(t.exports,"taskDecisionIconWithoutVisualRefresh",()=>i),e(t.exports,"taskItemStyles",()=>s);let a=(0,n("3jLHL").css)({'.ak-editor-selected-node > [data-decision-wrapper], ol[data-node-type="decisionList"].ak-editor-selected-node':[{borderRadius:"4px"},(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.BoxShadow,n("b38UX").SelectionStyle.Blanket])],".danger decisionItemView-content-wrap.ak-editor-selected-node > div":{boxShadow:"0 0 0 1px var(--ds-border-danger, #E2483D)",backgroundColor:"var(--ds-blanket-danger, #EF5C4814)","&::after":{content:"none"}},'[data-prosemirror-node-name="decisionItem"]':{listStyleType:"none"},'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper]':{cursor:"pointer",display:"flex",flexDirection:"row",margin:"var(--ds-space-100, 8px) 0 0 0",padding:"var(--ds-space-100, 8px)",paddingLeft:"var(--ds-space-150, 12px)",borderRadius:"var(--ds-border-radius-100, 4px)",backgroundColor:"var(--ds-background-neutral, #091E420F)",position:"relative"},'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper] > [data-component="icon"]':{flex:"0 0 16px",height:"16px",width:"16px",margin:"var(--ds-space-050, 4px) var(--ds-space-150, 12px) 0 0",color:"var(--ds-icon-subtle, #626F86)",display:"flex",alignItems:"center",justifyContent:"center"},'[data-prosemirror-node-name="decisionItem"]:not(:has([data-empty]):not(:has([data-type-ahead]))) > [data-decision-wrapper] > [data-component="icon"]':{color:"var(--ds-icon-success, #22A06B)"},'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper] > [data-component="icon"] > span':{display:"inline-block",flexShrink:0,lineHeight:1},'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper] > [data-component="icon"] > span > svg':{overflow:"hidden",pointerEvents:"none",color:"currentColor",verticalAlign:"bottom"},'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper] > [data-component="placeholder"]':{margin:"0 0 0 calc(var(--ds-space-100, 8px) * 3.5)",position:"absolute",color:"var(--ds-text-subtlest, #626F86)",pointerEvents:"none",textOverflow:"ellipsis",overflow:"hidden",whiteSpace:"nowrap",maxWidth:"calc(100% - 50px)"},'[data-prosemirror-node-name="decisionItem"]:not(:has([data-empty]):not(:has([data-type-ahead]))) > [data-decision-wrapper] > [data-component="placeholder"]':{display:"none"},'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper] > [data-component="content"]':{margin:0,wordWrap:"break-word",minWidth:0,flex:"1 1 auto"}}),o=(0,n("3jLHL").css)({'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper] > [data-component="icon"] > span >  svg[data-icon-source="legacy"]':{display:"none"},'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper] > [data-component="icon"] > span':{boxSizing:"border-box",paddingInlineEnd:"var(--ds--button--new-icon-padding-end, 0)",paddingInlineStart:"var(--ds--button--new-icon-padding-start, 0)","@media screen and (forced-colors: active)":{color:"canvastext",filter:"grayscale(1)"}},'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper] > [data-component="icon"] > span > svg':{width:"var(--ds-space-300, 24px)",height:"var(--ds-space-300, 24px)"}}),i=(0,n("3jLHL").css)({'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper] > [data-component="icon"] > span >  svg[data-icon-source="refreshed"]':{display:"none"},'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper] > [data-component="icon"] > span':{width:"32px",height:"32px","@media screen and (forced-colors: active)":{filter:"grayscale(1)",color:"canvastext",fill:"canvas"}},'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper] > [data-component="icon"] > span > svg':{maxWidth:"100%",maxHeight:"100%",fill:"var(--ds-surface, #FFFFFF)",width:"32px",height:"32px"}}),s=(0,n("3jLHL").css)({'[data-prosemirror-node-name="taskItem"]':{listStyle:"none"},'[data-prosemirror-node-name="taskItem"] [data-component="task-item-main"]':{display:"flex",flexDirection:"row",position:"relative"},'[data-prosemirror-node-name="taskItem"] [data-component="placeholder"]':{position:"absolute",color:"var(--ds-text-subtlest, #626F86)",margin:"0 0 0 calc(var(--ds-space-100, 8px) * 3)",pointerEvents:"none",textOverflow:"ellipsis",overflow:"hidden",whiteSpace:"nowrap",maxWidth:"calc(100% - 50px)",display:"none"},"[data-prosemirror-node-name='taskItem']:has([data-empty]):not(:has([data-type-ahead])) [data-component='placeholder']":{display:"block"},'[data-prosemirror-node-name="taskItem"] [data-component="content"]':{margin:0,wordWrap:"break-word",minWidth:0,flex:"1 1 auto"},'[data-prosemirror-node-name="taskItem"] [data-component="checkbox-icon-wrap"]':{display:"inline-block",boxSizing:"border-box",flexShrink:0,lineHeight:1,paddingInlineEnd:"var(--ds--button--new-icon-padding-end, 0)",paddingInlineStart:"var(--ds--button--new-icon-padding-start, 0)"},'[data-prosemirror-node-name="taskItem"] [data-component="checkbox-icon-wrap"] svg':{overflow:"hidden",pointerEvents:"none",color:"currentColor",verticalAlign:"bottom",width:"var(--ds-space-200, 16px)",height:"var(--ds-space-200, 16px)"},'[data-prosemirror-node-name="taskItem"] input[type=checkbox]:not(:checked) + span [data-component=checkbox-checked-icon]':{display:"none"},'[data-prosemirror-node-name="taskItem"] input[type=checkbox]:not(:checked) + span [data-component=checkbox-unchecked-icon]':{display:"inline"},'[data-prosemirror-node-name="taskItem"] input[type=checkbox]:checked + span [data-component=checkbox-checked-icon]':{display:"inline"},'[data-prosemirror-node-name="taskItem"] input[type=checkbox]:checked + span [data-component=checkbox-unchecked-icon]':{display:"none"},[`[data-prosemirror-node-name="taskItem"] .${n("7iisy").TaskDecisionSharedCssClassName.TASK_CHECKBOX_CONTAINER}`]:{flex:"0 0 24px",width:"24px",height:"24px",position:"relative",alignSelf:"start","& > input[type='checkbox']":{width:"16px",height:"16px",zIndex:1,cursor:"pointer",outline:"none",margin:0,opacity:0,position:"absolute",top:"50%",left:"50%",transform:"translate(-50%, -50%)","&[disabled]":{cursor:"default"},"+ span":{width:"24px",height:"24px",position:"absolute",top:"50%",left:"50%",transform:"translate(-50%, -50%)"},"+ span > svg":{boxSizing:"border-box",display:"inline",top:"50%",left:"50%",transform:"translate(-50%, -50%)",maxWidth:"unset",maxHeight:"unset",position:"absolute",overflow:"hidden",color:"var(--ds-background-input, #FFFFFF)",transition:"color 0.2s ease-in-out, fill 0.2s ease-in-out","path:first-of-type":{visibility:"hidden"},"rect:first-of-type":{stroke:"var(--ds-border-input, #8590A2)",strokeWidth:1,transition:"stroke 0.2s ease-in-out"}},"&:hover + span > svg":{color:"var(--ds-background-input-hovered, #F7F8F9)","rect:first-of-type":{stroke:"var(--ds-border-input, #8590A2)"}},"&:checked:hover + span > svg":{color:"var(--ds-background-selected-bold-hovered, #0055CC)",fill:"var(--ds-icon-inverse, #FFFFFF)","rect:first-of-type":{stroke:"var(--ds-background-selected-bold-hovered, #0055CC)"}},"&:checked":{"+ span > svg":{"path:first-of-type":{visibility:"visible"},color:"var(--ds-background-selected-bold, #0C66E4)",fill:"var(--ds-icon-inverse, #FFFFFF)","rect:first-of-type":{stroke:"var(--ds-background-selected-bold, #0C66E4)"}}},"&:active + span > svg":{color:"var(--ds-background-input-pressed, #FFFFFF)","rect:first-of-type":{stroke:"var(--ds-border, #091E4224)"}},"&:checked:active + span > svg":{color:"var(--ds-background-input-pressed, #FFFFFF)",fill:"var(--ds-icon-inverse, #FFFFFF)","rect:first-of-type":{stroke:"var(--ds-border, #091E4224)"}},"&:disabled + span > svg, &:disabled:hover + span > svg, &:disabled:focus + span > svg, &:disabled:active + span > svg":{color:"var(--ds-background-disabled, #091E4208)","rect:first-of-type":{stroke:"var(--ds-background-disabled, #091E4208)"}},"&:disabled:checked + span > svg":{fill:"var(--ds-icon-disabled, #091E424F)"},"&:focus + span::after":{position:"absolute",width:"var(--ds-space-200, 16px)",height:"var(--ds-space-200, 16px)",border:"2px solid var(--ds-border-focused, #388BFF)",borderRadius:"var(--ds-space-050, 4px)",content:"''",display:"block",top:"50%",left:"50%",transform:"translate(-50%, -50%)"}}}})}),i("axOCf",function(r,a){e(r.exports,"default",()=>p);var o=n("gwFzn"),i=n("1oCLl"),s=n("dZ8uq"),d=n("iu6m9"),l=n("i3P6T");let c="undefined"!=typeof navigator&&navigator.userAgent.toLowerCase().indexOf("firefox")>-1;var p=t(o).forwardRef((e,t)=>{let{className:r,children:a,viewMode:o,isScrollable:p,appearance:u}=e,m=(0,n("ja596").u)(),{colorMode:h}=(0,n("cOrQJ").default)(),g="full-page"===u||"full-width"===u,b="comment"===u;return(0,n("3jLHL").jsx)("div",{className:r,ref:t,css:[n("3J63U").baseStyles,n("9YmWB").whitespaceStyles,n("lk33U").indentationStyles,n("cICoC").shadowStyles,n("dIjG1").InlineNodeViewSharedStyles,n("45RBH").hideSelectionStyles,((0,n("dh538").fg)("platform_editor_hide_cursor_when_pm_hideselection")||(0,d.editorExperiment)("platform_editor_advanced_code_blocks",!0))&&n("45RBH").hideCursorWhenHideSelectionStyles,n("45RBH").selectedNodeStyles,n("GlTW0").cursorStyles,n("9PdTF").firstFloatingToolbarButtonStyles,n("bEq83").placeholderTextStyles,(0,n("dh538").fg)("platform_editor_system_fake_text_highlight_colour")&&n("bEq83").placeholderTextStylesMixin_fg_platform_editor_system_fake_text_highlight_colour,n("bEq83").placeholderStyles,(0,d.editorExperiment)("platform_editor_controls","variant1")&&n("bEq83").placeholderOverflowStyles,(0,d.editorExperiment)("platform_editor_controls","variant1")&&(0,n("dh538").fg)("platform_editor_quick_insert_placeholder")&&n("bEq83").placeholderWrapStyles,n("4JzGQ").codeBlockStyles,!(0,n("dh538").fg)("platform_editor_fix_code_block_bg_color_in_macro_2")&&n("4JzGQ").codeBgColorStyles,!(0,n("dh538").fg)("platform_editor_typography_ugc")&&n("bWLXI").editorUGCTokensDefault,(0,n("dh538").fg)("platform_editor_typography_ugc")&&n("bWLXI").editorUGCTokensRefreshed,n("2jug1").blocktypeStyles,(0,n("dh538").fg)("platform_editor_typography_ugc")?n("2jug1").blocktypeStyles_fg_platform_editor_typography_ugc:n("2jug1").blocktypeStyles_without_fg_platform_editor_typography_ugc,(0,n("dh538").fg)("platform_editor_nested_dnd_styles_changes")&&n("2jug1").blocktypeStyles_fg_platform_editor_nested_dnd_styles_changes,n("i1h2v").codeMarkStyles,n("lVQfd").textColorStyles,n("aGf6a").backgroundColorStyles,n("2Iy63").listsStyles,n("jFNRW").ruleStyles,l.mediaStyles,(0,n("dh538").fg)("confluence_team_presence_scroll_to_pointer")?n("4IK7C").telepointerStyle:n("4IK7C").telepointerStyleWithInitialOnly,n("4IK7C").telepointerColorAndCommonStyle,n("3wjeF").gapCursorStyles,n("b7ODQ").panelStyles,(0,n("dh538").fg)("platform_editor_add_border_for_nested_panel")&&n("b7ODQ").panelStylesMixin_fg_platform_editor_add_border_for_nested_panel,(0,n("dh538").fg)("platform_editor_nested_dnd_styles_changes")&&n("b7ODQ").panelStylesMixin_fg_platform_editor_nested_dnd_styles_changes,n("b7ODQ").panelStylesMixin,n("1OsG9").mentionsStyles,n("d5t0o").tasksAndDecisionsStyles,n("4fO6z").gridStyles,n("lpKTf").blockMarksStyles,n("dkk8A").dateStyles,n("lwlSB").extensionStyles,n("7ddzL").expandStyles,(0,n("dh538").fg)("platform_editor_nested_dnd_styles_changes")?n("7ddzL").expandStylesMixin_fg_platform_editor_nested_dnd_styles_changes:n("7ddzL").expandStylesMixin_without_fg_platform_editor_nested_dnd_styles_changes,(0,n("dh538").fg)("platform-visual-refresh-icons")&&n("7ddzL").expandStylesMixin_fg_platform_visual_refresh_icons,(0,i.expValEquals)("platform_editor_find_and_replace_improvements","isEnabled",!0)?(0,n("dh538").fg)("platform_editor_find_and_replace_magenta_match")?n("4gNYY").findReplaceStylesNewMagenta:n("4gNYY").findReplaceStylesNewYellow:n("4gNYY").findReplaceStyles,n("5EMiD").textHighlightStyle,n("d5t0o").decisionStyles,n("d5t0o").taskItemStyles,(0,n("dh538").fg)("platform-visual-refresh-icons")&&n("d5t0o").decisionIconWithVisualRefresh,!(0,n("dh538").fg)("platform-visual-refresh-icons")&&n("d5t0o").decisionIconWithoutVisualRefresh,n("483hX").statusStyles,(0,n("dh538").fg)("platform-component-visual-refresh")?n("483hX").statusStylesMixin_fg_platform_component_visual_refresh:n("483hX").statusStylesMixin_without_fg_platform_component_visual_refresh,n("ejPu0").annotationStyles,n("65RTY").smartCardStyles,n("6svai").embedCardStyles,n("cU5yf").unsupportedStyles,n("jCkqQ").resizerStyles,n("cO7tu").layoutBaseStyles,(0,d.editorExperiment)("advanced_layouts",!0)&&n("cO7tu").layoutBaseStylesAdvanced,(0,d.editorExperiment)("advanced_layouts",!0)?n("cO7tu").layoutSectionStylesAdvanced:n("cO7tu").layoutSectionStylesNotAdvanced,(0,d.editorExperiment)("advanced_layouts",!0)?n("cO7tu").layoutColumnStylesAdvanced:n("cO7tu").layoutColumnStylesNotAdvanced,(0,d.editorExperiment)("advanced_layouts",!0)?n("cO7tu").layoutSelectedStylesAdvanced:n("cO7tu").layoutSelectedStylesNotAdvanced,(0,d.editorExperiment)("advanced_layouts",!0)&&n("cO7tu").layoutColumnResponsiveStyles,(0,d.editorExperiment)("advanced_layouts",!0)&&n("cO7tu").layoutResponsiveBaseStyles,(0,n("dh538").fg)("platform_editor_nested_dnd_styles_changes")&&n("cO7tu").layoutBaseStylesFixesUnderNestedDnDFG,(0,n("dh538").fg)("platform_editor_nested_dnd_styles_changes")?n("cO7tu").layoutColumnMartinTopFixesNew:n("cO7tu").layoutColumnMartinTopFixesOld,(0,n("dh538").fg)("linking_platform_smart_links_in_live_pages")?n("65RTY").smartLinksInLivePagesStyles:n("65RTY").smartLinksInLivePagesStylesOld,(0,n("dh538").fg)("platform-linking-visual-refresh-v1")&&n("65RTY").linkingVisualRefreshV1Styles,n("dkk8A").dateVanillaStyles,(0,n("dh538").fg)("platform_editor_typography_ugc")?n("boGpU").paragraphStylesUGCRefreshed:n("boGpU").paragraphStylesOld,(0,n("dh538").fg)("platform_editor_hyperlink_underline")?n("432pP").linkStyles:n("432pP").linkStylesOld,n("d7ZU3").browser.safari&&n("2Iy63").listsStylesSafariFix,(0,s.expValEqualsNoExposure)("platform_editor_breakout_resizing","isEnabled",!0)?(0,n("dh538").fg)("platform_editor_breakout_resizing_width_changes")?n("jCkqQ").pragmaticResizerStylesNew:n("jCkqQ").pragmaticResizerStyles:void 0,(0,d.editorExperiment)("advanced_layouts",!0)&&(0,s.expValEqualsNoExposure)("platform_editor_breakout_resizing","isEnabled",!0)&&(0,n("dh538").fg)("platform_editor_breakout_resizing_hello_release")&&n("jCkqQ").pragmaticStylesLayoutFirstNodeResizeHandleFix,(0,s.expValEqualsNoExposure)("platform_editor_breakout_resizing","isEnabled",!0)&&(0,n("dh538").fg)("platform_editor_breakout_resizing_hello_release")&&n("jCkqQ").pragmaticResizerStylesForTooltip,n("8ntZB").aiPanelBaseStyles,c&&n("8ntZB").aiPanelBaseFirefoxStyles,"dark"===h&&n("8ntZB").aiPanelDarkStyles,"dark"===h&&c&&n("8ntZB").aiPanelDarkFirefoxStyles,"view"===o&&n("cO7tu").layoutStylesForView,"view"===o&&(0,d.editorExperiment)("advanced_layouts",!0)&&n("cO7tu").layoutSelectedStylesForViewAdvanced,"view"===o&&(0,d.editorExperiment)("advanced_layouts",!1)&&n("cO7tu").layoutSelectedStylesForViewNotAdvanced,"view"===o&&(0,d.editorExperiment)("advanced_layouts",!0)&&n("cO7tu").layoutResponsiveStylesForView,b&&n("lFYdo").commentEditorStyles,b&&n("jRxPK").tableCommentEditorStyles,g&&n("hRSb9").fullPageEditorStyles,g&&n("9exTD").scrollbarStyles,(0,n("dh538").fg)("platform_editor_nested_dnd_styles_changes")?n("4JzGQ").firstCodeBlockWithNoMargin:n("4JzGQ").firstCodeBlockWithNoMarginOld,n("1wqVI").firstBlockNodeStyles,n("1OsG9").mentionNodeStyles,n("1OsG9").mentionsSelectionStyles,(0,n("dh538").fg)("platform_editor_centre_mention_padding")&&n("1OsG9").mentionsStylesMixin_platform_editor_centre_mention_padding,n("jaHIY").emojiStyles,n("b7ODQ").panelViewStyles,l.mediaGroupStyles,l.mediaAlignmentStyles,n("jRxPK").tableLayoutFixes,n("432pP").hyperLinkFloatingToolbarStyles,!(0,n("dh538").fg)("platform-visual-refresh-icons")&&n("432pP").linkLegacyIconStylesFix,(0,n("dh538").fg)("confluence_floating_toolbar_animation")&&n("kxdG4").selectionToolbarAnimationStyles],"data-editor-scroll-container":p?"true":void 0,"data-testid":"editor-content-container",style:{"--ak-editor-base-font-size":`${(0,n("aFUXX").editorFontSize)({theme:m})}px`,"--ak-editor--large-gutter-padding":`${(0,n("aFUXX").akEditorGutterPaddingDynamic)()}px`}},a)})}),i("8ntZB",function(t,r){e(t.exports,"aiPanelBaseStyles",()=>x),e(t.exports,"aiPanelBaseFirefoxStyles",()=>v),e(t.exports,"aiPanelDarkStyles",()=>y),e(t.exports,"aiPanelDarkFirefoxStyles",()=>E);let a=(0,n("3jLHL").keyframes)({"0%":{"--panel-gradient-angle":"0deg"},"100%":{"--panel-gradient-angle":"360deg"}}),o=(0,n("3jLHL").keyframes)({"0%":{"--panel-gradient-angle":"0deg",backgroundPosition:"100%"},"100%":{"--panel-gradient-angle":"360deg",backgroundPosition:"-100%"}}),i="#0065FF",s="#0469FF",d="#BF63F3",l="#FFA900",c="#0065FF80",p="#0469FF80",u="#BF63F380",m="#FFA90080",h=`linear-gradient(90deg, ${i} 0%, ${s} 12%, ${d} 24%, ${l} 48%, ${d} 64%, ${s} 80%, ${i} 100%)`,g=`conic-gradient(from var(--panel-gradient-angle, 270deg), ${i} 0%, ${s} 20%, ${d} 50%, ${l} 56%, ${i} 100%)`,b=`linear-gradient(90deg, ${c} 0%, ${p} 12%, ${u} 24%, ${m} 48%, ${u} 64%, ${p} 80%, ${c} 100%)`,f=`conic-gradient(from var(--panel-gradient-angle, 270deg), ${c} 0%, ${p} 20%, ${u} 50%, ${m} 56%, ${c} 100%)`,x=(0,n("3jLHL").css)({"@property --panel-gradient-angle":{syntax:"<angle>",initialValue:"270deg",inherits:!1},'div[extensionType="com.atlassian.ai-blocks"]':{".extension-label":{display:"none"},".extension-container":{position:"relative",boxShadow:"none",overflow:"unset",backgroundColor:"var(--ds-surface, #FFFFFF) !important","&::before, &::after":{content:"''",position:"absolute",zIndex:-1,width:"calc(100% + 2px)",height:"calc(100% + 2px)",top:"-1px",left:"-1px",borderRadius:"calc(var(--ds-border-radius-100, 3px) + 1px)",transform:"translate3d(0, 0, 0)",background:g},"&.with-hover-border":{"&::before, &::after":{background:"var(--ds-border-input, #8590A2)"}},"& .with-margin-styles":{backgroundColor:"var(--ds-surface, #FFFFFF) !important",borderRadius:"var(--ds-border-radius-100, 3px)"}}},'div[extensionType="com.atlassian.ai-blocks"]:has(.streaming)':{".extension-container":{"&::before, &::after":{animationName:a,animationDuration:"2s",animationTimingFunction:"linear",animationIterationCount:"infinite","@media (prefers-reduced-motion)":{animation:"none"}}}},'div[extensionType="com.atlassian.ai-blocks"].danger':{".extension-container":{boxShadow:"0 0 0 1px var(--ds-border-danger, #E2483D)"}},'div[extensiontype="com.atlassian.ai-blocks"][extensionkey="ai-action-items-block:aiActionItemsBodiedExtension"]':{'div[data-node-type="actionList"]':{margin:"0 !important"}}}),v=(0,n("3jLHL").css)({'div[extensionType="com.atlassian.ai-blocks"]':{"&::before, &::after":{background:h,backgroundSize:"200%"}},'div[extensionType="com.atlassian.ai-blocks"]:has(.streaming)':{".extension-container":{"&::before, &::after":{animationName:o,animationDirection:"normal",animationDuration:"1s"}}}}),y=(0,n("3jLHL").css)({'div[extensionType="com.atlassian.ai-blocks"]':{".extension-container":{"&::before, &::after":{background:f}}}}),E=(0,n("3jLHL").css)({'div[extensionType="com.atlassian.ai-blocks"]':{".extension-container":{"&::before, &::after":{background:b,backgroundSize:"200%"}}}})}),i("ejPu0",function(t,r){e(t.exports,"annotationStyles",()=>a);let a=(0,n("3jLHL").css)({".ProseMirror":{[`.${n("6ESsx").AnnotationSharedClassNames.blur}, .${n("6ESsx").AnnotationSharedClassNames.focus}, .${n("6ESsx").AnnotationSharedClassNames.draft}, .${n("6ESsx").AnnotationSharedClassNames.hover}`]:{borderBottom:"2px solid transparent",cursor:"pointer",padding:"1px 0 2px","&:has(.card), &:has([data-inline-card])":{padding:"5px 0 3px 0"},"&:has(.date-lozenger-container)":{paddingTop:"var(--ds-space-025, 2px)"}},[`.${n("6ESsx").AnnotationSharedClassNames.focus}`]:{background:"var(--ds-background-accent-yellow-subtlest-pressed, #F5CD47)",borderBottomColor:"var(--ds-border-accent-yellow, #B38600)",boxShadow:"var(--ds-shadow-raised, 0px 1px 1px #091E4240, 0px 0px 1px #091E424f)"},[`.${n("6ESsx").AnnotationSharedClassNames.draft}`]:{background:"var(--ds-background-accent-yellow-subtlest-pressed, #F5CD47)",borderBottomColor:"var(--ds-border-accent-yellow, #B38600)",boxShadow:"var(--ds-shadow-raised, 0px 1px 1px #091E4240, 0px 0px 1px #091E424f)",cursor:"initial"},[`.${n("6ESsx").AnnotationSharedClassNames.blur}`]:{background:"var(--ds-background-accent-yellow-subtlest, #FFF7D6)",borderBottomColor:"var(--ds-border-accent-yellow, #B38600)"},[`.${n("6ESsx").AnnotationSharedClassNames.hover}`]:{background:"var(--ds-background-accent-yellow-subtlest-hovered, #F8E6A0)",borderBottomColor:"var(--ds-border-accent-yellow, #B38600)",boxShadow:"var(--ds-shadow-raised, 0px 1px 1px #091E4240, 0px 0px 1px #091E424f)"}}})}),i("aGf6a",function(t,r){e(t.exports,"backgroundColorStyles",()=>a);let a=(0,n("3jLHL").css)({".fabric-background-color-mark":{backgroundColor:"var(--custom-palette-color, inherit)",borderRadius:2,paddingTop:1,paddingBottom:2,boxDecorationBreak:"clone"},"a .fabric-background-color-mark":{backgroundColor:"unset"},".fabric-background-color-mark .ak-editor-annotation":{backgroundColor:"unset"}})}),i("3J63U",function(t,r){e(t.exports,"baseStyles",()=>a);let a=(0,n("3jLHL").css)({"--ak-editor--default-gutter-padding":"32px","--ak-editor--default-layout-width":"760px","--ak-editor--full-width-layout-width":"1800px","--ak-editor--line-length":"min(calc(100cqw - var(--ak-editor--large-gutter-padding) * 2), var(--ak-editor--default-layout-width))","--ak-editor--breakout-wide-layout-width":"905px","--ak-editor--breakout-full-page-guttering-padding":"calc(var(--ak-editor--large-gutter-padding) * 2 + var(--ak-editor--default-gutter-padding))","--ak-editor--breakout-fallback-width":"calc(100cqw - var(--ak-editor--breakout-full-page-guttering-padding))",".fabric-editor--full-width-mode":{"--ak-editor--line-length":"min(calc(100cqw - var(--ak-editor--large-gutter-padding) * 2), var(--ak-editor--full-width-layout-width))","--ak-editor--breakout-fallback-width":"100%"},".ProseMirror":{"--ak-editor-max-container-width":"calc(100cqw - var(--ak-editor--large-gutter-padding))",outline:"none",fontSize:"var(--ak-editor-base-font-size)"},".ProseMirror > div[data-prosemirror-node-block] [data-prosemirror-node-block]":{"--ak-editor-max-container-width":"100%"},"@container editor-area (width >= 1266px)":{".ProseMirror":{"--ak-editor--breakout-wide-layout-width":"1011px"}}})}),i("lpKTf",function(t,r){e(t.exports,"blockMarksStyles",()=>a);let a=(0,n("3jLHL").css)({"*:not(.fabric-editor-block-mark) >, *:not(.fabric-editor-block-mark) > div.fabric-editor-block-mark:first-of-type:not(.fabric-editor-indentation-mark):not(.fabric-editor-alignment), .fabric-editor-alignment:first-of-type:first-child, .ProseMirror .fabric-editor-indentation-mark:first-of-type:first-child":{"p, h1, h2, h3, h4, h5, h6, .heading-wrapper":{"&:first-child:not(style), style:first-child + *":{marginTop:0}}}})}),i("2jug1",function(t,r){e(t.exports,"blocktypeStyles",()=>a),e(t.exports,"blocktypeStyles_fg_platform_editor_typography_ugc",()=>o),e(t.exports,"blocktypeStyles_without_fg_platform_editor_typography_ugc",()=>i),e(t.exports,"blocktypeStyles_fg_platform_editor_nested_dnd_styles_changes",()=>s);let a=(0,n("3jLHL").css)({".ProseMirror":{"& blockquote":{boxSizing:"border-box",color:"inherit",width:"100%",display:"inline-block",paddingLeft:"var(--ds-space-200, 16px)",borderLeftWidth:"2px",borderLeftStyle:"solid",borderLeftColor:"var(--ds-border, #091E4224)",margin:"0.75rem 0 0 0",marginRight:0,'[dir="rtl"] &':{paddingLeft:0,paddingRight:"var(--ds-space-200, 16px)"},"&:first-child":{marginTop:0},"&::before":{content:"''"},"&::after":{content:"none"},"& p":{display:"block"},"& table, & table:last-child":{display:"inline-table"},"> .code-block:last-child, >.mediaSingleView-content-wrap:last-child, >.mediaGroupView-content-wrap:last-child":{display:"block"},"> .extensionView-content-wrap:last-child":{display:"block"}},".fabric-editor-block-mark.fabric-editor-alignment:not(:first-child)":{"> h1:first-child":{marginTop:"1.667em"},"> h2:first-child":{marginTop:"1.8em"},"> h3:first-child":{marginTop:"2em"},"> h4:first-child":{marginTop:"1.357em"},"> h5:first-child":{marginTop:"1.667em"},"> h6:first-child":{marginTop:"1.455em"}},".ProseMirror-gapcursor:first-child + .fabric-editor-block-mark.fabric-editor-alignment, .ProseMirror-widget:first-child + .fabric-editor-block-mark.fabric-editor-alignment, .ProseMirror-widget:first-child + .ProseMirror-widget:nth-child(2) + .fabric-editor-block-mark.fabric-editor-alignment":{"> :is(h1, h2, h3, h4, h5, h6):first-child":{marginTop:"0"}}}}),o=(0,n("3jLHL").css)({".ProseMirror":{"& h1":{font:"var(--editor-font-ugc-token-heading-h1)",marginBottom:0,marginTop:"1.45833em","& strong":{fontWeight:"var(--editor-font-ugc-token-weight-heading-bold)"}},"& h2":{font:"var(--editor-font-ugc-token-heading-h2)",marginBottom:0,marginTop:"1.4em","& strong":{fontWeight:"var(--editor-font-ugc-token-weight-heading-bold)"}},"& h3":{font:"var(--editor-font-ugc-token-heading-h3)",marginBottom:0,marginTop:"1.31249em","& strong":{fontWeight:"var(--editor-font-ugc-token-weight-heading-bold)"}},"& h4":{font:"var(--editor-font-ugc-token-heading-h4)",marginTop:"1.25em","& strong":{fontWeight:"var(--editor-font-ugc-token-weight-heading-bold)"}},"& h5":{font:"var(--editor-font-ugc-token-heading-h5)",marginTop:"1.45833em",textTransform:"none","& strong":{fontWeight:"var(--editor-font-ugc-token-weight-heading-bold)"}},"& h6":{font:"var(--editor-font-ugc-token-heading-h6)",marginTop:"1.59091em",textTransform:"none","& strong":{fontWeight:"var(--editor-font-ugc-token-weight-heading-bold)"}}}}),i=(0,n("3jLHL").css)({".ProseMirror":{"& h1":{fontSize:"calc(24em / 14)",fontStyle:"inherit",lineHeight:"calc(28 / 24)",color:"var(--ds-text, #172B4D)",fontWeight:"var(--ds-font-weight-medium, 500)",letterSpacing:"-0.01em",marginBottom:0,marginTop:"1.667em"},"& h2":{fontSize:"calc(20em / 14)",fontStyle:"inherit",lineHeight:"calc(24 / 20)",color:"var(--ds-text, #172B4D)",fontWeight:"var(--ds-font-weight-medium, 500)",letterSpacing:"-0.008em",marginTop:"1.8em",marginBottom:0},"& h3":{fontSize:"calc(16em / 14)",fontStyle:"inherit",lineHeight:"calc(20 / 16)",color:"var(--ds-text, #172B4D)",fontWeight:"var(--ds-font-weight-semibold, 600)",letterSpacing:"-0.006em",marginTop:"2em",marginBottom:0},"& h4":{fontSize:"calc(14em / 14)",fontStyle:"inherit",lineHeight:"calc(16 / 14)",color:"var(--ds-text, #172B4D)",fontWeight:"var(--ds-font-weight-semibold, 600)",letterSpacing:"-0.003em",marginTop:"1.357em"},"& h5":{fontSize:"calc(12em / 14)",fontStyle:"inherit",lineHeight:"calc(16 / 12)",color:"var(--ds-text, #172B4D)",fontWeight:"var(--ds-font-weight-semibold, 600)",marginTop:"1.667em",textTransform:"none"},"& h6":{fontSize:"calc(11em / 14)",fontStyle:"inherit",lineHeight:"calc(16 / 11)",color:"var(--ds-text-subtlest, #626F86)",fontWeight:"var(--ds-font-weight-bold, 700)",marginTop:"1.455em",textTransform:"none"}}}),s=(0,n("3jLHL").css)({".ak-editor-content-area.appearance-full-page .ProseMirror blockquote":{paddingLeft:"var(--ds-space-250, 20px)"},".ak-editor-content-area .ak-editor-content-area .ProseMirror blockquote":{paddingLeft:"var(--ds-space-200, 16px)"}})}),i("4JzGQ",function(t,r){e(t.exports,"CodeBlockSharedCssClassName",()=>a),e(t.exports,"codeBlockStyles",()=>d),e(t.exports,"codeBgColorStyles",()=>l),e(t.exports,"firstCodeBlockWithNoMargin",()=>c),e(t.exports,"firstCodeBlockWithNoMarginOld",()=>p);let a={CODEBLOCK_CONTAINER:"code-block",CODEBLOCK_START:"code-block--start",CODEBLOCK_END:"code-block--end",CODEBLOCK_CONTENT_WRAPPER:"code-block-content-wrapper",CODEBLOCK_LINE_NUMBER_GUTTER:"line-number-gutter",CODEBLOCK_CONTENT:"code-content",DS_CODEBLOCK:"[data-ds--code--code-block]",CODEBLOCK_CONTENT_WRAPPED:"code-content--wrapped",CODEBLOCK_CONTAINER_LINE_NUMBER_WIDGET:"code-content__line-number--wrapped"},o="0.875rem",i="0.75rem",s=(0,n("3jLHL").css)({"&::after":{height:"100%",content:"''",position:"absolute",left:0,top:0,width:"24px",backgroundColor:"var(--ds-blanket-danger, #EF5C4814)"}}),d=(0,n("3jLHL").css)({".ProseMirror":{[`.${a.CODEBLOCK_CONTENT_WRAPPED} > .${a.CODEBLOCK_CONTENT_WRAPPER} > .${a.CODEBLOCK_CONTENT}`]:{marginRight:"var(--ds-space-100, 8px)",code:{display:"block",wordBreak:"break-word",whiteSpace:"pre-wrap"}},[`.${a.CODEBLOCK_CONTENT_WRAPPER} > .${a.CODEBLOCK_CONTENT}`]:{display:"flex",flex:1,code:{flexGrow:1,whiteSpace:"pre"}},[`.${a.CODEBLOCK_CONTAINER}`]:{position:"relative",backgroundColor:"var(--ds-surface-raised, #FFFFFF)",borderRadius:"var(--ds-border-radius, 3px)",margin:`${i} 0 0 0`,fontFamily:'var(--ds-font-family-code, ui-monospace, Menlo, "Segoe UI Mono", "Ubuntu Mono", monospace)',minWidth:48,cursor:"pointer",clear:"both",whiteSpace:"normal",".code-block-gutter-pseudo-element::before":{content:"attr(data-label)"},[`.${a.CODEBLOCK_START}`]:{position:"absolute",visibility:"hidden",height:"1.5rem",top:0,left:0},[`.${a.CODEBLOCK_END}`]:{position:"absolute",visibility:"hidden",height:"1.5rem",bottom:0,right:0},[`.${a.CODEBLOCK_CONTENT_WRAPPER}`]:[n("8pI1J").overflowShadowStyles,{position:"relative",backgroundColor:"var(--ds-background-neutral, #091E420F)",display:"flex",borderRadius:"var(--ds-border-radius, 3px)",width:"100%",counterReset:"line",overflowX:"auto",backgroundRepeat:"no-repeat",backgroundAttachment:"local, local, local, local, scroll, scroll, scroll, scroll",backgroundSize:`var(--ds-space-300, 24px) 100%,
	                         var(--ds-space-300, 24px) 100%,
	                         var(--ds-space-100, 8px) 100%,
	                         var(--ds-space-100, 8px) 100%,
	                         var(--ds-space-100, 8px) 100%,
	                         1px 100%,
	                         var(--ds-space-100, 8px) 100%,
	                         1px 100%`,backgroundPosition:`0 0,
	                             0 0,
                               100% 0,
                               100% 0,
                               100% 0,
                               100% 0,
	                             0 0,
	                             0 0`,overflowY:"hidden"}],[`.${a.CODEBLOCK_LINE_NUMBER_GUTTER}`]:{backgroundColor:"var(--ds-background-neutral, #091E420F)",position:"relative",width:"var(--lineNumberGutterWidth, 2rem)",padding:"var(--ds-space-100, 8px)",flexShrink:0,fontSize:o,boxSizing:"content-box"},[`.${a.CODEBLOCK_LINE_NUMBER_GUTTER}::before`]:{content:"'1'",visibility:"hidden",fontSize:o,lineHeight:"1.5rem"},[`.${a.CODEBLOCK_CONTENT}`]:{code:{tabSize:4,cursor:"text",color:"var(--ds-text, #172B4D)",borderRadius:"var(--ds-border-radius, 3px)",margin:"var(--ds-space-100, 8px)",fontSize:o,lineHeight:"1.5rem"}},[`.${a.CODEBLOCK_CONTAINER_LINE_NUMBER_WIDGET}`]:{pointerEvents:"none",userSelect:"none",width:"var(--lineNumberGutterWidth, 2rem)",left:0,position:"absolute",fontSize:o,padding:"0px var(--ds-space-100, 8px)",lineHeight:"1.5rem",textAlign:"right",color:"var(--ds-text-subtlest, #505F79)",boxSizing:"content-box"}},li:{"> .code-block":{margin:`${i} 0 0 0`},"> .code-block:first-child, > .ProseMirror-gapcursor:first-child + .code-block":{marginTop:0},"> div:last-of-type.code-block, > pre:last-of-type.code-block":{marginBottom:i}},".code-block.ak-editor-selected-node:not(.danger)":[n("45RBH").boxShadowSelectionStyles,n("45RBH").blanketSelectionStyles,n("45RBH").hideNativeBrowserTextSelectionStyles],".danger.code-block":{boxShadow:"0 0 0 1px var(--ds-border-danger, #E2483D)",[`.${a.CODEBLOCK_LINE_NUMBER_GUTTER}`]:[{backgroundColor:"var(--ds-background-danger, #FFECEB)",color:"var(--ds-text-danger, #AE2E24)"},s],[`.${a.CODEBLOCK_CONTENT}`]:{backgroundColor:"var(--ds-blanket-danger, #EF5C4814)"}},".danger .code-block":{[`.${a.CODEBLOCK_LINE_NUMBER_GUTTER}`]:[{backgroundColor:"var(--ds-background-danger, #FFECEB)",color:"var(--ds-text-danger, #AE2E24)"},s],[`.${a.CODEBLOCK_CONTENT}`]:{backgroundColor:"var(--ds-blanket-danger, #EF5C4814)"}}}}),l=(0,n("3jLHL").css)({[`.${a.CODEBLOCK_CONTAINER}`]:{"--ds--code--bg-color":"transparent"}}),c=(0,n("3jLHL").css)({".ProseMirror":{".ak-editor-panel__content":{"> .code-block:first-child, > .ProseMirror-widget:first-child + .code-block, > .ProseMirror-widget:first-child + .ProseMirror-widget + .code-block":{margin:"0!important"}}}}),p=(0,n("3jLHL").css)({".ProseMirror":{".ak-editor-panel__content":{"> .code-block:first-child":{margin:"0!important"}}}})}),i("8pI1J",function(t,r){e(t.exports,"overflowShadowStyles",()=>a);let a=(0,n("3jLHL").css)({backgroundImage:`
		linear-gradient(
			to right,
			var(--ds-background-neutral, #091E420F) var(--ds-space-300, 24px),
			transparent var(--ds-space-300, 24px)
		),
		linear-gradient(
			to right,
			var(--ds-surface-raised, #FFFFFF) var(--ds-space-300, 24px),
			transparent var(--ds-space-300, 24px)
		),
		linear-gradient(
			to left,
			var(--ds-background-neutral, #091E420F) var(--ds-space-100, 8px),
			transparent var(--ds-space-100, 8px)
		),
		linear-gradient(
			to left,
			var(--ds-surface-raised, #FFFFFF) var(--ds-space-100, 8px),
			transparent var(--ds-space-100, 8px)
		),
		linear-gradient(
			to left,
			var(--ds-shadow-overflow-spread, #091e4229) 0,
			var(--ds-UNSAFE-transparent, transparent)  var(--ds-space-100, 8px)
		),
		linear-gradient(
			to left,
			var(--ds-shadow-overflow-perimeter, #091e421f) 0,
			var(--ds-UNSAFE-transparent, transparent)  var(--ds-space-100, 8px)
		),
		linear-gradient(
			to right,
			var(--ds-shadow-overflow-spread, #091e4229) 0,
			var(--ds-UNSAFE-transparent, transparent)  var(--ds-space-100, 8px)
		),
		linear-gradient(
			to right,
			var(--ds-shadow-overflow-perimeter, #091e421f) 0,
			var(--ds-UNSAFE-transparent, transparent)  var(--ds-space-100, 8px)
		)
	`})}),i("45RBH",function(t,r){e(t.exports,"hideNativeBrowserTextSelectionStyles",()=>a),e(t.exports,"borderSelectionStyles",()=>o),e(t.exports,"boxShadowSelectionStyles",()=>i),e(t.exports,"backgroundSelectionStyles",()=>s),e(t.exports,"blanketSelectionStyles",()=>d),e(t.exports,"hideSelectionStyles",()=>l),e(t.exports,"hideCursorWhenHideSelectionStyles",()=>c),e(t.exports,"selectedNodeStyles",()=>p);let a=(0,n("3jLHL").css)({"&::selection,*::selection":{backgroundColor:"transparent"},"&::-moz-selection,*::-moz-selection":{backgroundColor:"transparent"}}),o=(0,n("3jLHL").css)({border:"1px solid var(--ds-border-selected, #0C66E4)","&::after":{height:"100%",content:"'\\00a0'",background:"var(--ds-border-selected, #0C66E4)",position:"absolute",right:-1,top:0,bottom:0,width:1,border:"none",display:"inline-block"}}),i=(0,n("3jLHL").css)({boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4)",borderColor:"transparent"}),s=(0,n("3jLHL").css)({backgroundColor:"var(--ds-background-selected, #E9F2FF)"}),d=(0,n("3jLHL").css)({position:"relative","-webkit-user-select":"text","&::before":{position:"absolute",content:"''",left:0,right:0,top:0,bottom:0,width:"100%",pointerEvents:"none",zIndex:12,backgroundColor:"var(--ds-blanket-selected, #388BFF14)"}}),l=(0,n("3jLHL").css)({".ProseMirror-hideselection":{"*::selection":{background:"transparent"},"*::-moz-selection":{background:"transparent"}}}),c=(0,n("3jLHL").css)({".ProseMirror-hideselection":{caretColor:"transparent"}}),p=(0,n("3jLHL").css)({".ProseMirror-selectednode":{outline:"none"},".ProseMirror-selectednode:empty":{outline:"2px solid var(--ds-border-focused, #388BFF)"}})}),i("i1h2v",function(t,r){e(t.exports,"codeMarkStyles",()=>a);let a=(0,n("3jLHL").css)({".code":{"--ds--code--bg-color":"var(--ds-background-neutral, #091E420F)",display:"inline",padding:"2px 0.5ch",backgroundColor:"var(--ds--code--bg-color,var(--ds-background-neutral, #091E420F))",borderRadius:"var(--ds-border-radius, 3px)",borderStyle:"none",boxDecorationBreak:"clone",color:"var(--ds-text, #172B4D)",fontFamily:'var(--ds-font-family-code, ui-monospace, Menlo, "Segoe UI Mono", "Ubuntu Mono", monospace)',fontSize:"0.875em",fontWeight:"var(--ds-font-weight-regular, 400)",overflow:"auto",overflowWrap:"break-word",whiteSpace:"pre-wrap"}})}),i("lFYdo",function(t,r){e(t.exports,"commentEditorStyles",()=>a);let a=(0,n("3jLHL").css)({flexGrow:1,overflowX:"clip",lineHeight:"24px",".ProseMirror":{margin:"var(--ds-space-150, 12px)"},".gridParent":{marginLeft:"var(--ds-space-025, 2px)",marginRight:"var(--ds-space-025, 2px)",width:"calc(100% + 2px)"},padding:"var(--ds-space-250, 20px)"})}),i("GlTW0",function(t,r){e(t.exports,"cursorStyles",()=>a);let a=(0,n("3jLHL").css)({".ProseMirror.ProseMirror-focused:has(.ProseMirror-mark-boundary-cursor)":{caretColor:"transparent"},".ProseMirror:not(.ProseMirror-focused) .ProseMirror-mark-boundary-cursor":{display:"none"}})}),i("dkk8A",function(t,r){e(t.exports,"dateVanillaStyles",()=>i),e(t.exports,"dateStyles",()=>s);let a="date-lozenger-container",o="dateView-content-wrap",i=(0,n("3jLHL").css)({[`[data-prosemirror-node-name='date'] .${a} span`]:{backgroundColor:"var(--ds-background-neutral, #091E420F)",color:"var(--ds-text, #172B4D)",borderRadius:"var(--ds-border-radius-100, 4px)",padding:"var(--ds-space-025, 2px) var(--ds-space-050, 4px)",margin:"0 1px",position:"relative",transition:"background 0.3s",whiteSpace:"nowrap",cursor:"unset"},[`[data-prosemirror-node-name='date'] .${a} span:hover`]:{backgroundColor:"var(--ds-background-neutral-hovered, #091E4224)"},[`[data-prosemirror-node-name='date'] .${a} span.date-node-color-red`]:{backgroundColor:"var(--ds-background-accent-red-subtlest, #FFECEB)",color:"var(--ds-text-accent-red, #AE2E24)"},[`[data-prosemirror-node-name='date'] .${a} span.date-node-color-red:hover`]:{backgroundColor:"var(--ds-background-accent-red-subtler, #FFD5D2)"}}),s=(0,n("3jLHL").css)({[`.${a} span`]:{whiteSpace:"unset"},[`.${o}`]:{[`.${a}`]:{lineHeight:"initial",cursor:"pointer"},"&.ak-editor-selected-node":{[`.${a} > span`]:[n("45RBH").boxShadowSelectionStyles,n("45RBH").hideNativeBrowserTextSelectionStyles]}},".danger":{[`.${o}.ak-editor-selected-node .${a} > span`]:{boxShadow:"0 0 0 1px var(--ds-border-danger, #E2483D)"}}})}),i("bWLXI",function(t,r){e(t.exports,"editorUGCTokensDefault",()=>a),e(t.exports,"editorUGCTokensRefreshed",()=>o);let a=(0,n("3jLHL").css)({"--editor-font-ugc-token-heading-h1":'normal 500 1.71429em/1.16667 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',"--editor-font-ugc-token-heading-h2":'normal 500 1.42857em/1.2 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',"--editor-font-ugc-token-heading-h3":'normal 600 1.14286em/1.25 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',"--editor-font-ugc-token-heading-h4":'normal 600 1em/1.14286 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',"--editor-font-ugc-token-heading-h5":'normal 600 0.857143em/1.33333 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',"--editor-font-ugc-token-heading-h6":'normal 700 0.785714em/1.45455 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',"--editor-font-ugc-token-body":'normal 400 1em/1.714 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',"--editor-font-ugc-token-weight-heading-bold":"700"});(0,n("3jLHL").css)({"--editor-font-ugc-token-heading-h1":'normal 600 1.71429em/1.16667 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',"--editor-font-ugc-token-heading-h2":'normal 600 1.42857em/1.2 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',"--editor-font-ugc-token-heading-h3":'normal 600 1.14286em/1.25 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',"--editor-font-ugc-token-heading-h4":'normal 600  1em/1.14286 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',"--editor-font-ugc-token-heading-h5":'normal 600  0.857143em/1.33333 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',"--editor-font-ugc-token-heading-h6":'normal 600 0.785714em/1.45455 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',"--editor-font-ugc-token-body":'normal 400 1em/1.714 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',"--editor-font-ugc-token-weight-heading-bold":"700"});let o=(0,n("3jLHL").css)({"--editor-font-ugc-token-heading-h1":'normal 600 1.71429em/1.16667 "Atlassian Sans", ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',"--editor-font-ugc-token-heading-h2":'normal 600 1.42857em/1.2 "Atlassian Sans", ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',"--editor-font-ugc-token-heading-h3":'normal 600 1.14286em/1.25 "Atlassian Sans", ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',"--editor-font-ugc-token-heading-h4":'normal 600 1em/1.14286 "Atlassian Sans", ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',"--editor-font-ugc-token-heading-h5":'normal 600 0.857143em/1.33333 "Atlassian Sans", ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',"--editor-font-ugc-token-heading-h6":'normal 600 0.785714em/1.45455 "Atlassian Sans", ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',"--editor-font-ugc-token-body":'normal 400 1em/1.714 "Atlassian Sans", ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',"--editor-font-ugc-token-weight-heading-bold":"700"})}),i("6svai",function(t,r){e(t.exports,"embedCardStyles",()=>a);let a=(0,n("3jLHL").css)({".ProseMirror":{".embedCardView-content-wrap[layout^='wrap-']":{maxWidth:"100%",position:"relative",zIndex:2},".embedCardView-content-wrap[layout='wrap-left']":{float:"left"},".embedCardView-content-wrap[layout='wrap-right']":{float:"right"},".embedCardView-content-wrap[layout='wrap-right'] + .embedCardView-content-wrap[layout='wrap-left']":{clear:"both"}}})}),i("jaHIY",function(t,r){e(t.exports,"emojiStyles",()=>o);let a=(0,n("3jLHL").css)({borderRadius:"2px"}),o=(0,n("3jLHL").css)({[`.${n("98HrB").EmojiSharedCssClassName.EMOJI_CONTAINER}`]:{display:"inline-block"},[`.${n("98HrB").EmojiSharedCssClassName.EMOJI_SPRITE}, .${n("98HrB").EmojiSharedCssClassName.EMOJI_IMAGE}`]:{background:"no-repeat transparent",display:"inline-block",height:`${n("fhsiz").defaultEmojiHeight}px`,maxHeight:`${n("fhsiz").defaultEmojiHeight}px`,cursor:"pointer",verticalAlign:"middle",userSelect:"all"},[`.${n("aFUXX").akEditorSelectedNodeClassName}`]:{[`.${n("98HrB").EmojiSharedCssClassName.EMOJI_SPRITE}, .${n("98HrB").EmojiSharedCssClassName.EMOJI_IMAGE}`]:[a,n("45RBH").blanketSelectionStyles,n("45RBH").boxShadowSelectionStyles,n("45RBH").hideNativeBrowserTextSelectionStyles]}})}),i("7ddzL",function(t,r){e(t.exports,"expandStyles",()=>a),e(t.exports,"expandStylesMixin_fg_platform_visual_refresh_icons",()=>o),e(t.exports,"expandStylesMixin_fg_platform_editor_nested_dnd_styles_changes",()=>i),e(t.exports,"expandStylesMixin_without_fg_platform_editor_nested_dnd_styles_changes",()=>s);let a=(0,n("3jLHL").css)({".ak-editor-expand__icon > div":{display:"flex"},".ak-editor-expand":{borderWidth:"1px",borderStyle:"solid",borderColor:"transparent",borderRadius:"var(--ds-border-radius-100, 4px)",minHeight:"25px",background:"var(--ds-background-neutral-subtle, transparent)",margin:"var(--ds-space-050, 0.25rem) 0 0",transition:"background 0.3s cubic-bezier(0.15, 1, 0.3, 1), border-color 0.3s cubic-bezier(0.15, 1, 0.3, 1)",padding:"var(--ds-space-100, 8px)","td > :not(style):first-child, td > style:first-child + *":{marginTop:0},cursor:"pointer",boxSizing:"border-box","td > &":{marginTop:0},".ak-editor-expand__icon-container svg":{color:"var(--ds-icon-subtle, #626F86)",transform:"rotate(90deg)"},"&.ak-editor-selected-node:not(.danger)":{position:"relative","-webkit-user-select":"text","&::before":{position:"absolute",content:"''",left:0,right:0,top:0,bottom:0,width:"100%",pointerEvents:"none",zIndex:12,backgroundColor:"var(--ds-blanket-selected, #388BFF14)"},border:"1px solid var(--ds-border-selected, #0C66E4)","&::selection, *::selection":{backgroundColor:"transparent"},"&::-moz-selection, *::-moz-selection":{backgroundColor:"transparent"}},"&.danger":{background:"var(--ds-background-danger, #FFECEB)",borderColor:"var(--ds-border-danger, #E2483D)"}},".ProseMirror > .ak-editor-expand__type-expand, .fabric-editor-breakout-mark-dom > .ak-editor-expand__type-expand":{marginLeft:"-12px",marginRight:"-12px"},".ak-editor-expand__content":{paddingTop:"var(--ds-space-0, 0px)",paddingRight:"var(--ds-space-100, 8px)",paddingLeft:"var(--ds-space-300, 24px)",marginLeft:"var(--ds-space-050, 4px)",display:"flow-root","@supports not (display: flow-root)":{width:"100%",boxSizing:"border-box"},".expand-content-wrapper, .nestedExpand-content-wrapper":{width:"100%",display:"block",height:0,overflow:"hidden",clip:"rect(1px, 1px, 1px, 1px)",userSelect:"none"},cursor:"text"},".ak-editor-expand__title-input":{outline:"none",border:"none",fontSize:"calc(14rem / 16)",lineHeight:1.714,fontWeight:"var(--ds-font-weight-regular, 400)",color:"var(--ds-text-subtlest, #626F86)",background:"transparent",display:"flex",flex:1,padding:"0 0 0 var(--ds-space-050, 4px)",width:"100%","&::placeholder":{opacity:1,color:"var(--ds-text-subtlest, #626F86)"}},".ak-editor-expand__title-container":{padding:0,display:"flex",background:"none",border:"none",fontSize:"calc(14rem / 16)",width:"100%",color:"var(--ds-text-subtle, #44546F)",cursor:"pointer","&:focus":{outline:0},alignItems:"center",overflow:"visible"},".ak-editor-expand__expanded":{background:"var(--ds-background-neutral-subtle, #00000000)",borderColor:"var(--ds-border, #091E4224)",".ak-editor-expand__content":{paddingTop:"var(--ds-space-100, 8px)"}},".ak-editor-expand__input-container":{width:"100%"},".ak-editor-expand:not(.ak-editor-expand__expanded)":{".ak-editor-expand__content":{position:"absolute",height:"1px",width:"1px",overflow:"hidden",clip:"rect(1px, 1px, 1px, 1px)",whiteSpace:"nowrap"},".ak-editor-expand__icon-container svg":{color:"var(--ds-icon-subtle, #626F86)",transform:"rotate(0deg)"},"&:not(.ak-editor-selected-node):not(.danger)":{background:"transparent",borderColor:"transparent","&:hover":{borderColor:"var(--ds-border, #091E4224)",background:"var(--ds-background-neutral-subtle, #00000000)"}}}}),o=(0,n("3jLHL").css)({".ak-editor-expand__title-input":{lineHeight:1}}),i=(0,n("3jLHL").css)({".ak-editor-content-area.appearance-full-page .ProseMirror > .ak-editor-expand__type-expand, .fabric-editor-breakout-mark-dom > .ak-editor-expand__type-expand":{marginLeft:"-20px",marginRight:"-20px"},".ak-editor-expand__expanded":{".ak-editor-expand__content":{"> :nth-child(1 of :not(style, .ProseMirror-gapcursor, .ProseMirror-widget, span))":{marginTop:0},'> div.ak-editor-expand[data-node-type="nestedExpand"]':{marginTop:"var(--ds-space-050, 0.25rem)"}}}}),s=(0,n("3jLHL").css)({".ak-editor-expand":{"&.ak-editor-selected-node:not(.danger)":{"&::after":{height:"100%",content:"'\\00a0'",background:"var(--ds-border-selected, #0C66E4)",position:"absolute",right:"-1px",top:0,bottom:0,width:"1px",border:"none",display:"inline-block"}}}})}),i("lwlSB",function(t,r){e(t.exports,"extensionStyles",()=>a);let a=(0,n("3jLHL").css)({".multiBodiedExtensionView-content-wrap":{"&.danger > span > .multiBodiedExtension--container":{boxShadow:"0 0 0 1px var(--ds-border-danger, #E2483D)",backgroundColor:"var(--ds-background-danger, #FFECEB)"},"&.danger > span > div > .extension-label":{backgroundColor:"var(--ds-background-accent-red-subtler, #FFD5D2)",color:"var(--ds-text-danger, #AE2E24)",opacity:1,boxShadow:"none"},"&:not(.danger).ak-editor-selected-node > span > div > .extension-label":{backgroundColor:"var(--ds-background-selected, #E9F2FF)",color:"var(--ds-text-selected, #0C66E4)",opacity:1,boxShadow:"none"},"&.danger > span > div > .extension-label > span":{display:"inline"},"&:not(.danger).ak-editor-selected-node > span > div .extension-label > span":{display:"inline"},"&.danger.ak-editor-selected-node > span > .extension-edit-toggle-container":{opacity:1},"&:not(.danger).ak-editor-selected-node > span > .extension-edit-toggle-container":{opacity:1},"&.danger.ak-editor-selected-node > span > div > .extension-label.always-hide-label":{opacity:0},"&:not(.danger).ak-editor-selected-node > span > div > .extension-label.always-hide-label":{opacity:0},"&:not(.danger).ak-editor-selected-node > span > div > .extension-label.with-bodied-macro-live-page-styles":{boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4)"},"&.danger.ak-editor-selected-node > span > div > .extension-label.with-bodied-macro-live-page-styles":{boxShadow:"0 0 0 1px var(--ds-border-danger, #E2483D)"},"&.danger.ak-editor-selected-node > span > .extension-edit-toggle-container > .extension-edit-toggle":{backgroundColor:"var(--ds-background-accent-red-subtler, #FFD5D2)",color:"var(--ds-text-danger, #AE2E24)",boxShadow:"none"},"&.danger > span > .with-danger-overlay":{backgroundColor:"transparent",".multiBodiedExtension--overlay":{opacity:.3,backgroundColor:"var(--ds-background-danger-hovered, #FFD5D2)"}},"&:not(.danger).ak-editor-selected-node":{"& > span > .multiBodiedExtension--container":[n("45RBH").boxShadowSelectionStyles,n("45RBH").blanketSelectionStyles,n("45RBH").hideNativeBrowserTextSelectionStyles]},".multiBodiedExtension--container":{width:"100%",maxWidth:"100%"}},".inlineExtensionView-content-wrap":{"&.danger > span > .extension-container":{boxShadow:"0 0 0 1px var(--ds-border-danger, #E2483D)",backgroundColor:"var(--ds-background-danger, #FFECEB)"},"&.danger > span > .with-danger-overlay":{backgroundColor:"transparent",".extension-overlay":{opacity:.3,backgroundColor:"var(--ds-background-danger-hovered, #FFD5D2)"}},"&:not(.danger).ak-editor-selected-node":{"& > span > .extension-container":[n("45RBH").boxShadowSelectionStyles,n("45RBH").hideNativeBrowserTextSelectionStyles]},"&.danger > span > div > .extension-label":{backgroundColor:"var(--ds-background-accent-red-subtler, #FFD5D2)",color:"var(--ds-text-danger, #AE2E24)",opacity:1,boxShadow:"none"},"&:not(.danger).ak-editor-selected-node > span > div > .extension-label":{backgroundColor:"var(--ds-background-selected, #E9F2FF)",color:"var(--ds-text-selected, #0C66E4)",opacity:1,boxShadow:"none"},"&.danger > span > div > .extension-label > span":{display:"inline"},"&:not(.danger).ak-editor-selected-node > span > div .extension-label > span":{display:"inline"},"&.danger.ak-editor-selected-node > span > .extension-edit-toggle-container":{opacity:1},"&:not(.danger).ak-editor-selected-node > span > .extension-edit-toggle-container":{opacity:1},"&.danger.ak-editor-selected-node > span > div > .extension-label.always-hide-label":{opacity:0},"&:not(.danger).ak-editor-selected-node > span > div > .extension-label.always-hide-label":{opacity:0},"&:not(.danger).ak-editor-selected-node > span > div > .extension-label.with-bodied-macro-live-page-styles":{boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4)"},"&.danger.ak-editor-selected-node > span > div > .extension-label.with-bodied-macro-live-page-styles":{boxShadow:"0 0 0 1px var(--ds-border-danger, #E2483D)"},"&.danger.ak-editor-selected-node > span > .extension-edit-toggle-container > .extension-edit-toggle":{backgroundColor:"var(--ds-background-accent-red-subtler, #FFD5D2)",color:"var(--ds-text-danger, #AE2E24)",boxShadow:"none"}},".bodied-extension-to-dom-label::after":{content:"attr(data-bodied-extension-label)"},".extensionView-content-wrap, .multiBodiedExtensionView-content-wrap, .bodiedExtensionView-content-wrap":{margin:"0.75rem 0","&:first-of-type":{marginTop:0},"&:last-of-type":{marginBottom:0},"&:not(.danger).ak-editor-selected-node":{"& > span > .extension-container":[n("45RBH").boxShadowSelectionStyles,n("45RBH").hideNativeBrowserTextSelectionStyles]},"&.danger > span > .extension-container":{boxShadow:"0 0 0 1px var(--ds-border-danger, #E2483D)",backgroundColor:"var(--ds-background-danger, #FFECEB)"},"&.danger > span > div > .extension-label":{backgroundColor:"var(--ds-background-accent-red-subtler, #FFD5D2)",color:"var(--ds-text-danger, #AE2E24)",opacity:1,boxShadow:"none"},"&:not(.danger).ak-editor-selected-node > span > div > .extension-label":{backgroundColor:"var(--ds-background-selected, #E9F2FF)",color:"var(--ds-text-selected, #0C66E4)",opacity:1,boxShadow:"none"},"&.danger > span > div > .extension-label > span":{display:"inline"},"&:not(.danger).ak-editor-selected-node > span > div .extension-label > span":{display:"inline"},"&.danger.ak-editor-selected-node > span > .extension-edit-toggle-container":{opacity:1},"&:not(.danger).ak-editor-selected-node > span > .extension-edit-toggle-container":{opacity:1},"&.danger.ak-editor-selected-node > span > div > .extension-label.always-hide-label":{opacity:0},"&:not(.danger).ak-editor-selected-node > span > div > .extension-label.always-hide-label":{opacity:0},"&:not(.danger).ak-editor-selected-node > span > div > .extension-label.with-bodied-macro-live-page-styles":{boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4)"},"&.danger.ak-editor-selected-node > span > div > .extension-label.with-bodied-macro-live-page-styles":{boxShadow:"0 0 0 1px var(--ds-border-danger, #E2483D)"},"&.danger.ak-editor-selected-node > span > .extension-edit-toggle-container > .extension-edit-toggle":{backgroundColor:"var(--ds-background-accent-red-subtler, #FFD5D2)",color:"var(--ds-text-danger, #AE2E24)",boxShadow:"none"},"&.danger > span > .with-danger-overlay":{backgroundColor:"transparent",".extension-overlay":{opacity:.3,backgroundColor:"var(--ds-background-danger-hovered, #FFD5D2)"}},"&.inline":{}},".extensionView-content-wrap .extension-container":{overflow:"hidden","&:has(.extension-editable-area)":{overflow:"visible"}},".bodiedExtensionView-content-wrap .extensionView-content-wrap .extension-container":{width:"100%",maxWidth:"100%"},"[data-mark-type='fragment']":{"& > .extensionView-content-wrap, & > .bodiedExtensionView-content-wrap":{margin:"0.75rem 0"},"& > [data-mark-type='dataConsumer']":{"& > .extensionView-content-wrap, & > .bodiedExtensionView-content-wrap":{margin:"0.75rem 0"}},"&:first-child":{"& > .extensionView-content-wrap, & > .bodiedExtensionView-content-wrap":{marginTop:0},"& > [data-mark-type='dataConsumer']":{"& > .extensionView-content-wrap, & > .bodiedExtensionView-content-wrap":{marginTop:0}}},"&:nth-last-of-type(-n + 2):not(:first-of-type)":{"& > .extensionView-content-wrap, & > .bodiedExtensionView-content-wrap":{marginBottom:0},"& > [data-mark-type='dataConsumer']":{"& > .extensionView-content-wrap, & > .bodiedExtensionView-content-wrap":{marginBottom:0}}}}})}),i("4gNYY",function(t,r){e(t.exports,"findReplaceStyles",()=>a),e(t.exports,"findReplaceStylesNewYellow",()=>o),e(t.exports,"findReplaceStylesNewMagenta",()=>i);let a=(0,n("3jLHL").css)({".search-match":{borderRadius:"3px",backgroundColor:"var(--ds-background-accent-teal-subtlest, #E7F9FF)",boxShadow:"var(--ds-shadow-raised, 0 1px 1px 0 rgba(9, 30, 66, 0.25), 0 0 1px 0 rgba(9, 30, 66, 0.31)), inset 0 0 0 1px var(--ds-border-input, #8590A2)"},".selected-search-match":{backgroundColor:"var(--ds-background-accent-teal-subtle, #6CC3E0)"}}),o=(0,n("3jLHL").css)({".search-match-text":{borderRadius:"var(--ds-space-050, 4px)",boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-yellow-subtler-pressed, #E2B203),
		inset 0 0 0 5px var(--ds-background-accent-yellow-subtler, #F8E6A0)
		`,backgroundColor:"var(--ds-background-accent-yellow-subtler, #F8E6A0) !important",color:"var(--ds-text, #172B4D)"},".search-match-text.selected-search-match":{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-yellow-subtler-pressed, #E2B203),
		inset 0 0 0 5px var(--ds-background-accent-yellow-subtlest-pressed, #F5CD47)
		`,backgroundColor:"var(--ds-background-accent-yellow-subtlest-pressed, #F5CD47) !important"},".search-match-text.search-match-dark":{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-yellow-bolder, #946F00),
		inset 0 0 0 5px var(--ds-background-accent-yellow-bolder-pressed, #533F04)
		`,backgroundColor:"var(--ds-background-accent-yellow-bolder-pressed, #533F04) !important",color:"var(--ds-text-inverse, #FFFFFF)"},".search-match-text.selected-search-match.search-match-dark":{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-yellow-bolder, #946F00),
		inset 0 0 0 5px var(--ds-background-accent-yellow-bolder-hovered, #7F5F01)
		`,backgroundColor:"var(--ds-background-accent-yellow-bolder-hovered, #7F5F01) !important"},".search-match-block":{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-yellow-subtler-pressed, #E2B203),
			inset 0 0 0 5px var(--ds-background-accent-yellow-subtler, #F8E6A0)
			`},".loader-wrapper>a, .lozenge-wrapper, .editor-mention-primitive, .date-lozenger-container>span":{boxShadow:"0px 0px 0px 4px var(--ds-background-accent-yellow-subtler, #F8E6A0), 0px 0px 0px 5px var(--ds-background-accent-yellow-subtler-pressed, #E2B203)"}},".search-match-block.search-match-block-selected":{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-yellow-subtler-pressed, #E2B203),
			inset 0 0 0 4px var(--ds-background-accent-yellow-subtlest-pressed, #F5CD47)
			`},".loader-wrapper>a, .lozenge-wrapper, .editor-mention-primitive, .date-lozenger-container>span":{boxShadow:"0px 0px 0px 4px var(--ds-background-accent-yellow-subtlest-pressed, #F5CD47), 0px 0px 0px 5px var(--ds-background-accent-yellow-subtler-pressed, #E2B203)"}},".search-match-block.ak-editor-selected-node":{".loader-wrapper>div::after":{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-yellow-subtler-pressed, #E2B203),
			inset 0 0 0 5px var(--ds-background-accent-yellow-subtler, #F8E6A0),
			0 0 0 1px var(--ds-border-selected, #0C66E4)
			`},".loader-wrapper>a, .lozenge-wrapper, .editor-mention-primitive, .date-lozenger-container>span":{boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4), 0px 0px 0px 4px var(--ds-background-accent-yellow-subtler, #F8E6A0), 0px 0px 0px 5px var(--ds-background-accent-yellow-subtler-pressed, #E2B203) !important"}},".search-match-block.search-match-block-selected.ak-editor-selected-node":{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-yellow-subtler-pressed, #E2B203),
			inset 0 0 0 4px var(--ds-background-accent-yellow-subtlest-pressed, #F5CD47),
			0 0 0 1px var(--ds-border-selected, #0C66E4)
			`},".loader-wrapper>a, .lozenge-wrapper, .editor-mention-primitive, .date-lozenger-container>span":{boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4), 0px 0px 0px 4px var(--ds-background-accent-yellow-subtlest-pressed, #F5CD47), 0px 0px 0px 5px var(--ds-background-accent-yellow-subtler-pressed, #E2B203) !important"}},".search-match-block.search-match-dark":{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-yellow-bolder, #946F00),
			inset 0 0 0 5px var(--ds-background-accent-yellow-bolder-pressed, #533F04)
			`},".loader-wrapper>a, .lozenge-wrapper, .editor-mention-primitive, .date-lozenger-container>span":{boxShadow:"0px 0px 0px 4px var(--ds-background-accent-yellow-bolder-pressed, #533F04), 0px 0px 0px 5px var(--ds-background-accent-yellow-bolder, #946F00)"}},".search-match-block.search-match-block-selected.search-match-dark":{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-yellow-bolder, #946F00),
			inset 0 0 0 4px var(--ds-background-accent-yellow-bolder-hovered, #7F5F01)
			`},".loader-wrapper>a, .lozenge-wrapper, .editor-mention-primitive, .date-lozenger-container>span":{boxShadow:"0px 0px 0px 4px var(--ds-background-accent-yellow-bolder-hovered, #7F5F01), 0px 0px 0px 5px var(--ds-background-accent-yellow-bolder, #946F00)"}},".search-match-block.search-match-dark.ak-editor-selected-node":{".loader-wrapper>div::after":{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-yellow-bolder, #946F00),
			inset 0 0 0 5px var(--ds-background-accent-yellow-bolder-pressed, #533F04),
			0 0 0 1px var(--ds-border-selected, #0C66E4)
			`},".loader-wrapper>a, .lozenge-wrapper, .editor-mention-primitive, .date-lozenger-container>span":{boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4), 0px 0px 0px 4px var(--ds-background-accent-yellow-bolder-pressed, #533F04), 0px 0px 0px 5px var(--ds-background-accent-yellow-bolder, #946F00) !important"}},".search-match-block.search-match-block-selected.search-match-dark.ak-editor-selected-node":{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-yellow-bolder, #946F00),
			inset 0 0 0 4px var(--ds-background-accent-yellow-bolder-hovered, #7F5F01),
			0 0 0 1px var(--ds-border-selected, #0C66E4)
			`},".loader-wrapper>a, .lozenge-wrapper, .editor-mention-primitive, .date-lozenger-container>span":{boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4), 0px 0px 0px 4px var(--ds-background-accent-yellow-bolder-hovered, #7F5F01), 0px 0px 0px 5px var(--ds-background-accent-yellow-bolder, #946F00) !important"}},".search-match-expand-title > .ak-editor-expand__title-container > .ak-editor-expand__input-container":{borderRadius:"var(--ds-space-050, 4px)",boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-yellow-subtler-pressed, #E2B203),
		inset 0 0 0 5px var(--ds-background-accent-yellow-subtler, #F8E6A0)
		`,backgroundColor:"var(--ds-background-accent-yellow-subtler, #F8E6A0)",".ak-editor-expand__title-input":{color:"var(--ds-text, #172B4D)"}},".search-match-expand-title.selected-search-match > .ak-editor-expand__title-container > .ak-editor-expand__input-container":{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-yellow-subtler-pressed, #E2B203),
		inset 0 0 0 5px var(--ds-background-accent-yellow-subtlest-pressed, #F5CD47)
		`,backgroundColor:"var(--ds-background-accent-yellow-subtlest-pressed, #F5CD47)"},".search-match-expand-title.search-match-dark > .ak-editor-expand__title-container > .ak-editor-expand__input-container":{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-yellow-bolder, #946F00),
		inset 0 0 0 5px var(--ds-background-accent-yellow-bolder-pressed, #533F04)
		`,backgroundColor:"var(--ds-background-accent-yellow-bolder-pressed, #533F04)",".ak-editor-expand__title-input":{color:"var(--ds-text-inverse, #FFFFFF)"}},".search-match-expand-title.selected-search-match.search-match-dark > .ak-editor-expand__title-container > .ak-editor-expand__input-container":{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-yellow-bolder, #946F00),
		inset 0 0 0 5px var(--ds-background-accent-yellow-bolder-hovered, #7F5F01)
		`,backgroundColor:"var(--ds-background-accent-yellow-bolder-hovered, #7F5F01)"}}),i=(0,n("3jLHL").css)({".search-match-text":{borderRadius:"var(--ds-space-050, 4px)",boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-magenta-subtler-pressed, #E774BB),
		inset 0 0 0 5px var(--ds-background-accent-magenta-subtler, #FDD0EC)
		`,backgroundColor:"var(--ds-background-accent-magenta-subtler, #FDD0EC) !important",color:"var(--ds-text, #172B4D)"},".search-match-text.selected-search-match":{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-magenta-subtler-pressed, #E774BB),
		inset 0 0 0 5px var(--ds-background-accent-magenta-subtlest-pressed, #F797D2)
		`,backgroundColor:"var(--ds-background-accent-magenta-subtlest-pressed, #F797D2) !important"},".search-match-text.search-match-dark":{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-magenta-bolder, #AE4787),
		inset 0 0 0 5px var(--ds-background-accent-magenta-bolder-pressed, #50253F)
		`,backgroundColor:"var(--ds-background-accent-magenta-bolder-pressed, #50253F) !important",color:"var(--ds-text-inverse, #FFFFFF)"},".search-match-text.selected-search-match.search-match-dark":{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-magenta-bolder, #AE4787),
		inset 0 0 0 5px var(--ds-background-accent-magenta-bolder-hovered, #943D73)
		`,backgroundColor:"var(--ds-background-accent-magenta-bolder-hovered, #943D73) !important"},".search-match-block":{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-magenta-subtler-pressed, #E774BB),
			inset 0 0 0 5px var(--ds-background-accent-magenta-subtler, #FDD0EC)
			`},".loader-wrapper>a, .lozenge-wrapper, .editor-mention-primitive, .date-lozenger-container>span":{boxShadow:"0px 0px 0px 4px var(--ds-background-accent-magenta-subtler, #FDD0EC), 0px 0px 0px 5px var(--ds-background-accent-magenta-subtler-pressed, #E774BB)"}},".search-match-block.search-match-block-selected":{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-magenta-subtler-pressed, #E774BB),
			inset 0 0 0 4px var(--ds-background-accent-magenta-subtlest-pressed, #F797D2)
			`},".loader-wrapper>a, .lozenge-wrapper, .editor-mention-primitive, .date-lozenger-container>span":{boxShadow:"0px 0px 0px 4px var(--ds-background-accent-magenta-subtlest-pressed, #F797D2), 0px 0px 0px 5px var(--ds-background-accent-magenta-subtler-pressed, #E774BB)"}},".search-match-block.ak-editor-selected-node":{".loader-wrapper>div::after":{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-magenta-subtler-pressed, #E774BB),
			inset 0 0 0 5px var(--ds-background-accent-magenta-subtler, #FDD0EC),
			0 0 0 1px var(--ds-border-selected, #0C66E4)
			`},".loader-wrapper>a, .lozenge-wrapper, .editor-mention-primitive, .date-lozenger-container>span":{boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4), 0px 0px 0px 4px var(--ds-background-accent-magenta-subtler, #FDD0EC), 0px 0px 0px 5px var(--ds-background-accent-magenta-subtler-pressed, #E774BB) !important"}},".search-match-block.search-match-block-selected.ak-editor-selected-node":{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-magenta-subtler-pressed, #E774BB),
			inset 0 0 0 4px var(--ds-background-accent-magenta-subtlest-pressed, #F797D2),
			0 0 0 1px var(--ds-border-selected, #0C66E4)
			`},".loader-wrapper>a, .lozenge-wrapper, .editor-mention-primitive, .date-lozenger-container>span":{boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4), 0px 0px 0px 4px var(--ds-background-accent-magenta-subtlest-pressed, #F797D2), 0px 0px 0px 5px var(--ds-background-accent-magenta-subtler-pressed, #E774BB) !important"}},".search-match-block.search-match-dark":{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-magenta-bolder, #AE4787),
			inset 0 0 0 5px var(--ds-background-accent-magenta-bolder-pressed, #50253F)
			`},".loader-wrapper>a, .lozenge-wrapper, .editor-mention-primitive, .date-lozenger-container>span":{boxShadow:"0px 0px 0px 4px var(--ds-background-accent-magenta-bolder-pressed, #50253F), 0px 0px 0px 5px var(--ds-background-accent-magenta-bolder, #AE4787)"}},".search-match-block.search-match-block-selected.search-match-dark":{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-magenta-bolder, #AE4787),
			inset 0 0 0 4px var(--ds-background-accent-magenta-bolder-hovered, #943D73)
			`},".loader-wrapper>a, .lozenge-wrapper, .editor-mention-primitive, .date-lozenger-container>span":{boxShadow:"0px 0px 0px 4px var(--ds-background-accent-magenta-bolder-hovered, #943D73), 0px 0px 0px 5px var(--ds-background-accent-magenta-bolder, #AE4787)"}},".search-match-block.search-match-dark.ak-editor-selected-node":{".loader-wrapper>div::after":{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-magenta-bolder, #AE4787),
			inset 0 0 0 5px var(--ds-background-accent-magenta-bolder-pressed, #50253F),
			0 0 0 1px var(--ds-border-selected, #0C66E4)
			`},".loader-wrapper>a, .lozenge-wrapper, .editor-mention-primitive, .date-lozenger-container>span":{boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4), 0px 0px 0px 4px var(--ds-background-accent-magenta-bolder-pressed, #50253F), 0px 0px 0px 5px var(--ds-background-accent-magenta-bolder, #AE4787) !important"}},".search-match-block.search-match-block-selected.search-match-dark.ak-editor-selected-node":{'[data-smart-link-container="true"], .loader-wrapper>div::after':{boxShadow:`
			inset 0 0 0 1px var(--ds-background-accent-magenta-bolder, #AE4787),
			inset 0 0 0 4px var(--ds-background-accent-magenta-bolder-hovered, #943D73),
			0 0 0 1px var(--ds-border-selected, #0C66E4)
			`},".loader-wrapper>a, .lozenge-wrapper, .editor-mention-primitive, .date-lozenger-container>span":{boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4), 0px 0px 0px 4px var(--ds-background-accent-magenta-bolder-hovered, #943D73), 0px 0px 0px 5px var(--ds-background-accent-magenta-bolder, #AE4787) !important"}},".search-match-expand-title > .ak-editor-expand__title-container > .ak-editor-expand__input-container":{borderRadius:"var(--ds-space-050, 4px)",boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-magenta-subtler-pressed, #E774BB),
		inset 0 0 0 5px var(--ds-background-accent-magenta-subtler, #FDD0EC)
		`,backgroundColor:"var(--ds-background-accent-magenta-subtler, #FDD0EC)",".ak-editor-expand__title-input":{color:"var(--ds-text, #172B4D)"}},".search-match-expand-title.selected-search-match > .ak-editor-expand__title-container > .ak-editor-expand__input-container":{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-magenta-subtler-pressed, #E774BB),
		inset 0 0 0 5px var(--ds-background-accent-magenta-subtlest-pressed, #F797D2)
		`,backgroundColor:"var(--ds-background-accent-magenta-subtlest-pressed, #F797D2)"},".search-match-expand-title.search-match-dark > .ak-editor-expand__title-container > .ak-editor-expand__input-container":{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-magenta-bolder, #AE4787),
		inset 0 0 0 5px var(--ds-background-accent-magenta-bolder-pressed, #50253F)
		`,backgroundColor:"var(--ds-background-accent-magenta-bolder-pressed, #50253F)",".ak-editor-expand__title-input":{color:"var(--ds-text-inverse, #FFFFFF)"}},".search-match-expand-title.selected-search-match.search-match-dark > .ak-editor-expand__title-container > .ak-editor-expand__input-container":{boxShadow:`
		inset 0 0 0 1px var(--ds-background-accent-magenta-bolder, #AE4787),
		inset 0 0 0 5px var(--ds-background-accent-magenta-bolder-hovered, #943D73)
		`,backgroundColor:"var(--ds-background-accent-magenta-bolder-hovered, #943D73)"}})}),i("1wqVI",function(t,r){e(t.exports,"firstBlockNodeStyles",()=>a);let a=(0,n("3jLHL").css)({".ProseMirror":{[`> .${n("DoNsZ").PanelSharedCssClassName.prefix}, > .${n("4JzGQ").CodeBlockSharedCssClassName.CODEBLOCK_CONTAINER}, > .${n("cV5SN").SmartCardSharedCssClassName.BLOCK_CARD_CONTAINER}, > div[data-task-list-local-id], > div[data-layout-section], > .${n("iMS6j").expandClassNames.prefix}`]:{"&:first-child":{marginTop:0}},"> hr:first-child, > .ProseMirror-widget:first-child + hr":{marginTop:0}}})}),i("9PdTF",function(t,r){e(t.exports,"firstFloatingToolbarButtonStyles",()=>a);let a=(0,n("3jLHL").css)({"button.first-floating-toolbar-button:focus":{outline:"2px solid var(--ds-border-focused, #388BFF)"}})}),i("hRSb9",function(t,r){e(t.exports,"fullPageEditorStyles",()=>a);let a=(0,n("3jLHL").css)({flexGrow:1,height:"100%",overflowY:"scroll",position:"relative",display:"flex",flexDirection:"column",scrollBehavior:"smooth"})}),i("3wjeF",function(t,r){e(t.exports,"gapCursorStyles",()=>g);let a=(0,n("3jLHL").keyframes)({"from, to":{opacity:0},"50%":{opacity:1}}),o=".ProseMirror-gapcursor",i='.ProseMirror-widget:not([data-blocks-decoration-container="true"]):not([data-blocks-drag-handle-container="true"]):not([data-blocks-quick-insert-container="true"])',s='[layout="wrap-left"]',d='[layout="wrap-right"]',l=`
	&:first-of-type + ul,
	&:first-of-type + span + ul,
	&:first-of-type + ol,
	&:first-of-type + span + ol,
	&:first-of-type + pre,
	&:first-of-type + span + pre,
	&:first-of-type + blockquote,
	&:first-of-type + span + blockquote
`,c=`
  ${o}${s} + span + ${s},
  ${o}${d} + span + ${d},
  ${o} + ${s} + ${d},
  ${o} + ${s} + span + ${d},
  ${o} + ${d} + ${s},
  ${o} + ${d} + span + ${s},
  ${s} + ${o} + ${d},
  ${s} + ${o} + span ${d},
  ${d} + ${o} + ${s},
  ${d} + ${o} + span + ${s},
  ${s} + ${o}`,p=`
  ${s} + ${o} + ${d} > div,
  ${s} + ${o} + span + ${d} > div,
  ${d} + ${o} + ${s} > div,
  ${d} + ${o} + span + ${s} > div,
  ${o} + ${d} + ${s} > div,
  ${o} + ${d} + span + ${s} > div,
  ${o} + ${s} + ${d} > div,
  ${o} + ${s} + span + ${d} > div`,u=`
  ${s} + ${o},
  ${d} + ${o}`,m=`
  ${o} + ${s} + span + ${d}::after,
  ${o} + ${d} + span + ${s}::after,
  ${s} + ${o} + ${d}::after,
  ${s} + ${o} + span + ${d}::after,
  ${d} + ${o} + ${s}::after,
  ${d} + ${o} + span + ${s}::after`,h=`
${s} + ${o} + ${d} + *,
  ${s} + ${o} + ${d} + span + *,
  ${d} + ${o} + ${s} + *,
  ${d} + ${o} + ${s} + span + *,
  ${s} + ${o} + span + ${d} + *,
  ${d} + ${o} + span + ${s} + *,
  ${o} + ${s} + span + ${d} + *,
  ${o} + ${d} + span + ${s} + *,
  ${s} + ${o} + ${d} + * > *,
  ${s} + ${o} + ${d} + span + * > *,
  ${d} + ${o} + ${s} + * > *,
  ${d} + ${o} + ${s} + span + * > *,
  ${s} + ${o} + span + ${d} + * > *,
  ${d} + ${o} + span + ${s} + * > *,
  ${o} + ${s} + span + ${d} + * > *,
  ${o} + ${d} + span + ${s} + * > *,
  ${i} + ${o} + *,
  ${i} + ${o} + span + *`,g=(0,n("3jLHL").css)({".ProseMirror":{"&.ProseMirror-hide-gapcursor":{caretColor:"transparent"},[o]:{display:"none",pointerEvents:"none",position:"relative","& span":{caretColor:"transparent",position:"absolute",height:"100%",width:"100%",display:"block"},"& span::after":{animation:`1s ${a} step-start infinite`,borderLeft:"1px solid",content:"''",display:"block",position:"absolute",top:0,height:"100%"},"&.-left span::after":{left:"var(--ds-space-negative-050, -4px)"},"&.-right span::after":{right:"var(--ds-space-negative-050, -4px)"},'& span[layout="full-width"], & span[layout="wide"], & span[layout="fixed-width"]':{marginLeft:"50%",transform:"translateX(-50%)"},[`&${d}`]:{float:"right"},[l]:{marginTop:0}},[`&.ProseMirror-focused ${o}`]:{display:"block",borderColor:"transparent"}},[c]:{clear:"none"},[p]:{marginRight:0,marginLeft:0,marginBottom:0},[u]:{float:"left"},[m]:{visibility:"hidden",display:"block",fontSize:0,content:"' '",clear:"both",height:0},[h]:{marginTop:0}})}),i("4fO6z",function(t,r){e(t.exports,"gridStyles",()=>a);let a=(0,n("3jLHL").css)({".gridParent":{width:"calc(100% + 24px)",marginLeft:"var(--ds-space-negative-150, -12px)",marginRight:"var(--ds-space-negative-150, -12px)",transform:"scale(1)",zIndex:2},".gridContainer":{position:"fixed",height:"100vh",width:"100%",pointerEvents:"none"},".gridLine":{borderLeft:"1px solid var(--ds-border, #091E4224)",display:"inline-block",boxSizing:"border-box",height:"100%",marginLeft:"-1px",transition:"border-color 0.15s linear",zIndex:0},".highlight":{borderLeft:"1px solid var(--ds-border-focused, #388BFF)"}})}),i("lk33U",function(t,r){e(t.exports,"indentationStyles",()=>a);let a=(0,n("3jLHL").css)({".ProseMirror":{".fabric-editor-indentation-mark":{"&[data-level='1']":{marginLeft:30},"&[data-level='2']":{marginLeft:60},"&[data-level='3']":{marginLeft:90},"&[data-level='4']":{marginLeft:120},"&[data-level='5']":{marginLeft:150},"&[data-level='6']":{marginLeft:180}}}})}),i("dIjG1",function(t,r){e(t.exports,"InlineNodeViewSharedStyles",()=>a);let a=(0,n("3jLHL").css)({".ProseMirror":{".inlineNodeView":{display:"inline",userSelect:"all",whiteSpace:"nowrap","& > *:not(.zeroWidthSpaceContainer)":{whiteSpace:"pre-wrap"},"& > .assistive":{userSelect:"none"}},"&.ua-safari":{".inlineNodeView":{"&::selection, *::selection":{background:"transparent"}}},"&.ua-chrome .inlineNodeView > span":{userSelect:"none"},".inlineNodeViewAddZeroWidthSpace":{"&::after":{content:"'​'"}}}})}),i("cO7tu",function(t,r){e(t.exports,"layoutColumnStylesAdvanced",()=>c),e(t.exports,"layoutColumnStylesNotAdvanced",()=>p),e(t.exports,"layoutColumnResponsiveStyles",()=>u),e(t.exports,"layoutSectionStylesAdvanced",()=>m),e(t.exports,"layoutSectionStylesNotAdvanced",()=>h),e(t.exports,"layoutSelectedStylesNotAdvanced",()=>g),e(t.exports,"layoutSelectedStylesAdvanced",()=>f),e(t.exports,"layoutResponsiveBaseStyles",()=>x),e(t.exports,"layoutResponsiveStylesForView",()=>v),e(t.exports,"layoutBaseStyles",()=>y),e(t.exports,"layoutBaseStylesAdvanced",()=>E),e(t.exports,"layoutBaseStylesFixesUnderNestedDnDFG",()=>S),e(t.exports,"layoutSelectedStylesForViewAdvanced",()=>C),e(t.exports,"layoutSelectedStylesForViewNotAdvanced",()=>k),e(t.exports,"layoutStylesForView",()=>T),e(t.exports,"layoutColumnMartinTopFixesNew",()=>w),e(t.exports,"layoutColumnMartinTopFixesOld",()=>_);let a="ak-editor-selected-node",o=".fabric-editor--full-width-mode .ProseMirror > .layoutSectionView-content-wrap",i=".ak-editor-content-area:not(.fabric-editor--full-width-mode) .ProseMirror > .layoutSectionView-content-wrap",s=".ProseMirror .fabric-editor-breakout-mark .layoutSectionView-content-wrap",d=`&.selected, &:hover, &.selected.danger, &.${a}:not(.danger)`,l=`&.selected, [data-empty-layout='true'], &:hover, &.selected.danger [data-layout-section], &.${a}:not(.danger) [data-layout-section]`,c=(0,n("3jLHL").css)({".ProseMirror [data-layout-section]":{"> [data-layout-column]":{margin:"0 4px"},"> [data-layout-column]:first-of-type":{marginLeft:0},"> [data-layout-column]:last-of-type":{marginRight:0},"@media screen and (max-width: 1024px)":{"[data-layout-column] + [data-layout-column]":{margin:0}},[`> [data-layout-column].${a}:not(.danger)`]:[n("45RBH").blanketSelectionStyles,n("45RBH").hideNativeBrowserTextSelectionStyles,{"::before":{width:"calc(100% - 8px)",left:4,borderRadius:"var(--ds-border-radius, 3px)"}}]}}),p=(0,n("3jLHL").css)({".ProseMirror [data-layout-section]":{"[data-layout-column] + [data-layout-column]":{marginLeft:8},"@media screen and (max-width: 1024px)":{"[data-layout-column] + [data-layout-column]":{marginLeft:0}}}}),u=(0,n("3jLHL").css)({".ProseMirror [data-layout-section]":{display:"flex",flexDirection:"row",gap:"var(--ds-space-100, 8px)","& > *":{flex:1,minWidth:0},"& > .unsupportedBlockView-content-wrap":{minWidth:"initial"}},".layout-section-container":{containerType:"inline-size",containerName:"layout-area"}}),m=(0,n("3jLHL").css)({".ProseMirror .layout-section-container [data-layout-section]":{"> .ProseMirror-widget":{flex:"none",display:"contents !important","&[data-blocks-drag-handle-container] div":{display:"contents !important"},"&[data-blocks-drop-target-container]":{display:"block !important",margin:"var(--ds-space-negative-050, -4px)","[data-drop-target-for-element]":{position:"absolute"}},"& + [data-layout-column]":{margin:0}},"> [data-layout-column]":{margin:0}}}),h=(0,n("3jLHL").css)({".ProseMirror [data-layout-section]":{position:"relative",display:"flex",flexDirection:"row","& > *":{flex:1,minWidth:0},"& > .unsupportedBlockView-content-wrap":{minWidth:"initial"},"@media screen and (max-width: 1024px)":{flexDirection:"column"}}}),g=(0,n("3jLHL").css)({".ProseMirror":{"[data-layout-section], .layoutSectionView-content-wrap":{"&.selected [data-layout-column], &:hover [data-layout-column]":{border:"1px solid var(--ds-border, #091E4224)"},"&.selected.danger [data-layout-column]":{backgroundColor:"var(--ds-background-danger, #FFECEB)",borderColor:"var(--ds-border-danger, #E2483D)"},[`&.${a}:not(.danger)`]:{"[data-layout-column]":[n("45RBH").borderSelectionStyles,n("45RBH").blanketSelectionStyles,n("45RBH").hideNativeBrowserTextSelectionStyles,{"::after":{backgroundColor:"transparent"}}]}}}}),b=(0,n("3jLHL").css)({"[data-layout-content]::before":{content:"''",borderTop:"1px solid var(--ds-border, #091E4224)",position:"absolute",width:"calc(100% - 32px)",marginTop:-13,borderLeft:"unset",marginLeft:"unset",height:"unset"}}),f=(0,n("3jLHL").css)({".ProseMirror":{"[data-layout-section], .layoutSectionView-content-wrap":{[l]:{"[data-layout-column]:not(:first-of-type) [data-layout-content]::before":{content:"''",borderLeft:"1px solid var(--ds-border, #091E4224)",position:"absolute",height:"calc(100% - 24px)",marginLeft:-25}},"&.selected.danger [data-layout-section]":{backgroundColor:"var(--ds-background-danger, #FFECEB)",boxShadow:"0 0 0 1px var(--ds-border-danger, #E2483D)",borderRadius:4},[`&.${a}:not(.danger) [data-layout-section]`]:{boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4)",borderRadius:4,backgroundColor:"var(--ds-background-selected, #E9F2FF)","[data-layout-column]":[n("45RBH").blanketSelectionStyles,n("45RBH").hideNativeBrowserTextSelectionStyles,{border:0,"::before":{backgroundColor:"transparent"}}]}}}}),x=(0,n("3jLHL").css)({[o]:{"[data-layout-section]":{"@container editor-area (max-width:724px)":{flexDirection:"column"}},[d]:{"[data-layout-column]:not(:first-of-type)":{"@container editor-area (max-width:724px)":b}}},[i]:{"[data-layout-section]":{"@container editor-area (max-width:788px)":{flexDirection:"column"}},[d]:{"[data-layout-column]:not(:first-of-type)":{"@container editor-area (max-width:788px)":b}}},[s]:{"[data-layout-section]":{"@container editor-area (max-width:820px)":{flexDirection:"column"}},[d]:{"[data-layout-column]:not(:first-of-type)":{"@container editor-area (max-width:820px)":b}}}}),v=(0,n("3jLHL").css)({[o]:{[d]:{"[data-layout-column]:not(:first-of-type)":{"@container editor-area (max-width:724px)":{"[data-layout-content]::before":{borderTop:0}}}}},[i]:{[d]:{"[data-layout-column]:not(:first-of-type)":{"@container editor-area (max-width:788px)":{"[data-layout-content]::before":{borderTop:0}}}}},[s]:{[d]:{"[data-layout-column]:not(:first-of-type)":{"@container editor-area (max-width:820px)":{"[data-layout-content]::before":{borderTop:0}}}}}}),y=(0,n("3jLHL").css)({".ProseMirror":{"[data-layout-section]":{margin:"var(--ds-space-100, 8px) -12px 0",transition:"border-color 0.3s cubic-bezier(0.15, 1, 0.3, 1)",cursor:"pointer","[data-layout-column]":{flex:1,position:"relative",minWidth:0,border:"1px solid var(--ds-border, #091E4224)",borderRadius:4,padding:"var(--ds-space-150, 12px)",boxSizing:"border-box","> div":{"> .embedCardView-content-wrap:first-of-type .rich-media-item":{marginTop:0},"> .mediaSingleView-content-wrap:first-of-type .rich-media-item":{marginTop:0},"> .ProseMirror-gapcursor.-right:first-child + .mediaSingleView-content-wrap .rich-media-item, > style:first-child + .ProseMirror-gapcursor.-right + .mediaSingleView-content-wrap .rich-media-item, > .ProseMirror-gapcursor.-right:first-of-type + .embedCardView-content-wrap .rich-media-item":{marginTop:0},"> .ProseMirror-gapcursor:first-child + span + .mediaSingleView-content-wrap .rich-media-item, > style:first-child + .ProseMirror-gapcursor + span + .mediaSingleView-content-wrap .rich-media-item":{marginTop:0},"> [data-node-type='decisionList']":{"li:first-of-type [data-decision-wrapper]":{marginTop:0}}},"[data-layout-content]":{height:"100%",cursor:"text",".mediaGroupView-content-wrap":{clear:"both"}}}}},"[data-blocks-drop-target-container] ~ [data-layout-column] > [data-layout-content]::before":{display:"none"},".fabric-editor--full-width-mode .ProseMirror":{"[data-layout-section]":{".pm-table-container":{margin:"0 2px"}}}}),E=(0,n("3jLHL").css)({".ProseMirror [data-layout-section] [data-layout-column]":{border:0}}),S=(0,n("3jLHL").css)({".ProseMirror [data-layout-section]":{margin:"var(--ds-space-100, 8px) -20px 0"},".ProseMirror [data-layout-section] [data-layout-column]":{padding:"12px 20px"}}),C=(0,n("3jLHL").css)({".ProseMirror":{"[data-layout-section], .layoutSectionView-content-wrap":{[l]:{"[data-layout-column]:not(:first-of-type) [data-layout-content]::before":{borderLeft:0}},"&.selected.danger [data-layout-section]":{boxShadow:"0 0 0 0 var(--ds-border-danger, #E2483D)"},[`&.${a}:not(.danger) [data-layout-section]`]:{boxShadow:"0 0 0 0 var(--ds-border-selected, #0C66E4)"}}}}),k=(0,n("3jLHL").css)({".ProseMirror":{"[data-layout-section], .layoutSectionView-content-wrap":{"&.selected [data-layout-column], &:hover [data-layout-column]":{border:0}}}}),T=(0,n("3jLHL").css)({".ProseMirror":{"[data-layout-section]":{cursor:"default","[data-layout-column]":{border:0}}}}),w=(0,n("3jLHL").css)({".ProseMirror [data-layout-section] [data-layout-column] > div":{"> :nth-child(1 of :not(style, .ProseMirror-gapcursor, .ProseMirror-widget, span))":{marginTop:0}}}),_=(0,n("3jLHL").css)({".ProseMirror [data-layout-section] [data-layout-column] > div":{"> :not(style):first-child, > style:first-child + *":{marginTop:0},"> .ProseMirror-gapcursor:first-child + *, > style:first-child + .ProseMirror-gapcursor + *":{marginTop:0},"> .ProseMirror-gapcursor:first-child + span + *":{marginTop:0}}})}),i("432pP",function(t,r){e(t.exports,"linkStyles",()=>a),e(t.exports,"linkStylesOld",()=>o),e(t.exports,"hyperLinkFloatingToolbarStyles",()=>i),e(t.exports,"linkLegacyIconStylesFix",()=>s);let a=(0,n("3jLHL").css)({".ProseMirror a.blockLink":{display:"block"},'.ProseMirror a[data-prosemirror-mark-name="link"]':{textDecoration:"underline"},'.ProseMirror a[data-prosemirror-mark-name="link"]:hover':{textDecoration:"none"}}),o=(0,n("3jLHL").css)({".ProseMirror a.blockLink":{display:"block"}}),i=(0,n("3jLHL").css)({".hyperlink-floating-toolbar":{padding:0}}),s=(0,n("3jLHL").css)({".hyperlink-open-link":{minWidth:24,svg:{maxWidth:18}}})}),i("2Iy63",function(t,r){e(t.exports,"listsStyles",()=>o),e(t.exports,"listsStylesSafariFix",()=>i);let a="blockCardView-content-wrap",o=(0,n("3jLHL").css)({".ProseMirror":{"ul, ol":{boxSizing:"border-box",paddingLeft:"var(--ed--list--item-counter--padding, 24px)"},"&.ua-firefox":{"ul, ol":{"li p:empty, li p > span:empty":{display:"inline-block"}}},".ak-ol, .ak-ul":{display:"flow-root"},"ul, ul ul ul ul":{listStyleType:"disc"},"ul ul, ul ul ul ul ul":{listStyleType:"circle"},"ul ul ul, ul ul ul ul ul ul":{listStyleType:"square"},"ol, ol ol ol ol":{listStyleType:"decimal"},"ol ol, ol ol ol ol ol":{listStyleType:"lower-alpha"},"ol ol ol, ol ol ol ol ol ol":{listStyleType:"lower-roman"},"ol[data-indent-level='1'], ol[data-indent-level='4']":{listStyleType:"decimal"},"ol[data-indent-level='2'], ol[data-indent-level='5']":{listStyleType:"lower-alpha"},"ol[data-indent-level='3'], ol[data-indent-level='6']":{listStyleType:"lower-roman"},"ul[data-indent-level='1'], ul[data-indent-level='4']":{listStyleType:"disc"},"ul[data-indent-level='2'], ul[data-indent-level='5']":{listStyleType:"circle"},"ul[data-indent-level='3'], ul[data-indent-level='6']":{listStyleType:"square"},li:{position:"relative","& > p:not(:first-child)":{margin:"var(--ds-space-050, 4px) 0 0 0"},"& > style:first-child + p":{marginTop:"0.75rem"}}}}),i=(0,n("3jLHL").css)({[`.ProseMirror:not(.${a}) > li::before`]:{content:'" "',lineHeight:1.714},[`.ProseMirror:not(.${a}) > li > p:first-child, .ProseMirror:not(.${a}) > li > .code-block:first-child, .ProseMirror:not(.${a}) > li > .ProseMirror-gapcursor:first-child + .code-block`]:{marginTop:"-1.714em !important"}})}),i("i3P6T",function(t,r){e(t.exports,"mediaStyles",()=>o),e(t.exports,"mediaGroupStyles",()=>i),e(t.exports,"mediaAlignmentStyles",()=>s);let a=`> .mediaInlineView-content-wrap > .${n("fhm10").INLINE_IMAGE_WRAPPER_CLASS_NAME}, > :is(a, span[data-mark-type='border']) .mediaInlineView-content-wrap > .${n("fhm10").INLINE_IMAGE_WRAPPER_CLASS_NAME}, > .${n("fhm10").INLINE_IMAGE_WRAPPER_CLASS_NAME}, > :is(a, span[data-mark-type='border']) .${n("fhm10").INLINE_IMAGE_WRAPPER_CLASS_NAME}`,o=(0,n("3jLHL").css)({".ProseMirror":{[`li .${n("gnMzP").richMediaClassName}`]:{margin:0},"&.ua-chrome li > .mediaSingleView-content-wrap::before":{content:"''",display:"block",height:0},"&.ua-firefox":{".mediaSingleView-content-wrap":{userSelect:"none"},".captionView-content-wrap":{userSelect:"text"}},".mediaSingleView-content-wrap[layout^='wrap-']":{position:"relative",zIndex:n("aFUXX").akEditorWrappedNodeZIndex,maxWidth:"100%",clear:"inherit"},".mediaSingleView-content-wrap[layout='center']":{clear:"both"},[`table .${n("gnMzP").richMediaClassName}`]:{marginTop:"var(--ds-space-150, 12px)",marginBottom:"var(--ds-space-150, 12px)",clear:"both","&.image-wrap-left[data-layout], &.image-wrap-right[data-layout]":{clear:"none","&:first-child":{marginTop:"var(--ds-space-150, 12px)"}}},[`.${n("gnMzP").richMediaClassName}.image-wrap-right + .${n("gnMzP").richMediaClassName}.image-wrap-left`]:{clear:"both"},[`.${n("gnMzP").richMediaClassName}.image-wrap-left + .${n("gnMzP").richMediaClassName}.image-wrap-right, .${n("gnMzP").richMediaClassName}.image-wrap-right + .${n("gnMzP").richMediaClassName}.image-wrap-left, .${n("gnMzP").richMediaClassName}.image-wrap-left + .${n("gnMzP").richMediaClassName}.image-wrap-left, .${n("gnMzP").richMediaClassName}.image-wrap-right + .${n("gnMzP").richMediaClassName}.image-wrap-right`]:{marginRight:0,marginLeft:0},"@media all and (max-width: 410px)":{"div.mediaSingleView-content-wrap[layout='wrap-left'], div.mediaSingleView-content-wrap[data-layout='wrap-left'], div.mediaSingleView-content-wrap[layout='wrap-right'], div.mediaSingleView-content-wrap[data-layout='wrap-right']":{float:"none",overflow:"auto",margin:"var(--ds-space-150, 12px) 0"}},[`& [layout='full-width'] .${n("gnMzP").richMediaClassName}, & [layout='wide'] .${n("gnMzP").richMediaClassName}`]:{marginLeft:"50%",transform:"translateX(-50%)"},".media-extended-resize-experience[layout^='wrap-']":{overflow:"visible !important"},"& [layout^='wrap-'] + [layout^='wrap-']":{clear:"none","& + p, & + div[class^='fabric-editor-align'], & + ul, & + ol, & + h1, & + h2, & + h3, & + h4, & + h5, & + h6":{clear:"both !important"},[`& .${n("gnMzP").richMediaClassName}`]:{marginLeft:0,marginRight:0}},[`.${n("fhm10").INLINE_IMAGE_WRAPPER_CLASS_NAME}`]:{height:22,transform:"translateY(-2px)"},h1:{[a]:{height:36,transform:"translateY(-3px)"}},h2:{[a]:{height:31,transform:"translateY(-3px)"}},h3:{[a]:{height:25,transform:"translateY(-2px)"}},h4:{[a]:{height:23,transform:"translateY(-2px)"}},h5:{[a]:{height:20,transform:"translateY(-2px)"}},h6:{[a]:{height:18,transform:"translateY(-2px)"}},".mediaSingleView-content-wrap[layout='wrap-left']":{float:"left"},".mediaSingleView-content-wrap[layout='wrap-right']":{float:"right"},".mediaSingleView-content-wrap[layout='wrap-right'] + .mediaSingleView-content-wrap[layout='wrap-left']":{clear:"both"},"& > .mediaSingleView-content-wrap":{".richMedia-resize-handle-right":{marginRight:`-${n("aFUXX").akEditorMediaResizeHandlerPaddingWide}px`},".richMedia-resize-handle-left":{marginLeft:`-${n("aFUXX").akEditorMediaResizeHandlerPaddingWide}px`}}},[`.${n("ag6aQ").ClassNames.FLOATING_TOOLBAR_COMPONENT}`]:{padding:0},".richMedia-resize-handle-right, .richMedia-resize-handle-left":{display:"flex",flexDirection:"column",justifyContent:"center"},".richMedia-resize-handle-right":{alignItems:"flex-end",paddingRight:"var(--ds-space-150, 12px)",marginRight:`-${n("aFUXX").akEditorMediaResizeHandlerPadding}px`},".richMedia-resize-handle-left":{alignItems:"flex-start",paddingLeft:"var(--ds-space-150, 12px)",marginLeft:`-${n("aFUXX").akEditorMediaResizeHandlerPadding}px`},".richMedia-resize-handle-right::after, .richMedia-resize-handle-left::after":{content:"' '",display:"flex",width:3,height:64,borderRadius:6},[`.${n("gnMzP").richMediaClassName}:hover .richMedia-resize-handle-left::after, .${n("gnMzP").richMediaClassName}:hover .richMedia-resize-handle-right::after`]:{background:"var(--ds-border, #091E4224)"},[`.${n("aFUXX").akEditorSelectedNodeClassName} .richMedia-resize-handle-right::after, .${n("aFUXX").akEditorSelectedNodeClassName} .richMedia-resize-handle-left::after, .${n("gnMzP").richMediaClassName} .richMedia-resize-handle-right:hover::after, .${n("gnMzP").richMediaClassName} .richMedia-resize-handle-left:hover::after, .${n("gnMzP").richMediaClassName}.is-resizing .richMedia-resize-handle-right::after, .${n("gnMzP").richMediaClassName}.is-resizing .richMedia-resize-handle-left::after`]:{background:"var(--ds-border-focused, #388BFF)"},".__resizable_base__":{left:"unset !important",width:"auto !important",height:"auto !important"},".danger > div > div > .media-card-frame, .danger > span > a":{backgroundColor:"var(--ds-background-danger, #FFECEB)",boxShadow:`0px 0px 0px ${n("aFUXX").akEditorSelectedBorderBoldSize}px, var(--ds-border-danger, #E2483D)`,transition:"background-color 0s, box-shadow 0s"},".danger":{[`.${n("gnMzP").richMediaClassName} .${n("jTudT").fileCardImageViewSelector}::after`]:{border:"1px solid var(--ds-border-danger, #E2483D)"},[`.${n("gnMzP").richMediaClassName} .${n("cDSVG").inlinePlayerClassName}::after`]:{border:"1px solid var(--ds-border-danger, #E2483D)"},[`.${n("gnMzP").richMediaClassName} .${n("8jrlU").newFileExperienceClassName}`]:{boxShadow:"0 0 0 1px var(--ds-border-danger, #E2483D) !important"},".richMedia-resize-handle-right::after, .richMedia-resize-handle-left::after":{background:"var(--ds-icon-danger, #C9372C) !important"},".resizer-handle-thumb":{background:"var(--ds-icon-danger, #C9372C) !important"},"div div .media-card-frame, .inlineCardView-content-wrap > span > a":{backgroundColor:"var(--ds-blanket-danger, #EF5C4814)",transition:"background-color 0s"},"div div .media-card-frame::after":{boxShadow:"none"}},".warning":{[`.${n("gnMzP").richMediaClassName} .${n("jTudT").fileCardImageViewSelector}::after`]:{border:"1px solid var(--ds-border-warning, #E56910)"},[`.${n("gnMzP").richMediaClassName} .${n("cDSVG").inlinePlayerClassName}::after`]:{border:"1px solid var(--ds-border-warning, #E56910)"},[`.${n("gnMzP").richMediaClassName} .${n("8jrlU").newFileExperienceClassName}`]:{boxShadow:"0 0 0 1px var(--ds-border-warning, #E56910) !important"},".resizer-handle-thumb":{background:"var(--ds-icon-warning, #E56910) !important"}},".media-filmstrip-list-item":{cursor:"pointer"},[`.mediaGroupView-content-wrap.${n("aFUXX").akEditorSelectedNodeClassName} #newFileExperienceWrapper`]:{boxShadow:n("aFUXX").akEditorSelectedBoxShadow},".ak-editor-no-interaction #newFileExperienceWrapper":{boxShadow:"none"}}),i=(0,n("3jLHL").css)({".mediaGroupView-content-wrap ul":{padding:0}}),s=(0,n("3jLHL").css)({'.fabric-editor-block-mark[class^="fabric-editor-align"]':{clear:"none"},".fabric-editor-align-end":{textAlign:"right"},".fabric-editor-align-start":{textAlign:"left"},".fabric-editor-align-center":{textAlign:"center"},".fabric-editor--full-width-mode":{".pm-table-container":{".code-block, .extension-container, .multiBodiedExtension--container":{maxWidth:"100%"}}}})}),i("1OsG9",function(t,r){e(t.exports,"mentionsStyles",()=>o),e(t.exports,"mentionNodeStyles",()=>i),e(t.exports,"mentionsStylesMixin_platform_editor_centre_mention_padding",()=>s),e(t.exports,"mentionsSelectionStyles",()=>d);let a=(0,n("3jLHL").css)({color:"var(--ds-text-subtle, #44546F)"}),o=(0,n("3jLHL").css)({[`.${n("9WN1A").MentionSharedCssClassName.MENTION_CONTAINER}`]:{[`&.${n("aFUXX").akEditorSelectedNodeClassName} [data-mention-id] > span`]:[n("45RBH").boxShadowSelectionStyles,n("45RBH").backgroundSelectionStyles,a]},".danger":{[`.${n("9WN1A").MentionSharedCssClassName.MENTION_CONTAINER}.${n("aFUXX").akEditorSelectedNodeClassName}`]:{"> span > span > span":{boxShadow:`0 0 0 ${n("aFUXX").akEditorSelectedBorderSize}px ${n("aFUXX").akEditorDeleteBorder}`,backgroundColor:"var(--ds-background-danger, #FFECEB)"}},[`.${n("9WN1A").MentionSharedCssClassName.MENTION_CONTAINER} > span > span > span`]:{backgroundColor:"var(--ds-background-neutral, #091E420F)",color:"var(--ds-text-subtle, #44546F)"}}}),i=(0,n("3jLHL").css)({".editor-mention-primitive":{display:"inline",borderRadius:"20px",cursor:"pointer",padding:"0 0.3em 2px 0.23em",lineHeight:"1.714",fontWeight:"var(--ds-font-weight-regular, 400)",wordBreak:"break-word",background:"var(--ds-background-neutral, #091E420F)",border:"1px solid transparent",color:"var(--ds-text-subtle, #44546F)","&:hover":{background:"var(--ds-background-neutral-hovered, #091E4224)"},"&:active":{background:"var(--ds-background-neutral-pressed, #091E424F)"}},".editor-mention-primitive.mention-restricted":{background:"transparent",border:"1px solid var(--ds-border-bold, #758195)",color:"var(--ds-text, #172B4D)","&:hover":{background:"transparent"},"&:active":{background:"transparent"}},".editor-mention-primitive.mention-self":{background:"var(--ds-background-brand-bold, #0C66E4)",border:"1px solid transparent",color:"var(--ds-text-inverse, #FFFFFF)","&:hover":{background:"var(--ds-background-brand-bold-hovered, #0055CC)"},"&:active":{background:"var(--ds-background-brand-bold-pressed, #09326C)"}}}),s=(0,n("3jLHL").css)({".editor-mention-primitive":{padding:"1px 0.3em 1px 0.23em"}}),d=(0,n("3jLHL").css)({".danger":{".editor-mention-primitive":{boxShadow:`0 0 0 ${n("aFUXX").akEditorSelectedBorderSize}px ${n("aFUXX").akEditorDeleteBorder}`,backgroundColor:"var(--ds-background-danger, #FFECEB)"}},[`.${n("aFUXX").akEditorSelectedNodeClassName}`]:{"> .editor-mention-primitive, > .editor-mention-primitive.mention-self, > .editor-mention-primitive.mention-restricted":[n("45RBH").boxShadowSelectionStyles,n("45RBH").backgroundSelectionStyles,n("45RBH").hideNativeBrowserTextSelectionStyles,a]}})}),i("b7ODQ",function(t,r){e(t.exports,"panelStyles",()=>a),e(t.exports,"panelStylesMixin_fg_platform_editor_add_border_for_nested_panel",()=>o),e(t.exports,"panelStylesMixin_fg_platform_editor_nested_dnd_styles_changes",()=>i),e(t.exports,"panelStylesMixin",()=>s),e(t.exports,"panelViewStyles",()=>d);let a=(0,n("3jLHL").css)({".ProseMirror":{".ak-editor-panel":{cursor:"pointer","&.danger":{boxShadow:"0 0 0 1px var(--ds-border-danger, #E2483D)",backgroundColor:"var(--ds-background-danger, #FFECEB) !important",".ak-editor-panel__icon":{color:"var(--ds-icon-danger, #C9372C) !important"}},borderRadius:"var(--ds-border-radius, 3px)",margin:"0.75rem 0 0",paddingTop:"var(--ds-space-100, 8px)",paddingRight:"var(--ds-space-200, 16px)",paddingBottom:"var(--ds-space-100, 8px)",paddingLeft:"var(--ds-space-100, 8px)",minWidth:"48px",display:"flex",position:"relative",alignItems:"normal",wordBreak:"break-word",backgroundColor:"var(--ds-background-accent-blue-subtlest, #E9F2FF)",color:"inherit",".ak-editor-panel__icon":{flexShrink:0,height:"var(--ds-space-300, 24px)",width:"var(--ds-space-300, 24px)",boxSizing:"content-box",paddingRight:"var(--ds-space-100, 8px)",textAlign:"center",userSelect:"none","-moz-user-select":"none","-webkit-user-select":"none","-ms-user-select":"none",marginTop:"0.1em","> span":{verticalAlign:"middle",display:"inline-flex"},".emoji-common-emoji-sprite":{verticalAlign:"-2px"},".emoji-common-emoji-image":{verticalAlign:"-3px","@-moz-document url-prefix()":{img:{display:"inline-block"}}}},".ak-editor-panel__content":{margin:"var(--ds-space-025, 2px) 0 var(--ds-space-025, 2px)",flex:"1 0 0",minWidth:0},'&[data-panel-type="note"]':{backgroundColor:"var(--ds-background-accent-purple-subtlest, #F3F0FF)",color:"inherit"},'&[data-panel-type="tip"]':{backgroundColor:"var(--ds-background-accent-green-subtlest, #DCFFF1)",color:"inherit"},'&[data-panel-type="warning"]':{backgroundColor:"var(--ds-background-accent-yellow-subtlest, #FFF7D6)",color:"inherit"},'&[data-panel-type="error"]':{backgroundColor:"var(--ds-background-accent-red-subtlest, #FFECEB)",color:"inherit"},'&[data-panel-type="success"]':{backgroundColor:"var(--ds-background-accent-green-subtlest, #DCFFF1)",color:"inherit"}},".ak-editor-panel__content":{cursor:"text"},".danger .ak-editor-panel":{"&[data-panel-type]":{backgroundColor:"var(--ds-blanket-danger, #EF5C4814)",".ak-editor-panel__icon":{color:"var(--ds-icon-danger, #C9372C)"}}}},".ak-editor-panel.ak-editor-selected-node:not(.danger)":{boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4)",borderColor:"transparent",position:"relative","-webkit-user-select":"text","&::before":{position:"absolute",content:'""',left:0,right:0,top:0,bottom:0,width:"100%",pointerEvents:"none",zIndex:12,backgroundColor:"var(--ds-blanket-selected, #388BFF14)"},"&::selection, *::selection":{backgroundColor:"transparent"},"&::-moz-selection, *::-moz-selection":{backgroundColor:"transparent"}}}),o=(0,n("3jLHL").css)({".ProseMirror":{".ak-editor-panel":{".ak-editor-panel__content .ak-editor-panel":{border:"1px solid var(--ds-border, #091E4224)"}}}}),i=(0,n("3jLHL").css)({".ProseMirror":{".ak-editor-panel":{"&.ak-editor-panel__no-icon":{paddingRight:"var(--ds-space-150, 12px)",paddingLeft:"var(--ds-space-150, 12px)"}}},".ak-editor-content-area.appearance-full-page .ProseMirror":{".ak-editor-panel .ak-editor-panel__icon":{paddingRight:"var(--ds-space-150, 12px)"},".ak-editor-panel.ak-editor-panel__no-icon":{paddingLeft:"var(--ds-space-250, 20px)",paddingRight:"var(--ds-space-250, 20px)"}},".ak-editor-content-area .ak-editor-content-area .ProseMirror":{".ak-editor-panel .ak-editor-panel__icon":{paddingRight:"var(--ds-space-100, 8px)"},".ak-editor-panel.ak-editor-panel__no-icon":{paddingRight:"var(--ds-space-150, 12px)",paddingLeft:"var(--ds-space-150, 12px)"}}}),s=(0,n("3jLHL").css)({".ProseMirror":{".ak-editor-panel":{'&[data-panel-type="info"]':{'.ak-editor-panel__icon[data-panel-type="info"]':{color:"var(--ds-icon-information, #1D7AFC)"}},'&[data-panel-type="note"]':{'.ak-editor-panel__icon[data-panel-type="note"]':{color:"var(--ds-icon-discovery, #8270DB)"}},'&[data-panel-type="tip"]':{'.ak-editor-panel__icon[data-panel-type="tip"]':{color:"var(--ds-icon-success, #22A06B)"}},'&[data-panel-type="warning"]':{'.ak-editor-panel__icon[data-panel-type="warning"]':{color:"var(--ds-icon-warning, #E56910)"}},'&[data-panel-type="error"]':{'.ak-editor-panel__icon[data-panel-type="error"]':{color:"var(--ds-icon-danger, #C9372C)"}},'&[data-panel-type="success"]':{'.ak-editor-panel__icon[data-panel-type="success"]':{color:"var(--ds-icon-success, #22A06B)"}}}}}),d=(0,n("3jLHL").css)({".panelView-content-wrap":{boxSizing:"border-box"}})}),i("boGpU",function(t,r){e(t.exports,"paragraphStylesUGCRefreshed",()=>o),e(t.exports,"paragraphStylesOld",()=>i);let a="0.75rem",o=(0,n("3jLHL").css)({".ProseMirror p":{font:'normal 400 1em/1.714 "Atlassian Sans", ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',marginTop:a,marginBottom:0}});(0,n("3jLHL").css)({".ProseMirror p":{font:'normal 400 1em/1.714 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif',marginTop:a,marginBottom:0}});let i=(0,n("3jLHL").css)({".ProseMirror p":{fontSize:"1em",lineHeight:1.714,fontWeight:"var(--ds-font-weight-regular, 400)",marginTop:a,marginBottom:0,letterSpacing:"-0.005em"}})}),i("bEq83",function(t,r){e(t.exports,"placeholderTextStyles",()=>a),e(t.exports,"placeholderTextStylesMixin_fg_platform_editor_system_fake_text_highlight_colour",()=>o),e(t.exports,"placeholderStyles",()=>i),e(t.exports,"placeholderOverflowStyles",()=>s),e(t.exports,"placeholderWrapStyles",()=>d);let a=(0,n("3jLHL").css)({".ProseMirror span[data-placeholder]":{color:"var(--ds-text-subtlest, #626F86)",display:"inline"},".ProseMirror span.pm-placeholder":{display:"inline",color:"var(--ds-text-subtlest, #626F86)"},".ProseMirror span.pm-placeholder__text":{display:"inline",color:"var(--ds-text-subtlest, #626F86)"},".ProseMirror span.pm-placeholder.ak-editor-selected-node":{backgroundColor:"var(--ds-background-selected, #E9F2FF)","&::selection,*::selection":{backgroundColor:"transparent"},"&::-moz-selection,*::-moz-selection":{backgroundColor:"transparent"}},".ProseMirror span.pm-placeholder__text[data-placeholder]::after":{color:"var(--ds-text-subtlest, #626F86)",cursor:"text",content:"attr(data-placeholder)",display:"inline"},".ProseMirror":{".ProseMirror-fake-text-cursor":{display:"inline",pointerEvents:"none",position:"relative"},".ProseMirror-fake-text-cursor::after":{content:'""',display:"inline",top:0,position:"absolute",borderRight:"1px solid var(--ds-border, #091E4224)"},".ProseMirror-fake-text-selection":{display:"inline",pointerEvents:"none",position:"relative",backgroundColor:"var(--ds-background-selected, #B3D4FF)"}}}),o=(0,n("3jLHL").css)({".ProseMirror":{".ProseMirror-fake-text-selection":{backgroundColor:"Highlight",color:"HighlightText"}}}),i=(0,n("3jLHL").css)({".ProseMirror .placeholder-decoration":{color:"var(--ds-text-subtlest, #626F86)",width:"100%",pointerEvents:"none",userSelect:"none",".placeholder-android":{pointerEvents:"none",outline:"none",userSelect:"none",position:"absolute"}}}),s=(0,n("3jLHL").css)({".ProseMirror p:has(.placeholder-decoration-hide-overflow)":{overflow:"hidden",whiteSpace:"nowrap",textOverflow:"ellipsis"}}),d=(0,n("3jLHL").css)({'.ProseMirror mark[data-type-ahead-query="true"]:has(.placeholder-decoration-wrap)':{whiteSpace:"nowrap"}})}),i("jCkqQ",function(t,r){e(t.exports,"resizerStyles",()=>c),e(t.exports,"pragmaticResizerStylesForTooltip",()=>p),e(t.exports,"pragmaticStylesLayoutFirstNodeResizeHandleFix",()=>u),e(t.exports,"pragmaticResizerStyles",()=>m),e(t.exports,"pragmaticResizerStylesNew",()=>h);let a="resizer-hover-zone",o="resizer-is-extended",i="resizer-handle",s=`${i}-track`,d=`${i}-thumb`,l=`${i}-danger`,c=(0,n("3jLHL").css)({".resizer-item":{willChange:"width","&:hover, &.display-handle":{[`& > .resizer-handle-wrapper > .${i}`]:{visibility:"visible",opacity:1}},"&.is-resizing":{[`& .${d}`]:{background:"var(--ds-border-focused, #388BFF)"}},[`&.${l}`]:{[`& .${d}`]:{transition:"none",background:"var(--ds-icon-danger, #C9372C)"}}},[`.${i}`]:{display:"flex",visibility:"hidden",opacity:0,flexDirection:"column",justifyContent:"center",alignItems:"center",width:7,transition:"visibility 0.2s, opacity 0.2s","& div[role='presentation']":{width:"100%",height:"100%",display:"flex",flexDirection:"column",justifyContent:"center",alignItems:"center",marginTop:"var(--ds-space-negative-200, -16px)",whiteSpace:"normal"},"&.left":{alignItems:"flex-start"},"&.right":{alignItems:"flex-end"},"&.small":{[`& .${d}`]:{height:43}},"&.medium":{[`& .${d}`]:{height:64}},"&.large":{[`& .${d}`]:{height:96}},"&.clamped":{[`& .${d}`]:{height:"clamp(43px, calc(100% - 32px), 96px)"}},"&.sticky":{[`& .${d}`]:{position:"sticky",top:"var(--ds-space-150, 12px)",bottom:"var(--ds-space-150, 12px)"}},"&:hover":{[`& .${d}`]:{background:"var(--ds-border-focused, #388BFF)"},[`& .${s}`]:{visibility:"visible",opacity:.5}}},[`.${d}`]:{content:"' '",display:"flex",width:3,margin:"0 var(--ds-space-025, 2px)",height:64,transition:"background-color 0.2s",borderRadius:6,border:0,padding:0,zIndex:2,outline:"none",minHeight:24,background:"var(--ds-border, #091E4224)","&:hover":{cursor:"col-resize"},"&:focus":{background:"var(--ds-border-selected, #0C66E4)","&::after":{content:"''",position:"absolute",top:"var(--ds-space-negative-050, -4px)",right:"var(--ds-space-negative-050, -4px)",bottom:"var(--ds-space-negative-050, -4px)",left:"var(--ds-space-negative-050, -4px)",border:"2px solid var(--ds-border-focused, #388BFF)",borderRadius:"inherit",zIndex:-1}}},[`.${s}`]:{visibility:"hidden",position:"absolute",width:7,height:"calc(100% - 40px)",borderRadius:4,opacity:0,transition:"background-color 0.2s, visibility 0.2s, opacity 0.2s","&.none":{background:"none"},"&.shadow":{background:"var(--ds-background-selected, #E9F2FF)"},"&.full-height":{background:"var(--ds-background-selected, #E9F2FF)",height:"100%",minHeight:36}},".ak-editor-selected-node":{[`& .${d}`]:{background:"var(--ds-border-focused, #388BFF)"}},[`.ak-editor-no-interaction .ak-editor-selected-node .${i}:not(:hover) .${d}`]:{background:"var(--ds-border, #091E4224)"},[`.${a}`]:{position:"relative",display:"inline-block",width:"100%",[`&.${o}`]:{padding:"0 var(--ds-space-150, 12px)",left:"var(--ds-space-negative-150, -12px)"}},[`table .${a}, table .${a}.${o}`]:{padding:"unset",left:"unset"}}),p=(0,n("3jLHL").css)({".pm-breakout-resize-handle-rail-wrapper":{display:"flex",alignItems:"center",justifyContent:"center",height:"100%",cursor:"col-resize",borderRadius:4,zIndex:2,'[role="presentation"]':{height:"100%",width:"100%"},".pm-breakout-resize-handle-rail-inside-tooltip":{height:"100%"}}}),u=(0,n("3jLHL").css)({".fabric-editor-breakout-mark":{'&:has([data-prosemirror-node-name="layoutSection"].first-node-in-document)':{"> .pm-breakout-resize-handle-container":{height:"calc(100% - 8px)"}}}}),m=(0,n("3jLHL").css)({".fabric-editor-breakout-mark":{'&:has([data-prosemirror-node-name="codeBlock"])':{"> .pm-breakout-resize-handle-container--left":{left:"-12px"},"> .pm-breakout-resize-handle-container--right":{right:"-12px"},"> .pm-breakout-resize-handle-container":{height:"calc(100% - 12px)"}},'&:has([data-prosemirror-node-name="expand"]), &:has([data-prosemirror-node-name="layoutSection"])':{"> .pm-breakout-resize-handle-container--left":{left:"-32px"},"> .pm-breakout-resize-handle-container--right":{right:"-32px"}},'&:has([data-prosemirror-node-name="expand"])':{"> .pm-breakout-resize-handle-container":{height:"calc(100% - 4px)"}},'&:has([data-prosemirror-node-name="layoutSection"])':{"> .pm-breakout-resize-handle-container":{height:"calc(100% - 8px)"}},"&:has(.first-node-in-document)":{"> .pm-breakout-resize-handle-container":{height:"100%"}}},".pm-breakout-resize-handle-container":{position:"relative",alignSelf:"end",gridRow:1,gridColumn:1,height:"100%",width:7},".pm-breakout-resize-handle-container--left":{justifySelf:"start"},".pm-breakout-resize-handle-container--right":{justifySelf:"end"},".pm-breakout-resize-handle-rail":{position:"relative",display:"flex",alignItems:"center",justifyContent:"center",height:"100%",cursor:"col-resize",borderRadius:4,transition:"background-color 0.2s, visibility 0.2s, opacity 0.2s",zIndex:2,opacity:0,"&:hover":{background:"var(--ds-background-selected, #E9F2FF)",".pm-breakout-resize-handle-thumb":{background:"var(--ds-border-focused, #388BFF)"}}},".pm-breakout-resize-handle-container--active":{background:"var(--ds-background-selected, #E9F2FF)",".pm-breakout-resize-handle-thumb":{background:"var(--ds-border-focused, #388BFF)"}},".pm-breakout-resize-handle-hit-box":{position:"absolute",top:0,bottom:0,left:-20,right:-20,zIndex:0},".pm-breakout-resize-handle-thumb":{minWidth:3,height:"clamp(27px, calc(100% - 32px), 96px)",background:"var(--ds-border, #091E4224)",borderRadius:6,position:"sticky",top:"var(--ds-space-150, 12px)",bottom:"var(--ds-space-150, 12px)"}}),h=(0,n("3jLHL").css)({".fabric-editor-breakout-mark":{'&:has([data-prosemirror-node-name="codeBlock"])':{"> .pm-breakout-resize-handle-container--left":{left:"-5px"},"> .pm-breakout-resize-handle-container--right":{right:"-5px"},"> .pm-breakout-resize-handle-container":{height:"calc(100% - 12px)"}},'&:has([data-prosemirror-node-name="expand"]), &:has([data-prosemirror-node-name="layoutSection"])':{"> .pm-breakout-resize-handle-container--left":{left:"-25px"},"> .pm-breakout-resize-handle-container--right":{right:"-25px"}},'&:has([data-prosemirror-node-name="expand"])':{"> .pm-breakout-resize-handle-container":{height:"calc(100% - 4px)"}},'&:has([data-prosemirror-node-name="layoutSection"])':{"> .pm-breakout-resize-handle-container":{height:"calc(100% - 8px)"}},"&:has(.first-node-in-document)":{"> .pm-breakout-resize-handle-container":{height:"100%"}}},".pm-breakout-resize-handle-container":{position:"relative",alignSelf:"end",gridRow:1,gridColumn:1,height:"100%",width:7},".pm-breakout-resize-handle-container--left":{justifySelf:"start"},".pm-breakout-resize-handle-container--right":{justifySelf:"end"},".pm-breakout-resize-handle-rail":{position:"relative",display:"flex",alignItems:"center",justifyContent:"center",height:"100%",cursor:"col-resize",borderRadius:4,transition:"background-color 0.2s, visibility 0.2s, opacity 0.2s",zIndex:2,opacity:0,"&:hover":{background:"var(--ds-background-selected, #E9F2FF)",".pm-breakout-resize-handle-thumb":{background:"var(--ds-border-focused, #388BFF)"}}},".pm-breakout-resize-handle-container--active":{background:"var(--ds-background-selected, #E9F2FF)",".pm-breakout-resize-handle-thumb":{background:"var(--ds-border-focused, #388BFF)"}},".pm-breakout-resize-handle-hit-box":{position:"absolute",top:0,bottom:0,left:-20,right:-20,zIndex:0},".pm-breakout-resize-handle-thumb":{minWidth:3,height:"clamp(27px, calc(100% - 32px), 96px)",background:"var(--ds-border, #091E4224)",borderRadius:6,position:"sticky",top:"var(--ds-space-150, 12px)",bottom:"var(--ds-space-150, 12px)"}})}),i("jFNRW",function(t,r){e(t.exports,"ruleStyles",()=>a);let a=(0,n("3jLHL").css)({".ProseMirror hr":{border:"none",backgroundColor:"var(--ds-border, #091E4224)",height:"2px",borderRadius:"1px",cursor:"pointer",padding:"var(--ds-space-050, 4px) 0",margin:"var(--ds-space-300, 24px) 0",backgroundClip:"content-box"},[`.ProseMirror hr.${n("aFUXX").akEditorSelectedNodeClassName}`]:{outline:"none",backgroundColor:"var(--ds-border-selected, #0C66E4)"}})}),i("9exTD",function(t,r){e(t.exports,"scrollbarStyles",()=>a);let a=(0,n("3jLHL").css)({"-ms-overflow-style":"-ms-autohiding-scrollbar","&::-webkit-scrollbar-corner":{display:"none"},"&::-webkit-scrollbar-thumb":{backgroundColor:"var(--ds-background-neutral-subtle, #00000000)"},"&:hover::-webkit-scrollbar-thumb":{backgroundColor:"var(--ds-background-neutral-bold, #44546F)",borderRadius:8},"&::-webkit-scrollbar-thumb:hover":{backgroundColor:"var(--ds-background-neutral-bold-hovered, #2C3E5D)"}})}),i("kxdG4",function(t,r){e(t.exports,"selectionToolbarAnimationStyles",()=>o);let a=(0,n("3jLHL").keyframes)({from:{opacity:0,transform:"translateY(-16px)"},to:{opacity:1,transform:"translateY(0)"}}),o=(0,n("3jLHL").css)({"[aria-label='Selection toolbar']":{animationName:a,animationDuration:"0.2s",animationTimingFunction:"cubic-bezier(0.6, 0, 0, 1)"}})}),i("cICoC",function(t,r){e(t.exports,"shadowStyles",()=>i);let a="right-shadow",o="left-shadow",i=(0,n("3jLHL").css)({".ProseMirror":{[`& .${a}::before, .${a}::after, .${o}::before, .${o}::after`]:{display:"none",position:"absolute",pointerEvents:"none",zIndex:2,width:8,content:"''",height:"calc(100%)"},[`& .${a}, .${o}`]:{position:"relative"},[`& .${o}::before`]:{background:"linear-gradient(to left, transparent 0, var(--ds-shadow-overflow-spread, #091e4229) 140% ), linear-gradient( to right, var(--ds-shadow-overflow-perimeter, transparent) 0px, transparent 1px)",top:0,left:0,display:"block"},[`& .${a}::after`]:{background:"linear-gradient(to right, transparent 0, var(--ds-shadow-overflow-spread, #091e4229) 140% ), linear-gradient( to left, var(--ds-shadow-overflow-perimeter, transparent) 0px, transparent 1px)",right:0,top:0,display:"block"},"& .sentinel-left":{height:"100%",width:0,minWidth:0},"& .sentinel-right":{height:"100%",width:0,minWidth:0}}})}),i("65RTY",function(t,r){e(t.exports,"smartCardStyles",()=>d),e(t.exports,"smartLinksInLivePagesStyles",()=>l),e(t.exports,"smartLinksInLivePagesStylesOld",()=>c),e(t.exports,"linkingVisualRefreshV1Styles",()=>p);let a="datasourceView-content-inner-wrap",o="blockCardView-content-wrap",i="embedCardView-content-wrap",s="loader-wrapper",d=(0,n("3jLHL").css)({".inlineCardView-content-wrap":{maxWidth:"calc(100% - 20px)",verticalAlign:"top",wordBreak:"break-all",".card-with-comment":{background:"var(--ds-background-accent-yellow-subtler, #F8E6A0)",borderBottom:"2px solid var(--ds-border-accent-yellow, #B38600)",boxShadow:"var(--ds-shadow-overlay, 0px 8px 12px #091E4226, 0px 0px 1px #091E424f)"},".card":{paddingLeft:"var(--ds-space-025, 2px)",paddingRight:"var(--ds-space-025, 2px)",paddingTop:"var(--ds-space-100, 0.5em)",paddingBottom:"var(--ds-space-100, 0.5em)",marginBottom:"var(--ds-space-negative-100, -0.5em)",[`.${s} > a:focus`]:[n("45RBH").boxShadowSelectionStyles,n("45RBH").hideNativeBrowserTextSelectionStyles]},[`&.ak-editor-selected-node .${s} > a`]:[n("45RBH").boxShadowSelectionStyles,n("45RBH").hideNativeBrowserTextSelectionStyles],[`.${s} > a`]:{zIndex:1,position:"relative"},"&.danger":{[`.${s} > a`]:{boxShadow:"0 0 0 1px var(--ds-border-danger, #E2483D)",zIndex:2}}},[`.${o}`]:{display:"block",margin:"0.75rem 0 0",maxWidth:"760px",[`&.ak-editor-selected-node .${s} > div`]:[n("45RBH").boxShadowSelectionStyles,n("45RBH").hideNativeBrowserTextSelectionStyles,{borderRadius:"var(--ds-border-radius-200, 8px)"}],"&.danger":{[`.${s} > div`]:{boxShadow:"0 0 0 1px var(--ds-border-danger, #E2483D) !important"}}},[`.datasourceView-content-wrap.${o}`]:{maxWidth:"100%",display:"flex",justifyContent:"center",[`.${a}`]:{cursor:"pointer",backgroundColor:"var(--ds-background-neutral-subtle, #00000000)",borderRadius:"var(--ds-border-radius-200, 8px)",border:"1px solid var(--ds-border, #091E4224)",overflow:"hidden"},"&.ak-editor-selected-node":{[`.${a}`]:[n("45RBH").boxShadowSelectionStyles,n("45RBH").hideNativeBrowserTextSelectionStyles,{"input::selection":{backgroundColor:"var(--ds-background-selected-hovered, #CCE0FF)"},"input::-moz-selection":{backgroundColor:"var(--ds-background-selected-hovered, #CCE0FF)"}}]},"&.danger":{[`.${a}`]:{boxShadow:"0 0 0 1px var(--ds-border-danger, #E2483D)"}}},[`.${i}`]:{[`.${s} > div`]:{cursor:"pointer","&::after":{transition:"box-shadow 0s"}},[`&.ak-editor-selected-node .${s} > div::after`]:[n("45RBH").boxShadowSelectionStyles,n("45RBH").hideNativeBrowserTextSelectionStyles],"&.danger":{".media-card-frame::after":{boxShadow:"0 0 0 1px var(--ds-border-danger, #E2483D) !important",background:"var(--ds-background-danger, #FFECEB) !important"},".richMedia-resize-handle-right::after, .richMedia-resize-handle-left::after":{background:"var(--ds-border-danger, #E2483D)"}}},".card-floating-toolbar--link-picker":{padding:0}}),l=(0,n("3jLHL").css)({[`.${o}`]:{[`.${s} > div`]:{cursor:"text",a:{cursor:"pointer"}}},[`.${i}`]:{[`.${s} > div`]:{a:{cursor:"pointer"}}}}),c=(0,n("3jLHL").css)({[`.${o}`]:{[`.${s} > div`]:{cursor:"pointer",a:{cursor:"auto"}}},[`.${i}`]:{[`.${s} > div`]:{a:{cursor:"auto"}}}}),p=(0,n("3jLHL").css)({[`.${o}`]:{"ul, ol":{paddingLeft:"inherit"}}})}),i("483hX",function(t,r){e(t.exports,"statusStyles",()=>a),e(t.exports,"statusStylesMixin_fg_platform_component_visual_refresh",()=>o),e(t.exports,"statusStylesMixin_without_fg_platform_component_visual_refresh",()=>i);let a=(0,n("3jLHL").css)({".pm-table-cell-content-wrap, .pm-table-header-content-wrap, [data-layout-section]":{".statusView-content-wrap":{maxWidth:"100%",lineHeight:0,"& > span":{width:"100%"}}},".statusView-content-wrap":{"& > span":{cursor:"pointer",lineHeight:0}},".danger":{".status-lozenge-span > span":{backgroundColor:"rgba(255, 189, 173, 0.5)"},".statusView-content-wrap.ak-editor-selected-node":{".status-lozenge-span > span":{boxShadow:"0 0 0 1px var(--ds-border-danger, #E2483D)"}}},'[data-prosemirror-node-name="status"] .lozenge-wrapper':{backgroundColor:"var(--ds-background-neutral, #091E420F)",maxWidth:"100%",paddingInline:"var(--ds-space-050, 4px)",display:"inline-flex",borderRadius:"3px",blockSize:"min-content",position:"static",overflow:"hidden",boxSizing:"border-box",appearance:"none",border:"none"},'[data-prosemirror-node-name="status"] .lozenge-text':{fontSize:"11px",fontStyle:"normal",fontFamily:'var(--ds-font-family-body, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif)',fontWeight:"var(--ds-font-weight-bold, 700)",lineHeight:"16px",overflow:"hidden",textOverflow:"ellipsis",textTransform:"uppercase",whiteSpace:"nowrap",maxWidth:"calc(200px - var(--ds-space-100, 8px))"}}),o=(0,n("3jLHL").css)({".statusView-content-wrap":{"&.ak-editor-selected-node .status-lozenge-span > span":{boxShadow:"0 0 0 2px var(--ds-border-selected, #0C66E4)"}},'[data-prosemirror-node-name="status"] .lozenge-text':{color:"#292A2E"},'[data-prosemirror-node-name="status"] > [data-color=neutral] > .lozenge-wrapper':{backgroundColor:"#DDDEE1"},'[data-prosemirror-node-name="status"] > [data-color=purple] > .lozenge-wrapper':{backgroundColor:"#D8A0F7"},'[data-prosemirror-node-name="status"] > [data-color=blue] > .lozenge-wrapper':{backgroundColor:"#8FB8F6"},'[data-prosemirror-node-name="status"] > [data-color=yellow] > .lozenge-wrapper':{backgroundColor:"#F9C84E"},'[data-prosemirror-node-name="status"] > [data-color=red] > .lozenge-wrapper':{backgroundColor:"#FD9891"},'[data-prosemirror-node-name="status"] > [data-color=green] > .lozenge-wrapper':{backgroundColor:"#B3DF72"}}),i=(0,n("3jLHL").css)({".statusView-content-wrap":{"&.ak-editor-selected-node .status-lozenge-span > span":{boxShadow:"0 0 0 1px var(--ds-border-selected, #0C66E4)",borderColor:"transparent","&::selection, & *::selection":{backgroundColor:"transparent"},"&::-moz-selection, & *::-moz-selection":{backgroundColor:"transparent"}}},'[data-prosemirror-node-name="status"] > [data-color=neutral] .lozenge-wrapper':{backgroundColor:"var(--ds-background-neutral, #091E420F)"},'[data-prosemirror-node-name="status"] > [data-color=neutral] .lozenge-text':{color:"var(--ds-text-subtle, #44546F)"},'[data-prosemirror-node-name="status"] > [data-color=purple] .lozenge-wrapper':{backgroundColor:"var(--ds-background-discovery, #F3F0FF)"},'[data-prosemirror-node-name="status"] > [data-color=purple] .lozenge-text':{color:"var(--ds-text-discovery, #5E4DB2)"},'[data-prosemirror-node-name="status"] > [data-color=blue] .lozenge-wrapper':{backgroundColor:"var(--ds-background-information, #E9F2FF)"},'[data-prosemirror-node-name="status"] > [data-color=blue] .lozenge-text':{color:"var(--ds-text-information, #0055CC)"},'[data-prosemirror-node-name="status"] > [data-color=yellow] .lozenge-wrapper':{backgroundColor:"var(--ds-background-warning, #FFF7D6)"},'[data-prosemirror-node-name="status"] > [data-color=yellow] .lozenge-text':{color:"var(--ds-text-warning, #A54800)"},'[data-prosemirror-node-name="status"] > [data-color=red] .lozenge-wrapper':{backgroundColor:"var(--ds-background-danger, #FFECEB)"},'[data-prosemirror-node-name="status"] > [data-color=red] .lozenge-text':{color:"var(--ds-text-danger, #AE2E24)"},'[data-prosemirror-node-name="status"] > [data-color=green] .lozenge-wrapper':{backgroundColor:"var(--ds-background-success, #DCFFF1)"},'[data-prosemirror-node-name="status"] > [data-color=green] .lozenge-text':{color:"var(--ds-text-success, #216E4E)"}})}),i("jRxPK",function(t,r){e(t.exports,"tableLayoutFixes",()=>a),e(t.exports,"tableCommentEditorStyles",()=>i);let a=(0,n("3jLHL").css)({".pm-table-header-content-wrap :not(.fabric-editor-alignment), .pm-table-header-content-wrap :not(p, .fabric-editor-block-mark) + div.fabric-editor-block-mark, .pm-table-cell-content-wrap :not(p, .fabric-editor-block-mark) + div.fabric-editor-block-mark":{"p:first-of-type":{marginTop:0}},".pm-table-cell-content-wrap .mediaGroupView-content-wrap":{clear:"both"}}),o=(0,n("3jLHL").css)({marginLeft:0,marginRight:0}),i=(0,n("3jLHL").css)({".ProseMirror .pm-table-wrapper > table":[o,n("9exTD").scrollbarStyles]})}),i("d5t0o",function(t,r){e(t.exports,"tasksAndDecisionsStyles",()=>i),e(t.exports,"decisionStyles",()=>s),e(t.exports,"decisionIconWithVisualRefresh",()=>d),e(t.exports,"decisionIconWithoutVisualRefresh",()=>l),e(t.exports,"taskItemStyles",()=>c);let a="ak-editor-selected-node",o="decisionItemView-content-wrap",i=(0,n("3jLHL").css)({".ProseMirror":{[`.taskItemView-content-wrap, .${o}`]:{position:"relative",minWidth:48},[`.${o}`]:{marginTop:0},".taskItemView-content-wrap":{"span[contenteditable='false']":{height:"1.714em"}},".task-item":{lineHeight:1.714}},"div[data-task-local-id]":{"span[contenteditable='false']":{height:"1.714em"},"span[contenteditable='false'] + div":{lineHeight:"1.714em"}},"div[data-task-list-local-id]":{margin:"var(--ds-space-150, 12px) 0 0 0","div + div":{marginTop:"var(--ds-space-050, 4px)"}},"div[data-task-list-local-id] div[data-task-list-local-id]":{marginTop:"var(--ds-space-050, 4px)",marginLeft:"var(--ds-space-300, 24px)"},".ak-editor-panel__content":{"> div[data-task-list-local-id]:first-child":{margin:"0 !important"}}}),s=(0,n("3jLHL").css)({[`.${a} > [data-decision-wrapper], ol[data-node-type='decisionList'].${a}`]:[{borderRadius:"4px"},n("45RBH").boxShadowSelectionStyles,n("45RBH").blanketSelectionStyles,n("45RBH").hideNativeBrowserTextSelectionStyles],".danger":{[`.${o}.${a} > div`]:{boxShadow:"0 0 0 1px var(--ds-border-danger, #E2483D)",backgroundColor:"var(--ds-blanket-danger, #EF5C4814)","&::after":{content:"none"}}},'[data-prosemirror-node-name="decisionItem"]':{listStyleType:"none"},'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper]':{cursor:"pointer",display:"flex",flexDirection:"row",margin:"var(--ds-space-100, 8px) 0 0 0",padding:"var(--ds-space-100, 8px)",paddingLeft:"var(--ds-space-150, 12px)",borderRadius:"var(--ds-border-radius-100, 4px)",backgroundColor:"var(--ds-background-neutral, #091E420F)",position:"relative"},'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper] > [data-component="icon"]':{flex:"0 0 16px",height:"16px",width:"16px",margin:"var(--ds-space-050, 4px) var(--ds-space-150, 12px) 0 0",color:"var(--ds-icon-subtle, #626F86)",display:"flex",alignItems:"center",justifyContent:"center"},'[data-prosemirror-node-name="decisionItem"]:not(:has([data-empty]):not(:has([data-type-ahead]))) > [data-decision-wrapper] > [data-component="icon"]':{color:"var(--ds-icon-success, #22A06B)"},'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper] > [data-component="icon"] > span':{display:"inline-block",flexShrink:0,lineHeight:1},'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper] > [data-component="icon"] > span > svg':{overflow:"hidden",pointerEvents:"none",color:"currentColor",verticalAlign:"bottom"},'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper] > [data-component="placeholder"]':{margin:"0 0 0 calc(var(--ds-space-100, 8px) * 3.5)",position:"absolute",color:"var(--ds-text-subtlest, #626F86)",pointerEvents:"none",textOverflow:"ellipsis",overflow:"hidden",whiteSpace:"nowrap",maxWidth:"calc(100% - 50px)"},'[data-prosemirror-node-name="decisionItem"]:not(:has([data-empty]):not(:has([data-type-ahead]))) > [data-decision-wrapper] > [data-component="placeholder"]':{display:"none"},'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper] > [data-component="content"]':{margin:0,wordWrap:"break-word",minWidth:0,flex:"1 1 auto"}}),d=(0,n("3jLHL").css)({'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper] > [data-component="icon"] > span >  svg[data-icon-source="legacy"]':{display:"none"},'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper] > [data-component="icon"] > span':{boxSizing:"border-box",paddingInlineEnd:"var(--ds--button--new-icon-padding-end, 0)",paddingInlineStart:"var(--ds--button--new-icon-padding-start, 0)","@media screen and (forced-colors: active)":{color:"canvastext",filter:"grayscale(1)"}},'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper] > [data-component="icon"] > span > svg':{width:"var(--ds-space-300, 24px)",height:"var(--ds-space-300, 24px)"}}),l=(0,n("3jLHL").css)({'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper] > [data-component="icon"] > span >  svg[data-icon-source="refreshed"]':{display:"none"},'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper] > [data-component="icon"] > span':{width:"32px",height:"32px","@media screen and (forced-colors: active)":{filter:"grayscale(1)",color:"canvastext",fill:"canvas"}},'[data-prosemirror-node-name="decisionItem"] > [data-decision-wrapper] > [data-component="icon"] > span > svg':{maxWidth:"100%",maxHeight:"100%",fill:"var(--ds-surface, #FFFFFF)",width:"32px",height:"32px"}}),c=(0,n("3jLHL").css)({'[data-prosemirror-node-name="taskItem"]':{listStyle:"none"},'[data-prosemirror-node-name="taskItem"] [data-component="task-item-main"]':{display:"flex",flexDirection:"row",position:"relative"},'[data-prosemirror-node-name="taskItem"] [data-component="placeholder"]':{position:"absolute",color:"var(--ds-text-subtlest, #626F86)",margin:"0 0 0 calc(var(--ds-space-100, 8px) * 3)",pointerEvents:"none",textOverflow:"ellipsis",overflow:"hidden",whiteSpace:"nowrap",maxWidth:"calc(100% - 50px)",display:"none"},"[data-prosemirror-node-name='taskItem']:has([data-empty]):not(:has([data-type-ahead])) [data-component='placeholder']":{display:"block"},'[data-prosemirror-node-name="taskItem"] [data-component="content"]':{margin:0,wordWrap:"break-word",minWidth:0,flex:"1 1 auto"},'[data-prosemirror-node-name="taskItem"] [data-component="checkbox-icon-wrap"]':{display:"inline-block",boxSizing:"border-box",flexShrink:0,lineHeight:1,paddingInlineEnd:"var(--ds--button--new-icon-padding-end, 0)",paddingInlineStart:"var(--ds--button--new-icon-padding-start, 0)"},'[data-prosemirror-node-name="taskItem"] [data-component="checkbox-icon-wrap"] svg':{overflow:"hidden",pointerEvents:"none",color:"currentColor",verticalAlign:"bottom",width:"var(--ds-space-200, 16px)",height:"var(--ds-space-200, 16px)"},'[data-prosemirror-node-name="taskItem"] input[type=checkbox]:not(:checked) + span [data-component=checkbox-checked-icon]':{display:"none"},'[data-prosemirror-node-name="taskItem"] input[type=checkbox]:not(:checked) + span [data-component=checkbox-unchecked-icon]':{display:"inline"},'[data-prosemirror-node-name="taskItem"] input[type=checkbox]:checked + span [data-component=checkbox-checked-icon]':{display:"inline"},'[data-prosemirror-node-name="taskItem"] input[type=checkbox]:checked + span [data-component=checkbox-unchecked-icon]':{display:"none"},'[data-prosemirror-node-name="taskItem"] .task-item-checkbox-wrap':{flex:"0 0 24px",width:"24px",height:"24px",position:"relative",alignSelf:"start","& > input[type='checkbox']":{width:"16px",height:"16px",zIndex:1,cursor:"pointer",outline:"none",margin:0,opacity:0,position:"absolute",top:"50%",left:"50%",transform:"translate(-50%, -50%)","&[disabled]":{cursor:"default"},"+ span":{width:"24px",height:"24px",position:"absolute",top:"50%",left:"50%",transform:"translate(-50%, -50%)"},"+ span > svg":{boxSizing:"border-box",display:"inline",top:"50%",left:"50%",transform:"translate(-50%, -50%)",maxWidth:"unset",maxHeight:"unset",position:"absolute",overflow:"hidden",color:"var(--ds-background-input, #FFFFFF)",transition:"color 0.2s ease-in-out, fill 0.2s ease-in-out","path:first-of-type":{visibility:"hidden"},"rect:first-of-type":{stroke:"var(--ds-border-input, #8590A2)",strokeWidth:1,transition:"stroke 0.2s ease-in-out"}},"&:hover + span > svg":{color:"var(--ds-background-input-hovered, #F7F8F9)","rect:first-of-type":{stroke:"var(--ds-border-input, #8590A2)"}},"&:checked:hover + span > svg":{color:"var(--ds-background-selected-bold-hovered, #0055CC)",fill:"var(--ds-icon-inverse, #FFFFFF)","rect:first-of-type":{stroke:"var(--ds-background-selected-bold-hovered, #0055CC)"}},"&:checked":{"+ span > svg":{"path:first-of-type":{visibility:"visible"},color:"var(--ds-background-selected-bold, #0C66E4)",fill:"var(--ds-icon-inverse, #FFFFFF)","rect:first-of-type":{stroke:"var(--ds-background-selected-bold, #0C66E4)"}}},"&:active + span > svg":{color:"var(--ds-background-input-pressed, #FFFFFF)","rect:first-of-type":{stroke:"var(--ds-border, #091E4224)"}},"&:checked:active + span > svg":{color:"var(--ds-background-input-pressed, #FFFFFF)",fill:"var(--ds-icon-inverse, #FFFFFF)","rect:first-of-type":{stroke:"var(--ds-border, #091E4224)"}},"&:disabled + span > svg, &:disabled:hover + span > svg, &:disabled:focus + span > svg, &:disabled:active + span > svg":{color:"var(--ds-background-disabled, #091E4208)","rect:first-of-type":{stroke:"var(--ds-background-disabled, #091E4208)"}},"&:disabled:checked + span > svg":{fill:"var(--ds-icon-disabled, #091E424F)"},"&:focus + span::after":{position:"absolute",width:"var(--ds-space-200, 16px)",height:"var(--ds-space-200, 16px)",border:"2px solid var(--ds-border-focused, #388BFF)",borderRadius:"var(--ds-space-050, 4px)",content:"''",display:"block",top:"50%",left:"50%",transform:"translate(-50%, -50%)"}}}})}),i("4IK7C",function(t,r){e(t.exports,"telepointerColorAndCommonStyle",()=>d),e(t.exports,"telepointerStyle",()=>l),e(t.exports,"telepointerStyleWithInitialOnly",()=>c);let a=(0,n("3jLHL").keyframes)({"0%, 100%":{transform:"scaleX(0)",opacity:0},"10%":{transform:"scaleX(1.4)",opacity:1},"15%, 85%":{transform:"scaleX(1)",opacity:1}}),o=(0,n("3jLHL").keyframes)({"0%, 90%, 100%":{transform:"scaleX(1)",opacity:1},"10%, 80%":{transform:"scaleX(0)",opacity:0}}),i=(0,n("3jLHL").keyframes)({"0%, 95%":{transform:"scaleX(1)",opacity:1},"100%":{transform:"scaleX(0)",opacity:0}}),s=(0,n("3jLHL").keyframes)({"100%":{transform:"scaleX(1)",opacity:1},"0%, 90%":{transform:"scaleX(0)",opacity:0}}),d=(0,n("3jLHL").css)({".ProseMirror .telepointer":{position:"relative",transition:"opacity 200ms","&.telepointer-selection:not(.inlineNodeView)":{lineHeight:1.2,pointerEvents:"none",userSelect:"none"},"&.telepointer-dim":{opacity:.2},"&.color-0":{"--telepointer-participant-text-color":"var(--ds-text-inverse, #FFFFFF)","--telepointer-participant-bg-color":"var(--ds-background-accent-red-bolder, #C9372C)"},"&.color-1":{"--telepointer-participant-text-color":"var(--ds-text-inverse, #FFFFFF)","--telepointer-participant-bg-color":"var(--ds-background-accent-blue-bolder, #0C66E4)"},"&.color-2":{"--telepointer-participant-text-color":"var(--ds-text-inverse, #FFFFFF)","--telepointer-participant-bg-color":"var(--ds-background-accent-green-bolder, #1F845A)"},"&.color-3":{"--telepointer-participant-text-color":"var(--ds-text-inverse, #FFFFFF)","--telepointer-participant-bg-color":"var(--ds-background-accent-yellow-bolder, #946F00)"},"&.color-4":{"--telepointer-participant-text-color":"var(--ds-text-inverse, #FFFFFF)","--telepointer-participant-bg-color":"var(--ds-background-accent-purple-bolder, #6E5DC6)"},"&.color-5":{"--telepointer-participant-text-color":"var(--ds-text-inverse, #FFFFFF)","--telepointer-participant-bg-color":"var(--ds-background-accent-magenta-bolder, #AE4787)"},"&.color-6":{"--telepointer-participant-text-color":"var(--ds-text-inverse, #FFFFFF)","--telepointer-participant-bg-color":"var(--ds-background-accent-teal-bolder, #227D9B)"},"&.color-7":{"--telepointer-participant-text-color":"var(--ds-text-inverse, #FFFFFF)","--telepointer-participant-bg-color":"var(--ds-background-accent-orange-bolder, #C25100)"},"&.color-8":{"--telepointer-participant-text-color":"var(--ds-text-inverse, #FFFFFF)","--telepointer-participant-bg-color":"var(--ds-background-accent-lime-bolder, #5B7F24)"},"&.color-9":{"--telepointer-participant-text-color":"var(--ds-text-inverse, #FFFFFF)","--telepointer-participant-bg-color":"var(--ds-background-accent-gray-bolder, #626F86)"},"&.color-10":{"--telepointer-participant-text-color":"var(--ds-text-accent-gray-bolder, #091E42)","--telepointer-participant-bg-color":"var(--ds-background-accent-blue-subtle, #579DFF)"},"&.color-11":{"--telepointer-participant-text-color":"var(--ds-text-accent-gray-bolder, #091E42)","--telepointer-participant-bg-color":"var(--ds-background-accent-red-subtle, #F87168)"},"&.color-12":{"--telepointer-participant-text-color":"var(--ds-text-accent-gray-bolder, #091E42)","--telepointer-participant-bg-color":"var(--ds-background-accent-orange-subtle, #FEA362)"},"&.color-13":{"--telepointer-participant-text-color":"var(--ds-text-accent-gray-bolder, #091E42)","--telepointer-participant-bg-color":"var(--ds-background-accent-yellow-subtle, #F5CD47)"},"&.color-14":{"--telepointer-participant-text-color":"var(--ds-text-accent-gray-bolder, #091E42)","--telepointer-participant-bg-color":"var(--ds-background-accent-green-subtle, #4BCE97)"},"&.color-15":{"--telepointer-participant-text-color":"var(--ds-text-accent-gray-bolder, #091E42)","--telepointer-participant-bg-color":"var(--ds-background-accent-teal-subtle, #6CC3E0)"},"&.color-16":{"--telepointer-participant-text-color":"var(--ds-text-accent-gray-bolder, #091E42)","--telepointer-participant-bg-color":"var(--ds-background-accent-purple-subtle, #9F8FEF)"},"&.color-17":{"--telepointer-participant-text-color":"var(--ds-text-accent-gray-bolder, #091E42)","--telepointer-participant-bg-color":"var(--ds-background-accent-magenta-subtle, #E774BB)"},"html:not([data-color-mode=dark]) &":{"--telepointer-participant-background-first-stop":"-850000%","--telepointer-participant-background-second-stop":"150000%"},"html[data-color-mode=dark] &":{"--telepointer-participant-background-first-stop":"-800000%","--telepointer-participant-background-second-stop":"200000%"},'&[class*="color-"]':{background:"linear-gradient(to bottom, var(--telepointer-participant-bg-color) var(--telepointer-participant-background-first-stop), transparent var(--telepointer-participant-background-second-stop))","&::after":{backgroundColor:"var(--telepointer-participant-bg-color)",color:"var(--telepointer-participant-text-color)",borderColor:"var(--telepointer-participant-bg-color)"}}}}),l=(0,n("3jLHL").css)({".ProseMirror .telepointer":{"&.telepointer-selection-badge":{".telepointer-initial, .telepointer-fullname":{position:"absolute",display:"block",userSelect:"none",whiteSpace:"pre",top:-14,left:0,font:'var(--ds-font-body-small, normal 400 11px/16px ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Ubuntu, "Helvetica Neue", sans-serif)',paddingLeft:"var(--ds-space-050, 4px)",paddingRight:"var(--ds-space-050, 4px)",color:"var(--ds-text-inverse, #FFFFFF)",borderRadius:"0 2px 2px 0"},".telepointer-initial":{opacity:1,transition:"opacity 0.15s ease-out"},".telepointer-fullname":{opacity:0,transform:"scaleX(0)",transformOrigin:"top left",transition:"transform 0.15s ease-out, opacity 0.15s ease-out"}},"&.telepointer-pulse-animate":{".telepointer-initial":{animation:`${o} 2.5s ease-in-out`},".telepointer-fullname":{animation:`${a} 2.5s ease-in-out`}},"&.telepointer-pulse-during-tr":{".telepointer-initial":{animation:`${s} 7500ms ease-in-out`},".telepointer-fullname":{animation:`${i} 7500ms ease-in-out`}},"&:hover":{".telepointer-initial":{opacity:0,transitionDelay:"150ms"},".telepointer-fullname":{transform:"scaleX(1)",opacity:1,zIndex:1}}}}),c=(0,n("3jLHL").css)({".ProseMirror .telepointer":{"&.telepointer-selection-badge::after":{content:"attr(data-initial)",position:"absolute",display:"block",top:-14,fontSize:"0.5625rem",padding:"var(--ds-space-025, 2px)",color:"var(--ds-text-inverse, #FFFFFF)",left:0,borderRadius:"2px 2px 2px 0",lineHeight:"initial"}}})}),i("lVQfd",function(t,r){e(t.exports,"textColorStyles",()=>a);let a=(0,n("3jLHL").css)({".fabric-text-color-mark":{color:"var(--custom-palette-color, inherit)"},"a .fabric-text-color-mark":{color:"unset"}})}),i("5EMiD",function(t,r){e(t.exports,"textHighlightStyle",()=>a);let a=(0,n("3jLHL").css)({".text-highlight":{backgroundColor:"var(--ds-background-accent-blue-subtlest, #E9F2FF)",borderBottom:"2px solid var(--ds-background-accent-blue-subtler, #CCE0FF)"}})}),i("cU5yf",function(t,r){e(t.exports,"unsupportedStyles",()=>i);let a="unsupportedBlockView-content-wrap",o="unsupportedInlineView-content-wrap",i=(0,n("3jLHL").css)({[`.${a} > div, .${o} > span:nth-of-type(2)`]:{cursor:"pointer"},".ak-editor-selected-node":{[`&.${a} > div, &.${o} > span:nth-of-type(2)`]:[n("45RBH").backgroundSelectionStyles,n("45RBH").borderSelectionStyles,n("45RBH").hideNativeBrowserTextSelectionStyles]},".danger":{".ak-editor-selected-node":{[`&.${a} > div, &.${o} > span:nth-of-type(2)`]:{border:"1px solid var(--ds-border-danger, #E2483D)",backgroundColor:"var(--ds-blanket-danger, #EF5C4814)"}}}})}),i("9YmWB",function(t,r){e(t.exports,"whitespaceStyles",()=>a);let a=(0,n("3jLHL").css)({".ProseMirror":{wordWrap:"break-word",whiteSpace:"pre-wrap"}})}),i("3ae8F",function(r,a){e(r.exports,"default",()=>l);var o=n("gwFzn"),i=n("atveb");let s=(0,n("3jLHL").css)({display:"flex"}),d=t(o).memo(({items:e,editorView:r,editorActions:a,eventDispatcher:i,providerFactory:d,appearance:l,popupsMountPoint:c,popupsBoundariesElement:p,popupsScrollableElement:u,containerElement:m,disabled:h,dispatchAnalyticsEvent:g,wrapperElement:b,pluginHooks:f})=>(e||f)&&r?(0,n("3jLHL").jsx)(n("98MB9").ErrorBoundary,{component:n("d925B").ACTION_SUBJECT.PLUGIN_SLOT,fallbackComponent:null},(0,n("3jLHL").jsx)(n("3Zxyk").MountPluginHooks,{editorView:r,pluginHooks:f,containerElement:m}),(0,n("3jLHL").jsx)("div",{css:s},e?.map((e,n)=>{let s=e({editorView:r,editorActions:a,eventDispatcher:i,providerFactory:d,dispatchAnalyticsEvent:g,appearance:l,popupsMountPoint:c,popupsBoundariesElement:p,popupsScrollableElement:u,containerElement:m,disabled:h,wrapperElement:b});return s&&t(o).cloneElement(s,{key:n})}))):null,t(i));d.displayName="PluginSlot";var l=d}),i("98MB9",function(r,a){e(r.exports,"ErrorBoundary",()=>i);var o=n("gwFzn");class i extends t(o).Component{hasFallback(){return void 0!==this.props.fallbackComponent}shouldRecover(){return this.hasFallback()&&this.state.errorCaptured}componentDidCatch(e,t){this.props.dispatchAnalyticsEvent&&this.props.dispatchAnalyticsEvent({action:n("d925B").ACTION.EDITOR_CRASHED,actionSubject:this.props.component,actionSubjectId:this.props.componentId,eventType:n("d925B").EVENT_TYPE.OPERATIONAL,attributes:{error:e,errorInfo:t,errorRethrown:!this.hasFallback()}}),(0,n("hWRJP").logException)(e,{location:"editor-core/ui"}),this.hasFallback()&&this.setState({errorCaptured:!0})}render(){return this.shouldRecover()?this.props.fallbackComponent:this.props.children}constructor(...e){super(...e),this.state={errorCaptured:!1}}}}),i("3Zxyk",function(t,r){e(t.exports,"MountPluginHooks",()=>i);var a=n("7UHDa");function o({usePluginHook:e,editorView:t,containerElement:r}){return e({editorView:t,containerElement:r}),null}function i({pluginHooks:e,editorView:t,containerElement:r}){return t?(0,a.jsx)(a.Fragment,{children:e?.map((e,n)=>a.jsx(o,{usePluginHook:e,editorView:t,containerElement:r},n))}):null}n("gwFzn")}),i("uq7dM",function(r,a){e(r.exports,"default",()=>c);var o=n("gwFzn");let i=(0,n("3jLHL").keyframes)({"50%":{backgroundColor:"var(--ds-blanket-danger, #EF5C4814)"}}),s=(0,n("3jLHL").keyframes)({"0%":{backgroundColor:"var(--ds-blanket-danger, #EF5C4814)"},"50%":{backgroundColor:"auto"},"100%":{backgroundColor:"var(--ds-blanket-danger, #EF5C4814)"}}),d=(0,n("3jLHL").css)({"&.-flash > div":{animationName:s,animationDuration:"0.25s",animationTimingFunction:"ease-in-out"},"& > div":{animation:"'none'"}}),l=(0,n("3jLHL").css)({[`${d} & > div`]:{animationName:i,animationDuration:"0.25s",animationTimingFunction:"ease-in-out"}});class c extends t(o).Component{render(){let{animate:e,children:t}=this.props;return this.toggle=e&&!this.toggle,(0,n("3jLHL").jsx)("div",{css:e?l:d,className:this.toggle?"-flash":""},t)}constructor(...e){super(...e),this.toggle=!1}}}),i("6cQbn",function(r,a){e(r.exports,"CommentEditorWithIntl",()=>E);var o=n("gwFzn"),i=n("6qIXK"),s=n("5Gwdo");n("c4XA1");var d=n("1oCLl"),l=n("iu6m9"),c=n("761rI"),p=n("axOCf");let u=(0,n("3jLHL").css)({display:"flex",flexDirection:"column",".less-margin .ProseMirror":{margin:"var(--ds-space-150, 12px) var(--ds-space-100, 8px) var(--ds-space-100, 8px)"},minWidth:"272px",height:"auto",backgroundColor:"var(--ds-background-input, white)",border:"1px solid var(--ds-border-input, #8590A2)",boxSizing:"border-box",borderRadius:"var(--ds-border-radius, 3px)",maxWidth:"inherit",wordWrap:"break-word"}),m=(0,c.createEditorContentStyle)((0,n("3jLHL").css)({flexGrow:1,overflowX:"clip",lineHeight:"24px",".ProseMirror":{margin:"var(--ds-space-150, 12px)"},".gridParent":{marginLeft:"var(--ds-space-025, 2px)",marginRight:"var(--ds-space-025, 2px)",width:`calc(100% + ${14-n("87iYj").GRID_GUTTER}px)`},padding:"var(--ds-space-250, 20px)"},n("3teBi").tableCommentEditorStyles));m.displayName="ContentArea";let h=(0,n("3jLHL").css)({boxSizing:"border-box",justifyContent:"flex-end",alignItems:"center",display:"flex",padding:"var(--ds-space-150, 12px) var(--ds-space-025, 2px)"}),g=(e=!1)=>(0,n("3jLHL").css)`
		display: flex;
		justify-content: flex-end;
		align-items: center;
		flex-grow: 1;
		padding-right: ${"var(--ds-space-250, 20px)"};
		> div {
			display: flex;
			flex-shrink: 0;
		}
		${e&&`
    @media (max-width: 490px) {
      {
        padding-right: 0;
      }
    }
  `}
	`,b=(0,n("3jLHL").css)({display:"flex",justifyContent:"flex-end",alignItems:"center",flexGrow:1,paddingRight:"var(--ds-space-250, 20px)","> div":{display:"flex",flexShrink:0}}),f=(0,n("3jLHL").css)({"@media (max-width: 490px)":{paddingRight:0}}),x="comment",v=(0,n("9JpPs").componentWithCondition)(()=>(0,l.editorExperiment)("platform_editor_core_static_emotion",!0,{exposure:!0}),p.default,m),y=(0,n("574ry").sharedPluginStateHookMigratorFactory)(e=>(0,n("1Oo9w").useSharedPluginState)(e,["maxContentSize","primaryToolbar","editorViewMode"]),e=>{let t=(0,n("b3YrF").useSharedPluginStateSelector)(e,"maxContentSize.maxContentSizeReached"),r=(0,n("b3YrF").useSharedPluginStateSelector)(e,"primaryToolbar.components"),a=(0,n("b3YrF").useSharedPluginStateSelector)(e,"editorViewMode.mode");return{maxContentSizeState:void 0===t?void 0:{maxContentSizeReached:t},primaryToolbarState:r?{components:r}:void 0,editorViewModeState:a?{mode:a}:void 0}}),E=e=>{let{editorAPI:r}=e,{maxContentSizeState:a,primaryToolbarState:l,editorViewModeState:c}=y(r),p=(0,n("4cy2V").getPrimaryToolbarComponents)(r,l?.components),{mediaState:m}=(0,n("1Oo9w").useSharedPluginState)(r,["media"]),E=(0,n("dBxQj").default)(),{editorDOMElement:S,editorView:C,editorActions:k,eventDispatcher:T,providerFactory:w,contentComponents:_,customContentComponents:N,customPrimaryToolbarComponents:L,primaryToolbarComponents:$,customSecondaryToolbarComponents:R,popupsMountPoint:A,popupsBoundariesElement:I,popupsScrollableElement:F,maxHeight:P,minHeight:O=150,onSave:D,onCancel:B,disabled:M,dispatchAnalyticsEvent:H,useStickyToolbar:j,pluginHooks:U,featureFlags:z,innerRef:X}=e,W=!!a?.maxContentSizeReached,V=!!D||!!B||!!R,G=t(o).useRef(null),J=(0,o.useMemo)(()=>X||t(o).createRef(),[X]),[K,q]=(0,o.useState)(!1);(0,o.useEffect)(()=>(m&&m.subscribeToUploadInProgressState(q),()=>m?.unsubscribeFromUploadInProgressState(q)),[m]);let Z=(0,o.useCallback)(()=>{C&&D&&D(C)},[C,D]),Y=(0,o.useCallback)(()=>{C&&B&&B(C)},[C,B]),Q=(0,o.useCallback)(e=>e.altKey&&("F9"===e.key||120===e.keyCode),[]),ee=!!L,et=(0,o.useCallback)(e=>{C?.hasFocus()||C?.focus(),e.preventDefault(),e.stopPropagation()},[C]),er=$;return Array.isArray(p?.components)&&Array.isArray(er)&&(er=p.components.concat(er)),(0,n("3jLHL").jsx)(n("uq7dM").default,{animate:W},(0,n("3jLHL").jsx)(n("bWRlG").WidthProvider,null,(0,n("3jLHL").jsx)("div",{css:[u,(0,n("3jLHL").css)({minHeight:`${O}px`})],className:"akEditor",ref:J},(0,n("3jLHL").jsx)(n("7Ogr0").MainToolbar,{useStickyToolbar:j,twoLineEditorToolbar:ee},(0,n("3jLHL").jsx)(s.ToolbarArrowKeyNavigationProvider,{editorView:C,childComponentSelector:"[data-testid='ak-editor-main-toolbar']",isShortcutToFocusToolbar:Q,handleEscape:et,editorAppearance:x,useStickyToolbar:j,intl:E},(0,n("3jLHL").jsx)(n("1xxAs").ToolbarWithSizeDetector,{editorView:C,editorActions:k,eventDispatcher:T,providerFactory:w,appearance:x,items:er,popupsMountPoint:A,popupsBoundariesElement:I,popupsScrollableElement:F,disabled:!!M,dispatchAnalyticsEvent:H,containerElement:G.current,twoLineEditorToolbar:ee}),(0,n("3jLHL").jsx)("div",{css:(0,d.expValEquals)("platform_editor_core_static_emotion_non_central","isEnabled",!0)?[b,ee&&f]:g(ee)},L))),(0,n("3jLHL").jsx)(n("kXpLO").default,{editorView:C,editorDisabled:M},(0,n("3jLHL").jsx)(n("bWRlG").WidthConsumer,null,({width:e})=>(0,n("3jLHL").jsx)(v,{ref:G,css:P?(0,n("3jLHL").css)({maxHeight:`${P}px`,overflowY:"auto"}):null,className:t(i)("ak-editor-content-area",{"less-margin":e<n("aFUXX").akEditorMobileBreakoutPoint}),featureFlags:z,viewMode:c?.mode,appearance:x},N&&"before"in N?(0,n("45E6y").contentComponentClickWrapper)(N.before):(0,n("45E6y").contentComponentClickWrapper)(N),(0,n("3jLHL").jsx)(n("3ae8F").default,{editorView:C,editorActions:k,eventDispatcher:T,dispatchAnalyticsEvent:H,providerFactory:w,appearance:x,items:_,popupsMountPoint:A,popupsBoundariesElement:I,popupsScrollableElement:F,containerElement:G.current,disabled:!!M,wrapperElement:J.current,pluginHooks:U}),S,N&&"after"in N?(0,n("45E6y").contentComponentClickWrapper)(N.after):null)))),V&&(0,n("3jLHL").jsx)("div",{css:h,"data-testid":"ak-editor-secondary-toolbar"},(0,n("3jLHL").jsx)(n("hArLp").default,null,!!D&&(0,n("3jLHL").jsx)(n("ccHMk").default,{appearance:"primary",onClick:Z,testId:"comment-save-button",isDisabled:M||K,interactionName:"editor-comment-save-button"},E.formatMessage(n("61p3e").default.saveButton)),!!B&&(0,n("3jLHL").jsx)(n("ccHMk").default,{appearance:"subtle",onClick:Y,isDisabled:M,interactionName:"editor-comment-cancel-button"},E.formatMessage(n("61p3e").default.cancelButton))),(0,n("3jLHL").jsx)("span",{style:{flexGrow:1}}),R)))};E.displayName="CommentEditorAppearance"}),i("5Gwdo",function(r,a){e(r.exports,"KeyDownHandlerContext",()=>s),e(r.exports,"ToolbarArrowKeyNavigationProvider",()=>l);var o=n("gwFzn"),i=n("iu6m9");let s=t(o).createContext({handleArrowLeft:()=>{},handleArrowRight:()=>{},handleTab:()=>{}}),d=(0,n("3jLHL").css)({display:"flex",width:"100%",alignItems:"center"}),l=({children:e,editorView:t,childComponentSelector:r,handleEscape:a,disableArrowKeyNavigation:l,isShortcutToFocusToolbar:p,editorAppearance:u,useStickyToolbar:m,intl:h})=>{let g=(0,o.useRef)(null),b=(0,o.useRef)(0),f=(0,o.useCallback)(e=>{let t=0;document.activeElement&&(t=((t=e.indexOf(document.activeElement))+1)%e.length),b.current=t},[]),x=(0,o.useCallback)(e=>{let t=0;document.activeElement&&(t=e.indexOf(document.activeElement),t=(e.length+t-1)%e.length),b.current=t},[]),v=(0,o.useCallback)(()=>{let e=c(g?.current);f(e),e[b.current]?.focus()},[f]),y=(0,o.useCallback)(()=>{let e=c(g?.current);x(e),e[b.current]?.focus()},[x]),E=(0,o.useCallback)(()=>{let e=c(g?.current);e[b.current]?.focus()},[]),S=()=>{let e=c(g?.current);e.forEach(e=>{e.setAttribute("tabindex","-1")}),e[b.current].setAttribute("tabindex","0")},C=(e,t=!0)=>{t&&e?.scrollIntoView({behavior:"smooth",block:"center",inline:"nearest"}),e.focus()},k=(0,o.useMemo)(()=>({handleArrowLeft:y,handleArrowRight:v,handleTab:E}),[y,v,E]),T=(0,i.editorExperiment)("platform_editor_toolbar_rerender_optimization_exp",!0)?k:{handleArrowLeft:()=>{let e=c(g?.current);x(e),e[b.current]?.focus()},handleArrowRight:()=>{let e=c(g?.current);f(e),e[b.current]?.focus()},handleTab:()=>{let e=c(g?.current);e[b.current]?.focus()}};return(0,o.useLayoutEffect)(()=>{if(!g.current||l)return;let{current:e}=g,o=e=>{let t=e.target;if(t instanceof HTMLElement&&!t.closest(`${r}`)||t instanceof HTMLElement&&document.querySelector('[data-role="droplistContent"], [data-test-id="color-picker-menu"], [data-emoji-picker-container="true"]')?.contains(t)||t instanceof HTMLElement&&document.querySelector('[data-test-id="color-picker-menu"]')?.contains(t)||"ArrowUp"===e.key||"ArrowDown"===e.key||l||document.querySelector(".menu-key-handler-wrapper")||g?.current?.querySelector(`#${n("dK4ZR").ELEMENT_BROWSER_ID}`))return;let o=c(g?.current);if(!o||o?.length===0||t instanceof HTMLElement&&t.closest(`[aria-label="${h.formatMessage(n("b0RMS").mediaInsertMessages.mediaPickerPopupAriaLabel)}"]`))return;t instanceof HTMLElement&&!g.current?.contains(t)?b.current=-1:b.current=t instanceof HTMLElement&&o.indexOf(t)>-1?o.indexOf(t):b.current;let i=!("comment"===u&&m);switch(e.key){case"ArrowRight":f(o),C(o[b.current],i),e.preventDefault();break;case"ArrowLeft":x(o),C(o[b.current],i),e.preventDefault();break;case"Tab":S();break;case"Escape":a(e)}},i=e=>{if(p(e)){let e=c(g?.current);e[0]?.focus(),e[0]?.tagName==="BUTTON"&&e[0].classList.add("first-floating-toolbar-button"),e[0]?.scrollIntoView({behavior:"smooth",block:"center",inline:"nearest"})}};e?.addEventListener("keydown",o);let s=t?.dom;return p&&s?.addEventListener("keydown",i),()=>{e?.removeEventListener("keydown",o),p&&s?.removeEventListener("keydown",i)}},[b,g,t,l,a,r,f,x,p,u,m,h]),(0,n("3jLHL").jsx)("div",{css:"comment"===u&&d,className:"custom-key-handler-wrapper",ref:g,role:"toolbar","aria-label":h.formatMessage(n("8aWkM").messages.toolbarLabel),"aria-controls":n("f9zLy").EDIT_AREA_ID},(0,n("3jLHL").jsx)(s.Provider,{value:T},e))};function c(e){return(e?Array.from(e.querySelectorAll('a[href], button:not([disabled]), textarea, input, select, div[tabindex="-1"], div[tabindex="0"]')||[]):[]).filter(e=>{let t=window.getComputedStyle(e),r="hidden"!==t.visibility&&"none"!==t.display;return!e.closest('[data-role="droplistContent"]')&&!e.closest('[data-emoji-picker-container="true"]')&&!e.closest('[data-test-id="color-picker-menu"]')&&!e.closest(".scroll-buttons")&&r})}}),i("dK4ZR",function(t,r){e(t.exports,"GRID_SIZE",()=>a),e(t.exports,"DEVICE_BREAKPOINT_NUMBERS",()=>o),e(t.exports,"FLEX_ITEMS_CONTAINER_BREAKPOINT_NUMBERS",()=>n),e(t.exports,"SIDEBAR_WIDTH",()=>i),e(t.exports,"SIDEBAR_HEADING_WRAPPER_HEIGHT",()=>s),e(t.exports,"INLINE_SIDEBAR_HEIGHT",()=>d),e(t.exports,"SEARCH_ITEM_HEIGHT_WIDTH",()=>l),e(t.exports,"SCROLLBAR_WIDTH",()=>c),e(t.exports,"ELEMENT_LIST_PADDING",()=>p),e(t.exports,"ELEMENT_ITEM_HEIGHT",()=>u),e(t.exports,"ELEMENT_ITEM_PADDING",()=>m),e(t.exports,"ELEMENT_BROWSER_ID",()=>h);let a=8,o={small:320,medium:600,large:1024},n={small:400,medium:o.medium,large:o.large},i=`${25*a}px`,s=`${6*a}px`,d="54px",l="20px",c=15,p=2,u=60,m=10,h="editor-element-browser"}),i("f9zLy",function(t,r){e(t.exports,"EDIT_AREA_ID",()=>a);let a="ak-editor-textarea"}),i("c4XA1",function(t,r){e(t.exports,"tableFullPageEditorStyles",()=>n("3teBi").tableFullPageEditorStyles),e(t.exports,"tableCommentEditorStyles",()=>n("3teBi").tableCommentEditorStyles)}),i("3teBi",function(t,r){e(t.exports,"insertColumnButtonOffset",()=>i),e(t.exports,"tableStyles",()=>v),e(t.exports,"tableFullPageEditorStyles",()=>y),e(t.exports,"tableCommentEditorStyles",()=>E);var a=n("iu6m9");let o=n("eoFXy").tableToolbarSize+1,i=n("eoFXy").tableInsertColumnButtonSize/2,s=`
.${n("d5aTJ").TableCssClassName.NODEVIEW_WRAPPER}.${n("aFUXX").akEditorSelectedNodeClassName} table tbody tr {
  th,td {
    ${(0,n("ieXGd").getSelectionStyles)([n("b38UX").SelectionStyle.Blanket,n("b38UX").SelectionStyle.Border])}

    // The non-break space /00a0 in :after selector caused a table scroll issue when pressing Cmd+A to select table
    // This line is to override the content of :after selector from the shared getSelectionStyles
    &::after {
      content: '';
    }
  }
}
`,d=`.${n("d5aTJ").TableCssClassName.TABLE_CONTAINER} {
  > .${n("d5aTJ").TableCssClassName.TABLE_STICKY_SENTINEL_TOP}, > .${n("d5aTJ").TableCssClassName.TABLE_STICKY_SENTINEL_BOTTOM} {
    position: absolute;
    width: 100%;
    height: 1px;
    margin-top: -1px;
    // need this to avoid sentinel being focused via keyboard
    // this still allows it to be detected by intersection observer
    visibility: hidden;
  }
  > .${n("d5aTJ").TableCssClassName.TABLE_STICKY_SENTINEL_TOP} {
    top: ${n("eoFXy").columnControlsDecorationHeight}px;
  }
  > .${n("d5aTJ").TableCssClassName.TABLE_STICKY_SENTINEL_BOTTOM} {
      bottom: ${n("eoFXy").tableScrollbarOffset+n("eoFXy").stickyRowOffsetTop+2*n("eoFXy").tablePadding+23}px;
  }
  &.${n("d5aTJ").TableCssClassName.WITH_CONTROLS} {
    > .${n("d5aTJ").TableCssClassName.TABLE_STICKY_SENTINEL_TOP} {
      top: 0px;
    }
    > .${n("d5aTJ").TableCssClassName.TABLE_STICKY_SENTINEL_BOTTOM} {
      margin-bottom: ${n("eoFXy").columnControlsDecorationHeight}px;
    }
  }
}`,l=`.${n("d5aTJ").TableCssClassName.TABLE_CONTAINER} {
 > .${n("d5aTJ").TableCssClassName.TABLE_STICKY_SCROLLBAR_SENTINEL_BOTTOM},
 > .${n("d5aTJ").TableCssClassName.TABLE_STICKY_SCROLLBAR_SENTINEL_TOP} {
    position: absolute;
    width: 100%;
    height: 1px;
    margin-top: -1px;
    // need this to avoid sentinel being focused via keyboard
    // this still allows it to be detected by intersection observer
    visibility: hidden;
  }
  > .${n("d5aTJ").TableCssClassName.TABLE_STICKY_SCROLLBAR_SENTINEL_TOP} {
    top: ${n("eoFXy").columnControlsDecorationHeight+132}px;
  }
  > .${n("d5aTJ").TableCssClassName.TABLE_STICKY_SCROLLBAR_SENTINEL_BOTTOM} {
    bottom: ${n("aFUXX").MAX_BROWSER_SCROLLBAR_HEIGHT}px;
  }
}`,c=`.${n("d5aTJ").TableCssClassName.TABLE_CONTAINER} {
  > .${n("d5aTJ").TableCssClassName.TABLE_STICKY_SCROLLBAR_CONTAINER} {
    width: 100%;
    display: none;
    overflow-x: auto;
    position: sticky;
    bottom: 0;
    z-index: 1;
  }
}`,p=`${c} ${l}`,u=`
  .${n("d5aTJ").TableCssClassName.TABLE_SHADOW_SENTINEL_LEFT},
  .${n("d5aTJ").TableCssClassName.TABLE_SHADOW_SENTINEL_RIGHT} {
    position: absolute;
    top: 0;
    height: 100%;
    width: 1px;
    visibility: hidden;
  }
  .${n("d5aTJ").TableCssClassName.TABLE_SHADOW_SENTINEL_LEFT} {
    left: 0;
  }
  .${n("d5aTJ").TableCssClassName.TABLE_SHADOW_SENTINEL_RIGHT} {
    right: 0;
  }
`,m=()=>(0,n("3jLHL").css)`
		> *:not([data-mark-type='fragment'])
			.${n("d5aTJ").TableCssClassName.NODEVIEW_WRAPPER}
			.${n("d5aTJ").TableCssClassName.TABLE_CONTAINER} {
			margin-left: unset !important;
			width: 100% !important;
		}

		> [data-mark-type='fragment'] * .${n("d5aTJ").TableCssClassName.NODEVIEW_WRAPPER} .${n("d5aTJ").TableCssClassName.TABLE_CONTAINER} {
			margin-left: unset !important;
			width: 100% !important;
		}
	`,h=()=>(0,n("3jLHL").css)`
		/* new styles */
		th {
			.${n("5p8Hs").SORTING_ICON_CLASS_NAME} {
				+ p {
					margin-top: 0 !important;
				}
			}

			> .${n("5p8Hs").SORTING_ICON_CLASS_NAME} {
				&:has(.is-active) {
					.${n("1j8OE").SORTABLE_COLUMN_ICON_CLASSNAME} {
						opacity: 1;
					}
				}
			}

			> .${n("5p8Hs").SORTING_ICON_CLASS_NAME} {
				.${n("1j8OE").SORTABLE_COLUMN_ICON_CLASSNAME} {
					opacity: 0;
					&:focus {
						opacity: 1;
					}
				}
			}

			&:hover:not(:has(.${n("d5aTJ").TableCssClassName.TABLE_CONTAINER}:hover)) {
				> .${n("5p8Hs").SORTING_ICON_CLASS_NAME} {
					.${n("1j8OE").SORTABLE_COLUMN_ICON_CLASSNAME} {
						opacity: 1;
					}
				}
			}
		}
	`,g=()=>`border-color: ${n("eoFXy").tableBorderDeleteColor}`,b=()=>(0,n("3jLHL").css)`
		.${n("d5aTJ").TableCssClassName.TABLE_STICKY} .${n("d5aTJ").TableCssClassName.COLUMN_CONTROLS_DECORATIONS} {
			z-index: 0;
			left: -1px;
		}

		.${n("d5aTJ").TableCssClassName.TABLE_STICKY} .${n("d5aTJ").TableCssClassName.COLUMN_CONTROLS_DECORATIONS}::after {
			border-left: 1px solid ${n("eoFXy").tableBorderColor};
		}

		.${n("d5aTJ").TableCssClassName.TABLE_STICKY} tr:first-of-type th.${n("d5aTJ").TableCssClassName.TABLE_HEADER_CELL} {
			&.${n("d5aTJ").TableCssClassName.COLUMN_SELECTED}, &.${n("d5aTJ").TableCssClassName.HOVERED_COLUMN} {
				.${n("d5aTJ").TableCssClassName.COLUMN_CONTROLS_DECORATIONS}::after {
					left: 0;
				}
			}
		}
	`,f=()=>{if(n("d7ZU3").browser.gecko)return(0,n("3jLHL").css)`
			.${n("d5aTJ").TableCssClassName.TABLE_STICKY} > tbody::before {
				content: '';
			}
		`},x=e=>(0,n("3jLHL").css)`
	${(0,n("1zav4").tableSharedStyle)()};
	${(0,n("gvjT6").columnControlsLineMarker)()};
	${(0,n("gvjT6").hoveredDeleteButton)()};
	${(0,n("gvjT6").hoveredCell)()};
	${n("gvjT6").hoveredWarningCell};
	${(0,n("gvjT6").insertLine)()};
	${(0,n("gvjT6").resizeHandle)()};
	${s};
	${h()};

	.${n("d5aTJ").TableCssClassName.LAST_ITEM_IN_CELL} {
		margin-bottom: 0;
	}

	.${n("d5aTJ").TableCssClassName.TABLE_NODE_WRAPPER} {
		td.${n("d5aTJ").TableCssClassName.TABLE_CELL}, th.${n("d5aTJ").TableCssClassName.TABLE_HEADER_CELL} {
			position: relative;
			overflow: visible;
		}

		td.${n("d5aTJ").TableCssClassName.TABLE_CELL} {
			background-color: ${n("eoFXy").tableCellBackgroundColor};

			&::after {
				height: 100%;
				content: '';
				border-left: 1px solid ${n("eoFXy").tableBorderColor};
				border-bottom: 1px solid ${n("eoFXy").tableBorderColor};
				position: absolute;
				right: 0px;
				top: 0px;
				bottom: 0;
				width: 100%;
				display: inline-block;
				pointer-events: none;
			}
		}
	}

	.${n("d5aTJ").TableCssClassName.CONTROLS_FLOATING_BUTTON_COLUMN} {
		${(0,n("gvjT6").insertColumnButtonWrapper)()}
	}

	.${n("d5aTJ").TableCssClassName.CONTROLS_FLOATING_BUTTON_ROW} {
		${(0,n("gvjT6").insertRowButtonWrapper)()}
	}

	${(0,n("gvjT6").dragInsertButtonWrapper)()}

	${(0,n("gvjT6").dragCornerControlButton)()}

	/* Delete button */
	${(0,n("gvjT6").DeleteButton)()}
	/* Ends Delete button */

	/* sticky styles */
	${(0,n("dh538").fg)("platform_editor_nested_tables_sticky_header_bug")?`
		${(0,n("dh538").fg)("platform_editor_number_column_sticky_header_broken")?`.${n("d5aTJ").TableCssClassName.TABLE_STICKY} > .${e.isDragAndDropEnabled?n("d5aTJ").TableCssClassName.DRAG_ROW_CONTROLS_WRAPPER:n("d5aTJ").TableCssClassName.ROW_CONTROLS_WRAPPER} .${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN} .${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN_BUTTON}:first-of-type {`:`.${n("d5aTJ").TableCssClassName.TABLE_STICKY} > .${n("d5aTJ").TableCssClassName.DRAG_ROW_CONTROLS_WRAPPER} .${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN} .${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN_BUTTON}:first-of-type {`}
			margin-top: ${(0,n("dh538").fg)("platform_editor_number_column_sticky_header_bug")?n("eoFXy").stickyRowOffsetTop:n("eoFXy").stickyRowOffsetTop+2}px;
			width: ${n("aFUXX").akEditorTableNumberColumnWidth}px;

			position: fixed !important;
			z-index: ${n("aFUXX").akEditorStickyHeaderZIndex} !important;
			box-shadow: 0px -${n("eoFXy").stickyRowOffsetTop}px var(--ds-surface, white);
			border-right: 0 none;
			/* top set by NumberColumn component */
		}
		`:`
    	.${n("d5aTJ").TableCssClassName.TABLE_STICKY} .${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN} .${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN_BUTTON}:first-of-type {
			margin-top: ${(0,n("dh538").fg)("platform_editor_number_column_sticky_header_bug")?n("eoFXy").stickyRowOffsetTop:n("eoFXy").stickyRowOffsetTop+2}px;
			width: ${n("aFUXX").akEditorTableNumberColumnWidth}px;

			position: fixed !important;
			z-index: ${n("aFUXX").akEditorStickyHeaderZIndex} !important;
			box-shadow: 0px -${n("eoFXy").stickyRowOffsetTop}px var(--ds-surface, white);
			border-right: 0 none;
			/* top set by NumberColumn component */
		}
		`}

	.${n("d5aTJ").TableCssClassName.TABLE_STICKY} .${n("d5aTJ").TableCssClassName.CORNER_CONTROLS}.sticky {
		position: fixed !important;
		/* needs to be above row controls */
		z-index: ${n("aFUXX").akEditorSmallZIndex} !important;
		background: ${"var(--ds-surface, white)"};

		width: ${n("eoFXy").tableToolbarSize}px;
		height: ${n("eoFXy").tableToolbarSize}px;
	}

	.${n("d5aTJ").TableCssClassName.CORNER_CONTROLS}.sticky .${n("d5aTJ").TableCssClassName.CONTROLS_CORNER_BUTTON} {
		border-bottom: 0px none;
		border-right: 0px none;

		height: ${n("eoFXy").tableToolbarSize}px;
		width: ${n("eoFXy").tableToolbarSize}px;
	}

	${b()}

	${f()}

    .${n("d5aTJ").TableCssClassName.TABLE_STICKY}
      .${n("d5aTJ").TableCssClassName.ROW_CONTROLS}
      .${n("d5aTJ").TableCssClassName.ROW_CONTROLS_BUTTON_WRAP}.sticky {
		position: fixed !important;
		z-index: ${n("aFUXX").akEditorStickyHeaderZIndex} !important;
		display: flex;
		border-left: ${n("eoFXy").tableToolbarSize}px solid ${"var(--ds-surface, white)"};
		margin-left: -${n("eoFXy").tableToolbarSize}px;
	}

	.${n("d5aTJ").TableCssClassName.TABLE_STICKY} col:first-of-type {
		/* moving rows out of a table layout does weird things in Chrome */
		border-right: 1px solid ${"var(--ds-surface, green)"};
	}

	tr.sticky {
		padding-top: ${n("eoFXy").stickyRowOffsetTop}px;
		position: fixed;
		display: grid;

		/* to keep it above cell selection but below date and other nodes popups that are inside sticky header */
		z-index: ${n("aFUXX").akEditorTableCellOnStickyHeaderZIndex-5};

		overflow-y: visible;
		overflow-x: hidden;

		grid-auto-flow: column;

		/* background for where controls apply */
		background: ${"var(--ds-surface, white)"};
		box-sizing: content-box;
		box-shadow: 0 6px 4px -4px ${`var(--ds-shadow-overflow-perimeter, ${n("6fnsQ").N40A})`};
		margin-left: -1px;

		&.no-pointer-events {
			pointer-events: none;
		}
	}

	.${n("d5aTJ").TableCssClassName.TABLE_STICKY} .${n("d5aTJ").TableCssClassName.TABLE_STICKY_SHADOW} {
		left: unset;
		position: fixed;
		/* needs to be above sticky header row and below date and other nodes popups that are inside sticky header */
		z-index: ${n("aFUXX").akEditorTableCellOnStickyHeaderZIndex};
	}

	.${n("d5aTJ").TableCssClassName.WITH_CONTROLS}.${n("d5aTJ").TableCssClassName.TABLE_STICKY} .${n("d5aTJ").TableCssClassName.TABLE_STICKY_SHADOW} {
		padding-bottom: ${n("eoFXy").tableToolbarSize}px;
	}

	.tableView-content-wrap:has(.tableView-content-wrap):has(
			.${n("d5aTJ").TableCssClassName.NESTED_TABLE_WITH_CONTROLS}
		) {
		padding-left: unset;
	}

	.tableView-content-wrap:has(.${n("d5aTJ").TableCssClassName.NESTED_TABLE_WITH_CONTROLS}) {
		padding-left: 15px;
	}

	tr.sticky th {
		border-bottom: ${n("eoFXy").stickyHeaderBorderBottomWidth}px solid ${n("eoFXy").tableBorderColor};
		margin-right: -1px;
	}

	.${n("d5aTJ").TableCssClassName.TABLE_STICKY} tr.sticky > th:last-child {
		border-right-width: 1px;
	}

	/* add left edge for first cell */
	.${n("d5aTJ").TableCssClassName.TABLE_STICKY} tr.sticky > th:first-of-type {
		margin-left: 0px;
	}

	/* add a little bit so the scroll lines up with the table */
	.${n("d5aTJ").TableCssClassName.TABLE_STICKY} tr.sticky::after {
		content: ' ';
		width: ${i+1}px;
	}

	/* To fix jumpiness caused in Chrome Browsers for sticky headers */
	.${n("d5aTJ").TableCssClassName.TABLE_STICKY} .sticky + tr {
		min-height: 0px;
	}

	/* move resize line a little in sticky bar */
	.${n("d5aTJ").TableCssClassName.TABLE_CONTAINER}.${n("d5aTJ").TableCssClassName.TABLE_STICKY} {
		tr.sticky td.${n("d5aTJ").TableCssClassName.WITH_RESIZE_LINE}, tr.sticky th.${n("d5aTJ").TableCssClassName.WITH_RESIZE_LINE} {
			.${n("d5aTJ").TableCssClassName.RESIZE_HANDLE_DECORATION}::after {
				right: ${(n("eoFXy").resizeHandlerAreaWidth-n("eoFXy").resizeLineWidth)/2+1}px;
			}
		}

		/* when selected put it back to normal -- :not selector would be nicer */
		tr.sticky
			td.${n("d5aTJ").TableCssClassName.WITH_RESIZE_LINE}.${n("d5aTJ").TableCssClassName.SELECTED_CELL},
			tr.sticky
			th.${n("d5aTJ").TableCssClassName.WITH_RESIZE_LINE}.${n("d5aTJ").TableCssClassName.SELECTED_CELL} {
			.${n("d5aTJ").TableCssClassName.RESIZE_HANDLE_DECORATION}::after {
				right: ${(n("eoFXy").resizeHandlerAreaWidth-n("eoFXy").resizeLineWidth)/2}px;
			}
		}
	}

	tr.sticky .${n("d5aTJ").TableCssClassName.HOVERED_CELL}, tr.sticky .${n("d5aTJ").TableCssClassName.SELECTED_CELL} {
		z-index: 1;
	}

	.${n("d5aTJ").TableCssClassName.WITH_CONTROLS} tr.sticky {
		padding-top: ${n("eoFXy").tableControlsSpacing}px;
	}

	${(0,n("dh538").fg)("platform_editor_nested_tables_sticky_header_bug")?`
		.${n("d5aTJ").TableCssClassName.WITH_CONTROLS}.${n("d5aTJ").TableCssClassName.TABLE_STICKY} > .${n("d5aTJ").TableCssClassName.DRAG_ROW_CONTROLS_WRAPPER}
			.${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN}
			.${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN_BUTTON}:first-of-type {
			margin-top: ${(0,n("dh538").fg)("platform_editor_number_column_sticky_header_bug")?n("eoFXy").tableControlsSpacing:n("eoFXy").tableControlsSpacing+2}px;
		}
		`:`
		.${n("d5aTJ").TableCssClassName.WITH_CONTROLS}.${n("d5aTJ").TableCssClassName.TABLE_STICKY}
			.${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN}
			.${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN_BUTTON}:first-of-type {
			margin-top: ${(0,n("dh538").fg)("platform_editor_number_column_sticky_header_bug")?n("eoFXy").tableControlsSpacing:n("eoFXy").tableControlsSpacing+2}px;
		}
		`}

	.${n("d5aTJ").TableCssClassName.CORNER_CONTROLS}.sticky {
		border-top: ${(0,n("dh538").fg)("platform_editor_number_column_sticky_header_bug")?n("eoFXy").tableControlsSpacing-n("eoFXy").tableToolbarSize:n("eoFXy").tableControlsSpacing-n("eoFXy").tableToolbarSize+2}px
			solid ${"var(--ds-surface, white)"};
	}

	${d}
	${(0,n("gvjT6").OverflowShadow)(e.featureFlags?.tableDragAndDrop)}
    ${p}

    .${n("d5aTJ").TableCssClassName.TABLE_STICKY} .${n("d5aTJ").TableCssClassName.TABLE_STICKY_SHADOW} {
		height: 0; /* stop overflow flash & set correct height in update-overflow-shadows.ts */
	}

	.less-padding {
		padding: 0 ${n("eoFXy").tablePadding}px;

		.${n("d5aTJ").TableCssClassName.DRAG_ROW_CONTROLS_WRAPPER}, .${n("d5aTJ").TableCssClassName.ROW_CONTROLS_WRAPPER} {
			padding: 0 ${n("eoFXy").tablePadding}px;

			/* https://product-fabric.atlassian.net/browse/ED-16386
			Fixes issue where the extra padding that is added here throws off the position
			of the rows control dot */
			&::after {
				right: 6px !important;
			}
		}

		.${n("d5aTJ").TableCssClassName.DRAG_ROW_CONTROLS_WRAPPER}.${n("d5aTJ").TableCssClassName.TABLE_CHROMELESS} {
			left: -4px;
		}

		.${n("d5aTJ").TableCssClassName.DRAG_COLUMN_CONTROLS_WRAPPER} {
			padding: 0 ${n("eoFXy").tablePadding}px;
		}

		.${n("d5aTJ").TableCssClassName.DRAG_COLUMN_CONTROLS_WRAPPER}.${n("d5aTJ").TableCssClassName.TABLE_CHROMELESS} {
			left: -8px;
		}

		&.${n("d5aTJ").TableCssClassName.TABLE_CONTAINER}[data-number-column='true'] {
			padding-left: ${n("aFUXX").akEditorTableNumberColumnWidth+n("eoFXy").tablePadding-1}px;
		}
		.${n("d5aTJ").TableCssClassName.TABLE_LEFT_SHADOW}, .${n("d5aTJ").TableCssClassName.TABLE_RIGHT_SHADOW} {
			width: ${n("eoFXy").tableOverflowShadowWidth}px;
		}

		.${n("d5aTJ").TableCssClassName.TABLE_LEFT_SHADOW} {
			left: 6px;
		}
		.${n("d5aTJ").TableCssClassName.TABLE_LEFT_SHADOW}.${n("d5aTJ").TableCssClassName.TABLE_CHROMELESS} {
			left: 8px;
		}

		.${n("d5aTJ").TableCssClassName.TABLE_RIGHT_SHADOW} {
			left: calc(100% - 6px);
		}
		.${n("d5aTJ").TableCssClassName.TABLE_RIGHT_SHADOW}.${n("d5aTJ").TableCssClassName.TABLE_CHROMELESS} {
			left: calc(100% - 16px);
		}
	}

	> .${n("d5aTJ").TableCssClassName.NODEVIEW_WRAPPER} {
		/**
       * Prevent margins collapsing, aids with placing the gap-cursor correctly
       * @see https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Box_Model/Mastering_margin_collapsing
       *
       * TODO: Enable this, many tests will fail!
       * border-top: 1px solid transparent;
       */
	}

	/* Breakout only works on top level unless wrapped in fragment mark */
	${m()}

	${(0,n("gvjT6").columnControlsDecoration)()};
	${(0,n("gvjT6").rowControlsWrapperDotStyle)()};

	/* Corner controls */
	.${n("d5aTJ").TableCssClassName.CORNER_CONTROLS} {
		width: ${n("eoFXy").tableToolbarSize+1}px;
		height: ${o}px;
		display: none;

		.${n("d5aTJ").TableCssClassName.CORNER_CONTROLS_INSERT_ROW_MARKER} {
			position: relative;

			${(0,n("gvjT6").InsertMarker)(`
          left: -11px;
          top: 9px;
        `)};
		}
	}

	.${n("d5aTJ").TableCssClassName.CORNER_CONTROLS}.sticky {
		.${n("d5aTJ").TableCssClassName.CORNER_CONTROLS_INSERT_ROW_MARKER} {
			/* sticky row insert dot overlaps other row insert and messes things up */
			display: none !important;
		}
	}

	.${n("d5aTJ").TableCssClassName.CONTROLS_CORNER_BUTTON} {
		position: absolute;
		top: 0;
		width: ${n("eoFXy").tableToolbarSize+1}px;
		height: ${n("eoFXy").tableToolbarSize+1}px;
		border: 1px solid ${n("eoFXy").tableBorderColor};
		border-radius: 0;
		border-top-left-radius: ${n("eoFXy").tableBorderRadiusSize}px;
		background: ${n("eoFXy").tableHeaderCellBackgroundColor};
		box-sizing: border-box;
		padding: 0;
		:focus {
			outline: none;
		}
	}
	.active .${n("d5aTJ").TableCssClassName.CONTROLS_CORNER_BUTTON} {
		border-color: ${n("eoFXy").tableBorderSelectedColor};
		background: ${n("eoFXy").tableToolbarSelectedColor};
	}

	.${n("d5aTJ").TableCssClassName.TABLE_CONTAINER}[data-number-column='true'] {
		.${n("d5aTJ").TableCssClassName.CORNER_CONTROLS}, .${n("d5aTJ").TableCssClassName.CONTROLS_CORNER_BUTTON} {
			width: ${n("aFUXX").akEditorTableToolbarSize+n("aFUXX").akEditorTableNumberColumnWidth+1}px;
		}
		.${n("d5aTJ").TableCssClassName.ROW_CONTROLS} .${n("d5aTJ").TableCssClassName.CONTROLS_BUTTON} {
			border-right-width: 0;
		}
	}

	:not(.${n("d5aTJ").TableCssClassName.IS_RESIZING}) .${n("d5aTJ").TableCssClassName.CONTROLS_CORNER_BUTTON}:hover {
		border-color: ${n("eoFXy").tableBorderSelectedColor};
		background: ${n("eoFXy").tableToolbarSelectedColor};
		cursor: pointer;
	}

	:not(.${n("d5aTJ").TableCssClassName.IS_RESIZING})
		.${n("d5aTJ").TableCssClassName.CONTROLS_CORNER_BUTTON}.${n("d5aTJ").TableCssClassName.HOVERED_CELL_IN_DANGER} {
		border-color: ${n("eoFXy").tableBorderDeleteColor};
		background: ${n("eoFXy").tableToolbarDeleteColor};
	}

	/* Row controls */
	.${n("d5aTJ").TableCssClassName.ROW_CONTROLS} {
		width: ${n("eoFXy").tableToolbarSize}px;
		box-sizing: border-box;
		display: none;
		position: relative;

		${(0,n("gvjT6").InsertMarker)(`
        bottom: -1px;
        left: -11px;
      `)};

		.${n("d5aTJ").TableCssClassName.ROW_CONTROLS_INNER} {
			display: flex;
			flex-direction: column;
		}
		.${n("d5aTJ").TableCssClassName.ROW_CONTROLS_BUTTON_WRAP}:last-child > button {
			border-bottom-left-radius: ${n("eoFXy").tableBorderRadiusSize}px;
		}
		.${n("d5aTJ").TableCssClassName.ROW_CONTROLS_BUTTON_WRAP} {
			position: relative;
			margin-top: -1px;
		}
		.${n("d5aTJ").TableCssClassName.ROW_CONTROLS_BUTTON_WRAP}:hover,
			.${n("d5aTJ").TableCssClassName.ROW_CONTROLS_BUTTON_WRAP}.active,
			.${n("d5aTJ").TableCssClassName.CONTROLS_BUTTON}:hover {
			z-index: ${n("aFUXX").akEditorUnitZIndex};
		}

		${(0,n("gvjT6").HeaderButton)(`
        border-bottom: 1px solid ${n("eoFXy").tableBorderColor};
        border-right: 0px;
        border-radius: 0;
        height: 100%;
        width: ${n("eoFXy").tableToolbarSize}px;

        .${n("d5aTJ").TableCssClassName.CONTROLS_BUTTON_OVERLAY} {
          position: absolute;
          width: 30px;
          height: 50%;
          right: 0;
          bottom: 0;
        }
        .${n("d5aTJ").TableCssClassName.CONTROLS_BUTTON_OVERLAY}:first-of-type {
          top: 0;
        }
      `)}
	}

	.${n("d5aTJ").TableCssClassName.DRAG_ROW_CONTROLS} {
		display: grid;
		align-items: center;
		position: absolute;
		z-index: ${(0,n("dh538").fg)("platform_editor_table_column_selected_state_fix")?n("eoFXy").rowControlsZIndex+4:n("aFUXX").akEditorUnitZIndex};

		.${n("d5aTJ").TableCssClassName.DRAG_ROW_FLOATING_INSERT_DOT_WRAPPER} {
			position: absolute;
			align-self: end;
			height: 100%;
			width: 18px;
		}

		.${n("d5aTJ").TableCssClassName.DRAG_ROW_FLOATING_INSERT_DOT} {
			position: absolute;
			bottom: -3px;
			left: 2px;
			background-color: ${"var(--ds-background-accent-gray-subtler, #C1C7D0)"};
			height: 4px;
			width: 4px;
			border-radius: 50%;
			pointer-events: none;
		}
	}

	.${n("d5aTJ").TableCssClassName.DRAG_COLUMN_CONTROLS} {
		.${n("d5aTJ").TableCssClassName.DRAG_COLUMN_CONTROLS_INNER} {
			height: 24px;
			position: absolute;
			top: ${"var(--ds-space-negative-150, -12px)"};
			z-index: ${n("eoFXy").resizeHandlerZIndex};
		}

		.${n("d5aTJ").TableCssClassName.DRAG_COLUMN_FLOATING_INSERT_DOT_WRAPPER} {
			position: absolute;
			height: 24px;
			width: 100%;
		}

		.${n("d5aTJ").TableCssClassName.DRAG_COLUMN_FLOATING_INSERT_DOT} {
			background-color: ${"var(--ds-background-accent-gray-subtler, #C1C7D0)"};
			height: 4px;
			width: 4px;
			border-radius: 50%;
			position: absolute;
			right: -2px;
		}
	}

	.${n("d5aTJ").TableCssClassName.DRAG_HANDLE_BUTTON_CLICKABLE_ZONE} {
		background: none;
		border: none;
		outline: none;
		position: absolute;
		margin: 0;
		padding: 0;
		display: flex;
		align-items: center;
		cursor: pointer;

		:focus {
			outline: none;
		}
	}

	.${n("d5aTJ").TableCssClassName.DRAG_HANDLE_BUTTON_CONTAINER} {
		cursor: grab;
		pointer-events: auto;

		line-height: 0;
		padding: 0;
		border-radius: 6px;
		width: max-content;
		border: 2px solid ${`var(--ds-surface, ${n("6fnsQ").N0})`};

		display: flex;
		justify-content: center;
		align-items: center;
		background: transparent;
		outline: none;

		&.placeholder {
			background-color: transparent;
			border: 2px solid transparent;
		}

		&.${n("d5aTJ").TableCssClassName.DRAG_HANDLE_DISABLED} {
			cursor: pointer;
			& svg {
				& > rect.${n("d5aTJ").TableCssClassName.DRAG_HANDLE_MINIMISED} {
					fill: ${"var(--ds-background-accent-gray-subtler, #DCDFE4)"};
				}
				& > rect {
					fill: ${"var(--ds-background-accent-gray-subtlest, #F4F5F7)"};
				}
				& > g > rect {
					fill: ${"var(--ds-icon-disabled, #BFDBF847)"};
				}
			}
		}

		&:not(.${n("d5aTJ").TableCssClassName.DRAG_HANDLE_DISABLED}) {
			& svg {
				rect {
					fill: ${"var(--ds-background-accent-gray-subtler, #DCDFE4)"};
				}
				g {
					fill: ${"var(--ds-icon-subtle, #626f86)"};
				}
			}

			&:hover {
				svg {
					rect {
						fill: ${"var(--ds-background-accent-blue-subtle, #579DFF)"};
					}
					g {
						fill: ${"var(--ds-icon-inverse, #FFF)"};
					}
				}
			}

			&:active {
				cursor: grabbing;
			}

			&.selected {
				:focus {
					outline: 2px solid ${"var(--ds-border-focused, #2684FF)"};
					outline-offset: 1px;
				}

				&:active {
					outline: none;
				}

				svg {
					rect {
						fill: ${"var(--ds-background-accent-blue-subtle, #579dff)"};
					}
					g {
						fill: ${"var(--ds-icon-inverse, #fff)"};
					}
				}
			}

			&.danger {
				svg {
					rect {
						fill: ${"var(--ds-background-accent-red-subtler-pressed, #F87462)"};
					}
					g {
						fill: ${"var(--ds-border-inverse, #FFF)"};
					}
				}
			}
		}
	}

	${(0,n("gvjT6").floatingColumnControls)()}

	:not(.${n("d5aTJ").TableCssClassName.IS_RESIZING}) .${n("d5aTJ").TableCssClassName.ROW_CONTROLS} {
		${(0,n("gvjT6").HeaderButtonHover)()}
		${(0,n("gvjT6").HeaderButtonDanger)()}
	}

	/* Numbered column */
	.${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN} {
		position: relative;
		float: right;
		margin-left: ${n("aFUXX").akEditorTableToolbarSize}px;
		top: ${((0,n("dh538").fg)("platform_editor_number_column_sticky_header_broken")?e.isDragAndDropEnabled:e.featureFlags?.tableDragAndDrop)||(0,a.editorExperiment)("support_table_in_comment_jira",!0)?0:n("aFUXX").akEditorTableToolbarSize}px;
		width: ${n("aFUXX").akEditorTableNumberColumnWidth+1}px;
		box-sizing: border-box;
	}

	.${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN_BUTTON} {
		border: 1px solid ${n("eoFXy").tableBorderColor};
		box-sizing: border-box;
		margin-top: -1px;
		padding-bottom: 2px;
		padding: 10px 2px;
		text-align: center;
		font-size: ${(0,n("aFUXX").relativeFontSizeToBase16)(14)};
		background-color: ${n("eoFXy").tableHeaderCellBackgroundColor};
		color: ${n("eoFXy").tableTextColor};
		border-color: ${n("eoFXy").tableBorderColor};

		:first-child:not(style),
		style:first-child + * {
			margin-top: 0;
		}
		:last-child {
			border-bottom: 1px solid ${n("eoFXy").tableBorderColor};
		}
	}

	/* add a background above the first numbered column cell when sticky header is engaged
	which hides the table when scrolling */
	${(0,n("dh538").fg)("platform_editor_nested_tables_sticky_header_bug")?`
		${(0,n("dh538").fg)("platform_editor_number_column_sticky_header_broken")?`.${n("d5aTJ").TableCssClassName.TABLE_STICKY} > .${e.isDragAndDropEnabled?n("d5aTJ").TableCssClassName.DRAG_ROW_CONTROLS_WRAPPER:n("d5aTJ").TableCssClassName.ROW_CONTROLS_WRAPPER} {
				.${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN_BUTTON_DISABLED}:first-of-type::after {`:`.${n("d5aTJ").TableCssClassName.TABLE_STICKY} > .${n("d5aTJ").TableCssClassName.DRAG_ROW_CONTROLS_WRAPPER} {
				.${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN_BUTTON_DISABLED}:first-of-type::after {`}
				content: '';
				display: block;
				height: 33px;
				width: 100%;
				background-color: var(--ds-surface, white);
				position: absolute;

				/* the extra pixel is accounting for borders */
				top: -34px;
				left: -1px;
			}
		}
		`:`
		.${n("d5aTJ").TableCssClassName.TABLE_STICKY} {
			.${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN_BUTTON_DISABLED}:first-of-type::after {
				content: '';
				display: block;
				height: 33px;
				width: 100%;
				background-color: var(--ds-surface, white);
				position: absolute;

				/* the extra pixel is accounting for borders */
				top: -34px;
				left: -1px;
			}
		}
		`}

	.${n("d5aTJ").TableCssClassName.WITH_CONTROLS} {
		.${n("d5aTJ").TableCssClassName.CORNER_CONTROLS}, .${n("d5aTJ").TableCssClassName.ROW_CONTROLS} {
			display: block;
		}
		.${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN} {
			padding-left: 0px;

			.${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN_BUTTON} {
				border-left: 0 none;
			}

			.${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN_BUTTON}.active {
				border-bottom: 1px solid ${n("eoFXy").tableBorderSelectedColor};
				border-color: ${n("eoFXy").tableBorderSelectedColor};
				background-color: ${n("eoFXy").tableToolbarSelectedColor};
				position: relative;
				z-index: ${n("aFUXX").akEditorUnitZIndex};
				color: ${`var(--ds-text-selected, ${n("6fnsQ").N0})`};
			}
		}

		/* nested tables should be ignored when we apply border-left: 0 to the parent table */
		.${n("d5aTJ").TableCssClassName.TABLE_CONTAINER} {
			.${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN_BUTTON} {
				border-left: 1px solid ${n("eoFXy").tableBorderColor};
			}
		}
	}
	:not(.${n("d5aTJ").TableCssClassName.IS_RESIZING}) .${n("d5aTJ").TableCssClassName.WITH_CONTROLS} {
		.${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN_BUTTON}:not(.${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN_BUTTON_DISABLED}) {
			cursor: pointer;
		}
		.${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN_BUTTON}:not(.${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN_BUTTON_DISABLED}):hover {
			border-bottom: 1px solid ${n("eoFXy").tableBorderSelectedColor};
			border-color: ${n("eoFXy").tableBorderSelectedColor};
			background-color: ${n("eoFXy").tableToolbarSelectedColor};
			position: relative;
			z-index: ${n("aFUXX").akEditorUnitZIndex};
			color: ${`var(--ds-text-selected, ${n("6fnsQ").N0})`};
		}
		.${n("d5aTJ").TableCssClassName.NUMBERED_COLUMN_BUTTON}.${n("d5aTJ").TableCssClassName.HOVERED_CELL_IN_DANGER} {
			background-color: ${n("eoFXy").tableToolbarDeleteColor};
			border: 1px solid ${n("eoFXy").tableBorderDeleteColor};
			border-left: 0;
			color: ${`var(--ds-text-danger, ${n("6fnsQ").R500})`};
			position: relative;
			z-index: ${n("aFUXX").akEditorUnitZIndex};
		}
	}

	/* Table */
	.${n("d5aTJ").TableCssClassName.TABLE_NODE_WRAPPER} > table {
		table-layout: fixed;
		white-space: normal;
		border-top: none;
		/* 1px border width offset added here to prevent unwanted overflow and scolling - ED-16212 */
		margin-right: -1px;
		/* Allows better positioning for the shadow sentinels - ED-16668 */
		position: relative;

		> tbody > tr {
			white-space: pre-wrap;
		}

		.${n("d5aTJ").TableCssClassName.COLUMN_CONTROLS_DECORATIONS} + * {
			margin-top: 0;
		}

		/*
       * Headings have a top margin by default, but we don't want this on the
       * first heading within table header cells.
       *
       * This specifically sets margin-top for the first heading within a header
       * cell when center/right aligned.
       */
		th.${n("d5aTJ").TableCssClassName.TABLE_HEADER_CELL} > .fabric-editor-block-mark {
			> h1:first-of-type,
			> h2:first-of-type,
			> h3:first-of-type,
			> h4:first-of-type,
			> h5:first-of-type,
			> h6:first-of-type {
				margin-top: 0;
			}
		}

		.${n("d5aTJ").TableCssClassName.SELECTED_CELL}, .${n("d5aTJ").TableCssClassName.HOVERED_CELL_IN_DANGER} {
			position: relative;
		}
		/* Give selected cells a blue overlay */
		.${n("d5aTJ").TableCssClassName.SELECTED_CELL}::after, .${n("d5aTJ").TableCssClassName.HOVERED_CELL_IN_DANGER}::after {
			z-index: ${n("aFUXX").akEditorSmallZIndex};
			position: absolute;
			content: '';
			left: 0;
			right: 0;
			top: 0;
			bottom: 0;
			width: 100%;
			pointer-events: none;
		}
		.${n("d5aTJ").TableCssClassName.SELECTED_CELL} {
			border: 1px solid ${n("eoFXy").tableBorderSelectedColor};
		}
		.${n("d5aTJ").TableCssClassName.SELECTED_CELL}::after {
			background: ${n("eoFXy").tableCellSelectedColor};
			z-index: ${n("aFUXX").akEditorSmallZIndex};
		}
		th.${n("d5aTJ").TableCssClassName.HOVERED_CELL_IN_DANGER}::after, td.${n("d5aTJ").TableCssClassName.HOVERED_CELL_IN_DANGER}::after {
			background: ${n("eoFXy").tableCellDeleteColor};
			z-index: ${100*n("aFUXX").akEditorUnitZIndex};
		}
		td.${n("d5aTJ").TableCssClassName.HOVERED_CELL},
			td.${n("d5aTJ").TableCssClassName.SELECTED_CELL},
			th.${n("d5aTJ").TableCssClassName.TABLE_HEADER_CELL}.${n("d5aTJ").TableCssClassName.SELECTED_CELL},
			th.${n("d5aTJ").TableCssClassName.TABLE_HEADER_CELL}.${n("d5aTJ").TableCssClassName.HOVERED_CELL} {
			&::after {
				height: 100%;
				width: 100%;
				border: 1px solid ${n("eoFXy").tableBorderSelectedColor};
				content: '';
				position: absolute;
				left: -1px;
				top: -1px;
				bottom: 0;
				z-index: ${n("aFUXX").akEditorSmallZIndex};
				display: inline-block;
				pointer-events: none;
			}
			&.${n("d5aTJ").TableCssClassName.HOVERED_CELL_IN_DANGER}::after {
				${g()};
				z-index: ${100*n("aFUXX").akEditorUnitZIndex};
			}

			&.${n("d5aTJ").TableCssClassName.HOVERED_NO_HIGHLIGHT}.${n("d5aTJ").TableCssClassName.HOVERED_CELL_IN_DANGER}::after {
				${g()};
				z-index: ${100*n("aFUXX").akEditorUnitZIndex};
			}
		}
	}

	/* override for DnD controls */
	.${n("d5aTJ").TableCssClassName.DRAG_ROW_CONTROLS_WRAPPER} {
		position: absolute;
		margin-top: ${n("1zav4").tableMarginTop}px;
		left: -${n("eoFXy").tableToolbarSize+1}px;
		${(0,n("dh538").fg)("platform_editor_table_column_selected_state_fix")?"":`z-index: ${n("eoFXy").rowControlsZIndex+4}`}
	}

	.${n("d5aTJ").TableCssClassName.ROW_CONTROLS_WRAPPER} {
		position: absolute;
		/* this is to fix the misalignment of the numbered column in live page view mode */
		${e.isDragAndDropEnabled&&(0,n("dh538").fg)("platform_editor_numbered_column_misalignment")?`
			margin-top: ${n("1zav4").tableMarginTop}px;
			top: 0;
			left: -${n("eoFXy").tableToolbarSize+1}px;
		`:`
			/* top of corner control is table margin top - corner control height + 1 pixel of table border. */
			top: ${n("1zav4").tableMarginTop-o+1}px;
			margin-top: 0;
			left: -${n("eoFXy").tableToolbarSize}px;
		`}
	}

	.${n("d5aTJ").TableCssClassName.DRAG_ROW_CONTROLS_WRAPPER}.${n("d5aTJ").TableCssClassName.TABLE_LEFT_SHADOW},
		.${n("d5aTJ").TableCssClassName.ROW_CONTROLS_WRAPPER}.${n("d5aTJ").TableCssClassName.TABLE_LEFT_SHADOW} {
		z-index: ${n("aFUXX").akEditorUnitZIndex};
	}

	.${n("d5aTJ").TableCssClassName.DRAG_COLUMN_CONTROLS_WRAPPER} {
		position: absolute;
		top: ${n("1zav4").tableMarginTop}px;
	}

	.${n("d5aTJ").TableCssClassName.TABLE_STICKY} .${n("d5aTJ").TableCssClassName.DRAG_COLUMN_CONTROLS_WRAPPER} {
		position: fixed;
		/* higher zIndex than sticky header which is akEditorTableCellOnStickyHeaderZIndex - 5 */
		z-index: ${n("aFUXX").akEditorTableCellOnStickyHeaderZIndex-4};
	}

	/* nested tables */
	${(0,n("dh538").fg)("platform_editor_nested_table_drag_controls")?`
		.${n("d5aTJ").TableCssClassName.TABLE_CONTAINER} {
			.${n("d5aTJ").TableCssClassName.TABLE_STICKY} .${n("d5aTJ").TableCssClassName.DRAG_COLUMN_CONTROLS_WRAPPER} {
				position: absolute;
				z-index: ${n("aFUXX").akEditorUnitZIndex};
			}
		}
		`:""}

	.${n("d5aTJ").TableCssClassName.TABLE_NODE_WRAPPER} {
		padding-bottom: 0px;
		/* fixes gap cursor height */
		overflow: auto;
		overflow-y: hidden;
		position: relative;
	}
`,v=e=>(0,n("3jLHL").css)`
	.ProseMirror {
		${x(e)}
	}

	.ProseMirror.${n("d5aTJ").TableCssClassName.IS_RESIZING} {
		.${n("d5aTJ").TableCssClassName.TABLE_NODE_WRAPPER} {
			overflow-x: auto;
			${n("26eEE").scrollbarStyles};
		}
	}

	.ProseMirror.${n("d5aTJ").TableCssClassName.RESIZE_CURSOR} {
		cursor: col-resize;
	}

	${u}
`,y=(0,n("3jLHL").css)`
	.ProseMirror .${n("d5aTJ").TableCssClassName.TABLE_NODE_WRAPPER} > table {
		margin-left: 0;
		/* 1px border width offset added here to prevent unwanted overflow and scolling - ED-16212 */
		margin-right: -1px;
		width: 100%;
	}
`,E=(0,n("3jLHL").css)`
	.ProseMirror .${n("d5aTJ").TableCssClassName.TABLE_NODE_WRAPPER} > table {
		margin-left: 0;
		margin-right: 0;
		${n("26eEE").scrollbarStyles};
	}
`}),i("5p8Hs",function(t,r){e(t.exports,"SORTING_ICON_CLASS_NAME",()=>a),e(t.exports,"IS_DISABLED_CLASS_NAME",()=>o),e(t.exports,"SORT_INDEX_DATA_ATTRIBUTE",()=>n);let a="view-mode-sorting-icon",o="is-disabled",n="data-sort-index"}),i("gvjT6",function(t,r){e(t.exports,"InsertMarker",()=>i),e(t.exports,"HeaderButton",()=>d),e(t.exports,"HeaderButtonHover",()=>l),e(t.exports,"HeaderButtonDanger",()=>c),e(t.exports,"dragInsertButtonWrapper",()=>m),e(t.exports,"dragCornerControlButton",()=>h),e(t.exports,"insertColumnButtonWrapper",()=>g),e(t.exports,"insertRowButtonWrapper",()=>b),e(t.exports,"columnControlsLineMarker",()=>f),e(t.exports,"DeleteButton",()=>x),e(t.exports,"OverflowShadow",()=>v),e(t.exports,"floatingColumnControls",()=>k),e(t.exports,"rowControlsWrapperDotStyle",()=>T),e(t.exports,"columnControlsDecoration",()=>w),e(t.exports,"hoveredDeleteButton",()=>_),e(t.exports,"hoveredCell",()=>N),e(t.exports,"hoveredWarningCell",()=>L),e(t.exports,"resizeHandle",()=>R),e(t.exports,"insertLine",()=>O);let a=e=>(0,n("3jLHL").css)`
	.${n("d5aTJ").TableCssClassName.CONTROLS_INSERT_LINE} {
		background: ${n("eoFXy").tableBorderSelectedColor};
		display: none;
		position: absolute;
		z-index: ${n("aFUXX").akEditorUnitZIndex};
		${e}
	}
`,o=()=>(0,n("3jLHL").css)({backgroundColor:n("eoFXy").tableBorderColor,position:"absolute",height:`${n("eoFXy").lineMarkerSize}px`,width:`${n("eoFXy").lineMarkerSize}px`,borderRadius:"50%",pointerEvents:"none"}),i=e=>(0,n("3jLHL").css)`
	.${n("d5aTJ").TableCssClassName.CONTROLS_INSERT_MARKER} {
		${o()};
		${e}
	}
`,s=e=>(0,n("3jLHL").css)`
	border-radius: ${"var(--ds-border-radius, 3px)"};
	border-width: 0px;
	display: inline-flex;
	max-width: 100%;
	text-align: center;
	margin: 0px;
	padding: 0px;
	text-decoration: none;
	transition:
		background 0.1s ease-out 0s,
		box-shadow 0.15s cubic-bezier(0.47, 0.03, 0.49, 1.38) 0s;
	outline: none !important;
	cursor: none;

	> .${n("d5aTJ").TableCssClassName.CONTROLS_BUTTON_ICON} {
		display: inline-flex;
		max-height: 100%;
		max-width: 100%;
	}
	${e}
`,d=e=>(0,n("3jLHL").css)`
	.${n("d5aTJ").TableCssClassName.CONTROLS_BUTTON} {
		background: ${n("eoFXy").tableHeaderCellBackgroundColor};
		border: 1px solid ${n("eoFXy").tableBorderColor};
		display: block;
		box-sizing: border-box;
		padding: 0;

		:focus {
			outline: none;
		}
		${e}
	}

	.${n("d5aTJ").TableCssClassName.ROW_CONTROLS_BUTTON}::after {
		content: ' ';
		background-color: transparent;
		left: -15px;
		top: 0;
		position: absolute;
		width: 15px;
		height: 100%;
		z-index: 1;
	}

	.active .${n("d5aTJ").TableCssClassName.CONTROLS_BUTTON} {
		color: ${`var(--ds-icon-inverse, ${n("6fnsQ").N0})`};
		background-color: ${n("eoFXy").tableToolbarSelectedColor};
		border-color: ${n("eoFXy").tableBorderSelectedColor};
	}
`,l=()=>(0,n("3jLHL").css)`
	.${n("d5aTJ").TableCssClassName.CONTROLS_BUTTON}:hover {
		color: ${`var(--ds-icon-inverse, ${n("6fnsQ").N0})`};
		background-color: ${n("eoFXy").tableToolbarSelectedColor};
		border-color: ${n("eoFXy").tableBorderSelectedColor};
		cursor: pointer;
	}
`,c=()=>(0,n("3jLHL").css)`
	.${n("d5aTJ").TableCssClassName.HOVERED_CELL_IN_DANGER} .${n("d5aTJ").TableCssClassName.CONTROLS_BUTTON} {
		background-color: ${n("eoFXy").tableToolbarDeleteColor};
		border-color: ${n("eoFXy").tableBorderDeleteColor};
		position: relative;
		z-index: ${n("aFUXX").akEditorUnitZIndex};
	}
`,p=()=>(0,n("3jLHL").css)`
	.${n("d5aTJ").TableCssClassName.CONTROLS_INSERT_BUTTON_INNER} {
		position: absolute;
		z-index: ${n("aFUXX").akEditorUnitZIndex+10};
		bottom: 0;
	}
	.${n("d5aTJ").TableCssClassName.CONTROLS_INSERT_BUTTON_INNER}, .${n("d5aTJ").TableCssClassName.CONTROLS_INSERT_BUTTON} {
		height: ${n("eoFXy").tableInsertColumnButtonSize}px;
		width: ${n("eoFXy").tableInsertColumnButtonSize}px;
	}
	.${n("d5aTJ").TableCssClassName.CONTROLS_INSERT_BUTTON} {
		${s(`
      background: var(--ds-surface-overlay, white);
      box-shadow: var(--ds-shadow-overlay, 0 4px 8px -2px ${n("6fnsQ").N60A}, 0 0 1px ${n("6fnsQ").N60A});
      color: var(--ds-icon, ${n("6fnsQ").N300});
    `)}
	}
	.${n("d5aTJ").TableCssClassName.CONTROLS_INSERT_LINE} {
		display: none;
	}
	&:hover .${n("d5aTJ").TableCssClassName.CONTROLS_INSERT_LINE} {
		display: flex;
	}
`,u=()=>(0,n("3jLHL").css)`
	.${n("d5aTJ").TableCssClassName.CONTROLS_INSERT_BUTTON}:hover {
		background: ${`var(--ds-background-brand-bold, ${n("6fnsQ").B300})`};
		color: ${"var(--ds-icon-inverse, white)"};
		cursor: pointer;
	}
`,m=()=>(0,n("3jLHL").css)`
	.${n("d5aTJ").TableCssClassName.DRAG_CONTROLS_INSERT_BUTTON_INNER} {
		position: absolute;
		z-index: ${n("aFUXX").akEditorUnitZIndex+10};
	}

	.${n("d5aTJ").TableCssClassName.DRAG_CONTROLS_INSERT_BUTTON_INNER_COLUMN} {
		bottom: -3px;
		left: 2px;
	}

	.${n("d5aTJ").TableCssClassName.DRAG_CONTROLS_INSERT_BUTTON_INNER_ROW} {
		left: -3px;
		bottom: -2px;
	}
	.${n("d5aTJ").TableCssClassName.DRAG_CONTROLS_INSERT_BUTTON_INNER_ROW_CHROMELESS} {
		left: 6px;
		bottom: -2px;
	}

	.${n("d5aTJ").TableCssClassName.DRAG_CONTROLS_INSERT_BUTTON} {
		${s(`
    background: var(--ds-surface-overlay, white);
    color: var(--ds-icon, ${n("6fnsQ").N300});
    border: 1px solid var(--ds-background-accent-gray-subtler, #C1C7D0);
    border-radius: 50%;
    height: ${n("eoFXy").dragTableInsertColumnButtonSize}px;
    width: ${n("eoFXy").dragTableInsertColumnButtonSize}px;
  `)}
	}

	.${n("d5aTJ").TableCssClassName.DRAG_CONTROLS_INSERT_BUTTON}:hover {
		background: ${`var(--ds-background-brand-bold, ${n("6fnsQ").B300})`};
		border: 1px solid ${`var(--ds-background-brand-bold, ${n("6fnsQ").B300})`};
		color: ${"var(--ds-icon-inverse, white)"};
		cursor: pointer;
	}
`,h=()=>(0,n("3jLHL").css)`
	.${n("d5aTJ").TableCssClassName.DRAG_CORNER_BUTTON} {
		width: 15px;
		height: 15px;
		display: flex;
		justify-content: center;
		align-items: center;
		position: absolute;
		top: -17px;
		left: -5px;
		background-color: transparent;
		border: none;
		padding: 0;
		outline: none;
		z-index: ${99*n("aFUXX").akEditorUnitZIndex};

		&.active .${n("d5aTJ").TableCssClassName.DRAG_CORNER_BUTTON_INNER} {
			background-color: ${"var(--ds-border-selected, #0C66E4)"};
			width: 10px;
			height: 10px;
			border-width: 2px;
			border-radius: 4px;

			top: 3px;
			left: 2px;
		}

		&:hover {
			cursor: pointer;

			.${n("d5aTJ").TableCssClassName.DRAG_CORNER_BUTTON_INNER} {
				width: 10px;
				height: 10px;
				border-radius: 4px;
				top: 3px;
				left: 2px;
			}
		}
	}

	.${n("d5aTJ").TableCssClassName.DRAG_CORNER_BUTTON_INNER} {
		border: 1px solid ${"var(--ds-border-inverse, #FFF)"};
		background-color: ${"var(--ds-background-accent-gray-subtler, #DCDFE4)"};
		border-radius: 2px;
		width: 5px;
		height: 5px;
		position: relative;
	}
`,g=()=>(0,n("3jLHL").css)(p(),u(),a(`
    width: 2px;
    left: 9px;
  `)),b=()=>(0,n("3jLHL").css)(p(),u(),a(`
    height: 2px;
    top: -11px;
	
    left: ${n("eoFXy").tableInsertColumnButtonSize-1}px;
  `)),f=()=>(0,n("3jLHL").css)`
	.${n("d5aTJ").TableCssClassName.TABLE_CONTAINER}.${n("d5aTJ").TableCssClassName.WITH_CONTROLS} table tr:first-of-type td,
	.${n("d5aTJ").TableCssClassName.TABLE_CONTAINER}.${n("d5aTJ").TableCssClassName.WITH_CONTROLS} table tr:first-of-type th {
		position: relative;
	}
`,x=()=>(0,n("3jLHL").css)`
	.${n("d5aTJ").TableCssClassName.CONTROLS_DELETE_BUTTON_WRAP}, .${n("d5aTJ").TableCssClassName.CONTROLS_DELETE_BUTTON} {
		height: ${n("eoFXy").tableDeleteButtonSize}px;
		width: ${n("eoFXy").tableDeleteButtonSize}px;
	}
	.${n("d5aTJ").TableCssClassName.CONTROLS_DELETE_BUTTON_WRAP} {
		.${n("d5aTJ").TableCssClassName.CONTROLS_DELETE_BUTTON} {
			${s(`
        background: ${n("eoFXy").tableCellSelectedDeleteIconBackground};
        color: ${n("eoFXy").tableCellSelectedDeleteIconColor};
      `)}
		}
	}

	.${n("d5aTJ").TableCssClassName.CONTROLS_DELETE_BUTTON}:hover {
		background: ${n("eoFXy").tableCellHoverDeleteIconBackground};
		color: ${n("eoFXy").tableCellHoverDeleteIconColor};
		cursor: pointer;
	}
`,v=e=>(0,n("3jLHL").css)`
	.${n("d5aTJ").TableCssClassName.TABLE_RIGHT_SHADOW}, .${n("d5aTJ").TableCssClassName.TABLE_LEFT_SHADOW} {
		display: block;
		height: calc(100% - ${n("1zav4").tableMarginTop}px);
		position: absolute;
		pointer-events: none;
		top: ${n("1zav4").tableMarginTop}px;
		z-index: ${n("aFUXX").akEditorShadowZIndex};
		width: ${n("eoFXy").tableOverflowShadowWidthWide}px;
	}
	.${n("d5aTJ").TableCssClassName.TABLE_LEFT_SHADOW} {
		background: linear-gradient(
				to left,
				transparent 0,
				${`var(--ds-shadow-overflow-spread, ${n("6fnsQ").N40A})`} 140%
			),
			linear-gradient(
				to right,
				${"var(--ds-shadow-overflow-perimeter, transparent)"} 0px,
				transparent 1px
			);
		left: 0px;
	}
	.${n("d5aTJ").TableCssClassName.TABLE_CONTAINER}[data-number-column='true'] > :not(.${n("d5aTJ").TableCssClassName.TABLE_STICKY_SHADOW}).${n("d5aTJ").TableCssClassName.TABLE_LEFT_SHADOW} {
		left: ${n("aFUXX").akEditorTableNumberColumnWidth-1}px;
	}
	.${n("d5aTJ").TableCssClassName.TABLE_RIGHT_SHADOW} {
		background: linear-gradient(
				to right,
				transparent 0,
				${`var(--ds-shadow-overflow-spread, ${n("6fnsQ").N40A})`} 140%
			),
			linear-gradient(
				to left,
				${"var(--ds-shadow-overflow-perimeter, transparent)"} 0px,
				transparent 1px
			);
		left: calc(100% - ${n("eoFXy").tableOverflowShadowWidthWide}px);
	}
	.${n("d5aTJ").TableCssClassName.WITH_CONTROLS} {
		${y(e)}
		.${n("d5aTJ").TableCssClassName.TABLE_LEFT_SHADOW} {
			border-left: 1px solid ${n("eoFXy").tableBorderColor};
		}
	}
`,y=e=>{if(!e)return(0,n("3jLHL").css)`
			.${n("d5aTJ").TableCssClassName.TABLE_RIGHT_SHADOW}, .${n("d5aTJ").TableCssClassName.TABLE_LEFT_SHADOW} {
				height: calc(100% - ${n("1zav4").tableMarginTopWithControl}px);
				top: ${n("1zav4").tableMarginTopWithControl}px;
			}
		`},E=e=>(0,n("3jLHL").css)({background:n("eoFXy").tableHeaderCellBackgroundColor,display:"block",boxSizing:"border-box",padding:0,":focus":{outline:"none"}},e),S=()=>(0,n("3jLHL").css)({color:`var(--ds-text-inverse, ${n("6fnsQ").N0})`,backgroundColor:n("eoFXy").tableToolbarSelectedColor,borderColor:n("eoFXy").tableBorderSelectedColor,zIndex:n("eoFXy").columnControlsSelectedZIndex}),C=()=>(0,n("3jLHL").css)`
		tr
			th:last-child
			.${n("d5aTJ").TableCssClassName.COLUMN_CONTROLS_DECORATIONS}::before,
			tr
			td:last-child
			.${n("d5aTJ").TableCssClassName.COLUMN_CONTROLS_DECORATIONS}::before {
			content: '';
			background-color: ${n("eoFXy").tableBorderColor};
			position: absolute;
			height: ${n("eoFXy").lineMarkerSize}px;
			width: ${n("eoFXy").lineMarkerSize}px;
			border-radius: 50%;
			pointer-events: none;
			top: ${"var(--ds-space-025, 2px)"};
			right: 0px;
		}
	`,k=()=>(0,n("3jLHL").css)`
		.${n("d5aTJ").TableCssClassName.DRAG_COLUMN_DROP_TARGET_CONTROLS} {
			box-sizing: border-box;
			position: absolute;
			top: 0;

			.${n("d5aTJ").TableCssClassName.DRAG_COLUMN_CONTROLS_INNER} {
				display: flex;
				flex-direction: row;
			}
		}

		.${n("d5aTJ").TableCssClassName.DRAG_COLUMN_CONTROLS} {
			box-sizing: border-box;

			.${n("d5aTJ").TableCssClassName.DRAG_COLUMN_CONTROLS_INNER} {
				display: grid;
				justify-items: center;
			}
		}
	`,T=()=>(0,n("3jLHL").css)`
		/* override for DnD controls */
		div.${n("d5aTJ").TableCssClassName.WITH_CONTROLS}>.${n("d5aTJ").TableCssClassName.DRAG_ROW_CONTROLS_WRAPPER}::after {
			display: none;
		}

		div.${n("d5aTJ").TableCssClassName.WITH_CONTROLS}>.${n("d5aTJ").TableCssClassName.ROW_CONTROLS_WRAPPER}::after {
			content: ' ';
			background-color: ${n("eoFXy").tableBorderColor};
			position: absolute;
			height: ${n("eoFXy").lineMarkerSize}px;
			width: ${n("eoFXy").lineMarkerSize}px;
			border-radius: 50%;
			pointer-events: none;
			top: -${n("eoFXy").tableToolbarSize+n("1zav4").tableCellBorderWidth}px;
			right: -1px;
		}
	`,w=()=>(0,n("3jLHL").css)`
		.${n("d5aTJ").TableCssClassName.COLUMN_CONTROLS_DECORATIONS} {
			display: none;
			cursor: pointer;
			position: absolute;
			width: 100%;
			left: 0;
			top: -${n("eoFXy").columnControlsDecorationHeight+n("1zav4").tableCellBorderWidth}px;
			height: ${n("eoFXy").columnControlsDecorationHeight}px;
			/* floating dot for adding column button */
			&::before {
				content: ' ';
				background-color: ${n("eoFXy").tableBorderColor};
				position: absolute;
				height: ${n("eoFXy").lineMarkerSize}px;
				width: ${n("eoFXy").lineMarkerSize}px;
				border-radius: 50%;
				pointer-events: none;
				top: 2px;
				right: ${"var(--ds-space-negative-025, -2px)"};
			}

			&::after {
				content: ' ';

				${E(`
        border-right: ${n("1zav4").tableCellBorderWidth}px solid ${n("eoFXy").tableBorderColor};
        border-top: ${n("1zav4").tableCellBorderWidth}px solid ${n("eoFXy").tableBorderColor};
        border-bottom: ${n("1zav4").tableCellBorderWidth}px solid ${n("eoFXy").tableBorderColor};
        box-sizing: content-box;
        height: ${n("eoFXy").tableToolbarSize-1}px;
        width: 100%;
        position: absolute;
        top: ${n("eoFXy").columnControlsDecorationHeight-n("eoFXy").tableToolbarSize}px;
        left: 0px;
        z-index: ${n("eoFXy").columnControlsZIndex};
      `)}
			}
		}

		/* floating dot for adding column button - overriding style on last column to avoid scroll */
		${C()}

		.${n("d5aTJ").TableCssClassName.WITH_CONTROLS} .${n("d5aTJ").TableCssClassName.COLUMN_CONTROLS_DECORATIONS} {
			display: block;
		}

		table
			tr:first-of-type
			td.${n("d5aTJ").TableCssClassName.TABLE_CELL},table
			tr:first-of-type
			th.${n("d5aTJ").TableCssClassName.TABLE_HEADER_CELL} {
			&.${n("d5aTJ").TableCssClassName.COLUMN_SELECTED}, &.${n("d5aTJ").TableCssClassName.HOVERED_TABLE} {
				.${n("d5aTJ").TableCssClassName.COLUMN_CONTROLS_DECORATIONS}::after {
					${S()};
				}

				&.${n("d5aTJ").TableCssClassName.HOVERED_CELL_IN_DANGER} .${n("d5aTJ").TableCssClassName.COLUMN_CONTROLS_DECORATIONS}::after {
					background-color: ${n("eoFXy").tableToolbarDeleteColor};
					border-color: ${n("eoFXy").tableBorderDeleteColor};
					z-index: ${100*n("aFUXX").akEditorUnitZIndex};
				}
			}
		}

		table
			tr:first-of-type
			td.${n("d5aTJ").TableCssClassName.TABLE_CELL},table
			tr:first-of-type
			th.${n("d5aTJ").TableCssClassName.TABLE_HEADER_CELL} {
			&.${n("d5aTJ").TableCssClassName.COLUMN_SELECTED}, &.${n("d5aTJ").TableCssClassName.HOVERED_COLUMN} {
				.${n("d5aTJ").TableCssClassName.COLUMN_CONTROLS_DECORATIONS}::after {
					${S()};
					border-left: ${n("1zav4").tableCellBorderWidth}px solid ${n("eoFXy").tableBorderSelectedColor};
					left: -${n("1zav4").tableCellBorderWidth}px;
				}
			}
		}

		table
			tr:first-of-type
			td.${n("d5aTJ").TableCssClassName.TABLE_CELL},
			table
			tr:first-of-type
			th.${n("d5aTJ").TableCssClassName.TABLE_HEADER_CELL} {
			&.${n("d5aTJ").TableCssClassName.HOVERED_COLUMN} {
				.${n("d5aTJ").TableCssClassName.COLUMN_CONTROLS_DECORATIONS}::after {
					${S()};
				}

				&.${n("d5aTJ").TableCssClassName.HOVERED_CELL_IN_DANGER} .${n("d5aTJ").TableCssClassName.COLUMN_CONTROLS_DECORATIONS}::after {
					background-color: ${n("eoFXy").tableToolbarDeleteColor};
					border-color: ${n("eoFXy").tableBorderDeleteColor};
					border-left: ${n("1zav4").tableCellBorderWidth}px solid ${n("eoFXy").tableBorderDeleteColor};
					left: -${n("1zav4").tableCellBorderWidth}px;
					z-index: ${100*n("aFUXX").akEditorUnitZIndex};
				}
			}
		}

		.${n("d5aTJ").TableCssClassName.TABLE_SELECTED}
			table
			tr:first-of-type
			td.${n("d5aTJ").TableCssClassName.TABLE_CELL},
			.${n("d5aTJ").TableCssClassName.TABLE_SELECTED}
			table
			tr:first-of-type
			th.${n("d5aTJ").TableCssClassName.TABLE_HEADER_CELL} {
			.${n("d5aTJ").TableCssClassName.COLUMN_CONTROLS_DECORATIONS}::after {
				${S()};
			}
		}
	`,_=()=>(0,n("3jLHL").css)`
	.${n("d5aTJ").TableCssClassName.TABLE_CONTAINER}.${n("d5aTJ").TableCssClassName.HOVERED_DELETE_BUTTON} {
		.${n("d5aTJ").TableCssClassName.SELECTED_CELL}, .${n("d5aTJ").TableCssClassName.COLUMN_SELECTED}, .${n("d5aTJ").TableCssClassName.HOVERED_CELL} {
			border: 1px solid ${n("eoFXy").tableBorderDeleteColor};
		}
		.${n("d5aTJ").TableCssClassName.SELECTED_CELL}::after {
			background: ${n("eoFXy").tableCellDeleteColor};
		}

		.${n("d5aTJ").TableCssClassName.TABLE_NODE_WRAPPER} > table {
			td.${n("d5aTJ").TableCssClassName.HOVERED_NO_HIGHLIGHT}::after {
				background: ${n("eoFXy").tableCellDeleteColor};
				border: 1px solid ${n("eoFXy").tableBorderDeleteColor};
			}
			th.${n("d5aTJ").TableCssClassName.HOVERED_NO_HIGHLIGHT} {
				background-color: unset;
			}
			th.${n("d5aTJ").TableCssClassName.HOVERED_NO_HIGHLIGHT}::after {
				background: ${n("eoFXy").tableCellDeleteColor};
				border: 1px solid ${n("eoFXy").tableBorderDeleteColor};
			}
		}
	}
`,N=()=>(0,n("3jLHL").css)`
	:not(.${n("d5aTJ").TableCssClassName.IS_RESIZING})
		.${n("d5aTJ").TableCssClassName.TABLE_CONTAINER}:not(.${n("d5aTJ").TableCssClassName.HOVERED_DELETE_BUTTON}) {
		.${n("d5aTJ").TableCssClassName.HOVERED_CELL} {
			position: relative;
			border: 1px solid ${n("eoFXy").tableBorderSelectedColor};
		}
		.${n("d5aTJ").TableCssClassName.HOVERED_CELL}.${n("d5aTJ").TableCssClassName.HOVERED_NO_HIGHLIGHT} {
			position: relative;
			border: 1px solid ${n("eoFXy").tableBorderColor};
		}
	}
`,L=(0,n("3jLHL").css)`
	:not(.${n("d5aTJ").TableCssClassName.IS_RESIZING})
		.${n("d5aTJ").TableCssClassName.TABLE_CONTAINER}:not(.${n("d5aTJ").TableCssClassName.HOVERED_DELETE_BUTTON}) {
		td.${n("d5aTJ").TableCssClassName.HOVERED_CELL_WARNING} {
			background-color: ${`var(--ds-background-warning, ${n("6fnsQ").Y50})`} !important; /* We need to override the background-color added to the cell */
			border: 1px solid ${`var(--ds-border-warning, ${n("6fnsQ").Y200})`};
		}
	}
`,$=()=>(0,n("3jLHL").css)`
		th.${n("d5aTJ").TableCssClassName.WITH_DRAG_RESIZE_LINE}::before, td.${n("d5aTJ").TableCssClassName.WITH_DRAG_RESIZE_LINE}::before {
			content: ' ';
			position: absolute;
			left: ${"var(--ds-space-negative-025, -2px)"};
			top: -1px;
			width: ${n("eoFXy").resizeLineWidth}px;
			height: calc(100% + 2px);
			background-color: ${n("eoFXy").tableBorderSelectedColor};
			z-index: ${2*n("eoFXy").columnControlsZIndex};
		}

		th.${n("d5aTJ").TableCssClassName.WITH_DRAG_RESIZE_LINE_LAST_COLUMN}::before,
			td.${n("d5aTJ").TableCssClassName.WITH_DRAG_RESIZE_LINE_LAST_COLUMN}::before {
			content: ' ';
			position: absolute;
			right: -1px;
			top: -1px;
			width: ${n("eoFXy").resizeLineWidth}px;
			height: calc(100% + 2px);
			background-color: ${n("eoFXy").tableBorderSelectedColor};
			z-index: ${2*n("eoFXy").columnControlsZIndex};
		}

		/* Styles when drag and drop is disabled - will be removed */
		td.${n("d5aTJ").TableCssClassName.WITH_RESIZE_LINE}::before {
			content: ' ';
			position: absolute;
			left: ${"var(--ds-space-negative-025, -2px)"};
			top: -1px;
			width: ${n("eoFXy").resizeLineWidth}px;
			height: calc(100% + 2px);
			background-color: ${n("eoFXy").tableBorderSelectedColor};
			z-index: ${2*n("eoFXy").columnControlsZIndex};
		}

		th.${n("d5aTJ").TableCssClassName.WITH_RESIZE_LINE}::before {
			content: ' ';
			left: ${"var(--ds-space-negative-025, -2px)"};
			position: absolute;
			width: ${n("eoFXy").resizeLineWidth}px;
			height: calc(100% + ${n("eoFXy").tableToolbarSize+n("1zav4").tableCellBorderWidth}px);
			background-color: ${n("eoFXy").tableBorderSelectedColor};
			z-index: ${2*n("eoFXy").columnControlsZIndex};
			top: -${n("eoFXy").tableToolbarSize+n("1zav4").tableCellBorderWidth}px;
		}

		td.${n("d5aTJ").TableCssClassName.WITH_RESIZE_LINE_LAST_COLUMN}::before {
			content: ' ';
			position: absolute;
			right: -1px;
			top: -1px;
			width: ${n("eoFXy").resizeLineWidth}px;
			height: calc(100% + 2px);
			background-color: ${n("eoFXy").tableBorderSelectedColor};
			z-index: ${2*n("eoFXy").columnControlsZIndex};
		}

		th.${n("d5aTJ").TableCssClassName.WITH_RESIZE_LINE_LAST_COLUMN}::before {
			content: ' ';
			right: -1px;
			position: absolute;
			width: ${n("eoFXy").resizeLineWidth}px;
			height: calc(100% + ${n("eoFXy").tableToolbarSize+n("1zav4").tableCellBorderWidth}px);
			background-color: ${n("eoFXy").tableBorderSelectedColor};
			z-index: ${2*n("eoFXy").columnControlsZIndex};
			top: -${n("eoFXy").tableToolbarSize+n("1zav4").tableCellBorderWidth}px;
		}
	`,R=()=>(0,n("3jLHL").css)`
	.${n("d5aTJ").TableCssClassName.TABLE_CONTAINER} {
		.${n("d5aTJ").TableCssClassName.RESIZE_HANDLE_DECORATION} {
			background-color: transparent;
			position: absolute;
			width: ${n("eoFXy").resizeHandlerAreaWidth}px;
			height: 100%;
			top: 0;
			right: -${n("eoFXy").resizeHandlerAreaWidth/2}px;
			cursor: col-resize;
			z-index: ${n("eoFXy").resizeHandlerZIndex};
		}

		tr
			th:last-child
			.${n("d5aTJ").TableCssClassName.RESIZE_HANDLE_DECORATION},
			tr
			td:last-child
			.${n("d5aTJ").TableCssClassName.RESIZE_HANDLE_DECORATION} {
			background-color: transparent;
			position: absolute;
			width: ${n("eoFXy").resizeHandlerAreaWidth/2}px;
			height: 100%;
			top: 0;
			right: 0;
			cursor: col-resize;
			z-index: ${n("eoFXy").resizeHandlerZIndex};
		}

		${$()}

		table
      tr:first-of-type
      th.${n("d5aTJ").TableCssClassName.WITH_DRAG_RESIZE_LINE}
      .${n("d5aTJ").TableCssClassName.RESIZE_HANDLE_DECORATION}::after,
      table
      tr:first-of-type
      td.${n("d5aTJ").TableCssClassName.WITH_DRAG_RESIZE_LINE}
      .${n("d5aTJ").TableCssClassName.RESIZE_HANDLE_DECORATION}::after,
	  /* Styles when drag and drop is disabled - will be removed */
		table
      tr:first-of-type
      th.${n("d5aTJ").TableCssClassName.WITH_RESIZE_LINE}
      .${n("d5aTJ").TableCssClassName.RESIZE_HANDLE_DECORATION}::after,
      table
      tr:first-of-type
      td.${n("d5aTJ").TableCssClassName.WITH_RESIZE_LINE}
      .${n("d5aTJ").TableCssClassName.RESIZE_HANDLE_DECORATION}::after {
			top: -${n("eoFXy").tableToolbarSize+n("1zav4").tableCellBorderWidth}px;
			height: calc(100% + ${n("eoFXy").tableToolbarSize+n("1zav4").tableCellBorderWidth}px);
		}
	}
`,A=(0,n("3jLHL").css)({content:"' '",position:"absolute",height:`calc(100% + ${2*n("1zav4").tableCellBorderWidth}px)`,width:`${n("eoFXy").insertLineWidth}px`,zIndex:2*n("eoFXy").columnControlsZIndex}),I=(0,n("3jLHL").css)({content:"' '",position:"absolute",left:"var(--ds-space-negative-025, -2px)",height:`${n("eoFXy").insertLineWidth}px`,width:`calc(100% + ${2*n("1zav4").tableCellBorderWidth}px)`,zIndex:2*n("eoFXy").columnControlsZIndex}),F=(0,n("3jLHL").css)({backgroundColor:n("eoFXy").tableBorderSelectedColor}),P=(0,n("3jLHL").css)({backgroundColor:`var(--ds-background-accent-gray-subtler, ${n("aFUXX").akEditorTableBorder})`}),O=()=>(0,n("3jLHL").css)`
	.${n("d5aTJ").TableCssClassName.TABLE_CONTAINER} {
		td.${n("d5aTJ").TableCssClassName.WITH_FIRST_COLUMN_INSERT_LINE}::before {
			${A}
			left: -1px;
			top: -1px;
			${F}
		}

		td.${n("d5aTJ").TableCssClassName.WITH_FIRST_COLUMN_INSERT_LINE_INACTIVE}::before {
			${A}
			left: -1px;
			top: -1px;
			${P}
		}

		th.${n("d5aTJ").TableCssClassName.WITH_FIRST_COLUMN_INSERT_LINE}::before {
			${A}
			left: -1px;
			top: -${n("1zav4").tableCellBorderWidth}px;
			${F}
		}

		th.${n("d5aTJ").TableCssClassName.WITH_FIRST_COLUMN_INSERT_LINE_INACTIVE}::before {
			${A}
			left: -1px;
			top: -${n("1zav4").tableCellBorderWidth}px;
			${P}
		}

		td.${n("d5aTJ").TableCssClassName.WITH_COLUMN_INSERT_LINE}::before {
			${A}
			left: ${"var(--ds-space-negative-025, -2px)"};
			top: -1px;
			${F}
		}

		td.${n("d5aTJ").TableCssClassName.WITH_COLUMN_INSERT_LINE_INACTIVE}::before {
			${A}
			left: ${"var(--ds-space-negative-025, -2px)"};
			top: -1px;
			${P}
		}

		th.${n("d5aTJ").TableCssClassName.WITH_COLUMN_INSERT_LINE}::before {
			${A}
			left: ${"var(--ds-space-negative-025, -2px)"};
			top: -${n("1zav4").tableCellBorderWidth}px;
			${F}
		}

		th.${n("d5aTJ").TableCssClassName.WITH_COLUMN_INSERT_LINE_INACTIVE}::before {
			${A}
			left: ${"var(--ds-space-negative-025, -2px)"};
			top: -${n("1zav4").tableCellBorderWidth}px;
			${P}
		}

		td.${n("d5aTJ").TableCssClassName.WITH_LAST_COLUMN_INSERT_LINE}::before {
			${A}
			right: -1px;
			top: -1px;
			${F}
		}

		td.${n("d5aTJ").TableCssClassName.WITH_LAST_COLUMN_INSERT_LINE_INACTIVE}::before {
			${A}
			right: -1px;
			top: -1px;
			${P}
		}

		th.${n("d5aTJ").TableCssClassName.WITH_LAST_COLUMN_INSERT_LINE}::before {
			${A}
			right: -1px;
			top: -${n("1zav4").tableCellBorderWidth}px;
			${F}
		}

		th.${n("d5aTJ").TableCssClassName.WITH_LAST_COLUMN_INSERT_LINE_INACTIVE}::before {
			${A}
			right: -1px;
			top: -${n("1zav4").tableCellBorderWidth}px;
			${P}
		}

		td.${n("d5aTJ").TableCssClassName.WITH_ROW_INSERT_LINE}::before {
			${I}
			top: -1px;
			${F}
		}

		td.${n("d5aTJ").TableCssClassName.WITH_ROW_INSERT_LINE_INACTIVE}::before {
			${I}
			top: -1px;
			${P}
		}

		th.${n("d5aTJ").TableCssClassName.WITH_ROW_INSERT_LINE}::before {
			${I}
			top: -1px;
			${F}
		}

		th.${n("d5aTJ").TableCssClassName.WITH_ROW_INSERT_LINE_INACTIVE}::before {
			${I}
			top: -1px;
			${P}
		}

		td.${n("d5aTJ").TableCssClassName.WITH_LAST_ROW_INSERT_LINE}::before {
			${I}
			bottom: 0;
			${F}
		}

		td.${n("d5aTJ").TableCssClassName.WITH_LAST_ROW_INSERT_LINE_INACTIVE}::before {
			${I}
			bottom: 0;
			${P}
		}

		th.${n("d5aTJ").TableCssClassName.WITH_LAST_ROW_INSERT_LINE}::before {
			${I}
			bottom: 0;
			${F}
		}

		th.${n("d5aTJ").TableCssClassName.WITH_LAST_ROW_INSERT_LINE_INACTIVE}::before {
			${I}
			bottom: 0;
			${P}
		}
	}
`}),i("kXpLO",function(r,a){e(r.exports,"default",()=>s);var o=n("gwFzn");let i=(0,n("3jLHL").css)({flexGrow:1,height:"100%"});var s=({editorView:e,editorDisabled:r,children:a})=>{let s=t(o).useCallback(t=>{e&&!r&&(0,n("1NnoA").clickAreaClickHandler)(e,t)},[e,r]);return(0,n("3jLHL").jsx)("div",{"data-editor-click-wrapper":!0,"data-testid":"click-wrapper",css:i,onMouseDown:s},a)}}),i("1NnoA",function(t,r){e(t.exports,"clickAreaClickHandler",()=>s);let a=e=>{for(;e;){if(e.classList&&e.classList.contains("ak-editor-content-area"))return!0;e=e.parentNode}return!1},o=e=>!!e?.closest(".ProseMirror"),i=e=>{let t=e?.closest("[role=dialog]");return!t||!!t?.querySelector(".akEditor")},s=(e,t)=>{let r=!!e?.hasFocus?.();if(!(t.target instanceof HTMLElement))return;let s=t.target,l=s?.classList.contains("ak-editor-content-area"),c=a(s?.parentNode instanceof HTMLElement?s?.parentNode:null),p=o(s);if(p)return!1;let u=!!t.currentTarget.querySelector(".ak-editor-content-area"),m=s?.nodeName==="INPUT",h=!!(0,n("4vlwG").closestElement)(s,"[data-editor-popup]"),g=s?.nodeName==="TEXTAREA",b=!!(0,n("4vlwG").closestElement)(s,'nav[aria-label="Breadcrumbs"]'),f=window.getSelection(),x=f?.type==="Range"&&(0,n("4vlwG").closestElement)(f?.anchorNode,"[data-editor-popup]"),v=(0,n("dh538").fg)("platform_editor_keep_focus_on_content_comp_clicks")?s?.parentElement?.closest(`[${n("45E6y").ignoreAttribute}]`):!!(0,n("4vlwG").closestElement)(s,`[${n("45E6y").ignoreAttribute}]`)||s?.getAttribute(n("45E6y").ignoreAttribute)==="true",y=!!(0,n("4vlwG").closestElement)(t.currentTarget,"div[offset]")||!!(0,n("4vlwG").closestElement)(s,"div[offset]"),E=!!(0,n("4vlwG").closestElement)(t.currentTarget,"button")||!!(0,n("4vlwG").closestElement)(s,"button")||t.currentTarget?.nodeName==="BUTTON"||s?.nodeName==="BUTTON",S=!!c,C=!!s?.closest("#column-picker-popup");((S&&!p||!u)&&!r||!S&&r||l&&!S&&!r||u&&!l&&!S&&!r)&&!C&&!y&&!E&&!m&&!g&&!h&&!b&&!x&&!v&&i(s)&&e&&d(e,t)},d=(e,t)=>{let{dispatch:r,dom:a,state:o}=e,{tr:i}=o,s=!!e?.hasFocus?.();t.clientY>a.getBoundingClientRect().bottom&&(i.setMeta("outsideProsemirrorEditorClicked",!0),(0,n("dhoHU").addParagraphAtEnd)(i)),(0,n("1zPzM").setSelectionTopLevelBlocks)(i,t,a,e.posAtCoords.bind(e),s),(0,n("h3X17").tintDirtyTransaction)(i),(i.docChanged||i.selectionSet)&&(r&&r(i),e.focus(),t.preventDefault())}}),i("dhoHU",function(t,r){function a(e){let{doc:{type:{schema:{nodes:{paragraph:t}}}},doc:r}=e;r.lastChild&&!(r.lastChild.type===t&&0===r.lastChild.content.size)&&t&&e.insert(r.content.size,t.createAndFill()),e.setSelection((0,n("7T7aA").TextSelection).create(e.doc,e.doc.content.size-1)),e.scrollIntoView()}e(t.exports,"addParagraphAtEnd",()=>a),e(t.exports,"changeImageAlignment",()=>o),e(t.exports,"createToggleBlockMarkOnRange",()=>i),e(t.exports,"createToggleInlineMarkOnRange",()=>s),e(t.exports,"toggleBlockMark",()=>d),e(t.exports,"findCutBefore",()=>l);let o=e=>(t,r)=>{let{from:a,to:o}=t.selection,n=t.tr;return t.doc.nodesBetween(a,o,(r,a)=>{r.type===t.schema.nodes.mediaSingle&&n.setNodeMarkup(a,void 0,{...r.attrs,layout:"center"===e?"center":`align-${e}`})}),!!n.docChanged&&!!r&&(r(n.scrollIntoView()),!0)},i=(e,t,r)=>(a,o,n,i)=>{let s=!1;return i.doc.nodesBetween(a,o,(a,o,d)=>{if(!a.type.isBlock)return!1;if((!r||(Array.isArray(r)?r.indexOf(a.type)>-1:r(i.schema,a,d)))&&d?.type.allowsMarkType(e)){let r=a.marks.filter(t=>t.type===e),i=t(r.length?r[0].attrs:void 0,a);void 0!==i&&(n.setNodeMarkup(o,a.type,a.attrs,a.marks.filter(t=>!e.excludes(t.type)).concat(!1===i?[]:e.create(i))),s=!0)}}),s},s=(e,t)=>(r,a,o,i)=>{let s=!1;return i.doc.nodesBetween(r,a,(r,a,d)=>{if(d?.type.allowsMarkType(e)){let d=r.marks.filter(t=>t.type===e),l=t(d.length?d[0].attrs:void 0,r);void 0!==l&&(o.setNodeMarkup(a,r.type,r.attrs,r.marks.filter(t=>!e.excludes(t.type)).concat(!1===l?[]:e.create(l))),o.setSelection((0,n("7T7aA").NodeSelection).create(o.doc,i.selection.from)),s=!0)}}),s},d=(e,t,r)=>(a,o)=>{let s=!1,d=a.tr,l=i(e,t,r);if(a.selection instanceof n("7XFGZ").CellSelection)a.selection.forEachCell((e,t)=>{s=l(t,t+e.nodeSize,d,a)});else{let{from:e,to:t}=a.selection;s=l(e,t,d,a)}return!!s&&!!d.docChanged&&(o&&o(d.scrollIntoView()),!0)};function l(e){if(!e.parent.type.spec.isolating)for(let t=e.depth-1;t>=0;t--){if(e.index(t)>0)return e.doc.resolve(e.before(t+1));if(e.node(t).type.spec.isolating)break}return null}}),i("afcIe",function(t,r){e(t.exports,"insertBlock",()=>o);var a=n("gWR1e");let o=(e,t,r,o,i)=>{let s,d;let{hardBreak:l,codeBlock:c,listItem:p}=e.schema.nodes,u=e.doc.resolve(r);if(u.nodeAfter.type!==l||u.depth>1&&!(t===c&&(0,a.hasParentNodeOfType)(p)(e.selection)))return null;let m=e.tr.delete(r,o).split(r),h=m.doc.nodeAt(r+1),g=!1;m.doc.nodesBetween(r,r+h.nodeSize,(e,t)=>{g||e.type!==l||(g=!0,m=m.split(t+1).delete(t,t+1))}),g&&(h=m.doc.nodeAt(r+1));let{blockquote:b,paragraph:f}=e.schema.nodes;t===b?(d=3,s=[f.create({},h.content)]):(d=2,s=h.content);let x=t.create(i,s);return m=m.setSelection(new(n("7T7aA")).NodeSelection(m.doc.resolve(r+1))).replaceSelectionWith(x).setSelection(new(n("7T7aA")).TextSelection(m.doc.resolve(r+d)))}}),i("1zPzM",function(t,r){e(t.exports,"setSelectionTopLevelBlocks",()=>o),e(t.exports,"setGapCursorAtPos",()=>i);let a=(e,t,r,a)=>{let o=t.getBoundingClientRect();if(e.clientY<o.top)return{position:0,side:n("adhil").Side.LEFT};if(o.left>0){let t=r({left:o.left,top:e.clientY});if(t&&t.inside>-1){let r;let i=a.doc.resolve(t.inside).before(1),s=e.clientX<o.left?n("adhil").Side.LEFT:n("adhil").Side.RIGHT;if(s===n("adhil").Side.LEFT)r=i;else{let e=a.doc.nodeAt(i);e&&(r=i+e.nodeSize)}return{position:r,side:s}}}return null},o=(e,t,r,o,i)=>{let s=a(t,r,o,e);if(!s)return;let d=void 0!==s.position?e.doc.resolve(s.position):null;if(null!==d){if((s.side===n("adhil").Side.LEFT?(0,n("1gpr6").isValidTargetNode)(d.nodeAfter):(0,n("1gpr6").isValidTargetNode)(d.nodeBefore))&&(0,n("adhil").GapCursorSelection).valid(d))e.selection instanceof n("adhil").GapCursorSelection?e.setSelection((0,n("7T7aA").Selection).near(d)):e.setSelection(new(n("adhil")).GapCursorSelection(d,s.side));else if(!1===i){let t=(0,n("7T7aA").Selection).findFrom(d,s.side===n("adhil").Side.LEFT?1:-1,!0);t&&e.setSelection(t)}}},i=(e,t=n("adhil").Side.LEFT)=>(r,a)=>{if(e>r.doc.content.size)return!1;let o=r.doc.resolve(e);return!!(0,n("adhil").GapCursorSelection).valid(o)&&(a&&a(r.tr.setSelection(new(n("adhil")).GapCursorSelection(o,t))),!0)}}),i("adhil",function(t,r){e(t.exports,"Side",()=>o),e(t.exports,"JSON_ID",()=>i),e(t.exports,"GapCursorSelection",()=>s);var a,o=((a={}).LEFT="left",a.RIGHT="right",a);let i="gapcursor";class s extends n("7T7aA").Selection{static valid(e){let{parent:t,nodeBefore:r,nodeAfter:a}=e;if(!((0,n("1gpr6").isValidTargetNode)(r)?r:(0,n("1gpr6").isValidTargetNode)(a)?a:null)||t.isTextblock)return!1;let o=t.contentMatchAt(e.index()).defaultType;return o&&o.isTextblock}static findFrom(e,t,r=!1){let a=1===t?"right":"left";if(!r&&s.valid(e))return new s(e,a);let o=e.pos,n=null;for(let r=e.depth;;r--){let i=e.node(r);if("right"===a?e.indexAfter(r)<i.childCount:e.index(r)>0){n=i.maybeChild("right"===a?e.indexAfter(r):e.index(r)-1);break}if(0===r)return null;o+=t;let d=e.doc.resolve(o);if(s.valid(d))return new s(d,a)}for(;null!==(n="right"===a?n.firstChild:n.lastChild);){o+=t;let r=e.doc.resolve(o);if(s.valid(r))return new s(r,a)}return null}static fromJSON(e,t){return new s(e.resolve(t.pos),t.side)}map(e,t){let r=e.resolve(t.map(this.head));return s.valid(r)?new s(r,this.side):(0,n("7T7aA").Selection).near(r)}eq(e){return e instanceof s&&e.head===this.head}content(){return n("kviC1").Slice.empty}getBookmark(){return new d(this.anchor)}toJSON(){return{pos:this.head,type:i,side:this.side}}constructor(e,t="left"){super(e,e),this.side=t,this.visible=!1}}(0,n("7T7aA").Selection).jsonID(i,s);class d{map(e){return new d(e.map(this.pos))}resolve(e){let t=e.resolve(this.pos);return s.valid(t)?new s(t):(0,n("7T7aA").Selection).near(t)}constructor(e){this.pos=e}}}),i("1gpr6",function(t,r){e(t.exports,"isValidTargetNode",()=>a);let a=e=>!!e&&!(0,n("4Wd8f").isIgnored)(e)}),i("4Wd8f",function(t,r){e(t.exports,"isIgnored",()=>o);let a=["paragraph","bulletList","orderedList","listItem","taskItem","decisionItem","heading","blockquote","layoutColumn","caption","media","extensionFrame"],o=e=>!!e&&-1!==a.indexOf(e.type.name)}),i("45E6y",function(t,r){e(t.exports,"ignoreAttribute",()=>o),e(t.exports,"contentComponentClickWrapper",()=>i);var a=n("7UHDa");n("gwFzn");let o="data-editor-content-component",i=e=>(0,n("dh538").fg)("platform_editor_content_component_ignore_click")?(0,a.jsx)("div",{"data-editor-content-component":"true",children:e}):e}),i("4cy2V",function(t,r){e(t.exports,"getPrimaryToolbarComponents",()=>a);let a=(e,t)=>(0,n("dh538").fg)("platform_editor_setup_editorapi_sync")?{components:t??e?.primaryToolbar?.sharedState.currentState()?.components}:{components:t}}),i("1xxAs",function(r,a){e(r.exports,"ToolbarWithSizeDetector",()=>l);var o=n("gwFzn"),i=n("1oCLl");let s=(0,n("3jLHL").css)({width:"100%",position:"relative",[`@media (max-width: ${n("aFUXX").akEditorMobileMaxWidth}px)`]:{gridColumn:"1 / 2",gridRow:2,width:"calc(100% - 30px)",margin:"0 var(--ds-space-200, 16px)"}}),d=(0,n("3jLHL").css)({width:"100%",position:"relative"}),l=(0,n("9JpPs").componentWithCondition)(()=>(0,i.expValEquals)("platform_editor_core_static_emotion_non_central","isEnabled",!0),e=>{let r=t(o).useRef(null),[a,i]=t(o).useState(void 0),s=(0,n("khPmN").useElementWidth)(r,{skip:void 0!==a}),l=(0,n("eTj7Y").isSSR)()&&(0,n("geLSP").isFullPage)(e.appearance)?n("zMjD6").ToolbarSize.XXL:void 0,c=void 0===a&&void 0===s?l:(0,n("hoXJd").widthToToolbarSize)(a||s,e.appearance),p=(0,o.useMemo)(()=>{if(!e.hasMinWidth)return 254;{let t=(0,n("geLSP").isFullPage)(e.appearance)&&e.twoLineEditorToolbar?n("zMjD6").ToolbarSize.S:n("zMjD6").ToolbarSize.M;return(0,n("hoXJd").toolbarSizeToWidth)(t,e.appearance)}},[e.appearance,e.hasMinWidth,e.twoLineEditorToolbar]);return(0,n("3jLHL").jsx)("div",{css:d,style:{minWidth:`${p}px`}},(0,n("3jLHL").jsx)(n("4JDbp").WidthObserver,{setWidth:i}),e.editorView&&c?(0,n("3jLHL").jsx)(n("eUp7e").Toolbar,{toolbarSize:c,items:e.items,editorView:e.editorView,editorActions:e.editorActions,eventDispatcher:e.eventDispatcher,providerFactory:e.providerFactory,appearance:e.appearance,popupsMountPoint:e.popupsMountPoint,popupsBoundariesElement:e.popupsBoundariesElement,popupsScrollableElement:e.popupsScrollableElement,disabled:e.disabled,dispatchAnalyticsEvent:e.dispatchAnalyticsEvent,containerElement:e.containerElement,hasMinWidth:e.hasMinWidth,twoLineEditorToolbar:e.twoLineEditorToolbar}):(0,n("3jLHL").jsx)("div",{ref:r}))},e=>{let r=t(o).useRef(null),[a,i]=t(o).useState(void 0),d=(0,n("khPmN").useElementWidth)(r,{skip:void 0!==a}),l=(0,n("eTj7Y").isSSR)()&&(0,n("geLSP").isFullPage)(e.appearance)?n("zMjD6").ToolbarSize.XXL:void 0,c=void 0===a&&void 0===d?l:(0,n("hoXJd").widthToToolbarSize)(a||d,e.appearance),p=(0,o.useMemo)(()=>{let t=(0,n("geLSP").isFullPage)(e.appearance)&&e.twoLineEditorToolbar?n("zMjD6").ToolbarSize.S:n("zMjD6").ToolbarSize.M,r=(0,n("hoXJd").toolbarSizeToWidth)(t,e.appearance);return[s,`min-width: ${e.hasMinWidth?r:"254"}px`]},[e.appearance,e.hasMinWidth,e.twoLineEditorToolbar]);return(0,n("3jLHL").jsx)("div",{css:p},(0,n("3jLHL").jsx)(n("4JDbp").WidthObserver,{setWidth:i}),e.editorView&&c?(0,n("3jLHL").jsx)(n("eUp7e").Toolbar,{...e,toolbarSize:c}):(0,n("3jLHL").jsx)("div",{ref:r}))})}),i("khPmN",function(r,a){e(r.exports,"useElementWidth",()=>i);var o=n("gwFzn");let i=(e,{skip:r})=>{let[a,i]=t(o).useState(void 0);return t(o).useEffect(()=>{r||!e.current||(0,n("dh538").fg)("platform_editor_prevent_toolbar_width_reflow")||i(Math.round(e.current.getBoundingClientRect().width))},[r,i,e]),a}}),i("eUp7e",function(t,r){e(t.exports,"Toolbar",()=>o);var a=n("7UHDa");n("gwFzn");let o=e=>(0,a.jsx)(n("jlXEe").ToolbarInner,{items:e.items,editorView:e.editorView,editorActions:e.editorActions,eventDispatcher:e.eventDispatcher,providerFactory:e.providerFactory,appearance:e.appearance,popupsMountPoint:e.popupsMountPoint,popupsBoundariesElement:e.popupsBoundariesElement,popupsScrollableElement:e.popupsScrollableElement,disabled:e.disabled,dispatchAnalyticsEvent:e.dispatchAnalyticsEvent,toolbarSize:e.toolbarSize,isToolbarReducedSpacing:e.toolbarSize<n("zMjD6").ToolbarSize.XXL,containerElement:e.containerElement})}),i("jlXEe",function(r,a){e(r.exports,"ToolbarInner",()=>d);var o=n("gwFzn"),i=n("atveb");let s=(0,n("3jLHL").css)({display:"flex",[`@media (max-width: ${n("aFUXX").akEditorMobileMaxWidth}px)`]:{justifyContent:"space-between"}});class d extends t(o).Component{shouldComponentUpdate(e){return!t(i)(e,this.props)}render(){let{appearance:e,editorView:r,editorActions:a,eventDispatcher:i,providerFactory:d,items:l,popupsMountPoint:c,popupsBoundariesElement:p,popupsScrollableElement:u,toolbarSize:m,disabled:h,isToolbarReducedSpacing:g,dispatchAnalyticsEvent:b,containerElement:f}=this.props;return!l||!l.length||(0,n("eTj7Y").isSSR)()?null:(0,n("3jLHL").jsx)("div",{css:s,"data-vc":"toolbar-inner"},l.map((n,s)=>{let x=n({editorView:r,editorActions:a,eventDispatcher:i,providerFactory:d,appearance:e,popupsMountPoint:c,popupsBoundariesElement:p,popupsScrollableElement:u,disabled:h,toolbarSize:m,isToolbarReducedSpacing:g,containerElement:f,isLastItem:s===l.length-1,dispatchAnalyticsEvent:b,wrapperElement:null});return x&&t(o).cloneElement(x,{key:s})}))}}}),i("hoXJd",function(t,r){e(t.exports,"toolbarSizeToWidth",()=>l),e(t.exports,"widthToToolbarSize",()=>c);let a=[{width:n("zMjD6").ToolbarWidthsFullPageNext.XXL,size:n("zMjD6").ToolbarSize.XXL},{width:n("zMjD6").ToolbarWidthsFullPageNext.XL,size:n("zMjD6").ToolbarSize.XL},{width:n("zMjD6").ToolbarWidthsFullPageNext.L,size:n("zMjD6").ToolbarSize.L},{width:n("zMjD6").ToolbarWidthsFullPageNext.M,size:n("zMjD6").ToolbarSize.M},{width:n("zMjD6").ToolbarWidthsFullPageNext.S,size:n("zMjD6").ToolbarSize.S}],o=[{width:n("zMjD6").ToolbarWidthsFullPage.XXL,size:n("zMjD6").ToolbarSize.XXL},{width:n("zMjD6").ToolbarWidthsFullPage.XL,size:n("zMjD6").ToolbarSize.XL},{width:n("zMjD6").ToolbarWidthsFullPage.L,size:n("zMjD6").ToolbarSize.L},{width:n("zMjD6").ToolbarWidthsFullPage.M,size:n("zMjD6").ToolbarSize.M},{width:n("zMjD6").ToolbarWidthsFullPage.S,size:n("zMjD6").ToolbarSize.S}],i=[{width:n("zMjD6").ToolbarWidthsNext.XXL,size:n("zMjD6").ToolbarSize.XXL},{width:n("zMjD6").ToolbarWidthsNext.XL,size:n("zMjD6").ToolbarSize.XL},{width:n("zMjD6").ToolbarWidthsNext.L,size:n("zMjD6").ToolbarSize.L},{width:n("zMjD6").ToolbarWidthsNext.M,size:n("zMjD6").ToolbarSize.M},{width:n("zMjD6").ToolbarWidthsNext.S,size:n("zMjD6").ToolbarSize.S}],s=[{width:n("zMjD6").ToolbarWidths.XXL,size:n("zMjD6").ToolbarSize.XXL},{width:n("zMjD6").ToolbarWidths.XL,size:n("zMjD6").ToolbarSize.XL},{width:n("zMjD6").ToolbarWidths.L,size:n("zMjD6").ToolbarSize.L},{width:n("zMjD6").ToolbarWidths.M,size:n("zMjD6").ToolbarSize.M},{width:n("zMjD6").ToolbarWidths.S,size:n("zMjD6").ToolbarSize.S}],d=e=>(0,n("geLSP").isFullPage)(e)?(0,n("dh538").fg)("platform_editor_toolbar_responsive_fixes")?a:o:(0,n("dh538").fg)("platform_editor_toolbar_responsive_fixes")?i:s,l=(e,t)=>(d(t).find(({size:t})=>e===t)||{width:n("zMjD6").ToolbarWidths.S}).width,c=(e,t)=>(d(t).find(({width:t})=>e>t)||{size:n("zMjD6").ToolbarSize.XXXS}).size}),i("7Ogr0",function(t,r){e(t.exports,"MainToolbar",()=>g);var a=n("gwFzn"),o=n("1oCLl");let i=(e=!1)=>(0,n("3jLHL").css)`
	position: relative;
	align-items: center;
	padding: ${"var(--ds-space-100, 8px)"} ${"var(--ds-space-100, 8px)"} 0;
	display: flex;
	height: auto;
	background-color: ${"var(--ds-surface, white)"};
	box-shadow: none;
	padding-left: ${"var(--ds-space-250, 20px)"};

	& > div {
		> :first-child:not(style),
		> style:first-child + * {
			margin-left: 0;
		}
		${e&&`
        @media (max-width: 490px) {
          flex-direction: column-reverse;
          align-items: end;
          display: flex;
          justify-content: flex-end;
        }

        /* make this more explicit for a toolbar */
        > *:nth-child(1) {
          @media (max-width: 490px) {
            > div:nth-child(2) {
              justify-content: flex-end;
              display: flex;
            }
          }
        }
    `}
	}

	.block-type-btn {
		padding-left: 0;
	}

	${(0,n("dh538").fg)("platform-visual-refresh-icons")&&"span svg { max-width: 100%; }"}
`,s=(0,n("3jLHL").css)({position:"relative",alignItems:"center",padding:"var(--ds-space-100, 8px) var(--ds-space-100, 8px) 0",display:"flex",height:"auto",backgroundColor:"var(--ds-surface, white)",boxShadow:"none",paddingLeft:"var(--ds-space-250, 20px)","> div":{"> div:first-of-type:not(style), > style:first-of-type + *":{marginLeft:0}},".block-type-btn":{paddingLeft:0}}),d=(0,n("3jLHL").css)({"& > div":{"@media (max-width: 490px)":{flexDirection:"column-reverse",alignItems:"end",display:"flex",justifyContent:"flex-end"},"> div:first-of-type":{"@media (max-width: 490px)":{"> div:nth-of-type(2)":{justifyContent:"flex-end",display:"flex"}}}}}),l=(0,n("3jLHL").css)({"span svg":{maxWidth:"100%"}}),c=(0,n("3jLHL").css)`
	/* stylelint-disable declaration-block-no-duplicate-properties */
	position: relative;
	position: sticky;
	/* stylelint-enable declaration-block-no-duplicate-properties */
	padding-bottom: ${"var(--ds-space-100, 8px)"};
	z-index: ${500};
	transition: box-shadow ease-in-out 0.2s;
	&.show-keyline {
		box-shadow: 0 ${2}px 0 0
			${"var(--ds-background-accent-gray-subtlest, #F1F2F4)"};
	}
`,p=(0,n("3jLHL").css)({position:"sticky",paddingBottom:"var(--ds-space-100, 8px)",zIndex:500,transition:"box-shadow ease-in-out 0.2s","&.show-keyline":{boxShadow:"0 2px 0 0 var(--ds-background-accent-gray-subtlest, #F1F2F4)"}}),u=e=>{let[t,r]=(0,a.useState)(0);return(0,a.useEffect)(()=>{e.externalToolbarRef?.current?.clientHeight?r(e.externalToolbarRef.current.clientHeight):r(e.offsetTop||0)},[e.externalToolbarRef,e.offsetTop]),(0,n("3jLHL").jsx)("div",{css:(0,o.expValEquals)("platform_editor_core_static_emotion_non_central","isEnabled",!0)?[s,e.twoLineEditorToolbar&&d,(0,n("dh538").fg)("platform-visual-refresh-icons")&&l,p]:[i(e.twoLineEditorToolbar),c],style:{top:`${t}px`},"data-testid":"ak-editor-main-toolbar",className:"show-keyline"},e.children)},m=e=>(0,n("3jLHL").jsx)("div",{css:(0,o.expValEquals)("platform_editor_core_static_emotion_non_central","isEnabled",!0)?[s,e.twoLineEditorToolbar&&d,(0,n("dh538").fg)("platform-visual-refresh-icons")&&l]:i(e.twoLineEditorToolbar),"data-testid":"ak-editor-main-toolbar"},e.children),h=e=>{let t="object"==typeof e&&!("offsetTop"in e),r="object"==typeof e&&"offsetTop"in e;return"object"!=typeof e?{externalToolbarRef:void 0,offsetTop:void 0}:r?{offsetTop:e.offsetTop}:t?{externalToolbarRef:e}:void 0},g=({useStickyToolbar:e,twoLineEditorToolbar:t,children:r})=>e?(0,n("3jLHL").jsx)(u,{...h(e),twoLineEditorToolbar:t},r):(0,n("3jLHL").jsx)(m,{twoLineEditorToolbar:t},r)}),i("7bZ3i",function(r,a){e(r.exports,"SmartCardProvider",()=>l);var o=n("7UHDa"),i=n("gwFzn");n("2lEVN");var s=n("bUv13"),d=n("ewFdA");function l({storeOptions:e,client:r,authFlow:a,children:l,renderers:c,isAdminHubAIEnabled:p,product:u,shouldControlDataExport:m,isPreviewPanelAvailable:h,openPreviewPanel:g}){let b=(0,i.useContext)(n("eIleF").SmartCardContext),f=(0,i.useMemo)(()=>({}),[]),{initialState:x}=e||{initialState:f},v=(0,i.useMemo)(()=>(0,s.default)(n("dE3t3").cardReducer,x),[x]),y=(0,i.useMemo)(()=>{let e=r||new(n("k00oi")).default;return u&&e.setProduct&&e.setProduct(u),{renderers:c,store:v,prefetchStore:{},connections:{client:e},config:{authFlow:a||"oauth2"},extractors:{getPreview:(e,t)=>{let r=(0,n("6q0AE").getUrl)(v,e);return r.details?(0,n("dh538").fg)("smart_links_noun_support")?(0,n("79vw2").extractSmartLinkEmbed)(r.details):(0,n("9JHBV").extractPreview)(r.details.data,t):void 0}},isAdminHubAIEnabled:p,product:u,shouldControlDataExport:m,isPreviewPanelAvailable:h,openPreviewPanel:g}},[a,r,p,h,g,u,c,m,v]),E=(0,i.useMemo)(()=>t(d)({},b||y,{isPreviewPanelAvailable:h,openPreviewPanel:g}),[b,y,h,g]);return(0,o.jsx)(n("eIleF").SmartCardContext.Provider,{value:(0,n("dh538").fg)("gryf-5548_smart_card_provider_merge_props")?E:b||y,children:l})}}),i("2lEVN",function(t,r){e(t.exports,"createStore",()=>n("bUv13").default),n("bUv13"),n("fMKrO"),n("5nIDK"),n("gdPKY"),n("5cjm1"),n("ef23b")}),i("bUv13",function(t,r){e(t.exports,"ActionTypes",()=>o),e(t.exports,"default",()=>i);var a=n("eviWr"),o={INIT:"@@redux/INIT"};function i(e,t,r){if("function"==typeof t&&void 0===r&&(r=t,t=void 0),void 0!==r){if("function"!=typeof r)throw Error("Expected the enhancer to be a function.");return r(i)(e,t)}if("function"!=typeof e)throw Error("Expected the reducer to be a function.");var s,d=e,l=t,c=[],p=c,u=!1;function m(){p===c&&(p=c.slice())}function h(e){if("function"!=typeof e)throw Error("Expected listener to be a function.");var t=!0;return m(),p.push(e),function(){if(t){t=!1,m();var r=p.indexOf(e);p.splice(r,1)}}}function g(e){if(!(0,n("b0C22").default)(e))throw Error("Actions must be plain objects. Use custom middleware for async actions.");if(void 0===e.type)throw Error('Actions may not have an undefined "type" property. Have you misspelled a constant?');if(u)throw Error("Reducers may not dispatch actions.");try{u=!0,l=d(l,e)}finally{u=!1}for(var t=c=p,r=0;r<t.length;r++)(0,t[r])();return e}return g({type:o.INIT}),(s={dispatch:g,subscribe:h,getState:function(){return l},replaceReducer:function(e){if("function"!=typeof e)throw Error("Expected the nextReducer to be a function.");d=e,g({type:o.INIT})}})[a.default]=function(){var e;return(e={subscribe:function(e){if("object"!=typeof e)throw TypeError("Expected the observer to be an object.");function t(){e.next&&e.next(l)}return t(),{unsubscribe:h(t)}}})[a.default]=function(){return this},e},s}}),i("fMKrO",function(e,t){n("bUv13"),n("ef23b")}),i("ef23b",function(e,t){}),i("5nIDK",function(e,t){}),i("gdPKY",function(e,t){n("5cjm1")}),i("5cjm1",function(t,r){e(t.exports,"default",()=>a);function a(){for(var e=arguments.length,t=Array(e),r=0;r<e;r++)t[r]=arguments[r];return 0===t.length?function(e){return e}:1===t.length?t[0]:t.reduce(function(e,t){return function(){return e(t.apply(void 0,arguments))}})}}),i("6q0AE",function(t,r){e(t.exports,"getUrl",()=>a);let a=(e,t)=>e.getState()[t]||{status:"pending"}}),i("dE3t3",function(t,r){e(t.exports,"cardReducer",()=>i);let a=e=>[(0,n("9gPkz").ACTION_PENDING),(0,n("9gPkz").ACTION_RESOLVING),(0,n("9gPkz").ACTION_RESOLVED),(0,n("9gPkz").ACTION_RELOADING),(0,n("9gPkz").ACTION_ERROR),(0,n("9gPkz").ACTION_ERROR_FALLBACK),(0,n("9gPkz").ACTION_UPDATE_METADATA_STATUS)].includes(e.type);function o(e,t,r){let a={...t};return e?(a.status=(0,n("btw9C").getStatus)(e),a.details=e):a.status=r,a}let i=(e,t)=>{if(!a(t))return e;let r=e[t.url];if(!t.ignoreStatusCheck&&r&&r.status===t.type)return e;{let a=function(e,t){switch(t.type){case n("9gPkz").ACTION_PENDING:return{status:t.type};case n("9gPkz").ACTION_RESOLVING:return{...e,status:t.type};case n("9gPkz").ACTION_RESOLVED:return o(t.payload,e,t.type);case n("9gPkz").ACTION_RELOADING:return o(t.payload,e,"resolved");case n("9gPkz").ACTION_ERROR:return{...e,status:t.type,error:t.error};case n("9gPkz").ACTION_ERROR_FALLBACK:return{...e,status:t.type,error:t.error,details:t.payload};case n("9gPkz").ACTION_UPDATE_METADATA_STATUS:return{...e,metadataStatus:t.metadataStatus}}}(r,t);return{...e,[t.url]:a}}}}),i("9gPkz",function(t,r){e(t.exports,"ACTION_PENDING",()=>a),e(t.exports,"ACTION_RESOLVING",()=>o),e(t.exports,"ACTION_RESOLVED",()=>n),e(t.exports,"ACTION_RELOADING",()=>i),e(t.exports,"ACTION_ERROR",()=>s),e(t.exports,"ACTION_ERROR_FALLBACK",()=>d),e(t.exports,"ACTION_UPDATE_METADATA_STATUS",()=>l),e(t.exports,"cardAction",()=>c);let a="pending",o="resolving",n="resolved",i="reloading",s="errored",d="fallback",l="metadata",c=(e,{url:t},r,a,o,n)=>({type:e,url:t,payload:r,error:a,metadataStatus:o,ignoreStatusCheck:n})}),i("eIleF",function(t,r){e(t.exports,"SmartCardContext",()=>i),e(t.exports,"useSmartLinkContext",()=>s),e(t.exports,"useSmartCardContext",()=>d),e(t.exports,"EditorSmartCardProviderValueGuard",()=>l),e(t.exports,"EditorSmartCardProvider",()=>c);var a=n("7UHDa"),o=n("gwFzn");let i=(0,o.createContext)(void 0);function s(){let e=(0,o.useContext)(i);if(!e)throw Error("useSmartCard() must be wrapped in <SmartCardProvider>");return e}let d=()=>(function(e){let t=(0,o.useContext)(e);return(0,o.useMemo)(()=>({Provider:e.Provider,Consumer:e.Consumer,value:t}),[t,e])})(i),l=({children:e})=>{let t=d();return t?.value?(0,a.jsx)(a.Fragment,{children:e}):null},c=({children:e})=>{let t=d(),r=t.Provider;return(0,a.jsx)(r,{value:t.value,children:e})}}),i("le4yZ",function(t,r){e(t.exports,"KnowledgeDiscoveryKeyPhraseInputTextFormat",()=>d),e(t.exports,"KeyPhraseCategory",()=>l),e(t.exports,"getHighlightRegex",()=>p),e(t.exports,"useAutohighlightSupplier",()=>h);var a,o,i=n("gwFzn"),s=n("9pwVP"),d=((a={}).PLAIN="PLAIN",a.ADF="ADF",a),l=((o={}).PROJECT="PROJECT",o.TEAM="TEAM",o.ACRONYM="ACRONYM",o.AUTO="AUTO",o.OTHER="OTHER",o);let c=e=>e.replace(/[-[\]{}()*+?.,\\^$|#\s]/g,"\\$&"),p=e=>{try{if(!e.length)return RegExp("(?!)");return RegExp(e.map(e=>`\\b${c(e.keyPhrase)}\\b`).join("|"),"gi")}catch{return RegExp("(?!)")}},u=e=>e.length?e[0].category:"AUTO",m={keyPhrases:[],keyPhraseCategory:"AUTO",autoHighlightRegex:RegExp("(?!)"),loadAutohighlights:()=>Promise.resolve([]),resetAutohighlights:()=>{},autohighlightsLoading:!1,error:void 0},h=({entityAri:e,workspaceId:t,product:r,productConfig:a,fieldType:o,cloudId:d})=>{let[l,c]=(0,i.useState)(m),{createAnalyticsEvent:h}=(0,n("inPa6").useAnalyticsEvents)(),g=(0,i.useCallback)(e=>{h(e).fire(n("f7lNm").DEFAULT_GAS_CHANNEL)},[h]),{jiraReporterAccountId:b,jiraAssigneeAccountId:f}=a||{},x=(0,i.useCallback)(async({inputText:a})=>{try{c({...m,autohighlightsLoading:!0});let i=await (0,n("9EFEY").fetchAggResponse)({graphQuery:n("bbPOv").KeyPhrasesQuery,variables:{workspaceId:t,entityAri:e,...!!b&&{jiraReporterAccountId:b},...!!f&&{jiraAssigneeAccountId:f},...!!a&&{inputText:a}},operationName:n("bbPOv").KEY_PHRASES_OPERATION_NAME,headers:(0,n("6yuru").createAtlAttributionHeader)({atlWorkspaceId:t,tenantId:d,product:r})}),l=i?.data?.knowledgeDiscovery?.keyPhrases?.nodes?i.data.knowledgeDiscovery.keyPhrases.nodes:[];l.length>0&&(0,n("dh538").fg)("kd_definitions_click_and_show_event_product_parity")&&g((0,s.onShownAutoDefinitionHighlights)({product:r,contentId:e,keyPhrases:l,fieldType:o}));let h=p(l);return c({...m,keyPhraseCategory:u(l),autoHighlightRegex:h,keyPhrases:l}),l}catch(e){return c({...m,error:e.message}),[]}},[e,t,g,r,b,f,o,d]),v=(0,i.useCallback)(()=>{c(m)},[]),y=(0,i.useMemo)(()=>l.autoHighlightRegex,[l.autoHighlightRegex]),E=(0,i.useMemo)(()=>l.autohighlightsLoading,[l.autohighlightsLoading]),S=(0,i.useMemo)(()=>l.keyPhrases,[l.keyPhrases]),C=(0,i.useMemo)(()=>l.error,[l.error]);return{keyPhrases:S,keyPhraseCategory:l.keyPhraseCategory,autoHighlightRegex:y,loadAutohighlights:x,resetAutohighlights:v,autohighlightsLoading:E,error:C}}}),i("9EFEY",function(t,r){e(t.exports,"fetchAggResponse",()=>o);var a=n("dwp40");async function o({graphQuery:e,variables:t,operationName:r,aggAbsoluteUrl:o="/gateway/api/graphql",cache:i,headers:s}){let d={requestInit:{method:"POST",headers:{"Content-Type":"application/json",...s?{...s}:{}},body:JSON.stringify({operationName:r,query:e,variables:t})},queryParams:{...r&&{q:r}}};return i&&(0,n("dh538").fg)("kd_fe_enable_api_cache")?(0,n("i1ClO").fetchAggResponseWithCache)({graphQuery:e,variables:t,operationName:r,cache:i,headers:s}):(0,a.utils).requestService({url:o},d)}}),i("i1ClO",function(t,r){e(t.exports,"fetchAggResponseWithCache",()=>o);var a=n("dwp40");async function o({graphQuery:e,variables:t,operationName:r,aggAbsoluteUrl:o="/gateway/api/graphql",cache:i,headers:s}){let d={requestInit:{method:"POST",headers:{"Content-Type":"application/json",...s?{...s}:{}},body:JSON.stringify({operationName:r,query:e,variables:t})},queryParams:{...r&&{q:r}}},l=(0,n("iip0W").InMemCache).getData(i.key);if(l&&(0,n("iip0W").InMemCache).isValid(i.key))return Promise.resolve(l);let c=(0,n("iip0W").InMemCache).getInflightRequest(i.key);if(c)return c;let p=new Promise(async(e,t)=>{try{let t=await (0,a.utils).requestService({url:o},d);(0,n("iip0W").InMemCache).setData({key:i.key,response:t,ttl:i.ttl}),e(t)}catch(e){t(e)}finally{(0,n("iip0W").InMemCache).removeInflightRequest(i.key)}});return(0,n("iip0W").InMemCache).setInflightRequest({key:i.key,request:p}),p}}),i("iip0W",function(t,r){e(t.exports,"InMemCache",()=>a);class a{static setData({key:e,response:t,ttl:r}){this.cache.set(e,{ttl:Date.now()+(r||3e5),response:t})}static getData(e){return this.cache.get(e)?.response}static isValid(e){let t=this.cache.get(e);return!!t&&Date.now()<(t?.ttl||0)}static getInflightRequest(e){return this.inFlightRequests.get(e)}static setInflightRequest({key:e,request:t}){this.inFlightRequests.set(e,t)}static removeInflightRequest(e){return this.inFlightRequests.delete(e)}static clearCache(){this.cache.clear(),this.inFlightRequests.clear()}}a.cache=new Map,a.inFlightRequests=new Map}),i("6yuru",function(t,r){e(t.exports,"createAtlAttributionHeader",()=>a);function a({atlWorkspaceId:e,tenantId:t,product:r}){if((0,n("dh538").fg)("kd_agg_atl_attribution_header"))return{"atl-attribution":JSON.stringify({atlWorkspaceId:e,tenantId:t,product:r,businessUnit:"Engineering-AI",costCenter:"3533",team:"Eng - Knowledge Discovery"})}}}),i("f7lNm",function(t,r){e(t.exports,"ATLASSIAN_INTELLIGENCE_SEARCH_INFO_LINK",()=>a),e(t.exports,"ATLASSIAN_INTELLIGENCE_TRUST_LINK",()=>o),e(t.exports,"SAC_ATLASSIAN_INTELLIGENCE_TRUST_LINK",()=>n),e(t.exports,"ATLASSIAN_ACCEPTABLE_USE_POLICY_LINK",()=>i),e(t.exports,"ATLASSIAN_AI_USAGE_LIMITS_LINK",()=>s),e(t.exports,"ATLASSIAN_AI_TROUBLESHOOT_LINK",()=>d),e(t.exports,"ATLASSIAN_HIPAA_COMPLICANCE_LINK",()=>l),e(t.exports,"ATLASSIAN_ROVO_LINK",()=>c),e(t.exports,"FEEDBACK_ENTRYPOINT_ID_SAIN",()=>p),e(t.exports,"FEEDBACK_ENTRYPOINT_ID_TOPICS",()=>u),e(t.exports,"FEEDBACK_CONTEXT_CF",()=>m),e(t.exports,"DEFAULT_GAS_CHANNEL",()=>h),e(t.exports,"READING_AIDS_DIALOG_WIDTH",()=>g),e(t.exports,"SAIN_STREAMING_API",()=>b),e(t.exports,"ASSISTANCE_SERVICE_API_BASE_URL",()=>f),e(t.exports,"DEFAULT_GRAPHQL_ENDPOINT",()=>x),e(t.exports,"QueryIntent",()=>k),e(t.exports,"CardTemplate",()=>T),e(t.exports,"AiBrand",()=>w),e(t.exports,"AIAnswerTab",()=>_);let a="https://support.atlassian.com/confluence-cloud/docs/use-atlassian-intelligence-to-search-for-answers/",o="https://www.atlassian.com/trust/atlassian-intelligence",n="https://confluence.atlassian.com/support/atlassian-support-ai-chat-1455423797.html",i="https://www.atlassian.com/legal/acceptable-use-policy",s="https://support.atlassian.com/organization-administration/docs/usage-limits-in-atlassian-intelligence/",d="https://support.atlassian.com/organization-administration/docs/troubleshooting-for-atlassian-intelligence/",l="https://support.atlassian.com/organization-administration/docs/the-hipaa-implementation-guide/",c="https://www.atlassian.com/software/rovo",p="82633dea-7fbf-4faa-9a51-a83a3fd181d9",u="10f4daa4-bcfc-4d42-ae33-92888648d9db",m="customfield_10047",h="fabric-elements";(v={}).SEARCH_DIALOG="searchDialog",v.ADVANCED_SEARCH="advancedSearch",v.READING_AIDS="readingAids";let g="500px",b="/gateway/api/smartAnswers/stream",f="/gateway/api/assist",x="/gateway/api/graphql";var v,y,E,S,C,k=((y={}).DEFAULT="DEFAULT",y.NATURAL_LANGUAGE_QUERY="NATURAL_LANGUAGE_QUERY",y.KEYWORD_OR_ACRONYM="KEYWORD_OR_ACRONYM",y.PERSON="PERSON",y.TEAM="TEAM",y.NAVIGATIONAL="NAVIGATIONAL",y.NONE="NONE",y.LOCATION="LOCATION",y.DATE="DATE",y.JIRA_ISSUE="JIRA_ISSUE",y.TOPIC="TOPIC",y),T=((E={}).DEFAULT="DEFAULT",E.SMART_ANSWER="SMART_ANSWER",E.RIGHT_PANEL="RIGHT_PANEL",E),w=((S={}).ROVO="ROVO",S.AI="ATLASSIAN INTELLIGENCE",S),_=((C={}).AI_ANSWER="AI_ANSWER",C.SOURCES="SOURCES",C)}),i("9pwVP",function(t,r){e(t.exports,"onCuratedDefinitionUpdateButtonClicked",()=>o),e(t.exports,"onCuratedDefinitionSeeEditHistoryButtonClicked",()=>i),e(t.exports,"onLikeButtonClick",()=>s),e(t.exports,"onDislikeButtonClick",()=>d),e(t.exports,"onShownAutoDefinitionHighlights",()=>l),e(t.exports,"onClickAutoDefinitionHighlights",()=>c),e(t.exports,"onClickDisableDefinition",()=>p);var a=n("le4yZ");let o=({commonAttributes:e,newDefinition:t,restrictedScope:r,sourceSelected:a,aiDefinitionEdited:o})=>{let{query:n,answerString:i,extraAttributes:s,source:d}=e,{contentId:l,readingAidsSessionId:c}=s||{};return{action:"clicked",actionSubject:"aiCuratedDefinitionUpdateButton",source:d,eventType:"ui",attributes:{contentId:l,readingAidsSessionId:c,restrictedScope:r,sourceSelected:a,newDefinitionLength:t.length,aiDefinitionEdited:o},nonPrivacySafeAttributes:{keyPhrase:n,oldDefinition:i,newDefinition:t}}},i=e=>{let{query:t,answerString:r,extraAttributes:a,source:o}=e,{contentId:n,readingAidsSessionId:i}=a||{};return{action:"clicked",actionSubject:"aiCuratedDefinitionSeeEditHistoryButton",source:o,eventType:"ui",attributes:{contentId:n,readingAidsSessionId:i},nonPrivacySafeAttributes:{query:t,answerString:r}}},s=e=>{let{query:t,answerString:r,source:a}=e;return{action:"clicked",actionSubject:"aiAnswerLikeButton",source:a,eventType:"ui",attributes:{...(0,n("cqFuK").filterCommonAttributes)(e)},nonPrivacySafeAttributes:{query:t,answerString:r}}},d=e=>{let{query:t,answerString:r,source:a}=e;return{action:"clicked",actionSubject:"aiAnswerDislikeButton",source:a,eventType:"ui",attributes:{...(0,n("cqFuK").filterCommonAttributes)(e)},nonPrivacySafeAttributes:{query:t,answerString:r}}},l=({product:e,contentId:t,keyPhrases:r,fieldType:a})=>({action:"shown",actionSubject:"aiDefinitionsAutohighlights",source:"viewPageScreen",eventType:"track",attributes:{product:e,contentId:t,numHighlights:r.length,categories:(0,n("fjzE4").getHighlightCategories)(r),beAcronymsEnabled:!0,fieldType:a}}),c=({contentId:e,sessionId:t,keyPhraseCategory:r,fieldType:o})=>({action:"clicked",actionSubject:"aiDefinitionsAutohighlights",source:"viewPageScreen",eventType:"ui",attributes:{contentId:e,readingAidsSessionId:t,keyPhraseCategory:r||a.KeyPhraseCategory.AUTO,fieldType:o}}),p=e=>({action:"clicked",actionSubject:"aiDefinitionsDisableDefinition",source:"viewPageScreen",eventType:"ui",attributes:{...(0,n("cqFuK").filterCommonAttributes)(e)}})}),i("cqFuK",function(t,r){e(t.exports,"sanitizeExtraAttributes",()=>l),e(t.exports,"filterCommonAttributes",()=>c);let a=["Assets","Atlas","Confluence","Atlassian Analytics","Atlassian Cloud","Automation for Jira","Bamboo","Bitbucket","Compass","Jira","Jira Product Discovery","Jira Service Management","Jira Software","Jira Work Management","Jira Align","Migration","Loom","Opsgenie","Platform Experiences","Rovo","Statuspage","Trello","webSearch","web-page","Fisheye and Crucible","Crowd","Sourcetree","Unknown","Focus","file-upload","Advanced Roadmaps For Jira","Questions for Confluence"],o=e=>{let t={};return e.forEach(e=>{let r=e.product;r&&(t[r]=(t[r]??0)+1)}),t},i=e=>e.map(e=>({id:e.ari??e.id,type:e.type})),s=e=>e.some(e=>!!e.product&&!a.includes(e.product)&&!e.product.includes("Plugin")),d=new Set(["contentId","readingAidsSessionId","fieldType","multipleUserResultsShown","numAddtlWhoMatches","isCuratedDefinition","isPrecomputedDefinition","editDistance","bookmarkId","bookmarkState","dwellTime","availableProducts","isDescriptionEmpty","message_id","conversational_channel_id","experience_id","user_id","experiments","featureGates","isFullPageSearch","has3pProducts","is3pSearch","mode","triggeredBy"]),l=e=>{if(!(0,n("dh538").fg)("kd_fe_sanitize_analytics"))return e;let t={};for(let r in e)d.has(r)?t[r]=e[r]:t[r]="[sanitized]";return t},c=e=>{let{appliedFilters:t,answerFormat:r,answerLength:a,answerWordCount:d,answerCardType:c,cloudId:p,followUps:u,sources:m,extraAttributes:h,searchSessionId:g,queryHash:b,baseQueryHash:f,query:x,answerString:v,apiSource:y,brand:E,sessionId:S}=e;return{searchSessionId:g,queryHash:b,baseQueryHash:f,wordCount:(x.match(/\w+/g)||[]).length,queryLength:x.length,answerHash:(0,n("01aV7").sha256Hash)(v),appliedFilters:t,answerFormat:r,answerLength:a,answerWordCount:d,answerCardType:c,followUpsCount:u.length,followUpsLength:u.map(e=>e.length),has3PSources:s(m),sources:i(m),sourceProducts:o(m),apiSource:y,brand:E,sessionId:S,isHello:(0,n("01aV7").isHello)(p),...l(h)}}}),i("01aV7",function(r,a){e(r.exports,"sha256Hash",()=>o),e(r.exports,"extractUrlHostname",()=>i),e(r.exports,"isHello",()=>s),e(r.exports,"getAnswerCardType",()=>d);let o=e=>t(n("3rxD2")).createHash("sha256").update(e).digest("hex"),i=e=>{let t;try{t=new URL(e)}catch{return}return t.hostname},s=e=>"a436116f-02ce-4520-8fbb-7301462a1674"===e,d=(e,t)=>{if(e)return"definition";switch(t){case n("f7lNm").QueryIntent.PERSON:return"people";case n("f7lNm").QueryIntent.TEAM:return"team";case n("f7lNm").QueryIntent.DATE:return"date";case n("f7lNm").QueryIntent.LOCATION:return"location";case n("f7lNm").QueryIntent.TOPIC:return"topic";default:return"SAIN"}}}),i("fjzE4",function(t,r){e(t.exports,"getHighlightCategories",()=>a);let a=e=>{let t=new Map;try{e.forEach(e=>{let r=t.get(e.category);r?t.set(e.category,r+1):t.set(e.category,1)})}catch{return}return Object.fromEntries(t)}}),i("bbPOv",function(t,r){e(t.exports,"KEY_PHRASES_OPERATION_NAME",()=>a),e(t.exports,"KeyPhrasesQuery",()=>o);let a="PlatformHighlightKeywordsQuery",o=`
	query ${a}(
		$entityAri: String!
		$workspaceId: String!
		$jiraReporterAccountId: String
		$jiraAssigneeAccountId: String
		$inputText: KnowledgeDiscoveryKeyPhraseInputText
	) {
		knowledgeDiscovery  {
			keyPhrases(entityAri: $entityAri, workspaceId: $workspaceId, jiraReporterAccountId: $jiraReporterAccountId, jiraAssigneeAccountId: $jiraAssigneeAccountId, inputText: $inputText) 
				@optIn(to: "KnowledgeDiscovery Get Key Phrases") {
				__typename
				... on KnowledgeDiscoveryKeyPhraseConnection {
					nodes {
						... on KnowledgeDiscoveryKeyPhrase {
							keyPhrase
							category
						}
					}
				}
				... on QueryError {
					message
				}
			}
		}
	}
`}),i("cVtio",function(t,r){e(t.exports,"useAnalytics",()=>o);var a=n("gwFzn");let o=()=>{let{createAnalyticsEvent:e}=(0,n("inPa6").useAnalyticsEvents)();return[(0,a.useCallback)(t=>{e(t).fire(n("f7lNm").DEFAULT_GAS_CHANNEL)},[e])]}}),i("7DCm4",function(t,r){e(t.exports,"aiDefinitionsLoadUFOExperience",()=>o);let a="search-ai-definitions",o=new(n("5aVN7")).UFOExperience(`${a}-load`,{type:n("9NDUe").ExperienceTypes.Experience,performanceType:n("9NDUe").ExperiencePerformanceTypes.InlineResult,platform:{component:a}})}),i("5Ymlp",function(t,r){function a(e){return e?{named_id:"reading_aids_agent",experience:"reading-aids"}:{named_id:"sain_agent",experience:"sain"}}function o(e){switch("message_template"in e?e.message_template:e.message.message_template){case"NO_ANSWER_LLM":return n("7Zbm6").NLPSearchErrorState.NoAnswer;case"NO_ANSWER_PEOPLE":return n("7Zbm6").NLPSearchErrorState.NoAnswerWhoQuestion;case"NO_ANSWER_KEYWORDS":return n("7Zbm6").NLPSearchErrorState.NoAnswerKeywords;case"NO_ANSWER_SEARCH_QA_PLUGIN":return n("7Zbm6").NLPSearchErrorState.NoAnswerSearchResults;case"ACCEPTABLE_USE_VIOLATIONS":return n("7Zbm6").NLPSearchErrorState.AcceptableUseViolation;case"OPENAI_RATE_LIMIT_USER_ABUSE":return n("7Zbm6").NLPSearchErrorState.NoAnswerOpenAIRateLimitUserAbuse;case"FEATURE_DISABLED_ON_SITE":return n("7Zbm6").NLPSearchErrorState.AIDisabled;default:return n("7Zbm6").NLPSearchErrorState.NetworkError}}function i(e){let t=e.message||e;return{nlpResult:t.content,uniqueSources:e.sources?e.sources.map(e=>({ari:e.ari,id:e.id?.toString(),title:e.title,product:e.product,type:e.type,url:e.url,lastModified:e.lastModified,iconUrl:null,spaceName:null,spaceUrl:null})):[],disclaimer:t.message_metadata?.disclaimer??null,errorState:null,format:function(e){switch(e){case"text/markdown":default:return n("7Zbm6").NLPSearchResultFormat.MARKDOWN;case"text/adf":return n("7Zbm6").NLPSearchResultFormat.ADF;case"text/json":return n("7Zbm6").NLPSearchResultFormat.JSON}}(t.content_mime_type),extraAPIAnalyticsAttributes:{message_id:t.id,conversational_channel_id:t.conversation_channel_id,experience_id:t.experience_id,user_id:t.user_ari?.replace("ari:cloud:identity::user/","")??null}}}function s(e){return(0,n("2NVuz").isStreamError)(e)?{type:n("7Zbm6").AIAnswerQueryStreamType.FinalResponse,message:{errorState:o(e),errorCode:e.message.status_code,disclaimer:null,format:n("7Zbm6").NLPSearchResultFormat.MARKDOWN,uniqueSources:[]}}:(0,n("2NVuz").isStreamTrace)(e)?{type:n("7Zbm6").AIAnswerQueryStreamType.Trace,message:e.message.content}:(0,n("2NVuz").isStreamAnswerPart)(e)?{type:n("7Zbm6").AIAnswerQueryStreamType.AnswerPart,message:{nlpResult:e.message.content}}:(0,n("2NVuz").isStreamResponse)(e)?{type:n("7Zbm6").AIAnswerQueryStreamType.FinalResponse,message:i(e.message)}:(0,n("2NVuz").isStreamFollowUp)(e)?{type:"follow-up",queries:e.message.follow_up_queries??[]}:{type:"other"}}e(t.exports,"sainStreamFetchHandlerAssistanceService",()=>l),e(t.exports,"sainStreamFetchConvoAIService",()=>c),e(t.exports,"sainRestFetchHandlerAssistanceService",()=>p),e(t.exports,"aiDefinitionsStreamFetchConvoAIService",()=>u);let d=({variables:e,fetchConfig:t})=>{let{query:r,locale:a,additional_context:o}=e||{};return{content:r,locale:a,additional_context:o,entity_ari:t?.entity_ari}};async function*l({fetchReturn:e,variables:t,isReadingAids:r,fetchConfig:o,generatorConfig:i={yieldAnswerPart:!0,yieldFinalResponse:!1},onStreamFinalResponse:l}){try{let{filters:c,selectedProduct:p}=t||{},{experience:u,named_id:m}=a(r),h=`${o?.hostName||""}${n("f7lNm").ASSISTANCE_SERVICE_API_BASE_URL}/chat/v1/invoke_agent/stream`,g=[{confluenceFilters:c}];p&&g.push({knowledgeSources:[p]});let b=await (e||fetch(h,{method:"POST",headers:{"Content-Type":"application/json","X-Product":"confluence","X-Experience-Id":u,...o?.headers?o.headers:{}},body:JSON.stringify({recipient_agent_named_id:m,agent_input:{...d({variables:t,fetchConfig:o}),filters:(0,n("dh538").fg)("kd_sain_enable_source_filtering")?c?g:void 0:c}}),credentials:o?.credentials||"same-origin",signal:o?.timeout?AbortSignal.timeout(o?.timeout):void 0}));if(!b.body)return{state:"failed",reason:"backend",details:"response.body missing",errorCode:b.status};try{let e;let r=b.body.getReader(),a=new TextDecoder("utf-8"),o="",d=!1;for(yield{type:n("7Zbm6").AIAnswerQueryStreamType.AnswerType,message:{format:n("7Zbm6").NLPSearchResultFormat.MARKDOWN}};!d;){let{value:c,done:p}=await r.read();d=p;let u=a.decode(c),m=(o+=u).split("\n");if(!b.ok){let e=JSON.parse(m[0]);if(e?.errors.includes(n("7Zbm6").NLPSearchErrorCodes.HIPAA_ENABLED_ERROR))return{state:"failed",reason:"backend",details:n("7Zbm6").NLPSearchErrorCodes.HIPAA_ENABLED_ERROR,errorCode:b.status};return{state:"failed",reason:"backend",details:"Unhandled error response received",errorCode:b.status}}for(;m.length>1;){let r=m.shift(),a=s(JSON.parse(r));if("other"!==a.type){if(a.type===n("7Zbm6").AIAnswerQueryStreamType.AnswerType||a.type===n("7Zbm6").AIAnswerQueryStreamType.AnswerPart||a.type===n("7Zbm6").AIAnswerQueryStreamType.Trace)i.yieldAnswerPart&&(yield a);else if("follow-up"===a.type){if(!e?.message||!t?.followUpsEnabled)continue;e.message.nlpFollowUpResults={followUps:a.queries},d=!0}else e=a,l?.(),t?.followUpsEnabled||(d=!0),i.yieldFinalResponse&&(yield e)}}o=m[0]}if(e?.type!==n("7Zbm6").AIAnswerQueryStreamType.FinalResponse)return{state:"failed",reason:"parsing",error:"Unexpected final response value"};return{state:"complete",value:e}}catch(e){return{state:"failed",reason:"parsing",error:e}}}catch(e){if(e instanceof DOMException&&"AbortError"===e.name)return{state:"failed",reason:"aborted"};if(e instanceof DOMException&&"TimeoutError"===e.name)return{state:"failed",reason:"timeout"};if(e instanceof Error)return{state:"failed",reason:"error",details:e.message,error:e};return{state:"failed",reason:"unknown"}}}async function*c({fetchReturn:e,variables:t,isReadingAids:r,fetchConfig:o,generatorConfig:i={yieldAnswerPart:!0,yieldFinalResponse:!1},onStreamFinalResponse:l}){try{let{filters:c,selectedProduct:p}=t||{},{experience:u,named_id:m}=a(r),h=`${o?.hostName||""}${n("f7lNm").ASSISTANCE_SERVICE_API_BASE_URL}/rovo/v1/sain/stream`,g=[{confluenceFilters:c}];p&&g.push({knowledgeSources:[p]});let b=await (e||fetch(h,{method:"POST",headers:{"Content-Type":"application/json","X-Product":"confluence","X-Experience-Id":u,...o?.headers?o.headers:{}},body:JSON.stringify({recipient_agent_named_id:m,agent_input:{...d({variables:t,fetchConfig:o}),filters:(0,n("dh538").fg)("kd_sain_enable_source_filtering")?c?g:void 0:c}}),credentials:o?.credentials||"same-origin",signal:o?.timeout?AbortSignal.timeout(o?.timeout):void 0}));if(!b.body)return{state:"failed",reason:"backend",details:"response.body missing",errorCode:b.status};try{let e;let r=b.body.getReader(),a=new TextDecoder("utf-8"),o="",d=!1;for(yield{type:n("7Zbm6").AIAnswerQueryStreamType.AnswerType,message:{format:n("7Zbm6").NLPSearchResultFormat.MARKDOWN}};!d;){let{value:c,done:p}=await r.read();d=p;let u=a.decode(c),m=(o+=u).split("\n");if(!b.ok){let e=JSON.parse(m[0]);if(e?.errors.includes(n("7Zbm6").NLPSearchErrorCodes.HIPAA_ENABLED_ERROR))return{state:"failed",reason:"backend",details:n("7Zbm6").NLPSearchErrorCodes.HIPAA_ENABLED_ERROR,errorCode:b.status};return{state:"failed",reason:"backend",details:"Unhandled error response received",errorCode:b.status}}for(;m.length>1;){let r=m.shift(),a=s(JSON.parse(r));if("other"!==a.type){if(a.type===n("7Zbm6").AIAnswerQueryStreamType.AnswerType||a.type===n("7Zbm6").AIAnswerQueryStreamType.AnswerPart||a.type===n("7Zbm6").AIAnswerQueryStreamType.Trace)i.yieldAnswerPart&&(yield a);else if("follow-up"===a.type){if(!e?.message||!t?.followUpsEnabled)continue;e.message.nlpFollowUpResults={followUps:a.queries},d=!0}else e=a,l?.(),t?.followUpsEnabled||(d=!0),i.yieldFinalResponse&&(yield e)}}o=m[0]}if(e?.type!==n("7Zbm6").AIAnswerQueryStreamType.FinalResponse)return{state:"failed",reason:"parsing",error:"Unexpected final response value"};return{state:"complete",value:e}}catch(e){return{state:"failed",reason:"parsing",error:e}}}catch(e){if(e instanceof DOMException&&"AbortError"===e.name)return{state:"failed",reason:"aborted"};if(e instanceof DOMException&&"TimeoutError"===e.name)return{state:"failed",reason:"timeout"};if(e instanceof Error)return{state:"failed",reason:"error",details:e.message,error:e};return{state:"failed",reason:"unknown"}}}async function p({variables:e,isReadingAids:t,fetchConfig:r}){let{experience:s,named_id:l}=a(t),c=`${r?.hostName||""}${n("f7lNm").ASSISTANCE_SERVICE_API_BASE_URL}/chat/v1/invoke_agent`,p=await fetch(c,{method:"POST",headers:{"Content-Type":"application/json","X-Product":"confluence","X-Experience-Id":s,...r?.headers},body:JSON.stringify({recipient_agent_named_id:l,agent_input:d({variables:e,fetchConfig:r})}),credentials:r?.credentials||"same-origin",signal:r?.timeout?AbortSignal.timeout(r?.timeout):void 0}),u=await p.json();return"message_template"in u?{nlpSearch:{errorState:o(u),disclaimer:null,format:n("7Zbm6").NLPSearchResultFormat.MARKDOWN,uniqueSources:[]}}:{nlpSearch:i(u)}}async function*u({fetchReturn:e,variables:t,fetchConfig:r,generatorConfig:a={yieldAnswerPart:!0,yieldFinalResponse:!1},onStreamFinalResponse:o}){try{let i=`${r?.hostName||""}${n("f7lNm").ASSISTANCE_SERVICE_API_BASE_URL}/rovo/v1/ai-definition`,l=await (e||fetch(i,{method:"POST",headers:{"Content-Type":"application/json","X-Product":"confluence","X-Experience-Id":"reading-aids",...r?.headers?r.headers:{}},body:JSON.stringify({...d({variables:t,fetchConfig:r})}),credentials:r?.credentials||"same-origin",signal:r?.timeout?AbortSignal.timeout(r?.timeout):void 0}));if(!l.body)return{state:"failed",reason:"backend",details:"response.body missing",errorCode:l.status};try{let e;let r=l.body.getReader(),i=new TextDecoder("utf-8"),d="",c=!1;for(yield{type:n("7Zbm6").AIAnswerQueryStreamType.AnswerType,message:{format:n("7Zbm6").NLPSearchResultFormat.MARKDOWN}};!c;){let{value:p,done:u}=await r.read();c=u;let m=i.decode(p),h=(d+=m).split("\n");if(!l.ok){let e=JSON.parse(h[0]);if(e?.errors.includes(n("7Zbm6").NLPSearchErrorCodes.HIPAA_ENABLED_ERROR))return{state:"failed",reason:"backend",details:n("7Zbm6").NLPSearchErrorCodes.HIPAA_ENABLED_ERROR,errorCode:l.status};return{state:"failed",reason:"backend",details:"Unhandled error response received",errorCode:l.status}}for(;h.length>1;){let r=h.shift(),i=s(JSON.parse(r));if("other"!==i.type){if(i.type===n("7Zbm6").AIAnswerQueryStreamType.AnswerType||i.type===n("7Zbm6").AIAnswerQueryStreamType.AnswerPart||i.type===n("7Zbm6").AIAnswerQueryStreamType.Trace)a.yieldAnswerPart&&(yield i);else if("follow-up"===i.type){if(!e?.message||!t?.followUpsEnabled)continue;e.message.nlpFollowUpResults={followUps:i.queries},c=!0}else e=i,o?.(),t?.followUpsEnabled||(c=!0),a.yieldFinalResponse&&(yield e)}}d=h[0]}if(e?.type!==n("7Zbm6").AIAnswerQueryStreamType.FinalResponse)return{state:"failed",reason:"parsing",error:"Unexpected final response value"};return{state:"complete",value:e}}catch(e){return{state:"failed",reason:"parsing",error:e}}}catch(e){if(e instanceof DOMException&&"AbortError"===e.name)return{state:"failed",reason:"aborted"};if(e instanceof DOMException&&"TimeoutError"===e.name)return{state:"failed",reason:"timeout"};if(e instanceof Error)return{state:"failed",reason:"error",details:e.message,error:e};return{state:"failed",reason:"unknown"}}}}),i("2NVuz",function(t,r){e(t.exports,"isStreamResponse",()=>a),e(t.exports,"isStreamError",()=>o),e(t.exports,"isStreamAnswerPart",()=>n),e(t.exports,"isStreamTrace",()=>i),e(t.exports,"isStreamFollowUp",()=>s);let a=e=>e instanceof Object&&"FINAL_RESPONSE"===e.type,o=e=>e instanceof Object&&"ERROR"===e.type,n=e=>e instanceof Object&&"ANSWER_PART"===e.type,i=e=>e instanceof Object&&"TRACE"===e.type,s=e=>e instanceof Object&&"FOLLOW_UP_QUERIES"===e.type}),i("eVM9z",function(t,r){e(t.exports,"useDefinitionSupplier",()=>s);var a=n("gwFzn");let o=(0,n("2nPZH").defineMessages)({searchAiDialogQueryPretext:{id:"contextual-reading-aids.search-ai-dialog.query-pretext",defaultMessage:"what is {queryText}?"}}),i="No matching scope for Definition",s=({workspaceId:e,cloudIdARI:t,fetchConfig:r,isDefinitionCurationEnabled:s,productConfig:d,product:l})=>{let c=(0,n("dBxQj").default)(),[p,u]=(0,a.useState)(!0),{fireAnalyticsEvent:m,commonAttributes:h}=(0,n("eRXI0").useAIAnswerContext)(),{contentId:g}=d,b=(0,a.useCallback)(async({variables:a})=>{let{query:s,locale:d,additional_context:p,experience:b,followUpsEnabled:f}=a;if(""!==g)try{let r=await (0,n("9EFEY").fetchAggResponse)({graphQuery:n("4WiNS").PrecomputedDefinitionQuery,variables:{workspaceId:e,keyPhrase:a.query,contentId:g},headers:(0,n("6yuru").createAtlAttributionHeader)({atlWorkspaceId:e,tenantId:t,product:l})});if(r.data&&!r.data.knowledgeDiscovery.autoDefinition.message){let e={nlpSearch:(0,n("3qbRZ").mapCustomDefinitionToNLPSearchType)(r.data.knowledgeDiscovery.autoDefinition)};return u(!1),e}if(r.data&&r.data.knowledgeDiscovery.autoDefinition.message)throw Error(r.data.knowledgeDiscovery.autoDefinition.message);throw Error("Something went wrong with fetching precomputed definition")}catch(e){e instanceof Object&&"message"in e&&e.message!==i&&m((0,n("xhg8G").fetchPrecomputedDefinitionErrorPayload)(e,h))}let x={variables:{query:c.formatMessage(o.searchAiDialogQueryPretext,{queryText:s}),locale:d,cloudIdARI:t,additional_context:p,experience:b,followUpsEnabled:f},isReadingAids:!0,fetchConfig:r,generatorConfig:{yieldAnswerPart:!0,yieldFinalResponse:!0},onStreamFinalResponse:()=>{u(!1)}},v=(0,n("c6GJD").default).getExperimentValue("kd_definitions_convo_ai","cohort","control");return{type:n("7Zbm6").AIAnswerAPIType.STREAM,stream:"test"===v?(0,n("5Ymlp").aiDefinitionsStreamFetchConvoAIService)(x):(0,n("5Ymlp").sainStreamFetchHandlerAssistanceService)(x)}},[t,r,c,h,m,e,g,l]);return{fetchDefinition:(0,a.useCallback)(async({variables:r})=>{if(s)try{let a,o;"spaceId"in d?a=d:"projectId"in d&&(o={projectId:d.projectId});let i=await (0,n("9EFEY").fetchAggResponse)({graphQuery:n("9nZle").CuratedDefinitionQuery,variables:{workspaceId:e,keyPhrase:r.query,confluenceScopeId:a,jiraScopeId:o},operationName:n("9nZle").CURATED_DEFINITION_OPERATION_NAME,headers:(0,n("6yuru").createAtlAttributionHeader)({atlWorkspaceId:e,tenantId:t,product:l})});if(i.data&&!i.data.knowledgeDiscovery.definition.message){let e={nlpSearch:(0,n("3qbRZ").mapCustomDefinitionToNLPSearchType)(i.data.knowledgeDiscovery.definition)};return u(!1),e}if(i.data&&i.data.knowledgeDiscovery.definition.message)throw Error(i.data.knowledgeDiscovery.definition.message);throw Error("Something went wrong with fetching curated definition")}catch(e){e instanceof Object&&"message"in e&&e.message!==i&&m((0,n("xhg8G").fetchCuratedDefinitionErrorPayload)(e,h))}return b({variables:r})},[d,b,s,e,h,m,t,l]),loading:p}}}),i("eRXI0",function(r,a){e(r.exports,"AIAnswerContext",()=>s),e(r.exports,"useAIAnswerContext",()=>d);var o=n("gwFzn");let i={cloudId:"",query:"",queryHash:"",baseQueryHash:"",source:"",searchSessionId:"",answerString:"",answerLength:0,answerWordCount:0,answerFormat:null,answerCardType:"SAIN",sources:[],followUps:[],errorState:null,extraAttributes:{},apiSource:"cc-search-nlp",workspaceId:"",sessionId:"",brand:n("f7lNm").AiBrand.AI,orgId:""},s=t(o).createContext({loading:void 0,isAnswered:!1,hasError:!1,advancedSearchUrl:void 0,onNavigate:()=>{},updateContextCache:()=>{},fireAnalyticsEvent:()=>{},setQuery:()=>{},setData:()=>{},userDetails:{},disclaimer:null,commonAttributes:i,initialCollapsed:void 0,liked:void 0,setLiked:()=>{},likesDisabled:!1,setLikesDisabled:()=>{},initialReported:void 0,isReadingAids:!1,cardProviderProps:void 0,baseQuery:void 0,smartAnswersRoute:n("f7lNm").QueryIntent.DEFAULT,cardTemplate:n("f7lNm").CardTemplate.DEFAULT,brand:n("f7lNm").AiBrand.AI,answerEditor:void 0,closeParentDialog:()=>{},showBookends:!1,showGenericFooter:!1,initiallyExpanded:!1}),d=()=>(0,o.useContext)(s)}),i("xhg8G",function(t,r){e(t.exports,"fetchCuratedDefinitionErrorPayload",()=>a),e(t.exports,"fetchPrecomputedDefinitionErrorPayload",()=>o),e(t.exports,"updateDefinitionErrorPayload",()=>i),e(t.exports,"toggleDefinitionErrorPayload",()=>s);let a=(e,t)=>{let{extraAttributes:r,source:a}=t;return{action:"failed",actionSubject:"aiCuratedDefinitionFetch",source:a,eventType:"track",attributes:{...(0,n("cqFuK").sanitizeExtraAttributes)(r),errorName:e instanceof Object&&"name"in e?e.name:"",errorMessage:e instanceof Object&&"message"in e?e.message:"",errorStack:e instanceof Object&&"stack"in e&&"string"==typeof e.stack?e.stack?.split("\n").at(1):""}}},o=(e,t)=>{let{extraAttributes:r,source:a}=t;return{action:"failed",actionSubject:"aiPrecomputedDefinitionFetch",source:a,eventType:"track",attributes:{...(0,n("cqFuK").sanitizeExtraAttributes)(r),errorName:e instanceof Object&&"name"in e?e.name:"",errorMessage:e instanceof Object&&"message"in e?e.message:"",errorStack:e instanceof Object&&"stack"in e&&"string"==typeof e.stack?e.stack?.split("\n").at(1):""}}},i=(e,t)=>{let{extraAttributes:r,source:a}=t;return{action:"failed",actionSubject:"aiCuratedDefinitionUpdate",source:a,eventType:"track",attributes:{...(0,n("cqFuK").sanitizeExtraAttributes)(r),errorName:e instanceof Object&&"name"in e?e.name:"",errorMessage:e instanceof Object&&"message"in e?e.message:"",errorStack:e instanceof Object&&"stack"in e&&"string"==typeof e.stack?e.stack?.split("\n").at(1):""}}},s=(e,t)=>{let{extraAttributes:r,source:a}=t;return{action:"failed",actionSubject:"aiDefinitionToggle",source:a,eventType:"track",attributes:{...(0,n("cqFuK").sanitizeExtraAttributes)(r),errorName:e instanceof Object&&"name"in e?e.name:"",errorMessage:e instanceof Object&&"message"in e?e.message:"",errorStack:e instanceof Object&&"stack"in e&&"string"==typeof e.stack?e.stack?.split("\n").at(1):""}}}}),i("9nZle",function(t,r){e(t.exports,"CURATED_DEFINITION_OPERATION_NAME",()=>a),e(t.exports,"CuratedDefinitionQuery",()=>o);let a="CuratedDefinitionQuery",o=`
query ${a}(
		$workspaceId: String!
		$keyPhrase: String!
		$confluenceScopeId: KnowledgeDiscoveryDefinitionScopeIdConfluence
		$jiraScopeId: KnowledgeDiscoveryDefinitionScopeIdJira
	) {
		knowledgeDiscovery {
			definition(
				workspaceId: $workspaceId
				keyPhrase: $keyPhrase
				confluenceScopeId: $confluenceScopeId
				jiraScopeId: $jiraScopeId
			) @optIn(to: "KnowledgeDiscovery Get definition") {
				__typename
				... on KnowledgeDiscoveryDefinition {
					definition
					accountId
					createdAt
					editor {
						... on User {
							name
							accountId
						}
					}
					referenceUrl
					confluenceEntity {
						... on ConfluencePage {
							id
							type
							title
							space {
								name
							}
						}
						... on ConfluenceBlogPost {
							id
							type
							title
							space {
								name
							}
						}
					}
				}
				... on QueryError {
					message
				}
			}
		}
	}
`}),i("4WiNS",function(t,r){e(t.exports,"PrecomputedDefinitionQuery",()=>a);let a=`
query PrecomputedDefinitionQuery(
		$workspaceId: String!
		$keyPhrase: String!
        $contentId: String!
	) {
		knowledgeDiscovery {
			autoDefinition(
				workspaceId: $workspaceId
				keyPhrase: $keyPhrase
				contentId: $contentId
			) @optIn(to: "KnowledgeDiscovery Get auto definition") {
				__typename
				... on KnowledgeDiscoveryAutoDefinition {
					definition
                    createdAt
					confluenceEntity {
						... on ConfluencePage {
							id
							type
							title
							space {
								name
							}
                            links {
                                base
                                webUi
                            }
						}
						... on ConfluenceBlogPost {
							id
							type
							title
							space {
								name
							}
                            links {
                                base
                                webUi
                            }
						}
					}
				}
				... on QueryError {
					message
                    extensions {
                        statusCode
                        errorType
                    }
				}
			}
		}
	}
`}),i("3qbRZ",function(t,r){e(t.exports,"mapCustomDefinitionToNLPSearchType",()=>a);let a=e=>{let t=e.confluenceEntity;return{nlpResult:e.definition,uniqueSources:t?[{id:t?.id||"",title:t?.title||"",url:"referenceUrl"in e?e.referenceUrl||"":"links"in t&&t.links.base&&t.links.webUi?`${t.links.base}${t.links.webUi}`:"",type:t?.type||"",product:"Confluence",lastModified:"",iconUrl:"",spaceName:t?.space?.name||"",spaceUrl:null}]:[],nlpResultEditor:"editor"in e?{name:e.editor?.name||"",id:e.editor?.accountId||""}:void 0,disclaimer:null,errorState:null,format:n("7Zbm6").NLPSearchResultFormat.MARKDOWN,customDefinitionType:"editor"in e?n("7Zbm6").NLPSearchCustomDefinitionType.CURATED:n("7Zbm6").NLPSearchCustomDefinitionType.PRECOMPUTED}}}),i("9KkVf",function(t,r){e(t.exports,"EditedDefinitionScope",()=>o);var a,o=((a={}).SPACE="SPACE",a.PAGE="PAGE",a.BLOGPOST="BLOGPOST",a.ORGANIZATION="ORGANIZATION",a.PROJECT="PROJECT",a)}),i("lOkIA",function(r,a){e(r.exports,"CenteredSpinner",()=>d);var o=n("gwFzn");function i(e,t,r){var a;return(t="symbol"==typeof(a=function(e,t){if("object"!=typeof e||!e)return e;var r=e[Symbol.toPrimitive];if(void 0!==r){var a=r.call(e,t||"default");if("object"!=typeof a)return a;throw TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(t,"string"))?a:a+"")in e?Object.defineProperty(e,t,{value:r,enumerable:!0,configurable:!0,writable:!0}):e[t]=r,e}let s={small:12,medium:26,large:36};class d extends o.PureComponent{render(){let{style:e,size:r}=this.props;return t(o).createElement("div",{style:e,"data-test-id":"wrapper-spinner",className:(0,n("35pXk").default)(["_1bsb1osq _4t3i1osq _kqswh2mm"])},t(o).createElement("div",{"data-test-id":"spinner",style:{marginLeft:`${-s[r]/2}px`,marginTop:`${-s[r]/2}px`},className:(0,n("35pXk").default)(["_kqswstnw _1ltv1ssb _154i1ssb _1pbyb4wl"])},t(o).createElement(n("9hlns").default,{size:s[r]})))}}i(d,"displayName","CenteredSpinner"),i(d,"propTypes",{style:t(n("fppBw")).object,size:t(n("fppBw")).oneOf(["small","medium","large"])}),i(d,"defaultProps",{size:"small"})}),i("97Szk",function(r,a){e(r.exports,"useDefinitionRestrictionOptions",()=>s);var o=n("gwFzn");let i=(0,n("2nPZH").defineMessages)({editDefinitionRestrictedToSpaceOption:{id:"contextual-reading-aids.edit.definition.restricted.to.space.option",defaultMessage:"In this space"},editDefinitionRestrictedToPageOption:{id:"contextual-reading-aids.edit.definition.restricted.to.page.option",defaultMessage:"On this page"},editDefinitionRestrictedToBlogpostOption:{id:"contextual-reading-aids.edit.definition.restricted.to.blogpost.option",defaultMessage:"On this blogpost"},editDefinitionRestrictedToSiteOption:{id:"contextual-reading-aids.edit.definition.restricted.to.site.option",defaultMessage:"On this site"}});function s(e){let{formatMessage:r}=(0,n("dBxQj").default)();return(0,o.useMemo)(()=>[{label:r(i.editDefinitionRestrictedToSpaceOption),value:n("9KkVf").EditedDefinitionScope.SPACE,icon:t(o).createElement(t(n("nigEg")),{label:""})},"blogpost"===e?{label:r(i.editDefinitionRestrictedToBlogpostOption),value:n("9KkVf").EditedDefinitionScope.BLOGPOST,icon:t(o).createElement(t(n("am4ic")),{label:""})}:{label:r(i.editDefinitionRestrictedToPageOption),value:n("9KkVf").EditedDefinitionScope.PAGE,icon:t(o).createElement(t(n("kd3D9")),{label:""})},{label:r(i.editDefinitionRestrictedToSiteOption),value:n("9KkVf").EditedDefinitionScope.ORGANIZATION,icon:t(o).createElement(t(n("hYhtq")),{label:""})}],[e,r])}});
//# sourceMappingURL=ReadTimePopup.5319eb18.js.map
