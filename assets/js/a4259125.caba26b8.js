"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[419],{3905:(e,t,n)=>{n.d(t,{Zo:()=>p,kt:()=>m});var r=n(7294);function a(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function o(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function i(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?o(Object(n),!0).forEach((function(t){a(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):o(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function s(e,t){if(null==e)return{};var n,r,a=function(e,t){if(null==e)return{};var n,r,a={},o=Object.keys(e);for(r=0;r<o.length;r++)n=o[r],t.indexOf(n)>=0||(a[n]=e[n]);return a}(e,t);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(e);for(r=0;r<o.length;r++)n=o[r],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(a[n]=e[n])}return a}var c=r.createContext({}),l=function(e){var t=r.useContext(c),n=t;return e&&(n="function"==typeof e?e(t):i(i({},t),e)),n},p=function(e){var t=l(e.components);return r.createElement(c.Provider,{value:t},e.children)},u="mdxType",d={inlineCode:"code",wrapper:function(e){var t=e.children;return r.createElement(r.Fragment,{},t)}},h=r.forwardRef((function(e,t){var n=e.components,a=e.mdxType,o=e.originalType,c=e.parentName,p=s(e,["components","mdxType","originalType","parentName"]),u=l(n),h=a,m=u["".concat(c,".").concat(h)]||u[h]||d[h]||o;return n?r.createElement(m,i(i({ref:t},p),{},{components:n})):r.createElement(m,i({ref:t},p))}));function m(e,t){var n=arguments,a=t&&t.mdxType;if("string"==typeof e||a){var o=n.length,i=new Array(o);i[0]=h;var s={};for(var c in t)hasOwnProperty.call(t,c)&&(s[c]=t[c]);s.originalType=e,s[u]="string"==typeof e?e:a,i[1]=s;for(var l=2;l<o;l++)i[l]=n[l];return r.createElement.apply(null,i)}return r.createElement.apply(null,n)}h.displayName="MDXCreateElement"},3401:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>c,contentTitle:()=>i,default:()=>d,frontMatter:()=>o,metadata:()=>s,toc:()=>l});var r=n(7462),a=(n(7294),n(3905));const o={sidebar_position:3},i="LLMs",s={unversionedId:"llms/index",id:"llms/index",title:"LLMs",description:"Large Language Models like GPT-4 is the whole reason LiteChain exists, we want to build on top of LLMs to construct an application. After learning the Chain Basics, it should be clear how you can wrap any LLM in a Chain, you just need to produce an AsyncGenerator out of their output. However, LiteChain already come with some LLM chains out of the box to make it easier.",source:"@site/docs/llms/index.md",sourceDirName:"llms",slug:"/llms/",permalink:"/litechain/docs/llms/",draft:!1,editUrl:"https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/docs/llms/index.md",tags:[],version:"current",sidebarPosition:3,frontMatter:{sidebar_position:3},sidebar:"tutorialSidebar",previous:{title:"Type Signatures",permalink:"/litechain/docs/chain-basics/type_signatures"},next:{title:"OpenAI LLMs",permalink:"/litechain/docs/llms/open_ai"}},c={},l=[],p={toc:l},u="wrapper";function d(e){let{components:t,...n}=e;return(0,a.kt)(u,(0,r.Z)({},p,n,{components:t,mdxType:"MDXLayout"}),(0,a.kt)("h1",{id:"llms"},"LLMs"),(0,a.kt)("p",null,"Large Language Models like GPT-4 is the whole reason LiteChain exists, we want to build on top of LLMs to construct an application. After learning the ",(0,a.kt)("a",{parentName:"p",href:"/docs/chain-basics"},"Chain Basics"),", it should be clear how you can wrap any LLM in a ",(0,a.kt)("a",{parentName:"p",href:"pathname:///reference/litechain/index.html#chain"},(0,a.kt)("inlineCode",{parentName:"a"},"Chain")),", you just need to produce an ",(0,a.kt)("a",{parentName:"p",href:"https://peps.python.org/pep-0525/"},(0,a.kt)("inlineCode",{parentName:"a"},"AsyncGenerator"))," out of their output. However, LiteChain already come with some LLM chains out of the box to make it easier."),(0,a.kt)("p",null,"Like other things that are not part of the core of the library, they live under ",(0,a.kt)("inlineCode",{parentName:"p"},"litechain.contrib"),". Go ahead for OpenAI examples."))}d.isMDXComponent=!0}}]);